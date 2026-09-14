"""Regression tests for the exact equivariant Higgs comparison obstruction."""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_higgs_equivariant_obstruction import (
    OUTPUT,
)


def test_current_higgs_comparison_is_refuted_isotypically() -> None:
    """Character-(0,2) dimensions forbid the current equivariant comparison."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")

    assert digest == _canonical_digest(payload)
    assert payload["required_character"] == [0, 2]
    assert payload["source_derived_p1_h1_dimension"] == 1
    assert payload["current_chain_h1_dimension"] == 0
    assert payload["isotypic_dimension_mismatch"] is True
    assert payload["equivariant_quasi_isomorphism_available"] is False
    assert payload["current_comparison_route_refuted"] is True
    assert payload["character_twist_guessed"] is False
    assert payload["deck_generators_relabelled"] is False
    assert payload["observational_inputs_used"] is False


def test_exact_atlas_exposes_the_legacy_frame_gap() -> None:
    """The next dependency is the full atlas action, not a scalar relabeling."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    comparisons = payload["legacy_frame_atlas_comparisons"]

    assert payload["both_determinant_hom_orientations_blocked"] is True
    assert payload["constituent_atlases_exact"] is True
    assert payload["factor_action_orientations_exact"] is True
    assert payload["legacy_frame_matches_atlas"] is False
    assert [item["matches"] for item in comparisons] == [False, True, True, True]
    assert [
        (
            item["constituent"],
            item["generator"],
            item["native_atlas_character"],
            item["synchronized_generator_power"],
            item["synchronized_atlas_character"],
        )
        for item in comparisons
    ] == [
        ("W1", "P", "1", 1, "1"),
        ("W1", "T", "1", 1, "1"),
        ("W2", "P", "-1-omega", 2, "omega"),
        ("W2", "T", "-1-omega", 2, "omega"),
    ]
    assert "local-semilinear" in payload["next_required_object"]
