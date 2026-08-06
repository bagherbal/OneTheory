"""Construct exact Serre-extension diagnostics for global curvilinear schemes.

Owns:
    Fixed-target-line graded dual cokernels, explicit extension-coordinate
    representatives, support-local Fitting tests, and bounded polynomial unit
    certificates on the six dP9 presentation charts.

Depends on:
    Global curvilinear Hilbert--Burch presentations, exact polynomial and
    Eisenstein linear algebra, the existing dP9 chart atlas, and the bounded
    resolution-lift audit.

Must not:
    Call the graded cokernel a global Ext group, call a presentation witness
    a descended sheaf, infer honest group linearization from finite lifts, or
    claim stability, spectrum, or physical carrier promotion.

Phase 0:
    Exact non-equivariant presentation-level Serre witnesses are certified for
    the declared specializations; global line gluing, linearization, descent,
    and all downstream physical gates remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from itertools import product

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialMatrix

from .pencil import TierAPencilModel, tier_a_pencil_model
from .serre_pushout import _chart_matrix, _quotient_row, _relation_matrix
from .tier_b_curvilinear_actions import (
    TierBCurvilinearResolutionActionAudit,
    tier_b_curvilinear_resolution_actions,
)
from .tier_b_curvilinear_global import (
    TierBGlobalCurvilinearSpecialization,
    tier_b_global_curvilinear_specializations,
)
from .tier_b_serre_extensions import (
    BasisLabel,
    _dual_presentation,
    _extension_map,
)

Point = tuple[Eisenstein, Eisenstein, Eisenstein]
ExactCombination = tuple[tuple[int, Polynomial], ...]


def _polynomial_record(polynomial: Polynomial) -> dict[str, object]:
    """Serialize one exact affine polynomial certificate."""

    return {
        "terms": [
            {
                "exponents": list(exponents),
                "coefficient": str(coefficient),
            }
            for exponents, coefficient in polynomial.terms
        ]
    }


def _evaluate(polynomial: Polynomial, point: Point) -> Eisenstein:
    """Evaluate one exact homogeneous polynomial at a projective point."""

    value = Eisenstein(0)
    for exponents, coefficient in polynomial.terms:
        term = coefficient
        for coordinate, exponent in zip(point, exponents, strict=True):
            term *= coordinate**exponent
        value += term
    return value


def _coefficient_monomials(
    variable_count: int,
    degree_bound: int,
) -> tuple[tuple[int, ...], ...]:
    """Enumerate the normalized coefficient monomials in one bounded window."""

    return tuple(
        monomial
        for monomial in product(range(degree_bound + 1), repeat=variable_count)
        if sum(monomial) <= degree_bound
    )


def _unit_combination_at_bound(
    generators: tuple[Polynomial, ...],
    degree_bound: int,
) -> ExactCombination | None:
    """Solve an exact bounded polynomial Bezout system."""

    if not generators:
        raise ValueError("a unit certificate requires nonempty generators")
    variable_count = generators[0].variable_count
    if any(item.variable_count != variable_count for item in generators):
        raise ValueError("unit generators use incompatible polynomial variables")
    coefficient_basis = _coefficient_monomials(variable_count, degree_bound)
    product_exponents = {
        tuple(left + right for left, right in zip(monomial, coefficient, strict=True))
        for generator in generators
        for monomial, _ in generator.terms
        for coefficient in coefficient_basis
    }
    exponents = tuple(
        sorted(
            product_exponents | {(0,) * variable_count},
            key=lambda exponent: (sum(exponent), exponent),
        )
    )
    unknowns = tuple(
        (generator, monomial)
        for generator in range(len(generators))
        for monomial in coefficient_basis
    )
    rows = []
    right_hand_side = []
    for exponent in exponents:
        row = []
        for generator, coefficient in unknowns:
            predecessor = tuple(
                target - source
                for target, source in zip(exponent, coefficient, strict=True)
            )
            row.append(
                generators[generator].coefficient(predecessor)
                if min(predecessor) >= 0
                else Eisenstein(0)
            )
        rows.append(tuple(row))
        right_hand_side.append(
            Eisenstein(1)
            if exponent == (0,) * variable_count
            else Eisenstein(0)
        )
    augmented = Matrix(
        tuple(
            (*row, value)
            for row, value in zip(rows, right_hand_side, strict=True)
        ),
        scalar_type=Eisenstein,
    )
    reduced, pivots = augmented.rref()
    unknown_count = len(unknowns)
    if any(
        all(reduced[row][column].is_zero() for column in range(unknown_count))
        and not reduced[row][unknown_count].is_zero()
        for row in range(reduced.row_count)
    ):
        return None
    solution = [Eisenstein(0) for _ in unknowns]
    for row, pivot in enumerate(pivots):
        if pivot < unknown_count:
            solution[pivot] = reduced[row][unknown_count]
    return tuple(
        (
            generator,
            Polynomial(
                tuple(
                    (monomial, solution[index])
                    for index, (owner, monomial) in enumerate(unknowns)
                    if owner == generator and not solution[index].is_zero()
                ),
                variable_count=variable_count,
                scalar_type=Eisenstein,
            ),
        )
        for generator in range(len(generators))
    )


def _bounded_unit_combination(
    generators: tuple[Polynomial, ...],
    maximum_degree: int = 2,
) -> tuple[int, ExactCombination]:
    """Find the first exact polynomial unit identity in a declared window."""

    for degree_bound in range(maximum_degree + 1):
        combination = _unit_combination_at_bound(generators, degree_bound)
        if combination is None:
            continue
        identity = Polynomial.zero(
            generators[0].variable_count,
            scalar_type=Eisenstein,
        )
        for index, coefficient in combination:
            identity += coefficient * generators[index]
        if identity != Polynomial.one(
            generators[0].variable_count,
            scalar_type=Eisenstein,
        ):
            raise ValueError("bounded unit solve failed exact recomposition")
        return degree_bound, tuple(
            (index, coefficient)
            for index, coefficient in combination
            if not coefficient.is_zero()
        )
    raise ValueError(
        f"no polynomial unit certificate through degree {maximum_degree}"
    )


@dataclass(frozen=True, slots=True)
class CurvilinearFittingCertificate:
    """An exact polynomial unit identity for one affine chart."""

    chart: str
    minor_count: int
    coefficient_degree_bound: int
    nonzero_coefficients: ExactCombination
    identity: Polynomial

    @property
    def verified(self) -> bool:
        """Return whether the displayed combination is exactly one."""

        return self.identity == Polynomial.one(
            self.identity.variable_count,
            scalar_type=Eisenstein,
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact bounded Fitting-unit certificate."""

        return {
            "chart": self.chart,
            "minor_count": self.minor_count,
            "coefficient_degree_bound": self.coefficient_degree_bound,
            "nonzero_coefficients": [
                {
                    "minor_index": index,
                    "coefficient": _polynomial_record(coefficient),
                }
                for index, coefficient in self.nonzero_coefficients
            ],
            "identity": _polynomial_record(self.identity),
            "verified": self.verified,
        }


