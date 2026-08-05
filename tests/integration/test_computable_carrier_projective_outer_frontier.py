"""Test the scoped finite projective outer-extension no-candidate gate.

Owns:
    Regression checks that every declared projective invariant class is
    examined before the rank-four candidate count is set to zero.

Depends on:
    The research projective outer-extension frontier.

Must not:
    Turn the finite projective result into a global dP9 no-go or create a
    split or generic rank-four fallback.

Phase 0:
    The projective category is closed fail-closed; global comparison remains.
"""

from __future__ import annotations

from research.experiments.computable_carrier.projective_outer_frontier import (
    tier_a_projective_outer_frontier,
)


def test_projective_outer_frontier_has_no_invariant_rank_four_class() -> None:
    """All six exact projective pairs contribute zero outer candidates."""

    frontier = tier_a_projective_outer_frontier()

    assert len(frontier.pair_audits) == 6
    assert frontier.invariant_class_count == 0
    assert frontier.rank_four_candidate_count == 0
    assert frontier.scoped_no_candidate is True


def test_projective_outer_no_candidate_scope_is_explicit() -> None:
    """The no-candidate record keeps the global dP9 gate unresolved."""

    record = tier_a_projective_outer_frontier().as_record()

    assert record["scoped_no_candidate"] is True
    assert "global dP9" in str(record["status"])
    assert "Tier B" in str(record["status"])
