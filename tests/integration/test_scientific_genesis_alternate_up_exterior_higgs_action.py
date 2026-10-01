"""Reproduce the actual alternate reciprocal exterior primitives.

Owns:
    Content-pinned full-product and primitive reconstruction, ordinary
    odd-square conventions, and explicit remaining scientific boundaries.

Depends on:
    The frozen alternate covectors and checked exterior research machinery.

Must not:
    Assign a Yukawa coefficient or infer a global comparison with the
    physical Higgs-cone representative from a primitive alone.

Phase 0:
    Research-only regressions for the next complete first-order scalar.
"""

from __future__ import annotations

import json

import pytest

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis.alternate_up_exterior_higgs_action import (
    OUTPUT,
    alternate_up_exterior_context,
    alternate_up_exterior_primitive,
    exact_exterior_primitive,
    exterior_square_witness_count,
)


def test_actual_full_exterior_primitives_match_the_pinned_artifact() -> None:
    """Each saved witness must be reconstructed, not accepted from flags."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert [item["product_term_count"] for item in payload["witnesses"]] == [191628, 169983]
    _, context = alternate_up_exterior_context()
    for index, record in enumerate(payload["witnesses"]):
        witness = alternate_up_exterior_primitive(index)
        assert witness.as_record() == record
        assert not witness.product.is_zero()
        assert not witness.primitive.is_zero()
        assert all(basis.total_degree == 2 for basis, _ in witness.product.terms)
        assert all(basis.total_degree == 1 for basis, _ in witness.primitive.terms)
        assert context.differential(witness.primitive) == witness.product
        assert record["directly_transferred_candidate_columns"] == 144
        assert record["candidate_operator_globally_certified"] is False


def test_full_exterior_differential_has_all_declared_square_witnesses() -> None:
    """Keep syzygy squares and all four hypersurface Koszul summands."""

    exterior, _ = alternate_up_exterior_context()
    assert len(exterior.objects) == 31
    assert len(exterior.resolution_arrows) == 42
    assert len(exterior.extension_terms) == 2349
    assert [
        sum(item.position == degree for item in exterior.objects) for degree in (0, -1, -2)
    ] == [10, 15, 6]
    assert exterior_square_witness_count() == 124


def test_exterior_primitives_do_not_claim_a_complete_physical_higgs_or_matrix() -> None:
    """The full first-order scalar and its cone convention are still required."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["determinant_target_degree"] == [-2, 2, 0]
    assert payload["ordered_product"] == "h wedge q(e)"
    assert payload["odd_square_convention"] == "ordinary exterior monomials, not divided powers"
    for field in (
        "minor_inversion_used", "complete_exterior_cone_higgs_cocycle_constructed",
        "null_to_null_coefficients_computed", "rank_three_established",
        "complete_holomorphic_up_matrix_available", "physical_yukawa_matrix_available",
        "extension_point_selected", "observational_inputs_used",
    ):
        assert payload[field] is False
    with pytest.raises(ValueError, match="parameter index is unavailable"):
        alternate_up_exterior_primitive(2)
    for invalid_index in (True, 0.0, 1.0, -1, 2):
        with pytest.raises(ValueError, match="parameter index is unavailable"):
            exact_exterior_primitive(invalid_index, SparseOuterCechCochain())
