"""Test the deck-character diagnostic for the excess diagonal Higgs cone.

Owns:
    Reduced deck group relations and the content-addressed degree-one
    character decomposition that rules out character-only selection.

Depends on:
    The exact diagonal Higgs action diagnostic and its generated artifact.

Must not:
    Promote excess cone classes, select repeated characters, or replace the
    missing relative chain correction with the published character table.

Phase 0:
    Scoped diagonal-character no-go regression tests only.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.scientific_genesis.diagonal_higgs_actions import (
    OUTPUT,
    _diagonal_action_map,
    _identity,
)


def test_reduced_diagonal_actions_have_order_three() -> None:
    """Both generated deck maps realize their exact order on degree-one cochains."""

    for action in schoen_sparse_deck_actions():
        map_ = _diagonal_action_map(1, action)

        assert map_.compose(map_).compose(map_) == _identity(map_.domain)


def test_character_artifact_rules_out_projection() -> None:
    """The exact character table cannot canonically isolate four Higgs classes."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored["current_cone_h1_dimension"] == 14
    assert stored["character_multiplicities"] == [
        [[0, 0], 3],
        [[0, 1], 2],
        [[1, 0], 3],
        [[1, 1], 2],
        [[2, 0], 2],
        [[2, 1], 2],
    ]
    assert stored["characters_isolate_four_classes"] is False
    assert stored["character_projection_promoted"] is False
    assert stored["full_higgs_representatives_constructed"] is False
