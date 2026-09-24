"""Screen the unused one-dimensional Serre Ext character rays.

Owns:
    Exact joint-character decomposition, full Čech closure, and local
    dualizing-unit tests for each ray of the fixed I3/I6 presentations,
    plus the ray-only determinant-character necessary condition.

Depends on:
    Certified constituent Ext actions, the existing full Čech contraction,
    exact local frames, local residue arithmetic, and the selected quotient
    determinant audit.

Must not:
    Identify an alternate ray with the published carrier, infer a quotient
    determinant or Higgs spectrum, or select a ray from measured observables.

Phase 0:
    Research-only necessary screen of a finite declared Ext category.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import OMEGA, Eisenstein
from onetheory.models.heterotic_schoen.visible import InvariantSerreRay
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .local_constituent_frames import published_local_constituent_frames
from .published_constituent_deck_actions import (
    CHARACTERS,
    PublishedConstituentDeckAction,
    _simultaneous_eigenspace,
    published_constituent_deck_actions,
)
from .published_constituent_full_cech import (
    PublishedConstituentFullCech,
    _lift_vector,
    _transferred_matches_reduced,
)
from .published_constituent_local_units import evaluate_local_unit
from .published_constituent_ray_alignment import (
    PublishedConstituentRayAlignment,
    _combine_representatives,
    _generator_cell_dimension,
    published_constituent_ray_alignments,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/distinct_constituent_ray_screen.json"
DETERMINANT = ROOT / "data/generated/scientific_genesis/mixed_schoen_determinant_descent.json"


def _exponent(character: Eisenstein) -> int:
    """Return one exact cubic-root character exponent."""

    for exponent in range(3):
        if character == OMEGA**exponent:
            return exponent
    raise ValueError("the deck eigenvalue is not a cubic-root character")


def _selected_determinant_character() -> tuple[int, int]:
    """Verify the selected pair's quotient determinant character."""

    payload = json.loads(DETERMINANT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    character = payload.get("total_determinant_character")
    if (
        digest != _canonical_digest(payload)
        or payload.get("schema") != "mixed-schoen-determinant-descent-audit-v3"
        or character != [2, 1]
    ):
        raise ValueError("the selected quotient determinant certificate changed")
    return character[0], character[1]


def lift_joint_character_ray(
    action: PublishedConstituentDeckAction,
    p_character: Eisenstein,
    t_character: Eisenstein,
) -> PublishedConstituentFullCech:
    """Lift a unique Ext eigenray without borrowing the source-selected ray."""

    eigenspace = _simultaneous_eigenspace(
        action.p_induced, action.t_induced, p_character, t_character
    )
    if len(eigenspace) != 1:
        raise ValueError("this character must have exactly one Ext ray")
    coefficients = eigenspace[0].values
    extension = action.derived.extension
    reduced = _combine_representatives(
        extension.ext_one_representatives, coefficients
    )
    column = Matrix(
        tuple((value,) for value in coefficients), scalar_type=Eisenstein
    )
    published_column = action.intertwiner @ column
    ray = InvariantSerreRay(
        f"candidate {action.published.name}",
        Vector((row[0] for row in published_column.rows), scalar_type=Eisenstein),
        action.published.p.inverse().scale(p_character),
        action.published.t.inverse().scale(t_character),
    )
    alignment = PublishedConstituentRayAlignment(
        action,
        ray,
        (p_character, t_character),
        coefficients,
        reduced,
        _generator_cell_dimension(action),
    )
    full, depth = _lift_vector(extension, reduced, 1)
    result = PublishedConstituentFullCech(
        alignment,
        full,
        depth,
        _transferred_matches_reduced(extension),
    )
    if not (alignment.closed and result.transferred_matches_reduced and result.full_closed):
        raise ValueError("the candidate Ext ray failed its full Čech lift")
    return result


def distinct_constituent_ray_screen() -> dict[str, object]:
    """Test every one-dimensional joint Ext sector of the fixed point schemes."""

    actions = published_constituent_deck_actions()
    selected = published_constituent_ray_alignments()
    frame_groups = published_local_constituent_frames()
    results: list[dict[str, object]] = []
    for action, selection, frames in zip(
        actions, selected, frame_groups, strict=True
    ):
        extension = action.derived.extension
        sectors: list[dict[str, object]] = []
        for p_character in CHARACTERS:
            for t_character in CHARACTERS:
                eigenspace = _simultaneous_eigenspace(
                    action.p_induced,
                    action.t_induced,
                    p_character,
                    t_character,
                )
                if not eigenspace:
                    continue
                if len(eigenspace) != 1:
                    raise ValueError(
                        "a higher-dimensional character sector needs a family screen"
                    )
                lifted = lift_joint_character_ray(
                    action, p_character, t_character
                )
                coefficients = lifted.alignment.derived_coordinates
                reduced = lifted.alignment.representative
                full = lifted.representative
                depth = lifted.inclusion_depth
                reduced_closed = lifted.alignment.closed
                full_closed = lifted.full_closed
                local = tuple(
                    evaluate_local_unit(extension, full, frame)
                    for frame in frames
                )
                character = (_exponent(p_character), _exponent(t_character))
                source_character = tuple(
                    _exponent(value) for value in selection.source_character
                )
                sectors.append({
                    "character_exponents": list(character),
                    "native_subline_shift_from_source": [
                        (source - candidate) % 3
                        for source, candidate in zip(
                            source_character, character, strict=True
                        )
                    ],
                    "source_selected": (
                        (p_character, t_character) == selection.source_character
                    ),
                    "reduced_coordinates": [str(value) for value in coefficients],
                    "reduced_closed": reduced_closed,
                    "full_cech_closed": full_closed,
                    "full_term_count": len(full.terms),
                    "inclusion_depth": depth,
                    "syzygy_koszul_component_nonzero": any(
                        not value.is_zero()
                        for value in reduced.coordinates[
                            _generator_cell_dimension(action) :
                        ]
                    ),
                    "local_units_by_pivot": [
                        {
                            "pivot": unit.frame.pivot,
                            "residue_dimension": unit.local_ext_residue_dimension,
                            "nonzero_in_cokernel": unit.every_chart_nonzero_in_cokernel,
                            "chart_independent": (
                                unit.chart_independent_modulo_boundaries
                            ),
                            "unit": unit.unit_in_local_dualizing_algebra,
                        }
                        for unit in local
                    ],
                    "all_local_units": all(
                        unit.unit_in_local_dualizing_algebra for unit in local
                    ),
                })
        if len(sectors) != action.p_induced.row_count:
            raise ValueError("the joint character sectors do not exhaust Ext")
        if sum(bool(sector["source_selected"]) for sector in sectors) != 1:
            raise ValueError("the published selected ray was not recovered uniquely")
        results.append({
            "scheme": extension.scheme.name,
            "ext_dimension": action.p_induced.row_count,
            "sectors": sectors,
        })
    surviving = [
        {
            "scheme": result["scheme"],
            "character_exponents": sector["character_exponents"],
            "source_selected": sector["source_selected"],
        }
        for result in results
        for sector in cast(list[dict[str, object]], result["sectors"])
        if sector["all_local_units"]
    ]
    selected_determinant = _selected_determinant_character()
    unused_i6 = [
        sector
        for result in results
        for sector in cast(list[dict[str, object]], result["sectors"])
        if result["scheme"] == "I6"
        and sector["all_local_units"]
        and not sector["source_selected"]
    ]
    ray_only_t_characters = [
        (selected_determinant[1] - cast(
            list[int], sector["native_subline_shift_from_source"]
        )[1])
        % 3
        for sector in unused_i6
    ]
    return {
        "schema": "distinct-constituent-ray-screen-v1",
        "scope": "one-dimensional joint Ext rays of the fixed I3/I6 presentations",
        "constituents": results,
        "local_unit_survivors": surviving,
        "unused_i6_local_unit_rays": [
            item["character_exponents"]
            for item in surviving
            if item["scheme"] == "I6" and not item["source_selected"]
        ],
        "selected_quotient_determinant_character": list(selected_determinant),
        "ray_only_quotient_determinant_t_characters": ray_only_t_characters,
        "ray_only_trivial_determinant_possible": bool(ray_only_t_characters) and all(
            character == 0 for character in ray_only_t_characters
        ),
        "ray_only_scope": (
            "fixed I3 ray, fixed Serre quotient frames, fixed outer twists; "
            "only the I6 extension ray and its required subline character vary"
        ),
        "alternate_deck_atlases_constructed": False,
        "alternate_quotient_determinants_certified": False,
        "alternate_higgs_characters_computed": False,
        "next_required_object": (
            "full common-Schoen relinearization, quotient determinant, and "
            "Higgs H1 for the two unused I6 local-unit rays"
        ),
    }


def write_distinct_constituent_ray_screen(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed finite Ext-ray screen."""

    payload = distinct_constituent_ray_screen()
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
    report = write_distinct_constituent_ray_screen()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"unused_i6_local_unit_rays: {report['unused_i6_local_unit_rays']}")
