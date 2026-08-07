"""Induce corrected curvilinear actions on exact quotient frames.

Owns:
    Exact degree-zero frame matrices induced by corrected P/T presentation
    actions, their compatibility with principal-open quotient transitions,
    order-three checks, and local projective commutator comparisons.

Depends on:
    Support-free curvilinear eigenline relations, corrected middle actions,
    published coordinate lifts, exact fraction-field frame algebra, and the
    degree-corrected projective cocycle frontier.

Must not:
    Treat support-centered principal frames as a complete dP9 cover without a
    cover certificate, infer quotient descent from fraction-field identities,
    select a physical carrier, or bypass global Ext and stability gates.

Phase 0:
    Induced quotient-frame maps are audited exactly on the declared principal
    frames; complete dP9 cover descent and physical promotion remain open.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from functools import cache
from hashlib import sha256
from itertools import combinations

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialFraction, determinant

from .dp9_actions import CoordinateImage, published_coordinate_images
from .global_serre import _fraction_record
from .pencil import _pivot_images
from .serre_pushout import FractionMatrix, _relation_matrix
from .tier_b_curvilinear_actions import (
    TierBCurvilinearResolutionActionAudit,
    tier_b_curvilinear_resolution_actions,
)
from .tier_b_curvilinear_corrections import (
    CurvilinearRepresentativeCorrection,
    TierBCurvilinearCorrectionAudit,
    tier_b_curvilinear_correction_audits,
)
from .tier_b_curvilinear_eigenclasses import (
    CurvilinearPresentationEigenclass,
    TierBCurvilinearEigenclassAudit,
    tier_b_curvilinear_eigenclass_audits,
)
from .tier_b_curvilinear_projective_cocycles import (
    CurvilinearProjectiveCocycleLine,
    TierBCurvilinearProjectiveCocycleAudit,
    tier_b_curvilinear_projective_cocycle_audits,
)
from .tier_b_curvilinear_serre import (
    _bounded_unit_combination,
    _dual_presentation,
    _polynomial_record,
)

FrameData = tuple[tuple[int, ...], FractionMatrix, Polynomial]


@dataclass(frozen=True, slots=True)
class CurvilinearFittingCoverCertificate:
    """One affine-chart unit identity for all maximal relation minors."""

    base_pivot: int
    degree_bound: int
    nonzero_minor_count: int
    coefficients: tuple[tuple[int, Polynomial], ...]
    identity: Polynomial

    @property
    def exact(self) -> bool:
        """Return whether the displayed combination equals one exactly."""

        return self.identity == Polynomial.one(2, scalar_type=Eisenstein)

    def as_record(self) -> dict[str, object]:
        """Serialize the complete affine Fitting-cover identity."""

        return {
            "base_pivot": self.base_pivot,
            "dp9_charts": [f"U_{self.base_pivot}_mu", f"U_{self.base_pivot}_nu"],
            "degree_bound": self.degree_bound,
            "nonzero_minor_count": self.nonzero_minor_count,
            "coefficients": [
                {
                    "minor_index": index,
                    "coefficient": _polynomial_record(coefficient),
                }
                for index, coefficient in self.coefficients
                if not coefficient.is_zero()
            ],
            "identity": _polynomial_record(self.identity),
            "exact": self.exact,
        }


def _homogeneous_coordinate(index: int, degree: int) -> Polynomial:
    """Return one homogeneous coordinate raised to a nonnegative degree."""

    if index not in range(3):
        raise ValueError("homogeneous coordinate indices are 0, 1, and 2")
    if degree < 0:
        raise ValueError("frame shifts must be nonnegative")
    exponents = [0, 0, 0]
    exponents[index] = degree
    return Polynomial.monomial(tuple(exponents), scalar_type=Eisenstein)


def _fraction_matrix_record(matrix: FractionMatrix) -> list[list[dict[str, object]]]:
    """Serialize one exact fraction matrix without lossy formatting."""

    return [
        [_fraction_record(entry) for entry in row]
        for row in matrix.rows
    ]


def _matrix_digest(
    matrices: tuple[tuple[int, int, FractionMatrix], ...],
) -> str:
    """Hash one ordered family of exact local frame matrices."""

    payload = [
        {
            "source_pivot": source,
            "target_pivot": target,
            "matrix": _fraction_matrix_record(matrix),
        }
        for source, target, matrix in matrices
    ]
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode()).hexdigest()


def _target_pivot(source_pivot: int, images: CoordinateImage) -> int:
    """Return the target projective chart reached by one monomial lift."""

    candidates = tuple(
        target
        for target, (coefficient, exponents) in enumerate(images)
        if not coefficient.is_zero()
        and exponents[source_pivot] == 1
        and sum(exponents) == 1
    )
    if len(candidates) != 1:
        raise ValueError("coordinate lift does not map a pivot chart monomially")
    return candidates[0]


def _coordinate_order_three(images: CoordinateImage) -> bool:
    """Check one homogeneous coordinate substitution has exact order three."""

    for index in range(3):
        coordinate = _homogeneous_coordinate(index, 1)
        transformed = coordinate
        for _ in range(3):
            transformed = transformed.substitute_monomials(images)
        if transformed != coordinate:
            return False
    return True


def _frame_is_basis(frame: FrameData) -> bool:
    """Check that free generators have identity coordinates in one frame."""

    free_columns, coordinates, denominator = frame
    if denominator.is_zero():
        return False
    one = Polynomial.one(3, scalar_type=Eisenstein)
    return all(
        (
            entry.numerator == one and entry.denominator == one
            if row == column
            else entry.is_zero()
        )
        for row, generator in enumerate(free_columns)
        for column, entry in enumerate(coordinates.rows[generator])
    )


def _frame_relation_vanishes(relation, frame: FrameData) -> bool:
    """Check every relation has zero coordinates in one quotient frame."""

    _, coordinates, denominator = frame
    one = Polynomial.one(3, scalar_type=Eisenstein)
    zero = Polynomial.zero(3, scalar_type=Eisenstein)
    for relation_row in relation.rows:
        for frame_column in range(coordinates.shape[1]):
            numerator = zero
            for generator, relation_entry in enumerate(relation_row):
                coordinate = coordinates.rows[generator][frame_column]
                if coordinate.denominator == denominator:
                    contribution = relation_entry * coordinate.numerator
                elif coordinate.denominator == one:
                    contribution = (
                        relation_entry * coordinate.numerator * denominator
                    )
                else:
                    return False
                numerator += contribution
            if not numerator.is_zero():
                return False
    return True


def _frame_data(
    relation,
    eigenclass: CurvilinearPresentationEigenclass,
) -> tuple[FrameData, ...]:
    """Build one exact quotient frame at each coordinate support pivot."""

    column_sets = tuple(combinations(range(relation.shape[1]), relation.shape[0]))
    by_pivot: dict[int, FrameData] = {}
    for _, point, minor_indices in eigenclass.support_fitting:
        nonzero = tuple(index for index, value in enumerate(point) if not value.is_zero())
        if len(nonzero) != 1:
            raise ValueError("frame action audit requires the coordinate support orbit")
        if not minor_indices:
            raise ValueError("support-free eigenline has no local frame minor")
        pivot = nonzero[0]
        by_pivot[pivot] = _adjugate_frame_coordinates(
            relation,
            column_sets[minor_indices[0]],
        )
    if set(by_pivot) != set(range(3)):
        raise ValueError("coordinate support frames do not cover all three pivots")
    return tuple(by_pivot[pivot] for pivot in range(3))


def _adjugate_frame_coordinates(
    relation,
    eliminated_columns: tuple[int, ...],
) -> FrameData:
    """Build one rank-two frame with a common adjugate denominator."""

    relation_rows, generator_count = relation.shape
    if relation_rows != 3 or len(eliminated_columns) != 3:
        raise ValueError("curvilinear quotient frames require a 3 by 3 minor")
    free_columns = tuple(
        column
        for column in range(generator_count)
        if column not in eliminated_columns
    )
    if len(free_columns) != 2:
        raise ValueError("curvilinear quotient frames must have rank two")
    eliminated = tuple(
        tuple(relation.rows[row][column] for column in eliminated_columns)
        for row in range(3)
    )
    denominator = determinant(eliminated)
    if denominator.is_zero():
        raise ZeroDivisionError("selected curvilinear frame minor is zero")
    adjugate = tuple(
        tuple(
            determinant(
                tuple(
                    tuple(
                        eliminated[row][column]
                        for column in range(3)
                        if column != adjugate_row
                    )
                    for row in range(3)
                    if row != adjugate_column
                )
            ).scale(-1 if (adjugate_row + adjugate_column) % 2 else 1)
            for adjugate_column in range(3)
        )
        for adjugate_row in range(3)
    )
    free = tuple(
        tuple(relation.rows[row][column] for column in free_columns)
        for row in range(3)
    )
    eliminated_coordinates = tuple(
        tuple(
            -sum(
                (
                    adjugate[row][inner] * free[inner][column]
                    for inner in range(3)
                ),
                Polynomial.zero(3, scalar_type=Eisenstein),
            )
            for column in range(2)
        )
        for row in range(3)
    )
    one = Polynomial.one(3, scalar_type=Eisenstein)
    zero = Polynomial.zero(3, scalar_type=Eisenstein)
    coordinates = []
    for generator in range(generator_count):
        if generator in eliminated_columns:
            eliminated_row = eliminated_columns.index(generator)
            coordinates.append(
                tuple(
                    PolynomialFraction(
                        eliminated_coordinates[eliminated_row][column],
                        denominator,
                    )
                    for column in range(2)
                )
            )
        else:
            free_row = free_columns.index(generator)
            coordinates.append(
                tuple(
                    PolynomialFraction.from_polynomial(
                        one if free_row == column else zero
                    )
                    for column in range(2)
                )
            )
    return free_columns, FractionMatrix(tuple(coordinates)), denominator


def _fitting_frames(relation) -> tuple[tuple[tuple[int, ...], FrameData], ...]:
    """Construct every nonzero maximal-minor quotient frame."""

    frames = []
    for eliminated in combinations(range(relation.shape[1]), relation.shape[0]):
        frame = _adjugate_frame_coordinates(relation, eliminated)
        frames.append((eliminated, frame))
    return tuple(frames)


def _fitting_cover_certificates(
    relation,
) -> tuple[CurvilinearFittingCoverCertificate, ...]:
    """Prove maximal minors generate the unit ideal on every base chart."""

    minors = relation.minors(relation.shape[0])
    certificates = []
    for pivot in range(3):
        affine_minors = tuple(
            minor.substitute(_pivot_images(pivot))
            for minor in minors
        )
        degree_bound, coefficients = _bounded_unit_combination(
            affine_minors,
            maximum_degree=2,
        )
        identity = Polynomial.zero(2, scalar_type=Eisenstein)
        for index, coefficient in coefficients:
            identity += coefficient * affine_minors[index]
        certificates.append(
            CurvilinearFittingCoverCertificate(
                pivot,
                degree_bound,
                sum(not minor.is_zero() for minor in affine_minors),
                coefficients,
                identity,
            )
        )
    return tuple(certificates)


def _frame_transition(
    source_pivot: int,
    target_pivot: int,
    source_frame: FrameData,
    target_frame: FrameData,
    shifts: tuple[int, ...],
) -> FractionMatrix:
    """Express a target degree-zero quotient frame in a source frame."""

    source_free, source_coordinates, _ = source_frame
    target_free, _, _ = target_frame
    if len(source_free) != len(target_free):
        raise ValueError("quotient frames have incompatible ranks")
    columns = []
    for target_generator in target_free:
        column = []
        for row, source_generator in enumerate(source_free):
            factor = PolynomialFraction(
                _homogeneous_coordinate(
                    source_pivot,
                    shifts[source_generator],
                ),
                _homogeneous_coordinate(
                    target_pivot,
                    shifts[target_generator],
                ),
            )
            column.append(source_coordinates.rows[target_generator][row] * factor)
        columns.append(tuple(column))
    return FractionMatrix(
        tuple(
            tuple(columns[column][row] for column in range(len(columns)))
            for row in range(len(source_free))
        )
    )


def _transitions(
    frames: tuple[FrameData, ...],
    shifts: tuple[int, ...],
) -> dict[tuple[int, int], FractionMatrix]:
    """Construct every ordered base-pivot frame transition."""

    return {
        (source, target): (
            FractionMatrix.identity(2, 3)
            if source == target
            else _frame_transition(
                source,
                target,
                frames[source],
                frames[target],
                shifts,
            )
        )
        for source in range(3)
        for target in range(3)
    }


def _local_action_matrix(
    source_pivot: int,
    target_pivot: int,
    source_frame: FrameData,
    target_frame: FrameData,
    middle_action: Matrix,
    images: CoordinateImage,
    shifts: tuple[int, ...],
) -> FractionMatrix:
    """Express a corrected pullback action in degree-zero quotient frames."""

    source_free, source_coordinates, _ = source_frame
    frame_denominator = source_frame[2]
    target_free, _, _ = target_frame
    target_coordinate = _homogeneous_coordinate(target_pivot, 1)
    pulled_target_coordinate = target_coordinate.substitute_monomials(images)
    columns = []
    for target_generator in target_free:
        column = []
        for row, source_generator in enumerate(source_free):
            coefficient = _coordinate_linear_combination(
                source_coordinates,
                row,
                middle_action.rows[target_generator],
                frame_denominator,
            )
            factor = PolynomialFraction(
                _homogeneous_coordinate(
                    source_pivot,
                    shifts[source_generator],
                ),
                pulled_target_coordinate ** shifts[target_generator],
            )
            column.append(coefficient * factor)
        columns.append(tuple(column))
    return FractionMatrix(
        tuple(
            tuple(columns[column][row] for column in range(len(columns)))
            for row in range(len(source_free))
        )
    )


def _coordinate_linear_combination(
    coordinates: FractionMatrix,
    frame_row: int,
    coefficients: tuple[object, ...],
    frame_denominator: Polynomial,
) -> PolynomialFraction:
    """Combine frame coordinates over their declared common denominator."""

    one = Polynomial.one(3, scalar_type=Eisenstein)
    numerator = Polynomial.zero(3, scalar_type=Eisenstein)
    for generator, raw_coefficient in enumerate(coefficients):
        coefficient = Eisenstein.coerce(raw_coefficient)
        if coefficient.is_zero():
            continue
        entry = coordinates.rows[generator][frame_row]
        if entry.denominator == frame_denominator:
            contribution = entry.numerator
        elif entry.denominator == one:
            contribution = entry.numerator * frame_denominator
        else:
            raise ValueError("frame coordinate escaped its common denominator")
        numerator += contribution.scale(coefficient)
    return PolynomialFraction(numerator, frame_denominator)


@dataclass(frozen=True, slots=True)
class CurvilinearLocalFrameAction:
    """One corrected generator action on all three support-centered frames."""

    generator: str
    variant: str
    local_matrices: tuple[tuple[int, int, FractionMatrix], ...]
    all_invertible: bool
    overlap_compatible: bool
    order_three: bool
    coordinate_derived: bool
    matrix_digest: str

    @property
    def exact(self) -> bool:
        """Return whether all local action gates pass exactly."""

        return (
            self.all_invertible
            and self.overlap_compatible
            and self.order_three
            and self.coordinate_derived
        )

    def as_record(self) -> dict[str, object]:
        """Serialize every local matrix and its exact compatibility gates."""

        return {
            "generator": self.generator,
            "variant": self.variant,
            "local_matrices": [
                {
                    "source_pivot": source,
                    "target_pivot": target,
                    "matrix": _fraction_matrix_record(matrix),
                }
                for source, target, matrix in self.local_matrices
            ],
            "all_invertible": self.all_invertible,
            "overlap_compatible": self.overlap_compatible,
            "order_three": self.order_three,
            "coordinate_derived": self.coordinate_derived,
            "matrix_digest": self.matrix_digest,
            "exact": self.exact,
        }


def _action_family_record(
    actions: tuple[CurvilinearLocalFrameAction, ...],
) -> dict[str, object]:
    """Serialize variants with one exact matrix payload per distinct digest."""

    unique: dict[str, CurvilinearLocalFrameAction] = {}
    for action in actions:
        unique.setdefault(action.matrix_digest, action)
    return {
        "variant_count": len(actions),
        "distinct_matrix_count": len(unique),
        "variants": [
            {
                "generator": action.generator,
                "variant": action.variant,
                "matrix_digest": action.matrix_digest,
                "exact": action.exact,
            }
            for action in actions
        ],
        "distinct_matrices": [
            action.as_record()
            for action in unique.values()
        ],
    }


@dataclass(frozen=True, slots=True)
class CurvilinearFrameLinearizationLine:
    """Induced frame-action frontier for one corrected eigenline."""

    eigenline_index: int
    frame_columns: tuple[tuple[int, ...], ...]
    frame_denominators: tuple[Polynomial, ...]
    frame_bases_verified: bool
    fitting_frames: tuple[tuple[tuple[int, ...], tuple[int, ...], Polynomial], ...]
    fitting_frame_bases_verified: bool
    fitting_cover_certificates: tuple[CurvilinearFittingCoverCertificate, ...]
    transition_cocycle_derived: bool
    transition_digest: str
    p_actions: tuple[CurvilinearLocalFrameAction, ...]
    t_actions: tuple[CurvilinearLocalFrameAction, ...]
    occurrence_count: int
    commuting_occurrence_count: int

    @property
    def exact(self) -> bool:
        """Return whether every local action and P/T occurrence passes."""

        return (
            self.occurrence_count > 0
            and self.commuting_occurrence_count == self.occurrence_count
            and self.frame_bases_verified
            and self.fitting_frame_bases_verified
            and len(self.fitting_frames) == 10
            and len(self.fitting_cover_certificates) == 3
            and all(certificate.exact for certificate in self.fitting_cover_certificates)
            and self.transition_cocycle_derived
            and all(action.exact for action in (*self.p_actions, *self.t_actions))
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact frame frontier without claiming a full cover."""

        return {
            "eigenline_index": self.eigenline_index,
            "frames": [
                {
                    "pivot": pivot,
                    "free_columns": list(columns),
                    "denominator": _polynomial_record(denominator),
                }
                for pivot, (columns, denominator) in enumerate(
                    zip(self.frame_columns, self.frame_denominators, strict=True)
                )
            ],
            "frame_bases_verified": self.frame_bases_verified,
            "fitting_frames": [
                {
                    "minor_index": index,
                    "eliminated_columns": list(eliminated),
                    "free_columns": list(free),
                    "denominator": _polynomial_record(denominator),
                }
                for index, (eliminated, free, denominator) in enumerate(
                    self.fitting_frames
                )
            ],
            "fitting_frame_count": len(self.fitting_frames),
            "fitting_frame_bases_verified": self.fitting_frame_bases_verified,
            "fitting_cover_certificates": [
                certificate.as_record()
                for certificate in self.fitting_cover_certificates
            ],
            "fitting_cover_verified": all(
                certificate.exact
                for certificate in self.fitting_cover_certificates
            ),
            "covered_dp9_chart_count": 6,
            "transition_cocycle_derived": self.transition_cocycle_derived,
            "transition_digest": self.transition_digest,
            "p_action_family": _action_family_record(self.p_actions),
            "t_action_family": _action_family_record(self.t_actions),
            "occurrence_count": self.occurrence_count,
            "commuting_occurrence_count": self.commuting_occurrence_count,
            "exact": self.exact,
            "selected_as_physics": False,
            "status": (
                "exact induced actions on support-centered frames with a full "
                "maximal-minor dP9 cover; explicit full-cover action matrices "
                "and quotient descent remain unresolved"
            ),
        }


