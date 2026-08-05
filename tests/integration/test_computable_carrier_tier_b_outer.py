"""Test the scoped Tier B monomial outer-extension frontier.

Owns:
    Exact pair counts, totalization identities, deck-action gates, and the
    fail-closed invariant outer-class result for the declared I3/I6 category.

Depends on:
    The Tier B monomial outer experiment and pytest. It does not consume
    observations or promote a research presentation into the production model.

Must not:
    Treat this scoped result as a no-go for all Tier B schemes, twists, or
    Serre classes, or as evidence of a descended physical carrier.

Phase 0:
    The declared monomial outer frontier is exact; broader Tier B search and
    every physical promotion gate remain unresolved.
"""

from __future__ import annotations

from functools import cache

from research.experiments.computable_carrier.tier_b_outer import (
    TierBOuterFrontier,
    tier_b_outer_frontier,
)


@cache
def _frontier() -> TierBOuterFrontier:
    """Build the expensive scoped outer frontier once for this test module."""

    return tier_b_outer_frontier()


def test_tier_b_monomial_outer_pairs_are_exact() -> None:
    """All declared I3/I6 monomial pairs have exact outer totalizations."""

    frontier = _frontier()

    assert len(frontier.pair_audits) == 12
    assert frontier.complete_for_declared_category
    assert all(item.exact for item in frontier.pair_audits)
    assert all(item.parent.squared_zero for item in frontier.pair_audits)
    assert all(item.dp9.squared_zero for item in frontier.pair_audits)
    assert all(item.projective.ext_one_dimension == 5 for item in frontier.pair_audits)
    assert all(item.dp9.total_h1_dimension == 5 for item in frontier.pair_audits)


def test_tier_b_monomial_outer_actions_close_without_invariants() -> None:
    """The finite deck actions close and leave no invariant outer class."""

    frontier = _frontier()

    assert all(item.group_action_gate for item in frontier.pair_audits)
    assert all(item.invariant_outer_dimension == 0 for item in frontier.pair_audits)
    assert frontier.invariant_outer_class_count == 0
    assert frontier.no_candidate_in_declared_category
