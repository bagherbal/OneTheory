"""Lift alternate up-type matter sectors through the universal outer cone.

Owns:
    Exact constant first-constituent classes and parameter-linear corrections
    for all four required second-constituent up-type classes.

Depends on:
    The frozen alternate cone, strict I6 matter classes, exact common-DGA cup,
    mixed perturbation contraction, and certified atlas deck frames.

Must not:
    Select an outer parameter, identify a constituent class with a cone class
    before its correction is checked, or infer a Higgs cocycle or Yukawa value.

Phase 0:
    Research-only chain-level input for one holomorphic Yukawa matrix.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
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

from .alternate_constituent_hom_actions import _common_frame
from .alternate_constituent_outer_universal_cone import INVARIANTS
from .alternate_constituent_up_matter_representatives import (
    CARRIER,
    AlternateMatterClass,
    Character,
    _project,
    _strict,
    alternate_constituent_up_matter_representatives,
)
from .alternate_constituent_up_matter_representatives import (
    OUTPUT as UP_MATTER,
)
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_common_dga import exact_mixed_primitive, mixed_outer_cup
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import (
    _MixedContraction,
    _perturbed_inclusion,
    _perturbed_projection,
    _reduced_cochain,
)
from .mixed_schoen_outer_transfer import (
    MixedTransferredOuterHom,
    mixed_schoen_unit,
    mixed_transferred_outer_hom,
)
from .mixed_schoen_outer_universal_cone import _representative, _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_constituent_up_cone_matter_lifts.json"
CONE = ROOT / "data/generated/scientific_genesis/alternate_constituent_outer_universal_cone.json"
TARGETS: tuple[Character, Character] = ((0, 0), (1, 0))


@dataclass(frozen=True, slots=True)
class FirstMatterClass:
    """One strict unchanged I3 class in the alternate common atlas frame."""

    character: Character
    seed_index: int
    cohomology_coordinates: tuple[Eisenstein, ...]
    full_cochain: SparseOuterCechCochain

    def as_record(self) -> dict[str, object]:
        """Record exact first-constituent identity without a cone claim."""

        return {
            "character": list(self.character),
            "seed_index": self.seed_index,
            "cohomology_coordinates": [str(value) for value in self.cohomology_coordinates],
            "full_term_count": len(self.full_cochain.terms),
            "full_digest": _cochain_digest((self.full_cochain,)),
            "full_cycle_exact": True,
            "strict_alternate_character_exact": True,
        }


@dataclass(frozen=True, slots=True)
class ConeCoefficient:
    """One exact parameter coefficient of a second-constituent matter lift."""

    parameter: str
    product_term_count: int
    product_digest: str
    correction: SparseOuterCechCochain
    primitive_projection_depth: int
    primitive_inclusion_depth: int
    primitive_homotopy_depth: int

    def as_record(self) -> dict[str, object]:
        """Expose the exact cup and correction evidence for one parameter."""

        return {
            "parameter": self.parameter,
            "product_term_count": self.product_term_count,
            "product_digest": self.product_digest,
            "correction_term_count": len(self.correction.terms),
            "correction_digest": _cochain_digest((self.correction,)),
            "primitive_projection_depth": self.primitive_projection_depth,
            "primitive_inclusion_depth": self.primitive_inclusion_depth,
            "primitive_homotopy_depth": self.primitive_homotopy_depth,
            "product_cycle_exact": True,
            "coefficientwise_cone_identity_exact": True,
            "strict_alternate_character_exact": True,
        }


@dataclass(frozen=True, slots=True)
class ConeMatterLift:
    """One strict I6 class with both exact first-constituent corrections."""

    character: Character
    local_family_index: int
    seed_index: int
    full_cochain: SparseOuterCechCochain
    coefficients: tuple[ConeCoefficient, ConeCoefficient]

    def as_record(self) -> dict[str, object]:
        """Serialize the universal parameter-linear lift certificate."""

        return {
            "character": list(self.character),
            "local_family_index": self.local_family_index,
            "seed_index": self.seed_index,
            "i6_digest": _cochain_digest((self.full_cochain,)),
            "parameter_coefficients": [item.as_record() for item in self.coefficients],
        }


@dataclass(frozen=True, slots=True)
class AlternateUpConeMatterLifts:
    """All six exact up-sector classes on the determinant-repaired cone."""

    first_classes: tuple[FirstMatterClass, FirstMatterClass]
    second_lifts: tuple[ConeMatterLift, ...]
    carrier_digest: str
    constituent_digest: str
    cone_digest: str
    invariant_digest: str
    common_twist: Character

    def as_record(self) -> dict[str, object]:
        """Return one content-addressable exact matter-lift record."""

        if len(self.second_lifts) != 4:
            raise ValueError("four second-constituent lifts are required")
        if [item.character for item in self.first_classes] != list(TARGETS):
            raise ValueError("the first-constituent sectors are incomplete")
        if [item.character for item in self.second_lifts] != [
            TARGETS[0], TARGETS[0], TARGETS[1], TARGETS[1],
        ]:
            raise ValueError("the second-constituent sectors are incomplete")
        return {
            "schema": "alternate-constituent-up-cone-matter-lifts-v1",
            "coefficient_field": "Q(omega)",
            "carrier_parameter_basis": ["a0", "a1"],
            "carrier_locus": "P^1(Q(omega)) x K^s",
            "common_flat_twist": list(self.common_twist),
            "pre_twist_character_sectors": [list(item) for item in TARGETS],
            "prerequisite_artifact_digests": {
                "frozen_carrier": self.carrier_digest,
                "strict_i6_matter": self.constituent_digest,
                "universal_cone": self.cone_digest,
                "invariant_outer_basis": self.invariant_digest,
            },
            "first_constituent_constant_classes": [
                item.as_record() for item in self.first_classes
            ],
            "second_constituent_parameter_linear_lifts": [
                item.as_record() for item in self.second_lifts
            ],
            "universal_visible_family_dimension_per_character": 3,
            "all_coefficientwise_cone_identities_exact": True,
            "all_lifts_strict_in_declared_characters": True,
            "arbitrary_extension_point_selected": False,
            "higgs_cocycle_computed": False,
            "holomorphic_yukawa_matrix_computed": False,
            "next_required_object": (
                "construct the physical up-Higgs cocycle in the same cone "
                "and evaluate all nine common-DGA Yukawa entries"
            ),
        }


def _first_representatives() -> tuple[FirstMatterClass, FirstMatterClass]:
    """Recover only the two needed first-factor sectors in atlas frames."""

    first = mixed_schoen_constituents()[0]
    unit = mixed_schoen_unit()
    transferred = mixed_transferred_outer_hom(first, unit)
    differentials = dict(transferred.differentials)
    incoming, outgoing = differentials[0], differentials[1]
    if not transferred.squared_zero or transferred.cohomology_dimension(1) != 9:
        raise ValueError("the unchanged I3 matter complex changed")
    cycles = outgoing.kernel_inclusion()
    selected = _cohomology_complement_columns(incoming, cycles)
    representatives = _select_columns(cycles, selected, "alternate:up:first-matter")
    seeds = tuple(_columns(representatives))
    boundaries = _independent_columns(incoming)
    if len(seeds) != 9 or len(boundaries) != incoming.rank():
        raise ValueError("the I3 matter cohomology basis changed")
    solver = _SparseSpanSolver(boundaries + seeds)
    contraction = _MixedContraction(first, unit)
    entries = _reduced_basis(contraction.left_skeleton, contraction.right_skeleton, 1)
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    frames = {
        name: (_common_frame(first, action), Matrix.identity(1, scalar_type=Eisenstein))
        for name, action in actions.items()
    }
    found: dict[Character, FirstMatterClass] = {}
    for seed_index, coefficients in enumerate(seeds):
        full, _depth = _perturbed_inclusion(
            _reduced_cochain(entries, coefficients), contraction
        )
        if not contraction.differential(full).is_zero():
            raise ValueError("an I3 matter seed is not closed")
        for character in TARGETS:
            projected = _project(full, character, contraction, actions, frames)
            if projected.is_zero():
                continue
            if not contraction.differential(projected).is_zero():
                raise ValueError("an I3 character projection is not closed")
            if not _strict(projected, character, contraction, actions, frames):
                raise ValueError("an I3 character projection is not strict")
            reduced, _depth = _perturbed_projection(projected, contraction, 1)
            coordinates = solver.coordinates(reduced)
            cohomology = tuple(
                coordinates.get(len(boundaries) + index, Eisenstein(0))
                for index in range(9)
            )
            if all(value.is_zero() for value in cohomology):
                continue
            candidate = FirstMatterClass(character, seed_index, cohomology, projected)
            previous = found.get(character)
            if previous is not None and cohomology != previous.cohomology_coordinates:
                scale = next(
                    left / right
                    for left, right in zip(
                        cohomology, previous.cohomology_coordinates, strict=True
                    )
                    if not right.is_zero()
                )
                if any(
                    left != scale * right
                    for left, right in zip(
                        cohomology, previous.cohomology_coordinates, strict=True
                    )
                ):
                    raise ValueError("an I3 target character has multiplicity above one")
            elif previous is None:
                found[character] = candidate
    if set(found) != set(TARGETS):
        raise ValueError("the I3 target character sectors are incomplete")
    return cast(tuple[FirstMatterClass, FirstMatterClass], tuple(found[item] for item in TARGETS))


def _coefficient(
    parameter: str,
    matter: AlternateMatterClass,
    extension: SparseOuterCechCochain,
    contraction: _MixedContraction,
    transferred: MixedTransferredOuterHom,
) -> ConeCoefficient:
    """Solve one full-complex parameter coefficient with exact character."""

    product = mixed_outer_cup(extension, matter.full_cochain)
    if not contraction.differential(product).is_zero():
        raise ValueError("an outer-matter product is not a full cycle")
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    frames = {
        name: (
            _common_frame(contraction.left, action),
            Matrix.identity(1, scalar_type=Eisenstein),
        )
        for name, action in actions.items()
    }
    if not _strict(product, matter.character, contraction, actions, frames):
        raise ValueError("the outer-matter product lost its atlas character")
    primitive = exact_mixed_primitive(product, contraction, transferred, 2)
    correction = _project(
        primitive.primitive, matter.character, contraction, actions, frames
    ).scale(-1)
    if not (contraction.differential(correction) + product).is_zero():
        raise ValueError("the parameter-linear cone correction identity failed")
    if not _strict(correction, matter.character, contraction, actions, frames):
        raise ValueError("the cone correction lost its atlas character")
    return ConeCoefficient(
        parameter,
        len(product.terms),
        _cochain_digest((product,)),
        correction,
        primitive.projection_depth,
        primitive.inclusion_depth,
        primitive.homotopy_depth,
    )


def _coefficient_job(
    job: tuple[int, int, int, AlternateMatterClass, SparseOuterCechCochain],
) -> tuple[int, int, int, ConeCoefficient]:
    """Compute one independently checked universal coefficient in a worker."""

    character_index, local_index, parameter_index, matter, extension = job
    first = mixed_schoen_constituents()[0]
    unit = mixed_schoen_unit()
    coefficient = _coefficient(
        f"a{parameter_index}",
        matter,
        extension,
        _MixedContraction(first, unit),
        mixed_transferred_outer_hom(first, unit),
    )
    return character_index, local_index, parameter_index, coefficient


@cache
def alternate_up_cone_matter_lifts() -> AlternateUpConeMatterLifts:
    """Construct all six strict up-sector classes on the universal cone."""

    constituent_digest, constituent_payload = _verified_payload(UP_MATTER)
    cone_digest, cone = _verified_payload(CONE)
    invariant_digest, invariant = _verified_payload(INVARIANTS)
    carrier_digest, carrier = _verified_payload(CARRIER)
    strict = alternate_constituent_up_matter_representatives()
    if (
        constituent_payload.get("schema")
        != "alternate-constituent-up-matter-representatives-v1"
        or strict.as_record() != constituent_payload
        or cone.get("schema") != "alternate-constituent-outer-universal-cone-v1"
        or cone.get("invariant_artifact_digest") != invariant_digest
        or invariant.get("schema") != "alternate-constituent-outer-invariants-v1"
        or invariant.get("invariant_ext1_dimension") != 2
        or carrier.get("schema") != "alternate-constituent-carrier-state-v1"
    ):
        raise ValueError("the alternate universal matter-lift premises changed")
    raw = invariant.get("strict_full_cech_representatives")
    if not isinstance(raw, list) or len(raw) != 2:
        raise ValueError("the alternate invariant extension basis is missing")
    extensions = tuple(_representative(item) for item in raw)
    first = mixed_schoen_constituents()[0]
    transferred = mixed_transferred_outer_hom(first, mixed_schoen_unit())
    if transferred.cohomology_dimension(2) != 0:
        raise ValueError("the I3 matter H2 obstruction space is nonzero")
    first_classes = _first_representatives()
    jobs = []
    by_sector: dict[Character, list[AlternateMatterClass]] = {}
    for character_index, character in enumerate(TARGETS):
        selected = [item for item in strict.classes if item.character == character]
        if len(selected) != 2:
            raise ValueError("the strict I6 sector count changed")
        by_sector[character] = selected
        for local_index, matter in enumerate(selected, start=1):
            jobs.extend(
                (character_index, local_index, parameter_index, matter, extension)
                for parameter_index, extension in enumerate(extensions)
            )
    with ProcessPoolExecutor(max_workers=4) as pool:
        completed = tuple(pool.map(_coefficient_job, jobs))
    coefficient_map = {
        (character_index, local_index, parameter_index): coefficient
        for character_index, local_index, parameter_index, coefficient in completed
    }
    if len(coefficient_map) != 8:
        raise ValueError("the eight universal matter coefficients are incomplete")
    lifts = []
    for character_index, character in enumerate(TARGETS):
        for local_index, matter in enumerate(by_sector[character], start=1):
            coefficients = (
                coefficient_map[(character_index, local_index, 0)],
                coefficient_map[(character_index, local_index, 1)],
            )
            lifts.append(ConeMatterLift(
                character, local_index, matter.seed_index, matter.full_cochain,
                coefficients,
            ))
    return AlternateUpConeMatterLifts(
        first_classes,
        tuple(lifts),
        carrier_digest,
        constituent_digest,
        cone_digest,
        invariant_digest,
        strict.common_twist,
    )


def write_alternate_up_cone_matter_lifts(path: Path = OUTPUT) -> dict[str, object]:
    """Write one content-addressed all-parameter up-matter certificate."""

    payload = alternate_up_cone_matter_lifts().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_up_cone_matter_lifts()
    print(f"artifact_digest: {report['artifact_digest']}")
    count = len(report["second_constituent_parameter_linear_lifts"])
    print(f"parameter_linear_lift_count: {count}")
