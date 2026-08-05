"""Audit bounded Tier B resolution lifts against the deck-group relations.

Owns:
    Exact relation and middle-term checks for the finite monomial
    Hilbert--Burch lift family attached to Tier B Serre rays, including
    order-three, commutator, and exhaustive compatible-pair gates.

Depends on:
    Tier B monomial resolutions, graded Serre extension rays, exact
    polynomial relation matrices, Eisenstein linear algebra, and the finite
    resolution-lift enumerator.

Must not:
    Call a resolution lift a sheaf linearization, infer quotient descent from
    a presentation action, or turn the bounded family into a no-go theorem for
    the full global Ext problem.

Phase 0:
    This research diagnostic is exact within its declared finite lift family;
    global Serre comparison, honest equivariance, stability, and promotion
    remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import PolynomialMatrix
from onetheory.models.heterotic_schoen.visible import PointScheme

from .pushout_linearization import (
    _left_constant_product,
    _middle_action,
    _resolution_variants,
    _right_constant_product,
    _transformed_relation,
)
from .resolution_actions import ResolutionAction
from .serre_pushout import _relation_matrix
from .tier_b_monomial import (
    MonomialResolutionActionAudit,
    tier_b_monomial_resolution_actions,
)
from .tier_b_serre_extensions import (
    TierBSerreExtensionRay,
    tier_b_serre_eigenrays,
)


@dataclass(frozen=True, slots=True)
class TierBGeneratorLinearizationAudit:
    """Record one generator's exact relation and order checks."""

    name: str
    character: Eisenstein
    relation_equation: bool
    relation_order_three: bool
    middle_order_three: bool

    def as_record(self) -> dict[str, object]:
        """Serialize one generator gate without a descent claim."""

        return {
            "name": self.name,
            "character": str(self.character),
            "relation_equation": self.relation_equation,
            "relation_order_three": self.relation_order_three,
            "middle_order_three": self.middle_order_three,
        }


