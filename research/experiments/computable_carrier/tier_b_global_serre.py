"""Audit Tier B Serre presentations on the complete dP9 chart atlas.

Owns:
    Exact six-chart relation compositions, Fitting-unit certificates, graded
    line-frame transitions, and inverse/cocycle checks for every bounded Tier B
    Serre eigenray.

Depends on:
    Tier B graded Serre rays, the explicit cubic-pencil blow-up atlas, exact
    polynomial fraction matrices, and the reusable Fitting and frame algebra.
    It does not consume observations or numerical parameters.

Must not:
    Call a chart atlas a global quotient descent, infer a group linearization
    from frame cocycles, identify presentation local freeness with a physical
    bundle, or claim stability, spectrum, or carrier promotion.

Phase 0:
    The six-chart presentation comparison is exact where its Fitting gates
    pass; failed chart gates remain explicit and global equivariant descent is
    unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.polynomials import Polynomial, PolynomialMatrix
from onetheory.models.heterotic_schoen.visible import PointScheme

from .global_serre import (
    FittingUnitCertificate,
    _fitting_certificate,
    _fraction_record,
    _polynomial_record,
    _shifted_frame_transition,
    _transition_checks,
    _transition_digest,
)
from .pencil import TierAPencilModel, tier_a_pencil_model
from .serre_pushout import (
    FractionMatrix,
    _chart_matrix,
    _frame_coordinates,
    _quotient_row,
    _relation_matrix,
    _selected_fitting_columns,
)
from .tier_b_serre_extensions import TierBSerreExtensionRay, tier_b_serre_eigenrays


def _relation_is_graded(
    relation: PolynomialMatrix,
    source_shifts: tuple[int, ...],
    target_shifts: tuple[int, ...],
) -> bool:
    """Check every displayed relation entry against its free-module shifts."""

    if relation.shape != (len(source_shifts), len(target_shifts)):
        raise ValueError("relation shape does not match its graded shift data")
    return all(
        entry.is_zero() or entry.degree == source_shifts[row] - target_shifts[column]
        for row, relation_row in enumerate(relation.rows)
        for column, entry in enumerate(relation_row)
    )


def _matrix_record(matrix: FractionMatrix) -> list[list[dict[str, object]]]:
    """Serialize one exact fraction transition matrix."""

    return [
        [_fraction_record(entry) for entry in row]
        for row in matrix.rows
    ]


@dataclass(frozen=True, slots=True)
class TierBGlobalSerreAudit:
    """One complete dP9 chart comparison for a Tier B presentation ray."""

    ray: TierBSerreExtensionRay
    relation_shape: tuple[int, int]
    source_shifts: tuple[int, ...]
    target_shifts: tuple[int, ...]
    graded_relation: bool
    local_relation_composition: tuple[tuple[str, bool], ...]
    fitting_certificates: tuple[FittingUnitCertificate, ...]
    fitting_failures: tuple[tuple[str, str], ...]
    canonical_frames: tuple[tuple[str, tuple[int, ...], Polynomial], ...]
    line_frame_transitions: tuple[tuple[str, str, FractionMatrix], ...]
    line_frame_all_invertible: bool
    line_frame_cocycle_consistent: bool
    transition_digest: str
    status: str

    @property
    def relation_composition_verified(self) -> bool:
        """Return whether the relation maps to the ideal on every chart."""

        return all(verified for _, verified in self.local_relation_composition)

    @property
    def fitting_cover_verified(self) -> bool:
        """Return whether every dP9 chart has an exact unit Fitting identity."""

        return not self.fitting_failures and all(
            certificate.verified for certificate in self.fitting_certificates
        )

    @property
    def globally_locally_free(self) -> bool:
        """Return the full presentation-level dP9 local-freeness gate."""

        return (
            self.graded_relation
            and self.relation_composition_verified
            and self.fitting_cover_verified
            and self.line_frame_all_invertible
            and self.line_frame_cocycle_consistent
        )

    def as_record(self) -> dict[str, object]:
        """Serialize successes and exact chart failures without descent claims."""

        return {
            "scheme": self.ray.cokernel.scheme.name,
            "character_pair": [str(value) for value in self.ray.character_pair],
            "ray": self.ray.as_record(),
            "relation_shape": list(self.relation_shape),
            "source_shifts": list(self.source_shifts),
            "target_shifts": list(self.target_shifts),
            "graded_relation": self.graded_relation,
            "local_relation_composition": [
                [chart, verified]
                for chart, verified in self.local_relation_composition
            ],
            "fitting_cover": [
                certificate.as_record()
                for certificate in self.fitting_certificates
            ],
            "fitting_failures": [
                {"chart": chart, "error": error}
                for chart, error in self.fitting_failures
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
            "line_frame_transitions": [
                {
                    "source": source,
                    "target": target,
                    "matrix": _matrix_record(matrix),
                }
                for source, target, matrix in self.line_frame_transitions
            ],
            "line_frame_transition_count": len(self.line_frame_transitions),
            "line_frame_all_invertible": self.line_frame_all_invertible,
            "line_frame_cocycle_consistent": self.line_frame_cocycle_consistent,
            "line_frame_transition_digest": self.transition_digest,
            "globally_locally_free": self.globally_locally_free,
            "status": self.status,
        }


def tier_b_global_serre_audit(
    ray: TierBSerreExtensionRay,
    model: TierAPencilModel | None = None,
) -> TierBGlobalSerreAudit:
    """Build the exact six-chart dP9 comparison for one bounded ray."""

    current = tier_a_pencil_model() if model is None else model
    scheme = ray.cokernel.scheme
    point_scheme = PointScheme(
        scheme.name,
        tuple(scheme.ideal.generators),
        scheme.resolution,
    )
    relation = _relation_matrix(point_scheme, ray.extension_map)
    quotient = _quotient_row(point_scheme)
    source_shifts = ray.cokernel.syzygy_degrees
    target_shifts = ray.cokernel.generator_degrees + (ray.cokernel.target_line_shift,)
    graded_relation = _relation_is_graded(
        relation,
        source_shifts,
        target_shifts,
    )
    local_composition = []
    for chart in current.blowup_atlas.charts:
        local_relation = _chart_matrix(relation, chart)
        local_quotient = _chart_matrix(quotient, chart)
        quotient_column = PolynomialMatrix(
            tuple((entry,) for entry in local_quotient.rows[0])
        )
        local_composition.append(
            (chart.name, local_relation.compose(quotient_column).is_zero())
        )
    fitting_certificates = []
    fitting_failures = []
    for chart in current.blowup_atlas.charts:
        try:
            fitting_certificates.append(_fitting_certificate(relation, chart))
        except ValueError as error:
            fitting_failures.append((chart.name, str(error)))
    transitions: tuple[tuple[str, str, FractionMatrix], ...] = ()
    canonical_frames: tuple[tuple[str, tuple[int, ...], object], ...] = ()
    all_invertible = False
    cocycle_consistent = False
    transition_digest = ""
    if not fitting_failures:
        fitting_columns = _selected_fitting_columns(relation)
        frame_data = tuple(
            _frame_coordinates(relation, columns)
            for columns in fitting_columns
        )
        canonical_frames = tuple(
            (
                f"U_{pivot}_base",
                columns,
                frame_data[pivot][2],
            )
            for pivot, columns in enumerate(fitting_columns)
        )
        generated = []
        for source in current.blowup_atlas.charts:
            for target in current.blowup_atlas.charts:
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
                        target_shifts,
                    )
                )
                generated.append((source.name, target.name, matrix))
        transitions = tuple(generated)
        all_invertible, cocycle_consistent = _transition_checks(
            current,
            transitions,
        )
        transition_digest = _transition_digest(transitions)
    return TierBGlobalSerreAudit(
        ray,
        relation.shape,
        source_shifts,
        target_shifts,
        graded_relation,
        tuple(local_composition),
        tuple(fitting_certificates),
        tuple(fitting_failures),
        canonical_frames,
        transitions,
        all_invertible,
        cocycle_consistent,
        transition_digest,
        (
            "exact six-chart presentation comparison; quotient linearization, "
            "descent, stability, and physical promotion remain unresolved"
        ),
    )


def tier_b_global_serre_audits(
    rays: tuple[TierBSerreExtensionRay, ...] | None = None,
    model: TierAPencilModel | None = None,
) -> tuple[TierBGlobalSerreAudit, ...]:
    """Audit every bounded Tier B eigenray on the six-chart dP9 atlas."""

    selected = tier_b_serre_eigenrays() if rays is None else rays
    current = tier_a_pencil_model() if model is None else model
    return tuple(
        tier_b_global_serre_audit(ray, current)
        for ray in selected
    )


__all__ = [
    "TierBGlobalSerreAudit",
    "tier_b_global_serre_audit",
    "tier_b_global_serre_audits",
]
