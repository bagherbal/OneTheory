"""Regress actual reciprocal covectors for the alternate Higgs action.

Owns:
    Full-cycle reconstruction, reduced independence, and reciprocal
    target-line checks for the two outer images and saved Higgs input.

Depends on:
    The research-only global quotient map and exact mixed Hom transfer.

Must not:
    Infer the uncomputed exterior product, a Higgs primitive, or a
    null-to-null Yukawa from the existence of its inputs.

Phase 0:
    Research-only input reduction for the missing first-order action.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_up_dual_higgs_inputs import (
    OUTPUT,
    alternate_up_dual_higgs_inputs,
)


def test_reciprocal_inputs_are_actual_independent_full_cycles() -> None:
    """The quotient images are neither guessed nor reduced boundaries."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    inputs = alternate_up_dual_higgs_inputs()
    assert inputs.as_record() == payload
    assert [len(item.terms) for item in inputs.outer_covectors] == [16515, 13779]
    assert len(inputs.higgs_covector.terms) == 324
    assert payload["outer_images_independent_mod_boundaries"] is True
    assert all(
        basis.component.left_index == 0
        for cochain in (*inputs.outer_covectors, inputs.higgs_covector)
        for basis, _ in cochain.terms
    )


def test_reciprocal_targets_do_not_supply_a_higgs_primitive() -> None:
    """Reciprocal lines identify a target, not a computed physical product."""

    payload = alternate_up_dual_higgs_inputs().as_record()
    assert tuple(
        left + right for left, right in zip(
            payload["quotient_b_line_degree"],
            payload["higgs_target_line_degree"], strict=True,
        )
    ) == (0, 0, 0)
    assert payload["minor_inversion_used"] is False
    assert payload["hom_to_tensor_inverse_used"] is False
    assert payload["determinant_line_higgs_action_computed"] is False
    assert payload["determinant_line_higgs_primitive_computed"] is False
    assert payload["null_to_null_yukawa_computed"] is False
