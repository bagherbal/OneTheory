"""Exact convention-aware pseudo-Riemannian and differential-form geometry.

Owns:
    Arbitrary-dimensional signatures, orientations, index spaces, immutable tensors,
    metrics, exterior calculus, Hodge duality, integration records, and symbolic
    Levi-Civita and torsionful connection data.

Depends on:
    Exact linear algebra and convention errors. This general physical geometry layer
    is independent of compactification models, bundles, observations, and research.

Must not:
    Select a compactification, supply a numerical metric field, infer a connection from
    topology, or identify a mathematical manifold with a OneTheory carrier.

Phase 0:
    Generic exact geometry is implemented; coordinate-dependent derivatives and solved
    curvature fields remain explicit inputs rather than hidden numerical calculations.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from itertools import combinations, product
from math import isqrt
from typing import Any

from onetheory.core.errors import IncompatibleConvention
from onetheory.math.linear import Matrix, Scalar
from onetheory.math.numbers import Rational


class IndexVariance(StrEnum):
    """Variance of a tensor index."""

    COVARIANT = "covariant"
    CONTRAVARIANT = "contravariant"


@dataclass(frozen=True, slots=True)
class MetricSignature:
    """An exact diagonal pseudo-Riemannian signature."""

    signs: tuple[int, ...]

    def __init__(self, signs: Iterable[int] = (1, -1, -1, -1)) -> None:
        values = tuple(signs)
        if not values or any(value not in (-1, 1) for value in values):
            raise ValueError("metric signatures require nonempty signs ±1")
        object.__setattr__(self, "signs", values)

    @property
    def dimension(self) -> int:
        """Return the manifold dimension represented by the signature."""

        return len(self.signs)

    @property
    def negative_index(self) -> int:
        """Return the number of negative metric directions."""

        return self.signs.count(-1)

    @property
    def is_lorentzian(self) -> bool:
        """Return whether exactly one direction has the minority sign."""

        return self.negative_index in (1, self.dimension - 1)


@dataclass(frozen=True, slots=True)
class Orientation:
    """A positively oriented ordered coordinate frame."""

    order: tuple[int, ...]

    def __init__(self, order: Iterable[int] = (0, 1, 2, 3)) -> None:
        values = tuple(order)
        if tuple(sorted(values)) != tuple(range(len(values))):
            raise ValueError("orientation must be a permutation of 0 through n-1")
        object.__setattr__(self, "order", values)

    @property
    def dimension(self) -> int:
        """Return the orientation dimension."""

        return len(self.order)


@dataclass(frozen=True, slots=True)
class SpacetimeConvention:
    """The signature and orientation that make tensor operations comparable."""

    signature: MetricSignature
    orientation: Orientation

    def __post_init__(self) -> None:
        if self.signature.dimension != self.orientation.dimension:
            raise IncompatibleConvention("signature and orientation dimensions differ")

    @classmethod
    def lorentzian(
        cls,
        signature: MetricSignature | None = None,
        orientation: Orientation | None = None,
    ) -> SpacetimeConvention:
        """Construct the conventional four-dimensional Lorentzian convention."""

        chosen_signature = signature or MetricSignature()
        chosen_orientation = orientation or Orientation(range(chosen_signature.dimension))
        return cls(chosen_signature, chosen_orientation)


@dataclass(frozen=True, slots=True)
class IndexSpace:
    """A finite index space with declared dimension, variance, and convention."""

    name: str
    dimension: int
    variance: IndexVariance
    convention: SpacetimeConvention

    def __post_init__(self) -> None:
        if not self.name.strip() or self.dimension != self.convention.signature.dimension:
            raise ValueError("index spaces must match the declared convention")


@dataclass(frozen=True, slots=True)
class TensorBundle:
    """A typed tensor-bundle record over one pseudo-Riemannian manifold."""

    name: str
    manifold: PseudoRiemannianManifold
    rank: int
    index_variances: tuple[IndexVariance, ...]
    provenance: str

    def __init__(
        self,
        name: str,
        manifold: PseudoRiemannianManifold,
        index_variances: Iterable[IndexVariance],
        provenance: str,
    ) -> None:
        variances = tuple(index_variances)
        if not name.strip() or not variances or not provenance.strip():
            raise ValueError("tensor bundles require a name, rank, and provenance")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "manifold", manifold)
        object.__setattr__(self, "rank", len(variances))
        object.__setattr__(self, "index_variances", variances)
        object.__setattr__(self, "provenance", provenance)


def _shape_size(shape: Sequence[int]) -> int:
    result = 1
    for value in shape:
        result *= value
    return result


def _flat_index(indices: Sequence[int], shape: Sequence[int]) -> int:
    value = 0
    for index, size in zip(indices, shape, strict=True):
        if index < 0 or index >= size:
            raise IndexError("tensor index is outside its index space")
        value = value * size + index
    return value


def _sum(values: Iterable[Any]) -> Any:
    result: Any = 0
    for value in values:
        result = result + value
    return result


def _permutation_sign(sequence: Sequence[int]) -> int:
    if len(set(sequence)) != len(sequence):
        return 0
    inversions = sum(
        sequence[left] > sequence[right]
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def _concatenated_sign(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    return _permutation_sign((*left, *right))


@dataclass(frozen=True, slots=True)
class Tensor:
    """An immutable component tensor with typed index spaces."""

    index_spaces: tuple[IndexSpace, ...]
    components: tuple[Any, ...]

    def __init__(self, index_spaces: Iterable[IndexSpace], components: Iterable[Any]) -> None:
        spaces = tuple(index_spaces)
        values = tuple(components)
        expected = _shape_size(tuple(space.dimension for space in spaces))
        if not spaces and len(values) != 1:
            raise ValueError("a rank-zero tensor has one component")
        if len(values) != expected:
            raise ValueError("tensor components do not match index-space dimensions")
        conventions = {space.convention for space in spaces}
        if len(conventions) > 1:
            raise IncompatibleConvention("tensor index spaces use different conventions")
        object.__setattr__(self, "index_spaces", spaces)
        object.__setattr__(self, "components", values)

    @property
    def rank(self) -> int:
        """Return the tensor rank."""

        return len(self.index_spaces)

    @property
    def convention(self) -> SpacetimeConvention | None:
        """Return the common convention, if the tensor has an index."""

        return self.index_spaces[0].convention if self.index_spaces else None

    def component(self, indices: Sequence[int] = ()) -> Any:
        """Return one exact tensor component."""

        if len(indices) != self.rank:
            raise ValueError("tensor index rank does not match")
        return self.components[_flat_index(indices, tuple(s.dimension for s in self.index_spaces))]

    def contract(self, left_axis: int, right_axis: int) -> Tensor:
        """Contract one covariant and one contravariant index exactly."""

        if (
            left_axis == right_axis
            or not (0 <= left_axis < self.rank)
            or not (0 <= right_axis < self.rank)
        ):
            raise ValueError("contraction axes must be distinct valid indices")
        left = self.index_spaces[left_axis]
        right = self.index_spaces[right_axis]
        if left.dimension != right.dimension or left.variance is right.variance:
            raise ValueError("contraction requires opposite matching index spaces")
        remaining = tuple(
            space
            for index, space in enumerate(self.index_spaces)
            if index not in (left_axis, right_axis)
        )
        shape = tuple(space.dimension for space in remaining)
        components: list[Any] = []
        for output in product(*(range(size) for size in shape)) if shape else [()]:
            output_index = 0
            indices: list[int] = []
            total: Any = 0
            for axis in range(self.rank):
                if axis in (left_axis, right_axis):
                    indices.append(output_index)
                    if axis == right_axis:
                        output_index += 1
                else:
                    indices.append(output[output_index])
                    output_index += 1
            for repeated in range(left.dimension):
                indices[left_axis] = repeated
                indices[right_axis] = repeated
                total = total + self.component(indices)
            components.append(total)
        return Tensor(remaining, components)

    def _replace_index(
        self, axis: int, variance: IndexVariance, components: Iterable[Any]
    ) -> Tensor:
        spaces = list(self.index_spaces)
        spaces[axis] = IndexSpace(
            spaces[axis].name,
            spaces[axis].dimension,
            variance,
            spaces[axis].convention,
        )
        return Tensor(spaces, components)


@dataclass(frozen=True, slots=True)
class Metric:
    """A nondegenerate exact metric in one arbitrary-dimensional convention."""

    convention: SpacetimeConvention
    components: tuple[tuple[Scalar, ...], ...]

    def __init__(
        self,
        convention: SpacetimeConvention | None = None,
        components: Iterable[Iterable[object]] | None = None,
    ) -> None:
        chosen = convention or SpacetimeConvention.lorentzian()
        dimension = chosen.signature.dimension
        raw = (
            components
            if components is not None
            else (
                (sign if row == column else 0 for column in range(dimension))
                for row, sign in enumerate(chosen.signature.signs)
            )
        )
        values = tuple(tuple(row) for row in raw)
        if len(values) != dimension or any(len(row) != dimension for row in values):
            raise ValueError("metric shape does not match its convention")
        matrix = Matrix(values)
        if matrix.determinant().is_zero():
            raise ValueError("the metric must be nondegenerate")
        if any(
            values[row][column] != values[column][row]
            for row in range(dimension)
            for column in range(dimension)
        ):
            raise ValueError("the metric must be symmetric")
        object.__setattr__(self, "convention", chosen)
        object.__setattr__(self, "components", matrix.rows)

    @property
    def dimension(self) -> int:
        """Return the metric dimension."""

        return self.convention.signature.dimension

    @property
    def inverse_components(self) -> tuple[tuple[Scalar, ...], ...]:
        """Return the exact inverse metric."""

        return self._matrix().inverse().rows

    @property
    def determinant(self) -> Scalar:
        """Return the exact metric determinant."""

        return self._matrix().determinant()

    def _matrix(self) -> Matrix:
        return Matrix(self.components)

    def lower(self, tensor: Tensor, axis: int) -> Tensor:
        """Lower one contravariant index with this metric."""

        return self._transform(tensor, axis, IndexVariance.COVARIANT, self.components)

    def raise_(self, tensor: Tensor, axis: int) -> Tensor:
        """Raise one covariant index with the inverse metric."""

        return self._transform(tensor, axis, IndexVariance.CONTRAVARIANT, self.inverse_components)

    def lower_index(self, tensor: Tensor, axis: int) -> Tensor:
        """Named alias for lowering one index."""

        return self.lower(tensor, axis)

    def raise_index(self, tensor: Tensor, axis: int) -> Tensor:
        """Named alias for raising one index."""

        return self.raise_(tensor, axis)

    def _transform(
        self,
        tensor: Tensor,
        axis: int,
        variance: IndexVariance,
        matrix: Sequence[Sequence[Any]],
    ) -> Tensor:
        if not 0 <= axis < tensor.rank:
            raise ValueError("metric transform axis is invalid")
        space = tensor.index_spaces[axis]
        if space.convention != self.convention:
            raise IncompatibleConvention("metric and tensor use different conventions")
        if (
            variance is IndexVariance.COVARIANT
            and space.variance is not IndexVariance.CONTRAVARIANT
        ) or (
            variance is IndexVariance.CONTRAVARIANT
            and space.variance is not IndexVariance.COVARIANT
        ):
            raise ValueError("metric transform requires the opposite index variance")
        shape = tuple(item.dimension for item in tensor.index_spaces)
        values = []
        for indices in product(*(range(size) for size in shape)):
            values.append(
                _sum(
                    matrix[indices[axis]][old]
                    * tensor.component((*indices[:axis], old, *indices[axis + 1 :]))
                    for old in range(space.dimension)
                )
            )
        return tensor._replace_index(axis, variance, values)


@dataclass(frozen=True, slots=True)
class PseudoRiemannianManifold:
    """An arbitrary-dimensional manifold with an exact metric convention."""

    name: str
    convention: SpacetimeConvention
    metric: Metric

    def __init__(
        self,
        name: str = "M",
        convention: SpacetimeConvention | None = None,
        metric: Metric | None = None,
    ) -> None:
        chosen = convention or SpacetimeConvention.lorentzian()
        selected_metric = metric or Metric(chosen)
        if not name.strip():
            raise ValueError("manifolds require a nonempty name")
        if selected_metric.convention != chosen:
            raise IncompatibleConvention("manifold and metric conventions differ")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "convention", chosen)
        object.__setattr__(self, "metric", selected_metric)

    @property
    def dimension(self) -> int:
        """Return the manifold dimension."""

        return self.convention.signature.dimension


LorentzianSpacetime = PseudoRiemannianManifold
Manifold = PseudoRiemannianManifold
PseudoRiemannianSignature = MetricSignature


@dataclass(frozen=True, slots=True)
class SymbolicSqrt:
    """An exact symbolic square root retained when a metric determinant is nonsquare."""

    radicand: Scalar

    def __mul__(self, other: object) -> Any:
        if isinstance(other, SymbolicSqrt):
            if other.radicand == self.radicand:
                return self.radicand
            return SymbolicProduct((self, other))
        return SymbolicProduct((self, other))

    def __rmul__(self, other: object) -> Any:
        return self * other

    def __neg__(self) -> SymbolicSqrt:
        return SymbolicSqrt(-self.radicand)


@dataclass(frozen=True, slots=True)
class SymbolicProduct:
    """An immutable product used only when exact radical simplification is unavailable."""

    factors: tuple[Any, ...]

    def __mul__(self, other: object) -> SymbolicProduct:
        return SymbolicProduct((*self.factors, other))

    def __rmul__(self, other: object) -> SymbolicProduct:
        return SymbolicProduct((other, *self.factors))

    def __neg__(self) -> SymbolicProduct:
        return SymbolicProduct((-1, *self.factors))


def _sqrt_abs(value: Scalar) -> Scalar | SymbolicSqrt:
    if isinstance(value, Rational):
        numerator = abs(value.numerator)
        denominator = value.denominator
        root_numerator = isqrt(numerator)
        root_denominator = isqrt(denominator)
        if (
            root_numerator * root_numerator == numerator
            and root_denominator * root_denominator == denominator
        ):
            return Rational(root_numerator, root_denominator)
    return SymbolicSqrt(value)


def _minor_determinant(
    matrix: Sequence[Sequence[Scalar]], rows: tuple[int, ...], columns: tuple[int, ...]
) -> Scalar:
    if not rows:
        return Rational(1)
    return Matrix(
        tuple(tuple(matrix[row][column] for column in columns) for row in rows)
    ).determinant()


@dataclass(frozen=True, slots=True)
class DifferentialForm:
    """An exact differential form with sorted components and optional derivatives."""

    manifold: PseudoRiemannianManifold
    degree: int
    components: tuple[tuple[tuple[int, ...], Any], ...]
    derivative_components: tuple[tuple[tuple[int, tuple[int, ...]], Any], ...]

    def __init__(
        self,
        manifold: PseudoRiemannianManifold,
        degree: int,
        components: Iterable[tuple[Iterable[int], Any]] = (),
        derivatives: Mapping[tuple[int, tuple[int, ...]], Any] | None = None,
    ) -> None:
        if (
            isinstance(degree, bool)
            or not isinstance(degree, int)
            or not 0 <= degree <= manifold.dimension
        ):
            raise ValueError("form degree must lie between zero and the manifold dimension")
        normalized: dict[tuple[int, ...], Any] = {}
        for indices, value in components:
            key = tuple(indices)
            if key != tuple(sorted(key)) or len(key) != degree or len(set(key)) != degree:
                raise ValueError("form indices must be distinct sorted coordinates")
            if any(index < 0 or index >= manifold.dimension for index in key):
                raise ValueError("form index is outside the manifold")
            normalized[key] = normalized.get(key, 0) + value
        derivative_values = tuple(
            sorted(
                ((direction, tuple(indices)), value)
                for (direction, indices), value in (derivatives or {}).items()
            )
        )
        if any(
            direction not in range(manifold.dimension)
            or len(indices) != degree
            or tuple(sorted(indices)) != indices
            for (direction, indices), _ in derivative_values
        ):
            raise ValueError("derivative directions must be manifold coordinates")
        object.__setattr__(self, "manifold", manifold)
        object.__setattr__(self, "degree", degree)
        object.__setattr__(self, "components", tuple(sorted(normalized.items())))
        object.__setattr__(self, "derivative_components", derivative_values)

    @property
    def spacetime(self) -> PseudoRiemannianManifold:
        """Backward-compatible name for the underlying manifold."""

        return self.manifold

    def component(self, indices: Iterable[int]) -> Any:
        """Return one sorted component, or exact zero when absent."""

        key = tuple(indices)
        if key != tuple(sorted(key)):
            raise ValueError("form component lookup requires sorted indices")
        return dict(self.components).get(key, 0)

    def _derivative(self, direction: int, indices: tuple[int, ...]) -> Any:
        return dict(self.derivative_components).get((direction, indices), 0)

    def add(self, other: DifferentialForm) -> DifferentialForm:
        """Add forms of equal degree and convention."""

        if self.manifold != other.manifold or self.degree != other.degree:
            raise IncompatibleConvention("forms must share manifold and degree")
        values: dict[tuple[int, ...], Any] = dict(self.components)
        for key, value in other.components:
            values[key] = values.get(key, 0) + value
        derivatives: dict[tuple[int, tuple[int, ...]], Any] = dict(self.derivative_components)
        for derivative_key, value in other.derivative_components:
            derivatives[derivative_key] = derivatives.get(derivative_key, 0) + value
        return DifferentialForm(self.manifold, self.degree, values.items(), derivatives)

    def scale(self, scalar: Any) -> DifferentialForm:
        """Scale every component without introducing an implicit normalization."""

        return DifferentialForm(
            self.manifold,
            self.degree,
            ((key, scalar * value) for key, value in self.components),
            {key: scalar * value for key, value in self.derivative_components},
        )

    def wedge(self, other: DifferentialForm) -> DifferentialForm:
        """Return the exact graded-antisymmetric wedge product."""

        if self.manifold != other.manifold:
            raise IncompatibleConvention("forms use different manifold conventions")
        if self.degree + other.degree > self.manifold.dimension:
            raise ValueError("the wedge degree exceeds the manifold dimension")
        values: dict[tuple[int, ...], Any] = {}
        for left, left_value in self.components:
            for right, right_value in other.components:
                sign = _concatenated_sign(left, right)
                if sign:
                    key = tuple(sorted((*left, *right)))
                    values[key] = values.get(key, 0) + sign * left_value * right_value
        return DifferentialForm(self.manifold, self.degree + other.degree, values.items())

    def exterior_derivative(self) -> DifferentialForm:
        """Apply the coordinate exterior derivative to explicitly supplied derivatives."""

        if self.degree == self.manifold.dimension:
            return DifferentialForm(self.manifold, self.degree + 0, ())
        values: dict[tuple[int, ...], Any] = {}
        for output in combinations(range(self.manifold.dimension), self.degree + 1):
            total: Any = 0
            for position, direction in enumerate(output):
                source = output[:position] + output[position + 1 :]
                total = total + (-1 if position % 2 else 1) * self._derivative(direction, source)
            if total != 0:
                values[output] = total
        return DifferentialForm(self.manifold, self.degree + 1, values.items())

    d = exterior_derivative

    def interior_product(self, vector: Iterable[Any] | Tensor) -> DifferentialForm:
        """Contract the form with an explicitly supplied contravariant vector."""

        if isinstance(vector, Tensor):
            if vector.rank != 1 or vector.convention != self.manifold.convention:
                raise IncompatibleConvention("interior vector has incompatible index space")
            values = tuple(vector.components)
        else:
            values = tuple(vector)
        if len(values) != self.manifold.dimension:
            raise ValueError("interior vectors must match the manifold dimension")
        if self.degree == 0:
            return DifferentialForm(self.manifold, 0, ())
        output_values: dict[tuple[int, ...], Any] = {}
        for output in combinations(range(self.manifold.dimension), self.degree - 1):
            total: Any = 0
            for direction, coefficient in enumerate(values):
                if direction in output:
                    continue
                position = sum(index < direction for index in output)
                source = tuple(sorted((direction, *output)))
                total = total + (-1 if position % 2 else 1) * coefficient * self.component(source)
            if total != 0:
                output_values[output] = total
        return DifferentialForm(self.manifold, self.degree - 1, output_values.items())

    interior = interior_product

    def hodge_star(self) -> DifferentialForm:
        """Apply the exact Hodge star using the metric and orientation."""

        n = self.manifold.dimension
        target_degree = n - self.degree
        inverse = self.manifold.metric.inverse_components
        volume_factor = _sqrt_abs(self.manifold.metric.determinant)
        orientation_sign = _permutation_sign(self.manifold.convention.orientation.order)
        values: dict[tuple[int, ...], Any] = {}
        for target in combinations(range(n), target_degree):
            complement = tuple(index for index in range(n) if index not in target)
            total: Any = 0
            for source, coefficient in self.components:
                minor = _minor_determinant(inverse, source, complement)
                sign = orientation_sign * _concatenated_sign(complement, target)
                total = total + sign * volume_factor * minor * coefficient
            if total != 0:
                values[target] = total
        return DifferentialForm(self.manifold, target_degree, values.items())

    star = hodge_star

    def codifferential(self) -> DifferentialForm:
        """Apply the metric codifferential with the declared signature convention."""

        if self.degree == 0:
            return DifferentialForm(self.manifold, 0, ())
        sign = (-1) ** (
            self.manifold.dimension * (self.degree + 1)
            + self.manifold.convention.signature.negative_index
        )
        return self.hodge_star().exterior_derivative().hodge_star().scale(sign)

    delta = codifferential

    def laplacian(self) -> DifferentialForm:
        """Return the Hodge-de Rham Laplacian record for explicit derivatives."""

        return (
            self.exterior_derivative()
            .codifferential()
            .add(self.codifferential().exterior_derivative())
        )

    def is_closed(self) -> bool:
        """Return whether the explicit exterior derivative is exactly zero."""

        return not self.exterior_derivative().components

    def hodge_star_squared_sign(self) -> int:
        """Return the exact signature sign predicted for star squared."""

        n = self.manifold.dimension
        exponent = (
            self.degree * (n - self.degree) + self.manifold.convention.signature.negative_index
        )
        return 1 if exponent % 2 == 0 else -1

    def hodge_identity_holds(self) -> bool:
        """Return whether the exact star-square identity holds on this form."""

        expected = self.scale(self.hodge_star_squared_sign())
        return self.hodge_star().hodge_star().components == expected.components

    @classmethod
    def volume(cls, manifold: PseudoRiemannianManifold) -> DifferentialForm:
        """Return the positively oriented coordinate volume form."""

        return cls(manifold, manifold.dimension, ((tuple(range(manifold.dimension)), 1),))


@dataclass(frozen=True, slots=True)
class IntegrationRecord:
    """An orientation-aware exact integration record for top-degree forms."""

    manifold: PseudoRiemannianManifold
    orientation: Orientation
    provenance: str

    def __post_init__(self) -> None:
        if self.orientation != self.manifold.convention.orientation:
            raise IncompatibleConvention(
                "integration orientation differs from manifold orientation"
            )
        if not self.provenance.strip():
            raise ValueError("integration records require provenance")

    def integrate(self, form: DifferentialForm) -> Any:
        """Integrate a top form over the declared oriented coordinate chart."""

        if form.manifold != self.manifold:
            raise IncompatibleConvention("form and integration manifold differ")
        if form.degree != self.manifold.dimension:
            raise ValueError("only top-degree forms can be integrated")
        canonical = tuple(sorted(self.orientation.order))
        return _permutation_sign(self.orientation.order) * form.component(canonical)


@dataclass(frozen=True, slots=True)
class Connection:
    """A symbolic affine connection with explicit coefficients and torsion metadata."""

    manifold: PseudoRiemannianManifold
    coefficients: tuple[Any, ...]
    torsion_free: bool
    metric_compatible: bool


@dataclass(frozen=True, slots=True)
class LeviCivitaConnection(Connection):
    """The torsion-free metric-compatible connection associated with a metric."""

    def __init__(
        self, manifold: PseudoRiemannianManifold, coefficients: Iterable[Any] = ()
    ) -> None:
        object.__setattr__(self, "manifold", manifold)
        object.__setattr__(self, "coefficients", tuple(coefficients))
        object.__setattr__(self, "torsion_free", True)
        object.__setattr__(self, "metric_compatible", True)


@dataclass(frozen=True, slots=True)
class TorsionfulConnection(Connection):
    """A metric-compatible connection with an explicitly named torsion form."""

    torsion: DifferentialForm
    name: str

    def __init__(
        self,
        manifold: PseudoRiemannianManifold,
        torsion: DifferentialForm,
        name: str = "∇+",
        coefficients: Iterable[Any] = (),
    ) -> None:
        if torsion.manifold != manifold or torsion.degree != 3:
            raise IncompatibleConvention("torsion must be a three-form on the connection manifold")
        if not name.strip():
            raise ValueError("torsionful connections require a name")
        object.__setattr__(self, "manifold", manifold)
        object.__setattr__(self, "coefficients", tuple(coefficients))
        object.__setattr__(self, "torsion_free", False)
        object.__setattr__(self, "metric_compatible", True)
        object.__setattr__(self, "torsion", torsion)
        object.__setattr__(self, "name", name)


@dataclass(frozen=True, slots=True)
class CurvatureTwoForm:
    """A matrix-valued curvature two-form with one fixed connection."""

    connection: Connection
    components: tuple[tuple[int, int, Any], ...]

    def __init__(self, connection: Connection, components: Iterable[tuple[int, int, Any]]) -> None:
        values = tuple(components)
        n = connection.manifold.dimension
        if any(
            left == right or not 0 <= left < n or not 0 <= right < n for left, right, _ in values
        ):
            raise ValueError("curvature indices must be distinct manifold directions")
        if any((right, left, value) in values for left, right, value in values):
            raise ValueError("curvature components must use one orientation")
        object.__setattr__(self, "connection", connection)
        object.__setattr__(self, "components", values)

    def form(self, component: Any) -> DifferentialForm:
        """Return one selected matrix component as an ordinary two-form."""

        return DifferentialForm(
            self.connection.manifold,
            2,
            (
                ((left, right), value)
                for left, right, value in self.components
                if value == component
            ),
        )


def exterior_derivative(form: DifferentialForm) -> DifferentialForm:
    """Functional alias for :meth:`DifferentialForm.exterior_derivative`."""

    return form.exterior_derivative()


def hodge_star(form: DifferentialForm) -> DifferentialForm:
    """Functional alias for :meth:`DifferentialForm.hodge_star`."""

    return form.hodge_star()


def wedge(left: DifferentialForm, right: DifferentialForm) -> DifferentialForm:
    """Functional alias for the exact wedge product."""

    return left.wedge(right)


__all__ = [
    "Connection",
    "CurvatureTwoForm",
    "DifferentialForm",
    "IndexSpace",
    "IndexVariance",
    "IntegrationRecord",
    "LeviCivitaConnection",
    "LorentzianSpacetime",
    "Metric",
    "MetricSignature",
    "Manifold",
    "Orientation",
    "PseudoRiemannianManifold",
    "PseudoRiemannianSignature",
    "SpacetimeConvention",
    "SymbolicProduct",
    "SymbolicSqrt",
    "Tensor",
    "TensorBundle",
    "TorsionfulConnection",
    "exterior_derivative",
    "hodge_star",
    "wedge",
]
