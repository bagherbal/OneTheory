"""Test the fiber-sensitive reduced outer-model mismatch.

Owns:
    Sparse-map addition, square-zero outer totals, forward/reverse dimensions,
    Euler preservation, common excess, epistemic boundary, and artifact digest.

Depends on:
    Exact constituent cones and the cohomology-reduced Schoen outer model.

Must not:
    Insert the missing differential, refute the published carrier, or promote
    reduced cohomology to full outer Ext.

Phase 0:
    Reduced outer-model diagnostic regression tests only.
"""

import json

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_outer import SparseMap
from research.experiments.scientific_genesis.published_outer_reduced_mismatch import (
    OUTPUT,
    _canonical_total_dimensions,
    published_outer_reduced_mismatch,
)


def test_sparse_map_addition_normalizes_exact_cancellation() -> None:
    """Sparse block assembly can sum contributions without retaining zeros."""

    space = VectorSpace("sparse addition", ("e",), Eisenstein)
    left = SparseMap(space, space, (((0, Eisenstein(1)),),))
    right = SparseMap(space, space, (((0, -Eisenstein(1)),),))

    assert (left + right).is_zero()


def test_dimension_record_ignores_ambient_zero_padding() -> None:
    """Serialized support keeps one boundary degree, independent of engine range."""

    dimensions = tuple((degree, 7 if degree in (0, 1) else 0) for degree in range(-3, 5))

    assert _canonical_total_dimensions(dimensions) == [
        [-1, 0],
        [0, 7],
        [1, 7],
        [2, 0],
    ]


def test_reduced_outer_models_are_exact_complexes() -> None:
    """Both fiber-sensitive twisted totals satisfy square zero exactly."""

    result = published_outer_reduced_mismatch()

    assert result.forward.squared_zero
    assert result.reverse.squared_zero


def test_reduced_model_has_a_common_ninety_dimensional_excess() -> None:
    """Forward and reverse H1/H2 exceed source hypercohomology equally."""

    result = published_outer_reduced_mismatch()

    assert result.computed_forward == (126, 162)
    assert result.computed_reverse == (162, 126)
    assert result.common_excess == 90


def test_reduced_model_preserves_the_published_euler_characteristic() -> None:
    """The missing transfer changes adjacent dimensions without changing index."""

    result = published_outer_reduced_mismatch()

    assert result.euler_characteristics_match
    assert result.computed_forward[0] - result.computed_forward[1] == -36
    assert result.computed_reverse[0] - result.computed_reverse[1] == 36


def test_mismatch_requires_cech_transfer_without_guessing_a_map() -> None:
    """The exact discrepancy remains a prerequisite rather than a fitted correction."""

    record = published_outer_reduced_mismatch().as_record()

    assert record["rank_90_map_inserted"] is False
    assert record["published_carrier_refuted"] is False
    assert "Cech contraction" in record["next_required_object"]


def test_reduced_outer_mismatch_artifact_is_content_addressed() -> None:
    """The frozen mismatch equals fresh exact sparse elimination."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == published_outer_reduced_mismatch().as_record()
    assert digest == _canonical_digest(stored)
