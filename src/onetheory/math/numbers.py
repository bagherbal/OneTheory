"""Exact rational and Eisenstein-number arithmetic.

Owns:
    Strict rational values and immutable elements a + bω of Q(ω), where
    ω² + ω + 1 = 0, including exact coercion, field operations, powers, and text
    representations.

Depends on:
    Python’s standard-library fraction machinery only; no physical, matrix,
    polynomial, draft-source, or verification dependency is permitted.

Must not:
    Accept implicit approximation, fabricate coefficients, assign physical meaning
    to scalars, or implement matrices, polynomials, physics, certificates, or CLI
    behavior.

Phase 0:
    The exact scalar foundation is implemented; higher mathematical and physical
    modules remain structural only.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as _Fraction


class Rational(_Fraction):
    """An immutable rational that accepts only exact integer-based input."""

    def __new__(
        cls,
        numerator: int | _Fraction = 0,
        denominator: int | None = None,
    ) -> Rational:
        if isinstance(numerator, bool) or isinstance(denominator, bool):
            raise TypeError("boolean values are not exact rational inputs")
        if denominator is None:
            if not isinstance(numerator, (int, _Fraction)):
                raise TypeError("rational values require an integer or Fraction")
            return super().__new__(cls, numerator)
        if not isinstance(numerator, int) or not isinstance(denominator, int):
            raise TypeError("a rational numerator and denominator must be integers")
        return super().__new__(cls, numerator, denominator)

    def _coerce(self, other: object) -> Rational:
        return coerce_rational(other)

    def __add__(self, other: object) -> Rational:  # type: ignore[override]
        return Rational(_Fraction(self) + _Fraction(self._coerce(other)))

    def __radd__(self, other: object) -> Rational:  # type: ignore[override]
        return self._coerce(other) + self

    def __sub__(self, other: object) -> Rational:  # type: ignore[override]
        return Rational(_Fraction(self) - _Fraction(self._coerce(other)))

    def __rsub__(self, other: object) -> Rational:  # type: ignore[override]
        return self._coerce(other) - self

    def __mul__(self, other: object) -> Rational:  # type: ignore[override]
        return Rational(_Fraction(self) * _Fraction(self._coerce(other)))

    def __rmul__(self, other: object) -> Rational:  # type: ignore[override]
        return self._coerce(other) * self

    def __truediv__(self, other: object) -> Rational:  # type: ignore[override]
        return Rational(_Fraction(self) / _Fraction(self._coerce(other)))

    def __rtruediv__(self, other: object) -> Rational:  # type: ignore[override]
        return self._coerce(other) / self

    def __pow__(self, exponent: int) -> Rational:  # type: ignore[override]
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            raise TypeError("the exponent must be an integer")
        return Rational(_Fraction(self) ** exponent)

    def __neg__(self) -> Rational:
        return Rational(-_Fraction(self))

    def __pos__(self) -> Rational:
        return self

    def __abs__(self) -> Rational:
        return Rational(abs(_Fraction(self)))

    def __eq__(self, other: object) -> bool:
        return _Fraction(self) == _Fraction(coerce_rational(other))

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __lt__(self, other: object) -> bool:
        return _Fraction(self) < _Fraction(coerce_rational(other))

    def __le__(self, other: object) -> bool:
        return _Fraction(self) <= _Fraction(coerce_rational(other))

    def __gt__(self, other: object) -> bool:
        return _Fraction(self) > _Fraction(coerce_rational(other))

    def __ge__(self, other: object) -> bool:
        return _Fraction(self) >= _Fraction(coerce_rational(other))

    __hash__ = _Fraction.__hash__

    def is_zero(self) -> bool:
        """Return whether this rational is exactly zero."""

        return self.numerator == 0


def coerce_rational(value: object) -> Rational:
    """Convert an exact integer or Fraction to a strict :class:`Rational`.

    Boolean values are rejected even though Python treats them as integers. Floating,
    complex, string, decimal, and other approximate or implicit inputs are rejected.
    """

    if isinstance(value, bool):
        raise TypeError("boolean values are not exact rational inputs")
    if isinstance(value, Rational):
        return value
    if isinstance(value, _Fraction):
        return Rational(value.numerator, value.denominator)
    if isinstance(value, int):
        return Rational(value)
    raise TypeError("exact rational arithmetic accepts only int, Rational, or Fraction")


@dataclass(frozen=True, slots=True, init=False)
class Eisenstein:
    """An immutable exact element a + bω of Q(ω)."""

    a: Rational = Rational(0)
    b: Rational = Rational(0)

    def __init__(self, a: int | _Fraction = 0, b: int | _Fraction = 0) -> None:
        """Construct an element from exact coefficients in the basis (1, ω)."""

        object.__setattr__(self, "a", coerce_rational(a))
        object.__setattr__(self, "b", coerce_rational(b))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (bool, float, complex)):
            raise TypeError("Eisenstein equality requires exact Eisenstein values")
        if not isinstance(other, Eisenstein):
            return False
        return self.a == other.a and self.b == other.b

    @staticmethod
    def coerce(value: object) -> Eisenstein:
        """Coerce an exact scalar or return an existing Eisenstein value."""

        if isinstance(value, Eisenstein):
            return value
        try:
            return Eisenstein(coerce_rational(value))
        except TypeError as error:
            raise TypeError(
                "Q(omega) accepts only int, Rational, Fraction, or Eisenstein values"
            ) from error

    def __add__(self, other: object) -> Eisenstein:
        rhs = Eisenstein.coerce(other)
        return Eisenstein(self.a + rhs.a, self.b + rhs.b)

    def __radd__(self, other: object) -> Eisenstein:
        return self + other

    def __neg__(self) -> Eisenstein:
        return Eisenstein(-self.a, -self.b)

    def __sub__(self, other: object) -> Eisenstein:
        return self + (-Eisenstein.coerce(other))

    def __rsub__(self, other: object) -> Eisenstein:
        return Eisenstein.coerce(other) - self

    def __mul__(self, other: object) -> Eisenstein:
        rhs = Eisenstein.coerce(other)
        return Eisenstein(
            self.a * rhs.a - self.b * rhs.b,
            self.a * rhs.b + self.b * rhs.a - self.b * rhs.b,
        )

    def __rmul__(self, other: object) -> Eisenstein:
        return self * other

    def inverse(self) -> Eisenstein:
        """Return the exact multiplicative inverse of a nonzero element."""

        norm = self.a * self.a - self.a * self.b + self.b * self.b
        if norm.is_zero():
            raise ZeroDivisionError("zero has no inverse in Q(omega)")
        return Eisenstein((self.a - self.b) / norm, -self.b / norm)

    def __truediv__(self, other: object) -> Eisenstein:
        return self * Eisenstein.coerce(other).inverse()

    def __rtruediv__(self, other: object) -> Eisenstein:
        return Eisenstein.coerce(other) / self

    def __pow__(self, exponent: int) -> Eisenstein:
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            raise TypeError("the exponent must be an integer")
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = Eisenstein(1)
        base = self
        power = exponent
        while power:
            if power & 1:
                result *= base
            base *= base
            power >>= 1
        return result

    def is_zero(self) -> bool:
        """Return whether both exact coefficients are zero."""

        return self.a.is_zero() and self.b.is_zero()

    def text(self) -> str:
        """Return a compact human-readable expression in the basis (1, ω)."""

        if self.is_zero():
            return "0"
        if self.b.is_zero():
            return str(self.a)
        if self.a.is_zero():
            return "omega" if self.b == 1 else "-omega" if self.b == -1 else f"{self.b}*omega"
        sign = "+" if self.b > 0 else "-"
        magnitude = abs(self.b)
        omega_term = "omega" if magnitude == 1 else f"{magnitude}*omega"
        return f"{self.a}{sign}{omega_term}"

    def __str__(self) -> str:
        return self.text()


E_ZERO = Eisenstein(0)
E_ONE = Eisenstein(1)
OMEGA = Eisenstein(0, 1)
OMEGA2 = Eisenstein(-1, -1)

__all__ = [
    "E_ONE",
    "E_ZERO",
    "Eisenstein",
    "OMEGA",
    "OMEGA2",
    "Rational",
    "coerce_rational",
]
