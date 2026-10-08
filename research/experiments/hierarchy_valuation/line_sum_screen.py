"""Scoped screen for SU(4) line-bundle sums with families in three slots.

Owns:
    Exact cover cohomology of Schoen line bundles from the two-equation Koszul
    E2 page whenever no d2 transgression can act, the descent congruence filter, and
    an exhaustive search for c1-trivial four-line sums with 27 cover families,
    no anti-families, and family cohomology in at least three distinct slots.

Depends on:
    Exact ambient Schoen line cohomology, the published equation degrees, and
    the production descent congruence.

Must not:
    Guess a d2 transgression, treat the congruence as
    sufficient for equivariance, claim stability, or use observations.

Phase 0:
    Research gate-G3 screen; d2-ambiguous lines are reported as unresolved.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from itertools import combinations_with_replacement
from pathlib import Path

from onetheory.math.homological import LinearMap
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.schoen_linebundles import (
    _equation_one,
    _equation_two,
    ambient_schoen_line_bundle,
)

BOX = 4
ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/hierarchy_valuation/line_sum_screen.json"


def _dimension(degree: tuple[int, int, int], q: int) -> int:
    return ambient_schoen_line_bundle(*degree).space(q).vector_space.dimension


def line_cohomology(degree: tuple[int, int, int]) -> tuple[int, int, int, int] | None:
    """Exact H0..H3 of O_X(degree), or ``None`` when a d2 transgression may act.

    Columns K0, K1 = K1x + K1u, K2 of the two-equation Koszul resolution carry
    ambient cohomology; d1 is multiplication by the actual Schoen equations.
    The only higher differential, d2: E2(-2,q) -> E2(0,q-1), is never guessed:
    a line is resolved only if every such pair has a zero source or target.
    """

    a, b, c = degree
    k0, k1x, k1u, k2 = (a, b, c), (a - 3, b, c - 1), (a, b - 3, c - 1), (a - 3, b - 3, c - 2)
    page: dict[tuple[int, int], int] = {}
    for q in range(6):
        d0, d1x, d1u, d2 = (_dimension(k, q) for k in (k0, k1x, k1u, k2))
        r1 = r2 = 0
        if d0 and (d1x or d1u):
            r1 = LinearMap.block(((_equation_one(k1x, k0, q), _equation_two(k1u, k0, q)),)).rank()
        if d2 and (d1x or d1u):
            r2 = LinearMap.block(
                ((-_equation_two(k2, k1x, q),), (_equation_one(k2, k1u, q),)),
            ).rank()
        page[(0, q)] = d0 - r1
        page[(-1, q)] = d1x + d1u - r1 - r2
        page[(-2, q)] = d2 - r2
    if any(page[(-2, q)] and page[(0, q - 1)] for q in range(1, 6)):
        return None
    return tuple(  # type: ignore[return-value]
        page[(0, k)] + page[(-1, k + 1)] + (page[(-2, k + 2)] if k + 2 < 6 else 0)
        for k in range(4)
    )


def euler_characteristic(degree: tuple[int, int, int]) -> int:
    """Exact chi(O_X(degree)) from the ambient Koszul columns; no differential enters."""

    a, b, c = degree
    columns = (((a, b, c), 0), ((a - 3, b, c - 1), 1), ((a, b - 3, c - 1), 1),
               ((a - 3, b - 3, c - 2), 2))
    return sum(
        (-1) ** (q + shift) * _dimension(column, q) for column, shift in columns for q in range(6)
    )


@dataclass(frozen=True)
class LineSumScreen:
    box: int
    descending_lines: int
    resolved_pure_or_acyclic: int
    unresolved_d2_ambiguous: int
    unresolved_lines: tuple[tuple[int, int, int], ...]
    pure_h1_lines: tuple[tuple[tuple[int, int, int], int], ...]
    family_sums_any_slots: tuple[tuple[tuple[tuple[int, int, int], ...], tuple[int, ...]], ...]
    three_slot_candidates: tuple[tuple[tuple[int, int, int], ...], ...]
    unresolved_euler_characteristics: tuple[int, ...]
    optimistic_three_slot_candidates: tuple[tuple[tuple[int, int, int], ...], ...]


def screen(box: int = BOX, prefilter: bool = False) -> LineSumScreen:
    geometry = schoen_geometry()
    catalogue: dict[tuple[int, int, int], int] = {}
    descending = 0
    unresolved: list[tuple[int, int, int]] = []
    span = range(-box, box + 1)
    for a in span:
        for b in span:
            for c in span:
                if not geometry.descent_congruence((a, b, c)):
                    continue
                descending += 1
                # Rigorous prefilter: a summand of a 27-family sum without
                # anti-families is pure H1 with h1 <= 27 or acyclic.
                if prefilter and euler_characteristic((a, b, c)) not in (0, -9, -18, -27):
                    continue
                h = line_cohomology((a, b, c))
                if h is None:
                    unresolved.append((a, b, c))
                    continue
                if h[0] == h[2] == h[3] == 0 and h[1] % 9 == 0:
                    catalogue[(a, b, c)] = h[1]
    lines = sorted(catalogue)
    any_slots: dict[tuple[tuple[int, int, int], ...], tuple[int, ...]] = {}
    for trio in combinations_with_replacement(lines, 3):
        last = tuple(-sum(line[i] for line in trio) for i in range(3))
        if last not in catalogue:
            continue
        quad = tuple(sorted((*trio, last)))  # type: ignore[arg-type]
        families = tuple(catalogue[line] for line in quad)
        if sum(families) == 27:
            any_slots[quad] = families
    candidates = tuple(
        sorted(q for q, families in any_slots.items() if sum(1 for h in families if h) >= 3)
    )
    # Three slots with 27 families need three pure lines of exactly 9 each.
    # Admit every unresolved line optimistically: as a pure 9-line if chi = -9,
    # and as an acyclic fourth summand if chi = 0. Differentials cannot change chi.
    chis = tuple(euler_characteristic(line) for line in unresolved)
    nines = {line for line, h in catalogue.items() if h == 9}
    nines |= {line for line, chi in zip(unresolved, chis, strict=True) if chi == -9}
    acyclic = {line for line, h in catalogue.items() if h == 0}
    acyclic |= {line for line, chi in zip(unresolved, chis, strict=True) if chi == 0}
    optimistic = set()
    for trio in combinations_with_replacement(sorted(nines), 3):
        last = tuple(-sum(line[i] for line in trio) for i in range(3))
        if last in acyclic:
            optimistic.add(tuple(sorted((*trio, last))))
    return LineSumScreen(
        box, descending, len(catalogue), len(unresolved), tuple(unresolved),
        tuple((line, catalogue[line]) for line in lines if catalogue[line]),
        tuple(sorted(any_slots.items())), candidates, chis,
        tuple(sorted(optimistic)),  # type: ignore[arg-type]
    )


ARTIFACT_BOX = 8


def write_artifact(path: Path = OUTPUT) -> dict[str, object]:
    record: dict[str, object] = {
        "schema": "line-sum-three-slot-screen-v2",
        "euler_prefilter": "summands restricted to chi in {0,-9,-18,-27}",
        **json.loads(json.dumps(asdict(screen(box=ARTIFACT_BOX, prefilter=True)))),
        "equivariant_structures_constructed": False,
        "stability_checked": False,
        "observations_used": False,
    }
    payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    record["artifact_digest"] = hashlib.sha256(payload).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record




TEXTURES = ROOT / "data/generated/hierarchy_valuation/line_sum_textures.json"


def leading_texture(
    lines: tuple[tuple[int, int, int], ...], families: tuple[int, ...],
) -> dict[str, object]:
    """Leading 16.16.10 couplings of a split SU(4) sum.

    The automorphisms lambda_a of the slots, with product one, rescale a
    coupling 16_a 16_b 10_(cd) by lambda_a lambda_b lambda_c lambda_d, so a
    nonzero leading coupling needs four distinct slots. Families in slots s, t
    therefore couple only across slots, through the complementary Higgs pair.
    """

    slots = [i for i, h in enumerate(families) if h]
    couplings = []
    for a, b in ((a, b) for a in slots for b in slots if a < b):
        c, d = sorted(set(range(4)) - {a, b})
        pair = tuple(lines[c][k] + lines[d][k] for k in range(3))
        h = line_cohomology(pair)  # type: ignore[arg-type]
        couplings.append({"family_slots": [a, b], "higgs_slots": [c, d],
                          "higgs_line": list(pair), "higgs_h1": None if h is None else h[1]})
    live = [row for row in couplings if row["higgs_h1"]]
    if not live:
        kind = "no leading Yukawa"
    elif len(slots) == 2:
        kind = "cross: two unsuppressed families, one massless at leading order"
    else:
        kind = "three-slot"
    return {"lines": [list(x) for x in lines], "families": list(families),
            "couplings": couplings, "texture": kind}


def write_textures(path: Path = TEXTURES) -> dict[str, object]:
    screen_record = json.loads(OUTPUT.read_text())
    rows = [
        leading_texture(tuple(tuple(x) for x in quad), tuple(families))  # type: ignore[arg-type]
        for quad, families in screen_record["family_sums_any_slots"]
    ]
    record: dict[str, object] = {
        "schema": "line-sum-leading-textures-v1",
        "screen_digest": screen_record["artifact_digest"],
        "rows": rows,
        "one_heavy_texture_found": any(
            row["texture"] not in (
                "no leading Yukawa",
                "cross: two unsuppressed families, one massless at leading order",
            )
            for row in rows
        ),
        "observations_used": False,
    }
    payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    record["artifact_digest"] = hashlib.sha256(payload).hexdigest()
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


# Rank-two constituents of the frozen carrier: first Chern class and cover H1.
CONSTITUENTS = {"V1": ((-2, 2, 0), 9), "V2": ((2, -2, 0), 18)}


def one_family_lines(box: int) -> tuple[tuple[int, int, int], ...]:
    """Descending lines with cover cohomology exactly (0,9,0,0)."""

    geometry = schoen_geometry()
    span = range(-box, box + 1)
    return tuple(
        (a, b, c) for a in span for b in span for c in span
        if geometry.descent_congruence((a, b, c))
        and euler_characteristic((a, b, c)) == -9
        and line_cohomology((a, b, c)) == (0, 9, 0, 0)
    )


def partial_split_hits(box: int) -> dict[str, tuple[tuple[tuple[int, int, int], ...], ...]]:
    """W + L1 + L2 with W a frozen constituent and families in all three slots.

    Three slots with 27 cover families need W to carry exactly 9 and each line
    exactly 9, with c1(L1) + c1(L2) = -c1(W).
    """

    nines = one_family_lines(box)
    hits = {}
    for name, (c1, families) in CONSTITUENTS.items():
        need = tuple(-x for x in c1)
        pairs = tuple(
            (left, right) for left in nines for right in nines
            if left <= right and tuple(left[i] + right[i] for i in range(3)) == need
        )
        hits[name] = pairs if families == 9 else ()
    return hits


if __name__ == "__main__":
    print(write_artifact()["artifact_digest"])
    print(write_textures()["artifact_digest"])
