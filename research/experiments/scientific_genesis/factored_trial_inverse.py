"""Evaluate a separately declared full-factor inverse update in discovery arithmetic.

Owns:
    Explicit real QR row phases, triangular conditioning and whole inverse
    residual gates, and a complete original-basis computational H1 factor.

Depends on:
    The trusted complete sample factor and original failed Gram trial, the
    frozen inverse-form algebra, exact scalar bookkeeping and SciPy solvers.

Must not:
    Retroactively admit the failed Gram trial, change H0 or the sample space,
    regularize, infer physical normalization or claim controlled HYM convergence.

Phase 0:
    Research numerical full-factor updates only; physical metrics remain missing.
"""

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.linalg import get_lapack_funcs, solve_triangular

from . import full_trial_sample_factor as sample

inverse, full = sample.inverse, sample.full
OUTPUT = sample.OUTPUT.with_name("factored_trial_inverse.json")
REQUEST = OUTPUT.with_name("factored_trial_inverse_request.json")
NOTE = Path(__file__).with_name("FACTORED_TRIAL_INVERSE_NOTE.md")


def _sources():
    result = sample._sources()
    for path in (Path(__file__), NOTE):
        result[str(path.relative_to(full.ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def read_factor(expected_digest):
    """Inspect the original full factor and its source-bound numerical scope."""

    record = json.loads(sample.OUTPUT.read_bytes())
    unsigned = {key: value for key, value in record.items() if key != "artifact_digest"}
    if (
        record.get("artifact_digest") != expected_digest
        or full.cloud.inputs._digest(unsigned) != expected_digest
        or record["source_files_sha256"] != sample._sources()
        or record["section_count"] != 5345
        or record["training_count"] != 1536
        or record["validation_count"] != 512
        or record["reconstruction_columns_checked"] != 5345
        or record["original_column_order_retained"] is not True
        or record["all_original_training_samples_consumed"] is not True
        or record["all_original_validation_samples_retained"] is not True
        or any(
            record[key] is not False
            for key in (
                "pivoting_used",
                "validation_used_for_factorization",
                "diagnostic_is_physical_normalization",
                "reduced_section_basis_used",
                "ridge_or_pseudoinverse_used",
                "previous_inverse_policy_changed",
                "numerical_error_bound_certified",
                "exact_sample_rank_determined",
                "positive_full_basis_form_available",
                "inverse_step_executed",
                "nonunit_h_iteration_executed",
                "ricci_flat_or_hym_metric_available",
                "physical_yukawas_available",
                "common_stabilized_vacuum_available",
                "observations_used",
            )
        )
    ):
        raise ValueError("the trusted complete sample factor or its scientific scope changed")
    for key, path, shape in (
        ("weighted_factor_reference", sample.FACTOR, [6144, 5345]),
        ("upper_factor_reference", sample.UPPER, [5345, 5345]),
    ):
        ref = record[key]
        if (
            ref["path"] != str(path.relative_to(full.ROOT))
            or ref["sha256"] != inverse._array_digest(path)
            or ref["shape"] != shape
            or ref["dtype"] != "<c16"
            or ref["numpy_pickle_used"] is not False
        ):
            raise ValueError("a complete original-coordinate sample-factor array changed")
    return record


def create_request(
    *,
    expected_factor_digest,
    minimum_reciprocal_condition,
    maximum_triangular_inverse_residual,
    block_size,
):
    """Declare the distinct factor-solver gates before computing its inverse."""

    if REQUEST.exists():
        raise FileExistsError("preserve the separately declared factor-inverse policy")
    if (
        type(block_size) is not int
        or block_size < 1
        or any(
            type(value) is not float or not 0 < value < 1
            for value in (minimum_reciprocal_condition, maximum_triangular_inverse_residual)
        )
    ):
        raise ValueError("explicit full-factor inverse policies required")
    parent = read_factor(expected_factor_digest)
    record = {
        "schema": "full-factor-trial-inverse-request-v1",
        "sample_factor_digest": parent["artifact_digest"],
        "inverse_request_digest": parent["inverse_request_digest"],
        "original_gram_step_digest": parent["inverse_step_digest"],
        "original_section_basis_digest": parent["original_section_basis_digest"],
        "source_files_sha256": _sources(),
        "minimum_reciprocal_condition_of_triangular_factor": minimum_reciprocal_condition,
        "maximum_triangular_inverse_residual_infinity_norm": maximum_triangular_inverse_residual,
        "inverse_check_block_size": block_size,
        "old_gram_policy_modified": False,
        "new_policy_is_distinct_from_gram_inverse_policy": True,
        "projective_scale_convention": "r*mean(w)/N; explicit computational scalar gauge",
    }
    record["artifact_digest"] = full.cloud.inputs._digest(record)
    full._install_json(REQUEST, record)
    return record


def admitted_upper(
    upper,
    *,
    minimum_reciprocal_condition,
    maximum_triangular_inverse_residual,
    block_size,
    progress=None,
):
    """Check every column of R R-inverse; never solve a regularized normal matrix."""

    upper = np.asarray(upper, dtype=np.complex128)
    if (
        upper.ndim != 2
        or not upper.size
        or upper.shape[0] != upper.shape[1]
        or not np.all(np.isfinite(upper))
        or np.any(np.tril(upper, -1) != 0)
        or np.any(np.diag(upper).imag != 0)
        or np.any(np.diag(upper).real == 0)
        or type(block_size) is not int
        or block_size < 1
        or any(
            type(value) is not float or not 0 < value < 1
            for value in (minimum_reciprocal_condition, maximum_triangular_inverse_residual)
        )
    ):
        raise ValueError("a complete real-diagonal triangular factor and explicit gates required")
    phases = np.sign(np.diag(upper).real)
    canonical = np.array(upper, dtype=np.complex128, order="F", copy=True)
    canonical *= phases[:, None]
    # Row signs are explicit unitary solver operations: R'-dagger R'=R-dagger R.
    condition = get_lapack_funcs("trcon", (canonical,))
    reciprocal, info = condition(canonical, norm="1", uplo="U", diag="N")
    record = {
        "status": "unresolved",
        "positive_full_basis_form_available": False,
        "inverse_step_executed": False,
        "nonunit_h_iteration_executed": False,
        "triangular_reciprocal_condition_estimate_one_norm": float(reciprocal),
        "row_phase_convention": "explicit sign of each original real QR diagonal",
        "section_count": upper.shape[0],
    }
    if info or not math.isfinite(reciprocal) or reciprocal < minimum_reciprocal_condition:
        return None, phases, {**record, "reason": "full triangular conditioning gate unresolved"}
    n = upper.shape[0]
    error_rows = np.zeros(n)
    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        rhs = np.zeros((n, end - start), dtype=np.complex128)
        rhs[np.arange(start, end), np.arange(end - start)] = 1
        solved = solve_triangular(canonical, rhs, lower=False, check_finite=False)
        residual = canonical @ solved - rhs
        if not np.all(np.isfinite(residual)):
            return None, phases, {**record, "reason": "full triangular inverse overflowed"}
        error_rows += np.sum(np.abs(residual), axis=1)
        if progress:
            progress({"phase": "full triangular inverse check", "columns_checked": end})
    residual_norm = float(np.max(error_rows))
    record["triangular_inverse_residual_infinity_norm"] = residual_norm
    record["inverse_check_columns"] = n
    if residual_norm > maximum_triangular_inverse_residual:
        return (
            None,
            phases,
            {**record, "reason": "full triangular inverse residual gate unresolved"},
        )
    return (
        canonical.conj().T,
        phases,
        {
            **record,
            "status": "computed_discovery",
            "positive_full_basis_form_available": True,
            "inverse_step_executed": True,
        },
    )


def run(expected_request_digest, *, progress=None):
    """Execute the distinct full-factor update; the old failed trial stays failed."""

    if OUTPUT.exists():
        raise FileExistsError("preserve the original full-factor inverse result")
    request = json.loads(REQUEST.read_bytes())
    if (
        request.get("artifact_digest") != expected_request_digest
        or full.cloud.inputs._digest({k: v for k, v in request.items() if k != "artifact_digest"})
        != expected_request_digest
        or request["source_files_sha256"] != _sources()
    ):
        raise ValueError("the separately declared factor-inverse request changed")
    parent = read_factor(request["sample_factor_digest"])
    step, original_form = inverse.read_step(
        expected_request_digest=parent["inverse_request_digest"],
        expected_digest=parent["inverse_step_digest"],
    )
    if original_form is not None or step["status"] != "unresolved":
        raise ValueError("the old original Gram failure must remain unchanged")
    before = _sources()
    upper = np.load(sample.UPPER, mmap_mode="r", allow_pickle=False)
    lower, phases, result = admitted_upper(
        upper,
        minimum_reciprocal_condition=request["minimum_reciprocal_condition_of_triangular_factor"],
        maximum_triangular_inverse_residual=request[
            "maximum_triangular_inverse_residual_infinity_norm"
        ],
        block_size=request["inverse_check_block_size"],
        progress=progress,
    )
    arrays = {}
    coefficient = 4 * Fraction(step["summation"]["mean_reference_weight_exact_dyadic"]) / 5345
    if lower is not None:
        operator = np.load(inverse._array_path("operator"), mmap_mode="r", allow_pickle=False)
        diagonal = np.sqrt(np.diag(operator).real).copy()
        for kind, array, dtype in (
            ("lower", lower, "<c16"),
            ("diagonal", diagonal, "<f8"),
            ("row_phases", phases, "<f8"),
        ):
            arrays[kind] = inverse._install_array(
                OUTPUT.with_name(f"factored_trial_inverse.{kind}.npy"),
                array,
                dtype,
            )
    if _sources() != before:
        raise ValueError("full-factor inverse sources changed during execution")
    record = {
        **result,
        "schema": "full-factor-trial-inverse-v1",
        "request_digest": expected_request_digest,
        "sample_factor_digest": parent["artifact_digest"],
        "cloud_manifest_digest": parent["cloud_manifest_digest"],
        "original_gram_step_digest": step["artifact_digest"],
        "original_section_basis_digest": parent["original_section_basis_digest"],
        "source_files_sha256": before,
        "arrays": arrays,
        "training_count": 1536,
        "validation_count": 512,
        "initial_form": step["initial_form"],
        "projective_scale_exact_reference_fraction": str(coefficient),
        "projective_scale_convention": request["projective_scale_convention"],
        "all_original_training_and_validation_samples_retained": True,
        "old_gram_policy_modified": False,
        "new_policy_is_distinct_from_gram_inverse_policy": True,
        "validation_samples_used_to_select_h1": False,
        "reduced_section_basis_used": False,
        "ridge_or_pseudoinverse_used": False,
        "solver_phases_are_physical_normalization": False,
        "numerical_error_bound_certified": False,
        "sampling_error_bound_useful": False,
        "controlled_integral_available": False,
        "ricci_flat_or_hym_metric_available": False,
        "physical_yukawas_available": False,
        "common_stabilized_vacuum_available": False,
        "parameter_point_status": "SELECTED",
        "entropy_assumption_status": "ASSUMED",
        "observations_used": False,
    }
    record["nonunit_h_iteration_executed"] = (
        lower is not None and step["original_diagonal_ratio_discovery"] > 1 + 1e-6
    )
    record["artifact_digest"] = full.cloud.inputs._digest(record)
    full._install_json(OUTPUT, record)
    return record


def read_result(*, expected_request_digest, expected_digest):
    """Read an actual admitted full-basis computational form, never a physical metric."""

    record = json.loads(OUTPUT.read_bytes())
    if (
        record.get("artifact_digest") != expected_digest
        or full.cloud.inputs._digest({k: v for k, v in record.items() if k != "artifact_digest"})
        != expected_digest
        or record["source_files_sha256"] != _sources()
        or record["request_digest"] != expected_request_digest
    ):
        raise ValueError("the trusted full-factor inverse result changed")
    request = json.loads(REQUEST.read_bytes())
    if (
        request.get("artifact_digest") != expected_request_digest
        or full.cloud.inputs._digest({k: v for k, v in request.items() if k != "artifact_digest"})
        != expected_request_digest
        or request["source_files_sha256"] != _sources()
    ):
        raise ValueError("the separate full-factor inverse policy changed")
    parent = read_factor(request["sample_factor_digest"])
    computed = record["status"] == "computed_discovery"
    if (
        record["status"] not in ("computed_discovery", "unresolved")
        or record["sample_factor_digest"] != parent["artifact_digest"]
        or record["original_gram_step_digest"] != parent["inverse_step_digest"]
        or record["cloud_manifest_digest"] != parent["cloud_manifest_digest"]
        or record["original_section_basis_digest"] != parent["original_section_basis_digest"]
        or record["section_count"] != 5345
        or record["training_count"] != 1536
        or record["validation_count"] != 512
        or record["positive_full_basis_form_available"] is not computed
        or record["inverse_step_executed"] is not computed
        or record["all_original_training_and_validation_samples_retained"] is not True
        or record["new_policy_is_distinct_from_gram_inverse_policy"] is not True
        or any(
            record[key] is not False
            for key in (
                "old_gram_policy_modified",
                "validation_samples_used_to_select_h1",
                "reduced_section_basis_used",
                "ridge_or_pseudoinverse_used",
                "solver_phases_are_physical_normalization",
                "numerical_error_bound_certified",
                "sampling_error_bound_useful",
                "controlled_integral_available",
                "ricci_flat_or_hym_metric_available",
                "physical_yukawas_available",
                "common_stabilized_vacuum_available",
                "observations_used",
            )
        )
    ):
        raise ValueError("the complete computational form or its physical scope changed")
    if not computed:
        if record["arrays"] or not record.get("reason") or record["nonunit_h_iteration_executed"]:
            raise ValueError("an unresolved full-factor inverse must not export a form")
        return record, None
    if (
        record["triangular_reciprocal_condition_estimate_one_norm"]
        < request["minimum_reciprocal_condition_of_triangular_factor"]
        or not 0
        <= record["triangular_inverse_residual_infinity_norm"]
        <= request["maximum_triangular_inverse_residual_infinity_norm"]
        or record["inverse_check_columns"] != 5345
        or set(record["arrays"]) != {"lower", "diagonal", "row_phases"}
    ):
        raise ValueError("an admitted complete triangular inverse is required")
    arrays = {}
    for kind, shape, dtype in (
        ("lower", [5345, 5345], "<c16"),
        ("diagonal", [5345], "<f8"),
        ("row_phases", [5345], "<f8"),
    ):
        path = OUTPUT.with_name(f"factored_trial_inverse.{kind}.npy")
        ref = record["arrays"][kind]
        if (
            ref["path"] != str(path.relative_to(full.ROOT))
            or ref["sha256"] != inverse._array_digest(path)
            or ref["shape"] != shape
            or ref["dtype"] != dtype
            or ref["numpy_pickle_used"] is not False
        ):
            raise ValueError("an original-basis full-factor inverse array changed")
        arrays[kind] = np.load(path, mmap_mode="r", allow_pickle=False)
    if not np.all(np.isin(arrays["row_phases"], (-1.0, 1.0))):
        raise ValueError("the explicit real QR row phases changed")
    coefficient = Fraction(record["projective_scale_exact_reference_fraction"])
    step = json.loads(inverse.OUTPUT.read_bytes())
    if (
        step["artifact_digest"] != parent["inverse_step_digest"]
        or full.cloud.inputs._digest({k: v for k, v in step.items() if k != "artifact_digest"})
        != parent["inverse_step_digest"]
        or coefficient
        != 4 * Fraction(step["summation"]["mean_reference_weight_exact_dyadic"]) / 5345
    ):
        raise ValueError("the original exact reference scalar changed")
    return record, inverse.InverseForm(
        record["original_section_basis_digest"],
        arrays["diagonal"],
        arrays["lower"],
        coefficient,
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("provide the separately declared full-factor inverse request digest")
    print(
        json.dumps(run(sys.argv[1], progress=lambda r: print(json.dumps(r), flush=True))),
        flush=True,
    )
