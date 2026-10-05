"""Execute a predeclared original-basis training and validation cloud.

Owns:
    Immutable public input requests, disjoint resumable worker shards, complete
    native frame histories and numerical rows, and full-workload aggregation.

Depends on:
    The frozen named-stream sampler, native root/frame controller, original
    sparse discovery evaluator and unit-H rank-four row factorization.

Must not:
    Replace failed samples, reduce the section basis, average an admitted subset,
    infer IID from entropy receipts, or report numerical kernels as HYM metrics.

Phase 0:
    Research discovery execution only; statistical and physical gates stay open.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from time import perf_counter

from onetheory.math.numbers import OMEGA, Eisenstein

from . import independent_trial_cloud as cloud

ROOT = cloud.features.exact.domains.ROOT
INPUTS = cloud.OUTPUT.with_name("full_trial_cloud_inputs.json")
REQUEST = cloud.OUTPUT.with_name("full_trial_cloud_request.json")
OUTPUT = cloud.OUTPUT.with_name("full_trial_cloud.json")
PROOF = Path(__file__).with_name("FULL_TRIAL_CLOUD_NOTE.md")
PILOT_DIGEST = "706b323d3d1860767e916755d7b982ec2bd9cc4e6a884d064e67d29b8094b10c"


def _sources():
    result = cloud._sources()
    for path in (Path(__file__), PROOF):
        result[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _install_json(path, record):
    """Install immutable calculation metadata, not a replacement checkpoint."""

    encoded = cloud.inputs._canonical(record) + b"\n"
    if path.exists():
        if path.read_bytes() != encoded:
            raise FileExistsError("preserve the existing original workload")
        return
    with path.open("xb") as stream:
        stream.write(encoded)


def create_request(*, count, training_count, bytes_per_stream, levels, max_cells):
    """Fix the entire workload and hold-out split before seeing any geometry."""

    if (
        type(count) is not int
        or type(training_count) is not int
        or not 1337 <= training_count < count
        or type(bytes_per_stream) is not int
        or bytes_per_stream < 16
        or type(levels) is not tuple
        or not levels
        or any(type(j) is not int or not 2 <= j <= 2 * bytes_per_stream for j in levels)
        or any(a >= b for a, b in zip(levels, levels[1:], strict=False))
        or type(max_cells) is not int
        or max_cells < 1
    ):
        raise ValueError("sufficient full-basis training count and explicit policies required")
    if REQUEST.exists() or INPUTS.exists():
        raise FileExistsError("retain the existing request; do not obtain replacement entropy")
    before = _sources()
    inputs = cloud.inputs.create_inputs(count=count, bytes_per_stream=bytes_per_stream, path=INPUTS)
    result = {
        "schema": "full-original-trial-cloud-request-v1",
        "input_digest": inputs["artifact_digest"],
        "sample_count": count,
        "training_count": training_count,
        "validation_count": count - training_count,
        "split_rule": "training ordinal < training_count; all remaining ordinals are validation",
        "split_fixed_before_geometry": True,
        "policy": {
            "levels": levels,
            "max_cells": max_cells,
            "parameters": [["1", "0"], ["0", "1"]],
            "stop_after_first_resolved_kernel": True,
            "chart": [0, 0, 0],
            "first_pivots": [0, 2],
            "second_pivots": [0, 1, 2],
            "residue_scale": ["1", "0"],
            "covering_degree": 9,
        },
        "original_section_basis_digest": cloud.features.BASIS,
        "compilation_parent_digest": cloud.features.COMPILATION,
        "pilot_parent_digest": PILOT_DIGEST,
        "source_files_sha256": before,
        "entropy_assumption_status": "ASSUMED",
        "parameter_point_status": "SELECTED",
        "parameter_point_role": "same unstabilized computational point as the frozen pilot",
        "section_form": "explicit unit H0 in the full original 5345-dimensional section basis",
        "observations_used": False,
    }
    if _sources() != before:
        raise ValueError("workload sources changed while capturing inputs")
    result["artifact_digest"] = cloud.inputs._digest(result)
    _install_json(REQUEST, result)
    return read_request(expected_digest=result["artifact_digest"])


def read_request(*, expected_digest, path=REQUEST):
    """Inspect a trusted workload without obtaining entropy or doing geometry."""

    result = json.loads(path.read_bytes())
    unsigned = {k: v for k, v in result.items() if k != "artifact_digest"}
    if (
        result.get("artifact_digest") != expected_digest
        or cloud.inputs._digest(unsigned) != expected_digest
    ):
        raise ValueError("the trusted original cloud request changed")
    policy = result["policy"]
    inputs = cloud.inputs.read_inputs(expected_digest=result["input_digest"], path=INPUTS)
    if (
        result["schema"] != "full-original-trial-cloud-request-v1"
        or result["sample_count"] != inputs["sample_count"]
        or type(result["training_count"]) is not int
        or not 1337 <= result["training_count"] < result["sample_count"]
        or result["validation_count"] != result["sample_count"] - result["training_count"]
        or result["split_fixed_before_geometry"] is not True
        or result["split_rule"]
        != ("training ordinal < training_count; all remaining ordinals are validation")
        or result["original_section_basis_digest"] != cloud.features.BASIS
        or result["compilation_parent_digest"] != cloud.features.COMPILATION
        or result["pilot_parent_digest"] != PILOT_DIGEST
        or result["source_files_sha256"] != _sources()
        or result["entropy_assumption_status"] != "ASSUMED"
        or result["parameter_point_status"] != "SELECTED"
        or result["parameter_point_role"]
        != ("same unstabilized computational point as the frozen pilot")
        or result["section_form"]
        != ("explicit unit H0 in the full original 5345-dimensional section basis")
        or result["observations_used"] is not False
        or policy["parameters"] != [["1", "0"], ["0", "1"]]
        or policy["stop_after_first_resolved_kernel"] is not True
        or policy["chart"] != [0, 0, 0]
        or policy["first_pivots"] != [0, 2]
        or policy["second_pivots"] != [0, 1, 2]
        or policy["residue_scale"] != ["1", "0"]
        or policy["covering_degree"] != 9
        or type(policy["max_cells"]) is not int
        or policy["max_cells"] < 1
        or not policy["levels"]
        or any(
            type(j) is not int or not 2 <= j <= 2 * inputs["bytes_per_stream"]
            for j in policy["levels"]
        )
        or any(a >= b for a, b in zip(policy["levels"], policy["levels"][1:], strict=False))
    ):
        raise ValueError("the original physical input, split, policy or scientific scope changed")
    return result


def _sample_path(ordinal):
    return OUTPUT.with_name(f"full_trial_cloud.sample_{ordinal:04d}.json.gz")


def _role(request, ordinal):
    return "training" if ordinal < request["training_count"] else "validation"


def process_sample(request, inputs, ordinal, program, *, progress=None):
    """Refine one original address; stop only after that sample's kernel resolves."""

    if type(ordinal) is not int or not 0 <= ordinal < request["sample_count"]:
        raise ValueError("an original request ordinal required")
    identity = cloud.inputs.sample_identity(inputs, ordinal)
    available = cloud.inputs.address(inputs, ordinal)
    geometric = cloud.draws.declared_policy()
    previous, history = None, []
    for level in request["policy"]["levels"]:
        address = cloud.roots.refinement_address(available, level)
        policy, work = cloud.roots.refinement_policy(
            level, first_frame=geometric.first, second_frame=geometric.second
        )
        work["max_cells"] = request["policy"]["max_cells"]
        frame_policy = cloud.continuation.FramePolicy(
            (0, 0, 0), (0, 2), (0, 1, 2), 8 * level, Eisenstein(1), 9
        )
        if previous is None:
            admission = cloud.continuation.admit_frame(
                cloud.roots.attempt_subdivision_draw(address, policy, **work), frame_policy
            )
        else:
            admission = cloud.continuation.refine_frame(
                previous, address, policy, frame_policy, **work
            )
        previous = admission
        item = cloud._history(admission, level)
        if isinstance(admission, cloud.continuation.AdmittedFrame):
            try:
                values = program.evaluate(
                    admission.frame, source_signature=program.source_signature
                )
                q, diagnostics = cloud._kernel(values, (Eisenstein(1), OMEGA))
                bounds = admission.weight.quotient_weight_without_pi_cubed
                weight = float((bounds.lower + bounds.upper) / 2)
                if not cloud.math.isfinite(weight) or weight <= 0:
                    raise ArithmeticError("the numerical quotient weight is unresolved")
                item.update(
                    {
                        "kernel_status": "computed_discovery",
                        "kernel_rows": cloud._encode_rows(q),
                        "weight_midpoint_without_pi_cubed": weight.hex(),
                        "kernel_diagnostics": diagnostics,
                        "complete_original_sections_consumed": True,
                        "floating_mantissa_bits": sys.float_info.mant_dig,
                    }
                )
            except (ArithmeticError, ValueError) as error:
                item.update({"kernel_status": "unresolved", "kernel_reason": str(error)})
        history.append(item)
        if progress is not None:
            progress(
                {
                    "ordinal": ordinal,
                    "level": level,
                    "frame_status": item["status"],
                    "kernel_status": item.get("kernel_status", "unresolved"),
                }
            )
        if item.get("kernel_status") == "computed_discovery":
            break
    return {
        **identity,
        "role": _role(request, ordinal),
        "history": history,
        "request_digest": request["artifact_digest"],
        "original_section_basis_digest": cloud.features.BASIS,
    }


