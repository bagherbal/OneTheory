"""Certify the full Čech transfer of the published constituent outer Homs.

Owns:
    Independent exact reconstruction of both cover outer-Ext dimensions from
    standard-cover contraction and finite homological perturbation.

Depends on:
    Exact constituent mapping cones, the full Čech outer transfer engine, and
    content-addressed deterministic artifact utilities.

Must not:
    Use published Ext dimensions as rank inputs, infer quotient invariants, fit
    a rank-90 correction, or claim the four outer extension cocycles exist.

Phase 0:
    Exact cover hypercohomology dimensions are reconstructed; deck-invariant
    outer cocycles and local transition data remain unresolved.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    TransferredOuterHom,
    transferred_schoen_serre_outer_hom,
)
from research.experiments.computable_carrier.schoen_sparse_outer import SparseMap

from .published_outer_reduced_mismatch import published_outer_reduced_mismatch

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/published_outer_cech_transfer.json"


def _map_digest(map_: SparseMap) -> str:
    """Hash one exact sparse matrix including its typed basis order."""

    digest = hashlib.sha256()
    digest.update(map_.domain.name.encode("utf-8"))
    digest.update(b"\0")
    digest.update(map_.codomain.name.encode("utf-8"))
    digest.update(b"\0")
    for row_index, row in enumerate(map_.rows):
        for column, value in row:
            record = (
                row_index,
                column,
                value.a.numerator,
                value.a.denominator,
                value.b.numerator,
                value.b.denominator,
            )
            digest.update(repr(record).encode("ascii"))
            digest.update(b"\0")
    return digest.hexdigest()


def _direction_record(result: TransferredOuterHom) -> dict[str, object]:
    """Serialize one independently transferred outer-Hom direction."""

    return {
        "orientation": f"RHom({result.reduced.right.name},{result.reduced.left.name})",
        "total_dimensions": [
            [degree, space.dimension] for degree, space in result.reduced.total_spaces
        ],
        "differential_ranks": [
            [degree, map_.rank()] for degree, map_ in result.differentials
        ],
        "cohomology_dimensions": [
            [degree, result.cohomology_dimension(degree)]
            for degree, _ in result.reduced.total_spaces
        ],
        "transfer_depths": [list(item) for item in result.path_depths],
        "differential_digests": [
            [degree, _map_digest(map_)] for degree, map_ in result.differentials
        ],
        "squared_zero": result.squared_zero,
    }


@dataclass(frozen=True, slots=True)
class PublishedOuterCechTransfer:
    """Both exact transferred cover outer-Hom complexes."""

    forward: TransferredOuterHom
    reverse: TransferredOuterHom

    @property
    def forward_h1_h2(self) -> tuple[int, int]:
        """Return independently reconstructed forward cover dimensions."""

        return self.forward.cohomology_dimension(1), self.forward.cohomology_dimension(2)

    @property
    def reverse_h1_h2(self) -> tuple[int, int]:
        """Return independently reconstructed reverse cover dimensions."""

        return self.reverse.cohomology_dimension(1), self.reverse.cohomology_dimension(2)

    def __post_init__(self) -> None:
        if not self.forward.squared_zero or not self.reverse.squared_zero:
            raise ValueError("a transferred outer-Hom differential is not square zero")
        if self.forward_h1_h2 != (36, 72):
            raise ValueError("forward full-Čech reconstruction changed")
        if self.reverse_h1_h2 != (72, 36):
            raise ValueError("reverse full-Čech reconstruction changed")

    def as_record(self) -> dict[str, object]:
        """Serialize the exact reconstruction and its remaining epistemic gate."""

        return {
            "schema": "published-outer-cech-transfer-v1",
            "coefficient_field": "Q(omega)",
            "cover": "standard affine cover of P2_x x P2_u x P1",
            "transfer_formula": "p Delta (1 + h Delta)^(-1) i",
            "forward": _direction_record(self.forward),
            "reverse": _direction_record(self.reverse),
            "published_dimensions_used_as_rank_inputs": False,
            "rank_90_map_inserted": False,
            "all_full_cech_complexes_squared_zero": True,
            "published_cover_dimensions_reconstructed": True,
            "outer_deck_action_computed": False,
            "invariant_outer_cocycles_computed": False,
            "next_required_object": (
                "deck action on the transferred outer cohomology and explicit "
                "invariant representatives in the common Cech-Koszul complex"
            ),
            "status": (
                "exact independent full-Cech reconstruction of both published "
                "cover outer-Ext dimensions"
            ),
        }


@cache
def published_outer_cech_transfer() -> PublishedOuterCechTransfer:
    """Build both full-Čech transfers without source dimensions as inputs."""

    reduced = published_outer_reduced_mismatch()
    return PublishedOuterCechTransfer(
        transferred_schoen_serre_outer_hom(reduced.forward.left, reduced.forward.right),
        transferred_schoen_serre_outer_hom(reduced.reverse.left, reduced.reverse.right),
    )


def write_published_outer_cech_transfer(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed exact outer-transfer certificate."""

    payload = published_outer_cech_transfer().as_record()
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
    """Regenerate the exact full-Čech transfer artifact."""

    payload = write_published_outer_cech_transfer()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"forward_h1_h2: {payload['forward']['cohomology_dimensions']}")
    print(f"reverse_h1_h2: {payload['reverse']['cohomology_dimensions']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["PublishedOuterCechTransfer", "published_outer_cech_transfer"]
