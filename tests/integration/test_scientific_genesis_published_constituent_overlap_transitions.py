"""Test global overlap gluing of the selected constituent presentations.

Owns:
    Sixty ordered gauges, hypersurface residuals, path independence,
    determinant-one changes, inverse identities, cocycles, and artifact digest.

Depends on:
    The Scientific Genesis selected constituent overlap experiment.

Must not:
    Infer deck linearization or the rank-four outer extension.

Phase 0:
    Global cover-presentation regression tests only.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_constituent_overlap_transitions import (
    OUTPUT,
    published_constituent_overlap_atlases,
)


def test_both_selected_constituents_have_exact_global_cover_atlases() -> None:
    """All ordered overlap comparisons preserve the affine cokernel sheaves."""

    first, second = published_constituent_overlap_atlases()

    assert first.constituent == "I3"
    assert second.constituent == "I6"
    assert len(first.transitions) == len(second.transitions) == 30
    assert first.all_relations_compatible
    assert second.all_relations_compatible
    assert first.exact
    assert second.exact


def test_middle_generator_changes_form_determinant_one_cocycles() -> None:
    """Every transition has an exact inverse and every ordered triple composes."""

    for atlas in published_constituent_overlap_atlases():
        assert atlas.all_determinant_one
        assert atlas.inverse_consistent
        assert atlas.cocycle_consistent
        assert all(item.rectangle_path_independent for item in atlas.transitions)


def test_overlap_artifact_is_current_and_content_addressed() -> None:
    """The frozen global atlases leave only deck linearization unresolved."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored["all_global_cover_presentations_exact"] is True
    assert stored["selected_mixed_cocycles_used"] is True
    assert stored["deck_linearizations_constructed"] is False
