"""Construct bounded rank-four transition extensions from Hom cocycles.

Owns:
    Exact block-upper-triangular rank-four transition candidates obtained from
    bounded degree-one Hom Čech representatives, including cocycle, inverse,
    determinant, and bounded non-boundary certificates.

Depends on:
    Tier A constituent transitions, the bounded exact Hom Čech complex, and
    Laurent-polynomial matrix arithmetic. The coefficient window is explicit.

Must not:
    Call a bounded non-boundary class a global Ext class, infer equivariant
    descent, claim stability or local freeness beyond the transition checks, or
    hide an unconstructed polynomial horseshoe or mapping cone.

Phase 0:
    The bounded rank-four transition frontier is executable; global Ext,
    equivariance, local-freeness, stability, and promotion remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.homological import CoordinateVector
from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.sheaves import LaurentMatrix, LaurentPolynomial

from .hom_cech import BoundedHomCech, tier_a_hom_cech

TransitionRecord = tuple[int, int, LaurentMatrix]
HomBasis = tuple[int, int, tuple[int, ...]]


def _zero(variable_count: int) -> LaurentPolynomial:
    """Return the exact zero coefficient in the Hom localization."""

    return LaurentPolynomial.zero(variable_count, scalar_type=Eisenstein)


def _matrix_from_coordinates(
    coordinates: tuple[object, ...],
    basis: tuple[HomBasis, ...],
    variable_count: int,
) -> LaurentMatrix:
    """Convert one based Hom cochain block into an exact Laurent matrix."""

    if len(coordinates) != len(basis):
        raise ValueError("Hom coordinates do not match their simplex basis")
    entries = [
        [_zero(variable_count), _zero(variable_count)],
        [_zero(variable_count), _zero(variable_count)],
    ]
    for coefficient, (row, column, exponents) in zip(coordinates, basis, strict=True):
        monomial = LaurentPolynomial.monomial(
            exponents,
            coefficient,
            scalar_type=Eisenstein,
        )
        entries[row][column] = entries[row][column] + monomial
    return LaurentMatrix(tuple(tuple(entry for entry in row) for row in entries))


def _cochain_blocks(
    hom: BoundedHomCech,
    representative: CoordinateVector,
) -> tuple[tuple[tuple[int, ...], LaurentMatrix], ...]:
    """Split one degree-one vector into its ordered pairwise matrix blocks."""

    if representative.space != hom.complex.spaces.space(1):
        raise ValueError("the representative does not belong to Hom Cech degree one")
    blocks: list[tuple[tuple[int, ...], LaurentMatrix]] = []
    offset = 0
    variable_count = hom.left.cover.charts[0].variable_count
    for simplex, basis in hom.basis_by_simplex(1):
        end = offset + len(basis)
        blocks.append((
            simplex,
            _matrix_from_coordinates(
                representative.coordinates[offset:end],
                basis,
                variable_count,
            ),
        ))
        offset = end
    if offset != len(representative.coordinates):
        raise ValueError("Hom simplex bases do not span the degree-one space")
    return tuple(blocks)


def _block_upper(
    left: LaurentMatrix,
    upper: LaurentMatrix,
    right: LaurentMatrix,
) -> LaurentMatrix:
    """Assemble a two-by-two block-upper rank-four transition."""

    zero = LaurentPolynomial.zero(
        left.rows[0][0].variable_count,
        scalar_type=left.rows[0][0].scalar_type,
    )
    lower_left = tuple(
        tuple(zero for _ in range(right.shape[1]))
        for _ in range(right.shape[0])
    )
    return LaurentMatrix(
        tuple(
            tuple(left.rows[row][column] for column in range(left.shape[1]))
            + tuple(upper.rows[row][column] for column in range(upper.shape[1]))
            for row in range(left.shape[0])
        )
        + tuple(
            tuple(lower_left[row][column] for column in range(right.shape[1]))
            + tuple(right.rows[row][column] for column in range(right.shape[1]))
            for row in range(right.shape[0])
        )
    )


def _block_inverse(
    left: LaurentMatrix,
    upper: LaurentMatrix,
    right: LaurentMatrix,
    left_inverse: LaurentMatrix,
    right_inverse: LaurentMatrix,
) -> LaurentMatrix:
    """Return the exact inverse of one block-upper transition."""

    product = left_inverse.compose(upper).compose(right_inverse)
    inverse_upper = LaurentMatrix(
        tuple(tuple(-entry for entry in row) for row in product.rows)
    )
    return _block_upper(left_inverse, inverse_upper, right_inverse)


def _vector_rank(vectors: tuple[CoordinateVector, ...], dimension: int) -> int:
    """Return the exact rank of vectors in their common ordered basis."""

    if not vectors or dimension == 0:
        return 0
    return Matrix(
        tuple(tuple(vector.coordinates[index] for vector in vectors)
              for index in range(dimension)),
        scalar_type=Eisenstein,
    ).rank()


def _is_bounded_nonboundary(hom: BoundedHomCech, vector: CoordinateVector) -> bool:
    """Check that a representative increases the exact bounded boundary rank."""

    boundaries = hom.complex.boundaries(1)
    before = _vector_rank(boundaries, hom.complex.spaces.space(1).dimension)
    after = _vector_rank((*boundaries, vector), hom.complex.spaces.space(1).dimension)
    return after > before


@dataclass(frozen=True, slots=True)
class RankFourExtensionCandidate:
    """One bounded rank-four transition extension with exact certificates."""

    hom: BoundedHomCech
    representative_index: int
    representative: CoordinateVector
    transitions: tuple[TransitionRecord, ...]
    bounded_nonboundary: bool

    def __post_init__(self) -> None:
        if self.representative_index < 0:
            raise ValueError("rank-four representative indices must be nonnegative")
        if self.representative.space != self.hom.complex.spaces.space(1):
            raise ValueError("rank-four representatives require Hom Cech degree one")

    @property
    def rank(self) -> int:
        """Return the rank of the block transition system."""

        return 4

    def transition(self, left: int, right: int) -> LaurentMatrix:
        """Return one ordered rank-four transition."""

        for source, target, matrix in self.transitions:
            if (source, target) == (left, right):
                return matrix
        raise KeyError((left, right))

    @property
    def verifies_cocycle(self) -> bool:
        """Check the full ordered transition cocycle identity exactly."""

        count = len(self.hom.left.cover.charts)
        return all(
            self.transition(left, right) == self.transition(left, middle).compose(
                self.transition(middle, right)
            )
            for left in range(count)
            for middle in range(count)
            for right in range(count)
            if len({left, middle, right}) == 3
        )

    @property
    def pairwise_inverse(self) -> bool:
        """Check exact local invertibility on every ordered chart pair."""

        count = len(self.hom.left.cover.charts)
        return all(
            self.transition(left, right).compose(self.transition(right, left)).is_identity()
            for left in range(count)
            for right in range(count)
            if left != right
        )

    @property
    def determinant_one(self) -> bool:
        """Return the block-triangular determinant-one certificate."""

        return (
            all(matrix.shape == (4, 4) for _, _, matrix in self.transitions)
            and self.hom.left.determinant_one
            and self.hom.right.determinant_one
        )

    @property
    def local_freeness_on_cover(self) -> bool:
        """Return the exact transition-level local-freeness condition."""

        return self.pairwise_inverse

    def as_record(self) -> dict[str, object]:
        """Return exact checks without claiming a global bundle."""

        return {
            "representative_index": self.representative_index,
            "rank": self.rank,
            "transition_count": len(self.transitions),
            "transition_shapes": [
                [left, right, list(matrix.shape)]
                for left, right, matrix in self.transitions
            ],
            "cocycle": self.verifies_cocycle,
            "pairwise_inverse": self.pairwise_inverse,
            "determinant_one": self.determinant_one,
            "local_freeness_on_cover": self.local_freeness_on_cover,
            "bounded_nonboundary": self.bounded_nonboundary,
            "status": (
                "bounded transition extension; global Ext and descent remain unresolved"
            ),
        }


@dataclass(frozen=True, slots=True)
class RankFourFrontier:
    """The complete bounded rank-four representative frontier."""

    hom: BoundedHomCech
    candidates: tuple[RankFourExtensionCandidate, ...]
    mapping_cone_constructed: bool

    def __post_init__(self) -> None:
        if self.mapping_cone_constructed:
            raise ValueError("the bounded transition frontier cannot claim a mapping cone")

    @property
    def all_cocycles(self) -> bool:
        """Return whether every bounded representative gives a cocycle."""

        return all(candidate.verifies_cocycle for candidate in self.candidates)

    @property
    def all_locally_free(self) -> bool:
        """Return whether every transition candidate is locally invertible."""

        return all(candidate.local_freeness_on_cover for candidate in self.candidates)

    def as_record(self) -> dict[str, object]:
        """Return the complete bounded rank-four construction record."""

        return {
            "candidate_count": len(self.candidates),
            "h1_dimension": self.hom.h1_dimension,
            "all_cocycles": self.all_cocycles,
            "all_locally_free_on_cover": self.all_locally_free,
            "candidates": [candidate.as_record() for candidate in self.candidates],
            "selected_candidate": None,
            "mapping_cone": {
                "constructed": self.mapping_cone_constructed,
                "status": (
                    "no polynomial horseshoe or mapping cone has been derived from "
                    "the bounded Laurent representative"
                ),
            },
            "status": (
                "bounded rank-four transition frontier; no global carrier selected"
            ),
        }


def _candidate_from_representative(
    hom: BoundedHomCech,
    index: int,
    representative: CoordinateVector,
) -> RankFourExtensionCandidate:
    """Build one block transition system from a bounded Hom representative."""

    blocks = dict(_cochain_blocks(hom, representative))
    transitions: list[TransitionRecord] = []
    count = len(hom.left.cover.charts)
    for left in range(count):
        for right in range(left + 1, count):
            upper = blocks[(left, right)].compose(hom.right._transition(left, right))
            forward = _block_upper(
                hom.left._transition(left, right),
                upper,
                hom.right._transition(left, right),
            )
            reverse = _block_inverse(
                hom.left._transition(left, right),
                upper,
                hom.right._transition(left, right),
                hom.left._transition(right, left),
                hom.right._transition(right, left),
            )
            transitions.extend(((left, right, forward), (right, left, reverse)))
    return RankFourExtensionCandidate(
        hom,
        index,
        representative,
        tuple(transitions),
        _is_bounded_nonboundary(hom, representative),
    )


def rank_four_frontier(
    hom: BoundedHomCech | None = None,
) -> RankFourFrontier:
    """Construct all bounded rank-four transition representatives."""

    bounded_hom = tier_a_hom_cech() if hom is None else hom
    candidates = tuple(
        _candidate_from_representative(bounded_hom, index, representative)
        for index, representative in enumerate(bounded_hom.h1_representatives)
    )
    return RankFourFrontier(bounded_hom, candidates, False)


def tier_a_rank_four_frontier() -> RankFourFrontier:
    """Construct the bounded rank-four frontier for Tier A."""

    return rank_four_frontier()


__all__ = [
    "RankFourExtensionCandidate",
    "RankFourFrontier",
    "rank_four_frontier",
    "tier_a_rank_four_frontier",
]
