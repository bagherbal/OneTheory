"""Close the finite projective outer-extension frontier without inventing a class.

Owns:
    The scoped no-candidate result obtained from all exact projective Tier A
    ray-pair invariant Ext audits.

Depends on:
    The complete projective Hom ray-pair audit and its exact trivial-character
    projectors. It does not consume observations or reference cocycles.

Must not:
    Promote a projective no-candidate result to a global dP9 no-go, create a
    generic extension representative, or silently continue with a split bundle.

Phase 0:
    The declared projective presentation category has no invariant outer class;
    global dP9 comparison and later Tier B work remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from .projective_hom_search import (
    TierAProjectiveHomPairAudit,
    tier_a_projective_hom_pair_audits,
)


@dataclass(frozen=True, slots=True)
class ProjectiveOuterFrontier:
    """The exact finite projective outer-extension result."""

    pair_audits: tuple[TierAProjectiveHomPairAudit, ...]

    @property
    def invariant_class_count(self) -> int:
        """Return the total invariant projective Ext-one dimension."""

        return sum(item.invariant_ext_one_dimension for item in self.pair_audits)

    @property
    def rank_four_candidate_count(self) -> int:
        """Return the number of equivariant rank-four classes in this scope."""

        return self.invariant_class_count

    @property
    def scoped_no_candidate(self) -> bool:
        """Return whether the declared projective category is empty."""

        return bool(self.pair_audits) and self.rank_four_candidate_count == 0

    def as_record(self) -> dict[str, object]:
        """Serialize the no-candidate gate without widening its scope."""

        return {
            "pair_count": len(self.pair_audits),
            "pair_invariant_dimensions": [
                {
                    "left_character_pair": [
                        str(value) for value in item.left.character_pair
                    ],
                    "right_character_pair": [
                        str(value) for value in item.right.character_pair
                    ],
                    "invariant_ext1_dimension": item.invariant_ext_one_dimension,
                }
                for item in self.pair_audits
            ],
            "invariant_class_count": self.invariant_class_count,
            "rank_four_candidate_count": self.rank_four_candidate_count,
            "scoped_no_candidate": self.scoped_no_candidate,
            "status": (
                "scoped projective-presentation no-candidate result; global dP9 "
                "Ext comparison and Tier B search remain unresolved"
            ),
        }


def tier_a_projective_outer_frontier(
    pair_audits: tuple[TierAProjectiveHomPairAudit, ...] | None = None,
) -> ProjectiveOuterFrontier:
    """Return the finite projective outer-extension frontier."""

    return ProjectiveOuterFrontier(
        tier_a_projective_hom_pair_audits() if pair_audits is None else pair_audits
    )


__all__ = [
    "ProjectiveOuterFrontier",
    "tier_a_projective_outer_frontier",
]