@dataclass(frozen=True, slots=True)
class TierBCurvilinearSerreCokernel:
    """One exact fixed-target-line graded dual cokernel."""

    specialization: TierBGlobalCurvilinearSpecialization
    target_line_shift: int
    generator_degrees: tuple[int, ...]
    syzygy_degrees: tuple[int, ...]
    source_basis: tuple[BasisLabel, ...]
    target_basis: tuple[BasisLabel, ...]
    presentation: Matrix
    representative_indices: tuple[int, ...]

    @property
    def dimension(self) -> int:
        """Return the exact presentation-level quotient dimension."""

        return len(self.representative_indices)

    def as_record(self) -> dict[str, object]:
        """Serialize the cokernel bases and exact quotient complement."""

        return {
            "scheme": self.specialization.name,
            "target_line_shift": self.target_line_shift,
            "generator_degrees": list(self.generator_degrees),
            "syzygy_degrees": list(self.syzygy_degrees),
            "source_basis": [
                [row, list(monomial)] for row, monomial in self.source_basis
            ],
            "target_basis": [
                [column, list(monomial)]
                for column, monomial in self.target_basis
            ],
            "presentation_shape": list(self.presentation.shape),
            "presentation_rank": self.presentation.rank(),
            "representative_indices": list(self.representative_indices),
            "dimension": self.dimension,
            "status": (
                "exact fixed-target-line presentation cokernel; global Ext and "
                "quotient descent remain unresolved"
            ),
        }


