"""Check complete reference curvature integrals against fixed topological targets.

Owns:
    Identity and scope checks of the executed all-point H0 refinement, independent
    complete-population summation, and volume/trace normalization diagnostics.

Depends on:
    The retained H0 profile and failed parent, actual determinant-repaired cone,
    exact ambient intersections, and explicit Chern-Weil conventions.

Must not:
    Calibrate weights to a target, drop original samples, change the live H1
    experiment, or convert discovery offsets into certified integration errors.

Phase 0:
    Research normalization diagnostics only; physical metric gates stay closed.
"""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

from . import row_scaled_trial_curvature as refinement

PROFILE = "7ac7eea055ba4cea2d818f72096a10e7f9969013da0c92c549d10935f7ea57c7"
CONE = "b7c4327d8c1ee197f431cf05eebb38f38746a2a4eaf21440ac4338b051ce3fca"
ROOT = refinement.curvature.full.ROOT
OUTPUT = refinement.OUTPUT.with_name("reference_curvature_normalization.json")
NOTE = Path(__file__).with_name("REFERENCE_CURVATURE_EXECUTION_NOTE.md")


def validate_profile(record):
    """Check every retained identity and every producer mean, not an admitted subset."""

    parent = refinement._parent()
    altered = {"artifact_digest", "schema", "source_files_sha256", "points",
               "unresolved_ordinals", "complete_original_workload_available"}
    if any(record.get(key) != value for key, value in parent.items() if key not in altered):
        raise ValueError("the original scientific scope or inputs changed")
    if (record.get("schema") != "row-scaled-original-trial-curvature-v1"
            or record.get("source_files_sha256") != refinement._sources()
            or record.get("raw_curvature_parent_digest") != refinement.PARENT
            or record.get("constant_local_gauge_policy") != "diag(1/max_j abs(S_ij(center)))"
            or record.get("complete_original_workload_available") is not True
            or record.get("unresolved_ordinals") != []
            or record.get("conditioning_guard_relaxed") is not False
            or record.get("gauge_is_physical_normalization") is not False
            or any(record.get(key) is not True for key in (
                "all_points_recomputed", "gauge_treated_as_constant_in_each_local_germ",
                "original_population_section_form_and_failed_profile_preserved"))):
        raise ValueError("the complete constant-frame refinement or scope changed")
    points = record.get("points")
    if not isinstance(points, list) or len(points) != 2048:
        raise ValueError("every original point is required for a reference integral")
    for point, original in zip(points, parent["points"], strict=True):
        if (any(point.get(key) != original[key] for key in (
                "ordinal", "role", "sample_artifact_digest", "address", "selected_branch",
                "frame_policy", "fiber_basis_labels"))
                or point.get("status") != "computed_discovery"):
            raise ValueError("an original point or declared role changed")
        eigenvalues = point["trace_free_eigenvalues"]
        scalars = [*eigenvalues, point["trace_free_l1"], point["trace_free_frobenius"],
                   point["twisted_curvature_trace"], point["hermiticity_residual"],
                   point["reference_volume_weight"], point["weighted_trace_free_l1"],
                   point["fiber_condition_number_discovery"]]
        scales = [float.fromhex(value) for value in point["row_gauge_divisors"]]
        if (len(eigenvalues) != 4 or len(scales) != 4
                or not all(math.isfinite(value) for value in (*scalars, *scales))
                or min(scales) <= 0 or point["reference_volume_weight"] <= 0
                or not 0 < point["fiber_condition_number_discovery"] <= 1e12
                or point["trace_free_l1"] < 0 or point["trace_free_frobenius"] < 0
                or point["hermiticity_residual"] < 0
                or not math.isclose(point["trace_free_l1"], math.fsum(map(abs, eigenvalues)),
                                    rel_tol=1e-14, abs_tol=1e-14)
                or point["weighted_trace_free_l1"] != point["reference_volume_weight"]
                * point["trace_free_l1"]):
            raise ValueError("a full-point reference diagnostic changed")
    volume = record["reference_quotient_volume"]
    tau = math.fsum(p["weighted_trace_free_l1"] for p in points) / (
        len(points) * 2 * math.pi * volume * 4
    )
    empirical_volume = math.fsum(p["reference_volume_weight"] for p in points) / len(points)
    roles = {role: math.fsum(p["weighted_trace_free_l1"] for p in points if p["role"] == role)
             / (sum(p["role"] == role for p in points) * 2 * math.pi * volume * 4)
             for role in ("training", "validation")}
    if (record.get("full_population_tau_discovery") != tau
            or record.get("empirical_reference_volume_discovery") != empirical_volume
            or record.get("role_tau_discovery") != roles):
        raise ValueError("an aggregate does not consume the entire original population")
    return record


