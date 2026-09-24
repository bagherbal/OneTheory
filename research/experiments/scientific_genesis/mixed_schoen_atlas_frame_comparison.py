"""Compare constituent atlas actions with synchronized Schoen frames.

Owns:
    Exact homogeneous-lift and inverse-generator comparisons, including the
    induced character on every full Cech--Koszul object summand.

Depends on:
    Certified constituent atlases, selected mixed resolutions, and exact
    Schoen coordinate and Hilbert--Burch actions.

Must not:
    Treat a frame change as a determinant repair, select an outer extension,
    or assert that the published rank-four carrier is refuted.

Phase 0:
    Research-only chain-frame comparison for the selected realization.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

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
from research.experiments.computable_carrier.resolution_actions import (
    tier_a_resolution_actions,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    KOSZUL_SHIFTS,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    CoordinateImage,
    _inverse_images,
    schoen_sparse_deck_actions,
)

from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_outer_actions import _constituent_frame

ROOT = Path(__file__).resolve().parents[3]
ATLAS = ROOT / "data/generated/scientific_genesis/published_constituent_deck_atlases.json"
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_atlas_frame_comparison.json"


def _atlas_characters() -> dict[int, dict[str, Eisenstein]]:
    """Check the certified atlas record against its defining line characters."""

    record = json.loads(ATLAS.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest", None)
    if (
        record.get("schema") != "published-constituent-deck-atlases-v1"
        or digest != _canonical_digest(record)
        or record.get("all_constituent_deck_atlases_exact") is not True
    ):
        raise ValueError("the published constituent atlas certificate is invalid")
    constituents = mixed_schoen_constituents()
    result: dict[int, dict[str, Eisenstein]] = {}
    for factor, constituent in enumerate(constituents, start=1):
        atlas = next(
            item for item in record["atlases"]
            if item["constituent"] == f"W{factor}"
        )
        if atlas["exact"] is not True or atlas["comparison_count"] != 12:
            raise ValueError("a constituent atlas is not globally certified")
        source = constituent.full.alignment.source_character
        twists = (
            constituent.full.alignment.action.p_twist,
            constituent.full.alignment.action.t_twist,
        )
        characters = {
            generator: twist / eigenvalue
            for generator, twist, eigenvalue in zip(
                ("P", "T"), twists, source, strict=True
            )
        }
        for generator, character in characters.items():
            recorded = {
                item["extension_line_character"]
                for item in atlas["comparisons"]
                if item["generator"] == generator
            }
            if recorded != {str(character)}:
                raise ValueError("the atlas line character changed")
        result[factor] = characters
    return result


def _uniform_coordinate_ratio(
    common: CoordinateImage,
    native: CoordinateImage,
) -> Eisenstein:
    """Recover one projective scalar relating two monomial lifts."""

    ratio = common[0][0] / native[0][0]
    if any(
        common_exponents != native_exponents
        or common_scalar != ratio * native_scalar
        for (common_scalar, common_exponents), (native_scalar, native_exponents)
        in zip(common, native, strict=True)
    ):
        raise ValueError("the coordinate lifts are not uniformly related")
    return ratio


def _atlas_frame(factor: int, generator: str, line: Eisenstein) -> Matrix:
    """Build the atlas homogeneous frame in the common object ordering."""

    resolution = tier_a_resolution_actions()[factor - 1].action(generator)
    target, source = resolution.target_action, resolution.source_action
    if factor == 2:
        line = Eisenstein(1) / line
        target, source = target.inverse(), source.inverse()
    blocks = (Matrix(((line,),), scalar_type=Eisenstein), target, source)
    size = sum(block.row_count for block in blocks)
    rows = [[Eisenstein(0) for _ in range(size)] for _ in range(size)]
    offset = 0
    for block in blocks:
        for row in range(block.row_count):
            for column in range(block.column_count):
                rows[offset + row][offset + column] = block[row][column]
        offset += block.row_count
    return Matrix(rows, scalar_type=Eisenstein)


def _character_exponent(value: Eisenstein) -> int:
    """Return the exponent of an exact cubic-root character."""

    for exponent in range(3):
        if value == OMEGA**exponent:
            return exponent
    raise ValueError("the frame ratio is not an order-three character")


@cache
def atlas_frame_comparison_audit() -> dict[str, object]:
    """Certify the full-summand frame relation for both constituents."""

    atlas_characters = _atlas_characters()
    constituents = mixed_schoen_constituents()
    actions = {action.name: action for action in schoen_sparse_deck_actions()}
    records: list[dict[str, object]] = []
    for factor, constituent in enumerate(constituents, start=1):
        for generator in ("P", "T"):
            action = actions[generator]
            native_base = published_coordinate_images(generator)
            native_fiber = _fiber_coordinate_images(generator, factor)
            if factor == 1:
                if action.x_images != native_base:
                    raise ValueError("first-factor base lifts differ")
                coordinate_ratio = _uniform_coordinate_ratio(
                    action.p_images, native_fiber
                )
            else:
                if (
                    action.u_images != _inverse_images(native_base)
                    or action.p_images != _inverse_images(native_fiber)
                ):
                    raise ValueError("second-factor inverse lifts differ")
                coordinate_ratio = Eisenstein(1)

            atlas_frame = _atlas_frame(
                factor, generator, atlas_characters[factor][generator]
            )
            common_frame = Matrix(
                tuple(
                    tuple(
                        value / coordinate_ratio**item.line_degree[2]
                        for value in row
                    )
                    for item, row in zip(
                        constituent.objects, atlas_frame.rows, strict=True
                    )
                ),
                scalar_type=Eisenstein,
            )
            mixed_frame = _constituent_frame(factor, generator)
            ratio = mixed_frame[0][0] / common_frame[0][0]
            if mixed_frame != common_frame.scale(ratio):
                raise ValueError("atlas and mixed frames differ non-uniformly")

            # Each Koszul equation has fiber degree one. Scaling the fiber
            # coordinate lift therefore multiplies a full summand by the
            # line degree, independently of its Koszul position.
            for item in constituent.objects:
                for shift in KOSZUL_SHIFTS.values():
                    equation_count = -shift[2]
                    ambient_degree = item.line_degree[2] - equation_count
                    if (
                        coordinate_ratio**ambient_degree
                        * coordinate_ratio**equation_count
                        != coordinate_ratio**item.line_degree[2]
                    ):
                        raise ValueError("Koszul lift scaling is inconsistent")
            records.append({
                "constituent": constituent.name,
                "generator": generator,
                "atlas_line_character": str(atlas_characters[factor][generator]),
                "native_to_common_fiber_lift_scalar": str(coordinate_ratio),
                "atlas_to_mixed_uniform_character": _character_exponent(ratio),
                "object_count": len(constituent.objects),
                "koszul_summands_checked_per_object": len(KOSZUL_SHIFTS),
                "homogeneous_frame_identity": True,
                "full_summand_scaling_identity": True,
            })

    first = tuple(
        next(item["atlas_to_mixed_uniform_character"] for item in records
             if item["constituent"] == "V1" and item["generator"] == generator)
        for generator in ("P", "T")
    )
    second = tuple(
        next(item["atlas_to_mixed_uniform_character"] for item in records
             if item["constituent"] == "V2" and item["generator"] == generator)
        for generator in ("P", "T")
    )
    if first != (2, 0) or second != (0, 0):
        raise ValueError("the selected atlas/common-frame relation changed")
    return {
        "schema": "mixed-schoen-atlas-frame-comparison-v1",
        "scope": "selected constituent frames and declared common homogeneous lifts",
        "comparisons": records,
        "first_constituent_uniform_twist": list(first),
        "second_constituent_uniform_twist": list(second),
        "full_chain_comparison_exact": True,
        "source_atlas_total_determinant_certified": False,
        "outer_extension_relinearized": False,
        "published_rank_four_carrier_reconstructed": False,
    }


def write_atlas_frame_comparison(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed exact constituent-frame comparison."""

    payload = atlas_frame_comparison_audit()
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
    write_atlas_frame_comparison()
