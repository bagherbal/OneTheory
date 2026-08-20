"""Tests for generated matter cohomology of the published carrier.

Owns:
    Full-Čech dimensions, strict deck actions, regular representations, dual
    vanishing, parameter independence, and Wilson-projected family gates.

Depends on:
    The transferred constituent complexes and exact matter artifact.

Must not:
    Import published ranks as computation inputs, choose an extension point,
    infer Higgs multiplicity, or call associated-graded classes full cone lifts.

Phase 0:
    Matter-sector chain tests only; the Higgs complex remains unresolved.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_matter_cohomology import (
    OUTPUT,
    published_matter_cohomology,
)


def test_constituent_cech_complexes_derive_regular_h1_representations() -> None:
    """V1 and V2 produce one and two exact regular representations."""

    result = published_matter_cohomology()

    assert result.first.dimensions == (0, 9, 0, 0)
    assert result.second.dimensions == (0, 18, 0, 0)
    assert result.first.action.exact
    assert result.second.action.exact
    assert result.first.invariant_dimension == 1
    assert result.second.invariant_dimension == 2
    assert {value for _, value in result.first.character_multiplicities} == {1}
    assert {value for _, value in result.second.character_multiplicities} == {2}
    assert len(result.first.action.invariant_full_cech) == 1
    assert len(result.second.action.invariant_full_cech) == 2


def test_outer_long_exact_sequence_fixes_matter_for_every_parameter() -> None:
    """Pure constituent H1 makes extension-parameter jumping impossible."""

    result = published_matter_cohomology()
    record = result.as_record()

    assert result.visible_dimensions == (0, 27, 0, 0)
    assert result.dual_dimensions == (0, 0, 27, 0)
    assert {value for _, value in result.visible_character_multiplicities} == {3}
    assert result.wilson_projected_multiplicity == 3
    assert record["outer_long_exact_sequence"]["all_extension_parameters"] is True
    assert record["outer_long_exact_sequence"]["dual_h1_vanishes"] is True
    assert record["wilson_projection"] == {
        "embedding_source": "hep-th/0512177 eq:burt4",
        "multiplicity_per_spin10_16_weight": 3,
        "families": 3,
        "right_handed_neutrinos": 3,
        "anti_families": 0,
        "matter_exotic_blocks": 0,
        "selection_constraint_used_as_rank_input": False,
    }
    assert record["full_universal_visible_h1_chain_lifts_computed"] is False
    assert record["arbitrary_extension_point_selected"] is False


def test_matter_artifact_is_current_and_content_addressed() -> None:
    """The frozen matter certificate matches exact regeneration."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored == published_matter_cohomology().as_record()
    assert stored["source"]["published_dimensions_used_as_rank_inputs"] is False
