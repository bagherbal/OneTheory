"""Test the evidence-backed Scientific Genesis governance artifact.

Owns:
    Regression checks for deterministic state generation, epistemic statuses,
    the acyclic dependency graph, and the suspended action frontier.

Depends on:
    The research audit, generated exact carrier artifacts, and pytest.

Must not:
    Treat governance metadata as a carrier, select an extension point, or
    convert a blocked scientific edge into an implemented bridge.

Phase 0:
    State-audit tests only; common-DGA carrier representatives remain pending.
"""

import json
from pathlib import Path

from research.experiments.scientific_genesis.audit import (
    build_state,
    validate_state,
)

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "data/generated/scientific_genesis/scientific_genesis_state.json"


def test_scientific_genesis_state_is_current_and_valid() -> None:
    """The frozen artifact exactly matches a fresh evidence reconstruction."""

    stored = json.loads(STATE.read_text(encoding="utf-8"))
    rebuilt = build_state()

    validate_state(stored)
    assert stored == rebuilt


def test_vertical_path_uses_a_universal_family_without_selecting_a_point() -> None:
    """The scheduler pivots to source-bound reconstruction without guessing."""

    state = build_state()
    path = state["recommended_vertical_path"]
    checkpoint = state["automorphism_checkpoint"]
    claims = {claim["id"]: claim for claim in state["claims"]}

    assert path["candidate_pair"] is None
    assert path["criteria"]["retired_invariant_ext_dimension"] == 4
    assert path["criteria"]["retired_family_count"] == 72
    assert path["criteria"]["additional_retired_family_count"] == 72
    assert path["criteria"]["current_minimum_retired_family_count"] == 72
    assert path["criteria"]["forced_subobject_retired_family_count"] == 648
    assert path["criteria"]["mixed_sign_minimum_retired_family_count"] == 72
    assert path["criteria"]["slope_identity_retired_family_count"] == 72
    assert path["criteria"]["next_survivor_restriction_rank"] == 20
    assert path["criteria"]["next_survivor_lifting_kernels_unstable"] is True
    assert path["criteria"]["next_survivor_complements_stability_proved"] is False
    assert path["criteria"]["next_survivor_forced_chamber_nonempty"] is True
    assert path["criteria"]["next_survivor_generator_restriction_count"] == 288
    assert path["criteria"]["next_survivor_generator_kernels_proper"] is True
    assert path["criteria"]["next_survivor_lower_line_retired_family_count"] == 72
    assert path["criteria"]["next_survivor_lower_line_lifts_universally"] is True
    assert path["criteria"]["final_lower_line_retired_family_count"] == 72
    assert path["criteria"]["final_lower_line_lifts_universally"] is True
    assert path["criteria"]["remaining_nonzero_family_count"] == 0
    assert path["criteria"]["declared_computable_carrier_category_exhausted"] is True
    assert path["criteria"]["global_schoen_bundle_no_go"] is False
    assert path["criteria"]["next_candidate_blocks"] == []
    assert path["criteria"]["minimum_forced_chamber_nonempty"] is True
    assert path["criteria"]["arbitrary_point_selected"] is False
    assert path["criteria"]["mixed_cover_h1_dimensions"] == [18, 54]
    assert path["criteria"]["mixed_invariant_h1_dimensions"] == [2, 6]
    assert path["criteria"]["mixed_strict_invariant_representatives"] == [2, 6]
    assert path["criteria"]["lawful_mixed_projective_outer_space"] == (
        "P^1(Q(omega))"
    )
    assert path["criteria"]["retired_source_scoped_outer_space"] == (
        "P^3(Q(omega))"
    )
    assert path["criteria"]["outer_parameter_dimension_mismatch_unresolved"] is True
    assert path["criteria"]["lawful_P1_all_nonzero_parameters_stable_in_chamber"] is True
    assert path["criteria"]["lawful_P1_genuine_su4_on_stable_chamber"] is True
    assert path["criteria"]["retired_P3_embedding_used_for_stability"] is False
    assert path["criteria"]["lawful_matter_h0_to_h3"] == [0, 27, 0, 0]
    assert path["criteria"]["lawful_dual_matter_h0_to_h3"] == [0, 0, 27, 0]
    assert path["criteria"]["lawful_matter_deck_representation"] == (
        "3 Reg(Z3 x Z3)"
    )
    assert path["criteria"]["lawful_higgs_h0_to_h3"] == [0, 4, 4, 0]
    assert path["criteria"]["lawful_wilson_projected_families"] == 3
    assert path["criteria"]["lawful_wilson_projected_higgs_pairs"] == 1
    assert path["criteria"]["lawful_massless_color_triplets"] == 0
    assert path["criteria"]["lawful_structural_spectrum_all_P1"] is True
    assert path["criteria"]["computable_carrier_component_frozen"] is True
    assert path["criteria"]["lawful_chain_diagonal_transfer_seed_count"] == 4896
    assert path["criteria"]["lawful_chain_diagonal_squared_zero"] is True
    assert path["criteria"]["required_higgs_character"] == [0, 1]
    assert path["criteria"]["required_higgs_character_space_dimensions"] == [
        100,
        243,
        170,
    ]
    assert path["criteria"]["required_higgs_character_differential_ranks"] == [
        100,
        142,
    ]
    assert path["criteria"]["required_higgs_character_h1_dimension"] == 1
    assert path["criteria"]["physical_higgs_representative_available"] is True
    assert path["criteria"]["physical_higgs_representative_term_count"] == 27
    assert path["criteria"]["direct_matter_product_character"] == [0, 2]
    assert path["criteria"]["direct_matter_product_hull_available"] is True
    assert path["criteria"]["equivariant_matter_product_cycle_count"] == 4
    assert path["criteria"]["equivariant_matter_product_character"] == [0, 2]
    assert path["criteria"]["determinant_trace_available"] is True
    assert path["criteria"]["scalar_residue_target_available"] is True
    assert path["criteria"]["local_determinant_pairings_available"] is True
    assert path["criteria"]["complete_tree_level_up_matrix_available"] is True
    assert path["criteria"]["tree_level_up_matrix_rank"] == 0
    assert path["criteria"]["tree_level_up_scalar_primitives_exact"] is True
    assert path["criteria"]["nontrivial_holomorphic_up_matrix_available"] is False
    assert (
        path["criteria"]["deformation_diagonal_local_comparison_available"]
        is True
    )
    assert (
        path["criteria"]["global_polynomial_diagonal_comparison_available"]
        is False
    )
    assert path["criteria"]["cech_local_diagonal_comparison_required"] is True
    assert checkpoint["completed_pairs"] == 1296
    assert checkpoint["suspended"] is True
    assert claims["universal_rank_four_family"]["status"] == "COMPUTED"
    assert claims["algebraic_lawful_locus"]["status"] == "COMPUTED"
    assert claims["necessary_stability_walls"]["status"] == "COMPUTED"
    assert path["selection_status"] == (
        "complete lawful tree-level up matrix derived as an exact "
        "rank-zero result; exact local diagonal-comparison data now "
        "fix the first higher-product chain-map boundary"
    )
    assert path["next_required_object"] == (
        "the full Cech-local chain comparison applying the two chart "
        "coefficients and their overlap homotopy to the universal "
        "matter-correction cochains"
    )
    assert claims["mixed_matter_tensor_comparison"]["status"] == "COMPUTED"
    assert claims["mixed_scalar_trace_target"]["status"] == "COMPUTED"
    assert claims["mixed_local_determinant_pairings"]["status"] == "COMPUTED"
    assert claims["mixed_tree_up_matrix"]["status"] == "COMPUTED"
    assert claims["mixed_diagonal_local_comparison"]["status"] == "COMPUTED"
    assert claims["stability_chamber"]["status"] == "REFUTED"
    assert claims["minimum_dimensional_stability_block"]["status"] == "REFUTED"
    assert claims["next_topology_stability_block"]["status"] == "REFUTED"
    assert claims["current_minimum_stability_block"]["status"] == "REFUTED"
    assert claims["forced_subobject_stability_class"]["status"] == "REFUTED"
    assert claims["mixed_sign_minimum_forced_chamber"]["status"] == "COMPUTED"
    assert claims["mixed_sign_minimum_stability_block"]["status"] == "REFUTED"
    assert claims["lifted_line_slope_identity_block"]["status"] == "REFUTED"
    assert claims["next_survivor_lifting_kernel"]["status"] == "COMPUTED"
    assert claims["next_survivor_forced_chamber"]["status"] == "COMPUTED"
    assert claims["next_survivor_generator_strata"]["status"] == "COMPUTED"
    assert claims["next_survivor_lower_line_block"]["status"] == "REFUTED"
    assert claims["declared_carrier_category"]["status"] == "REFUTED"
    assert claims["published_projective_pushout_adapter"]["status"] == "REFUTED"
    assert claims["published_constituent_ext_spaces"]["status"] == "COMPUTED"
    assert claims["published_constituent_deck_actions"]["status"] == "COMPUTED"
    assert claims["published_constituent_ray_alignment"]["status"] == "COMPUTED"
    assert claims["published_constituent_full_cech"]["status"] == "COMPUTED"
    assert claims["published_constituent_local_units"]["status"] == "PROVED"
    assert claims["published_constituent_overlap_atlases"]["status"] == "COMPUTED"
    assert claims["published_constituent_deck_atlases"]["status"] == "COMPUTED"
    assert claims["mixed_constituent_schoen_arrows"]["status"] == "COMPUTED"
    assert claims["mixed_schoen_outer_transfer"]["status"] == "COMPUTED"
    assert claims["mixed_schoen_outer_actions"]["status"] == "COMPUTED"
    assert claims["mixed_schoen_outer_universal_cone"]["status"] == "COMPUTED"
    assert claims["published_constituent_mapping_cones"]["status"] == "REFUTED"
    assert claims["published_outer_reduced_model"]["status"] == "COMPUTED"
    assert claims["published_outer_cech_transfer"]["status"] == "COMPUTED"
    assert claims["published_outer_cech_invariants"]["status"] == "COMPUTED"
    assert claims["published_outer_universal_cone"]["status"] == "COMPUTED"
    assert claims["published_outer_stability_locus"]["status"] == "COMPUTED"
    assert claims["published_matter_cohomology"]["status"] == "BLOCKED"
    assert claims["published_higgs_cohomology"]["status"] == "BLOCKED"
    assert claims["relative_constituent_pushdowns"]["status"] == "COMPUTED"
    assert claims["mixed_schoen_observable_spectrum"]["status"] == "COMPUTED"
    assert claims["physical_spectrum"]["status"] == "COMPUTED"
    assert claims["computable_carrier_state"]["status"] == "COMPUTED"
    assert claims["strict_mixed_matter_representatives"]["status"] == "COMPUTED"
    assert claims["universal_matter_sector_lifts"]["status"] == "COMPUTED"
    assert claims["higgs_determinant_twist_route"]["status"] == "BLOCKED"
    assert claims["higgs_direct_tensor_diagonal"]["status"] == "COMPUTED"
    assert claims["strict_mixed_higgs_representative"]["status"] == "COMPUTED"
    assert claims["common_dga_package"]["status"] == "BLOCKED"
    assert claims["published_chain_reconstruction"]["status"] == "BLOCKED"
    assert claims["genesis_to_uv_bridge"]["status"] == "BLOCKED"
    assert state["fitted_inputs"] == []
