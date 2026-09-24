"""Test global deck atlases for the two unused locally free I6 rays.

Owns:
    Exact overlap and deck consistency for alternate full Čech lifts, plus
    a frame-level comparison that prevents reuse of the selected P action.

Depends on:
    The screened Ext rays, selected Serre presentation, homogeneous chart
    atlases, exact deck actions, and synchronized constituent resolutions.

Must not:
    Identify an alternate outer extension, certify its quotient determinant,
    or infer Wilson-projected Higgs characters from atlas frame scalars.

Phase 0:
    Research-only necessary constituent-equivariance certificate.
"""

from __future__ import annotations

import json
from pathlib import Path

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .alternate_constituent_higgs_dimensions import ALTERNATE_RAYS
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import MixedSchoenConstituent, _constituent
from .mixed_schoen_atlas_frame_comparison import _atlas_frame
from .published_constituent_deck_actions import (
    PublishedConstituentDeckAction,
    published_constituent_deck_actions,
)
from .published_constituent_deck_atlases import _deck_atlas
from .published_constituent_full_cech import published_constituent_full_cech
from .published_constituent_overlap_transitions import _atlas

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_constituent_deck_atlases.json"


def _exponent(value: Eisenstein) -> int:
    """Return the exact exponent of a cubic-root scalar."""

    for exponent in range(3):
        if value == OMEGA**exponent:
            return exponent
    raise ValueError("the determinant action is not a cubic-root character")


def _alternating_frame_character(
    constituent: MixedSchoenConstituent,
    frame: Matrix,
) -> int:
    """Take the graded determinant of a homogeneous constituent frame."""

    scalar = Eisenstein(1)
    for position in sorted({item.position for item in constituent.objects}):
        indices = tuple(
            index for index, item in enumerate(constituent.objects)
            if item.position == position
        )
        if any(
            not frame[row][column].is_zero()
            for row in indices
            for column, item in enumerate(constituent.objects)
            if item.position != position
        ):
            raise ValueError("a deck frame mixes complex degrees")
        block = Matrix(
            tuple(tuple(frame[row][column] for column in indices) for row in indices),
            scalar_type=Eisenstein,
        )
        determinant = block.determinant()
        scalar *= determinant if position % 2 == 0 else 1 / determinant
    return _exponent(scalar)


def _atlas_line_character(
    action: PublishedConstituentDeckAction,
    source: Eisenstein,
    generator: str,
) -> Eisenstein:
    """Return the line comparison scalar forced by the Ext eigencharacter."""

    twist = action.p_twist if generator == "P" else action.t_twist
    return twist / source


def alternate_constituent_deck_atlases() -> dict[str, object]:
    """Certify both alternate atlases while exposing the P-frame mismatch."""

    first = published_constituent_full_cech()[0]
    first_constituent = _constituent(first, "V1", 1, (-1, 1, 0))
    first_characters = []
    for index, generator in enumerate(("P", "T")):
        line = _atlas_line_character(
            first.alignment.action,
            first.alignment.source_character[index],
            generator,
        )
        first_characters.append(
            _alternating_frame_character(
                first_constituent, _atlas_frame(1, generator, line)
            )
        )

    action = published_constituent_deck_actions()[1]
    records = []
    for p_exponent, t_exponent in ALTERNATE_RAYS:
        full = lift_joint_character_ray(
            action, OMEGA**p_exponent, OMEGA**t_exponent
        )
        if not (
            full.alignment.selected_chain_eigenvector
            and full.alignment.source_ray.p_fixed
            and full.alignment.source_ray.t_fixed
        ):
            raise ValueError("an alternate ray is not an exact joint deck eigenray")
        overlap = _atlas(full)
        deck = _deck_atlas(full, overlap, 1)
        constituent = _constituent(
            full, f"I6-ray-{p_exponent}-{t_exponent}", 2, (1, -1, 0)
        )
        frame_records = []
        determinant_character = []
        for index, generator in enumerate(("P", "T")):
            source = full.alignment.source_character[index]
            line = _atlas_line_character(action, source, generator)
            recorded = {
                item.extension_line_character
                for item in deck.comparisons if item.generator == generator
            }
            if recorded != {line}:
                raise ValueError("the atlas line comparison changed")
            atlas_frame = _atlas_frame(2, generator, line)
            # This is the selected mixed-frame formula applied to the new ray.
            # It is a diagnostic only: it is not the new ray's deck action.
            legacy_line = source if generator == "P" else 1 / source
            legacy_frame = _atlas_frame(2, generator, legacy_line)
            ratio = legacy_frame[0][0] / atlas_frame[0][0]
            frame_records.append({
                "generator": generator,
                "atlas_extension_line_character": _exponent(line),
                "legacy_first_block_ratio": _exponent(ratio),
                "legacy_frame_uniformly_related": (
                    legacy_frame == atlas_frame.scale(ratio)
                ),
            })
            determinant_character.append(
                _alternating_frame_character(constituent, atlas_frame)
            )
        records.append({
            "ray_character_exponents": [p_exponent, t_exponent],
            "overlap_transition_count": len(overlap.transitions),
            "overlap_exact": overlap.exact,
            "overlap_digest": _canonical_digest(overlap.as_record()),
            "deck_comparison_count": len(deck.comparisons),
            "deck_exact": deck.exact,
            "deck_digest": _canonical_digest(deck.as_record()),
            "frame_comparisons": frame_records,
            "atlas_alternating_frame_character": determinant_character,
            "formal_pair_frame_character": [
                (left + right) % 3
                for left, right in zip(
                    first_characters, determinant_character, strict=True
                )
            ],
        })
    return {
        "schema": "alternate-constituent-deck-atlases-v1",
        "scope": "fixed I3 constituent and two alternate I6 local-unit rays",
        "first_constituent_atlas_alternating_frame_character": first_characters,
        "cases": records,
        "alternate_constituent_atlases_exact": all(
            item["overlap_exact"] and item["deck_exact"] for item in records
        ),
        "selected_mixed_p_frame_reusable_for_alternates": False,
        "alternate_outer_extension_equivariance_certified": False,
        "alternate_quotient_determinants_certified": False,
        "alternate_higgs_characters_computed": False,
        "next_required_object": (
            "transfer the atlas-derived frames to the common Schoen complex; "
            "then test outer equivariance, determinant descent, and H1 characters"
        ),
    }


def write_alternate_constituent_deck_atlases(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed alternate constituent-atlas certificate."""

    payload = alternate_constituent_deck_atlases()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_constituent_deck_atlases()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"alternate_constituent_atlases_exact: {report['alternate_constituent_atlases_exact']}")
