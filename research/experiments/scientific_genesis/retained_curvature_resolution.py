"""Test input-resolution sensitivity of the retained H1 curvature spikes.

Owns:
    Same-captured-stream continuation of two explicitly post-selected diagnostic
    points, original-frame replay checks, and full-section H0/H1 first-jet output.

Depends on:
    The original cloud receipts, existing native root/frame continuation,
    frozen compiled sections, and the actual admitted full-basis H1 factor.

Must not:
    Redraw, replace old checkpoints, form a hybrid or subset integral, run H2,
    change the extension point, or claim controlled HYM or a continuum no-go.

Phase 0:
    Research discovery sensitivity experiment; physical metric gates stay closed.
"""

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

from . import connection_curvature_comparison as comparison

nonunit = comparison.nonunit
curvature = nonunit.curvature
full = curvature.full
ROOT = full.ROOT
LEVELS = (16, 20, 24)
SAMPLES = {
    526: "e2ac139f18d90c2b15b8858328faa18640c104eadccd761163bd1cf2710be188",
    1360: "edbd3a26f847a691ac5254367a235799cb5281dad30548d7daf14518a4b5aaf7",
}
NOTE = Path(__file__).with_name("RETAINED_CURVATURE_RESOLUTION_NOTE.md")


def output_path(ordinal):
    """Name only the declared diagnostic cases, never an old cloud checkpoint."""

    if type(ordinal) is not int or ordinal not in SAMPLES:
        raise ValueError("only the two declared post-selected diagnostic points are allowed")
    return full.OUTPUT.with_name(f"retained_curvature_resolution.sample_{ordinal:04d}.json")


def _sources():
    result = nonunit._sources()
    paths = (Path(__file__), NOTE, ROOT /
             "tests/integration/test_scientific_genesis_retained_curvature_resolution.py")
    result.update({str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in paths})
    return result


def check_original_geometry(replayed, saved):
    """Require literal reproduction of every saved root/frame geometric field.

    Kernel rows belong to the original cloud experiment, not to root/frame
    reconstruction. Every field emitted by the geometric history writer must
    match; a different disk, center, frame, weight bound or address is rejected.
    """

    if (saved.get("status") != "admitted" or saved.get("level") != LEVELS[0]
            or saved.get("kernel_status") != "computed_discovery"
            or saved.get("complete_original_sections_consumed") is not True
            or saved.get("floating_mantissa_bits") != 53
            or replayed.get("status") != "admitted"
            or any(saved.get(key) != value for key, value in replayed.items())
            or any(key not in replayed for key in (
                "coordinate_bounds", "all_root_families", "selected_branch", "address",
                "frame_policy", "draw_policy", "fiber_basis_labels", "relation_minor",
                "quotient_weight_without_pi_cubed", "root_parent_retained",
                "frame_parent_retained", "level", "component"))):
        raise ValueError("the original saved root/frame geometry did not reproduce exactly")


def _diagnostics(admission, consumer, parameters, form):
    """Consume all original first jets at this admitted center and fixed H1."""

    coordinates = [curvature.features._complex(coordinate.center)
                   for group in (admission.frame.point.x, admission.frame.point.u,
                                 admission.frame.point.p) for coordinate in group]
    values, jets, metric, residue_squared = consumer.evaluate(
        coordinates, parameters, source_signature=consumer.program.source_signature,
    )
    h0_values, h0_jets, _ = nonunit.refinement.constant_row_gauge(values, jets)
    h0 = curvature.trace_free_curvature(h0_values, h0_jets, metric)
    h1_values, h1_jets = nonunit.inverse_form_jets(
        form, values, jets, basis_digest=curvature.features.BASIS,
    )
    h1_values, h1_jets, _ = nonunit.refinement.constant_row_gauge(h1_values, h1_jets)
    h1 = curvature.trace_free_curvature(h1_values, h1_jets, metric)
    bounds = admission.weight.quotient_weight_without_pi_cubed
    omega_weight = math.pi**3 * float((bounds.lower + bounds.upper) / 2)
    reference_weight = omega_weight * 8 * np.linalg.det(metric).real / residue_squared
    if not math.isfinite(reference_weight) or reference_weight <= 0:
        raise ArithmeticError("the refined discovery reference weight is unresolved")
    return {"h0": h0, "h1": h1, "reference_volume_weight_discovery": float(reference_weight),
            "floating_mantissa_bits": 53, "original_section_count": 5345}


