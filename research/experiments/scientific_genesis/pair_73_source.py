"""Extract a content-addressed pair-local source record for Scientific Genesis.

Owns:
    Validation and compact extraction of global pair 73 from the complete
    invariant-cocycle artifact for memory-bounded downstream reconstruction.

Depends on:
    The complete content-addressed invariant screen and its canonical digest
    validator; no scientific calculation is repeated or altered here.

Must not:
    Modify cocycles, omit their structural coordinates, select an extension
    point, or promote pair-local evidence beyond its parent certificate.

Phase 0:
    Pair-local evidence extraction only; carrier construction remains research.
"""

from __future__ import annotations

import json
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    DEFAULT_INVARIANT_ARTIFACT,
    _canonical_digest,
    _validated_invariant_records,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/pair_73_source.json"
PAIR_INDEX = 73


def write_pair_73_source(path: Path = OUTPUT) -> dict[str, object]:
    """Validate the parent artifact and write its exact pair-73 record."""

    parent_digest, records = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    pair = records[PAIR_INDEX - 1]
    if pair.get("global_pair_index") != PAIR_INDEX or pair.get("exact") is not True:
        raise ValueError("pair-73 source identity or exact gate failed")
    payload: dict[str, object] = {
        "schema": "scientific-genesis-pair-source-v1",
        "global_pair_index": PAIR_INDEX,
        "parent_artifact_digest": parent_digest,
        "pair_certificate_digest": pair["certificate_digest"],
        "pair": pair,
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact pair-local source artifact."""

    payload = write_pair_73_source()
    pair = payload["pair"]
    if not isinstance(pair, dict):
        raise ValueError("pair-local source record is invalid")
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"parent_artifact_digest: {payload['parent_artifact_digest']}")
    print(f"cocycle_dimension: {pair['cocycle_basis']['dimension']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
