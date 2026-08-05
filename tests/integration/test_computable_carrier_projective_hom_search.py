"""Test the complete declared Tier A projective Hom ray-pair audit.

Owns:
    Regression checks for all locally free I3/I6 presentation ray pairs and
    their exact raw, equivariant, and serialized Hom data.

Depends on:
    The research-only Tier A projective Hom search.

Must not:
    Interpret a presentation-level empty invariant space as a global dP9
    no-go, a quotient descent certificate, or a physical carrier result.

Phase 0:
    The finite presentation ray family is tested exactly; global comparison
    and physical promotion remain unresolved.
"""

from __future__ import annotations

from research.experiments.computable_carrier.projective_hom_search import (
    tier_a_projective_hom_pair_audits,
)


def test_all_tier_a_projective_ray_pairs_are_audited() -> None:
    """Every two-by-three locally free ray pair has explicit exact data."""

    audits = tier_a_projective_hom_pair_audits()

    assert len(audits) == 6
    assert {
        (audit.left.scheme, audit.right.scheme)
        for audit in audits
    } == {("I3", "I6")}
    assert all(audit.raw_ext_one_dimension == 5 for audit in audits)
    assert all(audit.invariant_ext_one_dimension == 0 for audit in audits)
    assert all(audit.deck.p_order_three for audit in audits)
    assert all(audit.deck.p_t_commute for audit in audits)
    assert all(audit.deck.reynolds_projectors_idempotent for audit in audits)


def test_projective_ray_pair_record_contains_chain_level_evidence() -> None:
    """The serialized result includes maps, bases, boundaries, and actions."""

    record = tier_a_projective_hom_pair_audits()[0].as_record()
    hypercohomology = record["hypercohomology"]
    assert isinstance(hypercohomology, dict)
    assert hypercohomology["h0"]["complex"]["differentials"]
    assert hypercohomology["h0"]["complex"]["cohomology"]
    assert hypercohomology["h0"]["complex"]["cohomology"][2]["boundaries"]
    deck = record["deck_action"]
    assert isinstance(deck, dict)
    assert deck["h0_action_p"]["components"]
    assert deck["h0_induced_p"]
    assert deck["h0_invariant_projector"]
    assert "dP9 sheafification" in str(record["status"])
