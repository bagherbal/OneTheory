"""Test the bounded affine rank-four equivariance search.

Owns:
    Exact Eisenstein affine solves for local upper-block gauge lifts and the
    distinction between generator-level transition solutions and group descent.

Depends on:
    One bounded rank-four transition candidate and exact Laurent/RREF algebra.

Must not:
    Treat a finite monomial window as a complete no-go theorem or use a local
    solution with failed group relations as an equivariant carrier.

Phase 0:
    The finite gauge search is diagnostic and remains outside production.
"""

from __future__ import annotations

from research.experiments.computable_carrier.equivariant_extensions import (
    bounded_extension_equivariance,
)
from research.experiments.computable_carrier.rank_four import tier_a_rank_four_frontier


def test_bounded_affine_search_records_scoped_lift_results() -> None:
    """A bounded solve reports local equations and group failures separately."""

    frontier = tier_a_rank_four_frontier()
    report = bounded_extension_equivariance(frontier.candidates[2], bound=2)

    assert all(lift.solvable for lift in report.lifts)
    assert all(lift.transition_equations_verified for lift in report.lifts)
    assert report.failed_group_relations == ("P^3 != identity", "PT != TP")
    assert report.group_relations_verified is False


def test_bounded_affine_search_can_fail_inside_the_declared_window() -> None:
    """No solution in one window is preserved as a scoped unresolved result."""

    frontier = tier_a_rank_four_frontier()
    report = bounded_extension_equivariance(frontier.candidates[0], bound=2)

    assert any(not lift.solvable for lift in report.lifts)
    assert report.group_relations_verified is False
