"""Lift curvilinear quotient eigenclasses to corrected pushout actions.

Owns:
    Exact mixed-block P/T action solves for every support-locally-free
    curvilinear presentation eigenline, character matching against its
    quotient occurrences, and strict presentation group-law diagnostics.

Depends on:
    The complete curvilinear eigenclass frontier, finite Hilbert--Burch lift
    actions, exact Serre relation matrices, and the reusable graded mixed-action
    solver over the Eisenstein field.

Must not:
    Call a corrected representative a sheaf linearization, promote a strict
    presentation failure to a global no-go, infer quotient descent, or select
    a physical carrier.

Phase 0:
    Representative corrections are exact in the declared finite lift family;
    dP9 sheaf comparison, group descent, and promotion remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.numbers import Eisenstein

from .serre_pushout import _relation_matrix
from .tier_b_curvilinear_actions import (
    TierBCurvilinearResolutionActionAudit,
    tier_b_curvilinear_resolution_actions,
)
from .tier_b_curvilinear_eigenclasses import (
    CurvilinearPresentationEigenclass,
    TierBCurvilinearEigenclassAudit,
    tier_b_curvilinear_eigenclass_audits,
)
from .tier_b_curvilinear_serre import _dual_presentation
from .tier_b_mixed_linearization import (
    MixedExtensionAction,
    action_identifier,
    solve_mixed_extension_action,
)


@dataclass(frozen=True, slots=True)
class CurvilinearRepresentativeCorrection:
    """Exact correction audit for one support-free quotient eigenline."""

    eigenline_index: int
    quotient_coordinates: tuple[Eisenstein, ...]
    occurrence_count: int
    p_actions: tuple[MixedExtensionAction, ...]
    t_actions: tuple[MixedExtensionAction, ...]
    corrected_character_occurrence_count: int
    strict_middle_commuting_occurrence_count: int
    strict_resolution_commuting_occurrence_count: int
    strict_complete_occurrence_count: int

    @property
    def p_compatible_count(self) -> int:
        """Return individually certified P corrections."""

        return sum(action.compatible for action in self.p_actions)

    @property
    def t_compatible_count(self) -> int:
        """Return individually certified T corrections."""

        return sum(action.compatible for action in self.t_actions)

    @property
    def action_solves_exact(self) -> bool:
        """Return whether every affine solve has an exact closed result."""

        actions = (*self.p_actions, *self.t_actions)
        return all(
            action.relation_equation or not action.solution_exists
            for action in actions
        ) and all(
            action.solution_nullity == 0
            for action in actions
            if action.solution_exists
        )

    @property
    def representative_correction_complete(self) -> bool:
        """Return whether every class occurrence has matching chain maps."""

        return (
            self.action_solves_exact
            and self.corrected_character_occurrence_count == self.occurrence_count
        )

    @property
    def scoped_no_representative_correction(self) -> bool:
        """Return the exact no-correction result in the declared lift family."""

        return (
            self.action_solves_exact
            and self.p_compatible_count == 0
            and self.t_compatible_count == 0
            and self.corrected_character_occurrence_count == 0
        )

    @property
    def strict_group_law_passes(self) -> bool:
        """Return whether one occurrence commutes on both resolution terms."""

        return self.strict_complete_occurrence_count > 0

    def as_record(self) -> dict[str, object]:
        """Serialize correction matrices and the remaining group-law boundary."""

        return {
            "eigenline_index": self.eigenline_index,
            "quotient_coordinates": [str(value) for value in self.quotient_coordinates],
            "occurrence_count": self.occurrence_count,
            "p_actions": [action.as_record() for action in self.p_actions],
            "t_actions": [action.as_record() for action in self.t_actions],
            "p_compatible_count": self.p_compatible_count,
            "t_compatible_count": self.t_compatible_count,
            "action_solves_exact": self.action_solves_exact,
            "corrected_character_occurrence_count": (
                self.corrected_character_occurrence_count
            ),
            "representative_correction_complete": (
                self.representative_correction_complete
            ),
            "scoped_no_representative_correction": (
                self.scoped_no_representative_correction
            ),
            "strict_middle_commuting_occurrence_count": (
                self.strict_middle_commuting_occurrence_count
            ),
            "strict_resolution_commuting_occurrence_count": (
                self.strict_resolution_commuting_occurrence_count
            ),
            "strict_complete_occurrence_count": self.strict_complete_occurrence_count,
            "strict_group_law_passes": self.strict_group_law_passes,
            "selected_as_physics": False,
            "status": (
                "exact class-representative correction in a finite graded lift "
                "family; strict presentation group laws do not establish or "
                "exclude dP9 sheaf linearization and quotient descent"
            ),
        }


@dataclass(frozen=True, slots=True)
class TierBCurvilinearCorrectionAudit:
    """Representative-correction frontier for one global specialization."""

    scheme: str
    orbit: str
    family: str
    parameter: Eisenstein
    support_free_eigenline_count: int
    corrections: tuple[CurvilinearRepresentativeCorrection, ...]

    @property
    def corrected_eigenline_count(self) -> int:
        """Return eigenlines with corrections for every class occurrence."""

        return sum(item.representative_correction_complete for item in self.corrections)

    @property
    def scoped_no_correction_eigenline_count(self) -> int:
        """Return eigenlines excluded by the declared correction family."""

        return sum(
            item.scoped_no_representative_correction for item in self.corrections
        )

    @property
    def strict_group_law_eigenline_count(self) -> int:
        """Return eigenlines with at least one strict commuting lift pair."""

        return sum(item.strict_group_law_passes for item in self.corrections)

    @property
    def exact(self) -> bool:
        """Return whether every support-free line has an exact finite result."""

        return (
            len(self.corrections) == self.support_free_eigenline_count
            and all(item.action_solves_exact for item in self.corrections)
            and all(
                item.representative_correction_complete
                or item.scoped_no_representative_correction
                for item in self.corrections
            )
        )

    def as_record(self) -> dict[str, object]:
        """Serialize all corrected and scoped-excluded eigenlines."""

        return {
            "scheme": self.scheme,
            "orbit": self.orbit,
            "family": self.family,
            "parameter": str(self.parameter),
            "parameter_is_selected_physics": False,
            "support_free_eigenline_count": self.support_free_eigenline_count,
            "corrected_eigenline_count": self.corrected_eigenline_count,
            "scoped_no_correction_eigenline_count": (
                self.scoped_no_correction_eigenline_count
            ),
            "strict_group_law_eigenline_count": (
                self.strict_group_law_eigenline_count
            ),
            "corrections": [item.as_record() for item in self.corrections],
            "exact": self.exact,
            "status": (
                "exact representative-correction frontier for all support-free "
                "curvilinear eigenlines; dP9 sheaf linearization and quotient "
                "descent remain unresolved"
            ),
        }


def _correction(
    line_index: int,
    eigenclass: CurvilinearPresentationEigenclass,
    action_audit: TierBCurvilinearResolutionActionAudit,
    generator_degrees: tuple[int, ...],
    target_line_shift: int,
) -> CurvilinearRepresentativeCorrection:
    """Solve and compare all P/T corrections for one quotient eigenline."""

    relation = _relation_matrix(
        action_audit.specialization.point_scheme,
        eigenclass.extension_map,
    )
    p_actions = tuple(
        solve_mixed_extension_action(
            relation,
            "P",
            action_identifier(action),
            action,
            generator_degrees,
            target_line_shift,
        )
        for action in action_audit.p_actions
    )
    t_actions = tuple(
        solve_mixed_extension_action(
            relation,
            "T",
            action_identifier(action),
            action,
            generator_degrees,
            target_line_shift,
        )
        for action in action_audit.t_actions
    )
    p_by_variant = {item.variant: item for item in p_actions}
    t_by_variant = {item.variant: item for item in t_actions}
    p_resolution = {
        action_identifier(item): item for item in action_audit.p_actions
    }
    t_resolution = {
        action_identifier(item): item for item in action_audit.t_actions
    }
    corrected = middle_commuting = resolution_commuting = complete = 0
    for occurrence in eigenclass.occurrences:
        p_action = p_by_variant[occurrence.p_variant]
        t_action = t_by_variant[occurrence.t_variant]
        if not p_action.compatible or not t_action.compatible:
            continue
        if p_action.matrix is None or t_action.matrix is None:
            raise ValueError("compatible correction actions require exact matrices")
        p_character = p_action.matrix[
            p_action.matrix.row_count - 1
        ][p_action.matrix.column_count - 1]
        t_character = t_action.matrix[
            t_action.matrix.row_count - 1
        ][t_action.matrix.column_count - 1]
        if (
            p_character != occurrence.p_character
            or t_character != occurrence.t_character
        ):
            continue
        corrected += 1
        middle = p_action.matrix @ t_action.matrix == t_action.matrix @ p_action.matrix
        middle_commuting += middle
        p_lift = p_resolution[occurrence.p_variant]
        t_lift = t_resolution[occurrence.t_variant]
        resolution = (
            p_lift.source_action @ t_lift.source_action
            == t_lift.source_action @ p_lift.source_action
            and p_lift.target_action @ t_lift.target_action
            == t_lift.target_action @ p_lift.target_action
        )
        resolution_commuting += resolution
        complete += middle and resolution
    return CurvilinearRepresentativeCorrection(
        line_index,
        eigenclass.quotient_coordinates,
        eigenclass.occurrence_count,
        p_actions,
        t_actions,
        corrected,
        middle_commuting,
        resolution_commuting,
        complete,
    )


def _audit_one(
    eigen_audit: TierBCurvilinearEigenclassAudit,
    action_audit: TierBCurvilinearResolutionActionAudit,
    target_line_shift: int,
) -> TierBCurvilinearCorrectionAudit:
    """Solve the correction frontier for one matching specialization."""

    if eigen_audit.scheme != action_audit.specialization.name:
        raise ValueError("eigenclass and resolution-action schemes do not match")
    generator_degrees, _, _, _, _ = _dual_presentation(
        action_audit.specialization,
        target_line_shift,
    )
    corrections = tuple(
        _correction(
            line_index,
            eigenclass,
            action_audit,
            generator_degrees,
            target_line_shift,
        )
        for line_index, eigenclass in enumerate(eigen_audit.eigenclasses)
        if eigenclass.support_locally_free
    )
    return TierBCurvilinearCorrectionAudit(
        eigen_audit.scheme,
        eigen_audit.orbit,
        eigen_audit.family,
        eigen_audit.parameter,
        eigen_audit.support_locally_free_eigenclass_count,
        corrections,
    )


@cache
def _cached_audits(
    parameter: Eisenstein,
    target_line_shift: int,
) -> tuple[TierBCurvilinearCorrectionAudit, ...]:
    """Cache all finite corrections for one exact parameter value."""

    actions = tier_b_curvilinear_resolution_actions(parameter)
    eigenclasses = tier_b_curvilinear_eigenclass_audits(
        parameter,
        target_line_shift,
    )
    return tuple(
        _audit_one(eigen_audit, action_audit, target_line_shift)
        for eigen_audit, action_audit in zip(eigenclasses, actions, strict=True)
    )


def tier_b_curvilinear_correction_audits(
    parameter: object = Eisenstein(1),
    target_line_shift: int = 3,
    action_audits: tuple[TierBCurvilinearResolutionActionAudit, ...] | None = None,
    eigenclass_audits: tuple[TierBCurvilinearEigenclassAudit, ...] | None = None,
) -> tuple[TierBCurvilinearCorrectionAudit, ...]:
    """Return exact representative corrections for all support-free lines."""

    value = Eisenstein.coerce(parameter)
    if value.is_zero():
        raise ValueError("the curvilinear parameter must be nonzero")
    if isinstance(target_line_shift, bool) or not isinstance(target_line_shift, int):
        raise TypeError("the target-line shift must be an integer")
    if action_audits is None and eigenclass_audits is None:
        audits = _cached_audits(value, target_line_shift)
    else:
        actions = (
            tier_b_curvilinear_resolution_actions(value)
            if action_audits is None
            else action_audits
        )
        eigenclasses = (
            tier_b_curvilinear_eigenclass_audits(
                value,
                target_line_shift,
                actions,
            )
            if eigenclass_audits is None
            else eigenclass_audits
        )
        if len(actions) != len(eigenclasses):
            raise ValueError("correction audits require matching action and eigenclass data")
        audits = tuple(
            _audit_one(eigen_audit, action_audit, target_line_shift)
            for eigen_audit, action_audit in zip(eigenclasses, actions, strict=True)
        )
    if len(audits) != 8 or not all(item.exact for item in audits):
        raise ValueError("curvilinear representative-correction audit failed exact gates")
    return audits


__all__ = [
    "CurvilinearRepresentativeCorrection",
    "TierBCurvilinearCorrectionAudit",
    "tier_b_curvilinear_correction_audits",
]
