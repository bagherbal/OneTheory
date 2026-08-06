"""Classify reduced projective orbits for the fixed Schoen deck action.

Owns:
    Exact projective-point normalization, orbit closure, fixed-point
    enumeration, and reduced orbit-type classification for the published
    order-nine coordinate action.

Depends on:
    Exact Eisenstein vectors and matrices, and the published Schoen
    coordinate lifts. This diagnostic does not consume observations.

Must not:
    Treat an orbit as a sheaf, infer a Serre extension, choose a physical
    coefficient, or claim completeness for non-reduced schemes or arbitrary
    equivariant sheaf constructions.

Phase 0:
    The reduced projective orbit types are certified exactly; ideal
    presentations, constituent construction, descent, and promotion remain
    unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry

ProjectivePoint = tuple[Eisenstein, Eisenstein, Eisenstein]


def _normalize(point: Vector) -> ProjectivePoint:
    """Normalize a nonzero projective vector by its first nonzero coordinate."""

    if point.dimension != 3:
        raise ValueError("the Schoen projective action requires three coordinates")
    pivot = next((value for value in point if not value.is_zero()), None)
    if pivot is None:
        raise ValueError("the zero vector has no projective point")
    return tuple(value / pivot for value in point)


def _point(values: tuple[object, object, object]) -> ProjectivePoint:
    """Construct one exactly normalized Eisenstein projective point."""

    return _normalize(Vector(values, scalar_type=Eisenstein))


@cache
def _deck_generators() -> tuple[Matrix, Matrix]:
    """Return the two exact projective generators used by the carrier audit."""

    geometry = schoen_geometry()
    return geometry.heisenberg.t, geometry.heisenberg.p.inverse() @ geometry.heisenberg.t


def _apply(matrix: Matrix, point: ProjectivePoint) -> ProjectivePoint:
    """Apply one exact linear lift and discard only its projective scalar."""

    return _normalize(matrix @ Vector(point, scalar_type=Eisenstein))


def projective_orbit(seed: ProjectivePoint) -> tuple[ProjectivePoint, ...]:
    """Return the deterministic orbit closure of one projective point."""

    if len(seed) != 3:
        raise ValueError("projective points require three coordinates")
    normalized = _point(seed)
    seen: list[ProjectivePoint] = [normalized]
    pending = [normalized]
    generators = _deck_generators()
    while pending:
        current = pending.pop(0)
        for generator in generators:
            image = _apply(generator, current)
            if image not in seen:
                seen.append(image)
                pending.append(image)
    return tuple(seen)


@dataclass(frozen=True, slots=True)
class ProjectiveOrbit:
    """One exact finite orbit in projective three-coordinate space."""

    identifier: str
    points: tuple[ProjectivePoint, ...]
    group_order: int = 9

    def __post_init__(self) -> None:
        if not self.identifier.strip() or not self.points:
            raise ValueError("projective orbits require a name and points")
        if self.group_order != 9:
            raise ValueError("the fixed Schoen projective action has order nine")
        if len(set(self.points)) != len(self.points):
            raise ValueError("projective orbit points must be distinct")
        if any(_point(point) != point for point in self.points):
            raise ValueError("projective orbit points must be normalized")
        if set(projective_orbit(self.points[0])) != set(self.points):
            raise ValueError("projective orbit points must be closed under the deck action")

    @property
    def size(self) -> int:
        """Return the exact orbit length."""

        return len(self.points)

    @property
    def stabilizer_order(self) -> int:
        """Return the exact stabilizer order from orbit--stabilizer."""

        if self.group_order % self.size:
            raise ValueError("orbit length does not divide the group order")
        return self.group_order // self.size

    @property
    def invariant(self) -> bool:
        """Return whether both named generators preserve the orbit."""

        point_set = set(self.points)
        return all(
            {_apply(generator, point) for point in self.points} == point_set
            for generator in _deck_generators()
        )

    @property
    def exact(self) -> bool:
        """Return the reduced orbit certificate."""

        return self.invariant and self.size in (3, 9) and self.size * self.stabilizer_order == 9

    def as_record(self) -> dict[str, object]:
        """Serialize the exact orbit without assigning physical meaning."""

        return {
            "identifier": self.identifier,
            "size": self.size,
            "stabilizer_order": self.stabilizer_order,
            "invariant": self.invariant,
            "points": [[str(value) for value in point] for point in self.points],
            "exact": self.exact,
            "status": "reduced projective orbit only; scheme and Serre data unresolved",
        }


@dataclass(frozen=True, slots=True)
class TierBReducedOrbitClassification:
    """Exact reduced orbit-type report for the bounded Tier B point search."""

    group_order: int
    nonidentity_fixed_point_count: int
    special_orbits: tuple[ProjectiveOrbit, ...]
    generic_orbit_size: int
    maximum_point_length: int = 9

    @property
    def special_orbit_sizes(self) -> tuple[int, ...]:
        """Return the ordered sizes of the finite special orbits."""

        return tuple(orbit.size for orbit in self.special_orbits)

    @property
    def complete_for_reduced_orbit_types(self) -> bool:
        """Return the exact finite fixed-point/orbit-type certificate."""

        return (
            self.group_order == 9
            and self.nonidentity_fixed_point_count == 12
            and self.special_orbit_sizes == (3, 3, 3, 3)
            and self.generic_orbit_size == 9
            and all(orbit.exact for orbit in self.special_orbits)
        )

    @property
    def reduced_lengths_within_bound(self) -> tuple[int, ...]:
        """Return possible nonempty reduced invariant lengths up to the bound."""

        return tuple(
            length
            for length in range(1, self.maximum_point_length + 1)
            if length % 3 == 0
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the reduced orbit classification and its boundary."""

        return {
            "category": "reduced invariant projective point orbits",
            "group_order": self.group_order,
            "nonidentity_fixed_point_count": self.nonidentity_fixed_point_count,
            "special_orbit_count": len(self.special_orbits),
            "special_orbit_sizes": list(self.special_orbit_sizes),
            "generic_orbit_size": self.generic_orbit_size,
            "maximum_point_length": self.maximum_point_length,
            "reduced_lengths_within_bound": list(self.reduced_lengths_within_bound),
            "complete_for_reduced_orbit_types": self.complete_for_reduced_orbit_types,
            "special_orbits": [orbit.as_record() for orbit in self.special_orbits],
            "nonreduced_schemes": "unresolved",
            "serre_constituents": "unresolved",
            "status": (
                "exact reduced orbit classification; non-reduced schemes, ideal "
                "presentations, Serre extensions, and descent remain unresolved"
            ),
        }


