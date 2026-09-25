"""Certify the determinant obstruction for the two unused constituent rays.

Owns:
    Exact cover degree, common-coordinate alternating deck characters, and
    scalar-cohomology checks for fixed atlas linearizations of both ray pairs.

Depends on:
    Certified alternate atlases, exact mixed constituents, Schoen deck actions,
    and the independent scalar Čech--Koszul residue calculation.

Must not:
    Exclude other linearizations or bundles, construct an outer extension,
    or infer a physical Higgs spectrum from a determinant character.

Phase 0:
    Research-only conditional no-go for fixed constituent linearizations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)

from .alternate_constituent_deck_atlases import OUTPUT as ATLAS
from .alternate_constituent_deck_atlases import (
    _alternating_frame_character,
    _exponent,
)
from .alternate_constituent_higgs_dimensions import ALTERNATE_RAYS
from .alternate_constituent_hom_actions import _common_frame
from .diagonal_schoen_line_actions import diagonal_line_full_action
from .diagonal_schoen_line_contraction import strict_line_inclusion
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import (
    MixedSchoenConstituent,
    _constituent,
    mixed_schoen_constituents,
)
from .mixed_schoen_yukawa_trace import scalar_full_differential, scalar_residue
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_constituent_determinant_descent.json"


def _certified_atlas() -> tuple[dict[str, object], str]:
    """Read the exact atlas evidence and reject a stale certificate."""

    record = json.loads(ATLAS.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest", None)
    if (
        digest != _canonical_digest(record)
        or record.get("schema") != "alternate-constituent-deck-atlases-v1"
        or record.get("alternate_constituent_atlases_exact") is not True
    ):
        raise ValueError("the alternate constituent atlas is not certified")
    return cast(dict[str, object], record), cast(str, digest)


def _alternating_degree(constituent: MixedSchoenConstituent) -> tuple[int, int, int]:
    """Return the determinant line degree of one resolution."""

    totals = [0, 0, 0]
    for item in constituent.objects:
        sign = 1 if item.position % 2 == 0 else -1
        for index, coordinate in enumerate(item.line_degree):
            totals[index] += sign * coordinate
    return totals[0], totals[1], totals[2]


def _common_character(constituent: MixedSchoenConstituent) -> tuple[int, int]:
    """Take exact graded determinants after common-coordinate transport."""

    return cast(
        tuple[int, int],
        tuple(
            _alternating_frame_character(
                constituent, _common_frame(constituent, action)
            )
            for action in schoen_sparse_deck_actions()
        ),
    )


def _scalar_top_character(character: tuple[int, int]) -> tuple[int, int]:
    """Independently read a declared determinant frame on scalar H3."""

    top, _depth = strict_line_inclusion(
        (0, 0, 0, 0), 3, ((0, Eisenstein(1)),)
    )
    if scalar_residue(top)[0] != Eisenstein(1):
        raise ValueError("the scalar top generator lost normalization")
    exponents = []
    for action in schoen_sparse_deck_actions():
        image = diagonal_line_full_action(top, action, character)
        if not scalar_full_differential(image).is_zero():
            raise ValueError("the determinant line action does not preserve H3")
        residue = scalar_residue(image)[0]
        exponents.append(_exponent(residue))
    return exponents[0], exponents[1]


def alternate_constituent_determinant_descent() -> dict[str, object]:
    """Certify a fixed-linearization SU(4) obstruction for both rays."""

    atlas, atlas_digest = _certified_atlas()
    first = mixed_schoen_constituents()[0]
    first_degree = _alternating_degree(first)
    first_character = _common_character(first)
    if first_character != tuple(
        atlas["first_constituent_atlas_alternating_frame_character"]
    ):
        raise ValueError("the first common frame disagrees with the atlas")

    action = published_constituent_deck_actions()[1]
    geometric_top = _scalar_top_character((0, 0))
    if geometric_top != (0, 0):
        raise ValueError("the geometric scalar top character changed")
    atlas_cases = {
        tuple(case["ray_character_exponents"]): case
        for case in cast(list[dict[str, object]], atlas["cases"])
    }
    records = []
    for p_exponent, t_exponent in ALTERNATE_RAYS:
        label = (p_exponent, t_exponent)
        atlas_case = atlas_cases[label]
        full = lift_joint_character_ray(
            action, OMEGA**p_exponent, OMEGA**t_exponent
        )
        second = _constituent(
            full, f"I6-ray-{p_exponent}-{t_exponent}", 2, (1, -1, 0)
        )
        second_degree = _alternating_degree(second)
        second_character = _common_character(second)
        total_degree = tuple(
            left + right for left, right in zip(
                first_degree, second_degree, strict=True
            )
        )
        total_character = tuple(
            (left + right) % 3 for left, right in zip(
                first_character, second_character, strict=True
            )
        )
        if (
            total_degree != (0, 0, 0)
            or list(second_character)
            != atlas_case["atlas_alternating_frame_character"]
            or list(total_character) != atlas_case["formal_pair_frame_character"]
            or _scalar_top_character(cast(tuple[int, int], total_character))
            != total_character
        ):
            raise ValueError("an alternate determinant comparison failed")
        records.append({
            "ray_character_exponents": list(label),
            "constituent_cover_line_degrees": [
                list(first_degree), list(second_degree)
            ],
            "total_cover_line_degree": list(total_degree),
            "constituent_determinant_characters": [
                list(first_character), list(second_character)
            ],
            "total_determinant_character": list(total_character),
            "geometric_scalar_h3_character": list(geometric_top),
            "scalar_h3_character": list(total_character),
            "equivariantly_trivial_determinant": total_character == (0, 0),
        })
    if {tuple(item["total_determinant_character"]) for item in records} != {
        (2, 1), (0, 1)
    }:
        raise ValueError("the alternate determinant character set changed")
    return {
        "schema": "alternate-constituent-determinant-descent-v1",
        "scope": "fixed I3 atlas plus the two unused I6 atlas linearizations",
        "atlas_artifact_digest": atlas_digest,
        "cases": records,
        "fixed_linearization_su4_excluded_for_both_rays": True,
        "conditional_on_equivariant_outer_extension": True,
        "outer_extension_constructed": False,
        "other_linearizations_or_bundles_excluded": False,
        "physical_higgs_spectrum_computed": False,
        "proof": (
            "determinant of any equivariant extension equals the tensor "
            "product of constituent determinants; both fixed products have "
            "a nontrivial T character on the cover-trivial determinant line"
        ),
        "next_required_object": (
            "find a determinant-trivial constituent linearization or distinct "
            "underlying bundle before an alternate physical spectrum"
        ),
    }


def write_alternate_constituent_determinant_descent(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed fixed-linearization obstruction."""

    payload = alternate_constituent_determinant_descent()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_constituent_determinant_descent()
    print(f"artifact_digest: {report['artifact_digest']}")