@dataclass(frozen=True, slots=True)
class TierBCurvilinearSerreAudit:
    """One exact non-equivariant presentation-level Serre witness."""

    specialization: TierBGlobalCurvilinearSpecialization
    cokernel: TierBCurvilinearSerreCokernel
    quotient_coordinates: tuple[Eisenstein, ...]
    witness_mask: int
    extension_map: tuple[Polynomial, ...]
    relation_shape: tuple[int, int]
    source_shifts: tuple[int, ...]
    target_shifts: tuple[int, ...]
    graded_relation: bool
    support_fitting: tuple[tuple[int, Point, tuple[int, ...]], ...]
    chart_relation_composition: tuple[tuple[str, bool], ...]
    fitting_certificates: tuple[CurvilinearFittingCertificate, ...]
    fitting_failures: tuple[tuple[str, str], ...]
    resolution_action_audit: TierBCurvilinearResolutionActionAudit

    @property
    def support_fitting_verified(self) -> bool:
        """Return whether every reduced support point has a unit minor."""

        return all(indices for _, _, indices in self.support_fitting)

    @property
    def chart_fitting_verified(self) -> bool:
        """Return whether every dP9 presentation chart has a unit ideal."""

        return not self.fitting_failures and all(
            certificate.verified for certificate in self.fitting_certificates
        )

    @property
    def relation_composition_verified(self) -> bool:
        """Return whether the relation composes to the ideal on every chart."""

        return all(verified for _, verified in self.chart_relation_composition)

    @property
    def presentation_locally_free(self) -> bool:
        """Return the exact presentation-level local-freeness gate."""

        return (
            self.graded_relation
            and self.support_fitting_verified
            and self.relation_composition_verified
            and self.chart_fitting_verified
        )

    @property
    def finite_lift_no_pair(self) -> bool:
        """Return the scoped no-pair result for the finite lift family."""

        return (
            self.resolution_action_audit.exact
            and self.resolution_action_audit.complete_commuting_pair_count == 0
        )

    @property
    def exact(self) -> bool:
        """Return the combined presentation and bounded-lift certificate."""

        return self.presentation_locally_free and self.finite_lift_no_pair

    def as_record(self) -> dict[str, object]:
        """Serialize the witness and every unresolved physical boundary."""

        return {
            "scheme": self.specialization.name,
            "orbit": self.specialization.orbit_identifier,
            "family": self.specialization.family,
            "parameter": str(self.specialization.parameter),
            "parameter_is_selected_physics": False,
            "cokernel": self.cokernel.as_record(),
            "quotient_coordinates": [str(value) for value in self.quotient_coordinates],
            "witness_mask": self.witness_mask,
            "extension_map": [
                _polynomial_record(polynomial) for polynomial in self.extension_map
            ],
            "relation_shape": list(self.relation_shape),
            "source_shifts": list(self.source_shifts),
            "target_shifts": list(self.target_shifts),
            "graded_relation": self.graded_relation,
            "support_fitting": [
                {
                    "point_index": index,
                    "point": [str(value) for value in point],
                    "unit_minor_indices": list(minor_indices),
                    "unit_minor_exists": bool(minor_indices),
                }
                for index, point, minor_indices in self.support_fitting
            ],
            "support_fitting_verified": self.support_fitting_verified,
            "chart_relation_composition": [
                [chart, verified]
                for chart, verified in self.chart_relation_composition
            ],
            "fitting_certificates": [
                certificate.as_record()
                for certificate in self.fitting_certificates
            ],
            "fitting_failures": [
                {"chart": chart, "error": error}
                for chart, error in self.fitting_failures
            ],
            "chart_fitting_verified": self.chart_fitting_verified,
            "presentation_locally_free": self.presentation_locally_free,
            "resolution_action_counts": {
                "P": len(self.resolution_action_audit.p_actions),
                "T": len(self.resolution_action_audit.t_actions),
                "complete_commuting_pairs": (
                    self.resolution_action_audit.complete_commuting_pair_count
                ),
            },
            "finite_lift_no_pair": self.finite_lift_no_pair,
            "exact": self.exact,
            "status": (
                "exact non-equivariant presentation-level Serre witness; finite "
                "resolution lifts have no complete commuting pair; honest sheaf "
                "linearization, dP9 line gluing, quotient descent, stability, "
                "and physical promotion remain unresolved"
            ),
        }