@dataclass(frozen=True, slots=True)
class TierBCurvilinearFrameActionAudit:
    """Induced quotient-frame frontier for one curvilinear specialization."""

    scheme: str
    support_free_eigenline_count: int
    scoped_no_correction_eigenline_count: int
    lines: tuple[CurvilinearFrameLinearizationLine, ...]

    @property
    def frame_linearized_eigenline_count(self) -> int:
        """Return corrected lines passing all declared local-frame gates."""

        return sum(line.exact for line in self.lines)

    @property
    def fitting_cover_eigenline_count(self) -> int:
        """Return lines with all ten frames and three exact chart identities."""

        return sum(
            len(line.fitting_frames) == 10
            and len(line.fitting_cover_certificates) == 3
            and all(
                certificate.exact
                for certificate in line.fitting_cover_certificates
            )
            for line in self.lines
        )

    @property
    def exact(self) -> bool:
        """Return whether every available finite frame audit has a result."""

        return (
            len(self.lines) + self.scoped_no_correction_eigenline_count
            == self.support_free_eigenline_count
            and all(line.exact for line in self.lines)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the finite frame-action result and cover boundary."""

        return {
            "scheme": self.scheme,
            "support_free_eigenline_count": self.support_free_eigenline_count,
            "scoped_no_correction_eigenline_count": (
                self.scoped_no_correction_eigenline_count
            ),
            "corrected_eigenline_count": len(self.lines),
            "frame_linearized_eigenline_count": (
                self.frame_linearized_eigenline_count
            ),
            "fitting_cover_eigenline_count": self.fitting_cover_eigenline_count,
            "lines": [line.as_record() for line in self.lines],
            "exact": self.exact,
            "status": (
                "exact quotient-frame action and maximal-minor dP9 cover "
                "frontier; full-cover action matrices, deck chart descent, "
                "global Ext, and promotion remain open"
            ),
        }


def _action_audit(
    generator: str,
    variant: str,
    middle_action: Matrix,
    frames: tuple[FrameData, ...],
    transitions: dict[tuple[int, int], FractionMatrix],
    shifts: tuple[int, ...],
    relation_equation: bool,
    middle_order_three: bool,
    frame_bases_verified: bool,
) -> CurvilinearLocalFrameAction:
    """Construct one generator's local matrices and exact compatibility checks."""

    images = published_coordinate_images(generator)
    local = tuple(
        (
            source,
            _target_pivot(source, images),
            _local_action_matrix(
                source,
                _target_pivot(source, images),
                frames[source],
                frames[_target_pivot(source, images)],
                middle_action,
                images,
                shifts,
            ),
        )
        for source in range(3)
    )
    by_source = {source: matrix for source, _, matrix in local}
    coordinate_derived = (
        len(by_source) == 3
        and all(matrix.shape == (2, 2) for matrix in by_source.values())
        and frame_bases_verified
    )
    order_three = middle_order_three and _coordinate_order_three(images)
    overlap = coordinate_derived and relation_equation
    return CurvilinearLocalFrameAction(
        generator,
        variant,
        local,
        coordinate_derived and order_three,
        overlap,
        order_three,
        coordinate_derived,
        _matrix_digest(local),
    )


def _unique_local_actions(
    generator: str,
    corrected_actions: tuple[object, ...],
    frames: tuple[FrameData, ...],
    transitions: dict[tuple[int, int], FractionMatrix],
    shifts: tuple[int, ...],
) -> tuple[CurvilinearLocalFrameAction, ...]:
    """Build one local audit per distinct matrix while retaining variants."""

    by_matrix: dict[tuple[tuple[object, ...], ...], CurvilinearLocalFrameAction] = {}
    result = []
    for action in corrected_actions:
        if not action.compatible or action.matrix is None:
            continue
        key = action.matrix.rows
        audit = by_matrix.get(key)
        if audit is None:
            audit = _action_audit(
                generator,
                action.variant,
                action.matrix,
                frames,
                transitions,
                shifts,
                action.relation_equation,
                action.order_three,
                all(_frame_is_basis(frame) for frame in frames),
            )
            by_matrix[key] = audit
        result.append(
            audit if audit.variant == action.variant else replace(audit, variant=action.variant)
        )
    return tuple(result)


def _line_audit(
    eigenline_index: int,
    eigenclass: CurvilinearPresentationEigenclass,
    correction: CurvilinearRepresentativeCorrection,
    projective_line: CurvilinearProjectiveCocycleLine,
    action_audit: TierBCurvilinearResolutionActionAudit,
    target_line_shift: int,
) -> CurvilinearFrameLinearizationLine:
    """Induce all corrected actions on one eigenline's exact quotient frames."""

    generator_degrees, _, _, _, _ = _dual_presentation(
        action_audit.specialization,
        target_line_shift,
    )
    shifts = (*generator_degrees, target_line_shift)
    relation = _relation_matrix(
        action_audit.specialization.point_scheme,
        eigenclass.extension_map,
    )
    frames = _frame_data(relation, eigenclass)
    frame_bases_verified = all(
        _frame_is_basis(frame) and _frame_relation_vanishes(relation, frame)
        for frame in frames
    )
    fitting_frame_data = _fitting_frames(relation)
    fitting_frame_bases_verified = all(
        _frame_is_basis(frame) and _frame_relation_vanishes(relation, frame)
        for _, frame in fitting_frame_data
    )
    fitting_cover_certificates = _fitting_cover_certificates(relation)
    transitions = _transitions(frames, shifts)
    p_actions = _unique_local_actions(
        "P",
        correction.p_actions,
        frames,
        transitions,
        shifts,
    )
    if (
        projective_line.eigenline_index != eigenline_index
        or projective_line.occurrence_count != eigenclass.occurrence_count
        or not projective_line.exact
    ):
        raise ValueError("frame action requires a matching exact projective cocycle")
    if correction.corrected_character_occurrence_count != eigenclass.occurrence_count:
        raise ValueError("frame audit requires every class occurrence to be corrected")
    t_actions = _unique_local_actions(
        "T",
        correction.t_actions,
        frames,
        transitions,
        shifts,
    )
    transition_tuple = tuple(
        (source, target, matrix)
        for (source, target), matrix in sorted(transitions.items())
    )
    return CurvilinearFrameLinearizationLine(
        eigenline_index,
        tuple(frame[0] for frame in frames),
        tuple(frame[2] for frame in frames),
        frame_bases_verified,
        tuple(
            (eliminated, frame[0], frame[2])
            for eliminated, frame in fitting_frame_data
        ),
        fitting_frame_bases_verified,
        fitting_cover_certificates,
        frame_bases_verified and fitting_frame_bases_verified,
        _matrix_digest(transition_tuple),
        p_actions,
        t_actions,
        eigenclass.occurrence_count,
        projective_line.complete_cocycle_occurrence_count,
    )


def _audit_one(
    action_audit: TierBCurvilinearResolutionActionAudit,
    eigen_audit: TierBCurvilinearEigenclassAudit,
    correction_audit: TierBCurvilinearCorrectionAudit,
    projective_audit: TierBCurvilinearProjectiveCocycleAudit,
    target_line_shift: int,
) -> TierBCurvilinearFrameActionAudit:
    """Construct the support-centered frame frontier for one specialization."""

    if not (
        action_audit.specialization.name
        == eigen_audit.scheme
        == correction_audit.scheme
        == projective_audit.scheme
    ):
        raise ValueError("frame-action inputs describe different schemes")
    eigenclasses = {
        index: eigenclass
        for index, eigenclass in enumerate(eigen_audit.eigenclasses)
        if eigenclass.support_locally_free
    }
    projective_lines = {
        line.eigenline_index: line
        for line in projective_audit.lines
        if line.exact
    }
    lines = tuple(
        _line_audit(
            correction.eigenline_index,
            eigenclasses[correction.eigenline_index],
            correction,
            projective_lines[correction.eigenline_index],
            action_audit,
            target_line_shift,
        )
        for correction in correction_audit.corrections
        if correction.eigenline_index in projective_lines
    )
    return TierBCurvilinearFrameActionAudit(
        eigen_audit.scheme,
        eigen_audit.support_locally_free_eigenclass_count,
        correction_audit.scoped_no_correction_eigenline_count,
        lines,
    )


@cache
def _cached_audits(
    parameter: Eisenstein,
    target_line_shift: int,
) -> tuple[TierBCurvilinearFrameActionAudit, ...]:
    """Cache the exact support-centered frame-action frontier."""

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
    projective = tier_b_curvilinear_projective_cocycle_audits(
        parameter,
        target_line_shift,
        actions,
        eigenclasses,
        corrections,
    )
    return tuple(
        _audit_one(action, eigen, correction, cocycle, target_line_shift)
        for action, eigen, correction, cocycle in zip(
            actions,
            eigenclasses,
            corrections,
            projective,
            strict=True,
        )
    )


def tier_b_curvilinear_frame_action_audits(
    parameter: object = Eisenstein(1),
    target_line_shift: int = 3,
    action_audits: tuple[TierBCurvilinearResolutionActionAudit, ...] | None = None,
    eigenclass_audits: tuple[TierBCurvilinearEigenclassAudit, ...] | None = None,
    correction_audits: tuple[TierBCurvilinearCorrectionAudit, ...] | None = None,
    projective_audits: tuple[TierBCurvilinearProjectiveCocycleAudit, ...]
    | None = None,
) -> tuple[TierBCurvilinearFrameActionAudit, ...]:
    """Return induced corrected actions on support-centered quotient frames."""

    value = Eisenstein.coerce(parameter)
    if value.is_zero():
        raise ValueError("the curvilinear parameter must be nonzero")
    if isinstance(target_line_shift, bool) or not isinstance(target_line_shift, int):
        raise TypeError("the target-line shift must be an integer")
    if all(
        item is None
        for item in (
            action_audits,
            eigenclass_audits,
            correction_audits,
            projective_audits,
        )
    ):
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
        projective = (
            tier_b_curvilinear_projective_cocycle_audits(
                value,
                target_line_shift,
                actions,
                eigenclasses,
                corrections,
            )
            if projective_audits is None
            else projective_audits
        )
        if not (
            len(actions)
            == len(eigenclasses)
            == len(corrections)
            == len(projective)
        ):
            raise ValueError("frame-action inputs require matching audit counts")
        audits = tuple(
            _audit_one(action, eigen, correction, cocycle, target_line_shift)
            for action, eigen, correction, cocycle in zip(
                actions,
                eigenclasses,
                corrections,
                projective,
                strict=True,
            )
        )
    if len(audits) != 8 or not all(audit.exact for audit in audits):
        raise ValueError("curvilinear frame-action audit failed exact gates")
    return audits


__all__ = [
    "CurvilinearFrameLinearizationLine",
    "CurvilinearLocalFrameAction",
    "TierBCurvilinearFrameActionAudit",
    "tier_b_curvilinear_frame_action_audits",
]
