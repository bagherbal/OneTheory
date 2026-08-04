"""Test the explicit split rank-four outer-extension baseline.

Owns:
    Exact block transition shapes, cocycle identities, determinant-one checks,
    and the explicit split-gauge exclusion.

Depends on:
    The computable-carrier constituent and outer-transition experiments.

Must not:
    Treat the split baseline as a stable non-split SU(4) carrier or claim an
    invariant physical outer class from its dimensions.

Phase 0:
    Split baseline only; the non-split outer extension remains to be derived.
"""

from __future__ import annotations

from research.experiments.computable_carrier.outer import split_rank_four_baseline


def test_split_rank_four_baseline_is_exactly_constructed() -> None:
    """The block transitions satisfy every local algebraic identity."""

    baseline = split_rank_four_baseline()

    assert baseline.rank == 4
    assert baseline.verifies_cocycle
    assert baseline.determinant_one
    assert baseline.split_gauge_witness
    assert all(
        matrix_shape == [4, 4]
        for _, _, matrix_shape in baseline.as_record()["transition_shapes"]
    )


def test_split_rank_four_baseline_cannot_promote_as_the_candidate() -> None:
    """The explicit split witness keeps the non-split gate closed."""

    baseline = split_rank_four_baseline()

    assert baseline.extension_status.endswith("excluded")
    assert baseline.split_gauge_witness