def run(ordinal, *, progress=None):
    """Replay level 16, then continue levels 20 and 24 without fresh entropy."""

    output = output_path(ordinal)
    if output.exists():
        raise FileExistsError("retain the original same-input resolution result")
    sources = _sources()
    h0 = comparison.baseline.read_profile(expected_digest=comparison.baseline.PROFILE)
    h1 = json.loads(nonunit.OUTPUT.read_bytes())
    if (h1.get("artifact_digest") != comparison.H1_PROFILE
            or full.cloud.inputs._digest({k: v for k, v in h1.items() if k != "artifact_digest"})
            != comparison.H1_PROFILE):
        raise ValueError("the terminal full-population H1 profile changed")
    comparison.validate_h1(h1, h0)
    request = full.read_request(expected_digest=curvature.PARENT_REQUEST)
    inputs = full.cloud.inputs.read_inputs(
        expected_digest=request["input_digest"], path=full.INPUTS,
    )
    saved = full._read_sample(request, inputs, ordinal)
    if (saved["artifact_digest"] != SAMPLES[ordinal]
            or [item["level"] for item in saved["history"]] != [LEVELS[0]]
            or request["policy"]["levels"] != list(LEVELS)):
        raise ValueError("the declared original sample or refinement schedule changed")
    _, form = nonunit.inverse.read_result(expected_request_digest=nonunit.H1_REQUEST,
                                         expected_digest=nonunit.H1)
    if form is None:
        raise ArithmeticError("the original full-basis H1 factor is unavailable")
    program = curvature.features.compile_features()
    consumer = curvature.FullSectionJets(program)
    parameters = tuple(curvature.features._complex(curvature.Eisenstein(Fraction(a), Fraction(b)))
                       for a, b in request["policy"]["parameters"])
    available = full.cloud.inputs.address(inputs, ordinal)
    geometry = full.cloud.draws.declared_policy()
    previous, history = None, []
    for level in LEVELS:
        address = full.cloud.roots.refinement_address(available, level)
        policy, work = full.cloud.roots.refinement_policy(
            level, first_frame=geometry.first, second_frame=geometry.second,
        )
        work["max_cells"] = request["policy"]["max_cells"]
        frame_policy = full.cloud.continuation.FramePolicy(
            (0, 0, 0), (0, 2), (0, 1, 2), 8 * level, curvature.Eisenstein(1), 9,
        )
        if previous is None:
            admission = full.cloud.continuation.admit_frame(
                full.cloud.roots.attempt_subdivision_draw(address, policy, **work), frame_policy,
            )
        else:
            admission = full.cloud.continuation.refine_frame(
                previous, address, policy, frame_policy, **work,
            )
        previous = admission
        item = full.cloud._history(admission, level)
        if level == LEVELS[0]:
            check_original_geometry(item, saved["history"][0])
        item["curvature_status"] = "unresolved"
        if isinstance(admission, full.cloud.continuation.AdmittedFrame):
            try:
                item.update(_diagnostics(admission, consumer, parameters, form))
                item["curvature_status"] = "computed_discovery"
                item["h0_relative_l1_change_from_original_discovery"] = (
                    item["h0"]["trace_free_l1"] / h0["points"][ordinal]["trace_free_l1"] - 1
                )
                item["h1_relative_l1_change_from_original_discovery"] = (
                    item["h1"]["trace_free_l1"] / h1["points"][ordinal]["trace_free_l1"] - 1
                )
            except (ArithmeticError, ValueError, np.linalg.LinAlgError) as error:
                item["curvature_reason"] = str(error)
        else:
            item["curvature_reason"] = admission.reason
        history.append(item)
        if progress:
            progress({"ordinal": ordinal, "level": level, "frame_status": item["status"],
                      "curvature_status": item["curvature_status"],
                      "h1_l1": item.get("h1", {}).get("trace_free_l1")})
    result = {"schema": "retained-curvature-resolution-v1", "source_files_sha256": sources,
              **full.cloud.inputs.sample_identity(inputs, ordinal),
              "original_sample_digest": saved["artifact_digest"], "role": saved["role"],
              "original_history": saved["history"],
              "cloud_request_digest": request["artifact_digest"],
              "input_digest": inputs["artifact_digest"],
              "h0_profile_digest": comparison.baseline.PROFILE,
              "h1_profile_digest": comparison.H1_PROFILE, "h1_factor_digest": nonunit.H1,
              "original_section_basis_digest": curvature.features.BASIS,
              "original_section_count": 5345, "levels": list(LEVELS),
              "work_cap_per_level": request["policy"]["max_cells"],
              "history": history, "original_geometry_reproduced_exactly": True,
              "case_selection": "post-selected large-curvature diagnostics; not blind or IID",
              "parameter_point_status": "SELECTED", "entropy_assumption_status": "ASSUMED",
              "new_entropy_obtained": False, "old_cloud_checkpoint_replaced": False,
              "hybrid_or_subset_integral_available": False, "h2_executed": False,
              "numerical_error_bound_certified": False,
              "cause_of_trace_discrepancy_established": False,
              "hym_convergence_established": False, "physical_yukawas_available": False,
              "common_stabilized_vacuum_available": False, "observations_used": False}
    if sources != _sources():
        raise ValueError("same-input resolution sources changed during execution")
    result["artifact_digest"] = full.cloud.inputs._digest(result)
    full._install_json(output, result)
    return result


if __name__ == "__main__":
    record = run(int(sys.argv[1]), progress=lambda item: print(json.dumps(item), flush=True))
    print(json.dumps({"ordinal": record["ordinal"], "artifact_digest": record["artifact_digest"]}),
          flush=True)
