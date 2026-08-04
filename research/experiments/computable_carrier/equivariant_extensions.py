"""Solve bounded rank-four equivariance equations exactly.

Owns:
    Finite affine linear searches for upper-block local gauge lifts of the
    rank-four transition candidates under the P and T coordinate generators.
    Every coefficient is solved over the exact Eisenstein field.

Depends on:
    Rank-four transition candidates, exact Laurent substitution and matrices,
    and deterministic Eisenstein RREF. The local gauge monomial bound is part
    of every returned record.

Must not:
    Guess a gauge matrix, infer a global linearization from solvability in one
    finite window, or treat a split diagnostic lift as a non-split extension.

Phase 0:
    Bounded affine equivariance searches are executable; completeness,
    group relations, global descent, and promotion remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from itertools import product

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from onetheory.math.sheaves import LaurentMatrix, LaurentPolynomial

from .equivariance import _derived_gauge_lift, _substitute_matrix
from .rank_four import RankFourExtensionCandidate, RankFourFrontier, tier_a_rank_four_frontier

Monomial = tuple[int, ...]


def _matrix_subtract(left: LaurentMatrix, right: LaurentMatrix) -> LaurentMatrix:
    """Subtract two same-shaped exact Laurent matrices."""

    return LaurentMatrix(
        tuple(
            tuple(left.rows[row][column] - right.rows[row][column]
                  for column in range(left.shape[1]))
            for row in range(left.shape[0])
        )
    )


def _block_upper(
    left: LaurentMatrix,
    upper: LaurentMatrix,
    right: LaurentMatrix,
) -> LaurentMatrix:
    """Assemble a four-by-four block-upper gauge matrix."""

    zero = LaurentPolynomial.zero(
        left.rows[0][0].variable_count,
        scalar_type=left.rows[0][0].scalar_type,
    )
    return LaurentMatrix(
        tuple(
            tuple(left.rows[row][column] for column in range(2))
            + tuple(upper.rows[row][column] for column in range(2))
            for row in range(2)
        )
        + tuple(
            tuple(zero for _ in range(2))
            + tuple(right.rows[row][column] for column in range(2))
            for row in range(2)
        )
    )


def _upper_block(matrix: LaurentMatrix) -> LaurentMatrix:
    """Extract the two-by-two upper-right block of a rank-four matrix."""

    return LaurentMatrix(
        tuple(
            tuple(matrix.rows[row][column] for column in range(2, 4))
            for row in range(2)
        )
    )


def _monomial_window(bound: int) -> tuple[Monomial, ...]:
    """Return the explicit nonnegative local gauge monomial window."""

    if isinstance(bound, bool) or not isinstance(bound, int) or bound < 0:
        raise ValueError("gauge bounds must be nonnegative integers")
    return tuple(
        exponent
        for exponent in product(range(bound + 1), repeat=3)
        if sum(exponent) <= bound
    )


def _unit_matrix(
    row: int,
    column: int,
    exponent: Monomial,
) -> LaurentMatrix:
    """Return one exact two-by-two monomial matrix basis element."""

    zero = LaurentPolynomial.zero(3, scalar_type=Eisenstein)
    one = LaurentPolynomial.monomial(exponent, scalar_type=Eisenstein)
    entries = [[zero, zero], [zero, zero]]
    entries[row][column] = one
    return LaurentMatrix(tuple(tuple(entry for entry in line) for line in entries))


def _matrix_scale_sign(matrix: LaurentMatrix, sign: int) -> LaurentMatrix:
    """Apply one exact sign to a Laurent matrix."""

    return matrix if sign == 1 else LaurentMatrix(
        tuple(tuple(-entry for entry in row) for row in matrix.rows)
    )


def _add_equation_matrix(
    rows: dict[tuple[int, int, int, int, Monomial], list[Eisenstein]],
    key_prefix: tuple[int, int],
    matrix: LaurentMatrix,
    column: int | None,
    sign: int,
    variable_count: int,
) -> None:
    """Add matrix coefficients to one deterministic linear system."""

    if variable_count != 3:
        raise ValueError("the bounded gauge solver requires three Cox variables")
    for row in range(2):
        for target_column in range(2):
            for exponent, coefficient in matrix.rows[row][target_column].terms:
                key = (*key_prefix, row, target_column, exponent)
                values = rows.setdefault(key, [])
                while len(values) <= (column if column is not None else -1):
                    values.append(Eisenstein(0))
                if column is not None:
                    values[column] += coefficient if sign == 1 else -coefficient


def _solve_affine(
    equations: dict[tuple[int, int, int, Monomial], list[Eisenstein]],
    unknown_count: int,
) -> tuple[bool, tuple[Eisenstein, ...], int, int]:
    """Solve an exact affine system and return solvability and one solution."""

    if not equations:
        return True, tuple(Eisenstein(0) for _ in range(unknown_count)), unknown_count, 0
    ordered_keys = sorted(equations)
    rows = []
    for key in ordered_keys:
        values = equations[key]
        coefficients = tuple(values[index] if index < len(values) else Eisenstein(0)
                            for index in range(unknown_count))
        constant = values[unknown_count] if len(values) > unknown_count else Eisenstein(0)
        rows.append(coefficients + (-constant,))
    augmented = Matrix(rows, scalar_type=Eisenstein)
    reduced, pivots = augmented.rref()
    if unknown_count in pivots:
        coefficient_rank = len(pivots) - 1
        return False, (), unknown_count - coefficient_rank, len(rows)
    coefficient_rank = len(pivots)
    solution = [Eisenstein(0) for _ in range(unknown_count)]
    for row, pivot in enumerate(pivots):
        if pivot < unknown_count:
            solution[pivot] = reduced.rows[row][-1]
    return True, tuple(solution), unknown_count - coefficient_rank, len(rows)


def _upper_solution(
    solution: tuple[Eisenstein, ...],
    monomials: tuple[Monomial, ...],
    chart: int,
) -> LaurentMatrix:
    """Convert one chart's affine solution coordinates into a two-by-two matrix."""

    entries = [
        [LaurentPolynomial.zero(3, scalar_type=Eisenstein) for _ in range(2)]
        for _ in range(2)
    ]
    for row in range(2):
        for column in range(2):
            start = ((chart * 4) + (row * 2) + column) * len(monomials)
            terms = tuple(
                (monomials[index], solution[start + index])
                for index in range(len(monomials))
                if not solution[start + index].is_zero()
            )
            entries[row][column] = LaurentPolynomial(
                terms,
                variable_count=3,
                scalar_type=Eisenstein,
            )
    return LaurentMatrix(tuple(tuple(entry for entry in row) for row in entries))


