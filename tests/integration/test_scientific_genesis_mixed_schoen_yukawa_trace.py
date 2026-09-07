"""Test the complete exact tree-level up-type trace calculation.

Owns:
    Regression gates for the unique determinant orientation, four lawful
    scalar cycles, exact primitives, and the resulting rank-zero matrix.

Depends on:
    The strict matter/Higgs representatives and certified determinant residue.

Must not:
    Promote the zero matrix as a nontrivial Yukawa result, infer a higher
    product, select an extension point, or call holomorphic data physical.

Phase 0:
    Integration tests for the scoped tree-level up-sector no-go.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_yukawa_trace import (
    OUTPUT,
    mixed_schoen_holomorphic_up_slice,
)


def test_all_tree_up_entries_are_exact_boundaries() -> None:
    """The four allowed traces vanish with explicit full-complex primitives."""

    result = mixed_schoen_holomorphic_up_slice()
    assert tuple((row, column) for row, column, _value in result.entries) == (
        (0, 1),
        (0, 2),
        (1, 0),
        (2, 0),
    )
    assert all(value.is_zero() for _row, _column, value in result.entries)
    assert result.scalar_term_counts == (6354, 5832, 6354, 5832)
    assert result.projection_depths == (4, 4, 4, 4)
    assert result.scalar_products_are_cycles
    assert result.primitive_term_counts == (4086, 3771, 4086, 3771)
    assert result.primitive_depths == (4, 4, 4, 4)
    assert all(result.primitive_reconstructions_exact)
    assert result.matrix.is_zero()
    assert result.matrix_rank == 0
    assert result.exact


def test_tree_trace_artifact_advances_to_the_first_higher_product() -> None:
    """The exact zero matrix leaves the nontrivial Yukawa milestone open."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    matrix = payload["up_type_tree_matrix"]
    assert matrix["determinant_orientation_vector"] == [1, 1, 1, -1, -1, -1, -1, 1]
    assert matrix["matrix"] == [["0", "0", "0"]] * 3
    assert matrix["matrix_rank"] == 0
    assert matrix["tree_level_nontrivial"] is False
    assert payload["classification"] == "SCOPED_TREE_LEVEL_NO_GO"
    assert payload["complete_tree_level_up_matrix_available"] is True
    assert payload["nontrivial_tree_level_up_matrix_available"] is False
    assert payload["physical_yukawa_matrix_available"] is False
    assert payload["extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert payload["next_required_object"].startswith(
        "the first exact deformation or higher product"
    )
