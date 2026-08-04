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
from onetheory.math.polynomials import (
    Polynomial,
    PolynomialFreeModule,
    PolynomialMap,
    PolynomialMatrix,
)
from onetheory.math.sheaves import (
    CoxChart,
    CoxChartCover,
    LaurentMatrix,
    LaurentPolynomial,
    LocalizedFreeModule,
    LocalizedModuleMap,
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


def test_polynomial_free_modules_sheafify_to_chart_localized_maps() -> None:
    """Polynomial map data retain named bases after exact localization."""

    chart = CoxChart("U_x", ("x",), ("x",))
    domain = PolynomialFreeModule("F1", ("e",), ((1,),), 1, Rational)
    codomain = PolynomialFreeModule("F0", ("f",), ((0,),), 1, Rational)
    x = Polynomial.monomial((1,), scalar_type=Rational)
    map_ = PolynomialMap(domain, codomain, PolynomialMatrix(((x,),)))

    localized_domain = LocalizedFreeModule.from_polynomial_module(chart, domain)
    localized_map = LocalizedModuleMap.from_polynomial_map(chart, map_)

    assert localized_map.domain == localized_domain
    assert localized_map.matrix.rows[0][0] == LaurentPolynomial.from_polynomial(x)
    assert localized_map.compose(
        LocalizedModuleMap.identity(localized_domain)
    ) == localized_map
