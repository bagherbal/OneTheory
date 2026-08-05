"""Audit graded global Serre pushout presentations on the Schoen charts.

Owns:
    Exact unit-ideal Fitting certificates for the pulled-back Tier A pushout
    relations and line-frame-corrected transitions across the six affine
    hypersurface charts of the explicit dP9 presentation.

Depends on:
    The exact Tier A pencil atlas, polynomial pushout relations, graded free
    module shifts, and polynomial fraction matrices. It does not consume
    observations or the published bundle artifact.

Must not:
    Call a graded pullback presentation equivariantly descended, identify it
    with the published carrier, infer stability or spectrum, or hide the
    unresolved quotient linearization and external verification gates.

Phase 0:
    The rank-two pullback local-freeness and line-frame identities are exact;
    global quotient descent and physical carrier promotion remain unresolved.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialFraction, PolynomialMatrix

from .pencil import BlowupChart, TierAPencilModel, tier_a_pencil_model
from .serre_pushout import (
    FractionMatrix,
    SerrePushoutCandidate,
    _chart_matrix,
    _frame_coordinates,
    tier_a_serre_pushouts,
)


def _polynomial_record(polynomial: Polynomial) -> dict[str, object]:
    """Serialize one exact polynomial for a local certificate."""

    return {
        "terms": [
            {
                "exponents": list(exponents),
                "coefficient": str(coefficient),
            }
            for exponents, coefficient in polynomial.terms
        ]
    }


def _fraction_record(fraction: PolynomialFraction) -> dict[str, object]:
    """Serialize one exact polynomial fraction for hashing transitions."""

    return {
        "numerator": _polynomial_record(fraction.numerator),
        "denominator": _polynomial_record(fraction.denominator),
    }


def _matrix_record(matrix: FractionMatrix) -> list[list[dict[str, object]]]:
    """Serialize one exact fraction matrix deterministically."""

    return [
        [_fraction_record(entry) for entry in row]
        for row in matrix.rows
    ]


def _constant_unit_combination(
    generators: tuple[Polynomial, ...],
) -> tuple[tuple[int, Polynomial], ...]:
    """Solve an exact constant-coefficient unit identity for generators."""

    if not generators:
        raise ValueError("a Fitting cover requires maximal minors")
    variable_count = generators[0].variable_count
    scalar_type = generators[0].scalar_type
    if any(
        generator.variable_count != variable_count
        or generator.scalar_type is not scalar_type
        for generator in generators
    ):
        raise TypeError("Fitting generators must use one exact polynomial ring")
    exponents = sorted(
        {exponent for generator in generators for exponent, _ in generator.terms}
        | {(0,) * variable_count}
    )
    rows = []
    for exponent in exponents:
        coefficients = tuple(
            generator.coefficient(exponent)
            for generator in generators
        )
        right = Eisenstein(1) if exponent == (0,) * variable_count else Eisenstein(0)
        if any(not value.is_zero() for value in coefficients) or not right.is_zero():
            rows.append((*coefficients, right))
    augmented = Matrix(rows, scalar_type=Eisenstein)
    reduced, pivots = augmented.rref()
    unknown_count = len(generators)
    if any(
        all(reduced[row][column].is_zero() for column in range(unknown_count))
        and not reduced[row][unknown_count].is_zero()
        for row in range(reduced.row_count)
    ):
        raise ValueError("the displayed Fitting minors do not generate the unit ideal")
    solution = [Eisenstein(0) for _ in range(unknown_count)]
    for row, pivot in enumerate(pivots):
        if pivot < unknown_count:
            solution[pivot] = reduced[row][unknown_count]
    coefficients = tuple(
        (index, Polynomial.constant(value, variable_count, scalar_type=Eisenstein))
        for index, value in enumerate(solution)
        if not value.is_zero()
    )
    identity = Polynomial.zero(variable_count, scalar_type=Eisenstein)
    for index, coefficient in coefficients:
        identity = identity + coefficient * generators[index]
    if identity != Polynomial.one(variable_count, scalar_type=Eisenstein):
        raise ValueError("the computed Fitting identity failed exact recomposition")
    return coefficients


@dataclass(frozen=True, slots=True)
class FittingUnitCertificate:
    """An exact unit-ideal identity for one affine chart relation."""

    chart: str
    minor_count: int
    nonzero_coefficients: tuple[tuple[int, Polynomial], ...]
    identity: Polynomial

    @property
    def verified(self) -> bool:
        """Return whether the recorded combination is exactly one."""

        return self.identity == Polynomial.one(
            self.identity.variable_count,
            scalar_type=Eisenstein,
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the unit identity and its scope."""

        return {
            "chart": self.chart,
            "minor_count": self.minor_count,
            "nonzero_coefficients": [
                {
                    "minor_index": index,
                    "coefficient": _polynomial_record(coefficient),
                }
                for index, coefficient in self.nonzero_coefficients
            ],
            "identity": _polynomial_record(self.identity),
            "verified": self.verified,
            "coefficient_degree_bound": 0,
        }


