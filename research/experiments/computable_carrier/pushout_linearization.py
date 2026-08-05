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

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialMatrix

from .resolution_actions import ResolutionAction, tier_a_resolution_actions
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
            "group_relations_verified": self.group_relations_verified,
            "status": self.status,
        }


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
    return PushoutRelationLinearization(
        candidate.scheme.name,
        tuple(actions),
        relation_matrices[0] @ relation_matrices[1]
        == relation_matrices[1] @ relation_matrices[0],
        middle_matrices[0] @ middle_matrices[1]
        == middle_matrices[1] @ middle_matrices[0],
        tuple(failures),
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
