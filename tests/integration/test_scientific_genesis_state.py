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

import pytest

from research.experiments.scientific_genesis import audit
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


def test_same_prefix_draw_workflow_preserves_conditional_metric_boundary() -> None:
    """A declared law workflow is not IID evidence or a normalized physical result."""

    stored = json.loads(STATE.read_text(encoding="utf-8"))
    claims = {claim["id"]: claim for claim in stored["claims"]}
    node = claims["auxiliary_cover_draws"]
    assert node["status"] == "DERIVED"
    assert "mutually independent infinite fair named bit streams" in node["assumptions"]
    assert "controlled integration errors" in node["missing_prerequisites"]
    assert claims["visible_metrics"]["status"] == "BLOCKED"
    edges = [edge for edge in stored["dependencies"] if edge["target"] == "auxiliary_cover_draws"]
    assert {edge["source"] for edge in edges} == {
        "projective_uniform_input_cells", "projective_uncertain_intersections",
        "alternate_metric_positive_measure",
    }
    record = stored["auxiliary_cover_draws"]
    assert record["independent_cover_cloud_available"] is False
    assert record["controlled_integral_available"] is False
    assert record["failed_draws_resampled_or_dropped"] is False


def test_full_section_covariance_is_not_physical_normalization() -> None:
    """Full execution and an all-parameter local denominator do not imply HYM."""

    stored = json.loads(STATE.read_text(encoding="utf-8"))
    claims = {claim["id"]: claim for claim in stored["claims"]}
    assert claims["alternate_section_covariance"]["status"] == "COMPUTED"
    assert claims["visible_metrics"]["status"] == "BLOCKED"
    record = stored["alternate_section_covariance"]
    assert record["section_count"] == 5345
    assert record["all_original_columns_consumed"] is True
    assert record["extension_parameters_specialized"] is False
    assert record["unit_form_is_physical_or_canonical"] is False
    assert record["hym_inverse_kernel_available"] is False
    assert record["controlled_integral_available"] is False
    assert record["physical_yukawas_available"] is False
    assert record["unit_family_determinant_certificate"]["extension_parameter_choice_used"] is False


def test_complete_new_domain_functionals_keep_throughput_and_physics_unresolved() -> None:
    stored = json.loads(STATE.read_text(encoding="utf-8"))
    claims = {claim["id"]: claim for claim in stored["claims"]}
    record = stored["alternate_metric_fiber_functionals"]
    assert claims["alternate_metric_fiber_functionals"]["status"] == "COMPUTED"
    assert claims["visible_metrics"]["status"] == "BLOCKED"
    assert claims["physical_yukawas"]["status"] == "BLOCKED"
    assert record["section_count"] == 5345
    assert record["complete_5345_column_matrix_on_declared_new_domain_available"] is True
    for gate in ("individual_units_asserted_closed", "all_15_domains_executed",
                 "practical_multi_point_throughput_certified", "independent_cloud_available",
                 "controlled_integral_available", "ricci_flat_or_hym_metric_available",
                 "physical_yukawas_available", "common_stabilized_vacuum_available"):
        assert record[gate] is False
    assert {edge["source"] for edge in stored["dependencies"]
            if edge["target"] == "alternate_metric_fiber_functionals"} == {
        "alternate_metric_bounded_support", "alternate_metric_lift_operator_certificate",
        "uncertain_cover_frames",
    }


def test_pending_symbolic_execution_uses_the_actual_point_independent_section_identity() -> None:
    """Verified section provenance is not evidence of complete numerical execution."""

    stored = json.loads(STATE.read_text(encoding="utf-8"))
    identity = stored["original_metric_section_basis_identity"]
    assert identity["artifact_digest"] == (
        "71f9c2f46c1f7a69087e8f3aab1ed98f4474cf76cf66db5bf2c902f4f372621c"
    )
    assert identity["constituent_counts"] == [2655, 2690]
    assert identity["section_count"] == 5345
    assert identity["numeric_point_or_chart_input"] is False
    assert "chart_pivots" not in identity
    assert "exact_column_stream_sha256" not in identity
    claims = {claim["id"]: claim for claim in stored["claims"]}
    for name in ("alternate_metric_symbolic_columns", "alternate_metric_symbolic_evaluation"):
        assert claims[name]["status"] == "CONJECTURED"
        assert name not in stored
    assert claims["visible_metrics"]["status"] == "BLOCKED"
    assert claims["physical_yukawas"]["status"] == "BLOCKED"


def test_proved_representation_constraints_do_not_relabel_quantum_or_uv_assumptions() -> None:
    """An exact scoped obstruction is neither quantum emergence nor a physical model."""

    stored = json.loads(STATE.read_text(encoding="utf-8"))
    claims = {claim["id"]: claim for claim in stored["claims"]}
    assert claims["canonical_representation_constraints"]["status"] == "PROVED"
    assert claims["quantum_phase_structure"]["status"] == "ASSUMED"
    assert "symbolic contracts" in claims["quantum_phase_structure"]["statement"]
    assert claims["genesis_to_uv_bridge"]["status"] == "BLOCKED"
    record = stored["canonical_representation_constraints"]
    assert record["artifact_digest"] == (
        "3cb170379b54658324e13d9511f18de939694473790686069c5cc91e3b7f0cbf"
    )
    assert record["actual_symbolic_contract"]["matrix_representation_supplied"] is False
    for flag in ("all_finite_quantum_theories_excluded",
                 "nonlinear_or_continuum_emergence_excluded",
                 "quantum_postulates_derived", "causal_geometry_derived",
                 "gravitational_coupling_derived", "dimensional_constants_derived",
                 "genesis_to_uv_derivation_available", "physical_quantum_state_generated",
                 "observations_used"):
        assert record[flag] is False
    assert any(edge["source"] == "canonical_representation_constraints"
               and edge["target"] == "genesis_to_uv_bridge" for edge in stored["dependencies"])


