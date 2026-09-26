"""Generate strict alternate-constituent matter classes for one Yukawa slice.

Owns:
    Two complete I6 matter character sectors required by the up-type Wilson
    weights, with exact full Cech cycles and alternate-atlas eigenactions.

Depends on:
    The frozen alternate component, exact mixed transfer and contraction,
    certified I6 atlas frames, and published Spin(10) Wilson weights.

Must not:
    Select an outer-extension point, treat constituent classes as cone
    classes, infer a Higgs cocycle, or claim a Yukawa matrix.

Phase 0:
    Research-only same-carrier constituent cocycles for a vertical slice.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
    _reduced_basis,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    _independent_columns,
    _SparseSpanSolver,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    SchoenSparseDeckAction,
    schoen_sparse_deck_actions,
)
from research.experiments.computable_carrier.schoen_sparse_outer_actions import (
    _cohomology_complement_columns,
    _columns,
    _select_columns,
)

from .alternate_constituent_hom_actions import _common_frame
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import _constituent
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_observable_spectrum import (
    SPECTRUM_ARXIV_ID,
    SPECTRUM_SOURCE_SHA256,
    _source_digest,
)
from .mixed_schoen_outer_actions import (
    _full_action,
    _MixedContraction,
    _perturbed_inclusion,
    _perturbed_projection,
    _reduced_cochain,
)
from .mixed_schoen_outer_transfer import mixed_schoen_unit, mixed_transferred_outer_hom
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
GENERATED = ROOT / "data/generated/scientific_genesis"
OUTPUT = GENERATED / "alternate_constituent_up_matter_representatives.json"
CARRIER = GENERATED / "alternate_constituent_carrier_state.json"
SPECTRUM = GENERATED / "alternate_constituent_structural_spectrum.json"
MATTER = GENERATED / "alternate_constituent_matter_profile.json"
Character = tuple[int, int]
UP_SPINOR_WILSON_WEIGHTS: tuple[Character, Character] = ((1, 2), (2, 2))
UP_HIGGS_WILSON_WEIGHT: Character = (0, 2)


def _add(left: Character, right: Character) -> Character:
    return (left[0] + right[0]) % 3, (left[1] + right[1]) % 3


def _negative(value: Character) -> Character:
    return (-value[0]) % 3, (-value[1]) % 3


def _project(
    cochain: SparseOuterCechCochain,
    character: Character,
    contraction: _MixedContraction,
    actions: dict[str, SchoenSparseDeckAction],
    frames: dict[str, tuple[Matrix, Matrix]],
) -> SparseOuterCechCochain:
    """Factor the exact nine-term projector into two order-three averages."""

    def average_generator(
        current: SparseOuterCechCochain,
        name: str,
        exponent: int,
    ) -> SparseOuterCechCochain:
        first = _full_action(
            current, contraction.left, contraction.right,
            actions[name], frames[name],
        )
        second = _full_action(
            first, contraction.left, contraction.right,
            actions[name], frames[name],
        )
        return (
            current
            + first.scale(OMEGA ** -exponent)
            + second.scale(OMEGA ** (-2 * exponent))
        )

    p_average = average_generator(cochain, "P", character[0])
    return average_generator(p_average, "T", character[1]).scale(Eisenstein(1) / 9)


def _strict(
    cochain: SparseOuterCechCochain,
    character: Character,
    contraction: _MixedContraction,
    actions: dict[str, SchoenSparseDeckAction],
    frames: dict[str, tuple[Matrix, Matrix]],
) -> bool:
    """Require both full-cochain eigenidentities in the alternate frames."""

    return all(
        _full_action(
            cochain, contraction.left, contraction.right,
            actions[generator], frames[generator],
        ) == cochain.scale(OMEGA ** character[index])
        for index, generator in enumerate(("P", "T"))
    )


@dataclass(frozen=True, slots=True)
class AlternateMatterClass:
    """One strict I6 class and its deterministic cohomology coordinates."""

    character: Character
    seed_index: int
    cohomology_coordinates: tuple[Eisenstein, ...]
    full_cochain: SparseOuterCechCochain
    inclusion_depth: int
    projection_depth: int

    def as_record(self, common_twist: Character) -> dict[str, object]:
        """Serialize exact identity and action evidence, not guessed physics."""

        return {
            "constituent_character": list(self.character),
            "repaired_carrier_character": list(_add(self.character, common_twist)),
            "seed_index": self.seed_index,
            "cohomology_coordinates": [str(value) for value in self.cohomology_coordinates],
            "full_term_count": len(self.full_cochain.terms),
            "full_digest": _cochain_digest((self.full_cochain,)),
            "inclusion_depth": self.inclusion_depth,
            "projection_depth": self.projection_depth,
            "full_cycle_exact": True,
            "strict_alternate_character_exact": True,
        }


@dataclass(frozen=True, slots=True)
class AlternateUpMatterRepresentatives:
    """The two I6 sectors needed by an up-type matrix on the alternate cone."""

    classes: tuple[AlternateMatterClass, ...]
    common_twist: Character
    carrier_digest: str
    spectrum_digest: str
    matter_digest: str
    source_digest: str
    reduced_dimension: int
    boundary_dimension: int

    def as_record(self) -> dict[str, object]:
        """Return the content-addressable exact constituent-slice certificate."""

        counts = {
            character: sum(item.character == character for item in self.classes)
            for character in ((_add(weight, _negative(self.common_twist)))
                              for weight in UP_SPINOR_WILSON_WEIGHTS)
        }
        if sorted(counts.values()) != [2, 2]:
            raise ValueError("both up-type I6 character sectors need two classes")
        return {
            "schema": "alternate-constituent-up-matter-representatives-v1",
            "ray_character_exponents": [0, 1],
            "coefficient_field": "Q(omega)",
            "prerequisite_artifact_digests": {
                "frozen_carrier": self.carrier_digest,
                "structural_spectrum": self.spectrum_digest,
                "cover_matter_profile": self.matter_digest,
                "published_wilson_source": self.source_digest,
            },
            "up_spinor_wilson_weights": [list(item) for item in UP_SPINOR_WILSON_WEIGHTS],
            "up_higgs_wilson_weight": list(UP_HIGGS_WILSON_WEIGHT),
            "common_flat_twist": list(self.common_twist),
            "constituent_character_sectors": [list(item) for item in counts],
            "reduced_h1_dimension": self.reduced_dimension,
            "independent_boundary_dimension": self.boundary_dimension,
            "classes": [item.as_record(self.common_twist) for item in self.classes],
            "target_character_multiplicities_complete": True,
            "outer_cone_lifts_computed": False,
            "higgs_cocycles_computed": False,
            "yukawa_matrix_computed": False,
            "next_required_object": (
                "lift these four I6 classes through the two-parameter outer "
                "cone and construct the physical up-Higgs chain class"
            ),
        }


@cache
def alternate_constituent_up_matter_representatives() -> AlternateUpMatterRepresentatives:
    """Generate four strict classes without enumerating other matter sectors."""

    carrier_digest, carrier = _verified_payload(CARRIER)
    spectrum_digest, spectrum = _verified_payload(SPECTRUM)
    matter_digest, matter = _verified_payload(MATTER)
    state = cast(dict[str, object], carrier["computable_one_theory_carrier_state"])
    if (
        carrier.get("schema") != "alternate-constituent-carrier-state-v1"
        or state.get("component_id") != "alternate-i6-ray-0-1-P1"
        or state.get("frozen") is not True
        or cast(dict[str, object], state["certificate_digests"]).get(
            "observable_spectrum"
        ) != spectrum_digest
        or spectrum.get("schema") != "alternate-constituent-structural-spectrum-v1"
        or spectrum.get("matter_cover_h0_to_h3") != [0, 27, 0, 0]
        or spectrum.get("cover_higgs_h0_to_h3") != [0, 4, 4, 0]
        or matter.get("schema") != "alternate-constituent-matter-profile-v1"
        or cast(dict[str, object], matter["second_constituent"])["cover_h0_to_h3"]
        != [0, 18, 0, 0]
    ):
        raise ValueError("the frozen alternate matter-slice premises changed")
    source_digest = _source_digest(SPECTRUM_ARXIV_ID, SPECTRUM_SOURCE_SHA256)
    common_twist = cast(Character, tuple(cast(list[int], spectrum["common_flat_twist"])))
    higgs_forward = cast(list[list[int]], spectrum["higgs_forward_characters"])
    if (
        common_twist != (1, 2)
        or list(UP_HIGGS_WILSON_WEIGHT) not in higgs_forward
        or _add(_add(UP_SPINOR_WILSON_WEIGHTS[0], UP_SPINOR_WILSON_WEIGHTS[1]),
                UP_HIGGS_WILSON_WEIGHT) != (0, 0)
    ):
        raise ValueError("the published up-type character route changed")
    target_characters = tuple(
        _add(weight, _negative(common_twist))
        for weight in UP_SPINOR_WILSON_WEIGHTS
    )
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    second = _constituent(ray, "I6-ray-0-1", 2, (1, -1, 0))
    unit = mixed_schoen_unit()
    transferred = mixed_transferred_outer_hom(second, unit)
    spaces = dict(transferred.spaces)
    differentials = dict(transferred.differentials)
    incoming, outgoing = differentials[0], differentials[1]
    if transferred.cohomology_dimension(1) != 18 or not transferred.squared_zero:
        raise ValueError("the alternate I6 matter complex changed")
    cycles = outgoing.kernel_inclusion()
    selected = _cohomology_complement_columns(incoming, cycles)
    representatives = _select_columns(cycles, selected, "alternate:up-matter")
    seeds = tuple(_columns(representatives))
    boundaries = _independent_columns(incoming)
    if len(seeds) != 18 or len(boundaries) != incoming.rank():
        raise ValueError("the alternate I6 H1 basis or boundaries changed")
    solver = _SparseSpanSolver(boundaries + seeds)
    contraction = _MixedContraction(second, unit)
    entries = _reduced_basis(contraction.left_skeleton, contraction.right_skeleton, 1)
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    frames = {
        name: (_common_frame(second, action), Matrix.identity(1, scalar_type=Eisenstein))
        for name, action in actions.items()
    }
    found: dict[Character, list[AlternateMatterClass]] = {
        target_characters[0]: [], target_characters[1]: []
    }
    for seed_index, coefficients in enumerate(seeds):
        full, inclusion_depth = _perturbed_inclusion(
            _reduced_cochain(entries, coefficients), contraction
        )
        if not contraction.differential(full).is_zero():
            raise ValueError("an alternate I6 matter seed is not a full cycle")
        for character in target_characters:
            if len(found[character]) == 2:
                continue
            projected = _project(full, character, contraction, actions, frames)
            if projected.is_zero():
                continue
            if not contraction.differential(projected).is_zero():
                raise ValueError("an alternate I6 character projection is not closed")
            if not _strict(projected, character, contraction, actions, frames):
                raise ValueError("an alternate I6 character projection is not strict")
            reduced, projection_depth = _perturbed_projection(projected, contraction, 1)
            if any(
                not sum(
                    (value * reduced.get(column, Eisenstein(0)) for column, value in row),
                    Eisenstein(0),
                ).is_zero()
                for row in outgoing.rows
            ):
                raise ValueError("the projected full cycle lost reduced closure")
            coordinates = solver.coordinates(reduced)
            cohomology = tuple(
                coordinates.get(len(boundaries) + index, Eisenstein(0))
                for index in range(18)
            )
            if all(value.is_zero() for value in cohomology):
                continue
            existing = found[character]
            vectors = [item.cohomology_coordinates for item in existing] + [cohomology]
            rank = Matrix(
                tuple(tuple(vector[row] for vector in vectors) for row in range(18)),
                scalar_type=Eisenstein,
            ).rank()
            if rank != len(vectors):
                continue
            existing.append(AlternateMatterClass(
                character, seed_index, cohomology, projected,
                inclusion_depth, projection_depth,
            ))
        if all(len(items) == 2 for items in found.values()):
            break
    if any(len(items) != 2 for items in found.values()):
        raise ValueError("the strict up-type I6 sectors did not reach expected dimension")
    return AlternateUpMatterRepresentatives(
        tuple(item for character in target_characters for item in found[character]),
        common_twist,
        carrier_digest,
        spectrum_digest,
        matter_digest,
        source_digest,
        spaces[1].dimension - incoming.rank() - outgoing.rank(),
        len(boundaries),
    )


def write_alternate_constituent_up_matter_representatives(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write an exact content-addressed four-class research certificate."""

    payload = alternate_constituent_up_matter_representatives().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_constituent_up_matter_representatives()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"strict_class_count: {len(report['classes'])}")
