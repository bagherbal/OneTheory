"""Test the topological screen for descended curvilinear constituents.

Owns:
    Regression checks for the Schoen hyperplane mapping, determinant parity,
    lawful bounded twists, exact Chern data, and the quotient-index exclusion.

Depends on:
    The current curvilinear topology research screen and exact rational data.

Must not:
    Construct outer Ext classes after a failed topology gate, generalize the
    scoped exclusion to other Chern types, or select a physical carrier.

Phase 0:
    The current Chern type is screened; broader Tier B searches remain open.
"""

import pytest

from onetheory.math.numbers import Rational
from research.experiments.computable_carrier.tier_b_curvilinear_topology import (
    curvilinear_topology_screen,
)


def test_cross_factor_pairs_have_an_integral_determinant_obstruction() -> None:
    """Odd tau1/tau2 coefficients cannot be removed by rank-two twists."""

    screen = curvilinear_topology_screen()

    assert screen.cross_factor_parity_obstruction
    assert screen.same_factor_index_identities == (True, True)
    assert screen.exact


def test_lawful_same_factor_pairs_all_have_zero_index() -> None:
    """Every radius-two determinant solution fails the target index exactly."""

    screen = curvilinear_topology_screen()

    assert len(screen.audits) == 40
    assert [sum(audit.factor == factor for audit in screen.audits) for factor in (1, 2)] == [
        20,
        20,
    ]
    assert all(audit.line_twists_descend for audit in screen.audits)
    assert all(audit.determinant_cancels for audit in screen.audits)
    assert all(audit.integrated_third_chern == Rational(0) for audit in screen.audits)
    assert all(audit.quotient_index == Rational(0) for audit in screen.audits)
    assert not any(audit.target_index for audit in screen.audits)
    assert screen.target_index_candidate_count == 0
    assert screen.as_record()["rank_four_outer_ext_available"] is False


def test_empty_smaller_twist_windows_remain_exact_no_candidate_screens() -> None:
    """A finite window with no determinant solution is not an unresolved result."""

    for radius in (0, 1):
        screen = curvilinear_topology_screen(radius)
        assert screen.audits == ()
        assert screen.target_index_candidate_count == 0
        assert screen.exact


def test_curvilinear_topology_radius_is_validated() -> None:
    """The finite twist bound rejects booleans, nonintegers, and negatives."""

    with pytest.raises(TypeError, match="integer"):
        curvilinear_topology_screen(True)
    with pytest.raises(TypeError, match="integer"):
        curvilinear_topology_screen(1.5)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="nonnegative"):
        curvilinear_topology_screen(-1)
