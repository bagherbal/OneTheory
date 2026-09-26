"""Compute the alternate ray's exact constituent matter profile.

Owns:
    Full mixed-Schoen transfer ranks for the unused I6 ray, their exact
    square-zero check, and the all-parameter outer-extension consequence.

Depends on:
    The certified alternate cone, the unchanged first constituent's exact
    matter certificate, and the synchronized mixed Cech transfer.

Must not:
    Import a published matter dimension, select an extension point, infer
    Higgs cocycles, or claim a physical spectrum from cover ranks alone.

Phase 0:
    Research-only exact matter gate for the alternate stable family.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer import (
    schoen_serre_outer_hom,
)

from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import _constituent, mixed_schoen_constituents
from .mixed_schoen_higgs_character_audit import _map_digest
from .mixed_schoen_observable_spectrum import (
    GEOMETRY_ARXIV_ID,
    GEOMETRY_SOURCE_SHA256,
    _source_digest,
)
from .mixed_schoen_outer_transfer import _skeleton, _transfer_map, mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_constituent_matter_profile.json"
CONE = ROOT / "data/generated/scientific_genesis/alternate_constituent_outer_universal_cone.json"
STABILITY = (
    ROOT / "data/generated/scientific_genesis/alternate_constituent_outer_stability_locus.json"
)
SELECTED_SPECTRUM = ROOT / "data/generated/scientific_genesis/mixed_schoen_observable_spectrum.json"
SELECTED_ARROWS = ROOT / "data/generated/scientific_genesis/mixed_constituent_schoen_arrows.json"


def _certified_first_profile() -> tuple[str, str, tuple[int, int, int, int]]:
    """Reuse only the unchanged first constituent's exact derived ranks."""

    arrows_digest, arrows = _verified_payload(SELECTED_ARROWS)
    spectrum_digest, spectrum = _verified_payload(SELECTED_SPECTRUM)
    first = mixed_schoen_constituents()[0]
    arrow_records = cast(list[dict[str, object]], arrows["constituents"])
    matter_records = cast(
        list[dict[str, object]],
        cast(dict[str, object], spectrum["matter"])["constituent_complexes"],
    )
    if (
        arrows.get("schema") != "mixed-constituent-schoen-arrows-v1"
        or arrow_records[0] != first.as_record()
        or spectrum.get("schema") != "mixed-schoen-observable-spectrum-v1"
        or matter_records[0].get("left") != first.name
        or matter_records[0].get("right") != "O_X"
        or matter_records[0].get("squared_zero") is not True
        or matter_records[0].get("space_dimensions")
        != [[-3, 0], [-2, 0], [-1, 0], [0, 90], [1, 126], [2, 27], [3, 0], [4, 0], [5, 0]]
        or matter_records[0].get("differential_ranks")
        != [[-3, 0], [-2, 0], [-1, 0], [0, 90], [1, 27], [2, 0], [3, 0], [4, 0], [5, 0]]
        or matter_records[0].get("geometric_h0_to_h3") != [0, 9, 0, 0]
    ):
        raise ValueError("the unchanged first constituent's exact profile changed")
    return arrows_digest, spectrum_digest, (0, 9, 0, 0)


