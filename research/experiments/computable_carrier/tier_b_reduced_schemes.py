"""Build exact reduced length-three schemes from classified deck orbits.

Owns:
    Quadratic vanishing spaces, linear syzygies, Hilbert--Burch resolutions,
    and exact ideal-invariance checks for the four reduced special projective
    orbits in the bounded Tier B diagnostic.

Depends on:
    Exact Eisenstein linear algebra, sparse polynomials, the production
    Hilbert--Burch record type, and the reduced orbit classification.

Must not:
    Construct a sheaf or Serre extension, infer line-bundle data, claim
    quotient descent, or interpret a reduced point scheme as a physical
    carrier constituent.

Phase 0:
    The four reduced length-three ideal presentations are exact research
    artifacts; non-reduced schemes, Serre data, and global descent remain
    unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialIdeal
from onetheory.models.heterotic_schoen.visible import HilbertBurchResolution, PointScheme

from .dp9_actions import published_coordinate_images
from .tier_b_orbits import ProjectiveOrbit, tier_b_reduced_orbit_classification

Monomial = tuple[int, int, int]

_QUADRATIC_MONOMIALS: tuple[Monomial, ...] = tuple(
    sorted(
        ((a, b, 2 - a - b) for a in range(3) for b in range(3 - a)),
        reverse=True,
    )
)
_CUBIC_MONOMIALS: tuple[Monomial, ...] = tuple(
    sorted(
        ((a, b, 3 - a - b) for a in range(4) for b in range(4 - a)),
        reverse=True,
    )
)
_LINEAR_MONOMIALS: tuple[Monomial, ...] = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def _evaluate_monomial(point: tuple[Eisenstein, ...], monomial: Monomial) -> Eisenstein:
    """Evaluate one homogeneous monomial at an exact projective point."""

    result = Eisenstein(1)
    for value, exponent in zip(point, monomial, strict=True):
        result *= value**exponent
    return result


def _polynomial_from_vector(
    monomials: tuple[Monomial, ...],
    coefficients: tuple[Eisenstein, ...],
) -> Polynomial:
    """Convert one exact homogeneous coefficient vector to a polynomial."""

    return Polynomial(
        zip(monomials, coefficients, strict=True),
        variable_count=3,
        scalar_type=Eisenstein,
    )


def _coefficient_vector(
    polynomial: Polynomial,
    monomials: tuple[Monomial, ...],
) -> tuple[Eisenstein, ...]:
    """Return one polynomial's exact coordinates in a homogeneous basis."""

    return tuple(
        polynomial.coefficient(monomial)
        for monomial in monomials
    )


def _quadratic_vanishing_basis(orbit: ProjectiveOrbit) -> tuple[Polynomial, ...]:
    """Compute the exact degree-two vanishing space of a reduced orbit."""

    evaluation = Matrix(
        tuple(
            tuple(_evaluate_monomial(point, monomial) for monomial in _QUADRATIC_MONOMIALS)
            for point in orbit.points
        ),
        scalar_type=Eisenstein,
    )
    nullspace = evaluation.nullspace()
    if len(nullspace) != 3:
        raise ValueError("a reduced length-three orbit must have three quadratic generators")
    return tuple(
        _polynomial_from_vector(_QUADRATIC_MONOMIALS, vector.values)
        for vector in nullspace
    )


def _linear_syzygy_matrix(
    generators: tuple[Polynomial, ...],
) -> tuple[tuple[Polynomial, ...], ...]:
    """Compute a two-column linear syzygy matrix for three quadrics."""

    equations = []
    for cubic in _CUBIC_MONOMIALS:
        row = []
        for generator in generators:
            for variable in range(3):
                predecessor = tuple(
                    exponent - (index == variable)
                    for index, exponent in enumerate(cubic)
                )
                row.append(
                    generator.coefficient(predecessor)
                    if min(predecessor) >= 0
                    else Eisenstein(0)
                )
        equations.append(tuple(row))
    syzygies = Matrix(tuple(equations), scalar_type=Eisenstein).nullspace()
    if len(syzygies) != 2:
        raise ValueError("three reduced points must have two independent linear syzygies")
    columns = []
    for syzygy in syzygies:
        entries = []
        for generator in range(3):
            entries.append(
                _polynomial_from_vector(
                    _LINEAR_MONOMIALS,
                    tuple(syzygy.values[3 * generator + index] for index in range(3)),
                )
            )
        columns.append(tuple(entries))
    matrix = tuple(
        tuple(columns[column][row] for column in range(2))
        for row in range(3)
    )
    for column in range(2):
        relation = sum(
            (matrix[row][column] * generators[row] for row in range(3)),
            Polynomial.zero(3, scalar_type=Eisenstein),
        )
        if not relation.is_zero():
            raise ValueError("linear syzygy construction failed its relation check")
    return matrix


