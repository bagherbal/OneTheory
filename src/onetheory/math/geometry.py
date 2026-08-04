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
from enum import StrEnum
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


class ClassKind(StrEnum):
    """Distinguish integral/topological classes from differential representatives."""

    INTEGRAL = "integral"
    DIFFERENTIAL = "differential"


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


def _scale_coordinates(coordinates: tuple[Rational, ...], scalar: object) -> tuple[Rational, ...]:
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
    _kind: ClassKind

    def __init__(
        self,
        basis: Basis,
        coordinates: Iterable[object],
        degree: int,
        normalization: Normalization,
        kind: ClassKind = ClassKind.INTEGRAL,
    ) -> None:
        if isinstance(degree, bool) or not isinstance(degree, int) or degree < 0:
            raise ValueError("characteristic-class degree must be a nonnegative integer")
        object.__setattr__(self, "_basis", basis)
        object.__setattr__(self, "_coordinates", _coordinates(coordinates, basis))
        object.__setattr__(self, "_degree", degree)
        object.__setattr__(self, "_normalization", normalization)
        object.__setattr__(self, "_kind", kind)

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

    @property
    def kind(self) -> ClassKind:
        """Return whether the coordinates are topological or differential data."""

        return self._kind

    def _check(self, other: CharacteristicClass) -> None:
        _require_coordinate_compatibility(
            self.basis,
            self.normalization,
            other.basis,
            other.normalization,
        )
        if self.degree != other.degree:
            raise ValueError("characteristic classes have incompatible degrees")
        if self.kind != other.kind:
            raise ValueError("integral and differential classes cannot be added")

    def __add__(self, other: CharacteristicClass) -> CharacteristicClass:
        self._check(other)
        return CharacteristicClass(
            self.basis,
            _scalar_coordinates(self.coordinates, other.coordinates),
            self.degree,
            self.normalization,
            self.kind,
        )

    def __sub__(self, other: CharacteristicClass) -> CharacteristicClass:
        self._check(other)
        return CharacteristicClass(
            self.basis,
            _scalar_coordinates(self.coordinates, other.coordinates, subtract=True),
            self.degree,
            self.normalization,
            self.kind,
        )

    def __neg__(self) -> CharacteristicClass:
        return CharacteristicClass(
            self.basis,
            (-value for value in self.coordinates),
            self.degree,
            self.normalization,
            self.kind,
        )

    def scale(self, scalar: object) -> CharacteristicClass:
        """Scale every exact characteristic-class coordinate."""

        return CharacteristicClass(
            self.basis,
            _scale_coordinates(self.coordinates, scalar),
            self.degree,
            self.normalization,
            self.kind,
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
            self.kind,
        )

    def to_quotient(self, covering_degree: int) -> CharacteristicClass:
        """Express class coordinates in an explicit quotient normalization."""

        _covering_degree(covering_degree)
        return CharacteristicClass(
            self.basis,
            self.coordinates,
            self.degree,
            Normalization("quotient"),
            self.kind,
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
            [[Rational(0) for _ in range(dimension)] for _ in range(dimension)]
            for _ in range(dimension)
        ]
        assigned: dict[tuple[int, int, int], Rational] = {}
        for raw_indices, raw_value in coefficients.items():
            indices = cast(tuple[int, int, int], tuple(raw_indices))
            if len(indices) != 3:
                raise ValueError("intersection indices must have length three")
            if any(
                isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < dimension
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
            {indices: value * degree for indices, value in self.entries},
            Normalization("cover"),
        )

    def to_quotient(self, covering_degree: int) -> TripleIntersectionTensor:
        """Convert intersection values to a quotient by an explicit degree."""

        degree = _covering_degree(covering_degree)
        return TripleIntersectionTensor(
            self.basis,
            {indices: value / degree for indices, value in self.entries},
            Normalization("quotient"),
        )


@dataclass(frozen=True, slots=True)
class VectorBundle:
    """A generic vector-bundle record whose topology does not imply a connection."""

    name: str
    rank: int
    basis: Basis
    normalization: Normalization
    c1: CharacteristicClass | None
    c2: CharacteristicClass | None
    c3: CharacteristicClass | None
    connection: object | None
    provenance: str

    def __init__(
        self,
        name: str,
        rank: int,
        basis: Basis,
        normalization: Normalization,
        c1: CharacteristicClass | None = None,
        c2: CharacteristicClass | None = None,
        c3: CharacteristicClass | None = None,
        connection: object | None = None,
        provenance: str = "",
    ) -> None:
        if not name.strip() or not provenance.strip():
            raise ValueError("vector bundles require a name and provenance")
        if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1:
            raise ValueError("vector-bundle rank must be positive")
        for degree, class_data in ((1, c1), (2, c2), (3, c3)):
            if class_data is not None and (
                class_data.basis != basis
                or class_data.normalization != normalization
                or class_data.degree != degree
                or class_data.kind is not ClassKind.INTEGRAL
            ):
                raise ValueError("bundle Chern classes must be integral data in its basis")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "rank", rank)
        object.__setattr__(self, "basis", basis)
        object.__setattr__(self, "normalization", normalization)
        object.__setattr__(self, "c1", c1)
        object.__setattr__(self, "c2", c2)
        object.__setattr__(self, "c3", c3)
        object.__setattr__(self, "connection", connection)
        object.__setattr__(self, "provenance", provenance)

    @property
    def has_connection(self) -> bool:
        """Return whether a connection was supplied independently of topology."""

        return self.connection is not None


