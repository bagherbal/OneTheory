"""Screen determinant-repaired alternate rays by exact Higgs characters.

Owns:
    Rank-two equivariant Hom-to-tensor character conversion, the unique
    common determinant-cancelling twist, and conditional Wilson multiplicities.

Depends on:
    Certified alternate Hom actions and determinant characters, exact acyclic
    line transfers, the source-action convention, and published Wilson weights.

Must not:
    Claim an outer extension, stability, Higgs cocycles, or a physical carrier.

Phase 0:
    Research-only necessary character screen for a future equivariant cone.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer import (
    schoen_unit_constituent,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    transferred_schoen_serre_outer_hom,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)

from .alternate_constituent_determinant_descent import OUTPUT as DETERMINANT
from .alternate_constituent_hom_actions import OUTPUT as HOM_ACTIONS
from .alternate_constituent_hom_actions import _common_frame
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import _constituent
from .mixed_schoen_observable_spectrum import (
    SPECTRUM_ARXIV_ID,
    SPECTRUM_SOURCE_SHA256,
    WILSON_HIGGS_CHARACTERS,
    _line_constituent,
    _line_profile,
    _source_digest,
)
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
CONVENTION = ROOT / "data/generated/scientific_genesis/mixed_schoen_character_convention.json"
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_constituent_character_screen.json"
Character = tuple[int, int]


def _verified(path: Path, schema: str) -> tuple[dict[str, object], str]:
    """Load one content-addressed prerequisite with its exact schema."""

    record = cast(dict[str, object], json.loads(path.read_text(encoding="utf-8")))
    digest = record.pop("artifact_digest", None)
    if record.get("schema") != schema or digest != _canonical_digest(record):
        raise ValueError(f"the prerequisite changed: {path.name}")
    return record, cast(str, digest)


def _add(left: Character, right: Character) -> Character:
    """Add exact Z3 x Z3 characters."""

    return (left[0] + right[0]) % 3, (left[1] + right[1]) % 3


def _negative(character: Character) -> Character:
    """Invert one exact deck character."""

    return (-character[0]) % 3, (-character[1]) % 3


def _twice(character: Character) -> Character:
    """Return the character shift on an exterior square."""

    return _add(character, character)


def _line_profiles() -> dict[str, list[int]]:
    """Recompute both determinant-line cohomologies from exact line transfer."""

    unit = schoen_unit_constituent()
    return {
        name: list(_line_profile(transferred_schoen_serre_outer_hom(
            _line_constituent(name, degree), unit
        )))
        for name, degree in (
            ("det_v1", (-2, 2, 0)),
            ("det_v2", (2, -2, 0)),
        )
    }


def _wilson_projection(characters: tuple[Character, ...]) -> dict[str, int]:
    """Count only selected source-character weights under the fixed Wilson line."""

    return {
        label: characters.count(_negative(weight))
        for label, weight in WILSON_HIGGS_CHARACTERS.items()
    }


def _hom_twist_uses_canonical_frame(ray: Character) -> bool:
    """Compare the untwisted and determinant-shifted second atlas frames."""

    action = published_constituent_deck_actions()[1]
    full = lift_joint_character_ray(
        action, OMEGA**ray[0], OMEGA**ray[1]
    )
    physical = _constituent(full, "physical-second", 2, (1, -1, 0))
    hom_source = _constituent(full, "hom-source", 2, (-1, 1, 0))
    if any(
        tuple(shifted - original for shifted, original in zip(
            source.line_degree, target.line_degree, strict=True
        )) != (-2, 2, 0)
        for target, source in zip(
            physical.objects, hom_source.objects, strict=True
        )
    ):
        return False
    return all(
        _common_frame(physical, generator) == _common_frame(hom_source, generator)
        for generator in schoen_sparse_deck_actions()
    )


def alternate_constituent_character_screen() -> dict[str, object]:
    """Derive conditional tensor characters without constructing a cone."""

    hom, hom_digest = _verified(HOM_ACTIONS, "alternate-constituent-hom-actions-v2")
    determinant, determinant_digest = _verified(
        DETERMINANT, "alternate-constituent-determinant-descent-v1"
    )
    convention, convention_digest = _verified(
        CONVENTION, "mixed-schoen-character-convention-v1"
    )
    if (
        hom.get("cohomology_action_certified") is not True
        or hom.get("equivariant_tensor_identification_available") is not False
        or determinant.get("fixed_linearization_su4_excluded_for_both_rays")
        is not True
        or convention.get("character_conversion")
        != "source=(-forward) mod 3 factorwise"
        or WILSON_HIGGS_CHARACTERS != {
            "up_higgs_doublet": (0, 2),
            "color_triplet": (2, 2),
            "down_higgs_doublet": (0, 1),
            "color_antitriplet": (1, 1),
        }
    ):
        raise ValueError("the character-screen premises changed")
    profiles = _line_profiles()
    if any(profile != [0, 0, 0, 0] for profile in profiles.values()):
        raise ValueError("a determinant endpoint is no longer acyclic")
    source_digest = _source_digest(SPECTRUM_ARXIV_ID, SPECTRUM_SOURCE_SHA256)
    hom_cases = cast(list[dict[str, object]], hom["cases"])
    determinant_cases = cast(list[dict[str, object]], determinant["cases"])
    if [item["ray_character_exponents"] for item in hom_cases] != [
        item["ray_character_exponents"] for item in determinant_cases
    ]:
        raise ValueError("the alternate ray ordering changed")

    records = []
    for hom_case, determinant_case in zip(
        hom_cases, determinant_cases, strict=True
    ):
        total = cast(
            Character, tuple(determinant_case["total_determinant_character"])
        )
        first = determinant_case["constituent_determinant_characters"][0]
        if (
            first != [0, 0]
            or hom_case["boundary_preservation_certified"] is not True
            or determinant_case["total_cover_line_degree"] != [0, 0, 0]
            or not _hom_twist_uses_canonical_frame(cast(Character, tuple(
                hom_case["ray_character_exponents"]
            )))
        ):
            raise ValueError("the declared determinant-twisted Hom is unavailable")
        # For rank-two F, F* = F tensor det(F)^-1 naturally and equivariantly.
        # Hence Hom(F tensor det(E), E) is E tensor F tensor
        # (det(E) tensor det(F))^-1, naturally for equivariant bundles.
        hom_characters = tuple(
            tuple(character) for character in hom_case["cover_hom_characters"]
        )
        original_tensor = tuple(sorted(
            _add(cast(Character, character), total)
            for character in hom_characters
        ))
        # Rank four makes theta = -det(E+F) the unique common character twist.
        common_twist = _negative(total)
        if _add(total, _add(_twice(common_twist), _twice(common_twist))) != (0, 0):
            raise ValueError("the common twist did not cancel the determinant")
        repaired_tensor = tuple(sorted(
            _add(character, _twice(common_twist))
            for character in original_tensor
        ))
        repaired_source = tuple(sorted(_negative(character) for character in repaired_tensor))
        projection = _wilson_projection(repaired_source)
        selected = (
            projection["up_higgs_doublet"] == 1
            and projection["down_higgs_doublet"] == 1
            and projection["color_triplet"] == 0
            and projection["color_antitriplet"] == 0
        )
        records.append({
            "ray_character_exponents": hom_case["ray_character_exponents"],
            "original_total_determinant_character": list(total),
            "unique_common_determinant_cancelling_twist": list(common_twist),
            "repaired_total_determinant_character": [0, 0],
            "hom_twist_uses_canonical_frame": True,
            "original_tensor_forward_characters": [list(c) for c in original_tensor],
            "repaired_tensor_forward_characters": [list(c) for c in repaired_tensor],
            "repaired_source_characters": [list(c) for c in repaired_source],
            "conditional_fixed_wilson_multiplicities": projection,
            "passes_conditional_one_higgs_zero_triplet_screen": selected,
        })
    if [item["passes_conditional_one_higgs_zero_triplet_screen"] for item in records] != [
        True, False
    ]:
        raise ValueError("the conditional alternate Higgs screen changed")
    return {
        "schema": "alternate-constituent-character-screen-v1",
        "scope": "two alternate atlas rays with a common determinant-cancelling character twist",
        "prerequisite_artifact_digests": {
            "hom_actions": hom_digest,
            "determinant": determinant_digest,
            "source_convention": convention_digest,
        },
        "published_spectrum_source_sha256": source_digest,
        "determinant_line_cohomology_h0_to_h3": profiles,
        "rank_two_character_identity": (
            "Hom(F tensor det(E), E) is equivariantly "
            "E tensor F tensor (det(E) tensor det(F))^-1"
        ),
        "proof_steps": [
            "For rank-two F, exterior contraction gives F* tensor det(F) = F naturally",
            "The fixed first atlas has determinant character zero, so its "
            "declared Hom twist uses the canonical determinant line action",
            "The product determinant character converts cover Hom to tensor characters",
            "A common rank-four character twist cancels the determinant uniquely",
            "Acyclic determinant endpoints identify H1 of any equivariant "
            "outer extension exterior square with H1 of the constituent tensor",
            "The source section convention inverts forward characters before "
            "the fixed Wilson projection",
        ],
        "determinant_filtration_identifies_h1_if_extension_exists": True,
        "cases": records,
        "ray_0_1_passes_conditional_higgs_screen": True,
        "ray_1_1_fails_conditional_triplet_screen": True,
        "outer_extension_constructed": False,
        "equivariant_chain_map_to_tensor_constructed": False,
        "outer_extension_equivariance_certified": False,
        "stability_chamber_certified": False,
        "physical_higgs_cocycles_available": False,
        "physical_carrier_frozen": False,
        "next_required_object": (
            "construct invariant outer Ext and a determinant-repaired universal "
            "extension for ray (0,1), then certify stability and full spectrum"
        ),
    }


def write_alternate_constituent_character_screen(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed conditional character screen."""

    payload = alternate_constituent_character_screen()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_constituent_character_screen()
    print(f"artifact_digest: {report['artifact_digest']}")
