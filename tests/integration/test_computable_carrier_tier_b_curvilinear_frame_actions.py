"""Test induced frame actions and Fitting covers for curvilinear candidates.

Owns:
    Regression assertions for normalized quotient frames, corrected local P/T
    action matrices, projective group-law descent, and exact maximal-minor
    cover certificates on all six dP9 charts.

Depends on:
    The exact curvilinear frame-action research audit.

Must not:
    Treat the finite presentation as the selected physical carrier, infer
    global Ext identification, or bypass explicit full-cover deck descent.

Phase 0:
    Frame actions and Fitting covers are tested; physical promotion remains
    unavailable.
"""

from research.experiments.computable_carrier.tier_b_curvilinear_frame_actions import (
    tier_b_curvilinear_frame_action_audits,
)


def test_corrected_curvilinear_lines_have_exact_frame_actions() -> None:
    """All corrected lines induce exact actions in normalized quotient frames."""

    audits = tier_b_curvilinear_frame_action_audits()

    assert len(audits) == 8
    assert [audit.frame_linearized_eigenline_count for audit in audits] == [
        3,
        3,
        0,
        0,
        0,
        0,
        0,
        0,
    ]
    assert [audit.fitting_cover_eigenline_count for audit in audits] == [
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
        line.frame_bases_verified
        and line.fitting_frame_bases_verified
        and line.transition_cocycle_derived
        and len(line.fitting_frames) == 10
        and line.occurrence_count == 72
        and line.commuting_occurrence_count == 72
        and len(line.p_actions) == 6
        and len(line.t_actions) == 12
        and all(action.exact for action in (*line.p_actions, *line.t_actions))
        and line.exact
        for audit in audits[:2]
        for line in audit.lines
    )


def test_corrected_curvilinear_fitting_frames_cover_every_dp9_chart() -> None:
    """Each candidate has degree-one unit identities on all base pivots."""

    audits = tier_b_curvilinear_frame_action_audits()

    assert all(
        [certificate.base_pivot for certificate in line.fitting_cover_certificates]
        == [0, 1, 2]
        and all(
            certificate.degree_bound == 1
            and certificate.nonzero_minor_count == 10
            and certificate.exact
            for certificate in line.fitting_cover_certificates
        )
        for audit in audits[:2]
        for line in audit.lines
    )
    records = [line.as_record() for audit in audits[:2] for line in audit.lines]
    assert all(
        record["covered_dp9_chart_count"] == 6
        and record["selected_as_physics"] is False
        for record in records
    )
