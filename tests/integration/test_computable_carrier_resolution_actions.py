"""Test exact deck lifts through the Tier A point-scheme resolutions.

Owns:
    Chain-equation, invertibility, order, and projective-commutator assertions
    for the derived I3/I6 Hilbert--Burch resolution actions.

Depends on:
    The computable-carrier resolution-action experiment and exact Eisenstein
    arithmetic.

Must not:
    Treat a resolution action as an Ext or Serre linearization, claim descent,
    or use the published invariant-ray matrices as a substitute for a chain
    derivation.

Phase 0:
    Resolution-level actions are tested; Serre comparison remains unresolved.
"""

from __future__ import annotations

from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from research.experiments.computable_carrier.resolution_actions import (
    tier_a_resolution_actions,
)


def test_tier_a_resolution_actions_are_exact_and_invertible() -> None:
    """Both named Hilbert--Burch complexes admit exact P/T lifts."""

    pairs = tier_a_resolution_actions()

    assert tuple(pair.scheme.name for pair in pairs) == ("I3", "I6")
    assert all(
        pair.order_three
        and all(action.chain_equation and action.invertible for action in pair.actions)
        for pair in pairs
    )


def test_resolution_actions_retain_projective_term_characters() -> None:
    """The two complex terms retain their exact projective commutator factors."""

    pairs = tier_a_resolution_actions()

    assert tuple(pair.target_commutator_scalar for pair in pairs) == (OMEGA, Eisenstein(1))
    assert tuple(pair.source_commutator_scalar for pair in pairs) == (Eisenstein(1), OMEGA2)
