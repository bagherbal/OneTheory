"""Test the registered leverage prediction on the expanded population.

Owns:
    The H1 inverse-T update from all 8192 expanded training checkpoints (same
    law as the retained H1: whitened rows, weights w/n, D = sqrt(diag T),
    unpivoted Householder QR, real row phases, c = 4 mean(w)/5345), and the
    trace-free curvature of H0 and H1 on two predeclared subsets: every 16th
    training ordinal and every 16th validation ordinal (512 each).

Depends on:
    The project's expanded-population checkpoints and reader, the frozen
    compiled section program, the original first-jet curvature consumer, the
    constant row gauge, and the InverseForm contract.

Must not:
    Drop, replace or reweight samples, use validation in the factor, choose the
    subsets after seeing curvature, regularize, or claim an HYM metric.

Phase 0:
    Research test of a registered prediction; no physical metric is supplied.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.linalg import qr, solve_triangular

from research.experiments.scientific_genesis import balanced_trial_iteration as balanced
from research.experiments.scientific_genesis import expanded_trial_cloud as expanded
from research.experiments.scientific_genesis import nonunit_connection_curvature as nonunit
from research.experiments.scientific_genesis import row_scaled_trial_curvature as refinement

curvature = refinement.curvature
DIGEST = "65d7683b549605256f95b23bccf1f97e6f5c4ffc07ae7cac68fdfa778b6e55b8"
ROOT = Path(__file__).resolve().parents[3]
UPPER = ROOT / "data/generated/metric_sampling/expanded_h1.upper.npy"
SCALES = ROOT / "data/generated/metric_sampling/expanded_h1.scales.npy"
OUTPUT = ROOT / "data/generated/metric_sampling/expanded_h1_test.json"
LEVERAGE = ROOT / "data/generated/metric_sampling/leverage_diagnosis.json"
SECTIONS, RANK, STRIDE, SUBSET = 5345, 4, 16, 512


def subsets(training_count: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Predeclared evaluation ordinals, fixed before any curvature is computed."""

    train = tuple(STRIDE * k for k in range(SUBSET))
    held = tuple(training_count + STRIDE * k for k in range(SUBSET))
    return train, held


def _request():
    request = expanded.read_request(expected_digest=DIGEST)
    inputs = expanded.frozen.cloud.inputs.read_inputs(
        expected_digest=request["input_digest"], path=expanded.INPUTS,
    )
    return request, inputs


def build_factor(progress=None) -> dict[str, object]:
    """Factor the weighted training operator from every training checkpoint."""

    request, inputs = _request()
    count = request["training_count"]
    weighted = np.empty((RANK * count, SECTIONS), dtype=np.complex128, order="F")
    weights = []
    for ordinal in range(count):
        saved = expanded.read_sample(request, inputs, ordinal)
        if saved["role"] != "training":
            raise ValueError("a training ordinal changed roles")
        final = saved["history"][-1]
        if final.get("kernel_status") != "computed_discovery":
            raise ArithmeticError(f"training ordinal {ordinal} is unresolved; no operator")
        rows = np.asarray(expanded.frozen.cloud._decode_rows(final["kernel_rows"]),
                          dtype=np.complex128)
        whitening = np.linalg.cholesky(rows @ rows.conj().T)
        weight = float.fromhex(final["weight_midpoint_without_pi_cubed"])
        weights.append(weight)
        weighted[RANK * ordinal: RANK * (ordinal + 1)] = (
            solve_triangular(whitening, rows, lower=True) * math.sqrt(weight / count)
        )
        if progress and (ordinal + 1) % 512 == 0:
            progress({"phase": "weighted factor", "samples": ordinal + 1})
    scales = np.sqrt(np.einsum("ij,ij->j", weighted.conj(), weighted).real)
    if not np.all(np.isfinite(scales)) or np.any(scales <= 0):
        raise ArithmeticError("the solver congruence D is unresolved")
    weighted /= scales[None, :]
    if progress:
        progress({"phase": "Householder QR", "shape": list(weighted.shape)})
    (upper,) = qr(weighted, mode="r", pivoting=False, overwrite_a=True, check_finite=False)
    upper = np.asarray(upper[:SECTIONS], dtype=np.complex128)
    del weighted
    phases = np.sign(np.diag(upper).real)
    if np.any(phases == 0):
        raise ArithmeticError("a zero triangular diagonal; the operator is singular")
    upper *= phases[:, None]
    UPPER.parent.mkdir(parents=True, exist_ok=True)
    np.save(UPPER, upper, allow_pickle=False)
    np.save(SCALES, scales, allow_pickle=False)
    diagonal = np.abs(np.diag(upper))
    effective = sum(weights) ** 2 / sum(w * w for w in weights)
    return {
        "training_count": count,
        "mean_weight": statistics.fmean(weights),
        "effective_training_size": effective,
        "minimum_over_maximum_triangular_diagonal": float(diagonal.min() / diagonal.max()),
        "upper_sha256": hashlib.sha256(UPPER.read_bytes()).hexdigest(),
        "scales_sha256": hashlib.sha256(SCALES.read_bytes()).hexdigest(),
    }


