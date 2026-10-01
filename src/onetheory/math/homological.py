"""Exact basis-aware homological algebra and transfer machinery.

Owns:
    Finite-dimensional graded vector spaces, typed exact linear maps, chain and
    cochain complexes, graded products and DGAs, DGA modules, commutators,
    cyclic pairings, Maurer--Cartan residuals, contractions, suspended planar
    homological perturbation transfer, and finite-group equivariant complexes.

Depends on:
    `onetheory.math.numbers` for exact scalars, `onetheory.math.linear` for
    deterministic rank, RREF, and nullspace calculations, and
    `onetheory.core.errors` for fail-closed missing-input signals.

Must not:
    Implement sheaves, Čech covers, physical bundle data, numerical geometry, or
    any speculative bridge between models. Synthetic transfer inputs are generic
    mathematical fixtures and are not physical carrier evidence.

Phase 0:
    Exact generic homological and transfer implementation is provided; physical
    applications remain outside this reusable module until independently derived.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from itertools import product
from typing import Any, cast

from onetheory.core.errors import MissingPhysicalInput
from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein, Rational, coerce_rational

Scalar = Rational | Eisenstein
type ScalarType = type[Rational] | type[Eisenstein]


def _coerce(value: object, scalar_type: ScalarType) -> Scalar:
    if scalar_type is Rational:
        return coerce_rational(value)
    if scalar_type is Eisenstein:
        return Eisenstein.coerce(value)
    raise TypeError("scalar_type must be Rational or Eisenstein")


def _zero(scalar_type: ScalarType) -> Scalar:
    return _coerce(0, scalar_type)


def _one(scalar_type: ScalarType) -> Scalar:
    return _coerce(1, scalar_type)


def _add(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) + right)


def _subtract(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) - right)


def _multiply(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) * right)


def _negate(value: Scalar) -> Scalar:
    return cast(Scalar, -cast(Any, value))


def _inverse(value: Scalar, scalar_type: ScalarType) -> Scalar:
    """Return one exact inverse in the declared scalar field."""

    return cast(Scalar, cast(Any, _one(scalar_type)) / value)


def _require_same_scalar(left: ScalarType, right: ScalarType) -> None:
    if left is not right:
        raise TypeError("exact linear objects must use the same scalar type")


def _rank_of_vectors(vectors: Sequence[CoordinateVector], space: VectorSpace) -> int:
    for vector in vectors:
        if vector.space != space:
            raise ValueError("vectors must belong to the declared ambient space")
    if not vectors or space.dimension == 0:
        return 0
    rows = tuple(
        tuple(vector.coordinates[index] for vector in vectors)
        for index in range(space.dimension)
    )
    return Matrix(rows, scalar_type=space.scalar_type).rank()


@dataclass(frozen=True, slots=True, init=False)
class VectorSpace:
    """A finite-dimensional exact vector space with a named ordered basis."""

    name: str
    basis: tuple[str, ...]
    scalar_type: ScalarType

    def __init__(
        self,
        name: str,
        basis: Iterable[str],
        scalar_type: ScalarType = Rational,
    ) -> None:
        if not name:
            raise ValueError("a vector-space name is required")
        labels = tuple(basis)
        if any(not isinstance(label, str) or not label for label in labels):
            raise TypeError("basis labels must be nonempty strings")
        if len(set(labels)) != len(labels):
            raise ValueError("basis labels must be unique")
        if scalar_type not in (Rational, Eisenstein):
            raise TypeError("scalar_type must be Rational or Eisenstein")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "basis", labels)
        object.__setattr__(self, "scalar_type", scalar_type)

    @property
    def dimension(self) -> int:
        """Return the dimension in the declared basis."""

        return len(self.basis)

    def direct_sum(self, other: VectorSpace, name: str | None = None) -> VectorSpace:
        """Return the ordered direct sum of two compatible spaces."""

        _require_same_scalar(self.scalar_type, other.scalar_type)
        prefix = f"{self.name}⊕{other.name}" if name is None else name
        labels = tuple(f"left:{self.name}:{label}" for label in self.basis) + tuple(
            f"right:{other.name}:{label}" for label in other.basis
        )
        return VectorSpace(prefix, labels, self.scalar_type)


@dataclass(frozen=True, slots=True, init=False)
class GradedVectorSpace:
    """An immutable integer-graded family of explicitly based vector spaces."""

    name: str
    components: tuple[tuple[int, VectorSpace], ...]

    def __init__(
        self,
        name: str,
        components: Mapping[int, VectorSpace] | Iterable[tuple[int, VectorSpace]],
    ) -> None:
        if not name:
            raise ValueError("a graded-space name is required")
        pairs = tuple(components.items()) if isinstance(components, Mapping) else tuple(components)
        if len({degree for degree, _ in pairs}) != len(pairs):
            raise ValueError("graded degrees must be unique")
        if any(not isinstance(degree, int) or isinstance(degree, bool) for degree, _ in pairs):
            raise TypeError("graded degrees must be integers")
        if any(not isinstance(space, VectorSpace) for _, space in pairs):
            raise TypeError("graded components must be VectorSpace instances")
        ordered = tuple(sorted(pairs, key=lambda pair: pair[0]))
        scalar_types = {space.scalar_type for _, space in ordered}
        if len(scalar_types) > 1:
            raise TypeError("all graded components must use one scalar type")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "components", ordered)

    @property
    def degrees(self) -> tuple[int, ...]:
        """Return the explicitly represented degrees in ascending order."""

        return tuple(degree for degree, _ in self.components)

    @property
    def scalar_type(self) -> ScalarType:
        """Return the common scalar type, defaulting to Rational when empty."""

        return self.components[0][1].scalar_type if self.components else Rational

    def space(self, degree: int) -> VectorSpace:
        """Return a component, or its canonical zero-dimensional component."""

        for component_degree, space in self.components:
            if component_degree == degree:
                return space
        return VectorSpace(f"{self.name}[{degree}]", (), self.scalar_type)

    def shift(self, amount: int, name: str | None = None) -> GradedVectorSpace:
        """Shift every component to degree ``degree + amount``."""

        if isinstance(amount, bool) or not isinstance(amount, int):
            raise TypeError("the shift amount must be an integer")
        shifted = {degree + amount: space for degree, space in self.components}
        return GradedVectorSpace(name or f"{self.name}[{amount}]", shifted)

    def direct_sum(self, other: GradedVectorSpace, name: str | None = None) -> GradedVectorSpace:
        """Take the degreewise direct sum with another graded space."""

        degrees = sorted(set(self.degrees) | set(other.degrees))
        components = {
            degree: self.space(degree).direct_sum(other.space(degree)) for degree in degrees
        }
        return GradedVectorSpace(name or f"{self.name}⊕{other.name}", components)


@dataclass(frozen=True, slots=True)
class CoordinateVector:
    """An exact coordinate vector whose basis is carried by its ambient space."""

    space: VectorSpace
    coordinates: tuple[Scalar, ...]

    def __post_init__(self) -> None:
        if len(self.coordinates) != self.space.dimension:
            raise ValueError("coordinate length does not match the vector-space basis")
        coerced = tuple(_coerce(value, self.space.scalar_type) for value in self.coordinates)
        object.__setattr__(self, "coordinates", coerced)

    def __add__(self, other: CoordinateVector) -> CoordinateVector:
        if self.space != other.space:
            raise ValueError("vectors require identical named bases")
        return CoordinateVector(
            self.space,
            tuple(_add(left, right) for left, right in zip(
                self.coordinates, other.coordinates, strict=True
            )),
        )

    def __sub__(self, other: CoordinateVector) -> CoordinateVector:
        if self.space != other.space:
            raise ValueError("vectors require identical named bases")
        return CoordinateVector(
            self.space,
            tuple(_subtract(left, right) for left, right in zip(
                self.coordinates, other.coordinates, strict=True
            )),
        )

    def scale(self, scalar: object) -> CoordinateVector:
        """Multiply the coordinates by one exact scalar in the basis."""

        factor = _coerce(scalar, self.space.scalar_type)
        return CoordinateVector(
            self.space,
            tuple(_multiply(factor, value) for value in self.coordinates),
        )

    def is_zero(self) -> bool:
        """Return whether every coordinate vanishes exactly."""

        return all(value.is_zero() for value in self.coordinates)


@dataclass(frozen=True, slots=True, init=False)
class LinearMap:
    """An exact matrix map between two explicitly based vector spaces."""

    domain: VectorSpace
    codomain: VectorSpace
    rows: tuple[tuple[Scalar, ...], ...]

    def __init__(
        self,
        domain: VectorSpace,
        codomain: VectorSpace,
        rows: Iterable[Iterable[object]],
    ) -> None:
        _require_same_scalar(domain.scalar_type, codomain.scalar_type)
        materialized = tuple(
            tuple(_coerce(value, domain.scalar_type) for value in row) for row in rows
        )
        if len(materialized) != codomain.dimension:
            raise ValueError("map row count must equal the codomain dimension")
        if any(len(row) != domain.dimension for row in materialized):
            raise ValueError("map column count must equal the domain dimension")
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "codomain", codomain)
        object.__setattr__(self, "rows", materialized)

    @classmethod
    def zero(cls, domain: VectorSpace, codomain: VectorSpace) -> LinearMap:
        """Construct the typed zero map, including zero-dimensional spaces."""

        _require_same_scalar(domain.scalar_type, codomain.scalar_type)
        zero = _zero(domain.scalar_type)
        return cls(
            domain,
            codomain,
            (tuple(zero for _ in range(domain.dimension))
             for _ in range(codomain.dimension)),
        )

    @classmethod
    def identity(cls, space: VectorSpace) -> LinearMap:
        """Construct the identity map in the declared basis."""

        rows = tuple(
            tuple(_one(space.scalar_type) if row == col else _zero(space.scalar_type)
                  for col in range(space.dimension))
            for row in range(space.dimension)
        )
        return cls(space, space, rows)

    @classmethod
    def block(cls, blocks: Sequence[Sequence[LinearMap]]) -> LinearMap:
        """Assemble a typed block matrix from complete zero or nonzero blocks."""

        if not blocks or not blocks[0] or any(len(row) != len(blocks[0]) for row in blocks):
            raise ValueError("a block matrix must be nonempty and rectangular")
        column_domains = tuple(blocks[0][column].domain for column in range(len(blocks[0])))
        row_codomains = tuple(blocks[row][0].codomain for row in range(len(blocks)))
        scalar_type = column_domains[0].scalar_type
        for row_index, row in enumerate(blocks):
            for column_index, block in enumerate(row):
                if block.domain != column_domains[column_index]:
                    raise ValueError("block domains are incompatible")
                if block.codomain != row_codomains[row_index]:
                    raise ValueError("block codomains are incompatible")
                _require_same_scalar(scalar_type, block.domain.scalar_type)
        rows: list[tuple[Scalar, ...]] = []
        for block_row, codomain in zip(blocks, row_codomains, strict=True):
            for local_row in range(codomain.dimension):
                rows.append(tuple(value for block in block_row for value in block.rows[local_row]))
        domain = column_domains[0]
        for component in column_domains[1:]:
            domain = domain.direct_sum(component)
        codomain = row_codomains[0]
        for component in row_codomains[1:]:
            codomain = codomain.direct_sum(component)
        return cls(domain, codomain, rows)

    def __call__(self, vector: CoordinateVector) -> CoordinateVector:
        if vector.space != self.domain:
            raise ValueError("the vector basis does not match the map domain")
        values = tuple(
            sum((_multiply(entry, value) for entry, value in zip(
                    row, vector.coordinates, strict=True
                )),
                _zero(self.domain.scalar_type))
            for row in self.rows
        )
        return CoordinateVector(self.codomain, values)

    def compose(self, previous: LinearMap) -> LinearMap:
        """Compose this map after ``previous``."""

        if previous.codomain != self.domain:
            raise ValueError("map composition requires matching named spaces")
        rows = tuple(
            tuple(
                sum(
                    (
                        _multiply(self.rows[row][inner], previous.rows[inner][column])
                        for inner in range(self.domain.dimension)
                        if not self.rows[row][inner].is_zero()
                        and not previous.rows[inner][column].is_zero()
                    ),
                    _zero(self.domain.scalar_type),
                )
                for column in range(previous.domain.dimension)
            )
            for row in range(self.codomain.dimension)
        )
        if previous.domain.dimension == 0:
            rows = tuple(tuple() for _ in range(self.codomain.dimension))
        elif self.domain.dimension == 0:
            rows = tuple(tuple(_zero(self.domain.scalar_type)
                               for _ in range(previous.domain.dimension))
                         for _ in range(self.codomain.dimension))
        return LinearMap(previous.domain, self.codomain, rows)

    def __add__(self, other: LinearMap) -> LinearMap:
        self._require_same_shape(other)
        rows = tuple(
            tuple(_add(left, right) for left, right in zip(left_row, right_row, strict=True))
            for left_row, right_row in zip(self.rows, other.rows, strict=True)
        )
        return LinearMap(self.domain, self.codomain, rows)

    def __sub__(self, other: LinearMap) -> LinearMap:
        self._require_same_shape(other)
        rows = tuple(
            tuple(_subtract(left, right) for left, right in zip(left_row, right_row, strict=True))
            for left_row, right_row in zip(self.rows, other.rows, strict=True)
        )
        return LinearMap(self.domain, self.codomain, rows)

    def scale(self, scalar: object) -> LinearMap:
        factor = _coerce(scalar, self.domain.scalar_type)
        return LinearMap(
            self.domain,
            self.codomain,
            tuple(tuple(_multiply(factor, value) for value in row) for row in self.rows),
        )

    def __neg__(self) -> LinearMap:
        return self.scale(-1)

    def is_zero(self) -> bool:
        """Return whether every matrix entry is exactly zero."""

        return all(value.is_zero() for row in self.rows for value in row)

    def rank(self) -> int:
        """Return the exact matrix rank."""

        if self.domain.dimension == 0 or self.codomain.dimension == 0:
            return 0
        return Matrix(self.rows, scalar_type=self.domain.scalar_type).rank()

    def kernel_basis(self) -> tuple[CoordinateVector, ...]:
        """Return a deterministic exact basis for the kernel."""

        if self.domain.dimension == 0:
            return ()
        if self.codomain.dimension == 0:
            return tuple(
                CoordinateVector(
                    self.domain,
                    tuple(_one(self.domain.scalar_type) if index == position
                          else _zero(self.domain.scalar_type)
                          for index in range(self.domain.dimension)),
                )
                for position in range(self.domain.dimension)
            )
        vectors = Matrix(self.rows, scalar_type=self.domain.scalar_type).nullspace()
        return tuple(CoordinateVector(self.domain, vector.values) for vector in vectors)

    def image_basis(self) -> tuple[CoordinateVector, ...]:
        """Return image vectors associated with pivot columns."""

        if self.domain.dimension == 0 or self.codomain.dimension == 0:
            return ()
        matrix = Matrix(self.rows, scalar_type=self.domain.scalar_type)
        _, pivots = matrix.rref()
        return tuple(
            CoordinateVector(self.codomain, tuple(self.rows[row][column]
                                                   for row in range(self.codomain.dimension)))
            for column in pivots
        )

    def _require_same_shape(self, other: LinearMap) -> None:
        if self.domain != other.domain or self.codomain != other.codomain:
            raise ValueError("linear map operations require identical typed spaces")

    @classmethod
    def direct_sum(cls, left: LinearMap, right: LinearMap) -> LinearMap:
        """Construct the block-diagonal direct sum of two maps."""

        return cls.block(
            (
                (
                    left,
                    cls.zero(right.domain, left.codomain),
                ),
                (
                    cls.zero(left.domain, right.codomain),
                    right,
                ),
            )
        )


def _complex_data(
    spaces: GradedVectorSpace,
    differentials: Mapping[int, LinearMap] | Iterable[tuple[int, LinearMap]],
    direction: str,
) -> tuple[tuple[tuple[int, LinearMap], ...], tuple[int, ...]]:
    if direction not in ("chain", "cochain"):
        raise ValueError("complex direction must be chain or cochain")
    pairs = (tuple(differentials.items()) if isinstance(differentials, Mapping)
             else tuple(differentials))
    if len({degree for degree, _ in pairs}) != len(pairs):
        raise ValueError("differential source degrees must be unique")
    step = -1 if direction == "chain" else 1
    for degree, differential in pairs:
        if differential.domain != spaces.space(degree):
            raise ValueError("a differential domain does not match its graded component")
        if differential.codomain != spaces.space(degree + step):
            raise ValueError("a differential codomain does not match its graded component")
    ordered = tuple(sorted(pairs, key=lambda pair: pair[0]))
    degrees = tuple(sorted(set(spaces.degrees) | {degree for degree, _ in ordered}))
    return ordered, degrees


class _ComplexMixin:
    _direction: str
    _spaces: GradedVectorSpace
    _differentials: tuple[tuple[int, LinearMap], ...]
    _degrees: tuple[int, ...]

    @property
    def spaces(self) -> GradedVectorSpace:
        return self._spaces

    @property
    def degrees(self) -> tuple[int, ...]:
        return self._degrees

    @property
    def direction(self) -> str:
        return self._direction

    def differential(self, degree: int) -> LinearMap:
        """Return the typed differential, including an implicit zero at an edge."""

        for source_degree, differential in self._differentials:
            if source_degree == degree:
                return differential
        step = -1 if self._direction == "chain" else 1
        return LinearMap.zero(self.spaces.space(degree), self.spaces.space(degree + step))

    @property
    def differentials(self) -> tuple[tuple[int, LinearMap], ...]:
        """Return explicitly supplied differentials in degree order."""

        return self._differentials

    def _validate_squared_zero(self) -> None:
        step = -1 if self._direction == "chain" else 1
        for degree in self.degrees:
            composite = self.differential(degree + step).compose(self.differential(degree))
            if not composite.is_zero():
                raise ValueError("complex differentials must satisfy d squared equals zero")

    def cycles(self, degree: int) -> tuple[CoordinateVector, ...]:
        """Return an exact basis of cycles in the requested degree."""

        return self.differential(degree).kernel_basis()

    def boundaries(self, degree: int) -> tuple[CoordinateVector, ...]:
        """Return an exact basis of boundaries in the requested degree."""

        source_degree = degree + 1 if self._direction == "chain" else degree - 1
        return self.differential(source_degree).image_basis()

    def cohomology_dimension(self, degree: int) -> int:
        """Return the dimension of homology or cohomology at a degree."""

        cycles = self.cycles(degree)
        boundaries = self.boundaries(degree)
        return len(cycles) - _rank_of_vectors(boundaries, self.spaces.space(degree))

    def cohomology_representatives(self, degree: int) -> tuple[CoordinateVector, ...]:
        """Return cycle representatives extending the boundary span."""

        space = self.spaces.space(degree)
        boundaries = self.boundaries(degree)
        cycles = self.cycles(degree)
        if not cycles:
            return ()
        columns = (*boundaries, *cycles)
        matrix = Matrix(
            tuple(
                tuple(vector.coordinates[column] for vector in columns)
                for column in range(space.dimension)
            ),
            scalar_type=space.scalar_type,
        )
        _, pivots = matrix.rref()
        boundary_count = len(boundaries)
        return tuple(
            cycles[pivot - boundary_count]
            for pivot in pivots
            if pivot >= boundary_count
        )

    def shift(self, amount: int) -> ChainComplex | CochainComplex:
        """Shift degrees by ``amount`` and apply the standard parity sign."""

        if isinstance(amount, bool) or not isinstance(amount, int):
            raise TypeError("the shift amount must be an integer")
        shifted_spaces = self.spaces.shift(amount)
        factor = -1 if amount % 2 else 1
        step = -1 if self._direction == "chain" else 1
        shifted_differentials = {}
        for degree, differential in self.differentials:
            shifted_degree = degree + amount
            if degree not in self.spaces.degrees or degree + step not in self.spaces.degrees:
                # Absent components acquire the shifted complex's canonical
                # zero-space names, unlike explicitly represented components.
                shifted_differentials[shifted_degree] = LinearMap.zero(
                    shifted_spaces.space(shifted_degree),
                    shifted_spaces.space(shifted_degree + step),
                )
            else:
                shifted_differentials[shifted_degree] = differential.scale(factor)
        if self._direction == "chain":
            return ChainComplex(shifted_spaces, shifted_differentials)
        return CochainComplex(shifted_spaces, shifted_differentials)

    def direct_sum(self, other: ChainComplex | CochainComplex) -> ChainComplex | CochainComplex:
        """Take the degreewise direct sum of two complexes of one direction."""

        if self._direction != other.direction:
            raise ValueError("chain and cochain complexes cannot be directly summed")
        spaces = self.spaces.direct_sum(other.spaces)
        degrees = sorted(
            {degree for degree, _ in self.differentials}
            | {degree for degree, _ in other.differentials}
        )
        step = -1 if self._direction == "chain" else 1
        differentials = {}
        for degree in degrees:
            if degree not in spaces.degrees or degree + step not in spaces.degrees:
                # An absent summand is the zero space of the assembled complex,
                # not the differently named direct sum of its two edge spaces.
                differentials[degree] = LinearMap.zero(
                    spaces.space(degree), spaces.space(degree + step)
                )
            else:
                differentials[degree] = LinearMap.direct_sum(
                    self.differential(degree), other.differential(degree)
                )
        if self._direction == "chain":
            return ChainComplex(spaces, differentials)
        return CochainComplex(spaces, differentials)


@dataclass(frozen=True, slots=True, init=False)
class ChainComplex(_ComplexMixin):
    """A finite exact chain complex with maps lowering integer degree."""

    _spaces: GradedVectorSpace
    _differentials: tuple[tuple[int, LinearMap], ...]
    _degrees: tuple[int, ...]
    _direction = "chain"

    def __init__(
        self,
        spaces: GradedVectorSpace,
        differentials: Mapping[int, LinearMap] | Iterable[tuple[int, LinearMap]],
    ) -> None:
        ordered, degrees = _complex_data(spaces, differentials, "chain")
        object.__setattr__(self, "_spaces", spaces)
        object.__setattr__(self, "_differentials", ordered)
        object.__setattr__(self, "_degrees", degrees)
        self._validate_squared_zero()


@dataclass(frozen=True, slots=True, init=False)
class CochainComplex(_ComplexMixin):
    """A finite exact cochain complex with maps raising integer degree."""

    _spaces: GradedVectorSpace
    _differentials: tuple[tuple[int, LinearMap], ...]
    _degrees: tuple[int, ...]
    _direction = "cochain"

    def __init__(
        self,
        spaces: GradedVectorSpace,
        differentials: Mapping[int, LinearMap] | Iterable[tuple[int, LinearMap]],
    ) -> None:
        ordered, degrees = _complex_data(spaces, differentials, "cochain")
        object.__setattr__(self, "_spaces", spaces)
        object.__setattr__(self, "_differentials", ordered)
        object.__setattr__(self, "_degrees", degrees)
        self._validate_squared_zero()


@dataclass(frozen=True, slots=True, init=False)
class ChainMap:
    """A typed degree-preserving map commuting exactly with differentials."""

    source: ChainComplex | CochainComplex
    target: ChainComplex | CochainComplex
    components: tuple[tuple[int, LinearMap], ...]

    def __init__(
        self,
        source: ChainComplex | CochainComplex,
        target: ChainComplex | CochainComplex,
        components: Mapping[int, LinearMap] | Iterable[tuple[int, LinearMap]],
    ) -> None:
        if source.direction != target.direction:
            raise ValueError("chain maps require complexes of one direction")
        pairs = tuple(components.items()) if isinstance(components, Mapping) else tuple(components)
        if len({degree for degree, _ in pairs}) != len(pairs):
            raise ValueError("map component degrees must be unique")
        for degree, component in pairs:
            if component.domain != source.spaces.space(degree):
                raise ValueError("chain-map component has the wrong domain")
            if component.codomain != target.spaces.space(degree):
                raise ValueError("chain-map component has the wrong codomain")
        ordered = tuple(sorted(pairs, key=lambda pair: pair[0]))
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "components", ordered)
        for degree in self.degrees:
            left = target.differential(degree).compose(self.component(degree))
            right = self.component(self._step(degree)).compose(source.differential(degree))
            if (left - right).is_zero() is False:
                raise ValueError("map components must commute with the differentials")

    @property
    def degrees(self) -> tuple[int, ...]:
        return tuple(sorted(set(self.source.degrees) | set(self.target.degrees) |
                            {degree for degree, _ in self.components}))

    def _step(self, degree: int) -> int:
        return degree - 1 if self.source.direction == "chain" else degree + 1

    def component(self, degree: int) -> LinearMap:
        """Return the typed component, using zero outside supplied degrees."""

        for component_degree, component in self.components:
            if component_degree == degree:
                return component
        return LinearMap.zero(self.source.spaces.space(degree), self.target.spaces.space(degree))

    @classmethod
    def identity(cls, complex_: ChainComplex | CochainComplex) -> ChainMap:
        """Construct the identity map of a complex."""

        return cls(complex_, complex_, {
            degree: LinearMap.identity(complex_.spaces.space(degree))
            for degree in complex_.degrees
        })

    def compose(self, previous: ChainMap) -> ChainMap:
        """Compose this map after ``previous``."""

        if previous.target != self.source:
            raise ValueError("chain-map composition requires matching complexes")
        degrees = sorted(set(previous.degrees) | set(self.degrees))
        return ChainMap(
            previous.source,
            self.target,
            {degree: self.component(degree).compose(previous.component(degree))
             for degree in degrees},
        )


@dataclass(frozen=True, slots=True, init=False)
class ChainHomotopy:
    """An exact chain or cochain homotopy between two typed maps."""

    first: ChainMap
    second: ChainMap
    components: tuple[tuple[int, LinearMap], ...]

    def __init__(
        self,
        first: ChainMap,
        second: ChainMap,
        components: Mapping[int, LinearMap] | Iterable[tuple[int, LinearMap]],
    ) -> None:
        if first.source != second.source or first.target != second.target:
            raise ValueError("homotopies require maps with identical source and target")
        pairs = tuple(components.items()) if isinstance(components, Mapping) else tuple(components)
        if len({degree for degree, _ in pairs}) != len(pairs):
            raise ValueError("homotopy component degrees must be unique")
        for degree, component in pairs:
            if component.domain != first.source.spaces.space(degree):
                raise ValueError("homotopy component has the wrong domain")
            target_degree = degree + 1 if first.source.direction == "chain" else degree - 1
            if component.codomain != first.target.spaces.space(target_degree):
                raise ValueError("homotopy component has the wrong shifted codomain")
        ordered = tuple(sorted(pairs, key=lambda pair: pair[0]))
        object.__setattr__(self, "first", first)
        object.__setattr__(self, "second", second)
        object.__setattr__(self, "components", ordered)
        for degree in self.degrees:
            left = self.first.component(degree) - self.second.component(degree)
            if first.source.direction == "chain":
                right = first.target.differential(degree + 1).compose(self.component(degree))
                right = right + self.component(degree - 1).compose(
                    first.source.differential(degree)
                )
            else:
                right = first.target.differential(degree - 1).compose(self.component(degree))
                right = right + self.component(degree + 1).compose(
                    first.source.differential(degree)
                )
            if not (left - right).is_zero():
                raise ValueError("homotopy components do not satisfy the homotopy equation")

    @property
    def degrees(self) -> tuple[int, ...]:
        return tuple(sorted(set(self.first.degrees) | set(self.second.degrees) |
                            {degree for degree, _ in self.components}))

    def component(self, degree: int) -> LinearMap:
        """Return the typed shifted component, including implicit zero maps."""

        for component_degree, component in self.components:
            if component_degree == degree:
                return component
        target_degree = degree + 1 if self.first.source.direction == "chain" else degree - 1
        return LinearMap.zero(self.first.source.spaces.space(degree),
                              self.first.target.spaces.space(target_degree))


def mapping_cone(map_: ChainMap) -> ChainComplex | CochainComplex:
    """Construct the signed mapping cone of a chain or cochain map."""

    source = map_.source
    target = map_.target
    if source.direction == "chain":
        degrees = sorted(set(target.degrees) | set(source.degrees) |
                         {degree + 1 for degree in source.degrees})
        spaces = GradedVectorSpace(
            "Cone",
            {degree: target.spaces.space(degree).direct_sum(source.spaces.space(degree - 1))
             for degree in degrees},
        )
        differentials = {}
        for degree in degrees:
            if not spaces.space(degree - 1).dimension:
                differentials[degree] = LinearMap.zero(
                    spaces.space(degree), spaces.space(degree - 1)
                )
                continue
            top_left = target.differential(degree)
            top_right = map_.component(degree - 1)
            bottom_left = LinearMap.zero(target.spaces.space(degree),
                                         source.spaces.space(degree - 2))
            bottom_right = -source.differential(degree - 1)
            differentials[degree] = LinearMap.block(
                ((top_left, top_right), (bottom_left, bottom_right))
            )
        return ChainComplex(spaces, differentials)
    degrees = sorted(set(target.degrees) | set(source.degrees) |
                     {degree - 1 for degree in source.degrees})
    spaces = GradedVectorSpace(
        "Cone",
        {degree: target.spaces.space(degree).direct_sum(source.spaces.space(degree + 1))
         for degree in degrees},
    )
    differentials = {}
    for degree in degrees:
        if not spaces.space(degree + 1).dimension:
            differentials[degree] = LinearMap.zero(
                spaces.space(degree), spaces.space(degree + 1)
            )
            continue
        top_left = target.differential(degree)
        top_right = map_.component(degree + 1)
        bottom_left = LinearMap.zero(target.spaces.space(degree),
                                     source.spaces.space(degree + 2))
        bottom_right = -source.differential(degree + 1)
        differentials[degree] = LinearMap.block(
            ((top_left, top_right), (bottom_left, bottom_right))
        )
    return CochainComplex(spaces, differentials)


@dataclass(frozen=True, slots=True, init=False)
class Bicomplex:
    """A finite basis-aware bicomplex with commuting unsigned directions."""

    name: str
    components: tuple[tuple[tuple[int, int], VectorSpace], ...]
    horizontal: tuple[tuple[tuple[int, int], LinearMap], ...]
    vertical: tuple[tuple[tuple[int, int], LinearMap], ...]

    def __init__(
        self,
        name: str,
        components: Mapping[tuple[int, int], VectorSpace] |
        Iterable[tuple[tuple[int, int], VectorSpace]],
        horizontal: Mapping[tuple[int, int], LinearMap] |
        Iterable[tuple[tuple[int, int], LinearMap]] = (),
        vertical: Mapping[tuple[int, int], LinearMap] |
        Iterable[tuple[tuple[int, int], LinearMap]] = (),
    ) -> None:
        component_pairs = (tuple(components.items()) if isinstance(components, Mapping)
                           else tuple(components))
        if len({cell for cell, _ in component_pairs}) != len(component_pairs):
            raise ValueError("bicomplex cells must be unique")
        if any(len(cell) != 2 for cell, _ in component_pairs):
            raise ValueError("bicomplex cells require (horizontal, vertical) degrees")
        scalar_types = {space.scalar_type for _, space in component_pairs}
        if len(scalar_types) > 1:
            raise TypeError("all bicomplex components must use one scalar type")
        horizontal_pairs = (tuple(horizontal.items()) if isinstance(horizontal, Mapping)
                            else tuple(horizontal))
        vertical_pairs = (tuple(vertical.items()) if isinstance(vertical, Mapping)
                          else tuple(vertical))
        if len({cell for cell, _ in horizontal_pairs}) != len(horizontal_pairs):
            raise ValueError("horizontal source cells must be unique")
        if len({cell for cell, _ in vertical_pairs}) != len(vertical_pairs):
            raise ValueError("vertical source cells must be unique")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "components", tuple(sorted(component_pairs)))
        object.__setattr__(self, "horizontal", tuple(sorted(horizontal_pairs)))
        object.__setattr__(self, "vertical", tuple(sorted(vertical_pairs)))
        self._validate_maps()

    @property
    def scalar_type(self) -> ScalarType:
        """Return the common coefficient type."""

        return self.components[0][1].scalar_type if self.components else Rational

    def space(self, cell: tuple[int, int]) -> VectorSpace:
        """Return a cell space or the canonical zero space at an absent cell."""

        for component_cell, space in self.components:
            if component_cell == cell:
                return space
        return VectorSpace(f"{self.name}{cell}", (), self.scalar_type)

    def _map(self, maps: tuple[tuple[tuple[int, int], LinearMap], ...],
             cell: tuple[int, int], target: tuple[int, int]) -> LinearMap:
        for source_cell, map_ in maps:
            if source_cell == cell:
                return map_
        return LinearMap.zero(self.space(cell), self.space(target))

    def _cells(self) -> tuple[tuple[int, int], ...]:
        cells = {cell for cell, _ in self.components}
        cells.update(cell for cell, _ in self.horizontal)
        cells.update(cell for cell, _ in self.vertical)
        return tuple(sorted(cells))

    def _validate_maps(self) -> None:
        for cell, map_ in self.horizontal:
            target = (cell[0] + 1, cell[1])
            if map_.domain != self.space(cell) or map_.codomain != self.space(target):
                raise ValueError("horizontal map has incompatible cell bases")
        for cell, map_ in self.vertical:
            target = (cell[0], cell[1] + 1)
            if map_.domain != self.space(cell) or map_.codomain != self.space(target):
                raise ValueError("vertical map has incompatible cell bases")
        for p, q in self._cells():
            horizontal_square = self._map(self.horizontal, (p + 1, q), (p + 2, q)).compose(
                self._map(self.horizontal, (p, q), (p + 1, q))
            )
            vertical_square = self._map(self.vertical, (p, q + 1), (p, q + 2)).compose(
                self._map(self.vertical, (p, q), (p, q + 1))
            )
            if not horizontal_square.is_zero() or not vertical_square.is_zero():
                raise ValueError("bicomplex directional squares must vanish")
            hv = self._map(self.vertical, (p + 1, q), (p + 1, q + 1)).compose(
                self._map(self.horizontal, (p, q), (p + 1, q))
            )
            vh = self._map(self.horizontal, (p, q + 1), (p + 1, q + 1)).compose(
                self._map(self.vertical, (p, q), (p, q + 1))
            )
            if not (hv - vh).is_zero():
                raise ValueError("unsigned bicomplex directions must commute")

    def totalize(self) -> CochainComplex:
        """Form the cochain total complex with sign ``(-1)^p`` on vertical maps."""

        degree_cells: dict[int, tuple[tuple[int, int], ...]] = {}
        for cell in self._cells():
            degree_cells.setdefault(sum(cell), tuple())
            degree_cells[sum(cell)] = tuple(sorted((*degree_cells[sum(cell)], cell)))
        spaces = GradedVectorSpace(
            f"Tot({self.name})",
            {degree: self._direct_sum_spaces(cells, degree)
             for degree, cells in degree_cells.items()},
        )
        differentials: dict[int, LinearMap] = {}
        for degree, source_cells in degree_cells.items():
            target_cells = degree_cells.get(degree + 1, ())
            if not target_cells:
                differentials[degree] = LinearMap.zero(
                    spaces.space(degree), spaces.space(degree + 1)
                )
                continue
            blocks: list[list[LinearMap]] = []
            for target_cell in target_cells:
                block_row = []
                for source_cell in source_cells:
                    if target_cell == (source_cell[0] + 1, source_cell[1]):
                        block = self._map(self.horizontal, source_cell, target_cell)
                    elif target_cell == (source_cell[0], source_cell[1] + 1):
                        block = self._map(self.vertical, source_cell, target_cell).scale(
                            -1 if source_cell[0] % 2 else 1
                        )
                    else:
                        block = LinearMap.zero(self.space(source_cell), self.space(target_cell))
                    block_row.append(block)
                blocks.append(block_row)
            differentials[degree] = LinearMap.block(blocks)
        return CochainComplex(spaces, differentials)

    def _direct_sum_spaces(self, cells: Sequence[tuple[int, int]], degree: int) -> VectorSpace:
        if not cells:
            return VectorSpace(f"Tot({self.name})[{degree}]", (), self.scalar_type)
        result = self.space(cells[0])
        for cell in cells[1:]:
            result = result.direct_sum(self.space(cell))
        return result


# The following objects extend the finite-complex foundation with the generic
# algebraic structures needed by exact deformation calculations.  They are
# deliberately independent of the Schoen carrier.


def _basis_vector(space: VectorSpace, index: int) -> CoordinateVector:
    """Return one exact standard basis vector in a named space."""

    if index < 0 or index >= space.dimension:
        raise IndexError(index)
    values = tuple(
        _one(space.scalar_type) if position == index else _zero(space.scalar_type)
        for position in range(space.dimension)
    )
    return CoordinateVector(space, values)


def _tensor_space(left: VectorSpace, right: VectorSpace, name: str | None = None) -> VectorSpace:
    """Construct the ordered tensor-product coordinate space."""

    _require_same_scalar(left.scalar_type, right.scalar_type)
    labels = tuple(
        f"{left.name}:{left.basis[i]}⊗{right.name}:{right.basis[j]}"
        for i in range(left.dimension)
        for j in range(right.dimension)
    )
    return VectorSpace(name or f"{left.name}⊗{right.name}", labels, left.scalar_type)


def tensor_product_space(
    left: VectorSpace,
    right: VectorSpace,
    name: str | None = None,
) -> VectorSpace:
    """Return the public exact tensor-product basis used by graded products."""

    return _tensor_space(left, right, name)


def _tensor_vector(left: CoordinateVector, right: CoordinateVector) -> CoordinateVector:
    """Flatten two coordinate vectors in left-major tensor order."""

    return CoordinateVector(
        _tensor_space(left.space, right.space),
        tuple(
            _multiply(left_value, right_value)
            for left_value in left.coordinates
            for right_value in right.coordinates
        ),
    )


def _sum_vectors(vectors: Sequence[CoordinateVector]) -> CoordinateVector:
    """Add nonempty vectors in one exact named basis."""

    if not vectors:
        raise ValueError("at least one vector is required")
    result = vectors[0]
    for vector in vectors[1:]:
        result = result + vector
    return result


@dataclass(frozen=True, slots=True)
class GradedElement:
    """A homogeneous exact vector together with its declared degree."""

    degree: int
    vector: CoordinateVector

    def __post_init__(self) -> None:
        if isinstance(self.degree, bool) or not isinstance(self.degree, int):
            raise TypeError("graded degrees must be integers")

    def scale(self, scalar: object) -> GradedElement:
        """Scale the homogeneous element in its exact coefficient field."""

        return GradedElement(self.degree, self.vector.scale(scalar))

    def __add__(self, other: GradedElement) -> GradedElement:
        if self.degree != other.degree:
            raise ValueError("graded elements must have the same degree")
        return GradedElement(self.degree, self.vector + other.vector)

    def __neg__(self) -> GradedElement:
        return self.scale(-1)


@dataclass(frozen=True, slots=True, init=False)
class GradedMap:
    """A typed homogeneous map of a fixed integer degree."""

    source: GradedVectorSpace
    target: GradedVectorSpace
    degree: int
    components: tuple[tuple[int, LinearMap], ...]

    def __init__(
        self,
        source: GradedVectorSpace,
        target: GradedVectorSpace,
        degree: int,
        components: Mapping[int, LinearMap] | Iterable[tuple[int, LinearMap]],
    ) -> None:
        if isinstance(degree, bool) or not isinstance(degree, int):
            raise TypeError("graded-map degree must be an integer")
        pairs = tuple(components.items()) if isinstance(components, Mapping) else tuple(components)
        if len({item[0] for item in pairs}) != len(pairs):
            raise ValueError("graded-map source degrees must be unique")
        for source_degree, component in pairs:
            if component.domain != source.space(source_degree):
                raise ValueError("graded-map component has the wrong domain")
            if component.codomain != target.space(source_degree + degree):
                raise ValueError("graded-map component has the wrong codomain")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "degree", degree)
        object.__setattr__(self, "components", tuple(sorted(pairs)))

    @property
    def source_degrees(self) -> tuple[int, ...]:
        """Return all degrees that can contribute nontrivially."""

        return tuple(sorted(set(self.source.degrees) | {degree for degree, _ in self.components}))

    def component(self, degree: int) -> LinearMap:
        """Return a component, using a typed zero map when absent."""

        for source_degree, component in self.components:
            if source_degree == degree:
                return component
        return LinearMap.zero(self.source.space(degree), self.target.space(degree + self.degree))

    def __call__(self, element: GradedElement) -> GradedElement:
        """Apply the typed graded map to one homogeneous element."""

        if element.vector.space != self.source.space(element.degree):
            raise ValueError("graded element does not belong to the map source")
        component = self.component(element.degree)
        return GradedElement(element.degree + self.degree, component(element.vector))

    def compose(self, previous: GradedMap) -> GradedMap:
        """Compose this graded map after another homogeneous map."""

        if previous.target != self.source:
            raise ValueError("graded-map composition requires matching spaces")
        degrees = sorted(
            set(previous.source_degrees) | {degree for degree, _ in previous.components}
        )
        return GradedMap(
            previous.source,
            self.target,
            previous.degree + self.degree,
            {
                degree: self.component(degree + previous.degree).compose(
                    previous.component(degree)
                )
                for degree in degrees
            },
        )

    @classmethod
    def zero(cls, source: GradedVectorSpace, target: GradedVectorSpace, degree: int) -> GradedMap:
        """Construct the typed zero map of a declared degree."""

        return cls(
            source,
            target,
            degree,
            {
                source_degree: LinearMap.zero(
                    source.space(source_degree), target.space(source_degree + degree)
                )
                for source_degree in source.degrees
            },
        )

    @classmethod
    def identity(cls, space: GradedVectorSpace) -> GradedMap:
        """Construct the degree-zero identity graded map."""

        return cls(
            space,
            space,
            0,
            {degree: LinearMap.identity(space.space(degree)) for degree in space.degrees},
        )

    def is_zero(self) -> bool:
        """Return whether every explicit component is exactly zero."""

        return all(component.is_zero() for _, component in self.components)


GradedLinearMap = GradedMap


@dataclass(frozen=True, slots=True, init=False)
class GradedProduct:
    """A bilinear product with explicitly typed degreewise components."""

    space: GradedVectorSpace
    components: tuple[tuple[tuple[int, int], LinearMap], ...]
    name: str

    def __init__(
        self,
        space: GradedVectorSpace,
        components: Mapping[tuple[int, int], LinearMap] |
        Iterable[tuple[tuple[int, int], LinearMap]],
        name: str = "product",
    ) -> None:
        pairs = tuple(components.items()) if isinstance(components, Mapping) else tuple(components)
        if len({degree for degree, _ in pairs}) != len(pairs):
            raise ValueError("graded-product components must have unique degree pairs")
        for (left_degree, right_degree), component in pairs:
            expected_domain = _tensor_space(
                space.space(left_degree), space.space(right_degree)
            )
            if component.domain != expected_domain:
                raise ValueError("graded-product component has the wrong tensor basis")
            if component.codomain != space.space(left_degree + right_degree):
                raise ValueError("graded-product component has the wrong output basis")
        if not name.strip():
            raise ValueError("graded products require a name")
        object.__setattr__(self, "space", space)
        object.__setattr__(self, "components", tuple(sorted(pairs)))
        object.__setattr__(self, "name", name)

    def component(self, left_degree: int, right_degree: int) -> LinearMap:
        """Return one typed product component, including an implicit zero."""

        for degrees, component in self.components:
            if degrees == (left_degree, right_degree):
                return component
        return LinearMap.zero(
            _tensor_space(self.space.space(left_degree), self.space.space(right_degree)),
            self.space.space(left_degree + right_degree),
        )

    def multiply(self, left: GradedElement, right: GradedElement) -> GradedElement:
        """Multiply two homogeneous elements in the declared bases."""

        if left.vector.space != self.space.space(left.degree):
            raise ValueError("left graded element has the wrong product basis")
        if right.vector.space != self.space.space(right.degree):
            raise ValueError("right graded element has the wrong product basis")
        tensor = _tensor_vector(left.vector, right.vector)
        return GradedElement(
            left.degree + right.degree,
            self.component(left.degree, right.degree)(tensor),
        )

    __call__ = multiply

    def is_associative(self, degrees: Iterable[int] | None = None) -> bool:
        """Check associativity on every basis triple in the selected degrees."""

        selected = tuple(self.space.degrees if degrees is None else degrees)
        for left_degree, middle_degree, right_degree in product(selected, repeat=3):
            left_space = self.space.space(left_degree)
            middle_space = self.space.space(middle_degree)
            right_space = self.space.space(right_degree)
            for i, j, k in product(
                range(left_space.dimension),
                range(middle_space.dimension),
                range(right_space.dimension),
            ):
                left = GradedElement(left_degree, _basis_vector(left_space, i))
                middle = GradedElement(middle_degree, _basis_vector(middle_space, j))
                right = GradedElement(right_degree, _basis_vector(right_space, k))
                if self.multiply(self.multiply(left, middle), right) != self.multiply(
                    left, self.multiply(middle, right)
                ):
                    return False
        return True


@dataclass(frozen=True, slots=True, init=False)
class DGA:
    """A finite exact differential graded algebra over one scalar field."""

    space: GradedVectorSpace
    differential_map: GradedMap
    product: GradedProduct
    name: str

    def __init__(
        self,
        space: GradedVectorSpace,
        differential: GradedMap,
        product: GradedProduct,
        name: str = "DGA",
    ) -> None:
        if differential.source != space or differential.target != space or differential.degree != 1:
            raise ValueError("a DGA differential must be a degree-one endomap")
        if product.space != space:
            raise ValueError("a DGA product must use the DGA graded space")
        object.__setattr__(self, "space", space)
        object.__setattr__(self, "differential_map", differential)
        object.__setattr__(self, "product", product)
        object.__setattr__(self, "name", name)
        self._validate_squared_zero()
        if not product.is_associative():
            raise ValueError("DGA product must be associative")
        self._validate_leibniz()

    def differential(self, element: GradedElement) -> GradedElement:
        """Apply the exact degree-one differential."""

        return self.differential_map(element)

    def multiply(self, left: GradedElement, right: GradedElement) -> GradedElement:
        """Apply the associative graded product."""

        return self.product(left, right)

    def _validate_squared_zero(self) -> None:
        for degree in self.differential_map.source_degrees:
            composite = self.differential_map.component(degree + 1).compose(
                self.differential_map.component(degree)
            )
            if not composite.is_zero():
                raise ValueError("DGA differential must satisfy D squared equals zero")

    def _validate_leibniz(self) -> None:
        for left_degree, right_degree in product(self.space.degrees, repeat=2):
            left_space = self.space.space(left_degree)
            right_space = self.space.space(right_degree)
            for i, j in product(range(left_space.dimension), range(right_space.dimension)):
                left = GradedElement(left_degree, _basis_vector(left_space, i))
                right = GradedElement(right_degree, _basis_vector(right_space, j))
                lhs = self.differential(self.multiply(left, right))
                rhs = self.multiply(self.differential(left), right) + self.multiply(
                    left, self.differential(right)
                ).scale(-1 if left_degree % 2 else 1)
                if lhs != rhs:
                    raise ValueError("DGA differential must satisfy the graded Leibniz rule")

    def residual(
        self,
        phi: Mapping[int, CoordinateVector] | Sequence[GradedElement],
    ) -> tuple[GradedElement, ...]:
        """Evaluate ``D phi + phi²`` without hiding nonzero terms."""

        terms = _normalize_expression(self.space, phi)
        residual: dict[int, GradedElement] = {}
        for term in terms:
            image = self.differential(term)
            residual[image.degree] = _add_term(residual.get(image.degree), image)
        for left in terms:
            for right in terms:
                image = self.multiply(left, right)
                residual[image.degree] = _add_term(residual.get(image.degree), image)
        return tuple(
            residual[degree]
            for degree in sorted(residual)
            if not residual[degree].vector.is_zero()
        )

    def is_maurer_cartan(
        self,
        phi: Mapping[int, CoordinateVector] | Sequence[GradedElement],
    ) -> bool:
        """Return whether the exact Maurer--Cartan residual vanishes."""

        return not self.residual(phi)


def _add_term(previous: GradedElement | None, value: GradedElement) -> GradedElement:
    """Add one homogeneous term to an expression accumulator."""

    return value if previous is None else previous + value


def _normalize_expression(
    space: GradedVectorSpace,
    expression: Mapping[int, CoordinateVector] | Sequence[GradedElement],
) -> tuple[GradedElement, ...]:
    """Normalize an inhomogeneous exact expression to ordered terms."""

    terms = (
        tuple(GradedElement(degree, vector) for degree, vector in expression.items())
        if isinstance(expression, Mapping)
        else tuple(expression)
    )
    if len({term.degree for term in terms}) != len(terms):
        raise ValueError("inhomogeneous expressions require one term per degree")
    for term in terms:
        if term.vector.space != space.space(term.degree):
            raise ValueError("expression term has the wrong graded basis")
    return tuple(sorted(terms, key=lambda term: term.degree))


@dataclass(frozen=True, slots=True, init=False)
class GradedAction:
    """A typed left or right DGA action on a graded module."""

    algebra: DGA
    module_space: GradedVectorSpace
    side: str
    components: tuple[tuple[tuple[int, int], LinearMap], ...]

    def __init__(
        self,
        algebra: DGA,
        module_space: GradedVectorSpace,
        side: str,
        components: Mapping[tuple[int, int], LinearMap] |
        Iterable[tuple[tuple[int, int], LinearMap]],
    ) -> None:
        if side not in {"left", "right"}:
            raise ValueError("DGA actions must be left or right")
        pairs = tuple(components.items()) if isinstance(components, Mapping) else tuple(components)
        for (algebra_degree, module_degree), component in pairs:
            if side == "left":
                expected_domain = _tensor_space(
                    algebra.space.space(algebra_degree), module_space.space(module_degree)
                )
            else:
                expected_domain = _tensor_space(
                    module_space.space(module_degree), algebra.space.space(algebra_degree)
                )
            if component.domain != expected_domain:
                raise ValueError("DGA action component has the wrong tensor basis")
            if component.codomain != module_space.space(algebra_degree + module_degree):
                raise ValueError("DGA action component has the wrong output basis")
        object.__setattr__(self, "algebra", algebra)
        object.__setattr__(self, "module_space", module_space)
        object.__setattr__(self, "side", side)
        object.__setattr__(self, "components", tuple(sorted(pairs)))

    def component(self, algebra_degree: int, module_degree: int) -> LinearMap:
        """Return one action component, with a typed zero default."""

        for degrees, component in self.components:
            if degrees == (algebra_degree, module_degree):
                return component
        if self.side == "left":
            domain = _tensor_space(
                self.algebra.space.space(algebra_degree), self.module_space.space(module_degree)
            )
        else:
            domain = _tensor_space(
                self.module_space.space(module_degree), self.algebra.space.space(algebra_degree)
            )
        return LinearMap.zero(domain, self.module_space.space(algebra_degree + module_degree))

    def apply(self, algebra_element: GradedElement, module_element: GradedElement) -> GradedElement:
        """Apply the action in its declared left or right order."""

        if algebra_element.vector.space != self.algebra.space.space(algebra_element.degree):
            raise ValueError("algebra element has the wrong action basis")
        if module_element.vector.space != self.module_space.space(module_element.degree):
            raise ValueError("module element has the wrong action basis")
        if self.side == "left":
            tensor = _tensor_vector(algebra_element.vector, module_element.vector)
        else:
            tensor = _tensor_vector(module_element.vector, algebra_element.vector)
        return GradedElement(
            algebra_element.degree + module_element.degree,
            self.component(algebra_element.degree, module_element.degree)(tensor),
        )


@dataclass(frozen=True, slots=True, init=False)
class DGAModule:
    """A left or right differential graded module with exact Leibniz checks."""

    algebra: DGA
    space: GradedVectorSpace
    differential_map: GradedMap
    action: GradedAction
    name: str

    def __init__(
        self,
        algebra: DGA,
        space: GradedVectorSpace,
        differential: GradedMap,
        action: GradedAction,
        name: str = "DGA module",
    ) -> None:
        if differential.source != space or differential.target != space or differential.degree != 1:
            raise ValueError("module differential must be a degree-one endomap")
        if action.algebra != algebra or action.module_space != space:
            raise ValueError("module action does not match the algebra and module")
        object.__setattr__(self, "algebra", algebra)
        object.__setattr__(self, "space", space)
        object.__setattr__(self, "differential_map", differential)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "name", name)
        for degree in differential.source_degrees:
            composite = differential.component(degree + 1).compose(
                differential.component(degree)
            )
            if not composite.is_zero():
                raise ValueError("module differential must satisfy D squared equals zero")
        self._validate_leibniz()

    def differential(self, element: GradedElement) -> GradedElement:
        """Apply the exact module differential."""

        return self.differential_map(element)

    def _validate_leibniz(self) -> None:
        for algebra_degree, module_degree in product(
            self.algebra.space.degrees, self.space.degrees
        ):
            algebra_space = self.algebra.space.space(algebra_degree)
            module_space = self.space.space(module_degree)
            for i, j in product(range(algebra_space.dimension), range(module_space.dimension)):
                algebra_element = GradedElement(algebra_degree, _basis_vector(algebra_space, i))
                module_element = GradedElement(module_degree, _basis_vector(module_space, j))
                lhs = self.differential(self.action.apply(algebra_element, module_element))
                if self.action.side == "left":
                    first = self.action.apply(
                        self.algebra.differential(algebra_element), module_element
                    )
                    second = self.action.apply(algebra_element, self.differential(module_element))
                    rhs = first + second.scale(-1 if algebra_degree % 2 else 1)
                else:
                    first = self.action.apply(algebra_element, self.differential(module_element))
                    second = self.action.apply(
                        self.algebra.differential(algebra_element), module_element
                    )
                    rhs = first.scale(-1 if module_degree % 2 else 1) + second
                if lhs != rhs:
                    raise ValueError("DGA module action must satisfy the graded Leibniz rule")


def graded_commutator(
    product_: GradedProduct,
    left: GradedElement,
    right: GradedElement,
) -> GradedElement:
    """Return ``left*right - (-1)^(|left||right|) right*left``."""

    first = product_(left, right)
    second = product_(right, left).scale(
        1 if (left.degree * right.degree) % 2 == 0 else -1
    )
    return first + second.scale(-1)


@dataclass(frozen=True, slots=True, init=False)
class CyclicPairing:
    """A trace functional inducing an exact cyclic pairing on a DGA."""

    dga: DGA
    trace_vectors: tuple[tuple[int, tuple[Scalar, ...]], ...]
    normalized: bool

    def __init__(
        self,
        dga: DGA,
        trace_vectors: Mapping[int, Sequence[object]],
        *,
        normalized: bool = False,
    ) -> None:
        values: list[tuple[int, tuple[Scalar, ...]]] = []
        for degree, raw in trace_vectors.items():
            space = dga.space.space(degree)
            vector = tuple(_coerce(value, space.scalar_type) for value in raw)
            if len(vector) != space.dimension:
                raise ValueError("trace vector length does not match its graded basis")
            values.append((degree, vector))
        object.__setattr__(self, "dga", dga)
        object.__setattr__(self, "trace_vectors", tuple(sorted(values)))
        object.__setattr__(self, "normalized", normalized)

    def trace(self, element: GradedElement) -> Scalar:
        """Evaluate the declared trace vector on one homogeneous element."""

        vector = dict(self.trace_vectors).get(element.degree)
        if vector is None:
            return _zero(element.vector.space.scalar_type)
        if element.vector.space != self.dga.space.space(element.degree):
            raise ValueError("trace element has the wrong DGA basis")
        return sum(
            (_multiply(left, right) for left, right in zip(
                vector, element.vector.coordinates, strict=True
            )),
            _zero(element.vector.space.scalar_type),
        )

    def pair(self, left: GradedElement, right: GradedElement) -> Scalar:
        """Evaluate the induced bilinear pairing ``trace(left*right)``."""

        return self.trace(self.dga.multiply(left, right))

    def is_cyclic(self) -> bool:
        """Check graded cyclicity on every basis triple."""

        for p, q, r in product(self.dga.space.degrees, repeat=3):
            spaces = (self.dga.space.space(p), self.dga.space.space(q), self.dga.space.space(r))
            for i, j, k in product(*(range(space.dimension) for space in spaces)):
                a = GradedElement(p, _basis_vector(spaces[0], i))
                b = GradedElement(q, _basis_vector(spaces[1], j))
                c = GradedElement(r, _basis_vector(spaces[2], k))
                lhs = self.pair(self.dga.multiply(a, b), c)
                sign = -1 if (p * (q + r)) % 2 else 1
                rhs = self.pair(self.dga.multiply(b, c), a)
                expected = rhs if sign == 1 else _negate(rhs)
                if lhs != expected:
                    return False
        return True

    def is_nondegenerate(self) -> bool:
        """Check nondegeneracy degree-by-degree for all complementary pairs."""

        for left_degree in self.dga.space.degrees:
            left = self.dga.space.space(left_degree)
            for right_degree in self.dga.space.degrees:
                right = self.dga.space.space(right_degree)
                rows = tuple(
                    tuple(
                        self.pair(
                            GradedElement(left_degree, _basis_vector(left, i)),
                            GradedElement(right_degree, _basis_vector(right, j)),
                        )
                        for j in range(right.dimension)
                    )
                    for i in range(left.dimension)
                )
                if rows and right.dimension:
                    pairing_matrix = Matrix(rows, scalar_type=left.scalar_type)
                    if (
                        not pairing_matrix.is_zero()
                        and pairing_matrix.rank() < min(left.dimension, right.dimension)
                    ):
                        return False
        return True

    def normalize(self, degree: int, basis_index: int = 0, target: object = 1) -> CyclicPairing:
        """Scale the trace so one declared basis trace equals ``target``."""

        space = self.dga.space.space(degree)
        if basis_index < 0 or basis_index >= space.dimension:
            raise IndexError(basis_index)
        value = self.trace(GradedElement(degree, _basis_vector(space, basis_index)))
        if value.is_zero():
            raise ValueError("cannot normalize a zero trace value")
        factor = cast(Scalar, cast(Any, _coerce(target, space.scalar_type)) / value)
        scaled = {
            trace_degree: tuple(_multiply(factor, entry) for entry in vector)
            for trace_degree, vector in self.trace_vectors
        }
        return CyclicPairing(self.dga, scaled, normalized=True)


def maurer_cartan_residual(
    dga: DGA,
    phi: Mapping[int, CoordinateVector] | Sequence[GradedElement],
) -> tuple[GradedElement, ...]:
    """Evaluate an exact Maurer--Cartan residual through the DGA contract."""

    return dga.residual(phi)


@dataclass(frozen=True, slots=True, init=False)
class Contraction:
    """A complete contraction from a large complex onto a smaller one."""

    source: ChainComplex | CochainComplex
    target: ChainComplex | CochainComplex
    inclusion: ChainMap
    projection: ChainMap
    homotopy: ChainHomotopy

    def __init__(
        self,
        source: ChainComplex | CochainComplex,
        target: ChainComplex | CochainComplex,
        inclusion: ChainMap | None = None,
        projection: ChainMap | None = None,
        homotopy: ChainHomotopy | None = None,
    ) -> None:
        if inclusion is None:
            raise MissingPhysicalInput("contraction inclusion", ("complete contraction package",))
        if projection is None:
            raise MissingPhysicalInput("contraction projection", ("complete contraction package",))
        if homotopy is None:
            raise MissingPhysicalInput("contracting homotopy", ("complete contraction package",))
        if inclusion.source != target or inclusion.target != source:
            raise ValueError("contraction inclusion must map target into source")
        if projection.source != source or projection.target != target:
            raise ValueError("contraction projection must map source onto target")
        if homotopy.first.source != source or homotopy.first.target != source:
            raise ValueError("contracting homotopy must be an endomorphism homotopy")
        identity = ChainMap.identity(source)
        composed = inclusion.compose(projection)
        if homotopy.first != identity or homotopy.second != composed:
            raise ValueError("homotopy must witness identity minus inclusion-projection")
        if projection.compose(inclusion) != ChainMap.identity(target):
            raise ValueError("contraction must satisfy projection after inclusion equals identity")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "inclusion", inclusion)
        object.__setattr__(self, "projection", projection)
        object.__setattr__(self, "homotopy", homotopy)
        self.validate_side_conditions()

    @property
    def direction(self) -> str:
        """Return the chain or cochain direction."""

        return self.source.direction

    def _homotopy_target_degree(self, degree: int) -> int:
        return degree + 1 if self.direction == "chain" else degree - 1

    def validate_side_conditions(self) -> bool:
        """Validate ``ph=0``, ``hi=0``, and ``h²=0`` exactly."""

        for degree in self.source.degrees:
            h = self.homotopy.component(degree)
            target_degree = self._homotopy_target_degree(degree)
            if not self.projection.component(target_degree).compose(h).is_zero():
                raise ValueError("contraction side condition p h = 0 failed")
            if not h.compose(self.inclusion.component(degree)).is_zero():
                raise ValueError("contraction side condition h i = 0 failed")
            next_h = self.homotopy.component(target_degree)
            if not next_h.compose(h).is_zero():
                raise ValueError("contraction side condition h squared = 0 failed")
        return True


ContractionRecord = Contraction


@dataclass(frozen=True, slots=True)
class TransferWord:
    """One exact transferred word and its memoization counts."""

    arity: int
    result: GradedElement
    source_value: GradedElement
    f_word_count: int
    b_word_count: int


@dataclass(frozen=True, slots=True)
class HPLTransfer:
    """Suspended planar homological perturbation transfer for a complete contraction."""

    contraction: Contraction
    product: GradedProduct

    def __post_init__(self) -> None:
        if self.product.space != self.contraction.source.spaces:
            raise ValueError("HPL product must be defined on the contracted source")

    def evaluate(self, inputs: Sequence[GradedElement]) -> TransferWord:
        """Evaluate one transferred word by exact memoized planar recursion."""

        if not inputs:
            raise ValueError("a transfer word requires at least one input")
        target_space = self.contraction.target.spaces
        for element in inputs:
            if element.vector.space != target_space.space(element.degree):
                raise ValueError("HPL input does not belong to the retract basis")
        f_cache: dict[tuple[GradedElement, ...], GradedElement] = {}
        b_cache: dict[tuple[GradedElement, ...], GradedElement] = {}

        def f_word(word: tuple[GradedElement, ...]) -> GradedElement:
            if word in f_cache:
                return f_cache[word]
            if len(word) == 1:
                item = word[0]
                image = self.contraction.inclusion.component(item.degree)(item.vector)
                result = GradedElement(item.degree, image)
            else:
                result = b_word(word)
                h = self.contraction.homotopy.component(result.degree)
                result = GradedElement(
                    self.contraction._homotopy_target_degree(result.degree),
                    h(result.vector).scale(-1),
                )
            f_cache[word] = result
            return result

        def b_word(word: tuple[GradedElement, ...]) -> GradedElement:
            if len(word) < 2:
                raise ValueError("the suspended HPL B word requires at least two inputs")
            if word in b_cache:
                return b_cache[word]
            pieces = [
                self.product.multiply(
                    f_word(word[:split]),
                    f_word(word[split:]),
                )
                for split in range(1, len(word))
            ]
            result = _sum_graded_elements(pieces)
            b_cache[word] = result
            return result

        word = tuple(inputs)
        source_value = f_word(word)
        transfer_source = source_value if len(word) == 1 else b_word(word)
        projection = self.contraction.projection.component(transfer_source.degree)
        result = GradedElement(
            transfer_source.degree,
            projection(transfer_source.vector),
        )
        return TransferWord(len(inputs), result, source_value, len(f_cache), len(b_cache))

    def transferred_product(self, inputs: Sequence[GradedElement]) -> GradedElement:
        """Return only the transferred higher product value."""

        return self.evaluate(inputs).result


def _sum_graded_elements(elements: Sequence[GradedElement]) -> GradedElement:
    """Add homogeneous elements after checking their degrees and bases."""

    if not elements:
        raise ValueError("at least one graded element is required")
    result = elements[0]
    for element in elements[1:]:
        result = result + element
    return result


@dataclass(frozen=True, slots=True, init=False)
class FiniteComplexAction:
    """A finite group action by exact chain or cochain maps."""

    complex: ChainComplex | CochainComplex
    identity: str
    actions: tuple[tuple[str, ChainMap], ...]
    multiplication: tuple[tuple[tuple[str, str], str], ...]

    def __init__(
        self,
        complex_: ChainComplex | CochainComplex,
        identity: str,
        actions: Mapping[str, ChainMap],
        multiplication: Mapping[tuple[str, str], str],
    ) -> None:
        if identity not in actions:
            raise ValueError("finite actions require an identity element")
        if any(
            action.source != complex_ or action.target != complex_
            for action in actions.values()
        ):
            raise ValueError("finite group actions must be endomorphisms of one complex")
        names = set(actions)
        product_values = tuple(multiplication.items())
        if any(left not in names or right not in names or result not in names
               for (left, right), result in product_values):
            raise ValueError("group multiplication is not closed on the action names")
        if len(product_values) != len(names) * len(names):
            raise ValueError("finite group multiplication must be complete")
        if actions[identity] != ChainMap.identity(complex_):
            raise ValueError("the declared finite-group identity must act identically")
        action_values = tuple(sorted(actions.items()))
        object.__setattr__(self, "complex", complex_)
        object.__setattr__(self, "identity", identity)
        object.__setattr__(self, "actions", action_values)
        object.__setattr__(self, "multiplication", tuple(sorted(product_values)))
        table = dict(product_values)
        for left, right in product(names, repeat=2):
            expected = actions[table[(left, right)]]
            if actions[left].compose(actions[right]) != expected:
                raise ValueError("finite action maps do not realize the group law")

    def action(self, name: str) -> ChainMap:
        """Return one named group action."""

        return dict(self.actions)[name]

    @property
    def elements(self) -> tuple[str, ...]:
        """Return group names in deterministic order."""

        return tuple(name for name, _ in self.actions)

    def character_projector(self, character: Mapping[str, object]) -> GradedMap:
        """Return the exact character projector ``|G|^-1 Σ χ(g)^-1 g``."""

        if set(character) != set(self.elements):
            raise ValueError("a character must provide exactly one value per group element")
        scalar_type = self.complex.spaces.scalar_type
        inverse_order = _inverse(_coerce(len(self.elements), scalar_type), scalar_type)
        components: dict[int, LinearMap] = {}
        for degree in self.complex.degrees:
            space = self.complex.spaces.space(degree)
            total = LinearMap.zero(space, space)
            for name in self.elements:
                total = total + self.action(name).component(degree).scale(
                    _inverse(_coerce(character[name], scalar_type), scalar_type)
                )
            components[degree] = total.scale(inverse_order)
        return GradedMap(
            self.complex.spaces,
            self.complex.spaces,
            0,
            components,
        )


GroupAction = FiniteComplexAction


def _coordinate_in_basis(
    basis: Sequence[CoordinateVector], vector: CoordinateVector,
) -> tuple[Scalar, ...]:
    """Express a vector in an independent exact basis by augmented RREF."""

    if not basis:
        if not vector.is_zero():
            raise ValueError("nonzero vector is outside a zero-dimensional basis")
        return ()
    if any(candidate.space != vector.space for candidate in basis):
        raise ValueError("coordinate basis and vector use different named spaces")
    augmented = Matrix(
        tuple(
            tuple(candidate.coordinates[row] for candidate in basis)
            + (vector.coordinates[row],)
            for row in range(vector.space.dimension)
        ),
        scalar_type=vector.space.scalar_type,
    )
    reduced, pivots = augmented.rref()
    unknown_count = len(basis)
    if any(
        all(reduced[row][column].is_zero() for column in range(unknown_count))
        and not reduced[row][unknown_count].is_zero()
        for row in range(reduced.row_count)
    ):
        raise ValueError("vector is not in the declared exact basis span")
    if any(pivot >= unknown_count for pivot in pivots) or len(
        tuple(pivot for pivot in pivots if pivot < unknown_count)
    ) != unknown_count:
        raise ValueError("the declared coordinate basis is not independent")
    result = [_zero(vector.space.scalar_type) for _ in basis]
    for row, pivot in enumerate(pivots):
        if pivot < unknown_count:
            result[pivot] = reduced[row][unknown_count]
    return tuple(result)


@dataclass(frozen=True, slots=True, init=False)
class InvariantSubcomplex:
    """The exact character-isotypic subcomplex cut out by a projector."""

    action: FiniteComplexAction
    character: tuple[tuple[str, Scalar], ...]
    projector: GradedMap
    complex: ChainComplex | CochainComplex
    inclusion_maps: tuple[tuple[int, LinearMap], ...]

    def __init__(self, action: FiniteComplexAction, character: Mapping[str, object]) -> None:
        projector = action.character_projector(character)
        source = action.complex
        spaces: dict[int, VectorSpace] = {}
        bases: dict[int, tuple[CoordinateVector, ...]] = {}
        inclusions: dict[int, LinearMap] = {}
        for degree in source.degrees:
            image = projector.component(degree).image_basis()
            bases[degree] = image
            spaces[degree] = VectorSpace(
                f"{source.spaces.name}[{degree}]^{character}",
                tuple(f"chi:{index}" for index in range(len(image))),
                source.spaces.scalar_type,
            )
            inclusions[degree] = LinearMap(
                spaces[degree],
                source.spaces.space(degree),
                tuple(
                    tuple(image[column].coordinates[row] for column in range(len(image)))
                    for row in range(source.spaces.space(degree).dimension)
                ),
            ) if image else LinearMap.zero(spaces[degree], source.spaces.space(degree))
        graded = GradedVectorSpace(f"{source.spaces.name}^{character}", spaces)
        differentials: dict[int, LinearMap] = {}
        step = -1 if source.direction == "chain" else 1
        for degree in source.degrees:
            basis = bases[degree]
            target_basis = bases.get(degree + step, ())
            target_space = graded.space(degree + step)
            if not basis or not target_basis:
                differentials[degree] = LinearMap.zero(spaces[degree], target_space)
                continue
            rows = []
            original_map = source.differential(degree)
            for target_index in range(len(target_basis)):
                rows.append(tuple(
                    _coordinate_in_basis(
                        target_basis,
                        original_map(basis[source_index]),
                    )[target_index]
                    for source_index in range(len(basis))
                ))
            differentials[degree] = LinearMap(spaces[degree], target_space, tuple(rows))
        restricted = (
            ChainComplex(graded, differentials)
            if source.direction == "chain"
            else CochainComplex(graded, differentials)
        )
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "character", tuple(sorted(
            (name, _coerce(value, source.spaces.scalar_type)) for name, value in character.items()
        )))
        object.__setattr__(self, "projector", projector)
        object.__setattr__(self, "complex", restricted)
        object.__setattr__(self, "inclusion_maps", tuple(sorted(inclusions.items())))

    def inclusion(self, degree: int) -> LinearMap:
        """Return the exact inclusion of one invariant component."""

        return dict(self.inclusion_maps)[degree]

    def project(self, element: GradedElement) -> GradedElement:
        """Project an ambient element to its exact character component."""

        return self.projector(element)

    def cohomology_representatives(self, degree: int) -> tuple[CoordinateVector, ...]:
        """Return representatives in the invariant subcomplex basis."""

        return self.complex.cohomology_representatives(degree)


@dataclass(frozen=True, slots=True, init=False)
class InducedCohomologyAction:
    """Exact matrices induced by a finite complex action on cohomology."""

    action: FiniteComplexAction
    matrices: tuple[tuple[str, int, Matrix], ...]

    def __init__(self, action: FiniteComplexAction) -> None:
        values: list[tuple[str, int, Matrix]] = []
        complex_ = action.complex
        for name in action.elements:
            chain_map = action.action(name)
            for degree in complex_.degrees:
                representatives = complex_.cohomology_representatives(degree)
                if not representatives:
                    continue
                boundaries = complex_.boundaries(degree)
                full_basis = (*boundaries, *representatives)
                columns = []
                for representative in representatives:
                    image = chain_map.component(degree)(representative)
                    coordinates = _coordinate_in_basis(full_basis, image)
                    columns.append(coordinates[len(boundaries):])
                rows: tuple[tuple[Scalar, ...], ...] = tuple(
                    tuple(columns[column][row] for column in range(len(columns)))
                    for row in range(len(representatives))
                )
                values.append((name, degree, Matrix(rows, scalar_type=complex_.spaces.scalar_type)))
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "matrices", tuple(sorted(values)))

    def matrix(self, name: str, degree: int) -> Matrix:
        """Return one exact induced cohomology action matrix."""

        for action_name, action_degree, matrix in self.matrices:
            if action_name == name and action_degree == degree:
                return matrix
        raise KeyError((name, degree))


CharacterProjector = GradedMap


def induced_action_on_cohomology(action: FiniteComplexAction) -> InducedCohomologyAction:
    """Construct exact cohomology actions from a finite chain action."""

    return InducedCohomologyAction(action)


def character_pure_representatives(
    action: FiniteComplexAction,
    character: Mapping[str, object],
    degree: int,
) -> tuple[CoordinateVector, ...]:
    """Extract deterministic exact representatives in one character subcomplex."""

    return InvariantSubcomplex(action, character).cohomology_representatives(degree)


def equivariant_chain_map(
    action: FiniteComplexAction,
    map_: ChainMap,
) -> bool:
    """Check that a chain map commutes with every declared group action."""

    if map_.source != action.complex or map_.target != action.complex:
        raise ValueError("equivariant endomorphism must use the declared complex")
    return all(
        map_.compose(action.action(name)) == action.action(name).compose(map_)
        for name in action.elements
    )


__all__ = [
    "Bicomplex",
    "ChainComplex",
    "ChainHomotopy",
    "ChainMap",
    "CochainComplex",
    "Contraction",
    "ContractionRecord",
    "CoordinateVector",
    "CyclicPairing",
    "DGA",
    "DGAModule",
    "FiniteComplexAction",
    "GradedAction",
    "GradedElement",
    "GradedLinearMap",
    "GradedMap",
    "GradedProduct",
    "GradedVectorSpace",
    "GroupAction",
    "HPLTransfer",
    "InvariantSubcomplex",
    "InducedCohomologyAction",
    "LinearMap",
    "TransferWord",
    "VectorSpace",
    "character_pure_representatives",
    "equivariant_chain_map",
    "graded_commutator",
    "induced_action_on_cohomology",
    "maurer_cartan_residual",
    "mapping_cone",
    "tensor_product_space",
]
