"""Test projective-presentation Hom hypercohomology and deck actions.

Owns:
    Exact H0/H2 presentation-Hom dimensions, explicit representative counts,
    and the selected-character P/T action audit.

Depends on:
    The research projective hypercohomology and deck-action experiments.

Must not:
    Promote the projective result to a global dP9 Ext no-go, reuse reference
    cocycles, or infer a completed equivariant carrier.

Phase 0:
    The selected presentation route is tested exactly; the broader Tier A
    search and global comparison remain unresolved.
"""

from __future__ import annotations

from research.experiments.computable_carrier.projective_hom_action import (
    tier_a_projective_hom_deck_audit,
)
from research.experiments.computable_carrier.projective_hyperhom import (
    tier_a_projective_hom_hypercohomology,
)


def test_projective_presentation_hypercohomology_is_exact() -> None:
    """The selected presentation has five explicit raw Hom-one classes."""

    hypercohomology = tier_a_projective_hom_hypercohomology()

    assert [
        hypercohomology.h0.complex.cohomology_dimension(degree)
        for degree in hypercohomology.h0.complex.degrees
    ] == [0, 0, 5]
    assert [
        hypercohomology.h2.complex.cohomology_dimension(degree)
        for degree in hypercohomology.h2.complex.degrees
    ] == [0, 0, 0]
    assert hypercohomology.ext_one_dimension == 5
    assert len(hypercohomology.ext_one_representatives) == 5
    assert hypercohomology.as_record()["squared_zero"] is True


def test_projective_presentation_invariant_route_is_scoped_and_empty() -> None:
    """The selected projective action has no trivial-character Hom-one class."""

    audit = tier_a_projective_hom_deck_audit()
    record = audit.as_record()

    assert record["h0_ext1_dimension"] == 5
    assert record["h2_ext_minus1_dimension"] == 0
    assert record["invariant_ext1_dimension"] == 0
    assert record["p_order_three"] is True
    assert record["p_t_commute"] is True
    assert "dP9 sheafification" in str(record["status"])
