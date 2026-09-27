"""Regress principal-open compatibility of the actual Hom quotient image.

Owns:
    Exact saved relation witnesses and hypersurface corrections for all
    nine comparisons against the reference Pluecker minor.

Depends on:
    The corrected Hom overlap, alternate quotient relation, and exact
    localized Laurent arithmetic.

Must not:
    Infer a full tensor or exterior-cone Higgs differential from these
    minor and base transition comparisons.

Phase 0:
    Research checks for the next actual chain-map input.
"""

import json

from onetheory.math.numbers import OMEGA
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pencil import tier_a_pencil_model
from research.experiments.scientific_genesis.alternate_constituent_duality_local_inverse import (
    inverse_numerator,
    local_dual_contraction,
)
from research.experiments.scientific_genesis.alternate_up_higgs_fiber_overlap_transport import (
    OUTPUT as FIBER_OUTPUT,
)
from research.experiments.scientific_genesis.alternate_up_higgs_fiber_overlap_transport import (
    _vector,
)
from research.experiments.scientific_genesis.alternate_up_higgs_local_syzygy_section import (
    _multiply_vector,
    _vector_record,
)
from research.experiments.scientific_genesis.alternate_up_higgs_minor_overlap_gluing import (
    OUTPUT,
    _scale,
    _subtract,
    alternate_up_higgs_minor_overlap_gluing,
)
from research.experiments.scientific_genesis.distinct_constituent_ray_screen import (
    lift_joint_character_ray,
)
from research.experiments.scientific_genesis.mixed_schoen_determinant_pairing import (
    _transpose,
    plucker_pairing,
)
from research.experiments.scientific_genesis.published_constituent_deck_actions import (
    published_constituent_deck_actions,
)
from research.experiments.scientific_genesis.published_constituent_overlap_transitions import (
    _atlas,
    _hypersurface_equation,
    _relation_columns,
)


def test_all_saved_minor_overlap_witnesses_close() -> None:
    """Each alternate quotient image differs by a relation modulo F."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert payload["reference_minor_rows"] == [0, 1]
    assert payload["target_charts_checked"] == ["U_0_nu", "U_1_nu", "U_2_nu"]
    assert payload["base_chart_transitions_checked"] == 12
    assert payload["base_chart_transitions_identity_exact"] is True
    records = payload["other_minor_records"]
    assert len(records) == 9
    assert len({tuple(record["other_minor_rows"]) for record in records}) == 9
    fiber = json.loads(FIBER_OUTPUT.read_text(encoding="utf-8"))
    middle = _vector(
        fiber["fiber_overlap_representative"]["corrected_middle_numerator_object_order"],
        5,
    )
    koszul = _vector(
        fiber["fiber_overlap_representative"]["koszul_residual_numerator"], 3
    )
    dual = (-middle[1], -middle[2], -middle[3], -middle[4], middle[0])
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    atlas = _atlas(ray)
    base_transitions = tuple(
        transition for transition in atlas.transitions
        if transition.source.base_pivot != transition.target.base_pivot
        and transition.source.fiber_chart == transition.target.fiber_chart
    )
    assert len(base_transitions) == 12
    assert all(transition.transition.is_identity() for transition in base_transitions)
    assert all(
        all(not item.terms for item in transition.gauge)
        and all(not item.terms for item in transition.hypersurface_homotopy)
        for transition in base_transitions
    )
    chart = next(
        chart for chart in tier_a_pencil_model().blowup_atlas.charts
        if chart.name == "U_0_nu"
    )
    relation = _relation_columns(ray, chart)
    pairing = plucker_pairing(relation)
    equation = _hypersurface_equation(ray)
    minor = pairing.rows[0][1]
    inverse = inverse_numerator(0, 1)
    quotient = _multiply_vector(inverse, dual)
    section = local_dual_contraction(relation, 0, 1).section_numerator
    section_koszul = _multiply_vector(section, koszul)
    for record in records:
        assert record["common_kernel_inverse_identity_exact"] is True
        first, second = record["other_minor_rows"]
        other_minor = pairing.rows[first][second]
        other_inverse = inverse_numerator(first, second)
        other_quotient = _multiply_vector(other_inverse, dual)
        difference = _subtract(
            _scale(quotient, other_minor), _scale(other_quotient, minor)
        )
        witness = _multiply_vector(_transpose(section), difference)
        residual = _subtract(
            _scale(difference, minor), _multiply_vector(relation, witness)
        )
        correction_source = _subtract(
            _scale(_multiply_vector(inverse, section_koszul), other_minor),
            _scale(_multiply_vector(other_inverse, section_koszul), minor),
        )
        correction = _multiply_vector(
            inverse, _multiply_vector(pairing, correction_source)
        )
        assert record["other_minor_digest"] == _canonical_digest(
            _vector_record((other_minor,))
        )
        assert record["other_quotient_digest"] == _canonical_digest(
            _vector_record(other_quotient)
        )
        assert record["relation_witness_digest"] == _canonical_digest(
            _vector_record(witness)
        )
        assert record["hypersurface_correction_digest"] == _canonical_digest(
            _vector_record(correction)
        )
        assert record["other_quotient_term_counts"] == [
            len(item.terms) for item in other_quotient
        ]
        assert record["relation_witness_term_counts"] == [
            len(item.terms) for item in witness
        ]
        assert record["hypersurface_correction_term_counts"] == [
            len(item.terms) for item in correction
        ]
        assert _scale(residual, minor) == _scale(correction, equation)
        assert residual == _multiply_vector(inverse, _multiply_vector(pairing, difference))
        wrong = _subtract(
            _scale(difference, minor), _multiply_vector(relation, tuple(-x for x in witness))
        )
        assert _scale(wrong, minor) != _scale(correction, equation)


def test_minor_gluing_stops_before_base_cover() -> None:
    """Principal-open compatibility does not imply a global Higgs class."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    payload.pop("artifact_digest")
    assert payload == alternate_up_higgs_minor_overlap_gluing()
    assert payload["all_ten_minor_images_compatible_on_common_opens"] is True
    assert payload["fiber_overlap_base_cover_compatibility_exact"] is True
    assert payload["global_hom_to_tensor_chain_map_constructed"] is False
    assert payload["exterior_cone_higgs_cocycle_constructed"] is False
