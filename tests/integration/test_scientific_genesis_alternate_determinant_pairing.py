"""Regress the frozen alternate constituent's local determinant pairing.

Owns:
    Exact chart, overlap, provenance, and nonpromotion assertions.

Depends on:
    The alternate research calculation and its content-addressed artifact.

Must not:
    Infer a physical Higgs cocycle or Yukawa from local pairings.

Phase 0:
    Research integration tests for a strict chain-map prerequisite.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_constituent_determinant_pairing import (
    OUTPUT,
    alternate_constituent_determinant_pairing,
)


def test_alternate_pairings_glue_but_do_not_reuse_selected_ray() -> None:
    """The alternate form annihilates relations and glues on all overlaps."""

    result = alternate_constituent_determinant_pairing()
    assert result["chart_count"] == 6
    assert result["overlap_count"] == 30
    assert 0 < result["charts_different_from_selected_ray"] <= 6
    assert len(result["chart_pairing_digests"]) == 6
    assert result["relation_annihilation_exact"] is True
    assert result["alternating_exact"] is True
    assert result["hypersurface_factorization_exact"] is True
    assert result["corrected_overlap_covariance_exact"] is True


def test_alternate_pairing_artifact_stops_at_local_scope() -> None:
    """A paired quotient is not yet a Higgs tensor chain map."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert payload == alternate_constituent_determinant_pairing()
    assert payload["hom_to_tensor_chain_map_constructed"] is False
    assert payload["exterior_cone_higgs_cocycle_constructed"] is False
