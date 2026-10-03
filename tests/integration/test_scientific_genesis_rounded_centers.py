"""Verify explicitly rounded uncertain centers without losing exact scalar inputs.

Owns:
    Independent Fraction norm bounds, off-center containment under arithmetic,
    policy compatibility, exact-singleton preservation, and precision refinement.

Depends on:
    Existing circular enclosures and exact Q(omega) arithmetic.

Must not:
    Prune uncertain zeros, silently select a precision, fabricate geometric
    inputs, or report physical metric or integration accuracy.

Phase 0:
    Research arithmetic tests; no physical object is approximated here.
"""

from fractions import Fraction

import pytest

from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.scientific_genesis.alternate_metric_enclosures import Ball


@pytest.mark.parametrize("center", (
    Eisenstein(Rational(5, 7), Rational(-2, 11)),
    Eisenstein(Rational(1, 1 << 17), Rational(3, 1 << 17)),
    Eisenstein(Rational(-3, 1 << 17), Rational(5, 1 << 17)),
))
def test_explicit_center_rounding_contains_the_entire_original_disk(center):
    radius = Rational(1, 1024)
    rounded = Ball(center, radius, 80, center_bits=16)
    da, db = Fraction(center.a-rounded.center.a), Fraction(center.b-rounded.center.b)
    # Independent squared complex norm in the fixed (1,omega) basis.
    distance_squared = da*da-da*db+db*db
    assert Fraction(rounded.radius-radius)**2 >= distance_squared
    assert (rounded.center.a * 2**16).denominator == 1
    assert (rounded.center.b * 2**16).denominator == 1
    for direction in (Eisenstein(1), OMEGA, OMEGA**2, -OMEGA):
        assert rounded.contains(center + Eisenstein(radius)*direction)


def test_declared_rounding_propagates_through_all_existing_circle_operations():
    original = ((Eisenstein(Rational(5, 7), Rational(2, 11)), Rational(1, 512)),
                (Eisenstein(Rational(7, 13), Rational(-2, 17)), Rational(1, 1024)))
    left, right = (Ball(c, r, 100, center_bits=40) for c, r in original)
    operations = (
        (left+right, lambda a, b: a+b), (left-right, lambda a, b: a-b),
        (left*right, lambda a, b: a*b), (left/right, lambda a, b: a/b),
        (left**5, lambda a, b: a**5), (left**-2, lambda a, b: a**-2),
        (left.conjugate(), lambda a, b: a.conjugate()), (-left, lambda a, b: -a),
    )
    for bound, operation in operations:
        assert bound.center_bits == 40
        for first in (Eisenstein(1), OMEGA, -OMEGA):
            for second in (Eisenstein(1), OMEGA, OMEGA**2):
                a, b = (c + Eisenstein(r)*direction for (c, r), direction in
                        zip(original, (first, second), strict=True))
                assert bound.contains(operation(a, b))


def test_exact_inputs_stay_exact_even_under_a_declared_center_policy():
    value = Eisenstein(Rational(1, 7), Rational(1, 11))
    exact = Ball(value, 0, 80, center_bits=10)
    assert exact.center == value and exact.radius == 0
    assert (exact**3).center == value**3 and (exact**3).radius == 0
    assert exact.inverse().center == value.inverse() and exact.inverse().radius == 0
    default = Ball(value, Rational(1, 1024), 80)
    assert default.center == value and default.center_bits is None
    rounded = Ball(value, Rational(1, 1024), 80, center_bits=10)
    assert (Ball(Eisenstein(1), 0, 80) + rounded).center_bits == 10
    assert (rounded + Ball(value, 0, 80)).center_bits == 10
    assert (default + exact).center_bits is None


@pytest.mark.parametrize("bits", (0, -1, True, 4.5))
def test_invalid_center_precision_is_rejected_even_for_exact_singletons(bits):
    with pytest.raises(ValueError, match="positive integer"):
        Ball(Eisenstein(1), 0, 80, center_bits=bits)


def test_incompatible_uncertain_center_policies_have_no_silent_conversion():
    left = Ball(Eisenstein(Rational(1, 7)), Rational(1, 1024), 80, center_bits=20)
    for bits in (None, 30):
        right = Ball(Eisenstein(1), Rational(1, 1024), 80, center_bits=bits)
        with pytest.raises(ValueError, match="uncertain-center precisions"):
            left + right
        with pytest.raises(ValueError, match="uncertain-center precisions"):
            right * left


def test_refinement_contracts_displacement_without_altering_declared_input_error():
    center = Eisenstein(Rational(5, 7), Rational(2, 11))
    radius = Rational(1, 2**40)
    coarse, fine = (Ball(center, radius, 100, center_bits=n) for n in (20, 40))
    assert radius <= fine.radius < coarse.radius / 1000
    # Two sound recentered disks need not contain one another. Each must
    # contain the original disk; only the certified error must contract.
    for bound in (coarse, fine):
        assert (center-bound.center).norm() <= (bound.radius-radius)**2


def test_uncertain_zero_is_retained_after_rounding_a_tiny_center():
    bound = Ball(Eisenstein(Rational(1, 2**100)), Rational(1, 2**100), 120, center_bits=20)
    assert bound.center.is_zero() and bound.radius > 0
    assert bound.contains(Eisenstein(Rational(2, 2**100)))
