"""Check presentation-level actions on the exact Serre pushouts.

Owns:
    Exact transpose actions on pushout relation matrices, extension-line
    characters, relation-equation checks, and order/commutator gates for the
    displayed I3/I6 base presentations.

Depends on:
    Newly derived Serre pushout relations, Hilbert--Burch resolution actions,
    exact polynomial matrices, and Eisenstein linear algebra.

Must not:
    Call a relation-level action a dP9 bundle linearization, infer quotient
    descent from an eigenclass, or conceal projective commutator failures.

Phase 0:
    Presentation-level linearization diagnostics are exact; global dP9
    frames, honest descent, and physical bundle promotion remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialMatrix
from onetheory.models.heterotic_schoen.visible import PointScheme

from .resolution_actions import (
    _UNITS,
    ResolutionAction,
    _coordinate_images,
    _generator_action,
    _generator_matrix,
    _solve_source_lift,
    _transformed_matrix,
    tier_a_resolution_actions,
)
from .serre_pushout import SerrePushoutCandidate, tier_a_serre_pushouts


def _left_constant_product(constant: Matrix, matrix: PolynomialMatrix) -> PolynomialMatrix:
    """Multiply a polynomial matrix by an exact constant matrix on the left."""

    return PolynomialMatrix(
        tuple(
            tuple(
                sum(
                    (
                        matrix.rows[inner][column].scale(constant[row][inner])
                        for inner in range(constant.column_count)
                    ),
                    Polynomial.zero(
                        matrix.variable_count,
                        scalar_type=matrix.scalar_type,
                    ),
                )
                for column in range(matrix.shape[1])
            )
            for row in range(constant.row_count)
        )
    )


def _right_constant_product(matrix: PolynomialMatrix, constant: Matrix) -> PolynomialMatrix:
    """Multiply a polynomial matrix by an exact constant matrix on the right."""

    return PolynomialMatrix(
        tuple(
            tuple(
                sum(
                    (
                        matrix.rows[row][inner].scale(constant[inner][column])
                        for inner in range(constant.row_count)
                    ),
                    Polynomial.zero(
                        matrix.variable_count,
                        scalar_type=matrix.scalar_type,
                    ),
                )
                for column in range(constant.column_count)
            )
            for row in range(matrix.shape[0])
        )
    )


def _transformed_relation(
    relation: PolynomialMatrix,
    action: ResolutionAction,
) -> PolynomialMatrix:
    """Apply one exact coordinate substitution to a relation matrix."""

    return PolynomialMatrix(
        tuple(
            tuple(entry.substitute_monomials(action.coordinate_images) for entry in row)
            for row in relation.rows
        )
    )


def _middle_action(action: ResolutionAction, character: Eisenstein) -> Matrix:
    """Extend the transposed ideal-generator action by one class line."""

    target = action.target_action.transpose()
    return Matrix(
        tuple(
            tuple(
                target[row][column]
                if row < target.row_count and column < target.column_count
                else (
                    character
                    if row == target.row_count and column == target.column_count
                    else Eisenstein(0)
                )
                for column in range(target.column_count + 1)
            )
            for row in range(target.row_count + 1)
        ),
        scalar_type=Eisenstein,
    )


@dataclass(frozen=True, slots=True)
class PushoutRelationAction:
    """One exact action check on a pushout relation presentation."""

    generator: str
    extension_character: Eisenstein
    relation_equation: bool
    relation_action_order_three: bool
    middle_action_order_three: bool

    def as_record(self) -> dict[str, object]:
        """Serialize relation compatibility without a descent claim."""

        return {
            "generator": self.generator,
            "extension_character": str(self.extension_character),
            "relation_equation": self.relation_equation,
            "relation_action_order_three": self.relation_action_order_three,
            "middle_action_order_three": self.middle_action_order_three,
        }


@dataclass(frozen=True, slots=True)
class PushoutRelationLinearization:
    """The complete presentation-level P/T linearization gate."""

    scheme: str
    actions: tuple[PushoutRelationAction, ...]
    relation_actions_commute: bool
    middle_actions_commute: bool
    failures: tuple[str, ...]
    resolution_variant_counts: tuple[int, int]
    resolution_lift_nullities: tuple[tuple[int, ...], tuple[int, ...]]
    graded_extension_mix_nullities: tuple[int, int]
    compatible_variant_counts: tuple[int, int]
    complete_variant_pair_count: int
    status: str

    @property
    def relation_equations_hold(self) -> bool:
        """Return whether both generators preserve the pushout relation."""

        return all(action.relation_equation for action in self.actions)

    @property
    def group_relations_verified(self) -> bool:
        """Return whether a genuine commuting presentation action is proved."""

        return (
            self.relation_equations_hold
            and all(
                action.relation_action_order_three
                and action.middle_action_order_three
                for action in self.actions
            )
            and self.relation_actions_commute
            and self.middle_actions_commute
            and not self.failures
        )

    def as_record(self) -> dict[str, object]:
        """Serialize all exact relation and group gates."""

        return {
            "scheme": self.scheme,
            "actions": [action.as_record() for action in self.actions],
            "relation_equations_hold": self.relation_equations_hold,
            "relation_actions_commute": self.relation_actions_commute,
            "middle_actions_commute": self.middle_actions_commute,
            "failures": list(self.failures),
            "resolution_variant_counts": list(self.resolution_variant_counts),
            "resolution_lift_nullities": [
                list(nullities) for nullities in self.resolution_lift_nullities
            ],
            "graded_extension_mix_nullities": list(self.graded_extension_mix_nullities),
            "compatible_variant_counts": list(self.compatible_variant_counts),
            "complete_variant_pair_count": self.complete_variant_pair_count,
            "group_relations_verified": self.group_relations_verified,
            "status": self.status,
        }


def _resolution_variants(
    scheme: PointScheme,
    generator: str,
) -> tuple[ResolutionAction, ...]:
    """Enumerate all finite monomial Hilbert--Burch lifts."""

    images = _coordinate_images(generator)
    matrix = scheme.resolution.matrix
    transformed = _transformed_matrix(matrix, images)
    permutation, scalars = _generator_action(scheme, images)
    variants = []
    for transpose in (False, True):
        for global_scalar in _UNITS:
            target_action = _generator_matrix(
                permutation,
                scalars,
                transpose,
                global_scalar,
            )
            source_action = _solve_source_lift(matrix, transformed, target_action)
            if source_action is None:
                continue
            if target_action.determinant().is_zero() or source_action.determinant().is_zero():
                continue
            variants.append(
                ResolutionAction(
                    scheme,
                    generator,
                    images,
                    target_action,
                    source_action,
                    permutation,
                    scalars,
                )
            )
    return tuple(variants)


def _relation_compatible(
    candidate: SerrePushoutCandidate,
    action: ResolutionAction,
    character: Eisenstein,
) -> tuple[bool, Matrix]:
    """Check one extension character against one resolution lift."""

    relation_action = action.source_action.transpose()
    middle_action = _middle_action(action, character)
    transformed = _transformed_relation(candidate.relation, action)
    return (
        _left_constant_product(relation_action, candidate.relation).rows
        == _right_constant_product(transformed, middle_action).rows,
        middle_action,
    )


def _source_lift_nullity(action: ResolutionAction) -> int:
    """Return the exact homogeneous freedom in one source lift equation."""

    matrix = action.scheme.resolution.matrix
    transformed = _transformed_matrix(matrix, action.coordinate_images)
    columns = len(matrix[0])
    exponents = sorted({
        exponent
        for row in (*matrix, *transformed)
        for polynomial in row
        for exponent, _ in polynomial.terms
    })
    equations = []
    for row in range(len(matrix)):
        for column in range(columns):
            for exponent in exponents:
                coefficients = [Eisenstein(0) for _ in range(columns * columns)]
                for inner in range(columns):
                    coefficients[inner * columns + column] = matrix[row][inner].coefficient(
                        exponent
                    )
                value = sum(
                    (
                        action.target_action[row][inner]
                        * transformed[inner][column].coefficient(exponent)
                        for inner in range(len(matrix))
                    ),
                    Eisenstein(0),
                )
                if (
                    any(not coefficient.is_zero() for coefficient in coefficients)
                    or not value.is_zero()
                ):
                    equations.append(coefficients)
    rank = Matrix(equations, scalar_type=Eisenstein).rank() if equations else 0
    return columns * columns - rank


def _graded_extension_mix_nullity(
    candidate: SerrePushoutCandidate,
    action: ResolutionAction,
) -> int:
    """Compute allowed graded mixing freedom into the extension generator."""

    original_shifts = candidate.target_shifts[:-1]
    extension_shift = candidate.target_shifts[-1]
    if len(set(original_shifts)) != 1:
        raise ValueError("pushout original target shifts must be uniform")
    degree = extension_shift - original_shifts[0]
    if degree < 0:
        return 0
    monomials = tuple(
        exponent
        for exponent in product(range(degree + 1), repeat=3)
        if sum(exponent) == degree
    )
    relation = _transformed_relation(candidate.relation, action)
    original_columns = candidate.relation.shape[1] - 1
    unknown_count = original_columns * len(monomials)
    equations = []
    exponents = sorted({
        tuple(left + right for left, right in zip(term, monomial, strict=True))
        for row in relation.rows
        for polynomial in row[:-1]
        for term, _ in polynomial.terms
        for monomial in monomials
    })
    for row in range(relation.shape[0]):
        for exponent in exponents:
            coefficients = [Eisenstein(0) for _ in range(unknown_count)]
            for column in range(original_columns):
                for monomial_index, monomial in enumerate(monomials):
                    source_exponent = tuple(
                        value - shift
                        for value, shift in zip(exponent, monomial, strict=True)
                    )
                    if any(value < 0 for value in source_exponent):
                        continue
                    coefficients[column * len(monomials) + monomial_index] = (
                        relation.rows[row][column].coefficient(source_exponent)
                    )
            if any(not coefficient.is_zero() for coefficient in coefficients):
                equations.append(coefficients)
    rank = Matrix(equations, scalar_type=Eisenstein).rank() if equations else 0
    return unknown_count - rank


def _alternative_variant_counts(
    candidate: SerrePushoutCandidate,
) -> tuple[
    tuple[int, int],
    tuple[tuple[int, ...], tuple[int, ...]],
    tuple[int, int],
    int,
]:
    """Search the finite monomial lift family for complete group pairs."""

    variants = tuple(
        _resolution_variants(candidate.scheme, generator)
        for generator in ("P", "T")
    )
    compatible = []
    for generator_variants in variants:
        compatible.append(
            tuple(
                (action, character, middle)
                for action in generator_variants
                for character in _UNITS
                for valid, middle in (
                    _relation_compatible(candidate, action, character),
                )
                if valid
            )
        )
    complete = 0
    identity_relation = Matrix.identity(2, scalar_type=Eisenstein)
    identity_middle = Matrix.identity(4, scalar_type=Eisenstein)
    for p_action, _, p_middle in compatible[0]:
        for t_action, _, t_middle in compatible[1]:
            p_relation = p_action.source_action.transpose()
            t_relation = t_action.source_action.transpose()
            if p_relation**3 != identity_relation or t_relation**3 != identity_relation:
                continue
            if p_middle**3 != identity_middle or t_middle**3 != identity_middle:
                continue
            if p_relation @ t_relation != t_relation @ p_relation:
                continue
            if p_middle @ t_middle != t_middle @ p_middle:
                continue
            complete += 1
    return (
        tuple(len(item) for item in variants),
        tuple(
            tuple(_source_lift_nullity(action) for action in generator_variants)
            for generator_variants in variants
        ),
        tuple(len(item) for item in compatible),
        complete,
    )


def _one_linearization(
    candidate: SerrePushoutCandidate,
    resolution_actions: tuple[ResolutionAction, ...],
) -> PushoutRelationLinearization:
    """Check one candidate against its two derived resolution actions."""

    actions = []
    relation_matrices = []
    middle_matrices = []
    for action, character in zip(
        resolution_actions,
        candidate.character_pair,
        strict=True,
    ):
        relation_action = action.source_action.transpose()
        middle_action = _middle_action(action, character)
        transformed = _transformed_relation(candidate.relation, action)
        compatible = (
            _left_constant_product(relation_action, candidate.relation).rows
            == _right_constant_product(transformed, middle_action).rows
        )
        actions.append(
            PushoutRelationAction(
                action.name,
                character,
                compatible,
                relation_action**3
                == Matrix.identity(2, scalar_type=Eisenstein),
                middle_action**3
                == Matrix.identity(4, scalar_type=Eisenstein),
            )
        )
        relation_matrices.append(relation_action)
        middle_matrices.append(middle_action)
    failures = []
    if not all(action.relation_equation for action in actions):
        failures.append("pushout relation equation failed")
    if relation_matrices[0] @ relation_matrices[1] != relation_matrices[1] @ relation_matrices[0]:
        failures.append("relation-row P/T actions do not commute")
    if middle_matrices[0] @ middle_matrices[1] != middle_matrices[1] @ middle_matrices[0]:
        failures.append("middle-generator P/T actions do not commute")
    variant_counts, lift_nullities, compatible_counts, complete_count = _alternative_variant_counts(
        candidate
    )
    graded_mix_nullities = tuple(
        _graded_extension_mix_nullity(candidate, action)
        for action in resolution_actions
    )
    return PushoutRelationLinearization(
        candidate.scheme.name,
        tuple(actions),
        relation_matrices[0] @ relation_matrices[1]
        == relation_matrices[1] @ relation_matrices[0],
        middle_matrices[0] @ middle_matrices[1]
        == middle_matrices[1] @ middle_matrices[0],
        tuple(failures),
        variant_counts,
        lift_nullities,
        graded_mix_nullities,
        compatible_counts,
        complete_count,
        "presentation-level action diagnostic; dP9 descent pending",
    )


def tier_a_pushout_relation_linearizations(
    candidates: tuple[SerrePushoutCandidate, ...] | None = None,
) -> tuple[PushoutRelationLinearization, ...]:
    """Check presentation actions for the derived I3/I6 pushouts."""

    selected = tier_a_serre_pushouts() if candidates is None else candidates
    resolution_pairs = tier_a_resolution_actions()
    return tuple(
        _one_linearization(candidate, pair.actions)
        for candidate, pair in zip(selected, resolution_pairs, strict=True)
    )


__all__ = [
    "PushoutRelationAction",
    "PushoutRelationLinearization",
    "tier_a_pushout_relation_linearizations",
]
