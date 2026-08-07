"""Audit projective cocycles for corrected curvilinear presentations.

Owns:
    Exact comparison of the corrected P/T presentation actions against the
    degree-dependent central scalar relating the published homogeneous lifts,
    including the source, middle, and target free-module terms.

Depends on:
    Exact curvilinear eigenclasses and representative corrections, published
    homogeneous coordinate substitutions, graded relation matrices, and
    Eisenstein linear algebra.

Must not:
    Replace the projective central comparison by strict matrix commutation,
    call a graded-presentation cocycle a dP9 sheaf linearization, infer quotient
    descent, select a physical carrier, or bypass the remaining frame checks.

Phase 0:
    Projective presentation cocycles are audited exactly; dP9 frame actions,
    global Ext identification, and physical promotion remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from onetheory.math.polynomials import PolynomialMatrix

from .dp9_actions import published_coordinate_images
from .pushout_linearization import (
    _left_constant_product,
    _right_constant_product,
)
from .serre_pushout import _relation_matrix
from .tier_b_curvilinear_actions import (
    TierBCurvilinearResolutionActionAudit,
    tier_b_curvilinear_resolution_actions,
)
from .tier_b_curvilinear_corrections import (
    TierBCurvilinearCorrectionAudit,
    tier_b_curvilinear_correction_audits,
)
from .tier_b_curvilinear_eigenclasses import (
    CurvilinearPresentationEigenclass,
    TierBCurvilinearEigenclassAudit,
    tier_b_curvilinear_eigenclass_audits,
)
from .tier_b_curvilinear_serre import _dual_presentation
from .tier_b_mixed_linearization import action_identifier


def _diagonal(values: tuple[Eisenstein, ...]) -> Matrix:
    """Return an exact diagonal matrix from declared values."""

    zero = Eisenstein(0)
    return Matrix(
        tuple(
            tuple(value if row == column else zero for column in range(len(values)))
            for row, value in enumerate(values)
        ),
        scalar_type=Eisenstein,
    )


def _degree_central_action(shifts: tuple[int, ...]) -> Matrix:
    """Return the central homogeneous scalar on graded free summands."""

    return _diagonal(tuple(OMEGA**shift for shift in shifts))


def _coordinate_matrix(name: str) -> Matrix:
    """Convert a published monomial substitution into its exact lift matrix."""

    images = published_coordinate_images(name)
    zero = Eisenstein(0)
    rows = []
    for coefficient, exponents in images:
        if sum(exponents) != 1 or any(exponent not in (0, 1) for exponent in exponents):
            raise ValueError("published projective coordinate lifts must be linear monomials")
        rows.append(
            tuple(
                coefficient if exponent == 1 else zero
                for exponent in exponents
            )
        )
    return Matrix(tuple(rows), scalar_type=Eisenstein)


def _central_relation_equation(
    relation: PolynomialMatrix,
    source_shifts: tuple[int, ...],
    target_shifts: tuple[int, ...],
) -> bool:
    """Check central coordinate scaling against every graded relation entry."""

    if relation.shape != (len(source_shifts), len(target_shifts)):
        raise ValueError("central relation comparison has incompatible shifts")
    images = tuple(
        (
            OMEGA,
            tuple(1 if row == column else 0 for column in range(3)),
        )
        for row in range(3)
    )
    transformed = PolynomialMatrix(
        tuple(
            tuple(entry.substitute_monomials(images) for entry in row)
            for row in relation.rows
        )
    )
    source = _degree_central_action(source_shifts)
    target = _degree_central_action(target_shifts)
    expected = _right_constant_product(
        _left_constant_product(source, relation),
        target.inverse(),
    )
    return transformed == expected


@dataclass(frozen=True, slots=True)
class CurvilinearProjectiveCocycleLine:
    """Central-cocycle counts for one corrected support-free eigenline."""

    eigenline_index: int
    occurrence_count: int
    central_relation_equation: bool
    degree_preserving_occurrence_count: int
    middle_cocycle_occurrence_count: int
    target_cocycle_occurrence_count: int
    source_cocycle_occurrence_count: int
    complete_cocycle_occurrence_count: int

    @property
    def exact(self) -> bool:
        """Return whether every corrected occurrence obeys the graded cocycle."""

        return (
            self.central_relation_equation
            and self.occurrence_count > 0
            and self.degree_preserving_occurrence_count == self.occurrence_count
            and self.middle_cocycle_occurrence_count == self.occurrence_count
            and self.target_cocycle_occurrence_count == self.occurrence_count
            and self.source_cocycle_occurrence_count == self.occurrence_count
            and self.complete_cocycle_occurrence_count == self.occurrence_count
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact central comparison and its remaining boundary."""

        return {
            "eigenline_index": self.eigenline_index,
            "occurrence_count": self.occurrence_count,
            "central_relation_equation": self.central_relation_equation,
            "degree_preserving_occurrence_count": (
                self.degree_preserving_occurrence_count
            ),
            "middle_cocycle_occurrence_count": (
                self.middle_cocycle_occurrence_count
            ),
            "target_cocycle_occurrence_count": (
                self.target_cocycle_occurrence_count
            ),
            "source_cocycle_occurrence_count": (
                self.source_cocycle_occurrence_count
            ),
            "complete_cocycle_occurrence_count": (
                self.complete_cocycle_occurrence_count
            ),
            "exact": self.exact,
            "selected_as_physics": False,
            "status": (
                "exact projective graded-presentation cocycle; induced dP9 "
                "frame actions and quotient descent remain unresolved"
            ),
        }


