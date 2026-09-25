"""Guard strict full-Čech invariant outer-Ext certificates for the I6 ray.

Owns:
    Content-addressed regression of exact Reynolds images and fail-closed
    rank-four carrier status for ray (0,1).

Depends on:
    The deterministic alternate invariant outer-Ext research artifact.

Must not:
    Promote invariant extension classes to a stable physical bundle.

Phase 0:
    Research-only regression for the equivariant outer-Ext prerequisite.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_constituent_outer_ext import (
    OUTPUT as COVER_OUTPUT,
)
from research.experiments.scientific_genesis.alternate_constituent_outer_invariants import (
    OUTPUT,
)


def test_strict_alternate_outer_invariants_do_not_claim_a_carrier() -> None:
    """Reynolds images must remain explicit cocycles, not a chosen cone."""

    cover = json.loads(COVER_OUTPUT.read_text(encoding="utf-8"))
    cover_digest = cover.pop("artifact_digest")
    assert cover_digest == _canonical_digest(cover)

    record = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest")
    assert digest == _canonical_digest(record)
    assert record["schema"] == "alternate-constituent-outer-invariants-v1"
    assert record["cover_artifact_digest"] == cover_digest
    assert record["ray_character_exponents"] == [0, 1]
    assert record["cover_ext1_dimension"] == 18
    assert record["cover_basis_averaged"] == 18
    invariant_dimension = record["invariant_ext1_dimension"]
    assert isinstance(invariant_dimension, int)
    assert invariant_dimension == 2
    assert record["strict_full_cech_representative_count"] == invariant_dimension
    representatives = record["strict_full_cech_representatives"]
    coordinates = record["reduced_invariant_coordinates"]
    assert len(representatives) == len(coordinates) == invariant_dimension
    assert all(item["term_count"] == len(item["terms"]) for item in representatives)
    assert all(item["terms"] for item in representatives)
    assert all(column for column in coordinates)
    assert record["all_representatives_closed"] is True
    assert record["all_representatives_strictly_deck_fixed"] is True
    assert record["all_representatives_nonboundary_and_independent"] is True
    assert record["common_character_twist_preserves_outer_hom_action"] is True
    assert record["extension_point_selected"] is False
    assert record["universal_rank_four_cone_constructed"] is False
    assert record["stability_chamber_certified"] is False
