"""Transpose the existing finite lifting evaluation onto original encoded units.

Owns:
    Per-frame finite-series functional caching and full original section access.

Depends on:
    The original bounded support evaluator, its exact pole encoding, homotopy,
    perturbation, deck pullback and determinant-certified quotient projection.

Must not:
    Replace sections or cochains, treat individual units as closed residuals,
    prune uncertain zeros, infer sampling independence or report physical metrics.

Phase 0:
    Research evaluation-order experiment; per-draw throughput requires execution.
"""

import gzip
import hashlib
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import perf_counter

from . import alternate_metric_bounded_matrix as archive
from . import alternate_metric_bounded_support as original
from . import uncertain_cover_frames as domains

OUTPUT = domains.OUTPUT.with_name("alternate_metric_fiber_functionals.json")
MATRIX = OUTPUT.with_suffix(".columns.jsonl.gz")
PROOF = Path(__file__).with_name("ALTERNATE_METRIC_FIBER_FUNCTIONALS_NOTE.md")
EXECUTION_DIGEST = "dcb30fb238c2e4414bd89285a7d9ed4c1e36d0e2299ca8ce40a399ae7671d13a"


class FunctionalEvaluator(original.BoundedSupportEvaluator):
    """Apply the same linear functional once per encountered original pole unit."""

    def __init__(self, frame):
        super().__init__(frame)
        self.functional_values = {}

    def _unit_correction(self, power, parameter, key):
        cache_key = power, parameter, key
        if cache_key in self.unit_values:
            return self.unit_values[cache_key]
        encoded = self._encoded_residual(power, parameter, key)
        result = self._apply_residual(power, encoded)
        self.unit_values[cache_key] = result
        return result

    def _apply_residual(self, power, encoded):
        if (type(power) is not int or not 0 <= power <= 2
            or not isinstance(encoded, original.BoundedCoefficients)
            or encoded.bits != self.frame.point.bits
            or any(b.total_degree != 1 for b, _ in encoded.terms)):
            raise ValueError(
                "original encoded degree-one inputs and an actual channel are required",
            )
        result = ((self.scalar(0),), (self.scalar(0),))
        for basis, coefficient in encoded.terms:
            functional_key = power, basis
            if functional_key not in self.functional_values:
                unit = original.BoundedCoefficients(((basis, self.scalar(1)),),
                                                    bits=self.frame.point.bits)
                self.functional_values[functional_key] = self._residual_functional(power, unit)
            value = self.functional_values[functional_key]
            result = original.bounded._add(result,
                tuple(tuple(c * coefficient for c in row) for row in value))
        return result


def write_complete_domain(*, progress=None):
    """Execute every original section on the explicitly declared first A domain.

    This domain is a computational regression from the existing coupled input
    family, not an independent draw, selected extension point or vacuum.
    Original outputs are never overwritten by this successor execution.
    """

    before = domains._parents()
    name, branch, frame = domains.declared_frames()[0]
    if name != "A" or branch != (0, 0):
        raise ValueError("the predeclared uncertain-input domain changed")
    evaluator = FunctionalEvaluator(frame)
    start = perf_counter()
    with NamedTemporaryFile(dir=OUTPUT.parent, prefix=".fiber_functionals_", delete=False) as raw:
        temporary = Path(raw.name)
    try:
        with temporary.open("wb") as raw, gzip.GzipFile(filename="", mode="wb",
                                                       fileobj=raw, mtime=0) as stream:
            for index in range(5345):
                matrices = evaluator.evaluate_basis(index)
                record = {"basis_index": index,
                    "coefficient_columns_constant_a0_a1": [original.bounded._matrix_record(m)
                                                           for m in matrices]}
                stream.write(archive._canonical(record) + b"\n")
                if progress is not None and (index % 250 == 0 or index == 5344):
                    progress({"last_original_index": index,
                              "functional_units": len(evaluator.functional_values),
                              "unit_residual_keys": len(evaluator.unit_values),
                              "elapsed_seconds": perf_counter() - start})
        verified = archive.verify_archive(temporary, bits=100)
        if domains._parents() != before:
            raise ValueError("an original section or uncertain-domain source changed")
        record = {
            "schema": "alternate-metric-fiber-functionals-v1",
            "prerequisite_digests_and_archives": before,
            "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
            "component": name, "root_pair": list(branch),
            "domain_role": "predeclared coupled-input regression; not an independent draw",
            "chart_pivots": list(frame.point.chart),
            "first_pivot_rows": list(frame.first_pivots),
            "second_pivot_rows": list(frame.second_pivots),
            "fiber_basis_labels": list(frame.basis_labels),
            "normalized_cover_bounds": [[domains.roots._ball_record(c) for c in group]
                                        for group in (frame.point.x, frame.point.u, frame.point.p)],
            "relation_minor": domains.roots._ball_record(frame.relation_minor),
            "bound_bits": 100, "uncertain_center_bits": 100,
            "parameter_order": ["constant", "a0", "a1"],
            "original_constituent_counts": [2655, 2690],
            "matrix_archive": str(MATRIX.relative_to(domains.ROOT)),
            "matrix_archive_sha256": archive._file_digest(temporary),
            "matrix_archive_bytes": temporary.stat().st_size,
            **verified,
            "functional_unit_count": len(evaluator.functional_values),
            "original_unit_residual_key_count": len(evaluator.unit_values),
            "observed_series_depths": sorted(evaluator.series_depths),
            "all_original_columns_consumed": True,
            "complete_5345_column_matrix_on_declared_new_domain_available": True,
            "individual_units_asserted_closed": False,
            "all_15_domains_executed": False,
            "practical_multi_point_throughput_certified": False,
            "independent_cloud_available": False, "controlled_integral_available": False,
            "ricci_flat_or_hym_metric_available": False, "physical_yukawas_available": False,
            "common_stabilized_vacuum_available": False, "extension_point_selected": False,
            "centers_are_exact_cover_points": False, "observations_used": False,
        }
        record["artifact_digest"] = hashlib.sha256(archive._canonical(record)).hexdigest()
        archive._install_unchanged_or_new(temporary, MATRIX)
        with NamedTemporaryFile(dir=OUTPUT.parent, prefix=".fiber_functionals_meta_",
                                delete=False) as raw:
            metadata = Path(raw.name)
        try:
            metadata.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n",
                                encoding="utf-8")
            archive._install_unchanged_or_new(metadata, OUTPUT)
        finally:
            metadata.unlink(missing_ok=True)
        return record
    finally:
        temporary.unlink(missing_ok=True)