def _read_sample(request, inputs, ordinal):
    """Validate a complete original checkpoint, including an unresolved one."""

    path = _sample_path(ordinal)
    result = json.loads(gzip.decompress(path.read_bytes()))
    unsigned = {k: v for k, v in result.items() if k != "artifact_digest"}
    identity = cloud.inputs.sample_identity(inputs, ordinal)
    if (
        cloud.inputs._digest(unsigned) != result.get("artifact_digest")
        or any(result[k] != value for k, value in identity.items())
        or result["request_digest"] != request["artifact_digest"]
        or result["role"] != _role(request, ordinal)
        or result["original_section_basis_digest"] != cloud.features.BASIS
        or not result["history"]
    ):
        raise ValueError("an original full-basis sample checkpoint changed")
    levels = request["policy"]["levels"]
    if [h["level"] for h in result["history"]] != levels[: len(result["history"])]:
        raise ValueError("a sample lost its original ordered refinement requests")
    if len(result["history"]) > len(levels):
        raise ValueError("a sample changed the declared refinement budget")
    for index, item in enumerate(result["history"]):
        expected_address = cloud.draws._address_record(
            cloud.roots.refinement_address(cloud.inputs.address(inputs, ordinal), item["level"])
        )
        if (
            item["address"] != expected_address
            or item["status"] not in ("admitted", "unresolved")
            or item["frame_policy"]
            != {
                "chart": [0, 0, 0],
                "first_pivots": [0, 2],
                "second_pivots": [0, 1, 2],
                "input_center_bits": 8 * item["level"],
                "volume_scale": ["1", "0"],
                "covering_degree": 9,
            }
        ):
            raise ValueError("the original retained frame or address changed")
        if "component" in item:
            component, branch = cloud.inputs.address(inputs, ordinal).choices()
            if item["component"] != component or item["selected_branch"] != list(branch):
                raise ValueError("the original component or selected branch changed")
        if index:
            parent = result["history"][index - 1]
            if ("all_root_families" in parent and item["root_parent_retained"] is not True) or (
                parent["status"] == "admitted" and item["frame_parent_retained"] is not True
            ):
                raise ValueError("a refinement abandoned its admitted original parent")
        if item.get("kernel_status") == "computed_discovery":
            if (
                index != len(result["history"]) - 1
                or item["status"] != "admitted"
                or item["complete_original_sections_consumed"] is not True
                or item["floating_mantissa_bits"] != 53
            ):
                raise ValueError("kernel admission cannot skip original samples or sections")
            cloud._decode_rows(item["kernel_rows"])
            weight = float.fromhex(item["weight_midpoint_without_pi_cubed"])
            if not cloud.math.isfinite(weight) or weight <= 0:
                raise ValueError("a resolved positive numerical weight required")
        elif item["status"] == "admitted" and not item.get("kernel_reason"):
            raise ValueError("a failed kernel must retain its unresolved reason")
        elif item["status"] == "unresolved" and not item.get("reason"):
            raise ValueError("a failed frame must retain its unresolved reason")
    if result["history"][-1].get("kernel_status") != "computed_discovery" and len(
        result["history"]
    ) != len(levels):
        raise ValueError("an unresolved sample cannot silently skip its refinement budget")
    return result


