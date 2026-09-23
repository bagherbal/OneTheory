"""Certify the reverse down-matrix support before scalar contraction.

Owns:
    Exterior-degree selection for the universal reverse matter/Higgs lifts and
    the independent exact tree-level zero witnesses for surviving off-diagonals.

Depends on:
    Content-addressed reverse lift certificates and the strict down-tree trace.

Must not:
    Assign the unresolved central Yukawa coefficient, select a P5 point, or
    interpret a support bound as a physical mass prediction.

Phase 0:
    Research-only scoped support certificate for the reverse down matrix.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .mixed_schoen_down_tree_matrix import OUTPUT as TREE_ARTIFACT
from .mixed_schoen_reverse_down_matter_lifts import FORWARD_MATTER_CHARACTERS
from .mixed_schoen_reverse_down_matter_lifts import OUTPUT as MATTER_ARTIFACT
from .mixed_schoen_reverse_higgs_lifts import OUTPUT as HIGGS_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_reverse_down_support.json"
)


@dataclass(frozen=True, slots=True)
class ExteriorTerm:
    """A constituent exterior bidegree with extension-parameter degree."""

    v1: int
    v2: int
    parameter_degree: int

    def __add__(self, other: ExteriorTerm) -> ExteriorTerm:
        """Tensor exterior components while retaining parameter degree."""

        return ExteriorTerm(
            self.v1 + other.v1,
            self.v2 + other.v2,
            self.parameter_degree + other.parameter_degree,
        )

    def survives(self) -> bool:
        """Test the rank-two exterior cutoffs of both constituents."""

        return self.v1 <= 2 and self.v2 <= 2


V1_QUOTIENT = (
    ExteriorTerm(1, 0, 0),
    ExteriorTerm(0, 1, 1),
)
V2_SUBOBJECT = (ExteriorTerm(0, 1, 0),)
DOWN_HIGGS = (
    ExteriorTerm(1, 1, 0),
    ExteriorTerm(0, 2, 1),
)
FAMILIES = (V1_QUOTIENT, V2_SUBOBJECT, V2_SUBOBJECT)


def surviving_degrees(row: int, column: int) -> tuple[int, ...]:
    """Enumerate all exterior-compatible parameter degrees for one slot."""

    if row not in range(3) or column not in range(3):
        raise ValueError("the reverse down family index must be zero, one, or two")
    degrees = {
        combined.parameter_degree
        for left, right, higgs in product(
            FAMILIES[row], FAMILIES[column], DOWN_HIGGS
        )
        if (combined := left + right + higgs).survives()
    }
    return tuple(sorted(degrees))


def _verified_payload(path: Path, schema: str) -> tuple[dict[str, object], str]:
    """Read a declared exact input only after its digest and schema agree."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid support prerequisite: {path.name}")
    digest = payload.pop("artifact_digest", None)
    if (
        not isinstance(digest, str)
        or digest != _canonical_digest(payload)
        or payload.get("schema") != schema
    ):
        raise ValueError(f"invalid support prerequisite: {path.name}")
    return payload, digest


def _certified_tree_zero_slots(tree: dict[str, object]) -> set[tuple[int, int]]:
    """Require exact boundary witnesses for every off-diagonal tree residue."""

    matrix = tree.get("down_tree_matrix")
    if not isinstance(matrix, dict) or matrix.get("exact") is not True:
        raise ValueError("the down-tree matrix is not certified")
    if matrix.get("family_basis") != ["V1", "V2:1", "V2:2"]:
        raise ValueError("the down-tree family basis changed")
    if (
        matrix.get("forward_row_matter_character_exponents")
        != list(FORWARD_MATTER_CHARACTERS[0])
        or matrix.get("forward_column_matter_character_exponents")
        != list(FORWARD_MATTER_CHARACTERS[1])
        or matrix.get("forward_higgs_character_exponents") != [0, 1]
    ):
        raise ValueError("the down-tree physical characters changed")
    records = matrix.get("entries")
    if not isinstance(records, list):
        raise ValueError("the down-tree entry certificate is absent")
    slots: set[tuple[int, int]] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("a down-tree entry is malformed")
        boundary = record.get("zero_boundary_witness")
        if (
            record.get("exact") is not True
            or record.get("value") != "0"
            or record.get("scalar_is_cycle") is not True
            or not isinstance(boundary, dict)
            or boundary.get("primitive_reconstruction_exact") is not True
        ):
            raise ValueError("an off-diagonal tree zero lacks a boundary proof")
        row, column = record.get("row"), record.get("column")
        if type(row) is not int or type(column) is not int:
            raise ValueError("an off-diagonal tree slot is malformed")
        slot = (row, column)
        if slot in slots:
            raise ValueError("a down-tree slot was certified twice")
        slots.add(slot)
    return slots


