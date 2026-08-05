"""Test the exact polynomial presentation Hom complex.

Owns:
    The integration checks for the Tier A three-term derived Hom
    presentation, its shifted bases, and its exact square-zero identity.

Depends on:
    The research presentation-Hom experiment and exact polynomial modules.

Must not:
    Treat a presentation-level complex as global Schoen Ext, infer invariant
    classes from its term ranks, or promote it into production physics.

Phase 0:
    The integration frontier is tested; dP9 hypercohomology and descent are
    intentionally unresolved.
"""

from __future__ import annotations

from research.experiments.computable_carrier.polynomial_hom import (
    tier_a_polynomial_hom_complex,
)


def test_tier_a_presentation_hom_is_shifted_and_square_zero() -> None:
    """The explicit I3/I6 Hom presentation has exact chain identities."""

    complex_ = tier_a_polynomial_hom_complex()

    assert [term.rank for _, term in complex_.terms] == [10, 26, 12]
    assert [map_.matrix.shape for _, map_ in complex_.differentials] == [
        (26, 10),
        (12, 26),
    ]
    assert complex_.homogeneous
    assert complex_.squared_zero


def test_presentation_hom_keeps_global_scope_unresolved() -> None:
    """The record names the missing sheafification and descent work."""

    record = tier_a_polynomial_hom_complex().as_record()

    assert record["status"] == (
        "exact presentation-level derived Hom complex; global dP9 "
        "hypercohomology and quotient descent remain unresolved"
    )