def run_shard(*, expected_request_digest, worker, workers, progress=None):
    """Resume disjoint ordinals without resampling any unresolved checkpoint."""

    if (
        type(workers) is not int
        or workers < 1
        or type(worker) is not int
        or not 0 <= worker < workers
    ):
        raise ValueError("an explicit disjoint worker shard required")
    request = read_request(expected_digest=expected_request_digest)
    inputs = cloud.inputs.read_inputs(expected_digest=request["input_digest"], path=INPUTS)
    before = _sources()
    ordinals = tuple(range(worker, request["sample_count"], workers))
    pending = tuple(i for i in ordinals if not _sample_path(i).exists())
    # No compilation or geometric replay when all owned checkpoints exist.
    if pending:
        program = cloud.features.compile_features()
        started = perf_counter()
        for ordinal in pending:
            sample = process_sample(request, inputs, ordinal, program, progress=progress)
            sample["artifact_digest"] = cloud.inputs._digest(sample)
            cloud._install_sample(_sample_path(ordinal), sample)
            _read_sample(request, inputs, ordinal)
            if progress is not None:
                progress(
                    {
                        "completed_original_ordinal": ordinal,
                        "role": sample["role"],
                        "worker": worker,
                        "elapsed_seconds": perf_counter() - started,
                    }
                )
    if _sources() != before:
        raise ValueError("original workload sources changed during execution")
    unresolved = []
    for ordinal in ordinals:
        sample = _read_sample(request, inputs, ordinal)
        if sample["history"][-1].get("kernel_status") != "computed_discovery":
            unresolved.append(ordinal)
    return {
        "worker": worker,
        "workers": workers,
        "owned_request_count": len(ordinals),
        "unresolved_ordinals": unresolved,
    }


