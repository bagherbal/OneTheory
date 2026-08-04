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

import pytest

from onetheory.math.cech import constant_cech_complex, restricted_cech_complex
from onetheory.math.homological import LinearMap, VectorSpace
from onetheory.math.numbers import Rational


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


def test_restricted_cech_complex_uses_typed_face_maps() -> None:
    """Explicit one-dimensional restrictions produce the exact interval Cech complex."""

    first = VectorSpace("U0", ("e0",), Rational)
    second = VectorSpace("U1", ("e1",), Rational)
    intersection = VectorSpace("U01", ("e01",), Rational)
    identity_first = LinearMap(first, intersection, ((1,),))
    identity_second = LinearMap(second, intersection, ((1,),))
    cech = restricted_cech_complex(
        ("U0", "U1"),
        {
            (0,): first,
            (1,): second,
            (0, 1): intersection,
        },
        {
            ((0,), (0, 1)): identity_first,
            ((1,), (0, 1)): identity_second,
        },
    )

    assert cech.complex.cohomology_dimension(0) == 1
    assert cech.complex.cohomology_dimension(1) == 0
    assert cech.complex.differential(1).compose(cech.complex.differential(0)).is_zero()


def test_restricted_cech_complex_rejects_missing_face_restrictions() -> None:
    """A typed cover cannot silently invent a restriction map."""

    space = VectorSpace("U", ("e",), Rational)
    with pytest.raises(ValueError, match="missing a face restriction"):
        restricted_cech_complex(
            ("U0", "U1"),
            {(0,): space, (1,): space, (0, 1): space},
            {},
        )