def _dual_cokernel(
    specialization: TierBGlobalCurvilinearSpecialization,
    target_line_shift: int,
) -> TierBCurvilinearSerreCokernel:
    """Construct the exact fixed-target-line cokernel and complement."""

    generator_degrees, syzygy_degrees, source_basis, target_basis, presentation = (
        _dual_presentation(specialization, target_line_shift)
    )
    if presentation is None:
        raise ValueError("curvilinear dual presentation unexpectedly has no map")
    representative_indices = tuple(
        index
        for index in range(presentation.row_count)
        if index not in presentation.transpose().rref()[1]
    )
    return TierBCurvilinearSerreCokernel(
        specialization,
        target_line_shift,
        generator_degrees,
        syzygy_degrees,
        source_basis,
        target_basis,
        presentation,
        representative_indices,
    )


def _support_witness(
    cokernel: TierBCurvilinearSerreCokernel,
) -> tuple[
    int,
    tuple[Eisenstein, ...],
    tuple[Polynomial, ...],
    tuple[tuple[int, Point, tuple[int, ...]], ...],
    PolynomialMatrix,
]:
    """Choose the first exact unit-at-support vector in the finite basis window."""

    support = cokernel.specialization.support_points
    for mask in range(1, 1 << cokernel.dimension):
        coordinates = tuple(
            Eisenstein(1) if mask & (1 << index) else Eisenstein(0)
            for index in range(cokernel.dimension)
        )
        extension_map = _extension_map(
            cokernel.target_basis,
            cokernel.representative_indices,
            coordinates,
        )
        relation = _relation_matrix(
            cokernel.specialization.point_scheme,
            extension_map,
        )
        minors = relation.minors(relation.shape[0])
        records = tuple(
            (
                index,
                point,
                tuple(
                    minor_index
                    for minor_index, minor in enumerate(minors)
                    if not _evaluate(minor, point).is_zero()
                ),
            )
            for index, point in enumerate(support)
        )
        if all(minor_indices for _, _, minor_indices in records):
            return mask, coordinates, extension_map, records, relation
    raise ValueError("no bounded extension witness is locally free at the support")


def _graded_relation(
    relation: PolynomialMatrix,
    source_shifts: tuple[int, ...],
    target_shifts: tuple[int, ...],
) -> bool:
    """Check the displayed pushout relation against its free-module shifts."""

    if relation.shape != (len(source_shifts), len(target_shifts)):
        raise ValueError("relation shape does not match its graded shifts")
    return all(
        entry.is_zero() or entry.degree == source_shifts[row] - target_shifts[column]
        for row, relation_row in enumerate(relation.rows)
        for column, entry in enumerate(relation_row)
    )


