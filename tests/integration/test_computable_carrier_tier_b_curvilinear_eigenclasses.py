"""Test exact common eigenclasses for curvilinear Serre presentations.

Owns:
    Deterministic assertions for simultaneous quotient-action eigenlines,
    explicit extension-map lifts, and support-local Fitting gates.

Depends on:
    The research curvilinear eigenclass audit and exact Eisenstein arithmetic.

Must not:
    Treat a presentation-cokernel eigenline as global Ext, infer descended
    sheaf equivariance, or promote any class to a physical carrier.

Phase 0:
    Class-level invariant candidates are tested; dP9 linearization, descent,
    stability, spectrum, and promotion remain unresolved.
"""

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.tier_b_curvilinear_corrections import (
    tier_b_curvilinear_correction_audits,
)
from research.experiments.computable_carrier.tier_b_curvilinear_eigenclasses import (
    tier_b_curvilinear_eigenclass_audits,
)


def test_curvilinear_quotient_actions_have_complete_exact_eigenlines() -> None:
    """Every commuting quotient-action pair diagonalizes into eight lines."""

    audits = tier_b_curvilinear_eigenclass_audits()

    assert len(audits) == 8
    assert [item.cokernel_dimension for item in audits] == [8] * 8
    assert [item.commuting_quotient_pair_count for item in audits] == [
        72,
        72,
        72,
        72,
        36,
        36,
        36,
        36,
    ]
    assert all(item.quotient_actions_exact for item in audits)
    assert all(item.eigenspaces_one_dimensional for item in audits)
    assert all(item.eigenclass_count == 8 for item in audits)
    assert all(item.commuting_pairs_diagonalize_completely for item in audits)
    assert all(item.exact for item in audits)
    assert all(
        eigenclass.occurrence_count == audit.commuting_quotient_pair_count
        for audit in audits
        for eigenclass in audit.eigenclasses
    )
    assert all(
        next(
            value
            for value in eigenclass.quotient_coordinates
            if not value.is_zero()
        )
        == Eisenstein(1)
        for audit in audits
        for eigenclass in audit.eigenclasses
    )


def test_curvilinear_eigenlines_expose_three_support_free_classes() -> None:
    """Exactly three explicit lines per specialization pass the support gate."""

    audits = tier_b_curvilinear_eigenclass_audits()

    assert all(item.support_locally_free_eigenclass_count == 3 for item in audits)
    assert all(
        eigenclass.relation_shape == (3, 5)
        and len(eigenclass.extension_map) == 3
        and len(eigenclass.support_fitting) == 3
        and all(len(indices) == 2 for _, _, indices in eigenclass.support_fitting)
        for audit in audits
        for eigenclass in audit.eigenclasses
        if eigenclass.support_locally_free
    )
    assert all(
        eigenclass.as_record()["selected_as_physics"] is False
        for audit in audits
        for eigenclass in audit.eigenclasses
    )


def test_curvilinear_eigenlines_have_exact_correction_frontiers() -> None:
    """Coordinate lines correct individually but no strict P/T pair survives."""

    audits = tier_b_curvilinear_correction_audits()

    assert len(audits) == 8
    assert [item.corrected_eigenline_count for item in audits] == [3, 3, 0, 0, 0, 0, 0, 0]
    assert [item.scoped_no_correction_eigenline_count for item in audits] == [
        0,
        0,
        3,
        3,
        3,
        3,
        3,
        3,
    ]
    assert all(item.strict_group_law_eigenline_count == 0 for item in audits)
    assert all(item.exact for item in audits)
    assert all(
        correction.p_compatible_count == 6
        and correction.t_compatible_count == 12
        and correction.corrected_character_occurrence_count == 72
        and correction.representative_correction_complete
        and correction.strict_middle_commuting_occurrence_count == 0
        and correction.strict_resolution_commuting_occurrence_count == 0
        and correction.strict_complete_occurrence_count == 0
        for audit in audits[:2]
        for correction in audit.corrections
    )
    assert all(
        correction.p_compatible_count == 0
        and correction.t_compatible_count == 0
        and correction.scoped_no_representative_correction
        for audit in audits[2:]
        for correction in audit.corrections
    )