def _span_contains(
    basis: tuple[Polynomial, ...],
    candidate: Polynomial,
    monomials: tuple[Monomial, ...],
) -> bool:
    """Check exact membership of one homogeneous polynomial in a span."""

    basis_matrix = Matrix(
        tuple(_coefficient_vector(item, monomials) for item in basis),
        scalar_type=Eisenstein,
    )
    extended = Matrix(
        (*basis_matrix.rows, _coefficient_vector(candidate, monomials)),
        scalar_type=Eisenstein,
    )
    return basis_matrix.rank() == extended.rank()


def _invariant_under(
    generators: tuple[Polynomial, ...],
    name: str,
) -> bool:
    """Check exact preservation of the quadratic vanishing space."""

    images = published_coordinate_images(name)
    return all(
        _span_contains(
            generators,
            generator.substitute_monomials(images),
            _QUADRATIC_MONOMIALS,
        )
        for generator in generators
    )


@dataclass(frozen=True, slots=True)
class ReducedOrbitScheme:
    """An exact Hilbert--Burch presentation of one reduced orbit scheme."""

    orbit: ProjectiveOrbit
    generators: tuple[Polynomial, ...]
    resolution: HilbertBurchResolution
    ideal: PolynomialIdeal
    p_invariant: bool
    t_invariant: bool

    def __post_init__(self) -> None:
        if self.orbit.size != 3:
            raise ValueError("the reduced scheme constructor requires a length-three orbit")
        if len(self.generators) != 3 or not self.resolution.verifies_generators():
            raise ValueError("reduced orbit generators failed Hilbert--Burch verification")
        if self.ideal.generators != self.generators:
            raise ValueError("the ideal record must use the declared quadratic generators")

    @property
    def length(self) -> int:
        """Return the exact projective scheme length."""

        return int(self.resolution.scheme_length)

    @property
    def exact(self) -> bool:
        """Return the complete reduced ideal certificate."""

        return (
            self.length == 3
            and self.resolution.verifies_generators()
            and self.p_invariant
            and self.t_invariant
        )

    @property
    def point_scheme(self) -> PointScheme:
        """Return the production point-scheme record without physical promotion."""

        return PointScheme(self.orbit.identifier, self.generators, self.resolution)

    def as_record(self) -> dict[str, object]:
        """Serialize the exact reduced scheme presentation."""

        return {
            "orbit": self.orbit.identifier,
            "length": self.length,
            "generators": [
                {
                    "terms": [
                        {"exponents": list(exponents), "coefficient": str(coefficient)}
                        for exponents, coefficient in generator.terms
                    ]
                }
                for generator in self.generators
            ],
            "hilbert_burch": {
                "matrix": [
                    [
                        {
                            "terms": [
                                {
                                    "exponents": list(exponents),
                                    "coefficient": str(coefficient),
                                }
                                for exponents, coefficient in entry.terms
                            ]
                        }
                        for entry in row
                    ]
                    for row in self.resolution.matrix
                ],
                "scheme_length": str(self.resolution.scheme_length),
                "verifies_generators": self.resolution.verifies_generators(),
            },
            "p_invariant": self.p_invariant,
            "t_invariant": self.t_invariant,
            "exact": self.exact,
            "status": (
                "exact reduced orbit ideal and Hilbert--Burch presentation; "
                "Serre construction and quotient descent remain unresolved"
            ),
        }


def _scheme(orbit: ProjectiveOrbit) -> ReducedOrbitScheme:
    """Construct one exact reduced orbit scheme."""

    generators = _quadratic_vanishing_basis(orbit)
    resolution = HilbertBurchResolution(
        orbit.identifier,
        _linear_syzygy_matrix(generators),
        generators,
        (1, 0, -3, 2),
    )
    result = ReducedOrbitScheme(
        orbit,
        generators,
        resolution,
        PolynomialIdeal(
            generators,
            variable_count=3,
            scalar_type=Eisenstein,
        ),
        _invariant_under(generators, "P"),
        _invariant_under(generators, "T"),
    )
    if not result.exact:
        raise ValueError("reduced orbit scheme failed exact gates")
    return result


@cache
def tier_b_reduced_orbit_schemes() -> tuple[ReducedOrbitScheme, ...]:
    """Construct all four exact reduced special-orbit presentations."""

    return tuple(
        _scheme(orbit)
        for orbit in tier_b_reduced_orbit_classification().special_orbits
    )


__all__ = [
    "ReducedOrbitScheme",
    "tier_b_reduced_orbit_schemes",
]
