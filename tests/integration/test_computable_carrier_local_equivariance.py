"""Test raw deck actions on local Serre Cech classes."""

from __future__ import annotations

from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.local_equivariance import (
    tier_a_local_cech_deck_actions,
)


def test_raw_local_deck_actions_have_exact_group_relations() -> None:
    """P/T actions have order three and commute before line compensation."""

    actions = tier_a_local_cech_deck_actions()
    assert len(actions) == 4
    assert all(action.order_three for action in actions)
    assert all(action.commutes_with_other_generator for action in actions)


def test_raw_local_invariants_distinguish_i3_and_i6() -> None:
    """I3 is raw-invariant while I6 needs line-character compensation."""

    actions = tier_a_local_cech_deck_actions()
    by_scheme = {
        scheme: tuple(item for item in actions if item.scheme == scheme)
        for scheme in ("I3", "I6")
    }
    assert {item.cocycle_multiplier for item in by_scheme["I3"]} == {Eisenstein(1)}
    assert {item.raw_invariant_dimension for item in by_scheme["I3"]} == {1}
    assert {item.cocycle_multiplier for item in by_scheme["I6"]} == {OMEGA}
    assert {item.raw_invariant_dimension for item in by_scheme["I6"]} == {0}