def test_complete_trial_kernel_keeps_independent_integration_and_physics_unresolved() -> None:
    """A global projector bound is not a metric or a uniform stochastic moduli claim."""

    stored = json.loads(STATE.read_text(encoding="utf-8"))
    claims = {claim["id"]: claim for claim in stored["claims"]}
    record = stored["alternate_metric_trial_kernel"]
    assert claims["alternate_metric_trial_kernel"]["status"] == "COMPUTED"
    assert claims["visible_metrics"]["status"] == "BLOCKED"
    assert claims["physical_yukawas"]["status"] == "BLOCKED"
    assert record["section_count"] == 5345
    assert record["complete_action_reference"]["each_original_action_array_length"] == 5345
    assert record["full_factorized_trial_kernel_available"] is True
    assert record["global_unit_kernel_integrand_bound_available"] is True
    assert record["line_metric_required_for_trial_kernel"] is False
    assert record["line_twist_removed"] is False
    assert record["nonunit_kernel_execution_available"] is False
    assert record["uniform_simultaneous_parameter_family_probability_bound_available"] is False
    assert record["independent_cloud_available"] is False
    assert record["controlled_integral_available"] is False
    assert record["ricci_flat_or_hym_metric_available"] is False
    assert record["physical_yukawas_available"] is False
    assert record["common_stabilized_vacuum_available"] is False
    assert {edge["source"] for edge in stored["dependencies"]
            if edge["target"] == "alternate_metric_trial_kernel"} == {
        "alternate_section_covariance", "alternate_metric_quotient_generation",
        "alternate_metric_lift_operator_certificate", "alternate_metric_global_weight_bound",
    }


