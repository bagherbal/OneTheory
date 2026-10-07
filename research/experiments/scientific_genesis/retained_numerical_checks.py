"""Compare numerical discovery with independent native same-input checks.

Owns:
    Four fixed retained ordinals chosen before their native finer calculations,
    actual native admission and full-section H0/H1 numerical comparisons.

Depends on:
    Original inputs, retained native root/frame certificates and the numerical
    discovery consumer; no source of new entropy or physical coefficients.

Must not:
    Select cases by their agreement, omit a failed case, tune the numerical
    policy to fit outcomes, or infer uniform error control from spot checks.

Phase 0:
    Independent-method discovery checks only; global accuracy stays unresolved.
"""

import hashlib
import json
import sys
from pathlib import Path
from time import perf_counter

import numpy as np

from . import retained_population_resolution as population

geometry, full = population.geometry, population.full
certified = geometry.certified
CASES = (17, 101, 1819, 1980)
NOTE = Path(__file__).with_name("RETAINED_NUMERICAL_CHECKS_NOTE.md")


def output_path(ordinal):
    if type(ordinal) is not int or ordinal not in CASES:
        raise ValueError("only the four predeclared independent-method cases are allowed")
    return full.OUTPUT.with_name(f"retained_numerical_checks.sample_{ordinal:04d}.json")


def _sources():
    result = population._sources()
    paths = (Path(__file__), Path(certified.__file__), NOTE, full.ROOT /
             "tests/integration/test_scientific_genesis_retained_numerical_checks.py")
    result.update({str(path.relative_to(full.ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in paths})
    return result


def run(ordinal, *, progress=None):
    output = output_path(ordinal)
    if output.exists():
        raise FileExistsError("retain the executed independent-method check")
    sources = _sources()
    original = full.read_request(expected_digest=population.curvature.PARENT_REQUEST)
    inputs = full.cloud.inputs.read_inputs(expected_digest=original["input_digest"],
                                          path=full.INPUTS)
    saved = full._read_sample(original, inputs, ordinal)
    if len(saved["history"]) != 1 or saved["history"][0]["level"] != 16:
        raise ValueError("this declared native restoration requires the original level-16 receipt")
    available = full.cloud.inputs.address(inputs, ordinal)
    frames = certified.draws.declared_policy()
    coarse_policy, _ = full.cloud.roots.refinement_policy(16, first_frame=frames.first,
                                                        second_frame=frames.second)
    draw = certified.restore_draw(full.cloud.roots.refinement_address(available, 16),
                                   coarse_policy, saved["history"][0])
    frame_policy = certified.continuation.FramePolicy((0, 0, 0), (0, 2), (0, 1, 2),
                                                      128, population.curvature.Eisenstein(1), 9)
    parent = certified.continuation.admit_frame(draw, frame_policy)
    if not isinstance(parent, certified.continuation.AdmittedFrame):
        raise ArithmeticError("the original retained native frame did not restore")
    restored = full.cloud._history(parent, 16)
    if any(saved["history"][0].get(k) != value for k, value in restored.items()):
        raise ValueError("the independent check changed original coarse geometry")
    fine_policy, _ = full.cloud.roots.refinement_policy(32, first_frame=frames.first,
                                                      second_frame=frames.second)
    start = perf_counter()
    finer_draw, steps = certified.refine_draw(draw,
        full.cloud.roots.refinement_address(available, 32), fine_policy, max_steps=8)
    finer_frame_policy = certified.continuation.FramePolicy((0, 0, 0), (0, 2), (0, 1, 2),
                                                            256, frame_policy.volume_scale, 9)
    admission = certified.continuation.admit_frame(finer_draw, finer_frame_policy, parent=parent)
    native_seconds = perf_counter() - start
    result = {"schema": "retained-numerical-check-v1", "source_files_sha256": sources,
        **full.cloud.inputs.sample_identity(inputs, ordinal), "role": saved["role"],
        "input_digest": inputs["artifact_digest"],
        "original_sample_digest": saved["artifact_digest"],
        "native_finer_history": full.cloud._history(admission, 32), "newton_steps": steps,
        "native_seconds": native_seconds, "status": "unresolved",
        "case_selection": "fixed ordinals chosen before independent native finer outcomes",
        "new_entropy_obtained": False, "old_checkpoint_replaced": False,
        "numerical_error_bound_certified": False, "global_accuracy_established": False,
        "hym_convergence_established": False, "physical_yukawas_available": False}
    if progress:
        progress({"ordinal": ordinal, "native_status": result["native_finer_history"]["status"],
                  "native_seconds": native_seconds})
    if not isinstance(admission, certified.continuation.AdmittedFrame):
        result["reason"] = admission.reason
    else:
        try:
            coordinates, weight, record = geometry.evaluate_geometry(
                available, saved["history"][0], bits=128, steps=8,
                residual_tolerance=1e-12, volume_scale=1, covering_degree=9)
            native_coordinates = [population.curvature.features._complex(c.center)
                for group in (admission.frame.point.x, admission.frame.point.u,
                              admission.frame.point.p) for c in group]
            interval = admission.weight.quotient_weight_without_pi_cubed
            result.update({"geometry_discovery": record,
                "coordinates_real_imag_discovery": [[c.real, c.imag] for c in coordinates],
                "maximum_relative_coordinate_difference_discovery": max(abs(a-b)/max(1, abs(b))
                    for a, b in zip(coordinates, native_coordinates, strict=True)),
                "native_weight_interval": [str(interval.lower), str(interval.upper)],
                "numerical_weight_discovery": weight})
            _, form = population.nonunit.inverse.read_result(
                expected_request_digest=population.nonunit.H1_REQUEST,
                expected_digest=population.nonunit.H1)
            if form is None:
                raise ArithmeticError("the full original H1 factor is unavailable")
            consumer = population.curvature.FullSectionJets(
                population.curvature.features.compile_features())
            parameters = (1, population.curvature.features._complex(
                population.curvature.Eisenstein(0, 1)))
            result["native_center_diagnostics_discovery"] = population.diagnostics(
                native_coordinates, float((interval.lower + interval.upper)/2),
                consumer, parameters, form)
            result["numerical_diagnostics_discovery"] = population.diagnostics(
                coordinates, weight, consumer, parameters, form)
            result["h1_relative_l1_difference_discovery"] = (
                result["numerical_diagnostics_discovery"]["h1"]["trace_free_l1"] /
                result["native_center_diagnostics_discovery"]["h1"]["trace_free_l1"] - 1)
            result["status"] = "computed_comparison"
        except (ArithmeticError, ValueError, np.linalg.LinAlgError) as error:
            result["reason"] = str(error)
    if sources != _sources():
        raise ValueError("the independent-method check sources changed during execution")
    result["artifact_digest"] = full.cloud.inputs._digest(result)
    full._install_json(output, result)
    return result


if __name__ == "__main__":
    record = run(int(sys.argv[1]), progress=lambda item: print(json.dumps(item), flush=True))
    print(json.dumps({"ordinal": record["ordinal"], "artifact_digest": record["artifact_digest"],
                      "status": record["status"], "coordinate_difference": record.get(
                          "maximum_relative_coordinate_difference_discovery"),
                      "h1_relative_difference": record.get("h1_relative_l1_difference_discovery"),
                      "reason": record.get("reason")}),
          flush=True)
