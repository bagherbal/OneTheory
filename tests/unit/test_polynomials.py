"""Test immutable exact sparse polynomial algebra.

Owns:
    Unit and property tests for normalized sparse terms, exact arithmetic,
    substitution, polynomial-matrix minors, and univariate field algorithms.

Depends on:
    `onetheory.math.polynomials`, `onetheory.math.numbers`, Hypothesis, pytest,
    and Python’s standard-library dataclass exceptions.

Must not:
    Import the standalone draft, test ideals or Groebner bases, use numerical roots,
    or treat Hilbert–Burch and modulus identities as physical claims.

Phase 0:
    Mathematical foundation tests only; no physical implementation is provided yet.
"""

from __future__ import annotations

import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from onetheory.math.numbers import E_ONE, OMEGA, Eisenstein, Rational
from onetheory.math.polynomials import (
    Polynomial,
    derivative,
    determinant,
    divmod_univariate,
    gcd,
    maximal_minors,
    substitute_monomials,
)


@st.composite
def rational_bivariate_polynomials(draw) -> Polynomial:
    coefficients = draw(
        st.lists(
            st.integers(min_value=-3, max_value=3),
            min_size=6,
            max_size=6,
        )
    )
    exponents = ((0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2))
    return Polynomial(
        zip(exponents, coefficients, strict=True),
        variable_count=2,
    )


def test_sparse_terms_are_normalized_and_immutable() -> None:
    polynomial = Polynomial(
        [((1, 0), 2), ((1, 0), -2), ((0, 1), 3)],
        variable_count=2,
    )
    zero = Polynomial({(2, 0): 0}, variable_count=2)

    assert polynomial.terms == (((0, 1), Rational(3)),)
    assert zero == Polynomial.zero(2)
    assert polynomial.is_zero() is False
    assert Polynomial.zero(2).is_zero() is True
    assert polynomial[(1, 0)] == Rational(0)

    with pytest.raises(FrozenInstanceError):
        polynomial._terms = ()  # type: ignore[misc]


def test_monomial_validation_and_exact_scalar_policy() -> None:
    assert Polynomial.monomial((2, 1), Eisenstein(1), scalar_type=Eisenstein).degree == 3
    assert Polynomial.one(2).coefficient((0, 0)) == Rational(1)
    assert Polynomial.from_coefficients((1, 0, 2)).univariate_degree == 2

    with pytest.raises(ValueError):
        Polynomial.monomial((1, -1))
    with pytest.raises(TypeError):
        Polynomial.monomial((1.0,))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        Polynomial.monomial((1,), 0.5)
    with pytest.raises(ValueError):
        Polynomial({(1,): 1}, variable_count=2)


def test_exact_arithmetic_and_integer_powers() -> None:
    x = Polynomial.monomial((1, 0))
    y = Polynomial.monomial((0, 1))
    polynomial = x + y

    assert polynomial - y == x
    assert -x + x == Polynomial.zero(2)
    assert polynomial.scale(Rational(1, 2)) * 2 == polynomial
    assert x * y == Polynomial.monomial((1, 1))
    assert (x + y) ** 2 == x**2 + 2 * x * y + y**2
    assert polynomial**0 == Polynomial.one(2)
    with pytest.raises(ValueError):
        polynomial**-1
    with pytest.raises(TypeError):
        polynomial**1.5  # type: ignore[operator]


def test_general_and_monomial_substitution_are_exact() -> None:
    x = Polynomial.monomial((1, 0))
    y = Polynomial.monomial((0, 1))
    t = Polynomial.monomial((1,))
    source = x + y

    assert source.substitute((t, t**2)) == Polynomial.from_coefficients((0, 1, 1))
    assert source.substitute((2, 3)) == Polynomial.constant(5)
    assert substitute_monomials(source, ((2, (1,)), (3, (1,)))) == Polynomial.from_coefficients(
        (0, 5)
    )

    with pytest.raises(ValueError):
        source.substitute((t,))
    with pytest.raises(ValueError):
        source.substitute((Polynomial.monomial((1,)), Polynomial.monomial((1, 0, 0))))


