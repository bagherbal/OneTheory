"""Check the actual ideal quotient used by the alternate Higgs cone.

Owns:
    The full quotient presentation, unchanged Higgs coefficients, and
    exact connecting-map and exterior-action reconstruction.

Depends on:
    The frozen alternate Serre resolution and natural global sheaf quotients.

Must not:
    Interpret the coherent quotient as a vector bundle or infer a matrix.

Phase 0:
    Research regressions for the physical Higgs-cone comparison.
"""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from research.experiments.scientific_genesis.alternate_up_exterior_higgs_action import (
    OUTPUT as EXTERIOR_WITNESSES,
)
from research.experiments.scientific_genesis.alternate_up_exterior_higgs_action import (
    alternate_up_exterior_context,
)
from research.experiments.scientific_genesis.alternate_up_higgs_hom_representative import (
    load_alternate_up_higgs_hom_full_cochain,
)
from research.experiments.scientific_genesis.alternate_up_higgs_quotient_cone import (
    OUTPUT,
    alternate_higgs_quotient_connecting_arrow,
    alternate_higgs_quotient_covector,
    alternate_higgs_quotient_models,
    checked_quotient_higgs_action,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_representatives import (
    _cochain_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import _MixedContraction
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import mixed_schoen_unit
from research.experiments.scientific_genesis.mixed_schoen_outer_universal_cone import (
    _verified_payload,
)


def test_quotient_certificate_reuses_pinned_primitives_without_inventing_a_bundle() -> None:
    """Keep the coherent quotient and existing identities explicitly scoped."""

    _, record = _verified_payload(OUTPUT)
    primitive_digest, primitives = _verified_payload(EXTERIOR_WITNESSES)
    assert record["schema"] == "alternate-up-higgs-quotient-cone-v1"
    assert record["prerequisite_artifact_digests"]["full_exterior_primitives"] == primitive_digest
    assert record["quotient_is_a_vector_bundle"] is False
    assert record["universal_triangular_quotient_cone_squared_zero_exact"] is True
    assert record["higgs_lift_exists_by_full_pinned_primitive_identities"] is True
    assert record["null_matter_quotient_tensor_comparison_exact"] is True
    for coefficient, primitive in zip(
        record["parameter_coefficients"], primitives["witnesses"], strict=True,
    ):
        assert coefficient["primitive_solver_reexecuted_by_this_writer"] is False
        assert coefficient["primitive_digest"] == primitive["primitive_digest"]
        assert coefficient["primitive_term_count"] == primitive["primitive_term_count"]
    for field in (
        "extension_point_selected", "observational_inputs_used",
        "complete_holomorphic_up_matrix_available", "physical_yukawa_matrix_available",
    ):
        assert record[field] is False


def test_actual_serre_quotient_preserves_the_complete_ideal_resolution() -> None:
    """Remove only the A subobject and its legitimately annihilated arrows."""

    second, quotient = alternate_higgs_quotient_models()
    assert len(quotient.objects) == 7
    assert len(quotient.resolution_arrows) == 6
    assert quotient.extension_terms == ()
    assert quotient.twist == (0, 0, 1)
    assert quotient.resolution_arrows == tuple(
        replace(arrow, source=arrow.source - 1, target=arrow.target - 1)
        for arrow in second.resolution_arrows
    )
    assert [item.position for item in quotient.objects] == [0, 0, 0, 0, -1, -1, -1]


def test_actual_quotient_higgs_is_the_same_full_nonzero_cycle() -> None:
    """Only the source index changes; every monomial and coefficient stays."""

    _, quotient = alternate_higgs_quotient_models()
    h = alternate_higgs_quotient_covector()
    original = load_alternate_up_higgs_hom_full_cochain()
    assert len(h.terms) == len(original.terms) == 324
    expected = {
        (replace(basis.component, right_index=basis.component.right_index - 1),
         basis.x_monomial, basis.u_monomial, basis.p_monomial, basis.cell): value
        for basis, value in original.terms
    }
    assert {
        (basis.component, basis.x_monomial, basis.u_monomial, basis.p_monomial, basis.cell): value
        for basis, value in h.terms
    } == expected
    assert _MixedContraction(mixed_schoen_unit(), quotient).differential(h).is_zero()


def test_actual_quotient_arrows_close_and_reproduce_both_exterior_actions() -> None:
    """Recompute the full maps, not the saved primitive's scalar metadata."""

    _, quotient = alternate_higgs_quotient_models()
    exterior, _ = alternate_up_exterior_context()
    context = _MixedContraction(quotient, exterior)
    records = json.loads(OUTPUT.read_text(encoding="utf-8"))["parameter_coefficients"]
    for index, expected_action_count in enumerate((191628, 169983)):
        arrow = alternate_higgs_quotient_connecting_arrow(index)
        assert not arrow.is_zero()
        assert all(basis.total_degree == 1 for basis, _ in arrow.terms)
        assert context.differential(arrow).is_zero()
        assert len(arrow.terms) == records[index]["connecting_arrow_term_count"]
        assert _cochain_digest((arrow,)) == records[index]["connecting_arrow_digest"]
        action = checked_quotient_higgs_action(index)
        assert len(action.terms) == expected_action_count
        assert _cochain_digest((action,)) == records[index]["higgs_action_digest"]
    with pytest.raises(ValueError, match="parameter index is unavailable"):
        alternate_higgs_quotient_connecting_arrow(2)
