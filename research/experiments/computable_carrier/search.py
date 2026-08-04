"""Enumerate the finite computable-carrier construction category.

Owns:
    Deterministic Tier A descriptors from the explicit I3/I6 architecture and
    bounded Tier B determinant-cancelling twist descriptors, with strict tier
    ordering and no candidate identity claim.

Depends on:
    The frozen specification plus exact Schoen geometry, point schemes, and
    Serre-ray checks from production. It does not import observations.

Must not:
    Reuse the published bundle as a candidate, invent an Ext representative,
    call an incomplete descriptor a bundle, or unlock a later tier early.

Phase 0:
    Finite search descriptors are implemented; chain construction and gates
    remain required before any promotion.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from onetheory.models.heterotic_schoen.visible import point_schemes, serre_data

from .specification import ComputableCarrierSpecification, computable_carrier_specification

Twist = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class CandidateDescriptor:
    """A finite candidate descriptor awaiting chain-level construction."""

    tier: str
    identifier: str
    left_scheme: str
    right_scheme: str
    left_twist: Twist
    right_twist: Twist
    determinant_cancels: bool
    constituent_linearizations: bool
    outer_extension_constructed: bool
    reference_bundle_identity_proved: bool
    status: str

    def __post_init__(self) -> None:
        if self.tier not in {"Tier A", "Tier B", "Tier C"}:
            raise ValueError("candidate descriptors require a declared tier")
        if not self.identifier.strip() or not self.left_scheme or not self.right_scheme:
            raise ValueError("candidate descriptors require named schemes")
        if self.left_twist != tuple(-value for value in self.right_twist):
            raise ValueError("candidate twists must cancel exactly")
        if self.reference_bundle_identity_proved:
            raise ValueError("reference-bundle identity must remain unproved")
        if self.status not in {"descriptor", "locked"}:
            raise ValueError("candidate descriptors require an explicit unresolved status")

    @property
    def is_constructed(self) -> bool:
        """Return whether all chain-level construction gates are present."""

        return self.outer_extension_constructed and self.constituent_linearizations

    def as_record(self) -> dict[str, object]:
        """Return deterministic JSON-ready descriptor metadata."""

        return {
            "tier": self.tier,
            "identifier": self.identifier,
            "left_scheme": self.left_scheme,
            "right_scheme": self.right_scheme,
            "left_twist": list(self.left_twist),
            "right_twist": list(self.right_twist),
            "determinant_cancels": self.determinant_cancels,
            "constituent_linearizations": self.constituent_linearizations,
            "outer_extension_constructed": self.outer_extension_constructed,
            "reference_bundle_identity_proved": self.reference_bundle_identity_proved,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class TierSearchReport:
    """A deterministic report over the currently declared finite tiers."""

    specification: ComputableCarrierSpecification
    geometry_verified: bool
    tier_a: tuple[CandidateDescriptor, ...]
    tier_b: tuple[CandidateDescriptor, ...]
    tier_c: tuple[CandidateDescriptor, ...]
    tier_b_locked: bool
    tier_c_locked: bool

    def __post_init__(self) -> None:
        if not self.geometry_verified:
            raise ValueError("a search report requires verified fixed geometry")
        if not self.tier_b_locked:
            raise ValueError("Tier B cannot be active before a Tier A no-go certificate")
        if not self.tier_c_locked:
            raise ValueError("Tier C cannot be active before Tier A and B no-go certificates")

    @property
    def candidate_count(self) -> int:
        """Return the number of declared descriptors, including locked tiers."""

        return len(self.tier_a) + len(self.tier_b) + len(self.tier_c)

    def as_record(self) -> dict[str, object]:
        """Return the complete ordered search report."""

        return {
            "geometry_verified": self.geometry_verified,
            "tier_a": [candidate.as_record() for candidate in self.tier_a],
            "tier_b": [candidate.as_record() for candidate in self.tier_b],
            "tier_c": [candidate.as_record() for candidate in self.tier_c],
            "tier_b_locked": self.tier_b_locked,
            "tier_c_locked": self.tier_c_locked,
            "candidate_count": self.candidate_count,
        }


def _tier_a() -> tuple[CandidateDescriptor, ...]:
    """Enumerate the single published-architecture descriptor as new work."""

    schemes = point_schemes()
    rays = serre_data().rays
    if len(schemes) != 2 or len(rays) != 2 or not all(
        ray.p_fixed and ray.t_fixed for ray in rays
    ):
        raise ValueError("Tier A requires independently recomputed I3/I6 invariant rays")
    return (
        CandidateDescriptor(
            "Tier A",
            "A-I3-I6-twist-minus-plus",
            schemes[0].name,
            schemes[1].name,
            (-1, 1, 0),
            (1, -1, 0),
            True,
            True,
            False,
            False,
            "descriptor",
        ),
    )


def _bounded_twists(radius: int) -> tuple[Twist, ...]:
    """Enumerate all integral three-coordinate twists in a closed bound."""

    return tuple(product(range(-radius, radius + 1), repeat=3))


def _tier_b() -> tuple[CandidateDescriptor, ...]:
    """Enumerate nearby determinant-cancelling descriptors without maps."""

    schemes = tuple(scheme.name for scheme in point_schemes())
    twists = _bounded_twists(2)
    return tuple(
        CandidateDescriptor(
            "Tier B",
            f"B-{left}-{right}-{index}",
            left,
            right,
            twist,
            tuple(-value for value in twist),
            True,
            False,
            False,
            False,
            "locked",
        )
        for index, (left, right, twist) in enumerate(
            item for item in product(schemes, schemes, twists)
            if item[2] != (-1, 1, 0)
        )
    )


def finite_tier_search(
    specification: ComputableCarrierSpecification | None = None,
) -> TierSearchReport:
    """Build the ordered finite search report without selecting a bundle."""

    contract = computable_carrier_specification() if specification is None else specification
    geometry = schoen_geometry()
    tier_a = _tier_a()
    tier_b = _tier_b()
    return TierSearchReport(contract, geometry.quotient.order == contract.quotient_order,
                            tier_a, tier_b, (), True, True)


__all__ = ["CandidateDescriptor", "TierSearchReport", "finite_tier_search"]
