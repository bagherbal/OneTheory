"""Guard the exact outer-Ext prerequisite for the surviving alternate ray.

Owns:
    Content-addressed differential ranks and fail-closed invariant-extension
    status for the ray (0,1) cover complex.

Depends on:
    The deterministic alternate mixed outer transfer artifact.

Must not:
    Identify positive cover Ext with invariant Ext or a lawful rank-four cone.

Phase 0:
    Research-only regression for the first alternate outer-Ext computation.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_constituent_outer_ext import (
    OUTPUT,
)


def test_alternate_cover_ext_remains_distinct_from_invariant_extension() -> None:
    """Exact cover ranks cannot be promoted to an equivariant cone by analogy."""

    record = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest")
    assert digest == _canonical_digest(record)
    assert record["schema"] == "alternate-constituent-outer-ext-v1"
    assert record["ray_character_exponents"] == [0, 1]
    assert record["outer_orientation"] == "Hom(V2,V1)"
    degree_zero, degree_one, degree_two = record[
        "reduced_dimensions_degree_0_to_2"
    ]
    incoming_rank, outgoing_rank = record["differential_ranks_degree_0_to_1"]
    assert (degree_zero, degree_one, degree_two) == (1512, 4536, 4824)
    assert (incoming_rank, outgoing_rank) == (1512, 3006)
    assert incoming_rank <= degree_zero
    assert outgoing_rank <= degree_two
    assert record["cover_h0_dimension"] == degree_zero - incoming_rank
    assert record["cover_ext1_dimension"] == (
        degree_one - incoming_rank - outgoing_rank
    )
    assert record["cover_h0_dimension"] == 0
    assert record["cover_ext1_dimension"] == 18
    assert record["d_squared_zero"] is True
    assert record["invariant_ext1_dimension_computed"] is False
    assert record["outer_extension_constructed"] is False
    assert record["determinant_repaired_universal_cone_constructed"] is False
