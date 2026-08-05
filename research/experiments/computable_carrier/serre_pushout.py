"""Construct exact Hilbert--Burch Serre pushout presentations.

Owns:
    New Tier A extension maps from the displayed point-scheme resolutions,
    their polynomial pushout relations, quotient identities, local Fitting
    minors, and exact character-action checks on the selected extension line.

Depends on:
    The production I3/I6 resolutions, derived resolution actions, the finite
    dual-presentation action diagnostic, and exact polynomial and Eisenstein
    arithmetic. It does not import observations or the published bundle.

Must not:
    Call a base projective pushout a completed dP9 bundle, reuse a published
    cocycle, infer stability or spectrum, or hide a failed full linearization.

Phase 0:
    Exact base pushout presentations and support-local freeness are provided;
    dP9 line-frame descent, global atlas gluing, and quotient promotion remain
    explicit gates.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialMatrix
from onetheory.models.heterotic_schoen.visible import PointScheme, point_schemes

from .dual_cokernels import (
    DualResolutionCokernel,
    _target_action,
    dual_resolution_cokernel,
)
from .pencil import (
    BlowupChart,
    TierAPencilModel,
    _embed_affine_polynomial,
    _pivot_images,
    tier_a_pencil_model,
)
from .resolution_actions import ResolutionActionPair, tier_a_resolution_actions

Point = tuple[int, int, int]
CHARACTERS = (Eisenstein(1), OMEGA, OMEGA2)
POINTS: tuple[tuple[str, Point], ...] = (
    ("p_a", (1, 0, 0)),
    ("p_b", (0, 1, 0)),
    ("p_c", (0, 0, 1)),
)


def _constant(value: Eisenstein, variable_count: int = 3) -> Polynomial:
    """Return one exact constant polynomial."""

    return Polynomial.monomial((0,) * variable_count, value, scalar_type=Eisenstein)


def _zero_polynomial(variable_count: int = 3) -> Polynomial:
    """Return one exact zero polynomial in the carrier coordinate ring."""

    return Polynomial.zero(variable_count, scalar_type=Eisenstein)


def _stacked_equations(left: Matrix, right: Matrix, left_value: Eisenstein,
                       right_value: Eisenstein) -> Matrix:
    """Build exact simultaneous-eigenvector equations for two actions."""

    identity_left = Matrix.identity(left.row_count, scalar_type=Eisenstein)
    identity_right = Matrix.identity(right.row_count, scalar_type=Eisenstein)
    return Matrix(
        (
            *((left - identity_left.scale(left_value)).rows),
            *((right - identity_right.scale(right_value)).rows),
        ),
        scalar_type=Eisenstein,
    )


def _row_vector(values: Iterable[Eisenstein]) -> Matrix:
    """Return a column of exact coefficients for one extension class."""

    return Matrix(((value,) for value in values), scalar_type=Eisenstein)


def _polynomial_from_basis(
    basis: tuple[tuple[int, tuple[int, ...]], ...],
    values: tuple[Eisenstein, ...],
    column: int,
) -> Polynomial:
    """Assemble one polynomial component from a dual-resolution basis."""

    terms = tuple(
        (monomial, values[index])
        for index, (basis_column, monomial) in enumerate(basis)
        if basis_column == column and not values[index].is_zero()
    )
    return Polynomial(terms, variable_count=3, scalar_type=Eisenstein)


def _evaluate(polynomial: Polynomial, point: Point) -> Eisenstein:
    """Evaluate one exact homogeneous polynomial at an integral point."""

    value = Eisenstein(0)
    for exponents, coefficient in polynomial.terms:
        term = coefficient
        for coordinate, exponent in zip(point, exponents, strict=True):
            term *= Eisenstein(coordinate) ** exponent
        value += term
    return value


def _relation_matrix(
    scheme: PointScheme,
    extension_map: tuple[Polynomial, ...],
) -> PolynomialMatrix:
    """Push out the Hilbert--Burch relations by the extension map."""

    matrix = scheme.resolution.matrix
    if len(extension_map) != len(matrix[0]):
        raise ValueError("extension-map length must equal the resolution source rank")
    return PolynomialMatrix(
        tuple(
            tuple(matrix[row][column] for row in range(len(matrix)))
            + (-extension_map[column],)
            for column in range(len(matrix[0]))
        )
    )


def _quotient_row(
    scheme: PointScheme,
    variable_count: int = 3,
) -> PolynomialMatrix:
    """Map the pushout generators onto the declared ideal generators."""

    return PolynomialMatrix((tuple(scheme.ideal_generators) + (_zero_polynomial(variable_count),),))


def _relation_composes_to_zero(
    relation: PolynomialMatrix,
    quotient: PolynomialMatrix,
) -> bool:
    """Check that every pushout relation maps to zero in the ideal."""

    quotient_column = PolynomialMatrix(tuple((entry,) for entry in quotient.rows[0]))
    return relation.compose(quotient_column).is_zero()


def _relation_shifts(
    scheme: PointScheme,
    extension_map: tuple[Polynomial, ...],
) -> tuple[tuple[int, ...], tuple[int, ...], bool]:
    """Derive free-module shifts and verify every pushout entry is graded."""

    generator_degrees = {
        generator.degree
        for generator in scheme.ideal_generators
        if not generator.is_zero()
    }
    matrix_degrees = {
        entry.degree
        for row in scheme.resolution.matrix
        for entry in row
        if not entry.is_zero()
    }
    extension_degrees = {entry.degree for entry in extension_map if not entry.is_zero()}
    if len(generator_degrees) != 1 or len(matrix_degrees) != 1 or len(extension_degrees) != 1:
        raise ValueError("Serre pushout terms must have homogeneous degree data")
    generator_degree = next(iter(generator_degrees))
    matrix_degree = next(iter(matrix_degrees))
    extension_degree = next(iter(extension_degrees))
    source_shift = generator_degree + matrix_degree
    target_shifts = (generator_degree,) * len(scheme.resolution.matrix) + (
        source_shift - extension_degree,
    )
    source_shifts = (source_shift,) * len(scheme.resolution.matrix[0])
    relation = _relation_matrix(scheme, extension_map)
    graded = all(
        entry.is_zero()
        or entry.degree == source_shifts[row] - target_shifts[column]
        for row, relation_row in enumerate(relation.rows)
        for column, entry in enumerate(relation_row)
    )
    return source_shifts, target_shifts, graded


def _local_fitting_data(
    relation: PolynomialMatrix,
) -> tuple[tuple[str, bool, tuple[int, ...]], ...]:
    """Evaluate every maximal relation minor at the three support points."""

    relation_rank = relation.shape[0]
    minors = relation.minors(relation_rank)
    records = []
    for name, point in POINTS:
        nonzero_indices = tuple(
            index
            for index, minor in enumerate(minors)
            if not _evaluate(minor, point).is_zero()
        )
        records.append((name, bool(nonzero_indices), nonzero_indices))
    return tuple(records)


def _chart_matrix(matrix: PolynomialMatrix, chart: BlowupChart) -> PolynomialMatrix:
    """Pull one homogeneous matrix into a three-variable affine chart."""

    images = _pivot_images(chart.base_pivot)
    return PolynomialMatrix(
        tuple(
            tuple(_embed_affine_polynomial(entry.substitute(images)) for entry in row)
            for row in matrix.rows
        )
    )


@dataclass(frozen=True, slots=True)
class ChartPushoutRecord:
    """One exact affine chart presentation of a base pushout."""

    chart: str
    base_pivot: int
    fiber_chart: str
    relation_shape: tuple[int, int]
    relation_composes_to_zero: bool

    def as_record(self) -> dict[str, object]:
        """Serialize chart identity and its local quotient check."""

        return {
            "chart": self.chart,
            "base_pivot": self.base_pivot,
            "fiber_chart": self.fiber_chart,
            "relation_shape": list(self.relation_shape),
            "relation_composes_to_zero": self.relation_composes_to_zero,
        }


def _chart_pushout_records(
    relation: PolynomialMatrix,
    quotient: PolynomialMatrix,
    model: TierAPencilModel,
) -> tuple[ChartPushoutRecord, ...]:
    """Pull one pushout to every declared affine blow-up chart."""

    records = []
    for chart in model.blowup_atlas.charts:
        local_relation = _chart_matrix(relation, chart)
        local_quotient = _chart_matrix(quotient, chart)
        quotient_column = PolynomialMatrix(
            tuple((entry,) for entry in local_quotient.rows[0])
        )
        records.append(
            ChartPushoutRecord(
                chart.name,
                chart.base_pivot,
                chart.fiber_chart,
                local_relation.shape,
                local_relation.compose(quotient_column).is_zero(),
            )
        )
    return tuple(records)


def _i3_class(
    pair: ResolutionActionPair,
) -> tuple[tuple[Polynomial, ...], tuple[Eisenstein, Eisenstein]]:
    """Derive the first local-free I3 eigenclass from the constant dual term."""

    p_action = pair.action("P").source_action.transpose()
    t_action = pair.action("T").source_action.transpose()
    equations = _stacked_equations(p_action, t_action, OMEGA, Eisenstein(1))
    vectors = equations.nullspace()
    if len(vectors) != 1:
        raise ValueError("I3 constant dual term must have one selected eigenline")
    values = vectors[0].values
    return tuple(_constant(value) for value in values), (OMEGA, Eisenstein(1))


def _full_dual_vector(
    cokernel: DualResolutionCokernel,
    quotient_vector: tuple[Eisenstein, ...],
) -> tuple[Eisenstein, ...]:
    """Lift a quotient representative into the deterministic dual basis."""

    values = [Eisenstein(0) for _ in cokernel.target_basis]
    for value, index in zip(quotient_vector, cokernel.representative_indices, strict=True):
        values[index] = value
    return tuple(values)


def _i6_class(
    pair: ResolutionActionPair,
    scheme: PointScheme,
) -> tuple[tuple[Polynomial, ...], tuple[Eisenstein, Eisenstein], DualResolutionCokernel]:
    """Derive the local-free I6 eigenclass from the exact dual cokernel."""

    cokernel = dual_resolution_cokernel(scheme, pair.actions)
    full_actions = tuple(_target_action(cokernel.target_basis, action) for action in pair.actions)
    for p_value in CHARACTERS:
        for t_value in CHARACTERS:
            equations = _stacked_equations(
                cokernel.action("P").matrix,
                cokernel.action("T").matrix,
                p_value,
                t_value,
            )
            vectors = equations.nullspace()
            for vector in vectors:
                values = _full_dual_vector(cokernel, vector.values)
                if not all(
                    action @ _row_vector(values)
                    == _row_vector(values).scale(character)
                    for action, character in zip(
                        full_actions,
                        (p_value, t_value),
                        strict=True,
                    )
                ):
                    continue
                extension_map = tuple(
                    _polynomial_from_basis(cokernel.target_basis, values, column)
                    for column in range(3)
                )
                relation = _relation_matrix(scheme, extension_map)
                if all(record[1] for record in _local_fitting_data(relation)):
                    return extension_map, (p_value, t_value), cokernel
    raise ValueError("no exact I6 dual eigenclass passes all local Fitting gates")


@dataclass(frozen=True, slots=True)
class PushoutLinearization:
    """One exact character action on a selected extension class."""

    generator: str
    character: Eisenstein
    class_eigenvector: bool
    full_action_order_three: bool
    full_actions_commute: bool

    def as_record(self) -> dict[str, object]:
        """Serialize the action and preserve full-versus-class scope."""

        return {
            "generator": self.generator,
            "character": str(self.character),
            "class_eigenvector": self.class_eigenvector,
            "full_action_order_three": self.full_action_order_three,
            "full_actions_commute": self.full_actions_commute,
        }


@dataclass(frozen=True, slots=True)
class SerrePushoutCandidate:
    """One exact rank-two base pushout with support-local gates."""

    scheme: PointScheme
    extension_map: tuple[Polynomial, ...]
    character_pair: tuple[Eisenstein, Eisenstein]
    relation: PolynomialMatrix
    quotient: PolynomialMatrix
    relation_composes_to_zero: bool
    source_shifts: tuple[int, ...]
    target_shifts: tuple[int, ...]
    graded_relation: bool
    local_fitting: tuple[tuple[str, bool, tuple[int, ...]], ...]
    chart_records: tuple[ChartPushoutRecord, ...]
    linearizations: tuple[PushoutLinearization, ...]
    source_rank: int
    middle_rank: int
    status: str

    @property
    def locally_free_at_support(self) -> bool:
        """Return whether every declared support point has a unit Fitting minor."""

        return all(item[1] for item in self.local_fitting)

    @property
    def relation_rank(self) -> int:
        """Return the exact number of pushout relations."""

        return self.relation.shape[0]

    def as_record(self) -> dict[str, object]:
        """Serialize the complete base pushout presentation and gates."""

        def polynomial_record(polynomial: Polynomial) -> dict[str, object]:
            return {
                "terms": [
                    {
                        "exponents": list(exponents),
                        "coefficient": str(coefficient),
                    }
                    for exponents, coefficient in polynomial.terms
                ]
            }

        return {
            "scheme": self.scheme.name,
            "extension_map": [polynomial_record(item) for item in self.extension_map],
            "character_pair": [str(value) for value in self.character_pair],
            "relation": [
                [polynomial_record(item) for item in row]
                for row in self.relation.rows
            ],
            "quotient": [
                [polynomial_record(item) for item in row]
                for row in self.quotient.rows
            ],
            "relation_composes_to_zero": self.relation_composes_to_zero,
            "source_shifts": list(self.source_shifts),
            "target_shifts": list(self.target_shifts),
            "graded_relation": self.graded_relation,
            "relation_shape": list(self.relation.shape),
            "relation_rank": self.relation_rank,
            "middle_rank": self.middle_rank,
            "local_fitting": [
                {
                    "point": point,
                    "unit_minor_exists": unit,
                    "unit_minor_indices": list(indices),
                }
                for point, unit, indices in self.local_fitting
            ],
            "locally_free_at_support": self.locally_free_at_support,
            "chart_records": [item.as_record() for item in self.chart_records],
            "linearizations": [item.as_record() for item in self.linearizations],
            "status": self.status,
        }


def _linearization_records(
    pair: ResolutionActionPair,
    character_pair: tuple[Eisenstein, Eisenstein],
    extension_map: tuple[Polynomial, ...],
    cokernel: DualResolutionCokernel | None,
) -> tuple[PushoutLinearization, ...]:
    """Certify selected-class eigenvectors and full action relations."""

    if cokernel is None:
        actions = tuple(action.source_action.transpose() for action in pair.actions)
        vector = _row_vector(tuple(value for polynomial in extension_map
                                   for _, value in polynomial.terms))
        # I3 uses constants and therefore has one coefficient per component.
        vector = _row_vector(tuple(polynomial.coefficient((0, 0, 0))
                                   for polynomial in extension_map))
    else:
        target_basis = cokernel.target_basis
        # Reconstruct the deterministic full coefficient vector in basis order.
        values_list = [Eisenstein(0) for _ in target_basis]
        for index, (column, monomial) in enumerate(target_basis):
            values_list[index] = extension_map[column].coefficient(monomial)
        vector = _row_vector(values_list)
        actions = tuple(_target_action(target_basis, action) for action in pair.actions)
    records = []
    for index, (action, character) in enumerate(zip(actions, character_pair, strict=True)):
        records.append(
            PushoutLinearization(
                ("P", "T")[index],
                character,
                action @ vector == vector.scale(character),
                action**3 == Matrix.identity(action.row_count, scalar_type=Eisenstein),
                actions[0] @ actions[1] == actions[1] @ actions[0],
            )
        )
    return tuple(records)


def _candidate(
    scheme: PointScheme,
    pair: ResolutionActionPair,
    model: TierAPencilModel,
) -> SerrePushoutCandidate:
    """Build one deterministic exact pushout candidate."""

    cokernel: DualResolutionCokernel | None = None
    if scheme.name == "I3":
        extension_map, character_pair = _i3_class(pair)
    elif scheme.name == "I6":
        extension_map, character_pair, cokernel = _i6_class(pair, scheme)
    else:
        raise ValueError("Tier A pushouts require I3 or I6")
    relation = _relation_matrix(scheme, extension_map)
    quotient = _quotient_row(scheme)
    source_shifts, target_shifts, graded_relation = _relation_shifts(
        scheme,
        extension_map,
    )
    local_fitting = _local_fitting_data(relation)
    chart_records = _chart_pushout_records(relation, quotient, model)
    linearizations = _linearization_records(
        pair,
        character_pair,
        extension_map,
        cokernel,
    )
    return SerrePushoutCandidate(
        scheme,
        extension_map,
        character_pair,
        relation,
        quotient,
        _relation_composes_to_zero(relation, quotient),
        source_shifts,
        target_shifts,
        graded_relation,
        local_fitting,
        chart_records,
        linearizations,
        len(scheme.resolution.matrix[0]),
        len(scheme.resolution.matrix) + 1 - len(scheme.resolution.matrix[0]),
        (
            "base projective Serre pushout constructed; dP9 line-frame descent "
            "and full bundle promotion pending"
        ),
    )


def tier_a_serre_pushouts(
    model: TierAPencilModel | None = None,
) -> tuple[SerrePushoutCandidate, ...]:
    """Construct exact I3/I6 pushouts from newly derived extension maps."""

    schemes = point_schemes()
    actions = tier_a_resolution_actions()
    current = tier_a_pencil_model() if model is None else model
    return tuple(
        _candidate(scheme, pair, current)
        for scheme, pair in zip(schemes, actions, strict=True)
    )


__all__ = ["PushoutLinearization", "SerrePushoutCandidate", "tier_a_serre_pushouts"]
