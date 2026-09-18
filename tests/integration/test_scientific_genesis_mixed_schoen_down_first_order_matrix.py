"""Test the complete universal convention-corrected down Yukawa matrix.

Owns:
    Regression gates for all eight exact coefficients, source-to-forward
    labels, polynomial assembly, generic rank, and filtration completion.

Depends on:
    The content-addressed universal physical down-matrix artifact.

Must not:
    Recompute dense coefficient cochains during routine tests, select a carrier
    point, or treat an unnormalized holomorphic matrix as a physical observable.

Phase 0:
    Integration tests for the all-orders physical down-flavor calculation.
"""

from __future__ import annotations

import json

import pytest

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_down_first_order_matrix import (
    OUTPUT,
    _coefficient_from_record,
)

EXPECTED_ARTIFACT_DIGEST = (
    "c112b27eae52f1f9223b8b45ccded5d30681fb037150c7bc9ad0ad02dcad55e4"
)
EXPECTED_COMPLETE_TERM_COUNTS = [
    345_342,
    343_902,
    318_471,
    344_610,
    337_356,
    333_765,
    302_238,
    335_703,
]
EXPECTED_COMPLETE_DIGESTS = [
    "6426db8af6a77525f0031905adddb3eaa5078c0ab3b80976b1966d4eaacc23ae",
    "ca1281b290d5919f8f6bcb49a927c06a1cc244ae6dfc6a83479b117b60942c00",
    "af7c51964ed4b8ce961238663e15c4f3c2f51c7a621ebb9891b75a8d9ada0fe3",
    "a5110fb74b284f3a53dffc69e15f1754d704d926fd231c007876b5aaf82f29a1",
    "e503c08693b0dd7521584926cc0d31fe3b0ffc8256938814973aa93eaeb6feac",
    "333f0beec6bdcdbc8ede75c00b4099a9f643b8f3736a36c307840081ee62fea8",
    "0722105ec6d8662d67efd759336597dab7030e320b48b7be5f833563da76f908",
    "9d3c1300d816fd200be54789ef1c93eda37b2c4c4198b2db328564ccc8a44f72",
]


def _payload() -> dict[str, object]:
    """Load the immutable matrix artifact and verify its content address."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == EXPECTED_ARTIFACT_DIGEST
    assert digest == _canonical_digest(payload)
    return payload


def test_down_coefficient_records_round_trip_fail_closed() -> None:
    """An exact record rehydrates while cycle tampering is rejected."""

    raw = _payload()["coefficients"][0]
    result = _coefficient_from_record(raw)
    assert result.as_record() == raw

    tampered = json.loads(json.dumps(raw))
    tampered["complete_scalar_cochain"]["is_cycle"] = False
    with pytest.raises(ValueError, match="canonical reconstruction"):
        _coefficient_from_record(tampered)


def test_all_down_coefficients_close_independently() -> None:
    """Every parameter and local-family coefficient has distinct evidence."""

    coefficients = _payload()["coefficients"]
    assert isinstance(coefficients, list)
    assert [
        (
            coefficient["parameter"],
            coefficient["row_local_family_index"],
            coefficient["column_local_family_index"],
        )
        for coefficient in coefficients
    ] == [
        (parameter, row, column)
        for parameter in ("a0", "a1")
        for row in (1, 2)
        for column in (1, 2)
    ]
    assert all(
        coefficient["matter_scalar_character_exact"] is True
        and coefficient["higgs_correction_character_exact"] is True
        and coefficient["leibniz_identity_exact"] is True
        and coefficient["comparison_residual"]["is_cycle"] is True
        and coefficient["raw_comparison_primitive"]["identity_exact"] is True
        and coefficient["strict_comparison_primitive"]["identity_exact"] is True
        and coefficient["strict_comparison_primitive"]["character_exact"] is True
        and coefficient["complete_scalar_cochain"]["is_cycle"] is True
        and coefficient["complete_scalar_cochain"]["projection_depth"] == 4
        and coefficient["exact"] is True
        for coefficient in coefficients
    )
    assert [
        coefficient["complete_scalar_cochain"]["term_count"]
        for coefficient in coefficients
    ] == EXPECTED_COMPLETE_TERM_COUNTS
    assert [
        coefficient["complete_scalar_cochain"]["digest"]
        for coefficient in coefficients
    ] == EXPECTED_COMPLETE_DIGESTS
    assert {
        coefficient["complete_scalar_cochain"]["residue"]
        for coefficient in coefficients
    } == {"0"}


def test_down_matrix_uses_only_convention_corrected_physical_sectors() -> None:
    """Physical source labels route to the exact forward-chain sectors."""

    physical_slice = _payload()["physical_slice"]
    assert physical_slice == {
        "matrix": "down-type holomorphic Yukawa",
        "source_matter_character_exponents": [[2, 1], [1, 0]],
        "forward_matter_character_exponents": [[1, 2], [2, 0]],
        "source_higgs_character_exponents": [0, 2],
        "forward_higgs_character_exponents": [0, 1],
    }


def test_down_matrix_is_an_all_orders_scoped_no_go() -> None:
    """Exterior filtration closes the rank-zero universal down matrix."""

    payload = _payload()
    assert payload["parameter_basis"] == ["a0", "a1"]
    assert payload["tree_matrix_rank"] == 0
    assert payload["first_order_slots"] == [
        [1, 1],
        [1, 2],
        [2, 1],
        [2, 2],
    ]
    assert payload["coefficient_matrices"] == {
        "a0": [["0", "0", "0"]] * 3,
        "a1": [["0", "0", "0"]] * 3,
    }
    assert payload["universal_lower_determinant"] == []
    assert payload["generic_rank"] == 0
    assert payload["nontrivial"] is False
    assert payload["maximum_exterior_allowed_parameter_order"] == 1
    assert payload["higher_orders_structurally_zero"] is True
    assert payload["all_eight_coefficients_exact"] is True
    assert payload["all_exterior_allowed_orders_complete"] is True
    assert payload["classification"] == "SCOPED_ALL_ORDERS_DOWN_NO_GO"
    assert payload["complete_universal_holomorphic_down_matrix_available"] is True
    assert payload["nontrivial_holomorphic_down_matrix_available"] is False
    assert payload["physical_yukawa_matrix_available"] is False
    assert payload["extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert payload["next_required_object"] == (
        "the convention-corrected charged-lepton interpretation of the "
        "existing forward-sector universal matrix"
    )
