"""Guard the exact atlas frontier for unused locally free Serre rays.

Owns:
    Reproduction of both alternate overlap and deck atlases, frame mismatch
    detection, and content-addressed research-artifact integrity.

Depends on:
    The alternate atlas experiment and exact Eisenstein deck actions.

Must not:
    Promote formal frame characters to a quotient determinant or Higgs count.

Phase 0:
    Research-only constituent-equivariance regression checks.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_constituent_deck_atlases import (
    OUTPUT,
    alternate_constituent_deck_atlases,
)


def test_alternate_constituent_atlases_reproduce() -> None:
    """The exact chart and deck gates regenerate the committed certificate."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    assert digest == _canonical_digest(stored)
    assert stored == alternate_constituent_deck_atlases()


def test_alternate_frame_gate_stays_separate_from_quotient_determinant() -> None:
    """A nonuniform P-frame mismatch prevents the selected-frame shortcut."""

    report = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert report["schema"] == "alternate-constituent-deck-atlases-v1"
    assert report["first_constituent_atlas_alternating_frame_character"] == [0, 0]
    assert report["alternate_constituent_atlases_exact"] is True
    assert [case["ray_character_exponents"] for case in report["cases"]] == [
        [0, 1], [1, 1]
    ]
    assert [case["formal_pair_frame_character"] for case in report["cases"]] == [
        [2, 1], [0, 1]
    ]
    for case in report["cases"]:
        assert case["overlap_transition_count"] == 30
        assert case["deck_comparison_count"] == 12
        assert case["overlap_exact"] is True
        assert case["deck_exact"] is True
        assert [
            frame["legacy_frame_uniformly_related"]
            for frame in case["frame_comparisons"]
        ] == [False, True]
    assert report["selected_mixed_p_frame_reusable_for_alternates"] is False
    assert report["alternate_outer_extension_equivariance_certified"] is False
    assert report["alternate_quotient_determinants_certified"] is False
    assert report["alternate_higgs_characters_computed"] is False
