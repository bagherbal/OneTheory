"""Audit outer extensions for the bounded Tier B monomial ray pairs.

Owns:
    Exact polynomial Hom presentations, projective and zero-fiber dP9
    totalizations, and induced deck-action audits for the declared I3/I6
    monomial Serre-ray pairs.

Depends on:
    Tier B monomial Serre rays and resolution actions, the exact presentation
    Hom engine, dP9 line-bundle cones, and finite deck-action diagnostics.
    It does not consume observations or numerical parameters.

Must not:
    Call a presentation totalization a global Ext group, infer a descended
    rank-four bundle from a zero invariant space, or extend this scoped result
    to non-monomial schemes, unexamined twists, stability, or spectrum.

Phase 0:
    The bounded I3/I6 monomial outer-pair frontier is exact and fail-closed;
    global sheaf comparison, honest equivariance, and physical promotion
    remain unresolved outside this declared category.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.polynomials import PolynomialMatrix
from onetheory.models.heterotic_schoen.visible import PointScheme

from .dp9_actions import DPSurfaceDeckActionAudit, dp9_deck_action_audit
from .dp9_homology import DPSurfaceDerivedHom, dp9_derived_hom
from .pencil import TierAPencilModel, tier_a_pencil_model
from .polynomial_hom import PolynomialHomComplex, polynomial_hom_complex
from .projective_hom_action import ProjectiveHomDeckAudit, projective_hom_deck_audit
from .projective_hyperhom import (
    ProjectiveHomHypercohomology,
    projective_hom_hypercohomology,
)
from .resolution_actions import ResolutionActionPair
from .serre_pushout import (
    SerrePushoutCandidate,
    _base_chern_data,
    _chart_pushout_records,
    _local_fitting_data,
    _quotient_row,
    _relation_matrix,
    _transition_atlas,
)
from .tier_b_global_serre import tier_b_global_serre_audits
from .tier_b_monomial import tier_b_monomial_resolution_actions
from .tier_b_serre_extensions import (
    TierBSerreExtensionRay,
    tier_b_serre_eigenrays,
)


def _complex_squared_zero(complex_) -> bool:
    """Check adjacent cochain compositions without serializing the complex."""

    return all(
        complex_.differential(degree + 1).compose(differential).is_zero()
        for degree, differential in complex_.differentials
    )


def _point_scheme(ray: TierBSerreExtensionRay) -> PointScheme:
    """Wrap one exact Tier B ideal in the production scheme record."""

    scheme = ray.cokernel.scheme
    return PointScheme(scheme.name, tuple(scheme.ideal.generators), scheme.resolution)


@cache
def _candidate(
    ray: TierBSerreExtensionRay,
    model: TierAPencilModel,
) -> SerrePushoutCandidate:
    """Build a complete presentation record from one Tier B ray."""

    scheme = _point_scheme(ray)
    relation = _relation_matrix(scheme, ray.extension_map)
    quotient = _quotient_row(scheme)
    quotient_column = PolynomialMatrix(tuple((entry,) for entry in quotient.rows[0]))
    source_shifts = ray.cokernel.syzygy_degrees
    target_shifts = ray.cokernel.generator_degrees + (
        ray.cokernel.target_line_shift,
    )
    graded = all(
        entry.is_zero() or entry.degree == source_shifts[row] - target_shifts[column]
        for row, relation_row in enumerate(relation.rows)
        for column, entry in enumerate(relation_row)
    )
    if not graded:
        raise ValueError("Tier B outer candidate has an inhomogeneous relation")
    local_fitting = _local_fitting_data(relation)
    if not all(unit for _, unit, _ in local_fitting):
        raise ValueError("Tier B outer candidate failed the support Fitting gate")
    return SerrePushoutCandidate(
        scheme=scheme,
        extension_map=ray.extension_map,
        character_pair=ray.character_pair,
        relation=relation,
        quotient=quotient,
        relation_composes_to_zero=relation.compose(quotient_column).is_zero(),
        source_shifts=source_shifts,
        target_shifts=target_shifts,
        graded_relation=graded,
        base_chern=_base_chern_data(source_shifts, target_shifts),
        local_fitting=local_fitting,
        chart_records=_chart_pushout_records(relation, quotient, model),
        transition_atlas=_transition_atlas(scheme, relation, model),
        linearizations=(),
        source_rank=len(source_shifts),
        middle_rank=len(target_shifts) - len(source_shifts),
        status=(
            "exact Tier B monomial presentation adapter; outer dP9 comparison, "
            "linearization, and quotient descent remain unresolved"
        ),
    )


@dataclass(frozen=True, slots=True)
class TierBOuterPairAudit:
    """One exact projective and dP9 outer audit for a monomial ray pair."""

    left: TierBSerreExtensionRay
    right: TierBSerreExtensionRay
    parent: PolynomialHomComplex
    projective: ProjectiveHomHypercohomology
    projective_deck: ProjectiveHomDeckAudit
    dp9: DPSurfaceDerivedHom
    dp9_deck: DPSurfaceDeckActionAudit

    @property
    def exact(self) -> bool:
        """Return all presentation and totalization square-zero gates."""

        return (
            self.parent.squared_zero
            and _complex_squared_zero(self.projective.h0.complex)
            and _complex_squared_zero(self.projective.h2.complex)
            and self.dp9.squared_zero
            and self.dp9.all_line_bundles_squared_zero
        )

    @property
    def invariant_outer_dimension(self) -> int:
        """Return the common fixed degree-one dP9 presentation dimension."""

        return self.dp9_deck.invariant_dimension

    @property
    def group_action_gate(self) -> bool:
        """Return the exact commuting order-three action gate."""

        return (
            self.projective_deck.p_order_three
            and self.projective_deck.p_t_commute
            and self.dp9_deck.actions_order_three
            and self.dp9_deck.actions_commute
        )

    def as_record(self) -> dict[str, object]:
        """Serialize cochains, representatives, actions, and the scope wall."""

        return {
            "left_scheme": self.left.cokernel.scheme.name,
            "right_scheme": self.right.cokernel.scheme.name,
            "left_character_pair": [str(value) for value in self.left.character_pair],
            "right_character_pair": [str(value) for value in self.right.character_pair],
            "projective_ext1_dimension": self.projective.ext_one_dimension,
            "dP9_total_h1_dimension": self.dp9.total_h1_dimension,
            "invariant_outer_dimension": self.invariant_outer_dimension,
            "exact": self.exact,
            "group_action_gate": self.group_action_gate,
            "projective_hypercohomology": self.projective.as_record(),
            "projective_deck_action": self.projective_deck.as_record(),
            "dP9_totalization": self.dp9.as_record(),
            "dP9_deck_action": self.dp9_deck.as_record(),
            "status": (
                "exact bounded Tier B I3/I6 monomial outer-pair audit; this is "
                "not a complete Tier B search or a descended physical bundle"
            ),
        }


@dataclass(frozen=True, slots=True)
class TierBOuterFrontier:
    """Scoped no-candidate report for all declared monomial I3/I6 pairs."""

    pair_audits: tuple[TierBOuterPairAudit, ...]
    category: str
    complete_for_declared_category: bool

    @property
    def invariant_outer_class_count(self) -> int:
        """Count invariant degree-one classes across the declared pairs."""

        return sum(item.invariant_outer_dimension for item in self.pair_audits)

    @property
    def no_candidate_in_declared_category(self) -> bool:
        """Return the fail-closed scoped no-candidate gate."""

        return (
            self.complete_for_declared_category
            and bool(self.pair_audits)
            and all(item.exact and item.group_action_gate for item in self.pair_audits)
            and self.invariant_outer_class_count == 0
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the complete scoped frontier and its unresolved boundary."""

        return {
            "category": self.category,
            "pair_count": len(self.pair_audits),
            "complete_for_declared_category": self.complete_for_declared_category,
            "invariant_outer_class_count": self.invariant_outer_class_count,
            "no_candidate_in_declared_category": self.no_candidate_in_declared_category,
            "pair_audits": [item.as_record() for item in self.pair_audits],
            "status": (
                "scoped Tier B monomial outer no-candidate result; non-monomial "
                "schemes, unexamined twists, broader Serre classes, stability, "
                "and spectrum remain unresolved"
            ),
        }


