"""Test exact polynomial free modules and chain maps.

Owns:
    Basis-shift validation, polynomial-valued map composition, square-zero
    free-module complexes, block maps, and exact chain-map commutation.

Depends on:
    `onetheory.math.polynomials` and exact Rational polynomial arithmetic.

Must not:
    Attach physical meanings to module ranks, use numerical coefficients, or
    stand in for a sheaf or bundle certificate.

Phase 0:
    Generic algebra tests only; carrier-specific promotion remains gated.
"""

from __future__ import annotations

import pytest

from onetheory.math.numbers import Rational
from onetheory.math.polynomials import (
    Polynomial,
    PolynomialChainComplex,
    PolynomialChainMap,
    PolynomialFreeModule,
    PolynomialIdeal,
    PolynomialMap,
    PolynomialMatrix,
    determinantal_ideal,
    fitting_ideal,
    polynomial_mapping_cone,
    rank_locus_ideal,
    saturate_by_monomial,
)


def _module(name: str, rank: int = 1) -> PolynomialFreeModule:
    """Return a one-variable exact free module for algebra tests."""

    return PolynomialFreeModule(
        name,
        tuple(f"e{index}" for index in range(rank)),
        tuple((0,) for _ in range(rank)),
        1,
        Rational,
    )


def test_polynomial_chain_complex_and_map_commute_exactly() -> None:
    """Multiplication by x gives a square-zero two-term complex boundary."""

    x = Polynomial.monomial((1,), scalar_type=Rational)
    source_zero = _module("A0")
    source_one = _module("A1")
    target_zero = _module("B0")
    target_one = _module("B1")
    source_differential = PolynomialMap(
        source_one,
        source_zero,
        PolynomialMatrix(((x,),)),
    )
    target_differential = PolynomialMap(
        target_one,
        target_zero,
        PolynomialMatrix(((x,),)),
    )
    source = PolynomialChainComplex({0: source_zero, 1: source_one}, {1: source_differential})
    target = PolynomialChainComplex({0: target_zero, 1: target_one}, {1: target_differential})
    identity_components = {
        0: PolynomialMap(source_zero, target_zero, PolynomialMap.identity(source_zero).matrix),
        1: PolynomialMap(source_one, target_one, PolynomialMap.identity(source_one).matrix),
    }

    chain_map = PolynomialChainMap(source, target, identity_components)

    assert source.squared_zero
    assert target.squared_zero
    assert chain_map.component(0).matrix == PolynomialMap.identity(source_zero).matrix

    cone = polynomial_mapping_cone(chain_map)
    assert cone.degrees == (0, 1, 2)
    assert cone.squared_zero


def test_polynomial_block_maps_preserve_named_direct_sums() -> None:
    """Block assembly retains module order and exact zero entries."""

    left = _module("left")
    right = _module("right")
    one = Polynomial.one(1, scalar_type=Rational)
    zero = Polynomial.zero(1, scalar_type=Rational)
    block = PolynomialMap.block(
        (
            (
                PolynomialMap(left, left, PolynomialMatrix(((one,),))),
                PolynomialMap(right, left, PolynomialMatrix(((zero,),))),
            ),
            (
                PolynomialMap(left, right, PolynomialMatrix(((zero,),))),
                PolynomialMap(right, right, PolynomialMatrix(((one,),))),
            ),
        )
    )

    assert block.domain.rank == 2
    assert block.codomain.rank == 2
    assert block.matrix.rows[0][0] == one
    assert block.matrix.rows[1][1] == one
    assert block.matrix.rows[0][1].is_zero()


def test_polynomial_map_rejects_wrong_module_shape() -> None:
    """A named polynomial map cannot hide a rank mismatch."""

    module = _module("rank-one")
    with pytest.raises(ValueError, match="shape"):
        PolynomialMap(module, module, PolynomialMatrix(((Polynomial.one(1), Polynomial.one(1)),)))


def test_exact_determinantal_fitting_rank_and_monomial_saturation() -> None:
    """Finite ideal operations preserve exact generators and ring scope."""

    x = Polynomial.monomial((1, 0), scalar_type=Rational)
    y = Polynomial.monomial((0, 1), scalar_type=Rational)
    matrix = PolynomialMatrix(((x, y), (Polynomial.zero(2), x)))
    maximal = determinantal_ideal(matrix, 2)
    rank_zero = rank_locus_ideal(matrix, 0)
    first_fitting = fitting_ideal(matrix, 1)

    assert maximal.generators == (x**2,)
    assert set(rank_zero.generators) == {x, y}
    assert set(first_fitting.generators) == {x, y}

    ideal = PolynomialIdeal((x * y, y**2), variable_count=2, scalar_type=Rational)
    saturated = saturate_by_monomial(ideal, (1, 0))
    assert saturated.is_monomial
    assert saturated.monomials == ((0, 1),)

    with pytest.raises(ValueError, match="monomial ideal"):
        saturate_by_monomial(PolynomialIdeal((x + y,)), (1, 0))
