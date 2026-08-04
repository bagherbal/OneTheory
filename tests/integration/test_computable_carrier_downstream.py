"""Test the fail-closed downstream frontier for the new carrier.

Owns:
    Stable dependency-chain records for downstream physical calculations.

Depends on:
    The exact bounded rank-four transition frontier and its explicit missing
    prerequisites.

Must not:
    Treat a missing-input report as a scientific result or import observations
    to fill the unresolved chain.

Phase 0:
    Downstream gates are intentionally unresolved until their complete inputs
    and independent certificates exist.
"""

from __future__ import annotations

from research.experiments.computable_carrier.downstream import tier_a_downstream_frontier


def test_downstream_frontier_is_explicit_and_fail_closed() -> None:
    """Every downstream domain exposes its first missing prerequisite."""

    frontier = tier_a_downstream_frontier()

    assert frontier.promotable is False
    assert tuple(gate.name for gate in frontier.gates) == (
        "stability",
        "spectrum",
        "common_dga",
        "metrics",
        "instantons",
        "hidden_consistency",
    )
    assert all(not gate.promotable for gate in frontier.gates)
    assert all(gate.first_missing_prerequisite == gate.prerequisite_chain[0]
               for gate in frontier.gates)