@dataclass(frozen=True, slots=True)
class BoundedGaugeLift:
    """One exact affine gauge-lift solve in a declared monomial window."""

    generator: str
    bound: int
    equation_count: int
    unknown_count: int
    solution_dimension: int
    solvable: bool
    transition_equations_verified: bool
    lifts: tuple[LaurentMatrix, ...]

    def as_record(self) -> dict[str, object]:
        """Return the bounded solve without suppressing its scope."""

        return {
            "generator": self.generator,
            "bound": self.bound,
            "equation_count": self.equation_count,
            "unknown_count": self.unknown_count,
            "solution_dimension": self.solution_dimension,
            "solvable": self.solvable,
            "transition_equations_verified": self.transition_equations_verified,
        }


@dataclass(frozen=True, slots=True)
class BoundedExtensionEquivariance:
    """Exact bounded gauge searches for one rank-four representative."""

    representative_index: int
    bound: int
    lifts: tuple[BoundedGaugeLift, ...]
    failed_group_relations: tuple[str, ...]

    @property
    def group_relations_verified(self) -> bool:
        """Return whether the selected bounded lifts obey all tested relations."""

        return not self.failed_group_relations

    def as_record(self) -> dict[str, object]:
        """Return bounded gauge and group-relation data."""

        return {
            "representative_index": self.representative_index,
            "bound": self.bound,
            "lifts": [lift.as_record() for lift in self.lifts],
            "failed_group_relations": list(self.failed_group_relations),
            "group_relations_verified": self.group_relations_verified,
            "status": "bounded affine lift search; completeness remains unproved",
        }


def _solve_generator(
    candidate: RankFourExtensionCandidate,
    generator: str,
    images: tuple[tuple[object, tuple[int, ...]], ...],
    permutation: tuple[int, int, int],
    bound: int,
) -> BoundedGaugeLift:
    """Solve the upper-block gauge equation for one coordinate generator."""

    monomials = _monomial_window(bound)
    unknown_count = 3 * 4 * len(monomials)
    equations: dict[tuple[int, int, int, int, Monomial], list[Eisenstein]] = {}
    left = candidate.hom.left
    right = candidate.hom.right
    left_lifts = tuple(_derived_gauge_lift(left, chart, images, permutation)
                       for chart in range(3))
    right_lifts = tuple(_derived_gauge_lift(right, chart, images, permutation)
                        for chart in range(3))
    for chart_left in range(3):
        for chart_right in range(chart_left + 1, 3):
            transition = candidate.transition(chart_left, chart_right)
            sigma_left = _substitute_matrix(
                left._transition(chart_left, chart_right), images
            )
            sigma_upper = _substitute_matrix(_upper_block(transition), images)
            target_upper = _upper_block(
                candidate.transition(
                    permutation[chart_left], permutation[chart_right]
                )
            )
            known = _matrix_subtract(
                sigma_upper.compose(right_lifts[chart_right]),
                left_lifts[chart_left].compose(target_upper),
            )
            prefix = (chart_left, chart_right)
            _add_equation_matrix(
                equations,
                prefix,
                known,
                unknown_count,
                1,
                3,
            )
            for chart in range(3):
                for row in range(2):
                    for column in range(2):
                        for monomial_index, exponent in enumerate(monomials):
                            unknown = (
                                chart * 4 * len(monomials)
                                + (row * 2 + column) * len(monomials)
                                + monomial_index
                            )
                            unit = _unit_matrix(row, column, exponent)
                            if chart == chart_right:
                                contribution = sigma_left.compose(unit)
                            elif chart == chart_left:
                                contribution = _matrix_scale_sign(
                                    unit.compose(
                                        right._transition(
                                            permutation[chart_left],
                                            permutation[chart_right],
                                        )
                                    ),
                                    -1,
                                )
                            else:
                                continue
                            _add_equation_matrix(
                                equations,
                                prefix,
                                contribution,
                                unknown,
                                1,
                                3,
                            )
    solvable, solution, solution_dimension, equation_count = _solve_affine(
        equations,
        unknown_count,
    )
    if not solvable:
        return BoundedGaugeLift(
            generator,
            bound,
            equation_count,
            unknown_count,
            solution_dimension,
            False,
            False,
            (),
        )
    upper_lifts = tuple(
        _upper_solution(solution, monomials, chart)
        for chart in range(3)
    )
    lifts = tuple(
        _block_upper(left_lifts[chart], upper_lifts[chart], right_lifts[chart])
        for chart in range(3)
    )
    verified = all(
        _substitute_matrix(candidate.transition(chart_left, chart_right), images).compose(
            lifts[chart_right]
        ) == lifts[chart_left].compose(
            candidate.transition(permutation[chart_left], permutation[chart_right])
        )
        for chart_left in range(3)
        for chart_right in range(chart_left + 1, 3)
    )
    return BoundedGaugeLift(
        generator,
        bound,
        equation_count,
        unknown_count,
        solution_dimension,
        True,
        verified,
        lifts if verified else (),
    )


