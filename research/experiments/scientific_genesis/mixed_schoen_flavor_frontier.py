"""Rerank exact flavor sectors after certified chain-level obstructions.

Owns:
    The deterministic next-sector selection after excluding the all-orders
    up-type no-go and the missing down-Higgs chain character.

Depends on:
    Published flavor-character support, the universal up no-go, and the exact
    down-Higgs character-complex obstruction.

Must not:
    Rank sectors by observations, invent a missing representative, select a
    carrier point, or treat character support as a Yukawa coefficient.

Phase 0:
    Research-only fail-closed scheduler for the next exact flavor matrix.
"""

from __future__ import annotations

import json
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .mixed_schoen_down_higgs_action import OUTPUT as DOWN_HIGGS_ARTIFACT
from .mixed_schoen_flavor_character_support import OUTPUT as SUPPORT_ARTIFACT
from .mixed_schoen_up_yukawa_no_go import OUTPUT as UP_NO_GO_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_flavor_frontier.json"


def _verified_payload(
    path: Path,
    gate: str,
) -> tuple[str, dict[str, object]]:
    """Load one content-addressed prerequisite after its exact gate passes."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest failed: {path.name}")
    if payload.get(gate) is not True:
        raise ValueError(f"upstream artifact gate failed: {path.name}")
    return digest, payload


def flavor_frontier() -> dict[str, object]:
    """Select the least-work sector whose exact chain inputs remain available."""

    support_digest, support = _verified_payload(
        SUPPORT_ARTIFACT,
        "all_character_products_invariant",
    )
    up_digest, up = _verified_payload(UP_NO_GO_ARTIFACT, "exact")
    down_digest, down = _verified_payload(
        DOWN_HIGGS_ARTIFACT,
        "route_blocked_exact",
    )
    if up.get("classification") != "SCOPED_HOLOMORPHIC_UP_NO_GO":
        raise ValueError("the up exclusion is not the scoped branch theorem")
    if down.get("required_character") != [0, 2]:
        raise ValueError("the down-Higgs obstruction changed character")
    sectors = {
        record["name"]: record
        for record in support["sectors"]
    }
    excluded = {
        "up": "complete universal holomorphic matrix has exact rank zero",
        "down": "required strict Higgs character has exact chain H1 dimension zero",
    }
    available = [
        sector
        for name, sector in sectors.items()
        if name not in excluded
    ]
    selected = min(
        available,
        key=lambda sector: (
            sector["minimum_new_chain_object_count"],
            sector["name"],
        ),
    )
    if selected["name"] != "dirac_neutrino":
        raise ValueError("the exact post-obstruction frontier changed")
    payload: dict[str, object] = {
        "schema": "mixed-schoen-flavor-frontier-v1",
        "coefficient_field": "Q(omega)",
        "prerequisite_artifact_digests": {
            "flavor_character_support": support_digest,
            "universal_up_no_go": up_digest,
            "down_higgs_chain_obstruction": down_digest,
        },
        "excluded_sectors": [
            {"name": name, "exact_reason": reason}
            for name, reason in excluded.items()
        ],
        "remaining_sector_workloads": {
            sector["name"]: sector["minimum_new_chain_object_count"]
            for sector in available
        },
        "selected_next_sector": selected["name"],
        "selected_coupling": selected["coupling"],
        "selected_required_cohomology_characters": selected[
            "required_cohomology_characters"
        ],
        "selected_required_new_matter_characters": selected[
            "missing_matter_characters"
        ],
        "selected_reused_higgs_character": selected[
            "required_cohomology_characters"
        ][2],
        "selected_minimum_new_chain_object_count": selected[
            "minimum_new_chain_object_count"
        ],
        "selection_exact": True,
        "observational_inputs_used": False,
        "arbitrary_extension_point_selected": False,
        "yukawa_coefficient_computed": False,
        "next_required_object": (
            "universal matter lifts in characters (0,0) and (0,2) for the "
            "Dirac-neutrino sector"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    return payload


def write_flavor_frontier(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed post-obstruction flavor frontier."""

    payload = flavor_frontier()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact flavor frontier and print its selected sector."""

    payload = write_flavor_frontier()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"selected_next_sector: {payload['selected_next_sector']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["OUTPUT", "flavor_frontier", "write_flavor_frontier"]
