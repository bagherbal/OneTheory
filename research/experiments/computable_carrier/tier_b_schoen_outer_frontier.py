"""Record the exact representative Schoen-cover outer frontier.

Owns:
    The first exact cover-level outer Hom screen for four distinct surviving
    length-six topology orientations and both invariant coordinate-orbit
    schemes at each orientation.

Depends on:
    The finite Tier B topology screen, sparse Schoen cover Hom complexes, and
    exact monomial Serre rays.

Must not:
    Call eight representatives a complete Tier B no-go, infer quotient
    invariants from a cover vanishing, or construct a rank-four bundle.

Phase 0:
    The declared representative screen is exact and deliberately incomplete;
    all topology twists, ray pairs, quotient invariants, and physics remain.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from .schoen_sparse_outer import sparse_outer_hom
from .tier_b_monomial_topology import (
    MonomialTopologyCandidate,
    tier_b_monomial_topology_screen,
)
from .tier_b_serre_extensions import (
    TierBSerreExtensionRay,
    tier_b_serre_eigenrays,
)


@dataclass(frozen=True, slots=True)
class SchoenCoverOuterRepresentative:
    """One exact representative topology/ray cover Hom audit."""

    topology_index: int
    candidate: MonomialTopologyCandidate
    scheme_suffix: str
    cover_ext_one_dimension: int
    squared_zero: bool

    @property
    def exact(self) -> bool:
        """Return whether the cover totalization and dimension are exact."""

        return self.squared_zero and self.cover_ext_one_dimension >= 0

    def as_record(self) -> dict[str, object]:
        """Serialize the scoped cover result without a quotient claim."""

        return {
            "topology_index": self.topology_index,
            "left_factor": self.candidate.left_factor,
            "right_factor": self.candidate.right_factor,
            "left_target_line_shift": self.candidate.left_target_line_shift,
            "right_target_line_shift": self.candidate.right_target_line_shift,
            "left_twist": list(self.candidate.left_twist),
            "right_twist": list(self.candidate.right_twist),
            "scheme_suffix": self.scheme_suffix,
            "cover_ext_one_dimension": self.cover_ext_one_dimension,
            "squared_zero": self.squared_zero,
            "exact": self.exact,
            "status": "representative Schoen-cover result; not a complete frontier",
        }


@dataclass(frozen=True, slots=True)
class SchoenCoverOuterRepresentativeFrontier:
    """The deliberately incomplete exact representative screen."""

    audits: tuple[SchoenCoverOuterRepresentative, ...]
    declared_topology_count: int
    full_presentation_pair_count: int

    @property
    def all_zero(self) -> bool:
        """Return whether every screened cover Ext-one dimension vanishes."""

        return bool(self.audits) and all(
            audit.cover_ext_one_dimension == 0 for audit in self.audits
        )

    @property
    def exact(self) -> bool:
        """Return whether every representative audit passed its exact gates."""

        return (
            len(self.audits) == 8
            and all(audit.exact for audit in self.audits)
            and self.all_zero
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the scoped boundary explicitly."""

        return {
            "category": (
                "four surviving length-six topology orientations, two "
                "coordinate-orbit scheme representatives each"
            ),
            "screened_count": len(self.audits),
            "declared_topology_count": self.declared_topology_count,
            "full_presentation_pair_count": self.full_presentation_pair_count,
            "all_zero": self.all_zero,
            "exact": self.exact,
            "complete_for_declared_category": False,
            "outer_extension_constructed": False,
            "promotion_ready": False,
            "audits": [audit.as_record() for audit in self.audits],
            "status": (
                "exact representative cover screen only; all topology twists, "
                "ray pairs, quotient invariants, and physical gates remain open"
            ),
        }


def _orientation_representatives(
    candidates: tuple[MonomialTopologyCandidate, ...],
) -> tuple[MonomialTopologyCandidate, ...]:
    """Select the first exact candidate for each factor/shift orientation."""

    selected: list[MonomialTopologyCandidate] = []
    seen: set[tuple[int, int, int]] = set()
    for candidate in candidates:
        key = (
            candidate.left_factor,
            candidate.left_target_line_shift,
            candidate.right_target_line_shift,
        )
        if key in seen:
            continue
        seen.add(key)
        selected.append(candidate)
    return tuple(selected)


def _ray(
    rays: tuple[TierBSerreExtensionRay, ...],
    suffix: str,
) -> TierBSerreExtensionRay:
    """Return one deterministic coordinate-orbit ray."""

    return next(
        ray for ray in rays if ray.cokernel.scheme.name.endswith(suffix)
    )


@cache
def schoen_cover_outer_representative_frontier(
) -> SchoenCoverOuterRepresentativeFrontier:
    """Compute the eight declared cover-level representative audits."""

    topology = tier_b_monomial_topology_screen()
    candidates = _orientation_representatives(
        topology.surviving_topology_candidates
    )
    rays = {
        shift: tier_b_serre_eigenrays(target_line_shift=shift)
        for shift in (-6, 0)
    }
    audits = []
    for topology_index, candidate in enumerate(candidates, 1):
        for suffix in ("-1", "-2"):
            left = _ray(rays[candidate.left_target_line_shift], suffix)
            right = _ray(rays[candidate.right_target_line_shift], suffix)
            outer = sparse_outer_hom(
                left,
                right,
                candidate.left_factor,
                candidate.left_twist,
                candidate.right_factor,
                candidate.right_twist,
            )
            audits.append(
                SchoenCoverOuterRepresentative(
                    topology_index,
                    candidate,
                    suffix,
                    outer.cover_ext_one_dimension,
                    outer.squared_zero,
                )
            )
            sparse_outer_hom.cache_clear()
    result = SchoenCoverOuterRepresentativeFrontier(
        tuple(audits),
        len(topology.surviving_topology_candidates),
        topology.surviving_presentation_count,
    )
    if not result.exact:
        raise ValueError("Schoen representative outer frontier failed exact gates")
    return result


__all__ = [
    "SchoenCoverOuterRepresentative",
    "SchoenCoverOuterRepresentativeFrontier",
    "schoen_cover_outer_representative_frontier",
]