@dataclass(frozen=True, slots=True)
class TierBCompatibleVariantPair:
    """Record group relations for one compatible finite lift pair."""

    relation_order_three: tuple[bool, bool]
    relation_commutes: bool
    middle_order_three: tuple[bool, bool]
    middle_commutes: bool

    @property
    def complete(self) -> bool:
        """Return whether this pair realizes the declared group relations."""

        return (
            all(self.relation_order_three)
            and self.relation_commutes
            and all(self.middle_order_three)
            and self.middle_commutes
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact finite-pair relation gates."""

        return {
            "relation_order_three": list(self.relation_order_three),
            "relation_commutes": self.relation_commutes,
            "middle_order_three": list(self.middle_order_three),
            "middle_commutes": self.middle_commutes,
            "complete": self.complete,
        }


@dataclass(frozen=True, slots=True)
class TierBLinearizationAudit:
    """Audit one globally locally free Tier B ray's finite lift family."""

    scheme: str
    character_pair: tuple[Eisenstein, Eisenstein]
    generators: tuple[TierBGeneratorLinearizationAudit, ...]
    direct_relation_commutes: bool
    direct_middle_commutes: bool
    resolution_variant_counts: tuple[int, int]
    compatible_variant_counts: tuple[int, int]
    compatible_variant_pairs: tuple[TierBCompatibleVariantPair, ...]
    status: str

    @property
    def direct_group_relations_verified(self) -> bool:
        """Return whether the selected resolution lifts form the group action."""

        return (
            all(
                generator.relation_equation
                and generator.relation_order_three
                and generator.middle_order_three
                for generator in self.generators
            )
            and self.direct_relation_commutes
            and self.direct_middle_commutes
        )

    @property
    def complete_variant_pair_count(self) -> int:
        """Count complete pairs in the declared exhaustive finite family."""

        return sum(pair.complete for pair in self.compatible_variant_pairs)

    @property
    def finite_group_gate_passes(self) -> bool:
        """Return whether any declared compatible pair passes every gate."""

        return self.complete_variant_pair_count > 0

    def as_record(self) -> dict[str, object]:
        """Serialize exact bounded results and preserve the unresolved boundary."""

        return {
            "scheme": self.scheme,
            "character_pair": [str(value) for value in self.character_pair],
            "generators": [generator.as_record() for generator in self.generators],
            "direct_relation_commutes": self.direct_relation_commutes,
            "direct_middle_commutes": self.direct_middle_commutes,
            "direct_group_relations_verified": self.direct_group_relations_verified,
            "resolution_variant_counts": list(self.resolution_variant_counts),
            "compatible_variant_counts": list(self.compatible_variant_counts),
            "compatible_variant_pairs": [
                pair.as_record() for pair in self.compatible_variant_pairs
            ],
            "complete_variant_pair_count": self.complete_variant_pair_count,
            "finite_group_gate_passes": self.finite_group_gate_passes,
            "status": self.status,
        }


def _point_scheme(ray: TierBSerreExtensionRay) -> PointScheme:
    """Convert one research scheme to the production point-scheme record."""

    scheme = ray.cokernel.scheme
    return PointScheme(
        scheme.name,
        tuple(scheme.ideal.generators),
        scheme.resolution,
    )


def _relation_compatible(
    relation: PolynomialMatrix,
    action: ResolutionAction,
    character: Eisenstein,
) -> bool:
    """Check the exact pushout relation for one lift and character."""

    return _left_constant_product(
        action.source_action.transpose(),
        relation,
    ).rows == _right_constant_product(
        _transformed_relation(relation, action),
        _middle_action(action, character),
    ).rows


def _compatible_pairs(
    relation: PolynomialMatrix,
    ray: TierBSerreExtensionRay,
    p_variants: tuple[ResolutionAction, ...],
    t_variants: tuple[ResolutionAction, ...],
) -> tuple[tuple[tuple[ResolutionAction, ResolutionAction], ...], tuple[int, int]]:
    """Enumerate relation-compatible pairs in the finite lift family."""

    compatible = []
    p_count = 0
    t_count = 0
    for action in p_variants:
        if _relation_compatible(relation, action, ray.character_pair[0]):
            p_count += 1
    for action in t_variants:
        if _relation_compatible(relation, action, ray.character_pair[1]):
            t_count += 1
    for p_action in p_variants:
        for t_action in t_variants:
            if _relation_compatible(relation, p_action, ray.character_pair[0]) and (
                _relation_compatible(relation, t_action, ray.character_pair[1])
            ):
                compatible.append((p_action, t_action))
    return tuple(compatible), (p_count, t_count)


def _pair_audit(
    pair: tuple[ResolutionAction, ResolutionAction],
    characters: tuple[Eisenstein, Eisenstein],
) -> TierBCompatibleVariantPair:
    """Check order and commutators for one relation-compatible pair."""

    p_action, t_action = pair
    relation_actions = tuple(
        action.source_action.transpose() for action in (p_action, t_action)
    )
    middle_actions = tuple(
        _middle_action(action, character)
        for action, character in zip((p_action, t_action), characters, strict=True)
    )
    relation_identity = Matrix.identity(
        relation_actions[0].row_count,
        scalar_type=Eisenstein,
    )
    middle_identity = Matrix.identity(
        middle_actions[0].row_count,
        scalar_type=Eisenstein,
    )
    return TierBCompatibleVariantPair(
        tuple(action**3 == relation_identity for action in relation_actions),
        relation_actions[0] @ relation_actions[1]
        == relation_actions[1] @ relation_actions[0],
        tuple(action**3 == middle_identity for action in middle_actions),
        middle_actions[0] @ middle_actions[1]
        == middle_actions[1] @ middle_actions[0],
    )


def tier_b_linearization_audit(
    ray: TierBSerreExtensionRay,
    resolution_audit: MonomialResolutionActionAudit,
) -> TierBLinearizationAudit:
    """Audit one Tier B ray against all declared resolution-lift choices."""

    point_scheme = _point_scheme(ray)
    relation = _relation_matrix(point_scheme, ray.extension_map)
    selected_actions = tuple(
        resolution_audit.actions.action(name) for name in ("P", "T")
    )
    generators = []
    for action, character in zip(
        selected_actions,
        ray.character_pair,
        strict=True,
    ):
        relation_action = action.source_action.transpose()
        middle_action = _middle_action(action, character)
        generators.append(
            TierBGeneratorLinearizationAudit(
                action.name,
                character,
                _relation_compatible(relation, action, character),
                relation_action**3
                == Matrix.identity(relation_action.row_count, scalar_type=Eisenstein),
                middle_action**3
                == Matrix.identity(middle_action.row_count, scalar_type=Eisenstein),
            )
        )
    direct_relation_actions = tuple(
        action.source_action.transpose() for action in selected_actions
    )
    direct_middle_actions = tuple(
        _middle_action(action, character)
        for action, character in zip(selected_actions, ray.character_pair, strict=True)
    )
    p_variants = _resolution_variants(point_scheme, "P")
    t_variants = _resolution_variants(point_scheme, "T")
    compatible, compatible_counts = _compatible_pairs(
        relation,
        ray,
        p_variants,
        t_variants,
    )
    pair_audits = tuple(
        _pair_audit(pair, ray.character_pair) for pair in compatible
    )
    return TierBLinearizationAudit(
        ray.cokernel.scheme.name,
        ray.character_pair,
        tuple(generators),
        direct_relation_actions[0] @ direct_relation_actions[1]
        == direct_relation_actions[1] @ direct_relation_actions[0],
        direct_middle_actions[0] @ direct_middle_actions[1]
        == direct_middle_actions[1] @ direct_middle_actions[0],
        (len(p_variants), len(t_variants)),
        compatible_counts,
        pair_audits,
        (
            "exact bounded resolution-lift group diagnostic; no complete finite "
            "pair is a Serre linearization or quotient-descent certificate"
        ),
    )


def tier_b_linearization_audits(
    rays: tuple[TierBSerreExtensionRay, ...] | None = None,
    eligible_schemes: frozenset[str] | None = None,
    resolution_audits: tuple[MonomialResolutionActionAudit, ...] | None = None,
) -> tuple[TierBLinearizationAudit, ...]:
    """Audit the finite lift family for globally eligible Tier B rays.

    ``eligible_schemes`` is supplied by the preceding chart local-freeness
    gate. If omitted, every supplied ray is audited, without implying that
    global local freeness has been established for it.
    """

    selected_rays = tier_b_serre_eigenrays() if rays is None else rays
    action_audits = (
        tier_b_monomial_resolution_actions()
        if resolution_audits is None
        else resolution_audits
    )
    actions_by_scheme = {audit.scheme.name: audit for audit in action_audits}
    if eligible_schemes is None:
        active_rays = selected_rays
    else:
        active_rays = tuple(
            ray
            for ray in selected_rays
            if ray.cokernel.scheme.name in eligible_schemes
        )
    return tuple(
        tier_b_linearization_audit(ray, actions_by_scheme[ray.cokernel.scheme.name])
        for ray in active_rays
    )


__all__ = [
    "TierBCompatibleVariantPair",
    "TierBGeneratorLinearizationAudit",
    "TierBLinearizationAudit",
    "tier_b_linearization_audit",
    "tier_b_linearization_audits",
]
