"""Test the complete exact first-order up-type matrix certificate.

Owns:
    Regression gates for all eight indexed residues, structural zero slots,
    parameter coefficient matrices, and the universal first-order rank.

Depends on:
    The committed content-addressed first-order matrix artifact.

Must not:
    Infer higher-order vanishing, select an extension point, or call a
    first-order truncation a complete holomorphic or physical Yukawa matrix.

Phase 0:
    Integration tests for the scoped first-order flavor no-go.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_first_order_matrix import (
    OUTPUT,
    first_order_filtration_allows,
)

EXPECTED_COUNTS = (
    268_905,
    324_489,
    324_054,
    254_919,
    259_299,
    315_426,
    314_847,
    243_414,
)
EXPECTED_DIGESTS = (
    "8eb2097e668c731020ecebf6e87554493dd613960c862ace74a4240e2eb57adb",
    "0621d150df99dae947eacdad43654e3cc4aa40099d2131835fd9d8372f1b257c",
    "95a067553b8afb580f02373e2baab3217e979fa6553a9e0d66e6207aba3cc18e",
    "ab0eb72f7c8effaf61f8ab335bf5aca79e5bc5a24c20ee6aa45f3e1d51c3c54a",
    "99adb1b6328e051ac94044105b0a85789bce6b6187b86f04c731dd610cea3dde",
    "e2cf12965375135e42de8be88f9b4b94f86064d90fc540c2da7101cc0256c354",
    "a46689fb31e1aca266f7d7c401ec855e054db903971df41f7ead3e03ac5b9a63",
    "404ba1c9b695672487bcec19075401aacb020944c6bec7d6bba7e425e8b3433f",
)


def _payload() -> dict[str, object]:
    """Load the immutable matrix artifact and verify its content address."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    return payload


def test_all_first_order_coefficients_close_and_vanish() -> None:
    """Each parameter and local-family slot has an exact zero residue."""

    payload = _payload()
    coefficients = payload["coefficients"]
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
    assert tuple(
        coefficient["complete_scalar_cochain"]["term_count"]
        for coefficient in coefficients
    ) == EXPECTED_COUNTS
    assert tuple(
        coefficient["complete_scalar_cochain"]["digest"]
        for coefficient in coefficients
    ) == EXPECTED_DIGESTS
    assert all(
        coefficient["strict_comparison_primitive"]["identity_exact"] is True
        and coefficient["strict_comparison_primitive"]["character_exact"] is True
        and coefficient["complete_scalar_cochain"]["is_cycle"] is True
        and coefficient["complete_scalar_cochain"]["projection_depth"] == 4
        and coefficient["complete_scalar_cochain"]["residue"] == "0"
        and coefficient["exact"] is True
        for coefficient in coefficients
    )


def test_universal_first_order_matrix_has_exact_rank_zero() -> None:
    """Both parameter matrices vanish without choosing a projective point."""

    payload = _payload()
    zero_matrix = [["0", "0", "0"]] * 3

    assert payload["parameter_basis"] == ["a0", "a1"]
    assert payload["first_order_slots"] == [[1, 1], [1, 2], [2, 1], [2, 2]]
    assert payload["structural_zero_slots"] == [
        [0, 0],
        [0, 1],
        [0, 2],
        [1, 0],
        [2, 0],
    ]
    assert payload["coefficient_matrices"] == {
        "a0": zero_matrix,
        "a1": zero_matrix,
    }
    assert payload["universal_lower_determinant"] == []
    assert payload["generic_first_order_rank"] == 0
    assert payload["all_eight_coefficients_exact"] is True
    assert payload["complete_first_order_up_matrix_available"] is True
    assert payload["complete_holomorphic_up_matrix_available"] is False
    assert payload["classification"] == "SCOPED_FIRST_ORDER_NO_GO"
    assert payload["extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert [
        [row, column]
        for row in range(3)
        for column in range(3)
        if first_order_filtration_allows(row, column)
    ] == payload["first_order_slots"]
