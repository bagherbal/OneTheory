"""Test exact constant-coefficient Čech incidence complexes.

Owns:
    Ordered simplex construction, alternating-sign differentials, exact
    square-zero validation, and cohomology dimensions for a finite cover.

Depends on:
    `onetheory.math.cech` and the generic exact homological layer.

Must not:
    Treat constant-coefficient cohomology as a bundle calculation, infer a
    Schoen cover, or use dimensions as missing sheaf representatives.

Phase 0:
    Generic Čech incidence tests only; localized sheaf input remains explicit.
"""

from __future__ import annotations

from onetheory.math.cech import constant_cech_complex


def test_constant_cech_complex_has_alternating_square_zero_differential() -> None:
    """A three-chart constant Čech complex has one H0 copy per coefficient."""

    cech = constant_cech_complex(("U0", "U1", "U2"), ("e", "f"))

    assert cech.complex.cohomology_dimension(0) == 2
    assert cech.complex.cohomology_dimension(1) == 0
    assert cech.complex.cohomology_dimension(2) == 0
    assert all(
        cech.complex.differential(degree + 1).compose(
            cech.complex.differential(degree)
        ).is_zero()
        for degree in (0, 1)
    )


def test_constant_cech_complex_preserves_simplex_basis_order() -> None:
    """Simplex bases and coefficient labels serialize deterministically."""

    cech = constant_cech_complex(("U0", "U1", "U2"), ("e",))

    assert cech.simplices_at(0)[0].vertices == (0,)
    assert cech.simplices_at(1)[-1].vertices == (1, 2)
    assert cech.complex.spaces.space(1).basis == ("(0, 1):e", "(0, 2):e", "(1, 2):e")
