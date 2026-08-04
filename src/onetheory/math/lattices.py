"""Integral lattice, reduction, and affine-action mathematics.

Owns:
    Immutable integral lattices from Gram matrices, exact pairings and norms,
    bounded root enumeration, reduction modulo primes, affine integer actions,
    quadratic shells, and deterministic orbit decomposition.

Depends on:
    `onetheory.math.finite` for prime-field reduction and generic finite orbit
    decomposition. This module assigns no physical meaning to lattice data.

Must not:
    Select geometry from observations, encode particle or carrier interpretations,
    hide unbounded searches behind finite answers, or implement Wilson-line models.

Phase 0:
    The reusable integral-lattice foundation is implemented; concrete physical
    models remain outside this module.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import product

from onetheory.math.finite import FiniteVector, PrimeField, orbit_decomposition

IntVector = tuple[int, ...]
IntMatrix = tuple[tuple[int, ...], ...]


def _validate_int_matrix(matrix: Iterable[Iterable[int]]) -> IntMatrix:
    rows = tuple(tuple(row) for row in matrix)
    if not rows or not rows[0]:
        raise ValueError("an integral matrix must be nonempty and rectangular")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("an integral matrix must be rectangular")
    if any(
        isinstance(value, bool) or not isinstance(value, int)
        for row in rows
        for value in row
    ):
        raise TypeError("integral matrices require integer entries")
    return rows


def _validate_vector(vector: Iterable[int], dimension: int) -> IntVector:
    values = tuple(vector)
    if len(values) != dimension:
        raise ValueError("lattice vector dimension does not agree")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise TypeError("lattice vectors require integer entries")
    return values


def _field(prime: int | PrimeField) -> PrimeField:
    return prime if isinstance(prime, PrimeField) else PrimeField(prime)


@dataclass(frozen=True, slots=True, init=False)
class IntegralLattice:
    """An immutable lattice with an integral symmetric Gram matrix."""

    _gram: IntMatrix

    def __init__(self, gram: Iterable[Iterable[int]]) -> None:
        matrix = _validate_int_matrix(gram)
        if len(matrix) != len(matrix[0]):
            raise ValueError("an integral lattice requires a square Gram matrix")
        if any(matrix[row][column] != matrix[column][row]
               for row in range(len(matrix))
               for column in range(len(matrix))):
            raise ValueError("a lattice Gram matrix must be symmetric")
        object.__setattr__(self, "_gram", matrix)

    @property
    def gram(self) -> IntMatrix:
        """Return the immutable symmetric Gram matrix."""

        return self._gram

    @property
    def rank(self) -> int:
        """Return the lattice rank."""

        return len(self._gram)

    def pair(self, left: Iterable[int], right: Iterable[int]) -> int:
        """Return the exact integral bilinear pairing."""

        left_values = _validate_vector(left, self.rank)
        right_values = _validate_vector(right, self.rank)
        return sum(
            left_values[row] * self._gram[row][column] * right_values[column]
            for row in range(self.rank)
            for column in range(self.rank)
        )

    def norm(self, vector: Iterable[int]) -> int:
        """Return the exact self-pairing of a lattice vector."""

        values = _validate_vector(vector, self.rank)
        return self.pair(values, values)

    def bounded_vectors(self, bound: int) -> tuple[IntVector, ...]:
        """Enumerate the integer box `[-bound,bound]^rank` deterministically."""

        if isinstance(bound, bool) or not isinstance(bound, int) or bound < 0:
            raise ValueError("lattice bounds must be nonnegative integers")
        return tuple(product(range(-bound, bound + 1), repeat=self.rank))

    def roots(self, bound: int = 3, norm: int = 2) -> tuple[IntVector, ...]:
        """Enumerate vectors of the requested norm inside an explicit bound."""

        if isinstance(norm, bool) or not isinstance(norm, int):
            raise TypeError("root norms require an integer target")
        return tuple(
            vector for vector in self.bounded_vectors(bound) if self.norm(vector) == norm
        )

    def reduce_mod_prime(
        self,
        vector: Iterable[int],
        prime: int | PrimeField,
    ) -> IntVector:
        """Reduce a lattice vector to canonical coordinates modulo a prime."""

        field = _field(prime)
        values = _validate_vector(vector, self.rank)
        return tuple(field.element(value) for value in values)

    def reduced_vector(
        self,
        vector: Iterable[int],
        prime: int | PrimeField,
    ) -> FiniteVector:
        """Return the finite-field vector associated with a lattice vector."""

        field = _field(prime)
        return FiniteVector(self.reduce_mod_prime(vector, field), field)

    def pairing_mod_prime(
        self,
        left: Iterable[int],
        right: Iterable[int],
        prime: int | PrimeField,
    ) -> int:
        """Return the lattice pairing reduced modulo a prime."""

        return self.pair(left, right) % _field(prime).modulus

    def norm_mod_prime(self, vector: Iterable[int], prime: int | PrimeField) -> int:
        """Return the exact norm reduced modulo a prime."""

        return self.norm(vector) % _field(prime).modulus

    def quadratic_mod_prime(self, vector: Iterable[int], prime: int | PrimeField) -> int:
        """Return the conventionally doubled quadratic value modulo a prime."""

        field = _field(prime)
        return field.element(2 * self.norm(vector))


@dataclass(frozen=True, slots=True, init=False)
class AffineQuadraticForm:
    """An exact integer quadratic polynomial with affine and constant terms."""

    _quadratic: IntMatrix
    _linear: IntVector
    _constant: int

    def __init__(
        self,
        quadratic: Iterable[Iterable[int]],
        linear: Iterable[int] | None = None,
        constant: int = 0,
    ) -> None:
        matrix = _validate_int_matrix(quadratic)
        if len(matrix) != len(matrix[0]):
            raise ValueError("an affine quadratic form requires a square matrix")
        coefficients = _validate_vector(
            (0,) * len(matrix) if linear is None else linear,
            len(matrix),
        )
        if isinstance(constant, bool) or not isinstance(constant, int):
            raise TypeError("affine quadratic constants require integer input")
        object.__setattr__(self, "_quadratic", matrix)
        object.__setattr__(self, "_linear", coefficients)
        object.__setattr__(self, "_constant", constant)

    @property
    def dimension(self) -> int:
        return len(self._quadratic)

    @property
    def quadratic(self) -> IntMatrix:
        """Return the quadratic coefficient matrix."""

        return self._quadratic

    @property
    def linear(self) -> IntVector:
        """Return the linear coefficient vector."""

        return self._linear

    @property
    def constant(self) -> int:
        """Return the constant term."""

        return self._constant

    def value(self, vector: Iterable[int]) -> int:
        """Evaluate the exact integer polynomial."""

        values = _validate_vector(vector, self.dimension)
        quadratic_value = sum(
            values[row] * self._quadratic[row][column] * values[column]
            for row in range(self.dimension)
            for column in range(self.dimension)
        )
        return quadratic_value + sum(
            coefficient * value
            for coefficient, value in zip(self._linear, values, strict=True)
        ) + self._constant

    def shell(self, value: int, bound: int) -> tuple[IntVector, ...]:
        """Enumerate the explicitly bounded level shell of the form."""

        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("shell values require integer input")
        if isinstance(bound, bool) or not isinstance(bound, int) or bound < 0:
            raise ValueError("shell bounds must be nonnegative integers")
        return tuple(
            vector
            for vector in product(range(-bound, bound + 1), repeat=self.dimension)
            if self.value(vector) == value
        )


@dataclass(frozen=True, slots=True, init=False)
class AffineAction:
    """An immutable affine action on an integer coordinate lattice."""

    _linear: IntMatrix
    _translation: IntVector

    def __init__(
        self,
        linear: Iterable[Iterable[int]],
        translation: Iterable[int] | None = None,
    ) -> None:
        matrix = _validate_int_matrix(linear)
        if len(matrix) != len(matrix[0]):
            raise ValueError("an affine action requires a square linear part")
        shift = _validate_vector(
            (0,) * len(matrix) if translation is None else translation,
            len(matrix),
        )
        object.__setattr__(self, "_linear", matrix)
        object.__setattr__(self, "_translation", shift)

    @property
    def dimension(self) -> int:
        return len(self._linear)

    @property
    def linear(self) -> IntMatrix:
        """Return the linear part."""

        return self._linear

    @property
    def translation(self) -> IntVector:
        """Return the translation part."""

        return self._translation

    def apply(self, point: Iterable[int]) -> IntVector:
        """Apply the affine map exactly."""

        values = _validate_vector(point, self.dimension)
        return tuple(
            sum(self._linear[row][column] * values[column] for column in range(self.dimension))
            + self._translation[row]
            for row in range(self.dimension)
        )

    def __call__(self, point: Iterable[int]) -> IntVector:
        return self.apply(point)

    def orbit(self, point: Iterable[int], period: int | None = None) -> tuple[IntVector, ...]:
        """Return a finite orbit, requiring an explicit or detected period."""

        start = _validate_vector(point, self.dimension)
        if period is not None:
            if isinstance(period, bool) or not isinstance(period, int) or period <= 0:
                raise ValueError("orbit periods must be positive integers")
            orbit = [start]
            current = start
            for _ in range(period - 1):
                current = self.apply(current)
                orbit.append(current)
            if self.apply(current) != start:
                raise ValueError("the supplied period does not close the orbit")
            return tuple(orbit)
        orbit = [start]
        current = start
        for _ in range(10000):
            current = self.apply(current)
            if current == start:
                return tuple(orbit)
            if current in orbit:
                raise ValueError("the affine orbit repeats without returning to its start")
            orbit.append(current)
        raise ValueError("affine orbit period exceeds the deterministic search limit")

    def orbits(self, points: Iterable[IntVector]) -> tuple[tuple[IntVector, ...], ...]:
        """Decompose an action-closed finite point set into deterministic orbits."""

        return orbit_decomposition(points, (self.apply,), key=lambda point: point)

    def shell_orbits(
        self,
        form: AffineQuadraticForm,
        value: int,
        bound: int,
    ) -> tuple[tuple[IntVector, ...], ...]:
        """Decompose a bounded affine-quadratic shell into action orbits."""

        if form.dimension != self.dimension:
            raise ValueError("action and shell dimensions do not agree")
        return self.orbits(form.shell(value, bound))


def affine_shell(form: AffineQuadraticForm, value: int, bound: int) -> tuple[IntVector, ...]:
    """Return an explicitly bounded affine-quadratic shell."""

    return form.shell(value, bound)


def affine_orbits(
    action: AffineAction,
    points: Iterable[IntVector],
) -> tuple[tuple[IntVector, ...], ...]:
    """Return deterministic orbits of an affine action."""

    return action.orbits(points)


__all__ = [
    "AffineAction",
    "AffineQuadraticForm",
    "IntegralLattice",
    "affine_orbits",
    "affine_shell",
]