@dataclass(frozen=True, slots=True)
class ChernCharacter:
    """Chern-character components with explicit truncation and provenance."""

    bundle: VectorBundle
    rank: int
    components: tuple[CharacteristicClass, ...]
    formal_terms: tuple[tuple[int, str], ...]
    provenance: str

    def __init__(
        self,
        bundle: VectorBundle,
        components: Iterable[CharacteristicClass] = (),
        formal_terms: Mapping[int, str] | None = None,
        provenance: str = "",
    ) -> None:
        values = tuple(components)
        if not provenance.strip():
            raise ValueError("Chern characters require provenance")
        if any(
            class_data.basis != bundle.basis
            or class_data.normalization != bundle.normalization
            or class_data.kind is not ClassKind.INTEGRAL
            for class_data in values
        ):
            raise ValueError("Chern-character components must match the bundle topology")
        if len({class_data.degree for class_data in values}) != len(values):
            raise ValueError("Chern-character degrees must be unique")
        object.__setattr__(self, "bundle", bundle)
        object.__setattr__(self, "rank", bundle.rank)
        object.__setattr__(self, "components", tuple(sorted(values, key=lambda item: item.degree)))
        object.__setattr__(
            self,
            "formal_terms",
            tuple(
                sorted((degree, expression) for degree, expression in (formal_terms or {}).items())
            ),
        )
        object.__setattr__(self, "provenance", provenance)

    @classmethod
    def from_bundle(
        cls, bundle: VectorBundle, provenance: str = "Chern character formula"
    ) -> ChernCharacter:
        """Create the known components without inventing unavailable cup products."""

        components = (bundle.c1,) if bundle.c1 is not None else ()
        terms: dict[int, str] = {0: f"{bundle.rank}"}
        if bundle.c1 is not None:
            terms[1] = "c1"
        if bundle.c2 is not None:
            terms[2] = "(c1^2 - 2 c2)/2"
        if bundle.c3 is not None:
            terms[3] = "(c1^3 - 3 c1 c2 + 3 c3)/6"
        return cls(bundle, components, terms, provenance)

    def component(self, degree: int) -> CharacteristicClass | None:
        """Return an explicitly supplied integral component."""

        return next((item for item in self.components if item.degree == degree), None)


@dataclass(frozen=True, slots=True)
class PontryaginClass:
    """A real Pontryagin-class record with no automatic bundle existence claim."""

    degree: int
    class_data: CharacteristicClass
    expression: str
    provenance: str

    def __init__(
        self,
        degree: int,
        class_data: CharacteristicClass,
        expression: str,
        provenance: str,
    ) -> None:
        if degree < 1 or not expression.strip() or not provenance.strip():
            raise ValueError("Pontryagin classes require degree, expression, and provenance")
        if class_data.kind is not ClassKind.INTEGRAL:
            raise ValueError("Pontryagin topology must remain an integral class")
        object.__setattr__(self, "degree", degree)
        object.__setattr__(self, "class_data", class_data)
        object.__setattr__(self, "expression", expression)
        object.__setattr__(self, "provenance", provenance)

    @classmethod
    def p1_from_c2(cls, c2: CharacteristicClass, provenance: str = "p1 = -2 c2") -> PontryaginClass:
        """Construct the first Pontryagin class for a real SU bundle convention."""

        if c2.degree != 2:
            raise ValueError("p1 from c2 requires a degree-two Chern class")
        return cls(1, c2.scale(-2), "p1 = -2 c2", provenance)


