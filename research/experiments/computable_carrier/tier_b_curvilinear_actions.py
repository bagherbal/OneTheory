"""Audit finite deck lifts for global curvilinear Tier B presentations.

Owns:
    Exact mixed-degree resolution-action enumeration for the eight declared
    global curvilinear specializations, including order-three and commuting
    pair certificates.

Depends on:
    The global curvilinear Hilbert--Burch presentations and the reusable exact
    resolution-lift solver over the Eisenstein coefficient field.

Must not:
    Treat a resolution action as a sheaf linearization, select a parameter as
    physics, infer quotient descent, or claim a Serre extension or bundle.

Phase 0:
    This is a bounded research diagnostic; all global specializations remain
    nonphysical until the Serre, descent, and downstream gates are certified.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from .tier_b_curvilinear_global import (
    TierBGlobalCurvilinearSpecialization,
    tier_b_global_curvilinear_specializations,
)
from .tier_b_transported_actions import (
    TransportedResolutionAction,
    _actions,
)


@dataclass(frozen=True, slots=True)
class TierBCurvilinearResolutionActionAudit:
    """One finite resolution-action audit for a global specialization."""

    specialization: TierBGlobalCurvilinearSpecialization
    p_actions: tuple[TransportedResolutionAction, ...]
    t_actions: tuple[TransportedResolutionAction, ...]

    @property
    def exact(self) -> bool:
        """Return whether all enumerated lifts pass their finite checks."""

        return all(action.exact for action in (*self.p_actions, *self.t_actions))

    @property
    def commuting_pairs(self) -> tuple[tuple[int, int], ...]:
        """Return pairs commuting on both terms of the resolution."""

        return tuple(
            (p_index, t_index)
            for p_index, p_action in enumerate(self.p_actions)
            for t_index, t_action in enumerate(self.t_actions)
            if p_action.target_action @ t_action.target_action
            == t_action.target_action @ p_action.target_action
            and p_action.source_action @ t_action.source_action
            == t_action.source_action @ p_action.source_action
        )

    @property
    def scoped_no_pair(self) -> bool:
        """Return the bounded no-pair result for this lift family."""

        return self.exact and not self.commuting_pairs

    def as_record(self) -> dict[str, object]:
        """Serialize the finite result with its sheaf-level boundary."""

        return {
            "specialization": self.specialization.name,
            "orbit": self.specialization.orbit_identifier,
            "family": self.specialization.family,
            "parameter": str(self.specialization.parameter),
            "p_action_count": len(self.p_actions),
            "t_action_count": len(self.t_actions),
            "p_actions": [action.as_record() for action in self.p_actions],
            "t_actions": [action.as_record() for action in self.t_actions],
            "exact": self.exact,
            "commuting_pairs": [list(pair) for pair in self.commuting_pairs],
            "complete_commuting_pair_count": len(self.commuting_pairs),
            "scoped_no_pair": self.scoped_no_pair,
            "status": (
                "finite global resolution-lift diagnostic only; sheaf "
                "linearization and quotient descent remain unresolved"
            ),
        }


@cache
def tier_b_curvilinear_resolution_actions(
    parameter: object = None,
) -> tuple[TierBCurvilinearResolutionActionAudit, ...]:
    """Enumerate finite P/T lifts for the declared global specializations."""

    specializations = tier_b_global_curvilinear_specializations(
        parameter if parameter is not None else 1,
    )
    audits = tuple(
        TierBCurvilinearResolutionActionAudit(
            specialization,
            _actions(specialization, "P"),
            _actions(specialization, "T"),
        )
        for specialization in specializations
    )
    if len(audits) != 8 or not all(audit.exact for audit in audits):
        raise ValueError("curvilinear resolution-action family failed exact gates")
    return audits


__all__ = [
    "TierBCurvilinearResolutionActionAudit",
    "tier_b_curvilinear_resolution_actions",
]
