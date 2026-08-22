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
    State-audit tests only; replacement-carrier stability remains pending.
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
    assert checkpoint["completed_pairs"] == 1296
    assert checkpoint["suspended"] is True
    assert claims["universal_rank_four_family"]["status"] == "COMPUTED"
    assert claims["algebraic_lawful_locus"]["status"] == "COMPUTED"
    assert claims["necessary_stability_walls"]["status"] == "COMPUTED"
    assert path["selection_status"] == (
        "mixed Schoen arrows closed; outer convolution open"
    )
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
    assert claims["published_constituent_mapping_cones"]["status"] == "REFUTED"
    assert claims["published_outer_reduced_model"]["status"] == "COMPUTED"
    assert claims["published_outer_cech_transfer"]["status"] == "COMPUTED"
    assert claims["published_outer_cech_invariants"]["status"] == "COMPUTED"
    assert claims["published_outer_universal_cone"]["status"] == "COMPUTED"
    assert claims["published_outer_stability_locus"]["status"] == "BLOCKED"
    assert claims["published_matter_cohomology"]["status"] == "BLOCKED"
    assert claims["published_higgs_cohomology"]["status"] == "BLOCKED"
    assert claims["physical_spectrum"]["status"] == "BLOCKED"
    assert claims["published_chain_reconstruction"]["status"] == "BLOCKED"
    assert claims["genesis_to_uv_bridge"]["status"] == "BLOCKED"
    assert state["fitted_inputs"] == []
