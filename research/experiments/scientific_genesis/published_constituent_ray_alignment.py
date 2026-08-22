"""Recover the source-selected constituent rays in the derived Ext bases.

Owns:
    Exact pullback of the selected W1/W2 Serre rays through the certified
    simultaneous intertwiners and separation of their edge-map components.

Depends on:
    The source-bound Serre kernel actions, exact derived dP9 deck actions, and
    deterministic cohomology representatives over the Eisenstein field.

Must not:
    Replace a selected nontrivial character by the trivial eigenspace, infer
    local freeness from a nonzero correction alone, or claim a global bundle.

Phase 0:
    Research-only correction of the constituent-ray alignment convention.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.homological import CoordinateVector
from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from onetheory.models.heterotic_schoen.visible import InvariantSerreRay, serre_data
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .published_constituent_deck_actions import (
    PublishedConstituentDeckAction,
    published_constituent_deck_actions,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/published_constituent_ray_alignment.json"


def _column(vector: Vector) -> Matrix:
    """Return one exact production vector as a matrix column."""

    return Matrix(
        tuple((value,) for value in vector.values),
        scalar_type=Eisenstein,
    )


def _combine_representatives(
    representatives: tuple[CoordinateVector, ...],
    coefficients: tuple[Eisenstein, ...],
) -> CoordinateVector:
    """Form one exact cocycle in the deterministic derived basis."""

    if not representatives or len(representatives) != len(coefficients):
        raise ValueError("ray coordinates must span the complete Ext basis")
    space = representatives[0].space
    if any(representative.space != space for representative in representatives):
        raise ValueError("Ext representatives use incompatible total spaces")
    return CoordinateVector(
        space,
        tuple(
            sum(
                (
                    coefficient * representative.coordinates[index]
                    for coefficient, representative in zip(
                        coefficients,
                        representatives,
                        strict=True,
                    )
                ),
                Eisenstein(0),
            )
            for index in range(space.dimension)
        ),
    )


def _eigencharacter(
    action: Matrix,
    vector: Matrix,
) -> Eisenstein:
    """Identify one exact order-three eigencharacter."""

    for character in (Eisenstein(1), OMEGA, OMEGA2):
        if action @ vector == vector.scale(character):
            return character
    raise ValueError("the selected source ray is not an order-three eigenvector")


def _generator_cell_dimension(action: PublishedConstituentDeckAction) -> int:
    """Return the degree-one generator/Čech cell dimension before syzygies."""

    return sum(
        bundle.complex.spaces.space(1).dimension
        for bundle in action.derived.extension.generator_bundles
    )


@dataclass(frozen=True, slots=True)
class PublishedConstituentRayAlignment:
    """One source-selected ray expressed in the exact derived Ext basis."""

    action: PublishedConstituentDeckAction
    source_ray: InvariantSerreRay
    source_character: tuple[Eisenstein, Eisenstein]
    derived_coordinates: tuple[Eisenstein, ...]
    representative: CoordinateVector
    generator_cell_dimension: int

    @property
    def selected_chain_eigenvector(self) -> bool:
        """Return whether both aligned chain maps realize the selected character."""

        p_character, t_character = self.source_character
        return (
            self.action.p_action.component(1)(self.representative)
            == self.representative.scale(p_character)
            and self.action.t_action.component(1)(self.representative)
            == self.representative.scale(t_character)
        )

    @property
    def closed(self) -> bool:
        """Return whether the pulled-back source ray is an exact total cocycle."""

        return self.action.derived.extension.total.differential(1)(
            self.representative
        ).is_zero()

    @property
    def correction_coordinates(self) -> tuple[Eisenstein, ...]:
        """Return the parent-degree-one syzygy/Koszul part of the cocycle."""

        return self.representative.coordinates[self.generator_cell_dimension :]

    @property
    def has_syzygy_koszul_component(self) -> bool:
        """Return whether the source ray survives the local-Ext edge map."""

        return any(not value.is_zero() for value in self.correction_coordinates)

    @property
    def old_trivial_character_is_different(self) -> bool:
        """Return whether the formerly selected fixed line is not this ray."""

        old = self.action.invariant_representatives
        return len(old) == 1 and old[0] != self.representative

    def as_record(self) -> dict[str, object]:
        """Serialize the corrected ray alignment and its exact boundary."""

        return {
            "constituent": self.action.published.name,
            "source_character": {
                "P": str(self.source_character[0]),
                "T": str(self.source_character[1]),
            },
            "derived_ext_coordinates": [
                str(value) for value in self.derived_coordinates
            ],
            "selected_chain_eigenvector": self.selected_chain_eigenvector,
            "total_cocycle_closed": self.closed,
            "generator_cech_nonzero_count": sum(
                not value.is_zero()
                for value in self.representative.coordinates[
                    : self.generator_cell_dimension
                ]
            ),
            "syzygy_koszul_nonzero_count": sum(
                not value.is_zero() for value in self.correction_coordinates
            ),
            "has_syzygy_koszul_component": self.has_syzygy_koszul_component,
            "old_trivial_character_is_different": (
                self.old_trivial_character_is_different
            ),
            "local_freeness_claimed": False,
            "status": (
                "source-selected mixed Ext cocycle; full Cech lift and local-unit "
                "evaluation remain required"
            ),
        }


def _alignment(
    action: PublishedConstituentDeckAction,
    source_ray: InvariantSerreRay,
) -> PublishedConstituentRayAlignment:
    """Pull one selected production ray through the simultaneous intertwiner."""

    source_column = _column(source_ray.vector)
    coordinates_column = action.intertwiner.inverse() @ source_column
    coordinates = tuple(row[0] for row in coordinates_column.rows)
    representative = _combine_representatives(
        action.derived.extension.ext_one_representatives,
        coordinates,
    )
    result = PublishedConstituentRayAlignment(
        action,
        source_ray,
        (
            _eigencharacter(action.published.p, source_column),
            _eigencharacter(action.published.t, source_column),
        ),
        coordinates,
        representative,
        _generator_cell_dimension(action),
    )
    if not (
        result.selected_chain_eigenvector
        and result.closed
        and result.has_syzygy_koszul_component
        and result.old_trivial_character_is_different
    ):
        raise ValueError("a source-selected constituent ray failed alignment")
    return result


@cache
def published_constituent_ray_alignments(
) -> tuple[PublishedConstituentRayAlignment, ...]:
    """Recover both selected W1/W2 rays in the derived total complexes."""

    source = serre_data()
    return tuple(
        _alignment(action, ray)
        for action, ray in zip(
            published_constituent_deck_actions(),
            source.rays,
            strict=True,
        )
    )


def write_published_constituent_ray_alignments(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed constituent-ray correction certificate."""

    payload: dict[str, object] = {
        "schema": "published-constituent-ray-alignment-v1",
        "constituents": [
            result.as_record() for result in published_constituent_ray_alignments()
        ],
        "source_selected_characters": [
            {"P": "omega", "T": "1"},
            {"P": "-1-omega", "T": "omega"},
        ],
        "trivial_character_selection_retired": True,
        "existing_pure_cech_mapping_cones_identified_with_published_W1_W2": False,
        "next_required_object": (
            "full standard-cover Cech lifts of the mixed source-selected rays, "
            "followed by local dualizing-unit evaluation"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact source-selected ray-alignment artifact."""

    payload = write_published_constituent_ray_alignments()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "trivial_character_selection_retired: "
        f"{payload['trivial_character_selection_retired']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PublishedConstituentRayAlignment",
    "published_constituent_ray_alignments",
]
