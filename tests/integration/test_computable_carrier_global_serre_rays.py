"""Test six-chart pullback certificates for every Tier A Serre ray.

Owns:
    Regression checks for ray-specific relation presentations, Fitting covers,
    and exact line-frame transition identities on the declared atlas.

Depends on:
    The research-only global Tier A Serre ray audit.

Must not:
    Treat the pullback result as quotient descent, global cohomology, or a
    physical bundle certificate.

Phase 0:
    Presentation-level six-chart checks are exact; the dP9 descent gate stays
    unresolved.
"""

from __future__ import annotations

from research.experiments.computable_carrier.global_serre_search import (
    tier_a_global_serre_ray_audits,
)


def test_all_tier_a_rays_have_exact_six_chart_pullback_checks() -> None:
    """All five locally free eigenrays pass the declared pullback gates."""

    audits = tier_a_global_serre_ray_audits()

    assert len(audits) == 5
    assert {item.ray.scheme for item in audits} == {"I3", "I6"}
    assert all(item.audit.fitting_cover_verified for item in audits)
    assert all(item.audit.line_frame_all_invertible for item in audits)
    assert all(item.audit.line_frame_cocycle_consistent for item in audits)


def test_global_ray_audit_keeps_descent_unresolved() -> None:
    """The serialized pullback result does not overclaim a descended bundle."""

    record = tier_a_global_serre_ray_audits()[0].as_record()

    assert record["global_pullback"]["fitting_cover_verified"] is True
    assert "quotient linearization" in str(record["global_pullback"]["status"])
    assert "dP9 descent" in str(record["status"])
