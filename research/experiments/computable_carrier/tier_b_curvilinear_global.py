"""Construct exact global specializations of Tier B curvilinear families.

Owns:
    Jet-condition linear algebra on the three-point coordinate orbit, exact
    homogeneous generators, Hilbert--Burch syzygies, projective transport to
    all four special reduced orbits, and P/T ideal-invariance checks for the
    nonzero Eisenstein-parameter curvilinear length-three family.

Depends on:
    Exact Eisenstein matrices and sparse polynomials, the production
    Hilbert--Burch record, the published deck substitutions, and the special
    Tier B orbit classification. It does not consume observations.

Must not:
    Treat an Eisenstein specialization as a physical coefficient, call a
    global ideal a Serre constituent, infer quotient descent, or claim
    stability, spectrum, or carrier promotion. Symbolic parameter-space
    elimination and global sheaf linearization remain outside this module.

Phase 0:
    Exact global length-nine ideal specializations are constructed for every
    declared nonzero parameter input; Serre extensions and descent remain
    unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialIdeal
from onetheory.models.heterotic_schoen.visible import (
    HilbertBurchResolution,
    PointScheme,
)

from .dp9_actions import published_coordinate_images
from .tier_b_orbits import tier_b_reduced_orbit_classification
from .tier_b_reduced_thickenings import _transport_images

Monomial = tuple[int, int, int]
Axis = str

_COORDINATE_ORBIT_INVERSES: tuple[
    tuple[tuple[int, int, int], ...], ...
] = (
    ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
    ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
)


def _homogeneous_monomials(degree: int) -> tuple[Monomial, ...]:
    """Enumerate the normalized three-variable monomial basis of one degree."""

    return tuple(
        sorted(
            (
                (first, second, degree - first - second)
                for first in range(degree + 1)
                for second in range(degree + 1 - first)
            ),
            reverse=True,
        )
    )


def _transport_monomial(
    monomial: Monomial,
    images: tuple[tuple[int, int, int], ...],
) -> Monomial:
    """Transport one monomial through a permutation of coordinates."""

    result = [0, 0, 0]
    for power, image in zip(monomial, images, strict=True):
        for index, exponent in enumerate(image):
            result[index] += power * exponent
    return tuple(result)


def _jet_matrix(degree: int, axis: Axis, parameter: Eisenstein) -> Matrix:
    """Build exact vanishing equations for all three completed local jets."""

    if axis not in ("u", "v"):
        raise ValueError("curvilinear axes must be u or v")
    monomials = _homogeneous_monomials(degree)
    rows = []
    for images in _COORDINATE_ORBIT_INVERSES:
        for jet in range(3):
            row = []
            for monomial in monomials:
                transformed = _transport_monomial(monomial, images)
                if axis == "u":
                    power = transformed[1] + 2 * transformed[2]
                    coefficient = parameter**transformed[2]
                else:
                    power = 2 * transformed[1] + transformed[2]
                    coefficient = parameter**transformed[1]
                row.append(coefficient if power == jet else Eisenstein(0))
            rows.append(tuple(row))
    return Matrix(rows, scalar_type=Eisenstein)


def _polynomial_from_vector(
    monomials: tuple[Monomial, ...],
    vector: tuple[Eisenstein, ...],
) -> Polynomial:
    """Convert one exact homogeneous coefficient vector to a polynomial."""

    return Polynomial(
        zip(monomials, vector, strict=True),
        variable_count=3,
        scalar_type=Eisenstein,
    )


def _coefficient_matrix(
    polynomials: tuple[Polynomial, ...],
    monomials: tuple[Monomial, ...],
) -> Matrix:
    """Build one exact coefficient matrix for a homogeneous span."""

    return Matrix(
        tuple(
            tuple(polynomial.coefficient(monomial) for monomial in monomials)
            for polynomial in polynomials
        ),
        scalar_type=Eisenstein,
    )


def _coordinate_generators(axis: Axis, parameter: Eisenstein) -> tuple[Polynomial, ...]:
    """Construct the cubic and complementary quartic jet-vanishing generators."""

    cubic_monomials = _homogeneous_monomials(3)
    cubic_space = _jet_matrix(3, axis, parameter).nullspace()
    if len(cubic_space) != 1:
        raise ValueError("the curvilinear union must have one cubic generator")
    cubic = _polynomial_from_vector(cubic_monomials, cubic_space[0].values)

    quartic_monomials = _homogeneous_monomials(4)
    quartic_space = _jet_matrix(4, axis, parameter).nullspace()
    if len(quartic_space) != 6:
        raise ValueError("the curvilinear union must have six quartic sections")
    quartics = tuple(
        _polynomial_from_vector(quartic_monomials, vector.values)
        for vector in quartic_space
    )
    products = tuple(
        cubic * Polynomial.monomial(monomial, scalar_type=Eisenstein)
        for monomial in ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    )
    basis = list(products)
    rank = _coefficient_matrix(tuple(basis), quartic_monomials).rank()
    selected = []
    for quartic in quartics:
        extended_rank = _coefficient_matrix(
            (*basis, quartic),
            quartic_monomials,
        ).rank()
        if extended_rank > rank:
            selected.append(quartic)
            basis.append(quartic)
            rank = extended_rank
    if len(selected) != 3 or rank != 6:
        raise ValueError("quartic jet sections did not produce a minimal complement")
    return (cubic, *selected)


def _syzygy_matrix(generators: tuple[Polynomial, ...]) -> tuple[tuple[Polynomial, ...], ...]:
    """Compute the three exact degree-five syzygies of the four generators."""

    if tuple(generator.degree for generator in generators) != (3, 4, 4, 4):
        raise ValueError("curvilinear generators require degrees (3, 4, 4, 4)")
    coefficient_bases = (
        _homogeneous_monomials(2),
        _homogeneous_monomials(1),
        _homogeneous_monomials(1),
        _homogeneous_monomials(1),
    )
    unknowns = tuple(
        (generator, monomial)
        for generator, basis in enumerate(coefficient_bases)
        for monomial in basis
    )
    target_monomials = _homogeneous_monomials(5)
    rows = []
    for target in target_monomials:
        row = []
        for generator, monomial in unknowns:
            predecessor = tuple(
                target_coordinate - coefficient_coordinate
                for target_coordinate, coefficient_coordinate in zip(
                    target,
                    monomial,
                    strict=True,
                )
            )
            row.append(
                generators[generator].coefficient(predecessor)
                if min(predecessor) >= 0
                else Eisenstein(0)
            )
        rows.append(tuple(row))
    syzygies = Matrix(rows, scalar_type=Eisenstein).nullspace()
    if len(syzygies) != 3:
        raise ValueError("the curvilinear Hilbert--Burch syzygy space must have rank three")
    columns = []
    for syzygy in syzygies:
        entries = []
        offset = 0
        for basis in coefficient_bases:
            entries.append(
                _polynomial_from_vector(
                    basis,
                    syzygy.values[offset : offset + len(basis)],
                )
            )
            offset += len(basis)
        columns.append(tuple(entries))
    return tuple(
        tuple(columns[column][row] for column in range(3))
        for row in range(4)
    )


def _invariant(generators: tuple[Polynomial, ...], name: str) -> bool:
    """Check exact degreewise ideal preservation under one deck generator."""

    images = published_coordinate_images(name)
    for generator in generators:
        same_degree = tuple(item for item in generators if item.degree == generator.degree)
        monomials = _homogeneous_monomials(generator.degree)
        basis = _coefficient_matrix(same_degree, monomials)
        candidate = generator.substitute_monomials(images)
        extended = Matrix(
            (*basis.rows, tuple(candidate.coefficient(monomial) for monomial in monomials)),
            scalar_type=Eisenstein,
        )
        if basis.rank() != extended.rank():
            return False
    return True


@dataclass(frozen=True, slots=True)
class TierBGlobalCurvilinearSpecialization:
    """One exact global length-nine curvilinear specialization."""

    orbit_identifier: str
    family: Axis
    parameter: Eisenstein
    generators: tuple[Polynomial, ...]
    resolution: HilbertBurchResolution
    ideal: PolynomialIdeal
    jet_constraint_rank: int
    p_invariant: bool
    t_invariant: bool

    def __post_init__(self) -> None:
        if self.family not in ("u", "v"):
            raise ValueError("curvilinear families must use u or v")
        if self.parameter.is_zero():
            raise ValueError("the curvilinear family parameter must be nonzero")
        if tuple(generator.degree for generator in self.generators) != (3, 4, 4, 4):
            raise ValueError("global curvilinear generators have incompatible degrees")

    @property
    def name(self) -> str:
        """Return a deterministic nonphysical specialization identifier."""

        return f"{self.orbit_identifier}:curvilinear-{self.family}:{self.parameter}"

    @property
    def length(self) -> int:
        """Return the exact projective length from the Hilbert numerator."""

        return int(self.resolution.scheme_length)

    @property
    def point_scheme(self) -> PointScheme:
        """Return the exact point-scheme wrapper without physical promotion."""

        return PointScheme(self.name, self.generators, self.resolution)

    @property
    def parameter_is_selected_physics(self) -> bool:
        """Return the fixed nonphysical-selection guard for this diagnostic."""

        return False

    @property
    def exact(self) -> bool:
        """Return the global specialization certificate."""

        return (
            self.resolution.verifies_generators()
            and self.length == 9
            and self.ideal.generators == self.generators
            and self.jet_constraint_rank == 9
            and self.p_invariant
            and self.t_invariant
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact specialization and its nonphysical boundary."""

        return {
            "name": self.name,
            "orbit": self.orbit_identifier,
            "family": self.family,
            "parameter": str(self.parameter),
            "parameter_field": "Q(omega)",
            "parameter_is_selected_physics": self.parameter_is_selected_physics,
            "length": self.length,
            "jet_constraint_rank": self.jet_constraint_rank,
            "generators": [
                {
                    "terms": [
                        {"exponents": list(exponents), "coefficient": str(coefficient)}
                        for exponents, coefficient in polynomial.terms
                    ]
                }
                for polynomial in self.generators
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
                "exact nonphysical global curvilinear specialization; Serre "
                "extension and quotient descent remain unresolved"
            ),
        }


