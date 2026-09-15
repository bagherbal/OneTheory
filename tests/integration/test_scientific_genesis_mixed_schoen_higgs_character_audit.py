"""Regression tests for the complete synchronized Higgs character audit."""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_higgs_character_audit import (
    OUTPUT,
)


def test_all_character_sectors_exhaust_the_synchronized_chain() -> None:
    """One shared ambient transfer restricts exactly to all nine characters."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")

    assert digest == _canonical_digest(payload)
    assert payload["ambient_space_dimensions"] == [900, 2180, 1539]
    assert len(payload["sectors"]) == 9
    assert payload["character_spaces_exhaust_ambient"] is True
    assert payload["all_character_restrictions_exact"] is True
    assert all(item["differential_squared_zero"] for item in payload["sectors"])
    assert payload["current_h1_dimension"] == 4
    assert payload["source_characters_used_as_rank_input"] is False
    assert payload["observational_inputs_used"] is False


def test_current_higgs_representation_is_compared_without_fitting() -> None:
    """The exact current support is recorded before source comparison."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["exact"] is True
    assert payload["current_h1_characters"] == [
        [0, 0],
        [0, 1],
        [2, 0],
        [2, 1],
    ]
    assert payload["current_characters_match_source"] is False
    assert payload["selected_source_h1_characters"] == [
        [0, 1],
        [0, 2],
        [1, 2],
        [2, 1],
    ]
    assert payload["matching_uniform_character_shifts"] == []
    assert "atlas-derived" in payload["next_required_object"]
