"""Build the exact reverse mixed outer extension family.

Owns:
    The universal parameter-linear cone on the six strict invariant classes in
    RHom(V1,V2), including split, square-zero, descent, and topology gates.

Depends on:
    The selected constituent chain, its exact reverse deck invariants, and the
    model-independent universal mixed-cone construction.

Must not:
    Select a projective point, infer an uncomputed stability chamber, reuse
    retired pure-Cech classes, or call the reverse family genuinely SU(4).

Phase 0:
    Research-only reverse rank-four derived family before stability.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .mixed_schoen_outer_universal_cone import (
    MixedSchoenUniversalOuterCone,
    _build_universal_outer_cone,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_reverse_outer_universal_cone.json"
)


@cache
def mixed_schoen_reverse_universal_outer_cone() -> (
    MixedSchoenUniversalOuterCone
):
    """Construct the exact reverse P5 family without choosing a point."""

    return _build_universal_outer_cone(
        "V2",
        "V1",
        "b",
        "mixed-schoen-reverse-outer-universal-cone-v1",
    )


def write_mixed_schoen_reverse_universal_outer_cone(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed reverse universal-cone certificate."""

    payload = mixed_schoen_reverse_universal_outer_cone().as_record()
    payload["extension_sequence"] = "0 -> V2 -> E_reverse -> V1 -> 0"
    payload["published_stability_scope"] = {
        "arxiv_id": "hep-th/0602073",
        "version": "v1",
        "source_archive_sha256": (
            "8e38123b9d2de8751deecbf295015497ab2ed891244215455fffe756bebf0aea"
        ),
        "result": (
            "a nonempty reverse stable subcone exists across the marginal wall"
        ),
        "used_as_existence_only": True,
    }
    payload["exact_reverse_stability_locus_computed"] = False
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact reverse universal-cone certificate."""

    payload = write_mixed_schoen_reverse_universal_outer_cone()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"projective_non_split_space: {payload['projective_non_split_space']}")
    print(
        "exact_reverse_stability_locus_computed: "
        f"{payload['exact_reverse_stability_locus_computed']}"
    )
    print(f"first_missing_input: {payload['first_missing_input']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "mixed_schoen_reverse_universal_outer_cone",
    "write_mixed_schoen_reverse_universal_outer_cone",
]
