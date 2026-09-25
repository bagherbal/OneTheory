"""Compute the first determinant-repairable alternate outer Ext space.

Owns:
    Exact reduced degree-zero and degree-one outer-Hom differentials for the
    unused I6 ray (0,1), with square-zero and cohomology-dimension checks.

Depends on:
    The conditional character screen, exact alternate mixed constituent,
    and the existing synchronized Schoen outer-Hom transfer engine.

Must not:
    Assume an invariant Ext class, select an extension point, construct a
    rank-four cone, or claim stability or a physical Higgs sector.

Phase 0:
    Research-only prerequisite for an equivariant universal outer extension.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .alternate_constituent_character_screen import OUTPUT as SCREEN
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import _constituent, mixed_schoen_constituents
from .mixed_schoen_outer_transfer import _transfer_map
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_constituent_outer_ext.json"


def _certified_screen() -> str:
    """Require the exact conditional selector without treating it as a cone."""

    record = cast(dict[str, object], json.loads(SCREEN.read_text(encoding="utf-8")))
    digest = record.pop("artifact_digest", None)
    if (
        record.get("schema") != "alternate-constituent-character-screen-v1"
        or digest != _canonical_digest(record)
        or record.get("ray_0_1_passes_conditional_higgs_screen") is not True
        or record.get("outer_extension_constructed") is not False
    ):
        raise ValueError("the alternate character-screen prerequisite changed")
    return cast(str, digest)


def alternate_constituent_outer_ext() -> dict[str, object]:
    """Compute cover Ext1(V2,V1) for the surviving alternate ray."""

    screen_digest = _certified_screen()
    first = mixed_schoen_constituents()[0]
    action = published_constituent_deck_actions()[1]
    full = lift_joint_character_ray(action, OMEGA**0, OMEGA**1)
    second = _constituent(full, "I6-ray-0-1", 2, (1, -1, 0))
    with ProcessPoolExecutor(max_workers=2) as pool:
        futures = {
            degree: pool.submit(_transfer_map, first, second, degree)
            for degree in (0, 1)
        }
        incoming, incoming_depth = futures[0].result()
        outgoing, outgoing_depth = futures[1].result()
    if incoming.codomain.dimension != outgoing.domain.dimension:
        raise ValueError("the alternate outer maps do not meet in degree one")
    if not outgoing.compose(incoming).is_zero():
        raise ValueError("the alternate outer differential is not square zero")
    incoming_rank = incoming.rank()
    outgoing_rank = outgoing.rank()
    h0 = incoming.domain.dimension - incoming_rank
    h1 = outgoing.domain.dimension - incoming_rank - outgoing_rank
    if h0 < 0 or h1 < 0:
        raise ValueError("the alternate Ext dimensions are negative")
    return {
        "schema": "alternate-constituent-outer-ext-v1",
        "scope": "cover Ext of V2 into V1 for the unused I6 ray (0,1)",
        "screen_artifact_digest": screen_digest,
        "ray_character_exponents": [0, 1],
        "outer_orientation": "Hom(V2,V1)",
        "reduced_dimensions_degree_0_to_2": [
            incoming.domain.dimension,
            incoming.codomain.dimension,
            outgoing.codomain.dimension,
        ],
        "differential_ranks_degree_0_to_1": [incoming_rank, outgoing_rank],
        "transfer_path_depths_degree_0_to_1": [incoming_depth, outgoing_depth],
        "d_squared_zero": True,
        "cover_h0_dimension": h0,
        "cover_ext1_dimension": h1,
        "invariant_ext1_dimension_computed": False,
        "outer_extension_constructed": False,
        "determinant_repaired_universal_cone_constructed": False,
        "next_required_object": (
            "transfer the exact atlas P/T action to outer Ext1, determine "
            "its invariant locus, then construct the universal cone"
        ),
    }


def write_alternate_constituent_outer_ext(path: Path = OUTPUT) -> dict[str, object]:
    """Write the exact content-addressed alternate outer-Ext prerequisite."""

    payload = alternate_constituent_outer_ext()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_constituent_outer_ext()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"cover_ext1_dimension: {report['cover_ext1_dimension']}")
