"""Certify atlas-derived deck actions on alternate cover Hom cohomology.

Owns:
    Exact P/T matrices on four cover H1 classes of a determinant-twisted
    Hom realization for each unused I6 ray, including boundary descent.

Depends on:
    Exact alternate constituent atlases, synchronized mixed Čech transfer,
    sparse cohomology, and exact rank-two determinant degrees.

Must not:
    Treat raw Hom characters as physical tensor characters, infer a Wilson
    spectrum, or claim a descended rank-four carrier.

Phase 0:
    Research-only exact cohomology action; physical tensor comparison is open.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.dp9_actions import (
    published_coordinate_images,
)
from research.experiments.computable_carrier.dp9_serre_actions import (
    _fiber_coordinate_images,
)
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    _independent_columns,
    _matrix_from_columns,
    _SparseSpanSolver,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    SchoenSparseDeckAction,
    _inverse_images,
    schoen_sparse_deck_actions,
)
from research.experiments.computable_carrier.schoen_sparse_outer import SparseMap
from research.experiments.computable_carrier.schoen_sparse_outer_actions import (
    _cohomology_complement_columns,
    _columns,
    _select_columns,
)

from .alternate_constituent_deck_atlases import OUTPUT as ATLAS
from .alternate_constituent_deck_atlases import _atlas_line_character
from .alternate_constituent_higgs_dimensions import ALTERNATE_RAYS
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import (
    MixedSchoenConstituent,
    _constituent,
    mixed_schoen_constituents,
)
from .mixed_schoen_atlas_frame_comparison import (
    _atlas_frame,
    _uniform_coordinate_ratio,
)
from .mixed_schoen_outer_actions import _apply_transferred_action, _MixedContraction
from .mixed_schoen_outer_transfer import _transfer_map
from .published_constituent_deck_actions import (
    _simultaneous_eigenspace,
    published_constituent_deck_actions,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_constituent_hom_actions.json"


def _certified_atlas() -> dict[str, object]:
    """Read the exact alternate atlas prerequisite without trusting file presence."""

    record = json.loads(ATLAS.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest", None)
    if (
        digest != _canonical_digest(record)
        or record.get("schema") != "alternate-constituent-deck-atlases-v1"
        or record.get("alternate_constituent_atlases_exact") is not True
    ):
        raise ValueError("the alternate atlas certificate changed")
    return cast(dict[str, object], record)


def _common_frame(
    constituent: MixedSchoenConstituent,
    action: SchoenSparseDeckAction,
) -> Matrix:
    """Transport the native atlas frame to common Schoen coordinates."""

    generator = action.name
    index = 0 if generator == "P" else 1
    alignment = constituent.full.alignment
    line = _atlas_line_character(
        alignment.action, alignment.source_character[index], generator
    )
    atlas = _atlas_frame(constituent.factor, generator, line)
    if constituent.factor == 1:
        if action.x_images != published_coordinate_images(generator):
            raise ValueError("the first-factor common base lift changed")
        ratio = _uniform_coordinate_ratio(
            action.p_images, _fiber_coordinate_images(generator, 1)
        )
        return Matrix(
            tuple(
                tuple(value / ratio**item.line_degree[2] for value in row)
                for item, row in zip(constituent.objects, atlas.rows, strict=True)
            ),
            scalar_type=Eisenstein,
        )
    if (
        action.u_images != _inverse_images(published_coordinate_images(generator))
        or action.p_images != _inverse_images(_fiber_coordinate_images(generator, 2))
    ):
        raise ValueError("the second-factor common coordinate lift changed")
    return atlas


def _cycle(map_: SparseMap, vector: dict[int, Eisenstein]) -> bool:
    """Check one sparse reduced cycle without a dense matrix conversion."""

    return all(
        sum((value * vector.get(column, Eisenstein(0)) for column, value in row),
            Eisenstein(0)).is_zero()
        for row in map_.rows
    )


def _require_boundary_image(
    image: dict[int, Eisenstein],
    solver: _SparseSpanSolver,
    boundary_dimension: int,
) -> None:
    """Reject a transferred boundary with any cohomology component."""

    coordinates = solver.coordinates(image)
    if any(index >= boundary_dimension for index in coordinates):
        raise ValueError("an alternate Hom action does not preserve boundaries")


def _candidate_h1(
    first: MixedSchoenConstituent,
    second: MixedSchoenConstituent,
    incoming: SparseMap,
    outgoing: SparseMap,
) -> dict[str, object]:
    """Certify exact matrices after checking every independent boundary."""

    if not outgoing.compose(incoming).is_zero():
        raise ValueError("the alternate cover differential is not square zero")
    cycles = outgoing.kernel_inclusion()
    selected = _cohomology_complement_columns(incoming, cycles)
    representatives = _select_columns(cycles, selected, "alternate:H1")
    columns = tuple(_columns(representatives))
    if len(columns) != 4:
        raise ValueError("the alternate cover H1 dimension changed")
    boundaries = _independent_columns(incoming)
    if len(boundaries) != incoming.rank():
        raise ValueError("the alternate boundary basis is incomplete")
    solver = _SparseSpanSolver(boundaries + columns)
    contraction = _MixedContraction(first, second)
    induced: dict[str, Matrix] = {}
    depths = []
    boundary_counts: dict[str, int] = {}
    for action in schoen_sparse_deck_actions():
        frames = (_common_frame(first, action), _common_frame(second, action))
        for boundary in boundaries:
            image, depth = _apply_transferred_action(
                boundary, contraction, 1, action, frames
            )
            _require_boundary_image(image, solver, len(boundaries))
            depths.append((action.name, *depth))
        # Cycles split as these boundaries plus the selected H1 representatives.
        # Linearity therefore reduces cycle preservation to the next four tests.
        boundary_counts[action.name] = len(boundaries)
        images = []
        for column in columns:
            image, depth = _apply_transferred_action(
                column, contraction, 1, action, frames
            )
            if not _cycle(outgoing, image):
                raise ValueError("an atlas-derived deck image is not a cycle")
            coordinates = solver.coordinates(image)
            images.append({
                index - len(boundaries): value
                for index, value in coordinates.items()
                if index >= len(boundaries)
            })
            depths.append((action.name, *depth))
        induced[action.name] = _matrix_from_columns(tuple(images), len(columns))
    p, t = induced["P"], induced["T"]
    identity = Matrix.identity(4, scalar_type=Eisenstein)
    if not (p**3 == identity and t**3 == identity and p @ t == t @ p):
        raise ValueError("the atlas-derived H1 deck matrices violate group laws")
    characters = sorted(
        (p_exponent, t_exponent)
        for p_exponent in range(3)
        for t_exponent in range(3)
        for _vector in _simultaneous_eigenspace(
            p, t, OMEGA**p_exponent, OMEGA**t_exponent
        )
    )
    if len(characters) != 4:
        raise ValueError("joint characters do not exhaust alternate cover H1")
    return {
        "h1_dimension": len(columns),
        "cover_hom_characters": [list(item) for item in characters],
        "P": [[str(value) for value in row] for row in p.rows],
        "T": [[str(value) for value in row] for row in t.rows],
        "cohomology_group_relations": True,
        "representative_images_closed": True,
        "boundary_preservation_certified": True,
        "boundary_basis_checked": boundary_counts,
        "maximum_transfer_depth": max(max(left, right) for _g, left, right in depths),
    }


def alternate_constituent_hom_actions() -> dict[str, object]:
    """Transfer both alternate actions on chosen Hom cohomology cycles."""

    atlas = _certified_atlas()
    first = mixed_schoen_constituents()[0]
    action = published_constituent_deck_actions()[1]
    cases = {}
    for p_exponent, t_exponent in ALTERNATE_RAYS:
        full = lift_joint_character_ray(
            action, OMEGA**p_exponent, OMEGA**t_exponent
        )
        cases[p_exponent, t_exponent] = _constituent(
            full, f"I6-ray-{p_exponent}-{t_exponent}", 2, (-1, 1, 0)
        )
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures = {
            (label, degree): pool.submit(_transfer_map, first, second, degree)
            for label, second in cases.items()
            for degree in (0, 1)
        }
        records = []
        for atlas_case in cast(list[dict[str, object]], atlas["cases"]):
            label = tuple(cast(list[int], atlas_case["ray_character_exponents"]))
            if label not in cases:
                raise ValueError("the alternate atlas ray set changed")
            incoming, incoming_depth = futures[label, 0].result()
            outgoing, outgoing_depth = futures[label, 1].result()
            h1 = _candidate_h1(first, cases[label], incoming, outgoing)
            records.append({
                "ray_character_exponents": list(label),
                "incoming_rank": incoming.rank(),
                "outgoing_rank": outgoing.rank(),
                "transfer_path_depths": [[0, incoming_depth], [1, outgoing_depth]],
                **h1,
                "formal_pair_frame_character": atlas_case[
                    "formal_pair_frame_character"
                ],
            })
    return {
        "schema": "alternate-constituent-hom-actions-v2",
        "scope": "atlas-derived cover H1 of Hom(V2 tensor det(V1), V1)",
        "cases": records,
        "outer_rank_four_extension_constructed": False,
        "quotient_determinant_certified": False,
        "cohomology_action_certified": True,
        "equivariant_tensor_identification_available": False,
        "wilson_projection_performed": False,
        "next_required_object": (
            "compare the certified Hom action equivariantly with "
            "V1 tensor V2; separately certify quotient determinant"
        ),
    }


def write_alternate_constituent_hom_actions(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed exact alternate action result."""

    payload = alternate_constituent_hom_actions()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_constituent_hom_actions()
    print(f"artifact_digest: {report['artifact_digest']}")
    for item in cast(list[dict[str, object]], report["cases"]):
        print(item["ray_character_exponents"], item["cover_hom_characters"])
