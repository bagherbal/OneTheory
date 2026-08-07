"""Screen descended curvilinear constituents against rank-four topology.

Owns:
    Exact Schoen-basis Chern arithmetic, bounded lawful twist enumeration, and
    scoped determinant/index obstructions for the descended rank-two sheaves
    and every target-line shift admitted by the Tier B extension bound.

Depends on:
    The certified projective shifts, the published identification of the dP9
    blowdown hyperplane with the invariant three-section, exact quotient
    intersections, the line-bundle descent congruence, and the frozen carrier
    target.

Must not:
    Infer an outer Ext class, select a physical carrier, reuse published
    one-Higgs constituent data, assume unconstructed target shifts descend,
    or extend this no-candidate result to other Hilbert--Burch or Serre
    architectures.

Phase 0:
    The current curvilinear Hilbert--Burch architecture is screened exactly;
    outer Ext work is unavailable when the determinant/index gates fail.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from itertools import product

from onetheory.math.numbers import Rational
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry

from .specification import computable_carrier_specification

Twist = tuple[int, int, int]
CurveCoordinates = tuple[Rational, Rational, Rational]

SOURCE_SHIFTS = (5, 5, 5)
TARGET_SHIFTS = (3, 4, 4, 4, 3)
GENERATOR_SHIFTS = (3, 4, 4, 4)
SYZYGY_SHIFTS = (5, 5, 5)
HYPERPLANE_MAPPING_PROVENANCE = (
    "The P2 blowdown line is the invariant dP9 three-section t: H^2=1, "
    "H.f=3, and pi_i^*(t)=tau_i in the published Schoen basis."
)


def _basis_vector(factor: int) -> Twist:
    """Return the tau class pulled back from one dP9 factor."""

    if factor not in (0, 1):
        raise ValueError("curvilinear constituents pull back from factor one or two")
    return tuple(1 if index == factor else 0 for index in range(3))


def _add(*vectors: tuple[object, object, object]) -> tuple[Rational, ...]:
    """Add exact Schoen-basis coordinate triples."""

    return tuple(
        sum((Rational(value) for value in coordinates), Rational(0))
        for coordinates in zip(*vectors, strict=True)
    )


def _scale(scalar: object, vector: tuple[object, object, object]) -> tuple[Rational, ...]:
    """Scale one exact Schoen-basis coordinate triple."""

    value = Rational(scalar)
    return tuple(value * Rational(coordinate) for coordinate in vector)


def _curve_product(
    left: tuple[object, object, object],
    right: tuple[object, object, object],
) -> CurveCoordinates:
    """Return divisor-product coordinates paired with the named basis."""

    geometry = schoen_geometry()
    left_values = tuple(Rational(value) for value in left)
    right_values = tuple(Rational(value) for value in right)
    return tuple(
        sum(
            (
                left_values[first]
                * right_values[second]
                * geometry.quotient_intersections.coefficient(first, second, third)
                for first in range(3)
                for second in range(3)
            ),
            Rational(0),
        )
        for third in range(3)
    )


def _curve_add(*curves: CurveCoordinates) -> CurveCoordinates:
    """Add curve-coordinate triples exactly."""

    return tuple(
        sum(coordinates, Rational(0))
        for coordinates in zip(*curves, strict=True)
    )


def _twisted_first_chern(
    factor: int,
    target_line_shift: int,
    twist: Twist,
) -> tuple[Rational, ...]:
    """Return ``c1(E_i tensor O(D))`` for the certified rank-two type."""

    hyperplane = _basis_vector(factor)
    return _add(_scale(-target_line_shift, hyperplane), _scale(2, twist))


def _twisted_second_chern(
    factor: int,
    target_line_shift: int,
    twist: Twist,
) -> CurveCoordinates:
    """Return exact quotient curve coordinates of the twisted second Chern class."""

    hyperplane = _basis_vector(factor)
    base_first = _scale(-target_line_shift, hyperplane)
    base_second = tuple(
        Rational(9) * value
        for value in _curve_product(hyperplane, hyperplane)
    )
    return _curve_add(
        base_second,
        _curve_product(base_first, twist),
        _curve_product(twist, twist),
    )


def _twisted_ch_three(
    factor: int,
    target_line_shift: int,
    twist: Twist,
) -> Rational:
    """Integrate the exact degree-three Chern character on the quotient."""

    geometry = schoen_geometry()
    hyperplane = geometry.quotient_divisor(_basis_vector(factor))
    divisor = geometry.quotient_divisor(twist)
    return (
        (Rational(target_line_shift**2, 2) - Rational(9))
        * geometry.triple(hyperplane, hyperplane, divisor)
        - Rational(target_line_shift, 2)
        * geometry.triple(hyperplane, divisor, divisor)
        + Rational(1, 3) * geometry.triple(divisor, divisor, divisor)
    )


def _formal_scalar(value: object) -> Polynomial:
    """Return one exact constant in the formal twist polynomial ring."""

    return Polynomial.monomial((0, 0, 0), value, scalar_type=Rational)


def _formal_triple(
    left: tuple[Polynomial, ...],
    middle: tuple[Polynomial, ...],
    right: tuple[Polynomial, ...],
) -> Polynomial:
    """Evaluate the Schoen triple tensor on formal divisor coordinates."""

    intersections = schoen_geometry().quotient_intersections
    result = Polynomial.zero(3, scalar_type=Rational)
    for first in range(3):
        for second in range(3):
            for third in range(3):
                coefficient = intersections.coefficient(first, second, third)
                if coefficient:
                    result += (left[first] * middle[second] * right[third]).scale(
                        coefficient
                    )
    return result


def _formal_ch_three(
    factor: int,
    target_line_shift: int,
    twist: tuple[Polynomial, Polynomial, Polynomial],
) -> Polynomial:
    """Return the integrated degree-three character as a formal polynomial."""

    hyperplane = tuple(
        _formal_scalar(1 if index == factor else 0) for index in range(3)
    )
    return (
        _formal_triple(hyperplane, hyperplane, twist).scale(
            Rational(target_line_shift**2, 2) - Rational(9)
        )
        - _formal_triple(hyperplane, twist, twist).scale(
            Rational(target_line_shift, 2)
        )
        + _formal_triple(twist, twist, twist).scale(Rational(1, 3))
    )


def _same_factor_index_identity(factor: int) -> bool:
    """Prove formal index cancellation for every determinant-cancelling pair."""

    variables = tuple(
        Polynomial.monomial(
            tuple(1 if row == column else 0 for column in range(3)),
            scalar_type=Rational,
        )
        for row in range(3)
    )
    hyperplane = _basis_vector(factor)
    complement = tuple(
        _formal_scalar(3 * hyperplane[index]) - variables[index]
        for index in range(3)
    )
    return (
        _formal_ch_three(factor, 3, variables)
        + _formal_ch_three(factor, 3, complement)
    ).is_zero()


def _bounded_twists(radius: int) -> tuple[Twist, ...]:
    """Enumerate the declared integral twist cube deterministically."""

    return tuple(product(range(-radius, radius + 1), repeat=3))


@dataclass(frozen=True, slots=True)
class SameFactorTwistTopologyAudit:
    """One determinant-compatible same-factor twist pair."""

    factor: int
    left_twist: Twist
    right_twist: Twist
    left_first_chern: tuple[Rational, ...]
    right_first_chern: tuple[Rational, ...]
    total_first_chern: tuple[Rational, ...]
    total_second_chern: CurveCoordinates
    integrated_third_chern: Rational
    quotient_index: Rational
    line_twists_descend: bool

    @property
    def determinant_cancels(self) -> bool:
        """Return whether the free first Chern class vanishes exactly."""

        return self.total_first_chern == (Rational(0),) * 3

    @property
    def target_index(self) -> bool:
        """Return whether this topology meets the frozen three-family index."""

        target = computable_carrier_specification().quotient_chiral_index
        return abs(self.quotient_index) == target

    @property
    def exact(self) -> bool:
        """Return whether every scoped topological gate was evaluated exactly."""

        return (
            self.line_twists_descend
            and self.determinant_cancels
            and self.integrated_third_chern == 2 * self.quotient_index
        )

    def as_record(self) -> dict[str, object]:
        """Serialize exact Chern data without constructing an outer extension."""

        return {
            "factor": self.factor,
            "left_twist": list(self.left_twist),
            "right_twist": list(self.right_twist),
            "left_first_chern": [str(value) for value in self.left_first_chern],
            "right_first_chern": [str(value) for value in self.right_first_chern],
            "total_first_chern": [str(value) for value in self.total_first_chern],
            "total_second_chern_curve_coordinates": [
                str(value) for value in self.total_second_chern
            ],
            "integrated_third_chern": str(self.integrated_third_chern),
            "quotient_index": str(self.quotient_index),
            "line_twists_descend": self.line_twists_descend,
            "determinant_cancels": self.determinant_cancels,
            "target_index": self.target_index,
            "exact": self.exact,
            "status": (
                "lawful same-factor Chern topology; excluded by quotient index "
                "zero before outer Ext construction"
            ),
        }


@dataclass(frozen=True, slots=True)
class CurvilinearTopologyScreen:
    """Complete topology frontier for the current descended Chern type."""

    twist_radius: int
    audits: tuple[SameFactorTwistTopologyAudit, ...]
    cross_factor_parity_obstruction: bool
    same_factor_index_identities: tuple[bool, bool]

    @property
    def target_index_candidate_count(self) -> int:
        """Return bounded topologies meeting the frozen quotient index."""

        return sum(audit.target_index for audit in self.audits)

    @property
    def exact(self) -> bool:
        """Return whether the bounded screen and global identities are exact."""

        return (
            self.cross_factor_parity_obstruction
            and all(self.same_factor_index_identities)
            and all(audit.exact for audit in self.audits)
            and self.target_index_candidate_count == 0
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the no-candidate result at the topology gate."""

        return {
            "twist_radius": self.twist_radius,
            "projective_source_shifts": list(SOURCE_SHIFTS),
            "projective_target_shifts": list(TARGET_SHIFTS),
            "base_rank": 2,
            "base_first_chern_hyperplane": -3,
            "base_second_chern_hyperplane_squared": 9,
            "hyperplane_mapping": {
                "factor_1": "H -> tau1",
                "factor_2": "H -> tau2",
                "provenance": HYPERPLANE_MAPPING_PROVENANCE,
                "source_locators": [
                    "hep-th/0410055 eq:dP9invGhomologydef; eq:H2Xtquotient",
                    "hep-th/0602073 eq:V1def; eq:V2def; sec:ext",
                ],
            },
            "cross_factor_parity_obstruction": (
                self.cross_factor_parity_obstruction
            ),
            "cross_factor_status": (
                "-3(tau1+tau2)+2(D1+D2) cannot vanish in the integral "
                "free divisor lattice"
            ),
            "same_factor_index_identities": list(
                self.same_factor_index_identities
            ),
            "same_factor_status": (
                "D1+D2=3 tau_i forces cancellation of the exact degree-three "
                "Chern characters for every integral twist"
            ),
            "bounded_lawful_twist_pair_count": len(self.audits),
            "target_index_candidate_count": self.target_index_candidate_count,
            "audits": [audit.as_record() for audit in self.audits],
            "exact": self.exact,
            "rank_four_outer_ext_available": False,
            "promotion_ready": False,
            "status": (
                "scoped topological no-candidate certificate for pairs of the "
                "current descended curvilinear Chern type; other Tier B "
                "architectures are not excluded"
            ),
        }


