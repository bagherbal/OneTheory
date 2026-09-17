"""Test the convention-corrected physical down tree matrix.

Owns:
    Regression gates for source/forward labels, all character-allowed slots,
    exact residues, zero-boundary witnesses, and content-addressed provenance.

Depends on:
    The exact down tree certificate and its fail-open entry record.

Must not:
    Infer universal corrections, force a zero residue, select a carrier point,
    or interpret the holomorphic tree matrix as physically normalized.

Phase 0:
    Integration tests for the associated-graded physical down matrix.
"""

from __future__ import annotations

import json

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_down_tree_matrix import (
    OUTPUT,
    DownTreeEntry,
)

EXPECTED_ARTIFACT_DIGEST = (
    "4c827630ff59bdab5e46ec63d606f1dc16df3cc6299ed04d517dbd78dec8e698"
)


def _payload() -> dict[str, object]:
    """Load the exact tree artifact after checking its frozen digest."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == EXPECTED_ARTIFACT_DIGEST
    assert digest == _canonical_digest(payload)
    return payload


def test_down_tree_matrix_uses_only_convention_corrected_physical_sectors() -> None:
    """Source labels route to the exact forward sectors used by the chain maps."""

    matrix = _payload()["down_tree_matrix"]

    assert matrix["source_row_matter_character_exponents"] == [2, 1]
    assert matrix["source_column_matter_character_exponents"] == [1, 0]
    assert matrix["forward_row_matter_character_exponents"] == [1, 2]
    assert matrix["forward_column_matter_character_exponents"] == [2, 0]
    assert matrix["source_higgs_character_exponents"] == [0, 2]
    assert matrix["forward_higgs_character_exponents"] == [0, 1]
    assert matrix["character_allowed_slots"] == [[0, 1], [0, 2], [1, 0], [2, 0]]


def test_all_down_tree_zeros_have_independent_exact_boundary_witnesses() -> None:
    """Every allowed zero is derived separately with a reconstructed primitive."""

    matrix = _payload()["down_tree_matrix"]
    entries = matrix["entries"]

    assert matrix["matrix"] == [["0", "0", "0"]] * 3
    assert matrix["matrix_rank"] == 0
    assert matrix["zero_entries_have_exact_primitives"] is True
    assert matrix["tree_level_nontrivial"] is False
    assert matrix["exact"] is True
    assert len(entries) == 4
    assert {entry["matter_term_count"] for entry in entries} == {23_409}
    assert sorted(entry["scalar_term_count"] for entry in entries) == [
        5_832,
        5_832,
        6_354,
        6_354,
    ]
    assert len({entry["matter_digest"] for entry in entries}) == 4
    assert len({entry["scalar_digest"] for entry in entries}) == 4
    assert all(entry["value"] == "0" and entry["exact"] is True for entry in entries)
    assert all(
        entry["zero_boundary_witness"]["primitive_reconstruction_exact"] is True
        for entry in entries
    )
    assert len(
        {
            entry["zero_boundary_witness"]["primitive_digest"]
            for entry in entries
        }
    ) == 4


def test_down_tree_certificate_remains_scoped_and_selection_free() -> None:
    """Tree-level vanishing does not close universal or physical flavor."""

    payload = _payload()

    assert payload["classification"] == "SCOPED_TREE_LEVEL_NO_GO"
    assert payload["complete_tree_level_down_matrix_available"] is True
    assert payload["nontrivial_holomorphic_down_matrix_available"] is False
    assert payload["physical_yukawa_matrix_available"] is False
    assert payload["extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert payload["exact"] is True
    assert payload["next_required_object"] == (
        "every exterior-allowed universal down-matrix coefficient"
    )


def test_nonzero_tree_entry_requires_no_fabricated_boundary() -> None:
    """A future nonzero residue is exact without an impossible primitive."""

    entry = DownTreeEntry(
        0,
        1,
        Eisenstein(1),
        1,
        "matter",
        1,
        "scalar",
        True,
        1,
        None,
        None,
        None,
        None,
    )

    assert entry.exact
    assert entry.as_record()["zero_boundary_witness"] is None
