"""Evaluate the strict alternate up-Higgs Hom class on I6 matter cocycles.

Owns:
    Exact first leg of the mixed-family derived evaluation, from the
    certified Hom class and each strict I6 matter class to Hom(det V1,V1).

Depends on:
    The frozen alternate I6 ray, full strict cochains, determinant degree,
    and signed common-cover outer-Hom composition.

Must not:
    Call an evaluated Hom cochain a scalar Yukawa, omit the V1 determinant
    contraction, or claim a same-cone exterior-square Higgs cocycle.

Phase 0:
    Research-only first Yoneda product toward one holomorphic up matrix.
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
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    _independent_columns,
    _SparseSpanSolver,
)

from .alternate_constituent_determinant_descent import OUTPUT as DETERMINANT
from .alternate_constituent_up_matter_representatives import OUTPUT as MATTER
from .alternate_constituent_up_matter_representatives import (
    alternate_constituent_up_matter_representatives,
)
from .alternate_up_higgs_hom_representative import FULL_OUTPUT as HOM
from .alternate_up_higgs_hom_representative import (
    load_alternate_up_higgs_hom_full_cochain,
)
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
    _constituent,
    mixed_schoen_constituents,
)
from .mixed_outer_yoneda import compose_outer_cochains
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction, _perturbed_projection
from .mixed_schoen_outer_transfer import MixedSchoenUnit, _transfer_map
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_yoneda_evaluation.json"


@dataclass(frozen=True, slots=True)
class EvaluatedHomClass:
    """One exact H2(det V1,V1) cochain before determinant contraction."""

    character: tuple[int, int]
    seed_index: int
    full_cochain: SparseOuterCechCochain
    reduced_coordinates: tuple[tuple[int, Eisenstein], ...]
    nonboundary_exact: bool
    projection_depth: int

    def as_record(self) -> dict[str, object]:
        """Serialize the exact class test without inferring a scalar trace."""

        return {
            "matter_character": list(self.character),
            "matter_seed_index": self.seed_index,
            "evaluated_term_count": len(self.full_cochain.terms),
            "evaluated_digest": _cochain_digest((self.full_cochain,)),
            "reduced_coordinates": [
                [index, str(value)] for index, value in self.reduced_coordinates
            ],
            "reduced_nonboundary_exact": self.nonboundary_exact,
            "projection_depth": self.projection_depth,
        }


@cache
def alternate_up_yoneda_evaluation() -> tuple[EvaluatedHomClass, ...]:
    """Compose the actual strict Hom class with all four strict I6 classes."""

    first = mixed_schoen_constituents()[0]
    _, determinant_record = _verified_payload(DETERMINANT)
    cases = cast(list[dict[str, object]], determinant_record["cases"])
    matching = [case for case in cases if case["ray_character_exponents"] == [0, 1]]
    if (
        len(matching) != 1
        or matching[0]["constituent_cover_line_degrees"]
        != [[-2, 2, 0], [2, -2, 0]]
    ):
        raise ValueError("the alternate determinant line frame changed")
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    twisted_second = _constituent(ray, "I6-ray-0-1", 2, (-1, 1, 0))
    determinant = MixedSchoenUnit(
        "det V1", 0, (-2, 2, 0),
        (MixedConstituentObject("det V1", 0, (-2, 2, 0)),),
    )
    hom_context = _MixedContraction(first, twisted_second)
    matter_context = _MixedContraction(twisted_second, determinant)
    target_context = _MixedContraction(first, determinant)
    hom = load_alternate_up_higgs_hom_full_cochain()
    if not hom_context.differential(hom).is_zero():
        raise ValueError("the saved alternate Hom input ceased to be a cycle")
    classes = alternate_constituent_up_matter_representatives().classes
    incoming, _ = _transfer_map(first, determinant, 1)
    boundaries = _independent_columns(incoming)
    boundary_solver = _SparseSpanSolver(boundaries)
    result = []
    for item in classes:
        if not matter_context.differential(item.full_cochain).is_zero():
            raise ValueError("determinant twisting changed an I6 matter cycle")
        evaluated = compose_outer_cochains(
            hom, item.full_cochain, target_context.components,
            left_middle=hom_context.right,
            right_middle=matter_context.left,
        )
        if any(basis.total_degree != 2 for basis, _ in evaluated.terms):
            raise ValueError("the Hom evaluation has the wrong total degree")
        if not target_context.differential(evaluated).is_zero():
            raise ValueError("the signed Hom evaluation is not a full cycle")
        coordinates, depth = _perturbed_projection(evaluated, target_context, 2)
        try:
            boundary_solver.coordinates(coordinates)
            nonboundary = False
        except ValueError as error:
            if str(error) != "transferred deck image escaped the cycle span":
                raise
            nonboundary = True
        result.append(EvaluatedHomClass(
            item.character, item.seed_index, evaluated,
            tuple(sorted(coordinates.items())),
            nonboundary, depth,
        ))
    return tuple(result)


def _ratio(
    reference: EvaluatedHomClass, candidate: EvaluatedHomClass
) -> Eisenstein:
    """Return an exact proportionality scalar in the fixed reduced basis."""

    if reference.character != candidate.character or not reference.nonboundary_exact:
        raise ValueError("a mixed-pairing ratio needs nonzero same-character classes")
    first = dict(reference.reduced_coordinates)
    second = dict(candidate.reduced_coordinates)
    if not first or not second:
        raise ValueError("a mixed-pairing ratio has an empty reduced image")
    pivot = min(first)
    scalar = second.get(pivot, Eisenstein(0)) / first[pivot]
    if scalar.is_zero() or any(
        second.get(index, Eisenstein(0))
        != scalar * first.get(index, Eisenstein(0))
        for index in first.keys() | second.keys()
    ):
        raise ValueError("the evaluated classes are not exactly proportional")
    return scalar


def write_alternate_up_yoneda_evaluation(path: Path = OUTPUT) -> dict[str, object]:
    """Persist four exact first-leg Yoneda products with unresolved trace."""

    hom_digest, _ = _verified_payload(HOM)
    matter_digest, _ = _verified_payload(MATTER)
    determinant_digest, _ = _verified_payload(DETERMINANT)
    evaluations = alternate_up_yoneda_evaluation()
    grouped = {
        character: tuple(item for item in evaluations if item.character == character)
        for character in ((0, 0), (1, 0))
    }
    if any(len(group) != 2 or not all(item.nonboundary_exact for item in group)
           for group in grouped.values()):
        raise ValueError("the four strict Yoneda images did not survive in cohomology")
    ratios = [
        {
            "matter_character": list(character),
            "reference_seed_index": group[0].seed_index,
            "candidate_seed_index": group[1].seed_index,
            "candidate_over_reference": str(_ratio(group[0], group[1])),
        }
        for character, group in grouped.items()
    ]
    payload: dict[str, object] = {
        "schema": "alternate-up-yoneda-evaluation-v1",
        "coefficient_field": "Q(omega)",
        "ray_character_exponents": [0, 1],
        "source_hom_orientation": "Hom(V2 tensor det(V1), V1)",
        "target_hom_orientation": "Hom(det(V1), V1)",
        "prerequisite_artifact_digests": {
            "strict_hom_full_cochain": hom_digest,
            "strict_i6_matter": matter_digest,
            "determinant_line": determinant_digest,
        },
        "evaluations": [item.as_record() for item in evaluations],
        "all_full_cycles_exact": True,
        "all_nonboundary_exact": all(item.nonboundary_exact for item in evaluations),
        "basis_dependent_mixed_entry_ratios": ratios,
        "cohomological_ratios_exact": True,
        "same_cone_higgs_cocycle_constructed": False,
        "holomorphic_yukawa_entries_computed": False,
        "next_required_object": (
            "contract each H2(det V1,V1) class with the strict first-constituent "
            "H1 matter class using the actual determinant form, then compute "
            "the exact scalar residue"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    record = write_alternate_up_yoneda_evaluation()
    print(f"artifact_digest: {record['artifact_digest']}")
    print(f"all_nonboundary_exact: {record['all_nonboundary_exact']}")
