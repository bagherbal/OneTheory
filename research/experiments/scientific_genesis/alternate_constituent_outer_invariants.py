"""Construct strict invariant outer-Ext cocycles for the surviving I6 ray.

Owns:
    Exact full Čech Reynolds projection of all cover Ext1 representatives,
    strict closure, deck-fixedness, non-boundary, and invariant-rank checks.

Depends on:
    The alternate cover Ext certificate, exact constituent deck atlases,
    synchronized mixed outer transfer, and reusable full-cochain actions.

Must not:
    Select an extension point, infer a stable bundle, or report a physical
    carrier from an invariant vector-space calculation alone.

Phase 0:
    Research-only invariant-Ext prerequisite for the universal outer cone.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    _reduced_basis,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    _independent_columns,
    _matrix_from_columns,
    _SparseSpanSolver,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.computable_carrier.schoen_sparse_outer_actions import (
    _cohomology_complement_columns,
    _columns,
    _select_columns,
)

from .alternate_constituent_hom_actions import _common_frame, _cycle
from .alternate_constituent_outer_ext import OUTPUT as OUTER_EXT
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import _constituent, mixed_schoen_constituents
from .mixed_schoen_outer_actions import (
    _average_full_invariant,
    _cech_record,
    _full_action,
    _MixedContraction,
    _perturbed_inclusion,
    _perturbed_projection,
    _reduced_cochain,
)
from .mixed_schoen_outer_transfer import _transfer_map
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_constituent_outer_invariants.json"


def _certified_cover_ext() -> tuple[dict[str, object], str]:
    """Read the exact cover prerequisite without granting equivariance."""

    record = cast(dict[str, object], json.loads(OUTER_EXT.read_text(encoding="utf-8")))
    digest = record.pop("artifact_digest", None)
    if (
        record.get("schema") != "alternate-constituent-outer-ext-v1"
        or digest != _canonical_digest(record)
        or record.get("cover_ext1_dimension") != 18
        or record.get("invariant_ext1_dimension_computed") is not False
    ):
        raise ValueError("the alternate cover Ext prerequisite changed")
    return record, cast(str, digest)


def alternate_constituent_outer_invariants() -> dict[str, object]:
    """Compute the full strict invariant subspace without selecting a point."""

    cover, cover_digest = _certified_cover_ext()
    first = mixed_schoen_constituents()[0]
    source = published_constituent_deck_actions()[1]
    full = lift_joint_character_ray(source, OMEGA**0, OMEGA**1)
    second = _constituent(full, "I6-ray-0-1", 2, (1, -1, 0))
    with ProcessPoolExecutor(max_workers=2) as pool:
        futures = {
            degree: pool.submit(_transfer_map, first, second, degree)
            for degree in (0, 1)
        }
        incoming, incoming_depth = futures[0].result()
        outgoing, outgoing_depth = futures[1].result()
    if (
        [incoming.domain.dimension, incoming.codomain.dimension,
         outgoing.codomain.dimension]
        != cover["reduced_dimensions_degree_0_to_2"]
        or [incoming.rank(), outgoing.rank()]
        != cover["differential_ranks_degree_0_to_1"]
        or not outgoing.compose(incoming).is_zero()
    ):
        raise ValueError("the alternate outer differential changed")

    cycles = outgoing.kernel_inclusion()
    selected = _cohomology_complement_columns(incoming, cycles)
    representatives = _select_columns(cycles, selected, "alternate:outer:H1")
    columns = tuple(_columns(representatives))
    if len(columns) != 18:
        raise ValueError("the alternate cover Ext1 basis dimension changed")
    boundaries = _independent_columns(incoming)
    if len(boundaries) != 1512:
        raise ValueError("the alternate outer boundary basis changed")
    solver = _SparseSpanSolver(boundaries + columns)
    contraction = _MixedContraction(first, second)
    entries = _reduced_basis(
        contraction.left_skeleton, contraction.right_skeleton, 1
    )
    actions = {action.name: action for action in schoen_sparse_deck_actions()}
    frames = {
        name: (_common_frame(first, action), _common_frame(second, action))
        for name, action in actions.items()
    }
    invariant_columns: list[dict[int, Eisenstein]] = []
    invariant_full = []
    maximum_inclusion_depth = 0
    maximum_projection_depth = 0
    for column in columns:
        included, inclusion_depth = _perturbed_inclusion(
            _reduced_cochain(entries, column), contraction
        )
        maximum_inclusion_depth = max(maximum_inclusion_depth, inclusion_depth)
        if not contraction.differential(included).is_zero():
            raise ValueError("a lifted alternate Ext representative is not closed")
        averaged = _average_full_invariant(
            included, contraction, actions["P"], actions["T"], frames
        )
        if not contraction.differential(averaged).is_zero():
            raise ValueError("an alternate Reynolds image is not closed")
        for generator in ("P", "T"):
            if _full_action(
                averaged, first, second, actions[generator], frames[generator]
            ) != averaged:
                raise ValueError("an alternate Reynolds image is not deck fixed")
        projected, projection_depth = _perturbed_projection(
            averaged, contraction, 1
        )
        maximum_projection_depth = max(maximum_projection_depth, projection_depth)
        if not _cycle(outgoing, projected):
            raise ValueError("an averaged full cocycle projected outside cycles")
        coordinates = solver.coordinates(projected)
        quotient = {
            index - len(boundaries): value
            for index, value in coordinates.items()
            if index >= len(boundaries)
        }
        candidate = invariant_columns + [quotient]
        if quotient and _matrix_from_columns(candidate, 18).rank() > len(
            invariant_columns
        ):
            invariant_columns.append(quotient)
            invariant_full.append(averaged)

    invariant_rank = len(invariant_columns)
    return {
        "schema": "alternate-constituent-outer-invariants-v1",
        "scope": "strict P/T-fixed cover Ext1(V2,V1) for ray (0,1)",
        "cover_artifact_digest": cover_digest,
        "ray_character_exponents": [0, 1],
        "cover_ext1_dimension": 18,
        "cover_basis_averaged": len(columns),
        "invariant_ext1_dimension": invariant_rank,
        "strict_full_cech_representative_count": len(invariant_full),
        "strict_full_cech_representatives": [
            _cech_record(cochain, f"alternate-invariant:{index}")
            for index, cochain in enumerate(invariant_full)
        ],
        "reduced_invariant_coordinates": [
            [[row, str(value)] for row, value in sorted(column.items())]
            for column in invariant_columns
        ],
        "all_representatives_closed": True,
        "all_representatives_strictly_deck_fixed": True,
        "all_representatives_nonboundary_and_independent": True,
        "transfer_depths_degree_0_to_1": [incoming_depth, outgoing_depth],
        "maximum_inclusion_depth": maximum_inclusion_depth,
        "maximum_projection_depth": maximum_projection_depth,
        "determinant_cancelling_common_twist": [1, 2],
        "common_character_twist_preserves_outer_hom_action": True,
        "extension_point_selected": False,
        "universal_rank_four_cone_constructed": False,
        "stability_chamber_certified": False,
        "next_required_object": (
            "construct the universal equivariant outer cone over the full "
            "invariant Ext space and certify its algebraic lawful locus"
        ),
    }


def write_alternate_constituent_outer_invariants(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write exact strict invariants and their full cocycle certificates."""

    payload = alternate_constituent_outer_invariants()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_constituent_outer_invariants()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"invariant_ext1_dimension: {report['invariant_ext1_dimension']}")
