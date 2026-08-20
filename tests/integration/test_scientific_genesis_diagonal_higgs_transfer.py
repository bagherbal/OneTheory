"""Test the synchronized diagonal transfer of the two published constituents.

Owns:
    Exact square-zero, cohomology, and perturbation-depth gates for the full
    diagonal tensor complex.

Depends on:
    Source-selected constituent cones and the diagonal Schoen line engine.

Must not:
    Use expected Higgs dimensions as matrix inputs or claim quotient physics.

Phase 0:
    Cover-level synchronized Higgs cohomology is tested.
"""

from research.experiments.scientific_genesis.diagonal_higgs_transfer import (
    diagonal_higgs_transfer,
)


def test_diagonal_tensor_transfer_exposes_constituent_pushdown_mismatch() -> None:
    """The reconstructed cones fail closed against published Higgs cohomology."""

    result = diagonal_higgs_transfer()

    assert result.squared_zero
    assert result.geometric_dimensions == (0, 14, 18, 4)
    assert not result.matches_published_higgs_cohomology
    assert all(
        result.cohomology_dimension(degree) == 0
        for degree, _ in result.spaces
        if degree not in range(4)
    )
    assert {
        degree: depth
        for degree, depth in result.path_depths
        if degree in (0, 1, 2)
    } == {0: 7, 1: 6, 2: 5}
