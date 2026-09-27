"""Apply alternate rank-two quotient duality to the actual Hom overlap.

Owns:
    Exact minor-open quotient numerators and hypersurface residuals for
    the gauge-corrected up-Higgs Hom fiber-overlap class.

Depends on:
    The certified alternate duality inverse, saved fiber transport,
    selected relation matrix, and exact Laurent arithmetic.

Must not:
    Infer global minor-open gluing, an exterior-cone Higgs cocycle, or
    a physical or holomorphic Yukawa coefficient from a local image.

Phase 0:
    Research-only local tensor-conversion input.
"""

from __future__ import annotations

import json
from pathlib import Path

from onetheory.math.numbers import OMEGA
from onetheory.math.sheaves import LaurentPolynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pencil import tier_a_pencil_model

from .alternate_constituent_duality_local_inverse import OUTPUT as LOCAL_INVERSE
from .alternate_constituent_duality_local_inverse import (
    inverse_numerator,
    local_dual_contraction,
)
from .alternate_up_higgs_fiber_overlap_transport import OUTPUT as FIBER_TRANSPORT
from .alternate_up_higgs_fiber_overlap_transport import _vector
from .alternate_up_higgs_local_syzygy_section import _multiply_vector, _vector_record
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_schoen_determinant_pairing import _transpose, plucker_pairing
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions
from .published_constituent_overlap_transitions import (
    _hypersurface_equation,
    _relation_columns,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_higgs_quotient_overlap_image.json"


def alternate_up_higgs_quotient_overlap_image() -> dict[str, object]:
    """Convert the actual corrected Hom overlap on one certified minor open."""

    fiber_digest, fiber = _verified_payload(FIBER_TRANSPORT)
    inverse_digest, inverse = _verified_payload(LOCAL_INVERSE)
    representative = fiber.get("fiber_overlap_representative", {})
    if (
        fiber.get("schema") != "alternate-up-higgs-fiber-overlap-transport-v1"
        or fiber.get("all_corrected_koszul_divisibility_exact") is not True
        or representative.get("base_pivots_checked") != [0, 1, 2]
        or inverse.get("schema") != "alternate-constituent-duality-local-inverse-v1"
        or inverse.get("combined_local_hom_to_quotient_identity_exact") is not True
    ):
        raise ValueError("the actual Hom quotient input is not certified")
    middle = _vector(representative["corrected_middle_numerator_object_order"], 5)
    koszul = _vector(representative["koszul_residual_numerator"], 3)
    relation_order = (-middle[1], -middle[2], -middle[3], -middle[4], middle[0])
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    equation = _hypersurface_equation(ray)
    chart_results = []
    reference: tuple[
        LaurentPolynomial,
        tuple[LaurentPolynomial, ...],
        tuple[LaurentPolynomial, ...],
    ] | None = None
    for chart in tier_a_pencil_model().blowup_atlas.charts:
        if chart.fiber_chart != "nu":
            continue
        relation = _relation_columns(ray, chart)
        pairing = plucker_pairing(relation)
        numerator_map = inverse_numerator(0, 1)
        contraction = local_dual_contraction(relation, 0, 1)
        delta = pairing.rows[0][1]
        denominator = contraction.denominator
        if delta.is_zero() or denominator != delta:
            raise ValueError("the selected quotient minor and retract disagree")
        source_residual = _multiply_vector(_transpose(relation), relation_order)
        if source_residual != tuple(equation * entry for entry in koszul):
            raise ValueError("the corrected Hom overlap is not the declared quotient source")
        quotient_numerator = _multiply_vector(numerator_map, relation_order)
        pairing_image = _multiply_vector(pairing, quotient_numerator)
        residual = tuple(
            pairing_image[index] - delta * relation_order[index]
            for index in range(5)
        )
        section_koszul = _multiply_vector(contraction.section_numerator, koszul)
        koszul_pairing = _multiply_vector(
            pairing, _multiply_vector(numerator_map, section_koszul)
        )
        correction = tuple(
            koszul_pairing[index] - delta * section_koszul[index]
            for index in range(5)
        )
        if tuple(denominator * entry for entry in residual) != tuple(
            equation * entry for entry in correction
        ):
            raise ValueError("the actual Hom quotient image failed exact localization")
        if not any(not item.is_zero() for item in quotient_numerator):
            raise ValueError("the actual Hom quotient image vanished")
        formula = (delta, quotient_numerator, correction)
        if reference is None:
            reference = formula
        elif formula != reference:
            raise ValueError("the homogeneous quotient image differs across base charts")
        chart_results.append(chart.name)
    if chart_results != ["U_0_nu", "U_1_nu", "U_2_nu"] or reference is None:
        raise ValueError("the selected quotient image missed an alternate base chart")
    delta, quotient_numerator, correction = reference
    return {
        "schema": "alternate-up-higgs-quotient-overlap-image-v1",
        "coefficient_field": "Q(omega)",
        "prerequisite_artifact_digests": {
            "fiber_overlap_transport": fiber_digest,
            "minor_open_inverse": inverse_digest,
        },
        "target_charts_checked": chart_results,
        "minor_rows": [0, 1],
        "minor_denominator": _vector_record((delta,))[0],
        "quotient_numerator_relation_order": _vector_record(quotient_numerator),
        "hypersurface_correction_relation_order": _vector_record(correction),
        "quotient_nonzero_exact": True,
        "three_chart_formula_independence_exact": True,
        "cross_multiplied_quotient_identity_exact": True,
        "minor_open_gluing_constructed": False,
        "global_hom_to_tensor_chain_map_constructed": False,
        "exterior_cone_higgs_cocycle_constructed": False,
        "next_required_object": (
            "glue the localized quotient image across minor and base opens, "
            "then lift it through the exterior cone"
        ),
    }


def write_alternate_up_higgs_quotient_overlap_image(path: Path = OUTPUT) -> dict[str, object]:
    """Persist the exact local quotient image with unresolved global gates."""

    payload = alternate_up_higgs_quotient_overlap_image()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    result = write_alternate_up_higgs_quotient_overlap_image()
    print(f"artifact_digest: {result['artifact_digest']}")
    print(f"target_charts_checked: {result['target_charts_checked']}")