def verify_completed_domain(*, expected_digest):
    """Verify the complete executed output without restarting its construction.

    The trusted digest must come from completed execution, not from the file
    being audited. Parse every original column and independently reconstruct
    all named domain/source fields. This does not claim a fresh cochain replay.
    """

    before = domains._parents()
    digest, record = original.fiber._verified_payload(OUTPUT)
    if digest != expected_digest:
        raise ValueError("the completed original functional execution changed its trusted digest")
    name, branch, frame = domains.declared_frames()[0]
    required = {
        "schema": "alternate-metric-fiber-functionals-v1",
        "prerequisite_digests_and_archives": before,
        "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
        "component": name, "root_pair": list(branch),
        "domain_role": "predeclared coupled-input regression; not an independent draw",
        "chart_pivots": list(frame.point.chart),
        "first_pivot_rows": list(frame.first_pivots),
        "second_pivot_rows": list(frame.second_pivots),
        "fiber_basis_labels": list(frame.basis_labels),
        "normalized_cover_bounds": [[domains.roots._ball_record(c) for c in group]
                                    for group in (frame.point.x, frame.point.u, frame.point.p)],
        "relation_minor": domains.roots._ball_record(frame.relation_minor),
        "bound_bits": 100, "uncertain_center_bits": 100,
        "parameter_order": ["constant", "a0", "a1"],
        "original_constituent_counts": [2655, 2690],
        "matrix_archive": str(MATRIX.relative_to(domains.ROOT)),
        "matrix_archive_sha256": archive._file_digest(MATRIX),
        "matrix_archive_bytes": MATRIX.stat().st_size,
        **archive.verify_archive(MATRIX, bits=100),
        "all_original_columns_consumed": True,
        "complete_5345_column_matrix_on_declared_new_domain_available": True,
    }
    for flag in ("individual_units_asserted_closed", "all_15_domains_executed",
                 "practical_multi_point_throughput_certified", "independent_cloud_available",
                 "controlled_integral_available", "ricci_flat_or_hym_metric_available",
                 "physical_yukawas_available", "common_stabilized_vacuum_available",
                 "extension_point_selected", "centers_are_exact_cover_points", "observations_used"):
        required[flag] = False
    archive._require_scope(record, required)
    if domains._parents() != before or archive._file_digest(MATRIX) != required[
        "matrix_archive_sha256"]:
        raise ValueError("an original source or complete functional stream changed during audit")
    return {"artifact_digest": digest, **record}


if __name__ == "__main__":
    print(write_complete_domain(progress=lambda r: print(json.dumps(r), flush=True))[
        "artifact_digest"], flush=True)
