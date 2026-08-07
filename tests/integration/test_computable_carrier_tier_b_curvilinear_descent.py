"""Test internal free-quotient descent of curvilinear rank-two sheaves.

Owns:
    Regression assertions for exact sheafification, Chern data, projective
    equivariance, dP9 deck compatibility, and descent along the free order-nine
    Schoen quotient.

Depends on:
    The internal curvilinear sheaf-descent research audit.

Must not:
    Treat internal verification as independent external certification, select
    a physical constituent, or infer rank-four stability or spectrum.

Phase 0:
    Internal descent is tested; external verification and promotion stay open.
"""

from onetheory.math.numbers import Rational
from research.experiments.computable_carrier.tier_b_curvilinear_descent import (
    tier_b_curvilinear_descent_audits,
)


def test_corrected_curvilinear_sheaves_descend_internally() -> None:
    """All six corrected lines pass exact sheafification and free descent."""

    audits = tier_b_curvilinear_descent_audits()

    assert len(audits) == 8
    assert [audit.internally_descended_eigenline_count for audit in audits] == [
        3,
        3,
        0,
        0,
        0,
        0,
        0,
        0,
    ]
    assert all(audit.exact for audit in audits)
    assert all(
        line.rank == 2
        and line.first_chern_hyperplane == -3
        and line.second_chern_hyperplane_squared == Rational(9)
        and line.locally_free_sheaf_verified
        and line.equivariant_sheaf_verified
        and line.schoen_action_free
        and line.quotient_order == 9
        and line.internal_descent_certificate
        for audit in audits[:2]
        for line in audit.lines
    )


def test_internal_descent_does_not_promote_physics() -> None:
    """External certification and physical selection remain explicit failures."""

    records = [
        line.as_record()
        for audit in tier_b_curvilinear_descent_audits()[:2]
        for line in audit.lines
    ]

    assert all(record["independent_external_descent_certificate"] is False for record in records)
    assert all(record["selected_as_physics"] is False for record in records)
    assert all(record["promotion_ready"] is False for record in records)
