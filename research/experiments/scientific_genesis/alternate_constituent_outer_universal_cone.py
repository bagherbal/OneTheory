"""Assemble the determinant-repaired alternate universal outer cone.

Owns:
    Exact parameter-linear assembly of both strict invariant ray (0,1)
    cocycles, split-locus and local-freeness deductions, and the common
    character repair of the descended determinant.

Depends on:
    The content-addressed invariant basis, certified alternate constituent
    atlases and local units, and the reusable parameterized outer cochain.

Must not:
    Select an extension point, import a published stability claim for a
    different ray, or infer genuine SU(4) or physical Higgs cocycles.

Phase 0:
    Research-only universal rank-four cone; stability remains unresolved.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from onetheory.models.heterotic_schoen.visible import visible_bundle
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.parameterized_outer import (
    ParameterizedOuterCechCochain,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)

from .alternate_constituent_character_screen import OUTPUT as CHARACTER_SCREEN
from .alternate_constituent_deck_atlases import OUTPUT as DECK_ATLASES
from .alternate_constituent_determinant_descent import OUTPUT as DETERMINANT
from .alternate_constituent_hom_actions import _common_frame
from .alternate_constituent_outer_invariants import OUTPUT as INVARIANTS
from .distinct_constituent_ray_screen import OUTPUT as RAY_SCREEN
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import (
    MixedSchoenConstituent,
    _constituent,
    mixed_schoen_constituents,
)
from .mixed_schoen_outer_actions import _full_action, _MixedContraction
from .mixed_schoen_outer_universal_cone import (
    MixedSchoenUniversalOuterCone,
    _parameter,
    _representative,
    _verified_payload,
)
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT / "data/generated/scientific_genesis/"
    "alternate_constituent_outer_universal_cone.json"
)
PARAMETERS = ("a0", "a1")


def _ray_case(payload: dict[str, object]) -> dict[str, object]:
    """Select only the certified unused I6 ray without a fallback."""

    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise ValueError("alternate ray cases are missing")
    matches = [
        case for case in cases
        if isinstance(case, dict)
        and case.get("ray_character_exponents") == [0, 1]
    ]
    if len(matches) != 1:
        raise ValueError("ray (0,1) must occur exactly once")
    return cast(dict[str, object], matches[0])


def _graded_line_objects(
    constituent: MixedSchoenConstituent,
) -> tuple[tuple[int, tuple[int, int, int]], ...]:
    """Read the exact perfect-complex K-class data of one constituent."""

    return tuple(
        (item.position, item.line_degree) for item in constituent.objects
    )


def alternate_constituent_outer_universal_cone() -> dict[str, object]:
    """Construct the full two-parameter cone without selecting a point."""

    invariant_digest, invariant = _verified_payload(INVARIANTS)
    atlas_digest, atlas = _verified_payload(DECK_ATLASES)
    determinant_digest, determinant = _verified_payload(DETERMINANT)
    screen_digest, screen = _verified_payload(CHARACTER_SCREEN)
    ray_digest, rays = _verified_payload(RAY_SCREEN)
    if (
        invariant.get("schema") != "alternate-constituent-outer-invariants-v1"
        or invariant.get("ray_character_exponents") != [0, 1]
        or invariant.get("invariant_ext1_dimension") != 2
        or invariant.get("strict_full_cech_representative_count") != 2
        or invariant.get("all_representatives_closed") is not True
        or invariant.get("all_representatives_strictly_deck_fixed") is not True
        or invariant.get("all_representatives_nonboundary_and_independent")
        is not True
        or atlas.get("schema") != "alternate-constituent-deck-atlases-v1"
        or atlas.get("alternate_constituent_atlases_exact") is not True
        or determinant.get("schema")
        != "alternate-constituent-determinant-descent-v1"
        or determinant.get("atlas_artifact_digest") != atlas_digest
        or screen.get("schema") != "alternate-constituent-character-screen-v1"
        or cast(dict[str, object], screen.get("prerequisite_artifact_digests", {})).get(
            "determinant"
        ) != determinant_digest
        or rays.get("schema") != "distinct-constituent-ray-screen-v1"
    ):
        raise ValueError("the alternate universal-cone premises changed")
    atlas_case = _ray_case(atlas)
    determinant_case = _ray_case(determinant)
    screen_case = _ray_case(screen)
    survivors = rays.get("local_unit_survivors")
    if (
        atlas_case.get("overlap_exact") is not True
        or atlas_case.get("deck_exact") is not True
        or determinant_case.get("total_cover_line_degree") != [0, 0, 0]
        or determinant_case.get("total_determinant_character") != [2, 1]
        or screen_case.get("unique_common_determinant_cancelling_twist") != [1, 2]
        or screen_case.get("repaired_total_determinant_character") != [0, 0]
        or screen_case.get("passes_conditional_one_higgs_zero_triplet_screen")
        is not True
        or not isinstance(survivors, list)
        or not all(
            any(
                isinstance(item, dict)
                and item.get("scheme") == scheme
                and item.get("character_exponents") == character
                for item in survivors
            )
            for scheme, character in (("I3", [1, 0]), ("I6", [0, 1]))
        )
    ):
        raise ValueError("the alternate local or determinant gates failed")

    first = mixed_schoen_constituents()[0]
    selected_second = mixed_schoen_constituents()[1]
    action = published_constituent_deck_actions()[1]
    full = lift_joint_character_ray(action, OMEGA**0, OMEGA**1)
    second = _constituent(full, "I6-ray-0-1", 2, (1, -1, 0))
    if _graded_line_objects(second) != _graded_line_objects(selected_second):
        raise ValueError("the alternate ray changed the constituent K-class")

    raw = invariant.get("strict_full_cech_representatives")
    if not isinstance(raw, list) or len(raw) != 2:
        raise ValueError("the alternate invariant basis is incomplete")
    representatives = tuple(_representative(item) for item in raw)
    contraction = _MixedContraction(first, second)
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    frames = {
        name: (_common_frame(first, deck), _common_frame(second, deck))
        for name, deck in actions.items()
    }
    determinant_before = cast(
        tuple[int, int], tuple(determinant_case["total_determinant_character"])
    )
    common_twist = cast(
        tuple[int, int],
        tuple(screen_case["unique_common_determinant_cancelling_twist"]),
    )
    determinant_after = tuple(
        (original + 4 * twist) % 3
        for original, twist in zip(determinant_before, common_twist, strict=True)
    )
    if determinant_after != (0, 0):
        raise ValueError("the common character does not repair the determinant")
    probe = SparseOuterCechCochain((representatives[0].terms[0],))
    for index, name in enumerate(("P", "T")):
        character = OMEGA ** common_twist[index]
        left_frame, right_frame = frames[name]
        twisted_frames = (
            left_frame.scale(character), right_frame.scale(character)
        )
        if _full_action(probe, first, second, actions[name], frames[name]) != (
            _full_action(probe, first, second, actions[name], twisted_frames)
        ):
            raise ValueError("the common twist changed the outer-Hom action")
    for representative in representatives:
        if not contraction.differential(representative).is_zero():
            raise ValueError("an alternate universal basis cocycle is not closed")
        if any(
            _full_action(representative, first, second, actions[name], frames[name])
            != representative
            for name in ("P", "T")
        ):
            raise ValueError("an alternate universal basis cocycle is not deck fixed")

    extension = ParameterizedOuterCechCochain(
        PARAMETERS,
        tuple(
            (basis, _parameter(index, 2).scale(coefficient))
            for index, representative in enumerate(representatives)
            for basis, coefficient in representative.terms
        ),
    )
    published = visible_bundle(schoen_geometry()).bundle
    cone = MixedSchoenUniversalOuterCone(
        invariant_digest,
        (
            ("alternate_constituent_deck_atlases", atlas_digest),
            ("alternate_constituent_determinant_descent", determinant_digest),
            ("alternate_constituent_character_screen", screen_digest),
            ("distinct_constituent_ray_screen", ray_digest),
        ),
        "V1",
        "V2",
        "alternate-constituent-outer-universal-cone-v1",
        PARAMETERS,
        representatives,
        extension,
        True,
        True,
        True,
        published.rank,
        cast(tuple[str, str, str], tuple(str(value) for value in published.c1)),
        cast(tuple[str, str, str], tuple(str(value) for value in published.c2)),
        str(published.c3),
    )
    record = cone.as_record()
    record["invariant_artifact_digest"] = invariant_digest
    record["ray_character_exponents"] = [0, 1]
    record["cover_ext1_dimension"] = 18
    record["invariant_ext1_dimension"] = 2
    record["strict_basis_rechecked_from_saved_terms"] = True
    record["constituent_graded_line_objects_match_published_selected_ray"] = True
    record["determinant_character_before_common_twist"] = list(determinant_before)
    record["common_flat_character_twist"] = list(common_twist)
    record["determinant_character_after_common_twist"] = list(determinant_after)
    record["common_twist_cancels_in_outer_hom"] = True
    record["quotient_determinant_trivial_exact"] = True
    record["chern_classes"]["provenance"] = (
        "alternate and selected perfect complexes have identical graded "
        "line objects; a flat character twist preserves rational Chern data"
    )
    record["rational_chern_data_only"] = True
    record["conditional_one_higgs_character_screen"] = True
    record["physical_higgs_cocycles_available"] = False
    record["stability_chamber_certified"] = False
    record["genuine_su4_locus_computed"] = False
    record["first_missing_input"] = (
        "certify the parameterwise stable locus and exclude accidental "
        "proper structure-group reductions on P^1(Q(omega))"
    )
    record["status"] = (
        "exact determinant-repaired non-split locally free descended "
        "rank-four universal cone; stability and genuine SU(4) unresolved"
    )
    return record


def write_alternate_constituent_outer_universal_cone(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the exact content-addressed alternate cone certificate."""

    payload = alternate_constituent_outer_universal_cone()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_constituent_outer_universal_cone()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"projective_non_split_space: {report['projective_non_split_space']}")
