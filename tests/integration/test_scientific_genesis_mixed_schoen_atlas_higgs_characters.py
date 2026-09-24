"""Regression tests for the exact atlas-induced Higgs representation."""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_atlas_higgs_characters import (
    OUTPUT,
)


def test_constituent_atlas_character_ratios_are_derived_exactly() -> None:
    """Full-summand normalization forces one character on each simple factor."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")

    assert digest == _canonical_digest(payload)
    assert payload["constituent_linearization_ratios"] == [
        {
            "constituent": "W1",
            "atlas_over_synchronized_character": [1, 0],
        },
        {
            "constituent": "W2",
            "atlas_over_synchronized_character": [0, 0],
        },
    ]
    assert payload["tensor_atlas_over_synchronized_character"] == [1, 0]
    assert payload["homogeneous_lift_normalization_included"] is True
    assert payload["raw_extension_line_ratio_used_as_tensor_character"] is False
    assert payload["source_pushdown_characters_used_as_construction_input"] is False
    assert payload["deck_generators_relabelled"] is False
    assert payload["character_twist_fitted"] is False


def test_atlas_higgs_characters_refute_the_selected_source_assignment() -> None:
    """The exact atlas tensor representation is not the source-bound multiset."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["exact"] is True
    assert payload["atlas_induced_h1_characters"] == [
        [0, 0],
        [0, 1],
        [1, 0],
        [1, 1],
    ]
    assert payload["atlas_source_action_h1_characters"] == [
        [0, 0],
        [0, 2],
        [2, 0],
        [2, 2],
    ]
    assert payload["source_action_convention_applied"] is True
    assert payload["selected_source_h1_characters"] == [
        [0, 1],
        [0, 2],
        [1, 2],
        [2, 1],
    ]
    assert payload["atlas_characters_match_selected_source"] is False
    assert payload["source_and_atlas_character_assignments_compatible"] is False
    assert payload["physical_h_d_representative_available"] is False
    assert payload["observational_inputs_used"] is False
