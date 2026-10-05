"""Execute new identity-preserving inputs through the full original trial operator.

Owns:
    Same-sample native refinement, complete sparse section evaluation, rank-four
    unit-H kernel factorization, global empirical operators, and scoped uncertainty.

Depends on:
    Retained entropy receipts, native root/frame controllers, the frozen original
    feature evaluator, and the established global auxiliary weight bound.

Must not:
    Redraw failures, equate residuals with error certificates, infer IID from
    finite bytes, invert a rank-deficient sample operator, or report HYM metrics.

Phase 0:
    Research global discovery experiment; controlled physical metrics remain open.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import perf_counter

from onetheory.math.numbers import OMEGA, Eisenstein

from . import compiled_section_features as features
from . import independent_cloud_inputs as inputs
from . import native_section_continuation as continuation

roots, draws, native = continuation.roots, continuation.draws, continuation.native
OUTPUT = inputs.OUTPUT.with_name("independent_trial_cloud.json")
PROOF = Path(__file__).with_name("INDEPENDENT_TRIAL_CLOUD_NOTE.md")
INPUT_DIGEST = "6a0def040a9ce1b2e702c7a5df428bb9ae35db84ae382599dca4d3caff55f748"
ORTHOGONAL_TOLERANCE = 1e-10
DEPENDENCE_TOLERANCE = 1e-13


def _sources():
    modules = (
        features,
        inputs,
        continuation,
        roots,
        draws,
        native,
        continuation.bounded,
        draws.weights,
    )
    result = {
        str(Path(m.__file__).relative_to(features.exact.domains.ROOT)): hashlib.sha256(
            Path(m.__file__).read_bytes()
        ).hexdigest()
        for m in modules
    }
    for path in (Path(__file__), PROOF):
        result[str(path.relative_to(features.exact.domains.ROOT))] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    features._sources()
    return result


def _dot(left, right):
    """Complex inner product with explicit compensated component summation."""

    products = tuple(a * b.conjugate() for a, b in zip(left, right, strict=True))
    return complex(math.fsum(c.real for c in products), math.fsum(c.imag for c in products))


def orthonormal_rows(rows, *, orthogonal_tolerance, dependence_tolerance):
    """Two-pass modified Gram--Schmidt avoids squaring the fiber condition number.

    This row preconditioning leaves the full section-space projector unchanged
    in exact arithmetic. Failure is numerical unresolvedness, not a rank theorem.
    """

    rows = tuple(tuple(complex(c) for c in row) for row in rows)
    if (
        len(rows) != 4
        or not rows[0]
        or any(len(r) != len(rows[0]) for r in rows)
        or any(not math.isfinite(c.real) or not math.isfinite(c.imag) for r in rows for c in r)
        or not 0 < dependence_tolerance < orthogonal_tolerance < 1
    ):
        raise ValueError("four finite rows and explicit ordered numerical tolerances required")
    q, transition, ratios = [], [], []
    for i, row in enumerate(rows):
        scale = math.sqrt(_dot(row, row).real)
        if not math.isfinite(scale) or scale <= 0:
            raise ArithmeticError("the discovery row has no resolved positive norm")
        value = [c / scale for c in row]
        coefficients = [complex(int(i == j) / scale) for j in range(4)]
        for _ in range(2):
            for previous, change in zip(q, transition, strict=True):
                coefficient = _dot(value, previous)
                value = [a - coefficient * b for a, b in zip(value, previous, strict=True)]
                coefficients = [
                    a - coefficient * b for a, b in zip(coefficients, change, strict=True)
                ]
        norm = math.sqrt(_dot(value, value).real)
        if not math.isfinite(norm) or norm <= dependence_tolerance:
            raise ArithmeticError(
                "binary64 does not resolve independence of all original fiber rows"
            )
        q.append(tuple(c / norm for c in value))
        transition.append(tuple(c / norm for c in coefficients))
        ratios.append(norm)
    residual = max(abs(_dot(a, b) - int(i == j)) for i, a in enumerate(q) for j, b in enumerate(q))
    if residual > orthogonal_tolerance:
        raise ArithmeticError("the discovery projector fails its declared orthogonality tolerance")
    return tuple(q), {
        "orthogonality_residual": residual,
        "relative_independence_norms": ratios,
        "row_change_of_basis": _encode_rows(transition),
        "row_preconditioner_is_physical_normalization": False,
    }


def _encode_rows(rows):
    return [[[c.real.hex(), c.imag.hex()] for c in row] for row in rows]


def _decode_rows(rows):
    result = tuple(
        tuple(complex(float.fromhex(c[0]), float.fromhex(c[1])) for c in row) for row in rows
    )
    if (
        len(result) != 4
        or any(len(r) != 5345 for r in result)
        or any(not math.isfinite(c.real) or not math.isfinite(c.imag) for r in result for c in r)
    ):
        raise ValueError("all four full original finite kernel rows required")
    return result


def _kernel(values, parameters):
    if values.basis_digest != features.BASIS or len(values.columns) != 5345 or len(parameters) != 2:
        raise ValueError("the complete original basis and explicit parameter pair required")
    eta = (complex(1), *(features._complex(p) for p in parameters))
    rows = tuple(
        tuple(sum(column[m][i] * eta[m] for m in range(3)) for column in values.columns)
        for i in range(4)
    )
    return orthonormal_rows(
        rows, orthogonal_tolerance=ORTHOGONAL_TOLERANCE, dependence_tolerance=DEPENDENCE_TOLERANCE
    )


def _history(admission, level):
    draw = admission.draw
    record = {
        "level": level,
        "address": draws._address_record(draw.address),
        "draw_policy": draws._policy_record(draw.policy),
        "frame_policy": {
            "chart": list(admission.policy.chart),
            "first_pivots": list(admission.policy.first_pivots),
            "second_pivots": list(admission.policy.second_pivots),
            "input_center_bits": admission.policy.center_bits,
            "volume_scale": [
                str(admission.policy.volume_scale.a),
                str(admission.policy.volume_scale.b),
            ],
            "covering_degree": admission.policy.covering_degree,
        },
        "root_parent_retained": draw.admitted_parent is not None,
        "frame_parent_retained": admission.admitted_parent is not None,
    }
    if isinstance(draw, draws.CoupledDraw):
        c = draw.configuration
        families = (
            (c.first, c.second) if isinstance(c, native.LineBaseLineConfiguration) else (c.partner,)
        )
        record.update(
            {
                "component": draw.address.choices()[0],
                "selected_branch": list(draw.branch),
                "all_root_families": [native._roots_record(r) for r in families],
            }
        )
    if isinstance(admission, continuation.PendingFrame):
        return {
            **record,
            "status": "unresolved",
            "stage": admission.stage,
            "reason": admission.reason,
        }
    return {
        **record,
        "status": "admitted",
        "fiber_basis_labels": list(admission.frame.basis_labels),
        "relation_minor": native._ball_record(admission.frame.relation_minor),
        "coordinate_bounds": [
            [native._ball_record(c) for c in group]
            for group in (admission.frame.point.x, admission.frame.point.u, admission.frame.point.p)
        ],
        "quotient_weight_without_pi_cubed": continuation.bounded.bounds._interval_record(
            admission.weight.quotient_weight_without_pi_cubed
        ),
    }


def process_sample(record, ordinal, program, *, parameters, levels, max_cells, progress=None):
    """Continue one original sample; a failure never changes its entropy address."""

    available = inputs.address(record, ordinal)
    identity = inputs.sample_identity(record, ordinal)
    history, previous = [], None
    frames = draws.declared_policy()
    for level in levels:
        address = roots.refinement_address(available, level)
        policy, work = roots.refinement_policy(
            level, first_frame=frames.first, second_frame=frames.second
        )
        work = {**work, "max_cells": max_cells}
        frame_policy = continuation.FramePolicy(
            (0, 0, 0), (0, 2), (0, 1, 2), 8 * level, Eisenstein(1), 9
        )
        if previous is None:
            draw = roots.attempt_subdivision_draw(address, policy, **work)
            admission = continuation.admit_frame(draw, frame_policy)
        else:
            admission = continuation.refine_frame(previous, address, policy, frame_policy, **work)
        previous = admission
        item = _history(admission, level)
        if isinstance(admission, continuation.AdmittedFrame):
            try:
                values = program.evaluate(
                    admission.frame, source_signature=program.source_signature
                )
                q, diagnostics = _kernel(values, parameters)
                interval = admission.weight.quotient_weight_without_pi_cubed
                midpoint = float((interval.lower + interval.upper) / 2)
                if not math.isfinite(midpoint) or midpoint <= 0:
                    raise ArithmeticError("the numerical quotient weight is unresolved")
                item.update(
                    {
                        "kernel_status": "computed_discovery",
                        "kernel_rows": _encode_rows(q),
                        "weight_midpoint_without_pi_cubed": midpoint.hex(),
                        "kernel_diagnostics": diagnostics,
                        "complete_original_sections_consumed": True,
                        "floating_mantissa_bits": sys.float_info.mant_dig,
                    }
                )
            except (ArithmeticError, ValueError) as error:
                item.update({"kernel_status": "unresolved", "kernel_reason": str(error)})
        history.append(item)
        if progress is not None:
            progress(
                {
                    "ordinal": ordinal,
                    "level": level,
                    "frame_status": item["status"],
                    "kernel_status": item.get("kernel_status", "unresolved"),
                }
            )
    return {**identity, "history": history}


def overlap(left, right):
    """Full section-space projector overlap via the four-by-four cross Gram."""

    return math.fsum(abs(_dot(a, b)) ** 2 for a in left for b in right)


def _statistics(samples, level):
    if not samples:
        raise ValueError("a complete nonempty original cloud is required")
    items = [next(h for h in sample["history"] if h["level"] == level) for sample in samples]
    missing = [
        s["ordinal"]
        for s, h in zip(samples, items, strict=True)
        if h.get("kernel_status") != "computed_discovery"
    ]
    if missing:
        return {
            "status": "unresolved",
            "missing_sample_ordinals": missing,
            "failed_samples_dropped": False,
        }
    q = tuple(_decode_rows(h["kernel_rows"]) for h in items)
    weights = tuple(float.fromhex(h["weight_midpoint_without_pi_cubed"]) for h in items)
    if any(not math.isfinite(w) or w <= 0 for w in weights):
        raise ValueError("finite positive quotient weights are required")
    n = len(samples)
    self_norms = tuple(overlap(rows, rows) for rows in q)
    norm_squared = (
        math.fsum(
            weights[i] * weights[j] * overlap(q[i], q[j]) * (1 if i == j else 2)
            for i in range(n)
            for j in range(i + 1)
        )
        / n**2
    )
    mean_weight = math.fsum(weights) / n
    trace = (
        math.fsum(
            w * sum(_dot(r, r).real for r in rows) for w, rows in zip(weights, q, strict=True)
        )
        / n
    )
    diagonal = tuple(
        math.fsum(weights[i] * sum(abs(row[k]) ** 2 for row in q[i]) for i in range(n)) / n
        for k in range(5345)
    )
    result = {
        "status": "computed_discovery",
        "sample_count": n,
        "mean_quotient_weight_without_pi_cubed": mean_weight,
        "global_operator_trace_without_pi_cubed": trace,
        "global_operator_frobenius_squared_without_pi_to_sixth": norm_squared,
        "full_operator_diagonal_without_pi_cubed": diagonal,
        "representation": "mean of full weighted Q-dagger Q; every original section retained",
        "sample_operator_rank_upper_bound": min(5345, 4 * n),
        "minimum_samples_necessary_for_invertibility": (5345 + 3) // 4,
        "full_sample_operator_invertibility_possible_by_rank": 4 * n >= 5345,
        "kernel_count": n,
        "failed_samples_dropped": False,
    }
    if n > 1:
        variance = (
            math.fsum(w * w * x for w, x in zip(weights, self_norms, strict=True)) / n
            - norm_squared
        ) / (n - 1)
        result["empirical_mean_operator_frobenius_variance"] = variance
        result["empirical_weight_mean_standard_error"] = math.sqrt(
            math.fsum((w - mean_weight) ** 2 for w in weights) / (n * (n - 1)),
        )
        result["empirical_standard_error_is_a_confidence_certificate"] = False
    return result


def _ideal_statistical_bound(count, alpha):
    """Use the actual bounded positive law, not the obsolete divergent proposal."""

    if type(count) is not int or count < 1 or not isinstance(alpha, Fraction) or not 0 < alpha < 1:
        raise ValueError("positive sample count and exact probability in (0, 1) required")
    path = OUTPUT.with_name("alternate_metric_global_weight_bound.json")
    digest, record = features.exact.original.fiber._verified_payload(path)
    if digest != "96e3d216aa6157dab686069b095e304de5f7e9600348f42c00fff0691986c0f4":
        raise ValueError("the unchanged positive-law global bound changed")
    delta = Fraction(record["conormal_lower_bound"])
    bound = Fraction(12, 9) / delta  # Explicit unit scale and ninefold quotient.
    return {
        "status": "DERIVED",
        "conditional_on": "independent fair input streams and ideal kernels",
        "weight_upper_bound_without_pi_cubed": str(bound),
        "failure_probability": str(alpha),
        "ideal_mean_operator_frobenius_radius_squared": str(4 * bound**2 / (count * alpha)),
        "covers_discovery_numerical_error": False,
        "global_weight_certificate_digest": digest,
    }


def _checkpoint_path(ordinal):
    return OUTPUT.with_name(f"independent_trial_cloud.sample_{ordinal:04d}.json.gz")


def _install_sample(path, record):
    encoded = inputs._canonical(record) + b"\n"
    with NamedTemporaryFile(dir=path.parent, prefix=".cloud_sample_", delete=False) as raw:
        temporary = Path(raw.name)
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            compressed.write(encoded)
    try:
        features.exact.archive._install_unchanged_or_new(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def run_cloud(*, expected_inputs_digest, parameters, levels, max_cells, progress=None):
    """Compute the complete predeclared workload, retaining pending samples too."""

    parameters = tuple(Eisenstein.coerce(p) for p in parameters)
    if (
        len(parameters) != 2
        or type(levels) is not tuple
        or len(levels) != 2
        or any(type(j) is not int or j < 2 for j in levels)
        or levels[1] <= levels[0]
        or type(max_cells) is not int
        or max_cells < 1
    ):
        raise ValueError(
            "two explicit increasing levels, parameters and positive work cap required"
        )
    record = inputs.read_inputs(expected_digest=expected_inputs_digest)
    before = _sources()
    policy = {
        "levels": levels,
        "max_cells": max_cells,
        "chart_order": (0, 1),
        "parameters": [[str(p.a), str(p.b)] for p in parameters],
        "orthogonal_tolerance": ORTHOGONAL_TOLERANCE,
        "dependence_tolerance": DEPENDENCE_TOLERANCE,
    }
    signature = inputs._digest(
        {"inputs": expected_inputs_digest, "sources": before, "policy": policy}
    )
    program = features.compile_features(progress=progress)
    samples, references = [], []
    start = perf_counter()
    for ordinal in range(record["sample_count"]):
        path = _checkpoint_path(ordinal)
        if path.exists():
            sample = json.loads(gzip.decompress(path.read_bytes()))
            unsigned = {k: v for k, v in sample.items() if k != "artifact_digest"}
            if (
                sample["execution_signature"] != signature
                or inputs._digest(unsigned) != (sample["artifact_digest"])
            ):
                raise ValueError("a checkpoint belongs to a different original cloud request")
        else:
            sample = process_sample(
                record,
                ordinal,
                program,
                parameters=parameters,
                levels=levels,
                max_cells=max_cells,
                progress=progress,
            )
            sample["execution_signature"] = signature
            sample["artifact_digest"] = inputs._digest(sample)
            _install_sample(path, sample)
        if sample["sample_id"] != inputs.sample_identity(record, ordinal)["sample_id"]:
            raise ValueError("a retained checkpoint changed its original sample identity")
        samples.append(sample)
        references.append(
            {
                "ordinal": ordinal,
                "path": str(path.relative_to(features.exact.domains.ROOT)),
                "sha256": features.exact.archive._file_digest(path),
                "artifact_digest": sample["artifact_digest"],
            }
        )
        if progress is not None:
            progress(
                {"completed_request_ordinal": ordinal, "elapsed_seconds": perf_counter() - start}
            )
    statistics = {str(j): _statistics(samples, j) for j in levels}
    differences = []
    for sample in samples:
        a, b = sample["history"]
        if all(h.get("kernel_status") == "computed_discovery" for h in (a, b)):
            q0, q1 = _decode_rows(a["kernel_rows"]), _decode_rows(b["kernel_rows"])
            differences.append(
                {
                    "ordinal": sample["ordinal"],
                    "projector_refinement_squared_raw": overlap(q0, q0)
                    + overlap(q1, q1)
                    - 2 * overlap(q0, q1),
                    "weight_refinement_absolute": abs(
                        float.fromhex(a["weight_midpoint_without_pi_cubed"])
                        - float.fromhex(b["weight_midpoint_without_pi_cubed"])
                    ),
                }
            )
    if _sources() != before or inputs.read_inputs(expected_digest=expected_inputs_digest) != record:
        raise ValueError("original cloud sources changed during execution")
    result = {
        "schema": "independent-trial-cloud-v1",
        "input_digest": expected_inputs_digest,
        "source_files_sha256": before,
        "execution_signature": signature,
        "policy": policy,
        "original_section_basis_digest": features.BASIS,
        "compilation_parent_digest": features.COMPILATION,
        "sample_count": record["sample_count"],
        "sample_archives": references,
        "global_statistics": statistics,
        "component_counts": dict(
            Counter(inputs.address(record, i).choices()[0] for i in range(record["sample_count"]))
        ),
        "same_sample_refinement_diagnostics": differences,
        "ideal_statistical_bound": _ideal_statistical_bound(
            record["sample_count"], Fraction(1, 20)
        ),
        "entropy_assumption_status": "ASSUMED",
        "randomness_certificate_available": False,
        "new_entropy_streams_executed": True,
        "conditional_independent_cloud_available": all(
            s["status"] == "computed_discovery" for s in statistics.values()
        ),
        "global_trial_operator_estimate_available": statistics[str(levels[-1])]["status"]
        == "computed_discovery",
        "section_form": "explicit unit H0 in the full original 5345-dimensional section basis",
        "parameter_point_status": "SELECTED",
        "parameter_point_role": (
            "predeclared computational point; not stabilized or chosen by observations"
        ),
        "residue_scale": ["1", "0"],
        "covering_degree": 9,
        "pi_cubed_omitted_explicitly": True,
        "numerical_error_bound_certified": False,
        "input_radii_propagated_into_kernel": False,
        "refinement_differences_are_error_certificates": False,
        "failed_samples_dropped": False,
        "controlled_integral_available": False,
        "nonunit_h_iteration_executed": False,
        "ricci_flat_or_hym_metric_available": False,
        "physical_yukawas_available": False,
        "common_stabilized_vacuum_available": False,
        "observations_used": False,
    }
    result["artifact_digest"] = inputs._digest(result)
    if OUTPUT.exists() and OUTPUT.read_bytes() != inputs._canonical(result) + b"\n":
        raise FileExistsError("preserve the existing cloud packet; no silent replacement")
    if not OUTPUT.exists():
        with OUTPUT.open("xb") as stream:
            stream.write(inputs._canonical(result) + b"\n")
    return result


def read_cloud(*, expected_digest, path=OUTPUT):
    """Inspect a trusted execution without compiling sections or drawing inputs."""

    result = json.loads(path.read_bytes())
    unsigned = {k: v for k, v in result.items() if k != "artifact_digest"}
    if (
        result.get("artifact_digest") != expected_digest
        or inputs._digest(unsigned) != expected_digest
    ):
        raise ValueError("the trusted integration cloud changed")
    if result.get("schema") != "independent-trial-cloud-v1" or result.get(
        "source_files_sha256"
    ) != (_sources()):
        raise ValueError("the cloud scope or executed sources changed")
    record = inputs.read_inputs(expected_digest=result["input_digest"])
    policy = result["policy"]
    signature = inputs._digest(
        {"inputs": result["input_digest"], "sources": _sources(), "policy": policy}
    )
    if (
        result["execution_signature"] != signature
        or result["sample_count"] != record["sample_count"]
        or len(result["sample_archives"]) != record["sample_count"]
        or result["original_section_basis_digest"] != features.BASIS
        or result["compilation_parent_digest"] != features.COMPILATION
        or result["entropy_assumption_status"] != "ASSUMED"
        or result["parameter_point_status"] != "SELECTED"
        or result["residue_scale"] != ["1", "0"]
        or result["covering_degree"] != 9
        or result["pi_cubed_omitted_explicitly"] is not True
        or result["new_entropy_streams_executed"] is not True
    ):
        raise ValueError("the retained cloud identity or scientific scope changed")
    for key in (
        "randomness_certificate_available",
        "numerical_error_bound_certified",
        "input_radii_propagated_into_kernel",
        "refinement_differences_are_error_certificates",
        "failed_samples_dropped",
        "controlled_integral_available",
        "nonunit_h_iteration_executed",
        "ricci_flat_or_hym_metric_available",
        "physical_yukawas_available",
        "common_stabilized_vacuum_available",
        "observations_used",
    ):
        if result[key] is not False:
            raise ValueError("uncertified trial execution cannot be promoted to physical output")
    samples = []
    for ordinal, reference in enumerate(result["sample_archives"]):
        archive_path = _checkpoint_path(ordinal)
        if (
            reference["ordinal"] != ordinal
            or reference["path"] != str(archive_path.relative_to(features.exact.domains.ROOT))
            or features.exact.archive._file_digest(archive_path) != reference["sha256"]
        ):
            raise ValueError("an original retained sample archive changed")
        sample = json.loads(gzip.decompress(archive_path.read_bytes()))
        sample_unsigned = {k: v for k, v in sample.items() if k != "artifact_digest"}
        if (
            sample["artifact_digest"] != reference["artifact_digest"]
            or inputs._digest(sample_unsigned) != reference["artifact_digest"]
            or sample["execution_signature"] != signature
            or {k: sample[k] for k in ("sample_id", "ordinal", "streams")}
            != (inputs.sample_identity(record, ordinal))
            or [h["level"] for h in sample["history"]] != policy["levels"]
        ):
            raise ValueError("a sample changed its stream identity or refinement history")
        for history in sample["history"]:
            expected_address = roots.refinement_address(
                inputs.address(record, ordinal), history["level"]
            )
            if history["address"] != draws._address_record(expected_address):
                raise ValueError("a failed or admitted sample changed its original prefix")
        samples.append(sample)
    expected_statistics = {str(j): _statistics(samples, j) for j in policy["levels"]}
    if inputs._canonical(result["global_statistics"]) != inputs._canonical(expected_statistics):
        raise ValueError("the global statistics do not use every original sample")
    if (
        result["conditional_independent_cloud_available"]
        is not all(s["status"] == "computed_discovery" for s in expected_statistics.values())
        or result["global_trial_operator_estimate_available"]
        is not (expected_statistics[str(policy["levels"][-1])]["status"] == "computed_discovery")
        or result["ideal_statistical_bound"]
        != _ideal_statistical_bound(record["sample_count"], Fraction(1, 20))
    ):
        raise ValueError("the cloud availability or ideal statistical bound changed")
    return result


if __name__ == "__main__":
    result = run_cloud(
        expected_inputs_digest=INPUT_DIGEST,
        parameters=(Eisenstein(1), OMEGA),
        levels=(12, 16),
        max_cells=65536,
        progress=lambda r: print(json.dumps(r), flush=True),
    )
    print(result["artifact_digest"], flush=True)
