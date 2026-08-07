"""Test projective cocycles for corrected curvilinear presentations.

Owns:
    Regression assertions for the central homogeneous-lift commutator and all
    degree-corrected source, middle, target, and relation cocycle counts.

Depends on:
    The exact curvilinear projective-cocycle research audit.

Must not:
    Replace projective cocycles by strict lift commutators, infer dP9 sheaf
    linearization or quotient descent, or select a physical carrier.

Phase 0:
    Presentation cocycles are tested; frame actions and descent remain open.
"""

from research.experiments.computable_carrier.tier_b_curvilinear_projective_cocycles import (
    tier_b_curvilinear_projective_cocycle_audits,
)


def test_corrected_curvilinear_lines_obey_projective_cocycles() -> None:
    """Every corrected occurrence satisfies the graded central comparison."""

    audits = tier_b_curvilinear_projective_cocycle_audits()

    assert len(audits) == 8
    assert all(audit.coordinate_lift_commutator for audit in audits)
    assert [audit.corrected_eigenline_count for audit in audits] == [
        3,
        3,
        0,
        0,
        0,
        0,
        0,
        0,
    ]
    assert [audit.projective_cocycle_eigenline_count for audit in audits] == [
        3,
        3,
        0,
        0,
        0,
        0,
        0,
        0,
    ]
    assert [audit.scoped_no_correction_eigenline_count for audit in audits] == [
        0,
        0,
        3,
        3,
        3,
        3,
        3,
        3,
    ]
    assert all(audit.exact for audit in audits)
    assert all(
        line.occurrence_count == 72
        and line.central_relation_equation
        and line.degree_preserving_occurrence_count == 72
        and line.middle_cocycle_occurrence_count == 72
        and line.target_cocycle_occurrence_count == 72
        and line.source_cocycle_occurrence_count == 72
        and line.complete_cocycle_occurrence_count == 72
        and line.exact
        for audit in audits[:2]
        for line in audit.lines
    )
