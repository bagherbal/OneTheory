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
    State-audit tests only; the reverse Yukawa contraction remains pending.
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
    assert path["criteria"]["lawful_P1_genuine_su4_on_stable_chamber"] is False
    assert path["criteria"]["retired_P3_embedding_used_for_stability"] is False
    assert path["criteria"]["lawful_matter_h0_to_h3"] == [0, 27, 0, 0]
    assert path["criteria"]["lawful_dual_matter_h0_to_h3"] == [0, 0, 27, 0]
    assert path["criteria"]["lawful_matter_deck_representation"] == (
        "3 Reg(Z3 x Z3)"
    )
    assert path["criteria"]["lawful_higgs_h0_to_h3"] == [0, 4, 4, 0]
    assert path["criteria"]["lawful_wilson_projected_families"] == 3
    assert path["criteria"]["lawful_wilson_projected_higgs_pairs"] == 0
    assert path["criteria"]["lawful_massless_color_triplets"] == 0
    assert path["criteria"]["lawful_structural_spectrum_all_P1"] is False
    assert path["criteria"]["prior_forward_computable_carrier_component"] == (
        "lawful-mixed-schoen-P1"
    )
    assert path["criteria"]["prior_forward_computable_carrier_component_frozen"] is False
    assert path["criteria"]["computable_carrier_component"] == (
        "alternate-i6-ray-0-1-P1"
    )
    assert path["criteria"]["computable_carrier_component_frozen"] is True
    assert path["criteria"]["selected_quotient_determinant_character"] == [2, 1]
    assert path["criteria"]["alternate_fixed_atlas_determinant_characters"] == [
        [2, 1], [0, 1]
    ]
    assert path["criteria"]["alternate_fixed_atlas_su4_excluded"] is True
    assert path["criteria"]["alternate_other_linearisations_excluded"] is False
    assert path["criteria"]["alternate_repaired_higgs_screen_survivor"] == [0, 1]
    assert path["criteria"]["alternate_repaired_higgs_screen_conditional"] is True
    assert (
        path["criteria"]["alternate_repaired_higgs_outer_extension_constructed"]
        is True
    )
    assert path["criteria"]["alternate_ray_0_1_cover_ext1_dimension"] == 18
    assert path["criteria"]["alternate_ray_0_1_invariant_ext1_dimension"] == 2
    assert path["criteria"]["alternate_ray_0_1_strict_invariant_representatives"] == 2
    assert path["criteria"]["alternate_ray_0_1_invariant_ext_unresolved"] is False
    assert path["criteria"]["alternate_ray_0_1_universal_cone_constructed"] is True
    assert path["criteria"]["alternate_ray_0_1_determinant_repaired"] is True
    assert path["criteria"]["alternate_ray_0_1_stability_unresolved"] is False
    assert path["criteria"][
        "alternate_ray_0_1_all_nonzero_p1_stable_in_sufficient_chamber"
    ] is True
    assert path["criteria"][
        "alternate_ray_0_1_genuine_su4_on_sufficient_chamber"
    ] is True
    assert path["criteria"]["alternate_ray_0_1_physical_spectrum_unresolved"] is True
    assert path["criteria"]["alternate_ray_0_1_charged_structural_spectrum_passes"] is True
    assert path["criteria"]["alternate_ray_0_1_higgs_h0_to_h3"] == [0, 4, 4, 0]
    assert path["criteria"]["alternate_ray_0_1_wilson_higgs_pairs"] == 1
    assert path["criteria"]["alternate_ray_0_1_explicit_cocycles_available"] is False
    assert path["criteria"]["selected_quotient_su4_certified"] is False
    assert path["criteria"]["first_constituent_atlas_to_mixed_character"] == [2, 0]
    assert path["criteria"]["second_constituent_atlas_to_mixed_character"] == [0, 0]
    assert path["criteria"]["atlas_frame_comparison_exact"] is True
    assert path["criteria"]["same_constituent_wilson_repair_available"] is False
    assert path["criteria"]["current_full_chain_wilson_multiplicities"] == {
        "up_higgs_doublet": 0,
        "down_higgs_doublet": 1,
        "color_triplet": 0,
        "color_antitriplet": 0,
    }
    assert (
        path["criteria"]["same_cover_bundle_relinearization_repair_available"]
        is False
    )
    assert path["criteria"]["lawful_reverse_matter_h0_to_h3"] == [0, 27, 0, 0]
    assert path["criteria"]["lawful_reverse_dual_matter_h0_to_h3"] == [0, 0, 27, 0]
    assert path["criteria"]["lawful_reverse_higgs_h0_to_h3"] == [0, 4, 4, 0]
    assert path["criteria"]["lawful_reverse_wilson_projected_families"] == 3
    assert path["criteria"]["lawful_reverse_wilson_projected_higgs_pairs"] == 0
    assert path["criteria"]["lawful_reverse_massless_color_triplets"] == 0
    assert path["criteria"]["lawful_reverse_structural_spectrum_all_P5"] is False
    assert (
        path["criteria"][
            "lawful_reverse_spectrum_source_assertion_used_as_rank_input"
        ]
        is False
    )
    assert path["criteria"]["reverse_down_universal_matter_character_count"] == 2
    assert path["criteria"]["reverse_down_constant_v2_class_count"] == 4
    assert path["criteria"]["reverse_down_universal_v1_lift_count"] == 2
    assert path["criteria"]["reverse_down_matter_parameter_correction_count"] == 12
    assert path["criteria"]["all_reverse_down_matter_lifts_exact"] is True
    assert path["criteria"]["reverse_down_extension_point_selected"] is False
    assert path["criteria"]["reverse_down_higgs_lift_available"] is True
    assert path["criteria"]["reverse_down_higgs_parameter_correction_count"] == 6
    assert path["criteria"]["reverse_down_higgs_character_exact"] is True
    assert path["criteria"]["reverse_down_higgs_canonical_frame_exact"] is True
    assert path["criteria"]["reverse_down_support_exact"] is True
    assert path["criteria"]["reverse_down_exterior_zero_slot_count"] == 4
    assert path["criteria"]["reverse_down_tree_boundary_zero_slot_count"] == 4
    assert path["criteria"]["reverse_down_matrix_rank_upper_bound"] == 1
    assert path["criteria"]["reverse_down_central_coefficient_computed"] is False
    assert path["criteria"]["reverse_down_v1_pairing_available"] is True
    assert path["criteria"]["reverse_down_v1_pairing_term_count"] == 8892
    assert path["criteria"]["reverse_down_v1_pairing_exchange_exact"] is True
    assert path["criteria"]["reverse_down_v1_pairing_character_exact"] is True
    assert path["criteria"]["reverse_down_v1_pairing_reduced_coordinate_count"] == 0
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
    assert path["criteria"]["cech_local_diagonal_chain_map_available"] is True
    assert path["criteria"]["canonical_chain_extension_term_count"] == 1278
    assert path["criteria"]["first_matter_leg_raw_term_count"] == 1_715_173
    assert path["criteria"]["first_matter_leg_projected_term_count"] == 866
    assert path["criteria"]["first_matter_leg_equivariant_term_count"] == 72_099
    assert path["criteria"]["first_matter_leg_residual_term_count"] == 7_797
    assert path["criteria"]["first_matter_leg_is_cycle"] is False
    assert path["criteria"]["first_matter_leg_partial_scalar_residue"] == "0"
    assert path["criteria"]["first_higgs_leg_action_term_count"] == 1_593
    assert path["criteria"]["first_higgs_leg_correction_term_count"] == 1_431
    assert path["criteria"]["first_higgs_leg_action_is_cycle"] is True
    assert path["criteria"]["first_higgs_leg_correction_exact"] is True
    assert path["criteria"]["canonical_higgs_leg_action_term_count"] == 2_124
    assert path["criteria"]["canonical_higgs_leg_correction_term_count"] == 1_908
    assert path["criteria"]["canonical_higgs_leg_action_is_cycle"] is True
    assert path["criteria"]["canonical_higgs_leg_correction_exact"] is True
    assert path["criteria"]["bottom_v2_plucker_chain_map_available"] is True
    assert path["criteria"]["bottom_v2_plucker_pairing_term_count"] == 8_592
    assert (
        path["criteria"]["bottom_v2_plucker_exchange_primitive_term_count"]
        == 3_900
    )
    assert (
        path["criteria"]["bottom_v2_plucker_equivariant_term_count"]
        == 11_340
    )
    assert path["criteria"]["bottom_v2_plucker_character"] == [0, 2]
    assert path["criteria"]["bottom_v2_plucker_character_exact"] is True
    assert (
        path["criteria"]["first_input_level_comparison_primitive_available"]
        is True
    )
    assert (
        path["criteria"]["first_input_level_comparison_primitive_term_count"]
        == 105_348
    )
    assert (
        path["criteria"]["first_complete_higher_product_coefficient_available"]
        is True
    )
    assert path["criteria"]["first_complete_higher_product_coefficient"] == "0"
    assert (
        path["criteria"]["first_complete_higher_product_cochain_term_count"]
        == 268_905
    )
    assert path["criteria"]["complete_first_order_coefficient_count"] == 8
    assert path["criteria"]["complete_first_order_matrix_available"] is True
    assert path["criteria"]["complete_first_order_matrix_rank"] == 0
    assert path["criteria"]["complete_first_order_matrix_parameter_basis"] == [
        "a0",
        "a1",
    ]
    assert (
        path["criteria"]["complete_first_order_matrix_extension_point_selected"]
        is False
    )
    assert path["criteria"]["up_maximum_exterior_allowed_parameter_order"] == 1
    assert path["criteria"]["up_f5_and_higher_structurally_zero"] is True
    assert (
        path["criteria"]["complete_universal_holomorphic_up_matrix_available"]
        is True
    )
    assert path["criteria"]["complete_universal_holomorphic_up_matrix_rank"] == 0
    assert path["criteria"]["declared_up_branch_can_reach_rank_three"] is False
    assert path["criteria"]["all_published_yukawa_character_products_invariant"] is True
    assert path["criteria"]["selected_next_flavor_sector"] == "down"
    assert path["criteria"]["selected_next_flavor_chain_object_count"] == 7
    assert path["criteria"]["selected_next_matter_character"] == [1, 0]
    assert path["criteria"]["selected_next_higgs_character"] == [0, 2]
    assert path["criteria"]["flavor_sector_selected_from_observations"] is False
    assert path["criteria"]["down_higgs_character_space_dimensions"] == [100, 243, 176]
    assert path["criteria"]["down_higgs_character_differential_ranks"] == [100, 143]
    assert path["criteria"]["down_higgs_character_h1_dimension"] == 0
    assert path["criteria"]["strict_down_higgs_representative_available"] is False
    assert path["criteria"]["down_higgs_character_twist_guessed"] is False
    assert path["criteria"]["source_derived_h_d_character_h1_dimension"] == 1
    assert path["criteria"]["current_h_d_comparison_route_refuted"] is True
    assert path["criteria"]["both_determinant_hom_orientations_blocked"] is True
    assert path["criteria"]["legacy_frame_matches_constituent_atlases"] is False
    assert path["criteria"]["factor_action_orientations_exact"] is True
    assert path["criteria"]["legacy_frame_atlas_mismatch_count"] == 1
    assert path["criteria"]["isolated_atlas_line_commutator_term_count"] == 14
    assert path["criteria"]["forced_uniform_w1_p_scalar"] == "-1-omega"
    assert path["criteria"]["uniform_scalar_shifted_character"] == [1, 2]
    assert path["criteria"]["uniform_scalar_character_space_dimensions"] == [
        100,
        243,
        176,
    ]
    assert path["criteria"]["uniform_scalar_differential_ranks"] == [100, 143]
    assert path["criteria"]["uniform_scalar_shifted_h1_dimension"] == 0
    assert path["criteria"]["scalar_higgs_action_repairs_refuted"] is True
    assert path["criteria"]["complete_current_higgs_characters"] == [
        [0, 0],
        [0, 1],
        [2, 0],
        [2, 1],
    ]
    assert path["criteria"]["selected_source_higgs_characters"] == [
        [0, 1],
        [0, 2],
        [1, 2],
        [2, 1],
    ]
    assert path["criteria"]["uniform_higgs_character_shift_matches"] == []
    assert path["criteria"]["complete_higgs_character_audit_exact"] is True
    assert path["criteria"]["selected_constituent_self_hom_h0_dimensions"] == [1, 1]
    assert path["criteria"]["selected_constituents_simple_over_q_omega"] is True
    assert (
        path["criteria"]["same_constituent_higgs_relinearization_available"]
        is False
    )
    assert path["criteria"]["constituent_atlas_over_synchronized_characters"] == [
        [2, 0],
        [0, 0],
    ]
    assert path["criteria"]["atlas_induced_higgs_characters"] == [
        [1, 0],
        [1, 1],
        [2, 0],
        [2, 1],
    ]
    assert path["criteria"]["atlas_higgs_characters_match_selected_source"] is False
    assert path["criteria"]["source_action_is_inverse_forward_pullback"] is True
    assert path["criteria"]["source_action_higgs_characters"] == [
        [0, 0],
        [0, 2],
        [1, 0],
        [1, 2],
    ]
    assert path["criteria"]["source_action_up_higgs_h1_dimension"] == 0
    assert path["criteria"]["source_action_down_higgs_h1_dimension"] == 1
    assert path["criteria"]["strict_forward_higgs_character"] == [0, 1]
    assert path["criteria"]["strict_source_higgs_character"] == [0, 2]
    assert (
        path["criteria"]["strict_source_down_higgs_representative_available"]
        is True
    )
    assert path["criteria"]["prior_physical_flavor_routing_valid"] is False
    assert path["criteria"]["selected_available_flavor_sector"] == "down"
    assert path["criteria"]["selected_available_flavor_chain_object_count"] is None
    assert path["criteria"]["selected_available_matter_characters"] == [
        [2, 1],
        [1, 0],
    ]
    assert path["criteria"]["selected_available_forward_matter_characters"] == [
        [1, 2],
        [2, 0],
    ]
    assert path["criteria"]["selected_available_reused_higgs_character"] == [0, 2]
    assert path["criteria"]["down_universal_matter_character_count"] == 2
    assert path["criteria"]["down_universal_v1_class_count"] == 2
    assert path["criteria"]["down_universal_v2_lift_count"] == 4
    assert path["criteria"]["down_matter_parameter_correction_count"] == 8
    assert path["criteria"]["all_down_matter_lifts_exact"] is True
    assert path["criteria"]["down_extension_point_selected"] is False
    assert path["criteria"]["complete_down_tree_matrix_available"] is True
    assert path["criteria"]["complete_down_tree_matrix_rank"] == 0
    assert (
        path["criteria"]["down_tree_zero_entries_have_exact_primitives"] is True
    )
    assert path["criteria"]["down_tree_extension_point_selected"] is False
    assert path["criteria"]["complete_down_first_order_coefficient_count"] == 8
    assert (
        path["criteria"]["complete_universal_holomorphic_down_matrix_available"]
        is True
    )
    assert path["criteria"]["complete_universal_holomorphic_down_matrix_rank"] == 0
    assert path["criteria"]["down_maximum_exterior_allowed_parameter_order"] == 1
    assert path["criteria"]["down_higher_orders_structurally_zero"] is True
    assert path["criteria"]["neutrino_universal_matter_character_count"] == 2
    assert path["criteria"]["neutrino_universal_v1_class_count"] == 2
    assert path["criteria"]["neutrino_universal_v2_lift_count"] == 4
    assert path["criteria"]["neutrino_matter_parameter_correction_count"] == 8
    assert path["criteria"]["all_neutrino_matter_lifts_exact"] is True
    assert path["criteria"]["complete_neutrino_tree_matrix_available"] is True
    assert path["criteria"]["complete_neutrino_tree_matrix_rank"] == 0
    assert (
        path["criteria"]["neutrino_tree_zero_entries_have_exact_primitives"]
        is True
    )
    assert path["criteria"]["neutrino_tree_extension_point_selected"] is False
    assert path["criteria"]["complete_neutrino_first_order_coefficient_count"] == 8
    assert (
        path["criteria"]["complete_universal_holomorphic_neutrino_matrix_available"]
        is True
    )
    assert (
        path["criteria"]["complete_universal_holomorphic_neutrino_matrix_rank"]
        == 0
    )
    assert (
        path["criteria"]["neutrino_maximum_exterior_allowed_parameter_order"]
        == 1
    )
    assert path["criteria"]["neutrino_higher_orders_structurally_zero"] is True
    assert path["criteria"]["neutrino_extension_point_selected"] is False
    assert path["criteria"]["prior_up_matrix_physical_assignment_valid"] is False
    assert (
        path["criteria"]["prior_neutrino_matrix_physical_assignment_valid"]
        is False
    )
    assert path["criteria"]["charged_lepton_source_matter_characters"] == [
        [0, 0],
        [0, 1],
    ]
    assert path["criteria"]["charged_lepton_forward_matter_characters"] == [
        [0, 0],
        [0, 2],
    ]
    assert path["criteria"]["charged_lepton_source_higgs_character"] == [0, 2]
    assert path["criteria"]["charged_lepton_forward_higgs_character"] == [0, 1]
    assert (
        path["criteria"][
            "complete_universal_holomorphic_charged_lepton_matrix_available"
        ]
        is True
    )
    assert (
        path["criteria"][
            "complete_universal_holomorphic_charged_lepton_matrix_rank"
        ]
        == 0
    )
    assert (
        path["criteria"][
            "charged_lepton_maximum_exterior_allowed_parameter_order"
        ]
        == 1
    )
    assert (
        path["criteria"]["charged_lepton_higher_orders_structurally_zero"]
        is True
    )
    assert (
        path["criteria"]["remaining_current_chain_flavor_sector_available"]
        is False
    )
    assert (
        path["criteria"][
            "current_carrier_nontrivial_holomorphic_yukawa_available"
        ]
        is False
    )
    assert path["criteria"]["shared_missing_higgs_character"] == [0, 1]
    assert path["criteria"]["next_exact_frontier_uses_observations"] is False
    assert path["criteria"]["lawful_reverse_projective_outer_space"] == (
        "P^5(Q(omega))"
    )
    assert path["criteria"]["lawful_reverse_split_locus"] == (
        "affine origin only"
    )
    assert path["criteria"]["lawful_reverse_local_freeness_all_parameters"] is True
    assert path["criteria"]["lawful_reverse_equivariant_descent_all_parameters"] is True
    assert path["criteria"]["lawful_reverse_extension_point_selected"] is False
    assert path["criteria"]["lawful_reverse_exact_stability_locus_computed"] is True
    assert path["criteria"]["lawful_reverse_stability_anchor"] == [3, 2, 2]
    assert path["criteria"]["lawful_reverse_stability_box_radius"] == "1/4"
    assert path["criteria"]["lawful_reverse_all_P5_stable_in_chamber"] is True
    assert path["criteria"]["lawful_reverse_genuine_su4_on_stable_chamber"] is False
    assert path["criteria"]["lawful_reverse_factor_exchange_assumed"] is False
    assert checkpoint["completed_pairs"] == 1296
    assert checkpoint["suspended"] is True
    assert claims["universal_rank_four_family"]["status"] == "COMPUTED"
    assert claims["algebraic_lawful_locus"]["status"] == "COMPUTED"
    assert claims["necessary_stability_walls"]["status"] == "COMPUTED"
    assert claims["alternate_constituent_matter_profile"]["status"] == "COMPUTED"
    assert claims["alternate_constituent_structural_spectrum"]["status"] == "COMPUTED"
    assert claims["alternate_constituent_carrier_state"]["status"] == "COMPUTED"
    assert claims["alternate_constituent_up_matter_representatives"]["status"] == (
        "COMPUTED"
    )
    assert claims["alternate_constituent_up_cone_matter_lifts"]["status"] == (
        "COMPUTED"
    )
    assert claims["alternate_up_higgs_hom_representative"]["status"] == (
        "COMPUTED"
    )
    assert claims["alternate_up_yoneda_evaluation"]["status"] == "COMPUTED"
    assert path["selection_status"] == (
        "the selected P1 and reverse P5 physical quotient freezes are "
        "refuted; the distinct determinant-repaired alternate P1 "
        "component passes the charged structural spectrum and is "
        "frozen only for chain-level physics"
    )
    assert path["next_required_object"] == (
        "contract the nonboundary alternate Yoneda images with "
        "strict first-constituent classes to obtain exact mixed "
        "scalar entries; then close the same-cone F-F block for "
        "one complete holomorphic 3x3 up-type Yukawa matrix"
    )
    assert claims["selected_atlas_common_frame_comparison"]["status"] == (
        "COMPUTED"
    )
    assert claims["same_constituent_wilson_shift_no_go"]["status"] == "REFUTED"
    assert claims["mixed_schoen_reverse_outer_universal_cone"]["status"] == (
        "COMPUTED"
    )
    assert claims["mixed_schoen_reverse_outer_stability_locus"]["status"] == (
        "PROVED"
    )
    assert claims["mixed_schoen_reverse_observable_spectrum"]["status"] == (
        "REFUTED"
    )
    assert claims["computable_carrier_state"]["status"] == "BLOCKED"
    assert claims["computable_reverse_carrier_state"]["status"] == "BLOCKED"
    assert claims["selected_mixed_determinant_descent"]["status"] == "REFUTED"
    assert claims["reverse_universal_down_matter_lifts"]["status"] == "COMPUTED"
    assert claims["reverse_universal_down_higgs_lift"]["status"] == "COMPUTED"
    assert claims["mixed_matter_tensor_comparison"]["status"] == "COMPUTED"
    assert claims["mixed_scalar_trace_target"]["status"] == "COMPUTED"
    assert claims["mixed_local_determinant_pairings"]["status"] == "COMPUTED"
    assert claims["mixed_tree_up_matrix"]["status"] == "COMPUTED"
    assert claims["mixed_diagonal_local_comparison"]["status"] == "COMPUTED"
    assert claims["mixed_diagonal_chain_map"]["status"] == "COMPUTED"
    assert claims["mixed_matter_leg_deformation"]["status"] == "COMPUTED"
    assert claims["mixed_higgs_leg_deformation"]["status"] == "COMPUTED"
    assert claims["mixed_v2_pluecker_chain_map"]["status"] == "COMPUTED"
    assert claims["mixed_first_higher_product_coefficient"]["status"] == "COMPUTED"
    assert claims["mixed_first_order_up_matrix"]["status"] == "COMPUTED"
    assert claims["mixed_up_yukawa_no_go"]["status"] == "PROVED"
    assert claims["mixed_flavor_character_support"]["status"] == "COMPUTED"
    assert claims["mixed_down_higgs_chain_obstruction"]["status"] == "REFUTED"
    assert (
        claims["mixed_higgs_equivariant_comparison_obstruction"]["status"]
        == "REFUTED"
    )
    assert claims["mixed_higgs_scalar_action_no_go"]["status"] == "REFUTED"
    assert claims["mixed_higgs_full_character_audit"]["status"] == "COMPUTED"
    assert claims["mixed_higgs_linearization_no_go"]["status"] == "REFUTED"
    assert (
        claims["mixed_atlas_higgs_character_incompatibility"]["status"]
        == "REFUTED"
    )
    assert claims["mixed_character_convention_correction"]["status"] == "PROVED"
    assert claims["universal_down_matter_lifts"]["status"] == "COMPUTED"
    assert claims["mixed_down_tree_matrix"]["status"] == "COMPUTED"
    assert claims["mixed_down_first_order_matrix"]["status"] == "PROVED"
    assert claims["mixed_flavor_frontier"]["status"] == "REFUTED"
    assert claims["universal_neutrino_matter_lifts"]["status"] == "COMPUTED"
    assert claims["mixed_neutrino_tree_matrix"]["status"] == "COMPUTED"
    assert claims["mixed_neutrino_first_order_matrix"]["status"] == "COMPUTED"
    assert claims["mixed_charged_lepton_convention"]["status"] == "PROVED"
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
    assert claims["relative_constituent_pushdowns"]["status"] == "SELECTED"
    assert claims["distinct_constituent_ray_screen"]["status"] == "COMPUTED"
    assert claims["alternate_constituent_cover_h1"]["status"] == "COMPUTED"
    assert claims["alternate_constituent_deck_atlases"]["status"] == "COMPUTED"
    assert claims["alternate_constituent_determinant_obstruction"]["status"] == (
        "COMPUTED"
    )
    assert claims["alternate_constituent_character_screen"]["status"] == "COMPUTED"
    assert claims["alternate_constituent_outer_cover_ext"]["status"] == "COMPUTED"
    assert claims["alternate_constituent_outer_invariants"]["status"] == "COMPUTED"
    assert claims["alternate_constituent_outer_universal_cone"]["status"] == (
        "COMPUTED"
    )
    assert claims["alternate_constituent_outer_stability_locus"]["status"] == (
        "COMPUTED"
    )
    assert claims["alternate_constituent_hom_cycle_actions"]["status"] == "COMPUTED"
    assert "determinant-trivial carrier" in claims[
        "alternate_constituent_cover_h1"
    ]["missing_prerequisites"]
    assert claims["mixed_schoen_observable_spectrum"]["status"] == "REFUTED"
    assert claims["physical_spectrum"]["status"] == "BLOCKED"
    assert claims["computable_carrier_state"]["status"] == "BLOCKED"
    assert claims["strict_mixed_matter_representatives"]["status"] == "COMPUTED"
    assert claims["universal_matter_sector_lifts"]["status"] == "COMPUTED"
    assert claims["higgs_determinant_twist_route"]["status"] == "REFUTED"
    assert claims["higgs_direct_tensor_diagonal"]["status"] == "COMPUTED"
    assert claims["strict_mixed_higgs_representative"]["status"] == "COMPUTED"
    assert claims["common_dga_package"]["status"] == "COMPUTED"
    assert claims["published_chain_reconstruction"]["status"] == "BLOCKED"
    assert claims["genesis_to_uv_bridge"]["status"] == "BLOCKED"
    scheduler = state["research_value_scheduler"]
    assert scheduler[0]["task"] == "distinct_constituent_realization_screen"
    assert scheduler[1]["task"] == "distinct_su4_carrier_screen"
    assert state["fitted_inputs"] == []