def reverse_down_support() -> dict[str, object]:
    """Certify eight zeros and isolate the unresolved parameter-linear entry."""

    matter, matter_digest = _verified_payload(
        MATTER_ARTIFACT, "mixed-schoen-reverse-down-matter-lifts-v1"
    )
    higgs, higgs_digest = _verified_payload(
        HIGGS_ARTIFACT, "mixed-schoen-reverse-higgs-lifts-v1"
    )
    tree, tree_digest = _verified_payload(
        TREE_ARTIFACT, "mixed-schoen-holomorphic-down-tree-matrix-v1"
    )
    if (
        matter.get("exact") is not True
        or matter.get("carrier_parameter_basis")
        != [f"b{index}" for index in range(6)]
        or matter.get("universal_visible_family_dimension_per_character") != 3
        or matter.get("all_coefficientwise_cone_identities_exact") is not True
        or higgs.get("all_coefficients_exact") is not True
        or len(higgs.get("parameter_coefficients", [])) != 6
        or tree.get("exact") is not True
    ):
        raise ValueError("the reverse support inputs are not exact")
    tree_zero_slots = _certified_tree_zero_slots(tree)
    expected_tree_slots = {(0, 1), (0, 2), (1, 0), (2, 0)}
    if tree_zero_slots != expected_tree_slots:
        raise ValueError("the tree-zero certificate does not cover all off-diagonals")
    support = {
        (row, column): surviving_degrees(row, column)
        for row in range(3)
        for column in range(3)
    }
    if support != {
        (0, 0): (1,),
        (0, 1): (0,),
        (0, 2): (0,),
        (1, 0): (0,),
        (2, 0): (0,),
        (1, 1): (),
        (1, 2): (),
        (2, 1): (),
        (2, 2): (),
    }:
        raise ValueError("the reverse exterior-degree support changed")
    return {
        "schema": "mixed-schoen-reverse-down-support-v1",
        "coefficient_field": "Q(omega)",
        "carrier_locus": "P^5(Q(omega)) x K_reverse^s",
        "family_basis": ["V1 quotient", "V2 subobject:1", "V2 subobject:2"],
        "constituent_ranks": [2, 2],
        "parameter_basis": [f"b{index}" for index in range(6)],
        "surviving_parameter_degrees_by_slot": [
            {
                "row": row,
                "column": column,
                "degrees": list(support[(row, column)]),
            }
            for row in range(3)
            for column in range(3)
        ],
        "exterior_forced_zero_slots": [
            [row, column]
            for (row, column), degrees in support.items()
            if not degrees
        ],
        "tree_boundary_zero_slots": [list(slot) for slot in sorted(tree_zero_slots)],
        "only_unresolved_slot": [0, 0],
        "unresolved_slot_parameter_degree": 1,
        "matrix_rank_upper_bound": 1,
        "central_coefficient_computed": False,
        "nontrivial_holomorphic_matrix_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "exact_support": True,
        "prerequisite_artifact_digests": {
            "reverse_matter": matter_digest,
            "reverse_higgs": higgs_digest,
            "strict_tree": tree_digest,
        },
        "next_required_object": (
            "six exact reverse central Yukawa coefficients from the common "
            "determinant contraction, including its comparison homotopy"
        ),
    }


def write_reverse_down_support(path: Path = OUTPUT) -> dict[str, object]:
    """Persist the exact scoped support certificate without matrix values."""

    payload = reverse_down_support()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    result = write_reverse_down_support()
    print(f"artifact_digest: {result['artifact_digest']}")
    print(f"next_required_object: {result['next_required_object']}")
