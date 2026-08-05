"""Test the bounded matrix-valued Hom Čech construction.

Owns:
    Exact transition conjugation, closed coefficient bases, square-zero
    differentials, bounded H1 representatives, and explicit non-Ext status.

Depends on:
    The Tier A constituent transitions, bounded Hom Čech experiment, exact
    homological algebra, and pytest.

Must not:
    Call bounded H1 the full geometric Ext group, infer invariants without a
    deck action, or promote representatives into a physical extension.

Phase 0:
    Bounded Hom computation only; full cover, equivariance, and convergence
    gates remain unresolved.
"""

from __future__ import annotations

from research.experiments.computable_carrier.constituents import tier_a_constituents
from research.experiments.computable_carrier.hom_cech import (
    _monomial_window,
    cached_tier_a_hom_cech,
    tier_a_hom_cech,
)
from research.experiments.computable_carrier.outer_actions import bounded_outer_action


def test_bounded_hom_cech_builds_exact_cycles_and_boundaries() -> None:
    """The generated finite Hom complex has exact d squared equal to zero."""

    hom = tier_a_hom_cech()

    assert hom.bound == 0
    assert tuple(len(hom.basis(degree)) for degree in hom.complex.degrees) == (12, 48, 23)
    assert hom.h1_dimension == 14
    assert len(hom.h1_representatives) == 14
    assert tuple(simplex for simplex, _ in hom.basis_by_simplex(1)) == (
        (0, 1),
        (0, 2),
        (1, 2),
    )
    assert all(
        hom.complex.differential(degree + 1).compose(
            hom.complex.differential(degree)
        ).is_zero()
        for degree in (0, 1)
    )


def test_bounded_hom_cech_does_not_claim_full_ext_or_invariance() -> None:
    """The artifact status preserves the missing global and equivariant gates."""

    hom = tier_a_hom_cech()

    assert hom.status == (
        "bounded Hom Cech complex; full Ext and equivariance remain unproved"
    )


def test_hom_window_respects_each_chart_localization() -> None:
    """Higher bounds admit poles only in the declared inverted Cox variable."""

    chart = tier_a_constituents()[0].cover.charts[0]

    assert _monomial_window(chart, 0) == ((0, 0, 0),)
    assert (-1, 0, 0) in _monomial_window(chart, 1)
    assert (0, -1, 0) not in _monomial_window(chart, 1)


def test_bound_one_builds_a_larger_exact_hom_complex() -> None:
    """The first expanded window has a distinct exact bounded H1 space."""

    hom = cached_tier_a_hom_cech(1)

    assert tuple(hom.complex.spaces.space(i).dimension for i in hom.complex.degrees) == (
        144,
        439,
        210,
    )
    assert hom.h1_dimension == 94
    assert all(
        hom.complex.differential(degree + 1).compose(
            hom.complex.differential(degree)
        ).is_zero()
        for degree in (0, 1)
    )
    action = bounded_outer_action(hom)
    assert all(not item.closed for item in action.actions)
    assert action.invariant_projector_defined is False
