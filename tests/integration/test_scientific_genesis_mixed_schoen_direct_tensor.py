"""Integration tests for the lawful direct-tensor boundary audit."""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_direct_tensor import (
    OUTPUT,
    combined_tensor_sign_law_scan,
    naive_tensor_square_witness,
    ordinary_tensor_skeleton_square_zero,
)


def test_naive_full_tensor_merge_has_an_exact_square_witness() -> None:
    """The ordinary skeleton closes while merged resolved arrows do not."""

    witness = naive_tensor_square_witness()

    assert ordinary_tensor_skeleton_square_zero()
    assert witness.exact_obstruction
    assert witness.degree == 0
    assert witness.reduced_index == 0
    assert witness.seed_term_count == 2
    assert witness.first_image_term_count == 50
    assert witness.square_term_count == 3


def test_direct_tensor_artifact_is_content_addressed_and_fail_closed() -> None:
    """The certificate names the missing diagonal without exposing a Higgs class."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")

    assert digest == _canonical_digest(payload)
    assert payload["candidate_shape"] == {
        "object_count": 48,
        "resolution_arrow_count": 68,
        "full_extension_term_count": 3834,
        "ordinary_resolution_skeleton_square_zero": True,
    }
    assert payload["naive_merged_arrow_witness"][
        "differential_square_nonzero"
    ] is True
    assert payload["parity_sign_law_scan"]["declared_law_count"] == 64
    assert payload["parity_sign_law_scan"]["survivor_counts"] == [4, 2, 0]
    assert payload["parity_sign_law_scan"]["sign_only_repair_exists"] is False
    assert payload["combined_static_live_parity_scan"] == (
        combined_tensor_sign_law_scan()
    )
    assert payload["combined_static_live_parity_scan"]["survivor_counts"] == [
        64,
        32,
        0,
    ]
    assert payload["combined_static_live_parity_scan"]["parity_repair_exists"] is False
    assert payload["physical_higgs_representative_available"] is False
    assert "chain diagonal" in payload["first_missing_input"]
