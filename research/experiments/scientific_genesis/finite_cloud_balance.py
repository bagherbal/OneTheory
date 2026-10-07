"""Test weighted finite-cloud balance without changing the section space.

Owns:
    Exact atomic-mass necessary conditions for a balanced empirical measure,
    retained-input certificates and full-coordinate H1 witness diagnostics.

Depends on:
    The original cloud readers, its rational positive-weight enclosures, the
    admitted full-factor H1 and research-only numerical linear algebra.

Must not:
    Infer continuum bundle instability from an empirical obstruction, discard
    samples, truncate sections, reweight the cloud or report HYM convergence.

Phase 0:
    Research finite-measure falsification only; physical metrics remain missing.
"""

import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.linalg import get_lapack_funcs, solve_triangular

from . import factored_trial_inverse as parent

full = parent.full
OUTPUT = parent.OUTPUT.with_name("finite_cloud_balance.json")
PROBE_REQUEST = OUTPUT.with_name("finite_cloud_balance_h1_request.json")
PROBE_OUTPUT = OUTPUT.with_name("finite_cloud_balance_h1.json")
NOTE = Path(__file__).with_name("FINITE_CLOUD_BALANCE_NOTE.md")


def _sources():
    result = parent._sources()
    for path in (Path(__file__), NOTE):
        result[str(path.relative_to(full.ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def atomic_bound(weights, *, section_count, fiber_rank):
    """Bound every positive-form balance operator using exact weight intervals.

    Entries are (ordinal, lower, reference, upper), all three weights Fraction.
    Passing the condition is necessary, never sufficient for balance or span.
    """

    rows = tuple(weights)
    if (
        type(section_count) is not int
        or type(fiber_rank) is not int
        or not 0 < fiber_rank <= section_count
        or not rows
        or any(len(row) != 4 for row in rows)
    ):
        raise ValueError("positive section/fiber dimensions and complete exact weights required")
    if len({row[0] for row in rows}) != len(rows):
        raise ValueError("each original weight ordinal must occur exactly once")
    for ordinal, lower, reference, upper in rows:
        if type(ordinal) is not int or ordinal < 0:
            raise ValueError("original integer ordinals required")
        if any(type(value) is not Fraction for value in (lower, reference, upper)):
            raise TypeError("weight endpoints and references must be exact Fractions")
        if not 0 < lower <= reference <= upper:
            raise ValueError("positive ordered intervals must contain their reference weight")
    total_upper = sum((row[3] for row in rows), Fraction())
    total_reference = sum((row[2] for row in rows), Fraction())
    # Deterministic first-in-ordinal-order witnesses, not a new basis or sample.
    witness = max(sorted(rows), key=lambda row: row[1])
    reference_witness = max(sorted(rows), key=lambda row: row[2])
    multiplier = Fraction(section_count, fiber_rank)
    lower = multiplier * witness[1] / total_upper
    reference = multiplier * reference_witness[2] / total_reference
    margin = max(Fraction(), lower - 1)
    return {
        "sample_count": len(rows),
        "section_count": section_count,
        "fiber_rank": fiber_rank,
        "witness_ordinal": witness[0],
        "reference_witness_ordinal": reference_witness[0],
        "sum_upper_exact": str(total_upper),
        "sum_reference_exact": str(total_reference),
        "atomic_multiplier_lower_exact": str(lower),
        "atomic_multiplier_reference_exact": str(reference),
        "balanced_fixed_point_excluded_on_retained_intervals": lower > 1,
        "balanced_fixed_point_excluded_for_reference_weights": reference > 1,
        "operator_norm_balance_residual_lower_exact": str(margin),
        "trace_normalized_frobenius_residual_squared_lower_exact": str(
            Fraction(fiber_rank, section_count) * margin**2
        ),
        "finite_sample_rank_upper_bound": min(section_count, fiber_rank * len(rows)),
        "condition_is_sufficient_for_balance": False,
    }


def _manifest(expected_request_digest, expected_digest):
    request = full.read_request(expected_digest=expected_request_digest)
    record = json.loads(full.OUTPUT.read_bytes())
    if (
        record.get("artifact_digest") != expected_digest
        or full.cloud.inputs._digest({k: v for k, v in record.items() if k != "artifact_digest"})
        != expected_digest
        or record["request_digest"] != request["artifact_digest"]
        or record["input_digest"] != request["input_digest"]
        or record["source_files_sha256"] != full._sources()
        or record["original_section_basis_digest"] != request["original_section_basis_digest"]
        or record["sample_count"] != request["sample_count"]
        or record["training_count"] != request["training_count"]
        or record["validation_count"] != request["validation_count"]
        or record["completed_checkpoint_count"] != request["sample_count"]
        or record["complete_original_workload_available"] is not True
        or record["missing_sample_ordinals"]
        or record["unresolved_sample_ordinals"]
        or [entry["ordinal"] for entry in record["sample_archives"]]
        != list(range(request["sample_count"]))
        or record["failed_samples_dropped"] is not False
        or record["observations_used"] is not False
    ):
        raise ValueError("the trusted complete original cloud or its scientific scope changed")
    inputs = full.cloud.inputs.read_inputs(
        expected_digest=request["input_digest"], path=full.INPUTS,
    )
    return request, record, inputs


def _sample(request, manifest, inputs, ordinal):
    ref = manifest["sample_archives"][ordinal]
    path = full._sample_path(ordinal)
    if (
        ref["path"] != str(path.relative_to(full.ROOT))
        or ref["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest()
    ):
        raise ValueError("a retained original archive changed its manifest binding")
    saved = full._read_sample(request, inputs, ordinal)
    if saved["artifact_digest"] != ref["artifact_digest"]:
        raise ValueError("a retained original checkpoint changed its trusted digest")
    if saved["history"][-1]["kernel_status"] != "computed_discovery":
        raise ValueError("all original checkpoints must remain resolved and retained")
    return saved


def run(*, expected_request_digest, expected_cloud_digest, progress=None):
    """Certify all original atomic weights; obtain no new inputs or geometry."""

    if OUTPUT.exists():
        raise FileExistsError("preserve the original finite-cloud obstruction certificate")
    sources = _sources()
    request, manifest, inputs = _manifest(expected_request_digest, expected_cloud_digest)
    weights = []
    for ordinal in range(request["sample_count"]):
        saved = _sample(request, manifest, inputs, ordinal)
        final = saved["history"][-1]
        lower, upper = map(Fraction, final["quotient_weight_without_pi_cubed"])
        reference = Fraction.from_float(float.fromhex(final["weight_midpoint_without_pi_cubed"]))
        weights.append({
            "ordinal": ordinal,
            "role": saved["role"],
            "checkpoint_digest": saved["artifact_digest"],
            "weight_lower_exact": str(lower),
            "weight_reference_exact": str(reference),
            "weight_upper_exact": str(upper),
        })
        if progress and (ordinal + 1) % 256 == 0:
            progress({"phase": "original exact positive weights", "samples_checked": ordinal + 1})
    result = {
        "schema": "retained-finite-cloud-balance-v1",
        "request_digest": expected_request_digest,
        "cloud_manifest_digest": expected_cloud_digest,
        "original_section_basis_digest": request["original_section_basis_digest"],
        "source_files_sha256": sources,
        "section_count": 5345,
        "fiber_rank": 4,
        "all_original_training_and_validation_samples_retained": True,
        "all_original_weight_intervals_checked": True,
        "weight_enclosures_independently_replayed": False,
        "certificate_scope": "all positive weights in the retained producer intervals; "
        "rank-four section law; fixed finite weighted measure only",
        "entropy_assumption_status": "ASSUMED",
        "parameter_point_status": "SELECTED",
        "numerical_kernel_error_bound_certified": False,
        "sampling_error_bound_useful": False,
        "continuum_bundle_instability_proved": False,
        "ricci_flat_or_hym_metric_available": False,
        "physical_yukawas_available": False,
        "common_stabilized_vacuum_available": False,
        "observations_used": False,
        "weights": weights,
    }
    for role in ("training", "validation"):
        result[role] = atomic_bound(_weight_rows(weights, role), section_count=5345, fiber_rank=4)
    if sources != _sources():
        raise ValueError("the finite-measure proof sources changed during execution")
    result["artifact_digest"] = full.cloud.inputs._digest(result)
    full._install_json(OUTPUT, result)
    return result


def _weight_rows(weights, role):
    return tuple(
        (row["ordinal"], Fraction(row["weight_lower_exact"]),
         Fraction(row["weight_reference_exact"]), Fraction(row["weight_upper_exact"]))
        for row in weights if row["role"] == role
    )


def read_certificate(*, expected_digest):
    """Recheck the exact inequality and complete manifest-bound weight inventory."""

    record = json.loads(OUTPUT.read_bytes())
    if (
        record.get("artifact_digest") != expected_digest
        or full.cloud.inputs._digest({k: v for k, v in record.items() if k != "artifact_digest"})
        != expected_digest
        or record["source_files_sha256"] != _sources()
        or record["schema"] != "retained-finite-cloud-balance-v1"
        or record["section_count"] != 5345
        or record["fiber_rank"] != 4
        or record["all_original_training_and_validation_samples_retained"] is not True
        or record["all_original_weight_intervals_checked"] is not True
        or record["entropy_assumption_status"] != "ASSUMED"
        or record["parameter_point_status"] != "SELECTED"
        or any(record[key] is not False for key in (
            "weight_enclosures_independently_replayed", "numerical_kernel_error_bound_certified",
            "sampling_error_bound_useful", "continuum_bundle_instability_proved",
            "ricci_flat_or_hym_metric_available", "physical_yukawas_available",
            "common_stabilized_vacuum_available", "observations_used",
        ))
    ):
        raise ValueError("the exact finite-measure certificate or its scope changed")
    request, manifest, _ = _manifest(record["request_digest"], record["cloud_manifest_digest"])
    weights = record["weights"]
    if [row["ordinal"] for row in weights] != list(range(request["sample_count"])):
        raise ValueError("the certificate must retain every original ordinal exactly once")
    for row, ref in zip(weights, manifest["sample_archives"], strict=True):
        if (
            row["checkpoint_digest"] != ref["artifact_digest"]
            or row["role"] != full._role(request, row["ordinal"])
        ):
            raise ValueError("an original weight changed its checkpoint or declared role")
    for role in ("training", "validation"):
        actual = atomic_bound(_weight_rows(weights, role), section_count=5345, fiber_rank=4)
        if record[role] != actual:
            raise ValueError("an exact finite-measure necessary condition changed")
    return record


def projector_rows(form, rows, *, basis_digest, minimum_condition, maximum_residual):
    """Evaluate all original H1 coordinates and whiten only the rank-four fiber.

    The resulting row span gives an orthogonal projector in a full-dimensional
    invertible solver frame. It is not a reduced model or matter normalization.
    """

    rows = np.asarray(rows, dtype=np.complex128)
    if (
        basis_digest != form.basis_digest
        or rows.ndim != 2
        or rows.shape[1] != form.section_count
        or not 0 < rows.shape[0] <= form.section_count
        or not np.all(np.isfinite(rows))
        or any(type(value) is not float or not 0 < value < 1
               for value in (minimum_condition, maximum_residual))
    ):
        raise ValueError("full original-basis fiber rows and explicit admission policies required")
    z = solve_triangular(form.lower, (rows / form.diagonal).conj().T,
                         lower=True, check_finite=False)
    transformed = math.sqrt(float(form.coefficient)) * z.conj().T
    gram = transformed @ transformed.conj().T
    if not np.all(np.isfinite(gram)) or not np.all(np.isfinite(transformed)):
        raise ArithmeticError("the full H1 fiber evaluation overflowed")
    lower = np.linalg.cholesky(gram)
    reciprocal, info = get_lapack_funcs("pocon", (lower,))(
        lower, float(np.linalg.norm(gram, 1)), uplo="L",
    )
    if info or not math.isfinite(reciprocal) or reciprocal < minimum_condition:
        raise ArithmeticError("full H1 fiber conditioning is unresolved")
    whitened = solve_triangular(lower, transformed, lower=True, check_finite=False)
    residual = float(np.linalg.norm(
        whitened @ whitened.conj().T - np.eye(rows.shape[0]), np.inf,
    ))
    if not math.isfinite(residual) or residual > maximum_residual:
        raise ArithmeticError("full H1 fiber projector residual is unresolved")
    return whitened, {
        "fiber_reciprocal_condition_discovery": float(reciprocal),
        "fiber_projector_row_residual_discovery": residual,
    }


def create_probe_request(*, expected_certificate_digest, expected_h1_request_digest,
                         expected_h1_digest, minimum_condition, maximum_residual):
    """Freeze full H1 witness policies; held-out samples never select its form."""

    if PROBE_REQUEST.exists():
        raise FileExistsError("preserve the original full H1 witness policy")
    if any(type(value) is not float or not 0 < value < 1
           for value in (minimum_condition, maximum_residual)):
        raise ValueError("explicit positive full H1 fiber policies required")
    certificate = read_certificate(expected_digest=expected_certificate_digest)
    h1_record, form = parent.read_result(
        expected_request_digest=expected_h1_request_digest, expected_digest=expected_h1_digest,
    )
    if form is None or form.section_count != certificate["section_count"]:
        raise ValueError("the actual full original-basis nonunit H1 is required")
    del form
    record = {
        "schema": "full-h1-finite-balance-witness-request-v1",
        "certificate_digest": expected_certificate_digest,
        "h1_request_digest": expected_h1_request_digest,
        "h1_digest": h1_record["artifact_digest"],
        "source_files_sha256": _sources(),
        "minimum_fiber_reciprocal_condition": minimum_condition,
        "maximum_projector_row_residual": maximum_residual,
        "witness_rule": "retained training atomic-bound ordinal; no selection by held-out rows",
        "witness_ordinal": certificate["training"]["witness_ordinal"],
        "population": "all original 1536 training and 512 validation checkpoints",
    }
    record["artifact_digest"] = full.cloud.inputs._digest(record)
    full._install_json(PROBE_REQUEST, record)
    return record


def run_probe(*, expected_request_digest, progress=None):
    """Consume actual H1 on every retained fiber and test one balance witness."""

    if PROBE_OUTPUT.exists():
        raise FileExistsError("preserve the original complete H1 balance witness")
    request = json.loads(PROBE_REQUEST.read_bytes())
    sources = _sources()
    if (
        request.get("artifact_digest") != expected_request_digest
        or full.cloud.inputs._digest({k: v for k, v in request.items() if k != "artifact_digest"})
        != expected_request_digest
        or request["source_files_sha256"] != sources
    ):
        raise ValueError("the original H1 witness request changed")
    certificate = read_certificate(expected_digest=request["certificate_digest"])
    original, manifest, inputs = _manifest(
        certificate["request_digest"], certificate["cloud_manifest_digest"],
    )
    h1_record, form = parent.read_result(
        expected_request_digest=request["h1_request_digest"], expected_digest=request["h1_digest"],
    )
    if form is None or form.section_count != 5345:
        raise ValueError("the admitted actual full H1 must remain available")
    policy = {"basis_digest": form.basis_digest,
              "minimum_condition": request["minimum_fiber_reciprocal_condition"],
              "maximum_residual": request["maximum_projector_row_residual"]}
    ordinal = request["witness_ordinal"]
    if ordinal != certificate["training"]["witness_ordinal"]:
        raise ValueError("the predeclared retained training witness changed")
    saved = _sample(original, manifest, inputs, ordinal)
    witness, _ = projector_rows(
        form, full.cloud._decode_rows(saved["history"][-1]["kernel_rows"]), **policy,
    )
    sums = {role: np.zeros((4, 4), dtype=np.complex128) for role in ("training", "validation")}
    diagnostics = []
    for ordinal in range(original["sample_count"]):
        saved = _sample(original, manifest, inputs, ordinal)
        rows, diagnostic = projector_rows(
            form, full.cloud._decode_rows(saved["history"][-1]["kernel_rows"]), **policy,
        )
        overlap = rows @ witness.conj().T
        weight = float.fromhex(saved["history"][-1]["weight_midpoint_without_pi_cubed"])
        sums[saved["role"]] += weight * (overlap.conj().T @ overlap)
        diagnostics.append({"ordinal": ordinal, "role": saved["role"], **diagnostic})
        if progress and (ordinal + 1) % 128 == 0:
            progress({"phase": "actual full H1 retained-fiber evaluation",
                      "samples_checked": ordinal + 1})
    result = {
        "schema": "full-h1-finite-balance-witness-v1",
        "request_digest": expected_request_digest,
        "certificate_digest": certificate["artifact_digest"],
        "h1_digest": h1_record["artifact_digest"],
        "source_files_sha256": sources,
        "original_section_basis_digest": form.basis_digest,
        "section_count": form.section_count,
        "fiber_rank": 4,
        "witness_ordinal": request["witness_ordinal"],
        "nonunit_h1_consumed_on_all_original_fibers": True,
        "all_original_training_and_validation_samples_retained": True,
        "complete_original_coordinates_used": True,
        "diagnostic_is_only_a_lower_bound_witness_not_a_reduced_model": True,
        "held_out_samples_used_to_select_h1_or_witness": False,
        "full_operator_norm_computed": False,
        "numerical_error_bound_certified": False,
        "sampling_error_bound_useful": False,
        "ricci_flat_or_hym_metric_available": False,
        "physical_yukawas_available": False,
        "common_stabilized_vacuum_available": False,
        "observations_used": False,
        "fiber_diagnostics": diagnostics,
    }
    for role, matrix in sums.items():
        total = float(Fraction(certificate[role]["sum_reference_exact"]))
        matrix *= 5345 / (4 * total)
        if not np.all(np.isfinite(matrix)):
            raise ArithmeticError("the all-population H1 witness overflowed")
        result[role] = {
            "sample_count": certificate[role]["sample_count"],
            "witness_matrix": full.cloud._encode_rows(matrix.tolist()),
            "maximum_witness_eigenvalue_discovery": float(np.linalg.eigvalsh(matrix)[-1]),
            "witness_hermitian_residual_discovery": float(
                np.linalg.norm(matrix - matrix.conj().T, "fro") / np.linalg.norm(matrix, "fro")
            ),
        }
    if sources != _sources():
        raise ValueError("the complete H1 witness sources changed during execution")
    result["artifact_digest"] = full.cloud.inputs._digest(result)
    full._install_json(PROBE_OUTPUT, result)
    return result


def read_probe(*, expected_request_digest, expected_digest):
    """Inspect a complete numerical witness without promoting its epistemic scope."""

    request = json.loads(PROBE_REQUEST.read_bytes())
    record = json.loads(PROBE_OUTPUT.read_bytes())
    for packet, trusted in ((request, expected_request_digest), (record, expected_digest)):
        if (
            packet.get("artifact_digest") != trusted
            or full.cloud.inputs._digest({k: v for k, v in packet.items()
                                         if k != "artifact_digest"}) != trusted
            or packet["source_files_sha256"] != _sources()
        ):
            raise ValueError("the trusted original full H1 balance witness changed")
    certificate = read_certificate(expected_digest=request["certificate_digest"])
    if (
        record["request_digest"] != expected_request_digest
        or record["certificate_digest"] != certificate["artifact_digest"]
        or record["h1_digest"] != request["h1_digest"]
        or record["original_section_basis_digest"] != certificate["original_section_basis_digest"]
        or record["section_count"] != 5345
        or record["fiber_rank"] != 4
        or record["witness_ordinal"] != request["witness_ordinal"]
        or request["witness_ordinal"] != certificate["training"]["witness_ordinal"]
        or any(record[key] is not True for key in (
            "nonunit_h1_consumed_on_all_original_fibers",
            "all_original_training_and_validation_samples_retained",
            "complete_original_coordinates_used",
            "diagnostic_is_only_a_lower_bound_witness_not_a_reduced_model",
        ))
        or any(record[key] is not False for key in (
            "held_out_samples_used_to_select_h1_or_witness", "full_operator_norm_computed",
            "numerical_error_bound_certified", "sampling_error_bound_useful",
            "ricci_flat_or_hym_metric_available", "physical_yukawas_available",
            "common_stabilized_vacuum_available", "observations_used",
        ))
    ):
        raise ValueError("the complete H1 diagnostic or its scientific scope changed")
    diagnostics = record["fiber_diagnostics"]
    if [row["ordinal"] for row in diagnostics] != list(range(len(certificate["weights"]))):
        raise ValueError("every original H1 fiber must be checked exactly once")
    for row, weight in zip(diagnostics, certificate["weights"], strict=True):
        condition = row["fiber_reciprocal_condition_discovery"]
        residual = row["fiber_projector_row_residual_discovery"]
        if (
            row["role"] != weight["role"]
            or not math.isfinite(condition)
            or not request["minimum_fiber_reciprocal_condition"] <= condition <= 1
            or not math.isfinite(residual)
            or not 0 <= residual <= request["maximum_projector_row_residual"]
        ):
            raise ValueError("an original H1 fiber failed its predeclared numerical gate")
    for role in ("training", "validation"):
        entry = record[role]
        if (
            entry["sample_count"] != certificate[role]["sample_count"]
            or not math.isfinite(entry["maximum_witness_eigenvalue_discovery"])
            or not math.isfinite(entry["witness_hermitian_residual_discovery"])
            or not 0 <= entry["witness_hermitian_residual_discovery"] < 1e-10
        ):
            raise ValueError("the all-population numerical H1 witness is unresolved")
        matrix = np.asarray([
            [complex(float.fromhex(real), float.fromhex(imag)) for real, imag in row]
            for row in entry["witness_matrix"]
        ], dtype=np.complex128)
        if matrix.shape != (4, 4) or not np.all(np.isfinite(matrix)):
            raise ValueError("a complete finite witness matrix is required")
        if float(np.linalg.eigvalsh(matrix)[-1]) != entry["maximum_witness_eigenvalue_discovery"]:
            raise ValueError("the numerical witness eigenvalue changed")
    return record


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "certificate":
        result = run(expected_request_digest=sys.argv[2], expected_cloud_digest=sys.argv[3],
                     progress=lambda row: print(json.dumps(row), flush=True))
    elif len(sys.argv) == 3 and sys.argv[1] == "probe":
        result = run_probe(expected_request_digest=sys.argv[2],
                           progress=lambda row: print(json.dumps(row), flush=True))
    else:
        raise ValueError(
            "provide certificate plus trusted cloud digests, or probe plus request digest",
        )
    print(json.dumps({"artifact_digest": result["artifact_digest"]}), flush=True)
