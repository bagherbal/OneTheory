"""Test deck linearization of the selected constituent atlases.

Owns:
    Local relation squares, overlap equivariance, order-three laws, deck
    commutation, source-selected line characters, and artifact integrity.

Depends on:
    The Scientific Genesis constituent deck-atlas experiment.

Must not:
    Infer the outer rank-four extension or reuse retired pure-Cech cones.

Phase 0:
    Exact constituent equivariance regression tests only.
"""

import json

from onetheory.math.numbers import OMEGA2, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_constituent_deck_atlases import (
    OUTPUT,
    published_constituent_deck_atlases,
)


def test_selected_constituent_atlases_have_exact_deck_comparisons() -> None:
    """All twenty-four chart maps preserve relations and overlap gauges."""

    first, second = published_constituent_deck_atlases()

    assert first.constituent == "W1"
    assert second.constituent == "W2"
    assert len(first.comparisons) == len(second.comparisons) == 12
    assert first.all_relations_compatible
    assert second.all_relations_compatible
    assert first.overlap_equivariant
    assert second.overlap_equivariant
    assert first.exact
    assert second.exact


def test_local_frame_factors_close_the_deck_group_laws() -> None:
    """The localized P/T comparisons have order three and commute exactly."""

    for atlas in published_constituent_deck_atlases():
        assert atlas.p_order_three
        assert atlas.t_order_three
        assert atlas.actions_commute


def test_extension_line_characters_follow_the_selected_mixed_rays() -> None:
    """W1 uses trivial comparison lines while W2 uses omega squared."""

    first, second = published_constituent_deck_atlases()

    assert {
        item.extension_line_character for item in first.comparisons
    } == {Eisenstein(1)}
    assert {
        item.extension_line_character for item in second.comparisons
    } == {OMEGA2}


def test_constituent_deck_atlas_artifact_is_current() -> None:
    """The frozen certificate records the remaining mixed outer transfer."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored["all_constituent_deck_atlases_exact"] is True
    assert stored["local_line_frame_factors_included"] is True
    assert stored["projective_resolution_commutators_used_as_group_law"] is False
    assert stored["outer_rank_four_extension_reconstructed"] is False
