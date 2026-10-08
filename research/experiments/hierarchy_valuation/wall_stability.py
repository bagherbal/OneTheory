"""Exact constituent stability on the whole wall and extension stability beside it.

Owns:
    Affine degree functions of every source-order line candidate along the wall
    J = (1, 1, s), the exact all-s proof that both constituents are slope-stable
    on the wall, the proper-rank case margins of the outer extension there, and
    exact off-wall spot checks on the stable side j2 > j1.

Depends on:
    The frozen source-order line bounds and minimal effective divisors, the
    trusted retained-stability certificate's polarization-independent cover
    line-Hom vanishing, and the exact ambient cover triple product.

Must not:
    Re-run or replace the line-Hom transfers, claim stability in the full
    Kähler cone, choose a polarization or extension point, or use observations.

Phase 0:
    Research certificate for premise 2 of the wall-valuation theorem.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from fractions import Fraction

from research.experiments.scientific_genesis.metric_polarization_scope import (
    _digest,
    ambient_cover_triple,
)
from research.experiments.scientific_genesis.retained_slope_stability import (
    LINE_BOUNDS,
    MINIMAL_EFFECTIVE,
)
from research.experiments.scientific_genesis.retained_slope_stability import (
    OUTPUT as RETAINED_CERTIFICATE,
)

V1_DETERMINANT = (-2, 2, 0)
# Necessary hidden HYM pairing of ALTERNATE_NECESSARY_HIDDEN_CHAMBER_NOTE.md:
# 4 j1 + 7 j2 - 12 j3 > 0 (quotient pairing times three), no extra sources.
HIDDEN_PAIRING = (4, 7, -12)
PROPER_RANK_CASES = ((1, 0), (0, 1), (2, 0), (1, 1), (0, 2), (2, 1), (1, 2))


def certified_vanishing_lines() -> frozenset[tuple[int, tuple[int, int, int]]]:
    """Lines with trusted zero cover Hom; this property is polarization independent."""

    record = json.loads(RETAINED_CERTIFICATE.read_bytes())
    unsigned = {key: value for key, value in record.items() if key != "artifact_digest"}
    if record.get("artifact_digest") != _digest(unsigned) or record.get("status") != "PROVED":
        raise ValueError("the retained line-Hom certificate is not self-consistent")
    lines = set()
    for probe in record["actual_cover_line_Hom_probes"]:
        if probe["cover_line_hom_dimension"] != 0:
            raise ValueError("a recorded probe does not certify vanishing")
        lines.add((probe["constituent_index"], tuple(probe["candidate_line_class"])))
    return frozenset(lines)


def degree(line: tuple[int, int, int], polarization: tuple[object, ...]) -> Fraction:
    return Fraction(ambient_cover_triple(line, polarization, polarization))


def wall_affine(line: tuple[int, int, int]) -> tuple[Fraction, Fraction]:
    """Return (alpha, beta) with deg(line, (1,1,s)) = alpha + beta s exactly.

    The quadratic coefficient vanishes because phi^2 = 0 on the cover ambient;
    this is checked at a third point rather than assumed.
    """

    alpha = degree(line, (1, 1, 0))
    beta = degree(line, (1, 1, 1)) - alpha
    if degree(line, (1, 1, 2)) != alpha + 2 * beta:
        raise ValueError("wall degree is not affine in s")
    return alpha, beta


def _negative_on(alpha: Fraction, beta: Fraction, upper: Fraction | None) -> bool:
    """alpha + beta s < 0 for every s in (0, upper], or (0, infinity) if upper is None."""

    if alpha > 0:
        return False
    if upper is None:
        return beta < 0 or (beta == 0 and alpha < 0)
    return alpha + beta * upper < 0


@dataclass(frozen=True)
class WallLineRow:
    constituent: int
    line: tuple[int, int, int]
    affine_degree: tuple[str, str]
    nonnegative_for_s_up_to: str | None
    hom_vanishing_used: bool
    strictly_negative_bound_for_all_s: bool


def constituent_wall_rows() -> tuple[WallLineRow, ...]:
    """Prove every remaining constituent line degree is negative on the whole wall.

    For a candidate with nonnegative degree on (0, s*], the maximal line is
    excluded by its certified Hom vanishing and every proper descendant loses
    at least one minimal effective divisor: deg(line) - deg(e) < 0 is required
    for every minimal effective e on (0, s*].
    """

    vanishing = certified_vanishing_lines()
    effective = [wall_affine(e) for e in MINIMAL_EFFECTIVE]
    rows = []
    for index, candidates in enumerate(LINE_BOUNDS):
        for line in candidates:
            alpha, beta = wall_affine(line)
            if alpha < 0 and beta <= 0:
                threshold = None
                used = False
                ok = True
            else:
                if beta >= 0:
                    raise ValueError("a candidate is nonnegative on an unbounded wall ray")
                threshold = -alpha / beta
                used = (index, line) in vanishing
                differences_negative = all(
                    _negative_on(alpha - ea, beta - eb, threshold) for ea, eb in effective
                )
                ok = used and differences_negative
            rows.append(WallLineRow(
                index, line, (str(alpha), str(beta)),
                None if threshold is None else str(threshold), used, ok,
            ))
    if not all(row.strictly_negative_bound_for_all_s for row in rows):
        raise ValueError("a constituent line may destabilize somewhere on the wall")
    return tuple(rows)


def extension_case_bounds(polarization: tuple[object, ...]) -> dict[tuple[int, int], Fraction]:
    """Proper-rank case upper bounds of the retained proof at any polarization."""

    vanishing = certified_vanishing_lines()
    gap = min(degree(e, polarization) for e in MINIMAL_EFFECTIVE)
    if gap <= 0:
        raise ValueError("the polarization is not ample on the minimal effective divisors")
    maxima = []
    for index, candidates in enumerate(LINE_BOUNDS):
        uppers = []
        for line in candidates:
            value = degree(line, polarization)
            if value >= 0:
                if (index, line) not in vanishing:
                    raise ValueError("a nonnegative candidate has no certified Hom vanishing")
                value -= gap
            uppers.append(value)
        maxima.append(max(uppers))
    d1 = degree(V1_DETERMINANT, polarization)
    left = {0: Fraction(0), 1: maxima[0], 2: d1}
    right = {0: Fraction(0), 1: maxima[1], 2: -d1}
    bounds = {}
    for case in PROPER_RANK_CASES:
        total = left[case[0]] + right[case[1]]
        if case == (0, 2):
            total -= gap
        bounds[case] = total
    return bounds


def hidden_pairing(polarization: tuple[object, ...]) -> Fraction:
    return sum(
        (Fraction(c) * Fraction(j) for c, j in zip(HIDDEN_PAIRING, polarization, strict=True)),
        Fraction(0),
    )


def hidden_compatible_wall_interval() -> tuple[str, str]:
    """Open s-interval of the wall J=(1,1,s) meeting the necessary hidden chamber."""

    alpha = hidden_pairing((1, 1, 0))
    beta = hidden_pairing((1, 1, 1)) - alpha
    if not (alpha > 0 and beta < 0):
        raise ValueError("unexpected hidden pairing along the wall")
    return ("0", str(-alpha / beta))


@dataclass(frozen=True)
class WallStabilityReport:
    constituent_rows: tuple[WallLineRow, ...]
    constituents_stable_on_entire_wall: bool
    wall_case_bounds_at_s_one: dict[str, str]
    only_vanishing_case_at_wall: str
    stable_side_spot_checks: tuple[tuple[str, bool], ...]
    opposite_side_destabilized_by_v1: bool
    hidden_compatible_wall_s_interval: tuple[str, str]
    hidden_compatible_stable_points: tuple[str, ...]
    full_kahler_chamber_claimed: bool = False
    observations_used: bool = False


STABLE_SIDE_POINTS = (
    (1, Fraction(101, 100), Fraction(1, 6)),
    (1, Fraction(101, 100), 1),
    (1, Fraction(11, 10), Fraction(1, 2)),
    (1, Fraction(11, 10), 2),
    (14, 16, 1),
)


def build_report() -> WallStabilityReport:
    rows = constituent_wall_rows()
    at_wall = extension_case_bounds((1, 1, 1))
    zero_cases = [case for case, value in at_wall.items() if value >= 0]
    if zero_cases != [(2, 0)] or at_wall[(2, 0)] != 0:
        raise ValueError("at the wall only the V1 determinant case may reach zero")
    checks = tuple(
        (str(tuple(map(str, point))),
         all(value < 0 for value in extension_case_bounds(point).values()))
        for point in STABLE_SIDE_POINTS
    )
    if not all(ok for _, ok in checks):
        raise ValueError("a declared stable-side point failed")
    opposite = degree(V1_DETERMINANT, (Fraction(11, 10), 1, 1)) > 0
    compatible = tuple(
        str(tuple(map(str, point))) for point in STABLE_SIDE_POINTS
        if hidden_pairing(point) > 0
    )
    return WallStabilityReport(
        rows, True, {str(k): str(v) for k, v in at_wall.items()}, str((2, 0)),
        checks, opposite, hidden_compatible_wall_interval(), compatible,
    )


if __name__ == "__main__":
    report = build_report()
    print("constituents stable on entire wall:", report.constituents_stable_on_entire_wall)
    print("wall case bounds:", report.wall_case_bounds_at_s_one)
    print("stable-side checks:", report.stable_side_spot_checks)