def h1_form(mean_weight: float) -> balanced.InverseForm:
    upper = np.load(UPPER, allow_pickle=False)
    scales = np.load(SCALES, allow_pickle=False)
    coefficient = Fraction(RANK) * Fraction(mean_weight) / SECTIONS
    return balanced.InverseForm(curvature.features.BASIS, scales, upper.conj().T, coefficient)


def evaluate(form: balanced.InverseForm, ordinals, progress=None) -> list[dict[str, object]]:
    """H0 and H1 trace-free curvature at the saved centers of the given ordinals."""

    request, inputs = _request()
    parent = refinement._parent()
    program = curvature.features.compile_features()
    consumer = curvature.FullSectionJets(program)
    parameters = tuple(
        curvature.features._complex(curvature.Eisenstein(Fraction(a), Fraction(b)))
        for a, b in parent["parameter_point"]
    )
    rows = []
    for index, ordinal in enumerate(ordinals):
        saved = expanded.read_sample(request, inputs, ordinal)
        final = saved["history"][-1]
        row: dict[str, object] = {"ordinal": ordinal, "role": saved["role"]}
        try:
            if final.get("kernel_status") != "computed_discovery":
                raise ArithmeticError("unresolved checkpoint")
            coordinates = [curvature.features._complex(curvature.Eisenstein(
                Fraction(c["center"][0]), Fraction(c["center"][1]),
            )) for group in final["coordinate_bounds"] for c in group]
            values, jets, metric, _ = consumer.evaluate(
                coordinates, parameters, source_signature=program.source_signature,
            )
            v0, j0, _ = refinement.constant_row_gauge(values, jets)
            h0 = curvature.trace_free_curvature(v0, j0, metric)
            v1, j1 = nonunit.inverse_form_jets(form, values, jets,
                                              basis_digest=curvature.features.BASIS)
            v1, j1, _ = refinement.constant_row_gauge(v1, j1)
            h1 = curvature.trace_free_curvature(v1, j1, metric)
            row.update({"status": "computed_discovery",
                        "h0_trace_free_l1": h0["trace_free_l1"],
                        "h1_trace_free_l1": h1["trace_free_l1"]})
        except (ArithmeticError, ValueError, np.linalg.LinAlgError) as error:
            row.update({"status": "unresolved", "reason": str(error)})
        rows.append(row)
        if progress and (index + 1) % 32 == 0:
            progress({"phase": "curvature", "evaluated": index + 1, "of": len(ordinals)})
    return rows


def run(progress=None) -> dict[str, object]:
    request, _ = _request()
    train, held = subsets(request["training_count"])
    factor = build_factor(progress)
    form = h1_form(factor["mean_weight"])
    rows = evaluate(form, train + held, progress)
    resolved = {role: [r for r in rows if r["role"] == role and r["status"] != "unresolved"]
                for role in ("training", "validation")}

    def median(role: str, key: str) -> float:
        return statistics.median(r[key] for r in resolved[role])

    ratio_h1 = median("training", "h1_trace_free_l1") / median("validation", "h1_trace_free_l1")
    ratio_h0 = median("training", "h0_trace_free_l1") / median("validation", "h0_trace_free_l1")
    registered = json.loads(LEVERAGE.read_text())
    record: dict[str, object] = {
        "schema": "expanded-h1-leverage-test-v1",
        "registered_prediction": registered["registered_prediction"],
        "registered_prediction_artifact_digest": registered["artifact_digest"],
        "request_digest": DIGEST,
        "factor": factor,
        "training_subset": list(train), "validation_subset": list(held),
        "unresolved_evaluations": [r["ordinal"] for r in rows if r["status"] == "unresolved"],
        "h1_training_over_validation_median_ratio": ratio_h1,
        "h0_training_over_validation_median_ratio": ratio_h0,
        "prediction_passed": ratio_h1 < 10,
        "points": rows,
        "validation_used_in_factor": False,
        "hym_metric_claimed": False,
        "observations_used": False,
    }
    payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    record["artifact_digest"] = hashlib.sha256(payload).hexdigest()
    OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


if __name__ == "__main__":
    result = run(progress=lambda item: print(json.dumps(item), flush=True))
    print(json.dumps({key: result[key] for key in (
        "h1_training_over_validation_median_ratio", "h0_training_over_validation_median_ratio",
        "prediction_passed", "unresolved_evaluations", "artifact_digest",
    )}), flush=True)
    sys.exit(0)