@dataclass(frozen=True, slots=True)
class TierBCurvilinearProjectiveCocycleAudit:
    """Projective-cocycle frontier for one curvilinear specialization."""

    scheme: str
    coordinate_lift_commutator: bool
    support_free_eigenline_count: int
    scoped_no_correction_eigenline_count: int
    lines: tuple[CurvilinearProjectiveCocycleLine, ...]

    @property
    def corrected_eigenline_count(self) -> int:
        """Return eigenlines admitting corrected representative actions."""

        return len(self.lines)

    @property
    def projective_cocycle_eigenline_count(self) -> int:
        """Return corrected lines passing every projective cocycle occurrence."""

        return sum(line.exact for line in self.lines)

    @property
    def exact(self) -> bool:
        """Return whether the finite projective-cocycle frontier is complete."""

        return (
            self.coordinate_lift_commutator
            and self.corrected_eigenline_count
            + self.scoped_no_correction_eigenline_count
            == self.support_free_eigenline_count
            and all(line.exact for line in self.lines)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize projective candidates without making a sheaf claim."""

        return {
            "scheme": self.scheme,
            "central_coordinate_scalar": str(OMEGA),
            "coordinate_lift_commutator": self.coordinate_lift_commutator,
            "support_free_eigenline_count": self.support_free_eigenline_count,
            "corrected_eigenline_count": self.corrected_eigenline_count,
            "scoped_no_correction_eigenline_count": (
                self.scoped_no_correction_eigenline_count
            ),
            "projective_cocycle_eigenline_count": (
                self.projective_cocycle_eigenline_count
            ),
            "lines": [line.as_record() for line in self.lines],
            "exact": self.exact,
            "status": (
                "exact central-corrected projective presentation frontier; "
                "dP9 frame actions, global Ext, and quotient descent remain open"
            ),
        }


def _line_audit(
    line_index: int,
    eigenclass: CurvilinearPresentationEigenclass,
    correction,
    action_audit: TierBCurvilinearResolutionActionAudit,
    generator_degrees: tuple[int, ...],
    syzygy_degrees: tuple[int, ...],
    target_line_shift: int,
) -> CurvilinearProjectiveCocycleLine:
    """Check every corrected occurrence against the projective central scalar."""

    target_shifts = (*generator_degrees, target_line_shift)
    relation = _relation_matrix(
        action_audit.specialization.point_scheme,
        eigenclass.extension_map,
    )
    central_relation = _central_relation_equation(
        relation,
        syzygy_degrees,
        target_shifts,
    )
    target_central = _degree_central_action(generator_degrees)
    source_central = _degree_central_action(syzygy_degrees)
    middle_central = _degree_central_action(target_shifts)
    p_mixed = {item.variant: item for item in correction.p_actions}
    t_mixed = {item.variant: item for item in correction.t_actions}
    p_resolution = {
        action_identifier(item): item for item in action_audit.p_actions
    }
    t_resolution = {
        action_identifier(item): item for item in action_audit.t_actions
    }
    degree_preserving = middle = target = source = complete = 0
    corrected_occurrences = 0
    for occurrence in eigenclass.occurrences:
        p_action = p_mixed[occurrence.p_variant]
        t_action = t_mixed[occurrence.t_variant]
        if not p_action.compatible or not t_action.compatible:
            continue
        if p_action.matrix is None or t_action.matrix is None:
            raise ValueError("compatible projective actions require exact matrices")
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
        corrected_occurrences += 1
        p_lift = p_resolution[occurrence.p_variant]
        t_lift = t_resolution[occurrence.t_variant]
        preserves_degree = (
            p_action.matrix @ middle_central
            == middle_central @ p_action.matrix
            and t_action.matrix @ middle_central
            == middle_central @ t_action.matrix
        )
        middle_cocycle = (
            p_action.matrix @ t_action.matrix
            == middle_central @ (t_action.matrix @ p_action.matrix)
        )
        target_cocycle = (
            p_lift.target_action @ t_lift.target_action
            == target_central.inverse()
            @ (t_lift.target_action @ p_lift.target_action)
        )
        source_cocycle = (
            p_lift.source_action @ t_lift.source_action
            == source_central.inverse()
            @ (t_lift.source_action @ p_lift.source_action)
        )
        degree_preserving += preserves_degree
        middle += middle_cocycle
        target += target_cocycle
        source += source_cocycle
        complete += (
            preserves_degree
            and middle_cocycle
            and target_cocycle
            and source_cocycle
        )
    if corrected_occurrences != correction.corrected_character_occurrence_count:
        raise ValueError("projective cocycle lost a corrected class occurrence")
    return CurvilinearProjectiveCocycleLine(
        line_index,
        corrected_occurrences,
        central_relation,
        degree_preserving,
        middle,
        target,
        source,
        complete,
    )


def _audit_one(
    eigen_audit: TierBCurvilinearEigenclassAudit,
    correction_audit: TierBCurvilinearCorrectionAudit,
    action_audit: TierBCurvilinearResolutionActionAudit,
    target_line_shift: int,
) -> TierBCurvilinearProjectiveCocycleAudit:
    """Build the central-corrected cocycle frontier for one specialization."""

    if not (
        eigen_audit.scheme
        == correction_audit.scheme
        == action_audit.specialization.name
    ):
        raise ValueError("projective cocycle inputs describe different schemes")
    generator_degrees, syzygy_degrees, _, _, _ = _dual_presentation(
        action_audit.specialization,
        target_line_shift,
    )
    support_free = tuple(
        (index, eigenclass)
        for index, eigenclass in enumerate(eigen_audit.eigenclasses)
        if eigenclass.support_locally_free
    )
    eigenclasses = {index: item for index, item in support_free}
    lines = tuple(
        _line_audit(
            correction.eigenline_index,
            eigenclasses[correction.eigenline_index],
            correction,
            action_audit,
            generator_degrees,
            syzygy_degrees,
            target_line_shift,
        )
        for correction in correction_audit.corrections
        if correction.representative_correction_complete
    )
    p_coordinates = _coordinate_matrix("P")
    t_coordinates = _coordinate_matrix("T")
    coordinate_commutator = (
        p_coordinates @ t_coordinates
        == (t_coordinates @ p_coordinates).scale(OMEGA)
    )
    return TierBCurvilinearProjectiveCocycleAudit(
        eigen_audit.scheme,
        coordinate_commutator,
        eigen_audit.support_locally_free_eigenclass_count,
        correction_audit.scoped_no_correction_eigenline_count,
        lines,
    )


@cache
def _cached_audits(
    parameter: Eisenstein,
    target_line_shift: int,
) -> tuple[TierBCurvilinearProjectiveCocycleAudit, ...]:
    """Cache the complete finite projective-cocycle frontier."""

    actions = tier_b_curvilinear_resolution_actions(parameter)
    eigenclasses = tier_b_curvilinear_eigenclass_audits(
        parameter,
        target_line_shift,
        actions,
    )
    corrections = tier_b_curvilinear_correction_audits(
        parameter,
        target_line_shift,
        actions,
        eigenclasses,
    )
    return tuple(
        _audit_one(eigen, correction, action, target_line_shift)
        for eigen, correction, action in zip(
            eigenclasses,
            corrections,
            actions,
            strict=True,
        )
    )


def tier_b_curvilinear_projective_cocycle_audits(
    parameter: object = Eisenstein(1),
    target_line_shift: int = 3,
    action_audits: tuple[TierBCurvilinearResolutionActionAudit, ...] | None = None,
    eigenclass_audits: tuple[TierBCurvilinearEigenclassAudit, ...] | None = None,
    correction_audits: tuple[TierBCurvilinearCorrectionAudit, ...] | None = None,
) -> tuple[TierBCurvilinearProjectiveCocycleAudit, ...]:
    """Return exact central-corrected P/T cocycle audits."""

    value = Eisenstein.coerce(parameter)
    if value.is_zero():
        raise ValueError("the curvilinear parameter must be nonzero")
    if isinstance(target_line_shift, bool) or not isinstance(target_line_shift, int):
        raise TypeError("the target-line shift must be an integer")
    if action_audits is None and eigenclass_audits is None and correction_audits is None:
        audits = _cached_audits(value, target_line_shift)
    else:
        actions = (
            tier_b_curvilinear_resolution_actions(value)
            if action_audits is None
            else action_audits
        )
        eigenclasses = (
            tier_b_curvilinear_eigenclass_audits(value, target_line_shift, actions)
            if eigenclass_audits is None
            else eigenclass_audits
        )
        corrections = (
            tier_b_curvilinear_correction_audits(
                value,
                target_line_shift,
                actions,
                eigenclasses,
            )
            if correction_audits is None
            else correction_audits
        )
        if not (len(actions) == len(eigenclasses) == len(corrections)):
            raise ValueError("projective cocycle inputs require matching audit counts")
        audits = tuple(
            _audit_one(eigen, correction, action, target_line_shift)
            for eigen, correction, action in zip(
                eigenclasses,
                corrections,
                actions,
                strict=True,
            )
        )
    if len(audits) != 8 or not all(audit.exact for audit in audits):
        raise ValueError("curvilinear projective-cocycle audit failed exact gates")
    return audits


__all__ = [
    "CurvilinearProjectiveCocycleLine",
    "TierBCurvilinearProjectiveCocycleAudit",
    "tier_b_curvilinear_projective_cocycle_audits",
]
