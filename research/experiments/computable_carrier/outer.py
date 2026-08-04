"""Construct and certify the split rank-four transition baseline.

Owns:
    Exact block-upper-triangular transitions from two Tier A constituent
    cocycles, their mapping-style cocycle identity, determinant-one structure,
    and an explicit split-gauge witness.

Depends on:
    Tier A local candidate data and generic exact Laurent matrices only.

Must not:
    Present a split coboundary as a non-split physical extension, infer stable
    SU(4) structure, or claim the published bundle’s outer class.

Phase 0:
    The exact split baseline is constructed to exclude hidden fallbacks; a
    non-split invariant outer class still requires its own derived cocycle.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.sheaves import LaurentMatrix, LaurentPolynomial

from .constituents import SerreConstituentCandidate, tier_a_constituents


def _matrix_sub(left: LaurentMatrix, right: LaurentMatrix) -> LaurentMatrix:
    """Subtract two same-shaped exact Laurent matrices."""

    if left.shape != right.shape:
        raise ValueError("Laurent matrices have incompatible shapes")
    return LaurentMatrix(
        tuple(
            tuple(left.rows[row][column] - right.rows[row][column]
                  for column in range(left.shape[1]))
            for row in range(left.shape[0])
        )
    )


def _scalar_identity(scalar: LaurentPolynomial) -> LaurentMatrix:
    """Embed one scalar as a two-by-two scalar matrix."""

    zero = LaurentPolynomial.zero(scalar.variable_count, scalar_type=scalar.scalar_type)
    return LaurentMatrix(((scalar, zero), (zero, scalar)))


def _block_upper(
    upper_left: LaurentMatrix,
    upper_right: LaurentMatrix,
    lower_right: LaurentMatrix,
) -> LaurentMatrix:
    """Assemble a two-by-two block-upper-triangular matrix."""

    zero = LaurentPolynomial.zero(
        upper_left.rows[0][0].variable_count,
        scalar_type=upper_left.rows[0][0].scalar_type,
    )
    lower_left = LaurentMatrix(tuple(
        tuple(zero for _ in range(lower_right.shape[1]))
        for _ in range(lower_right.shape[0])
    ))
    return LaurentMatrix(
        tuple(
            tuple(upper_left.rows[row][column] for column in range(upper_left.shape[1]))
            + tuple(upper_right.rows[row][column] for column in range(upper_right.shape[1]))
            for row in range(upper_left.shape[0])
        )
        + tuple(
            tuple(lower_left.rows[row][column] for column in range(lower_left.shape[1]))
            + tuple(lower_right.rows[row][column] for column in range(lower_right.shape[1]))
            for row in range(lower_right.shape[0])
        )
    )


@dataclass(frozen=True, slots=True)
class SplitRankFourTransitionCandidate:
    """A fully explicit but intentionally excluded split rank-four baseline."""

    left: SerreConstituentCandidate
    right: SerreConstituentCandidate
    transitions: tuple[tuple[int, int, LaurentMatrix], ...]
    extension_status: str

    @property
    def rank(self) -> int:
        """Return the rank of the block transition system."""

        return 4

    @property
    def determinant_one(self) -> bool:
        """Return the exact determinant-one block certificate."""

        return self.left.determinant_one and self.right.determinant_one

    @property
    def verifies_cocycle(self) -> bool:
        """Check every ordered triple of four-by-four transitions."""

        count = len(self.left.cover.charts)
        values = {(left, right): matrix for left, right, matrix in self.transitions}
        return all(
            values[(left, right)] == values[(left, middle)].compose(values[(middle, right)])
            for left in range(count)
            for middle in range(count)
            for right in range(count)
            if len({left, middle, right}) == 3
        )

    @property
    def split_gauge_witness(self) -> bool:
        """Return whether the stored local potentials explicitly split it."""

        return self.extension_status.startswith("split coboundary")

    def as_record(self) -> dict[str, object]:
        """Return exact rank-four transition metadata and exclusion status."""

        return {
            "rank": self.rank,
            "left_scheme": self.left.scheme.name,
            "right_scheme": self.right.scheme.name,
            "cocycle": self.verifies_cocycle,
            "determinant_one": self.determinant_one,
            "split_gauge_witness": self.split_gauge_witness,
            "extension_status": self.extension_status,
            "transition_shapes": [
                [left, right, list(matrix.shape)]
                for left, right, matrix in self.transitions
            ],
        }


def split_rank_four_baseline(
    constituents: tuple[SerreConstituentCandidate, SerreConstituentCandidate] | None = None,
) -> SplitRankFourTransitionCandidate:
    """Build the exact block-upper-triangular split baseline."""

    left, right = tier_a_constituents() if constituents is None else constituents
    if left.cover != right.cover:
        raise ValueError("rank-four constituents require one common chart cover")
    transitions: list[tuple[int, int, LaurentMatrix]] = []
    for chart_left in range(len(left.cover.charts)):
        for chart_right in range(len(left.cover.charts)):
            if chart_left == chart_right:
                continue
            left_transition = left._transition(chart_left, chart_right)
            right_transition = right._transition(chart_left, chart_right)
            left_potential = _scalar_identity(
                left.local_potentials[chart_left] + right.local_potentials[chart_left]
            )
            right_potential = _scalar_identity(
                left.local_potentials[chart_right] + right.local_potentials[chart_right]
            )
            upper_right = _matrix_sub(
                left_potential.compose(right_transition),
                left_transition.compose(right_potential),
            )
            transitions.append(
                (
                    chart_left,
                    chart_right,
                    _block_upper(left_transition, upper_right, right_transition),
                )
            )
    return SplitRankFourTransitionCandidate(
        left,
        right,
        tuple(transitions),
        "split coboundary generated from explicit local gauge potentials; excluded",
    )


__all__ = ["SplitRankFourTransitionCandidate", "split_rank_four_baseline"]