def inspect_progress(*, expected_request_digest):
    """Report missing and failed original requests, never an admitted-subset integral."""

    request = read_request(expected_digest=expected_request_digest)
    inputs = cloud.inputs.read_inputs(expected_digest=request["input_digest"], path=INPUTS)
    missing, unresolved, references, components = [], [], [], Counter()
    for ordinal in range(request["sample_count"]):
        path = _sample_path(ordinal)
        if not path.exists():
            missing.append(ordinal)
            continue
        sample = _read_sample(request, inputs, ordinal)
        if sample["history"][-1].get("kernel_status") != "computed_discovery":
            unresolved.append(ordinal)
        else:
            components[sample["history"][-1]["component"]] += 1
        references.append(
            {
                "ordinal": ordinal,
                "path": str(path.relative_to(ROOT)),
                "sha256": cloud.features.exact.archive._file_digest(path),
                "artifact_digest": sample["artifact_digest"],
            }
        )
    complete = not missing and not unresolved
    return {
        "schema": "full-original-trial-cloud-v1",
        "request_digest": request["artifact_digest"],
        "input_digest": request["input_digest"],
        "sample_count": request["sample_count"],
        "training_count": request["training_count"],
        "validation_count": request["validation_count"],
        "source_files_sha256": _sources(),
        "original_section_basis_digest": cloud.features.BASIS,
        "compilation_parent_digest": cloud.features.COMPILATION,
        "sample_archives": references,
        "missing_sample_ordinals": missing,
        "unresolved_sample_ordinals": unresolved,
        "completed_checkpoint_count": len(references),
        "complete_original_workload_available": complete,
        "resolved_component_counts": dict(components),
        "training_rank_upper_bound": min(5345, 4 * request["training_count"]),
        "minimum_training_samples_necessary_for_invertibility": 1337,
        "entropy_assumption_status": "ASSUMED",
        "parameter_point_status": "SELECTED",
        "failed_samples_dropped": False,
        "admitted_subset_mean_available": False,
        "numerical_error_bound_certified": False,
        "sampling_error_bound_useful": False,
        "global_trial_operator_estimate_available": False,
        "controlled_integral_available": False,
        "nonunit_h_iteration_executed": False,
        "ricci_flat_or_hym_metric_available": False,
        "physical_yukawas_available": False,
        "common_stabilized_vacuum_available": False,
        "observations_used": False,
    }


def collect(*, expected_request_digest):
    """Install the complete checkpoint manifest; failure never manufactures a mean."""

    result = inspect_progress(expected_request_digest=expected_request_digest)
    if result["missing_sample_ordinals"]:
        raise FileNotFoundError("the declared original workload is still running or incomplete")
    result["artifact_digest"] = cloud.inputs._digest(result)
    _install_json(OUTPUT, result)
    return result


def read_cloud(*, expected_request_digest, expected_digest, path=OUTPUT):
    """Verify the trusted whole-workload manifest without calculations or entropy."""

    saved = json.loads(path.read_bytes())
    unsigned = {k: v for k, v in saved.items() if k != "artifact_digest"}
    if (
        saved.get("artifact_digest") != expected_digest
        or cloud.inputs._digest(unsigned) != expected_digest
    ):
        raise ValueError("the trusted whole-workload manifest changed")
    actual = inspect_progress(expected_request_digest=expected_request_digest)
    if unsigned != actual or actual["missing_sample_ordinals"]:
        raise ValueError("the complete original workload or its scientific scope changed")
    return saved


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise ValueError("provide the trusted request digest, worker index, and worker count")
    result = run_shard(
        expected_request_digest=sys.argv[1],
        worker=int(sys.argv[2]),
        workers=int(sys.argv[3]),
        progress=lambda r: print(json.dumps(r), flush=True),
    )
    print(json.dumps(result), flush=True)
