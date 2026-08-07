"""Audit extension-level deck actions for curvilinear Serre witnesses.

Owns:
    Induced dual-cokernel actions, exact extension-line character tests,
    full graded degree-three mixing solves, pushout relation compatibility,
    and finite commuting-pair enumeration for the global curvilinear Tier B
    presentations.

Depends on:
    Curvilinear Serre presentation audits, exact resolution lifts, polynomial
    pushout actions, and Eisenstein linear algebra.

Must not:
    Call a quotient-cokernel action a sheaf linearization, infer descent from
    a finite compatible pair, choose physical extension coefficients, or claim
    stability, spectrum, or carrier promotion.

Phase 0:
    The induced presentation actions and the declared finite mixed-action
    boundary are exact; honest global sheaf linearization, quotient descent,
    and physical promotion remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein

from .pushout_linearization import (
    _left_constant_product,
    _middle_action,
    _right_constant_product,
    _transformed_relation,
)
from .serre_pushout import _relation_matrix
from .tier_b_curvilinear_actions import (
    TierBCurvilinearResolutionActionAudit,
    tier_b_curvilinear_resolution_actions,
)
from .tier_b_curvilinear_serre import (
    TierBCurvilinearSerreAudit,
    tier_b_curvilinear_serre_audits,
)
from .tier_b_serre_extensions import _quotient_action

CHARACTERS = (Eisenstein(1), OMEGA, OMEGA2)


def _action_identifier(action: object) -> str:
    """Return a deterministic identifier for one finite lift variant."""

    orientations = ",".join("1" if value else "0" for value in action.orientations)
    scalars = ",".join(str(value) for value in action.scalars)
    return (
        f"{action.name}:orientations={orientations}:scalars={scalars}"
    )


@dataclass(frozen=True, slots=True)
class CurvilinearDualAction:
    """One exact induced action on the fixed-target-line cokernel."""

    generator: str
    variant: str
    matrix: Matrix
    preserves_relations: bool

    @property
    def order_three(self) -> bool:
        """Return whether the induced quotient action has order three."""

        return self.matrix**3 == Matrix.identity(
            self.matrix.row_count,
            scalar_type=Eisenstein,
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact induced action and its finite gates."""

        return {
            "generator": self.generator,
            "variant": self.variant,
            "matrix": [[str(value) for value in row] for row in self.matrix.rows],
            "preserves_relations": self.preserves_relations,
            "order_three": self.order_three,
        }


@dataclass(frozen=True, slots=True)
class CurvilinearCompatibleVariant:
    """One resolution lift and extension-line character preserving a witness."""

    generator: str
    variant: str
    character: Eisenstein
    relation_equation: bool

    def as_record(self) -> dict[str, object]:
        """Serialize one exact relation-compatible finite variant."""

        return {
            "generator": self.generator,
            "variant": self.variant,
            "character": str(self.character),
            "relation_equation": self.relation_equation,
        }


