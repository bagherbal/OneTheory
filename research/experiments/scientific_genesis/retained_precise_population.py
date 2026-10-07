"""Evaluate the entire retained population under uniform explicit arithmetic.

Owns:
    A separately frozen 256-bit geometry workload, saved-native method checks,
    full-section H0/H1 consumption and complete-population-only aggregation.

Depends on:
    Original input receipts, the retained failed binary64 result, precise geometry
    and unchanged full-basis numerical curvature laws.

Must not:
    Patch a hybrid mean, loosen a residual gate, select a new H1, omit failures,
    redraw or export a physical metric from an empirical discovery profile.

Phase 0:
    Research resolution experiment only; physical gates remain unresolved.
"""

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

from . import retained_population_resolution as previous
from . import retained_precise_geometry as geometry

full, curvature = previous.full, previous.curvature
RAW = "075cb9178730d9a900e519ec8df649ca861e13fdf064e94ba4f10f0dd0d8d49e"
REQUEST = previous.REQUEST.with_name("retained_precise_population_request.json")
OUTPUT = previous.OUTPUT.with_name("retained_precise_population.json")
NOTE = Path(__file__).with_name("RETAINED_PRECISE_POPULATION_NOTE.md")


def _sources():
    result = previous._sources()
    paths = (Path(__file__), Path(geometry.__file__), NOTE, previous.OUTPUT,
        previous.REQUEST, full.ROOT / "requirements-dev.txt",
        Path(__file__).with_name("RETAINED_PRECISE_GEOMETRY_NOTE.md"),
        full.ROOT / "tests/integration/test_scientific_genesis_retained_precise_geometry.py",
        full.ROOT / "tests/integration/test_scientific_genesis_retained_precise_population.py")
    result.update({str(p.relative_to(full.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in paths})
    return result


def _declaration():
    raw = json.loads(previous.OUTPUT.read_bytes())
    if (raw.get("artifact_digest") != RAW
            or full.cloud.inputs._digest({k: v for k, v in raw.items()
                                         if k != "artifact_digest"}) != RAW
            or raw["sample_count"] != 2048 or len(raw["points"]) != 2048
            or raw["unresolved_ordinals"] != [345, 478, 587, 711, 735, 967, 1340, 1356,
                                               1610, 1720, 1777, 1981]
            or any("population_" in k and "tau" in k for k in raw)
            or raw["source_files_sha256"] != previous._sources()
            or geometry.__version__ != "1.3.0"):
        raise ValueError("the actual complete binary64 failure or arithmetic library changed")
    base = previous._declaration()
    return {**base, "schema": "retained-precise-population-request-v1",
        "policy": {**base["policy"], "geometry_working_precision_bits": 256},
        "failed_binary64_result_digest": RAW, "mpmath_version": geometry.__version__,
        "independent_native_method_checks": previous._method_checks(),
        "hybrid_or_subset_mean_available": False}


def create_request():
    """Check new arithmetic against saved native cases before uniform execution."""

    if REQUEST.exists():
        raise FileExistsError("retain the existing uniform arithmetic request")
    declaration, sources = _declaration(), _sources()
    original_request = full.read_request(expected_digest=curvature.PARENT_REQUEST)
    inputs = full.cloud.inputs.read_inputs(expected_digest=declaration["input_digest"],
                                          path=full.INPUTS)
    _, form = previous.nonunit.inverse.read_result(
        expected_request_digest=previous.nonunit.H1_REQUEST, expected_digest=previous.nonunit.H1)
    if form is None:
        raise ArithmeticError("the unchanged full H1 factor is unavailable")
    consumer = curvature.FullSectionJets(curvature.features.compile_features())
    parameters = tuple(curvature.features._complex(curvature.Eisenstein(Fraction(a), Fraction(b)))
                       for a, b in declaration["policy"]["parameters"])
    comparisons = []
    for ref in declaration["independent_native_method_checks"]:
        ordinal = ref["ordinal"]
        saved = full._read_sample(original_request, inputs, ordinal)
        native = json.loads((full.ROOT / ref["path"]).read_bytes())
        coordinates, weight, record = geometry.evaluate_geometry(
            full.cloud.inputs.address(inputs, ordinal), saved["history"][-1], bits=128, steps=8,
            residual_tolerance=1e-12, volume_scale=1, covering_degree=9, precision_bits=256)
        low, high = map(Fraction, native["native_weight_interval"])
        if not low <= Fraction(weight) <= high:
            raise ArithmeticError(
                "the predeclared arithmetic check missed the native weight interval")
        diagnostic = previous.diagnostics(coordinates, weight, consumer, parameters, form)
        native_l1 = native["native_center_diagnostics_discovery"]["h1"]["trace_free_l1"]
        comparisons.append({"ordinal": ordinal, "native_packet_digest": ref["artifact_digest"],
            "original_sample_digest": saved["artifact_digest"], "status": "computed_comparison",
            "coordinates_real_imag_discovery": [[c.real, c.imag] for c in coordinates],
            "geometry_discovery": record, "numerical_diagnostics_discovery": diagnostic,
            "numerical_weight_inside_native_interval": True,
            "h1_relative_l1_difference_discovery": diagnostic["h1"]["trace_free_l1"]/native_l1-1})
    if sources != _sources():
        raise ValueError("the explicit arithmetic declaration changed during its native checks")
    result = {**declaration, "source_files_sha256": sources,
              "multiprecision_method_comparisons": comparisons}
    result["artifact_digest"] = full.cloud.inputs._digest(result)
    full._install_json(REQUEST, result)
    return result


def read_request(*, expected_digest):
    record = json.loads(REQUEST.read_bytes())
    unsigned = {k: v for k, v in record.items() if k != "artifact_digest"}
    comparison = unsigned.pop("multiprecision_method_comparisons")
    if (record.get("artifact_digest") != expected_digest
            or full.cloud.inputs._digest({k: v for k, v in record.items()
                                         if k != "artifact_digest"}) != expected_digest
            or unsigned != {**_declaration(), "source_files_sha256": _sources()}
            or [r["ordinal"] for r in comparison] != [17, 101, 1819, 1980]
            or any(r["status"] != "computed_comparison"
                   or r["numerical_weight_inside_native_interval"] is not True
                   or r["geometry_discovery"]["geometry_working_precision_bits"] != 256
                   or r["numerical_diagnostics_discovery"]["original_section_count"] != 5345
                   for r in comparison)):
        raise ValueError("the full arithmetic workload or saved native comparisons changed")
    return record


def sample_path(ordinal):
    if type(ordinal) is not int or not 0 <= ordinal < 2048:
        raise ValueError("an original retained-population ordinal is required")
    return OUTPUT.with_name(f"retained_precise_population.sample_{ordinal:04d}.json")


def process_sample(request, inputs, original_request, manifest, ordinal,
                   consumer, parameters, form):
    saved = full._read_sample(original_request, inputs, ordinal)
    if saved["artifact_digest"] != manifest["sample_archives"][ordinal]["artifact_digest"]:
        raise ValueError("the original archived sample changed")
    item = {**full.cloud.inputs.sample_identity(inputs, ordinal), "role": saved["role"],
        "request_digest": request["artifact_digest"],
        "original_sample_digest": saved["artifact_digest"],
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
            covering_degree=policy["frame"]["covering_degree"],
            precision_bits=policy["geometry_working_precision_bits"])
        item.update(geometry_record)
        item["coordinates_real_imag_discovery"] = [[c.real, c.imag] for c in coordinates]
        item.update(previous.diagnostics(coordinates, weight, consumer, parameters, form))
        item["status"] = "computed_discovery"
    except (ArithmeticError, ValueError, np.linalg.LinAlgError) as error:
        item["reason"] = str(error)
    item["artifact_digest"] = full.cloud.inputs._digest(item)
    return item


def read_sample(request, inputs, manifest, ordinal):
    record = json.loads(sample_path(ordinal).read_bytes())
    if (full.cloud.inputs._digest({k: v for k, v in record.items()
                                  if k != "artifact_digest"}) != record.get("artifact_digest")
            or record["request_digest"] != request["artifact_digest"]
            or any(record.get(k) != v for k, v in full.cloud.inputs.sample_identity(
                inputs, ordinal).items())
            or record["original_sample_digest"] != manifest["sample_archives"][ordinal][
                "artifact_digest"]
            or record["role"] != ("training" if ordinal < 1536 else "validation")
            or record["status"] not in ("unresolved", "computed_discovery")):
        raise ValueError("an explicit-arithmetic checkpoint changed its original identity")
    if record["status"] == "unresolved":
        if not record.get("reason"):
            raise ValueError("every unresolved original input must retain its failure")
    elif (record["geometry_working_precision_bits"] != 256 or record["floating_mantissa_bits"] != 53
            or record["original_section_count"] != 5345
            or record["input_prefix_bits"] != 128
            or record["native_cover_membership_certified"] is not False
            or not math.isfinite(record["reference_volume_weight_discovery"])
            or record["reference_volume_weight_discovery"] <= 0
            or any(not math.isfinite(record[h]["trace_free_l1"]) for h in ("h0", "h1"))):
        raise ValueError("an explicit-arithmetic checkpoint lost its scope or full basis")
    return record


def run_shard(*, expected_digest, worker, workers, progress=None):
    if (type(workers) is not int or workers < 1 or type(worker) is not int
            or not 0 <= worker < workers):
        raise ValueError("explicit disjoint worker indices required")
    request = read_request(expected_digest=expected_digest)
    original_request = full.read_request(expected_digest=curvature.PARENT_REQUEST)
    inputs = full.cloud.inputs.read_inputs(expected_digest=request["input_digest"],
                                          path=full.INPUTS)
    manifest = previous._parent_manifest()
    _, form = previous.nonunit.inverse.read_result(
        expected_request_digest=previous.nonunit.H1_REQUEST, expected_digest=previous.nonunit.H1)
    if form is None:
        raise ArithmeticError("the unchanged full H1 factor is unavailable")
    consumer = curvature.FullSectionJets(curvature.features.compile_features())
    parameters = tuple(curvature.features._complex(curvature.Eisenstein(Fraction(a), Fraction(b)))
                       for a, b in request["policy"]["parameters"])
    for ordinal in range(worker, 2048, workers):
        if not sample_path(ordinal).exists():
            record = process_sample(request, inputs, original_request, manifest, ordinal,
                                    consumer, parameters, form)
            full._install_json(sample_path(ordinal), record)
        record = read_sample(request, inputs, manifest, ordinal)
        if progress:
            progress({"ordinal": ordinal, "worker": worker, "status": record["status"],
                      "reason": record.get("reason")})
    if _sources() != request["source_files_sha256"]:
        raise ValueError("the explicit arithmetic sources changed during execution")
    return {"worker": worker, "workers": workers, "shard_complete": True}


def collect(*, expected_digest):
    request = read_request(expected_digest=expected_digest)
    inputs = full.cloud.inputs.read_inputs(expected_digest=request["input_digest"],
                                          path=full.INPUTS)
    manifest = previous._parent_manifest()
    if any(not sample_path(ordinal).exists() for ordinal in range(2048)):
        raise FileNotFoundError("the complete uniform arithmetic population is not available")
    points = [read_sample(request, inputs, manifest, ordinal) for ordinal in range(2048)]
    unresolved = [point["ordinal"] for point in points if point["status"] == "unresolved"]
    result = {"schema": "retained-precise-population-v1", "request_digest": expected_digest,
        "source_files_sha256": request["source_files_sha256"], "sample_count": 2048,
        "points": points, "unresolved_ordinals": unresolved,
        "failed_binary64_result_digest": RAW, "original_section_count": 5345,
        "h1_factor_digest": previous.nonunit.H1, "old_validation_is_blind": False,
        "new_entropy_obtained": False, "old_checkpoint_replaced": False,
        "hybrid_or_subset_mean_available": False, "h1_rebuilt": False, "h2_executed": False,
        "numerical_and_sampling_error_certified": False, "hym_convergence_established": False,
        "physical_yukawas_available": False, "observations_used": False,
        "status": "unresolved" if unresolved else "computed_discovery"}
    if not unresolved:
        j = curvature.POLARIZATION
        volume = curvature.ambient_cover_triple(j, j, j)/(
            6*request["policy"]["frame"]["covering_degree"])
        result["reference_quotient_volume_exact"] = str(volume)
        result["empirical_reference_volume_discovery"] = math.fsum(
            point["reference_volume_weight_discovery"] for point in points)/2048
        for h in ("h0", "h1"):
            result[f"full_population_{h}_tau_discovery"] = math.fsum(
                point["reference_volume_weight_discovery"]*point[h]["trace_free_l1"]
                for point in points)/(2048*2*math.pi*float(volume)*4)
            result[f"{h}_role_tau_discovery"] = {role: math.fsum(
                point["reference_volume_weight_discovery"]*point[h]["trace_free_l1"]
                for point in points if point["role"] == role)/(count*2*math.pi*float(volume)*4)
                for role, count in (("training", 1536), ("validation", 512))}
    result["artifact_digest"] = full.cloud.inputs._digest(result)
    full._install_json(OUTPUT, result)
    return result


if __name__ == "__main__":
    worker = int(sys.argv[2])

    def report(item):
        if item["ordinal"] % 128 == worker or item["status"] == "unresolved":
            print(json.dumps(item), flush=True)

    result = run_shard(expected_digest=sys.argv[1], worker=worker,
                       workers=int(sys.argv[3]), progress=report)
    print(json.dumps(result), flush=True)
