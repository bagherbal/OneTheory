"""Screen invariant monomial Serre resolutions against Tier B topology.

Owns:
    Exact Betti-derived extension dimensions, determinant-bounded target-line
    enumeration, Schoen Chern-index filtering, and common deck-eigenray gates
    for the declared invariant monomial resolutions.

Depends on:
    The frozen Tier B bounds, exact monomial Hilbert--Burch certificates,
    sparse graded Serre quotient actions, and the Schoen quotient intersection
    and line-descent arithmetic.

Must not:
    Call a presentation eigenray a descended sheaf, infer an outer extension,
    select a physical carrier, or extend this finite result to non-monomial
    invariant schemes or other Serre architectures.

Phase 0:
    Necessary topology and presentation-eigenclass gates are exact; dP9
    sheafification, honest constituent descent, and outer Ext remain open.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from itertools import product

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein, Rational
from onetheory.models.heterotic_schoen.geometry import schoen_geometry

from .specification import computable_carrier_specification
from .tier_b_monomial import (
    InvariantMonomialScheme,
    tier_b_invariant_monomial_schemes,
    tier_b_monomial_resolution_actions,
)
from .tier_b_serre_extensions import (
    _resolution_degrees,
    tier_b_serre_dual_cokernels,
    tier_b_serre_eigenrays,
)

Twist = tuple[int, int, int]


def _section_dimension(degree: int) -> int:
    """Return ``dim H^0(P2, O(degree))`` exactly."""

    if degree < 0:
        return 0
    return (degree + 1) * (degree + 2) // 2


@dataclass(frozen=True, slots=True)
class MonomialResolutionType:
    """One Betti type represented by exact invariant monomial schemes."""

    identifier: str
    length: int
    generator_shifts: tuple[int, ...]
    syzygy_shifts: tuple[int, ...]
    scheme_names: tuple[str, ...]

    def cokernel_dimension(self, target_line_shift: int) -> int:
        """Return the exact graded dual-cokernel dimension."""

        return (
            sum(
                _section_dimension(shift - target_line_shift)
                for shift in self.syzygy_shifts
            )
            - sum(
                _section_dimension(shift - target_line_shift)
                for shift in self.generator_shifts
            )
            + _section_dimension(-target_line_shift)
        )

    def maximum_admissible_shift(self, maximum_dimension: int) -> int:
        """Return the largest nonzero shift within the extension bound."""

        candidates = tuple(
            shift
            for shift in range(max(self.syzygy_shifts) + 1)
            if 0 < self.cokernel_dimension(shift) <= maximum_dimension
        )
        if not candidates:
            raise ValueError("resolution type has no bounded extension shift")
        return max(candidates)

    def as_record(self, maximum_dimension: int) -> dict[str, object]:
        """Serialize the exact Betti and target-shift frontier."""

        upper = self.maximum_admissible_shift(maximum_dimension)
        return {
            "identifier": self.identifier,
            "length": self.length,
            "generator_shifts": list(self.generator_shifts),
            "syzygy_shifts": list(self.syzygy_shifts),
            "scheme_names": list(self.scheme_names),
            "cokernel_dimension_formula": (
                "sum h(b_j-e)-sum h(a_i-e)+h(-e)"
            ),
            "maximum_admissible_shift": upper,
            "sample_dimensions": [
                {
                    "target_line_shift": shift,
                    "dimension": self.cokernel_dimension(shift),
                }
                for shift in range(-1, upper + 2)
            ],
        }


def _resolution_types() -> tuple[MonomialResolutionType, ...]:
    """Group the exact monomial schemes by length and sorted Betti shifts."""

    grouped: dict[
        tuple[int, tuple[int, ...], tuple[int, ...]],
        list[str],
    ] = {}
    for scheme in tier_b_invariant_monomial_schemes():
        generators, syzygies = _resolution_degrees(scheme)
        key = (
            int(scheme.length),
            tuple(sorted(generators)),
            tuple(sorted(syzygies)),
        )
        grouped.setdefault(key, []).append(scheme.name)
    return tuple(
        MonomialResolutionType(
            f"length-{length}-monomial",
            length,
            generators,
            syzygies,
            tuple(sorted(names)),
        )
        for (length, generators, syzygies), names in sorted(grouped.items())
    )


def _basis_vector(factor: int) -> Twist:
    """Return one Schoen pullback-factor basis vector."""

    if factor not in (0, 1):
        raise ValueError("a constituent factor must be one or two")
    return tuple(1 if index == factor else 0 for index in range(3))


@cache
def _intersection_terms(
    factor: int,
    twist: Twist,
) -> tuple[Rational, Rational, Rational]:
    """Cache the three exact intersection terms used by every Chern type."""

    geometry = schoen_geometry()
    hyperplane = geometry.quotient_divisor(_basis_vector(factor))
    divisor = geometry.quotient_divisor(twist)
    return (
        geometry.triple(hyperplane, hyperplane, divisor),
        geometry.triple(hyperplane, divisor, divisor),
        geometry.triple(divisor, divisor, divisor),
    )


def _twisted_ch_three(
    length: int,
    factor: int,
    target_line_shift: int,
    twist: Twist,
) -> Rational:
    """Return the integrated rank-two degree-three Chern character."""

    hyperplane_squared_twist, hyperplane_twist_squared, twist_cubed = (
        _intersection_terms(factor, twist)
    )
    return (
        (Rational(target_line_shift**2, 2) - Rational(length))
        * hyperplane_squared_twist
        - Rational(target_line_shift, 2) * hyperplane_twist_squared
        + Rational(1, 3) * twist_cubed
    )


def _twisted_first_chern(
    factor: int,
    target_line_shift: int,
    twist: Twist,
) -> Twist:
    """Return exact integral first-Chern coordinates after a line twist."""

    hyperplane = _basis_vector(factor)
    return tuple(
        -target_line_shift * hyperplane[index] + 2 * twist[index]
        for index in range(3)
    )


@dataclass(frozen=True, slots=True)
class MonomialTopologyCandidate:
    """One determinant-descended radius-two topology attaining index three."""

    left_resolution: str
    left_factor: int
    left_target_line_shift: int
    left_twist: Twist
    right_resolution: str
    right_factor: int
    right_target_line_shift: int
    right_twist: Twist
    quotient_index: Rational
    individual_line_twists_descend: bool

    def as_record(self) -> dict[str, object]:
        """Serialize one exact necessary topology candidate."""

        return {
            "left_resolution": self.left_resolution,
            "left_factor": self.left_factor,
            "left_target_line_shift": self.left_target_line_shift,
            "left_twist": list(self.left_twist),
            "right_resolution": self.right_resolution,
            "right_factor": self.right_factor,
            "right_target_line_shift": self.right_target_line_shift,
            "right_twist": list(self.right_twist),
            "quotient_index": str(self.quotient_index),
            "determinant_cancels": True,
            "constituent_determinant_lines_descend": True,
            "individual_line_twists_descend": (
                self.individual_line_twists_descend
            ),
        }


@dataclass(frozen=True, slots=True)
class MonomialSchemeShiftAudit:
    """One exact quotient-action and locally-free eigenray result."""

    scheme: str
    resolution: str
    target_line_shift: int
    cokernel_dimension: int
    expected_dimension: int
    relations_preserved: bool
    actions_order_three: bool
    actions_commute: bool
    locally_free_eigenray_characters: tuple[tuple[Eisenstein, Eisenstein], ...]

    @property
    def locally_free_eigenray_count(self) -> int:
        """Return the number of exact common-character rays."""

        return len(self.locally_free_eigenray_characters)

    @property
    def available(self) -> bool:
        """Return whether this scheme/shift can enter later sheaf gates."""

        return self.actions_commute and self.locally_free_eigenray_count > 0

    @property
    def exact(self) -> bool:
        """Return whether every evaluated algebraic gate is internally exact."""

        return (
            self.cokernel_dimension == self.expected_dimension
            and self.relations_preserved
            and self.actions_order_three
            and (self.actions_commute or self.locally_free_eigenray_count == 0)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize one exact presentation-eigenclass gate."""

        return {
            "scheme": self.scheme,
            "resolution": self.resolution,
            "target_line_shift": self.target_line_shift,
            "cokernel_dimension": self.cokernel_dimension,
            "expected_dimension": self.expected_dimension,
            "relations_preserved": self.relations_preserved,
            "actions_order_three": self.actions_order_three,
            "actions_commute": self.actions_commute,
            "locally_free_eigenray_count": self.locally_free_eigenray_count,
            "locally_free_eigenray_characters": [
                [str(left), str(right)]
                for left, right in self.locally_free_eigenray_characters
            ],
            "available": self.available,
            "exact": self.exact,
            "status": (
                "support-locally-free common presentation eigenrays available"
                if self.available
                else (
                    "projective quotient actions do not commute"
                    if not self.actions_commute
                    else "no support-locally-free common presentation eigenray"
                )
            ),
        }


