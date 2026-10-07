"""Execute a fresh full-section population after the empirical balance no-go.

Owns:
    A separately predeclared training/held-out population, immutable new entropy
    receipts, disjoint resumable shards and complete native checkpoint histories.

Depends on:
    The frozen full-cloud sample evaluator, exact finite-weight obstruction,
    named-stream auxiliary sampler and complete original section compiler.

Must not:
    Replace any older input, clip weights, reuse inspected held-out points as
    blind validation, average an admitted subset or claim continuum convergence.

Phase 0:
    Research discovery execution only; integration and physical gates stay open.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from time import perf_counter

from . import finite_cloud_balance as balance
from . import full_trial_cloud as frozen

ROOT = frozen.ROOT
OUTPUT = frozen.OUTPUT.with_name("expanded_trial_cloud.json")
INPUTS = OUTPUT.with_name("expanded_trial_cloud_inputs.json")
REQUEST = OUTPUT.with_name("expanded_trial_cloud_request.json")
PROOF = Path(__file__).with_name("EXPANDED_TRIAL_CLOUD_NOTE.md")
OBSTRUCTION = "1a60352d1c7b4287621e5eb53e8b7902f7bf7f1c3bf37cce2bb1fd35e3100288"
PARENT_REQUEST = "9e13a565bc13a2bd27320e5746d3fbf2104c3290f8792efc97d8d3316bc8a5b5"
PARENT_CLOUD = "3138e6d6eb4c17fb977714f78069cc704e09f3eab45fb73e1b8d16d540cd29cc"


def _sources():
    sources = balance._sources()
    for path in (Path(__file__), PROOF):
        sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return sources


def _parent():
    """Read immutable parent metadata without replay, new entropy or geometry."""

    result = balance.read_certificate(expected_digest=OBSTRUCTION)
    if (
        result["request_digest"] != PARENT_REQUEST
        or result["cloud_manifest_digest"] != PARENT_CLOUD
        or result["training"]["balanced_fixed_point_excluded_on_retained_intervals"] is not True
    ):
        raise ValueError("the parent empirical obstruction is not established")
    return frozen.read_request(expected_digest=PARENT_REQUEST)


def _declaration(parent, *, count, training_count, levels, max_cells):
    """Derive the exact experimental scope; no sample result enters this scope."""

    if (
        type(count) is not int
        or type(training_count) is not int
        or training_count <= parent["training_count"]
        or count - training_count < 1337
        or type(levels) is not tuple
        or not levels
        or any(type(level) is not int or not 2 <= level for level in levels)
        or any(a >= b for a, b in zip(levels, levels[1:], strict=False))
        or type(max_cells) is not int
        or max_cells < 1
    ):
        raise ValueError("a larger fixed training population and explicit held-out policy required")
    policy = {**parent["policy"], "levels": list(levels), "max_cells": max_cells}
    return {
        "schema": "expanded-original-trial-cloud-request-v1",
        "sample_count": count,
        "training_count": training_count,
        "validation_count": count - training_count,
        "split_rule": "training ordinal < training_count; all remaining ordinals are validation",
        "split_fixed_before_geometry": True,
        "policy": policy,
        "parent_request_digest": PARENT_REQUEST,
        "parent_cloud_digest": PARENT_CLOUD,
        "parent_obstruction_digest": OBSTRUCTION,
        "older_populations_retained_unchanged": True,
        "older_validation_is_blind_for_this_experiment": False,
        "old_and_new_populations_combined_in_an_estimator": False,
        "auxiliary_law": "unchanged beta^3 / integral_cover beta^3 with exact mixture selectors",
        "original_section_basis_digest": parent["original_section_basis_digest"],
        "compilation_parent_digest": parent["compilation_parent_digest"],
        "entropy_assumption_status": "ASSUMED",
        "parameter_point_status": "SELECTED",
        "section_form": parent["section_form"],
        "sample_budget_proves_balance": False,
        "new_validation_used_to_select_request": False,
        "observations_used": False,
    }


def create_request(*, count, training_count, bytes_per_stream, levels, max_cells):
    """Capture the whole new population before evaluating any of its geometry."""

    if REQUEST.exists() or INPUTS.exists():
        raise FileExistsError("retain the new population; never obtain replacement entropy")
    if type(bytes_per_stream) is not int or bytes_per_stream < 32:
        raise ValueError("at least 256 retained bits per named stream required")
    sources = _sources()
    declaration = _declaration(
        _parent(), count=count, training_count=training_count, levels=levels, max_cells=max_cells,
    )
    if any(level > 2 * bytes_per_stream for level in levels):
        raise ValueError("the declared refinement exceeds the retained stream length")
    inputs = frozen.cloud.inputs.create_inputs(
        count=count, bytes_per_stream=bytes_per_stream, path=INPUTS,
    )
    # Even the extremely unlikely repeated receipt must be retained and rejected,
    # not replaced. Equal points themselves are lawful independent outcomes.
    _require_distinct_receipts(inputs)
    result = {**declaration, "input_digest": inputs["artifact_digest"],
              "source_files_sha256": sources}
    if sources != _sources():
        raise ValueError("the new workload sources changed during input capture")
    result["artifact_digest"] = frozen.cloud.inputs._digest(result)
    frozen._install_json(REQUEST, result)
    return read_request(expected_digest=result["artifact_digest"])


def _require_distinct_receipts(inputs):
    """Reject wholesale reuse of an older retained receipt, not equal individual draws."""

    for path in (frozen.INPUTS, frozen.cloud.inputs.OUTPUT):
        previous = json.loads(path.read_bytes())
        if inputs["artifact_digest"] == previous["artifact_digest"]:
            raise ValueError("preserve the repeated receipt; fresh inputs were not captured")


def read_request(*, expected_digest, path=REQUEST):
    """Verify the trusted fresh population and scope without running geometry."""

    result = json.loads(path.read_bytes())
    unsigned = {key: value for key, value in result.items() if key != "artifact_digest"}
    if result.get("artifact_digest") != expected_digest or frozen.cloud.inputs._digest(
        unsigned
    ) != expected_digest:
        raise ValueError("the trusted expanded request changed")
    inputs = frozen.cloud.inputs.read_inputs(expected_digest=result["input_digest"], path=INPUTS)
    declaration = _declaration(
        _parent(), count=result["sample_count"], training_count=result["training_count"],
        levels=tuple(result["policy"]["levels"]), max_cells=result["policy"]["max_cells"],
    )
    expected = {**declaration, "input_digest": inputs["artifact_digest"],
                "source_files_sha256": _sources()}
    if (
        unsigned != expected
        or inputs["sample_count"] != result["sample_count"]
        or inputs["bytes_per_stream"] < 32
        or any(level > 2 * inputs["bytes_per_stream"] for level in declaration["policy"]["levels"])
    ):
        raise ValueError("the expanded population, law, sources or scientific scope changed")
    _require_distinct_receipts(inputs)
    return result


def _sample_path(ordinal):
    return OUTPUT.with_name(f"expanded_trial_cloud.sample_{ordinal:05d}.json.gz")


def read_sample(request, inputs, ordinal, *, path=None):
    """Check all native history, original columns and precision for one new input.

    This independently parameterized reader checks the same contract as the
    frozen reader, without rebinding its module globals or changing old paths.
    """

    if type(ordinal) is not int or not 0 <= ordinal < request["sample_count"]:
        raise ValueError("an original new-request ordinal required")
    path = _sample_path(ordinal) if path is None else path
    result = json.loads(gzip.decompress(path.read_bytes()))
    unsigned = {key: value for key, value in result.items() if key != "artifact_digest"}
    identity = frozen.cloud.inputs.sample_identity(inputs, ordinal)
    if (
        frozen.cloud.inputs._digest(unsigned) != result.get("artifact_digest")
        or any(result.get(key) != value for key, value in identity.items())
        or result.get("request_digest") != request["artifact_digest"]
        or result.get("role") != frozen._role(request, ordinal)
        or result.get("original_section_basis_digest") != frozen.cloud.features.BASIS
        or not result.get("history")
    ):
        raise ValueError("a complete original new-population checkpoint required")
    levels = request["policy"]["levels"]
    history = result["history"]
    if len(history) > len(levels) or [item["level"] for item in history] != levels[:len(history)]:
        raise ValueError("the original ordered refinement budget changed")
    address = frozen.cloud.inputs.address(inputs, ordinal)
    for index, item in enumerate(history):
        level = item["level"]
        policy = request["policy"]
        if (
            item["address"] != frozen.cloud.draws._address_record(
                frozen.cloud.roots.refinement_address(address, level)
            )
            or item["status"] not in ("admitted", "unresolved")
            or item["frame_policy"] != {
                "chart": policy["chart"], "first_pivots": policy["first_pivots"],
                "second_pivots": policy["second_pivots"], "input_center_bits": 8 * level,
                "volume_scale": policy["residue_scale"],
                "covering_degree": policy["covering_degree"],
            }
        ):
            raise ValueError("the original address, frame or precision changed")
        if "component" in item:
            component, branch = address.choices()
            if item["component"] != component or item["selected_branch"] != list(branch):
                raise ValueError("the original component or branch changed")
        if index:
            parent = history[index - 1]
            if (
                "all_root_families" in parent and item["root_parent_retained"] is not True
            ) or (parent["status"] == "admitted" and item["frame_parent_retained"] is not True):
                raise ValueError("an original refinement parent was abandoned")
        if item.get("kernel_status") == "computed_discovery":
            if (
                index != len(history) - 1 or item["status"] != "admitted"
                or item["complete_original_sections_consumed"] is not True
                or item["floating_mantissa_bits"] != 53
            ):
                raise ValueError("kernel admission cannot skip original inputs or columns")
            frozen.cloud._decode_rows(item["kernel_rows"])
            weight = float.fromhex(item["weight_midpoint_without_pi_cubed"])
            if not frozen.cloud.math.isfinite(weight) or weight <= 0:
                raise ValueError("a resolved finite positive weight required")
        elif not item.get("kernel_reason" if item["status"] == "admitted" else "reason"):
            raise ValueError("an unresolved frame or kernel must retain its reason")
    if history[-1].get("kernel_status") != "computed_discovery" and len(history) != len(levels):
        raise ValueError("an unresolved sample skipped its original refinement budget")
    return result


def run_shard(*, expected_request_digest, worker, workers, progress=None):
    """Resume only missing ordinals; keep every terminal unresolved checkpoint."""

    if (
        type(workers) is not int or workers < 1 or type(worker) is not int
        or not 0 <= worker < workers
    ):
        raise ValueError("an explicit disjoint worker shard required")
    request = read_request(expected_digest=expected_request_digest)
    inputs = frozen.cloud.inputs.read_inputs(expected_digest=request["input_digest"], path=INPUTS)
    sources = _sources()
    ordinals = tuple(range(worker, request["sample_count"], workers))
    pending = tuple(ordinal for ordinal in ordinals if not _sample_path(ordinal).exists())
    if pending:
        program = frozen.cloud.features.compile_features()
        started = perf_counter()
        for ordinal in pending:
            sample = frozen.process_sample(request, inputs, ordinal, program, progress=progress)
            sample["artifact_digest"] = frozen.cloud.inputs._digest(sample)
            frozen.cloud._install_sample(_sample_path(ordinal), sample)
            read_sample(request, inputs, ordinal)
            if progress is not None:
                progress({"completed_original_ordinal": ordinal, "worker": worker,
                          "role": sample["role"], "elapsed_seconds": perf_counter() - started})
    if sources != _sources():
        raise ValueError("expanded workload sources changed during execution")
    unresolved = [ordinal for ordinal in ordinals if read_sample(request, inputs, ordinal)[
        "history"
    ][-1].get("kernel_status") != "computed_discovery"]
    return {"worker": worker, "workers": workers, "owned_request_count": len(ordinals),
            "unresolved_ordinals": unresolved}


def inspect_progress(*, expected_request_digest):
    """Inspect whole-population coverage without entropy, geometry or subset averages."""

    request = read_request(expected_digest=expected_request_digest)
    inputs = frozen.cloud.inputs.read_inputs(expected_digest=request["input_digest"], path=INPUTS)
    missing, unresolved, references, components = [], [], [], Counter()
    for ordinal in range(request["sample_count"]):
        path = _sample_path(ordinal)
        if not path.exists():
            missing.append(ordinal)
            continue
        sample = read_sample(request, inputs, ordinal)
        if sample["history"][-1].get("kernel_status") != "computed_discovery":
            unresolved.append(ordinal)
        else:
            components[sample["history"][-1]["component"]] += 1
        references.append({"ordinal": ordinal, "path": str(path.relative_to(ROOT)),
                           "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                           "artifact_digest": sample["artifact_digest"]})
    return {
        "schema": "expanded-original-trial-cloud-v1",
        "request_digest": request["artifact_digest"], "input_digest": request["input_digest"],
        "sample_count": request["sample_count"], "training_count": request["training_count"],
        "validation_count": request["validation_count"], "source_files_sha256": _sources(),
        "original_section_basis_digest": frozen.cloud.features.BASIS,
        "sample_archives": references, "missing_sample_ordinals": missing,
        "unresolved_sample_ordinals": unresolved, "completed_checkpoint_count": len(references),
        "resolved_component_counts": dict(components),
        "complete_original_workload_available": not missing and not unresolved,
        "older_populations_retained_unchanged": True,
        "entropy_assumption_status": "ASSUMED", "parameter_point_status": "SELECTED",
        "failed_samples_dropped": False, "admitted_subset_mean_available": False,
        "atomic_condition_tested": False, "balanced_fixed_point_available": False,
        "numerical_error_bound_certified": False, "sampling_error_bound_useful": False,
        "controlled_integral_available": False, "nonunit_h_iteration_executed": False,
        "ricci_flat_or_hym_metric_available": False, "physical_yukawas_available": False,
        "common_stabilized_vacuum_available": False, "observations_used": False,
    }


def collect(*, expected_request_digest):
    """Install all checkpoints, including failures; incomplete coverage has no manifest."""

    result = inspect_progress(expected_request_digest=expected_request_digest)
    if result["missing_sample_ordinals"]:
        raise FileNotFoundError("the original expanded workload is still running or incomplete")
    result["artifact_digest"] = frozen.cloud.inputs._digest(result)
    frozen._install_json(OUTPUT, result)
    return result


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise ValueError("provide the trusted expanded digest, worker index and worker count")
    print(json.dumps(run_shard(
        expected_request_digest=sys.argv[1], worker=int(sys.argv[2]), workers=int(sys.argv[3]),
        progress=lambda record: print(json.dumps(record), flush=True),
    )), flush=True)
