"""Glue actual alternate Hom quotient images across minor principal opens.

Owns:
    Exact relation witnesses and hypersurface corrections comparing all
    ten sparse Pluecker inverses of the saved Hom fiber-overlap class.

Depends on:
    The content-addressed local quotient image, corrected Hom overlap,
    alternate relation, and certified minor-open duality identities.

Must not:
    Infer a full tensor differential, an exterior Higgs cocycle, or a
    Yukawa matrix from scoped minor and base transition compatibility.

Phase 0:
    Research-only local quotient transition data.
"""

from __future__ import annotations

import json
from itertools import combinations
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
from .alternate_up_higgs_quotient_overlap_image import OUTPUT as QUOTIENT_IMAGE
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_schoen_determinant_pairing import _matrix_scale, _transpose, plucker_pairing
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions
from .published_constituent_overlap_transitions import (
    _atlas,
    _hypersurface_equation,
    _relation_columns,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_higgs_minor_overlap_gluing.json"


def _scale(
    vector: tuple[LaurentPolynomial, ...], scalar: LaurentPolynomial
) -> tuple[LaurentPolynomial, ...]:
    return tuple(scalar * entry for entry in vector)


def _subtract(
    left: tuple[LaurentPolynomial, ...],
    right: tuple[LaurentPolynomial, ...],
) -> tuple[LaurentPolynomial, ...]:
    if len(left) != len(right):
        raise ValueError("minor overlap vectors have different lengths")
    return tuple(a - b for a, b in zip(left, right, strict=True))


def alternate_up_higgs_minor_overlap_gluing() -> dict[str, object]:
    """Compare every actual quotient inverse to the selected minor frame."""

    fiber_digest, fiber = _verified_payload(FIBER_TRANSPORT)
    quotient_digest, quotient = _verified_payload(QUOTIENT_IMAGE)
    inverse_digest, inverse = _verified_payload(LOCAL_INVERSE)
    if (
        quotient.get("schema") != "alternate-up-higgs-quotient-overlap-image-v1"
        or quotient.get("prerequisite_artifact_digests", {}).get("fiber_overlap_transport")
        != fiber_digest
        or quotient.get("cross_multiplied_quotient_identity_exact") is not True
        or inverse.get("schema") != "alternate-constituent-duality-local-inverse-v1"
        or inverse.get("principal_open_count") != 60
    ):
        raise ValueError("the alternate minor-overlap inputs changed")
    record = fiber["fiber_overlap_representative"]
    middle = _vector(record["corrected_middle_numerator_object_order"], 5)
    koszul = _vector(record["koszul_residual_numerator"], 3)
    dual = (-middle[1], -middle[2], -middle[3], -middle[4], middle[0])
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    target_charts = tuple(
        chart for chart in tier_a_pencil_model().blowup_atlas.charts
        if chart.fiber_chart == "nu"
    )
    relations = tuple(_relation_columns(ray, chart) for chart in target_charts)
    if (
        len(relations) != 3
        or any(relation != relations[0] for relation in relations[1:])
    ):
        raise ValueError("the homogeneous alternate relation differs across base charts")
    relation = relations[0]
    atlas = _atlas(ray)
    base_transitions = tuple(
        transition for transition in atlas.transitions
        if transition.source.base_pivot != transition.target.base_pivot
        and transition.source.fiber_chart == transition.target.fiber_chart
    )
    if (
        len(base_transitions) != 12
        or any(
            not transition.transition.is_identity()
            or any(not entry.is_zero() for entry in transition.gauge)
            or any(not entry.is_zero() for entry in transition.hypersurface_homotopy)
            for transition in base_transitions
        )
    ):
        raise ValueError("the alternate base-chart quotient frames do not agree")
    pairing = plucker_pairing(relation)
    equation = _hypersurface_equation(ray)
    reference_pair = (0, 1)
    reference_minor = pairing.rows[0][1]
    reference_inverse = inverse_numerator(*reference_pair)
    reference_quotient = _multiply_vector(reference_inverse, dual)
    if _vector(quotient["quotient_numerator_relation_order"], 5) != reference_quotient:
        raise ValueError("the saved reference quotient image changed")
    contraction = local_dual_contraction(relation, *reference_pair)
    if contraction.denominator != reference_minor:
        raise ValueError("the reference minor has the wrong contraction sign")
    section = contraction.section_numerator
    section_koszul = _multiply_vector(section, koszul)
    if _multiply_vector(_transpose(relation), dual) != _scale(koszul, equation):
        raise ValueError("the actual Hom overlap has the wrong Koszul residual")
    pair_records = []
    for pair in combinations(range(5), 2):
        if pair == reference_pair:
            continue
        other_minor = pairing.rows[pair[0]][pair[1]]
        if other_minor.is_zero():
            raise ValueError("an alternate minor principal open vanished")
        other_inverse = inverse_numerator(*pair)
        if pairing.compose(other_inverse).compose(contraction.projection_numerator) != (
            _matrix_scale(contraction.projection_numerator, other_minor)
        ):
            raise ValueError("the alternate inverse fails the common kernel projector")
        other_quotient = _multiply_vector(other_inverse, dual)
        difference = _subtract(
            _scale(reference_quotient, other_minor),
            _scale(other_quotient, reference_minor),
        )
        relation_witness = _multiply_vector(_transpose(section), difference)
        residual = _subtract(
            _scale(difference, reference_minor),
            _multiply_vector(relation, relation_witness),
        )
        if residual != _multiply_vector(
            reference_inverse, _multiply_vector(pairing, difference)
        ):
            raise ValueError("the alternate relation projector identity failed")
        correction_source = _subtract(
            _scale(_multiply_vector(reference_inverse, section_koszul), other_minor),
            _scale(_multiply_vector(other_inverse, section_koszul), reference_minor),
        )
        hypersurface_correction = _multiply_vector(
            reference_inverse,
            _multiply_vector(pairing, correction_source),
        )
        if _scale(residual, reference_minor) != _scale(
            hypersurface_correction, equation
        ):
            raise ValueError("the actual minor-overlap quotient images do not glue")
        pair_records.append({
            "other_minor_rows": list(pair),
            "other_minor_digest": _canonical_digest(_vector_record((other_minor,))),
            "other_quotient_digest": _canonical_digest(_vector_record(other_quotient)),
            "relation_witness_digest": _canonical_digest(_vector_record(relation_witness)),
            "hypersurface_correction_digest": _canonical_digest(
                _vector_record(hypersurface_correction)
            ),
            "other_quotient_term_counts": [len(item.terms) for item in other_quotient],
            "relation_witness_term_counts": [len(item.terms) for item in relation_witness],
            "hypersurface_correction_term_counts": [
                len(item.terms) for item in hypersurface_correction
            ],
            "projector_identity_exact": True,
            "common_kernel_inverse_identity_exact": True,
            "cross_multiplied_gluing_exact": True,
        })
    if len(pair_records) != 9:
        raise ValueError("the reference minor did not cover the other nine opens")
    return {
        "schema": "alternate-up-higgs-minor-overlap-gluing-v1",
        "coefficient_field": "Q(omega)",
        "prerequisite_artifact_digests": {
            "fiber_overlap_transport": fiber_digest,
            "reference_quotient_image": quotient_digest,
            "minor_open_inverse": inverse_digest,
        },
        "reference_minor_rows": list(reference_pair),
        "target_charts_checked": [chart.name for chart in target_charts],
        "homogeneous_relation_equal_on_target_charts": True,
        "base_chart_transitions_checked": len(base_transitions),
        "base_chart_transitions_identity_exact": True,
        "fiber_overlap_base_cover_compatibility_exact": True,
        "other_minor_records": pair_records,
        "all_ten_minor_images_compatible_on_common_opens": True,
        "global_hom_to_tensor_chain_map_constructed": False,
        "exterior_cone_higgs_cocycle_constructed": False,
        "next_required_object": (
            "construct the full Cech-Koszul Hom-to-tensor chain map from "
            "these compatible local images, then lift into the exterior cone"
        ),
    }


def write_alternate_up_higgs_minor_overlap_gluing(path: Path = OUTPUT) -> dict[str, object]:
    """Persist exact relation witnesses without claiming global gluing."""

    payload = alternate_up_higgs_minor_overlap_gluing()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    result = write_alternate_up_higgs_minor_overlap_gluing()
    print(f"artifact_digest: {result['artifact_digest']}")
    print(f"other_minors: {len(result['other_minor_records'])}")
