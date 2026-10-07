"""Evaluate a complete retained population under one finer discovery policy.

Owns:
    Immutable same-input resolution requests, full-section H0/H1 diagnostics,
    failure-preserving disjoint shards and complete-population-only summaries.

Depends on:
    Original cloud identities, numerical discovery geometry, the frozen full
    section jets and the admitted original-basis H1 factor.

Must not:
    Redraw, replace old checkpoints, reduce sections, calibrate weights, rebuild
    H1, run H2, average a resolved subset or claim controlled HYM convergence.

Phase 0:
    Whole-population numerical sensitivity experiment; physical gates stay closed.
"""

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

from . import nonunit_connection_curvature as nonunit
from . import retained_numerical_geometry as geometry

full, curvature = nonunit.curvature.full, nonunit.curvature
REQUEST = full.OUTPUT.with_name("retained_population_resolution_request.json")
OUTPUT = full.OUTPUT.with_name("retained_population_resolution.json")
NOTE = Path(__file__).with_name("RETAINED_POPULATION_RESOLUTION_NOTE.md")


def _sources():
    sources = nonunit._sources()
    paths = (Path(__file__), Path(geometry.__file__), NOTE, full.REQUEST, full.INPUTS,
             full.OUTPUT, full.ROOT /
             "tests/integration/test_scientific_genesis_retained_numerical_geometry.py",
             full.ROOT /
             "tests/integration/test_scientific_genesis_retained_population_resolution.py")
    sources.update({str(p.relative_to(full.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in paths})
    return sources


def _parent_manifest():
    """Check the complete pinned cloud; individual archived rows are checked at use."""

    record = json.loads(full.OUTPUT.read_bytes())
    if (record.get("artifact_digest") != curvature.PARENT_CLOUD
            or full.cloud.inputs._digest({k: v for k, v in record.items()
                                         if k != "artifact_digest"}) != curvature.PARENT_CLOUD
            or record["request_digest"] != curvature.PARENT_REQUEST
            or len(record["sample_archives"]) != 2048):
        raise ValueError("the original complete retained population changed")
    return record


def _declaration():
    request = full.read_request(expected_digest=curvature.PARENT_REQUEST)
    manifest = _parent_manifest()
    if (request["sample_count"] != 2048 or request["training_count"] != 1536
            or manifest["input_digest"] != request["input_digest"]):
        raise ValueError("the original population or split changed")
    return {"schema": "retained-population-resolution-request-v1",
        "original_request_digest": request["artifact_digest"],
        "original_manifest_digest": manifest["artifact_digest"],
        "input_digest": request["input_digest"], "sample_count": 2048,
        "training_count": 1536, "validation_count": 512,
        "policy": {"input_prefix_bits": 128, "newton_steps": 8,
                   "scaled_equation_residual_tolerance": 1e-12,
                   "parameters": request["policy"]["parameters"],
                   "frame": request["policy"], "floating_mantissa_bits": 53},
        "h1_factor_digest": nonunit.H1, "original_section_count": 5345,
        "original_section_basis_digest": curvature.features.BASIS,
        "old_validation_is_blind": False, "new_entropy_obtained": False,
        "entropy_assumption_status": "ASSUMED", "parameter_point_status": "SELECTED",
        "numerical_error_bound_certified": False, "observations_used": False}


def create_request():
    """Freeze the entire original population and policy without obtaining entropy."""

    if REQUEST.exists():
        raise FileExistsError("retain the existing resolution request")
    result = {**_declaration(), "independent_method_checks": _method_checks(),
              "source_files_sha256": _sources()}
    result["artifact_digest"] = full.cloud.inputs._digest(result)
    full._install_json(REQUEST, result)
    return result


def read_request(*, expected_digest):
    record = json.loads(REQUEST.read_bytes())
    unsigned = {k: v for k, v in record.items() if k != "artifact_digest"}
    if (record.get("artifact_digest") != expected_digest
            or full.cloud.inputs._digest(unsigned) != expected_digest
            or unsigned != {**_declaration(), "independent_method_checks": _method_checks(),
                            "source_files_sha256": _sources()}):
        raise ValueError("the declared retained-population resolution policy or sources changed")
    return record


def _method_checks():
    """Require every predeclared native comparison before broad discovery.

    Successful comparisons establish method testing, not a numerical error
    theorem. Their actual discrepancies remain in the pinned packets.
    """

    paths = (Path(__file__).with_name("retained_numerical_checks.py"),
             Path(geometry.certified.__file__),
             Path(__file__).with_name("RETAINED_NUMERICAL_CHECKS_NOTE.md"),
             full.ROOT / "tests/integration/test_scientific_genesis_retained_numerical_checks.py")
    expected_sources = {**_sources(), **{
        str(path.relative_to(full.ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths}}
    manifest = _parent_manifest()
    references = []
    for ordinal in (17, 101, 1819, 1980):
        path = OUTPUT.with_name(f"retained_numerical_checks.sample_{ordinal:04d}.json")
        record = json.loads(path.read_bytes())
        unsigned = {k: v for k, v in record.items() if k != "artifact_digest"}
        if (full.cloud.inputs._digest(unsigned) != record.get("artifact_digest")
                or record["source_files_sha256"] != expected_sources
                or record["ordinal"] != ordinal
                or record["input_digest"] != manifest["input_digest"]
                or record["original_sample_digest"] != manifest["sample_archives"][ordinal][
                    "artifact_digest"]
                or record["status"] != "computed_comparison"
                or record["native_finer_history"]["status"] != "admitted"
                or record["native_finer_history"]["level"] != 32
                or record["geometry_discovery"]["input_prefix_bits"] != 128
                or record["numerical_error_bound_certified"] is not False
                or record["new_entropy_obtained"] is not False):
            raise ValueError(
                "all fixed native comparisons must retain their actual method evidence")
        references.append({"ordinal": ordinal, "path": str(path.relative_to(full.ROOT)),
                           "artifact_digest": record["artifact_digest"]})
    return references


def sample_path(ordinal):
    if type(ordinal) is not int or not 0 <= ordinal < 2048:
        raise ValueError("an original retained-population ordinal is required")
    return OUTPUT.with_name(f"retained_population_resolution.sample_{ordinal:04d}.json")


def diagnostics(coordinates, weight, consumer, parameters, form):
    """Compose existing all-section laws, including the same constant row gauges."""

    values, jets, metric, residue_squared = consumer.evaluate(
        coordinates, parameters, source_signature=consumer.program.source_signature)
    h0_values, h0_jets, _ = nonunit.refinement.constant_row_gauge(values, jets)
    h0 = curvature.trace_free_curvature(h0_values, h0_jets, metric)
    h1_values, h1_jets = nonunit.inverse_form_jets(form, values, jets,
                                                basis_digest=curvature.features.BASIS)
    h1_values, h1_jets, _ = nonunit.refinement.constant_row_gauge(h1_values, h1_jets)
    h1 = curvature.trace_free_curvature(h1_values, h1_jets, metric)
    reference_weight = math.pi**3*weight*8*np.linalg.det(metric).real/residue_squared
    if not math.isfinite(reference_weight) or reference_weight <= 0:
        raise ArithmeticError("the unchanged reference weight is numerically unresolved")
    return {"h0": h0, "h1": h1, "reference_volume_weight_discovery": float(reference_weight),
            "omega_quotient_weight_without_pi_cubed_discovery": weight,
            "original_section_count": 5345}


def process_sample(request, inputs, manifest, ordinal, consumer, parameters, form, *,
                   original_request):
    saved = full._read_sample(original_request, inputs, ordinal)
    reference = manifest["sample_archives"][ordinal]
    if saved["artifact_digest"] != reference["artifact_digest"] or reference["ordinal"] != ordinal:
        raise ValueError("the original archived sample changed")
    item = {**full.cloud.inputs.sample_identity(inputs, ordinal), "role": saved["role"],
        "request_digest": request["artifact_digest"],
        "original_sample_digest": saved["artifact_digest"],
        "original_history_path": str(full._sample_path(ordinal).relative_to(full.ROOT)),
        "original_final_level": saved["history"][-1]["level"],
        "frame_policy": saved["history"][-1]["frame_policy"], "status": "unresolved"}
    policy = request["policy"]
    try:
        coordinates, weight, geometry_record = geometry.evaluate_geometry(
            full.cloud.inputs.address(inputs, ordinal), saved["history"][-1],
            bits=policy["input_prefix_bits"], steps=policy["newton_steps"],
            residual_tolerance=policy["scaled_equation_residual_tolerance"],
            volume_scale=curvature.features._complex(curvature.Eisenstein(
                *(Fraction(v) for v in policy["frame"]["residue_scale"]))),
            covering_degree=policy["frame"]["covering_degree"])
        item.update(geometry_record)
        item["coordinates_real_imag_discovery"] = [[c.real, c.imag] for c in coordinates]
        item.update(diagnostics(coordinates, weight, consumer, parameters, form))
        item["status"] = "computed_discovery"
    except (ArithmeticError, ValueError, ZeroDivisionError, np.linalg.LinAlgError) as error:
        item["reason"] = str(error)
    item["artifact_digest"] = full.cloud.inputs._digest(item)
    return item


def read_sample(request, inputs, manifest, ordinal):
    record = json.loads(sample_path(ordinal).read_bytes())
    unsigned = {k: v for k, v in record.items() if k != "artifact_digest"}
    if (full.cloud.inputs._digest(unsigned) != record.get("artifact_digest")
            or record["request_digest"] != request["artifact_digest"]
            or any(record.get(k) != value for k, value in full.cloud.inputs.sample_identity(
                inputs, ordinal).items())
            or record["original_sample_digest"] != manifest["sample_archives"][ordinal][
                "artifact_digest"]
            or record["role"] != ("training" if ordinal < 1536 else "validation")
            or record["status"] not in ("computed_discovery", "unresolved")):
        raise ValueError("a retained-resolution checkpoint changed its original identity")
    if record["status"] == "unresolved":
        if not record.get("reason"):
            raise ValueError("an unresolved original sample must retain its reason")
    elif (record["original_section_count"] != 5345
            or record["native_cover_membership_certified"] is not False
            or record["input_prefix_bits"] != request["policy"]["input_prefix_bits"]
            or record["floating_mantissa_bits"] != 53
            or not math.isfinite(record["reference_volume_weight_discovery"])
            or record["reference_volume_weight_discovery"] <= 0):
        raise ValueError("a discovery checkpoint lost full-basis consumption or scope")
    return record


def run_shard(*, expected_digest, worker, workers, progress=None):
    if (type(workers) is not int or workers < 1 or type(worker) is not int
            or not 0 <= worker < workers):
        raise ValueError("explicit disjoint worker indices are required")
    request = read_request(expected_digest=expected_digest)
    original_request = full.read_request(expected_digest=curvature.PARENT_REQUEST)
    inputs = full.cloud.inputs.read_inputs(expected_digest=request["input_digest"],
                                          path=full.INPUTS)
    manifest = _parent_manifest()
    _, form = nonunit.inverse.read_result(expected_request_digest=nonunit.H1_REQUEST,
                                         expected_digest=nonunit.H1)
    if form is None:
        raise ArithmeticError("the actual full H1 factor is unavailable")
    consumer = curvature.FullSectionJets(curvature.features.compile_features())
    parameters = tuple(curvature.features._complex(curvature.Eisenstein(Fraction(a), Fraction(b)))
                       for a, b in request["policy"]["parameters"])
    for ordinal in range(worker, 2048, workers):
        if not sample_path(ordinal).exists():
            result = process_sample(request, inputs, manifest, ordinal, consumer, parameters, form,
                                    original_request=original_request)
            full._install_json(sample_path(ordinal), result)
        result = read_sample(request, inputs, manifest, ordinal)
        if progress:
            progress({"ordinal": ordinal, "worker": worker, "status": result["status"],
                      "reason": result.get("reason")})
    if _sources() != request["source_files_sha256"]:
        raise ValueError("the retained-resolution sources changed during execution")
    return {"worker": worker, "workers": workers, "shard_complete": True}


def collect(*, expected_digest):
    request = read_request(expected_digest=expected_digest)
    inputs = full.cloud.inputs.read_inputs(expected_digest=request["input_digest"],
                                          path=full.INPUTS)
    manifest = _parent_manifest()
    missing = [ordinal for ordinal in range(2048) if not sample_path(ordinal).exists()]
    if missing:
        raise FileNotFoundError("the complete original resolution workload is not yet available")
    points = [read_sample(request, inputs, manifest, ordinal) for ordinal in range(2048)]
    unresolved = [point["ordinal"] for point in points if point["status"] == "unresolved"]
    result = {"schema": "retained-population-resolution-v1", "request_digest": expected_digest,
        "source_files_sha256": request["source_files_sha256"], "sample_count": 2048,
        "points": points, "unresolved_ordinals": unresolved,
        "original_section_count": 5345, "h1_factor_digest": nonunit.H1,
        "new_entropy_obtained": False, "old_checkpoint_replaced": False,
        "hybrid_or_subset_mean_available": False, "old_validation_is_blind": False,
        "numerical_and_sampling_error_certified": False, "h1_rebuilt": False,
        "h2_executed": False, "hym_convergence_established": False,
        "physical_yukawas_available": False, "observations_used": False}
    if not unresolved:
        j = curvature.POLARIZATION
        volume = float(curvature.ambient_cover_triple(j, j, j)/(
            6*request["policy"]["frame"]["covering_degree"]))
        result["reference_quotient_volume_exact"] = str(curvature.ambient_cover_triple(j, j, j)/(
            6*request["policy"]["frame"]["covering_degree"]))
        result["empirical_reference_volume_discovery"] = math.fsum(
            point["reference_volume_weight_discovery"] for point in points)/2048
        for h in ("h0", "h1"):
            result[f"full_population_{h}_tau_discovery"] = math.fsum(
                point["reference_volume_weight_discovery"]*point[h]["trace_free_l1"]
                for point in points)/(2048*2*math.pi*volume*4)
    result["artifact_digest"] = full.cloud.inputs._digest(result)
    full._install_json(OUTPUT, result)
    return result


if __name__ == "__main__":
    result = run_shard(expected_digest=sys.argv[1], worker=int(sys.argv[2]),
                       workers=int(sys.argv[3]),
                       progress=lambda record: print(json.dumps(record), flush=True))
    print(json.dumps(result), flush=True)
