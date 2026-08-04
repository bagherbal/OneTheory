"""Build a bounded exact Čech Hom complex from constituent transitions.

Owns:
    Matrix-valued localized sections of ``Hom(V2,V1)``, exact transition
    conjugation, bounded cochain bases closed under the displayed maps, and
    cycle/boundary representatives computed by the generic homological engine.

Depends on:
    Tier A transition candidates, exact Laurent matrices, and finite exact
    vector-space complexes. The coefficient window is explicit and finite.

Must not:
    Call a bounded complex the full geometric Ext complex, infer invariant
    classes from a target dimension, or fabricate a deck action.

Phase 0:
    The bounded Hom Čech complex is executable; full cover certification,
    convergence, equivariance, and promotion remain open gates.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from itertools import combinations

from onetheory.math.homological import CochainComplex, GradedVectorSpace, LinearMap, VectorSpace
from onetheory.math.numbers import Eisenstein
from onetheory.math.sheaves import LaurentMatrix, LaurentPolynomial

from .constituents import SerreConstituentCandidate, tier_a_constituents

HomBasis = tuple[int, int, tuple[int, ...]]
Simplex = tuple[int, ...]
SimplexBasisRecords = tuple[tuple[Simplex, tuple[HomBasis, ...]], ...]
MatrixTransform = Callable[[LaurentMatrix], LaurentMatrix]


def _identity_transform(matrix: LaurentMatrix) -> LaurentMatrix:
    """Return one matrix without changing its local frame."""

    return matrix


def _zero_matrix(variable_count: int, scalar_type: type[Eisenstein]) -> LaurentMatrix:
    """Return an exact two-by-two zero matrix."""

    zero = LaurentPolynomial.zero(variable_count, scalar_type=scalar_type)
    return LaurentMatrix(((zero, zero), (zero, zero)))


def _matrix_add(left: LaurentMatrix, right: LaurentMatrix) -> LaurentMatrix:
    """Add same-shaped exact Laurent matrices."""

    return LaurentMatrix(
        tuple(
            tuple(left.rows[row][column] + right.rows[row][column]
                  for column in range(left.shape[1]))
            for row in range(left.shape[0])
        )
    )


def _matrix_scale_sign(matrix: LaurentMatrix, sign: int) -> LaurentMatrix:
    """Apply one Čech sign to an exact Laurent matrix."""

    if sign not in (-1, 1):
        raise ValueError("Čech signs must be plus or minus one")
    return matrix if sign == 1 else LaurentMatrix(
        tuple(
            tuple(-entry for entry in row)
            for row in matrix.rows
        )
    )


def _basis_matrix(
    basis: HomBasis,
    variable_count: int,
    scalar_type: type[Eisenstein],
) -> LaurentMatrix:
    """Return one matrix-valued monomial basis element."""

    row, column, exponents = basis
    zero = LaurentPolynomial.zero(variable_count, scalar_type=scalar_type)
    one = LaurentPolynomial.monomial(exponents, scalar_type=scalar_type)
    values = [[zero, zero], [zero, zero]]
    values[row][column] = one
    return LaurentMatrix(tuple(tuple(value for value in row_values) for row_values in values))


def _matrix_terms(matrix: LaurentMatrix) -> tuple[HomBasis, ...]:
    """Return all nonzero matrix monomials in deterministic order."""

    return tuple(
        (row, column, exponents)
        for row in range(matrix.shape[0])
        for column in range(matrix.shape[1])
        for exponents, coefficient in matrix.rows[row][column].terms
        if not coefficient.is_zero()
    )


def _map_from_faces(
    source_records: tuple[tuple[tuple[int, ...], tuple[HomBasis, ...]], ...],
    target_records: tuple[tuple[tuple[int, ...], tuple[HomBasis, ...]], ...],
    faces: tuple[tuple[tuple[int, ...], tuple[int, ...], int, MatrixTransform], ...],
    variable_count: int,
    source_space: VectorSpace,
    target_space: VectorSpace,
) -> LinearMap:
    """Assemble one exact map from signed matrix-valued face restrictions."""

    source_offsets: dict[tuple[int, ...], int] = {}
    offset = 0
    for simplex, basis in source_records:
        source_offsets[simplex] = offset
        offset += len(basis)
    target_offsets: dict[tuple[int, ...], int] = {}
    offset = 0
    for simplex, basis in target_records:
        target_offsets[simplex] = offset
        offset += len(basis)
    rows = [[Eisenstein(0) for _ in range(source_space.dimension)]
            for _ in range(target_space.dimension)]
    for target_simplex, source_simplex, sign, transform in faces:
        source_basis = dict(source_records)[source_simplex]
        target_basis = dict(target_records)[target_simplex]
        local_target_index = {basis: index for index, basis in enumerate(target_basis)}
        for source_index, basis in enumerate(source_basis):
            image = _matrix_scale_sign(
                transform(_basis_matrix(basis, variable_count, Eisenstein)),
                sign,
            )
            for row, column, exponents in _matrix_terms(image):
                local_index = local_target_index.get((row, column, exponents))
                if local_index is None:
                    raise ValueError("restriction image escaped the closed coefficient basis")
                coefficient = image.rows[row][column].coefficient(exponents)
                rows[
                    target_offsets[target_simplex] + local_index
                ][source_offsets[source_simplex] + source_index] += coefficient
    return LinearMap(source_space, target_space, rows)


@dataclass(frozen=True, slots=True)
class BoundedHomCech:
    """A bounded exact Hom Čech complex with explicit basis metadata."""

    left: SerreConstituentCandidate
    right: SerreConstituentCandidate
    bound: int
    complex: CochainComplex
    bases: tuple[tuple[int, tuple[HomBasis, ...]], ...]
    simplex_bases: tuple[tuple[int, SimplexBasisRecords], ...]
    status: str

    def __post_init__(self) -> None:
        if self.left.cover != self.right.cover:
            raise ValueError("Hom Čech candidates require one common chart cover")
        if isinstance(self.bound, bool) or not isinstance(self.bound, int) or self.bound < 0:
            raise ValueError("Hom Čech bounds must be nonnegative integers")

    def basis(self, degree: int) -> tuple[HomBasis, ...]:
        """Return the ordered matrix-monomial basis in one degree."""

        return dict(self.bases)[degree]

    def basis_by_simplex(self, degree: int) -> SimplexBasisRecords:
        """Return the ordered local basis grouped by its Čech simplex."""

        return dict(self.simplex_bases)[degree]

    @property
    def h1_dimension(self) -> int:
        """Return the exact bounded first cohomology dimension."""

        return self.complex.cohomology_dimension(1)

    @property
    def h1_representatives(self):
        """Return exact bounded first-cohomology representatives."""

        return self.complex.cohomology_representatives(1)

    def as_record(self) -> dict[str, object]:
        """Return basis, dimensions, and explicit truncation status."""

        return {
            "left_scheme": self.left.scheme.name,
            "right_scheme": self.right.scheme.name,
            "bound": self.bound,
            "basis_sizes": [[degree, len(basis)] for degree, basis in self.bases],
            "simplex_basis_sizes": [
                [degree, list(simplex), len(basis)]
                for degree, records in self.simplex_bases
                for simplex, basis in records
            ],
            "cohomology_dimensions": [
                [degree, self.complex.cohomology_dimension(degree)]
                for degree in self.complex.degrees
            ],
            "h1_representative_count": len(self.h1_representatives),
            "squared_zero": all(
                self.complex.differential(degree + 1).compose(
                    self.complex.differential(degree)
                ).is_zero()
                for degree in (0, 1)
            ),
            "status": self.status,
        }


def _conjugation(
    left: SerreConstituentCandidate,
    right: SerreConstituentCandidate,
    source: int,
    target: int,
) -> MatrixTransform:
    """Return ``H -> g_left H g_right^{-1}`` between chart frames."""

    left_transition = left._transition(source, target)
    right_inverse = right._transition(target, source)
    return lambda matrix: left_transition.compose(matrix).compose(right_inverse)


def bounded_hom_cech(
    left: SerreConstituentCandidate,
    right: SerreConstituentCandidate,
    bound: int = 0,
) -> BoundedHomCech:
    """Construct the closed finite Hom Čech complex from two transitions."""

    if left.cover != right.cover:
        raise ValueError("Hom Čech candidates require one common chart cover")
    if isinstance(bound, bool) or not isinstance(bound, int) or bound < 0:
        raise ValueError("Hom Čech bounds must be nonnegative integers")
    chart_count = len(left.cover.charts)
    variable_count = left.cover.charts[0].variable_count
    zero_exponents = (0,) * variable_count
    degree_zero = {
        (index,): tuple(
            (row, column, zero_exponents)
            for row in range(2)
            for column in range(2)
        )
        for index in range(chart_count)
    }
    bases: dict[int, dict[tuple[int, ...], tuple[HomBasis, ...]]] = {0: degree_zero}
    pairs = tuple(combinations(range(chart_count), 2))
    for pair in pairs:
        pair_basis: set[HomBasis] = set()
        for vertex in pair:
            transform = (
                _identity_transform
                if vertex == pair[0]
                else _conjugation(left, right, pair[0], vertex)
            )
            for basis in degree_zero[(vertex,)]:
                pair_basis.update(
                    _matrix_terms(transform(_basis_matrix(basis, variable_count, Eisenstein)))
                )
        bases.setdefault(1, {})[pair] = tuple(sorted(pair_basis))
    triples = tuple(combinations(range(chart_count), 3))
    for triple in triples:
        triple_basis: set[HomBasis] = set()
        for pair in combinations(triple, 2):
            transform = (
                _identity_transform
                if pair[0] == triple[0]
                else _conjugation(left, right, triple[0], pair[0])
            )
            for basis in bases[1][pair]:
                triple_basis.update(
                    _matrix_terms(transform(_basis_matrix(basis, variable_count, Eisenstein)))
                )
        bases.setdefault(2, {})[triple] = tuple(sorted(triple_basis))
    ordered_bases = {
        degree: tuple(sorted(values.items())) for degree, values in bases.items()
    }
    spaces = {
        degree: VectorSpace(
            f"Hom Cech^{degree}",
            tuple(
                f"{simplex}:{basis}"
                for simplex, basis_values in records
                for basis in basis_values
            ),
            Eisenstein,
        )
        for degree, records in ordered_bases.items()
    }
    graded = GradedVectorSpace("bounded Hom Cech", spaces)
    d0_faces = tuple(
        (pair, (pair[0],), -1, _identity_transform)
        for pair in pairs
    ) + tuple(
        (pair, (pair[1],), 1, _conjugation(left, right, pair[0], pair[1]))
        for pair in pairs
    )
    d1_faces = tuple(
        (
            triple,
            (triple[1], triple[2]),
            1,
            _conjugation(left, right, triple[0], triple[1]),
        )
        for triple in triples
    ) + tuple(
        (triple, (triple[0], triple[2]), -1, _identity_transform)
        for triple in triples
    ) + tuple(
        (triple, (triple[0], triple[1]), 1, _identity_transform)
        for triple in triples
    )
    d0 = _map_from_faces(
        ordered_bases[0],
        ordered_bases[1],
        d0_faces,
        variable_count,
        spaces[0],
        spaces[1],
    )
    d1 = _map_from_faces(
        ordered_bases[1],
        ordered_bases[2],
        d1_faces,
        variable_count,
        spaces[1],
        spaces[2],
    )
    complex_ = CochainComplex(graded, {0: d0, 1: d1})
    basis_records = tuple(
        (degree, tuple(basis for _, values in records for basis in values))
        for degree, records in sorted(ordered_bases.items())
    )
    simplex_basis_records = tuple(
        (degree, tuple(records))
        for degree, records in sorted(ordered_bases.items())
    )
    return BoundedHomCech(
        left,
        right,
        bound,
        complex_,
        basis_records,
        simplex_basis_records,
        "bounded Hom Cech complex; full Ext and equivariance remain unproved",
    )


def tier_a_hom_cech() -> BoundedHomCech:
    """Construct the first bounded Hom complex for Tier A."""

    left, right = tier_a_constituents()
    return bounded_hom_cech(left, right, 0)


__all__ = ["BoundedHomCech", "bounded_hom_cech", "tier_a_hom_cech"]
