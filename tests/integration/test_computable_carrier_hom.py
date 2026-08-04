"""Test the bounded matrix-valued Hom Čech construction.

Owns:
    Exact transition conjugation, closed coefficient bases, square-zero
    differentials, bounded H1 representatives, and explicit non-Ext status.

Depends on:
    The Tier A constituent transitions, bounded Hom Čech experiment, exact
    homological algebra, and pytest.

Must not:
    Call bounded H1 the full geometric Ext group, infer invariants without a
    deck action, or promote representatives into a physical extension.

Phase 0:
    Bounded Hom computation only; full cover, equivariance, and convergence
    gates remain unresolved.
"""

from __future__ import annotations

from research.experiments.computable_carrier.hom_cech import tier_a_hom_cech


def test_bounded_hom_cech_builds_exact_cycles_and_boundaries() -> None:
    """The generated finite Hom complex has exact d squared equal to zero."""

    hom = tier_a_hom_cech()

    assert hom.bound == 0
    assert tuple(len(hom.basis(degree)) for degree in hom.complex.degrees) == (12, 48, 23)
    assert hom.h1_dimension == 14
    assert len(hom.h1_representatives) == 14
    assert all(
        hom.complex.differential(degree + 1).compose(
            hom.complex.differential(degree)
        ).is_zero()
        for degree in (0, 1)
    )


def test_bounded_hom_cech_does_not_claim_full_ext_or_invariance() -> None:
    """The artifact status preserves the missing global and equivariant gates."""

    hom = tier_a_hom_cech()

    assert hom.status == (
        "bounded Hom Cech complex; full Ext and equivariance remain unproved"
    )
