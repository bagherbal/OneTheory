"""Tests for exact all-parameter Higgs cohomology of the published carrier.

Owns:
    Determinant acyclicity, derived-pushdown dimensions, filtration, jumping,
    source-character provenance, and Wilson color-triplet projection gates.

Depends on:
    The exact Higgs constructor and its content-addressed artifact.

Must not:
    Relabel selected deck characters as generated, choose an extension point,
    or claim full Higgs Čech representatives are available.

Phase 0:
    Higgs dimension and scoped projection tests only; cocycles remain open.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_higgs_cohomology import (
    OUTPUT,
    published_higgs_cohomology,
)


def test_determinant_filtration_makes_higgs_dimensions_parameter_independent() -> None:
    """Acyclic determinant lines remove every outer-parameter connecting map."""

    result = published_higgs_cohomology()

    assert result.determinant_one_dimensions == (0, 0, 0, 0)
    assert result.determinant_two_dimensions == (0, 0, 0, 0)
    assert result.tensor_dimensions == (0, 4, 4, 0)
    assert result.wedge_square_dimensions == (0, 4, 4, 0)
    assert len(result.tensor_terms) == 8


def test_higgs_projection_preserves_selected_character_provenance() -> None:
    """Exact character arithmetic yields one pair without claiming chain derivation."""

    record = published_higgs_cohomology().as_record()

    assert record["wedge_square"] == {
        "cohomology_h0_to_h3": [0, 4, 4, 0],
        "all_extension_parameters": True,
        "jumping_locus": "empty",
        "h1_dimension": 4,
    }
    assert record["deck_characters"] == {
        "h1_character_exponents": [[0, 1], [0, 2], [1, 2], [2, 1]],
        "status": "SELECTED",
        "source_bound": True,
        "generated_from_current_tensor_chain": False,
    }
    assert record["wilson_projection"] == {
        "multiplicities": {
            "up_higgs_doublet": 1,
            "color_triplet": 0,
            "down_higgs_doublet": 1,
            "color_antitriplet": 0,
        },
        "higgs_pairs": 1,
        "massless_color_triplets": 0,
        "character_arithmetic_exact": True,
        "character_input_status": "SELECTED",
    }
    assert record["full_higgs_cech_representatives_computed"] is False
    assert record["arbitrary_extension_point_selected"] is False


def test_higgs_artifact_is_current_and_content_addressed() -> None:
    """The frozen all-parameter Higgs certificate regenerates exactly."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored == published_higgs_cohomology().as_record()
    assert stored["source"]["published_dimensions_used_as_rank_inputs"] is False
