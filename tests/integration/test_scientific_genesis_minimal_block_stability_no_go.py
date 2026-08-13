"""Test the exact minimum-dimensional stability-block exclusion.

Owns:
    Exhaustive pair counts, factor-exchanged topology profiles, Hom restriction
    support, orbit spaces, opposite slopes, and the scoped no-go boundary.

Depends on:
    Complete invariant and automorphism artifacts plus the deterministic
    minimum-block stability classifier.

Must not:
    Extrapolate beyond candidates 3 and 23, select a pair or Ext point, or call
    the scoped block exclusion a global computable-carrier no-go.

Phase 0:
    Minimum-dimensional block tests only; larger invariant Ext blocks remain open.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.minimal_block_stability_no_go import (
    OUTPUT,
    minimal_block_stability_no_go,
)


def test_both_factor_orientations_are_exhaustive_and_independent() -> None:
    """The classifier spans exactly 36 pairs in each factor orientation."""

    result = minimal_block_stability_no_go()
    record = result.as_record()

    assert result.checked_pair_count == 72
    assert result.block_pair_ranges == ((3, 73, 108), (23, 793, 828))
    assert [block["pair_count"] for block in record["candidate_blocks"]] == [36, 36]
    assert [block["topology"]["left_factor"] for block in record["candidate_blocks"]] == [
        1,
        2,
    ]
    assert [block["topology"]["right_factor"] for block in record["candidate_blocks"]] == [
        1,
        2,
    ]


def test_every_minimum_family_has_the_lifted_line_obstruction() -> None:
    """All 72 Ext bases miss the same exact right-line restriction columns."""

    result = minimal_block_stability_no_go()
    record = result.as_record()

    assert result.support_profile == (20, 21, 22, 23)
    assert result.right_line_restriction_indices == (4, 9, 14, 19, 24)
    assert record["restriction_support_intersection"] == []
    assert record["restriction_map_zero_for_every_pair"] is True
    assert record["right_serre_line_lifts_for_every_parameter"] is True
    assert record["opposite_slope_obstruction"] is True
    assert record["every_pair_unstable"] is True


def test_minimum_block_artifact_remains_a_scoped_no_go() -> None:
    """The exact block retirement leaves larger computable families open."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == minimal_block_stability_no_go().as_record()
    assert digest == _canonical_digest(stored)
    assert stored["minimum_dimensional_block_refuted"] is True
    assert stored["global_computable_carrier_no_go"] is False
    assert stored["arbitrary_pair_selected"] is False
    assert stored["arbitrary_extension_point_selected"] is False