@pytest.mark.parametrize(
    "schema,field,error",
    (
        (
            "alternate-down-lepton-ff-entry-v1", "physical_yukawas_available",
            "an independently trace-checked actual down a0 checkpoint changed",
        ),
        (
            "alternate-neutrino-ff-matter-lift-v1", "extension_point_selected",
            "the independently replayed actual neutrino matter lift changed",
        ),
        *tuple(
            ("alternate-remaining-flavor-matter-lift-v1", field,
             "the independently replayed actual remaining matter lift changed")
            for field in ("extension_point_selected", "physical_yukawas_available",
                          "yukawa_entries_assigned", "existing_Q_and_L_recomputed")
        ),
        (
            "alternate-down-higgs-quotient-cone-v1", "full_exterior_square_higgs_constructed",
            "the independently replayed actual down-Higgs quotient cone changed",
        ),
        (
            "alternate-neutrino-full-holomorphic-matrix-v1", "physical_yukawa_matrix_available",
            "the completed neutrino matrix changed its trusted output digest",
        ),
        *tuple(
            ("alternate-down-lepton-mixed-pairing-v1", field,
             "the actual down/lepton mixed packet changed its trusted digest")
            for field in ("complete_down_matrix_available",
                          "complete_charged_lepton_matrix_available", "physical_yukawas_available",
                          "second_second_entries_assigned", "extension_point_selected")
        ),
        *tuple(
            ("alternate-remaining-flavor-matter-v1", field,
             "the remaining flavor input changed its expected content digest")
            for field in ("physical_yukawas_available", "full_cone_matter_corrections_computed")
        ),
        *tuple(
            ("alternate-down-higgs-hom-class-v1", field,
             "the down-Higgs Hom input changed its expected content digest")
            for field in (
                "higgs_exterior_cocycle_constructed", "complete_down_matrix_available",
                "complete_charged_lepton_matrix_available", "extension_point_selected",
            )
        ),
        *tuple(
            ("alternate-neutrino-mixed-pairing-v1", field,
             "the actual neutrino witnesses changed their trusted scope or inputs")
            for field in (
                "complete_holomorphic_neutrino_matrix_available",
                "physical_yukawa_matrix_available", "majorana_mechanism_derived",
                "observational_inputs_used",
            )
        ),
        *tuple(
            ("alternate-metric-global-weight-bound-v1", field,
             "the global auxiliary weight bound or its scope is not certified")
            for field in (
                "point_grid_used_as_proof", "practical_sampling_cost_certified",
                "controlled_numerical_sampling_available",
                "complete_global_input_coverage_certified",
                "matrix_integrand_bounds_available", "numerical_metrics_available",
                "physical_yukawas_available", "physical_kahler_class_selected", "vacuum_selected",
                "observational_inputs_used",
            )
        ),
        *tuple(
            ("alternate-metric-bounded-matrix-v1", field,
             "completed output differs from the trusted execution digest")
            for field in (
                "independent_all_column_full_cochain_replay_performed",
                "practical_multi_point_integration_throughput_certified",
                "bounded_section_and_density_evaluation_available",
                "controlled_numerical_sampling_available", "numerical_metrics_available",
                "physical_yukawas_available", "centers_are_exact_cover_points",
                "extension_point_selected", "vacuum_selected", "observational_inputs_used",
            )
        ),
        *tuple(
            ("alternate-metric-projection-free-weights-v1", field,
             "the projection-free weights or their scientific scope are not certified")
            for field in (
                "individual_projection_inverses_required", "all_triangle_node_inputs_certified",
                "complete_global_input_coverage_certified",
                "quantitative_global_weight_bound_available",
                "controlled_numerical_sampling_available", "numerical_metrics_available",
                "physical_yukawas_available", "vacuum_selected", "observational_inputs_used",
            )
        ),
        *tuple(
            ("alternate-metric-critical-charts-v1", field,
             "the declared critical charts or their scientific scope is not certified")
            for field in (
                "all_triangle_node_inputs_certified", "complete_global_atlas_coverage_certified",
                "quantitative_global_weight_bound_available",
                "controlled_numerical_sampling_available", "numerical_metrics_available",
                "physical_yukawas_available", "physical_kahler_class_selected", "vacuum_selected",
                "observational_inputs_used",
            )
        ),
        *tuple(
            ("alternate-metric-positive-measure-v1", field,
             "the positive auxiliary law or its scientific scope is not certified")
            for field in (
                "quantitative_global_weight_bound_available",
                "critical_fiber_chart_enclosures_available",
                "controlled_numerical_sampling_available", "numerical_metrics_available",
                "physical_yukawas_available", "physical_kahler_class_selected", "vacuum_selected",
                "observational_inputs_used",
            )
        ),
        *tuple(
            ("alternate-metric-weight-moments-v1", field,
             "the actual weight integrability or its scientific scope is not certified")
            for field in (
                "weight_third_moment_finite", "quantitative_variance_bound_available",
                "standard_finite_third_absolute_moment_error_bound_applicable_to_weight",
                "controlled_numerical_sampling_available", "numerical_metrics_available",
                "physical_yukawas_available", "vacuum_selected", "observational_inputs_used",
            )
        ),
        (
            "alternate-metric-bounded-support-v1",
            "complete_bounded_5345_column_matrix_materialized",
            "bounded original support evaluation or its scope is not certified",
        ),
        (
            "alternate-metric-bounded-support-v1",
            "practical_multi_point_integration_throughput_certified",
            "bounded original support evaluation or its scope is not certified",
        ),
        (
            "alternate-metric-bounded-support-v1",
            "bounded_section_and_density_evaluation_available",
            "bounded original support evaluation or its scope is not certified",
        ),
        (
            "alternate-metric-bounded-support-v1", "controlled_numerical_sampling_available",
            "bounded original support evaluation or its scope is not certified",
        ),
        (
            "alternate-metric-bounded-support-v1", "numerical_metrics_available",
            "bounded original support evaluation or its scope is not certified",
        ),
        (
            "alternate-metric-bounded-fibers-v1",
            "complete_bounded_5345_column_matrix_materialized",
            "bounded universal fibers or their scientific scope are not certified",
        ),
        (
            "alternate-metric-bounded-fibers-v1",
            "compressed_complete_section_enclosure_engine_available",
            "bounded universal fibers or their scientific scope are not certified",
        ),
        (
            "alternate-metric-bounded-fibers-v1",
            "bounded_section_and_density_evaluation_available",
            "bounded universal fibers or their scientific scope are not certified",
        ),
        (
            "alternate-metric-bounded-fibers-v1", "controlled_numerical_sampling_available",
            "bounded universal fibers or their scientific scope are not certified",
        ),
        (
            "alternate-metric-bounded-fibers-v1", "numerical_metrics_available",
            "bounded universal fibers or their scientific scope are not certified",
        ),
        (
            "alternate-metric-enclosures-v1", "bounded_universal_fiber_frame_available",
            "local enclosure inputs or their scientific scope are not certified",
        ),
        (
            "alternate-metric-enclosures-v1", "centers_are_exact_cover_points",
            "local enclosure inputs or their scientific scope are not certified",
        ),
        (
            "alternate-metric-enclosures-v1", "bounded_section_and_density_evaluation_available",
            "local enclosure inputs or their scientific scope are not certified",
        ),
        (
            "alternate-metric-enclosures-v1", "controlled_numerical_sampling_available",
            "local enclosure inputs or their scientific scope are not certified",
        ),
        (
            "alternate-metric-enclosures-v1", "numerical_metrics_available",
            "local enclosure inputs or their scientific scope are not certified",
        ),
        (
            "alternate-metric-projective-roots-v1", "centers_are_exact_cover_points",
            "certified projective roots or their scientific scope is not certified",
        ),
        (
            "alternate-metric-projective-roots-v1", "projective_uniform_sampling_law_implemented",
            "certified projective roots or their scientific scope is not certified",
        ),
        (
            "alternate-metric-projective-roots-v1",
            "bounded_section_and_density_evaluation_available",
            "certified projective roots or their scientific scope is not certified",
        ),
        (
            "alternate-metric-projective-roots-v1", "numerical_metrics_available",
            "certified projective roots or their scientific scope is not certified",
        ),
        (
            "alternate-metric-measure-v1", "controlled_numerical_sampling_available",
            "exact geometric measure or its scientific scope is not certified",
        ),
        (
            "alternate-metric-measure-v1", "numerical_metrics_available",
            "exact geometric measure or its scientific scope is not certified",
        ),
        (
            "alternate-metric-measure-v1", "vacuum_selected",
            "exact geometric measure or its scientific scope is not certified",
        ),
        (
            "alternate-metric-specialized-evaluation-v1", "numerical_metrics_available",
            "complete exact section evaluation or scope is not certified",
        ),
        (
            "alternate-metric-specialized-evaluation-v1", "controlled_numerical_sampling_available",
            "complete exact section evaluation or scope is not certified",
        ),
        (
            "alternate-metric-fiber-evaluation-v1", "numerical_metrics_available",
            "actual local rank-four fiber evaluation or scope is not certified",
        ),
        (
            "alternate-metric-fiber-evaluation-v1",
            "complete_5345_column_point_matrix_materialized",
            "actual local rank-four fiber evaluation or scope is not certified",
        ),
        (
            "alternate-up-higgs-quotient-cone-v1", "quotient_is_a_vector_bundle",
            "actual alternate Higgs quotient cone is not certified",
        ),
        (
            "alternate-up-first-order-scalar-screen-v1", "physical_null_coefficients_computed",
            "complete ordered alternate null scalar screens are not certified",
        ),
        (
            "alternate-up-quotient-equivariance-v1", "physical_pairing_chain_map_constructed",
            "inherited alternate quotient equivariance is not certified",
        ),
        (
            "alternate-up-pairing-exchange-v1", "physical_higgs_identification_certified",
            "actual alternate pairing exchange screen is not certified",
        ),
        (
            "alternate-up-null-line-homotopies-v1", "complete_comparison_indeterminacy_eliminated",
            "actual null line homotopies and ambiguity groups are not certified",
        ),
        (
            "alternate-up-exterior-boundary-attack-v1", "natural_product_comparison_certified",
            "scoped exterior boundary counterexample and repair are not certified",
        ),
        (
            "alternate-up-syzygy-tensor-comparison-v1", "complete_tensor_comparison_certified",
            "actual syzygy tensor comparison and scope are not certified",
        ),
        (
            "alternate-up-coupled-tensor-comparison-v1", "full_carrier_scalar_pairing_evaluated",
            "actual coupled quotient tensor comparison and scope are not certified",
        ),
        (
            "alternate-up-quotient-trace-v1", "physical_null_coefficient_assigned",
            "actual scalar descent and explicit quotient trace are not certified",
        ),
        (
            "alternate-up-mixed-quotient-pairing-v1", "second_second_entries_assigned",
            "actual Higgs-first mixed quotient entries are not certified",
        ),
        (
            "alternate-up-coupled-null-scalar-v1", "complete_holomorphic_up_matrix_available",
            "complete natural null contraction and its scope are not certified",
        ),
        (
            "alternate-up-ff-entry-v1", "physical_yukawa_matrix_available",
            "an exact a0 F-F scalar entry or archive is not certified",
        ),
        (
            "alternate-up-ff-coefficient-v1", "complete_holomorphic_up_matrix_available",
            "the complete exact a0 F-F block and natural null check are not certified",
        ),
        (
            "alternate-metric-first-resolution-ambient-sections-v1",
            "first_constituent_section_basis_available",
            "the actual ambient resolution sections or scope are not certified",
        ),
        (
            "alternate-metric-first-quotient-sections-v1", "serre_lifts_constructed",
            "the actual first Serre quotient basis or scope is not certified",
        ),
        (
            "alternate-metric-first-serre-lifts-v1", "rank_four_section_basis_available",
            "the actual complete first-constituent section basis is not certified",
        ),
        (
            "alternate-metric-second-sections-v1", "rank_four_section_basis_available",
            "the actual complete second-constituent section basis is not certified",
        ),
        (
            "alternate-metric-outer-lift-formula-v1", "rank_four_section_basis_available",
            "the finite universal outer lifting formula or scope is not certified",
        ),
        (
            "alternate-metric-lift-operator-certificate-v1", "physical_yukawas_available",
            "the independent universal lift operator certificate is not certified",
        ),
    ),
)
def test_audit_rejects_scope_inflation_even_with_a_recomputed_digest(
    monkeypatch: pytest.MonkeyPatch, schema: str, field: str, error: str,
) -> None:
    """A valid content hash cannot turn an ideal or a screen into physics."""

    original = json.loads

    def inflated_loads(text: str) -> object:
        record = original(text)
        if isinstance(record, dict) and record.get("schema") == schema:
            record.pop("artifact_digest")
            record[field] = True
            record["artifact_digest"] = audit._canonical_digest(record)
        return record

    monkeypatch.setattr(audit.json, "loads", inflated_loads)
    with pytest.raises(ValueError, match=error):
        build_state()


