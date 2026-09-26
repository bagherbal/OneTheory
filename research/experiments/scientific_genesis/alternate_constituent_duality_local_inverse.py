"""Invert the alternate rank-two quotient pairing on minor principal opens.

Owns:
    Exact numerator/denominator data for the inverse of the Pluecker map
    from the quotient to its determinant-twisted dual.

Depends on:
    The frozen alternate presentation, its local-freeness certificate, and
    the six-chart determinant-pairing overlap audit.

Must not:
    Divide by a minor outside its principal open, identify a local inverse
    with the full Cech--Koszul map, or claim a cone Higgs cocycle.

Phase 0:
    Research-only local chain inverse for the up-Higgs Hom route.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA, Eisenstein
from onetheory.math.sheaves import LaurentMatrix, LaurentPolynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pencil import tier_a_pencil_model

from .alternate_constituent_determinant_pairing import OUTPUT as PAIRING
from .alternate_constituent_up_matter_representatives import CARRIER
from .alternate_up_higgs_hom_representative import OUTPUT as HOM_CLASS
from .distinct_constituent_ray_screen import OUTPUT as SCREEN
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_schoen_determinant_pairing import (
    _is_zero,
    _matrix_difference,
    _matrix_scale,
    _transpose,
    plucker_pairing,
)
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions
from .published_constituent_overlap_transitions import (
    _determinant,
    _hypersurface_equation,
    _relation_columns,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_constituent_duality_local_inverse.json"


def inverse_numerator(first: int, second: int) -> LaurentMatrix:
    """Return S with S[first,second]=-1 and S[second,first]=1."""

    if not 0 <= first < second < 5:
        raise ValueError("a rank-two principal open needs two ordered middle rows")
    zero = LaurentPolynomial.zero(5, scalar_type=Eisenstein)
    one = LaurentPolynomial.one(5, scalar_type=Eisenstein)
    return LaurentMatrix(tuple(
        tuple(
            -one if (row, column) == (first, second)
            else one if (row, column) == (second, first)
            else zero
            for column in range(5)
        )
        for row in range(5)
    ))


def principal_open_inverse_identity(
    pairing: LaurentMatrix, first: int, second: int
) -> bool:
    """Check J S J = J[first,second] J without any division."""

    if pairing.shape != (5, 5):
        raise ValueError("the alternate quotient pairing must be five by five")
    numerator = inverse_numerator(first, second)
    minor = pairing.rows[first][second]
    if not minor.terms:
        raise ValueError("a zero minor has no principal-open inverse")
    for row in range(5):
        for column in range(5):
            left = (
                pairing.rows[row][first]
                * numerator.rows[first][second]
                * pairing.rows[second][column]
                + pairing.rows[row][second]
                * numerator.rows[second][first]
                * pairing.rows[first][column]
            )
            if left != minor * pairing.rows[row][column]:
                return False
    return True


def _value(
    polynomial: LaurentPolynomial, coordinates: tuple[Eisenstein, ...]
) -> Eisenstein:
    """Evaluate an exact Laurent expression at nonzero declared coordinates."""

    return cast(
        Eisenstein,
        polynomial.substitute_monomials(
            tuple((coordinate, ()) for coordinate in coordinates)
        ).coefficient(()),
    )


def _adjugate_three(matrix: LaurentMatrix) -> LaurentMatrix:
    """Return the exact cofactor adjugate of a three-by-three matrix."""

    if matrix.shape != (3, 3):
        raise ValueError("the syzygy pivot block must be three by three")
    return LaurentMatrix(tuple(
        tuple(
            _determinant(LaurentMatrix(tuple(
                tuple(matrix.rows[row][column] for column in range(3) if column != i)
                for row in range(3) if row != j
            ))).scale(-1 if (i + j) % 2 else 1)
            for j in range(3)
        )
        for i in range(3)
    ))


@dataclass(frozen=True, slots=True)
class LocalDualContraction:
    """Numerators for the localized dual differential retract."""

    denominator: LaurentPolynomial
    section_numerator: LaurentMatrix
    projection_numerator: LaurentMatrix


def local_dual_contraction(
    relation: LaurentMatrix, first: int, second: int
) -> LocalDualContraction:
    """Split M* -> R* on the principal open of a complementary relation minor."""

    if relation.shape != (5, 3) or not 0 <= first < second < 5:
        raise ValueError("the alternate dual contraction needs a 5x3 relation")
    pivot_rows = tuple(row for row in range(5) if row not in {first, second})
    block = _transpose(LaurentMatrix(tuple(relation.rows[row] for row in pivot_rows)))
    denominator = _determinant(block)
    if not denominator.terms:
        raise ValueError("the selected relation minor vanishes")
    adjugate = _adjugate_three(block)
    zero = LaurentPolynomial.zero(5, scalar_type=Eisenstein)
    positions = {row: index for index, row in enumerate(pivot_rows)}
    section = LaurentMatrix(tuple(
        adjugate.rows[positions[row]] if row in positions else (zero, zero, zero)
        for row in range(5)
    ))
    dual_differential = _transpose(relation)
    identity_three = LaurentMatrix.identity(3, 5, scalar_type=Eisenstein)
    identity_five = LaurentMatrix.identity(5, 5, scalar_type=Eisenstein)
    projection = _matrix_difference(
        _matrix_scale(identity_five, denominator),
        section.compose(dual_differential),
    )
    if (
        section.shape != (5, 3)
        or projection.shape != (5, 5)
        or dual_differential.compose(section)
        != _matrix_scale(identity_three, denominator)
        or not _is_zero(dual_differential.compose(projection))
        or projection.compose(projection) != _matrix_scale(projection, denominator)
    ):
        raise ValueError("the alternate dual syzygy contraction failed")
    return LocalDualContraction(denominator, section, projection)


def alternate_constituent_duality_local_inverse() -> dict[str, object]:
    """Check every minor open of the frozen locally free alternate quotient."""

    carrier_digest, carrier = _verified_payload(CARRIER)
    pairing_digest, pairing_audit = _verified_payload(PAIRING)
    screen_digest, screen = _verified_payload(SCREEN)
    hom_digest, hom = _verified_payload(HOM_CLASS)
    state = cast(dict[str, object], carrier["computable_one_theory_carrier_state"])
    survivors = cast(list[dict[str, object]], screen["local_unit_survivors"])
    if (
        carrier.get("schema") != "alternate-constituent-carrier-state-v1"
        or state.get("component_id") != "alternate-i6-ray-0-1-P1"
        or state.get("frozen") is not True
        or pairing_audit.get("schema")
        != "alternate-constituent-determinant-pairing-v1"
        or pairing_audit.get("prerequisite_artifact_digests", {}).get("frozen_carrier")
        != carrier_digest
        or pairing_audit.get("corrected_overlap_covariance_exact") is not True
        or screen.get("schema") != "distinct-constituent-ray-screen-v1"
        or not any(
            item.get("scheme") == "I6"
            and item.get("character_exponents") == [0, 1]
            for item in survivors
        )
        or hom.get("schema") != "alternate-up-higgs-hom-representative-v1"
        or hom.get("full_cycle_exact") is not True
        or hom.get("strict_hom_character_exact") is not True
        or hom.get("nonboundary_exact") is not True
        or hom.get("higgs_tensor_chain_map_constructed") is not False
    ):
        raise ValueError("the local duality inverse premises changed")

    alternate = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    equation = _hypersurface_equation(alternate)
    base = (Eisenstein(1), Eisenstein(2), Eisenstein(3))
    first_coefficient = _value(equation, (*base, Eisenstein(1), Eisenstein(0)))
    second_coefficient = _value(equation, (*base, Eisenstein(0), Eisenstein(1)))
    fiber = (second_coefficient, -first_coefficient)
    witness = (*base, *fiber)
    if any(value.is_zero() for value in witness) or not _value(equation, witness).is_zero():
        raise ValueError("the common minor-open witness is not on the hypersurface")
    minors_per_chart: dict[str, list[list[int]]] = {}
    dual_contraction_count = 0
    for chart in tier_a_pencil_model().blowup_atlas.charts:
        relation = _relation_columns(alternate, chart)
        pairing = plucker_pairing(relation)
        if relation.shape != (5, 3) or pairing.shape != (5, 5):
            raise ValueError("the alternate quotient rank changed")
        if (
            not _is_zero(pairing.compose(relation))
            or not _is_zero(_transpose(relation).compose(pairing))
        ):
            raise ValueError("the local duality map fails a two-term chain identity")
        chart_minors = []
        for first, second in combinations(range(5), 2):
            if not pairing.rows[first][second].terms:
                continue
            if _value(pairing.rows[first][second], witness).is_zero():
                raise ValueError("a declared minor open lacks the exact common witness")
            if not principal_open_inverse_identity(pairing, first, second):
                raise ValueError("the rank-two local inverse identity failed")
            contraction = local_dual_contraction(relation, first, second)
            expected_denominator = pairing.rows[first][second].scale(
                -1 if (first + second + 1) % 2 else 1
            )
            if contraction.denominator != expected_denominator:
                raise ValueError("the dual retract and Pluecker frames disagree")
            if (
                pairing.compose(inverse_numerator(first, second))
                .compose(contraction.projection_numerator)
                != _matrix_scale(
                    contraction.projection_numerator,
                    pairing.rows[first][second],
                )
            ):
                raise ValueError("the combined local Hom-to-quotient map failed")
            dual_contraction_count += 1
            chart_minors.append([first, second])
        if not chart_minors:
            raise ValueError("no minor principal open survives on a chart")
        minors_per_chart[chart.name] = chart_minors
    if len(minors_per_chart) != pairing_audit.get("chart_count"):
        raise ValueError("the local inverse misses an alternate affine chart")

    return {
        "schema": "alternate-constituent-duality-local-inverse-v1",
        "coefficient_field": "Q(omega)",
        "ray_character_exponents": [0, 1],
        "map_direction": "F -> F^dual tensor det(F)",
        "local_inverse": "S_uv / J_uv on D(J_uv)",
        "principal_open_row_pairs": minors_per_chart,
        "principal_open_count": sum(map(len, minors_per_chart.values())),
        "dual_syzygy_contraction_count": dual_contraction_count,
        "common_hypersurface_witness_base": [str(value) for value in base],
        "common_hypersurface_witness_fiber": [str(value) for value in fiber],
        "all_principal_opens_nonempty_at_witness": True,
        "inverse_identity_exact": True,
        "two_term_chain_map_exact": True,
        "dual_syzygy_contraction_exact": True,
        "combined_local_hom_to_quotient_identity_exact": True,
        "quotient_local_freeness_prerequisite_verified": True,
        "corrected_overlap_covariance_prerequisite_verified": True,
        "prerequisite_artifact_digests": {
            "frozen_carrier": carrier_digest,
            "alternate_pairing": pairing_digest,
            "local_unit_screen": screen_digest,
            "strict_up_higgs_hom_class": hom_digest,
        },
        "hom_to_tensor_cech_koszul_map_constructed": False,
        "exterior_cone_higgs_cocycle_constructed": False,
        "yukawa_matrix_computed": False,
        "next_required_object": (
            "restrict the strict Hom cocycle to the minor-open cover, apply "
            "these local inverses, and solve the Cech--Koszul gluing homotopies"
        ),
    }


def write_alternate_constituent_duality_local_inverse(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the pinned local inverse data without a global Higgs claim."""

    payload = alternate_constituent_duality_local_inverse()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    record = write_alternate_constituent_duality_local_inverse()
    print(f"artifact_digest: {record['artifact_digest']}")
    print(f"principal_open_count: {record['principal_open_count']}")
