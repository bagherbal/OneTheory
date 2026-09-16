"""Test the published-carrier projective-pushout adapter no-go.

Owns:
    Source-ledger dimensions, exact sparse adapter dimensions, square-zero
    gates, content addressing, and the fiber-sensitive reconstruction boundary.

Depends on:
    The visible-carrier artifact and published-pushout mismatch classifier.

Must not:
    Refute the published carrier, identify base pushouts with W1/W2, or fill
    missing fiber-direction maps by convention.

Phase 0:
    Fail-closed published-presentation adapter regression tests only.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_pushout_mismatch import (
    OUTPUT,
    _canonical_total_dimensions,
    published_pushout_mismatch,
)


def test_published_ext_ledger_remains_source_bound() -> None:
    """The selected carrier records 36/72 cover and 4/8 invariant classes."""

    result = published_pushout_mismatch()

    assert result.expected_forward_cover_ext_one == 36
    assert result.expected_reverse_cover_ext_one == 72
    assert result.expected_forward_invariant_ext_one == 4
    assert result.expected_reverse_invariant_ext_one == 8


def test_adapter_dimension_record_ignores_ambient_zero_padding() -> None:
    """The no-go artifact records exact support, not arbitrary zero tails."""

    dimensions = tuple((degree, 5 if degree in (0, 1) else 0) for degree in range(-4, 6))

    assert _canonical_total_dimensions(dimensions) == [
        [-1, 0],
        [0, 5],
        [1, 5],
        [2, 0],
    ]


def test_projective_pushout_adapter_fails_both_cover_dimensions() -> None:
    """Exact sparse complexes disagree with both published Ext directions."""

    result = published_pushout_mismatch()

    assert result.computed_forward_cover_ext_one == 0
    assert result.computed_reverse_cover_ext_one == 63
    assert result.both_complexes_squared_zero
    assert result.computed_forward_cover_ext_one != (
        result.expected_forward_cover_ext_one
    )
    assert result.computed_reverse_cover_ext_one != (
        result.expected_reverse_cover_ext_one
    )


def test_mismatch_preserves_the_published_carrier_scope_boundary() -> None:
    """The failed adapter requires dP9 data without becoming a carrier no-go."""

    record = published_pushout_mismatch().as_record()

    assert record["dimension_mismatch_exact"] is True
    assert record["base_pushouts_identified_with_published_constituents"] is False
    assert record["published_carrier_refuted"] is False
    assert "fiber-sensitive" in record["next_required_object"]


def test_published_pushout_mismatch_artifact_is_content_addressed() -> None:
    """The frozen adapter no-go matches a fresh exact reconstruction."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == published_pushout_mismatch().as_record()
    assert digest == _canonical_digest(stored)
