"""Test the exact universal Higgs-leg deformation lift.

Owns:
    Regression gates for the determinant-line action, primitive, explicit
    diagonal normalization, and unresolved bottom-matter pairing.

Depends on:
    The committed content-addressed Higgs-leg deformation artifact.

Must not:
    Infer the missing V2 determinant contraction or a Yukawa coefficient.

Phase 0:
    Integration tests for the first exact Higgs-leg lift.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_higgs_leg_deformation import (
    OUTPUT,
)


def test_first_higgs_leg_lift_is_exact_and_fail_closed() -> None:
    """The exact determinant-line correction stops before the missing pairing."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")

    assert digest == _canonical_digest(payload)
    assert payload["parameter"] == "a0"
    assert payload["determinant_ambient_degrees"] == [-2, 1, 2, -1]
    assert payload["extension_source_term_count"] == 2_196
    assert payload["action_term_count"] == 1_593
    assert payload["correction_term_count"] == 1_431
    assert payload["canonical_determinant_ambient_degrees"] == [-2, 0, 2, 0]
    assert payload["canonical_action_term_count"] == 2_124
    assert payload["canonical_correction_term_count"] == 1_908
    assert payload["projection_depth"] == 3
    assert payload["inclusion_depth"] == 0
    assert payload["homotopy_depth"] == 3
    assert payload["action_is_cycle"] is True
    assert payload["correction_identity_exact"] is True
    assert payload["diagonal_line_identity_exact"] is True
    assert payload["canonical_action_is_cycle"] is True
    assert payload["canonical_correction_identity_exact"] is True
    assert payload["exact"] is True
    assert payload["bottom_matter_determinant_pairing_available"] is False
    assert payload["holomorphic_yukawa_entry_available"] is False
    assert payload["extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert "Pluecker chain map" in payload["first_missing_input"]