def test_hilbert_burch_minor_identities_from_the_draft() -> None:
    zero = Polynomial.zero(3, scalar_type=Eisenstein)
    a = Polynomial.monomial((1, 0, 0), scalar_type=Eisenstein)
    b = Polynomial.monomial((0, 1, 0), scalar_type=Eisenstein)
    c = Polynomial.monomial((0, 0, 1), scalar_type=Eisenstein)
    matrix_three = ((c, c), (-b, zero), (zero, -a))
    matrix_six = (
        (a, zero, zero),
        (zero, b, zero),
        (-b, -c, a),
        (zero, zero, -c),
    )

    assert maximal_minors(matrix_three) == (a * b, -a * c, b * c)
    assert maximal_minors(matrix_six) == (
        -(b**2 * c),
        a * c**2,
        -(a * b * c),
        a**2 * b,
    )


def test_polynomial_matrix_determinants_and_maximal_minor_validation() -> None:
    x = Polynomial.monomial((1,))
    one = Polynomial.one(1)
    zero = Polynomial.zero(1)

    assert determinant(((x, one), (zero, x))) == x**2
    assert maximal_minors(((x, one), (one, x), (zero, one))) == (
        one,
        x,
        x**2 - one,
    )
    with pytest.raises(ValueError):
        determinant(((x, one),))
    with pytest.raises(ValueError):
        maximal_minors(((x, one),))


def test_degree_nine_modulus_is_square_free() -> None:
    modulus = Polynomial.from_coefficients(
        (
            -1,
            0,
            0,
            -51 - 27 * OMEGA,
            0,
            0,
            24 - 27 * OMEGA,
            0,
            0,
            E_ONE,
        ),
        scalar_type=Eisenstein,
    )
    derivative_modulus = derivative(modulus)
    quotient, remainder = divmod_univariate(modulus, derivative_modulus)

    assert modulus.univariate_degree == 9
    assert quotient * derivative_modulus + remainder == modulus
    assert gcd(modulus, derivative_modulus) == Polynomial.one(
        1,
        scalar_type=Eisenstein,
    )


def test_univariate_division_and_monic_gcd_are_exact() -> None:
    x = Polynomial.monomial((1,), scalar_type=Eisenstein)
    factor = x + Polynomial.one(1, scalar_type=Eisenstein)
    other = x**2 + x.scale(OMEGA) + Polynomial.one(1, scalar_type=Eisenstein)
    dividend = factor * other

    quotient, remainder = dividend.divmod_univariate(factor)
    assert quotient == other
    assert remainder.is_zero()
    assert gcd(dividend, factor) == factor.monic()
    assert derivative(x**3).coefficient((2,)) == Eisenstein(3)

    with pytest.raises(ZeroDivisionError):
        divmod_univariate(dividend, Polynomial.zero(1, scalar_type=Eisenstein))
    with pytest.raises(ValueError):
        Polynomial.zero(2).gcd(Polynomial.zero(2))


@given(
    left=rational_bivariate_polynomials(),
    middle=rational_bivariate_polynomials(),
    right=rational_bivariate_polynomials(),
)
def test_sparse_polynomial_ring_laws(
    left: Polynomial,
    middle: Polynomial,
    right: Polynomial,
) -> None:
    assert left + middle == middle + left
    assert (left + middle) + right == left + (middle + right)
    assert left * (middle + right) == left * middle + left * right


def test_polynomial_module_does_not_import_the_standalone_draft() -> None:
    module_path = Path(
        __import__("onetheory.math.polynomials", fromlist=["__file__"]).__file__ or ""
    )

    assert module_path.name == "polynomials.py"
    assert "Experimental_Draft_OneTheory" not in str(module_path)
    assert not any(name.startswith("Experimental_Draft_OneTheory") for name in sys.modules)
