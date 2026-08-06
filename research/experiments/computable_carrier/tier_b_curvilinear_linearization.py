"""Audit extension-level deck actions for curvilinear Serre witnesses.

Owns:
    Induced dual-cokernel actions, exact extension-line character tests,
    pushout relation compatibility, and finite commuting-pair enumeration for
    the global curvilinear Tier B presentations.

Depends on:
    Curvilinear Serre presentation audits, exact resolution lifts, polynomial
    pushout actions, and Eisenstein linear algebra.

Must not:
    Call a quotient-cokernel action a sheaf linearization, infer descent from
    a finite compatible pair, choose physical extension coefficients, or claim
    stability, spectrum, or carrier promotion.

Phase 0:
    The induced presentation actions and their finite compatibility boundary
    are exact; global sheaf linearization, dP9 gluing, quotient descent, and
    physical promotion remain unresolved.
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
class TierBCurvilinearLinearizationAudit:
    """Finite extension-level linearization audit for one specialization."""

    serre_audit: TierBCurvilinearSerreAudit
    p_dual_actions: tuple[CurvilinearDualAction, ...]
    t_dual_actions: tuple[CurvilinearDualAction, ...]
    p_compatible_variants: tuple[CurvilinearCompatibleVariant, ...]
    t_compatible_variants: tuple[CurvilinearCompatibleVariant, ...]
    source_commuting_pair_count: int
    middle_commuting_pair_count: int
    dual_commuting_pair_count: int
    complete_variant_pair_count: int
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
    def exact(self) -> bool:
        """Return whether this finite action boundary is internally certified."""

        return (
            self.serre_audit.exact
            and self.resolution_action_audit.exact
            and self.induced_actions_exact
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
            "source_commuting_pair_count": self.source_commuting_pair_count,
            "middle_commuting_pair_count": self.middle_commuting_pair_count,
            "dual_commuting_pair_count": self.dual_commuting_pair_count,
            "complete_variant_pair_count": self.complete_variant_pair_count,
            "induced_actions_exact": self.induced_actions_exact,
            "finite_group_gate_passes": self.finite_group_gate_passes,
            "scoped_no_complete_pair": self.scoped_no_complete_pair,
            "exact": self.exact,
            "status": (
                "exact finite extension-level action diagnostic; no complete "
                "pair is a sheaf linearization or quotient-descent certificate"
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
        source,
        middle,
        dual,
        complete,
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
    "TierBCurvilinearLinearizationAudit",
    "tier_b_curvilinear_linearization_audits",
]
