"""Regress the persisted strict alternate up-Higgs Hom cochain.

Owns:
    Exact term round-trip, full differential, and right-resolution support.

Depends on:
    The frozen alternate constituent pair and content-addressed Hom terms.

Must not:
    Identify a Hom term as a tensor or exterior-cone Higgs cocycle.

Phase 0:
    Research integration checks for reusable full-chain input.
"""

import json
from collections import Counter

from onetheory.math.numbers import OMEGA
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_up_higgs_hom_representative import (
    FULL_OUTPUT,
    load_alternate_up_higgs_hom_full_cochain,
)
from research.experiments.scientific_genesis.distinct_constituent_ray_screen import (
    lift_joint_character_ray,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    _constituent,
    mixed_schoen_constituents,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_representatives import (
    _cochain_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import (
    _MixedContraction,
)
from research.experiments.scientific_genesis.published_constituent_deck_actions import (
    published_constituent_deck_actions,
)


def test_saved_hom_terms_remain_an_exact_full_cycle() -> None:
    """Reloaded terms retain the source Hom differential and right support."""

    cochain = load_alternate_up_higgs_hom_full_cochain()
    first = mixed_schoen_constituents()[0]
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    right = _constituent(ray, "I6-ray-0-1", 2, (-1, 1, 0))
    assert len(cochain.terms) == 324
    assert _MixedContraction(first, right).differential(cochain).is_zero()
    assert dict(Counter(basis.component.right_index for basis, _ in cochain.terms)) == {
        1: 18, 2: 18, 3: 27, 4: 18, 5: 81, 6: 81, 7: 81,
    }


def test_full_hom_artifact_has_exact_round_trip_provenance() -> None:
    """The stored source data is content-addressed but not a Higgs lift."""

    payload = json.loads(FULL_OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    cochain = load_alternate_up_higgs_hom_full_cochain()
    assert digest == _canonical_digest(payload)
    assert payload["term_count"] == len(payload["terms"]) == 324
    assert payload["full_digest"] == _cochain_digest((cochain,))
    assert payload["higgs_tensor_chain_map_constructed"] is False
    assert payload["exterior_cone_higgs_cocycle_constructed"] is False
