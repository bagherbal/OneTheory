"""Exact basis-aware chain and cochain constructions.

Owns:
    Finite-dimensional graded vector spaces, typed exact linear maps, chain and
    cochain complexes, homology computations, homotopies, cones, shifts, direct
    sums, bicomplexes, and signed totalization over Rational or Eisenstein data.

Depends on:
    `onetheory.math.numbers` for exact scalars and `onetheory.math.linear` for
    deterministic rank, RREF, and nullspace calculations.

Must not:
    Implement sheaves, Čech covers, DGAs, Maurer–Cartan equations, A-infinity or
    HPL transfer, physical bundle data, or any speculative bridge between models.

Phase 0:
    Exact mathematical implementation is provided; physical applications remain
    outside this reusable module until independently derived and verified.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, cast

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
                sum((_multiply(left, right) for left, right in zip(
                        self.rows[row], column, strict=True
                    )),
                    _zero(self.domain.scalar_type))
                for column in zip(*previous.rows, strict=True) if previous.rows
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
                    cls.zero(left.domain, right.codomain),
                ),
                (
                    cls.zero(right.domain, left.codomain),
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
        selected: list[CoordinateVector] = []
        current_rank = _rank_of_vectors(boundaries, space)
        for cycle in self.cycles(degree):
            candidate_rank = _rank_of_vectors((*boundaries, *selected, cycle), space)
            if candidate_rank > current_rank:
                selected.append(cycle)
                current_rank = candidate_rank
        return tuple(selected)

    def shift(self, amount: int) -> ChainComplex | CochainComplex:
        """Shift degrees by ``amount`` and apply the standard parity sign."""

        if isinstance(amount, bool) or not isinstance(amount, int):
            raise TypeError("the shift amount must be an integer")
        shifted_spaces = self.spaces.shift(amount)
        factor = -1 if amount % 2 else 1
        shifted_differentials = {
            degree + amount: differential.scale(factor)
            for degree, differential in self.differentials
        }
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
        differentials = {
            degree: LinearMap.direct_sum(self.differential(degree), other.differential(degree))
            for degree in degrees
        }
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
