"""Classify the reduced outer model's common 90-dimensional excess.

Owns:
    Exact forward/reverse cohomology of the ambient-cohomology-reduced
    constituent cones, comparison with the source-bound carrier dimensions,
    and the resulting homotopy-transfer prerequisite.

Depends on:
    Certified constituent mapping cones, the reduced sparse Schoen outer
    model, and immutable published outer-dimension metadata.

Must not:
    Refute the published carrier, insert a rank-90 map by hand, identify an
    E-page with full hypercohomology, or claim invariant outer cocycles.

Phase 0:
    Exact reduced-model mismatch certificate; full Čech contraction remains
    the next research calculation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer import (
    SchoenSerreOuterHom,
    schoen_serre_constituent,
    schoen_serre_outer_hom,
)

from .published_constituent_mapping_cones import published_constituent_mapping_cones

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/published_outer_reduced_mismatch.json"


@dataclass(frozen=True, slots=True)
class PublishedOuterReducedMismatch:
    """Exact E-page excess relative to the published outer hypercohomology."""

    forward: SchoenSerreOuterHom
    reverse: SchoenSerreOuterHom
    published_forward: tuple[int, int]
    published_reverse: tuple[int, int]

    @property
    def computed_forward(self) -> tuple[int, int]:
        """Return reduced forward ``(H1,H2)`` dimensions."""

        return (
            self.forward.cohomology_dimension(1),
            self.forward.cohomology_dimension(2),
        )

    @property
    def computed_reverse(self) -> tuple[int, int]:
        """Return reduced reverse ``(H1,H2)`` dimensions."""

        return (
            self.reverse.cohomology_dimension(1),
            self.reverse.cohomology_dimension(2),
        )

    @property
    def common_excess(self) -> int:
        """Return the equal H1/H2 reduction still required in each direction."""

        differences = (
            self.computed_forward[0] - self.published_forward[0],
            self.computed_forward[1] - self.published_forward[1],
            self.computed_reverse[0] - self.published_reverse[0],
            self.computed_reverse[1] - self.published_reverse[1],
        )
        if len(set(differences)) != 1:
            raise ValueError("reduced outer mismatch is not one common excess")
        return differences[0]

    @property
    def euler_characteristics_match(self) -> bool:
        """Return whether reduction preserves both source Euler characteristics."""

        return (
            self.computed_forward[0] - self.computed_forward[1]
            == self.published_forward[0] - self.published_forward[1]
            and self.computed_reverse[0] - self.computed_reverse[1]
            == self.published_reverse[0] - self.published_reverse[1]
        )

    def __post_init__(self) -> None:
        if self.published_forward != (36, 72) or self.published_reverse != (72, 36):
            raise ValueError("published outer dimensions changed")
        if self.computed_forward != (126, 162):
            raise ValueError("forward reduced outer dimensions changed")
        if self.computed_reverse != (162, 126):
            raise ValueError("reverse reduced outer dimensions changed")
        if not self.forward.squared_zero or not self.reverse.squared_zero:
            raise ValueError("a reduced outer total differential is not square zero")
        if not self.euler_characteristics_match or self.common_excess != 90:
            raise ValueError("reduced outer mismatch lost its structural rank identity")

    def as_record(self) -> dict[str, object]:
        """Serialize the mismatch and forbid a fabricated correction map."""

        return {
            "schema": "published-outer-reduced-mismatch-v1",
            "forward": {
                "computed_h1_h2": list(self.computed_forward),
                "published_h1_h2": list(self.published_forward),
                "total_dimensions": [
                    [degree, space.dimension]
                    for degree, space in self.forward.total_spaces
                ],
                "squared_zero": self.forward.squared_zero,
            },
            "reverse": {
                "computed_h1_h2": list(self.computed_reverse),
                "published_h1_h2": list(self.published_reverse),
                "total_dimensions": [
                    [degree, space.dimension]
                    for degree, space in self.reverse.total_spaces
                ],
                "squared_zero": self.reverse.squared_zero,
            },
            "euler_characteristics_match": self.euler_characteristics_match,
            "common_cohomology_excess": self.common_excess,
            "rank_90_map_inserted": False,
            "published_carrier_refuted": False,
            "mathematical_interpretation": (
                "ambient Cech cohomology reduction omits transferred "
                "differentials/homotopies needed by the full hypercohomology"
            ),
            "next_required_object": (
                "full standard-cover Cech contraction for the constituent "
                "twisted outer complex and its transferred differential"
            ),
            "status": (
                "exact reduced-model mismatch with a common 90-dimensional "
                "excess; no correction is guessed"
            ),
        }


@cache
def published_outer_reduced_mismatch() -> PublishedOuterReducedMismatch:
    """Build both reduced outer directions without source dimensions as inputs."""

    w1_cone, w2_cone = published_constituent_mapping_cones()
    v1 = schoen_serre_constituent("V1", 1, (-1, 1, 0), w1_cone.cocycle)
    v2 = schoen_serre_constituent("V2", 2, (1, -1, 0), w2_cone.cocycle)
    return PublishedOuterReducedMismatch(
        schoen_serre_outer_hom(v1, v2),
        schoen_serre_outer_hom(v2, v1),
        (36, 72),
        (72, 36),
    )


def write_published_outer_reduced_mismatch(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed reduced outer mismatch certificate."""

    payload = published_outer_reduced_mismatch().as_record()
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
    """Regenerate the reduced outer mismatch artifact."""

    payload = write_published_outer_reduced_mismatch()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"common_cohomology_excess: {payload['common_cohomology_excess']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PublishedOuterReducedMismatch",
    "published_outer_reduced_mismatch",
]