FrameData = tuple[tuple[int, ...], FractionMatrix, Polynomial]


def _homogeneous_monomial(pivot: int, degree: int) -> Polynomial:
    """Return the pivot-coordinate monomial of one nonnegative degree."""

    if degree < 0:
        raise ValueError("graded frame shifts must be nonnegative here")
    exponents = [0, 0, 0]
    exponents[pivot] = degree
    return Polynomial.monomial(tuple(exponents), scalar_type=Eisenstein)


def _line_factor(source_pivot: int, target_pivot: int, shift: int) -> PolynomialFraction:
    """Return ``x_source**shift / x_target**shift`` exactly."""

    if shift >= 0:
        numerator = _homogeneous_monomial(source_pivot, shift)
        denominator = _homogeneous_monomial(target_pivot, shift)
    else:
        numerator = _homogeneous_monomial(target_pivot, -shift)
        denominator = _homogeneous_monomial(source_pivot, -shift)
    return PolynomialFraction(numerator, denominator)


def _shifted_frame_transition(
    source_pivot: int,
    target_pivot: int,
    source_frame: FrameData,
    target_frame: FrameData,
    target_shifts: tuple[int, ...],
) -> FractionMatrix:
    """Express a target degree-zero frame in a source degree-zero frame."""

    source_free, source_coordinates, _ = source_frame
    target_free, _, _ = target_frame
    if len(source_free) != len(target_free):
        raise ValueError("Fitting frames have incompatible free ranks")
    rank = len(source_free)
    columns = []
    for generator in target_free:
        factor = _line_factor(source_pivot, target_pivot, target_shifts[generator])
        columns.append(
            tuple(
                source_coordinates.rows[generator][row] * factor
                for row in range(rank)
            )
        )
    return FractionMatrix(
        tuple(
            tuple(columns[column][row] for column in range(rank))
            for row in range(rank)
        )
    )


@dataclass(frozen=True, slots=True)
class GlobalSerrePushoutAudit:
    """Exact graded pullback presentation and its local-freeness gates."""

    scheme: str
    relation_shape: tuple[int, int]
    graded_relation: bool
    local_relation_composition: tuple[tuple[str, bool], ...]
    fitting_certificates: tuple[FittingUnitCertificate, ...]
    canonical_frames: tuple[tuple[str, tuple[int, ...], Polynomial], ...]
    line_frame_transitions: tuple[tuple[str, str, FractionMatrix], ...]
    line_frame_all_invertible: bool
    line_frame_cocycle_consistent: bool
    transition_digest: str
    status: str

    @property
    def fitting_cover_verified(self) -> bool:
        """Return whether every declared affine chart has a unit Fitting cover."""

        return all(certificate.verified for certificate in self.fitting_certificates)

    def as_record(self) -> dict[str, object]:
        """Serialize exact gates without claiming quotient descent."""

        return {
            "scheme": self.scheme,
            "relation_shape": list(self.relation_shape),
            "graded_relation": self.graded_relation,
            "local_relation_composition": [
                [chart, verified]
                for chart, verified in self.local_relation_composition
            ],
            "fitting_cover": [
                certificate.as_record()
                for certificate in self.fitting_certificates
            ],
            "fitting_cover_verified": self.fitting_cover_verified,
            "canonical_frames": [
                {
                    "chart": chart,
                    "eliminated_columns": list(columns),
                    "denominator": _polynomial_record(denominator),
                }
                for chart, columns, denominator in self.canonical_frames
            ],
            "line_frame_transition_count": len(self.line_frame_transitions),
            "line_frame_all_invertible": self.line_frame_all_invertible,
            "line_frame_cocycle_consistent": self.line_frame_cocycle_consistent,
            "line_frame_transition_digest": self.transition_digest,
            "status": self.status,
        }


def _fitting_certificate(
    relation: PolynomialMatrix,
    chart: BlowupChart,
) -> FittingUnitCertificate:
    """Build one exact unit identity from all local maximal minors."""

    local_relation = _chart_matrix(relation, chart)
    minors = local_relation.minors(local_relation.shape[0])
    coefficients = _constant_unit_combination(minors)
    identity = Polynomial.zero(3, scalar_type=Eisenstein)
    for index, coefficient in coefficients:
        identity = identity + coefficient * minors[index]
    return FittingUnitCertificate(chart.name, len(minors), coefficients, identity)