def _group_relation_failures(
    p_lift: BoundedGaugeLift,
    t_lift: BoundedGaugeLift,
    p_images: tuple[tuple[object, tuple[int, ...]], ...],
    t_images: tuple[tuple[object, tuple[int, ...]], ...],
) -> tuple[str, ...]:
    """Check exact group relations on selected bounded rank-four lifts."""

    if not p_lift.transition_equations_verified or not t_lift.transition_equations_verified:
        return ("generator lift unavailable",)
    p_permutation = (1, 2, 0)
    t_permutation = (0, 1, 2)
    failures: list[str] = []
    p_power = p_lift.lifts
    t_power = t_lift.lifts
    for _ in range(2):
        p_power = tuple(
            _substitute_matrix(p_power[chart], p_images).compose(
                p_lift.lifts[p_permutation[chart]]
            )
            for chart in range(3)
        )
        t_power = tuple(
            _substitute_matrix(t_power[chart], t_images).compose(
                t_lift.lifts[t_permutation[chart]]
            )
            for chart in range(3)
        )
    if not all(matrix.is_identity() for matrix in p_power):
        failures.append("P^3 != identity")
    if not all(matrix.is_identity() for matrix in t_power):
        failures.append("T^3 != identity")
    p_then_t = tuple(
        _substitute_matrix(p_lift.lifts[chart], t_images).compose(
            t_lift.lifts[p_permutation[chart]]
        )
        for chart in range(3)
    )
    t_then_p = tuple(
        _substitute_matrix(t_lift.lifts[chart], p_images).compose(
            p_lift.lifts[t_permutation[chart]]
        )
        for chart in range(3)
    )
    if p_then_t != t_then_p:
        failures.append("PT != TP")
    return tuple(failures)


def bounded_extension_equivariance(
    candidate: RankFourExtensionCandidate,
    bound: int = 2,
) -> BoundedExtensionEquivariance:
    """Run the exact finite P/T gauge search for one candidate."""

    p_images = ((OMEGA, (0, 1, 0)), (OMEGA2, (0, 0, 1)), (1, (1, 0, 0)))
    t_images = ((1, (1, 0, 0)), (OMEGA, (0, 1, 0)), (OMEGA2, (0, 0, 1)))
    p_lift = _solve_generator(candidate, "P", p_images, (1, 2, 0), bound)
    t_lift = _solve_generator(candidate, "T", t_images, (0, 1, 2), bound)
    return BoundedExtensionEquivariance(
        candidate.representative_index,
        bound,
        (p_lift, t_lift),
        _group_relation_failures(p_lift, t_lift, p_images, t_images),
    )


def tier_a_bounded_extension_equivariance(
    frontier: RankFourFrontier | None = None,
    bound: int = 2,
) -> tuple[BoundedExtensionEquivariance, ...]:
    """Search every Tier A bounded rank-four representative."""

    selected = tier_a_rank_four_frontier() if frontier is None else frontier
    return tuple(
        bounded_extension_equivariance(candidate, bound)
        for candidate in selected.candidates
    )


@cache
def cached_tier_a_bounded_extension_equivariance(
    bound: int = 2,
) -> tuple[BoundedExtensionEquivariance, ...]:
    """Cache the complete no-argument Tier A finite search in one process."""

    return tier_a_bounded_extension_equivariance(bound=bound)


__all__ = [
    "BoundedExtensionEquivariance",
    "BoundedGaugeLift",
    "bounded_extension_equivariance",
    "cached_tier_a_bounded_extension_equivariance",
    "tier_a_bounded_extension_equivariance",
]
