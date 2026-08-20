"""Test the independent full-Čech outer-hypercohomology certificate.

Owns:
    Raw chain square-zero samples, frozen transferred ranks and dimensions,
    epistemic boundaries, and deterministic artifact content addressing.

Depends on:
    Exact constituent cones, the standard-cover transfer engine, and its
    generated scientific certificate.

Must not:
    Recompute the expensive full artifact in every test run, fit rank 90, infer
    deck invariants, or claim explicit outer extension representatives.

Phase 0:
    Cover outer dimensions only; quotient-invariant cocycles remain unresolved.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    _full_differential,
    _include,
    _reduced_basis,
)
from research.experiments.scientific_genesis.published_outer_cech_transfer import OUTPUT
from research.experiments.scientific_genesis.published_outer_reduced_mismatch import (
    published_outer_reduced_mismatch,
)


def test_outer_full_cech_differential_squares_to_zero_on_mixed_sectors() -> None:
    """Koszul and extension signs close on representative edge and middle cells."""

    reduced = published_outer_reduced_mismatch().forward
    samples = (
        _reduced_basis(reduced.left, reduced.right, 0)[252],
        _reduced_basis(reduced.left, reduced.right, 2)[1602],
    )
    for sample in samples:
        initial = _include(sample)
        square = _full_differential(
            _full_differential(initial, reduced.left, reduced.right),
            reduced.left,
            reduced.right,
        )
        assert square.is_zero()


def test_outer_full_cech_transfer_artifact_is_exact_and_content_addressed() -> None:
    """Frozen exact ranks derive both source dimensions without a fitted map."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored["published_dimensions_used_as_rank_inputs"] is False
    assert stored["rank_90_map_inserted"] is False
    assert stored["all_full_cech_complexes_squared_zero"] is True
    assert stored["forward"]["differential_ranks"] == [
        [-1, 0],
        [0, 1512],
        [1, 2988],
        [2, 1764],
        [3, 0],
        [4, 0],
    ]
    assert stored["reverse"]["differential_ranks"] == [
        [-1, 0],
        [0, 1764],
        [1, 2988],
        [2, 1512],
        [3, 0],
        [4, 0],
    ]
    assert stored["forward"]["cohomology_dimensions"] == [
        [-1, 0],
        [0, 0],
        [1, 36],
        [2, 72],
        [3, 0],
        [4, 0],
    ]
    assert stored["reverse"]["cohomology_dimensions"] == [
        [-1, 0],
        [0, 0],
        [1, 72],
        [2, 36],
        [3, 0],
        [4, 0],
    ]
    assert stored["outer_deck_action_computed"] is False
    assert stored["invariant_outer_cocycles_computed"] is False


def test_transferred_cohomology_treats_absent_edge_maps_as_zero() -> None:
    """The serialized edge degrees do not require fabricated boundary maps."""

    reduced = published_outer_reduced_mismatch().forward
    from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
        TransferredOuterHom,
    )

    transfer = TransferredOuterHom(
        reduced,
        reduced.total_differentials,
        tuple((degree, 0) for degree, _ in reduced.total_differentials),
    )

    assert transfer.cohomology_dimension(-1) == 0
    assert transfer.cohomology_dimension(4) == 0
