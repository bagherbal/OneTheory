"""Test exact P1 pushdown constraints used by the Tier A architecture.

Owns:
    Leray basis dimensions, character-labelled representatives, and source
    provenance for the W1/W2 pushdown boundary.

Depends on:
    The computable-carrier pushdown experiment and the exact homological
    vector-space primitives.

Must not:
    Treat source-backed pushdowns as a new global bundle, fabricate the missing
    dP9 coboundary, or identify them with a selected carrier.

Phase 0:
    Pushdown constraints are tested; global Serre patching and outer
    hypercohomology remain unresolved.
"""

from __future__ import annotations

from research.experiments.computable_carrier.pushdown import (
    tier_a_pushdown_constraints,
)


def test_tier_a_pushdowns_have_exact_leray_dimensions() -> None:
    """The source-backed W1/W2 constraints produce deterministic bases."""

    constraints = tier_a_pushdown_constraints()

    assert tuple(constraint.dimensions() for constraint in constraints) == (
        ((0, 0), (1, 1), (2, 0)),
        ((0, 0), (1, 4), (2, 0)),
    )
    assert all(
        len(constraint.representatives(1)) == constraint.space(1).dimension
        for constraint in constraints
    )


def test_pushdown_constraints_keep_coboundary_and_provenance_explicit() -> None:
    """The two distinct coboundary statuses remain source-labelled inputs."""

    constraints = tier_a_pushdown_constraints()

    assert tuple(constraint.coboundary_status for constraint in constraints) == (
        "isomorphism",
        "zero",
    )
    assert all(constraint.source_equations for constraint in constraints)
