"""Test the exact local determinant pairings of both constituents.

Owns:
    Regression gates for complementary-minor forms, relation annihilation,
    hypersurface factorization, and corrected overlap covariance.

Depends on:
    The selected constituent chart presentations and global overlap atlases.

Must not:
    Equate local pairings with the unresolved grouped chain contraction or
    report a scalar Yukawa trace.

Phase 0:
    Integration tests for the determinant-pairing descent certificate.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_determinant_pairing import (
    OUTPUT,
    mixed_schoen_determinant_pairing_audit,
)


def test_complementary_minors_descend_both_rank_two_pairings() -> None:
    """All relation and hypersurface-corrected overlap gates close exactly."""

    audit = mixed_schoen_determinant_pairing_audit()
    assert audit.constituent_names == ("I3", "I6")
    assert audit.middle_ranks == (4, 5)
    assert audit.relation_ranks == (2, 3)
    assert audit.chart_pairing_count == 12
    assert audit.overlap_count == 60
    assert audit.alternating_pairings
    assert audit.relation_annihilation_exact
    assert audit.hypersurface_factorization_exact
    assert audit.corrected_overlap_covariance_exact
    assert len(set(audit.chart_pairing_digests)) == 4
    assert audit.exact


def test_pairing_artifact_stops_before_grouped_totalization() -> None:
    """Local quotient pairings do not masquerade as a cyclic trace."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert payload["local_determinant_pairings_available"] is True
    assert payload["grouped_chain_contraction_available"] is False
    assert payload["cyclic_trace_evaluated"] is False
    assert payload["holomorphic_yukawa_matrix_available"] is False
    assert payload["next_required_object"].startswith(
        "the Alexander-Whitney-compatible lift"
    )
