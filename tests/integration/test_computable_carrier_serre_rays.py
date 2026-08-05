"""Test the complete finite presentation-level Serre eigenray audit.

Owns:
    Enumeration and local-freeness filtering of all exact I3/I6 rays in the
    declared derived presentation diagnostic.

Depends on:
    The research ray audit, exact Eisenstein algebra, and pytest. It does not
    consume observations or reference-carrier cocycles.

Must not:
    Treat finite eigenray counts as sheaf Ext dimensions, claim a global
    linearization, or promote a ray without independent sheaf comparison.

Phase 0:
    The finite presentation family is audited exactly; full global Ext and
    quotient descent remain unresolved.
"""

from __future__ import annotations

from collections import Counter

from research.experiments.computable_carrier.serre_rays import (
    tier_a_serre_eigenclass_variants,
)


def test_all_locally_free_presentation_eigenrays_are_serialized() -> None:
    """The finite diagnostic retains both I3 and all I6 local-free rays."""

    variants = tier_a_serre_eigenclass_variants()

    assert Counter(variant.scheme for variant in variants) == Counter({"I3": 2, "I6": 3})
    assert all(variant.locally_free_at_support for variant in variants)
    assert all(
        variant.complete_variant_pair_count == 0
        for variant in variants
    )


def test_finite_ray_audit_keeps_sheaf_scope_explicit() -> None:
    """Presentation rays cannot silently become invariant sheaf classes."""

    variants = tier_a_serre_eigenclass_variants()

    assert all("sheaf Ext comparison" in variant.as_record()["status"] for variant in variants)
