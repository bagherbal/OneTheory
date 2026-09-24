"""Test all factorwise relinearizations against fixed Wilson selection.

Owns:
    A character-support proof that this simple constituent pair cannot keep
    one Higgs pair without color triplets under any factorwise character shift.

Depends on:
    Certified full-chain tensor Higgs characters, constituent simplicity,
    acyclic determinant endpoints, inverse-pullback section conventions, and
    published Wilson characters.

Must not:
    Exclude distinct underlying bundles, use observations as selectors, or
    treat the older derived-pushdown Higgs characters as full-chain results.

Phase 0:
    Research-only scoped Wilson-spectrum obstruction.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import cast

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .mixed_schoen_observable_spectrum import WILSON_HIGGS_CHARACTERS

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_wilson_shift_no_go.json"
PREREQUISITES = (
    (
        "full_chain_higgs_characters",
        "mixed_schoen_higgs_character_audit.json",
        "mixed-schoen-higgs-character-audit-v1",
    ),
    (
        "constituent_simplicity",
        "mixed_schoen_higgs_linearization_no_go.json",
        "mixed-schoen-higgs-linearization-no-go-v1",
    ),
    (
        "acyclic_determinants",
        "mixed_schoen_observable_spectrum.json",
        "mixed-schoen-observable-spectrum-v1",
    ),
    (
        "atlas_frame_comparison",
        "mixed_schoen_atlas_frame_comparison.json",
        "mixed-schoen-atlas-frame-comparison-v1",
    ),
    (
        "atlas_higgs_characters",
        "mixed_schoen_atlas_higgs_characters.json",
        "mixed-schoen-atlas-higgs-characters-v2",
    ),
    (
        "source_action_convention",
        "mixed_schoen_character_convention.json",
        "mixed-schoen-character-convention-v1",
    ),
)
Character = tuple[int, int]


def _verified_inputs() -> tuple[dict[str, dict[str, object]], dict[str, str]]:
    """Read only the named exact prerequisites and their source digests."""

    records: dict[str, dict[str, object]] = {}
    digests: dict[str, str] = {}
    for name, filename, schema in PREREQUISITES:
        path = ROOT / "data/generated/scientific_genesis" / filename
        record = cast(dict[str, object], json.loads(path.read_text(encoding="utf-8")))
        digest = record.pop("artifact_digest", None)
        if record.get("schema") != schema or digest != _canonical_digest(record):
            raise ValueError(f"the {name} prerequisite certificate is invalid")
        records[name] = record
        digests[name] = cast(str, digest)
    return records, digests


def _add(left: Character, right: Character) -> Character:
    """Add two exact deck characters modulo three."""

    return (left[0] + right[0]) % 3, (left[1] + right[1]) % 3


def _projection(characters: tuple[Character, ...]) -> dict[str, int]:
    """Apply only the fixed published Wilson characters to a multiset."""

    return {
        label: characters.count(tuple((-value) % 3 for value in wilson))
        for label, wilson in WILSON_HIGGS_CHARACTERS.items()
    }


@cache
def wilson_shift_no_go_audit() -> dict[str, object]:
    """Prove the two-doublet character shifts necessarily retain a triplet."""

    records, digests = _verified_inputs()
    higgs = records["full_chain_higgs_characters"]
    simplicity = records["constituent_simplicity"]
    spectrum = records["acyclic_determinants"]
    frame = records["atlas_frame_comparison"]
    atlas_higgs = records["atlas_higgs_characters"]
    convention = records["source_action_convention"]
    if (
        higgs.get("exact") is not True
        or higgs.get("current_h1_dimension") != 4
        or higgs.get("character_spaces_exhaust_ambient") is not True
        or higgs.get("all_character_restrictions_exact") is not True
        or simplicity.get("all_selected_constituents_simple") is not True
        or simplicity.get("same_constituent_factorwise_linearization_repair_available")
        is not False
    ):
        raise ValueError("the full-chain character or simplicity premise failed")
    filtration = cast(dict[str, object], cast(dict[str, object], spectrum["higgs"])[
        "determinant_filtration"
    ])
    if (
        filtration.get("acyclic") is not True
        or filtration.get("all_extension_parameters") is not True
        or filtration.get("det_v1_cohomology_h0_to_h3") != [0, 0, 0, 0]
        or filtration.get("det_v2_cohomology_h0_to_h3") != [0, 0, 0, 0]
    ):
        raise ValueError("the exterior-square filtration premise failed")
    if WILSON_HIGGS_CHARACTERS != {
        "up_higgs_doublet": (0, 2),
        "down_higgs_doublet": (0, 1),
        "color_triplet": (2, 2),
        "color_antitriplet": (1, 1),
    }:
        raise ValueError("the fixed Wilson characters changed")
    forward = tuple(
        tuple(character)
        for character in cast(list[list[int]], higgs["current_h1_characters"])
    )
    if forward != ((0, 0), (0, 1), (2, 0), (2, 1)):
        raise ValueError("the forward Higgs character support changed")
    if convention.get("character_conversion") != "source=(-forward) mod 3 factorwise":
        raise ValueError("the source section character convention changed")
    current = tuple(sorted(((-a) % 3, (-b) % 3) for a, b in forward))
    if (
        current != ((0, 0), (0, 2), (1, 0), (1, 2))
        or convention.get("source_action_h1_characters")
        != [list(character) for character in current]
    ):
        raise ValueError("the rectangular Higgs character support changed")
    current_projection = _projection(current)
    if current_projection != {
        "up_higgs_doublet": 0,
        "down_higgs_doublet": 1,
        "color_triplet": 0,
        "color_antitriplet": 0,
    }:
        raise ValueError("the synchronized Wilson projection changed")

    first_support = {character[0] for character in current}
    second_support = {character[1] for character in current}
    if set(current) != {
        (first, second)
        for first in first_support
        for second in second_support
    }:
        raise ValueError("the Higgs support is not a character rectangle")
    # Both inverse Wilson doublet weights have first coordinate zero and
    # second coordinates one and two. Factorization leaves only two shifts.
    first_shifts = tuple(
        shift for shift in range(3)
        if 0 in {(value + shift) % 3 for value in first_support}
    )
    second_shifts = tuple(
        shift for shift in range(3)
        if {1, 2} <= {(value + shift) % 3 for value in second_support}
    )
    both_doublet_shifts: tuple[Character, ...] = tuple(
        (first, second)
        for first in first_shifts
        for second in second_shifts
    )
    if both_doublet_shifts != ((0, 2), (2, 2)):
        raise ValueError("the rectangular doublet shifts changed")
    doublet_cases = []
    for shift in both_doublet_shifts:
        characters = tuple(sorted(_add(character, shift) for character in current))
        projection = _projection(characters)
        if (
            projection["up_higgs_doublet"] != 1
            or projection["down_higgs_doublet"] != 1
            or projection["color_triplet"] + projection["color_antitriplet"] != 1
        ):
            raise ValueError("the two-case Wilson obstruction failed")
        doublet_cases.append({
            "shift": list(shift),
            "characters": [list(character) for character in characters],
            "wilson_multiplicities": projection,
        })

    atlas_to_mixed = cast(list[int], frame["first_constituent_uniform_twist"])
    if atlas_to_mixed != [2, 0] or frame["second_constituent_uniform_twist"] != [0, 0]:
        raise ValueError("the atlas-bound constituent relation changed")
    atlas_forward_shift: Character = (
        -atlas_to_mixed[0] % 3,
        -atlas_to_mixed[1] % 3,
    )
    atlas_shift: Character = (
        -atlas_forward_shift[0] % 3,
        -atlas_forward_shift[1] % 3,
    )
    atlas_characters = tuple(sorted(_add(character, atlas_shift) for character in current))
    atlas_projection = _projection(atlas_characters)
    if (
        atlas_higgs.get("atlas_source_action_h1_characters")
        != [list(character) for character in atlas_characters]
        or atlas_higgs.get("tensor_atlas_over_synchronized_character")
        != list(atlas_forward_shift)
        or atlas_higgs.get("homogeneous_lift_normalization_included") is not True
        or atlas_higgs.get("source_action_convention_applied") is not True
    ):
        raise ValueError("the corrected atlas Higgs representation disagrees")
    if atlas_projection != {
        "up_higgs_doublet": 0,
        "down_higgs_doublet": 1,
        "color_triplet": 0,
        "color_antitriplet": 1,
    }:
        raise ValueError("the atlas-bound Wilson projection changed")
    return {
        "schema": "mixed-schoen-wilson-shift-no-go-v1",
        "scope": (
            "the same selected simple V1/V2 cover objects, all factorwise "
            "character relinearizations, both nonsplit extension orientations, "
            "and the fixed published Wilson embedding"
        ),
        "full_chain_forward_h1_characters": [list(character) for character in forward],
        "source_action_h1_characters": [list(character) for character in current],
        "source_action_convention_applied": True,
        "current_wilson_multiplicities": current_projection,
        "rectangular_support": {
            "first_coordinates": [0, 1],
            "second_coordinates": [0, 2],
        },
        "both_doublet_shift_cases": doublet_cases,
        "both_doublets_without_triplets_possible": False,
        "atlas_bound_source_action_shift_from_mixed": list(atlas_shift),
        "atlas_bound_source_action_higgs_characters": [
            list(character) for character in atlas_characters
        ],
        "atlas_bound_wilson_multiplicities": atlas_projection,
        "extension_parameters_can_change_h1_character_support": False,
        "distinct_underlying_constituents_excluded": False,
        "source_derived_pushdown_characters_used_as_rank_input": False,
        "prerequisite_artifact_digests": digests,
        "proof_steps": [
            "acyclic endpoint determinants identify exterior-square H1 with tensor H1",
            "simplicity restricts factorwise relinearizations to character shifts",
            "inverse pullback converts full-chain labels to source section characters",
            "both Wilson doublets force second-coordinate shift two",
            "the first-coordinate support leaves only shifts (0,2) and (2,2)",
            "those shifts respectively retain a triplet and an antitriplet",
        ],
        "next_required_object": (
            "a distinct constituent realization or an independent correction "
            "of the full-chain Higgs character premise"
        ),
    }


def write_wilson_shift_no_go(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed two-case Wilson obstruction."""

    payload = wilson_shift_no_go_audit()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    write_wilson_shift_no_go()
