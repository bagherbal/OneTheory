"""Exact four-dimensional Lorentzian spacetime primitives.

Owns:
    Dimensions, metric signatures, index variance, immutable tensors, contractions,
    metric raising and lowering, orientations, volume forms, and differential-form
    wedge products under explicit conventions.

Depends on:
    Core errors and exact linear algebra; it is independent of Standard Model and
    Schoen data.

Must not:
    Select a compactification from observations, insert a numerical gravitational
    scale, encode sacred geometry as physics, or bridge unrelated theories.

Phase 0:
    The reusable four-dimensional geometric law vocabulary is implemented; curvature
    dynamics are represented in `gravity.py`.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from itertools import product
from typing import Any

from onetheory.core.errors import IncompatibleConvention
from onetheory.math.linear import Matrix


class IndexVariance(StrEnum):
    """Variance of a tensor index."""

    COVARIANT = "covariant"
    CONTRAVARIANT = "contravariant"


@dataclass(frozen=True, slots=True)
class MetricSignature:
    """An explicit diagonal Lorentzian signature."""

    signs: tuple[int, ...]

    def __init__(self, signs: Iterable[int] = (1, -1, -1, -1)) -> None:
        values = tuple(signs)
        if len(values) != 4 or any(value not in (-1, 1) for value in values):
            raise ValueError("four-dimensional signatures require four signs ±1")
        if values.count(1) == 0 or values.count(-1) == 0:
            raise ValueError("a Lorentzian signature requires both signs")
        object.__setattr__(self, "signs", values)

    @property
    def dimension(self) -> int:
        return len(self.signs)


@dataclass(frozen=True, slots=True)
class Orientation:
    """A positively oriented ordered coordinate frame."""

    order: tuple[int, ...]

    def __init__(self, order: Iterable[int] = (0, 1, 2, 3)) -> None:
        values = tuple(order)
        if tuple(sorted(values)) != tuple(range(len(values))):
            raise ValueError("orientation must be a permutation of 0 through n-1")
        if len(values) != 4:
            raise ValueError("the initial spacetime orientation is four-dimensional")
        object.__setattr__(self, "order", values)


@dataclass(frozen=True, slots=True)
class SpacetimeConvention:
    """The signature and orientation that make tensor operations comparable."""

    signature: MetricSignature
    orientation: Orientation

    @classmethod
    def lorentzian(cls, signature: MetricSignature | None = None) -> SpacetimeConvention:
        return cls(signature or MetricSignature(), Orientation())


@dataclass(frozen=True, slots=True)
class IndexSpace:
    """A finite index space with declared dimension, variance, and convention."""

    name: str
    dimension: int
    variance: IndexVariance
    convention: SpacetimeConvention

    def __post_init__(self) -> None:
        if not self.name.strip() or self.dimension != self.convention.signature.dimension:
            raise ValueError("index spaces must match the four-dimensional convention")


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


def _unflatten(value: int, shape: Sequence[int]) -> tuple[int, ...]:
    result = [0] * len(shape)
    for position in range(len(shape) - 1, -1, -1):
        value, result[position] = divmod(value, shape[position])
    return tuple(result)


def _sum(values: Iterable[Any]) -> Any:
    result: Any = 0
    for value in values:
        result = result + value
    return result


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
        return len(self.index_spaces)

    @property
    def convention(self) -> SpacetimeConvention | None:
        return self.index_spaces[0].convention if self.index_spaces else None

    def component(self, indices: Sequence[int] = ()) -> Any:
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
        components = []
        for output in product(*(range(size) for size in shape)) if shape else [()]:
            total = _sum(
                self.component(
                    tuple(
                        output[
                            sum(
                                1
                                for position in range(axis)
                                if position not in (left_axis, right_axis)
                            )
                        ]
                        if axis not in (left_axis, right_axis)
                        else repeated
                        for axis in range(self.rank)
                    )
                )
                for repeated in range(left.dimension)
            )
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
    """A nondegenerate four-dimensional metric in one explicit convention."""

    convention: SpacetimeConvention
    components: tuple[tuple[Any, ...], ...]

    def __init__(
        self,
        convention: SpacetimeConvention | None = None,
        components: Iterable[Iterable[Any]] | None = None,
    ) -> None:
        chosen = convention or SpacetimeConvention.lorentzian()
        rows = (
            tuple(row)
            for row in (
                components
                if components is not None
                else (
                    (sign if row == column else 0 for column in range(4))
                    for row, sign in enumerate(chosen.signature.signs)
                )
            )
        )
        values = tuple(rows)
        if len(values) != 4 or any(len(row) != 4 for row in values):
            raise ValueError("four-dimensional metrics require a 4 by 4 matrix")
        matrix = Matrix(values)
        if matrix.determinant().is_zero():
            raise ValueError("the spacetime metric must be nondegenerate")
        if any(
            values[row][column] != values[column][row] for row in range(4) for column in range(4)
        ):
            raise ValueError("the spacetime metric must be symmetric")
        object.__setattr__(self, "convention", chosen)
        object.__setattr__(self, "components", values)

    @property
    def inverse_components(self) -> tuple[tuple[Any, ...], ...]:
        return self._matrix().inverse().rows

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
class LorentzianSpacetime:
    """A four-dimensional Lorentzian manifold convention with a supplied metric."""

    convention: SpacetimeConvention
    metric: Metric

    def __init__(
        self, convention: SpacetimeConvention | None = None, metric: Metric | None = None
    ) -> None:
        chosen = convention or SpacetimeConvention.lorentzian()
        selected_metric = metric or Metric(chosen)
        if selected_metric.convention != chosen:
            raise IncompatibleConvention("spacetime and metric conventions differ")
        object.__setattr__(self, "convention", chosen)
        object.__setattr__(self, "metric", selected_metric)

    @property
    def dimension(self) -> int:
        return self.convention.signature.dimension


def _permutation_sign(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    sequence = left + right
    if len(set(sequence)) != len(sequence):
        return 0
    inversions = sum(
        sequence[i] > sequence[j] for i in range(len(sequence)) for j in range(i + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


@dataclass(frozen=True, slots=True)
class DifferentialForm:
    """An exact coordinate differential form with sorted component indices."""

    spacetime: LorentzianSpacetime
    degree: int
    components: tuple[tuple[tuple[int, ...], Any], ...]

    def __init__(
        self,
        spacetime: LorentzianSpacetime,
        degree: int,
        components: Iterable[tuple[Iterable[int], Any]] = (),
    ) -> None:
        if isinstance(degree, bool) or not isinstance(degree, int) or not 0 <= degree <= 4:
            raise ValueError("form degrees must lie between zero and four")
        normalized: dict[tuple[int, ...], Any] = {}
        for indices, value in components:
            key = tuple(indices)
            if key != tuple(sorted(key)) or len(key) != degree or len(set(key)) != degree:
                raise ValueError("form indices must be distinct sorted coordinates")
            if any(index < 0 or index >= spacetime.dimension for index in key):
                raise ValueError("form index is outside spacetime")
            normalized[key] = normalized.get(key, 0) + value
        object.__setattr__(self, "spacetime", spacetime)
        object.__setattr__(self, "degree", degree)
        object.__setattr__(self, "components", tuple(sorted(normalized.items())))

    def component(self, indices: Iterable[int]) -> Any:
        key = tuple(indices)
        if key != tuple(sorted(key)):
            raise ValueError("form component lookup requires sorted indices")
        return dict(self.components).get(key, 0)

    def wedge(self, other: DifferentialForm) -> DifferentialForm:
        """Return the exact graded-antisymmetric wedge product."""

        if self.spacetime != other.spacetime:
            raise IncompatibleConvention("forms use different spacetime conventions")
        if self.degree + other.degree > 4:
            raise ValueError("the wedge degree exceeds four-dimensional spacetime")
        values: dict[tuple[int, ...], Any] = {}
        for left, left_value in self.components:
            for right, right_value in other.components:
                sign = _permutation_sign(left, right)
                if sign:
                    key = tuple(sorted(left + right))
                    values[key] = values.get(key, 0) + sign * left_value * right_value
        return DifferentialForm(self.spacetime, self.degree + other.degree, values.items())

    @classmethod
    def volume(cls, spacetime: LorentzianSpacetime) -> DifferentialForm:
        """Return the positively oriented coordinate volume form."""

        return cls(spacetime, 4, (((0, 1, 2, 3), 1),))


__all__ = [
    "DifferentialForm",
    "IndexSpace",
    "IndexVariance",
    "LorentzianSpacetime",
    "Metric",
    "MetricSignature",
    "Orientation",
    "SpacetimeConvention",
    "Tensor",
]