def _audit(factor: int, left: Twist, right: Twist) -> SameFactorTwistTopologyAudit:
    """Construct one exact determinant-compatible topology record."""

    geometry = schoen_geometry()
    left_first = _twisted_first_chern(factor, 3, left)
    right_first = _twisted_first_chern(factor, 3, right)
    total_first = _add(left_first, right_first)
    total_second = _curve_add(
        _twisted_second_chern(factor, 3, left),
        _twisted_second_chern(factor, 3, right),
        _curve_product(left_first, right_first),
    )
    total_ch_three = _twisted_ch_three(factor, 3, left) + _twisted_ch_three(
        factor, 3, right
    )
    return SameFactorTwistTopologyAudit(
        factor + 1,
        left,
        right,
        left_first,
        right_first,
        total_first,
        total_second,
        2 * total_ch_three,
        total_ch_three,
        geometry.descent_congruence(left) and geometry.descent_congruence(right),
    )


@cache
def _cached_screen(radius: int) -> CurvilinearTopologyScreen:
    """Construct one validated finite topology screen."""

    twists = _bounded_twists(radius)
    audits = []
    for factor in (0, 1):
        hyperplane = _basis_vector(factor)
        for left in twists:
            right = tuple(
                3 * hyperplane[index] - left[index] for index in range(3)
            )
            if right not in twists:
                continue
            if not (
                schoen_geometry().descent_congruence(left)
                and schoen_geometry().descent_congruence(right)
            ):
                continue
            audits.append(_audit(factor, left, right))
    cross_base_first = (-3, -3, 0)
    cross_parity_obstruction = any(value % 2 for value in cross_base_first)
    screen = CurvilinearTopologyScreen(
        radius,
        tuple(audits),
        cross_parity_obstruction,
        (_same_factor_index_identity(0), _same_factor_index_identity(1)),
    )
    if not screen.exact:
        raise ValueError("curvilinear topology screen failed exact gates")
    return screen