@dataclass(frozen=True, slots=True)
class CurvilinearMixedExtensionAction:
    """One exact graded action solve allowing degree-three extension mixing."""

    generator: str
    variant: str
    matrix: Matrix | None
    relation_equation: bool
    order_three: bool
    solution_nullity: int

    @property
    def solution_exists(self) -> bool:
        """Return whether the exact graded action equations are consistent."""

        return self.matrix is not None

    @property
    def compatible(self) -> bool:
        """Return whether a unique order-three mixed action was certified."""

        return (
            self.solution_exists
            and self.relation_equation
            and self.order_three
            and self.solution_nullity == 0
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the mixed solve and its exact negative boundary."""

        return {
            "generator": self.generator,
            "variant": self.variant,
            "solution_exists": self.solution_exists,
            "relation_equation": self.relation_equation,
            "order_three": self.order_three,
            "solution_nullity": self.solution_nullity,
            "compatible": self.compatible,
            "matrix": (
                None
                if self.matrix is None
                else [[str(value) for value in row] for row in self.matrix.rows]
            ),
        }


@dataclass(frozen=True, slots=True)
class TierBCurvilinearLinearizationAudit:
    """Finite extension-level linearization audit for one specialization."""

    serre_audit: TierBCurvilinearSerreAudit
    p_dual_actions: tuple[CurvilinearDualAction, ...]
    t_dual_actions: tuple[CurvilinearDualAction, ...]
    p_compatible_variants: tuple[CurvilinearCompatibleVariant, ...]
    t_compatible_variants: tuple[CurvilinearCompatibleVariant, ...]
    p_mixed_actions: tuple[CurvilinearMixedExtensionAction, ...]
    t_mixed_actions: tuple[CurvilinearMixedExtensionAction, ...]
    source_commuting_pair_count: int
    middle_commuting_pair_count: int
    dual_commuting_pair_count: int
    complete_variant_pair_count: int
    mixed_complete_variant_pair_count: int
    resolution_action_audit: TierBCurvilinearResolutionActionAudit

    @property
    def induced_actions_exact(self) -> bool:
        """Return whether all induced dual actions pass exact finite gates."""

        return all(
            action.preserves_relations and action.order_three
            for action in (*self.p_dual_actions, *self.t_dual_actions)
        )

    @property
    def finite_group_gate_passes(self) -> bool:
        """Return whether a complete bounded extension action exists."""

        return self.complete_variant_pair_count > 0

    @property
    def scoped_no_complete_pair(self) -> bool:
        """Return the exact no-pair result in the declared lift family."""

        return self.induced_actions_exact and self.complete_variant_pair_count == 0

    @property
    def mixed_action_solves_exact(self) -> bool:
        """Return whether every finite mixed-action solve is certified."""

        return all(
            action.relation_equation
            or not action.solution_exists
            for action in (*self.p_mixed_actions, *self.t_mixed_actions)
        ) and all(
            action.solution_nullity == 0
            for action in (*self.p_mixed_actions, *self.t_mixed_actions)
            if action.solution_exists
        )

    @property
    def mixed_scoped_no_complete_pair(self) -> bool:
        """Return the no-pair result after allowing graded extension mixing."""

        return self.mixed_action_solves_exact and self.mixed_complete_variant_pair_count == 0

    @property
    def exact(self) -> bool:
        """Return whether this finite action boundary is internally certified."""

        return (
            self.serre_audit.exact
            and self.resolution_action_audit.exact
            and self.induced_actions_exact
            and self.mixed_action_solves_exact
        )

    def as_record(self) -> dict[str, object]:
        """Serialize induced actions, compatibility, and unresolved descent."""

        return {
            "scheme": self.serre_audit.specialization.name,
            "p_dual_actions": [action.as_record() for action in self.p_dual_actions],
            "t_dual_actions": [action.as_record() for action in self.t_dual_actions],
            "p_compatible_variants": [
                item.as_record() for item in self.p_compatible_variants
            ],
            "t_compatible_variants": [
                item.as_record() for item in self.t_compatible_variants
            ],
            "p_compatible_variant_count": len(self.p_compatible_variants),
            "t_compatible_variant_count": len(self.t_compatible_variants),
            "p_mixed_actions": [
                item.as_record() for item in self.p_mixed_actions
            ],
            "t_mixed_actions": [
                item.as_record() for item in self.t_mixed_actions
            ],
            "p_mixed_compatible_count": sum(
                item.compatible for item in self.p_mixed_actions
            ),
            "t_mixed_compatible_count": sum(
                item.compatible for item in self.t_mixed_actions
            ),
            "source_commuting_pair_count": self.source_commuting_pair_count,
            "middle_commuting_pair_count": self.middle_commuting_pair_count,
            "dual_commuting_pair_count": self.dual_commuting_pair_count,
            "complete_variant_pair_count": self.complete_variant_pair_count,
            "mixed_complete_variant_pair_count": self.mixed_complete_variant_pair_count,
            "induced_actions_exact": self.induced_actions_exact,
            "finite_group_gate_passes": self.finite_group_gate_passes,
            "scoped_no_complete_pair": self.scoped_no_complete_pair,
            "mixed_action_solves_exact": self.mixed_action_solves_exact,
            "mixed_scoped_no_complete_pair": self.mixed_scoped_no_complete_pair,
            "exact": self.exact,
            "status": (
                "exact finite extension-level action diagnostic including the "
                "full declared degree-three mixing block; no complete pair is "
                "a sheaf linearization or quotient-descent certificate"
            ),
        }


def _relation_compatible(
    relation,
    action: object,
    character: Eisenstein,
) -> bool:
    """Check the exact pushout relation for one lift and line character."""

    return _left_constant_product(
        action.source_action.transpose(),
        relation,
    ).rows == _right_constant_product(
        _transformed_relation(relation, action),
        _middle_action(action, character),
    ).rows


def _dual_actions(
    audit: TierBCurvilinearSerreAudit,
    generator: str,
    actions: tuple[object, ...],
) -> tuple[CurvilinearDualAction, ...]:
    """Derive every exact quotient action from the full dual presentation."""

    result = []
    for action in actions:
        quotient, preserves, representatives = _quotient_action(
            audit.cokernel.presentation,
            audit.cokernel.target_basis,
            action,
        )
        if representatives != audit.cokernel.representative_indices:
            raise ValueError("induced action changed the deterministic quotient complement")
        result.append(
            CurvilinearDualAction(
                generator,
                _action_identifier(action),
                quotient,
                preserves,
            )
        )
    return tuple(result)


def _compatible_variants(
    relation,
    generator: str,
    actions: tuple[object, ...],
) -> tuple[CurvilinearCompatibleVariant, ...]:
    """Enumerate all exact extension-line characters preserving the witness."""

    return tuple(
        CurvilinearCompatibleVariant(
            generator,
            _action_identifier(action),
            character,
            True,
        )
        for action in actions
        for character in CHARACTERS
        if _relation_compatible(relation, action, character)
    )


def _mixed_extension_action(
    relation,
    generator: str,
    action: object,
) -> CurvilinearMixedExtensionAction:
    """Solve the full constant degree-three extension mixing block."""

    if relation.shape != (3, 5):
        raise ValueError("curvilinear pushout relations must have shape (3, 5)")
    target = action.target_action.transpose()
    if target.shape != (4, 4):
        raise ValueError("curvilinear ideal actions must have shape (4, 4)")

    left = _left_constant_product(action.source_action.transpose(), relation)
    transformed = _transformed_relation(relation, action)
    fixed = [
        [Eisenstein(0) for _ in range(5)]
        for _ in range(5)
    ]
    for row in range(4):
        for column in range(4):
            fixed[row][column] = target[row][column]

    exponents = sorted(
        {
            exponent
            for polynomial_row in (*left.rows, *transformed.rows)
            for polynomial in polynomial_row
            for exponent, _ in polynomial.terms
        }
    )
    equations: list[tuple[Eisenstein, Eisenstein, Eisenstein, Eisenstein]] = []
    zero = Eisenstein(0)
    for row in range(3):
        for column in range(5):
            for exponent in exponents:
                fixed_value = zero
                for inner in range(5):
                    fixed_value += (
                        transformed.rows[row][inner].coefficient(exponent)
                        * fixed[inner][column]
                    )
                coefficients = (
                    transformed.rows[row][4].coefficient(exponent)
                    if column == 0
                    else zero,
                    transformed.rows[row][0].coefficient(exponent)
                    if column == 4
                    else zero,
                    transformed.rows[row][4].coefficient(exponent)
                    if column == 4
                    else zero,
                )
                value = left.rows[row][column].coefficient(exponent) - fixed_value
                if (
                    any(not coefficient.is_zero() for coefficient in coefficients)
                    or not value.is_zero()
                ):
                    equations.append((*coefficients, value))

    if not equations:
        equations.append((zero, zero, zero, zero))
    augmented = Matrix(equations, scalar_type=Eisenstein)
    coefficients = Matrix(
        (equation[:3] for equation in equations),
        scalar_type=Eisenstein,
    )
    reduced, pivots = augmented.rref()
    inconsistent = any(
        all(reduced[row][column].is_zero() for column in range(3))
        and not reduced[row][3].is_zero()
        for row in range(reduced.row_count)
    )
    if inconsistent:
        return CurvilinearMixedExtensionAction(
            generator,
            _action_identifier(action),
            None,
            False,
            False,
            0,
        )

    values = [zero, zero, zero]
    for row, pivot in enumerate(pivots):
        if pivot < 3:
            values[pivot] = reduced[row][3]
    mixed_rows = [row[:] for row in fixed]
    mixed_rows[4][0] = values[0]
    mixed_rows[0][4] = values[1]
    mixed_rows[4][4] = values[2]
    mixed = Matrix(mixed_rows, scalar_type=Eisenstein)
    relation_equation = left.rows == _right_constant_product(transformed, mixed).rows
    order_three = mixed**3 == Matrix.identity(5, scalar_type=Eisenstein)
    return CurvilinearMixedExtensionAction(
        generator,
        _action_identifier(action),
        mixed,
        relation_equation,
        order_three,
        3 - coefficients.rank(),
    )


def _mixed_actions(
    relation,
    generator: str,
    actions: tuple[object, ...],
) -> tuple[CurvilinearMixedExtensionAction, ...]:
    """Solve the declared mixed action space for every finite lift."""

    return tuple(
        _mixed_extension_action(relation, generator, action)
        for action in actions
    )


def _mixed_pair_count(
    p_actions: tuple[object, ...],
    t_actions: tuple[object, ...],
    p_mixed: tuple[CurvilinearMixedExtensionAction, ...],
    t_mixed: tuple[CurvilinearMixedExtensionAction, ...],
) -> int:
    """Count complete pairs after exact mixed-block action solving."""

    p_by_variant = {action.variant: action for action in p_mixed}
    t_by_variant = {action.variant: action for action in t_mixed}
    complete = 0
    for p_action in p_actions:
        for t_action in t_actions:
            p_mixed_action = p_by_variant[_action_identifier(p_action)]
            t_mixed_action = t_by_variant[_action_identifier(t_action)]
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


def _pair_counts(
    p_actions: tuple[object, ...],
    t_actions: tuple[object, ...],
    p_dual: tuple[CurvilinearDualAction, ...],
    t_dual: tuple[CurvilinearDualAction, ...],
    p_variants: tuple[CurvilinearCompatibleVariant, ...],
    t_variants: tuple[CurvilinearCompatibleVariant, ...],
) -> tuple[int, int, int, int]:
    """Count source, middle, dual, and complete finite commuting pairs."""

    source = middle = dual = complete = 0
    p_dual_by_variant = {item.variant: item for item in p_dual}
    t_dual_by_variant = {item.variant: item for item in t_dual}
    for p_action in p_actions:
        for t_action in t_actions:
            source_commutes = (
                p_action.source_action @ t_action.source_action
                == t_action.source_action @ p_action.source_action
                and p_action.target_action @ t_action.target_action
                == t_action.target_action @ p_action.target_action
            )
            if source_commutes:
                source += 1
            p_dual_action = p_dual_by_variant[_action_identifier(p_action)]
            t_dual_action = t_dual_by_variant[_action_identifier(t_action)]
            if p_dual_action.matrix @ t_dual_action.matrix == (
                t_dual_action.matrix @ p_dual_action.matrix
            ):
                dual += 1
            p_matching = tuple(
                item
                for item in p_variants
                if item.variant == _action_identifier(p_action)
            )
            t_matching = tuple(
                item
                for item in t_variants
                if item.variant == _action_identifier(t_action)
            )
            for p_variant in p_matching:
                for t_variant in t_matching:
                    p_middle = _middle_action(
                        p_action,
                        p_variant.character,
                    )
                    t_middle = _middle_action(
                        t_action,
                        t_variant.character,
                    )
                    middle_commutes = p_middle @ t_middle == t_middle @ p_middle
                    if middle_commutes:
                        middle += 1
                    if source_commutes and middle_commutes and (
                        p_dual_action.matrix @ t_dual_action.matrix
                        == t_dual_action.matrix @ p_dual_action.matrix
                    ):
                        complete += 1
    return source, middle, dual, complete


def _audit_one(
    serre_audit: TierBCurvilinearSerreAudit,
    action_audit: TierBCurvilinearResolutionActionAudit,
) -> TierBCurvilinearLinearizationAudit:
    """Build one exact extension-level action audit."""

    relation = _relation_matrix(
        serre_audit.specialization.point_scheme,
        serre_audit.extension_map,
    )
    p_dual = _dual_actions(serre_audit, "P", action_audit.p_actions)
    t_dual = _dual_actions(serre_audit, "T", action_audit.t_actions)
    p_variants = _compatible_variants(relation, "P", action_audit.p_actions)
    t_variants = _compatible_variants(relation, "T", action_audit.t_actions)
    p_mixed = _mixed_actions(relation, "P", action_audit.p_actions)
    t_mixed = _mixed_actions(relation, "T", action_audit.t_actions)
    source, middle, dual, complete = _pair_counts(
        action_audit.p_actions,
        action_audit.t_actions,
        p_dual,
        t_dual,
        p_variants,
        t_variants,
    )
    return TierBCurvilinearLinearizationAudit(
        serre_audit,
        p_dual,
        t_dual,
        p_variants,
        t_variants,
        p_mixed,
        t_mixed,
        source,
        middle,
        dual,
        complete,
        _mixed_pair_count(
            action_audit.p_actions,
            action_audit.t_actions,
            p_mixed,
            t_mixed,
        ),
        action_audit,
    )


@cache
def _cached_audits(
    parameter: Eisenstein,
) -> tuple[TierBCurvilinearLinearizationAudit, ...]:
    """Construct extension-level action audits for all eight specializations."""

    serre_audits = tier_b_curvilinear_serre_audits(parameter)
    action_audits = tier_b_curvilinear_resolution_actions(parameter)
    action_by_name = {
        audit.specialization.name: audit for audit in action_audits
    }
    result = tuple(
        _audit_one(serre_audit, action_by_name[serre_audit.specialization.name])
        for serre_audit in serre_audits
    )
    if len(result) != 8 or not all(item.exact for item in result):
        raise ValueError("curvilinear extension-level action audit failed exact gates")
    return result


def tier_b_curvilinear_linearization_audits(
    parameter: object = Eisenstein(1),
) -> tuple[TierBCurvilinearLinearizationAudit, ...]:
    """Construct exact finite extension-level linearization audits."""

    value = Eisenstein.coerce(parameter)
    if value.is_zero():
        raise ValueError("the curvilinear parameter must be nonzero")
    return _cached_audits(value)


__all__ = [
    "CurvilinearCompatibleVariant",
    "CurvilinearDualAction",
    "CurvilinearMixedExtensionAction",
    "TierBCurvilinearLinearizationAudit",
    "tier_b_curvilinear_linearization_audits",
]
