"""Solve exact graded extension actions with all same-degree mixing.

Owns:
    Exact affine solves for constant extension-generator action blocks whose
    entries may mix every ideal generator of the same graded degree, together
    with relation, order, and commuting-pair checks.

Depends on:
    Exact polynomial relation matrices, resolution actions, and Eisenstein
    linear algebra. The solver is reusable across the declared Tier B
    presentation diagnostics.

Must not:
    Call a presentation action a sheaf linearization, infer quotient descent,
    choose physical extension coefficients, or claim stability, spectrum, or
    carrier promotion from a finite solution.

Phase 0:
    The declared graded affine action spaces are solved exactly; global sheaf
    comparison and physical construction remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein

from .pushout_linearization import (
    _left_constant_product,
    _right_constant_product,
    _transformed_relation,
)


def action_identifier(action: object) -> str:
    """Return a deterministic identifier for one finite resolution lift."""

    orientations = getattr(action, "orientations", ())
    scalars = getattr(action, "scalars", ())
    if orientations or scalars:
        orientation_text = ",".join("1" if value else "0" for value in orientations)
        scalar_text = ",".join(str(value) for value in scalars)
        return f"{action.name}:orientations={orientation_text}:scalars={scalar_text}"
    return str(action.name)


@dataclass(frozen=True, slots=True)
class MixedExtensionAction:
    """One exact action solve in a declared graded mixing space."""

    generator: str
    variant: str
    matrix: Matrix | None
    relation_equation: bool
    order_three: bool
    solution_nullity: int
    mixing_indices: tuple[int, ...]

    @property
    def solution_exists(self) -> bool:
        """Return whether the exact affine equations are consistent."""

        return self.matrix is not None

    @property
    def compatible(self) -> bool:
        """Return whether a unique order-three graded action was certified."""

        return (
            self.solution_exists
            and self.relation_equation
            and self.order_three
            and self.solution_nullity == 0
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact solve and its declared mixing support."""

        return {
            "generator": self.generator,
            "variant": self.variant,
            "solution_exists": self.solution_exists,
            "relation_equation": self.relation_equation,
            "order_three": self.order_three,
            "solution_nullity": self.solution_nullity,
            "mixing_indices": list(self.mixing_indices),
            "compatible": self.compatible,
            "matrix": (
                None
                if self.matrix is None
                else [[str(value) for value in row] for row in self.matrix.rows]
            ),
        }


