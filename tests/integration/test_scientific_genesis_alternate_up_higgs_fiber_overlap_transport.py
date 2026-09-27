"""Regress the actual alternate Hom fiber-overlap Koszul transport.

Owns:
    Exact corrected middle numerators, hypersurface residuals, and
    first-factor Čech replication checks on the three base overlaps.

Depends on:
    The saved strict Hom source, alternate atlas, local syzygy sections,
    and exact Laurent arithmetic.

Must not:
    Treat fiber-overlap divisibility as complete global Higgs gluing.

Phase 0:
    Research integration checks for the next tensor-transport input.
"""

import json

from onetheory.math.numbers import OMEGA, Eisenstein
from onetheory.math.sheaves import LaurentPolynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pencil import tier_a_pencil_model
from research.experiments.scientific_genesis.alternate_up_higgs_fiber_overlap_transport import (
    OUTPUT,
    _vector,
    alternate_up_higgs_fiber_overlap_transport,
)
from research.experiments.scientific_genesis.alternate_up_higgs_local_syzygy_section import (
    _multiply_vector,
    _right_mixed_matrix,
)
from research.experiments.scientific_genesis.distinct_constituent_ray_screen import (
    lift_joint_character_ray,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    _constituent,
)
from research.experiments.scientific_genesis.published_constituent_deck_actions import (
    published_constituent_deck_actions,
)
from research.experiments.scientific_genesis.published_constituent_overlap_transitions import (
    _hypersurface_equation,
)


def test_all_saved_fiber_overlap_blocks_close_modulo_schoen_equation() -> None:
    """Actual arrow matrices send corrected numerators to Koszul residues."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert payload["fiber_overlap_blocks_checked"] == 9
    assert payload["first_factor_x_cell_independence_exact"] is True
    record = payload["fiber_overlap_representative"]
    assert record["base_pivots_checked"] == [0, 1, 2]
    assert payload["base_chart_formula_independence_exact"] is True
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    right = _constituent(ray, "I6-ray-0-1", 2, (-1, 1, 0))
    equation = _hypersurface_equation(ray)
    charts = {chart.name: chart for chart in tier_a_pencil_model().blowup_atlas.charts}
    assert record["first_factor_x_cells_checked"] == [[0], [1], [2]]
    assert record["middle_source_term_count_per_x_cell"] == 9
    assert record["koszul_source_term_count_per_x_cell"] == 6
    assert record["koszul_term_necessary_exact"] is True
    numerator = _vector(record["corrected_middle_numerator_object_order"], 5)
    koszul = _vector(record["koszul_residual_numerator"], 3)
    denominator = _vector([record["minor_product_denominator"]], 1)[0]
    assert not denominator.is_zero()
    assert any(not item.is_zero() for item in numerator)
    assert any(not item.is_zero() for item in koszul)
    for base_pivot in range(3):
        for x_pivot in range(3):
            target_name = f"U_{base_pivot}_nu"
            differential = _right_mixed_matrix(
                right, charts[target_name], (x_pivot,)
            )
            assert _multiply_vector(differential, numerator) == tuple(
                equation * entry for entry in koszul
            )
            altered = (
                numerator[0] + LaurentPolynomial.one(5, scalar_type=Eisenstein),
                *numerator[1:],
            )
            assert _multiply_vector(differential, altered) != tuple(
                equation * entry for entry in koszul
            )


def test_fiber_transport_artifact_retains_global_gates() -> None:
    """The exact overlap identity is not promoted to a full chain map."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    payload.pop("artifact_digest")
    assert payload == alternate_up_higgs_fiber_overlap_transport()
    assert payload["base_overlap_gluing_constructed"] is False
    assert payload["global_hom_to_tensor_chain_map_constructed"] is False
    assert payload["exterior_cone_higgs_cocycle_constructed"] is False
