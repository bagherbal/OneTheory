"""Compare the actual full-basis H1 connection with the retained H0 experiment.

Owns:
    First-jet actions of the admitted original-basis inverse factor and a
    complete old-population reference curvature profile, with retained failures.

Depends on:
    The frozen original analytic consumer, constant local row-gauge policy,
    source-bound H1 factor, and unchanged original coordinate receipts.

Must not:
    Construct a reduced section form, regularize, redraw, execute H2 on the
    obstructed finite measure, or identify reference curvature with physical HYM.

Phase 0:
    Research discovery comparison only; physical metric gates remain unresolved.
"""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.linalg import solve_triangular

from . import factored_trial_inverse as inverse
from . import row_scaled_trial_curvature as refinement

curvature = refinement.curvature
H1 = "202980d12d88fef5b9398edd6150a3da8083312c8cd1f2e030d9efbfaadce80c"
H1_REQUEST = "2de18a347a4b94e6472228815c21a2133254bdd02211f0a4fc6b3ff05d8e6d53"
OUTPUT = curvature.OUTPUT.with_name("nonunit_connection_curvature.json")
NOTE = Path(__file__).with_name("NONUNIT_CONNECTION_CURVATURE_NOTE.md")


def inverse_form_jets(form, values, jets, *, basis_digest):
    """Apply sqrt(c) S D^-1 L^-dagger to all values and first jets.

    H1 is constant on X, so its factor commutes with differentiation. This
    invertible action retains all 5345 original coordinates, unlike a low-rank
    substitute. A positive constant section-form scale does not change curvature.
    """

    values = np.asarray(values, dtype=np.complex128)
    jets = np.asarray(jets, dtype=np.complex128)
    if (not isinstance(form, inverse.inverse.InverseForm)
            or form.basis_digest != basis_digest or basis_digest != curvature.features.BASIS
            or form.section_count != 5345 or values.shape != (4, 5345)
            or jets.shape != (3, 4, 5345)
            or not np.all(np.isfinite(values)) or not np.all(np.isfinite(jets))):
        raise ValueError("the named complete original H1 form and first jets are required")
    combined = np.concatenate((values[None], jets), axis=0).reshape(16, 5345)
    solved = solve_triangular(form.lower, (combined / form.diagonal).conj().T, lower=True)
    transformed = math.sqrt(float(form.coefficient)) * solved.conj().T
    if not np.all(np.isfinite(transformed)):
        raise ArithmeticError("the complete H1 first-jet action overflowed")
    transformed = transformed.reshape(4, 4, 5345)
    return transformed[0], transformed[1:]


def _sources():
    result = refinement._sources()
    result.update(inverse._sources())
    paths = (Path(__file__), NOTE, curvature.full.ROOT /
             "tests/integration/test_scientific_genesis_nonunit_curvature.py")
    result.update({str(path.relative_to(curvature.full.ROOT)):
                   hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    return result


def run(*, progress=None):
    """Evaluate every old point at H1; a single failure prevents every mean."""

    if OUTPUT.exists():
        raise FileExistsError("retain the original nonunit connection profile")
    parent = refinement._parent()
    sources = _sources()
    h1_record, form = inverse.read_result(expected_request_digest=H1_REQUEST, expected_digest=H1)
    if form is None:
        raise ArithmeticError("the actual original-basis H1 factor is unavailable")
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
            raise ValueError("the retained original sample identity changed")
        final = saved["history"][-1]
        item = {key: original[key] for key in (
            "ordinal", "role", "sample_artifact_digest", "address", "selected_branch",
            "frame_policy", "fiber_basis_labels",
        )}
        item["status"] = "unresolved"
        try:
            if final["kernel_status"] != "computed_discovery":
                raise ArithmeticError("the original retained sample is unresolved")
            coordinates = [curvature.features._complex(curvature.Eisenstein(
                Fraction(c["center"][0]), Fraction(c["center"][1]),
            )) for group in final["coordinate_bounds"] for c in group]
            values, jets, metric, residue_squared = consumer.evaluate(
                coordinates, parameters, source_signature=program.source_signature,
            )
            values, jets = inverse_form_jets(
                form, values, jets, basis_digest=curvature.features.BASIS,
            )
            values, jets, scales = refinement.constant_row_gauge(values, jets)
            diagnostic = curvature.trace_free_curvature(values, jets, metric)
            omega_weight = math.pi**3 * float.fromhex(final["weight_midpoint_without_pi_cubed"])
            weight = omega_weight * 8 * np.linalg.det(metric).real / residue_squared
            weighted_l1 = weight * diagnostic["trace_free_l1"]
            if (not math.isfinite(weight) or weight <= 0 or not math.isfinite(weighted_l1)
                    or weighted_l1 < 0):
                raise ArithmeticError("the reference volume weighting is unresolved")
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
        "complete_original_workload_available", "section_form", "fiber_metric_convention",
    )}
    record.update({"schema": "full-original-nonunit-curvature-v1",
                   "source_files_sha256": sources,
                   "raw_h0_curvature_parent_digest": refinement.PARENT,
                   "h1_digest": H1, "h1_request_digest": H1_REQUEST,
                   "original_trial_section_form": parent["section_form"],
                   "section_form": {"basis_digest": form.basis_digest, "section_count": 5345,
                                    "factor_artifact_digest": h1_record["artifact_digest"]},
                   "fiber_metric_convention": "h=(S H1 S^dagger)^-1; original full-basis H1",
                   "constant_local_gauge_policy": "diag(1/max_j abs(S_H1_ij(center)))",
                   "gauge_treated_as_constant_in_each_local_germ": True,
                   "gauge_is_physical_normalization": False,
                   "all_points_recomputed": True, "conditioning_guard_relaxed": False,
                   "h2_executed": False, "finite_atomic_obstruction_preserved": True,
                   "h1_selected_using_curvature_or_validation": False,
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
        raise ValueError("the complete H1 comparison changed during execution")
    record["artifact_digest"] = full.cloud.inputs._digest(record)
    full._install_json(OUTPUT, record)
    return record


if __name__ == "__main__":
    result = run(progress=lambda item: print(json.dumps(item), flush=True))
    print(json.dumps({key: result[key] for key in (
        "artifact_digest", "sample_count", "unresolved_ordinals",
        "complete_original_workload_available",
    )}), flush=True)
