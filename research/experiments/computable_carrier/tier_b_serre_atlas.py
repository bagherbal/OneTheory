"""Generate bare blow-up-chart pushout atlases for lci local types.

Owns:
    Exact invertible chart-transition matrices and cocycle checks for the
    unit local pushouts admitted by the bounded monomial Serre gate.

Depends on:
    The exact cubic-pencil blow-up atlas, the reusable bare pushout transition
    construction, and local monomial Serre audits. It does not consume global
    bundle transitions or observations.

Must not:
    Call bare ideal transitions a global Serre cocycle, assign a dP9 line-frame
    normalization without proof, construct an equivariant linearization, or
    create an atlas for the non-lci staircase.

Phase 0:
    The five lci local types have exact bare chart atlases; global sheaf
    patching, dP9 frame comparison, linearization, and descent remain open.
"""

from __future__ import annotations

from dataclasses import dataclass

from .pencil import TierAPencilModel, tier_a_pencil_model
from .serre_atlas import SerrePushoutAtlas, _pushout_atlas
from .tier_b_local_serre import LocalMonomialSerreAudit, tier_b_local_monomial_serre_audits
from .tier_b_monomial import InvariantMonomialScheme, tier_b_invariant_monomial_schemes


@dataclass(frozen=True, slots=True)
class TierBSerreAtlasAudit:
    """One local Serre atlas result with an explicit global scope boundary."""

    scheme: InvariantMonomialScheme
    local_audit: LocalMonomialSerreAudit
    multiplicity: int
    atlas: SerrePushoutAtlas | None

    @property
    def transitions_available(self) -> bool:
        """Return whether an exact bare transition atlas exists."""

        return self.atlas is not None

    @property
    def all_invertible(self) -> bool:
        """Return the exact chart-transition invertibility gate."""

        return self.atlas is not None and self.atlas.all_invertible

    @property
    def cocycle_consistent(self) -> bool:
        """Return the exact bare chart cocycle gate."""

        return self.atlas is not None and self.atlas.cocycle_consistent

    def as_record(self) -> dict[str, object]:
        """Serialize the bare atlas without promoting global gluing."""

        return {
            "scheme": self.scheme.name,
            "multiplicity": self.multiplicity,
            "transitions_available": self.transitions_available,
            "all_invertible": self.all_invertible,
            "cocycle_consistent": self.cocycle_consistent,
            "atlas": None if self.atlas is None else self.atlas.as_record(),
            "status": (
                "bare ideal-level chart atlas only; dP9 line frames, global Serre "
                "gluing, linearization, and quotient descent remain unresolved"
            ),
        }


def tier_b_serre_atlas_audits(
    schemes: tuple[InvariantMonomialScheme, ...] | None = None,
    model: TierAPencilModel | None = None,
) -> tuple[TierBSerreAtlasAudit, ...]:
    """Build bare chart atlases for every locally Serre-admissible scheme."""

    selected = tier_b_invariant_monomial_schemes() if schemes is None else schemes
    local_audits = tier_b_local_monomial_serre_audits(selected)
    current = tier_a_pencil_model() if model is None else model
    results = []
    for scheme, local_audit in zip(selected, local_audits, strict=True):
        multiplicity = len(scheme.local_standard_monomials)
        atlas = (
            _pushout_atlas(scheme.name, multiplicity, current)
            if local_audit.unit_extension_available
            else None
        )
        result = TierBSerreAtlasAudit(scheme, local_audit, multiplicity, atlas)
        if result.transitions_available and not result.all_invertible:
            raise ValueError("bare Tier B Serre atlas has a noninvertible transition")
        if result.transitions_available and not result.cocycle_consistent:
            raise ValueError("bare Tier B Serre atlas failed its cocycle check")
        results.append(result)
    return tuple(results)


__all__ = ["TierBSerreAtlasAudit", "tier_b_serre_atlas_audits"]
