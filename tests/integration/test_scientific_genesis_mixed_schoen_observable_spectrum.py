"""Tests for the observable spectrum of the lawful mixed Schoen family.

Owns:
    Mixed matter ranks, Lefschetz character compression, Higgs filtration,
    Wilson projection, all-parameter selection gates, and artifact integrity.

Depends on:
    The synchronized spectrum constructor and its generated certificate.

Must not:
    Import source dimensions as rank inputs, select a projective parameter,
    or treat derived-P1 representatives as full Schoen DGA cocycles.

Phase 0:
    Structural spectrum tests only; common-DGA lifts remain unresolved.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_observable_spectrum import (
    OUTPUT,
    mixed_schoen_observable_spectrum,
)


def test_synchronized_constituents_derive_parameter_independent_matter() -> None:
    """Selected mixed arrows give pure H1 and hence no extension jumping."""

    result = mixed_schoen_observable_spectrum()

    assert result.first_matter.squared_zero
    assert result.second_matter.squared_zero
    assert result.first_matter_profile == (0, 9, 0, 0)
    assert result.second_matter_profile == (0, 18, 0, 0)
    assert result.visible_matter_profile == (0, 27, 0, 0)
    assert result.dual_matter_profile == (0, 0, 27, 0)


def test_free_action_lefschetz_compresses_matter_deck_representation() -> None:
    """Pure H1 on the free cover forces three regular representations."""

    result = mixed_schoen_observable_spectrum()

    assert len(result.matter_character_multiplicities) == 9
    assert {value for _character, value in result.matter_character_multiplicities} == {3}
    record = result.as_record()
    assert record["matter"]["deck_representation"]["representation"] == (
        "3 Reg(Z3 x Z3)"
    )
    assert record["matter"]["deck_representation"]["chain_action_enumeration_required"] is False
    assert record["matter"]["deck_representation"]["theorem_hypotheses"] == {
        "deck_action_free": True,
        "carrier_equivariant": True,
        "cohomology_concentrated_in_h1": True,
    }


def test_lawful_higgs_filtration_has_one_pair_and_no_triplets() -> None:
    """Acyclic determinant lines make the four Higgs classes all-parameter."""

    result = mixed_schoen_observable_spectrum()
    record = result.as_record()

    assert result.determinant_one_profile == (0, 0, 0, 0)
    assert result.determinant_two_profile == (0, 0, 0, 0)
    assert result.higgs_profile == (0, 4, 4, 0)
    assert result.higgs_characters == ((0, 1), (0, 2), (1, 2), (2, 1))
    assert result.higgs_group_relations
    assert record["higgs"]["wedge_square"]["jumping_locus"] == "empty"
    assert record["higgs"]["wilson_projection"] == {
        "multiplicities": {
            "up_higgs_doublet": 1,
            "color_triplet": 0,
            "down_higgs_doublet": 1,
            "color_antitriplet": 0,
        },
        "higgs_pairs": 1,
        "massless_color_triplets": 0,
    }


def test_entire_lawful_family_passes_without_a_selected_point() -> None:
    """Every stable projective parameter satisfies the structural selection."""

    record = mixed_schoen_observable_spectrum().as_record()

    assert set(record["physical_selection_constraints"].values()) == {False, True}
    assert record["physical_selection_constraints"]["used_as_construction_inputs"] is False
    assert all(
        value
        for key, value in record["physical_selection_constraints"].items()
        if key != "used_as_construction_inputs"
    )
    assert record["lawful_physical_locus"] == "P^1(Q(omega)) x K^s"
    assert record["entire_stable_family_passes_structural_spectrum"] is True
    assert record["arbitrary_extension_point_selected"] is False
    assert record["full_matter_schoen_representatives_computed"] is False
    assert record["full_higgs_schoen_representatives_computed"] is False


def test_lawful_spectrum_artifact_is_current_and_content_addressed() -> None:
    """The frozen certificate exactly matches deterministic regeneration."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored == mixed_schoen_observable_spectrum().as_record()
    assert stored["source"]["source_cohomology_dimensions_used_as_rank_inputs"] is False