def alternate_constituent_matter_profile() -> dict[str, object]:
    """Transfer the alternate I6 ray and test the all-parameter matter gate."""

    cone_digest, cone = _verified_payload(CONE)
    stability_digest, stability = _verified_payload(STABILITY)
    if (
        cone.get("schema") != "alternate-constituent-outer-universal-cone-v1"
        or cone.get("ray_character_exponents") != [0, 1]
        or cone.get("projective_non_split_space") != "P^1(Q(omega))"
        or cone.get("equivariant_descent_exact") is not True
        or stability.get("schema") != "alternate-constituent-outer-stability-locus-v1"
        or stability.get("universal_cone_digest") != cone_digest
        or stability.get("all_nonzero_parameters_stable_in_chamber") is not True
    ):
        raise ValueError("the alternate family prerequisites changed")
    arrows_digest, first_digest, first_profile = _certified_first_profile()
    ray = lift_joint_character_ray(published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1)
    second = _constituent(ray, "I6-ray-0-1", 2, (1, -1, 0))
    unit = mixed_schoen_unit()
    reduced = schoen_serre_outer_hom(_skeleton(second), _skeleton(unit))
    spaces = dict(reduced.total_spaces)
    if any(spaces[degree].dimension for degree in (-3, -2, -1, 3, 4, 5)):
        raise ValueError("the alternate reduced matter complex changed its range")
    with ProcessPoolExecutor(max_workers=2) as executor:
        map0_future = executor.submit(_transfer_map, second, unit, 0)
        map1_future = executor.submit(_transfer_map, second, unit, 1)
        map0, depth0 = map0_future.result()
        map1, depth1 = map1_future.result()
    if not map1.compose(map0).is_zero():
        raise ValueError("the alternate matter differential does not square to zero")
    rank0, rank1 = map0.rank(), map1.rank()
    second_profile = (
        spaces[0].dimension - rank0,
        spaces[1].dimension - rank0 - rank1,
        spaces[2].dimension - rank1,
        0,
    )
    pure_h1 = first_profile[0] == first_profile[2] == first_profile[3] == 0 and (
        second_profile[0] == second_profile[2] == second_profile[3] == 0
    )
    visible_profile = (
        [left + right for left, right in zip(first_profile, second_profile, strict=True)]
        if pure_h1
        else None
    )
    geometry_digest = _source_digest(GEOMETRY_ARXIV_ID, GEOMETRY_SOURCE_SHA256)
    regular_multiplicity = (
        visible_profile[1] // 9
        if visible_profile is not None and visible_profile[1] % 9 == 0
        else None
    )
    return {
        "schema": "alternate-constituent-matter-profile-v1",
        "ray_character_exponents": [0, 1],
        "coefficient_field": "Q(omega)",
        "prerequisite_artifact_digests": {
            "alternate_cone": cone_digest,
            "alternate_stability": stability_digest,
            "unchanged_first_arrows": arrows_digest,
            "unchanged_first_exact_spectrum": first_digest,
            "free_quotient_geometry_source": geometry_digest,
        },
        "first_constituent_cover_h0_to_h3": list(first_profile),
        "first_constituent_reused_only_because_identical_object": True,
        "second_constituent": {
            "name": second.name,
            "full_mixed_arrow_exact": second.exact,
            "space_dimensions": [[degree, spaces[degree].dimension] for degree in (0, 1, 2)],
            "differential_ranks": [[0, rank0], [1, rank1]],
            "map_digests": [[0, _map_digest(map0)], [1, _map_digest(map1)]],
            "path_depths": [[0, depth0], [1, depth1]],
            "squared_zero": True,
            "cover_h0_to_h3": list(second_profile),
        },
        "all_nonzero_outer_parameters": True,
        "long_exact_sequence_collapses_if_constituents_pure_h1": pure_h1,
        "visible_cover_h0_to_h3": visible_profile,
        "deck_representation": {
            "theorem": (
                "The free Z3 x Z3 action has zero holomorphic Lefschetz number "
                "for every nonidentity element. Pure H1 therefore has trace "
                "zero away from the identity and is a sum of regular modules."
            ),
            "free_action_selected_from_published_geometry": True,
            "equivariant_bundle_certified_by_alternate_cone": True,
            "common_flat_twist_preserves_regular_multiplicity": True,
            "regular_multiplicity": regular_multiplicity,
            "joint_character_multiplicities": (
                [
                    {"character_exponents": [p, t], "multiplicity": regular_multiplicity}
                    for p in range(3)
                    for t in range(3)
                ]
                if regular_multiplicity is not None
                else None
            ),
        },
        "published_matter_dimensions_used_as_rank_inputs": False,
        "physical_spectrum_established": False,
        "explicit_alternate_matter_cocycles_computed": False,
        "explicit_alternate_higgs_cocycles_computed": False,
        "next_required_object": (
            "derive strict alternate matter/Higgs representatives and their "
            "deck actions on the same determinant-repaired cone"
        ),
    }


def write_alternate_constituent_matter_profile(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed exact matter certificate."""

    payload = alternate_constituent_matter_profile()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_constituent_matter_profile()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"visible_cover_h0_to_h3: {report['visible_cover_h0_to_h3']}")