@dataclass(frozen=True, slots=True)
class TierBMonomialTopologyScreen:
    """Topology-first frontier for all declared invariant monomial resolutions."""

    twist_radius: int
    maximum_extension_dimension: int
    resolution_types: tuple[MonomialResolutionType, ...]
    raw_target_index_candidate_count: int
    determinant_descended_candidates: tuple[MonomialTopologyCandidate, ...]
    shift_audits: tuple[MonomialSchemeShiftAudit, ...]

    @property
    def determinant_descended_candidate_count(self) -> int:
        """Return necessary topology candidates after determinant descent."""

        return len(self.determinant_descended_candidates)

    @property
    def available_resolution_shifts(self) -> frozenset[tuple[str, int]]:
        """Return resolution shifts with at least one locally-free eigenray."""

        return frozenset(
            (audit.resolution, audit.target_line_shift)
            for audit in self.shift_audits
            if audit.available
        )

    @property
    def surviving_topology_candidates(self) -> tuple[MonomialTopologyCandidate, ...]:
        """Return topology candidates whose two constituent shifts have rays."""

        available = self.available_resolution_shifts
        return tuple(
            candidate
            for candidate in self.determinant_descended_candidates
            if (
                candidate.left_resolution,
                candidate.left_target_line_shift,
            )
            in available
            and (
                candidate.right_resolution,
                candidate.right_target_line_shift,
            )
            in available
        )

    @property
    def surviving_presentation_count(self) -> int:
        """Count scheme/eigenray choices over surviving topology candidates."""

        ray_counts: dict[tuple[str, int], int] = {}
        for audit in self.shift_audits:
            key = audit.resolution, audit.target_line_shift
            ray_counts[key] = ray_counts.get(key, 0) + (
                audit.locally_free_eigenray_count
            )
        return sum(
            ray_counts[
                candidate.left_resolution,
                candidate.left_target_line_shift,
            ]
            * ray_counts[
                candidate.right_resolution,
                candidate.right_target_line_shift,
            ]
            for candidate in self.surviving_topology_candidates
        )

    @property
    def exact(self) -> bool:
        """Return whether topology and presentation gates close consistently."""

        return (
            len(self.resolution_types) == 3
            and self.raw_target_index_candidate_count
            >= self.determinant_descended_candidate_count
            and all(audit.exact for audit in self.shift_audits)
            and bool(self.surviving_topology_candidates)
            and all(
                candidate.individual_line_twists_descend
                for candidate in self.surviving_topology_candidates
            )
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact surviving monomial Tier B frontier."""

        surviving = self.surviving_topology_candidates
        return {
            "category": "declared invariant coordinate-supported monomial schemes",
            "twist_radius": self.twist_radius,
            "maximum_extension_dimension": self.maximum_extension_dimension,
            "resolution_types": [
                item.as_record(self.maximum_extension_dimension)
                for item in self.resolution_types
            ],
            "target_shift_completeness": (
                "positive shifts terminate when the dual target vanishes; "
                "determinant cancellation against the bounded twist cube "
                "bounds every negative shift"
            ),
            "raw_target_index_candidate_count": (
                self.raw_target_index_candidate_count
            ),
            "determinant_descended_candidate_count": (
                self.determinant_descended_candidate_count
            ),
            "determinant_descended_candidates": [
                item.as_record()
                for item in self.determinant_descended_candidates
            ],
            "shift_audits": [audit.as_record() for audit in self.shift_audits],
            "available_resolution_shifts": [
                [resolution, shift]
                for resolution, shift in sorted(self.available_resolution_shifts)
            ],
            "surviving_topology_candidate_count": len(surviving),
            "surviving_topology_candidates": [
                item.as_record() for item in surviving
            ],
            "surviving_presentation_count": self.surviving_presentation_count,
            "all_surviving_line_twists_descend": all(
                item.individual_line_twists_descend for item in surviving
            ),
            "outer_ext_computation_available": bool(surviving),
            "outer_extension_constructed": False,
            "promotion_ready": False,
            "exact": self.exact,
            "status": (
                "exact finite topology and presentation-eigenray frontier; "
                "constituent sheafification, honest descent, outer Ext, and "
                "physical gates remain unresolved"
            ),
        }


def _bounded_twists(radius: int) -> tuple[Twist, ...]:
    """Return the frozen integral divisor-twist cube."""

    return tuple(product(range(-radius, radius + 1), repeat=3))


def _target_shift_lower_bound(
    left_factor: int,
    right_factor: int,
    other_upper: int,
    radius: int,
) -> int:
    """Derive a finite lower shift bound from determinant cancellation."""

    if left_factor != right_factor:
        return -4 * radius
    return -4 * radius - other_upper


def _topology_candidates(
    resolution_types: tuple[MonomialResolutionType, ...],
    radius: int,
    maximum_dimension: int,
) -> tuple[int, tuple[MonomialTopologyCandidate, ...]]:
    """Enumerate every exact target-index topology in the derived finite box."""

    target = computable_carrier_specification().quotient_chiral_index
    geometry = schoen_geometry()
    twists = _bounded_twists(radius)
    twist_set = frozenset(twists)
    raw_count = 0
    descended = []
    for left, right in product(resolution_types, repeat=2):
        left_upper = left.maximum_admissible_shift(maximum_dimension)
        right_upper = right.maximum_admissible_shift(maximum_dimension)
        for left_factor, right_factor in product(range(2), repeat=2):
            left_lower = _target_shift_lower_bound(
                left_factor,
                right_factor,
                right_upper,
                radius,
            )
            right_lower = _target_shift_lower_bound(
                right_factor,
                left_factor,
                left_upper,
                radius,
            )
            for left_shift in range(left_lower, left_upper + 1):
                if not (
                    0
                    < left.cokernel_dimension(left_shift)
                    <= maximum_dimension
                ):
                    continue
                for right_shift in range(right_lower, right_upper + 1):
                    if not (
                        0
                        < right.cokernel_dimension(right_shift)
                        <= maximum_dimension
                    ):
                        continue
                    left_hyperplane = _basis_vector(left_factor)
                    right_hyperplane = _basis_vector(right_factor)
                    base_sum = tuple(
                        left_shift * left_hyperplane[index]
                        + right_shift * right_hyperplane[index]
                        for index in range(3)
                    )
                    if any(value % 2 for value in base_sum):
                        continue
                    required_twist_sum = tuple(value // 2 for value in base_sum)
                    for left_twist in twists:
                        right_twist = tuple(
                            required_twist_sum[index] - left_twist[index]
                            for index in range(3)
                        )
                        if right_twist not in twist_set:
                            continue
                        quotient_index = _twisted_ch_three(
                            left.length,
                            left_factor,
                            left_shift,
                            left_twist,
                        ) + _twisted_ch_three(
                            right.length,
                            right_factor,
                            right_shift,
                            right_twist,
                        )
                        if abs(quotient_index) != target:
                            continue
                        raw_count += 1
                        left_first = _twisted_first_chern(
                            left_factor,
                            left_shift,
                            left_twist,
                        )
                        right_first = _twisted_first_chern(
                            right_factor,
                            right_shift,
                            right_twist,
                        )
                        if tuple(
                            left_first[index] + right_first[index]
                            for index in range(3)
                        ) != (0, 0, 0):
                            raise ValueError("determinant enumeration lost c1 zero")
                        if not (
                            geometry.descent_congruence(left_first)
                            and geometry.descent_congruence(right_first)
                        ):
                            continue
                        descended.append(
                            MonomialTopologyCandidate(
                                left.identifier,
                                left_factor + 1,
                                left_shift,
                                left_twist,
                                right.identifier,
                                right_factor + 1,
                                right_shift,
                                right_twist,
                                quotient_index,
                                geometry.descent_congruence(left_twist)
                                and geometry.descent_congruence(right_twist),
                            )
                        )
    return raw_count, tuple(descended)


def _schemes_by_name() -> dict[str, InvariantMonomialScheme]:
    """Index exact monomial schemes by deterministic identifier."""

    return {scheme.name: scheme for scheme in tier_b_invariant_monomial_schemes()}


def _shift_audits(
    resolution_types: tuple[MonomialResolutionType, ...],
    candidates: tuple[MonomialTopologyCandidate, ...],
) -> tuple[MonomialSchemeShiftAudit, ...]:
    """Evaluate only shifts that survive the necessary topology gates."""

    required: dict[str, set[int]] = {
        resolution.identifier: set() for resolution in resolution_types
    }
    for candidate in candidates:
        required[candidate.left_resolution].add(candidate.left_target_line_shift)
        required[candidate.right_resolution].add(candidate.right_target_line_shift)
    schemes = _schemes_by_name()
    audits = []
    for resolution in resolution_types:
        selected = tuple(schemes[name] for name in resolution.scheme_names)
        actions = tier_b_monomial_resolution_actions(selected)
        for shift in sorted(required[resolution.identifier]):
            cokernels = tier_b_serre_dual_cokernels(selected, actions, shift)
            rays = tier_b_serre_eigenrays(selected, actions, shift)
            for scheme, cokernel in zip(selected, cokernels, strict=True):
                scheme_rays = tuple(
                    ray for ray in rays if ray.cokernel.scheme.name == scheme.name
                )
                actions_order_three = all(
                    action.matrix**3
                    == Matrix.identity(
                        action.matrix.row_count,
                        scalar_type=Eisenstein,
                    )
                    for action in cokernel.actions
                )
                audits.append(
                    MonomialSchemeShiftAudit(
                        scheme.name,
                        resolution.identifier,
                        shift,
                        cokernel.dimension,
                        resolution.cokernel_dimension(shift),
                        cokernel.relations_preserved,
                        actions_order_three,
                        cokernel.actions_commute,
                        tuple(ray.character_pair for ray in scheme_rays),
                    )
                )
    return tuple(audits)


@cache
def tier_b_monomial_topology_screen() -> TierBMonomialTopologyScreen:
    """Return the exact topology-first monomial Tier B frontier."""

    tier_b = next(
        tier
        for tier in computable_carrier_specification().tiers
        if tier.name == "Tier B"
    )
    resolution_types = _resolution_types()
    raw_count, candidates = _topology_candidates(
        resolution_types,
        tier_b.twist_radius,
        tier_b.maximum_extension_dimension,
    )
    screen = TierBMonomialTopologyScreen(
        tier_b.twist_radius,
        tier_b.maximum_extension_dimension,
        resolution_types,
        raw_count,
        candidates,
        _shift_audits(resolution_types, candidates),
    )
    if not screen.exact:
        raise ValueError("Tier B monomial topology screen failed exact gates")
    return screen


__all__ = [
    "MonomialResolutionType",
    "MonomialSchemeShiftAudit",
    "MonomialTopologyCandidate",
    "TierBMonomialTopologyScreen",
    "tier_b_monomial_topology_screen",
]