def _canonical_line_frames(
    candidate: SerrePushoutCandidate,
) -> tuple[tuple[str, tuple[int, ...], Polynomial], ...]:
    """Return the selected Fitting frame and denominator on each chart."""

    records = []
    for pivot, columns in enumerate(candidate.transition_atlas.eliminated_columns):
        denominator = _frame_coordinates(candidate.relation, columns)[2]
        records.append((f"U_{pivot}_base", columns, denominator))
    return tuple(dict.fromkeys(records))


def _canonical_transitions(
    candidate: SerrePushoutCandidate,
    model: TierAPencilModel,
) -> tuple[tuple[str, str, FractionMatrix], ...]:
    """Build shift-corrected transitions on the six canonical chart frames."""

    pivots = candidate.transition_atlas.eliminated_columns
    frame_data = tuple(
        _frame_coordinates(candidate.relation, columns)
        for columns in pivots
    )
    transitions = []
    for source in model.blowup_atlas.charts:
        for target in model.blowup_atlas.charts:
            if source == target:
                continue
            matrix = (
                FractionMatrix.identity(2, 3)
                if source.base_pivot == target.base_pivot
                else _shifted_frame_transition(
                    source.base_pivot,
                    target.base_pivot,
                    frame_data[source.base_pivot],
                    frame_data[target.base_pivot],
                    candidate.target_shifts,
                )
            )
            transitions.append((source.name, target.name, matrix))
    return tuple(transitions)


def _transition_digest(
    transitions: tuple[tuple[str, str, FractionMatrix], ...],
) -> str:
    """Hash every generated line-frame transition without lossy formatting."""

    payload = [
        {
            "source": source,
            "target": target,
            "matrix": _matrix_record(matrix),
        }
        for source, target, matrix in transitions
    ]
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _transition_checks(
    model: TierAPencilModel,
    transitions: tuple[tuple[str, str, FractionMatrix], ...],
) -> tuple[bool, bool]:
    """Check exact inverse and triple-cocycle identities."""

    by_pair = {(source, target): matrix for source, target, matrix in transitions}
    names = tuple(chart.name for chart in model.blowup_atlas.charts)

    def transition(source: str, target: str) -> FractionMatrix:
        if source == target:
            return FractionMatrix.identity(2, 3)
        return by_pair[(source, target)]

    invertible = all(
        transition(source, target).compose(transition(target, source)).is_identity()
        for source in names
        for target in names
    )
    cocycle = all(
        transition(source, middle).compose(transition(middle, target))
        == transition(source, target)
        for source in names
        for middle in names
        for target in names
    )
    return invertible, cocycle


def global_serre_pushout_audit(
    candidate: SerrePushoutCandidate,
    model: TierAPencilModel | None = None,
) -> GlobalSerrePushoutAudit:
    """Construct the exact graded pullback audit for one Tier A pushout."""

    current = tier_a_pencil_model() if model is None else model
    local_relations = tuple(
        (
            chart.name,
            _chart_matrix(candidate.relation, chart)
            .compose(
                PolynomialMatrix(
                    tuple(
                        (entry,)
                        for entry in _chart_matrix(candidate.quotient, chart).rows[0]
                    )
                )
            ).is_zero(),
        )
        for chart in current.blowup_atlas.charts
    )
    fitting = tuple(
        _fitting_certificate(candidate.relation, chart)
        for chart in current.blowup_atlas.charts
    )
    transitions = _canonical_transitions(candidate, current)
    invertible, cocycle = _transition_checks(current, transitions)
    return GlobalSerrePushoutAudit(
        candidate.scheme.name,
        candidate.relation.shape,
        candidate.graded_relation,
        local_relations,
        fitting,
        _canonical_line_frames(candidate),
        transitions,
        invertible,
        cocycle,
        _transition_digest(transitions),
        (
            "graded pullback presentation is locally free on the six-chart dP9 "
            "atlas; quotient linearization and physical promotion remain pending"
        ),
    )


def tier_a_global_serre_pushout_audits(
    model: TierAPencilModel | None = None,
    candidates: tuple[SerrePushoutCandidate, ...] | None = None,
) -> tuple[GlobalSerrePushoutAudit, ...]:
    """Audit both newly constructed Tier A rank-two pushouts."""

    current = tier_a_pencil_model() if model is None else model
    selected = tier_a_serre_pushouts(current) if candidates is None else candidates
    return tuple(global_serre_pushout_audit(candidate, current) for candidate in selected)


__all__ = [
    "FittingUnitCertificate",
    "GlobalSerrePushoutAudit",
    "global_serre_pushout_audit",
    "tier_a_global_serre_pushout_audits",
]
