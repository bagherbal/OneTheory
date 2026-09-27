"""Regress the actual minor-open quotient image of the alternate Hom class.

Owns:
    Exact Pluecker numerator, hypersurface correction, and failure of a
    reversed inverse orientation on the saved fiber-overlap input.

Depends on:
    The corrected Hom overlap, alternate relation, and local duality map.

Must not:
    Identify a local quotient image with a global tensor or Higgs class.

Phase 0:
    Research integration checks for the next chain-map ingredient.
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
)
from research.experiments.scientific_genesis.alternate_up_higgs_quotient_overlap_image import (
    OUTPUT,
    alternate_up_higgs_quotient_overlap_image,
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
    _hypersurface_equation,
    _relation_columns,
)


def test_saved_quotient_image_has_exact_hypersurface_correction() -> None:
    """The actual corrected Hom numerator is locally Pluecker invertible."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    fiber = json.loads(FIBER_OUTPUT.read_text(encoding="utf-8"))
    record = fiber["fiber_overlap_representative"]
    middle = _vector(record["corrected_middle_numerator_object_order"], 5)
    koszul = _vector(record["koszul_residual_numerator"], 3)
    relation_order = (-middle[1], -middle[2], -middle[3], -middle[4], middle[0])
    quotient = _vector(payload["quotient_numerator_relation_order"], 5)
    correction = _vector(payload["hypersurface_correction_relation_order"], 5)
    minor = _vector([payload["minor_denominator"]], 1)[0]
    assert [len(entry.terms) for entry in quotient] == [24, 24, 0, 0, 0]
    assert [len(entry.terms) for entry in correction] == [0, 0, 132, 149, 33]
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    equation = _hypersurface_equation(ray)
    charts = tuple(
        chart for chart in tier_a_pencil_model().blowup_atlas.charts
        if chart.fiber_chart == "nu"
    )
    assert [chart.name for chart in charts] == payload["target_charts_checked"]
    for chart in charts:
        relation = _relation_columns(ray, chart)
        pairing = plucker_pairing(relation)
        section = local_dual_contraction(relation, 0, 1)
        inverse = inverse_numerator(0, 1)
        assert minor == pairing.rows[0][1] == section.denominator
        assert _multiply_vector(_transpose(relation), relation_order) == tuple(
            equation * entry for entry in koszul
        )
        assert quotient == _multiply_vector(inverse, relation_order)
        image = _multiply_vector(pairing, quotient)
        residual = tuple(image[i] - minor * relation_order[i] for i in range(5))
        assert tuple(minor * entry for entry in residual) == tuple(
            equation * entry for entry in correction
        )
        wrong_image = _multiply_vector(pairing, tuple(-entry for entry in quotient))
        wrong_residual = tuple(
            wrong_image[i] - minor * relation_order[i] for i in range(5)
        )
        assert tuple(minor * entry for entry in wrong_residual) != tuple(
            equation * entry for entry in correction
        )


def test_quotient_image_remains_local() -> None:
    """The saved image is tied to exact inputs but not a full Higgs lift."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    payload.pop("artifact_digest")
    assert payload == alternate_up_higgs_quotient_overlap_image()
    assert payload["minor_open_gluing_constructed"] is False
    assert payload["global_hom_to_tensor_chain_map_constructed"] is False
    assert payload["exterior_cone_higgs_cocycle_constructed"] is False
