"""Test the first complete exact higher-product coefficient.

Owns:
    Regression gates for the comparison primitive, quotient character,
    complete scalar closure, and scoped first-order residue.

Depends on:
    The committed content-addressed first higher-product artifact.

Must not:
    Generalize one vanishing coefficient to a matrix or a physical coupling.

Phase 0:
    Integration tests for the first complete parameter-linear coefficient.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_first_higher_product import (
    OUTPUT,
)


def test_first_higher_product_coefficient_is_exact_and_scoped() -> None:
    """The descended a0 lower-(1,1) coefficient closes and vanishes exactly."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")

    assert digest == _canonical_digest(payload)
    assert payload["parameter"] == "a0"
    assert payload["row_local_family_index"] == 1
    assert payload["column_local_family_index"] == 1
    assert payload["v1_determinant_character_exponents"] == [1, 0]
    assert payload["v2_determinant_character_exponents"] == [1, 1]
    assert payload["scalar_frame_character_exponents"] == [2, 1]
    assert payload["matter_scalar_term_count"] == 9_414
    assert payload["matter_scalar_character_exact"] is True
    assert payload["bottom_pairing_term_count"] == 11_340
    assert payload["higgs_correction_term_count"] == 1_980
    assert payload["higgs_correction_character_exact"] is True
    assert payload["correction_product"]["term_count"] == 260_391
    assert payload["action_product"]["term_count"] == 130_725
    assert payload["leibniz_identity_exact"] is True
    assert payload["comparison_residual"] == {
        "digest": "0ef02a264ec35e12046df33f60f9f5a86e6b3159f2b543e8fd7fd752e9463ab3",
        "is_cycle": True,
        "term_count": 130_815,
    }
    assert payload["raw_comparison_primitive"]["term_count"] == 79_450
    assert payload["raw_comparison_primitive"]["depth"] == 3
    assert payload["raw_comparison_primitive"]["identity_exact"] is True
    strict = payload["strict_comparison_primitive"]
    assert strict["term_count"] == 105_348
    assert strict["character_exact"] is True
    assert strict["identity_exact"] is True
    complete = payload["complete_scalar_cochain"]
    assert complete["term_count"] == 268_905
    assert complete["is_cycle"] is True
    assert complete["residue"] == "0"
    assert complete["projection_depth"] == 4
    assert payload["classification"] == "SCOPED_FIRST_ORDER_ENTRY_VANISHING"
    assert payload["exact"] is True
    assert payload["input_level_comparison_primitive_available"] is True
    assert payload["general_chain_homotopy_available"] is False
    assert payload["complete_first_order_matrix_available"] is False
    assert payload["holomorphic_yukawa_matrix_available"] is False
    assert payload["extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert "remaining local-family" in payload["first_missing_input"]
