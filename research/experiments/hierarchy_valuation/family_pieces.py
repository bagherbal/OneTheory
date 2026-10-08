"""Locate every family of the frozen carrier in its complete filtration.

Owns:
    Exact cover cohomology of both Serre sublines from the two-equation Koszul
    complex, the induced injection of each constituent's H1 into its quotient
    piece, and the tropical singular-value orders allowed by any U(1) charges
    attached to the graded pieces of 0 < L1 < V1 < V1+L2 < V.

Depends on:
    Exact ambient Schoen line cohomology, the published complete-intersection
    degrees, and the recorded alternate constituent matter profile.

Must not:
    Assign charges, choose walls or Kähler classes, compute metrics, or use
    observations.

Phase 0:
    Research structural theorem extending the stability-wall valuation result.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import combinations, permutations
from pathlib import Path

from research.experiments.scientific_genesis.alternate_metric_subbundle_vanishing import (
    _equation_degrees,
    _koszul_profile,
)

ROOT = Path(__file__).resolve().parents[3]
GENERATED = ROOT / "data/generated/scientific_genesis"
MATTER_PROFILE = GENERATED / "alternate_constituent_matter_profile.json"

# Serre sublines in cover (tau1, tau2, phi) order: V1 subline (13,17,0) at the
# metric twist (14,16,1), alternate V2 subline (6,6,0) at the trial twist (5,7,1).
SERRE_SUBLINES = {"V1": (-1, 1, -1), "V2": (1, -1, -1)}


def koszul_line_cohomology(degree: tuple[int, int, int]) -> tuple[int, int, int, int]:
    """H0..H3 of O_X(degree) when exactly one Koszul column has cohomology.

    For 0 -> K2 -> K1 -> K0 -> O_X(L) -> 0, a single nonzero column K_j with
    ambient H^q contributes H^(q-j) on X with no possible differential.
    Mixed supports are rejected rather than resolved by a guessed differential.
    """

    profile = _koszul_profile(degree, _equation_degrees())
    columns = {"k0": 0, "k1_x": 1, "k1_u": 1, "k2": 2}
    contributions: dict[int, int] = {}
    for name, shift in columns.items():
        dims = profile[name]["ambient_h0_to_h5"]  # type: ignore[index]
        for q, dim in enumerate(dims):
            if dim:
                contributions[q - shift] = contributions.get(q - shift, 0) + dim
    supporting = [
        name for name in columns
        if any(profile[name]["ambient_h0_to_h5"])  # type: ignore[index]
    ]
    if len(supporting) > 1:
        raise ValueError("several Koszul columns carry cohomology; a differential may act")
    if any(degree_ < 0 or degree_ > 3 for degree_ in contributions):
        raise ValueError("Koszul contribution outside the threefold range")
    return tuple(contributions.get(i, 0) for i in range(4))  # type: ignore[return-value]


@dataclass(frozen=True)
class FamilyPieces:
    subline_cohomology: dict[str, tuple[int, int, int, int]]
    constituent_h1: dict[str, int]
    occupied_graded_pieces: tuple[str, ...]
    family_count_by_piece: dict[str, int]
    max_distinct_family_charges: int
    charges_obstruct_three_level_hierarchy: bool


def tropical_orders(row: tuple[int, ...], col: tuple[int, ...], offset: int) -> tuple[float, ...]:
    """Generic singular-value orders of entries eps^(row_i + col_j + offset).

    An entry with negative total charge is holomorphically forbidden (zero).
    The cumulative k-th order is the minimum, over k x k minors, of the minimal
    admissible permutation weight; ``inf`` marks generic rank deficiency.
    """

    infinity = float("inf")
    n = len(row)
    cumulative = [0.0]
    for k in range(1, n + 1):
        best = infinity
        for rows in combinations(range(n), k):
            for cols in combinations(range(n), k):
                for image in permutations(cols):
                    weight = 0.0
                    for i, j in zip(rows, image, strict=True):
                        total = row[i] + col[j] + offset
                        if total < 0:
                            weight = infinity
                            break
                        weight += total
                    best = min(best, weight)
        cumulative.append(best)
    return tuple(
        cumulative[k] - cumulative[k - 1] if cumulative[k] < infinity else infinity
        for k in range(1, n + 1)
    )


def two_piece_violations(bound: int = 4) -> tuple[int, tuple[tuple[int, int, int], ...]]:
    """Exhaust charges (a,b,b) shared by left and right fields with offset h.

    Returns the number of cases and every case with three distinct finite
    orders; the theorem is that the second component is empty.
    """

    cases, violations = 0, []
    for a in range(-bound, bound + 1):
        for b in range(-bound, bound + 1):
            for h in range(-2 * bound, 2 * bound + 1):
                cases += 1
                finite = [o for o in tropical_orders((a, b, b), (a, b, b), h) if o != float("inf")]
                if len(finite) == 3 and len(set(finite)) == 3:
                    violations.append((a, b, h))
    return cases, tuple(violations)


def audit_family_pieces() -> FamilyPieces:
    sublines = {name: koszul_line_cohomology(line) for name, line in SERRE_SUBLINES.items()}
    profile = json.loads(MATTER_PROFILE.read_text())
    v1 = tuple(profile["first_constituent_cover_h0_to_h3"])
    total = tuple(profile["visible_cover_h0_to_h3"])
    if v1 != (0, 9, 0, 0) or total != (0, 27, 0, 0):
        raise ValueError("recorded constituent matter profiles changed")
    h1 = {"V1": v1[1], "V2": total[1] - v1[1]}
    if any(cohomology[1] != 0 for cohomology in sublines.values()):
        raise ValueError("a Serre subline carries H1; families could sit in it")
    # H1(L_i) = 0 makes H1(V_i) -> H1(V_i / L_i) injective; H2(V1) = 0 makes
    # H1(V) an extension of H1(V2) by H1(V1).
    pieces = {"L1": 0, "V1/L1": h1["V1"] // 9, "L2": 0, "V/(V1+L2)": h1["V2"] // 9}
    occupied = tuple(name for name, count in pieces.items() if count)
    # Families in one graded piece share every filtration charge, and left-
    # and right-handed fields both come from H1(V), so they share the vector.
    distinct = len(occupied)
    _, violations = two_piece_violations()
    if distinct < 3 and violations:
        raise ValueError("a two-piece charge pattern produced three distinct orders")
    return FamilyPieces(
        sublines, h1, occupied, pieces, distinct, distinct < 3,
    )


if __name__ == "__main__":
    print(audit_family_pieces())
