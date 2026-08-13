"""Certify the published constituent Serre extension-space dimensions.

Owns:
    A content-addressed record of the exact fiber-sensitive dP9 total
    complexes for the published length-three and length-six point schemes.

Depends on:
    The executable dP9 Serre Ext construction and source-bound constituent
    action dimensions used only as an independent comparison target.

Must not:
    Import action matrices into the calculation, identify total cocycles with
    published equivariant rays, or claim that W1 and W2 have been descended.

Phase 0:
    Constituent extension-space dimensions are derived; deck-linearized
    representatives and the outer carrier complex remain unresolved.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.models.heterotic_schoen.visible import serre_data
from research.experiments.computable_carrier.dp9_serre_ext import (
    DPSurfaceSerreExt,
    published_constituent_serre_exts,
)
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/published_constituent_ext_spaces.json"


@dataclass(frozen=True, slots=True)
class PublishedConstituentExtSpaces:
    """Exact dP9 Serre Ext dimensions and their independent source check."""

    constituents: tuple[DPSurfaceSerreExt, ...]
    source_bound_dimensions: tuple[int, ...]

    def __post_init__(self) -> None:
        if tuple(item.scheme.name for item in self.constituents) != ("I3", "I6"):
            raise ValueError("the published point-scheme order changed")
        if tuple(item.surface_factor for item in self.constituents) != (1, 2):
            raise ValueError("the published dP9 factor assignment changed")
        if self.source_bound_dimensions != (2, 5):
            raise ValueError("the source-bound constituent dimensions changed")
        if not all(item.squared_zero for item in self.constituents):
            raise ValueError("a constituent total differential is not square zero")
        if self.computed_dimensions != self.source_bound_dimensions:
            raise ValueError("computed constituent Ext dimensions do not match the source")

    @property
    def computed_dimensions(self) -> tuple[int, ...]:
        """Return exact total-cohomology dimensions in constituent order."""

        return tuple(item.ext_one_dimension for item in self.constituents)

    def as_record(self) -> dict[str, object]:
        """Serialize the promoted dimension certificate and open boundary."""

        return {
            "schema": "published-constituent-ext-spaces-v1",
            "constituents": [item.as_record() for item in self.constituents],
            "source_bound_dimensions": list(self.source_bound_dimensions),
            "computed_dimensions": list(self.computed_dimensions),
            "dimension_match_exact": True,
            "published_action_matrices_used_in_computation": False,
            "equivariant_extension_rays_selected": False,
            "constituent_descent_claimed": False,
            "next_required_object": (
                "exact deck action on the dP9 total complexes and induced "
                "action on their Ext-one representatives"
            ),
            "status": (
                "computed fiber-sensitive constituent extension spaces; "
                "equivariant chain representatives remain unresolved"
            ),
        }


@cache
def published_constituent_ext_spaces() -> PublishedConstituentExtSpaces:
    """Compute the constituent spaces and compare only their dimensions."""

    source_dimensions = tuple(action.dimension for action in serre_data().actions)
    return PublishedConstituentExtSpaces(
        published_constituent_serre_exts(),
        source_dimensions,
    )


def write_published_constituent_ext_spaces(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed exact constituent-space certificate."""

    payload = published_constituent_ext_spaces().as_record()
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
    """Regenerate the exact constituent extension-space artifact."""

    payload = write_published_constituent_ext_spaces()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"computed_dimensions: {payload['computed_dimensions']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PublishedConstituentExtSpaces",
    "published_constituent_ext_spaces",
]