def _fixed_points() -> tuple[ProjectivePoint, ...]:
    """Enumerate every projective fixed point of every nonidentity element."""

    identity = Matrix.identity(3, scalar_type=Eisenstein)
    points: list[ProjectivePoint] = []
    generators = _deck_generators()
    for first_power in range(3):
        for second_power in range(3):
            element = (generators[0] ** first_power) @ (generators[1] ** second_power)
            if element == identity:
                continue
            if element**3 != identity:
                raise ValueError("the projective generator product failed its cubic relation")
            for eigenvalue in (Eisenstein(1), OMEGA, OMEGA2):
                eigenspace = (element - identity.scale(eigenvalue)).nullspace()
                if len(eigenspace) != 1:
                    raise ValueError(
                        "a nonidentity deck element must have one-dimensional eigenspaces"
                    )
                point = _normalize(eigenspace[0])
                if point not in points:
                    points.append(point)
    return tuple(points)


def _partition(points: tuple[ProjectivePoint, ...]) -> tuple[ProjectiveOrbit, ...]:
    """Partition the fixed-point set into exact deck orbits."""

    remaining = list(points)
    orbits: list[ProjectiveOrbit] = []
    while remaining:
        seed = remaining.pop(0)
        closure = projective_orbit(seed)
        if not set(closure).issubset(set(points)):
            raise ValueError("a fixed-point orbit escaped the exact fixed-point set")
        for point in closure:
            if point in remaining:
                remaining.remove(point)
        orbits.append(ProjectiveOrbit(f"fixed-orbit-{len(orbits)}", closure))
    return tuple(orbits)


@cache
def tier_b_reduced_orbit_classification() -> TierBReducedOrbitClassification:
    """Construct the exact reduced orbit classification within Tier B length nine."""

    fixed_points = _fixed_points()
    orbits = _partition(fixed_points)
    coordinate_orbit = set(projective_orbit(_point((1, 0, 0))))
    ordered = tuple(
        sorted(
            orbits,
            key=lambda orbit: (0 if set(orbit.points) == coordinate_orbit else 1, orbit.identifier),
        )
    )
    renamed = tuple(
        ProjectiveOrbit(
            "coordinate-fixed-orbit" if index == 0 else f"nonmonomial-fixed-orbit-{index}",
            orbit.points,
        )
        for index, orbit in enumerate(ordered)
    )
    result = TierBReducedOrbitClassification(9, len(fixed_points), renamed, 9)
    if not result.complete_for_reduced_orbit_types:
        raise ValueError("reduced Tier B orbit classification failed exact gates")
    return result


__all__ = [
    "ProjectiveOrbit",
    "ProjectivePoint",
    "TierBReducedOrbitClassification",
    "projective_orbit",
    "tier_b_reduced_orbit_classification",
]
