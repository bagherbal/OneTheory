"""Refute the projective-pushout adapter for the published visible carrier.

Owns:
    Exact forward and reverse Schoen-cover Hom dimensions obtained by applying
    the current I3/I6 base pushouts to the published constituent twists.

Depends on:
    Source-bound visible-carrier dimensions, exact Tier A pushouts, and the
    sparse Schoen Koszul outer-Hom engine.

Must not:
    Refute the published carrier, identify a base pushout with W1 or W2, or
    fabricate the missing fiber-sensitive Serre maps.

Phase 0:
    Research-only incompatibility certificate for one tempting reconstruction.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_outer import (
    sparse_outer_hom_candidates,
)
from research.experiments.computable_carrier.serre_pushout import (
    tier_a_serre_pushouts,
)

ROOT = Path(__file__).resolve().parents[3]
VISIBLE_ARTIFACT = ROOT / "data/generated/visible_carrier/visible_carrier_artifact.json"
OUTPUT = ROOT / "data/generated/scientific_genesis/published_pushout_mismatch.json"


def _canonical_total_dimensions(
    dimensions: tuple[tuple[int, int], ...],
) -> list[list[int]]:
    """Keep exact support with one zero-dimensional boundary on each side."""

    values = dict(dimensions)
    support = [degree for degree, dimension in dimensions if dimension > 0]
    if not support:
        return []
    return [
        [degree, values.get(degree, 0)]
        for degree in range(min(support) - 1, max(support) + 2)
    ]


def _published_dimensions() -> tuple[int, int, int, int]:
    """Read and verify the source-bound cover and quotient Ext dimensions."""

    payload = json.loads(VISIBLE_ARTIFACT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError("the visible-carrier artifact digest does not verify")
    outer = payload.get("outer_extension")
    flavor = payload.get("flavor")
    if not isinstance(outer, dict) or not isinstance(flavor, dict):
        raise ValueError("the visible-carrier Ext ledger is malformed")
    cohomology = outer.get("cohomology_dimensions_h0_to_h3")
    split_wall = flavor.get("abstract_split_wall")
    if not (
        isinstance(cohomology, list)
        and len(cohomology) == 4
        and all(isinstance(value, int) for value in cohomology)
        and isinstance(split_wall, dict)
        and isinstance(split_wall.get("forward_dimension"), int)
        and isinstance(split_wall.get("reverse_dimension"), int)
    ):
        raise ValueError("the visible-carrier Ext dimensions are malformed")
    return (
        cohomology[1],
        cohomology[2],
        split_wall["forward_dimension"],
        split_wall["reverse_dimension"],
    )


@dataclass(frozen=True, slots=True)
class PublishedPushoutMismatch:
    """Exact failure of the base-pushout presentation substitution."""

    expected_forward_cover_ext_one: int
    expected_reverse_cover_ext_one: int
    expected_forward_invariant_ext_one: int
    expected_reverse_invariant_ext_one: int
    computed_forward_cover_ext_one: int
    computed_reverse_cover_ext_one: int
    forward_total_dimensions: tuple[tuple[int, int], ...]
    reverse_total_dimensions: tuple[tuple[int, int], ...]
    both_complexes_squared_zero: bool

    def __post_init__(self) -> None:
        if (
            self.expected_forward_cover_ext_one,
            self.expected_reverse_cover_ext_one,
            self.expected_forward_invariant_ext_one,
            self.expected_reverse_invariant_ext_one,
        ) != (36, 72, 4, 8):
            raise ValueError("the source-bound visible Ext ledger changed")
        if (
            self.computed_forward_cover_ext_one,
            self.computed_reverse_cover_ext_one,
        ) != (0, 63):
            raise ValueError("the projective-pushout mismatch changed")
        if not self.both_complexes_squared_zero:
            raise ValueError("the projective-pushout complexes are not exact complexes")
        if (
            self.computed_forward_cover_ext_one
            == self.expected_forward_cover_ext_one
            or self.computed_reverse_cover_ext_one
            == self.expected_reverse_cover_ext_one
        ):
            raise ValueError("the adapter unexpectedly matches a published Ext direction")

    def as_record(self) -> dict[str, object]:
        """Serialize the fail-closed reconstruction mismatch and scope."""

        return {
            "schema": "published-pushout-mismatch-v1",
            "published_source_ledger": {
                "forward_cover_ext_one_dimension": self.expected_forward_cover_ext_one,
                "reverse_cover_ext_one_dimension": self.expected_reverse_cover_ext_one,
                "forward_invariant_ext_one_dimension": (
                    self.expected_forward_invariant_ext_one
                ),
                "reverse_invariant_ext_one_dimension": (
                    self.expected_reverse_invariant_ext_one
                ),
            },
            "tested_adapter": {
                "left_base_pushout": "I3",
                "right_base_pushout": "I6",
                "left_factor_and_twist": [1, [-1, 1, 0]],
                "right_factor_and_twist": [2, [1, -1, 0]],
                "forward_cover_ext_one_dimension": (
                    self.computed_forward_cover_ext_one
                ),
                "reverse_cover_ext_one_dimension": (
                    self.computed_reverse_cover_ext_one
                ),
                "forward_total_dimensions": _canonical_total_dimensions(
                    self.forward_total_dimensions
                ),
                "reverse_total_dimensions": _canonical_total_dimensions(
                    self.reverse_total_dimensions
                ),
                "both_complexes_squared_zero": self.both_complexes_squared_zero,
            },
            "dimension_mismatch_exact": True,
            "base_pushouts_identified_with_published_constituents": False,
            "published_carrier_refuted": False,
            "missing_mathematical_data": [
                "fiber-sensitive dP9 Serre presentations for W1 and W2",
                "their exact deck-linearized chain maps",
                "a synchronized Schoen Cech-Koszul convention",
            ],
            "next_required_object": (
                "exact fiber-sensitive dP9 Serre presentation of W1 and W2 "
                "before recomputing the published outer Hom"
            ),
            "status": (
                "exact adapter no-go: current base-projective pushouts are not "
                "chain models of the published W1/W2 constituents"
            ),
        }


@cache
def published_pushout_mismatch() -> PublishedPushoutMismatch:
    """Compute both exact outer-Hom directions for the tested adapter."""

    expected = _published_dimensions()
    w1_adapter, w2_adapter = tier_a_serre_pushouts()
    forward = sparse_outer_hom_candidates(
        w1_adapter,
        w2_adapter,
        1,
        (-1, 1, 0),
        2,
        (1, -1, 0),
    )
    reverse = sparse_outer_hom_candidates(
        w2_adapter,
        w1_adapter,
        2,
        (1, -1, 0),
        1,
        (-1, 1, 0),
    )
    return PublishedPushoutMismatch(
        *expected,
        forward.cover_ext_one_dimension,
        reverse.cover_ext_one_dimension,
        tuple(
            (degree, space.dimension)
            for degree, space in forward.total_spaces
        ),
        tuple(
            (degree, space.dimension)
            for degree, space in reverse.total_spaces
        ),
        forward.squared_zero and reverse.squared_zero,
    )


def write_published_pushout_mismatch(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed adapter no-go atomically."""

    payload = published_pushout_mismatch().as_record()
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
    """Regenerate the exact published-pushout mismatch artifact."""

    payload = write_published_pushout_mismatch()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"dimension_mismatch_exact: {payload['dimension_mismatch_exact']}")
    print(f"published_carrier_refuted: {payload['published_carrier_refuted']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PublishedPushoutMismatch",
    "published_pushout_mismatch",
]
