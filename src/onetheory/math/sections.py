"""Exact multigraded Cox-ring section spaces and finite section actions.

Owns:
    Immutable multidegrees, finite Cox monomial enumeration, homogeneous ideal
    quotient normal forms, exact section multiplication, polynomial pullbacks,
    restriction maps, deterministic basis serialization, and finite linear
    actions on a declared quotient section basis.

Depends on:
    `onetheory.math.numbers`, `polynomials`, and `linear` only. The machinery is
    independent of any Schoen degree, bundle, chart, or physical interpretation.

Must not:
    Insert model-specific degrees, infer global generation from samples, choose
    extension cocycles, implement numerical metrics, or treat section dimensions
    as evidence for a physical bundle.

Phase 0:
    Generic exact section machinery is implemented; carrier bases, lifts, and
    metric data remain unavailable until their physical inputs are supplied.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from itertools import product
from typing import Any, cast

from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import Eisenstein, Rational, coerce_rational
from onetheory.math.polynomials import Polynomial, Scalar, ScalarType

DegreeCoordinates = tuple[int, ...]
Monomial = tuple[int, ...]


def _add(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) + right)


def _subtract(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) - right)


def _multiply(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) * right)


def _zero(scalar_type: ScalarType) -> Scalar:
    return Rational(0) if scalar_type is Rational else Eisenstein(0)


def _coerce(value: object, scalar_type: ScalarType) -> Scalar:
    if scalar_type is Rational:
        return coerce_rational(value)
    return Eisenstein.coerce(value)


@dataclass(frozen=True, slots=True, order=True)
class MultiDegree:
    """One ordered integral multidegree in a fixed grading dimension."""

    coordinates: DegreeCoordinates

    def __init__(self, coordinates: Iterable[int]) -> None:
        values = tuple(coordinates)
        if not values:
            raise ValueError("multidegrees require at least one coordinate")
        if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
            raise TypeError("multidegree coordinates must be integers")
        object.__setattr__(self, "coordinates", values)

    @property
    def dimension(self) -> int:
        """Return the grading dimension."""

        return len(self.coordinates)

    def _check(self, other: MultiDegree) -> None:
        if self.dimension != other.dimension:
            raise ValueError("multidegree dimensions do not agree")

    def __add__(self, other: MultiDegree) -> MultiDegree:
        self._check(other)
        return MultiDegree(left + right for left, right in zip(self, other, strict=True))

    def __sub__(self, other: MultiDegree) -> MultiDegree:
        self._check(other)
        return MultiDegree(left - right for left, right in zip(self, other, strict=True))

    def __iter__(self) -> Iterator[int]:
        return iter(self.coordinates)

    def __getitem__(self, index: int) -> int:
        return self.coordinates[index]

    def is_nonnegative(self) -> bool:
        """Return whether every coordinate is nonnegative."""

        return all(value >= 0 for value in self)

    def componentwise_le(self, other: MultiDegree) -> bool:
        """Return the componentwise partial-order comparison."""

        self._check(other)
        return all(left <= right for left, right in zip(self, other, strict=True))


@dataclass(frozen=True, slots=True)
class CoxVariable:
    """A named Cox variable with an exact declared multidegree."""

    name: str
    degree: MultiDegree

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Cox variables require nonempty names")


@dataclass(frozen=True, slots=True)
class CoxRing:
    """A finite-section Cox polynomial ring over Rational or Eisenstein scalars."""

    variables: tuple[CoxVariable, ...]
    scalar_type: ScalarType

    def __init__(
        self,
        variables: Iterable[CoxVariable],
        *,
        scalar_type: ScalarType = Rational,
    ) -> None:
        values = tuple(variables)
        if not values or len({variable.name for variable in values}) != len(values):
            raise ValueError("Cox variables must be nonempty and uniquely named")
        grading_dimension = values[0].degree.dimension
        if any(variable.degree.dimension != grading_dimension for variable in values):
            raise ValueError("Cox variables must use one grading dimension")
        if any(
            not variable.degree.is_nonnegative() or not any(value > 0 for value in variable.degree)
            for variable in values
        ):
            raise ValueError("finite monomial enumeration requires positive Cox degrees")
        if scalar_type not in (Rational, Eisenstein):
            raise TypeError("Cox rings require Rational or Eisenstein coefficients")
        object.__setattr__(self, "variables", values)
        object.__setattr__(self, "scalar_type", scalar_type)

    @property
    def variable_count(self) -> int:
        """Return the number of Cox variables."""

        return len(self.variables)

    @property
    def grading_dimension(self) -> int:
        """Return the number of grading coordinates."""

        return self.variables[0].degree.dimension

    def _check_degree(self, degree: MultiDegree) -> None:
        if degree.dimension != self.grading_dimension:
            raise ValueError("degree dimension does not match the Cox ring")

    def monomial_degree(self, exponents: Monomial) -> MultiDegree:
        """Return the multidegree of one nonnegative exponent tuple."""

        if len(exponents) != self.variable_count or any(value < 0 for value in exponents):
            raise ValueError("monomial exponents do not match the Cox ring")
        result = [0] * self.grading_dimension
        for exponent, variable in zip(exponents, self.variables, strict=True):
            for index, degree in enumerate(variable.degree):
                result[index] += exponent * degree
        return MultiDegree(result)

    def monomial_basis(self, degree: MultiDegree) -> tuple[Monomial, ...]:
        """Enumerate all Cox monomials of one nonnegative target degree."""

        self._check_degree(degree)
        if not degree.is_nonnegative():
            return ()
        upper_bounds: list[int] = []
        for variable in self.variables:
            bounds = [
                target // weight
                for target, weight in zip(degree, variable.degree, strict=True)
                if weight > 0
            ]
            upper_bounds.append(min(bounds))
        candidates = product(*(range(bound + 1) for bound in upper_bounds))
        return tuple(
            exponents
            for exponents in candidates
            if self.monomial_degree(exponents) == degree
        )

    def polynomial(
        self,
        terms: Mapping[Monomial, object] | Iterable[tuple[Monomial, object]],
    ) -> Polynomial:
        """Construct a polynomial after validating its Cox exponent dimension."""

        raw = tuple(terms.items()) if isinstance(terms, Mapping) else tuple(terms)
        if any(len(exponents) != self.variable_count for exponents, _ in raw):
            raise ValueError("polynomial exponents do not match the Cox ring")
        return Polynomial(raw, variable_count=self.variable_count, scalar_type=self.scalar_type)

    def monomial(self, exponents: Monomial, coefficient: object = 1) -> Polynomial:
        """Construct one exact Cox monomial."""

        return self.polynomial(((tuple(exponents), coefficient),))

    def homogeneous_degree(self, polynomial: Polynomial) -> MultiDegree:
        """Return the common multidegree of a nonzero homogeneous polynomial."""

        if (
            polynomial.variable_count != self.variable_count
            or polynomial.scalar_type is not self.scalar_type
        ):
            raise TypeError("polynomial is incompatible with the Cox ring")
        if polynomial.is_zero():
            raise ValueError("the zero polynomial has no intrinsic homogeneous degree")
        degrees = {self.monomial_degree(exponents) for exponents, _ in polynomial.terms}
        if len(degrees) != 1:
            raise ValueError("polynomial is not homogeneous in the Cox grading")
        return next(iter(degrees))


@dataclass(frozen=True, slots=True)
class HomogeneousIdeal:
    """A declared homogeneous ideal used for exact degree-wise quotienting."""

    ring: CoxRing
    generators: tuple[Polynomial, ...]

    def __init__(self, ring: CoxRing, generators: Iterable[Polynomial] = ()) -> None:
        values = tuple(generators)
        for generator in values:
            ring.homogeneous_degree(generator)
        object.__setattr__(self, "ring", ring)
        object.__setattr__(self, "generators", values)

    def relation_rows(self, degree: MultiDegree) -> tuple[tuple[Scalar, ...], ...]:
        """Generate exact ideal multiples in one target degree."""

        ambient = self.ring.monomial_basis(degree)
        index = {monomial: position for position, monomial in enumerate(ambient)}
        rows: list[tuple[Scalar, ...]] = []
        for generator in self.generators:
            generator_degree = self.ring.homogeneous_degree(generator)
            multiplier_degree = degree - generator_degree
            if not multiplier_degree.is_nonnegative():
                continue
            for multiplier in self.ring.monomial_basis(multiplier_degree):
                row = [_zero(self.ring.scalar_type) for _ in ambient]
                for exponents, coefficient in generator.terms:
                    product_exponents = tuple(
                        left + right for left, right in zip(exponents, multiplier, strict=True)
                    )
                    row[index[product_exponents]] = _add(
                        row[index[product_exponents]], coefficient
                    )
                rows.append(tuple(row))
        return tuple(rows)


@dataclass(frozen=True, slots=True, init=False)
class SectionSpace:
    """One exact homogeneous Cox quotient section space."""

    ring: CoxRing
    degree: MultiDegree
    ideal: HomogeneousIdeal
    ambient_basis: tuple[Monomial, ...]
    quotient_basis: tuple[Monomial, ...]
    relation_matrix: Matrix | None
    _rref: Matrix | None
    _pivots: tuple[int, ...]

    def __init__(
        self,
        ring: CoxRing,
        degree: MultiDegree,
        ideal: HomogeneousIdeal | None = None,
    ) -> None:
        chosen_ideal = HomogeneousIdeal(ring) if ideal is None else ideal
        if chosen_ideal.ring != ring:
            raise ValueError("section ideal must use the same Cox ring")
        ambient = ring.monomial_basis(degree)
        rows = chosen_ideal.relation_rows(degree)
        relation_matrix = (
            Matrix(rows, scalar_type=ring.scalar_type)
            if rows
            else None
        )
        reduced, pivots = relation_matrix.rref() if relation_matrix is not None else (None, ())
        pivot_set = set(pivots)
        quotient = tuple(
            monomial for index, monomial in enumerate(ambient) if index not in pivot_set
        )
        object.__setattr__(self, "ring", ring)
        object.__setattr__(self, "degree", degree)
        object.__setattr__(self, "ideal", chosen_ideal)
        object.__setattr__(self, "ambient_basis", ambient)
        object.__setattr__(self, "quotient_basis", quotient)
        object.__setattr__(self, "relation_matrix", relation_matrix)
        object.__setattr__(self, "_rref", reduced)
        object.__setattr__(self, "_pivots", pivots)

    @property
    def ambient_dimension(self) -> int:
        """Return the exact ambient monomial count."""

        return len(self.ambient_basis)

    @property
    def dimension(self) -> int:
        """Return the exact quotient section dimension."""

        return len(self.quotient_basis)

    @property
    def scalar_type(self) -> ScalarType:
        """Return the exact coefficient field."""

        return self.ring.scalar_type

    def _ambient_vector(self, values: Iterable[object]) -> Vector:
        """Coerce one full ambient coordinate vector."""

        coordinates = tuple(values)
        if len(coordinates) != self.ambient_dimension:
            raise ValueError("ambient section coordinates have the wrong dimension")
        return Vector(coordinates, scalar_type=self.scalar_type)

    def normal_form(self, values: Iterable[object]) -> Vector:
        """Reduce ambient coordinates to the deterministic quotient normal form."""

        vector = self._ambient_vector(values)
        if self._rref is None:
            return vector
        work = list(vector.values)
        for row, pivot in enumerate(self._pivots):
            factor = work[pivot]
            if factor.is_zero():
                continue
            work = [
                _subtract(value, _multiply(factor, entry))
                for value, entry in zip(work, self._rref[row], strict=True)
            ]
        return Vector(work, scalar_type=self.scalar_type)

    def from_ambient(self, values: Iterable[object]) -> Section:
        """Create a section from ambient coordinates and reduce it exactly."""

        return Section(self, self.normal_form(values))

    def from_quotient_coordinates(self, values: Iterable[object]) -> Section:
        """Create a section from coordinates in the deterministic quotient basis."""

        coordinates = tuple(values)
        if len(coordinates) != self.dimension:
            raise ValueError("quotient section coordinates have the wrong dimension")
        ambient = [_zero(self.scalar_type) for _ in self.ambient_basis]
        indices = {monomial: index for index, monomial in enumerate(self.ambient_basis)}
        for coefficient, monomial in zip(coordinates, self.quotient_basis, strict=True):
            ambient[indices[monomial]] = _coerce(coefficient, self.scalar_type)
        return self.from_ambient(ambient)

    def basis(self) -> tuple[Section, ...]:
        """Return the deterministic quotient basis as exact sections."""

        return tuple(
            self.from_quotient_coordinates(
                1 if position == index else 0 for position in range(self.dimension)
            )
            for index in range(self.dimension)
        )

    def quotient_coordinates(self, section: Section) -> Vector:
        """Return exact coordinates in the deterministic quotient basis."""

        self._require_section(section)
        indices = {monomial: index for index, monomial in enumerate(self.ambient_basis)}
        return Vector(
            (section.ambient[indices[monomial]] for monomial in self.quotient_basis),
            scalar_type=self.scalar_type,
        )

    def polynomial(self, section: Section) -> Polynomial:
        """Return the normalized ambient polynomial representative."""

        self._require_section(section)
        return self.ring.polynomial(
            (monomial, coefficient)
            for monomial, coefficient in zip(self.ambient_basis, section.ambient, strict=True)
            if not coefficient.is_zero()
        )

    def multiply(self, left: Section, right: Section, target: SectionSpace) -> Section:
        """Multiply sections and reduce in a compatible target quotient."""

        self._require_section(left)
        self._require_section(right)
        if left.space is not self or right.space is not self:
            raise ValueError("section multiplication requires one source space")
        if target.ring != self.ring or target.ideal != self.ideal:
            raise ValueError("section products require compatible quotient rings")
        expected_degree = self.degree + self.degree
        if target.degree != expected_degree:
            raise ValueError("target degree does not match the section product")
        return target.from_ambient(
            polynomial_terms_to_vector(
                self.polynomial(left) * self.polynomial(right), target.ambient_basis
            )
        )

    def pullback(self, section: Section, map_: CoxMap, target: SectionSpace) -> Section:
        """Pull back one section through an exact polynomial Cox map."""

        self._require_section(section)
        if map_.source != self.ring or target.ring != map_.target:
            raise ValueError("pullback rings do not match the section and map")
        if target.degree != map_.pullback_degree(self.degree):
            raise ValueError("target degree does not match the Cox pullback")
        return target.from_ambient(
            polynomial_terms_to_vector(
                map_.pullback_polynomial(self.polynomial(section)), target.ambient_basis
            )
        )

    def restrict(self, section: Section, map_: CoxMap, target: SectionSpace) -> Section:
        """Restrict one section through a declared exact polynomial map."""

        return self.pullback(section, map_, target)

    def basis_serialization(self) -> tuple[tuple[Monomial, ...], ...]:
        """Return a deterministic machine-readable quotient-basis serialization."""

        return tuple(
            tuple(
                monomial
                for monomial, coefficient in zip(self.ambient_basis, section.ambient, strict=True)
                if not coefficient.is_zero()
            )
            for section in self.basis()
        )

    def _require_section(self, section: Section) -> None:
        if section.space != self:
            raise ValueError("section belongs to an incompatible quotient space")


@dataclass(frozen=True, slots=True)
class Section:
    """One exact quotient section with its normalized ambient representative."""

    space: SectionSpace
    ambient: Vector

    def __post_init__(self) -> None:
        if self.ambient.scalar_type is not self.space.scalar_type:
            raise TypeError("section scalar field does not match its space")
        if self.ambient.dimension != self.space.ambient_dimension:
            raise ValueError("section ambient dimension does not match its space")

    def is_zero(self) -> bool:
        """Return whether the section class is exactly zero."""

        return self.ambient.is_zero()


@dataclass(frozen=True, slots=True)
class CoxMap:
    """An exact polynomial map between Cox rings with homogeneous images."""

    source: CoxRing
    target: CoxRing
    images: tuple[Polynomial, ...]
    image_degrees: tuple[MultiDegree, ...]
    grading_images: tuple[MultiDegree, ...]

    def __init__(
        self,
        source: CoxRing,
        target: CoxRing,
        images: Sequence[Polynomial],
        grading_images: Sequence[MultiDegree] | None = None,
    ) -> None:
        values = tuple(images)
        if len(values) != source.variable_count:
            raise ValueError("Cox maps require one image per source variable")
        if any(image.scalar_type is not source.scalar_type for image in values):
            raise TypeError("Cox map images must use the source scalar field")
        if any(image.variable_count != target.variable_count for image in values):
            raise ValueError("Cox map images must use the target variables")
        degrees = tuple(target.homogeneous_degree(image) for image in values)
        declared_grading_images: tuple[MultiDegree, ...]
        if grading_images is None:
            if source.grading_dimension != 1 or len({degree for degree in degrees}) != 1:
                raise ValueError("the Cox grading map must be declared explicitly")
            declared_grading_images = (degrees[0],)
        else:
            declared_grading_images = tuple(grading_images)
            if len(declared_grading_images) != source.grading_dimension:
                raise ValueError("grading image count does not match the source grading")
            if any(
                degree.dimension != target.grading_dimension
                for degree in declared_grading_images
            ):
                raise ValueError("grading images must use the target grading dimension")
        for variable, image_degree in zip(source.variables, degrees, strict=True):
            expected = MultiDegree((0,) * target.grading_dimension)
            for exponent, grading_image in zip(
                variable.degree, declared_grading_images, strict=True
            ):
                expected = expected + MultiDegree(
                    grading_image.coordinates[index] * exponent
                    for index in range(grading_image.dimension)
                )
            if expected != image_degree:
                raise ValueError("Cox images do not preserve the declared grading")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "images", values)
        object.__setattr__(self, "image_degrees", degrees)
        object.__setattr__(self, "grading_images", declared_grading_images)

    def pullback_degree(self, degree: MultiDegree) -> MultiDegree:
        """Return the target degree induced by a source multidegree."""

        if degree.dimension != self.source.grading_dimension:
            raise ValueError("source degree does not match the Cox map")
        result = MultiDegree((0,) * self.target.grading_dimension)
        for exponent, grading_image in zip(degree, self.grading_images, strict=True):
            result = result + MultiDegree(
                grading_image.coordinates[i] * exponent
                for i in range(grading_image.dimension)
            )
        return result

    def pullback_polynomial(self, polynomial: Polynomial) -> Polynomial:
        """Substitute the exact target polynomials into one source polynomial."""

        if polynomial.variable_count != self.source.variable_count:
            raise ValueError("polynomial does not use the Cox map source ring")
        if polynomial.scalar_type is not self.source.scalar_type:
            raise TypeError("polynomial scalar field does not match the Cox map")
        return polynomial.substitute(self.images)


@dataclass(frozen=True, slots=True, init=False)
class SectionGroupAction:
    """A finite exact linear action on one quotient section basis."""

    space: SectionSpace
    identity: str
    matrices: tuple[tuple[str, Matrix], ...]
    multiplication: tuple[tuple[tuple[str, str], str], ...]

    def __init__(
        self,
        space: SectionSpace,
        identity: str,
        matrices: Mapping[str, Matrix],
        multiplication: Mapping[tuple[str, str], str],
    ) -> None:
        if identity not in matrices:
            raise ValueError("section actions require a declared identity")
        if any(
            matrix.shape != (space.dimension, space.dimension)
            or matrix.scalar_type is not space.scalar_type
            or matrix.determinant().is_zero()
            for matrix in matrices.values()
        ):
            raise ValueError("section actions require invertible quotient-basis matrices")
        names = set(matrices)
        entries = tuple(multiplication.items())
        if len(entries) != len(names) * len(names):
            raise ValueError("section group multiplication must be complete")
        if any(left not in names or right not in names or result not in names
               for (left, right), result in entries):
            raise ValueError("section group multiplication is not closed")
        identity_matrix = Matrix.identity(space.dimension, scalar_type=space.scalar_type)
        if matrices[identity] != identity_matrix:
            raise ValueError("the section identity must act identically")
        table = dict(entries)
        for left, right in product(names, repeat=2):
            if matrices[left].matmul(matrices[right]) != matrices[table[(left, right)]]:
                raise ValueError("section matrices do not realize the group law")
        object.__setattr__(self, "space", space)
        object.__setattr__(self, "identity", identity)
        object.__setattr__(self, "matrices", tuple(sorted(matrices.items())))
        object.__setattr__(self, "multiplication", tuple(sorted(entries)))

    def apply(self, name: str, section: Section) -> Section:
        """Apply one exact group element to a quotient section."""

        self.space._require_section(section)
        matrix = dict(self.matrices)[name]
        return self.space.from_quotient_coordinates(
            matrix.matvec(self.space.quotient_coordinates(section))
        )

    def matrix(self, name: str) -> Matrix:
        """Return one exact action matrix."""

        return dict(self.matrices)[name]


def polynomial_terms_to_vector(
    polynomial: Polynomial,
    basis: Sequence[Monomial],
) -> tuple[Scalar, ...]:
    """Convert exact polynomial terms into coordinates in a declared basis."""

    coefficients = {_monomial: coefficient for _monomial, coefficient in polynomial.terms}
    if any(len(monomial) != polynomial.variable_count for monomial in basis):
        raise ValueError("basis monomials do not match the polynomial variables")
    return tuple(coefficients.get(monomial, _zero(polynomial.scalar_type)) for monomial in basis)


__all__ = [
    "CoxMap",
    "CoxRing",
    "CoxVariable",
    "HomogeneousIdeal",
    "MultiDegree",
    "Section",
    "SectionGroupAction",
    "SectionSpace",
    "polynomial_terms_to_vector",
]
