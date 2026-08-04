"""Exact localization and transition data for affine Cox-chart calculations.

Owns:
    Laurent polynomial localization, named affine Cox charts, finite chart
    intersections, exact transition matrices, and Čech 1-cocycle checks.

Depends on:
    `onetheory.math.numbers` for exact Rational and Eisenstein coefficients and
    `onetheory.math.polynomials` for conversion from ordinary polynomials.

Must not:
    Declare a cover of a selected Calabi–Yau, infer local freeness from sampled
    ranks, construct physical bundles, or attach observations to transition
    functions.

Phase 0:
    Generic localization and transition primitives are implemented; a
    carrier-specific cover requires an independent geometric certificate.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, cast

from onetheory.math.numbers import Eisenstein, Rational, coerce_rational
from onetheory.math.polynomials import Polynomial

Scalar = Rational | Eisenstein
type ScalarType = type[Rational] | type[Eisenstein]
type LaurentMonomial = tuple[int, ...]


def _coerce(value: object, scalar_type: ScalarType) -> Scalar:
    if scalar_type is Rational:
        return coerce_rational(value)
    if scalar_type is Eisenstein:
        return Eisenstein.coerce(value)
    raise TypeError("scalar_type must be Rational or Eisenstein")


def _zero(scalar_type: ScalarType) -> Scalar:
    return _coerce(0, scalar_type)


def _add(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) + right)


def _subtract(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) - right)


def _multiply(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) * right)


def _negate(value: Scalar) -> Scalar:
    return cast(Scalar, -cast(Any, value))


def _validate_exponents(exponents: Iterable[int], variable_count: int) -> LaurentMonomial:
    values = tuple(exponents)
    if len(values) != variable_count:
        raise ValueError("Laurent monomial dimension does not match variable_count")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise TypeError("Laurent monomial exponents must be integers")
    return values


@dataclass(frozen=True, slots=True, init=False)
class LaurentPolynomial:
    """An immutable sparse exact Laurent polynomial."""

    terms: tuple[tuple[LaurentMonomial, Scalar], ...]
    variable_count: int
    scalar_type: ScalarType

    def __init__(
        self,
        terms: Mapping[LaurentMonomial, object]
        | Iterable[tuple[Iterable[int], object]] = (),
        *,
        variable_count: int | None = None,
        scalar_type: ScalarType | None = None,
    ) -> None:
        raw = tuple(terms.items()) if isinstance(terms, Mapping) else tuple(terms)
        raw_terms = tuple((tuple(exponents), coefficient) for exponents, coefficient in raw)
        count = len(raw_terms[0][0]) if raw_terms else 0
        if variable_count is not None:
            if isinstance(variable_count, bool) or not isinstance(variable_count, int):
                raise TypeError("variable_count must be an integer")
            if variable_count < 0:
                raise ValueError("variable_count must be nonnegative")
            count = variable_count
        resolved = (
            Eisenstein
            if any(isinstance(coefficient, Eisenstein) for _, coefficient in raw_terms)
            else Rational
        ) if scalar_type is None else scalar_type
        combined: dict[LaurentMonomial, Scalar] = {}
        for exponents, coefficient in raw_terms:
            monomial = _validate_exponents(exponents, count)
            value = _coerce(coefficient, resolved)
            combined[monomial] = _add(combined.get(monomial, _zero(resolved)), value)
        normalized = tuple(
            sorted(
                (
                    (monomial, coefficient)
                    for monomial, coefficient in combined.items()
                    if not coefficient.is_zero()
                ),
                key=lambda item: item[0],
                reverse=True,
            )
        )
        object.__setattr__(self, "terms", normalized)
        object.__setattr__(self, "variable_count", count)
        object.__setattr__(self, "scalar_type", resolved)

    @classmethod
    def zero(cls, variable_count: int, *, scalar_type: ScalarType = Rational) -> LaurentPolynomial:
        """Construct the normalized zero Laurent polynomial."""

        return cls((), variable_count=variable_count, scalar_type=scalar_type)

    @classmethod
    def one(cls, variable_count: int, *, scalar_type: ScalarType = Rational) -> LaurentPolynomial:
        """Construct the multiplicative identity."""

        return cls(
            ((((0,) * variable_count), 1),),
            variable_count=variable_count,
            scalar_type=scalar_type,
        )

    @classmethod
    def monomial(
        cls,
        exponents: Iterable[int],
        coefficient: object = 1,
        *,
        scalar_type: ScalarType | None = None,
    ) -> LaurentPolynomial:
        """Construct one exact Laurent monomial."""

        values = tuple(exponents)
        return cls(((values, coefficient),), variable_count=len(values), scalar_type=scalar_type)

    @classmethod
    def from_polynomial(cls, polynomial: Polynomial) -> LaurentPolynomial:
        """Embed an ordinary exact polynomial into its localization."""

        return cls(
            polynomial.terms,
            variable_count=polynomial.variable_count,
            scalar_type=polynomial.scalar_type,
        )

    def _check(self, other: LaurentPolynomial) -> None:
        if self.variable_count != other.variable_count:
            raise ValueError("Laurent polynomials use different variable counts")
        if self.scalar_type is not other.scalar_type:
            raise TypeError("Laurent polynomials use different exact scalar fields")

    def __add__(self, other: LaurentPolynomial) -> LaurentPolynomial:
        self._check(other)
        return LaurentPolynomial(
            (*self.terms, *other.terms),
            variable_count=self.variable_count,
            scalar_type=self.scalar_type,
        )

    def __neg__(self) -> LaurentPolynomial:
        return LaurentPolynomial(
            ((monomial, _negate(coefficient)) for monomial, coefficient in self.terms),
            variable_count=self.variable_count,
            scalar_type=self.scalar_type,
        )

    def __sub__(self, other: LaurentPolynomial) -> LaurentPolynomial:
        return self + (-other)

    def scale(self, scalar: object) -> LaurentPolynomial:
        """Multiply by one exact scalar."""

        factor = _coerce(scalar, self.scalar_type)
        return LaurentPolynomial(
            ((monomial, _multiply(factor, coefficient)) for monomial, coefficient in self.terms),
            variable_count=self.variable_count,
            scalar_type=self.scalar_type,
        )

    def __mul__(self, other: LaurentPolynomial) -> LaurentPolynomial:
        self._check(other)
        terms: list[tuple[LaurentMonomial, Scalar]] = []
        for left_monomial, left_coefficient in self.terms:
            for right_monomial, right_coefficient in other.terms:
                terms.append(
                    (
                        tuple(
                            left + right
                            for left, right in zip(left_monomial, right_monomial, strict=True)
                        ),
                        _multiply(left_coefficient, right_coefficient),
                    )
                )
        return LaurentPolynomial(
            terms,
            variable_count=self.variable_count,
            scalar_type=self.scalar_type,
        )

    def is_zero(self) -> bool:
        """Return whether normalization removed all terms."""

        return not self.terms

    def __pow__(self, exponent: int) -> LaurentPolynomial:
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            raise TypeError("Laurent polynomial powers require an integer")
        if exponent < 0:
            raise ValueError("negative powers require a unit Laurent monomial")
        result = LaurentPolynomial.one(self.variable_count, scalar_type=self.scalar_type)
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result


@dataclass(frozen=True, slots=True)
class CoxChart:
    """A named principal Cox chart with an explicit inverted-variable set."""

    name: str
    variables: tuple[str, ...]
    inverted_variables: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.variables:
            raise ValueError("Cox charts require a name and variables")
        if len(set(self.variables)) != len(self.variables):
            raise ValueError("Cox chart variables must be unique")
        if any(variable not in self.variables for variable in self.inverted_variables):
            raise ValueError("a chart can invert only one of its variables")
        if len(set(self.inverted_variables)) != len(self.inverted_variables):
            raise ValueError("Cox chart inversions must be unique")

    @property
    def variable_count(self) -> int:
        """Return the ambient Cox variable count."""

        return len(self.variables)

    def localize(self, polynomial: Polynomial) -> LaurentPolynomial:
        """Embed an exact polynomial into this chart localization."""

        if polynomial.variable_count != self.variable_count:
            raise ValueError("polynomial variables do not match the Cox chart")
        return LaurentPolynomial.from_polynomial(polynomial)

    def inverse_monomial(self, variable: str) -> LaurentPolynomial:
        """Return the exact inverse of one declared inverted variable."""

        if variable not in self.inverted_variables:
            raise ValueError("the requested variable is not inverted on this chart")
        index = self.variables.index(variable)
        exponents = [0] * self.variable_count
        exponents[index] = -1
        return LaurentPolynomial.monomial(exponents)

    def intersection(self, other: CoxChart) -> CoxChart:
        """Return the named intersection chart with both inversion sets."""

        if self.variables != other.variables:
            raise ValueError("Cox charts use incompatible ambient variables")
        inverted = tuple(dict.fromkeys((*self.inverted_variables, *other.inverted_variables)))
        return CoxChart(f"{self.name}∩{other.name}", self.variables, inverted)


@dataclass(frozen=True, slots=True)
class CoxChartCover:
    """A finite named chart cover with deterministic intersections."""

    charts: tuple[CoxChart, ...]

    def __post_init__(self) -> None:
        if not self.charts or len({chart.name for chart in self.charts}) != len(self.charts):
            raise ValueError("a Cox chart cover requires uniquely named charts")
        variables = {chart.variables for chart in self.charts}
        if len(variables) != 1:
            raise ValueError("all charts in a cover need one ambient variable basis")

    def intersection(self, left: int, right: int) -> CoxChart:
        """Return one deterministic pairwise intersection chart."""

        return self.charts[left].intersection(self.charts[right])


@dataclass(frozen=True, slots=True)
class LaurentMatrix:
    """An exact rectangular matrix over one Laurent localization."""

    rows: tuple[tuple[LaurentPolynomial, ...], ...]

    def __post_init__(self) -> None:
        if not self.rows or not self.rows[0]:
            raise ValueError("Laurent matrices must be nonempty and rectangular")
        width = len(self.rows[0])
        if any(len(row) != width for row in self.rows):
            raise ValueError("Laurent matrices must be rectangular")
        first = self.rows[0][0]
        for row in self.rows:
            for entry in row:
                if entry.variable_count != first.variable_count:
                    raise ValueError("Laurent matrix variable counts do not agree")
                if entry.scalar_type is not first.scalar_type:
                    raise TypeError("Laurent matrix scalar fields do not agree")

    @property
    def shape(self) -> tuple[int, int]:
        """Return row and column counts."""

        return len(self.rows), len(self.rows[0])

    @classmethod
    def identity(
        cls,
        size: int,
        variable_count: int,
        *,
        scalar_type: ScalarType = Rational,
    ) -> LaurentMatrix:
        """Construct an exact identity matrix."""

        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise ValueError("Laurent identity size must be positive")
        one = LaurentPolynomial.one(variable_count, scalar_type=scalar_type)
        zero = LaurentPolynomial.zero(variable_count, scalar_type=scalar_type)
        return cls(tuple(tuple(one if row == column else zero for column in range(size))
                         for row in range(size)))

    def compose(self, previous: LaurentMatrix) -> LaurentMatrix:
        """Compose two compatible exact Laurent matrices."""

        if self.shape[1] != previous.shape[0]:
            raise ValueError("Laurent matrices have incompatible shapes")
        zero = LaurentPolynomial.zero(
            self.rows[0][0].variable_count,
            scalar_type=self.rows[0][0].scalar_type,
        )
        return LaurentMatrix(
            tuple(
                tuple(
                    sum(
                        (self.rows[row][inner] * previous.rows[inner][column]
                         for inner in range(self.shape[1])),
                        zero,
                    )
                    for column in range(previous.shape[1])
                )
                for row in range(self.shape[0])
            )
        )

    def is_identity(self) -> bool:
        """Return whether the matrix is exactly an identity matrix."""

        if self.shape[0] != self.shape[1]:
            return False
        identity = LaurentMatrix.identity(
            self.shape[0],
            self.rows[0][0].variable_count,
            scalar_type=self.rows[0][0].scalar_type,
        )
        return self == identity


@dataclass(frozen=True, slots=True)
class TransitionCocycle:
    """Exact ordered transition matrices with a Čech cocycle certificate."""

    cover: CoxChartCover
    rank: int
    transitions: tuple[tuple[int, int, LaurentMatrix], ...]

    def __post_init__(self) -> None:
        if isinstance(self.rank, bool) or not isinstance(self.rank, int) or self.rank <= 0:
            raise ValueError("transition cocycles require a positive rank")
        chart_count = len(self.cover.charts)
        for left, right, matrix in self.transitions:
            if not 0 <= left < chart_count or not 0 <= right < chart_count or left == right:
                raise ValueError("transition indices must name distinct cover charts")
            if matrix.shape != (self.rank, self.rank):
                raise ValueError("transition matrices must match the declared rank")
        pairs = {(left, right) for left, right, _ in self.transitions}
        expected = {(left, right) for left in range(chart_count)
                    for right in range(chart_count) if left != right}
        if pairs != expected:
            raise ValueError("transition data must include every ordered chart pair")

    def transition(self, left: int, right: int) -> LaurentMatrix:
        """Return one ordered transition matrix."""

        for source, target, matrix in self.transitions:
            if (source, target) == (left, right):
                return matrix
        raise KeyError((left, right))

    def verifies_cocycle(self) -> bool:
        """Check ``g_ik = g_ij g_jk`` for every ordered chart triple."""

        count = len(self.cover.charts)
        return all(
            self.transition(left, right) == self.transition(left, middle).compose(
                self.transition(middle, right)
            )
            for left in range(count)
            for middle in range(count)
            for right in range(count)
            if len({left, middle, right}) == 3
        )


__all__ = [
    "CoxChart",
    "CoxChartCover",
    "LaurentMatrix",
    "LaurentMonomial",
    "LaurentPolynomial",
    "TransitionCocycle",
]
