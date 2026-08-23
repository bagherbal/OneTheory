"""Test strict deck transfer on the selected mixed outer cohomology.

Owns:
    Chain-level equivariance, finite deck relations, independently derived
    invariant dimensions, strict representatives, and artifact integrity.

Depends on:
    The Scientific Genesis mixed outer transfer and Schoen deck actions.

Must not:
    Recompute the full transfer during tests, import retired fixed dimensions,
    select an extension coordinate, or claim a rank-four carrier exists.

Phase 0:
    Research-only exact mixed outer deck-action regression tests.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    _include,
    _reduced_basis,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import (
    OUTPUT,
    _full_action,
    _orientation_contraction,
)


def test_full_mixed_actions_are_exact_chain_automorphisms() -> None:
    """P and T commute with each mixed differential and obey the group law."""

    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    for orientation in range(2):
        contraction = _orientation_contraction(orientation)
        entries = _reduced_basis(
            contraction.left_skeleton,
            contraction.right_skeleton,
            1,
        )
        source = _include(entries[len(entries) // 2])

        for generator in ("P", "T"):
            action = actions[generator]
            acted = _full_action(
                source,
                contraction.left,
                contraction.right,
                action,
            )
            assert contraction.differential(acted) == _full_action(
                contraction.differential(source),
                contraction.left,
                contraction.right,
                action,
            )
            squared = _full_action(
                acted,
                contraction.left,
                contraction.right,
                action,
            )
            assert _full_action(
                squared,
                contraction.left,
                contraction.right,
                action,
            ) == source
        p_after_t = _full_action(
            _full_action(
                source,
                contraction.left,
                contraction.right,
                actions["T"],
            ),
            contraction.left,
            contraction.right,
            actions["P"],
        )
        t_after_p = _full_action(
            _full_action(
                source,
                contraction.left,
                contraction.right,
                actions["P"],
            ),
            contraction.left,
            contraction.right,
            actions["T"],
        )
        assert p_after_t == t_after_p


def test_mixed_outer_action_artifact_is_current() -> None:
    """The certificate freezes exact strict invariants without a point choice."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    orientations = stored["orientations"]

    assert digest == _canonical_digest(stored)
    assert stored["all_deck_actions_exact"] is True
    assert stored["expected_invariant_dimensions_imported"] is False
    assert stored["retired_pure_cech_frames_used"] is False
    assert stored["outer_extension_coordinate_selected"] is False
    assert [item["cover_cohomology_dimension"] for item in orientations] == [
        18,
        54,
    ]
    assert [item["invariant_dimension"] for item in orientations] == [2, 6]
    assert [
        item["strict_invariant_representative_count"] for item in orientations
    ] == [2, 6]
    assert all(item["maximum_action_depth"] <= 4 for item in orientations)
    assert all(item["exact"] for item in orientations)
    assert [
        (len(item["P"]), len(item["P"][0]), len(item["T"]), len(item["T"][0]))
        for item in orientations
    ] == [(18, 18, 18, 18), (54, 54, 54, 54)]