def _chart_audit(
    relation: PolynomialMatrix,
    quotient: PolynomialMatrix,
    model: TierAPencilModel,
) -> tuple[
    tuple[tuple[str, bool], ...],
    tuple[CurvilinearFittingCertificate, ...],
    tuple[tuple[str, str], ...],
]:
    """Check relation composition and bounded unit Fitting identities per chart."""

    compositions = []
    certificates = []
    failures = []
    for chart in model.blowup_atlas.charts:
        local_relation = _chart_matrix(relation, chart)
        local_quotient = _chart_matrix(quotient, chart)
        quotient_column = PolynomialMatrix(
            tuple((entry,) for entry in local_quotient.rows[0])
        )
        compositions.append(
            (chart.name, local_relation.compose(quotient_column).is_zero())
        )
        minors = local_relation.minors(local_relation.shape[0])
        try:
            degree_bound, combination = _bounded_unit_combination(minors)
            identity = Polynomial.zero(3, scalar_type=Eisenstein)
            for index, coefficient in combination:
                identity += coefficient * minors[index]
            certificates.append(
                CurvilinearFittingCertificate(
                    chart.name,
                    len(minors),
                    degree_bound,
                    combination,
                    identity,
                )
            )
        except ValueError as error:
            failures.append((chart.name, str(error)))
    return tuple(compositions), tuple(certificates), tuple(failures)


def _audit_one(
    specialization: TierBGlobalCurvilinearSpecialization,
    action_audit: TierBCurvilinearResolutionActionAudit,
    model: TierAPencilModel,
    target_line_shift: int,
) -> TierBCurvilinearSerreAudit:
    """Build one exact global curvilinear Serre presentation audit."""

    cokernel = _dual_cokernel(specialization, target_line_shift)
    mask, coordinates, extension_map, support_fitting, relation = _support_witness(cokernel)
    source_shifts = cokernel.syzygy_degrees
    target_shifts = (
        tuple(generator.degree for generator in cokernel.specialization.generators)
        + (target_line_shift,)
    )
    quotient = _quotient_row(specialization.point_scheme)
    compositions, certificates, failures = _chart_audit(
        relation,
        quotient,
        model,
    )
    return TierBCurvilinearSerreAudit(
        specialization,
        cokernel,
        coordinates,
        mask,
        extension_map,
        relation.shape,
        source_shifts,
        target_shifts,
        _graded_relation(relation, source_shifts, target_shifts),
        support_fitting,
        compositions,
        certificates,
        failures,
        action_audit,
    )


@cache
def _cached_audits(
    parameter: Eisenstein,
    target_line_shift: int,
) -> tuple[TierBCurvilinearSerreAudit, ...]:
    """Construct all exact audits for one declared parameter specialization."""

    specializations = tier_b_global_curvilinear_specializations(parameter)
    action_audits = tier_b_curvilinear_resolution_actions(parameter)
    actions_by_name = {
        audit.specialization.name: audit for audit in action_audits
    }
    model = tier_a_pencil_model()
    result = tuple(
        _audit_one(
            specialization,
            actions_by_name[specialization.name],
            model,
            target_line_shift,
        )
        for specialization in specializations
    )
    if len(result) != 8 or not all(item.exact for item in result):
        raise ValueError("curvilinear Serre presentation family failed exact gates")
    return result


def tier_b_curvilinear_serre_audits(
    parameter: object = Eisenstein(1),
    target_line_shift: int = 3,
) -> tuple[TierBCurvilinearSerreAudit, ...]:
    """Construct exact presentation-level Serre audits for one parameter."""

    value = Eisenstein.coerce(parameter)
    if value.is_zero():
        raise ValueError("the curvilinear parameter must be nonzero")
    if isinstance(target_line_shift, bool) or not isinstance(target_line_shift, int):
        raise TypeError("the target-line shift must be an integer")
    return _cached_audits(value, target_line_shift)


__all__ = [
    "CurvilinearFittingCertificate",
    "TierBCurvilinearSerreAudit",
    "TierBCurvilinearSerreCokernel",
    "tier_b_curvilinear_serre_audits",
]
