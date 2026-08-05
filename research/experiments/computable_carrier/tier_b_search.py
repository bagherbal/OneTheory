"""Enumerate the bounded known-scheme Tier B subcategory.

Owns:
    The finite Tier B descriptor category formed from the exact invariant I3
    and I6 schemes and every determinant-cancelling divisor twist in the
    frozen radius-two bound, gated by the exact Tier A outer audit.

Depends on:
    The immutable carrier specification, production point schemes and Serre
    ray checks, Tier A projective/dP9 action audits, and standard dataclasses.

Must not:
    Call a descriptor a sheaf or bundle, fabricate extension cocycles, infer
    stability or spectrum, or claim that this known-scheme subcategory is the
    complete universe of invariant zero-dimensional schemes.

Phase 0:
    Tier A unlock and Tier B descriptor enumeration are exact for this
    explicitly scoped subcategory; constituent construction and promotion are
    unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from onetheory.models.heterotic_schoen.visible import PointScheme, point_schemes, serre_data

from .dp9_actions import DPSurfaceDeckActionAudit
from .projective_hom_search import TierAProjectiveHomPairAudit
from .specification import computable_carrier_specification

Twist = tuple[int, int, int]


def _bounded_twists(radius: int) -> tuple[Twist, ...]:
    """Return every integral three-coordinate twist in a closed cube."""

    return tuple(product(range(-radius, radius + 1), repeat=3))


@dataclass(frozen=True, slots=True)
class TierBKnownSchemeDescriptor:
    """One unresolved Tier B descriptor in the known-scheme category."""

    identifier: str
    left_scheme: PointScheme
    right_scheme: PointScheme
    left_twist: Twist
    right_twist: Twist
    known_schemes_are_invariant: bool
    determinant_cancels: bool
    constituent_constructed: bool
    outer_extension_constructed: bool

    def __post_init__(self) -> None:
        if self.left_twist != tuple(-value for value in self.right_twist):
            raise ValueError("Tier B twists must cancel exactly")
        if not self.known_schemes_are_invariant:
            raise ValueError("Tier B known-scheme descriptors require invariant schemes")
        if not self.determinant_cancels:
            raise ValueError("Tier B descriptors require determinant cancellation")
        if self.constituent_constructed or self.outer_extension_constructed:
            raise ValueError("unconstructed Tier B descriptors cannot claim construction")

    @property
    def status(self) -> str:
        """Return the explicit unresolved construction status."""

        return "descriptor only; constituent and outer constructions pending"

    def as_record(self) -> dict[str, object]:
        """Serialize one descriptor without fabricating physical objects."""

        return {
            "identifier": self.identifier,
            "left_scheme": self.left_scheme.name,
            "right_scheme": self.right_scheme.name,
            "left_point_length": str(self.left_scheme.length),
            "right_point_length": str(self.right_scheme.length),
            "left_twist": list(self.left_twist),
            "right_twist": list(self.right_twist),
            "known_schemes_are_invariant": self.known_schemes_are_invariant,
            "determinant_cancels": self.determinant_cancels,
            "constituent_constructed": self.constituent_constructed,
            "outer_extension_constructed": self.outer_extension_constructed,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class TierBKnownSchemeSearch:
    """Exact gated enumeration report for the known-scheme Tier B category."""

    tier_a_pair_count: int
    tier_a_invariant_dimension: int
    tier_a_action_gate: bool
    twist_radius: int
    maximum_point_length: int
    descriptors: tuple[TierBKnownSchemeDescriptor, ...]

    @property
    def unlocked(self) -> bool:
        """Return whether the exact Tier A gate permits this enumeration."""

        return (
            self.tier_a_pair_count == 6
            and self.tier_a_invariant_dimension == 0
            and self.tier_a_action_gate
        )

    @property
    def complete_for_declared_category(self) -> bool:
        """Return whether every known-scheme bounded descriptor was enumerated."""

        return self.unlocked and bool(self.descriptors)

    def as_record(self) -> dict[str, object]:
        """Serialize the gated finite search and its explicit scope boundary."""

        return {
            "category": "known invariant I3/I6 schemes with bounded twists",
            "tier_a_pair_count": self.tier_a_pair_count,
            "tier_a_invariant_dimension": self.tier_a_invariant_dimension,
            "tier_a_action_gate": self.tier_a_action_gate,
            "unlocked": self.unlocked,
            "twist_radius": self.twist_radius,
            "maximum_point_length": self.maximum_point_length,
            "descriptor_count": len(self.descriptors),
            "complete_for_declared_category": self.complete_for_declared_category,
            "full_tier_b_invariant_scheme_search": "unresolved",
            "descriptors": [item.as_record() for item in self.descriptors],
            "status": (
                "exact finite known-scheme enumeration; no constituent, outer "
                "extension, stability, or spectrum result is claimed"
            ),
        }


def _scheme_invariance() -> bool:
    """Check the exact production invariant-ray certificates for I3 and I6."""

    schemes = point_schemes()
    rays = serre_data().rays
    return len(schemes) == 2 and len(rays) == 2 and all(
        ray.p_fixed and ray.t_fixed for ray in rays
    )


def tier_b_known_scheme_search(
    pair_audits: tuple[TierAProjectiveHomPairAudit, ...],
    action_audits: tuple[DPSurfaceDeckActionAudit, ...],
) -> TierBKnownSchemeSearch:
    """Enumerate the known-scheme Tier B category after the Tier A gate."""

    specification = computable_carrier_specification()
    tier_b = next(tier for tier in specification.tiers if tier.name == "Tier B")
    schemes = point_schemes()
    invariant = _scheme_invariance()
    pair_count = len(pair_audits)
    invariant_dimension = sum(item.invariant_ext_one_dimension for item in pair_audits)
    action_gate = (
        len(action_audits) == pair_count
        and all(
            item.homology.squared_zero
            and item.actions_commute
            and item.actions_order_three
            for item in action_audits
        )
    )
    unlocked = pair_count == 6 and invariant_dimension == 0 and action_gate and invariant
    if not unlocked:
        return TierBKnownSchemeSearch(
            pair_count,
            invariant_dimension,
            action_gate,
            tier_b.twist_radius,
            tier_b.maximum_point_length,
            (),
        )
    descriptors = tuple(
        TierBKnownSchemeDescriptor(
            f"B-known-{left.name}-{right.name}-{index}",
            left,
            right,
            twist,
            tuple(-value for value in twist),
            invariant,
            True,
            False,
            False,
        )
        for index, (left, right, twist) in enumerate(
            item
            for item in product(schemes, schemes, _bounded_twists(tier_b.twist_radius))
            if not (
                item[0].name == "I3"
                and item[1].name == "I6"
                and item[2] == (-1, 1, 0)
            )
            and int(item[0].length) <= tier_b.maximum_point_length
            and int(item[1].length) <= tier_b.maximum_point_length
        )
    )
    return TierBKnownSchemeSearch(
        pair_count,
        invariant_dimension,
        action_gate,
        tier_b.twist_radius,
        tier_b.maximum_point_length,
        descriptors,
    )


__all__ = [
    "TierBKnownSchemeDescriptor",
    "TierBKnownSchemeSearch",
    "tier_b_known_scheme_search",
]
