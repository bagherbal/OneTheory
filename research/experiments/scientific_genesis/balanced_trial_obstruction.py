"""Diagnose a failed full-basis discovery Gram inverse without supplying a metric.

Owns:
    Full-coordinate smallest-eigenvector diagnostics and independent positive
    quadratic sums over every original training kernel at the frozen unit H0.

Depends on:
    The trusted complete cloud, saved full operator and frozen inverse reader,
    NumPy/SciPy discovery arithmetic and explicit solver congruence.

Must not:
    Drop coordinates or samples, regularize, relax admission gates, infer an
    exact null vector or HYM obstruction, or manufacture a nonunit-H input.

Phase 0:
    Research numerical obstruction diagnostics only; physical metrics stay open.
"""

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.linalg import eigh, solve_triangular

from . import balanced_trial_iteration as inverse

full = inverse.full
OUTPUT = inverse.OUTPUT.with_name("balanced_trial_obstruction.json")
WITNESS = OUTPUT.with_name("balanced_trial_obstruction.witness.npy")


def smallest_direction(operator):
    """Inspect the whole matrix; the eigenvector is a diagnostic, never a state."""

    operator = np.asarray(operator, dtype=np.complex128)
    if (
        operator.ndim != 2
        or operator.shape[0] != operator.shape[1]
        or not operator.size
        or not np.all(np.isfinite(operator))
        or not np.array_equal(operator, operator.conj().T)
        or np.any(np.diag(operator).real <= 0)
    ):
        raise ValueError("a finite full Hermitian operator with positive diagonal required")
    scales = np.sqrt(np.diag(operator).real)
    normalized = operator / scales[:, None] / scales[None, :]
    asymmetry = float(np.max(np.abs(normalized - normalized.conj().T)))
    if asymmetry > 1e-12:
        raise ArithmeticError("solver congruence Hermitian rounding is unresolved")
    normalized = (normalized + normalized.conj().T) / 2
    # LAPACK inspects the complete original matrix. Selecting one diagnostic
    # eigenpair does not discard section coordinates or define a reduced model.
    eigenvalues, vectors = eigh(
        normalized,
        subset_by_index=(0, 0),
        driver="evr",
        check_finite=False,
    )
    direction = vectors[:, 0]
    pivot = int(np.argmax(np.abs(direction)))
    direction *= direction[pivot].conjugate() / abs(direction[pivot])
    eigenvalue = float(eigenvalues[0])
    size = float(np.linalg.norm(normalized, np.inf))
    residual = float(np.linalg.norm(normalized @ direction - eigenvalue * direction))
    rayleigh = complex(np.vdot(direction, normalized @ direction))
    return (
        direction,
        scales,
        {
            "section_count": operator.shape[0],
            "diagnostic_congruence": "B=D^-1 A D^-1, D=sqrt(diag A), every coordinate retained",
            "hermitian_rounding_projection_explicit": True,
            "congruence_hermitian_asymmetry_before_projection": asymmetry,
            "smallest_eigenvalue_discovery": eigenvalue,
            "normalized_operator_infinity_norm_discovery": size,
            "eigenpair_relative_residual_discovery": residual / size,
            "normalized_rayleigh_real_discovery": rayleigh.real,
            "normalized_rayleigh_imaginary_discovery": rayleigh.imag,
            "diagnostic_phase_convention": "largest absolute component positive real; first tie",
            "diagnostic_phase_pivot": pivot,
            "normalized_direction_norm_discovery": float(np.linalg.norm(direction)),
        },
    )


def run(*, expected_request_digest, expected_step_digest, progress=None):
    """Retain a whole-operator witness and inspect all original training samples."""

    if OUTPUT.exists():
        raise FileExistsError("preserve the original full-operator diagnostic")
    record, form = inverse.read_step(
        expected_request_digest=expected_request_digest,
        expected_digest=expected_step_digest,
    )
    if (
        form is not None
        or record.get("reason") != "full equilibrated Cholesky positivity is unresolved"
    ):
        raise ValueError("this diagnostic requires the actual failed full Cholesky trial")
    sources = {
        **inverse._sources(),
        str(Path(__file__).relative_to(full.ROOT)): hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
    }
    operator = np.load(inverse._array_path("operator"), mmap_mode="r", allow_pickle=False)
    if progress:
        progress({"phase": "trusted full operator verified; inspecting smallest direction"})
    direction, scales, diagnostics = smallest_direction(operator)
    witness = inverse._install_array(WITNESS, direction, "<c16")
    original_direction = direction / scales
    parent = full.read_request(expected_digest=record["cloud_request_digest"])
    inputs = full.cloud.inputs.read_inputs(expected_digest=record["input_digest"], path=full.INPUTS)
    terms = []
    for ordinal in range(parent["training_count"]):
        sample = full._read_sample(parent, inputs, ordinal)
        final = sample["history"][-1]
        rows = np.asarray(full.cloud._decode_rows(final["kernel_rows"]), dtype=np.complex128)
        gram = rows @ rows.conj().T
        vector = solve_triangular(np.linalg.cholesky(gram), rows @ original_direction, lower=True)
        squared = float(np.vdot(vector, vector).real)
        weight = float.fromhex(final["weight_midpoint_without_pi_cubed"])
        term = weight * squared / parent["training_count"]
        if not math.isfinite(term) or term < 0 or (squared > 0 and term == 0):
            raise ArithmeticError("an original positive quadratic contribution is unresolved")
        terms.append(term)
        if progress and (ordinal + 1) % 128 == 0:
            progress({"phase": "independent positive quadratic sum", "samples": ordinal + 1})
    if sources != {
        **inverse._sources(),
        str(Path(__file__).relative_to(full.ROOT)): hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
    }:
        raise ValueError("diagnostic sources changed during execution")
    result = {
        "schema": "full-original-trial-obstruction-v1",
        "inverse_request_digest": expected_request_digest,
        "inverse_step_digest": record["artifact_digest"],
        "cloud_manifest_digest": record["cloud_manifest_digest"],
        "original_section_basis_digest": record["original_section_basis_digest"],
        "source_files_sha256": sources,
        "operator_reference": record["arrays"]["operator"],
        "witness_reference": witness,
        "training_count": len(terms),
        "validation_count": record["validation_count"],
        "all_original_training_samples_consumed": len(terms) == 1536,
        "independent_positive_quadratic_sum_discovery": math.fsum(terms),
        **diagnostics,
        "numpy_version": record["numpy_version"],
        "scipy_version": record["scipy_version"],
        "diagnostic_is_physical_normalization": False,
        "reduced_section_basis_used": False,
        "ridge_or_pseudoinverse_used": False,
        "numerical_error_bound_certified": False,
        "exact_sample_rank_determined": False,
        "nonunit_h_iteration_executed": False,
        "ricci_flat_or_hym_metric_available": False,
        "physical_yukawas_available": False,
        "observations_used": False,
        "interpretation": "numerical diagnostic only; neither exact rank nor metric admission",
    }
    result["artifact_digest"] = full.cloud.inputs._digest(result)
    full._install_json(OUTPUT, result)
    return result


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError("provide the trusted inverse request and actual failed-step digests")
    print(
        json.dumps(
            run(
                expected_request_digest=sys.argv[1],
                expected_step_digest=sys.argv[2],
                progress=lambda r: print(json.dumps(r), flush=True),
            )
        ),
        flush=True,
    )
