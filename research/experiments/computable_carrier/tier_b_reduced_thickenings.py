"""Enumerate transported invariant thickenings of special projective orbits.

Owns:
    Exact projective transport of the six certified coordinate-local monomial
    Hilbert--Burch schemes to each of the four special reduced deck orbits,
    with transformed resolutions and independent P/T ideal-invariance checks.

Depends on:
    Exact Eisenstein matrices and linear polynomial substitution, the bounded
    coordinate-local monomial scheme certificates, and reduced orbit data.

Must not:
    Treat transported ideals as Serre constituents, invent extension maps,
    infer global local freeness or quotient descent, or call this finite
    transported category the complete Tier B universe.

Phase 0:
    The 24 transported invariant scheme presentations are exact within their
    declared support/local-type category; Serre construction and descent
    remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialIdeal
from onetheory.models.heterotic_schoen.visible import HilbertBurchResolution, PointScheme

from .dp9_actions import published_coordinate_images
from .tier_b_monomial import InvariantMonomialScheme, tier_b_invariant_monomial_schemes
from .tier_b_orbits import tier_b_reduced_orbit_classification


def _linear_polynomial(values: tuple[Eisenstein, ...]) -> Polynomial:
    """Build one exact linear coordinate form."""

    if len(values) != 3:
        raise ValueError("the projective transport requires three coordinates")
    return Polynomial(
        (
            ((1, 0, 0), values[0]),
            ((0, 1, 0), values[1]),
            ((0, 0, 1), values[2]),
        ),
        variable_count=3,
        scalar_type=Eisenstein,
    )


def _transport_images(orbit_points) -> tuple[Polynomial, ...]:
    """Return the exact inverse-coordinate forms for one special orbit."""

    basis = Matrix(
        tuple(
            tuple(point[column] for column in range(3))
            for point in orbit_points
        ),
        scalar_type=Eisenstein,
    )
    inverse = basis.inverse()
    return tuple(
        _linear_polynomial(tuple(inverse[row][column] for row in range(3)))
        for column in range(3)
    )


def _polynomial_record(polynomial: Polynomial) -> dict[str, object]:
    """Serialize one exact polynomial without physical interpretation."""

    return {
        "terms": [
            {
                "exponents": list(exponents),
                "coefficient": str(coefficient),
            }
            for exponents, coefficient in polynomial.terms
        ]
    }


def _span_contains(
    basis: tuple[Polynomial, ...],
    candidate: Polynomial,
) -> bool:
    """Check exact span membership within one homogeneous degree slice."""

    if not basis or any(item.degree != candidate.degree for item in basis):
        return False
    monomials = tuple(
        sorted(
            {
                exponent
                for item in (*basis, candidate)
                for exponent, _ in item.terms
            },
            reverse=True,
        )
    )
    basis_matrix = Matrix(
        tuple(
            tuple(item.coefficient(monomial) for monomial in monomials)
            for item in basis
        ),
        scalar_type=Eisenstein,
    )
    extended = Matrix(
        (*basis_matrix.rows, tuple(candidate.coefficient(monomial) for monomial in monomials)),
        scalar_type=Eisenstein,
    )
    return basis_matrix.rank() == extended.rank()


def _invariant(generators: tuple[Polynomial, ...], name: str) -> bool:
    """Check ideal preservation degree by degree under one deck generator."""

    images = published_coordinate_images(name)
    for generator in generators:
        same_degree = tuple(item for item in generators if item.degree == generator.degree)
        if not _span_contains(same_degree, generator.substitute_monomials(images)):
            return False
    return True


@dataclass(frozen=True, slots=True)
class TransportedInvariantScheme:
    """One exact transported invariant zero-dimensional scheme presentation."""

    orbit_name: str
    source_scheme: InvariantMonomialScheme
    generators: tuple[Polynomial, ...]
    resolution: HilbertBurchResolution
    ideal: PolynomialIdeal
    p_invariant: bool
    t_invariant: bool

    @property
    def name(self) -> str:
        """Return the deterministic transported scheme identifier."""

        return f"{self.orbit_name}:{self.source_scheme.name}"

    @property
    def length(self) -> int:
        """Return the exact projective scheme length."""

        return int(self.resolution.scheme_length)

    @property
    def point_scheme(self) -> PointScheme:
        """Return the exact production-compatible point-scheme record."""

        return PointScheme(self.name, self.generators, self.resolution)

    @property
    def exact(self) -> bool:
        """Return the complete transported-scheme certificate."""

        return (
            self.resolution.verifies_generators()
            and self.ideal.generators == self.generators
            and self.p_invariant
            and self.t_invariant
            and self.length == int(self.source_scheme.length)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact transported scheme and its finite boundary."""

        return {
            "name": self.name,
            "orbit": self.orbit_name,
            "source_scheme": self.source_scheme.name,
            "source_length": str(self.source_scheme.length),
            "length": self.length,
            "generators": [_polynomial_record(item) for item in self.generators],
            "hilbert_burch": {
                "matrix": [
                    [_polynomial_record(entry) for entry in row]
                    for row in self.resolution.matrix
                ],
                "scheme_length": str(self.resolution.scheme_length),
                "verifies_generators": self.resolution.verifies_generators(),
            },
            "p_invariant": self.p_invariant,
            "t_invariant": self.t_invariant,
            "exact": self.exact,
            "status": (
                "exact transported invariant scheme presentation; Serre "
                "construction and quotient descent remain unresolved"
            ),
        }


def _transport(
    orbit_name: str,
    source_scheme: InvariantMonomialScheme,
    images: tuple[Polynomial, ...],
) -> TransportedInvariantScheme:
    """Transport one certified coordinate-local presentation exactly."""

    generators = tuple(
        generator.substitute(images)
        for generator in source_scheme.ideal.generators
    )
    matrix = tuple(
        tuple(entry.substitute(images) for entry in row)
        for row in source_scheme.resolution.matrix
    )
    resolution = HilbertBurchResolution(
        f"{orbit_name}:{source_scheme.name}",
        matrix,
        generators,
        source_scheme.resolution.hilbert_numerator,
    )
    result = TransportedInvariantScheme(
        orbit_name,
        source_scheme,
        generators,
        resolution,
        PolynomialIdeal(generators, variable_count=3, scalar_type=Eisenstein),
        _invariant(generators, "P"),
        _invariant(generators, "T"),
    )
    if not result.exact:
        raise ValueError("transported invariant scheme failed exact gates")
    return result


@cache
def tier_b_transported_invariant_schemes() -> tuple[TransportedInvariantScheme, ...]:
    """Enumerate all four special orbits times six certified local types."""

    source_schemes = tier_b_invariant_monomial_schemes()
    result = []
    for orbit in tier_b_reduced_orbit_classification().special_orbits:
        images = _transport_images(orbit.points)
        result.extend(
            _transport(orbit.identifier, source_scheme, images)
            for source_scheme in source_schemes
        )
    values = tuple(result)
    if len(values) != 24 or not all(item.exact for item in values):
        raise ValueError("transported Tier B category failed its finite exact gate")
    return values


__all__ = [
    "TransportedInvariantScheme",
    "tier_b_transported_invariant_schemes",
]
