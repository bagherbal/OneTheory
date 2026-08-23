"""Evaluate exact homogeneous slope inequalities and witness boxes.

Owns:
    Immutable quadratic slope polynomials and rigorous rational upper bounds
    on common coordinate boxes.

Depends on:
    Exact rational arithmetic only.

Must not:
    Attach inequalities to a carrier, infer a stability theorem, choose a
    Kähler point, or identify a structure group.

Phase 0:
    Research-only reusable exact stability-polynomial machinery.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.numbers import Rational


@dataclass(frozen=True, slots=True)
class StabilityPolynomial:
    """One exact quadratic slope inequality in a declared divisor basis."""

    line_class: tuple[int, int, int]
    coefficients: tuple[int, int, int, int, int]
    published_anchor_value: int

    def evaluate(self, point: tuple[Rational, Rational, Rational]) -> Rational:
        """Evaluate the slope at ``(x1, x2, y)`` exactly."""

        x1, x2, y = point
        a, b, c, d, e = (Rational(value) for value in self.coefficients)
        return (
            a * x1 * x1
            + b * x1 * x2
            + c * x1 * y
            + d * x2 * x2
            + e * x2 * y
        )

    def box_upper_bound(
        self,
        center: tuple[Rational, Rational, Rational],
        radius: Rational,
    ) -> Rational:
        """Bound the polynomial above on a common coordinate box."""

        x1, x2, y = center
        a, b, c, d, e = (Rational(value) for value in self.coefficients)
        gradient = (
            Rational(2) * a * x1 + b * x2 + c * y,
            b * x1 + Rational(2) * d * x2 + e * y,
            c * x1 + e * x2,
        )
        linear_bound = sum((abs(value) for value in gradient), Rational(0))
        quadratic_bound = sum(
            (abs(value) for value in (a, b, c, d, e)),
            Rational(0),
        )
        return (
            self.evaluate(center)
            + linear_bound * radius
            + quadratic_bound * radius * radius
        )


__all__ = ["StabilityPolynomial"]
