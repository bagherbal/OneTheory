"""Test exact chart localization and transition-cocycle primitives.

Owns:
    Laurent normalization, principal-chart inversion, pairwise intersections,
    exact transition composition, and ordered Čech cocycle verification.

Depends on:
    `onetheory.math.sheaves`, exact polynomial arithmetic, and pytest.

Must not:
    Treat a coboundary fixture as a physical bundle, assert a Schoen cover, or
    infer local freeness from a matrix sample.

Phase 0:
    Generic sheaf-engine primitives only; carrier-specific chart certification
    remains a separate research gate.
"""

from __future__ import annotations

from onetheory.math.numbers import Rational
from onetheory.math.polynomials import Polynomial
from onetheory.math.sheaves import (
    CoxChart,
    CoxChartCover,
    LaurentMatrix,
    LaurentPolynomial,
    TransitionCocycle,
)


def _transition(delta: LaurentPolynomial) -> LaurentMatrix:
    """Build a determinant-one unipotent transition matrix."""

    one = LaurentPolynomial.one(3, scalar_type=Rational)
    zero = LaurentPolynomial.zero(3, scalar_type=Rational)
    return LaurentMatrix(((one, delta), (zero, one)))


def test_localization_preserves_exact_terms_and_declares_inversions() -> None:
    """A Cox chart embeds polynomials and exposes only declared inverses."""

    chart = CoxChart("U_x0", ("x0", "x1", "x2"), ("x0",))
    polynomial = Polynomial.monomial((1, 0, 0), scalar_type=Rational)

    localized = chart.localize(polynomial)
    inverse = chart.inverse_monomial("x0")

    assert localized.terms == (((1, 0, 0), Rational(1)),)
    assert (localized * inverse).terms == (((0, 0, 0), Rational(1)),)

    inverse_image = inverse.substitute_monomials(
        ((2, (0, 1, 0)), (1, (0, 0, 1)), (1, (1, 0, 0)))
    )
    assert inverse_image.terms == (((0, -1, 0), Rational(1, 2)),)


def test_chart_intersections_and_transition_cocycle_are_exact() -> None:
    """Coboundary transitions satisfy every ordered triple identity exactly."""

    charts = CoxChartCover(
        (
            CoxChart("U_x0", ("x0", "x1", "x2"), ("x0",)),
            CoxChart("U_x1", ("x0", "x1", "x2"), ("x1",)),
            CoxChart("U_x2", ("x0", "x1", "x2"), ("x2",)),
        )
    )
    f0 = LaurentPolynomial.monomial((1, 0, 0), scalar_type=Rational)
    f1 = LaurentPolynomial.monomial((0, 1, 0), scalar_type=Rational)
    f2 = LaurentPolynomial.monomial((0, 0, 1), scalar_type=Rational)
    values = (f0, f1, f2)
    transitions = tuple(
        (left, right, _transition(values[left] - values[right]))
        for left in range(3)
        for right in range(3)
        if left != right
    )
    cocycle = TransitionCocycle(charts, 2, transitions)

    assert charts.intersection(0, 1).inverted_variables == ("x0", "x1")
    assert cocycle.verifies_cocycle()
    assert cocycle.transition(0, 1).compose(cocycle.transition(1, 0)).is_identity()
