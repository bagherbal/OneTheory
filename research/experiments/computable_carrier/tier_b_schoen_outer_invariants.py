"""Compute exact quotient-invariant Tier B Schoen outer cocycles.

Owns:
    Deterministic pair identities, simultaneous deck-invariant Hom
    subcomplexes, and explicit invariant Ext-one cocycle certificates for the
    declared length-six Tier B Schoen presentations.

Depends on:
    The frozen cover-level outer screen, sparse deck actions, exact invariant
    restriction, and root-normalized sparse cohomology representatives.

Must not:
    Infer a rank-four bundle from an invariant class, identify distinct
    extension coordinates without an automorphism calculation, or claim
    local freeness, descent, stability, or a physical carrier.

Phase 0:
    Pair-level invariant cocycles are executable; the exhaustive screen,
    automorphism orbits, and rank-four construction remain open.
"""

from __future__ import annotations

from dataclasses import dataclass

from .schoen_sparse_outer import sparse_outer_hom
from .schoen_sparse_outer_actions import (
    SparseInvariantCocycleBasis,
    SparseOuterInvariantAudit,
    sparse_outer_invariant_audit,
    sparse_outer_invariant_cocycles,
)
from .tier_b_monomial_topology import MonomialTopologyCandidate
from .tier_b_schoen_outer_full import (
    _clear_worker_caches,
    declared_schoen_outer_pairs,
)
from .tier_b_serre_extensions import TierBSerreExtensionRay

InvariantPairTask = tuple[
    int,
    int,
    int,
    MonomialTopologyCandidate,
    TierBSerreExtensionRay,
    TierBSerreExtensionRay,
    int,
]


@dataclass(frozen=True, slots=True)
class SchoenInvariantOuterPairAudit:
    """One exact invariant Ext-one and cocycle audit for a declared pair."""

    global_pair_index: int
    candidate_pair_index: int
    candidate_index: int
    candidate: MonomialTopologyCandidate
    left_ray: TierBSerreExtensionRay
    right_ray: TierBSerreExtensionRay
    invariant: SparseOuterInvariantAudit
    cocycles: SparseInvariantCocycleBasis

    @property
    def exact(self) -> bool:
        """Return whether the quotient complex and cocycle gates all close."""

        return (
            self.invariant.exact
            and self.cocycles.exact
            and self.cocycles.representatives.domain.dimension
            == self.invariant.invariant_ext_one_dimension
        )

    def as_record(self) -> dict[str, object]:
        """Serialize this pair without constructing an outer extension."""

        return {
            "global_pair_index": self.global_pair_index,
            "candidate_pair_index": self.candidate_pair_index,
            "candidate_index": self.candidate_index,
            "topology": self.candidate.as_record(),
            "left_scheme": self.left_ray.cokernel.scheme.name,
            "left_character_pair": [
                str(value) for value in self.left_ray.character_pair
            ],
            "right_scheme": self.right_ray.cokernel.scheme.name,
            "right_character_pair": [
                str(value) for value in self.right_ray.character_pair
            ],
            "deck_action": {
                "p_chain_map": self.invariant.deck.p_chain_map,
                "t_chain_map": self.invariant.deck.t_chain_map,
                "p_order_three": self.invariant.deck.p_order_three,
                "t_order_three": self.invariant.deck.t_order_three,
                "commute": self.invariant.deck.commute,
                "exact": self.invariant.deck.exact,
            },
            "invariant_subcomplex": self.invariant.as_record(),
            "cocycle_basis": self.cocycles.as_record(),
            "automorphism_action_computed": False,
            "canonical_orbits_computed": False,
            "outer_extension_constructed": False,
            "exact": self.exact,
            "status": (
                "exact invariant Ext-one cocycles; automorphism orbits and "
                "rank-four construction remain unresolved"
            ),
        }


def declared_schoen_invariant_pair_tasks(
    cover_dimensions: tuple[int, ...],
) -> tuple[InvariantPairTask, ...]:
    """Attach certified cover dimensions to all declared pair identities."""

    pairs = declared_schoen_outer_pairs()
    if len(cover_dimensions) != len(pairs):
        raise ValueError("cover dimensions do not span the declared pair category")
    tasks = []
    for global_pair_index, (pair, cover_dimension) in enumerate(
        zip(pairs, cover_dimensions, strict=True),
        1,
    ):
        candidate_index, candidate, left_ray, right_ray = pair
        candidate_pair_index = (global_pair_index - 1) % 36 + 1
        tasks.append(
            (
                global_pair_index,
                candidate_pair_index,
                candidate_index,
                candidate,
                left_ray,
                right_ray,
                cover_dimension,
            )
        )
    return tuple(tasks)


def audit_schoen_invariant_pair(
    task: InvariantPairTask,
) -> SchoenInvariantOuterPairAudit:
    """Compute one exact invariant pair and release all heavy map caches."""

    (
        global_pair_index,
        candidate_pair_index,
        candidate_index,
        candidate,
        left_ray,
        right_ray,
        cover_dimension,
    ) = task
    try:
        outer = sparse_outer_hom(
            left_ray,
            right_ray,
            candidate.left_factor,
            candidate.left_twist,
            candidate.right_factor,
            candidate.right_twist,
        )
        invariant = sparse_outer_invariant_audit(outer, cover_dimension)
        cocycles = sparse_outer_invariant_cocycles(invariant)
        result = SchoenInvariantOuterPairAudit(
            global_pair_index,
            candidate_pair_index,
            candidate_index,
            candidate,
            left_ray,
            right_ray,
            invariant,
            cocycles,
        )
        if not result.exact:
            raise ValueError("Schoen invariant pair failed an exact cocycle gate")
        return result
    finally:
        _clear_worker_caches()


__all__ = [
    "InvariantPairTask",
    "SchoenInvariantOuterPairAudit",
    "audit_schoen_invariant_pair",
    "declared_schoen_invariant_pair_tasks",
]
