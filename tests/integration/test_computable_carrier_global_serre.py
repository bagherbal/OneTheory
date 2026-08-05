"""Test the graded global pullback presentation audit.

Owns:
    Unit-ideal Fitting certificates and shift-corrected line-frame transition
    identities for the newly constructed Tier A rank-two pushouts.

Depends on:
    The research global-Serre audit, exact dP9 pencil charts, and pytest.
    It does not consume observations or the published carrier.

Must not:
    Treat local-freeness and line-frame checks as quotient descent, stability,
    spectrum, or equivalence to the published bundle.

Phase 0:
    The exact pullback presentation is tested; equivariant linearization and
    physical promotion remain unresolved.
"""

from __future__ import annotations

from research.experiments.computable_carrier.global_serre import (
    tier_a_global_serre_pushout_audits,
)


def test_tier_a_pushouts_have_unit_fitting_covers_on_every_chart() -> None:
    """Every affine dP9 chart has an exact unit ideal of maximal minors."""

    audits = tier_a_global_serre_pushout_audits()

    assert tuple(audit.scheme for audit in audits) == ("I3", "I6")
    assert all(audit.fitting_cover_verified for audit in audits)
    assert all(
        len(audit.fitting_certificates) == 6
        and all(certificate.minor_count > 0 for certificate in audit.fitting_certificates)
        for audit in audits
    )
    assert all(
        all(verified for _, verified in audit.local_relation_composition)
        for audit in audits
    )


def test_graded_line_frames_glue_exactly_on_the_six_chart_atlas() -> None:
    """Shift-corrected projective frames pass inverse and triple-cocycle checks."""

    audits = tier_a_global_serre_pushout_audits()

    assert tuple(len(audit.line_frame_transitions) for audit in audits) == (30, 30)
    assert all(audit.line_frame_all_invertible for audit in audits)
    assert all(audit.line_frame_cocycle_consistent for audit in audits)
    assert len({audit.transition_digest for audit in audits}) == 2


def test_pullback_audit_keeps_quotient_descent_unresolved() -> None:
    """Exact chart gluing cannot silently become an equivariant carrier."""

    audits = tier_a_global_serre_pushout_audits()

    assert all("quotient linearization" in audit.status for audit in audits)
