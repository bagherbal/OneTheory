"""Audit the global six-chart pullback for every Tier A Serre ray.

Owns:
    Rebuilt relation presentations, exact six-chart Fitting identities, and
    line-frame transition checks for every locally free I3 and I6 eigenray.

Depends on:
    The finite Tier A ray enumeration, the exact cubic-pencil atlas, and the
    global graded Serre pullback audit.

Must not:
    Call a locally free pullback presentation a descended dP9 bundle, infer
    quotient equivariance from frame cocycles, or claim a global Ext result.

Phase 0:
    All declared presentation rays receive exact six-chart pullback checks;
    quotient descent, global cohomology, and physical promotion remain open.
"""

from __future__ import annotations

from dataclasses import dataclass

from .global_serre import GlobalSerrePushoutAudit, global_serre_pushout_audit
from .pencil import TierAPencilModel, tier_a_pencil_model
from .projective_hom_search import _presentation_candidate
from .resolution_actions import ResolutionActionPair, tier_a_resolution_actions
from .serre_pushout import SerrePushoutCandidate, tier_a_serre_pushouts
from .serre_rays import SerreEigenclassVariant, tier_a_serre_eigenclass_variants


@dataclass(frozen=True, slots=True)
class TierAGlobalSerreRayAudit:
    """One exact global pullback audit for a locally free Tier A ray."""

    ray: SerreEigenclassVariant
    audit: GlobalSerrePushoutAudit

    def as_record(self) -> dict[str, object]:
        """Serialize the ray and its six-chart local-freeness evidence."""

        return {
            "ray": self.ray.as_record(),
            "global_pullback": self.audit.as_record(),
            "status": (
                "exact six-chart graded pullback audit; quotient linearization "
                "and dP9 descent remain unresolved"
            ),
        }


def tier_a_global_serre_ray_audits(
    model: TierAPencilModel | None = None,
    candidates: tuple[SerrePushoutCandidate, ...] | None = None,
    actions: tuple[ResolutionActionPair, ...] | None = None,
    variants: tuple[SerreEigenclassVariant, ...] | None = None,
) -> tuple[TierAGlobalSerreRayAudit, ...]:
    """Audit the six-chart pullback for all five declared Tier A rays."""

    current = tier_a_pencil_model() if model is None else model
    selected = tier_a_serre_pushouts(current) if candidates is None else candidates
    resolution_actions = tier_a_resolution_actions() if actions is None else actions
    eigenrays = (
        tier_a_serre_eigenclass_variants(selected, resolution_actions)
        if variants is None
        else variants
    )
    base_by_scheme = {candidate.scheme.name: candidate for candidate in selected}
    return tuple(
        TierAGlobalSerreRayAudit(
            variant,
            global_serre_pushout_audit(
                _presentation_candidate(
                    variant,
                    base_by_scheme[variant.scheme],
                    current,
                ),
                current,
            ),
        )
        for variant in eigenrays
    )


__all__ = [
    "TierAGlobalSerreRayAudit",
    "tier_a_global_serre_ray_audits",
]
