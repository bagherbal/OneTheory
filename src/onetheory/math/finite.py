"""Exact finite-field linear algebra, forms, and finite group actions.

Owns:
    Prime fields, immutable vectors and matrices over those fields, quadratic and
    polar forms, exhaustive isotropic enumeration, invertible linear maps, and
    deterministic orbit decomposition for finite actions.

Depends on:
    Python’s exact integer arithmetic and standard-library iteration utilities only.
    No physical interpretation, carrier model, or observational input is required.

Must not:
    Assign physical meaning to finite coincidences, hide incomplete enumeration,
    implement particle or carrier structures, or import research or draft code.

Phase 0:
    The reusable finite-structure foundation is implemented; physical domains
    remain outside this module.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable, Iterator
from dataclasses import dataclass
from itertools import product
from math import isqrt
from typing import Any, cast


def _is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value == 2:
        return True
    if value % 2 == 0:
        return False
    for divisor in range(3, isqrt(value) + 1, 2):
        if value % divisor == 0:
            return False
    return True


@dataclass(frozen=True, slots=True)
class PrimeField:
    """The prime field with the declared characteristic."""

    modulus: int

    def __post_init__(self) -> None:
        if isinstance(self.modulus, bool) or not isinstance(self.modulus, int):
            raise TypeError("a prime-field modulus must be an integer")
        if not _is_prime(self.modulus):
            raise ValueError("the field modulus must be prime")

    @property
    def characteristic(self) -> int:
        """Return the prime characteristic."""

        return self.modulus

    @property
    def elements(self) -> tuple[int, ...]:
        """Return all canonical field elements in deterministic order."""

        return tuple(range(self.modulus))

    def element(self, value: object) -> int:
        """Reduce one exact integer to its canonical field representative."""

        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("finite-field elements require integer input")
        return value % self.modulus

    def __call__(self, value: object) -> int:
        return self.element(value)

    def add(self, left: int, right: int) -> int:
        return (self.element(left) + self.element(right)) % self.modulus

    def subtract(self, left: int, right: int) -> int:
        return (self.element(left) - self.element(right)) % self.modulus

    def negate(self, value: int) -> int:
        return (-self.element(value)) % self.modulus

    def multiply(self, left: int, right: int) -> int:
        return self.element(left) * self.element(right) % self.modulus

    def inverse(self, value: int) -> int:
        normalized = self.element(value)
        if normalized == 0:
            raise ZeroDivisionError("zero has no finite-field inverse")
        return pow(normalized, self.modulus - 2, self.modulus)

    def divide(self, left: int, right: int) -> int:
        return self.multiply(left, self.inverse(right))

    def power(self, value: int, exponent: int) -> int:
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            raise TypeError("finite-field powers require an integer exponent")
        normalized = self.element(value)
        if exponent < 0:
            normalized = self.inverse(normalized)
            exponent = -exponent
        return pow(normalized, exponent, self.modulus)


@dataclass(frozen=True, slots=True, init=False)
class FiniteVector:
    """An immutable vector over one prime field."""

    _values: tuple[int, ...]
    _field: PrimeField

    def __init__(self, values: Iterable[object], field: PrimeField) -> None:
        object.__setattr__(self, "_values", tuple(field.element(value) for value in values))
        object.__setattr__(self, "_field", field)

    @classmethod
    def zero(cls, dimension: int, field: PrimeField) -> FiniteVector:
        if isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 0:
            raise ValueError("vector dimension must be a nonnegative integer")
        return cls((field.element(0) for _ in range(dimension)), field)

    @property
    def values(self) -> tuple[int, ...]:
        """Return canonical coordinates."""

        return self._values

    @property
    def field(self) -> PrimeField:
        """Return the coefficient field."""

        return self._field

    @property
    def dimension(self) -> int:
        """Return the vector dimension."""

        return len(self._values)

    def __len__(self) -> int:
        return self.dimension

    def __iter__(self) -> Iterator[int]:
        return iter(self._values)

    def __getitem__(self, index: int) -> int:
        return self._values[index]

    def _check_compatible(self, other: FiniteVector) -> None:
        if self.field != other.field:
            raise TypeError("finite vectors must use the same prime field")
        if self.dimension != other.dimension:
            raise ValueError("finite-vector dimensions do not agree")

    def __add__(self, other: FiniteVector) -> FiniteVector:
        self._check_compatible(other)
        return FiniteVector(
            (
                self.field.add(left, right)
                for left, right in zip(self, other, strict=True)
            ),
            self.field,
        )

    def __sub__(self, other: FiniteVector) -> FiniteVector:
        self._check_compatible(other)
        return FiniteVector(
            (
                self.field.subtract(left, right)
                for left, right in zip(self, other, strict=True)
            ),
            self.field,
        )

    def __neg__(self) -> FiniteVector:
        return FiniteVector((self.field.negate(value) for value in self), self.field)

    def scale(self, scalar: int) -> FiniteVector:
        """Multiply every coordinate by one field element."""

        return FiniteVector(
            (self.field.multiply(scalar, value) for value in self),
            self.field,
        )

    def __mul__(self, scalar: int) -> FiniteVector:
        return self.scale(scalar)

    def __rmul__(self, scalar: int) -> FiniteVector:
        return self.scale(scalar)

    def dot(self, other: FiniteVector) -> int:
        """Return the standard exact dot product."""

        self._check_compatible(other)
        result = self.field.element(0)
        for left, right in zip(self, other, strict=True):
            result = self.field.add(result, self.field.multiply(left, right))
        return result

    def is_zero(self) -> bool:
        """Return whether every coordinate is zero."""

        return all(value == 0 for value in self)


@dataclass(frozen=True, slots=True, init=False)
class FiniteMatrix:
    """An immutable nonempty rectangular matrix over a prime field."""

    _rows: tuple[tuple[int, ...], ...]
    _field: PrimeField

    def __init__(self, rows: Iterable[Iterable[object]], field: PrimeField) -> None:
        materialized = tuple(tuple(field.element(value) for value in row) for row in rows)
        if not materialized or not materialized[0]:
            raise ValueError("finite matrix must be nonempty and rectangular")
        width = len(materialized[0])
        if any(len(row) != width for row in materialized):
            raise ValueError("finite matrix must be rectangular")
        object.__setattr__(self, "_rows", materialized)
        object.__setattr__(self, "_field", field)

    @classmethod
    def identity(cls, size: int, field: PrimeField) -> FiniteMatrix:
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise ValueError("identity size must be a positive integer")
        return cls(
            (
                (1 if row == column else 0 for column in range(size))
                for row in range(size)
            ),
            field,
        )

    @property
    def rows(self) -> tuple[tuple[int, ...], ...]:
        """Return canonical immutable rows."""

        return self._rows

    @property
    def field(self) -> PrimeField:
        """Return the coefficient field."""

        return self._field

    @property
    def shape(self) -> tuple[int, int]:
        """Return `(row_count, column_count)`."""

        return len(self._rows), len(self._rows[0])

    @property
    def row_count(self) -> int:
        return self.shape[0]

    @property
    def column_count(self) -> int:
        return self.shape[1]

    def __len__(self) -> int:
        return self.row_count

    def __iter__(self) -> Iterator[tuple[int, ...]]:
        return iter(self._rows)

    def __getitem__(self, index: int) -> tuple[int, ...]:
        return self._rows[index]

    def _check_compatible(self, other: FiniteMatrix) -> None:
        if self.field != other.field:
            raise TypeError("finite matrices must use the same prime field")
        if self.shape != other.shape:
            raise ValueError("finite-matrix dimensions do not agree")

    def __add__(self, other: FiniteMatrix) -> FiniteMatrix:
        self._check_compatible(other)
        return FiniteMatrix(
            (
                (
                    self.field.add(left, right)
                    for left, right in zip(left_row, right_row, strict=True)
                )
                for left_row, right_row in zip(self, other, strict=True)
            ),
            self.field,
        )

    def __sub__(self, other: FiniteMatrix) -> FiniteMatrix:
        self._check_compatible(other)
        return FiniteMatrix(
            (
                (
                    self.field.subtract(left, right)
                    for left, right in zip(left_row, right_row, strict=True)
                )
                for left_row, right_row in zip(self, other, strict=True)
            ),
            self.field,
        )

    def __neg__(self) -> FiniteMatrix:
        return FiniteMatrix(
            (
                (self.field.negate(value) for value in row)
                for row in self
            ),
            self.field,
        )

    def scale(self, scalar: int) -> FiniteMatrix:
        """Multiply every entry by one field element."""

        return FiniteMatrix(
            (
                (self.field.multiply(scalar, value) for value in row)
                for row in self
            ),
            self.field,
        )

    def __mul__(self, other: object) -> FiniteMatrix:
        if isinstance(other, FiniteMatrix):
            return self.matmul(other)
        return self.scale(cast(int, other))

    def __rmul__(self, other: object) -> FiniteMatrix:
        if isinstance(other, FiniteMatrix):
            return other.matmul(self)
        return self.scale(cast(int, other))

    def __matmul__(self, other: FiniteMatrix | FiniteVector) -> FiniteMatrix | FiniteVector:
        if isinstance(other, FiniteMatrix):
            return self.matmul(other)
        if isinstance(other, FiniteVector):
            return self.matvec(other)
        raise TypeError("finite matrix products require a matrix or vector")

    def matmul(self, other: FiniteMatrix) -> FiniteMatrix:
        """Return the exact product of compatible finite matrices."""

        if self.field != other.field:
            raise TypeError("finite matrices must use the same prime field")
        if self.column_count != other.row_count:
            raise ValueError("finite-matrix dimensions do not agree")
        return FiniteMatrix(
            (
                (
                    sum(
                        (
                            self.field.multiply(self[row][inner], other[inner][column])
                            for inner in range(self.column_count)
                        ),
                        0,
                    )
                    % self.field.modulus
                    for column in range(other.column_count)
                )
                for row in range(self.row_count)
            ),
            self.field,
        )

    def matvec(self, vector: FiniteVector) -> FiniteVector:
        """Return the exact matrix–vector product."""

        if self.field != vector.field:
            raise TypeError("finite matrix and vector fields do not agree")
        if self.column_count != vector.dimension:
            raise ValueError("finite matrix and vector dimensions do not agree")
        return FiniteVector(
            (
                sum(
                    (
                        self.field.multiply(entry, coordinate)
                        for entry, coordinate in zip(row, vector, strict=True)
                    ),
                    0,
                )
                % self.field.modulus
                for row in self
            ),
            self.field,
        )

    def transpose(self) -> FiniteMatrix:
        """Return the exact transpose."""

        return FiniteMatrix(zip(*self._rows, strict=True), self.field)

    def rref(self) -> tuple[FiniteMatrix, tuple[int, ...]]:
        """Return deterministic reduced row-echelon form and pivot columns."""

        work = [list(row) for row in self._rows]
        pivots: list[int] = []
        pivot_row = 0
        for column in range(self.column_count):
            pivot = next(
                (
                    row
                    for row in range(pivot_row, self.row_count)
                    if work[row][column] != 0
                ),
                None,
            )
            if pivot is None:
                continue
            work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
            inverse = self.field.inverse(work[pivot_row][column])
            work[pivot_row] = [
                self.field.multiply(inverse, entry) for entry in work[pivot_row]
            ]
            for row in range(self.row_count):
                if row == pivot_row or work[row][column] == 0:
                    continue
                factor = work[row][column]
                work[row] = [
                    self.field.subtract(entry, self.field.multiply(factor, pivot_entry))
                    for entry, pivot_entry in zip(work[row], work[pivot_row], strict=True)
                ]
            pivots.append(column)
            pivot_row += 1
            if pivot_row == self.row_count:
                break
        return FiniteMatrix(work, self.field), tuple(pivots)

    def rank(self) -> int:
        """Return the rank over the finite field."""

        return len(self.rref()[1])

    def determinant(self) -> int:
        """Return the exact determinant of a square finite matrix."""

        if self.row_count != self.column_count:
            raise ValueError("finite determinant requires a square matrix")
        work = [list(row) for row in self._rows]
        result = 1
        sign = 1
        for column in range(self.column_count):
            pivot = next(
                (row for row in range(column, self.row_count) if work[row][column] != 0),
                None,
            )
            if pivot is None:
                return 0
            if pivot != column:
                work[column], work[pivot] = work[pivot], work[column]
                sign = -sign
            pivot_value = work[column][column]
            result = self.field.multiply(result, pivot_value)
            inverse = self.field.inverse(pivot_value)
            for row in range(column + 1, self.row_count):
                if work[row][column] == 0:
                    continue
                factor = self.field.multiply(work[row][column], inverse)
                work[row] = [
                    self.field.subtract(entry, self.field.multiply(factor, pivot_entry))
                    for entry, pivot_entry in zip(work[row], work[column], strict=True)
                ]
        return self.field.negate(result) if sign < 0 else result

    def inverse(self) -> FiniteMatrix:
        """Return the exact inverse of a nonsingular square matrix."""

        if self.row_count != self.column_count:
            raise ValueError("finite inverse requires a square matrix")
        identity = FiniteMatrix.identity(self.row_count, self.field)
        augmented = FiniteMatrix(
            (left + right for left, right in zip(self, identity, strict=True)),
            self.field,
        )
        reduced, pivots = augmented.rref()
        if pivots[: self.row_count] != tuple(range(self.row_count)):
            raise ValueError("finite matrix is singular")
        return FiniteMatrix(
            (row[self.row_count :] for row in reduced),
            self.field,
        )

    def is_invertible(self) -> bool:
        """Return whether this matrix has a two-sided inverse."""

        return (
            self.row_count == self.column_count
            and self.determinant() != 0
        )

    def __pow__(self, exponent: int) -> FiniteMatrix:
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            raise TypeError("finite matrix powers require an integer exponent")
        if self.row_count != self.column_count:
            raise ValueError("finite matrix powers require a square matrix")
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = FiniteMatrix.identity(self.row_count, self.field)
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result.matmul(base)
            base = base.matmul(base)
            power >>= 1
        return result


@dataclass(frozen=True, slots=True)
class QuadraticForm:
    """A quadratic form `v ↦ vᵀAv` over a prime field."""

    matrix: FiniteMatrix

    def __post_init__(self) -> None:
        if self.matrix.row_count != self.matrix.column_count:
            raise ValueError("a quadratic form requires a square matrix")
        canonical: list[tuple[int, ...]] = []
        for row in range(self.matrix.row_count):
            canonical.append(
                tuple(
                    self.matrix[row][column]
                    if row == column
                    else self.field.add(
                        self.matrix[row][column], self.matrix[column][row]
                    )
                    if row < column
                    else 0
                    for column in range(self.matrix.column_count)
                )
            )
        object.__setattr__(self, "matrix", FiniteMatrix(canonical, self.field))

    @property
    def field(self) -> PrimeField:
        """Return the coefficient field."""

        return self.matrix.field

    @classmethod
    def binary(
        cls,
        field: PrimeField,
        a: int,
        b: int,
        c: int,
    ) -> QuadraticForm:
        """Construct `a x² + b xy + c y²` without division by two."""

        return cls(FiniteMatrix(((a, b), (0, c)), field))

    @property
    def dimension(self) -> int:
        return self.matrix.row_count

    def value(self, vector: FiniteVector) -> int:
        """Evaluate the form exactly."""

        if vector.field != self.field or vector.dimension != self.dimension:
            raise ValueError("quadratic-form vector is incompatible")
        transformed = self.matrix.matvec(vector)
        return vector.dot(transformed)

    def polar(self, left: FiniteVector, right: FiniteVector) -> int:
        """Return `q(left+right)-q(left)-q(right)`."""

        return self.field.subtract(
            self.field.subtract(self.value(left + right), self.value(left)),
            self.value(right),
        )

    def polar_matrix(self) -> FiniteMatrix:
        """Return the matrix of the associated polar bilinear form."""

        basis = tuple(
            FiniteVector(
                (1 if row == column else 0 for row in range(self.dimension)),
                self.field,
            )
            for column in range(self.dimension)
        )
        return FiniteMatrix(
            (
                (self.polar(left, right) for right in basis)
                for left in basis
            ),
            self.field,
        )

    def is_nondegenerate(self) -> bool:
        """Return whether the polar form has full rank."""

        return self.polar_matrix().is_invertible()

    def isotropic_vectors(self, include_zero: bool = True) -> tuple[FiniteVector, ...]:
        """Enumerate all vectors with exactly zero quadratic value."""

        vectors = enumerate_vectors(self.field, self.dimension)
        if include_zero:
            return tuple(vector for vector in vectors if self.value(vector) == 0)
        return tuple(
            vector
            for vector in vectors
            if not vector.is_zero() and self.value(vector) == 0
        )

    def transformed_by(self, linear_map: FiniteMatrix) -> QuadraticForm:
        """Pull the form back along an invertible linear map."""

        if linear_map.field != self.field or linear_map.shape != self.matrix.shape:
            raise ValueError("linear map is incompatible with the form")
        if not linear_map.is_invertible():
            raise ValueError("quadratic-form changes require an invertible map")
        transformed = linear_map.transpose().matmul(self.matrix).matmul(linear_map)
        return QuadraticForm(transformed)


def enumerate_vectors(field: PrimeField, dimension: int) -> tuple[FiniteVector, ...]:
    """Exhaustively enumerate vectors in deterministic lexicographic order."""

    if isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 0:
        raise ValueError("vector dimension must be a nonnegative integer")
    return tuple(
        FiniteVector(values, field)
        for values in product(field.elements, repeat=dimension)
    )


def enumerate_invertible_matrices(field: PrimeField, dimension: int) -> tuple[FiniteMatrix, ...]:
    """Exhaustively enumerate `GL(d, field)` in deterministic order."""

    if isinstance(dimension, bool) or not isinstance(dimension, int) or dimension <= 0:
        raise ValueError("matrix dimension must be a positive integer")
    return tuple(
        matrix
        for values in product(field.elements, repeat=dimension * dimension)
        for matrix in (
            FiniteMatrix(
                (
                    values[row * dimension : (row + 1) * dimension]
                    for row in range(dimension)
                ),
                field,
            ),
        )
        if matrix.is_invertible()
    )


def orbit_decomposition[T: Hashable](
    elements: Iterable[T],
    actions: Iterable[Callable[[T], T]],
    *,
    key: Callable[[T], object] | None = None,
) -> tuple[tuple[T, ...], ...]:
    """Decompose a finite action into deterministic closed orbits."""

    universe = set(elements)
    action_list = tuple(actions)
    sort_key: Callable[[T], Any] = (
        cast(Callable[[T], Any], key)
        if key is not None
        else lambda item: repr(item)
    )
    remaining = set(universe)
    orbits: list[tuple[T, ...]] = []
    while remaining:
        seed = min(remaining, key=sort_key)
        orbit = {seed}
        frontier = [seed]
        while frontier:
            current = frontier.pop(0)
            for action in action_list:
                image = action(current)
                if image not in universe:
                    raise ValueError("the supplied set is not closed under the action")
                if image not in orbit:
                    orbit.add(image)
                    frontier.append(image)
        remaining.difference_update(orbit)
        orbits.append(tuple(sorted(orbit, key=sort_key)))
    return tuple(orbits)


def quadratic_form_orbits(
    forms: Iterable[QuadraticForm],
    linear_maps: Iterable[FiniteMatrix],
) -> tuple[tuple[QuadraticForm, ...], ...]:
    """Decompose forms under a declared finite group of linear maps."""

    maps = tuple(linear_maps)
    actions: list[Callable[[QuadraticForm], QuadraticForm]] = []
    for linear_map in maps:
        def transform(
            form: QuadraticForm,
            map_value: FiniteMatrix = linear_map,
        ) -> QuadraticForm:
            return form.transformed_by(map_value)

        actions.append(transform)
    return orbit_decomposition(
        forms,
        actions,
    )


def enumerate_binary_quadratic_forms(field: PrimeField) -> tuple[QuadraticForm, ...]:
    """Enumerate all coefficient triples `a x²+bxy+c y²` over a field."""

    return tuple(
        QuadraticForm.binary(field, a, b, c)
        for a, b, c in product(field.elements, repeat=3)
    )


def nondegenerate_binary_quadratic_forms(field: PrimeField) -> tuple[QuadraticForm, ...]:
    """Enumerate the binary forms with nondegenerate polar form."""

    return tuple(
        form for form in enumerate_binary_quadratic_forms(field) if form.is_nondegenerate()
    )


__all__ = [
    "FiniteMatrix",
    "FiniteVector",
    "PrimeField",
    "QuadraticForm",
    "enumerate_binary_quadratic_forms",
    "enumerate_invertible_matrices",
    "enumerate_vectors",
    "nondegenerate_binary_quadratic_forms",
    "orbit_decomposition",
    "quadratic_form_orbits",
]
