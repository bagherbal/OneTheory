"""Immutable exact basis-aware algebraic-geometric quantities.

Owns:
    Named bases, normalization labels, divisor and curve coordinates, symmetric
    triple-intersection tensors, exact class arithmetic, volumes, slopes, and
    explicit quotient/cover conversions.

Depends on:
    `onetheory.math.numbers` for strict Rational coercion only. No selected
    compactification, bundle, sheaf, physical, or numerical geometry is imported.

Must not:
    Embed Schoen constants, choose a carrier, implement bundles or sheaves,
    calculate cohomology, infer geometry from observations, or silently mix bases
    or quotient and cover normalizations.

Phase 0:
    The reusable exact geometry foundation is implemented; model-specific geometry
    remains outside this module.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from itertools import permutations
from typing import cast

from onetheory.math.numbers import Rational, coerce_rational


@dataclass(frozen=True, slots=True)
class Basis:
    """A named ordered coordinate basis with immutable labels."""

    name: str
    labels: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("a basis requires a nonempty name")
        if not self.labels:
            raise ValueError("a basis requires at least one label")
        if any(not isinstance(label, str) or not label for label in self.labels):
            raise TypeError("basis labels must be nonempty strings")
        if len(set(self.labels)) != len(self.labels):
            raise ValueError("basis labels must be distinct")

    @property
    def dimension(self) -> int:
        """Return the basis dimension."""

        return len(self.labels)


@dataclass(frozen=True, slots=True)
class Normalization:
    """A named normalization convention kept explicit on every quantity."""

    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("a normalization requires a nonempty name")


def _coordinates(values: Iterable[object], basis: Basis) -> tuple[Rational, ...]:
    coordinates = tuple(coerce_rational(value) for value in values)
    if len(coordinates) != basis.dimension:
        raise ValueError("coordinate dimension does not agree with the basis")
    return coordinates


def _scalar_coordinates(
    left: tuple[Rational, ...],
    right: tuple[Rational, ...],
    subtract: bool = False,
) -> tuple[Rational, ...]:
    if subtract:
        return tuple(a - b for a, b in zip(left, right, strict=True))
    return tuple(a + b for a, b in zip(left, right, strict=True))


def _scale_coordinates(
    coordinates: tuple[Rational, ...], scalar: object
) -> tuple[Rational, ...]:
    factor = coerce_rational(scalar)
    return tuple(factor * coordinate for coordinate in coordinates)


def _require_coordinate_compatibility(
    left_basis: Basis,
    left_normalization: Normalization,
    right_basis: Basis,
    right_normalization: Normalization,
) -> None:
    if left_basis != right_basis:
        raise ValueError("geometric quantities use incompatible bases")
    if left_normalization != right_normalization:
        raise ValueError("geometric quantities use incompatible normalizations")


def _covering_degree(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError("covering degree must be a positive integer")
    return value


@dataclass(frozen=True, slots=True, init=False)
class Divisor:
    """An immutable divisor coordinate vector in a named basis."""

    _basis: Basis
    _coordinates: tuple[Rational, ...]
    _normalization: Normalization

    def __init__(
        self,
        basis: Basis,
        coordinates: Iterable[object],
        normalization: Normalization,
    ) -> None:
        object.__setattr__(self, "_basis", basis)
        object.__setattr__(self, "_coordinates", _coordinates(coordinates, basis))
        object.__setattr__(self, "_normalization", normalization)

    @property
    def basis(self) -> Basis:
        return self._basis

    @property
    def coordinates(self) -> tuple[Rational, ...]:
        return self._coordinates

    @property
    def normalization(self) -> Normalization:
        return self._normalization

    def _check(self, other: Divisor) -> None:
        _require_coordinate_compatibility(
            self.basis,
            self.normalization,
            other.basis,
            other.normalization,
        )

    def __add__(self, other: Divisor) -> Divisor:
        self._check(other)
        return Divisor(
            self.basis,
            _scalar_coordinates(self.coordinates, other.coordinates),
            self.normalization,
        )

    def __sub__(self, other: Divisor) -> Divisor:
        self._check(other)
        return Divisor(
            self.basis,
            _scalar_coordinates(self.coordinates, other.coordinates, subtract=True),
            self.normalization,
        )

    def __neg__(self) -> Divisor:
        return Divisor(self.basis, (-value for value in self.coordinates), self.normalization)

    def scale(self, scalar: object) -> Divisor:
        """Scale every exact divisor coordinate."""

        return Divisor(
            self.basis,
            _scale_coordinates(self.coordinates, scalar),
            self.normalization,
        )

    def __mul__(self, scalar: object) -> Divisor:
        return self.scale(scalar)

    def __rmul__(self, scalar: object) -> Divisor:
        return self.scale(scalar)

    def to_cover(self, covering_degree: int) -> Divisor:
        """Express the divisor in an explicit cover normalization."""

        _covering_degree(covering_degree)
        return Divisor(self.basis, self.coordinates, Normalization("cover"))

    def to_quotient(self, covering_degree: int) -> Divisor:
        """Express the divisor in an explicit quotient normalization."""

        _covering_degree(covering_degree)
        return Divisor(self.basis, self.coordinates, Normalization("quotient"))


@dataclass(frozen=True, slots=True, init=False)
class Curve:
    """An immutable curve-class coordinate vector in a named basis."""

    _basis: Basis
    _coordinates: tuple[Rational, ...]
    _normalization: Normalization

    def __init__(
        self,
        basis: Basis,
        coordinates: Iterable[object],
        normalization: Normalization,
    ) -> None:
        object.__setattr__(self, "_basis", basis)
        object.__setattr__(self, "_coordinates", _coordinates(coordinates, basis))
        object.__setattr__(self, "_normalization", normalization)

    @property
    def basis(self) -> Basis:
        return self._basis

    @property
    def coordinates(self) -> tuple[Rational, ...]:
        return self._coordinates

    @property
    def normalization(self) -> Normalization:
        return self._normalization

    def _check(self, other: Curve) -> None:
        _require_coordinate_compatibility(
            self.basis,
            self.normalization,
            other.basis,
            other.normalization,
        )

    def __add__(self, other: Curve) -> Curve:
        self._check(other)
        return Curve(
            self.basis,
            _scalar_coordinates(self.coordinates, other.coordinates),
            self.normalization,
        )

    def __sub__(self, other: Curve) -> Curve:
        self._check(other)
        return Curve(
            self.basis,
            _scalar_coordinates(self.coordinates, other.coordinates, subtract=True),
            self.normalization,
        )

    def __neg__(self) -> Curve:
        return Curve(self.basis, (-value for value in self.coordinates), self.normalization)

    def scale(self, scalar: object) -> Curve:
        """Scale every exact curve coordinate."""

        return Curve(
            self.basis,
            _scale_coordinates(self.coordinates, scalar),
            self.normalization,
        )

    def __mul__(self, scalar: object) -> Curve:
        return self.scale(scalar)

    def __rmul__(self, scalar: object) -> Curve:
        return self.scale(scalar)

    def to_cover(self, covering_degree: int) -> Curve:
        """Express the curve class in an explicit cover normalization."""

        _covering_degree(covering_degree)
        return Curve(self.basis, self.coordinates, Normalization("cover"))

    def to_quotient(self, covering_degree: int) -> Curve:
        """Express the curve class in an explicit quotient normalization."""

        _covering_degree(covering_degree)
        return Curve(self.basis, self.coordinates, Normalization("quotient"))


@dataclass(frozen=True, slots=True, init=False)
class CharacteristicClass:
    """Exact coordinate data for a characteristic class of declared degree."""

    _basis: Basis
    _coordinates: tuple[Rational, ...]
    _degree: int
    _normalization: Normalization

    def __init__(
        self,
        basis: Basis,
        coordinates: Iterable[object],
        degree: int,
        normalization: Normalization,
    ) -> None:
        if isinstance(degree, bool) or not isinstance(degree, int) or degree < 0:
            raise ValueError("characteristic-class degree must be a nonnegative integer")
        object.__setattr__(self, "_basis", basis)
        object.__setattr__(self, "_coordinates", _coordinates(coordinates, basis))
        object.__setattr__(self, "_degree", degree)
        object.__setattr__(self, "_normalization", normalization)

    @property
    def basis(self) -> Basis:
        return self._basis

    @property
    def coordinates(self) -> tuple[Rational, ...]:
        return self._coordinates

    @property
    def degree(self) -> int:
        return self._degree

    @property
    def normalization(self) -> Normalization:
        return self._normalization

    def _check(self, other: CharacteristicClass) -> None:
        _require_coordinate_compatibility(
            self.basis,
            self.normalization,
            other.basis,
            other.normalization,
        )
        if self.degree != other.degree:
            raise ValueError("characteristic classes have incompatible degrees")

    def __add__(self, other: CharacteristicClass) -> CharacteristicClass:
        self._check(other)
        return CharacteristicClass(
            self.basis,
            _scalar_coordinates(self.coordinates, other.coordinates),
            self.degree,
            self.normalization,
        )

    def __sub__(self, other: CharacteristicClass) -> CharacteristicClass:
        self._check(other)
        return CharacteristicClass(
            self.basis,
            _scalar_coordinates(self.coordinates, other.coordinates, subtract=True),
            self.degree,
            self.normalization,
        )

    def __neg__(self) -> CharacteristicClass:
        return CharacteristicClass(
            self.basis,
            (-value for value in self.coordinates),
            self.degree,
            self.normalization,
        )

    def scale(self, scalar: object) -> CharacteristicClass:
        """Scale every exact characteristic-class coordinate."""

        return CharacteristicClass(
            self.basis,
            _scale_coordinates(self.coordinates, scalar),
            self.degree,
            self.normalization,
        )

    def __mul__(self, scalar: object) -> CharacteristicClass:
        return self.scale(scalar)

    def __rmul__(self, scalar: object) -> CharacteristicClass:
        return self.scale(scalar)

    def to_cover(self, covering_degree: int) -> CharacteristicClass:
        """Express class coordinates in an explicit cover normalization."""

        _covering_degree(covering_degree)
        return CharacteristicClass(
            self.basis,
            self.coordinates,
            self.degree,
            Normalization("cover"),
        )

    def to_quotient(self, covering_degree: int) -> CharacteristicClass:
        """Express class coordinates in an explicit quotient normalization."""

        _covering_degree(covering_degree)
        return CharacteristicClass(
            self.basis,
            self.coordinates,
            self.degree,
            Normalization("quotient"),
        )


@dataclass(frozen=True, slots=True, init=False)
class TripleIntersectionTensor:
    """A symmetric exact rank-three tensor in a named basis."""

    _basis: Basis
    _coefficients: tuple[tuple[tuple[Rational, ...], ...], ...]
    _normalization: Normalization

    def __init__(
        self,
        basis: Basis,
        coefficients: Mapping[tuple[int, int, int], object],
        normalization: Normalization,
    ) -> None:
        dimension = basis.dimension
        dense = [
            [
                [Rational(0) for _ in range(dimension)]
                for _ in range(dimension)
            ]
            for _ in range(dimension)
        ]
        assigned: dict[tuple[int, int, int], Rational] = {}
        for raw_indices, raw_value in coefficients.items():
            indices = cast(tuple[int, int, int], tuple(raw_indices))
            if len(indices) != 3:
                raise ValueError("intersection indices must have length three")
            if any(
                isinstance(index, bool)
                or not isinstance(index, int)
                or not 0 <= index < dimension
                for index in indices
            ):
                raise ValueError("intersection indices are outside the named basis")
            value = coerce_rational(raw_value)
            for raw_permutation in set(permutations(indices)):
                permutation = cast(tuple[int, int, int], raw_permutation)
                previous = assigned.get(permutation)
                if previous is not None and previous != value:
                    raise ValueError("intersection tensor is not symmetric")
                assigned[permutation] = value
                row, middle, column = permutation
                dense[row][middle][column] = value
        object.__setattr__(
            self,
            "_basis",
            basis,
        )
        object.__setattr__(
            self,
            "_coefficients",
            tuple(tuple(tuple(row) for row in middle) for middle in dense),
        )
        object.__setattr__(self, "_normalization", normalization)

    @property
    def basis(self) -> Basis:
        return self._basis

    @property
    def normalization(self) -> Normalization:
        return self._normalization

    @property
    def coefficients(self) -> tuple[tuple[tuple[Rational, ...], ...], ...]:
        """Return the immutable dense symmetric tensor."""

        return self._coefficients

    @property
    def entries(self) -> tuple[tuple[tuple[int, int, int], Rational], ...]:
        """Return nonzero entries using sorted index triples."""

        result = []
        for first in range(self.basis.dimension):
            for second in range(first, self.basis.dimension):
                for third in range(second, self.basis.dimension):
                    value = self.coefficient(first, second, third)
                    if value.is_zero():
                        continue
                    result.append(((first, second, third), value))
        return tuple(result)

    def coefficient(self, first: int, second: int, third: int) -> Rational:
        """Return one symmetric tensor coefficient."""

        indices = (first, second, third)
        if any(
            isinstance(index, bool)
            or not isinstance(index, int)
            or not 0 <= index < self.basis.dimension
            for index in indices
        ):
            raise IndexError("intersection index is outside the named basis")
        return self._coefficients[first][second][third]

    def _check_divisors(self, divisors: tuple[Divisor, ...]) -> None:
        for divisor in divisors:
            _require_coordinate_compatibility(
                self.basis,
                self.normalization,
                divisor.basis,
                divisor.normalization,
            )

    def triple_product(
        self,
        left: Divisor,
        middle: Divisor,
        right: Divisor,
    ) -> Rational:
        """Evaluate the exact symmetric triple product."""

        self._check_divisors((left, middle, right))
        return sum(
            (
                left.coordinates[first]
                * middle.coordinates[second]
                * right.coordinates[third]
                * self.coefficient(first, second, third)
                for first in range(self.basis.dimension)
                for second in range(self.basis.dimension)
                for third in range(self.basis.dimension)
            ),
            Rational(0),
        )

    def divisor_square(self, divisor: Divisor) -> Curve:
        """Return the curve-coordinate vector obtained by squaring a divisor."""

        self._check_divisors((divisor,))
        coordinates = []
        for index in range(self.basis.dimension):
            basis_divisor = Divisor(
                self.basis,
                (1 if position == index else 0 for position in range(self.basis.dimension)),
                self.normalization,
            )
            coordinates.append(self.triple_product(divisor, divisor, basis_divisor))
        return Curve(self.basis, coordinates, self.normalization)

    def volume(self, divisor: Divisor) -> Rational:
        """Return the exact cubic volume of a divisor."""

        return self.triple_product(divisor, divisor, divisor)

    def slope(self, first_chern: Divisor, kahler: Divisor, rank: int) -> Rational:
        """Return the exact slope `c1·J²/rank`."""

        if isinstance(rank, bool) or not isinstance(rank, int) or rank <= 0:
            raise ValueError("bundle rank must be a positive integer")
        return self.triple_product(first_chern, kahler, kahler) / rank

    def to_cover(self, covering_degree: int) -> TripleIntersectionTensor:
        """Convert intersection values to a cover by an explicit degree."""

        degree = _covering_degree(covering_degree)
        return TripleIntersectionTensor(
            self.basis,
            {
                indices: value * degree for indices, value in self.entries
            },
            Normalization("cover"),
        )

    def to_quotient(self, covering_degree: int) -> TripleIntersectionTensor:
        """Convert intersection values to a quotient by an explicit degree."""

        degree = _covering_degree(covering_degree)
        return TripleIntersectionTensor(
            self.basis,
            {
                indices: value / degree for indices, value in self.entries
            },
            Normalization("quotient"),
        )


GeometryObject = (
    Divisor
    | Curve
    | CharacteristicClass
    | TripleIntersectionTensor
)


def triple_product(
    intersections: TripleIntersectionTensor,
    left: Divisor,
    middle: Divisor,
    right: Divisor,
) -> Rational:
    """Evaluate a tensor-backed exact triple product."""

    return intersections.triple_product(left, middle, right)


def divisor_square(
    intersections: TripleIntersectionTensor,
    divisor: Divisor,
) -> Curve:
    """Return a divisor square as exact curve coordinates."""

    return intersections.divisor_square(divisor)


def volume(intersections: TripleIntersectionTensor, divisor: Divisor) -> Rational:
    """Return a tensor-backed exact divisor volume."""

    return intersections.volume(divisor)


def slope(
    intersections: TripleIntersectionTensor,
    first_chern: Divisor,
    kahler: Divisor,
    rank: int,
) -> Rational:
    """Return the exact slope of coordinate data without a bundle object."""

    return intersections.slope(first_chern, kahler, rank)


def quotient_to_cover(value: GeometryObject, covering_degree: int) -> GeometryObject:
    """Convert an explicit quotient quantity to cover normalization."""

    _covering_degree(covering_degree)
    return value.to_cover(covering_degree)


def cover_to_quotient(value: GeometryObject, covering_degree: int) -> GeometryObject:
    """Convert an explicit cover quantity to quotient normalization."""

    _covering_degree(covering_degree)
    return value.to_quotient(covering_degree)


__all__ = [
    "Basis",
    "CharacteristicClass",
    "Curve",
    "Divisor",
    "Normalization",
    "TripleIntersectionTensor",
    "cover_to_quotient",
    "divisor_square",
    "quotient_to_cover",
    "slope",
    "triple_product",
    "volume",
]
