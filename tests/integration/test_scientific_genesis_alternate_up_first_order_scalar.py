"""Check the complete ordered null-channel scalar and its comparison limits.

Owns:
    Full three-term reconstruction, content-pinned prerequisite checks, and
    a primitive-free independent check of the recorded scalar differential.

Depends on:
    The actual alternate matter lifts, exterior primitives, natural ideal
    quotient, exact full differential, and ordered cover trace.

Must not:
    Convert a closed cover scalar into a normalized physical Yukawa entry
    or infer a permanent physical rank bound from this screen alone.

Phase 0:
    Research regressions; the physical tensor identification remains separate.
"""

from __future__ import annotations

import json

import pytest

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_up_exterior_higgs_action import (
    OUTPUT as EXTERIOR_WITNESSES,
)
from research.experiments.scientific_genesis.alternate_up_first_order_scalar import (
    OUTPUT,
    alternate_up_first_order_scalar,
    alternate_up_ordered_tensor_defect,
    alternate_up_ordered_tensor_difference,
)
from research.experiments.scientific_genesis.alternate_up_higgs_quotient_cone import (
    OUTPUT as QUOTIENT_CONE,
)
from research.experiments.scientific_genesis.alternate_up_null_channel import (
    OUTPUT as NULL_CHANNELS,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_representatives import (
    _cochain_digest,
)


def test_scalar_screen_pins_its_sources_without_claiming_physical_couplings() -> None:
    """A recorded residue cannot silently complete the physical comparison."""

    record = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest")
    assert digest == _canonical_digest(record)
    assert record["schema"] == "alternate-up-first-order-scalar-screen-v1"
    assert record["outer_parameter_basis"] == ["a0", "a1"]
    assert len(record["parameter_coefficients"]) == 2
    assert [item["ordered_cover_residue"] for item in record["parameter_coefficients"]] == [
        "0", "2673/49-486/49*omega",
    ]
    for name, path in (
        ("null_channels", NULL_CHANNELS), ("exterior_primitives", EXTERIOR_WITNESSES),
    ):
        source = json.loads(path.read_text(encoding="utf-8"))
        assert record["prerequisite_artifact_digests"][name] == source["artifact_digest"]
    for field in (
        "derived_tensor_comparison_certified", "physical_null_coefficients_computed",
        "rank_three_established", "complete_holomorphic_up_matrix_available",
        "physical_yukawa_matrix_available", "extension_point_selected", "observational_inputs_used",
    ):
        assert record[field] is False
    assert record["signed_two_slot_cone_actions_exact"] is True
    for index, coefficient in enumerate(record["parameter_coefficients"]):
        assert coefficient["parameter"] == f"a{index}"
        assert coefficient["null_wedge_term_count"] == 2997
        assert coefficient["scalar_term_count"] > 0
        assert coefficient["ordered_scalar_closed_exact"] is True
        assert coefficient["scalar_defect_term_count"] == 0
        assert isinstance(coefficient["ordered_cover_residue"], str)
        assert coefficient["physical_null_coefficient_assigned"] is False


def test_null_tensor_comparison_vanishes_before_the_higgs_annihilator() -> None:
    """Use the actual A quotient, not scalar vanishing, to test comparison."""

    scalar = json.loads(OUTPUT.read_text(encoding="utf-8"))
    quotient = json.loads(QUOTIENT_CONE.read_text(encoding="utf-8"))
    for index, (scalar_record, quotient_record) in enumerate(zip(
        scalar["parameter_coefficients"], quotient["parameter_coefficients"], strict=True,
    )):
        difference = alternate_up_ordered_tensor_difference(index)
        assert len(difference.terms) == (31668, 30234)[index]
        assert _cochain_digest((difference,)) == quotient_record[
            "raw_null_tensor_difference_digest"
        ]
        assert all(basis.component.left_index == 0 for basis, _ in difference.terms)
        defect = alternate_up_ordered_tensor_defect(index)
        assert defect.is_zero()
        assert _cochain_digest((defect,)) == scalar_record["scalar_defect_digest"]
        assert quotient_record["projected_null_tensor_difference_zero_exact"] is True


@pytest.mark.parametrize("parameter_index", (0, 1))
def test_complete_ordered_scalar_reconstructs_the_pinned_record(parameter_index: int) -> None:
    """Recompute both matter homotopies, k, full differential, and residue."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))["parameter_coefficients"][
        parameter_index
    ]
    actual = alternate_up_first_order_scalar(parameter_index)
    assert actual.as_record() == stored
    assert actual.scalar == actual.matter_term + actual.higgs_term
    assert actual.defect.is_zero()


def test_unavailable_parameter_fails_before_any_primitive_solve() -> None:
    """No fallback extension direction is silently substituted."""

    for index in (-1, 2):
        with pytest.raises(ValueError, match="parameter index is unavailable"):
            alternate_up_first_order_scalar(index)
