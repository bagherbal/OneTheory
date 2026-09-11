"""Test the exact down-Higgs character-complex obstruction.

Owns:
    Regression gates for the restricted differential, zero H1 dimension,
    source comparison, and refusal to fabricate a strict down-Higgs class.

Depends on:
    The content-addressed down-Higgs chain audit and its pinned source record.

Must not:
    Turn the source multiplicity into a rank input, guess a character twist,
    or generalize this scoped obstruction to another chain construction.

Phase 0:
    Integration tests for the current chain action's down-Higgs boundary.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_down_higgs_action import (
    OUTPUT,
)


def test_down_higgs_character_complex_fails_closed_exactly() -> None:
    """The current chain action has no H1 class in required character (0,2)."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")

    assert digest == _canonical_digest(payload)
    assert payload["required_character"] == [0, 2]
    assert payload["ambient_space_dimensions"] == {
        "0": 900,
        "1": 2180,
        "2": 1539,
    }
    assert payload["character_space_dimensions"] == {
        "0": 100,
        "1": 243,
        "2": 176,
    }
    assert payload["differential_ranks"] == {"0": 100, "1": 143}
    assert payload["character_h1_dimension"] == 0
    assert payload["transferred_differential_squared_zero"] is True
    assert payload["group_relations_exact"] is True
    assert payload["character_bases_exact"] is True
    assert payload["source_comparison"]["expected_h1_multiplicity"] == 1
    assert payload["source_comparison"]["used_as_rank_input"] is False
    assert payload["strict_down_higgs_representative_available"] is False
    assert payload["repair_character_twist_guessed"] is False
    assert payload["route_blocked_exact"] is True
    assert payload["observational_inputs_used"] is False
