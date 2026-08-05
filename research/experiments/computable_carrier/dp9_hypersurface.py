"""Compare projective Hom data with the explicit dP9 hypersurface.

Owns:
    The exact Koszul restriction certificate for the cubic-pencil hypersurface
    in ``P2 x P1`` and its consequence for the current zero-fiber-twist Hom
    presentation category.

Depends on:
    The frozen Schoen cubic pencil, exact P1 line-bundle cohomology dimensions,
    and the projective presentation Hom complexes.

Must not:
    Treat a zero Koszul correction as a comparison for arbitrary fiber twists,
    claim quotient descent or global constituent cohomology, or reuse a
    projective invariant class as a descended dP9 extension.

Phase 0:
    The zero-fiber-twist hypersurface comparison is exact; nonzero fiber twists,
    full dP9 sheafification, and quotient descent remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from .polynomial_hom import PolynomialHomComplex
from .projective_hom_search import (
    TierAProjectiveHomPairAudit,
    tier_a_projective_hom_pair_audits,
)
from .projective_hyperhom import (
    ProjectiveHomHypercohomology,
    projective_hom_hypercohomology,
)


def _p1_dimensions(degree: int) -> tuple[int, int]:
    """Return exact ``(H0,H1)`` dimensions for ``O_P1(degree)``."""

    return (
        (degree + 1 if degree >= 0 else 0),
        (-degree - 1 if degree <= -2 else 0),
    )


@dataclass(frozen=True, slots=True)
class DPSurfaceHomComparison:
    """The exact hypersurface restriction result for one Hom presentation."""

    parent: PolynomialHomComplex
    projective: ProjectiveHomHypercohomology
    fiber_degree: int
    hypersurface_bidegree: tuple[int, int]
    koszul_source_fiber_degree: int
    koszul_correction_dimensions: tuple[tuple[int, tuple[int, int]], ...]

    @property
    def koszul_correction_vanishes(self) -> bool:
        """Return whether every ambient correction cohomology space vanishes."""

        return all(
            dimensions == (0, 0)
            for _, dimensions in self.koszul_correction_dimensions
        )

    @property
    def restriction_is_exact(self) -> bool:
        """Return whether the Koszul sequence gives an isomorphism here."""

        return (
            self.hypersurface_bidegree == (3, 1)
            and self.koszul_source_fiber_degree == self.fiber_degree - 1
            and self.koszul_correction_vanishes
        )

    @property
    def dP9_matches_projective(self) -> bool:
        """Return whether the exact restriction preserves the Hom dimensions."""

        return self.restriction_is_exact and self.projective.ext_one_dimension == (
            self.projective.h0.complex.cohomology_dimension(1)
            + self.projective.h2.complex.cohomology_dimension(-1)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the hypersurface equation and exact restriction gates."""

        return {
            "left_scheme": self.parent.left.scheme.name,
            "right_scheme": self.parent.right.scheme.name,
            "fiber_degree": self.fiber_degree,
            "hypersurface_bidegree": list(self.hypersurface_bidegree),
            "koszul_source_fiber_degree": self.koszul_source_fiber_degree,
            "koszul_correction_dimensions": [
                [degree, list(dimensions)]
                for degree, dimensions in self.koszul_correction_dimensions
            ],
            "koszul_correction_vanishes": self.koszul_correction_vanishes,
            "restriction_is_exact": self.restriction_is_exact,
            "dP9_matches_projective": self.dP9_matches_projective,
            "projective_ext1_dimension": self.projective.ext_one_dimension,
            "status": (
                "exact dP9 hypersurface restriction for zero fiber twist; "
                "nonzero fiber twists and quotient descent remain unresolved"
            ),
        }


def dP9_hypersurface_hom_comparison(
    parent: PolynomialHomComplex,
    projective: ProjectiveHomHypercohomology | None = None,
    fiber_degree: int = 0,
) -> DPSurfaceHomComparison:
    """Compare one presentation Hom complex through the dP9 Koszul sequence."""

    if isinstance(fiber_degree, bool) or not isinstance(fiber_degree, int):
        raise TypeError("fiber degree must be an integer")
    if fiber_degree != 0:
        raise ValueError(
            "the current exact restriction certificate supports fiber degree zero only"
        )
    correction = tuple(
        (
            degree,
            tuple(
                sum(
                    _p1_dimensions(fiber_degree - 1)[index]
                    for _ in module.shifts
                )
                for index in (0, 1)
            ),
        )
        for degree, module in parent.terms
    )
    return DPSurfaceHomComparison(
        parent,
        projective or projective_hom_hypercohomology(parent),
        fiber_degree,
        (3, 1),
        fiber_degree - 1,
        correction,
    )


def tier_a_dp9_hypersurface_comparisons(
    pair_audits: tuple[TierAProjectiveHomPairAudit, ...] | None = None,
) -> tuple[DPSurfaceHomComparison, ...]:
    """Return the exact dP9 comparison for every declared projective ray pair."""

    audits = tier_a_projective_hom_pair_audits() if pair_audits is None else pair_audits
    return tuple(
        dP9_hypersurface_hom_comparison(
            audit.hypercohomology.parent,
            audit.hypercohomology,
        )
        for audit in audits
    )


__all__ = [
    "DPSurfaceHomComparison",
    "dP9_hypersurface_hom_comparison",
    "tier_a_dp9_hypersurface_comparisons",
]
