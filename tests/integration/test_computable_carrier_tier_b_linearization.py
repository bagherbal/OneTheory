"""Test the bounded Tier B resolution-lift group diagnostic.

Owns:
    Exact assertions for the finite compatible-lift enumeration after the
    Tier B chart local-freeness gate.

Depends on:
    The research Tier B rays, monomial resolution actions, and pytest.
    It does not consume observations or physical parameters.

Must not:
    Treat a failed finite lift search as a global Serre no-go, or promote a
    presentation-level action to quotient descent or a physical bundle.

Phase 0:
    The bounded linearization boundary is tested; global sheaf comparison,
    stability, spectrum, and carrier promotion remain unresolved.
"""

from research.experiments.computable_carrier.tier_b_linearization import tier_b_linearization_audits
from research.experiments.computable_carrier.tier_b_serre_extensions import tier_b_serre_eigenrays

ELIGIBLE_SCHEMES = frozenset(
    {
        "B-monomial-coordinate-orbit-0",
        "B-monomial-coordinate-orbit-1",
        "B-monomial-coordinate-orbit-2",
    }
)


def test_tier_b_linearization_enumerates_the_eligible_rays() -> None:
    """The eight globally locally free rays enter the finite lift audit."""

    audits = tier_b_linearization_audits(
        tier_b_serre_eigenrays(),
        ELIGIBLE_SCHEMES,
    )

    assert len(audits) == 8
    assert {audit.scheme for audit in audits} == ELIGIBLE_SCHEMES
    assert all(len(audit.generators) == 2 for audit in audits)
    assert all(
        generator.relation_equation
        and generator.relation_order_three
        and generator.middle_order_three
        for audit in audits
        for generator in audit.generators
    )


def test_tier_b_linearization_records_the_finite_obstruction() -> None:
    """No declared compatible resolution-lift pair satisfies both commutators."""

    audits = tier_b_linearization_audits(
        tier_b_serre_eigenrays(),
        ELIGIBLE_SCHEMES,
    )

    assert all(audit.resolution_variant_counts == (6, 12) for audit in audits)
    assert all(audit.compatible_variant_counts == (1, 2) for audit in audits)
    assert all(len(audit.compatible_variant_pairs) == 2 for audit in audits)
    assert all(audit.complete_variant_pair_count == 0 for audit in audits)
    assert all(not audit.finite_group_gate_passes for audit in audits)
    assert all(not audit.direct_group_relations_verified for audit in audits)
    assert all(audit.mixed_action_solves_exact for audit in audits)
    assert all(audit.mixed_complete_variant_pair_count == 0 for audit in audits)
    assert all(audit.mixed_scoped_no_complete_pair for audit in audits)
    assert all("quotient-descent certificate" in audit.status for audit in audits)
