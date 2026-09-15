"""Regression tests for the exact factorwise linearization obstruction."""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_higgs_linearization_no_go import (
    OUTPUT,
)


def test_selected_constituents_are_exactly_simple() -> None:
    """Both synchronized constituent self-Hom spaces contain only scalars."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    audits = payload["constituent_self_hom_audits"]

    assert digest == _canonical_digest(payload)
    assert [item["constituent"] for item in audits] == ["V1", "V2"]
    assert [item["negative_self_hom_space_dimensions"] for item in audits] == [
        [0, 0, 0],
        [0, 0, 0],
    ]
    assert [item["degree_zero_space_dimension"] for item in audits] == [54, 124]
    assert [item["degree_one_space_dimension"] for item in audits] == [102, 258]
    assert [item["degree_zero_differential_rank"] for item in audits] == [53, 123]
    assert [item["h0_endomorphism_dimension"] for item in audits] == [1, 1]
    assert all(item["simple_over_q_omega"] for item in audits)
    assert payload["all_selected_constituents_simple"] is True


def test_no_factorwise_relinearization_repairs_higgs_characters() -> None:
    """Simplicity reduces every same-factor repair to an exhausted shift."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert payload["exact"] is True
    assert payload["matching_uniform_character_shifts"] == []
    assert (
        payload["same_constituent_factorwise_linearization_repair_available"]
        is False
    )
    assert payload["non_scalar_resolution_comparison_can_repair_cohomology"] is False
    assert payload["selected_source_equivariance_realized_by_current_complex"] is False
    assert payload["physical_h_d_representative_available"] is False
    assert payload["character_twist_fitted"] is False
    assert payload["observational_inputs_used"] is False
    assert "unrelated constituent realizations are not excluded" in payload["scope"]
