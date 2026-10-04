"""Evaluate complete compiled original sections in the actual bounded quotient.

Owns:
    Full original-order numerical execution from trusted exact polynomial
    columns, with unchanged domain uncertainty and named quotient frames.

Depends on:
    Complete exact section compilation, native certified cover domains, original
    quotient projection and existing outward-arithmetic/archive verification.

Must not:
    Compile a second carrier, reinterpret stream hashes as global basis identity,
    select extension parameters, infer IID draws or report physical metrics.

Phase 0:
    Research complete-domain execution; integration and stabilization remain open.
"""

import gzip
import hashlib
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import perf_counter

from . import alternate_metric_symbolic_columns as symbolic

archive, domains = symbolic.archive, symbolic.domains
OUTPUT = domains.OUTPUT.with_name("alternate_metric_symbolic_evaluation.json")
MATRIX = OUTPUT.with_suffix(".columns.jsonl.gz")
PROOF = symbolic.PROOF


def _scope(compilation_digest, frame):
    if not isinstance(frame, symbolic.original.bounded.BoundedFiberFrame):
        raise TypeError("the actual original bounded quotient frame is required")
    if frame != domains.declared_frames()[0][2]:
        raise ValueError("this execution scope requires the predeclared A branch (0,0)")
    return {
        "schema": "alternate-metric-symbolic-evaluation-v1",
        "complete_compilation_digest": compilation_digest,
        "original_section_basis_digest": symbolic.section_basis_identity()["artifact_digest"],
        "original_source_signature": symbolic._source_signature(),
        "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
        "component": "A", "root_pair": [0, 0],
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
        "point_dependent_stream_is_global_section_identity": False,
        "all_15_domains_executed": False, "independent_all_column_cochain_replay": False,
        "practical_multi_point_throughput_certified": False,
        "independent_cloud_available": False, "controlled_integral_available": False,
        "ricci_flat_or_hym_metric_available": False, "physical_yukawas_available": False,
        "common_stabilized_vacuum_available": False, "extension_point_selected": False,
        "centers_are_exact_cover_points": False, "observations_used": False,
    }


def write_complete_domain(*, expected_compilation_digest, progress=None):
    """Execute all original polynomial columns on the same declared A domain."""

    columns = symbolic.read_completed_columns(expected_digest=expected_compilation_digest)
    before = symbolic._source_signature()
    name, branch, frame = domains.declared_frames()[0]
    if name != "A" or branch != (0, 0) or frame.point.bits != 100:
        raise ValueError("the predeclared original uncertain domain changed")
    start = perf_counter()
    with NamedTemporaryFile(dir=OUTPUT.parent, prefix=".symbolic_evaluation_", delete=False) as raw:
        temporary = Path(raw.name)
    try:
        with temporary.open("wb") as raw, gzip.GzipFile(filename="", mode="wb",
                                                       fileobj=raw, mtime=0) as stream:
            for column in columns:
                values = column.evaluate(frame, source_signature=before)
                record = {"basis_index": column.basis_index,
                    "coefficient_columns_constant_a0_a1": [
                        symbolic.original.bounded._matrix_record(m) for m in values]}
                stream.write(archive._canonical(record) + b"\n")
                if progress is not None and (column.basis_index % 500 == 0
                                             or column.basis_index == 5344):
                    cache = symbolic.original._monomial.cache_info()._asdict()
                    progress({"last_original_index": column.basis_index,
                              "elapsed_seconds": perf_counter() - start,
                              "regular_monomial_cache": cache})
        verified = archive.verify_archive(temporary, bits=100)
        if symbolic._source_signature() != before:
            raise ValueError("an original source changed during complete polynomial evaluation")
        record = {**_scope(expected_compilation_digest, frame), **verified,
                  "complete_original_basis_evaluated": True,
                  "matrix_archive_sha256": archive._file_digest(temporary),
                  "matrix_archive_bytes": temporary.stat().st_size}
        record["artifact_digest"] = hashlib.sha256(archive._canonical(record)).hexdigest()
        archive._install_unchanged_or_new(temporary, MATRIX)
        with NamedTemporaryFile(dir=OUTPUT.parent, prefix=".symbolic_evaluation_meta_",
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


def verify_completed_domain(*, expected_digest, expected_compilation_digest):
    """Validate the full bounded stream against trusted execution and source inputs."""

    before = symbolic._source_signature()
    symbolic.verify_completed_chart(expected_digest=expected_compilation_digest)
    digest, record = symbolic.original.fiber._verified_payload(OUTPUT)
    if digest != expected_digest:
        raise ValueError("the completed polynomial evaluation changed its trusted digest")
    name, branch, frame = domains.declared_frames()[0]
    if name != "A" or branch != (0, 0):
        raise ValueError("the declared original evaluation domain changed")
    required = {**_scope(expected_compilation_digest, frame),
                **archive.verify_archive(MATRIX, bits=100),
                "complete_original_basis_evaluated": True,
                "matrix_archive_sha256": archive._file_digest(MATRIX),
                "matrix_archive_bytes": MATRIX.stat().st_size}
    archive._require_scope(record, required)
    if symbolic._source_signature() != before or archive._file_digest(MATRIX) != required[
        "matrix_archive_sha256"]:
        raise ValueError("an original source or complete polynomial-evaluation stream changed")
    return {"artifact_digest": digest, **record}
