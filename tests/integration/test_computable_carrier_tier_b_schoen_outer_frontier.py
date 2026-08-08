"""Test the scoped representative Schoen-cover outer frontier.

Owns:
    Regression checks for eight exact cover-level length-six outer Hom audits.

Depends on:
    The research-only representative Schoen outer frontier.

Must not:
    Treat the representative screen as a complete Tier B no-go or infer a
    quotient-invariant rank-four extension.

Phase 0:
    The representative screen is exact but intentionally incomplete.
"""

from research.experiments.computable_carrier.tier_b_schoen_outer_frontier import (
    schoen_cover_outer_representative_frontier,
)


def test_eight_representative_cover_outer_audits_vanish() -> None:
    """Both coordinate-orbit schemes vanish in all four orientations."""

    frontier = schoen_cover_outer_representative_frontier()

    assert len(frontier.audits) == 8
    assert frontier.declared_topology_count == 40
    assert frontier.full_presentation_pair_count == 1440
    assert frontier.exact
    assert frontier.all_zero
    assert frontier.as_record()["complete_for_declared_category"] is False
