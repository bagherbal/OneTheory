"""Test the lawful independent-cover tensor of strict matter cocycles.

Owns:
    Regression gates for independent fiber units, the direct-product cycle
    obstruction, deck characters, and the fail-closed trace frontier.

Depends on:
    The generated strict matter representatives and chain-diagonal engine.

Must not:
    Supply a determinant pairing, infer a Yukawa value, or select a carrier
    extension point from the split support pattern.

Phase 0:
    Integration tests for the exact split matter-product hull only.
"""

import json
from collections import Counter

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_tensor import (
    OUTPUT,
    split_matter_tensor_audit,
)


def test_direct_matter_products_fail_closed_in_the_higgs_complex() -> None:
    """The canonical candidates preserve character but are not chain cycles."""

    result = split_matter_tensor_audit()
    assert result.support == ((0, 1), (0, 2), (1, 0), (2, 0))
    assert result.product_character == (0, 2)
    assert result.total_character_is_invariant
    assert result.inserted_units_exact
    assert not result.products_are_cycles
    assert result.products_have_required_character
    assert not result.direct_product_hull_available
    assert result.audit_exact
    assert all(
        product.terms
        and {basis.total_degree for basis, _coefficient in product.terms} == {2}
        for _row, _column, product in result.products
    )


def test_direct_tensor_residual_is_not_diagonal_only() -> None:
    """Every obstruction spans ordinary sectors and excludes the H wedge."""

    result = split_matter_tensor_audit()
    expected_subsets = Counter(
        {
            (): 52_908,
            (0,): 4_617,
            (1,): 9_573,
            (0, 1): 756,
        }
    )
    assert all(
        len(residual.terms) == 67_854
        and Counter(
            basis.component.subset
            for basis, _coefficient in residual.terms
        )
        == expected_subsets
        and all(
            2 not in basis.component.subset
            for basis, _coefficient in residual.terms
        )
        for _row, _column, residual in result.residuals
    )


def test_matter_tensor_artifact_stops_before_the_unproved_trace() -> None:
    """The frozen hull exposes no scalar coupling before determinant tracing."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert payload["external_cover_substitution_used"] is False
    assert payload["extension_point_selected"] is False
    assert payload["direct_product_hull_available"] is False
    assert payload["cyclic_trace_available"] is False
    assert payload["holomorphic_yukawa_matrix_available"] is False
    assert payload["next_required_object"].startswith(
        "an exact equivariant chain comparison"
    )
