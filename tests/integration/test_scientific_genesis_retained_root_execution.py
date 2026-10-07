"""Check executed root acceleration without rerunning its costly geometry.

Owns:
    Independently pinned actual packets, original input identity, native root
    ancestry, full-basis consumption and local-only numerical interpretation.

Depends on:
    Completed retained-root benchmarks and their frozen producer sources.

Must not:
    Infer a population speedup, certified numerical agreement or physical
    convergence from two post-selected cases.

Phase 0:
    Executed research result checks; no physical result is exported.
"""

import hashlib
import json

import pytest

from research.experiments.scientific_genesis import retained_root_benchmark as module

DIGESTS = {
    526: "9611df5e2db00075ec7de54d4aa04d9080c8902b2c1256771f7f69790f40ad31",
    1360: "7afe1e86379cbb459cf93d9a6919a5788d5d6f5c5ba2b2b4e0262ee6546dfc5a",
}


def _actual(ordinal):
    record = json.loads(module.output_path(ordinal).read_bytes())
    assert record["artifact_digest"] == DIGESTS[ordinal]
    assert module.prior.full.cloud.inputs._digest({k: v for k, v in record.items()
        if k != "artifact_digest"}) == DIGESTS[ordinal]
    assert all(hashlib.sha256((module.prior.ROOT / path).read_bytes()).hexdigest() == digest
               for path, digest in record["source_files_sha256"].items())
    return record


@pytest.mark.parametrize("ordinal", tuple(DIGESTS))
def test_executed_finer_inputs_and_roots_keep_the_original_identity(ordinal):
    record, native = _actual(ordinal), module.read_native(ordinal)
    assert record["original_sample_digest"] == module.prior.SAMPLES[ordinal]
    assert record["original_history"] == native["original_history"]
    assert record["input_digest"] == native["input_digest"]
    assert record["sample_id"] == native["sample_id"]
    assert record["streams"] == native["streams"]
    assert len(record["streams"]) == 13
    fine = record["finer_history"]
    assert fine["address"] == native["history"][-1]["address"]
    assert fine["frame_policy"] == native["history"][-1]["frame_policy"]
    assert fine["fiber_basis_labels"] == native["history"][-1]["fiber_basis_labels"]
    assert fine["root_parent_retained"] is True
    assert fine["frame_parent_retained"] is True
    assert fine["status"] == "admitted"
    assert record["newton_steps_by_family"] == [[1, 1, 1]] * (2 if ordinal == 526 else 1)
    for mapping, family, saved in zip(record["independent_native_root_mappings"],
        fine["all_root_families"], native["history"][-1]["all_root_families"], strict=True):
        assert mapping["new_to_parent"] == [0, 1, 2]
        assert sorted(mapping["native_to_parent"]) == [0, 1, 2]
        assert family["binary_coefficients"] == saved["binary_coefficients"]


@pytest.mark.parametrize("ordinal", tuple(DIGESTS))
def test_actual_full_h1_curvature_agreement_remains_discovery_only(ordinal):
    record, native = _actual(ordinal), module.read_native(ordinal)
    fine = record["finer_history"]
    assert fine["curvature_status"] == "computed_discovery"
    assert fine["original_section_count"] == record["original_section_count"] == 5345
    assert record["h1_factor_digest"] == module.prior.nonunit.H1
    expected = fine["h1"]["trace_free_l1"] / native["history"][-1]["h1"]["trace_free_l1"] - 1
    assert fine["h1_relative_l1_difference_from_native_discovery"] == expected
    assert abs(expected) < 2e-5  # Observed regression, never a certified error bound.
    assert all(value > 0 for value in record["timings_seconds"].values())


@pytest.mark.parametrize("ordinal", tuple(DIGESTS))
def test_acceleration_does_not_promote_a_global_or_physical_result(ordinal):
    record = _actual(ordinal)
    for field in ("new_entropy_obtained", "checkpoint_replaced", "subdivision_fallback_used",
        "hybrid_or_subset_mean_available", "h1_rebuilt", "h2_executed",
        "numerical_error_bound_certified", "controlled_global_integral",
        "hym_convergence_established", "physical_yukawas_available", "observations_used"):
        assert record[field] is False
    assert "post-selected" in record["case_selection"]
    assert "full_population_tau_discovery" not in record


def test_live_ledger_freezes_local_refinement_and_keeps_global_physics_missing():
    from research.experiments.scientific_genesis import audit

    nodes, edges = audit._nodes(), audit._edges()
    claims = {node["id"]: node for node in nodes}
    assert claims["retained_curvature_resolution"]["status"] == "COMPUTED"
    assert claims["conditional_curvature_trace_constraint"]["status"] == "DERIVED"
    for identifier in ("retained_polarization_stability", "visible_metrics", "physical_yukawas"):
        assert claims[identifier]["status"] == "BLOCKED"
    packet = audit._retained_resolution_summary()
    assert packet["conditional_continuum_tau_upper_bound_exact"] == "9/2"
    assert len(packet["cases"]) == 2
    assert packet["controlled_global_integral"] is False
    task = next(item for item in audit._scheduler()
                if item["task"] == "alternate_metric_convergence")
    assert "Freeze the local precision ladder" in task["rationale"]
    assert "whole retained-population numerical resolution" in task["rationale"]
    state = {"claims": nodes, "dependencies": edges, "fitted_inputs": []}
    state["artifact_digest"] = audit._canonical_digest(state)
    audit.validate_state(state)