@pytest.mark.parametrize(
    "schema,field,error",
    (
        (
            "alternate-up-ff-entry-v1", "physical_yukawa_matrix_available",
            "an exact a1 F-F scalar entry or archive is not certified",
        ),
        (
            "alternate-up-ff-coefficient-v1", "complete_holomorphic_up_matrix_available",
            "the complete exact a1 F-F block and natural null check are not certified",
        ),
    ),
)
def test_a1_producer_archives_cannot_claim_a_physical_or_complete_matrix(
    monkeypatch: pytest.MonkeyPatch, schema: str, field: str, error: str,
) -> None:
    """A coefficient archive cannot claim the matrix assembled above it."""

    original = json.loads

    def inflated_loads(text: str) -> object:
        record = original(text)
        if (isinstance(record, dict) and record.get("schema") == schema
                and record.get("parameter") == "a1"):
            record.pop("artifact_digest")
            record[field] = True
            record["artifact_digest"] = audit._canonical_digest(record)
        return record

    monkeypatch.setattr(audit.json, "loads", inflated_loads)
    with pytest.raises(ValueError, match=error):
        build_state()


@pytest.mark.parametrize("field", (
    "physical_yukawa_matrix_available", "canonical_matter_metrics_available",
    "common_vacuum_stabilized", "extension_point_selected",
    "observational_inputs_used",
))
def test_full_holomorphic_matrix_cannot_claim_physical_scope(
    monkeypatch: pytest.MonkeyPatch, field: str,
) -> None:
    """A fresh hash cannot turn the conditional matrix into a prediction."""

    original = json.loads

    def inflated_loads(text: str) -> object:
        record = original(text)
        if isinstance(record, dict) and record.get("schema") == (
            "alternate-up-full-holomorphic-matrix-v1"
        ):
            record.pop("artifact_digest")
            record[field] = True
            record["artifact_digest"] = audit._canonical_digest(record)
        return record

    monkeypatch.setattr(audit.json, "loads", inflated_loads)
    with pytest.raises(ValueError, match="complete alternate holomorphic matrix or its scope"):
        build_state()


