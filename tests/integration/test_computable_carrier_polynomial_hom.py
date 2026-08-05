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
    polynomial_hom_degree_slice,
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


def test_low_degree_slices_produce_explicit_cohomology() -> None:
    """Small homogeneous components expose computed, not guessed, classes."""

    parent = tier_a_polynomial_hom_complex()
    observed = {
        degree: polynomial_hom_degree_slice(parent, degree)
        for degree in (-2, -1, 0)
    }

    assert [observed[degree].h1_dimension for degree in (-2, -1, 0)] == [9, 9, 5]
    for _degree, slice_ in observed.items():
        assert slice_.h1_dimension == len(slice_.h1_representatives)
        assert all(
            slice_.complex.differential(1)(representative).is_zero()
            for representative in slice_.h1_representatives
        )
        assert slice_.as_record()["squared_zero"] is True
