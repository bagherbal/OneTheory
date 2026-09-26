"""Derive extension-parameter support of the alternate up Yukawa matrix.

Owns:
    Exterior-filtration support and the resulting determinant degree on the
    frozen one-plus-two family bases, without evaluating a coupling.

Depends on:
    The exact alternate matter lifts, acyclic determinant endpoints, and
    frozen two-parameter outer cone.

Must not:
    Invent Yukawa coefficients, infer nonzero entries from allowed support,
    choose an extension point, or call a Hom class a Higgs cocycle.

Phase 0:
    Research-only structural rank test preceding the chain contraction.
"""

from __future__ import annotations

import json
from itertools import permutations, product
from pathlib import Path
from typing import cast

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .alternate_constituent_outer_universal_cone import OUTPUT as CONE
from .alternate_constituent_structural_spectrum import OUTPUT as SPECTRUM
from .alternate_constituent_up_cone_matter_lifts import OUTPUT as MATTER
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_yukawa_support.json"

type Weight = tuple[int, int, int]  # E degree, F degree, outer-parameter degree.
E_MATTER: frozenset[Weight] = frozenset({(1, 0, 0)})
F_MATTER: frozenset[Weight] = frozenset({(0, 1, 0), (1, 0, 1)})
HIGGS: frozenset[Weight] = frozenset({(1, 1, 0), (2, 0, 1)})


def _allowed_degrees(left: str, right: str) -> tuple[int, ...]:
    """Retain only terms with two E and two F exterior factors."""

    matter = {"E": E_MATTER, "F": F_MATTER}
    return tuple(sorted({
        left_weight[2] + right_weight[2] + higgs_weight[2]
        for left_weight, right_weight, higgs_weight in product(
            matter[left], matter[right], HIGGS
        )
        if (
            left_weight[0] + right_weight[0] + higgs_weight[0] == 2
            and left_weight[1] + right_weight[1] + higgs_weight[1] == 2
        )
    }))


def alternate_up_yukawa_support() -> dict[str, object]:
    """Prove the block support and linear determinant, not its nonvanishing."""

    cone_digest, cone = _verified_payload(CONE)
    matter_digest, matter = _verified_payload(MATTER)
    spectrum_digest, spectrum = _verified_payload(SPECTRUM)
    inputs = cast(dict[str, object], matter["prerequisite_artifact_digests"])
    spectrum_inputs = cast(dict[str, object], spectrum["prerequisite_artifact_digests"])
    if (
        cone.get("schema") != "alternate-constituent-outer-universal-cone-v1"
        or cone.get("parameters") != ["a0", "a1"]
        or matter.get("schema") != "alternate-constituent-up-cone-matter-lifts-v1"
        or inputs.get("universal_cone") != cone_digest
        or matter.get("universal_visible_family_dimension_per_character") != 3
        or matter.get("all_coefficientwise_cone_identities_exact") is not True
        or len(cast(list[object], matter["first_constituent_constant_classes"])) != 2
        or len(cast(list[object], matter["second_constituent_parameter_linear_lifts"])) != 4
        or spectrum.get("schema") != "alternate-constituent-structural-spectrum-v1"
        or spectrum_inputs.get("alternate_cone") != cone_digest
        or spectrum.get("determinant_endpoints_acyclic") is not True
        or spectrum.get("higgs_h1_equivariantly_identified_with_constituent_tensor")
        is not True
    ):
        raise ValueError("the alternate Yukawa support premises changed")

    rows = ("E", "F", "F")
    columns = ("E", "F", "F")
    degrees = tuple(
        tuple(_allowed_degrees(row, column) for column in columns)
        for row in rows
    )
    expected = (
        ((), (0,), (0,)),
        ((0,), (1,), (1,)),
        ((0,), (1,), (1,)),
    )
    if degrees != expected:
        raise ValueError("the exterior-filtration up-matrix support changed")
    determinant_degrees = tuple(sorted({
        sum(choice)
        for assignment in permutations(range(3))
        if all(degrees[row][assignment[row]] for row in range(3))
        for choice in product(*(degrees[row][assignment[row]] for row in range(3)))
    }))
    if determinant_degrees != (1,):
        raise ValueError("the universal up determinant is not homogeneous linear")

    return {
        "schema": "alternate-up-yukawa-support-v1",
        "carrier_parameter_basis": ["a0", "a1"],
        "row_and_column_filtration": list(rows),
        "entry_parameter_degrees": [
            [list(entry) for entry in row] for row in degrees
        ],
        "determinant_parameter_degrees_if_nonzero": list(determinant_degrees),
        "determinant_form": "a0*lambda0 + a1*lambda1",
        "lambda_coefficients_computed": False,
        "rank_three_established": False,
        "exact_exterior_support": True,
        "prerequisite_artifact_digests": {
            "universal_cone": cone_digest,
            "strict_matter_lifts": matter_digest,
            "structural_spectrum": spectrum_digest,
        },
        "higgs_chain_cocycle_constructed": False,
        "yukawa_matrix_computed": False,
        "next_required_object": (
            "construct the same-cone Higgs chain class and evaluate the two "
            "determinant coefficients, then all allowed matrix entries"
        ),
    }


def write_alternate_up_yukawa_support(path: Path = OUTPUT) -> dict[str, object]:
    """Write the exact support theorem with pinned prerequisite digests."""

    payload = alternate_up_yukawa_support()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    record = write_alternate_up_yukawa_support()
    print(f"artifact_digest: {record['artifact_digest']}")
    print(f"entry_parameter_degrees: {record['entry_parameter_degrees']}")