def read_profile(*, expected_digest, path=refinement.OUTPUT):
    """Require the externally observed terminal digest, not a self-chosen checksum."""

    record = json.loads(path.read_bytes())
    if (expected_digest != PROFILE or record.get("artifact_digest") != PROFILE
            or refinement.curvature.full.cloud.inputs._digest({
                k: v for k, v in record.items() if k != "artifact_digest"
            }) != PROFILE):
        raise ValueError("the completed reference curvature execution changed")
    return validate_profile(record)


def normalization_targets():
    """Return the actual quotient volume and integral trace coefficient in units of pi.

    With F ordered dz wedge dbar z, c1(E)=[i tr F/(2 pi)]. Thus
    integral tr(Lambda F) omega^3/6 = 2 pi integral c1(E) omega^2/2.
    E=V tensor L_J has c1(E)=4J because the retained cone has trivial determinant.
    These targets do not depend on H or on a Ricci-flat representative.
    """

    path = ROOT / (
        "data/generated/scientific_genesis/alternate_constituent_outer_universal_cone.json"
    )
    cone = json.loads(path.read_bytes())
    if (cone.get("artifact_digest") != CONE
            or refinement.curvature.full.cloud.inputs._digest({
                k: v for k, v in cone.items() if k != "artifact_digest"
            }) != CONE or cone["rank"] != 4
            or cone["chern_classes"]["c1"] != ["0", "0", "0"]
            or cone["quotient_determinant_trivial_exact"] is not True):
        raise ValueError("the actual determinant-trivial cone changed")
    polarization = refinement.curvature.POLARIZATION
    cubic = Fraction(str(refinement.curvature.ambient_cover_triple(
        polarization, polarization, polarization,
    ))) / 9
    volume = cubic / 6
    trace_integral_pi_coefficient = 4 * cubic
    return {"quotient_volume_exact": str(volume), "quotient_j_cubed_exact": str(cubic),
            "twisted_c1_coordinates": [4 * x for x in polarization],
            "trace_integral_pi_coefficient_exact": str(trace_integral_pi_coefficient),
            "volume_average_trace_pi_coefficient_exact":
            str(trace_integral_pi_coefficient / volume)}


def run():
    """Record unadjusted diagnostic offsets, not a passed accuracy threshold."""

    if OUTPUT.exists():
        raise FileExistsError("retain the original reference normalization diagnostics")
    profile = read_profile(expected_digest=PROFILE)
    targets = normalization_targets()
    trace = math.fsum(p["reference_volume_weight"] * p["twisted_curvature_trace"]
                      for p in profile["points"]) / profile["sample_count"]
    volume = float(Fraction(targets["quotient_volume_exact"]))
    target_trace = math.pi * float(Fraction(targets["trace_integral_pi_coefficient_exact"]))
    paths = (Path(__file__), NOTE, ROOT /
             "tests/integration/test_scientific_genesis_reference_curvature_checks.py",
             Path(__file__).with_name("metric_polarization_scope.py"),
             ROOT / "src/onetheory/math/numbers.py", ROOT / "src/onetheory/math/polynomials.py",
             ROOT / ("data/generated/scientific_genesis/"
                     "alternate_constituent_outer_universal_cone.json"))
    sources = refinement._sources()
    sources.update({str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in paths})
    record = {"schema": "reference-curvature-normalization-discovery-v1",
              "source_files_sha256": sources, "profile_digest": PROFILE, "cone_digest": CONE,
              "sample_count": 2048, "all_original_points_retained": True,
              "reference_polarization": list(refinement.curvature.POLARIZATION),
              "primary_source": "https://arxiv.org/pdf/1103.3041",
              "normalization_targets": targets, "full_population_tau_discovery":
              profile["full_population_tau_discovery"],
              "empirical_reference_volume_discovery":
              profile["empirical_reference_volume_discovery"],
              "volume_relative_offset_discovery":
              profile["empirical_reference_volume_discovery"] / volume - 1,
              "weighted_trace_integral_discovery": trace,
              "trace_integral_relative_offset_discovery": trace / target_trace - 1,
              "weights_calibrated_to_topology": False, "old_validation_is_blind": False,
              "numerical_and_sampling_error_certified": False, "accuracy_threshold_passed": False,
              "hym_convergence_established": False, "physical_yukawas_available": False,
              "common_stabilized_vacuum_available": False}
    record["artifact_digest"] = refinement.curvature.full.cloud.inputs._digest(record)
    refinement.curvature.full._install_json(OUTPUT, record)
    return record


if __name__ == "__main__":
    print(json.dumps(run(), indent=2), flush=True)
