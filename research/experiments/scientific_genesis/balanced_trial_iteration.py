"""Evaluate full-basis finite-cloud inverse T-operator steps in discovery arithmetic.

Owns:
    Complete unit-input kernel sums, explicit diagonal solver congruences,
    Cholesky admission, immutable inverse factors and declared projective scale.

Depends on:
    NumPy and SciPy numerical linear algebra, the original complete trial cloud,
    and exact rational bookkeeping for the computational scalar convention.

Must not:
    Reduce the section space, add a ridge, use a pseudoinverse, silently change
    H0, treat a residual as an error certificate, or infer HYM or a vacuum.

Phase 0:
    Research finite-cloud numerical steps only; physical normalization stays open.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np
import scipy
from scipy.linalg import cho_factor, cho_solve, get_lapack_funcs, solve_triangular

from . import full_trial_cloud as full

ROOT = full.ROOT
REQUEST = full.OUTPUT.with_name("balanced_trial_request.json")
OUTPUT = full.OUTPUT.with_name("balanced_trial_step.json")
PROOF = Path(__file__).with_name("BALANCED_TRIAL_ITERATION_NOTE.md")


def _sources():
    result = full._sources()
    for path in (Path(__file__), PROOF):
        result[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def create_request(
    *,
    expected_cloud_request_digest,
    block_size,
    maximum_hermitian_residual,
    minimum_reciprocal_condition,
    maximum_inverse_residual,
):
    """Fix the numerical inverse admission policy before the full cloud completes."""

    if (
        type(block_size) is not int
        or block_size < 1
        or any(
            not isinstance(value, float) or not 0 < value < 1
            for value in (
                maximum_hermitian_residual,
                minimum_reciprocal_condition,
                maximum_inverse_residual,
            )
        )
    ):
        raise ValueError("explicit numerical policies required before solving")
    if REQUEST.exists():
        raise FileExistsError("preserve the original numerical inverse admission request")
    parent = full.read_request(expected_digest=expected_cloud_request_digest)
    record = {
        "schema": "full-original-trial-inverse-request-v1",
        "cloud_request_digest": parent["artifact_digest"],
        "input_digest": parent["input_digest"],
        "original_section_basis_digest": parent["original_section_basis_digest"],
        "sample_count": parent["sample_count"],
        "training_count": parent["training_count"],
        "validation_count": parent["validation_count"],
        "initial_form": parent["section_form"],
        "policy": {
            "block_size": block_size,
            "maximum_hermitian_residual": maximum_hermitian_residual,
            "minimum_reciprocal_condition": minimum_reciprocal_condition,
            "maximum_inverse_residual": maximum_inverse_residual,
        },
        "source_files_sha256": _sources(),
        "required_population": "all original training and validation checkpoints",
        "update_count": 1,
        "projective_scale_convention": "r*mean(w)/N; explicit computational scalar gauge",
        "entropy_assumption_status": "ASSUMED",
        "parameter_point_status": "SELECTED",
        "observations_used": False,
    }
    record["artifact_digest"] = full.cloud.inputs._digest(record)
    full._install_json(REQUEST, record)
    return record


def read_request(*, expected_digest, path=REQUEST):
    """Verify the trusted inverse policy without entropy or geometric replay."""

    record = json.loads(path.read_bytes())
    unsigned = {k: v for k, v in record.items() if k != "artifact_digest"}
    if (
        record.get("artifact_digest") != expected_digest
        or full.cloud.inputs._digest(unsigned) != expected_digest
    ):
        raise ValueError("the trusted inverse policy request changed")
    parent = full.read_request(expected_digest=record["cloud_request_digest"])
    policy = record["policy"]
    if (
        record["schema"] != "full-original-trial-inverse-request-v1"
        or record["source_files_sha256"] != _sources()
        or any(
            record[k] != parent[k]
            for k in (
                "input_digest",
                "original_section_basis_digest",
                "sample_count",
                "training_count",
                "validation_count",
            )
        )
        or record["initial_form"] != parent["section_form"]
        or record["required_population"] != "all original training and validation checkpoints"
        or type(record["update_count"]) is not int
        or record["update_count"] != 1
        or record["projective_scale_convention"]
        != "r*mean(w)/N; explicit computational scalar gauge"
        or record["entropy_assumption_status"] != "ASSUMED"
        or record["parameter_point_status"] != "SELECTED"
        or record["observations_used"] is not False
        or set(policy)
        != {
            "block_size",
            "maximum_hermitian_residual",
            "minimum_reciprocal_condition",
            "maximum_inverse_residual",
        }
        or type(policy["block_size"]) is not int
        or policy["block_size"] < 1
        or any(
            not isinstance(policy[k], float) or not 0 < policy[k] < 1
            for k in (
                "maximum_hermitian_residual",
                "minimum_reciprocal_condition",
                "maximum_inverse_residual",
            )
        )
    ):
        raise ValueError("the original inverse population, policy or scientific scope changed")
    return record


def _array_path(kind):
    if kind not in ("operator", "diagonal", "lower"):
        raise ValueError("an explicit original-basis array kind required")
    return OUTPUT.with_name(f"balanced_trial_step.{kind}.npy")


def _array_digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _install_array(path, array, dtype):
    """Atomically install a deterministic non-pickle full-coordinate array."""

    fd, temporary = tempfile.mkstemp(prefix=".balanced-array-", dir=path.parent)
    scratch = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as stream:
            np.lib.format.write_array(stream, np.asarray(array, dtype=dtype), allow_pickle=False)
            stream.flush()
            os.fsync(stream.fileno())
        digest = _array_digest(scratch)
        try:
            os.link(scratch, path)
        except FileExistsError:
            if _array_digest(path) != digest:
                raise FileExistsError(
                    "preserve the original full-coordinate numerical array"
                ) from None
        return {
            "path": str(path.relative_to(ROOT)),
            "sha256": digest,
            "shape": list(array.shape),
            "dtype": dtype,
            "numpy_pickle_used": False,
        }
    finally:
        scratch.unlink(missing_ok=True)


def run_full_cloud(*, expected_request_digest, expected_cloud_digest, progress=None):
    """Execute the real full training inverse only after the whole cloud is available."""

    request = read_request(expected_digest=expected_request_digest)
    manifest = full.read_cloud(
        expected_request_digest=request["cloud_request_digest"],
        expected_digest=expected_cloud_digest,
    )
    if not manifest["complete_original_workload_available"]:
        raise ValueError("every original training and validation sample must resolve")
    parent = full.read_request(expected_digest=request["cloud_request_digest"])
    inputs = full.cloud.inputs.read_inputs(
        expected_digest=request["input_digest"], path=full.INPUTS
    )
    sources = _sources()
    if OUTPUT.exists():
        raise FileExistsError("retain the existing full-cloud inverse result")
    if progress is not None:
        progress(
            {"phase": "all original checkpoints verified", "sample_count": parent["sample_count"]}
        )

    def samples():
        for ordinal in range(parent["training_count"]):
            saved = full._read_sample(parent, inputs, ordinal)
            final = saved["history"][-1]
            if final.get("kernel_status") != "computed_discovery" or saved["role"] != "training":
                raise ValueError("a failed or reselected original sample prevents the inverse")
            yield (
                saved["sample_id"],
                np.asarray(full.cloud._decode_rows(final["kernel_rows"]), dtype=np.complex128),
                float.fromhex(final["weight_midpoint_without_pi_cubed"]),
            )
            if progress is not None and (ordinal + 1) % request["policy"]["block_size"] == 0:
                progress(
                    {"phase": "training accumulation", "original_samples_consumed": ordinal + 1}
                )

    operator, mean, summation = unit_operator(
        samples(),
        sample_count=parent["training_count"],
        section_count=5345,
        fiber_rank=4,
        block_size=request["policy"]["block_size"],
        maximum_hermitian_residual=request["policy"]["maximum_hermitian_residual"],
    )
    arrays = {"operator": _install_array(_array_path("operator"), operator, "<c16")}
    if progress is not None:
        progress({"phase": "complete full-basis operator saved; testing inverse"})
    result = inverse_step(
        operator,
        mean_weight=mean,
        fiber_rank=4,
        sample_count=parent["training_count"],
        basis_digest=parent["original_section_basis_digest"],
        minimum_reciprocal_condition=request["policy"]["minimum_reciprocal_condition"],
        maximum_inverse_residual=request["policy"]["maximum_inverse_residual"],
    )
    factor = result.pop("factor", None)
    if factor is not None:
        arrays["diagonal"] = _install_array(_array_path("diagonal"), factor.diagonal, "<f8")
        arrays["lower"] = _install_array(_array_path("lower"), factor.lower, "<c16")
    if _sources() != sources:
        raise ValueError("inverse calculation sources changed during execution")
    record = {
        **result,
        "schema": "full-original-trial-inverse-step-v1",
        "inverse_request_digest": request["artifact_digest"],
        "cloud_manifest_digest": manifest["artifact_digest"],
        "cloud_request_digest": request["cloud_request_digest"],
        "input_digest": request["input_digest"],
        "source_files_sha256": sources,
        "training_operator_estimate_available": True,
        "validation_count": request["validation_count"],
        "validation_samples_used_to_select_h1": False,
        "all_original_training_and_validation_samples_retained": True,
        "summation": summation,
        "arrays": arrays,
        "initial_form": request["initial_form"],
        "entropy_assumption_status": "ASSUMED",
        "parameter_point_status": "SELECTED",
        "observations_used": False,
    }
    record["artifact_digest"] = full.cloud.inputs._digest(record)
    full._install_json(OUTPUT, record)
    return record


def read_step(*, expected_request_digest, expected_digest, path=OUTPUT):
    """Inspect a trusted discovery result; no metric or error certificate is inferred."""

    record = json.loads(path.read_bytes())
    unsigned = {k: v for k, v in record.items() if k != "artifact_digest"}
    if (
        record.get("artifact_digest") != expected_digest
        or full.cloud.inputs._digest(unsigned) != expected_digest
    ):
        raise ValueError("the trusted full-cloud inverse result changed")
    request = read_request(expected_digest=expected_request_digest)
    manifest = full.read_cloud(
        expected_request_digest=request["cloud_request_digest"],
        expected_digest=record["cloud_manifest_digest"],
    )
    computed = record["status"] == "computed_discovery"
    if (
        record["schema"] != "full-original-trial-inverse-step-v1"
        or record["status"] not in ("computed_discovery", "unresolved")
        or record["inverse_request_digest"] != request["artifact_digest"]
        or record["cloud_request_digest"] != request["cloud_request_digest"]
        or record["input_digest"] != request["input_digest"]
        or record["original_section_basis_digest"] != request["original_section_basis_digest"]
        or record["source_files_sha256"] != _sources()
        or record["section_count"] != 5345
        or record["fiber_rank"] != 4
        or record["sample_count"] != request["training_count"]
        or record["validation_count"] != request["validation_count"]
        or record["initial_form"] != request["initial_form"]
        or record["minimum_reciprocal_condition"]
        != request["policy"]["minimum_reciprocal_condition"]
        or record["maximum_inverse_residual"] != request["policy"]["maximum_inverse_residual"]
        or record["positive_full_basis_form_available"] is not computed
        or record["inverse_step_executed"] is not computed
        or manifest["complete_original_workload_available"] is not True
        or any(
            record[k] is not False
            for k in (
                "solver_equilibration_is_physical_normalization",
                "reduced_section_basis_used",
                "ridge_or_pseudoinverse_used",
                "numerical_error_bound_certified",
                "sampling_error_bound_useful",
                "controlled_integral_available",
                "ricci_flat_or_hym_metric_available",
                "physical_yukawas_available",
                "common_stabilized_vacuum_available",
                "validation_samples_used_to_select_h1",
                "observations_used",
            )
        )
        or record["training_operator_estimate_available"] is not True
        or record["all_original_training_and_validation_samples_retained"] is not True
        or record["entropy_assumption_status"] != "ASSUMED"
        or record["parameter_point_status"] != "SELECTED"
        or (
            not computed
            and (not record.get("reason") or record["nonunit_h_iteration_executed"] is not False)
        )
    ):
        raise ValueError("the original inverse result population or scientific scope changed")
    summation = record["summation"]
    if (
        summation["sample_count"] != request["training_count"]
        or summation["section_count"] != 5345
        or summation["fiber_rank"] != 4
        or summation["all_original_samples_consumed"] is not True
        or summation["full_coordinate_columns_retained"] is not True
        or summation["hermitian_roundoff_projection_explicit"] is not True
        or summation["numerical_and_input_error_certified"] is not False
        or summation["sampling_error_included"] is not False
        or not 0
        <= summation["hermitian_residual_before_roundoff_projection"]
        <= request["policy"]["maximum_hermitian_residual"]
        or Fraction(summation["mean_reference_weight_exact_dyadic"]) <= 0
    ):
        raise ValueError("the complete training summation or numerical scope changed")
    required = {"operator", "diagonal", "lower"} if computed else {"operator"}
    if set(record["arrays"]) != required:
        raise ValueError("a failed inverse must not supply a fabricated form")
    arrays = {}
    for kind in required:
        reference = record["arrays"][kind]
        n = 5345
        shape = [n] if kind == "diagonal" else [n, n]
        dtype = "<f8" if kind == "diagonal" else "<c16"
        array_path = _array_path(kind)
        if (
            reference["path"] != str(array_path.relative_to(ROOT))
            or reference["sha256"] != _array_digest(array_path)
            or reference["shape"] != shape
            or reference["dtype"] != dtype
            or reference["numpy_pickle_used"] is not False
        ):
            raise ValueError("an original full-basis array reference changed")
        array = np.load(array_path, mmap_mode="r", allow_pickle=False)
        if list(array.shape) != shape or array.dtype.str != dtype or not np.all(np.isfinite(array)):
            raise ValueError("a complete finite non-pickle original-basis array required")
        arrays[kind] = array
    factor = None
    if computed:
        coefficient = Fraction(record["projective_scale_exact_reference_fraction"])
        if (
            coefficient != 4 * Fraction(summation["mean_reference_weight_exact_dyadic"]) / 5345
            or record["projective_scale_convention"] != request["projective_scale_convention"]
            or not math.isfinite(record["equilibrated_reciprocal_condition_estimate"])
            or record["equilibrated_reciprocal_condition_estimate"]
            < request["policy"]["minimum_reciprocal_condition"]
            or not 0
            <= record["equilibrated_inverse_residual_infinity_norm"]
            <= request["policy"]["maximum_inverse_residual"]
            or record["source_operator_bytes_sha256"]
            != hashlib.sha256(memoryview(arrays["operator"]).cast("B")).hexdigest()
        ):
            raise ValueError("the declared original inverse scale or admission gate changed")
        factor = InverseForm(
            record["original_section_basis_digest"],
            arrays["diagonal"],
            arrays["lower"],
            coefficient,
        )
    return record, factor


def _immutable(array, dtype):
    value = np.asarray(array, dtype=dtype)
    # Bytes-backed views cannot be made writable again through setflags.
    return np.frombuffer(value.tobytes(order="C"), dtype=dtype).reshape(value.shape)


@dataclass(frozen=True, slots=True)
class InverseForm:
    """Original-basis H=c D^-1 L^-dagger L^-1 D^-1, not a reduced model.

    D is the explicitly declared solver congruence, not a physical normalization.
    Every original coordinate is retained. Positive c and invertible L define
    an actual positive Hermitian computational input for the next iteration.
    """

    basis_digest: str
    diagonal: np.ndarray
    lower: np.ndarray
    coefficient: Fraction

    def __post_init__(self):
        d = np.asarray(self.diagonal, dtype=np.float64)
        lower = np.asarray(self.lower, dtype=np.complex128)
        if (
            not isinstance(self.basis_digest, str)
            or not self.basis_digest
            or not isinstance(self.coefficient, Fraction)
            or self.coefficient <= 0
            or not math.isfinite(float(self.coefficient))
            or float(self.coefficient) <= 0
            or d.ndim != 1
            or not d.size
            or lower.shape != (d.size, d.size)
            or not np.all(np.isfinite(d))
            or np.any(d <= 0)
            or not np.all(np.isfinite(lower))
            or any(np.any(lower[i, i + 1 :] != 0) for i in range(d.size))
            or np.any(np.diag(lower).imag != 0)
            or np.any(np.diag(lower).real <= 0)
        ):
            raise ValueError("a complete named positive inverse factor required")
        object.__setattr__(self, "diagonal", _immutable(d, "<f8"))
        object.__setattr__(self, "lower", _immutable(lower, "<c16"))

    @property
    def section_count(self):
        return self.diagonal.size

    def apply(self, values, *, basis_digest):
        if basis_digest != self.basis_digest:
            raise ValueError("inverse actions require the original named section basis")
        values = np.asarray(values, dtype=np.complex128)
        if values.ndim not in (1, 2) or values.shape[0] != self.section_count:
            raise ValueError("all original section coordinates required")
        if not np.all(np.isfinite(values)):
            raise ValueError("finite declared discovery coordinates required")
        divisor = self.diagonal if values.ndim == 1 else self.diagonal[:, None]
        first = solve_triangular(self.lower, values / divisor, lower=True)
        second = solve_triangular(self.lower.conj().T, first, lower=False)
        result = float(self.coefficient) * second / divisor
        if not np.all(np.isfinite(result)):
            raise ArithmeticError("the full inverse action overflowed discovery arithmetic")
        return result

    def fiber_gram(self, rows, *, basis_digest):
        """Evaluate Q H Q-dagger using the actual original-basis inverse form."""

        if basis_digest != self.basis_digest:
            raise ValueError("fiber contractions require the original named section basis")
        rows = np.asarray(rows, dtype=np.complex128)
        if rows.ndim != 2 or rows.shape[1] != self.section_count or not np.all(np.isfinite(rows)):
            raise ValueError("complete finite original section rows required")
        z = solve_triangular(self.lower, (rows / self.diagonal).conj().T, lower=True)
        result = float(self.coefficient) * (z.conj().T @ z)
        if not np.all(np.isfinite(result)):
            raise ArithmeticError("the full fiber contraction overflowed discovery arithmetic")
        return result


def unit_operator(
    samples, *, sample_count, section_count, fiber_rank, block_size, maximum_hermitian_residual
):
    """Sum every supplied unit-H kernel, preserving all coordinate columns.

    Each sample is (identifier, full row matrix, positive numerical weight).
    Gram normalization accounts for nonorthonormal saved reference rows; it is
    an invertible fiber operation, not normalization of physical matter states.
    """

    if (
        any(
            type(v) is not int or v < 1
            for v in (sample_count, section_count, fiber_rank, block_size)
        )
        or fiber_rank > section_count
        or not isinstance(maximum_hermitian_residual, float)
        or not 0 < maximum_hermitian_residual < 1
    ):
        raise ValueError("explicit full counts and a numerical diagnostic tolerance required")
    operator = np.zeros((section_count, section_count), dtype=np.complex128)
    block, seen, weights = [], set(), []

    def consume():
        rows = np.concatenate(block, axis=0)
        operator[:] += rows.conj().T @ rows
        block.clear()

    for identifier, rows, weight in samples:
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError("every original sample identity must occur exactly once")
        if len(seen) >= sample_count:
            raise ValueError("the declared complete sample count changed")
        seen.add(identifier)
        rows = np.asarray(rows, dtype=np.complex128)
        if (
            rows.shape != (fiber_rank, section_count)
            or not np.all(np.isfinite(rows))
            or not isinstance(weight, float)
            or not math.isfinite(weight)
            or weight <= 0
        ):
            raise ValueError("all finite original rows and a positive declared weight required")
        gram = rows @ rows.conj().T
        factor = np.linalg.cholesky(gram)
        whitened = solve_triangular(factor, rows, lower=True)
        scale = math.sqrt(weight / sample_count)
        if scale == 0:
            raise ArithmeticError("positive sample weighting underflowed discovery arithmetic")
        block.append(whitened * scale)
        weights.append(Fraction.from_float(weight))
        if len(block) == block_size:
            consume()
    if len(seen) != sample_count:
        raise ValueError("a partial admitted subset cannot become the global operator")
    if block:
        consume()
    if not np.all(np.isfinite(operator)):
        raise ArithmeticError("the original full operator overflowed discovery arithmetic")
    magnitude = float(np.max(np.abs(operator)))
    if magnitude <= 0:
        raise ArithmeticError("the full numerical operator has no resolved positive scale")
    hermitian = float(np.max(np.abs(operator - operator.conj().T))) / magnitude
    if hermitian > maximum_hermitian_residual:
        raise ArithmeticError("the full numerical operator fails the Hermitian diagnostic")
    # This explicit roundoff projection is recorded below, not hidden as a law.
    operator = (operator + operator.conj().T) / 2
    mean_weight = sum(weights, Fraction(0)) / sample_count
    return (
        operator,
        mean_weight,
        {
            "sample_count": sample_count,
            "section_count": section_count,
            "fiber_rank": fiber_rank,
            "all_original_samples_consumed": True,
            "full_coordinate_columns_retained": True,
            "hermitian_residual_before_roundoff_projection": hermitian,
            "hermitian_roundoff_projection_explicit": True,
            "mean_reference_weight_exact_dyadic": str(mean_weight),
            "operator_trace_discovery": float(np.trace(operator).real),
            "ideal_reference_trace": str(fiber_rank * mean_weight),
            "numerical_and_input_error_certified": False,
            "sampling_error_included": False,
        },
    )


def inverse_step(
    operator,
    *,
    mean_weight,
    fiber_rank,
    sample_count,
    basis_digest,
    minimum_reciprocal_condition,
    maximum_inverse_residual,
):
    """Admit a full inverse with declared solver scaling, or return its obstruction.

    The projective scalar convention is c=r*mean(w)/N. It is explicitly r times
    the published unscaled inverse step; positive constant metric scale does not
    affect the connection. No physical volume or canonical normalization is inferred.
    """

    operator = np.asarray(operator, dtype=np.complex128)
    if (
        operator.ndim != 2
        or operator.shape[0] != operator.shape[1]
        or not operator.size
        or not np.all(np.isfinite(operator))
        or not isinstance(mean_weight, Fraction)
        or mean_weight <= 0
        or type(fiber_rank) is not int
        or fiber_rank < 1
        or type(sample_count) is not int
        or sample_count < 1
        or not isinstance(basis_digest, str)
        or not basis_digest
        or not isinstance(minimum_reciprocal_condition, float)
        or not 0 < minimum_reciprocal_condition < 1
        or not isinstance(maximum_inverse_residual, float)
        or not 0 < maximum_inverse_residual < 1
    ):
        raise ValueError(
            "a complete named operator and explicit numerical admission policy required"
        )
    n = operator.shape[0]
    base = {
        "section_count": n,
        "sample_count": sample_count,
        "fiber_rank": fiber_rank,
        "original_section_basis_digest": basis_digest,
        "solver_equilibration_is_physical_normalization": False,
        "reduced_section_basis_used": False,
        "ridge_or_pseudoinverse_used": False,
        "numerical_error_bound_certified": False,
        "sampling_error_bound_useful": False,
        "controlled_integral_available": False,
        "positive_full_basis_form_available": False,
        "inverse_step_executed": False,
        "nonunit_h_iteration_executed": False,
        "ricci_flat_or_hym_metric_available": False,
        "physical_yukawas_available": False,
        "common_stabilized_vacuum_available": False,
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "minimum_reciprocal_condition": minimum_reciprocal_condition,
        "maximum_inverse_residual": maximum_inverse_residual,
    }
    if fiber_rank * sample_count < n:
        return {
            **base,
            "status": "unresolved",
            "reason": "original sample-rank bound forbids inversion",
        }
    if np.max(np.abs(operator - operator.conj().T)) != 0:
        raise ValueError("the explicitly Hermitian full operator is required")
    diagonal = operator.diagonal().real
    if np.any(diagonal <= 0):
        return {
            **base,
            "status": "unresolved",
            "reason": "an original coordinate has unresolved positive norm",
        }
    scales = np.sqrt(diagonal)
    normalized = np.asfortranarray(operator / scales[:, None] / scales[None, :])
    norm_one = float(np.linalg.norm(normalized, 1))
    base["original_diagonal_ratio_discovery"] = float(np.max(diagonal) / np.min(diagonal))
    base["solver_congruence"] = (
        "B = D^-1 A D^-1; D = sqrt(diag A), all original coordinates retained"
    )
    try:
        chol, lower = cho_factor(normalized, lower=True, overwrite_a=False)
    except np.linalg.LinAlgError:
        return {
            **base,
            "status": "unresolved",
            "reason": "full equilibrated Cholesky positivity is unresolved",
        }
    pocon = get_lapack_funcs("pocon", (chol,))
    reciprocal, info = pocon(chol, norm_one, uplo="L")
    base["equilibrated_reciprocal_condition_estimate"] = float(reciprocal)
    if info != 0 or not math.isfinite(reciprocal) or reciprocal < minimum_reciprocal_condition:
        return {
            **base,
            "status": "unresolved",
            "reason": "full inverse conditioning fails the declared resolution gate",
        }
    inverse = cho_solve((chol, lower), np.eye(n, dtype=np.complex128))
    residual = normalized @ inverse
    residual.flat[:: n + 1] -= 1
    relative = float(np.linalg.norm(residual, np.inf))
    base["equilibrated_inverse_residual_infinity_norm"] = relative
    if not math.isfinite(relative) or relative > maximum_inverse_residual:
        return {
            **base,
            "status": "unresolved",
            "reason": "full inverse residual fails the declared gate",
        }
    del inverse, residual, normalized
    coefficient = fiber_rank * mean_weight / n
    if not math.isfinite(float(coefficient)) or float(coefficient) <= 0:
        return {
            **base,
            "status": "unresolved",
            "reason": "positive projective inverse scale is unresolved in discovery arithmetic",
        }
    factor = InverseForm(basis_digest, scales, np.tril(chol), coefficient)
    # A scalar identity update requires A to be a scalar identity. Diagnose that
    # in the original basis without constructing a second full inverse matrix.
    scalar = float(np.trace(operator).real) / n
    deviation = operator.copy()
    deviation.flat[:: n + 1] -= scalar
    non_scalar = float(np.linalg.norm(deviation, "fro") / np.linalg.norm(operator, "fro"))
    return {
        **base,
        "status": "computed_discovery",
        "factor": factor,
        "positive_full_basis_form_available": True,
        "inverse_step_executed": True,
        "nonunit_h_iteration_executed": non_scalar > maximum_inverse_residual,
        "original_operator_non_scalar_deviation_discovery": non_scalar,
        "source_operator_bytes_sha256": hashlib.sha256(
            memoryview(np.ascontiguousarray(operator)).cast("B")
        ).hexdigest(),
        "projective_scale_convention": "r*mean(w)/N; explicit computational scalar gauge",
        "projective_scale_exact_reference_fraction": str(coefficient),
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError("provide the trusted inverse request and complete cloud digests")
    result = run_full_cloud(
        expected_request_digest=sys.argv[1],
        expected_cloud_digest=sys.argv[2],
        progress=lambda r: print(json.dumps(r), flush=True),
    )
    print(json.dumps(result), flush=True)