def _coordinate_specialization(
    family: Axis,
    parameter: Eisenstein,
) -> tuple[tuple[Polynomial, ...], HilbertBurchResolution, int]:
    """Construct one exact coordinate-orbit specialization."""

    generators = _coordinate_generators(family, parameter)
    resolution = HilbertBurchResolution(
        f"coordinate-curvilinear-{family}",
        _syzygy_matrix(generators),
        generators,
        (1, 0, 0, -1, -3, 3),
    )
    jet_rank = _jet_matrix(3, family, parameter).rank()
    if not resolution.verifies_generators() or int(resolution.scheme_length) != 9:
        raise ValueError("coordinate curvilinear specialization failed Hilbert--Burch checks")
    if jet_rank != 9:
        raise ValueError("coordinate curvilinear jet conditions are not independent")
    return generators, resolution, jet_rank


def _transported_specialization(
    orbit_identifier: str,
    family: Axis,
    parameter: Eisenstein,
    source: tuple[tuple[Polynomial, ...], HilbertBurchResolution, int],
    images: tuple[Polynomial, ...],
) -> TierBGlobalCurvilinearSpecialization:
    """Transport one coordinate specialization to a classified orbit."""

    source_generators, source_resolution, jet_rank = source
    generators = tuple(generator.substitute(images) for generator in source_generators)
    matrix = tuple(
        tuple(entry.substitute(images) for entry in row)
        for row in source_resolution.matrix
    )
    resolution = HilbertBurchResolution(
        f"{orbit_identifier}:curvilinear-{family}",
        matrix,
        generators,
        source_resolution.hilbert_numerator,
    )
    result = TierBGlobalCurvilinearSpecialization(
        orbit_identifier,
        family,
        parameter,
        generators,
        resolution,
        PolynomialIdeal(generators, variable_count=3, scalar_type=Eisenstein),
        jet_rank,
        _invariant(generators, "P"),
        _invariant(generators, "T"),
    )
    if not result.exact:
        raise ValueError("transported curvilinear specialization failed exact gates")
    return result


@cache
def _cached_specializations(
    parameter: Eisenstein,
) -> tuple[TierBGlobalCurvilinearSpecialization, ...]:
    """Construct both curvilinear families over all four special orbits."""

    classification = tier_b_reduced_orbit_classification()
    coordinate_sources = {
        family: _coordinate_specialization(family, parameter)
        for family in ("u", "v")
    }
    result = tuple(
        _transported_specialization(
            orbit.identifier,
            family,
            parameter,
            coordinate_sources[family],
            _transport_images(orbit.points),
        )
        for orbit in classification.special_orbits
        for family in ("u", "v")
    )
    if len(result) != 8 or not all(item.exact for item in result):
        raise ValueError("global curvilinear specialization family failed exact gates")
    return result


def tier_b_global_curvilinear_specializations(
    parameter: object = Eisenstein(1),
) -> tuple[TierBGlobalCurvilinearSpecialization, ...]:
    """Construct exact global specializations for one declared nonzero parameter."""

    value = Eisenstein.coerce(parameter)
    if value.is_zero():
        raise ValueError("the global curvilinear parameter must be nonzero")
    return _cached_specializations(value)


__all__ = [
    "TierBGlobalCurvilinearSpecialization",
    "tier_b_global_curvilinear_specializations",
]
