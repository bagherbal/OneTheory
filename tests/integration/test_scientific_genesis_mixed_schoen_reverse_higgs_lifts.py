"""Test the exact universal Higgs lift on the reverse Schoen carrier.

Owns:
    Regression gates for all determinant-two correction coefficients, strict
    character routing, and content-addressed provenance.

Depends on:
    The generated reverse Higgs lift artifact and canonical digest routine.

Must not:
    Recompute exact line primitives during routine tests, select a P5 point,
    or interpret a Higgs cocycle as a Yukawa entry.

Phase 0:
    Integration tests for the reverse common-chain Higgs prerequisite.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_reverse_higgs_lifts import (
    OUTPUT,
)

EXPECTED_ARTIFACT_DIGEST = (
    "0a5b527f8308304cfabc8fb42205987baf8cb993a99d181d0d4f7277f3d6cf35"
)


def _payload() -> dict[str, object]:
    """Verify the stored artifact before inspecting scientific gates."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == EXPECTED_ARTIFACT_DIGEST
    assert digest == _canonical_digest(payload)
    return payload


def test_reverse_higgs_lift_closes_every_parameter_direction() -> None:
    """All six exact determinant corrections retain strict deck covariance."""

    payload = _payload()
    coefficients = payload["parameter_coefficients"]

    assert payload["schema"] == "mixed-schoen-reverse-higgs-lifts-v1"
    assert payload["extension_sequence"] == "0 -> V2 -> E_reverse -> V1 -> 0"
    assert payload["carrier_locus"] == "P^5(Q(omega)) x K_reverse^s"
    assert payload["forward_higgs_character_exponents"] == [0, 1]
    assert payload["source_higgs_character_exponents"] == [0, 2]
    assert payload["strict_middle_higgs_term_count"] == 27
    assert payload["det_v2_raw_ambient_degrees"] == [2, -1, -2, 1]
    assert payload["det_v2_canonical_ambient_degrees"] == [2, 0, -2, 0]
    assert payload["det_v2_frame_character"] == [1, 1]
    assert [item["parameter"] for item in coefficients] == [
        f"b{index}" for index in range(6)
    ]
    assert [item["action_term_count"] for item in coefficients] == [
        1323, 1377, 1539, 1566, 1566, 1431
    ]
    assert [item["correction_term_count"] for item in coefficients] == [
        972, 1026, 1323, 1323, 1269, 1215
    ]
    assert len({item["action_digest"] for item in coefficients}) == 6
    assert len({item["correction_digest"] for item in coefficients}) == 6
    assert all(
        item["action_is_cycle"]
        and item["action_character_exact"]
        and item["correction_identity_exact"]
        and item["correction_character_exact"]
        and item["exact"]
        for item in coefficients
    )
    assert payload["all_coefficients_exact"] is True
    assert payload["arbitrary_extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert payload["next_required_object"] == (
        "reverse same-chain determinant contraction for one complete "
        "down-type holomorphic Yukawa matrix"
    )
