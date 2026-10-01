"""Test exact rational and Eisenstein-number arithmetic.

Owns:
    Unit and property tests for strict coercion, immutable values, field identities,
    powers, inverses, zero checks, and readable scalar representations.

Depends on:
    `onetheory.math.numbers`, Hypothesis, pytest, and Python’s standard library.

Must not:
    Import the standalone draft, test matrices or polynomials, or use approximate
    coefficients as expected physical data.

Phase 0:
    Mathematical foundation tests only; no physical implementation is provided yet.
"""

from __future__ import annotations

import sys
from dataclasses import FrozenInstanceError
from fractions import Fraction
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from onetheory.math import numbers
from onetheory.math.numbers import (
    E_ONE,
    E_ZERO,
    OMEGA,
    OMEGA2,
    Eisenstein,
    Rational,
    coerce_rational,
)


@st.composite
def rational_values(draw):
    numerator = draw(st.integers(min_value=-100, max_value=100))
    denominator = draw(st.integers(min_value=1, max_value=20))
    return Rational(numerator, denominator)


@st.composite
def eisenstein_values(draw):
    return Eisenstein(draw(rational_values()), draw(rational_values()))


def test_rational_values_are_normalized_and_exact() -> None:
    value = Rational(6, -8)

    assert value == Fraction(-3, 4)
    assert value.numerator == -3
    assert value.denominator == 4
    assert value.is_zero() is False
    assert Rational(0).is_zero() is True
    with pytest.raises(AttributeError):
        value.numerator = 1  # type: ignore[misc]


def test_exact_coercion_accepts_only_supported_scalar_forms() -> None:
    rational = Fraction(5, 7)

    assert coerce_rational(3) == Rational(3)
    assert coerce_rational(rational) == Rational(5, 7)
    assert coerce_rational(Rational(11, 13)) == Rational(11, 13)
    assert Eisenstein.coerce(3) == Eisenstein(3)
    assert Eisenstein.coerce(rational) == Eisenstein(rational)
    assert Eisenstein.coerce(Eisenstein(2, 1)) == Eisenstein(2, 1)


@pytest.mark.parametrize("value", [True, False, 0.5, 1 + 2j, "1/2"])
def test_rational_coercion_rejects_nonexact_values(value: object) -> None:
    with pytest.raises(TypeError):
        coerce_rational(value)
    with pytest.raises(TypeError):
        Rational(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [True, False, 0.5, 1 + 2j, "1/2"])
def test_eisenstein_coercion_rejects_nonexact_values(value: object) -> None:
    with pytest.raises(TypeError):
        Eisenstein.coerce(value)
    with pytest.raises(TypeError):
        Eisenstein(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [True, False, 0.5, 1 + 2j])
def test_eisenstein_equality_rejects_nonexact_values(value: object) -> None:
    with pytest.raises(TypeError):
        assert Eisenstein(1) == value  # type: ignore[comparison-overlap]


def test_rational_arithmetic_remains_exact() -> None:
    left = Rational(1, 3)
    right = Rational(1, 6)

    assert left + right == Rational(1, 2)
    assert left - right == Rational(1, 6)
    assert left * right == Rational(1, 18)
    assert left / right == Rational(2)
    assert 1 - left == Rational(2, 3)
    assert 1 / right == Rational(6)
    assert left**3 == Rational(1, 27)
    assert left ** -1 == Rational(3)


def test_rational_arithmetic_rejects_approximate_operands() -> None:
    value = Rational(1, 2)

    operations = (
        lambda: value + 0.5,
        lambda: value - 0.5,
        lambda: value * 0.5,
        lambda: value / 0.5,
        lambda: 0.5 + value,
        lambda: 0.5 - value,
        lambda: 0.5 * value,
        lambda: 0.5 / value,
    )
    for operation in operations:
        with pytest.raises(TypeError):
            operation()

    for comparison in (
        lambda: value == 0.5,
        lambda: value != 0.5,
        lambda: value < 0.5,
        lambda: value <= 0.5,
        lambda: value > 0.5,
        lambda: value >= 0.5,
        lambda: value == bool(1),
    ):
        with pytest.raises(TypeError):
            comparison()


def test_eisenstein_basis_relation_and_constants() -> None:
    assert OMEGA**2 + OMEGA + E_ONE == E_ZERO
    assert OMEGA2 == OMEGA**2
    assert OMEGA2 + OMEGA + E_ONE == E_ZERO
    assert E_ZERO.is_zero() is True
    assert E_ONE.is_zero() is False


