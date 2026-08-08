"""Enumerate every declared Tier B Schoen-cover outer pair.

Owns:
    The deterministic pairing of all 40 determinant-compatible length-six
    topology candidates with all six exact length-six Serre eigenrays at each
    target shift, plus cover-level sparse Hom certificates for every pair.

Depends on:
    The frozen Tier B topology screen, exact Serre eigenrays, and the sparse
    Schoen-cover outer Hom totalization.

Must not:
    Treat cover Ext as quotient-invariant Ext, construct an outer extension,
    claim descent, or promote a complete cover screen into a physical no-go.

Phase 0:
    This is a research-only exhaustive cover screen; invariant cocycles,
    rank-four bundles, stability, spectra, and physical gates remain open.
"""

from __future__ import annotations

from dataclasses import dataclass
from multiprocessing import get_context

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
class SchoenCoverOuterAudit:
    """One exact sparse cover Hom result for one presentation pair."""

    candidate_index: int
    left_scheme: str
    left_character_pair: tuple[str, str]
    right_scheme: str
    right_character_pair: tuple[str, str]
    cover_ext_one_dimension: int
    squared_zero: bool

    @property
    def exact(self) -> bool:
        """Return whether the sparse cover cochain gates are closed."""

        return self.cover_ext_one_dimension >= 0 and self.squared_zero

    def as_record(self) -> dict[str, object]:
        """Serialize this cover result without a quotient claim."""

        return {
            "candidate_index": self.candidate_index,
            "left_scheme": self.left_scheme,
            "left_character_pair": list(self.left_character_pair),
            "right_scheme": self.right_scheme,
            "right_character_pair": list(self.right_character_pair),
            "cover_ext_one_dimension": self.cover_ext_one_dimension,
            "squared_zero": self.squared_zero,
            "exact": self.exact,
        }


