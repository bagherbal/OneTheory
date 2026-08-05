"""Audit every Tier A projective Hom ray pair.

Owns:
    Construction of presentation-level candidates from every locally free I3
    and I6 eigenray, exact projective hypercohomology for all six pairs, and
    their full deck-action and invariant-projector records.

Depends on:
    The derived Tier A Serre eigenray enumeration, the polynomial Hom complex,
    projective line-bundle cohomology, and exact resolution actions.

Must not:
    Treat the six projective pairs as the complete dP9 Ext search, infer a
    global quotient no-go, or promote a zero invariant space to a carrier.

Phase 0:
    All declared presentation ray pairs are audited exactly; dP9
    sheafification, global descent, and physical promotion remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .polynomial_hom import polynomial_hom_complex
from .projective_hom_action import (
    ProjectiveHomDeckAudit,
    projective_hom_deck_audit,
)
from .projective_hyperhom import (
    ProjectiveHomHypercohomology,
    projective_hom_hypercohomology,
)
from .resolution_actions import ResolutionActionPair, tier_a_resolution_actions
from .serre_pushout import (
    SerrePushoutCandidate,
    _relation_matrix,
    tier_a_serre_pushouts,
)
from .serre_rays import (
    SerreEigenclassVariant,
    tier_a_serre_eigenclass_variants,
)


def _presentation_candidate(
    variant: SerreEigenclassVariant,
    base: SerrePushoutCandidate,
) -> SerrePushoutCandidate:
    """Attach one exact eigenray to its matching presentation metadata."""

    if variant.scheme != base.scheme.name:
        raise ValueError("an eigenray must match its presentation scheme")
    return replace(
        base,
        extension_map=variant.extension_map,
        character_pair=variant.character_pair,
        relation=_relation_matrix(base.scheme, variant.extension_map),
        local_fitting=variant.local_fitting,
    )


@dataclass(frozen=True, slots=True)
class TierAProjectiveHomPairAudit:
    """One exact projective Hom and deck audit for a lawful ray pair."""

    left: SerreEigenclassVariant
    right: SerreEigenclassVariant
    hypercohomology: ProjectiveHomHypercohomology
    deck: ProjectiveHomDeckAudit

    @property
    def raw_ext_one_dimension(self) -> int:
        """Return the exact projective degree-one dimension."""

        return self.hypercohomology.ext_one_dimension

    @property
    def invariant_ext_one_dimension(self) -> int:
        """Return the exact trivial-character degree-one dimension."""

        return self.deck.invariant_ext_one_dimension

    def as_record(self) -> dict[str, object]:
        """Serialize the pair, full cochain data, and action gates."""

        return {
            "left_ray": self.left.as_record(),
            "right_ray": self.right.as_record(),
            "raw_ext1_dimension": self.raw_ext_one_dimension,
            "invariant_ext1_dimension": self.invariant_ext_one_dimension,
            "hypercohomology": self.hypercohomology.as_record(),
            "deck_action": self.deck.as_record(),
            "status": (
                "exact projective-presentation ray-pair audit; global dP9 "
                "sheafification and quotient descent remain unresolved"
            ),
        }


def tier_a_projective_hom_pair_audits(
    candidates: tuple[SerrePushoutCandidate, ...] | None = None,
    actions: tuple[ResolutionActionPair, ...] | None = None,
    variants: tuple[SerreEigenclassVariant, ...] | None = None,
) -> tuple[TierAProjectiveHomPairAudit, ...]:
    """Audit every pair in the declared two-I3-by-three-I6 ray family."""

    selected = tier_a_serre_pushouts() if candidates is None else candidates
    resolution_actions = tier_a_resolution_actions() if actions is None else actions
    if len(selected) != 2 or tuple(item.scheme.name for item in selected) != ("I3", "I6"):
        raise ValueError("Tier A ray pairs require I3 and I6 presentations in order")
    if len(resolution_actions) != 2:
        raise ValueError("Tier A ray pairs require I3 and I6 resolution actions")
    eigenrays = (
        tier_a_serre_eigenclass_variants(selected, resolution_actions)
        if variants is None
        else variants
    )
    by_scheme: dict[str, list[SerreEigenclassVariant]] = {"I3": [], "I6": []}
    for variant in eigenrays:
        if variant.scheme not in by_scheme:
            raise ValueError(f"unexpected Tier A scheme: {variant.scheme}")
        by_scheme[variant.scheme].append(variant)
    if not by_scheme["I3"] or not by_scheme["I6"]:
        raise ValueError("Tier A ray enumeration must contain both schemes")
    audits = []
    for left_variant in by_scheme["I3"]:
        left = _presentation_candidate(left_variant, selected[0])
        for right_variant in by_scheme["I6"]:
            right = _presentation_candidate(right_variant, selected[1])
            hypercohomology = projective_hom_hypercohomology(
                polynomial_hom_complex(left, right)
            )
            deck = projective_hom_deck_audit(
                hypercohomology,
                left_candidate=left,
                right_candidate=right,
                resolution_pairs=resolution_actions,
            )
            audits.append(
                TierAProjectiveHomPairAudit(
                    left_variant,
                    right_variant,
                    hypercohomology,
                    deck,
                )
            )
    return tuple(audits)


__all__ = [
    "TierAProjectiveHomPairAudit",
    "tier_a_projective_hom_pair_audits",
]
