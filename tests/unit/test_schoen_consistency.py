"""Test exact curve-lattice and topological carrier identities.

Owns:
    Mordell–Weil action order, degree-one and degree-two shells, orbit counts,
    square-free degree-nine modulus, Chern budgets, descent, Bianchi identity,
    and quotient/cover slopes.

Depends on:
    `onetheory.models.heterotic_schoen.consistency`, concrete geometry, exact
    Rational and Eisenstein arithmetic, and pytest.

Must not:
    Instantiate a hidden bundle, claim HYM or stability, use observations, or
    create a vacuum or physical observable.

Phase 0:
    Exact topological checks only; the hidden output remains a required class.
"""

from __future__ import annotations

from onetheory.math.numbers import Rational
from onetheory.models.heterotic_schoen.consistency import (
    basepoint_algebra,
    mordell_weil_action,
    topological_consistency,
)
from onetheory.models.heterotic_schoen.geometry import schoen_geometry


def test_mordell_weil_shells_and_orbits_have_published_counts() -> None:
    action = mordell_weil_action()

    assert action.apply(action.apply(action.apply((4, -2)))) == (4, -2)
    assert len(action.shell(1)) == 3
    assert len(action.shell_orbits(1)) == 1
    assert len(action.shell(2)) == 6
    assert len(action.shell_orbits(2)) == 2


def test_degree_nine_basepoint_algebra_is_square_free() -> None:
    algebra = basepoint_algebra()

    assert algebra.degree == 9
    assert algebra.square_free


def test_topological_target_is_not_mistaken_for_a_hidden_bundle() -> None:
    result = topological_consistency(schoen_geometry())

    assert result.cover_curve_count == 81
    assert result.quotient_curve_count == 9
    assert result.degree_two_quotient_count == 18
    assert result.hidden_target.coordinates == (Rational(4, 3), Rational(7, 3), Rational(-4))
    assert not result.hidden_target.is_bundle
    assert result.bianchi_identity
    assert result.visible_descent
    assert result.quotient_slope == Rational(-33)
    assert result.cover_slope == Rational(-297)