@dataclass(frozen=True, slots=True)
class SchoenCoverOuterFullScreen:
    """The complete declared Tier B cover-level outer Hom screen."""

    audits: tuple[SchoenCoverOuterAudit, ...]
    declared_topology_count: int
    declared_presentation_pair_count: int

    @property
    def all_zero(self) -> bool:
        """Return whether every declared cover Ext-one dimension vanishes."""

        return bool(self.audits) and all(
            audit.cover_ext_one_dimension == 0 for audit in self.audits
        )

    @property
    def exact(self) -> bool:
        """Return whether the complete cover screen passed its exact gates."""

        return (
            len(self.audits) == self.declared_presentation_pair_count
            and all(audit.exact for audit in self.audits)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the complete cover boundary explicitly."""

        return {
            "category": (
                "all determinant-compatible length-six Tier B topology and "
                "Serre-eigenray presentation pairs"
            ),
            "screened_count": len(self.audits),
            "declared_topology_count": self.declared_topology_count,
            "declared_presentation_pair_count": (
                self.declared_presentation_pair_count
            ),
            "all_zero": self.all_zero,
            "exact": self.exact,
            "complete_for_declared_category": True,
            "cover_level_only": True,
            "quotient_invariant_ext_computed": False,
            "outer_extension_constructed": False,
            "promotion_ready": False,
            "status": (
                "complete exact Schoen-cover screen; quotient invariants, "
                "rank-four construction, descent, and physical gates remain "
                "unresolved"
            ),
            "audits": [audit.as_record() for audit in self.audits],
        }


def _length_six_rays(
    target_line_shift: int,
) -> tuple[TierBSerreExtensionRay, ...]:
    """Return all exact rays belonging to the declared length-six type."""

    screen = tier_b_monomial_topology_screen()
    length_six = frozenset(
        name
        for resolution in screen.resolution_types
        if resolution.length == 6
        for name in resolution.scheme_names
    )
    rays = tuple(
        ray
        for ray in tier_b_serre_eigenrays(
            target_line_shift=target_line_shift,
        )
        if ray.cokernel.scheme.name in length_six
    )
    return tuple(
        sorted(
            rays,
            key=lambda ray: (
                ray.cokernel.scheme.name,
                tuple(str(value) for value in ray.character_pair),
            ),
        )
    )


def declared_schoen_outer_pairs() -> tuple[
    tuple[int, MonomialTopologyCandidate, TierBSerreExtensionRay, TierBSerreExtensionRay],
    ...,
]:
    """Return all 1,440 declared candidate/eigenray presentation pairs."""

    screen = tier_b_monomial_topology_screen()
    rays = {
        shift: _length_six_rays(shift)
        for shift in (-6, 0)
    }
    pairs = []
    for candidate_index, candidate in enumerate(
        screen.surviving_topology_candidates,
        1,
    ):
        left_rays = rays[candidate.left_target_line_shift]
        right_rays = rays[candidate.right_target_line_shift]
        pairs.extend(
            (
                candidate_index,
                candidate,
                left_ray,
                right_ray,
            )
            for left_ray in left_rays
            for right_ray in right_rays
        )
    expected = screen.surviving_presentation_count
    if len(pairs) != expected:
        raise ValueError(
            "declared Schoen outer pair count disagrees with topology screen"
        )
    return tuple(pairs)


def _audit_pair(
    pair: tuple[
        int,
        MonomialTopologyCandidate,
        TierBSerreExtensionRay,
        TierBSerreExtensionRay,
    ],
) -> SchoenCoverOuterAudit:
    """Evaluate one pair and release the outer-object cache afterward."""

    candidate_index, candidate, left_ray, right_ray = pair
    try:
        outer = sparse_outer_hom(
            left_ray,
            right_ray,
            candidate.left_factor,
            candidate.left_twist,
            candidate.right_factor,
            candidate.right_twist,
        )
        return SchoenCoverOuterAudit(
            candidate_index,
            left_ray.cokernel.scheme.name,
            tuple(str(value) for value in left_ray.character_pair),
            right_ray.cokernel.scheme.name,
            tuple(str(value) for value in right_ray.character_pair),
            outer.cover_ext_one_dimension,
            outer.squared_zero,
        )
    finally:
        sparse_outer_hom.cache_clear()


def _audit_candidate(
    candidate_data: tuple[
        int,
        MonomialTopologyCandidate,
        tuple[TierBSerreExtensionRay, ...],
        tuple[TierBSerreExtensionRay, ...],
    ],
) -> tuple[SchoenCoverOuterAudit, ...]:
    """Evaluate one topology candidate while reusing worker-local caches."""

    candidate_index, candidate, left_rays, right_rays = candidate_data
    return tuple(
        _audit_pair((candidate_index, candidate, left_ray, right_ray))
        for left_ray in left_rays
        for right_ray in right_rays
    )


def schoen_cover_outer_full_screen(
    workers: int = 1,
) -> SchoenCoverOuterFullScreen:
    """Compute every declared Tier B cover-level outer Hom pair.

    ``workers`` controls independent candidate-level processes.  Each process
    retains only reusable line-bundle maps and releases completed outer
    totalizations, keeping the exhaustive screen deterministic.
    """

    if isinstance(workers, bool) or not isinstance(workers, int) or workers < 1:
        raise ValueError("workers must be a positive integer")
    screen = tier_b_monomial_topology_screen()
    rays = {
        shift: _length_six_rays(shift)
        for shift in (-6, 0)
    }
    candidate_data = tuple(
        (
            candidate_index,
            candidate,
            rays[candidate.left_target_line_shift],
            rays[candidate.right_target_line_shift],
        )
        for candidate_index, candidate in enumerate(
            screen.surviving_topology_candidates,
            1,
        )
    )
    if workers == 1:
        grouped = tuple(map(_audit_candidate, candidate_data))
    else:
        with get_context("fork").Pool(processes=workers) as pool:
            grouped = tuple(pool.map(_audit_candidate, candidate_data))
    audits = tuple(audit for group in grouped for audit in group)
    result = SchoenCoverOuterFullScreen(
        audits,
        len(screen.surviving_topology_candidates),
        screen.surviving_presentation_count,
    )
    if not result.exact:
        raise ValueError("complete Schoen cover outer screen failed exact gates")
    return result


__all__ = [
    "SchoenCoverOuterAudit",
    "SchoenCoverOuterFullScreen",
    "declared_schoen_outer_pairs",
    "schoen_cover_outer_full_screen",
]
