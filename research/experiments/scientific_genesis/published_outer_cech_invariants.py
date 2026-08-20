"""Certify invariant outer classes in the common Schoen Čech–Koszul complex.

Owns:
    Exact transferred deck representations, strict Reynolds-averaged cocycle
    representatives, and content-addressed certificates in both outer directions.

Depends on:
    The published constituent cones, full standard-cover transfer, source-bound
    constituent linearizations, and synchronized Schoen coordinate actions.

Must not:
    Select an outer extension coordinate, use expected dimensions as rank
    inputs, identify a cover cocycle with a locally free bundle, or fit a character.

Phase 0:
    Exact invariant outer bases are reconstructed; extension selection remains open.
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
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    TransferredCohomologyDeckAction,
    _constituent_frame,
    transferred_outer_cohomology_deck_action,
)
from research.experiments.computable_carrier.schoen_sparse_outer import SparseMap

from .published_outer_reduced_mismatch import published_outer_reduced_mismatch

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/published_outer_cech_invariants.json"


def _matrix_digest(matrix) -> str:
    """Hash one exact small matrix in deterministic row-major order."""

    digest = hashlib.sha256()
    for row in matrix.rows:
        for value in row:
            digest.update(
                repr(
                    (
                        value.a.numerator,
                        value.a.denominator,
                        value.b.numerator,
                        value.b.denominator,
                    )
                ).encode("ascii")
            )
            digest.update(b"\0")
    return digest.hexdigest()


def _basis_record(basis: OuterCechBasis) -> dict[str, object]:
    """Serialize one full Čech–Koszul basis label without interpretation."""

    component = basis.component
    return {
        "left_object": component.left_index,
        "right_object": component.right_index,
        "object_degree": component.object_degree,
        "line_degree": list(component.line_degree),
        "koszul_summand": component.koszul_summand,
        "x_monomial": list(basis.x_monomial),
        "u_monomial": list(basis.u_monomial),
        "p_monomial": list(basis.p_monomial),
        "cell": [[*simplex] for simplex in basis.cell],
    }


def _cech_record(cochain: SparseOuterCechCochain, name: str) -> dict[str, object]:
    """Serialize one strict invariant full-complex representative."""

    return {
        "name": name,
        "term_count": len(cochain.terms),
        "terms": [
            {
                "basis": _basis_record(basis),
                "coefficient": str(coefficient),
            }
            for basis, coefficient in cochain.terms
        ],
    }


def _sparse_representatives(map_: SparseMap) -> list[dict[str, object]]:
    """Serialize sparse reduced representatives in indexed coordinates."""

    columns: list[list[dict[str, object]]] = [
        [] for _ in range(map_.domain.dimension)
    ]
    for row, entries in enumerate(map_.rows):
        for column, coefficient in entries:
            columns[column].append({"index": row, "coefficient": str(coefficient)})
    return [
        {"name": map_.domain.basis[index], "terms": terms}
        for index, terms in enumerate(columns)
    ]


def _direction_record(
    result: TransferredCohomologyDeckAction,
) -> dict[str, object]:
    """Serialize one exact quotient-action and representative certificate."""

    return {
        "orientation": (
            f"RHom({result.transferred.reduced.right.name},"
            f"{result.transferred.reduced.left.name})"
        ),
        "cover_h1_dimension": result.transferred.cohomology_dimension(1),
        "invariant_h1_dimension": result.invariant_dimension,
        "cohomology_action": {
            "dimension": result.p_induced.row_count,
            "p_digest": _matrix_digest(result.p_induced),
            "t_digest": _matrix_digest(result.t_induced),
            "order_three_and_commuting": result.group_relations,
        },
        "action_depth_maxima": {
            "perturbed_inclusion": max(item[1] for item in result.action_depths),
            "perturbed_projection": max(item[2] for item in result.action_depths),
        },
        "reduced_representatives": _sparse_representatives(
            result.invariant_representatives
        ),
        "full_cech_koszul_representatives": [
            _cech_record(cochain, f"invariant:{index}")
            for index, cochain in enumerate(result.invariant_full_cech)
        ],
        "images_are_cycles": result.images_are_cycles,
        "full_representatives_are_cycles": result.full_representatives_are_cycles,
        "full_representatives_are_strictly_invariant": (
            result.full_representatives_are_invariant
        ),
        "exact": result.exact,
    }


@dataclass(frozen=True, slots=True)
class PublishedOuterCechInvariants:
    """Both exact invariant outer cohomology bases on the Schoen cover."""

    forward: TransferredCohomologyDeckAction
    reverse: TransferredCohomologyDeckAction

    def __post_init__(self) -> None:
        if not self.forward.exact or not self.reverse.exact:
            raise ValueError("an invariant outer Čech certificate is not exact")
        if (self.forward.invariant_dimension, self.reverse.invariant_dimension) != (
            4,
            8,
        ):
            raise ValueError("derived invariant dimensions disagree with the source ledger")

    def as_record(self) -> dict[str, object]:
        """Serialize exact representatives while preserving the selection gate."""

        mismatch = published_outer_reduced_mismatch()
        frame_characters = {
            constituent.name: {
                generator: str(_constituent_frame(constituent, generator)[0][0])
                for generator in ("P", "T")
            }
            for constituent in (mismatch.forward.left, mismatch.forward.right)
        }
        return {
            "schema": "published-outer-cech-invariants-v1",
            "coefficient_field": "Q(omega)",
            "cover": "standard affine cover of P2_x x P2_u x P1",
            "action_transfer_formula": "p' g i'",
            "reynolds_projector": "(1/9) sum_{a,b=0}^2 P^a T^b",
            "synchronized_constituent_frame_characters": frame_characters,
            "frame_character_status": (
                "derived from source-bound dP9 linearizations and the exact "
                "change to the shared Schoen P1 overlap cocycle"
            ),
            "forward": _direction_record(self.forward),
            "reverse": _direction_record(self.reverse),
            "expected_invariant_dimensions_used_as_action_inputs": False,
            "relative_character_fitted": False,
            "all_representatives_explicit": True,
            "outer_extension_coordinate_selected": False,
            "rank_four_bundle_constructed": False,
            "next_required_object": (
                "a source-justified nonzero coordinate in the four-dimensional "
                "forward invariant outer space, followed by its derived cone"
            ),
            "status": (
                "exact invariant outer Ext bases in one common Cech-Koszul "
                "complex; no extension coordinate is selected"
            ),
        }


@cache
def published_outer_cech_invariants() -> PublishedOuterCechInvariants:
    """Build both invariant bases without target dimensions as action inputs."""

    mismatch = published_outer_reduced_mismatch()
    return PublishedOuterCechInvariants(
        transferred_outer_cohomology_deck_action(
            mismatch.forward.left,
            mismatch.forward.right,
        ),
        transferred_outer_cohomology_deck_action(
            mismatch.reverse.left,
            mismatch.reverse.right,
        ),
    )


def write_published_outer_cech_invariants(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed invariant outer-cocycle certificate."""

    payload = published_outer_cech_invariants().as_record()
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
    """Regenerate the exact invariant outer-cocycle artifact."""

    payload = write_published_outer_cech_invariants()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"forward_invariant_h1: {payload['forward']['invariant_h1_dimension']}")
    print(f"reverse_invariant_h1: {payload['reverse']['invariant_h1_dimension']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PublishedOuterCechInvariants",
    "published_outer_cech_invariants",
]
