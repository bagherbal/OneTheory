"""Enumerate exact common eigenclasses for curvilinear Serre presentations.

Owns:
    Simultaneous P/T eigenspaces in the fixed-target-line presentation
    cokernels, canonical projective representatives, exact lifted extension
    maps, and support-local Fitting certificates for every declared global
    curvilinear specialization.

Depends on:
    Exact curvilinear Hilbert--Burch actions, graded dual presentations,
    Eisenstein linear algebra, and polynomial Serre pushout relations.

Must not:
    Identify a presentation cokernel with global Ext, select an eigenline as
    physics, infer sheaf linearization or quotient descent, or claim stability,
    spectrum, or carrier promotion from class-level invariance.

Phase 0:
    Common presentation-cokernel eigenlines are explicit; representative
    correction, dP9 linearization, and physical promotion remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from itertools import combinations

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialMatrix

from .serre_pushout import _relation_matrix
from .tier_b_curvilinear_actions import (
    TierBCurvilinearResolutionActionAudit,
    tier_b_curvilinear_resolution_actions,
)
from .tier_b_curvilinear_serre import _dual_presentation, _evaluate, _polynomial_record
from .tier_b_mixed_linearization import action_identifier
from .tier_b_serre_extensions import (
    _extension_map,
    _quotient_action,
    _stacked_character_equations,
)

CHARACTERS = (Eisenstein(1), OMEGA, OMEGA2)
Point = tuple[Eisenstein, Eisenstein, Eisenstein]
SupportFitting = tuple[tuple[int, Point, tuple[int, ...]], ...]


def _normalize_projective_vector(
    values: tuple[Eisenstein, ...],
) -> tuple[Eisenstein, ...]:
    """Normalize a nonzero exact vector by its first nonzero coordinate."""

    try:
        leading = next(value for value in values if not value.is_zero())
    except StopIteration as error:
        raise ValueError("a projective eigenvector cannot be zero") from error
    return tuple(value / leading for value in values)


def _vector_key(
    values: tuple[Eisenstein, ...],
) -> tuple[tuple[object, object], ...]:
    """Return a deterministic sortable key in the basis ``(1, omega)``."""

    return tuple((value.a, value.b) for value in values)


def _support_fitting(
    relation: PolynomialMatrix,
    support: tuple[Point, ...],
) -> SupportFitting:
    """Find exact nonzero maximal minors after evaluation at every point."""

    relation_rank = relation.shape[0]
    column_sets = tuple(combinations(range(relation.shape[1]), relation_rank))
    records = []
    for point_index, point in enumerate(support):
        evaluated = tuple(
            tuple(_evaluate(entry, point) for entry in row)
            for row in relation.rows
        )
        nonzero = tuple(
            minor_index
            for minor_index, columns in enumerate(column_sets)
            if not Matrix(
                tuple(
                    tuple(evaluated[row][column] for column in columns)
                    for row in range(relation_rank)
                ),
                scalar_type=Eisenstein,
            )
            .determinant()
            .is_zero()
        )
        records.append((point_index, point, nonzero))
    return tuple(records)


@dataclass(frozen=True, slots=True)
class CurvilinearEigenclassOccurrence:
    """One lift pair and character pair realizing a common eigenline."""

    p_variant: str
    t_variant: str
    p_character: Eisenstein
    t_character: Eisenstein

    def as_record(self) -> dict[str, object]:
        """Serialize one exact simultaneous-character occurrence."""

        return {
            "p_variant": self.p_variant,
            "t_variant": self.t_variant,
            "p_character": str(self.p_character),
            "t_character": str(self.t_character),
        }


@dataclass(frozen=True, slots=True)
class CurvilinearPresentationEigenclass:
    """One canonical projective class in the graded presentation cokernel."""

    quotient_coordinates: tuple[Eisenstein, ...]
    occurrences: tuple[CurvilinearEigenclassOccurrence, ...]
    extension_map: tuple[Polynomial, ...]
    relation_shape: tuple[int, int]
    support_fitting: SupportFitting

    @property
    def support_locally_free(self) -> bool:
        """Return whether one maximal relation minor survives at every point."""

        return all(indices for _, _, indices in self.support_fitting)

    @property
    def occurrence_count(self) -> int:
        """Return the number of exact lift/character realizations."""

        return len(self.occurrences)

    def as_record(self) -> dict[str, object]:
        """Serialize the exact class and preserve its unresolved boundary."""

        return {
            "quotient_coordinates": [str(value) for value in self.quotient_coordinates],
            "occurrences": [item.as_record() for item in self.occurrences],
            "occurrence_count": self.occurrence_count,
            "extension_map": [_polynomial_record(item) for item in self.extension_map],
            "relation_shape": list(self.relation_shape),
            "support_fitting": [
                {
                    "point_index": point_index,
                    "point": [str(value) for value in point],
                    "unit_minor_indices": list(indices),
                    "unit_minor_exists": bool(indices),
                }
                for point_index, point, indices in self.support_fitting
            ],
            "support_locally_free": self.support_locally_free,
            "selected_as_physics": False,
            "status": (
                "exact common presentation-cokernel eigenline with an explicit "
                "lifted extension map; representative correction, dP9 "
                "linearization, and quotient descent remain unresolved"
            ),
        }


@dataclass(frozen=True, slots=True)
class TierBCurvilinearEigenclassAudit:
    """Complete common-eigenline audit for one global specialization."""

    scheme: str
    orbit: str
    family: str
    parameter: Eisenstein
    cokernel_dimension: int
    representative_indices: tuple[int, ...]
    p_action_count: int
    t_action_count: int
    quotient_actions_exact: bool
    commuting_quotient_pair_count: int
    eigenspaces_one_dimensional: bool
    eigenclasses: tuple[CurvilinearPresentationEigenclass, ...]

    @property
    def eigenclass_count(self) -> int:
        """Return the number of distinct canonical projective eigenlines."""

        return len(self.eigenclasses)

    @property
    def support_locally_free_eigenclass_count(self) -> int:
        """Return the number of eigenlines passing the support Fitting gate."""

        return sum(item.support_locally_free for item in self.eigenclasses)

    @property
    def occurrence_count(self) -> int:
        """Return all lift-pair/character realizations across distinct lines."""

        return sum(item.occurrence_count for item in self.eigenclasses)

    @property
    def commuting_pairs_diagonalize_completely(self) -> bool:
        """Return whether every commuting pair supplies a full eigenbasis."""

        return self.occurrence_count == (
            self.commuting_quotient_pair_count * self.cokernel_dimension
        )

    @property
    def exact(self) -> bool:
        """Return whether the finite class-level audit closes exactly."""

        return (
            self.quotient_actions_exact
            and self.commuting_quotient_pair_count > 0
            and self.eigenspaces_one_dimensional
            and self.eigenclass_count == self.cokernel_dimension
            and self.commuting_pairs_diagonalize_completely
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the complete eigenline frontier without selecting one."""

        return {
            "scheme": self.scheme,
            "orbit": self.orbit,
            "family": self.family,
            "parameter": str(self.parameter),
            "parameter_is_selected_physics": False,
            "cokernel_dimension": self.cokernel_dimension,
            "representative_indices": list(self.representative_indices),
            "p_action_count": self.p_action_count,
            "t_action_count": self.t_action_count,
            "quotient_actions_exact": self.quotient_actions_exact,
            "commuting_quotient_pair_count": self.commuting_quotient_pair_count,
            "eigenspaces_one_dimensional": self.eigenspaces_one_dimensional,
            "eigenclass_count": self.eigenclass_count,
            "support_locally_free_eigenclass_count": (
                self.support_locally_free_eigenclass_count
            ),
            "occurrence_count": self.occurrence_count,
            "commuting_pairs_diagonalize_completely": (
                self.commuting_pairs_diagonalize_completely
            ),
            "eigenclasses": [item.as_record() for item in self.eigenclasses],
            "exact": self.exact,
            "status": (
                "complete exact common-eigenline audit in the declared graded "
                "presentation cokernel; no line is a global Ext class, sheaf "
                "linearization, descended constituent, or physical selection"
            ),
        }


