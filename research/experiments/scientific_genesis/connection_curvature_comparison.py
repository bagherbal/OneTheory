"""Compare complete retained H0 and H1 reference connection diagnostics.

Owns:
    A source- and identity-bound join of the two executed full populations,
    unadjusted residual/trace comparisons, and dominant-point diagnostic records.

Depends on:
    The independently checked H0 profile and exact topological targets, actual
    full-basis H1 curvature output, and their unchanged original sample receipts.

Must not:
    Select a subset mean, calibrate weights, infer continuum instability,
    execute H2, or interpret validation alone as physical metric convergence.

Phase 0:
    Research discovery comparison only; physical metric gates remain closed.
"""

import hashlib
import json
import math
from pathlib import Path

from . import nonunit_connection_curvature as nonunit
from . import reference_curvature_checks as baseline

H1_PROFILE = "aaf4d3388212bc08c7f98cde8308ca841a6864782e343409e53cd5d2d4789930"
OUTPUT = nonunit.OUTPUT.with_name("connection_curvature_comparison.json")
NOTE = Path(__file__).with_name("CONNECTION_CURVATURE_COMPARISON_NOTE.md")


def validate_h1(record, h0):
    """Retain all old identities, reference weights and scientific boundaries."""

    if (record.get("schema") != "full-original-nonunit-curvature-v1"
            or record.get("source_files_sha256") != nonunit._sources()
            or record.get("h1_digest") != nonunit.H1
            or record.get("h1_request_digest") != nonunit.H1_REQUEST
            or record.get("raw_h0_curvature_parent_digest") != nonunit.refinement.PARENT
            or record.get("complete_original_workload_available") is not True
            or record.get("unresolved_ordinals") != []
            or record.get("all_points_recomputed") is not True
            or record.get("finite_atomic_obstruction_preserved") is not True
            or record.get("gauge_treated_as_constant_in_each_local_germ") is not True
            or any(record.get(key) is not False for key in (
                "conditioning_guard_relaxed", "gauge_is_physical_normalization", "h2_executed",
                "h1_selected_using_curvature_or_validation", "admitted_subset_mean_available",
                "old_validation_is_blind", "numerical_and_sampling_error_certified",
                "reference_background_is_ricci_flat", "hym_convergence_established",
                "determinant_normalized_su4_metric_exported", "matter_or_higgs_metrics_available",
                "physical_yukawas_available", "common_stabilized_vacuum_available",
                "observations_used"))):
        raise ValueError("the complete H1 comparison or scientific boundary changed")
    if any(record.get(key) != h0[key] for key in (
        "cloud_request_digest", "cloud_manifest_digest", "input_digest",
        "original_section_basis_digest", "original_section_count", "parameter_point",
        "parameter_point_status", "entropy_assumption_status", "reference_polarization",
        "reference_quotient_volume", "reference_background", "numerical_policy", "sample_count",
    )):
        raise ValueError("a comparison requires the same complete population and geometry")
    if not isinstance(record.get("points"), list) or len(record["points"]) != 2048:
        raise ValueError("all original H1 points are required")
    for point, original in zip(record["points"], h0["points"], strict=True):
        if (any(point.get(key) != original[key] for key in (
                "ordinal", "role", "sample_artifact_digest", "address", "selected_branch",
                "frame_policy", "fiber_basis_labels", "reference_volume_weight"))
                or point.get("status") != "computed_discovery"
                or len(point["trace_free_eigenvalues"]) != 4
                or not all(math.isfinite(x) for x in point["trace_free_eigenvalues"])
                or not all(math.isfinite(point[key]) and point[key] >= 0 for key in (
                    "trace_free_l1", "twisted_curvature_trace", "weighted_trace_free_l1",
                    "trace_free_frobenius", "hermiticity_residual"))
                or not 0 < point["fiber_condition_number_discovery"] <= 1e12
                or point["weighted_trace_free_l1"] != point["reference_volume_weight"]
                * point["trace_free_l1"]):
            raise ValueError("an original H1 point, weight or finite diagnostic changed")
    volume = record["reference_quotient_volume"]
    points = record["points"]
    tau = math.fsum(p["weighted_trace_free_l1"] for p in points) / (
        2048 * 2 * math.pi * 4 * volume
    )
    roles = {role: math.fsum(p["weighted_trace_free_l1"] for p in points if p["role"] == role)
             / (sum(p["role"] == role for p in points) * 2 * math.pi * volume * 4)
             for role in ("training", "validation")}
    if (record.get("full_population_tau_discovery") != tau
            or record.get("role_tau_discovery") != roles
            or record.get("empirical_reference_volume_discovery")
            != h0["empirical_reference_volume_discovery"]):
        raise ValueError("the comparison must consume every original point without calibration")
    return record


