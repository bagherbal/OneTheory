"""Test the exact deck-equivariance gate for Tier A local transitions.

Owns:
    Coordinate substitution, chart permutation, failed transition-pair
    reporting, and the prohibition on guessed gauge lifts.

Depends on:
    The computable-carrier equivariance experiment and exact Heisenberg
    coordinate convention.

Must not:
    Convert kernel actions into bundle linearizations or report quotient descent
    after an invariant-transition failure.

Phase 0:
    The formal Tier A transition candidates fail this gate and remain research
    data until explicit lifts are derived.
"""

from __future__ import annotations

from research.experiments.computable_carrier.equivariance import (
    tier_a_equivariance,
    tier_a_split_equivariance,
)


def test_tier_a_equivariance_failure_is_exact_and_explicit() -> None:
    """Both coordinate generators fail every formal transition pair."""

    report = tier_a_equivariance()

    assert report.group_relations_verified
    assert not report.honest
    assert len(report.checks) == 4
    assert all(not check.invariant for check in report.checks)
    assert all(not check.gauge_lift_constructed for check in report.checks)
    assert all(len(check.failed_pairs) == 6 for check in report.checks)


def test_split_derived_lifts_pass_transitions_but_not_group_gate() -> None:
    """Derived split lifts do not substitute for a group linearization."""

    report = tier_a_split_equivariance()

    assert not report.group_relations_verified
    assert not report.honest
    assert report.failed_group_relations == (
        "I3:P^3 != identity",
        "I3:PT != TP",
        "I6:P^3 != identity",
    )
    assert all(check.invariant for check in report.checks)
    assert all(check.gauge_lift_constructed for check in report.checks)