def _audit_one(
    action_audit: TierBCurvilinearResolutionActionAudit,
    target_line_shift: int,
) -> TierBCurvilinearEigenclassAudit:
    """Enumerate and lift all common projective eigenlines exactly."""

    specialization = action_audit.specialization
    _, _, _, target_basis, presentation = _dual_presentation(
        specialization,
        target_line_shift,
    )
    p_actions = tuple(
        _quotient_action(presentation, target_basis, action)
        for action in action_audit.p_actions
    )
    t_actions = tuple(
        _quotient_action(presentation, target_basis, action)
        for action in action_audit.t_actions
    )
    representative_indices = p_actions[0][2]
    quotient_actions_exact = all(
        preserves
        and representatives == representative_indices
        and matrix**3
        == Matrix.identity(matrix.row_count, scalar_type=Eisenstein)
        for matrix, preserves, representatives in (*p_actions, *t_actions)
    )
    occurrences: dict[
        tuple[Eisenstein, ...],
        list[CurvilinearEigenclassOccurrence],
    ] = {}
    commuting_pairs = 0
    eigenspaces_one_dimensional = True
    for p_index, (p_matrix, _, _) in enumerate(p_actions):
        for t_index, (t_matrix, _, _) in enumerate(t_actions):
            if p_matrix @ t_matrix != t_matrix @ p_matrix:
                continue
            commuting_pairs += 1
            for p_character in CHARACTERS:
                for t_character in CHARACTERS:
                    eigenspace = _stacked_character_equations(
                        p_matrix,
                        t_matrix,
                        p_character,
                        t_character,
                    ).nullspace()
                    if len(eigenspace) > 1:
                        eigenspaces_one_dimensional = False
                    for vector in eigenspace:
                        normalized = _normalize_projective_vector(vector.values)
                        occurrences.setdefault(normalized, []).append(
                            CurvilinearEigenclassOccurrence(
                                action_identifier(action_audit.p_actions[p_index]),
                                action_identifier(action_audit.t_actions[t_index]),
                                p_character,
                                t_character,
                            )
                        )
    eigenclasses = []
    for coordinates in sorted(occurrences, key=_vector_key):
        extension_map = _extension_map(
            target_basis,
            representative_indices,
            coordinates,
        )
        relation = _relation_matrix(specialization.point_scheme, extension_map)
        eigenclasses.append(
            CurvilinearPresentationEigenclass(
                coordinates,
                tuple(occurrences[coordinates]),
                extension_map,
                relation.shape,
                _support_fitting(relation, specialization.support_points),
            )
        )
    return TierBCurvilinearEigenclassAudit(
        specialization.name,
        specialization.orbit_identifier,
        specialization.family,
        specialization.parameter,
        len(representative_indices),
        representative_indices,
        len(action_audit.p_actions),
        len(action_audit.t_actions),
        quotient_actions_exact,
        commuting_pairs,
        eigenspaces_one_dimensional,
        tuple(eigenclasses),
    )