@dataclass(frozen=True, slots=True)
class ChernWeilRepresentative:
    """A differential representative tied to supplied curvature data."""

    class_data: CharacteristicClass
    curvature: object
    polynomial: str
    provenance: str

    def __init__(
        self,
        class_data: CharacteristicClass,
        curvature: object,
        polynomial: str,
        provenance: str,
    ) -> None:
        if class_data.kind is not ClassKind.DIFFERENTIAL:
            raise ValueError("Chern–Weil representatives require differential class data")
        if not polynomial.strip() or not provenance.strip():
            raise ValueError("Chern–Weil representatives require polynomial provenance")
        object.__setattr__(self, "class_data", class_data)
        object.__setattr__(self, "curvature", curvature)
        object.__setattr__(self, "polynomial", polynomial)
        object.__setattr__(self, "provenance", provenance)

    @property
    def represents_integral_class(self) -> bool:
        """Return false: differential data are not silently promoted to topology."""

        return False


@dataclass(frozen=True, slots=True)
class WedgePairing:
    """An exact cup/wedge pairing table in one named basis."""

    basis: Basis
    left_degree: int
    right_degree: int
    coefficients: tuple[tuple[tuple[int, int], Rational], ...]
    normalization: Normalization
    provenance: str

    def __init__(
        self,
        basis: Basis,
        left_degree: int,
        right_degree: int,
        coefficients: Mapping[tuple[int, int], object],
        normalization: Normalization,
        provenance: str,
    ) -> None:
        if left_degree < 0 or right_degree < 0 or not provenance.strip():
            raise ValueError("pairings require nonnegative degrees and provenance")
        values = tuple(
            sorted(
                (
                    (tuple(indices), coerce_rational(value))
                    for indices, value in coefficients.items()
                )
            )
        )
        if any(
            len(indices) != 2 or any(index < 0 or index >= basis.dimension for index in indices)
            for indices, _ in values
        ):
            raise ValueError("pairing indices are outside the named basis")
        object.__setattr__(self, "basis", basis)
        object.__setattr__(self, "left_degree", left_degree)
        object.__setattr__(self, "right_degree", right_degree)
        object.__setattr__(self, "coefficients", values)
        object.__setattr__(self, "normalization", normalization)
        object.__setattr__(self, "provenance", provenance)

    def evaluate(self, left: CharacteristicClass, right: CharacteristicClass) -> Rational:
        """Evaluate the exact pairing and reject incompatible class kinds."""

        if (
            left.basis != self.basis
            or right.basis != self.basis
            or left.normalization != self.normalization
            or right.normalization != self.normalization
            or left.degree != self.left_degree
            or right.degree != self.right_degree
            or left.kind != right.kind
        ):
            raise ValueError(
                "pairing inputs use incompatible basis, degree, normalization, or kind"
            )
        return sum(
            (
                left.coordinates[first] * right.coordinates[second] * value
                for (first, second), value in self.coefficients
            ),
            Rational(0),
        )


@dataclass(frozen=True, slots=True)
class Pushforward:
    """An explicit internal integration map with a declared topological degree."""

    basis: Basis
    top_degree: int
    coefficients: tuple[Rational, ...]
    normalization: Normalization
    provenance: str

    def __init__(
        self,
        basis: Basis,
        top_degree: int,
        coefficients: Iterable[object],
        normalization: Normalization,
        provenance: str,
    ) -> None:
        values = tuple(coerce_rational(value) for value in coefficients)
        if len(values) != basis.dimension or top_degree < 0 or not provenance.strip():
            raise ValueError("pushforwards require basis-sized coefficients and provenance")
        object.__setattr__(self, "basis", basis)
        object.__setattr__(self, "top_degree", top_degree)
        object.__setattr__(self, "coefficients", values)
        object.__setattr__(self, "normalization", normalization)
        object.__setattr__(self, "provenance", provenance)

    def integrate(self, class_data: CharacteristicClass) -> Rational:
        """Push a top-degree class to an exact scalar."""

        if (
            class_data.basis != self.basis
            or class_data.normalization != self.normalization
            or class_data.degree != self.top_degree
        ):
            raise ValueError("pushforward input is incompatible with its internal space")
        return sum(
            (
                coordinate * coefficient
                for coordinate, coefficient in zip(
                    class_data.coordinates, self.coefficients, strict=True
                )
            ),
            Rational(0),
        )


def cup_pairing(
    pairing: WedgePairing,
    left: CharacteristicClass,
    right: CharacteristicClass,
) -> Rational:
    """Evaluate a named cup/wedge pairing."""

    return pairing.evaluate(left, right)


GeometryObject = Divisor | Curve | CharacteristicClass | TripleIntersectionTensor


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
    "ClassKind",
    "CharacteristicClass",
    "ChernCharacter",
    "ChernWeilRepresentative",
    "Curve",
    "Divisor",
    "Normalization",
    "PontryaginClass",
    "Pushforward",
    "TripleIntersectionTensor",
    "VectorBundle",
    "WedgePairing",
    "cover_to_quotient",
    "cup_pairing",
    "divisor_square",
    "quotient_to_cover",
    "slope",
    "triple_product",
    "volume",
]