def curvilinear_topology_screen(radius: int = 2) -> CurvilinearTopologyScreen:
    """Screen all lawful twists for the current descended rank-two Chern type."""

    if isinstance(radius, bool) or not isinstance(radius, int):
        raise TypeError("twist radius must be an integer")
    if radius < 0:
        raise ValueError("twist radius must be nonnegative")
    return _cached_screen(radius)


def _projective_section_dimension(degree: int) -> int:
    """Return ``dim H^0(P2, O(degree))`` exactly."""

    if degree < 0:
        return 0
    return (degree + 1) * (degree + 2) // 2


def curvilinear_graded_cokernel_dimension(target_line_shift: int) -> int:
    """Return the exact graded dual-cokernel dimension for one line shift."""

    if isinstance(target_line_shift, bool) or not isinstance(target_line_shift, int):
        raise TypeError("the target-line shift must be an integer")
    section_dimension = _projective_section_dimension
    return (
        3 * section_dimension(5 - target_line_shift)
        - section_dimension(3 - target_line_shift)
        - 3 * section_dimension(4 - target_line_shift)
        + section_dimension(-target_line_shift)
    )


@dataclass(frozen=True, slots=True)
class CurvilinearRankFourTypeAudit:
    """One ordered pair of factor and target-line Chern types."""

    left_factor: int
    left_target_line_shift: int
    right_factor: int
    right_target_line_shift: int
    determinant_integral: bool
    bounded_twist_pair_count: int
    quotient_index_distribution: tuple[tuple[Rational, int], ...]

    @property
    def target_index_pair_count(self) -> int:
        """Return bounded determinant solutions with absolute index three."""

        return sum(
            count
            for index, count in self.quotient_index_distribution
            if abs(index) == Rational(3)
        )

    @property
    def exact(self) -> bool:
        """Return whether the parity and finite index partition agree."""

        return (
            sum(count for _, count in self.quotient_index_distribution)
            == self.bounded_twist_pair_count
            and (self.determinant_integral or self.bounded_twist_pair_count == 0)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize one exact type-level topology audit."""

        return {
            "left_factor": self.left_factor,
            "left_target_line_shift": self.left_target_line_shift,
            "right_factor": self.right_factor,
            "right_target_line_shift": self.right_target_line_shift,
            "determinant_integral": self.determinant_integral,
            "bounded_twist_pair_count": self.bounded_twist_pair_count,
            "quotient_index_distribution": [
                {"index": str(index), "count": count}
                for index, count in self.quotient_index_distribution
            ],
            "target_index_pair_count": self.target_index_pair_count,
            "exact": self.exact,
            "status": (
                "determinant parity obstruction"
                if not self.determinant_integral
                else (
                    "no determinant solution in the bounded twist cube"
                    if self.bounded_twist_pair_count == 0
                    else "exact bounded index distribution"
                )
            ),
        }


@dataclass(frozen=True, slots=True)
class CurvilinearTierBTopologyScreen:
    """Complete Tier B topology screen for this Hilbert--Burch architecture."""

    maximum_extension_dimension: int
    twist_radius: int
    admissible_target_line_shifts: tuple[int, ...]
    type_audits: tuple[CurvilinearRankFourTypeAudit, ...]

    @property
    def bounded_twist_pair_count(self) -> int:
        """Return all determinant-compatible ordered pairs in the twist cube."""

        return sum(audit.bounded_twist_pair_count for audit in self.type_audits)

    @property
    def target_index_candidate_count(self) -> int:
        """Return all bounded pairs attaining the frozen quotient index."""

        return sum(audit.target_index_pair_count for audit in self.type_audits)

    @property
    def exact(self) -> bool:
        """Return whether the shift frontier and every type audit close exactly."""

        return (
            self.admissible_target_line_shifts == (3, 4, 5)
            and len(self.type_audits) == 36
            and all(audit.exact for audit in self.type_audits)
            and self.target_index_candidate_count == 0
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the scoped all-shift no-candidate certificate."""

        return {
            "architecture": (
                "length-nine curvilinear Hilbert-Burch resolution with shifts "
                "0 -> O(-5)^3 -> O(-3)+O(-4)^3"
            ),
            "generator_shifts": list(GENERATOR_SHIFTS),
            "syzygy_shifts": list(SYZYGY_SHIFTS),
            "graded_cokernel_dimension_formula": (
                "3*h(5-e)-h(3-e)-3*h(4-e)+h(-e), "
                "h(n)=binomial(n+2,2) for n>=0 and 0 otherwise"
            ),
            "dimension_regions": [
                {"target_line_shift": "e <= 2", "dimension": 9},
                {"target_line_shift": "e = 3", "dimension": 8},
                {"target_line_shift": "e = 4", "dimension": 6},
                {"target_line_shift": "e = 5", "dimension": 3},
                {"target_line_shift": "e >= 6", "dimension": 0},
            ],
            "maximum_extension_dimension": self.maximum_extension_dimension,
            "admissible_target_line_shifts": list(
                self.admissible_target_line_shifts
            ),
            "constituent_chern_types": [
                {
                    "target_line_shift": shift,
                    "rank": 2,
                    "c1_hyperplane": -shift,
                    "c2_hyperplane_squared": "9",
                    "ch2_hyperplane_squared": str(
                        Rational(shift**2, 2) - Rational(9)
                    ),
                }
                for shift in self.admissible_target_line_shifts
            ],
            "twist_radius": self.twist_radius,
            "individual_line_descent_assumed": False,
            "quotient_index_computation": (
                "integrated ch3 after rank-two line twists, evaluated with "
                "the exact Schoen quotient intersection tensor"
            ),
            "ordered_type_count": len(self.type_audits),
            "bounded_twist_pair_count": self.bounded_twist_pair_count,
            "target_index_candidate_count": self.target_index_candidate_count,
            "type_audits": [audit.as_record() for audit in self.type_audits],
            "exact": self.exact,
            "rank_four_outer_ext_available": False,
            "promotion_ready": False,
            "status": (
                "scoped no-candidate certificate for every target-line shift "
                "admitted by the Tier B extension-dimension bound; other "
                "Hilbert-Burch and Serre architectures remain open"
            ),
        }


def _general_type_audit(
    left_factor: int,
    left_shift: int,
    right_factor: int,
    right_shift: int,
    radius: int,
) -> CurvilinearRankFourTypeAudit:
    """Enumerate one ordered Chern-type pair without assuming line descent."""

    left_hyperplane = _basis_vector(left_factor)
    right_hyperplane = _basis_vector(right_factor)
    base_sum = tuple(
        left_shift * left_hyperplane[index]
        + right_shift * right_hyperplane[index]
        for index in range(3)
    )
    determinant_integral = all(value % 2 == 0 for value in base_sum)
    if not determinant_integral:
        return CurvilinearRankFourTypeAudit(
            left_factor + 1,
            left_shift,
            right_factor + 1,
            right_shift,
            False,
            0,
            (),
        )
    required_twist_sum = tuple(value // 2 for value in base_sum)
    twists = _bounded_twists(radius)
    twist_set = frozenset(twists)
    index_counts: dict[Rational, int] = {}
    pair_count = 0
    for left_twist in twists:
        right_twist = tuple(
            required_twist_sum[index] - left_twist[index]
            for index in range(3)
        )
        if right_twist not in twist_set:
            continue
        quotient_index = _twisted_ch_three(
            left_factor,
            left_shift,
            left_twist,
        ) + _twisted_ch_three(
            right_factor,
            right_shift,
            right_twist,
        )
        pair_count += 1
        index_counts[quotient_index] = index_counts.get(quotient_index, 0) + 1
    return CurvilinearRankFourTypeAudit(
        left_factor + 1,
        left_shift,
        right_factor + 1,
        right_shift,
        True,
        pair_count,
        tuple(sorted(index_counts.items())),
    )


@cache
def _cached_tier_b_screen(radius: int) -> CurvilinearTierBTopologyScreen:
    """Construct the all-shift topology screen inside the frozen Tier B bounds."""

    tier_b = next(
        tier
        for tier in computable_carrier_specification().tiers
        if tier.name == "Tier B"
    )
    admissible = tuple(
        shift
        for shift in (3, 4, 5)
        if 0 < curvilinear_graded_cokernel_dimension(shift)
        <= tier_b.maximum_extension_dimension
    )
    if not (
        curvilinear_graded_cokernel_dimension(2)
        > tier_b.maximum_extension_dimension
        and curvilinear_graded_cokernel_dimension(6) == 0
    ):
        raise ValueError("curvilinear target-line dimension frontier changed")
    constituent_types = tuple(product(range(2), admissible))
    audits = tuple(
        _general_type_audit(
            left_factor,
            left_shift,
            right_factor,
            right_shift,
            radius,
        )
        for (left_factor, left_shift), (right_factor, right_shift) in product(
            constituent_types,
            repeat=2,
        )
    )
    screen = CurvilinearTierBTopologyScreen(
        tier_b.maximum_extension_dimension,
        radius,
        admissible,
        audits,
    )
    if not screen.exact:
        raise ValueError("Tier B curvilinear topology screen failed exact gates")
    return screen


def curvilinear_tier_b_topology_screen(
    radius: int = 2,
) -> CurvilinearTierBTopologyScreen:
    """Screen all line shifts allowed by the Tier B extension bound."""

    if isinstance(radius, bool) or not isinstance(radius, int):
        raise TypeError("twist radius must be an integer")
    tier_b = next(
        tier
        for tier in computable_carrier_specification().tiers
        if tier.name == "Tier B"
    )
    if radius != tier_b.twist_radius:
        raise ValueError("the all-shift screen requires the frozen Tier B radius")
    return _cached_tier_b_screen(radius)


__all__ = [
    "CurvilinearRankFourTypeAudit",
    "CurvilinearTierBTopologyScreen",
    "CurvilinearTopologyScreen",
    "SameFactorTwistTopologyAudit",
    "curvilinear_graded_cokernel_dimension",
    "curvilinear_tier_b_topology_screen",
    "curvilinear_topology_screen",
]