@cache
def _cached_audits(
    parameter: Eisenstein,
    target_line_shift: int,
) -> tuple[TierBCurvilinearEigenclassAudit, ...]:
    """Cache the exact eigenline audit for one declared specialization."""

    return tuple(
        _audit_one(action_audit, target_line_shift)
        for action_audit in tier_b_curvilinear_resolution_actions(parameter)
    )


def tier_b_curvilinear_eigenclass_audits(
    parameter: object = Eisenstein(1),
    target_line_shift: int = 3,
    action_audits: tuple[TierBCurvilinearResolutionActionAudit, ...] | None = None,
) -> tuple[TierBCurvilinearEigenclassAudit, ...]:
    """Return all exact common eigenlines for the declared global schemes."""

    value = Eisenstein.coerce(parameter)
    if value.is_zero():
        raise ValueError("the curvilinear parameter must be nonzero")
    if isinstance(target_line_shift, bool) or not isinstance(target_line_shift, int):
        raise TypeError("the target-line shift must be an integer")
    audits = (
        _cached_audits(value, target_line_shift)
        if action_audits is None
        else tuple(_audit_one(item, target_line_shift) for item in action_audits)
    )
    if len(audits) != 8 or not all(item.exact for item in audits):
        raise ValueError("curvilinear common-eigenline audit failed exact gates")
    return audits


__all__ = [
    "CurvilinearEigenclassOccurrence",
    "CurvilinearPresentationEigenclass",
    "TierBCurvilinearEigenclassAudit",
    "tier_b_curvilinear_eigenclass_audits",
]
