"""Test exact finite Čech incidence and projective-monomial complexes.

Owns:
    Ordered simplex construction, alternating-sign differentials, exact
    square-zero validation, and cohomology dimensions for a finite cover.

Depends on:
    `onetheory.math.cech` and the generic exact homological layer.

Must not:
    Treat constant-coefficient cohomology as a bundle calculation, infer a
    Schoen cover, or use dimensions as missing sheaf representatives.

Phase 0:
    Generic Čech and standard-projective monomial tests only; carrier-specific
    localized sheaf input remains explicit.
"""

from __future__ import annotations

import pytest

from onetheory.math.cech import (
    constant_cech_complex,
    product_projective_monomial_cech_complex,
    projective_monomial_cech_complex,
    restricted_cech_complex,
)
from onetheory.math.homological import LinearMap, VectorSpace
from onetheory.math.numbers import Eisenstein, Rational


def test_constant_cech_complex_has_alternating_square_zero_differential() -> None:
    """A three-chart constant Čech complex has one H0 copy per coefficient."""

    cech = constant_cech_complex(("U0", "U1", "U2"), ("e", "f"))

    assert cech.complex.cohomology_dimension(0) == 2
    assert cech.complex.cohomology_dimension(1) == 0
    assert cech.complex.cohomology_dimension(2) == 0
    assert all(
        cech.complex.differential(degree + 1).compose(cech.complex.differential(degree)).is_zero()
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


def test_projective_monomial_cech_recovers_standard_line_cohomology() -> None:
    """Negative support gives the exact H0, acyclic, and top-degree cases."""

    h0 = projective_monomial_cech_complex(("x0", "x1", "x2"), (2, 1, 0))
    acyclic = projective_monomial_cech_complex(("x0", "x1", "x2"), (-1, 2, 0))
    h2 = projective_monomial_cech_complex(("x0", "x1", "x2"), (-1, -2, -1))

    assert h0.expected_cohomology_degree == 0
    assert tuple(h0.complex.cohomology_dimension(degree) for degree in (0, 1, 2)) == (
        1,
        0,
        0,
    )
    assert acyclic.expected_cohomology_degree is None
    assert tuple(acyclic.complex.cohomology_dimension(degree) for degree in (0, 1, 2)) == (0, 0, 0)
    assert h2.expected_cohomology_degree == 2
    assert tuple(h2.complex.cohomology_dimension(degree) for degree in (0, 1, 2)) == (
        0,
        0,
        1,
    )


def test_projective_monomial_cech_primitive_is_exact_and_deterministic() -> None:
    """An acyclic Laurent monomial cocycle has a reconstructed exact primitive."""

    cech = projective_monomial_cech_complex(
        ("x0", "x1", "x2"),
        (-1, 2, 0),
    )
    cocycle = cech.cochain(1, {(0, 1): 1, (0, 2): 1})

    primitive = cech.primitive(cocycle)

    assert primitive == cech.cochain(0, {(0,): -1})
    assert cech.complex.differential(0)(primitive) == cocycle


def test_projective_monomial_cech_rejects_nontrivial_top_class() -> None:
    """A genuine top cohomology monomial cannot be silently contracted."""

    cech = projective_monomial_cech_complex(
        ("x0", "x1", "x2"),
        (-1, -2, -1),
    )
    top_class = cech.cochain(2, {(0, 1, 2): 1})

    with pytest.raises(ValueError, match="nonzero Čech cohomology"):
        cech.primitive(top_class)


def test_projective_product_cech_uses_signed_totalization() -> None:
    """The tensor differential anticommutes across two projective factors."""

    first = projective_monomial_cech_complex(
        ("x0", "x1", "x2"),
        (-1, 2, 0),
        scalar_type=Eisenstein,
    )
    second = projective_monomial_cech_complex(
        ("p0", "p1"),
        (1, 0),
        scalar_type=Eisenstein,
    )
    total = product_projective_monomial_cech_complex((first, second))

    assert all(
        total.complex.differential(degree + 1).compose(total.complex.differential(degree)).is_zero()
        for degree in total.complex.degrees
    )
    assert all(total.complex.cohomology_dimension(degree) == 0 for degree in total.complex.degrees)


def test_projective_product_cech_preserves_tensor_cohomology_class() -> None:
    """Canonical factor classes tensor to the unique expected product class."""

    p2_top = projective_monomial_cech_complex(
        ("x0", "x1", "x2"),
        (-1, -2, -1),
    )
    p1_top = projective_monomial_cech_complex(("p0", "p1"), (-1, -1))
    total = product_projective_monomial_cech_complex((p2_top, p1_top))
    representative = total.canonical_representative()

    assert representative.space == total.complex.spaces.space(3)
    assert total.complex.differential(3)(representative).is_zero()
    assert total.complex.cohomology_dimension(3) == 1
    with pytest.raises(ValueError, match="nonzero product Čech cohomology"):
        total.primitive(representative)


def test_projective_product_cech_tensor_contraction_is_exact() -> None:
    """Every P2-by-P1 support satisfies ``dh+hd=1-ip`` on every basis cell."""

    p2_supports = tuple(
        tuple(index for index in range(3) if mask & (1 << index))
        for mask in range(8)
    )
    p1_supports = tuple(
        tuple(index for index in range(2) if mask & (1 << index))
        for mask in range(4)
    )
    for p2_support in p2_supports:
        for p1_support in p1_supports:
            factors = (
                projective_monomial_cech_complex(
                    ("x0", "x1", "x2"),
                    tuple(-1 if index in p2_support else 0 for index in range(3)),
                    scalar_type=Eisenstein,
                ),
                projective_monomial_cech_complex(
                    ("p0", "p1"),
                    tuple(-1 if index in p1_support else 0 for index in range(2)),
                    scalar_type=Eisenstein,
                ),
            )
            total = product_projective_monomial_cech_complex(factors)
            for degree in total.complex.degrees:
                space = total.complex.spaces.space(degree)
                for basis_index in range(space.dimension):
                    basis = total.cochain(
                        degree,
                        {total.cells_at(degree)[basis_index]: 1},
                    )
                    homotopy = total.contracting_homotopy(basis)
                    left = total.complex.differential(degree - 1)(homotopy)
                    if degree == max(total.complex.degrees):
                        right = total.cochain(degree, {})
                    else:
                        right = total.contracting_homotopy(
                            total.complex.differential(degree)(basis)
                        )
                    assert left + right == basis - total.projected_representative(basis)
