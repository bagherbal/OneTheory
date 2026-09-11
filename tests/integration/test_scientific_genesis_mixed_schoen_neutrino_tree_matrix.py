"""Test the complete exact tree-level Dirac-neutrino matrix.

Owns:
    Regression gates for all allowed residues, exact zero-entry primitives,
    matrix rank, artifact provenance, and the scoped no-go boundary.

Depends on:
    Source-reconstructed neutrino matter comparisons and strict Higgs trace.

Must not:
    Treat the associated-graded zero as an all-orders result, select a carrier
    point, or call the unnormalized holomorphic calculation physical.

Phase 0:
    Integration tests for the Dirac-neutrino tree-level frontier.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_neutrino_tree_matrix import (
    OUTPUT,
    mixed_schoen_holomorphic_neutrino_tree_matrix,
)


def test_neutrino_tree_entries_are_exact_global_boundaries() -> None:
    """Every character-allowed tree entry vanishes by an explicit primitive."""

    result = mixed_schoen_holomorphic_neutrino_tree_matrix()
    assert tuple((entry.row, entry.column) for entry in result.entries) == (
        (0, 1),
        (0, 2),
        (1, 0),
        (2, 0),
    )
    assert tuple(entry.matter_term_count for entry in result.entries) == (
        23409,
        23409,
        23409,
        23409,
    )
    assert tuple(entry.scalar_term_count for entry in result.entries) == (
        6354,
        5832,
        5832,
        6354,
    )
    assert tuple(entry.primitive_term_count for entry in result.entries) == (
        4086,
        3771,
        3771,
        4086,
    )
    assert tuple(entry.projection_depth for entry in result.entries) == (4,) * 4
    assert tuple(entry.primitive_depth for entry in result.entries) == (4,) * 4
    assert all(entry.scalar_is_cycle for entry in result.entries)
    assert all(entry.value.is_zero() for entry in result.entries)
    assert all(entry.primitive_reconstruction_exact for entry in result.entries)
    assert result.matrix.is_zero()
    assert result.matrix_rank == 0
    assert result.exact


def test_neutrino_tree_artifact_advances_to_universal_corrections() -> None:
    """The scoped zero leaves the first universal coefficient as the frontier."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    matrix = payload["dirac_neutrino_tree_matrix"]
    assert matrix["matrix"] == [["0", "0", "0"]] * 3
    assert matrix["matrix_rank"] == 0
    assert matrix["all_zero_entries_have_exact_primitives"] is True
    assert payload["classification"] == "SCOPED_TREE_LEVEL_NO_GO"
    assert payload["complete_tree_level_neutrino_matrix_available"] is True
    assert payload["nontrivial_holomorphic_neutrino_matrix_available"] is False
    assert payload["physical_yukawa_matrix_available"] is False
    assert payload["extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert payload["next_required_object"].startswith(
        "the complete first mathematically allowed universal"
    )