def test_eisenstein_arithmetic_and_inverse() -> None:
    left = Eisenstein(Fraction(2, 3), Fraction(1, 4))
    right = Eisenstein(Fraction(-1, 5), Fraction(2, 7))

    assert left + right == right + left
    assert left - right + right == left
    assert left * right == right * left
    assert left / right * right == left
    assert left.inverse() * left == E_ONE
    assert 2 * left == left + left
    assert left / 2 == left * Rational(1, 2)
    assert 2 / left == Eisenstein(2) * left.inverse()


def test_eisenstein_zero_inverse_and_division_fail() -> None:
    with pytest.raises(ZeroDivisionError):
        E_ZERO.inverse()
    with pytest.raises(ZeroDivisionError):
        E_ONE / E_ZERO
    with pytest.raises(ZeroDivisionError):
        E_ZERO**-1


def test_conjugation_and_norm_of_the_declared_field_generators() -> None:
    """The primitive root and rational subfield fix the involution uniquely."""

    assert OMEGA.conjugate() == OMEGA2
    assert OMEGA2.conjugate() == OMEGA
    assert E_ZERO.norm() == Rational(0)
    assert E_ONE.norm() == OMEGA.norm() == OMEGA2.norm() == Rational(1)
    assert Eisenstein(Rational(2, 3)).conjugate() == Eisenstein(Rational(2, 3))
    assert Eisenstein(Rational(2, 3)).norm() == Rational(4, 9)


@given(left=eisenstein_values(), right=eisenstein_values())
def test_conjugation_is_an_exact_involutive_field_automorphism(
    left: Eisenstein, right: Eisenstein,
) -> None:
    assert left.conjugate().conjugate() == left
    assert (left + right).conjugate() == left.conjugate() + right.conjugate()
    assert (left * right).conjugate() == left.conjugate() * right.conjugate()


@given(left=eisenstein_values(), right=eisenstein_values())
def test_field_norm_is_positive_multiplicative_and_matches_the_inverse(
    left: Eisenstein, right: Eisenstein,
) -> None:
    norm = left.norm()
    assert isinstance(norm, Rational)
    assert norm >= 0
    assert norm.is_zero() == left.is_zero()
    assert left * left.conjugate() == Eisenstein(norm)
    assert (left * right).norm() == norm * right.norm()
    if not left.is_zero():
        assert left.inverse() == left.conjugate() / norm


@pytest.mark.parametrize("exponent", [True, False, 1.0, 1 + 0j])
def test_integer_powers_reject_noninteger_exponents(exponent: object) -> None:
    with pytest.raises(TypeError):
        OMEGA**exponent  # type: ignore[operator]


@given(value=eisenstein_values(), exponent=st.integers(min_value=0, max_value=8))
def test_nonnegative_powers_agree_with_repeated_multiplication(
    value: Eisenstein,
    exponent: int,
) -> None:
    expected = E_ONE
    for _ in range(exponent):
        expected *= value
    assert value**exponent == expected


@given(value=eisenstein_values())
def test_nonzero_inverse_is_a_two_sided_inverse(value: Eisenstein) -> None:
    if value.is_zero():
        return
    inverse = value.inverse()
    assert value * inverse == E_ONE
    assert inverse * value == E_ONE


@given(left=eisenstein_values(), middle=eisenstein_values(), right=eisenstein_values())
def test_eisenstein_field_laws(
    left: Eisenstein,
    middle: Eisenstein,
    right: Eisenstein,
) -> None:
    assert (left + middle) + right == left + (middle + right)
    assert (left * middle) * right == left * (middle * right)
    assert left * (middle + right) == left * middle + left * right


def test_eisenstein_is_immutable_and_has_readable_text() -> None:
    value = Eisenstein(Fraction(3, 2), Fraction(-1, 3))

    with pytest.raises(FrozenInstanceError):
        value.a = Rational(0)  # type: ignore[misc]

    assert str(E_ZERO) == "0"
    assert str(E_ONE) == "1"
    assert str(OMEGA) == "omega"
    assert str(-OMEGA) == "-omega"
    assert value.text() == "3/2-1/3*omega"
    assert "Eisenstein" in repr(value)


def test_numbers_module_does_not_import_the_standalone_draft() -> None:
    source_path = Path(numbers.__file__ or "")

    assert source_path.name == "numbers.py"
    assert "Experimental_Draft_OneTheory" not in str(source_path)
    assert not any(name.startswith("Experimental_Draft_OneTheory") for name in sys.modules)