def summarize(*, path=nonunit.OUTPUT):
    """Inspect immutable executed profiles without geometry replay or new entropy."""

    h0 = baseline.read_profile(expected_digest=baseline.PROFILE)
    h1 = json.loads(path.read_bytes())
    if (h1.get("artifact_digest") != H1_PROFILE
            or nonunit.curvature.full.cloud.inputs._digest({
                key: value for key, value in h1.items() if key != "artifact_digest"
            }) != H1_PROFILE):
        raise ValueError("the terminal H1 execution digest changed")
    validate_h1(h1, h0)
    numerator = math.fsum(p["weighted_trace_free_l1"] for p in h1["points"])
    targets = baseline.normalization_targets()
    trace = math.fsum(p["reference_volume_weight"] * p["twisted_curvature_trace"]
                      for p in h1["points"]) / 2048
    dominant = sorted(h1["points"], key=lambda p: p["weighted_trace_free_l1"], reverse=True)[:12]
    return {"h0_profile_digest": baseline.PROFILE, "h1_profile_digest": H1_PROFILE,
            "sample_count": 2048, "original_section_count": 5345,
            "all_original_identities_and_reference_weights_equal": True,
            "h0_tau_discovery": h0["full_population_tau_discovery"],
            "h1_tau_discovery": h1["full_population_tau_discovery"],
            "h1_over_h0_tau_discovery": h1["full_population_tau_discovery"] /
            h0["full_population_tau_discovery"], "h0_role_tau_discovery": h0["role_tau_discovery"],
            "h1_role_tau_discovery": h1["role_tau_discovery"],
            "empirical_reference_volume_discovery": h0["empirical_reference_volume_discovery"],
            "h1_trace_integral_discovery": trace, "h1_trace_target_relative_offset_discovery":
            trace / (float(targets["trace_integral_pi_coefficient_exact"]) * math.pi) - 1,
            "large_l1_point_count_discovery": sum(p["trace_free_l1"] > 1000 for p in h1["points"]),
            "dominant_points_discovery": [{"ordinal": p["ordinal"], "role": p["role"],
                "h1_l1": p["trace_free_l1"], "h0_l1": h0["points"][p["ordinal"]]["trace_free_l1"],
                "share_full_l1_numerator": p["weighted_trace_free_l1"] / numerator,
                "fiber_condition_number_discovery": p["fiber_condition_number_discovery"]}
                for p in dominant],
            "dominant_points_removed_from_mean": False, "weights_calibrated_to_topology": False,
            "whole_population_reference_residual_improves":
            h1["full_population_tau_discovery"] < h0["full_population_tau_discovery"],
            "cause_of_trace_discrepancy_established": False,
            "numerical_and_sampling_error_certified": False, "old_validation_is_blind": False,
            "continuum_instability_or_hym_no_go_proved": False, "h2_executed": False,
            "hym_convergence_established": False, "physical_yukawas_available": False,
            "common_stabilized_vacuum_available": False}


def run():
    """Record the complete failed improvement diagnostic, never a favorable subset."""

    if OUTPUT.exists():
        raise FileExistsError("retain the original complete H0-H1 comparison")
    record = {"schema": "complete-reference-curvature-comparison-v1", **summarize()}
    paths = (Path(__file__), NOTE, baseline.ROOT /
             "tests/integration/test_scientific_genesis_curvature_comparison.py")
    record["source_files_sha256"] = nonunit._sources()
    record["source_files_sha256"].update({str(path.relative_to(baseline.ROOT)):
        hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    record["source_files_sha256"][str(Path(baseline.__file__).relative_to(baseline.ROOT))] = (
        hashlib.sha256(Path(baseline.__file__).read_bytes()).hexdigest()
    )
    record["artifact_digest"] = nonunit.curvature.full.cloud.inputs._digest(record)
    nonunit.curvature.full._install_json(OUTPUT, record)
    return record


if __name__ == "__main__":
    print(json.dumps(run(), indent=2), flush=True)
