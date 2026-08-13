"""Test derived and source-aligned dP9 constituent deck actions.

Owns:
    Natural chain actions, exact group relations, source-bound character
    alignment, simultaneous conjugacy, invariant classes, and artifact digest.

Depends on:
    The fiber-sensitive Serre complexes, derived deck-action engine, and
    published constituent representation ledger.

Must not:
    Call the linearization character fundamentally derived, promote a
    cohomology class to a mapping cone, or claim the outer bundle exists.

Phase 0:
    Constituent equivariant-cohomology regression tests only.
"""

import json

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.dp9_serre_actions import (
    published_constituent_serre_actions,
)
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_constituent_deck_actions import (
    OUTPUT,
    published_constituent_deck_actions,
)


def test_natural_constituent_actions_are_exact_chain_actions() -> None:
    """Both geometric pullbacks commute with the full total differential."""

    actions = published_constituent_serre_actions()

    assert all(action.actions_commute for action in actions)
    assert all(action.actions_order_three for action in actions)
    assert all(action.induced_actions_commute for action in actions)


def test_published_linearization_character_is_unique_and_common() -> None:
    """Both source representations identify the same unique character twist."""

    actions = published_constituent_deck_actions()

    assert tuple((action.p_twist, action.t_twist) for action in actions) == (
        (OMEGA, Eisenstein(1)),
        (OMEGA, Eisenstein(1)),
    )


def test_aligned_actions_are_simultaneously_conjugate_to_source() -> None:
    """Exact intertwiners identify both P/T pairs with published matrices."""

    actions = published_constituent_deck_actions()

    assert all(action.conjugate_to_published for action in actions)
    assert all(not action.intertwiner.determinant().is_zero() for action in actions)
    assert all(action.chain_relations for action in actions)


def test_each_constituent_has_one_exact_invariant_ext_class() -> None:
    """The aligned two- and five-dimensional spaces each contain one fixed line."""

    actions = published_constituent_deck_actions()

    assert tuple(action.invariant_dimension for action in actions) == (1, 1)
    for action in actions:
        representative = action.invariant_representatives[0]
        assert action.derived.extension.total.differential(1)(representative).is_zero()
        identity = Matrix.identity(
            action.p_induced.row_count,
            scalar_type=Eisenstein,
        )
        fixed_dimension = len(
            Matrix(
                (
                    *((action.p_induced - identity).rows),
                    *((action.t_induced - identity).rows),
                ),
                scalar_type=Eisenstein,
            ).nullspace()
        )
        assert fixed_dimension == 1


def test_constituent_deck_action_artifact_is_content_addressed() -> None:
    """The frozen action certificate matches fresh exact chain calculations."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    fresh = {
        "schema": "published-constituent-deck-actions-v1",
        "constituents": [
            result.as_record() for result in published_constituent_deck_actions()
        ],
        "common_linearization_character": {"P": "omega", "T": "1"},
        "linearization_status": (
            "source-bound selection from published equivariant representations; "
            "not a fundamental derivation"
        ),
        "outer_extension_reconstructed": False,
        "next_required_object": (
            "mapping-cone presentations of W1 and W2 from the certified "
            "invariant constituent cocycles"
        ),
    }

    assert stored == fresh
    assert digest == _canonical_digest(stored)
