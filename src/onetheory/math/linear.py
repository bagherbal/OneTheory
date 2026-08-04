"""Immutable exact linear algebra over OneTheory scalar fields.

Owns:
    Rectangular matrices and vectors, matrix products, deterministic RREF, rank,
    nullspaces, inverses, arbitrary square determinants, transposition, and integer
    powers over Rational or Eisenstein scalars.

Depends on:
    `onetheory.math.numbers` for exact scalar coercion and arithmetic only. This
    module contains one scalar-generic algorithmic path for both supported fields.

Must not:
    Convert to floats, implement tensors, polynomials, geometry, physics,
    certificates, numerical linear algebra, or project-specific sample matrices.

Phase 0:
    The exact matrix foundation is implemented; higher mathematical and physical
    modules remain structural only.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any, cast

from onetheory.math.numbers import Eisenstein, Rational, coerce_rational

Scalar = Rational | Eisenstein
type ScalarType = type[Rational] | type[Eisenstein]


def _scalar_type_for(value: object) -> ScalarType:
    if isinstance(value, Eisenstein):
        return Eisenstein
    return Rational


def _resolve_scalar_type(first_value: object, scalar_type: ScalarType | None) -> ScalarType:
    return _scalar_type_for(first_value) if scalar_type is None else scalar_type


def _coerce(value: object, scalar_type: ScalarType) -> Scalar:
    if scalar_type is Rational:
        return coerce_rational(value)
    if scalar_type is Eisenstein:
        return Eisenstein.coerce(value)
    raise TypeError("scalar_type must be Rational or Eisenstein")


def _zero(scalar_type: ScalarType) -> Scalar:
    return _coerce(0, scalar_type)


def _one(scalar_type: ScalarType) -> Scalar:
    return _coerce(1, scalar_type)


def _add(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) + right)


def _subtract(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) - right)


def _multiply(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) * right)


def _negate(value: Scalar) -> Scalar:
    return cast(Scalar, -cast(Any, value))


def _divide(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) / right)


def _inverse(value: Scalar, scalar_type: ScalarType) -> Scalar:
    return _divide(_one(scalar_type), value)


def _is_zero(value: Scalar) -> bool:
    return value.is_zero()


def _require_same_scalar_type(left: ScalarType, right: ScalarType) -> None:
    if left is not right:
        raise TypeError("linear operands must use the same exact scalar type")


def _raw_rows(rows: Iterable[Iterable[object]]) -> tuple[tuple[object, ...], ...]:
    materialized = tuple(tuple(row) for row in rows)
    if not materialized:
        raise ValueError("matrix must contain at least one row")
    width = len(materialized[0])
    if width == 0 or any(len(row) != width for row in materialized):
        raise ValueError("matrix must be nonempty and rectangular")
    return materialized


@dataclass(frozen=True, slots=True, init=False)
class Vector:
    """An immutable finite vector over one exact scalar field."""

    _values: tuple[Scalar, ...]
    _scalar_type: ScalarType

    def __init__(
        self,
        values: Iterable[object],
        *,
        scalar_type: ScalarType | None = None,
    ) -> None:
        materialized = tuple(values)
        resolved = _resolve_scalar_type(materialized[0], scalar_type) if materialized else (
            Rational if scalar_type is None else scalar_type
        )
        coerced = tuple(_coerce(value, resolved) for value in materialized)
        object.__setattr__(self, "_values", coerced)
        object.__setattr__(self, "_scalar_type", resolved)

    @property
    def values(self) -> tuple[Scalar, ...]:
        """Return the immutable coordinate tuple."""

        return self._values

    @property
    def dimension(self) -> int:
        """Return the number of coordinates."""

        return len(self._values)

    @property
    def scalar_type(self) -> ScalarType:
        """Return the exact scalar class used by this vector."""

        return self._scalar_type

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> Iterator[Scalar]:
        return iter(self._values)

    def __getitem__(self, index: int) -> Scalar:
        return self._values[index]

    def _check_compatible(self, other: Vector) -> None:
        _require_same_scalar_type(self._scalar_type, other._scalar_type)
        if self.dimension != other.dimension:
            raise ValueError("vector dimensions do not agree")

    def __add__(self, other: Vector) -> Vector:
        self._check_compatible(other)
        return Vector(
            (_add(left, right) for left, right in zip(self, other, strict=True)),
            scalar_type=self._scalar_type,
        )

    def __sub__(self, other: Vector) -> Vector:
        self._check_compatible(other)
        return Vector(
            (_subtract(left, right) for left, right in zip(self, other, strict=True)),
            scalar_type=self._scalar_type,
        )

    def __neg__(self) -> Vector:
        return Vector((_negate(value) for value in self), scalar_type=self._scalar_type)

    def scale(self, scalar: object) -> Vector:
        """Multiply every coordinate by one exact scalar."""

        factor = _coerce(scalar, self._scalar_type)
        return Vector(
            (_multiply(factor, value) for value in self),
            scalar_type=self._scalar_type,
        )

    def __mul__(self, scalar: object) -> Vector:
        return self.scale(scalar)

    def __rmul__(self, scalar: object) -> Vector:
        return self.scale(scalar)

    def is_zero(self) -> bool:
        """Return whether every coordinate is exactly zero."""

        return all(_is_zero(value) for value in self)


@dataclass(frozen=True, slots=True, init=False)
class Matrix:
    """An immutable nonempty rectangular matrix over an exact scalar field."""

    _rows: tuple[tuple[Scalar, ...], ...]
    _scalar_type: ScalarType

    def __init__(
        self,
        rows: Iterable[Iterable[object]],
        *,
        scalar_type: ScalarType | None = None,
    ) -> None:
        raw = _raw_rows(rows)
        resolved = _resolve_scalar_type(raw[0][0], scalar_type)
        coerced = tuple(tuple(_coerce(value, resolved) for value in row) for row in raw)
        object.__setattr__(self, "_rows", coerced)
        object.__setattr__(self, "_scalar_type", resolved)

    @classmethod
    def identity(
        cls,
        size: int,
        *,
        scalar_type: ScalarType = Rational,
    ) -> Matrix:
        """Construct an exact identity matrix of the requested positive size."""

        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise ValueError("identity size must be a positive integer")
        zero = _zero(scalar_type)
        one = _one(scalar_type)
        return cls(
            (
                (one if row == column else zero for column in range(size))
                for row in range(size)
            ),
            scalar_type=scalar_type,
        )

    @property
    def rows(self) -> tuple[tuple[Scalar, ...], ...]:
        """Return the immutable row tuple."""

        return self._rows

    @property
    def shape(self) -> tuple[int, int]:
        """Return `(row_count, column_count)`."""

        return len(self._rows), len(self._rows[0])

    @property
    def row_count(self) -> int:
        """Return the number of rows."""

        return self.shape[0]

    @property
    def column_count(self) -> int:
        """Return the number of columns."""

        return self.shape[1]

    @property
    def scalar_type(self) -> ScalarType:
        """Return the exact scalar class used by this matrix."""

        return self._scalar_type

    def __len__(self) -> int:
        return self.row_count

    def __iter__(self) -> Iterator[tuple[Scalar, ...]]:
        return iter(self._rows)

    def __getitem__(self, index: int) -> tuple[Scalar, ...]:
        return self._rows[index]

    def _check_compatible(self, other: Matrix) -> None:
        _require_same_scalar_type(self._scalar_type, other._scalar_type)
        if self.shape != other.shape:
            raise ValueError("matrix dimensions do not agree")

    def __add__(self, other: Matrix) -> Matrix:
        self._check_compatible(other)
        return Matrix(
            (
                (_add(left, right) for left, right in zip(left_row, right_row, strict=True))
                for left_row, right_row in zip(self, other, strict=True)
            ),
            scalar_type=self._scalar_type,
        )

    def __sub__(self, other: Matrix) -> Matrix:
        self._check_compatible(other)
        return Matrix(
            (
                (_subtract(left, right) for left, right in zip(left_row, right_row, strict=True))
                for left_row, right_row in zip(self, other, strict=True)
            ),
            scalar_type=self._scalar_type,
        )

    def __neg__(self) -> Matrix:
        return Matrix(
            ((_negate(value) for value in row) for row in self),
            scalar_type=self._scalar_type,
        )

    def scale(self, scalar: object) -> Matrix:
        """Multiply every entry by one exact scalar."""

        factor = _coerce(scalar, self._scalar_type)
        return Matrix(
            ((_multiply(factor, value) for value in row) for row in self),
            scalar_type=self._scalar_type,
        )

    def __mul__(self, other: object) -> Matrix:
        if isinstance(other, Matrix):
            return self.matmul(other)
        return self.scale(other)

    def __rmul__(self, other: object) -> Matrix:
        if isinstance(other, Matrix):
            return other.matmul(self)
        return self.scale(other)

    def __matmul__(self, other: Matrix | Vector) -> Matrix | Vector:
        if isinstance(other, Matrix):
            return self.matmul(other)
        if isinstance(other, Vector):
            return self.matvec(other)
        raise TypeError("matrix multiplication requires a Matrix or Vector")

    def matmul(self, other: Matrix) -> Matrix:
        """Return the exact product of two dimensionally compatible matrices."""

        _require_same_scalar_type(self._scalar_type, other._scalar_type)
        if self.column_count != other.row_count:
            raise ValueError("matrix dimensions do not agree")
        zero = _zero(self._scalar_type)
        return Matrix(
            (
                (
                    _sum_products(
                        (self[row][inner], other[inner][column])
                        for inner in range(self.column_count)
                    )
                    if self.column_count
                    else zero
                    for column in range(other.column_count)
                )
                for row in range(self.row_count)
            ),
            scalar_type=self._scalar_type,
        )

    def matvec(self, vector: Vector) -> Vector:
        """Return the exact matrix–vector product."""

        _require_same_scalar_type(self._scalar_type, vector._scalar_type)
        if self.column_count != vector.dimension:
            raise ValueError("matrix and vector dimensions do not agree")
        return Vector(
            (_sum_products(zip(row, vector, strict=True)) for row in self),
            scalar_type=self._scalar_type,
        )

    def transpose(self) -> Matrix:
        """Return the exact transpose."""

        return Matrix(zip(*self._rows, strict=True), scalar_type=self._scalar_type)

    def rref(self) -> tuple[Matrix, tuple[int, ...]]:
        """Return deterministic reduced row-echelon form and pivot columns."""

        work = [list(row) for row in self._rows]
        pivots: list[int] = []
        pivot_row = 0
        for column in range(self.column_count):
            pivot = next(
                (
                    row
                    for row in range(pivot_row, self.row_count)
                    if not _is_zero(work[row][column])
                ),
                None,
            )
            if pivot is None:
                continue
            work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
            pivot_inverse = _inverse(work[pivot_row][column], self._scalar_type)
            work[pivot_row] = [
                _multiply(pivot_inverse, entry) for entry in work[pivot_row]
            ]
            for row in range(self.row_count):
                if row == pivot_row or _is_zero(work[row][column]):
                    continue
                factor = work[row][column]
                work[row] = [
                    _subtract(entry, _multiply(factor, pivot_entry))
                    for entry, pivot_entry in zip(work[row], work[pivot_row], strict=True)
                ]
            pivots.append(column)
            pivot_row += 1
            if pivot_row == self.row_count:
                break
        return Matrix(work, scalar_type=self._scalar_type), tuple(pivots)

    def rank(self) -> int:
        """Return the exact rank from deterministic RREF pivots."""

        return len(self.rref()[1])

    def nullspace(self) -> tuple[Vector, ...]:
        """Return a deterministic basis for the right nullspace."""

        reduced, pivots = self.rref()
        pivot_set = set(pivots)
        free_columns = [column for column in range(self.column_count) if column not in pivot_set]
        basis: list[Vector] = []
        for free_column in free_columns:
            coordinates = [_zero(self._scalar_type) for _ in range(self.column_count)]
            coordinates[free_column] = _one(self._scalar_type)
            for row, pivot in enumerate(pivots):
                coordinates[pivot] = _negate(reduced[row][free_column])
            basis.append(Vector(coordinates, scalar_type=self._scalar_type))
        return tuple(basis)

    def inverse(self) -> Matrix:
        """Return the exact inverse, rejecting nonsquare or singular matrices."""

        if self.row_count != self.column_count:
            raise ValueError("inverse requires a square matrix")
        identity = Matrix.identity(self.row_count, scalar_type=self._scalar_type)
        augmented = Matrix(
            (left_row + right_row for left_row, right_row in zip(self, identity, strict=True)),
            scalar_type=self._scalar_type,
        )
        reduced, pivots = augmented.rref()
        if pivots[: self.row_count] != tuple(range(self.row_count)):
            raise ValueError("matrix is singular")
        return Matrix(
            (row[self.row_count :] for row in reduced),
            scalar_type=self._scalar_type,
        )

    def determinant(self) -> Scalar:
        """Return the exact determinant of any square matrix."""

        if self.row_count != self.column_count:
            raise ValueError("determinant requires a square matrix")
        work = [list(row) for row in self._rows]
        result = _one(self._scalar_type)
        sign = 1
        for column in range(self.column_count):
            pivot = next(
                (row for row in range(column, self.row_count) if not _is_zero(work[row][column])),
                None,
            )
            if pivot is None:
                return _zero(self._scalar_type)
            if pivot != column:
                work[column], work[pivot] = work[pivot], work[column]
                sign = -sign
            pivot_value = work[column][column]
            result = _multiply(result, pivot_value)
            pivot_inverse = _inverse(pivot_value, self._scalar_type)
            for row in range(column + 1, self.row_count):
                if _is_zero(work[row][column]):
                    continue
                factor = _multiply(work[row][column], pivot_inverse)
                work[row] = [
                    _subtract(entry, _multiply(factor, pivot_entry))
                    for entry, pivot_entry in zip(work[row], work[column], strict=True)
                ]
        return _negate(result) if sign < 0 else result

    def __pow__(self, exponent: int) -> Matrix:
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            raise TypeError("the exponent must be an integer")
        if self.row_count != self.column_count:
            raise ValueError("power requires a square matrix")
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = Matrix.identity(self.row_count, scalar_type=self._scalar_type)
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result.matmul(base)
            base = base.matmul(base)
            power >>= 1
        return result

    def is_zero(self) -> bool:
        """Return whether every entry is exactly zero."""

        return all(_is_zero(value) for row in self for value in row)


def _sum_products(pairs: Iterable[tuple[Scalar, Scalar]]) -> Scalar:
    materialized = tuple(pairs)
    if not materialized:
        raise ValueError("a product needs at least one scalar pair")
    total = _zero(_scalar_type_for(materialized[0][0]))
    for left, right in materialized:
        total = _add(total, _multiply(left, right))
    return total


def matmul(left: Matrix, right: Matrix) -> Matrix:
    """Return `left @ right` through the matrix implementation."""

    return left.matmul(right)


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    """Return `matrix @ vector` through the matrix implementation."""

    return matrix.matvec(vector)


def rref(matrix: Matrix) -> tuple[Matrix, tuple[int, ...]]:
    """Return deterministic reduced row-echelon form and pivots."""

    return matrix.rref()


def rank(matrix: Matrix) -> int:
    """Return the exact matrix rank."""

    return matrix.rank()


def nullspace(matrix: Matrix) -> tuple[Vector, ...]:
    """Return a deterministic basis for the right nullspace."""

    return matrix.nullspace()


def inverse(matrix: Matrix) -> Matrix:
    """Return the exact matrix inverse."""

    return matrix.inverse()


def determinant(matrix: Matrix) -> Scalar:
    """Return the exact determinant."""

    return matrix.determinant()


def matrix_power(matrix: Matrix, exponent: int) -> Matrix:
    """Return an exact integer power of a square matrix."""

    return matrix**exponent


__all__ = [
    "Matrix",
    "Vector",
    "determinant",
    "inverse",
    "matmul",
    "matrix_power",
    "matvec",
    "nullspace",
    "rank",
    "rref",
]