def _ray_action_pairs() -> dict[str, ResolutionActionPair]:
    """Return exact deck actions keyed by the bounded monomial scheme."""

    return {
        audit.scheme.name: audit.actions
        for audit in tier_b_monomial_resolution_actions()
    }


@cache
def tier_b_outer_frontier() -> TierBOuterFrontier:
    """Audit every eligible monomial I3/I6 ray pair exactly once."""

    rays = tier_b_serre_eigenrays()
    global_audits = tier_b_global_serre_audits(rays)
    eligible_schemes = frozenset(
        audit.ray.cokernel.scheme.name
        for audit in global_audits
        if audit.globally_locally_free
    )
    left_rays = tuple(
        ray
        for ray in rays
        if ray.cokernel.scheme.name.endswith("-0")
        and ray.cokernel.scheme.name in eligible_schemes
    )
    right_rays = tuple(
        ray
        for ray in rays
        if ray.cokernel.scheme.name.endswith(("-1", "-2"))
        and ray.cokernel.scheme.name in eligible_schemes
    )
    if not left_rays or not right_rays:
        raise ValueError("the declared Tier B I3/I6 ray category is empty")
    model = tier_a_pencil_model()
    candidates = {
        id(ray): _candidate(ray, model)
        for ray in (*left_rays, *right_rays)
    }
    actions = _ray_action_pairs()
    audits = []
    for left_ray in left_rays:
        for right_ray in right_rays:
            left = candidates[id(left_ray)]
            right = candidates[id(right_ray)]
            parent = polynomial_hom_complex(left, right)
            projective = projective_hom_hypercohomology(parent)
            projective_deck = projective_hom_deck_audit(
                projective,
                left,
                right,
                (actions[left.scheme.name], actions[right.scheme.name]),
            )
            dp9 = dp9_derived_hom(parent)
            dp9_deck = dp9_deck_action_audit(
                dp9,
                (actions[left.scheme.name], actions[right.scheme.name]),
            )
            audit = TierBOuterPairAudit(
                left_ray,
                right_ray,
                parent,
                projective,
                projective_deck,
                dp9,
                dp9_deck,
            )
            if not audit.exact or not audit.group_action_gate:
                raise ValueError("Tier B outer pair failed an exact action gate")
            audits.append(audit)
    return TierBOuterFrontier(
        tuple(audits),
        "eligible coordinate-supported monomial I3/I6 ray pairs at zero fiber twist",
        len(audits) == len(left_rays) * len(right_rays),
    )


__all__ = ["TierBOuterFrontier", "TierBOuterPairAudit", "tier_b_outer_frontier"]
