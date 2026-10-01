"""Materialize the original bounded section matrix on one certified chart domain.

Owns:
    Deterministic complete-column streaming, atomic content-addressed output,
    independent archive validation, and explicit single-domain scope metadata.

Depends on:
    The established bounded all-index evaluator, certified projective roots,
    original section archives, and determinant-certified universal frames.

Must not:
    Substitute centers as exact points, omit columns, select moduli, turn a
    regression configuration into a sampling law, or infer a converged metric.

Phase 0:
    Research complete-output execution; physical normalization remains open.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from contextlib import contextmanager
from fractions import Fraction
from pathlib import Path
from tempfile import NamedTemporaryFile

from onetheory.math.numbers import Eisenstein, Rational

from . import alternate_metric_bounded_support as support

bounds, bounded, fiber = support.bounds, support.bounded, support.fiber
OUTPUT = support.OUTPUT.with_name("alternate_metric_bounded_matrix.json")
MATRIX = OUTPUT.with_suffix(".columns.jsonl.gz")


def declared_frame(name):
    """Reconstruct an explicitly named regression domain, not a probability draw."""

    root_digest, root_parent = fiber._verified_payload(bounds.roots.OUTPUT)
    matches = tuple(r for r in root_parent["actual_configurations"] if r["name"] == name)
    if len(matches) != 1 or name not in ("finite_chart", "infinity_branch"):
        raise ValueError("one explicitly named certified regression configuration is required")
    raw = matches[0]

    def scalar(pair):
        return Eisenstein(Fraction(pair[0]), Fraction(pair[1]))

    lines = tuple(bounds.roots.ProjectiveLine(*(tuple(scalar(c) for c in v) for v in raw[key]))
                  for key in ("first_line", "second_line"))
    intersection = bounds.roots.intersection_roots(
        *lines, tuple(scalar(c) for c in raw["P1_point"]),
        parameter_pivots=(raw["first"]["parameter_pivot"], raw["second"]["parameter_pivot"]),
        policy=bounds.roots.RootPolicy(Rational(1, 2**30), 60, 80, 128),
    )
    pair = (0, 0) if name == "finite_chart" else ("infinity", 0)
    chart = (0, 0, 0) if name == "finite_chart" else (1, 0, 1)
    point = bounds.BoundedCoverPoint(intersection, pair, chart, 80)
    return bounded.BoundedFiberFrame(point, (0, 2), (0, 1, 2)), root_digest


def _canonical(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode()


def _file_digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _validate_column(record, index, bits):
    """Validate stream identity and exact enclosures independently of the producer."""

    if not isinstance(record, dict) or type(record.get("basis_index")) is not int:
        raise ValueError("every column needs its original integer basis identity")
    if record["basis_index"] != index:
        raise ValueError("the original column ordering or completeness changed")
    matrices = record.get("coefficient_columns_constant_a0_a1")
    if not isinstance(matrices, list) or len(matrices) != 3:
        raise ValueError("all constant/a0/a1 coefficient columns are required")
    uncertain, radius = 0, Fraction(0)
    for parameter, matrix in enumerate(matrices):
        if not isinstance(matrix, list) or len(matrix) != 4:
            raise ValueError("each original fiber column has four named coordinates")
        for row in matrix:
            if not isinstance(row, list) or len(row) != 1:
                raise ValueError("fiber coefficients require four-by-one columns")
            c = row[0]
            if (not isinstance(c, dict) or set(c) != {"center", "radius"}
                or not isinstance(c["center"], list) or len(c["center"]) != 2
                or not all(isinstance(v, str) for v in (*c["center"], c["radius"]))):
                raise ValueError("explicit rational center pairs and radii are required")
            center = tuple(Fraction(v) for v in c["center"])
            r = Fraction(c["radius"])
            if r < 0 or (r * 2**bits).denominator != 1:
                raise ValueError("radii must be nonnegative at the declared outward mesh")
            if index < 2655 and parameter > 0 and (r or any(center)):
                raise ValueError("injected V1 sections cannot acquire extension coefficients")
            uncertain += int(r > 0)
            radius = max(radius, r)
    return uncertain, radius


def verify_archive(path, *, bits):
    """Read every stored column with an independent streaming parser and hash."""

    bounds._bits(bits)
    digest, count, uncertain, radius = hashlib.sha256(), 0, 0, Fraction(0)
    with gzip.open(path, "rb") as stream:
        for line in stream:
            record = json.loads(line)
            if line != _canonical(record) + b"\n":
                raise ValueError("stored columns must have canonical deterministic encoding")
            n, r = _validate_column(record, count, bits)
            digest.update(line)
            count += 1
            uncertain += n
            radius = max(radius, r)
    if count != 5345:
        raise ValueError("the complete matrix must contain all 5345 original columns")
    return {"section_count": count, "exact_column_stream_sha256": digest.hexdigest(),
            "coefficient_entry_count": 12 * count, "uncertain_entry_count": uncertain,
            "largest_coefficient_radius": str(radius)}


def _install_unchanged_or_new(temporary, destination):
    if destination.exists():
        if _file_digest(destination) != _file_digest(temporary):
            raise ValueError("refusing to overwrite a different existing scientific output")
    else:
        temporary.replace(destination)


@contextmanager
def _scratch_files():
    """Use private files in the output filesystem, not architectural directories."""

    with NamedTemporaryFile(dir=OUTPUT.parent, prefix=".bounded_matrix_", delete=False) as stream:
        temporary = Path(stream.name)
    meta = temporary.with_name(temporary.name + ".metadata")
    try:
        yield temporary, meta
    finally:
        temporary.unlink(missing_ok=True)
        meta.unlink(missing_ok=True)


def write_complete_matrix(*, progress=None):
    """Evaluate every original index; install output only after complete validation.

    The fixed regression input is explicitly the predecessor finite chart.
    It is not a selected point in bundle/vacuum moduli or a sampled geometry.
    Timing/progress are emitted externally and never enter the artifact hash.
    """

    parent_digest, parent = fiber._verified_payload(support.OUTPUT)
    if (parent.get("compressed_complete_section_enclosure_engine_available") is not True
        or parent.get("original_constituent_counts") != [2655, 2690]):
        raise ValueError("the original bounded all-index engine prerequisite is absent")
    frame, root_digest = declared_frame("finite_chart")
    engine = support.BoundedSupportEvaluator(frame)
    if progress is not None:
        progress("frame_ready", 0)
    with _scratch_files() as (temporary, meta):
        with temporary.open("wb") as raw, gzip.GzipFile(
            fileobj=raw, mode="wb", filename="", mtime=0, compresslevel=9,
        ) as stream:
            for index in range(5345):
                record = {"basis_index": index, "coefficient_columns_constant_a0_a1": [
                    bounded._matrix_record(m) for m in engine.evaluate_basis(index)
                ]}
                _validate_column(record, index, 80)
                stream.write(_canonical(record) + b"\n")
                if progress is not None and (index % 100 == 0 or index == 5344):
                    progress("columns_written", index + 1)
        verified = verify_archive(temporary, bits=80)
        payload = {
            "schema": "alternate-metric-bounded-matrix-v1",
            "bounded_support_artifact_digest": parent_digest,
            "root_artifact_digest": root_digest,
            "configuration_name": "finite_chart", "root_pair": [0, 0],
            "chart_pivots": [0, 0, 0], "first_pivot_rows": [0, 2],
            "second_pivot_rows": [0, 1, 2], "fiber_basis_labels": list(frame.basis_labels),
            "bound_bits": 80, "parameter_basis": ["a0", "a1"],
            "original_constituent_counts": [2655, 2690],
            "matrix_archive": str(MATRIX.relative_to(fiber.lifts.first.ROOT)),
            "matrix_archive_sha256": _file_digest(temporary),
            "matrix_archive_bytes": temporary.stat().st_size,
            **verified,
            "complete_bounded_5345_column_matrix_materialized": True,
            "single_certified_local_domain_only": True,
            "independent_full_cochain_checks_from_parent": [2655],
            "independent_all_column_full_cochain_replay_performed": False,
            "practical_multi_point_integration_throughput_certified": False,
            "bounded_section_and_density_evaluation_available": False,
            "controlled_numerical_sampling_available": False,
            "numerical_metrics_available": False, "physical_yukawas_available": False,
            "centers_are_exact_cover_points": False,
            "extension_point_selected": False, "vacuum_selected": False,
            "observational_inputs_used": False,
            "next_required_object": (
                "control multi-point cost, SU-uniform proposal precision, integration error, "
                "and Ricci-flat/HYM convergence; keep the common vacuum unresolved"
            ),
        }
        payload["artifact_digest"] = hashlib.sha256(_canonical(payload)).hexdigest()
        meta.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        _install_unchanged_or_new(temporary, MATRIX)
        _install_unchanged_or_new(meta, OUTPUT)
    return payload
