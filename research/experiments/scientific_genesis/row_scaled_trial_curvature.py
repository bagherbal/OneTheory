"""Refine full-population curvature in explicitly constant numerical fiber frames.

Owns:
    One declared row equilibration of every original value/first-jet matrix,
    retained identities and failures, and a whole-population reference diagnostic.

Depends on:
    The frozen original analytic curvature consumer and its failed complete
    population, unchanged coordinate receipts and full original section compiler.

Must not:
    Relax the conditioning guard, drop points or columns, differentiate a
    nonholomorphic global row gauge, change H0, or export physical normalization.

Phase 0:
    Research numerical refinement only; physical metric gates remain unresolved.
"""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np

from . import trial_connection_curvature as curvature

PARENT = "a60e2349513da60505a79be51f21db65aefc11525a64fd027ab35d2260124990"
OUTPUT = curvature.OUTPUT.with_name("row_scaled_trial_curvature.json")
NOTE = Path(__file__).with_name("ROW_SCALED_TRIAL_CURVATURE_NOTE.md")


def constant_row_gauge(values, jets):
    """Treat diag(1/max_j |S_ij(x0)|) as constant in a germ around each center.

    This is not a global nonholomorphic frame whose derivatives are omitted.
    Both the values and first jets transform by the same fixed local matrix.
    All original section coordinates survive; no physical normalization occurs.
    """

    values = np.asarray(values, dtype=np.complex128)
    jets = np.asarray(jets, dtype=np.complex128)
    if (values.shape != (4, 5345) or jets.shape != (3, 4, 5345)
            or not np.all(np.isfinite(values)) or not np.all(np.isfinite(jets))):
        raise ValueError("all finite original section values and first jets required")
    scales = np.max(np.abs(values), axis=1)
    if not np.all(np.isfinite(scales)) or np.any(scales <= 0):
        raise ArithmeticError("the declared constant row gauge is unresolved")
    return values / scales[:, None], jets / scales[None, :, None], scales


def _sources():
    result = curvature._sources()
    paths = (Path(__file__), NOTE,
             curvature.full.ROOT / "tests/integration/test_scientific_genesis_curvature_formula.py")
    result.update({str(path.relative_to(curvature.full.ROOT)):
                   hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    return result


def _parent():
    record = json.loads(curvature.OUTPUT.read_bytes())
    if (record["artifact_digest"] != PARENT
            or curvature.full.cloud.inputs._digest({k: v for k, v in record.items()
                                                   if k != "artifact_digest"}) != PARENT
            or record["source_files_sha256"] != curvature._sources()
            or record["unresolved_ordinals"] != [632, 956, 1007, 1161, 1637, 1962]):
        raise ValueError("the original retained curvature failure changed")
    return record


def run(*, progress=None):
    """Repeat every old input under one fixed gauge policy; never patch a subset mean."""

    if OUTPUT.exists():
        raise FileExistsError("retain the original row-scaled curvature refinement")
    parent = _parent()
    sources = _sources()
    full = curvature.full
    request = full.read_request(expected_digest=curvature.PARENT_REQUEST)
    inputs = full.cloud.inputs.read_inputs(
        expected_digest=request["input_digest"], path=full.INPUTS,
    )
    program = curvature.features.compile_features()
    consumer = curvature.FullSectionJets(program)
    parameters = tuple(curvature.features._complex(curvature.Eisenstein(Fraction(a), Fraction(b)))
                       for a, b in parent["parameter_point"])
    points = []
    for ordinal in range(parent["sample_count"]):
        saved = full._read_sample(request, inputs, ordinal)
        original = parent["points"][ordinal]
        if saved["artifact_digest"] != original["sample_artifact_digest"]:
            raise ValueError("an original refinement sample lost its retained source identity")
        final = saved["history"][-1]
        item = {key: original[key] for key in (
            "ordinal", "role", "sample_artifact_digest", "address", "selected_branch",
            "frame_policy", "fiber_basis_labels",
        )}
        item["status"] = "unresolved"
        try:
            coordinates = [curvature.features._complex(curvature.Eisenstein(
                Fraction(c["center"][0]), Fraction(c["center"][1]),
            )) for group in final["coordinate_bounds"] for c in group]
            values, jets, metric, residue_squared = consumer.evaluate(
                coordinates, parameters, source_signature=program.source_signature,
            )
            scaled_values, scaled_jets, scales = constant_row_gauge(values, jets)
            diagnostic = curvature.trace_free_curvature(scaled_values, scaled_jets, metric)
            omega_weight = math.pi**3 * float.fromhex(final["weight_midpoint_without_pi_cubed"])
            weight = omega_weight * 8 * np.linalg.det(metric).real / residue_squared
            weighted_l1 = weight * diagnostic["trace_free_l1"]
            if not math.isfinite(weight) or weight <= 0 or not math.isfinite(weighted_l1):
                raise ArithmeticError("the reference volume weight is unresolved")
            item.update({"status": "computed_discovery", **diagnostic,
                         "row_gauge_divisors": [float(x).hex() for x in scales],
                         "reference_volume_weight": float(weight),
                         "weighted_trace_free_l1": float(weighted_l1)})
        except (ArithmeticError, ValueError, np.linalg.LinAlgError) as error:
            item["reason"] = str(error)
        points.append(item)
        if progress and (ordinal % 128 == 0 or ordinal + 1 == parent["sample_count"]):
            progress({"samples_consumed": ordinal + 1, "sample_count": parent["sample_count"],
                      "unresolved_count": sum(p["status"] == "unresolved" for p in points)})
    failures = [p["ordinal"] for p in points if p["status"] == "unresolved"]
    record = {key: value for key, value in parent.items() if key not in (
        "artifact_digest", "source_files_sha256", "points", "unresolved_ordinals",
        "complete_original_workload_available",
    )}
    record.update({"schema": "row-scaled-original-trial-curvature-v1",
                   "source_files_sha256": sources, "raw_curvature_parent_digest": PARENT,
                   "constant_local_gauge_policy": "diag(1/max_j abs(S_ij(center)))",
                   "gauge_treated_as_constant_in_each_local_germ": True,
                   "gauge_is_physical_normalization": False,
                   "original_population_section_form_and_failed_profile_preserved": True,
                   "conditioning_guard_relaxed": False, "all_points_recomputed": True,
                   "points": points, "unresolved_ordinals": failures,
                   "complete_original_workload_available": not failures})
    if not failures:
        volume = parent["reference_quotient_volume"]
        record["full_population_tau_discovery"] = math.fsum(
            p["weighted_trace_free_l1"] for p in points
        ) / (len(points) * 2 * math.pi * volume * 4)
        record["empirical_reference_volume_discovery"] = math.fsum(
            p["reference_volume_weight"] for p in points
        ) / len(points)
        record["role_tau_discovery"] = {
            role: math.fsum(p["weighted_trace_free_l1"] for p in points if p["role"] == role)
            / (sum(p["role"] == role for p in points) * 2 * math.pi * volume * 4)
            for role in ("training", "validation")
        }
    if _sources() != sources:
        raise ValueError("the declared full-population refinement changed during execution")
    record["artifact_digest"] = full.cloud.inputs._digest(record)
    full._install_json(OUTPUT, record)
    return record


if __name__ == "__main__":
    result = run(progress=lambda item: print(json.dumps(item), flush=True))
    print(json.dumps({key: result[key] for key in (
        "artifact_digest", "sample_count", "unresolved_ordinals",
        "complete_original_workload_available",
    )}), flush=True)
