"""Regression tests for the exact scalar Higgs-action no-go."""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_higgs_scalar_action_no_go import (
    OUTPUT,
)


def test_isolated_atlas_line_replacement_breaks_the_chain_map() -> None:
    """Changing only W1/P's line block has a nonzero exact commutator."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")

    assert digest == _canonical_digest(payload)
    assert payload["discrepant_constituent_generator"] == ["W1", "P"]
    assert payload["isolated_line_replacement_is_chain_map"] is False
    assert payload["isolated_line_commutator_term_count"] == 14
    assert payload["character_twist_fitted"] is False


def test_forced_uniform_scalar_still_has_no_down_higgs_class() -> None:
    """The unique scalar propagation shifts to another zero-dimensional H1."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["forced_uniform_scalar"] == "-1-omega"
    assert payload["w1_resolution_connected"] is True
    assert payload["uniform_scalar_action_is_chain_map"] is True
    assert payload["uniform_scalar_action_group_laws_exact"] is True
    assert payload["legacy_shifted_character"] == [1, 2]
    assert payload["character_space_dimensions"] == {
        "0": 100,
        "1": 243,
        "2": 176,
    }
    assert payload["differential_ranks"] == {"0": 100, "1": 143}
    assert payload["differential_squared_zero"] is True
    assert payload["shifted_character_h1_dimension"] == 0
    assert payload["scalar_action_repairs_refuted"] is True
    assert payload["observational_inputs_used"] is False
    assert "non-scalar" in payload["next_required_object"]
