"""Inspect the complete weighted sample factor before forming its normal Gram.

Owns:
    Original-coordinate weighted kernel rows, full unpivoted Householder QR,
    whole-factor reconstruction diagnostics and triangular condition estimates.

Depends on:
    The trusted actual full cloud and failed inverse, frozen original kernel
    readers, and NumPy/SciPy numerical linear algebra in discovery arithmetic.

Must not:
    Reduce the section space, drop samples, change H0, regularize, infer exact
    rank from floating diagonals, relax the old inverse gate or export H1.

Phase 0:
    Research full-factor diagnostics only; no physical metric is provided.
"""

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.linalg import get_lapack_funcs, qr, solve_triangular

from . import balanced_trial_iteration as inverse

full = inverse.full
OUTPUT = inverse.OUTPUT.with_name("full_trial_sample_factor.json")
FACTOR = OUTPUT.with_name("full_trial_sample_factor.weighted.npy")
UPPER = OUTPUT.with_name("full_trial_sample_factor.upper.npy")
NOTE = Path(__file__).with_name("FULL_TRIAL_SAMPLE_FACTOR_NOTE.md")


def _sources():
    result = inverse._sources()
    for path in (Path(__file__), NOTE):
        result[str(path.relative_to(full.ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def factor_diagnostic(matrix, scales, *, block_size, progress=None):
    """Use every row and column; reflectors never represent physical basis data."""

    matrix = np.asarray(matrix, dtype=np.complex128)
    scales = np.asarray(scales, dtype=np.float64)
    if (
        matrix.ndim != 2
        or not matrix.size
        or matrix.shape[0] < matrix.shape[1]
        or scales.shape != (matrix.shape[1],)
        or not np.all(np.isfinite(matrix))
        or not np.all(np.isfinite(scales))
        or np.any(scales <= 0)
        or type(block_size) is not int
        or block_size < 1
    ):
        raise ValueError("a complete finite tall factor and positive explicit scales required")
    working = np.array(matrix, dtype=np.complex128, order="F", copy=True)
    working /= scales[None, :]
    if not np.all(np.isfinite(working)):
        raise ArithmeticError("full-factor solver congruence overflowed")
    if progress:
        progress({"phase": "full original-column Householder factorization"})
    (packed, tau), upper = qr(
        working,
        mode="raw",
        pivoting=False,
        overwrite_a=True,
        check_finite=False,
    )
    if not np.all(np.isfinite(upper)):
        raise ArithmeticError("the full triangular factor is unresolved")
    apply = get_lapack_funcs("unmqr", (packed,))
    n = matrix.shape[1]
    errors, norms = [], []
    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = np.array(matrix[:, start:end], dtype=np.complex128, order="F", copy=True)
        block /= scales[None, start:end]
        norms.append(float(np.linalg.norm(block, "fro")) ** 2)
        _, workspace, info = apply("L", "C", packed, tau, block, -1)
        if info:
            raise ArithmeticError("full-reflector workspace query failed")
        transformed, _, info = apply(
            "L",
            "C",
            packed,
            tau,
            block,
            int(workspace[0].real),
            overwrite_c=True,
        )
        if info or not np.all(np.isfinite(transformed)):
            raise ArithmeticError("the complete factor reconstruction is unresolved")
        transformed[:n] -= upper[:, start:end]
        errors.append(float(np.linalg.norm(transformed, "fro")) ** 2)
        if progress:
            progress({"phase": "complete factor reconstruction", "columns_checked": end})
    condition = get_lapack_funcs("trcon", (upper,))
    reciprocal, info = condition(upper, norm="1", uplo="U", diag="N")
    if info or not math.isfinite(reciprocal) or not 0 <= reciprocal <= 1:
        raise ArithmeticError("the full triangular condition estimate is unresolved")
    diagonal = np.abs(np.diag(upper))
    return upper, {
        "sample_factor_shape": list(matrix.shape),
        "upper_factor_shape": list(upper.shape),
        "original_column_order_retained": True,
        "pivoting_used": False,
        "qr_driver": "LAPACK zgeqrf; raw reflectors; full-column zunmqr check",
        "solver_congruence": "weighted sample factor times D^-1; D=sqrt(diag original A)",
        "reconstruction_block_size": block_size,
        "reconstruction_columns_checked": n,
        "qr_relative_reconstruction_residual_discovery": math.sqrt(
            math.fsum(errors) / math.fsum(norms)
        ),
        "triangular_reciprocal_condition_estimate_one_norm": float(reciprocal),
        "minimum_absolute_triangular_diagonal_discovery": float(np.min(diagonal)),
        "maximum_absolute_triangular_diagonal_discovery": float(np.max(diagonal)),
        "zero_triangular_diagonal_count_discovery": int(np.count_nonzero(diagonal == 0)),
    }


def run(*, expected_request_digest, expected_step_digest, block_size, progress=None):
    """Diagnose the original full training population, never an admitted subset."""

    if OUTPUT.exists():
        raise FileExistsError("preserve the original complete sample-factor result")
    if type(block_size) is not int or block_size < 1:
        raise ValueError("an explicit positive reconstruction block size required")
    step, form = inverse.read_step(
        expected_request_digest=expected_request_digest,
        expected_digest=expected_step_digest,
    )
    if form is not None or step["status"] != "unresolved":
        raise ValueError("this diagnostic requires the actual unresolved original inverse")
    sources = _sources()
    operator = np.load(inverse._array_path("operator"), mmap_mode="r", allow_pickle=False)
    scales = np.sqrt(np.diag(operator).real).copy()
    del operator
    parent = full.read_request(expected_digest=step["cloud_request_digest"])
    inputs = full.cloud.inputs.read_inputs(expected_digest=step["input_digest"], path=full.INPUTS)
    n, rank, count = 5345, 4, parent["training_count"]
    weighted = np.empty((rank * count, n), dtype=np.complex128)
    for ordinal in range(count):
        saved = full._read_sample(parent, inputs, ordinal)
        if saved["role"] != "training":
            raise ValueError("an original training ordinal changed roles")
        final = saved["history"][-1]
        rows = np.asarray(full.cloud._decode_rows(final["kernel_rows"]), dtype=np.complex128)
        whitening = np.linalg.cholesky(rows @ rows.conj().T)
        weight = float.fromhex(final["weight_midpoint_without_pi_cubed"])
        scale = math.sqrt(weight / count)
        if not math.isfinite(scale) or scale <= 0:
            raise ArithmeticError("an original positive weighting is unresolved")
        weighted[rank * ordinal : rank * (ordinal + 1)] = (
            solve_triangular(whitening, rows, lower=True) * scale
        )
        if progress and (ordinal + 1) % 128 == 0:
            progress({"phase": "original weighted factor construction", "samples": ordinal + 1})
    reference = inverse._install_array(FACTOR, weighted, "<c16")
    del weighted
    weighted = np.load(FACTOR, mmap_mode="r", allow_pickle=False)
    upper, diagnostics = factor_diagnostic(
        weighted,
        scales,
        block_size=block_size,
        progress=progress,
    )
    upper_reference = inverse._install_array(UPPER, upper, "<c16")
    if _sources() != sources:
        raise ValueError("full sample-factor sources changed during execution")
    result = {
        "schema": "full-original-trial-sample-factor-v1",
        "inverse_request_digest": expected_request_digest,
        "inverse_step_digest": step["artifact_digest"],
        "cloud_manifest_digest": step["cloud_manifest_digest"],
        "original_section_basis_digest": step["original_section_basis_digest"],
        "source_files_sha256": sources,
        "training_count": count,
        "validation_count": step["validation_count"],
        "section_count": n,
        "fiber_rank": rank,
        "all_original_training_samples_consumed": True,
        "all_original_validation_samples_retained": True,
        "validation_used_for_factorization": False,
        "initial_form": step["initial_form"],
        "weighted_factor_reference": reference,
        "upper_factor_reference": upper_reference,
        **diagnostics,
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "diagnostic_is_physical_normalization": False,
        "reduced_section_basis_used": False,
        "ridge_or_pseudoinverse_used": False,
        "previous_inverse_policy_changed": False,
        "numerical_error_bound_certified": False,
        "exact_sample_rank_determined": False,
        "positive_full_basis_form_available": False,
        "inverse_step_executed": False,
        "nonunit_h_iteration_executed": False,
        "ricci_flat_or_hym_metric_available": False,
        "physical_yukawas_available": False,
        "common_stabilized_vacuum_available": False,
        "observations_used": False,
    }
    result["artifact_digest"] = full.cloud.inputs._digest(result)
    full._install_json(OUTPUT, result)
    return result


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise ValueError(
            "provide trusted inverse-request/step digests and reconstruction block size"
        )
    print(
        json.dumps(
            run(
                expected_request_digest=sys.argv[1],
                expected_step_digest=sys.argv[2],
                block_size=int(sys.argv[3]),
                progress=lambda item: print(json.dumps(item), flush=True),
            )
        ),
        flush=True,
    )