@pytest.mark.parametrize("field", (
    "global_generation_of_constituents_certified", "numerical_metrics_available",
))
def test_vanishing_artifact_cannot_claim_a_metric_gate(
    monkeypatch: pytest.MonkeyPatch, field: str,
) -> None:
    """One vanishing proof cannot certify section evaluation or metrics."""

    original = json.loads

    def inflated_loads(text: str) -> object:
        record = original(text)
        if isinstance(record, dict) and record.get("schema") == (
            "alternate-metric-subbundle-vanishing-v1"
        ):
            record.pop("artifact_digest")
            record[field] = True
            record["artifact_digest"] = audit._canonical_digest(record)
        return record

    monkeypatch.setattr(audit.json, "loads", inflated_loads)
    with pytest.raises(ValueError, match="alternate metric subbundle vanishing or its scope"):
        build_state()


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
    assert claims["alternate_up_mixed_scalar_trace"]["status"] == "COMPUTED"
    assert claims["alternate_up_rank_floor"]["status"] == "DERIVED"
    assert claims["alternate_up_null_channel"]["status"] == "COMPUTED"
    assert claims["alternate_up_dual_higgs_inputs"]["status"] == "COMPUTED"
    assert claims["alternate_up_exterior_higgs_action"]["status"] == "COMPUTED"
    assert claims["alternate_up_higgs_quotient_cone"]["status"] == "COMPUTED"
    assert claims["alternate_up_first_order_scalar"]["status"] == "COMPUTED"
    assert claims["alternate_up_quotient_equivariance"]["status"] == "COMPUTED"
    assert claims["alternate_up_pairing_exchange"]["status"] == "COMPUTED"
    assert claims["alternate_up_null_line_homotopies"]["status"] == "COMPUTED"
    assert path["criteria"]["alternate_up_ordered_exterior_products_closed"] is True
    assert path["criteria"]["alternate_up_reciprocal_exterior_primitives_verified"] is True
    assert path["criteria"]["alternate_up_natural_quotient_cone_available"] is True
    assert path["criteria"]["alternate_up_null_tensor_projection_exact"] is True
    assert path["criteria"]["alternate_up_complete_ordered_null_screens_computed"] is True
    assert path["criteria"]["alternate_up_ordered_null_cover_residues"] == [
        "0", "2673/49-486/49*omega",
    ]
    assert path["criteria"]["alternate_up_ordered_null_a1_coefficient_nonzero"] is True
    assert path["criteria"]["alternate_up_inherited_quotient_equivariance_certified"] is True
    assert path["criteria"]["alternate_up_repaired_quotient_higgs_character"] == [0, 2]
    assert path["criteria"]["alternate_up_ordered_null_direct_trace_independently_verified"] is True
    assert path["criteria"]["alternate_up_ordered_exchange_screen_computed"] is True
    assert path["criteria"]["alternate_up_null_yoneda_line_homotopies_verified"] is True
    assert path["criteria"]["alternate_up_null_line_h0_to_h3"] == [0, 0, 9, 0]
    assert path["criteria"]["alternate_up_quotient_fixed_endpoint_map_ambiguity_dimension"] == 0
    assert path["criteria"]["alternate_up_quotient_K_h0_to_h3"] == [0, 5, 5, 0]
    assert path["criteria"]["alternate_up_quotient_matter_product_ambiguity_dimension"] == 5
    assert claims["alternate_up_exterior_boundary_attack"]["status"] == "REFUTED"
    assert claims["mixed_even_rank_one_tensor_homotopy"]["status"] == "DERIVED"
    assert path["criteria"]["alternate_up_raw_exterior_cup_all_input_chain_map_refuted"] is True
    assert path["criteria"]["alternate_up_even_tensor_boundary_repair_verified"] is True
    assert claims["mixed_graded_rank_one_tensor_comparison"]["status"] == "DERIVED"
    assert claims["product_cover_homotopy_strict_hirsch"]["status"] == "REFUTED"
    assert path["criteria"]["alternate_up_graded_rank_one_F_tensor_identity_derived"] is True
    assert path["criteria"]["alternate_up_actual_syzygy_boundary_comparison_verified"] is True
    assert claims["mixed_schoen_hirsch_coherence"]["status"] == "DERIVED"
    assert claims["mixed_coupled_quotient_tensor_identity"]["status"] == "DERIVED"
    assert claims["alternate_up_coupled_tensor_presentation"]["status"] == "COMPUTED"
    assert claims["mixed_coupled_vertex_comparison"]["status"] == "DERIVED"
    assert claims["alternate_up_canonical_quotient_product"]["status"] == "DERIVED"
    assert claims["alternate_up_quotient_trace"]["status"] == "COMPUTED"
    assert claims["alternate_up_same_higgs_class"]["status"] == "DERIVED"
    assert claims["alternate_up_mixed_quotient_pairing"]["status"] == "COMPUTED"
    assert claims["alternate_up_coupled_null_pairing"]["status"] == "COMPUTED"
    assert path["criteria"]["alternate_up_first_slot_cover_coherence_derived"] is True
    assert path["criteria"]["alternate_up_coupled_outer_tensor_comparison_available"] is True
    assert path["criteria"]["alternate_up_local_vertex_tensor_comparison_available"] is True
    assert path["criteria"]["alternate_up_canonical_quotient_sheaf_product_identified"] is True
    assert path["criteria"]["alternate_up_scalar_class_descent_certified"] is True
    assert path["criteria"]["alternate_up_explicit_quotient_trace_constructed"] is True
    assert path["criteria"]["alternate_up_cover_to_quotient_trace_factor"] == "1/9"
    assert path["criteria"]["alternate_up_same_higgs_class_identified"] is True
    assert path["criteria"]["alternate_up_higgs_first_constant_mixed_entries_computed"] is True
    assert path["criteria"]["alternate_up_complete_carrier_scalar_pairing_evaluated"] is True
    assert path["criteria"]["alternate_up_natural_null_cover_residues"] == [
        "0", "2673/49-486/49*omega",
    ]
    assert path["criteria"]["alternate_up_complete_tensor_comparison_available"] is False
    assert path["criteria"]["alternate_up_complete_comparison_indeterminacy_eliminated"] is False
    exchange = json.loads((STATE.parent / "alternate_up_pairing_exchange.json").read_text())
    assert path["criteria"]["alternate_up_ordered_exchange_consistent"] == all(
        item["reverse_scalar_closed_exact"] and item["exchange_difference_boundary_exact"]
        for item in exchange["parameter_coefficients"]
    )
    assert path["criteria"]["alternate_up_ordered_reverse_null_cover_residues"] == [
        item["reverse_cover_residue"] for item in exchange["parameter_coefficients"]
    ]
    assert path["criteria"]["alternate_up_full_higgs_cone_comparison_available"] is False
    assert path["criteria"]["alternate_up_null_to_null_coefficients_computed"] is False
    assert path["selection_status"] == (
        "the selected P1 and reverse P5 physical quotient freezes are "
        "refuted; the distinct determinant-repaired alternate P1 "
        "component passes the charged structural spectrum and is "
        "frozen only for chain-level physics"
    )
    assert path["next_required_object"] == (
        "close controlled independent metric integration with original complete "
        "section data, verify Ricci-flat/HYM convergence and stabilize one common "
        "vacuum before physical Yukawa normalization; Genesis-to-UV remains unresolved"
    )
    assert path["criteria"][
        "alternate_metric_exact_residue_and_auxiliary_measure_available"
    ] is True
    assert path["criteria"]["alternate_metric_controlled_numerical_sampling_available"] is False
    assert claims["alternate_metric_measure"]["status"] == "COMPUTED"
    assert claims["alternate_metric_projective_roots"]["status"] == "COMPUTED"
    assert claims["alternate_metric_enclosures"]["status"] == "COMPUTED"
    assert claims["alternate_metric_bounded_fibers"]["status"] == "COMPUTED"
    assert claims["alternate_metric_bounded_support"]["status"] == "COMPUTED"
    assert claims["uncertain_cover_frames"]["status"] == "COMPUTED"
    assert claims["uncertain_cover_frames"]["missing_prerequisites"] == []
    domains = state["uncertain_cover_frames"]
    assert domains["uncertain_center_bits"] == domains["bound_bits"] == 100
    assert len(domains["actual_domain_probes"]) == 15
    assert domains["complete_5345_column_matrix_on_new_domains_available"] is False
    assert domains["independent_sampling_cloud_available"] is False
    assert domains["controlled_integral_available"] is False
    assert domains["physical_yukawas_available"] is False
    assert claims["alternate_metric_weight_moments"]["status"] == "DERIVED"
    assert claims["alternate_metric_positive_measure"]["status"] == "DERIVED"
    assert claims["alternate_metric_critical_charts"]["status"] == "COMPUTED"
    assert claims["alternate_metric_projection_free_weights"]["status"] == "DERIVED"
    assert path["criteria"][
        "alternate_metric_projection_free_positive_weight_engine_available"
    ] is True
    assert path["criteria"][
        "alternate_metric_weight_individual_projection_inverses_required"
    ] is False
    assert path["criteria"][
        "alternate_metric_complete_global_weight_input_coverage_certified"
    ] is False
    assert path["criteria"][
        "alternate_metric_declared_critical_fiber_chart_enclosures_available"
    ] is True
    assert path["criteria"]["alternate_metric_complete_global_atlas_coverage_certified"] is False
    assert path["criteria"]["alternate_metric_positive_auxiliary_law_derived"] is True
    assert path["criteria"]["alternate_metric_positive_law_ideal_weight_globally_bounded"] is True
    assert path["criteria"][
        "alternate_metric_positive_law_quantitative_global_bound_available"
    ] is True
    assert claims["alternate_metric_global_weight_bound"]["status"] == "DERIVED"
    assert path["criteria"][
        "alternate_metric_positive_law_quantitative_ideal_weight_variance_bound_available"
    ] is True
    assert path["criteria"]["alternate_metric_critical_fiber_chart_enclosures_available"] is False
    assert path["criteria"]["alternate_metric_weight_second_moment_finite"] is True
    assert path["criteria"]["alternate_metric_weight_third_moment_finite"] is False
    assert path["criteria"]["alternate_metric_quantitative_variance_bound_available"] is False
    assert claims["alternate_metric_bounded_matrix"]["status"] == "COMPUTED"
    assert claims["alternate_metric_bounded_matrix"]["missing_prerequisites"] == []
    assert path["criteria"][
        "alternate_metric_certified_chart_and_density_enclosures_available"
    ] is True
    assert path["criteria"][
        "alternate_metric_bounded_universal_fiber_frame_available"
    ] is True
    assert path["criteria"][
        "alternate_metric_compressed_complete_section_enclosure_engine_available"
    ] is True
    assert path["criteria"][
        "alternate_metric_practical_multi_point_integration_throughput_certified"
    ] is False
    assert path["criteria"][
        "alternate_metric_complete_bounded_5345_column_matrix_materialized"
    ] is True
    assert path["criteria"][
        "alternate_metric_certified_Qomega_intersection_roots_available"
    ] is True
    assert path["criteria"][
        "alternate_metric_bounded_section_and_density_evaluation_available"
    ] is False
    assert claims["visible_metrics"]["status"] == "BLOCKED"
    assert path["criteria"]["alternate_up_holomorphic_matrix_available"] is True
    assert path["criteria"]["alternate_up_holomorphic_rank_three_locus"] == "a1 != 0"
    assert path["criteria"]["alternate_up_physical_yukawa_matrix_available"] is False
    assert claims["alternate_up_ff_block"]["status"] == "COMPUTED"
    assert claims["first_exact_yukawa"]["status"] == "COMPUTED"
    assert claims["alternate_metric_generation_reduction"]["status"] == "PROVED"
    assert claims["alternate_metric_subbundle_vanishing"]["status"] == "COMPUTED"
    assert path["criteria"]["alternate_metric_subbundle_h1_vanishing"] is True
    assert path["criteria"]["alternate_metric_first_constituent_cover_generated"] is True
    assert claims["alternate_metric_quotient_generation"]["status"] == "PROVED"
    assert claims["alternate_metric_first_subline_sections"]["status"] == "COMPUTED"
    assert path["criteria"]["alternate_metric_large_generating_twist"] == [14, 16, 1]
    assert path["criteria"]["alternate_metric_quotient_section_count"] == 5345
    assert path["criteria"]["alternate_metric_first_subline_basis_count"] == 1115
    assert claims["alternate_metric_first_resolution_ambient_sections"]["status"] == "COMPUTED"
    assert path["criteria"]["alternate_metric_first_resolution_ambient_generator_counts"] == [
        13338, 7524,
    ]
    assert claims["alternate_metric_first_quotient_sections"]["status"] == "COMPUTED"
    assert path["criteria"]["alternate_metric_first_serre_quotient_basis_count"] == 1540
    assert claims["alternate_metric_first_serre_lifts"]["status"] == "COMPUTED"
    assert path["criteria"]["alternate_metric_first_serre_lifts_remaining_count"] == 0
    assert path["criteria"]["alternate_metric_first_constituent_section_basis_count"] == 2655
    assert path["criteria"]["alternate_metric_first_constituent_section_basis_available"] is True
    assert claims["alternate_metric_second_sections"]["status"] == "COMPUTED"
    assert path["criteria"]["alternate_metric_second_constituent_section_basis_count"] == 2690
    assert path["criteria"]["alternate_metric_second_constituent_section_basis_available"] is True
    assert path["criteria"]["alternate_metric_constituent_section_bases_available"] is True
    assert path["criteria"]["alternate_metric_rank_four_quotient_lifts_remaining_count"] == 0
    assert claims["alternate_metric_outer_lift_formula"]["status"] == "DERIVED"
    assert claims["alternate_metric_lift_operator_certificate"]["status"] == "DERIVED"
    assert path["criteria"]["alternate_metric_universal_section_constructor_available"] is True
    assert path["criteria"]["alternate_metric_full_lift_formula_independently_certified"] is True
    assert path["criteria"]["alternate_metric_full_independent_rank_four_replay_completed"] is False
    assert path["criteria"]["alternate_metric_constituents_globally_generated"] is True
    assert path["criteria"]["alternate_metric_rank_four_globally_generated"] is True
    assert path["criteria"]["alternate_metric_explicit_invariant_basis_available"] is True
    assert claims["alternate_metric_fiber_evaluation"]["status"] == "COMPUTED"
    assert path["criteria"]["alternate_metric_local_rank_four_evaluation_available"] is True
    assert path["criteria"][
        "alternate_metric_complete_point_evaluation_matrix_materialized"
    ] is True
    assert claims["alternate_metric_specialized_evaluation"]["status"] == "COMPUTED"
    assert path["criteria"]["alternate_metric_controlled_numerical_sampling_available"] is False
    assert claims["visible_metrics"]["status"] == "BLOCKED"
    assert "controlled numerical full-basis evaluation and metric sampling" in (
        claims["visible_metrics"]["missing_prerequisites"]
    )
    assert claims["physical_yukawas"]["status"] == "BLOCKED"
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
    assert scheduler[0]["task"] == "alternate_metric_convergence"
    assert claims["alternate_neutrino_mixed_pairing"]["status"] == "COMPUTED"
    assert claims["alternate_neutrino_matrix"]["status"] == "COMPUTED"
    assert claims["alternate_down_lepton_matter"]["status"] == "COMPUTED"
    assert claims["alternate_down_higgs_quotient_cone"]["status"] == "COMPUTED"
    assert claims["alternate_down_lepton_mixed_pairing"]["status"] == "COMPUTED"
    assert claims["alternate_down_lepton_matrices"]["status"] == "COMPUTED"
    assert claims["alternate_down_lepton_matrices"]["missing_prerequisites"] == []
    assert claims["physical_yukawas"]["status"] == "BLOCKED"
    assert "all holomorphic Yukawa sectors" not in (
        claims["physical_yukawas"]["missing_prerequisites"]
    )
    assert claims["alternate_remaining_flavor_matter_lifts"]["status"] == "COMPUTED"
    assert claims["alternate_remaining_flavor_matter_lifts"]["missing_prerequisites"] == []
    assert len([path for path in claims["alternate_remaining_flavor_matter_lifts"]["evidence"]
                if path.startswith("data/generated/")]) == 16
    assert path["criteria"]["alternate_neutrino_constant_mixed_entry_count"] == 4
    assert path["criteria"]["alternate_down_lepton_constant_mixed_entry_count"] == 8
    assert path["criteria"]["alternate_down_lepton_mixed_blocks_available"] is True
    assert path["criteria"]["alternate_down_a0_archived_coefficient_count"] == 4
    assert path["criteria"]["alternate_down_a0_determinant_coefficient"] == "1/42-2/21*omega"
    assert path["criteria"]["alternate_down_lepton_scalar_archive_count"] == 16
    assert path["criteria"]["alternate_down_lepton_complete_scalar_source_set_available"] is True
    assert path["criteria"]["alternate_down_lepton_arithmetic_rank_coefficients"] == [
        ["1/42-2/21*omega", "-1/21-5/84*omega"],
        ["-1/84+1/21*omega", "-1/21-5/84*omega"],
    ]
    assert path["criteria"][
        "alternate_down_lepton_all_sixteen_fresh_entry_replays_complete"
    ] is True
    assert path["criteria"][
        "alternate_down_lepton_complete_holomorphic_matrices_available"
    ] is True
    assert path["criteria"]["alternate_all_four_holomorphic_sectors_available"] is True
    assert path["criteria"]["alternate_four_sector_common_rank_three_locus_nonempty"] is True
    assert len(path["criteria"]["alternate_four_sector_common_rank_three_locus"]) == 3
    assert path["criteria"]["alternate_down_lepton_physical_yukawa_matrices_available"] is False
    assert path["criteria"]["alternate_neutrino_complete_holomorphic_matrix_available"] is True
    assert path["criteria"]["alternate_neutrino_holomorphic_rank_three_locus"] == "a0 != 0"
    assert path["criteria"]["alternate_up_neutrino_common_rank_three_locus"] == "a0*a1 != 0"
    assert path["criteria"]["alternate_neutrino_majorana_mechanism_derived"] is False
    assert not {"alternate_physical_quotient_pairing", "alternate_complete_up_matrix",
                "lawful_carrier_global_generation", "certify_universal_metric_lift_formula",
                "rank_four_local_fiber_evaluation"
                } & {task["task"] for task in scheduler}
    assert state["fitted_inputs"] == []
