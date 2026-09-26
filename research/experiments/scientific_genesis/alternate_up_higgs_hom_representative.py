"""Extract the alternate Hom class needed by the up-Higgs chain route.

Owns:
    One strict full-Čech representative in the unique Hom character that the
    certified determinant and flat frames send to the up-Higgs sector.

Depends on:
    The frozen alternate carrier, exact Hom transfer, atlas deck actions, and
    the published Wilson-character assignment.

Must not:
    Call a Hom cochain a tensor or exterior-square cocycle, choose an outer
    extension point, or infer a Yukawa coefficient.

Phase 0:
    Research-only input to a future same-cone Higgs construction.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

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
    schoen_sparse_deck_actions,
)
from research.experiments.computable_carrier.schoen_sparse_outer_actions import (
    _cohomology_complement_columns,
    _columns,
    _select_columns,
)

from .alternate_constituent_hom_actions import OUTPUT as HOM_ACTIONS
from .alternate_constituent_hom_actions import _common_frame
from .alternate_constituent_outer_universal_cone import OUTPUT as CONE
from .alternate_constituent_structural_spectrum import OUTPUT as SPECTRUM
from .alternate_constituent_up_matter_representatives import (
    CARRIER,
    Character,
    _add,
    _negative,
    _project,
    _strict,
)
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import _constituent, mixed_schoen_constituents
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import (
    _MixedContraction,
    _perturbed_inclusion,
    _perturbed_projection,
    _reduced_cochain,
)
from .mixed_schoen_outer_transfer import mixed_transferred_outer_hom
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_higgs_hom_representative.json"
HOM_CHARACTER: Character = (2, 0)
UP_HIGGS_FORWARD_CHARACTER: Character = (0, 2)


@dataclass(frozen=True, slots=True)
class AlternateUpHiggsHomRepresentative:
    """One exact source-Hom class, not yet an exterior-square Higgs class."""

    full_cochain: SparseOuterCechCochain
    seed_index: int
    cohomology_coordinates: tuple[Eisenstein, ...]
    carrier_digest: str
    cone_digest: str
    spectrum_digest: str
    hom_action_digest: str
    inclusion_depth: int
    projection_depth: int

    def as_record(self) -> dict[str, object]:
        """Serialize exact character and nonpromotion gates."""

        return {
            "schema": "alternate-up-higgs-hom-representative-v1",
            "coefficient_field": "Q(omega)",
            "ray_character_exponents": [0, 1],
            "hom_orientation": "Hom(V2 tensor det(V1), V1)",
            "hom_character": list(HOM_CHARACTER),
            "repaired_higgs_forward_character": list(UP_HIGGS_FORWARD_CHARACTER),
            "repaired_higgs_source_character": list(_negative(UP_HIGGS_FORWARD_CHARACTER)),
            "prerequisite_artifact_digests": {
                "frozen_carrier": self.carrier_digest,
                "universal_cone": self.cone_digest,
                "structural_spectrum": self.spectrum_digest,
                "alternate_hom_action": self.hom_action_digest,
            },
            "seed_index": self.seed_index,
            "cohomology_coordinates": [str(value) for value in self.cohomology_coordinates],
            "full_term_count": len(self.full_cochain.terms),
            "full_digest": _cochain_digest((self.full_cochain,)),
            "inclusion_depth": self.inclusion_depth,
            "projection_depth": self.projection_depth,
            "full_cycle_exact": True,
            "strict_hom_character_exact": True,
            "nonboundary_exact": True,
            "higgs_tensor_chain_map_constructed": False,
            "exterior_cone_higgs_cocycle_constructed": False,
            "yukawa_matrix_computed": False,
            "next_required_object": (
                "realize the rank-two determinant identity as a certified "
                "chain map, then lift this class through the exterior cone"
            ),
        }


@cache
def alternate_up_higgs_hom_representative() -> AlternateUpHiggsHomRepresentative:
    """Project exact Hom H1 into the one up-Higgs-relevant character."""

    carrier_digest, carrier = _verified_payload(CARRIER)
    cone_digest, cone = _verified_payload(CONE)
    spectrum_digest, spectrum = _verified_payload(SPECTRUM)
    hom_action_digest, hom_action = _verified_payload(HOM_ACTIONS)
    cases = hom_action.get("cases")
    if not isinstance(cases, list):
        raise ValueError("alternate Hom-action cases are missing")
    matches = [
        item for item in cases
        if isinstance(item, dict) and item.get("ray_character_exponents") == [0, 1]
    ]
    if len(matches) != 1:
        raise ValueError("the alternate ray must have one certified Hom action")
    case = matches[0]
    state = cast(dict[str, object], carrier["computable_one_theory_carrier_state"])
    state_digests = cast(dict[str, object], state["certificate_digests"])
    prerequisites = cast(dict[str, object], spectrum["prerequisite_artifact_digests"])
    twist = cast(Character, tuple(cast(list[int], spectrum["common_flat_twist"])))
    total_determinant = cast(
        Character,
        tuple(cast(list[int], cone["determinant_character_before_common_twist"])),
    )
    if (
        carrier.get("schema") != "alternate-constituent-carrier-state-v1"
        or state.get("component_id") != "alternate-i6-ray-0-1-P1"
        or state.get("frozen") is not True
        or state_digests.get("universal_cone") != cone_digest
        or cone.get("schema") != "alternate-constituent-outer-universal-cone-v1"
        or spectrum.get("schema") != "alternate-constituent-structural-spectrum-v1"
        or prerequisites.get("alternate_cone") != cone_digest
        or prerequisites.get("alternate_hom_actions") != hom_action_digest
        or spectrum.get("hom_fourier_characters")
        != [[0, 0], [1, 2], [2, 0], [2, 2]]
        or list(UP_HIGGS_FORWARD_CHARACTER)
        not in cast(list[list[int]], spectrum["higgs_forward_characters"])
        or hom_action.get("schema") != "alternate-constituent-hom-actions-v2"
        or case.get("cohomology_group_relations") is not True
        or case.get("boundary_preservation_certified") is not True
        or case.get("cover_hom_characters")
        != [[0, 0], [1, 2], [2, 0], [2, 2]]
        or case.get("h1_dimension") != 4
        or twist != (1, 2)
        or total_determinant != (2, 1)
        or _add(_add(HOM_CHARACTER, total_determinant), _add(twist, twist))
        != UP_HIGGS_FORWARD_CHARACTER
    ):
        raise ValueError("the alternate up-Higgs Hom character premises changed")

    first = mixed_schoen_constituents()[0]
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    second = _constituent(ray, "I6-ray-0-1", 2, (-1, 1, 0))
    transferred = mixed_transferred_outer_hom(first, second)
    differentials = dict(transferred.differentials)
    incoming, outgoing = differentials[0], differentials[1]
    if (
        not transferred.squared_zero
        or transferred.cohomology_dimension(1) != 4
        or incoming.rank() != case["incoming_rank"]
        or outgoing.rank() != case["outgoing_rank"]
    ):
        raise ValueError("the alternate up-Higgs Hom transfer changed")
    cycles = outgoing.kernel_inclusion()
    selected = _cohomology_complement_columns(incoming, cycles)
    representatives = _select_columns(cycles, selected, "alternate:up-higgs:Hom")
    seeds = tuple(_columns(representatives))
    boundaries = _independent_columns(incoming)
    if len(seeds) != 4 or len(boundaries) != incoming.rank():
        raise ValueError("the alternate Hom H1 basis changed")
    solver = _SparseSpanSolver(boundaries + seeds)
    contraction = _MixedContraction(first, second)
    entries = _reduced_basis(contraction.left_skeleton, contraction.right_skeleton, 1)
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    frames = {
        name: (_common_frame(first, action), _common_frame(second, action))
        for name, action in actions.items()
    }
    found: AlternateUpHiggsHomRepresentative | None = None
    for seed_index, coefficients in enumerate(seeds):
        full, inclusion_depth = _perturbed_inclusion(
            _reduced_cochain(entries, coefficients), contraction
        )
        if not contraction.differential(full).is_zero():
            raise ValueError("an alternate Hom seed is not a full cycle")
        projected = _project(full, HOM_CHARACTER, contraction, actions, frames)
        if projected.is_zero():
            continue
        if not contraction.differential(projected).is_zero():
            raise ValueError("the alternate Hom character projection is not closed")
        if not _strict(projected, HOM_CHARACTER, contraction, actions, frames):
            raise ValueError("the alternate Hom character projection is not strict")
        reduced, projection_depth = _perturbed_projection(projected, contraction, 1)
        coordinates = solver.coordinates(reduced)
        cohomology = tuple(
            coordinates.get(len(boundaries) + index, Eisenstein(0))
            for index in range(4)
        )
        if all(value.is_zero() for value in cohomology):
            continue
        candidate = AlternateUpHiggsHomRepresentative(
            projected, seed_index, cohomology,
            carrier_digest, cone_digest, spectrum_digest, hom_action_digest,
            inclusion_depth, projection_depth,
        )
        if found is None:
            found = candidate
        else:
            scale = next(
                left / right
                for left, right in zip(
                    cohomology, found.cohomology_coordinates, strict=True
                )
                if not right.is_zero()
            )
            if any(
                left != scale * right
                for left, right in zip(
                    cohomology, found.cohomology_coordinates, strict=True
                )
            ):
                raise ValueError("the target Hom character has multiplicity above one")
    if found is None:
        raise ValueError("the up-Higgs-relevant Hom character has no full class")
    return found


def write_alternate_up_higgs_hom_representative(path: Path = OUTPUT) -> dict[str, object]:
    """Write an exact strict Hom-class certificate without a Higgs claim."""

    payload = alternate_up_higgs_hom_representative().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_up_higgs_hom_representative()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"full_term_count: {report['full_term_count']}")
