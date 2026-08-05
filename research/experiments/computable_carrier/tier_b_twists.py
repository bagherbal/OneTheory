"""Screen bounded divisor twists against the quotient class congruence.

Owns:
    Exact enumeration of determinant-cancelling integral twist pairs in the
    declared Tier B radius and their necessary Schoen quotient divisor-class
    descent checks.

Depends on:
    The finite Tier B specification and published exact Schoen geometry. It
    does not depend on extension maps, observations, or fitted parameters.

Must not:
    Treat a congruence-compatible divisor class as an equivariant line bundle,
    construct a linearization, infer a Serre extension, or select a carrier.

Phase 0:
    The bounded necessary divisor-class screen is exact; cocycle-level
    linearization, constituent construction, and quotient descent remain open.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from onetheory.models.heterotic_schoen.geometry import schoen_geometry

Twist = tuple[int, int, int]


def _bounded_twists(radius: int) -> tuple[Twist, ...]:
    """Return every integral twist in the closed radius cube."""

    return tuple(product(range(-radius, radius + 1), repeat=3))


@dataclass(frozen=True, slots=True)
class TwistDescentAudit:
    """One exact necessary class-descent result for a twist pair."""

    left_twist: Twist
    right_twist: Twist
    left_class_congruence: bool
    right_class_congruence: bool
    determinant_cancels: bool

    @property
    def necessary_descent_gate(self) -> bool:
        """Return the necessary divisor-class gate for both constituents."""

        return (
            self.determinant_cancels
            and self.left_class_congruence
            and self.right_class_congruence
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the class screen without claiming line linearization."""

        return {
            "left_twist": list(self.left_twist),
            "right_twist": list(self.right_twist),
            "left_class_congruence": self.left_class_congruence,
            "right_class_congruence": self.right_class_congruence,
            "determinant_cancels": self.determinant_cancels,
            "necessary_descent_gate": self.necessary_descent_gate,
            "status": (
                "necessary divisor-class screen only; line linearization, Serre "
                "construction, and quotient descent remain unresolved"
            ),
        }


@dataclass(frozen=True, slots=True)
class TierBTwistDescentScreen:
    """Complete bounded necessary descent screen for Tier B twist pairs."""

    radius: int
    audits: tuple[TwistDescentAudit, ...]

    @property
    def compatible_audits(self) -> tuple[TwistDescentAudit, ...]:
        """Return the twist pairs passing the necessary class gate."""

        return tuple(item for item in self.audits if item.necessary_descent_gate)

    def as_record(self) -> dict[str, object]:
        """Serialize the complete finite screen and its unresolved boundary."""

        return {
            "radius": self.radius,
            "twist_count": len(self.audits),
            "necessary_descent_count": len(self.compatible_audits),
            "necessary_descent_twists": [
                list(item.left_twist) for item in self.compatible_audits
            ],
            "audits": [item.as_record() for item in self.audits],
            "status": (
                "complete bounded divisor-class screen; honest line and Serre "
                "linearizations remain unresolved"
            ),
        }


def tier_b_twist_descent_screen(radius: int = 2) -> TierBTwistDescentScreen:
    """Enumerate and screen every determinant-cancelling bounded twist pair."""

    if isinstance(radius, bool) or not isinstance(radius, int):
        raise TypeError("twist radius must be an integer")
    if radius < 0:
        raise ValueError("twist radius must be nonnegative")
    geometry = schoen_geometry()
    audits = tuple(
        TwistDescentAudit(
            twist,
            tuple(-value for value in twist),
            geometry.descent_congruence(twist),
            geometry.descent_congruence(tuple(-value for value in twist)),
            True,
        )
        for twist in _bounded_twists(radius)
    )
    return TierBTwistDescentScreen(radius, audits)


__all__ = [
    "TierBTwistDescentScreen",
    "TwistDescentAudit",
    "tier_b_twist_descent_screen",
]
