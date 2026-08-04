"""Test exact published Schoen geometry and symmetry invariants.

Owns:
    Frozen Cox metadata, free quotient data, Heisenberg relations, cubic
    characters, quotient intersections, descent, and slope normalization.

Depends on:
    `onetheory.models.heterotic_schoen.geometry`, exact Rational and Eisenstein
    arithmetic, and pytest.

Must not:
    Implement metrics, bundles, physical Yukawas, observations, or native-origin
    maps; these tests cover only the established carrier handoff.

Phase 0:
    Concrete exact carrier tests only; unresolved downstream physics remains open.
"""

from __future__ import annotations

from onetheory.math.numbers import OMEGA2, Eisenstein, Rational
from onetheory.models.heterotic_schoen.geometry import (
    SCHOEN_COVERING_DEGREE,
    schoen_geometry,
)


def test_schoen_cover_quotient_and_frozen_cox_presentation() -> None:
    geometry = schoen_geometry()

    assert geometry.cover.space.fundamental_group_order == 1
    assert geometry.quotient.order == SCHOEN_COVERING_DEGREE
    assert geometry.quotient.acts_freely
    assert geometry.cover.cox.multidegrees[-2:] == (("p1", (3, 1, 0)), ("p2", (0, 1, 3)))
    assert geometry.cover.cox.coefficient_relation == "omega^2 + omega + 1 = 0"


def test_heisenberg_lifts_and_eigen_cubic_characters_are_exact() -> None:
    geometry = schoen_geometry()

    assert geometry.heisenberg.order_three_p
    assert geometry.heisenberg.order_three_t
    assert geometry.heisenberg.projective_commutator
    assert geometry.heisenberg.deck_commutator
    assert tuple(cubic.name for cubic in geometry.eigen_cubics) == ("F", "G")
    assert geometry.eigen_cubics[0].p_character == OMEGA2
    assert geometry.eigen_cubics[1].p_character == Eisenstein(1)


def test_quotient_intersections_descent_and_cover_slope_use_named_normalizations() -> None:
    geometry = schoen_geometry()
    divisor = geometry.quotient_divisor((1, 2, -1))
    first_chern = geometry.quotient_divisor((-2, 2, 0))
    kahler = geometry.quotient_divisor((6, 9, 3))

    assert geometry.quotient_intersections.entries == (
        ((0, 0, 1), Rational(1, 3)),
        ((0, 1, 1), Rational(1, 3)),
        ((0, 1, 2), Rational(1)),
    )
    assert geometry.square(divisor) == (Rational(-4, 3), Rational(-1, 3), Rational(4))
    assert geometry.descent_congruence((1, 2, 0))
    assert not geometry.descent_congruence((1, 1, 0))
    assert geometry.bundle_slope(first_chern, kahler, 2) == Rational(-33)
    assert geometry.cover_slope(
        geometry.cover_divisor((-2, 2, 0)), geometry.cover_divisor((6, 9, 3)), 2
    ) == Rational(-297)
