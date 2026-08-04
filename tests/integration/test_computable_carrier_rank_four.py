"""Test the bounded rank-four outer-extension frontier.

Owns:
    Exact block-transition cocycles, inverse checks, determinant-one structure,
    and bounded non-boundary certificates for every computed H1 representative.

Depends on:
    The research Hom Čech complex, exact Laurent matrices, and Tier A
    constituent transitions.

Must not:
    Treat bounded representatives as global Ext classes, infer equivariant
    descent, or select a physical carrier from a finite basis ordering.

Phase 0:
    Transition-level rank-four candidates are tested; global mapping-cone,
    descent, stability, spectrum, and promotion gates remain unresolved.
"""

from __future__ import annotations

from research.experiments.computable_carrier.rank_four import tier_a_rank_four_frontier


def test_bounded_rank_four_frontier_has_exact_transition_certificates() -> None:
    """Every bounded H1 representative yields an exact local extension."""

    frontier = tier_a_rank_four_frontier()

    assert frontier.hom.h1_dimension == 14
    assert len(frontier.candidates) == 14
    assert frontier.all_cocycles
    assert frontier.all_locally_free
    assert all(candidate.determinant_one for candidate in frontier.candidates)
    assert all(candidate.bounded_nonboundary for candidate in frontier.candidates)


def test_bounded_rank_four_frontier_does_not_claim_a_mapping_cone() -> None:
    """Transition identities do not promote an unconstructed global complex."""

    frontier = tier_a_rank_four_frontier()

    assert frontier.mapping_cone_constructed is False
    assert frontier.as_record()["selected_candidate"] is None