def solve_mixed_extension_action(
    relation,
    generator: str,
    variant: str,
    action: object,
    generator_degrees: tuple[int, ...],
    extension_degree: int,
) -> MixedExtensionAction:
    """Solve the full constant block allowed by the graded degrees."""

    target = action.target_action.transpose()
    if len(generator_degrees) != target.row_count:
        raise ValueError("generator degrees do not match the target action")
    if relation.shape[1] != target.row_count + 1:
        raise ValueError("the relation matrix must include one extension column")
    mixing_indices = tuple(
        index
        for index, degree in enumerate(generator_degrees)
        if degree == extension_degree
    )
    matrix_size = target.row_count + 1
    fixed = [
        [Eisenstein(0) for _ in range(matrix_size)]
        for _ in range(matrix_size)
    ]
    for row in range(target.row_count):
        for column in range(target.column_count):
            fixed[row][column] = target[row][column]

    unknowns = (
        tuple(("lower", index) for index in mixing_indices)
        + tuple(("upper", index) for index in mixing_indices)
        + (("diagonal", target.row_count),)
    )
    left = _left_constant_product(action.source_action.transpose(), relation)
    transformed = _transformed_relation(relation, action)
    exponents = sorted(
        {
            exponent
            for polynomial_row in (*left.rows, *transformed.rows)
            for polynomial in polynomial_row
            for exponent, _ in polynomial.terms
        }
    )
    zero = Eisenstein(0)
    equations: list[tuple[Eisenstein, ...]] = []
    for row in range(relation.shape[0]):
        for column in range(matrix_size):
            for exponent in exponents:
                fixed_value = zero
                for inner in range(matrix_size):
                    fixed_value += (
                        transformed.rows[row][inner].coefficient(exponent)
                        * fixed[inner][column]
                    )
                coefficients = []
                for kind, index in unknowns:
                    if kind == "lower":
                        coefficient = (
                            transformed.rows[row][target.row_count]
                            .coefficient(exponent)
                            if column == index
                            else zero
                        )
                    elif kind == "upper":
                        coefficient = (
                            transformed.rows[row][index].coefficient(exponent)
                            if column == target.row_count
                            else zero
                        )
                    else:
                        coefficient = (
                            transformed.rows[row][target.row_count]
                            .coefficient(exponent)
                            if column == target.row_count
                            else zero
                        )
                    coefficients.append(coefficient)
                value = left.rows[row][column].coefficient(exponent) - fixed_value
                if (
                    any(not coefficient.is_zero() for coefficient in coefficients)
                    or not value.is_zero()
                ):
                    equations.append((*coefficients, value))
    if not equations:
        equations.append(tuple(zero for _ in range(len(unknowns) + 1)))

    augmented = Matrix(equations, scalar_type=Eisenstein)
    coefficient_matrix = Matrix(
        (equation[:-1] for equation in equations),
        scalar_type=Eisenstein,
    )
    reduced, pivots = augmented.rref()
    unknown_count = len(unknowns)
    inconsistent = any(
        all(reduced[row][column].is_zero() for column in range(unknown_count))
        and not reduced[row][unknown_count].is_zero()
        for row in range(reduced.row_count)
    )
    if inconsistent:
        return MixedExtensionAction(
            generator,
            variant,
            None,
            False,
            False,
            0,
            mixing_indices,
        )

    values = [zero for _ in unknowns]
    for row, pivot in enumerate(pivots):
        if pivot < unknown_count:
            values[pivot] = reduced[row][unknown_count]
    mixed_rows = [row[:] for row in fixed]
    for (kind, index), value in zip(unknowns, values, strict=True):
        if kind == "lower":
            mixed_rows[target.row_count][index] = value
        elif kind == "upper":
            mixed_rows[index][target.row_count] = value
        else:
            mixed_rows[target.row_count][target.row_count] = value
    mixed = Matrix(mixed_rows, scalar_type=Eisenstein)
    relation_equation = left.rows == _right_constant_product(transformed, mixed).rows
    order_three = mixed**3 == Matrix.identity(matrix_size, scalar_type=Eisenstein)
    return MixedExtensionAction(
        generator,
        variant,
        mixed,
        relation_equation,
        order_three,
        unknown_count - coefficient_matrix.rank(),
        mixing_indices,
    )


def mixed_pair_count(
    p_actions: tuple[object, ...],
    t_actions: tuple[object, ...],
    p_mixed: tuple[MixedExtensionAction, ...],
    t_mixed: tuple[MixedExtensionAction, ...],
) -> int:
    """Count complete P/T pairs after the exact mixed solves."""

    p_by_variant = {action.variant: action for action in p_mixed}
    t_by_variant = {action.variant: action for action in t_mixed}
    complete = 0
    for p_action in p_actions:
        for t_action in t_actions:
            p_mixed_action = p_by_variant[action_identifier(p_action)]
            t_mixed_action = t_by_variant[action_identifier(t_action)]
            if not p_mixed_action.compatible or not t_mixed_action.compatible:
                continue
            source_commutes = (
                p_action.source_action @ t_action.source_action
                == t_action.source_action @ p_action.source_action
                and p_action.target_action @ t_action.target_action
                == t_action.target_action @ p_action.target_action
            )
            mixed_commutes = (
                p_mixed_action.matrix @ t_mixed_action.matrix
                == t_mixed_action.matrix @ p_mixed_action.matrix
            )
            if source_commutes and mixed_commutes:
                complete += 1
    return complete


__all__ = [
    "MixedExtensionAction",
    "action_identifier",
    "mixed_pair_count",
    "solve_mixed_extension_action",
]
