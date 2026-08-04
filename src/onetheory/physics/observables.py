"""Terminal physical observables and comparison objects.

Owns:
    Canonical normalization, masses, mixing, CP invariants, running, thresholds,
    uncertainty propagation, and objects used to compare predictions with data.

Depends on:
    Core policy, reusable mathematics, and general quantum, gauge, matter, gravity,
    string, and vacuum concepts.

Must not:
    Feed measured values upstream into geometry or vacuum selection, hide basis choices,
    or call an unresolved prediction a physical observable.

Phase 0:
    The generic low-energy kernel is implemented; carrier-specific inputs remain
    fail-closed until one complete controlled vacuum supplies them.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from math import atan2, cos, sin, sqrt
from typing import cast

from onetheory.core.errors import IncompatibleConvention, MissingPhysicalInput, NonExactInput
from onetheory.math.linear import Matrix
from onetheory.math.numbers import Rational, coerce_rational


def _complex(value: object) -> complex:
    """Convert a supported numerical scalar to a complex value."""

    if isinstance(value, bool):
        raise NonExactInput("boolean values are not numerical observable inputs")
    if isinstance(value, (int, float, complex, Rational)):
        return complex(value)
    raise TypeError("observable matrices require numerical scalar entries")


def _matrix_det(values: tuple[tuple[complex, ...], ...]) -> complex:
    """Return a deterministic complex determinant."""

    size = len(values)
    if size == 0 or any(len(row) != size for row in values):
        raise ValueError("determinants require nonempty square matrices")
    work = [list(row) for row in values]
    result = 1.0 + 0.0j
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(work[row][column]))
        if abs(work[pivot][column]) <= 1e-15:
            return 0.0 + 0.0j
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, size):
            factor = work[row][column] / pivot_value
            for inner in range(column + 1, size):
                work[row][inner] -= factor * work[column][inner]
    return result


def _matrix_inverse(
    values: tuple[tuple[complex, ...], ...], tolerance: float = 1e-14
) -> tuple[tuple[complex, ...], ...]:
    """Invert a numerical square matrix with explicit singular-pivot failure."""

    size = len(values)
    if size == 0 or any(len(row) != size for row in values):
        raise ValueError("inversion requires a nonempty square matrix")
    work = [
        list(values[row]) + [1.0 + 0.0j if row == column else 0.0 + 0.0j for column in range(size)]
        for row in range(size)
    ]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(work[row][column]))
        if abs(work[pivot][column]) <= tolerance:
            raise ValueError("matrix is numerically singular")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [entry / divisor for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [
                left - factor * right for left, right in zip(work[row], work[column], strict=True)
            ]
    return tuple(tuple(row[size:]) for row in work)


@dataclass(frozen=True, slots=True, init=False)
class ComplexMatrix:
    """An immutable numerical complex matrix for finite-dimensional observables."""

    rows: tuple[tuple[complex, ...], ...]

    def __init__(self, rows: Iterable[Iterable[object]]) -> None:
        values = tuple(tuple(_complex(value) for value in row) for row in rows)
        if not values or not values[0] or any(len(row) != len(values[0]) for row in values):
            raise ValueError("complex matrices require nonempty rectangular rows")
        object.__setattr__(self, "rows", values)

    @classmethod
    def identity(cls, size: int) -> ComplexMatrix:
        """Construct an identity matrix."""

        if isinstance(size, bool) or size < 1:
            raise ValueError("identity size must be positive")
        return cls(
            tuple(tuple(1 if row == column else 0 for column in range(size)) for row in range(size))
        )

    @property
    def shape(self) -> tuple[int, int]:
        """Return matrix dimensions."""

        return len(self.rows), len(self.rows[0])

    @property
    def row_count(self) -> int:
        """Return the row count."""

        return self.shape[0]

    @property
    def column_count(self) -> int:
        """Return the column count."""

        return self.shape[1]

    def __getitem__(self, index: int) -> tuple[complex, ...]:
        return self.rows[index]

    def __iter__(self) -> Iterator[tuple[complex, ...]]:
        return iter(self.rows)

    def __matmul__(self, other: ComplexMatrix) -> ComplexMatrix:
        """Return an exact-shape checked numerical matrix product."""

        if self.column_count != other.row_count:
            raise ValueError("matrix dimensions do not agree")
        return ComplexMatrix(
            tuple(
                tuple(
                    sum(
                        (
                            self[row][inner] * other[inner][column]
                            for inner in range(self.column_count)
                        ),
                        0.0 + 0.0j,
                    )
                    for column in range(other.column_count)
                )
                for row in range(self.row_count)
            )
        )

    def __add__(self, other: ComplexMatrix) -> ComplexMatrix:
        if self.shape != other.shape:
            raise ValueError("matrix dimensions do not agree")
        return ComplexMatrix(
            tuple(
                tuple(left + right for left, right in zip(row, other[index], strict=True))
                for index, row in enumerate(self.rows)
            )
        )

    def __sub__(self, other: ComplexMatrix) -> ComplexMatrix:
        return self + other.scale(-1)

    def scale(self, scalar: object) -> ComplexMatrix:
        """Scale every entry by one numerical scalar."""

        factor = _complex(scalar)
        return ComplexMatrix(tuple(tuple(factor * value for value in row) for row in self.rows))

    def transpose(self) -> ComplexMatrix:
        """Return the ordinary transpose."""

        return ComplexMatrix(zip(*self.rows, strict=True))

    def conjugate_transpose(self) -> ComplexMatrix:
        """Return the Hermitian adjoint."""

        return ComplexMatrix(
            tuple(tuple(value.conjugate() for value in row) for row in zip(*self.rows, strict=True))
        )

    def determinant(self) -> complex:
        """Return the numerical determinant."""

        return _matrix_det(self.rows)

    def inverse(self, tolerance: float = 1e-14) -> ComplexMatrix:
        """Return the numerical inverse."""

        return ComplexMatrix(_matrix_inverse(self.rows, tolerance))

    def rank(self, tolerance: float = 1e-10) -> int:
        """Return numerical rank by deterministic row reduction."""

        work = [list(row) for row in self.rows]
        pivot_row = 0
        rank = 0
        for column in range(self.column_count):
            pivot = max(range(pivot_row, self.row_count), key=lambda row: abs(work[row][column]))
            if abs(work[pivot][column]) <= tolerance:
                continue
            work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
            divisor = work[pivot_row][column]
            work[pivot_row] = [entry / divisor for entry in work[pivot_row]]
            for row in range(self.row_count):
                if row == pivot_row:
                    continue
                factor = work[row][column]
                work[row] = [
                    left - factor * right
                    for left, right in zip(work[row], work[pivot_row], strict=True)
                ]
            pivot_row += 1
            rank += 1
            if pivot_row == self.row_count:
                break
        return rank

    def norm(self) -> float:
        """Return the Frobenius norm."""

        return sqrt(sum(abs(value) ** 2 for row in self.rows for value in row))

    def is_close(self, other: ComplexMatrix, tolerance: float = 1e-10) -> bool:
        """Compare equal-shaped matrices entrywise."""

        return self.shape == other.shape and all(
            abs(left - right) <= tolerance
            for row, other_row in zip(self.rows, other.rows, strict=True)
            for left, right in zip(row, other_row, strict=True)
        )


def _as_complex_matrix(value: Matrix | ComplexMatrix | Iterable[Iterable[object]]) -> ComplexMatrix:
    """Convert exact or numerical matrix input to the numerical matrix kernel."""

    if isinstance(value, ComplexMatrix):
        return value
    if isinstance(value, Matrix):
        return ComplexMatrix(value.rows)
    return ComplexMatrix(value)


@dataclass(frozen=True, slots=True, init=False)
class PhysicalEvaluationContext:
    """The immutable compactification, vacuum, scheme, scale, and precision context."""

    compactification_id: str
    geometry_digest: str
    bundle_digest: str
    vacuum_id: str
    moduli_values: tuple[tuple[str, complex], ...]
    renormalization_scheme: str
    matching_scale: Rational
    unit_convention: str
    precision: int
    tolerance: float
    approximation_order: str
    input_provenance: tuple[str, ...]

    def __init__(
        self,
        compactification_id: str,
        geometry_digest: str,
        bundle_digest: str,
        vacuum_id: str,
        moduli_values: Mapping[str, object] | Iterable[tuple[str, object]],
        renormalization_scheme: str,
        matching_scale: object,
        unit_convention: str,
        precision: int,
        tolerance: float,
        approximation_order: str,
        input_provenance: Iterable[str],
    ) -> None:
        values = tuple(
            sorted((name, _complex(value)) for name, value in dict(moduli_values).items())
        )
        provenance = tuple(input_provenance)
        strings = (
            compactification_id,
            geometry_digest,
            bundle_digest,
            vacuum_id,
            renormalization_scheme,
            unit_convention,
            approximation_order,
        )
        if any(not value.strip() for value in strings) or not values or not provenance:
            raise ValueError("physical contexts require complete identifiers and provenance")
        if any(not name.strip() for name, _ in values):
            raise ValueError("moduli names must be nonempty")
        if isinstance(precision, bool) or precision < 1 or tolerance <= 0:
            raise ValueError("context precision and tolerance must be positive")
        if any(not item.strip() for item in provenance):
            raise ValueError("context provenance entries must be nonempty")
        object.__setattr__(self, "compactification_id", compactification_id)
        object.__setattr__(self, "geometry_digest", geometry_digest)
        object.__setattr__(self, "bundle_digest", bundle_digest)
        object.__setattr__(self, "vacuum_id", vacuum_id)
        object.__setattr__(self, "moduli_values", values)
        object.__setattr__(self, "renormalization_scheme", renormalization_scheme)
        object.__setattr__(self, "matching_scale", coerce_rational(matching_scale))
        object.__setattr__(self, "unit_convention", unit_convention)
        object.__setattr__(self, "precision", precision)
        object.__setattr__(self, "tolerance", float(tolerance))
        object.__setattr__(self, "approximation_order", approximation_order)
        object.__setattr__(self, "input_provenance", provenance)

    def assert_compatible(
        self,
        other: PhysicalEvaluationContext,
        *,
        allow_scale_transport: bool = False,
        allow_basis_transport: bool = False,
    ) -> None:
        """Reject mixed physical contexts unless a declared transport is allowed."""

        if self.compactification_id != other.compactification_id:
            raise IncompatibleConvention("physical objects use different compactifications")
        if (
            self.geometry_digest != other.geometry_digest
            or self.bundle_digest != other.bundle_digest
        ):
            raise IncompatibleConvention(
                "physical objects use different geometry or bundle digests"
            )
        if self.vacuum_id != other.vacuum_id or self.moduli_values != other.moduli_values:
            raise IncompatibleConvention("physical objects use different frozen vacua")
        if self.renormalization_scheme != other.renormalization_scheme:
            raise IncompatibleConvention("physical objects use different renormalization schemes")
        if self.unit_convention != other.unit_convention:
            raise IncompatibleConvention("physical objects use different unit conventions")
        if not allow_scale_transport and self.matching_scale != other.matching_scale:
            raise IncompatibleConvention("physical objects use different matching scales")
        if not allow_basis_transport and self.approximation_order != other.approximation_order:
            raise IncompatibleConvention("physical objects use different approximation orders")


@dataclass(frozen=True, slots=True)
class PhysicalMatrix:
    """A numerical matrix bound to a frozen physical evaluation context and basis."""

    matrix: ComplexMatrix
    context: PhysicalEvaluationContext
    basis: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            not self.basis.strip()
            or not self.provenance
            or any(not item.strip() for item in self.provenance)
        ):
            raise ValueError("physical matrices require basis and provenance")

    @property
    def rank(self) -> int:
        """Return numerical rank."""

        return self.matrix.rank(self.context.tolerance)

    def require_compatible(self, other: PhysicalMatrix) -> None:
        """Reject matrix operations across physical contexts or bases."""

        self.context.assert_compatible(other.context)
        if self.basis != other.basis:
            raise IncompatibleConvention("physical matrices use different bases")


ContextBoundArray = PhysicalMatrix


@dataclass(frozen=True, slots=True)
class HermitianMetric:
    """A positive-definiteness-certified Hermitian kinetic or matter metric."""

    matrix: ComplexMatrix
    context: PhysicalEvaluationContext
    basis: str
    name: str
    provenance: tuple[str, ...]

    def __init__(
        self,
        matrix: Matrix | ComplexMatrix | Iterable[Iterable[object]],
        context: PhysicalEvaluationContext,
        basis: str,
        name: str,
        provenance: Iterable[str],
    ) -> None:
        numerical = _as_complex_matrix(matrix)
        if numerical.row_count != numerical.column_count or not basis.strip() or not name.strip():
            raise ValueError("Hermitian metrics require named nonempty square matrices")
        if not numerical.conjugate_transpose().is_close(numerical, context.tolerance):
            raise ValueError("kinetic metrics must be Hermitian")
        values = tuple(provenance)
        if not values or any(not item.strip() for item in values):
            raise ValueError("metrics require provenance")
        object.__setattr__(self, "matrix", numerical)
        object.__setattr__(self, "context", context)
        object.__setattr__(self, "basis", basis)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "provenance", values)

    @property
    def dimension(self) -> int:
        """Return the metric dimension."""

        return self.matrix.row_count

    @property
    def positive_definite(self) -> bool:
        """Certify positive definiteness using exact-size principal minors."""

        for size in range(1, self.dimension + 1):
            minor = tuple(
                tuple(self.matrix[row][column] for column in range(size)) for row in range(size)
            )
            determinant = _matrix_det(minor)
            if (
                abs(determinant.imag) > self.context.tolerance
                or determinant.real <= self.context.tolerance
            ):
                return False
        return True

    @property
    def positive_semidefinite(self) -> bool:
        """Check the nonnegative principal-minor boundary."""

        return all(
            _matrix_det(
                tuple(
                    tuple(self.matrix[row][column] for column in range(size)) for row in range(size)
                )
            ).real
            >= -self.context.tolerance
            for size in range(1, self.dimension + 1)
        )

    def eigenvalues_vectors(self) -> tuple[tuple[float, ...], ComplexMatrix]:
        """Return sorted Hermitian eigenvalues with deterministic phase fixing."""

        return _hermitian_eigensystem(self.matrix, self.context.tolerance)

    @property
    def degenerate_eigenspaces(self) -> tuple[tuple[int, ...], ...]:
        """Return indices whose eigenvalues are degenerate at context precision."""

        eigenvalues, _ = self.eigenvalues_vectors()
        groups: list[tuple[int, ...]] = []
        for index, value in enumerate(eigenvalues):
            if index and abs(value - eigenvalues[index - 1]) <= self.context.tolerance:
                if groups:
                    groups[-1] = (*groups[-1], index)
            else:
                groups.append((index,))
        return tuple(group for group in groups if len(group) > 1)

    def inverse_sqrt(self) -> ComplexMatrix:
        """Return G⁻¹/², rejecting singular or non-positive metrics."""

        if not self.positive_definite:
            raise ValueError("inverse square roots require a positive-definite metric")
        eigenvalues, vectors = self.eigenvalues_vectors()
        diagonal = ComplexMatrix(
            tuple(
                tuple(
                    1 / sqrt(eigenvalues[row]) if row == column else 0
                    for column in range(self.dimension)
                )
                for row in range(self.dimension)
            )
        )
        return vectors @ diagonal @ vectors.conjugate_transpose()

    def condition_number(self) -> float:
        """Return the spectral condition number."""

        eigenvalues, _ = self.eigenvalues_vectors()
        if not eigenvalues or min(eigenvalues) <= self.context.tolerance:
            return float("inf")
        return max(eigenvalues) / min(eigenvalues)


HermitianMatrix = HermitianMetric


def _matmul_lists(left: list[list[complex]], right: list[list[complex]]) -> list[list[complex]]:
    """Multiply mutable complex matrices for the Jacobi eigensolver."""

    return [
        [
            sum(
                (left[row][inner] * right[inner][column] for inner in range(len(right))), 0.0 + 0.0j
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def _hermitian_eigensystem(
    matrix: ComplexMatrix, tolerance: float
) -> tuple[tuple[float, ...], ComplexMatrix]:
    """Diagonalize a small Hermitian matrix by deterministic complex Jacobi rotations."""

    size = matrix.row_count
    values = [list(row) for row in matrix.rows]
    vectors = [
        [1.0 + 0.0j if row == column else 0.0 + 0.0j for column in range(size)]
        for row in range(size)
    ]
    for _ in range(max(20, 20 * size * size)):
        pair = max(
            (
                (abs(values[row][column]), row, column)
                for row in range(size)
                for column in range(row + 1, size)
            ),
            default=(0.0, 0, 0),
        )
        magnitude, p, q = pair
        if magnitude <= tolerance:
            break
        apq = values[p][q]
        phase = apq / abs(apq)
        theta = 0.5 * atan2(2 * abs(apq), (values[q][q] - values[p][p]).real)
        c, s = cos(theta), sin(theta)
        rotation = ComplexMatrix(
            tuple(
                tuple(
                    c
                    if row == column and row in (p, q)
                    else s * phase
                    if row == p and column == q
                    else -s * phase.conjugate()
                    if row == q and column == p
                    else 1
                    if row == column
                    else 0
                    for column in range(size)
                )
                for row in range(size)
            )
        )
        rotated = rotation.conjugate_transpose() @ ComplexMatrix(values) @ rotation
        values = [list(row) for row in rotated.rows]
        vectors = [list(row) for row in (ComplexMatrix(vectors) @ rotation).rows]
    order = tuple(sorted(range(size), key=lambda index: values[index][index].real, reverse=True))
    eigenvalues = tuple(values[index][index].real for index in order)
    columns = []
    for index in order:
        column = [vectors[row][index] for row in range(size)]
        pivot = max(range(size), key=lambda row: abs(column[row]))
        if abs(column[pivot]) > tolerance:
            phase = column[pivot] / abs(column[pivot])
            column = [entry / phase for entry in column]
        columns.append(column)
    eigenvectors = ComplexMatrix(
        tuple(tuple(columns[column][row] for column in range(size)) for row in range(size))
    )
    return eigenvalues, eigenvectors


@dataclass(frozen=True, slots=True)
class CanonicalTransformation:
    """A context-bound inverse-square-root field transformation."""

    metric: HermitianMetric
    matrix: ComplexMatrix
    condition_number: float
    degenerate_eigenspaces: tuple[tuple[int, ...], ...]

    @classmethod
    def from_metric(cls, metric: HermitianMetric) -> CanonicalTransformation:
        """Construct a canonical transformation from a positive metric."""

        matrix = metric.inverse_sqrt()
        return cls(metric, matrix, metric.condition_number(), metric.degenerate_eigenspaces)

    def transform(self, physical: PhysicalMatrix) -> PhysicalMatrix:
        """Transform a matrix in the metric basis without changing its context."""

        self.metric.context.assert_compatible(physical.context)
        if physical.basis != self.metric.basis:
            raise IncompatibleConvention("canonical transformation uses a different basis")
        return PhysicalMatrix(
            self.matrix @ physical.matrix, physical.context, physical.basis, physical.provenance
        )


@dataclass(frozen=True, slots=True)
class HolomorphicYukawa:
    """An explicit holomorphic generation tensor before canonical normalization."""

    matrix: PhysicalMatrix
    left_basis: str
    right_basis: str
    higgs_basis: str

    def __post_init__(self) -> None:
        if (
            not self.left_basis.strip()
            or not self.right_basis.strip()
            or not self.higgs_basis.strip()
        ):
            raise ValueError("holomorphic Yukawas require explicit field bases")


@dataclass(frozen=True, slots=True)
class PhysicalYukawa:
    """A canonically normalized Yukawa matrix built only from explicit metrics."""

    matrix: PhysicalMatrix
    holomorphic: HolomorphicYukawa
    left_normalization: CanonicalTransformation
    right_normalization: CanonicalTransformation
    higgs_norm: float
    rank_preserved: bool

    @classmethod
    def from_inputs(
        cls,
        holomorphic: HolomorphicYukawa,
        left_metric: HermitianMetric,
        right_metric: HermitianMetric,
        higgs_metric: HermitianMetric,
    ) -> PhysicalYukawa:
        """Construct physical Yukawas from positive matter and Higgs metrics."""

        holomorphic.matrix.context.assert_compatible(left_metric.context)
        holomorphic.matrix.context.assert_compatible(right_metric.context)
        holomorphic.matrix.context.assert_compatible(higgs_metric.context)
        if left_metric.basis != holomorphic.left_basis:
            raise IncompatibleConvention("left matter metric uses a different field basis")
        if right_metric.basis != holomorphic.right_basis:
            raise IncompatibleConvention("right matter metric uses a different field basis")
        if higgs_metric.basis != holomorphic.higgs_basis:
            raise IncompatibleConvention("Higgs metric uses a different field basis")
        if holomorphic.matrix.matrix.shape != (left_metric.dimension, right_metric.dimension):
            raise ValueError("Yukawa and matter metric dimensions do not agree")
        left = CanonicalTransformation.from_metric(left_metric)
        right = CanonicalTransformation.from_metric(right_metric)
        higgs = CanonicalTransformation.from_metric(higgs_metric)
        transformed = left.matrix.transpose() @ holomorphic.matrix.matrix @ right.matrix
        higgs_value = higgs.matrix[0][0].real
        if higgs_metric.dimension != 1 or higgs_value <= 0:
            raise ValueError("a single positive Higgs normalization is required")
        transformed = transformed.scale(1 / higgs_value)
        physical = PhysicalMatrix(
            transformed,
            holomorphic.matrix.context,
            holomorphic.matrix.basis,
            (*holomorphic.matrix.provenance, "canonical matter and Higgs metrics"),
        )
        return cls(
            physical,
            holomorphic,
            left,
            right,
            higgs_value,
            physical.rank == holomorphic.matrix.rank,
        )


def canonicalize_yukawa(
    holomorphic: HolomorphicYukawa,
    left_metric: HermitianMetric,
    right_metric: HermitianMetric,
    higgs_metric: HermitianMetric,
) -> PhysicalYukawa:
    """Canonicalize one explicit holomorphic Yukawa tensor."""

    return PhysicalYukawa.from_inputs(holomorphic, left_metric, right_metric, higgs_metric)


@dataclass(frozen=True, slots=True)
class SingularValueDecomposition:
    """A context-bound singular-value decomposition with degeneracy metadata."""

    singular_values: tuple[float, ...]
    left_vectors: PhysicalMatrix
    right_vectors: PhysicalMatrix
    degenerate_blocks: tuple[tuple[int, ...], ...]

    @property
    def rank(self) -> int:
        """Return the number of nonzero singular values."""

        return sum(value > self.left_vectors.context.tolerance for value in self.singular_values)


def singular_value_decomposition(matrix: PhysicalMatrix) -> SingularValueDecomposition:
    """Compute a deterministic SVD from the Hermitian right Gram matrix."""

    gram = matrix.matrix.conjugate_transpose() @ matrix.matrix
    values, right = _hermitian_eigensystem(gram, matrix.context.tolerance)
    singular = tuple(sqrt(max(0.0, value)) for value in values)
    left_columns: list[list[complex]] = []
    for index, value in enumerate(singular):
        vector = [right[row][index] for row in range(right.row_count)]
        if value > matrix.context.tolerance:
            product = matrix.matrix @ ComplexMatrix(tuple((item,) for item in vector))
            column = [entry[0] / value for entry in product.rows]
        else:
            column = [1.0 if row == index else 0.0 for row in range(matrix.matrix.row_count)]
        left_columns.append(column)
    left_rows = tuple(
        tuple(left_columns[column][row] for column in range(len(left_columns)))
        for row in range(matrix.matrix.row_count)
    )
    right_physical = PhysicalMatrix(
        right, matrix.context, matrix.basis, (*matrix.provenance, "SVD")
    )
    left_physical = PhysicalMatrix(
        ComplexMatrix(left_rows), matrix.context, matrix.basis, (*matrix.provenance, "SVD")
    )
    blocks: list[tuple[int, ...]] = []
    for index, value in enumerate(singular):
        if index and abs(value - singular[index - 1]) <= matrix.context.tolerance:
            if blocks:
                blocks[-1] = (*blocks[-1], index)
        else:
            blocks.append((index,))
    return SingularValueDecomposition(
        singular, left_physical, right_physical, tuple(block for block in blocks if len(block) > 1)
    )


def ordered_masses(matrix: PhysicalMatrix) -> tuple[float, ...]:
    """Return descending singular values as physical masses."""

    return singular_value_decomposition(matrix).singular_values


@dataclass(frozen=True, slots=True)
class MixingMatrix:
    """A unitary mixing matrix with explicit context and degeneracy status."""

    matrix: PhysicalMatrix
    physical: bool
    degenerate_blocks: tuple[tuple[int, ...], ...]

    @property
    def unitarity_residual(self) -> float:
        """Return ||V†V-I||."""

        identity = ComplexMatrix.identity(self.matrix.matrix.column_count)
        return (self.matrix.matrix.conjugate_transpose() @ self.matrix.matrix - identity).norm()


def mixing_matrix(up: SingularValueDecomposition, down: SingularValueDecomposition) -> MixingMatrix:
    """Construct a left-handed mixing matrix with context and degeneracy checks."""

    up.left_vectors.require_compatible(down.left_vectors)
    if up.left_vectors.matrix.shape != down.left_vectors.matrix.shape:
        raise ValueError("mixing matrices require equal dimensions")
    matrix = up.left_vectors.matrix.conjugate_transpose() @ down.left_vectors.matrix
    physical = not up.degenerate_blocks and not down.degenerate_blocks
    return MixingMatrix(
        PhysicalMatrix(
            matrix, up.left_vectors.context, up.left_vectors.basis, ("left singular vectors",)
        ),
        physical,
        (*up.degenerate_blocks, *down.degenerate_blocks),
    )


@dataclass(frozen=True, slots=True)
class FlavorObservables:
    """Basis-safe CKM/PMNS invariants derived from one mixing matrix."""

    mixing: MixingMatrix
    angles: tuple[float, float, float]
    jarlskog: float
    commutator_determinant: complex | None

    @classmethod
    def from_mixing(
        cls,
        mixing: MixingMatrix,
        up_mass_squared: PhysicalMatrix | None = None,
        down_mass_squared: PhysicalMatrix | None = None,
    ) -> FlavorObservables:
        """Extract invariant quantities without selecting arbitrary degenerate phases."""

        if not mixing.physical:
            raise MissingPhysicalInput("nondegenerate flavor basis")
        values = mixing.matrix.matrix
        if values.shape[0] < 3 or values.shape[1] < 3:
            raise ValueError("three-family flavor observables require a 3x3 matrix")
        s13 = min(1.0, abs(values[0][2]))
        s12 = min(1.0, abs(values[0][1]) / max(cos(asin_safe(s13)), 1e-15))
        s23 = min(1.0, abs(values[1][2]) / max(cos(asin_safe(s13)), 1e-15))
        angles = (asin_safe(s12), asin_safe(s23), asin_safe(s13))
        jarlskog = (
            values[0][0] * values[1][1] * values[0][1].conjugate() * values[1][0].conjugate()
        ).imag
        commutator = None
        if up_mass_squared is not None and down_mass_squared is not None:
            up_mass_squared.require_compatible(down_mass_squared)
            commutator = (
                up_mass_squared.matrix @ down_mass_squared.matrix
                - down_mass_squared.matrix @ up_mass_squared.matrix
            ).determinant()
        return cls(mixing, angles, jarlskog, commutator)


def asin_safe(value: float) -> float:
    """Return a clamped inverse sine for bounded mixing magnitudes."""

    from math import asin

    return asin(max(-1.0, min(1.0, value)))


def jarlskog_invariant(matrix: PhysicalMatrix) -> float:
    """Return the rephasing-invariant three-family Jarlskog quantity."""

    values = matrix.matrix
    if values.row_count < 2 or values.column_count < 2:
        raise ValueError("Jarlskog invariants require at least two families")
    return (values[0][0] * values[1][1] * values[0][1].conjugate() * values[1][0].conjugate()).imag


@dataclass(frozen=True, slots=True)
class DiracNeutrinoMatrix:
    """An explicit context-bound Dirac neutrino matrix."""

    matrix: PhysicalMatrix


@dataclass(frozen=True, slots=True)
class MajoranaMatrix:
    """An explicit symmetric Majorana matrix with no implicit heavy scale."""

    matrix: PhysicalMatrix

    def __post_init__(self) -> None:
        if not self.matrix.matrix.transpose().is_close(
            self.matrix.matrix, self.matrix.context.tolerance
        ):
            raise ValueError("Majorana matrices must be symmetric")


@dataclass(frozen=True, slots=True)
class SeesawResult:
    """Full and reduced type-I seesaw matrices with agreement diagnostics."""

    light_matrix: PhysicalMatrix
    heavy_matrix: PhysicalMatrix
    full_matrix: PhysicalMatrix
    reduced_agreement_residual: float
    provenance: tuple[str, ...]

    @property
    def light_eigenvalues(self) -> tuple[float, ...]:
        """Return the singular values of the reduced light-neutrino matrix."""

        values, _ = _hermitian_eigensystem(
            self.light_matrix.matrix.conjugate_transpose() @ self.light_matrix.matrix,
            self.light_matrix.context.tolerance,
        )
        return tuple(sqrt(max(0.0, value)) for value in values)

    @property
    def heavy_eigenvalues(self) -> tuple[float, ...]:
        """Return the singular values of the explicit heavy Majorana matrix."""

        values, _ = _hermitian_eigensystem(
            self.heavy_matrix.matrix.conjugate_transpose() @ self.heavy_matrix.matrix,
            self.heavy_matrix.context.tolerance,
        )
        return tuple(sqrt(max(0.0, value)) for value in values)


@dataclass(frozen=True, slots=True)
class NeutrinoObservables:
    """Neutrino masses and double-beta amplitude from explicit seesaw data."""

    light_masses: tuple[float, ...]
    heavy_masses: tuple[float, ...]
    majorana_phases: tuple[float, ...]
    effective_neutrinoless_double_beta: float
    context: PhysicalEvaluationContext
    provenance: tuple[str, ...]


def neutrino_observables(
    seesaw: SeesawResult,
    majorana_phases: Sequence[float],
    electron_index: int = 0,
) -> NeutrinoObservables:
    """Evaluate neutrino observables only with explicit phase data."""

    if electron_index < 0 or electron_index >= seesaw.light_matrix.matrix.row_count:
        raise ValueError("the electron index must select a light-neutrino state")
    phases = tuple(float(value) for value in majorana_phases)
    if len(phases) != len(seesaw.light_eigenvalues):
        raise ValueError("one explicit Majorana phase is required per light state")
    effective = abs(seesaw.light_matrix.matrix[electron_index][electron_index])
    return NeutrinoObservables(
        seesaw.light_eigenvalues,
        seesaw.heavy_eigenvalues,
        phases,
        effective,
        seesaw.light_matrix.context,
        (*seesaw.provenance, "explicit Majorana phases and double-beta amplitude"),
    )

def type_i_seesaw(dirac: DiracNeutrinoMatrix, majorana: MajoranaMatrix) -> SeesawResult:
    """Compute a type-I seesaw only from explicit Dirac and Majorana inputs."""

    dirac.matrix.require_compatible(majorana.matrix)
    inverse = majorana.matrix.matrix.inverse(dirac.matrix.context.tolerance)
    light = dirac.matrix.matrix @ inverse @ dirac.matrix.matrix.transpose()
    reduced = light.scale(-1)
    zero = ComplexMatrix(
        tuple(
            tuple(0 for _ in range(dirac.matrix.matrix.row_count))
            for _ in range(dirac.matrix.matrix.row_count)
        )
    )
    full = ComplexMatrix(
        tuple(
            tuple(zero[row][column] for column in range(zero.column_count))
            + tuple(
                dirac.matrix.matrix[row][column]
                for column in range(dirac.matrix.matrix.column_count)
            )
            for row in range(zero.row_count)
        )
        + tuple(
            tuple(
                dirac.matrix.matrix.transpose()[row][column]
                for column in range(dirac.matrix.matrix.transpose().column_count)
            )
            + tuple(
                majorana.matrix.matrix[row][column]
                for column in range(majorana.matrix.matrix.column_count)
            )
            for row in range(majorana.matrix.matrix.row_count)
        )
    )
    return SeesawResult(
        PhysicalMatrix(
            reduced,
            dirac.matrix.context,
            dirac.matrix.basis,
            (*dirac.matrix.provenance, "type-I seesaw"),
        ),
        majorana.matrix,
        PhysicalMatrix(
            full,
            dirac.matrix.context,
            dirac.matrix.basis,
            (*dirac.matrix.provenance, "full seesaw block"),
        ),
        (light + reduced).norm(),
        (*dirac.matrix.provenance, *majorana.matrix.provenance),
    )


@dataclass(frozen=True, slots=True)
class OperatorBasis:
    """An immutable effective-field-theory operator basis."""

    name: str
    operators: tuple[str, ...]
    scheme: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            not self.name.strip()
            or not self.operators
            or len(set(self.operators)) != len(self.operators)
        ):
            raise ValueError("operator bases require unique named operators")
        if not self.scheme.strip() or not self.provenance:
            raise ValueError("operator bases require scheme and provenance")


@dataclass(frozen=True, slots=True)
class EffectiveTheory:
    """One ultraviolet or infrared theory at a declared matching scale."""

    name: str
    operator_basis: OperatorBasis
    context: PhysicalEvaluationContext
    loop_order: int
    direction: str

    def __post_init__(self) -> None:
        if not self.name.strip() or self.loop_order < 0 or self.direction not in {"UV", "IR"}:
            raise ValueError("effective theories require a direction and nonnegative loop order")
        if self.operator_basis.scheme != self.context.renormalization_scheme:
            raise IncompatibleConvention("theory basis and context use different schemes")


@dataclass(frozen=True, slots=True)
class WilsonCoefficient:
    """A context-bound Wilson coefficient in an explicit operator basis."""

    operator: str
    value: complex
    theory: EffectiveTheory
    context: PhysicalEvaluationContext

    def __post_init__(self) -> None:
        if self.operator not in self.theory.operator_basis.operators:
            raise ValueError("Wilson coefficient uses an undeclared operator")
        self.context.assert_compatible(self.theory.context)


@dataclass(frozen=True, slots=True)
class ThresholdEvent:
    """An ordered decoupling event naming every integrated-out field and mass."""

    name: str
    integrated_out_fields: tuple[str, ...]
    masses: tuple[float, ...]
    scale: Rational
    context: PhysicalEvaluationContext
    matching: Callable[[Mapping[str, complex]], Mapping[str, complex]] | None = None

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.integrated_out_fields:
            raise ValueError("thresholds require named integrated-out fields")
        if len(self.integrated_out_fields) != len(self.masses) or any(
            mass <= 0 for mass in self.masses
        ):
            raise ValueError("threshold fields require positive masses")
        if self.scale <= 0 or any(not field.strip() for field in self.integrated_out_fields):
            raise ValueError("threshold fields and scales must be positive and named")

    @property
    def available(self) -> bool:
        """Return whether an explicit matching calculation was supplied."""

        return self.matching is not None

    def apply(self, values: Mapping[str, complex]) -> dict[str, complex]:
        """Apply explicit matching or fail closed for a symbolic-only threshold."""

        if self.matching is None:
            raise MissingPhysicalInput(f"threshold calculation for {self.name}")
        return dict(self.matching(values))


@dataclass(frozen=True, slots=True)
class MatchingCondition:
    """A calculated UV-to-IR matching condition."""

    ultraviolet: EffectiveTheory
    infrared: EffectiveTheory
    threshold: ThresholdEvent
    coefficient_map: tuple[WilsonCoefficient, ...]
    continuity_residual: float
    truncation_uncertainty: float

    def __post_init__(self) -> None:
        self.ultraviolet.context.assert_compatible(
            self.infrared.context, allow_scale_transport=True
        )
        if self.ultraviolet.direction != "UV" or self.infrared.direction != "IR":
            raise ValueError("matching requires UV then IR theories")
        if self.continuity_residual < 0 or self.truncation_uncertainty < 0:
            raise ValueError("matching diagnostics must be nonnegative")


@dataclass(frozen=True, slots=True)
class MatchingReport:
    """A threshold-matching report with explicit availability status."""

    condition: MatchingCondition | None
    status: str
    reason: str


def match_threshold(
    ultraviolet: EffectiveTheory,
    infrared: EffectiveTheory,
    threshold: ThresholdEvent,
    values: Mapping[str, complex],
    tolerance: float,
    truncation_uncertainty: float,
) -> MatchingReport:
    """Execute one threshold match only when its calculation is explicit."""

    ultraviolet.context.assert_compatible(infrared.context, allow_scale_transport=True)
    threshold.context.assert_compatible(ultraviolet.context, allow_scale_transport=True)
    if (
        threshold.scale <= infrared.context.matching_scale
        or threshold.scale >= ultraviolet.context.matching_scale
    ):
        raise ValueError("threshold scale must lie strictly between UV and IR scales")
    matched = threshold.apply(values)
    residual = max(
        (abs(matched[name] - values[name]) for name in matched if name in values), default=0.0
    )
    coefficients = tuple(
        WilsonCoefficient(name, value, infrared, infrared.context)
        for name, value in matched.items()
        if name in infrared.operator_basis.operators
    )
    condition = MatchingCondition(
        ultraviolet, infrared, threshold, coefficients, residual, truncation_uncertainty
    )
    status = "PASS" if residual <= tolerance else "FAIL"
    return MatchingReport(condition, status, "explicit threshold calculation and continuity check")


RGEStateValue = complex | float | ComplexMatrix
RGEFunction = Callable[[float, Mapping[str, RGEStateValue]], Mapping[str, RGEStateValue]]


@dataclass(frozen=True, slots=True)
class RGState:
    """One immutable point on a piecewise effective-theory RG trajectory."""

    scale: float
    values: tuple[tuple[str, RGEStateValue], ...]
    context: PhysicalEvaluationContext

    def mapping(self) -> dict[str, RGEStateValue]:
        """Return state values as a fresh mapping."""

        return dict(self.values)


@dataclass(frozen=True, slots=True)
class RGETheory:
    """A coupled beta-function system with an explicit loop order."""

    name: str
    parameters: tuple[str, ...]
    beta_function: RGEFunction
    loop_order: int
    context: PhysicalEvaluationContext
    invariant_checks: tuple[Callable[[Mapping[str, RGEStateValue]], bool], ...] = ()
    positivity_checks: tuple[Callable[[Mapping[str, RGEStateValue]], bool], ...] = ()

    def __post_init__(self) -> None:
        if (
            not self.name.strip()
            or not self.parameters
            or len(set(self.parameters)) != len(self.parameters)
        ):
            raise ValueError("RGE theories require unique parameter names")
        if self.loop_order < 1:
            raise ValueError("RGE loop order must be positive")


@dataclass(frozen=True, slots=True)
class RGEResult:
    """A refined RG trajectory with threshold and diagnostic evidence."""

    states: tuple[RGState, ...]
    threshold_events: tuple[str, ...]
    refinement_errors: tuple[float, ...]
    stiffness_diagnostic: float
    converged: bool
    provenance: tuple[str, ...]


def _state_add(left: RGEStateValue, right: RGEStateValue) -> RGEStateValue:
    if isinstance(left, ComplexMatrix) and isinstance(right, ComplexMatrix):
        return left + right
    if isinstance(left, ComplexMatrix) or isinstance(right, ComplexMatrix):
        raise TypeError("RGE matrix and scalar values cannot be mixed")
    return complex(left) + complex(right)


def _state_scale(value: RGEStateValue, scalar: float) -> RGEStateValue:
    if isinstance(value, ComplexMatrix):
        return value.scale(scalar)
    return value * scalar


def _scalar_rge(value: RGEStateValue) -> complex:
    """Extract a scalar RGE value, rejecting matrix values in scalar formulas."""

    if isinstance(value, ComplexMatrix):
        raise TypeError("this RGE operation requires scalar parameters")
    return complex(value)


def _rk4_step(
    theory: RGETheory, scale: float, values: Mapping[str, RGEStateValue], step: float
) -> dict[str, RGEStateValue]:
    """Perform one coupled fourth-order Runge–Kutta step."""

    def derivative(
        at_scale: float, at_values: Mapping[str, RGEStateValue]
    ) -> dict[str, RGEStateValue]:
        result = dict(theory.beta_function(at_scale, at_values))
        if set(result) != set(theory.parameters):
            raise ValueError("RGE beta functions must return every declared parameter")
        return result

    k1 = derivative(scale, values)
    mid1 = {
        name: _state_add(values[name], _state_scale(k1[name], step / 2))
        for name in theory.parameters
    }
    k2 = derivative(scale + step / 2, mid1)
    mid2 = {
        name: _state_add(values[name], _state_scale(k2[name], step / 2))
        for name in theory.parameters
    }
    k3 = derivative(scale + step / 2, mid2)
    end = {
        name: _state_add(values[name], _state_scale(k3[name], step)) for name in theory.parameters
    }
    k4 = derivative(scale + step, end)
    return {
        name: _state_add(
            values[name],
            _state_scale(
                _state_add(
                    _state_add(k1[name], _state_scale(k2[name], 2)),
                    _state_add(_state_scale(k3[name], 2), k4[name]),
                ),
                step / 6,
            ),
        )
        for name in theory.parameters
    }


def run_rge(
    theory: RGETheory,
    initial: RGState,
    target_scale: float,
    step: float,
    tolerance: float,
    thresholds: Iterable[ThresholdEvent] = (),
    max_steps: int = 100000,
) -> RGEResult:
    """Integrate forward or backward with adaptive refinement and thresholds."""

    theory.context.assert_compatible(initial.context, allow_scale_transport=True)
    if target_scale <= 0 or step <= 0 or tolerance <= 0 or max_steps < 1:
        raise ValueError("RGE target, step, tolerance, and step limit must be positive")
    direction = 1.0 if target_scale >= initial.scale else -1.0
    supplied_events = tuple(thresholds)
    for event in supplied_events:
        theory.context.assert_compatible(event.context, allow_scale_transport=True)
        if (float(event.scale) - initial.scale) * direction <= 0 or (
            target_scale - float(event.scale)
        ) * direction <= 0:
            raise ValueError("thresholds must lie strictly between initial and target scales")
    events = tuple(
        sorted(supplied_events, key=lambda event: float(event.scale), reverse=direction < 0)
    )
    if any(
        left.scale == right.scale for left, right in zip(events[:-1], events[1:], strict=True)
    ):
        raise ValueError("threshold scales must be distinct")
    states = [initial]
    refinement: list[float] = []
    current = initial.scale
    values = initial.mapping()
    event_names: list[str] = []
    event_index = 0
    steps = 0
    while (target_scale - current) * direction > tolerance:
        if steps >= max_steps:
            return RGEResult(
                tuple(states),
                tuple(event_names),
                tuple(refinement),
                0.0,
                False,
                ("maximum step count",),
            )
        next_scale = current + direction * min(step, abs(target_scale - current))
        if event_index < len(events):
            event_scale = float(events[event_index].scale)
            if (event_scale - current) * direction > tolerance and (
                event_scale - next_scale
            ) * direction <= tolerance:
                next_scale = event_scale
        candidate = _rk4_step(theory, current, values, next_scale - current)
        half = _rk4_step(theory, current, values, (next_scale - current) / 2)
        refined = _rk4_step(
            theory, current + (next_scale - current) / 2, half, (next_scale - current) / 2
        )
        errors = []
        for name in theory.parameters:
            if isinstance(candidate[name], ComplexMatrix):
                errors.append(
                    (
                        cast(ComplexMatrix, refined[name]) - cast(ComplexMatrix, candidate[name])
                    ).norm()
                )
            else:
                errors.append(abs(_scalar_rge(refined[name]) - _scalar_rge(candidate[name])))
        error = max(errors, default=0.0)
        refinement.append(float(error))
        values = refined
        current = next_scale
        for check in (*theory.invariant_checks, *theory.positivity_checks):
            if not check(values):
                raise ValueError("RGE invariant or positivity monitor failed")
        states.append(
            RGState(
                current, tuple((name, values[name]) for name in theory.parameters), initial.context
            )
        )
        if (
            event_index < len(events)
            and abs(current - float(events[event_index].scale)) <= tolerance
        ):
            matched = events[event_index].apply(
                {name: _scalar_rge(value) for name, value in values.items()}
            )
            if set(matched) != set(values):
                raise ValueError("threshold matching must return every running parameter")
            values = cast(dict[str, RGEStateValue], matched)
            event_names.append(events[event_index].name)
            event_index += 1
        steps += 1
        if error > tolerance:
            step /= 2
        elif error < tolerance / 32:
            step *= 1.5
    stiffness = max(refinement, default=0.0) / max(min(refinement, default=tolerance), tolerance)
    return RGEResult(
        tuple(states),
        tuple(event_names),
        tuple(refinement),
        stiffness,
        all(error <= tolerance for error in refinement),
        (theory.name, f"loop order {theory.loop_order}"),
    )


def standard_model_one_loop_beta(
    _: float, values: Mapping[str, RGEStateValue]
) -> Mapping[str, RGEStateValue]:
    """Return established one-loop gauge beta functions in the SM convention."""

    coefficients = (Rational(41, 10), Rational(-19, 6), Rational(-7))
    result: dict[str, RGEStateValue] = {}
    for name, coefficient in zip(("g1", "g2", "g3"), coefficients, strict=True):
        if name not in values:
            raise MissingPhysicalInput(name)
        value = _scalar_rge(values[name])
        result[name] = complex(coefficient) * value**3 / (16 * 3.141592653589793**2)
    return result


@dataclass(frozen=True, slots=True)
class MonteCarloConfig:
    """Explicit seeded numerical-uncertainty propagation settings."""

    samples: int
    seed: int

    def __post_init__(self) -> None:
        if self.samples < 1 or isinstance(self.seed, bool):
            raise ValueError(
                "Monte Carlo propagation requires positive samples and an explicit seed"
            )


@dataclass(frozen=True, slots=True)
class MonteCarloResult:
    """Deterministic numerical samples with a declared seed."""

    mean: tuple[float, ...]
    covariance: CovarianceMatrix
    samples: int
    seed: int
    provenance: tuple[str, ...]


def monte_carlo_propagate(
    function: Callable[[tuple[float, ...]], tuple[float, ...]],
    mean: Sequence[float],
    covariance: CovarianceMatrix,
    configuration: MonteCarloConfig,
) -> MonteCarloResult:
    """Propagate numerical uncertainty with an explicit deterministic seed."""

    import random
    import statistics

    if len(mean) != len(covariance.values):
        raise ValueError("Monte Carlo mean and covariance dimensions do not agree")
    rng = random.Random(configuration.seed)
    dimension = len(mean)
    chol = [[0.0 for _ in range(dimension)] for _ in range(dimension)]
    for row in range(dimension):
        for column in range(row + 1):
            residual = covariance.values[row][column] - sum(
                chol[row][inner] * chol[column][inner] for inner in range(column)
            )
            if row == column:
                if residual < -1e-10:
                    raise ValueError("covariance is not positive semidefinite")
                chol[row][column] = sqrt(max(0.0, residual))
            elif chol[column][column] > 0:
                chol[row][column] = residual / chol[column][column]
    outputs = [
        function(tuple(
            float(mean[row])
            + sum(chol[row][column] * draws[column] for column in range(dimension))
            for row in range(dimension)
        ))
        for _ in range(configuration.samples)
        for draws in [tuple(rng.gauss(0.0, 1.0) for _ in range(dimension))]
    ]
    dimension = len(outputs[0])
    average = tuple(
        statistics.fmean(output[index] for output in outputs) for index in range(dimension)
    )
    covariance_values = tuple(
        tuple(
            sum(
                (output[row] - average[row]) * (output[column] - average[column])
                for output in outputs
            )
            / max(1, configuration.samples - 1)
            for column in range(dimension)
        )
        for row in range(dimension)
    )
    return MonteCarloResult(
        average,
        CovarianceMatrix(covariance_values, ("Monte Carlo numerical uncertainty",)),
        configuration.samples,
        configuration.seed,
        ("explicit seed",),
    )


@dataclass(frozen=True, slots=True)
class UncertaintyComponent:
    """One separately tracked uncertainty source."""

    name: str
    covariance: tuple[tuple[float, ...], ...]
    category: str
    confidence: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            not self.name.strip()
            or not self.category.strip()
            or not self.confidence.strip()
            or not self.provenance
        ):
            raise ValueError("uncertainty components require labels and provenance")
        if not _is_psd(self.covariance):
            raise ValueError("uncertainty covariance must be positive semidefinite")


@dataclass(frozen=True, slots=True)
class AsymmetricUncertainty:
    """A retained asymmetric uncertainty interval for one quantity."""

    central: float
    lower: float
    upper: float
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.lower < 0 or self.upper < 0 or not self.provenance:
            raise ValueError("asymmetric uncertainties require nonnegative bounds")


@dataclass(frozen=True, slots=True)
class BoundedUncertainty:
    """A bounded uncertainty with explicit support endpoints."""

    lower: float
    upper: float
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.lower > self.upper or not self.provenance:
            raise ValueError("bounded uncertainties require ordered endpoints")


@dataclass(frozen=True, slots=True)
class ConfidenceMetadata:
    """Confidence or credibility metadata kept separate from covariance values."""

    kind: str
    level: float
    method: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.kind.strip() or not self.method.strip() or not self.provenance:
            raise ValueError("uncertainty metadata require kind, method, and provenance")
        if not 0 < self.level < 1:
            raise ValueError("uncertainty levels must lie strictly between zero and one")


def _is_psd(matrix: Sequence[Sequence[float]], tolerance: float = 1e-10) -> bool:
    """Check symmetric positive semidefiniteness through Jacobi eigenvalues."""

    values = tuple(tuple(complex(item) for item in row) for row in matrix)
    if not values or any(len(row) != len(values) for row in values):
        return False
    if any(
        abs(values[row][column] - values[column][row].conjugate()) > tolerance
        for row in range(len(values))
        for column in range(len(values))
    ):
        return False
    eigenvalues, _ = _hermitian_eigensystem(ComplexMatrix(values), tolerance)
    return min(eigenvalues, default=-1.0) >= -tolerance


@dataclass(frozen=True, slots=True)
class CovarianceMatrix:
    """A traceable positive-semidefinite covariance matrix."""

    values: tuple[tuple[float, ...], ...]
    sources: tuple[str, ...]

    def __init__(self, values: Iterable[Iterable[float]], sources: Iterable[str]) -> None:
        data = tuple(tuple(float(value) for value in row) for row in values)
        labels = tuple(sources)
        if not data or any(len(row) != len(data) for row in data) or not labels:
            raise ValueError("covariances require square values and source labels")
        if not _is_psd(data):
            raise ValueError("covariance matrices must be positive semidefinite")
        object.__setattr__(self, "values", data)
        object.__setattr__(self, "sources", labels)

    @property
    def positive_semidefinite(self) -> bool:
        """Return the PSD certificate."""

        return _is_psd(self.values)

    def combine(self, other: CovarianceMatrix) -> CovarianceMatrix:
        """Add independent or correlated covariance contributions explicitly."""

        if len(self.values) != len(other.values):
            raise ValueError("covariance dimensions do not agree")
        return CovarianceMatrix(
            tuple(
                tuple(left + right for left, right in zip(row, other.values[index], strict=True))
                for index, row in enumerate(self.values)
            ),
            (*self.sources, *other.sources),
        )


@dataclass(frozen=True, slots=True)
class SensitivityMatrix:
    """A Jacobian with named inputs, outputs, and provenance."""

    values: tuple[tuple[float, ...], ...]
    input_names: tuple[str, ...]
    output_names: tuple[str, ...]
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            not self.values
            or len(self.values) != len(self.output_names)
            or any(len(row) != len(self.input_names) for row in self.values)
            or not self.input_names
            or not self.output_names
            or not self.provenance
        ):
            raise ValueError("sensitivity matrices require named rectangular data")


@dataclass(frozen=True, slots=True)
class PrincipalUncertaintyDirection:
    """One eigen-direction of a covariance matrix."""

    variance: float
    direction: tuple[float, ...]
    provenance: tuple[str, ...]


def principal_uncertainty_directions(
    covariance: CovarianceMatrix,
) -> tuple[PrincipalUncertaintyDirection, ...]:
    """Return deterministic principal covariance directions in descending variance."""

    values, vectors = _hermitian_eigensystem(
        ComplexMatrix(covariance.values), 1e-12
    )
    return tuple(
        PrincipalUncertaintyDirection(
            max(0.0, value),
            tuple(vectors[row][index].real for row in range(vectors.row_count)),
            (*covariance.sources, "principal covariance direction"),
        )
        for index, value in enumerate(values)
        if value > 1e-12
    )


@dataclass(frozen=True, slots=True)
class UncertainValue:
    """A value with separately retained uncertainty categories."""

    value: tuple[float, ...]
    covariance: CovarianceMatrix
    components: tuple[UncertaintyComponent, ...]
    context: PhysicalEvaluationContext

    def __post_init__(self) -> None:
        if len(self.value) != len(self.covariance.values):
            raise ValueError("uncertain values and covariance dimensions do not agree")
        if not self.components:
            raise ValueError("uncertain values require separately classified components")

    @property
    def standard_deviations(self) -> tuple[float, ...]:
        """Return marginal standard deviations."""

        return tuple(
            sqrt(max(0.0, self.covariance.values[index][index])) for index in range(len(self.value))
        )


def finite_difference_jacobian(
    function: Callable[[tuple[float, ...]], tuple[float, ...]],
    point: Sequence[float],
    step: float = 1e-6,
) -> tuple[tuple[float, ...], ...]:
    """Compute a central finite-difference Jacobian for numerical checking."""

    if step <= 0:
        raise ValueError("finite-difference steps must be positive")
    base = tuple(float(value) for value in point)
    output = function(base)
    columns: list[tuple[float, ...]] = []
    for column in range(len(base)):
        plus = list(base)
        minus = list(base)
        plus[column] += step
        minus[column] -= step
        columns.append(
            tuple(
                (left - right) / (2 * step)
                for left, right in zip(function(tuple(plus)), function(tuple(minus)), strict=True)
            )
        )
    return tuple(
        tuple(columns[column][row] for column in range(len(columns))) for row in range(len(output))
    )


def propagate_covariance(
    jacobian: Sequence[Sequence[float]], covariance: CovarianceMatrix
) -> CovarianceMatrix:
    """Propagate a PSD input covariance through an explicit Jacobian."""

    j = ComplexMatrix(jacobian)
    c = ComplexMatrix(covariance.values)
    result = j @ c @ j.conjugate_transpose()
    return CovarianceMatrix(
        tuple(tuple(value.real for value in row) for row in result.rows), covariance.sources
    )


class PredictionRole(StrEnum):
    """Immutable roles in the prediction and comparison firewall."""

    DERIVED = "DERIVED"
    DISCRETE_SELECTION = "DISCRETE_SELECTION"
    FITTED = "FITTED"
    CALIBRATION = "CALIBRATION"
    HELD_OUT_PREDICTION = "HELD_OUT_PREDICTION"
    TERMINAL_COMPARISON = "TERMINAL_COMPARISON"


@dataclass(frozen=True, slots=True)
class DataManifest:
    """A frozen data manifest identified by digest and cutoff."""

    identifier: str
    digest: str
    cutoff: str

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.identifier, self.digest, self.cutoff)):
            raise ValueError("data manifests require identifier, digest, and cutoff")


@dataclass(frozen=True, slots=True)
class SelectionRecord:
    """One model, branch, geometry, or fit selection with leakage status."""

    name: str
    value: str
    influenced_upstream: bool
    provenance: str

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.name, self.value, self.provenance)):
            raise ValueError("selection records require complete provenance")


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    """An uncertainty-aware comparison at one matching context."""

    predicted: tuple[float, ...]
    observed: tuple[float, ...]
    covariance: CovarianceMatrix
    chi_squared: float
    passed: bool
    consequence: str
    provenance: tuple[str, ...]
    context: PhysicalEvaluationContext | None = None


class FalsificationScope(StrEnum):
    """Scientific scope of a failed held-out comparison."""

    NUMERICAL_SOLUTION = "one numerical solution"
    VACUUM = "one vacuum"
    BRANCH = "one branch"
    CARRIER = "the carrier"
    UNIVERSAL_LAW = "a universal law"


@dataclass(frozen=True, slots=True)
class FalsificationReport:
    """A scoped consequence for one preregistered comparison."""

    comparison: ComparisonResult
    scope: FalsificationScope
    falsifies: bool
    provenance: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PredictionRecord:
    """A frozen prediction record with selection-leakage protection."""

    role: PredictionRole
    observable: str
    context: PhysicalEvaluationContext
    model_digest: str
    vacuum_digest: str
    selections: tuple[SelectionRecord, ...]
    fitted_quantities: tuple[str, ...]
    data_manifest: DataManifest
    predicted_value: UncertainValue
    comparison_procedure: str
    pass_fail_criterion: str
    evidence_digests: tuple[str, ...]
    software_digest: str
    comparison: ComparisonResult | None = None
    observable_influenced_upstream: bool = False
    correlated_data_influenced_upstream: bool = False

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (
                self.observable,
                self.model_digest,
                self.vacuum_digest,
                self.comparison_procedure,
                self.pass_fail_criterion,
                self.software_digest,
            )
        ):
            raise ValueError("prediction records require complete frozen metadata")
        self.context.assert_compatible(self.predicted_value.context)
        if not self.evidence_digests or any(not item.strip() for item in self.evidence_digests):
            raise ValueError("prediction records require evidence digests")
        if self.role is PredictionRole.HELD_OUT_PREDICTION and (
            any(item.influenced_upstream for item in self.selections)
            or self.observable_influenced_upstream
            or self.correlated_data_influenced_upstream
        ):
            raise ValueError("held-out predictions cannot use data-influenced upstream selections")


@dataclass(frozen=True, slots=True)
class PredictionRegistry:
    """An immutable registry that rejects duplicate or leaked held-out records."""

    records: tuple[PredictionRecord, ...] = ()
    frozen: bool = False

    def register(self, record: PredictionRecord) -> PredictionRegistry:
        """Return a new registry containing one lawful record."""

        if self.frozen:
            raise ValueError("prediction registry is frozen")
        if any(
            item.observable == record.observable and item.role is record.role
            for item in self.records
        ):
            raise ValueError("prediction registry already contains this role and observable")
        return PredictionRegistry((*self.records, record), False)

    def freeze(self) -> PredictionRegistry:
        """Return an immutable frozen registry."""

        return PredictionRegistry(self.records, True)

    def held_out(self) -> tuple[PredictionRecord, ...]:
        """Return only records protected as held-out predictions."""

        return tuple(
            item for item in self.records if item.role is PredictionRole.HELD_OUT_PREDICTION
        )


def compare_with_data(
    predicted: UncertainValue,
    observed: Sequence[float],
    experimental_covariance: CovarianceMatrix,
    criterion: float,
    consequence: str,
    provenance: Iterable[str],
    observation_context: PhysicalEvaluationContext | None = None,
) -> ComparisonResult:
    """Compare predictions through combined theoretical and experimental covariance."""

    if len(predicted.value) != len(observed):
        raise ValueError("prediction and observation dimensions do not agree")
    if observation_context is not None:
        predicted.context.assert_compatible(observation_context)
    covariance = predicted.covariance.combine(experimental_covariance)
    difference = tuple(
        value - other for value, other in zip(predicted.value, observed, strict=True)
    )
    inverse = _matrix_inverse(
        tuple(tuple(complex(value) for value in row) for row in covariance.values)
    )
    chi_squared = sum(
        difference[row] * inverse[row][column].real * difference[column]
        for row in range(len(difference))
        for column in range(len(difference))
    )
    return ComparisonResult(
        tuple(predicted.value),
        tuple(float(value) for value in observed),
        covariance,
        chi_squared,
        chi_squared <= criterion,
        consequence,
        tuple(provenance),
        predicted.context,
    )


def falsification_report(
    comparison: ComparisonResult,
    scope: FalsificationScope,
    provenance: Iterable[str],
) -> FalsificationReport:
    """Attach an explicit scientific scope to a failed comparison."""

    return FalsificationReport(
        comparison,
        scope,
        not comparison.passed,
        (*comparison.provenance, *tuple(provenance)),
    )


__all__ = [
    "AsymmetricUncertainty",
    "BoundedUncertainty",
    "CanonicalTransformation",
    "ComparisonResult",
    "ConfidenceMetadata",
    "ComplexMatrix",
    "ContextBoundArray",
    "CovarianceMatrix",
    "DataManifest",
    "DiracNeutrinoMatrix",
    "EffectiveTheory",
    "FalsificationScope",
    "FalsificationReport",
    "FlavorObservables",
    "HermitianMatrix",
    "HermitianMetric",
    "HolomorphicYukawa",
    "MajoranaMatrix",
    "MixingMatrix",
    "MatchingCondition",
    "MatchingReport",
    "MonteCarloConfig",
    "MonteCarloResult",
    "NeutrinoObservables",
    "OperatorBasis",
    "PhysicalEvaluationContext",
    "PhysicalMatrix",
    "PhysicalYukawa",
    "PredictionRecord",
    "PredictionRegistry",
    "PredictionRole",
    "RGETheory",
    "RGEResult",
    "RGState",
    "SelectionRecord",
    "SensitivityMatrix",
    "SeesawResult",
    "SingularValueDecomposition",
    "UncertainValue",
    "UncertaintyComponent",
    "canonicalize_yukawa",
    "compare_with_data",
    "finite_difference_jacobian",
    "falsification_report",
    "jarlskog_invariant",
    "mixing_matrix",
    "ordered_masses",
    "neutrino_observables",
    "principal_uncertainty_directions",
    "propagate_covariance",
    "match_threshold",
    "monte_carlo_propagate",
    "run_rge",
    "singular_value_decomposition",
    "standard_model_one_loop_beta",
    "type_i_seesaw",
]
