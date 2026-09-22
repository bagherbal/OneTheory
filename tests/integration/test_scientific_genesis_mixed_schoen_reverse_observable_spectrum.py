"""Test the exact structural spectrum of the reverse mixed family.

Owns:
    Pure-H1 orientation independence, exterior-filtration invariance, Wilson
    projection, all-P5 physical selection, and artifact integrity.

Depends on:
    The reverse stable family and synchronized constituent spectrum engine.

Must not:
    Import source spectrum dimensions, select a P5 point, or treat reduced
    representatives as full Schoen DGA cocycles.

Phase 0:
    Reverse structural-spectrum regression tests only.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_reverse_observable_spectrum import (
    OUTPUT,
    mixed_schoen_reverse_observable_spectrum,
)


def test_reverse_matter_is_parameter_and_orientation_independent() -> None:
    """Pure constituent H1 makes every reverse connecting rank zero."""

    result = mixed_schoen_reverse_observable_spectrum()
    synchronized = result.synchronized
    record = result.as_record()
    long_exact = record["matter"]["universal_long_exact_sequence"]

    assert result.matter_orientation_independent
    assert synchronized.visible_matter_profile == (0, 27, 0, 0)
    assert synchronized.dual_matter_profile == (0, 0, 27, 0)
    assert long_exact["extension_sequence"] == (
        "0 -> V2 -> E_reverse -> V1 -> 0"
    )
    assert long_exact["orientation_independence"] == {
        "constituent_profiles": [[0, 9, 0, 0], [0, 18, 0, 0]],
        "connecting_map_source_or_target_dimensions": 0,
        "extension_parameter_can_change_rank": False,
        "published_same_spectrum_assertion_used_as_rank_input": False,
    }


def test_reverse_higgs_filtration_is_parameter_independent() -> None:
    """Acyclic determinant endpoints leave the same tensor cohomology."""

    result = mixed_schoen_reverse_observable_spectrum()
    synchronized = result.synchronized
    record = result.as_record()
    filtration = record["higgs"]["determinant_filtration"]

    assert result.higgs_orientation_independent
    assert synchronized.higgs_profile == (0, 4, 4, 0)
    assert synchronized.higgs_characters == ((0, 1), (0, 2), (1, 2), (2, 1))
    assert filtration["reverse_graded_piece_order"] == [
        "det(V2)",
        "V2 tensor V1",
        "det(V1)",
    ]
    assert filtration["orientation_independence"][
        "published_same_spectrum_assertion_used_as_rank_input"
    ] is False


def test_entire_reverse_p5_passes_structural_selection() -> None:
    """Every stable reverse class yields three families and one Higgs pair."""

    record = mixed_schoen_reverse_observable_spectrum().as_record()
    constraints = record["physical_selection_constraints"]

    assert all(
        value
        for key, value in constraints.items()
        if key != "used_as_construction_inputs"
    )
    assert constraints["used_as_construction_inputs"] is False
    assert record["lawful_physical_locus"] == (
        "P^5(Q(omega)) x K_reverse^s"
    )
    assert record["entire_stable_family_passes_structural_spectrum"] is True
    assert record["arbitrary_extension_point_selected"] is False


def test_reverse_spectrum_artifact_is_current_and_content_addressed() -> None:
    """The frozen reverse spectrum matches deterministic regeneration."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored == mixed_schoen_reverse_observable_spectrum().as_record()
