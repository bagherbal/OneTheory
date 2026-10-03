"""Execute original universal frames and section probes on coupled input families.

Owns:
    Declared 9/3/3 domain execution, original relation-minor certificates,
    named quotient coefficients, and full outer-corrected section enclosures.

Depends on:
    Native uncertain root families, unchanged bounded quotient arithmetic,
    original exact universal cochains, and traceable frozen source archives.

Must not:
    Supply a second bundle or section engine, select extension parameters,
    promote probe columns into a complete matrix, or claim integration or metrics.

Phase 0:
    Conditional research domain verification; physical normalization is unresolved.
"""

from __future__ import annotations

import hashlib
import json
from functools import cache
from pathlib import Path

from . import alternate_metric_bounded_fibers as bounded
from . import projective_uncertain_intersections as roots
from . import uncertain_cover_weights as weights

ROOT = roots.ROOT
OUTPUT = ROOT / "data/generated/scientific_genesis/uncertain_cover_frames.json"
PROOF = Path(__file__).with_name("UNCERTAIN_COVER_FRAMES_NOTE.md")
INDICES = (0, 2655)


def _parents():
    """Check fresh source bytes even when immutable evaluated objects are cached."""

    paths = (
        (roots.OUTPUT, "97981cfe6a6d67fd40287c8902a99f4ce3a73729fea6a64b4f133fdce82c0d26"),
        (weights.OUTPUT, "5be593ab1bfa8d1200b72a944d127cde33343158f1be79236ed5bcef51934429"),
        (bounded.OUTPUT, "d9e320a952cc6d5fc843ea2f9c0254823d8d9a49b8d6dbd1d2dda0dd2d61f01c"),
        (bounded.fiber.lifts.OUTPUT,
         "3708b3f7757ec12080daa98d09315ed53a2c7d0e0ead61ff3a55777bb00aaa4c"),
    )
    parents = {}
    for path, expected in paths:
        digest, _ = bounded.fiber._verified_payload(path)
        if digest != expected:
            raise ValueError("an original uncertain-domain frame prerequisite changed")
        parents[str(path.relative_to(ROOT))] = digest
    actual, _, _ = bounded.fiber.lifts._inputs()
    _, original = bounded.fiber._verified_payload(bounded.fiber.lifts.OUTPUT)
    if actual != original["prerequisite_artifact_digests"]:
        raise ValueError("the original ordered universal section inputs changed")
    sources = (
        (bounded.fiber.lifts.first.OUTPUT, actual["first"]),
        (bounded.fiber.lifts.second.OUTPUT, actual["second"]),
        (bounded.fiber.lifts.INVARIANTS, actual["invariants"]),
        (bounded.fiber.lifts.second.CONE, actual["cone"]),
    )
    archives = {}
    for path, expected in sources:
        digest, source = bounded.fiber._verified_payload(path)
        if digest != expected:
            raise ValueError("the actual section or outer-cone source changed")
        parents[str(path.relative_to(ROOT))] = digest
        if "section_archive" in source:
            archive = ROOT / source["section_archive"]
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            if digest != source["section_archive_sha256"]:
                raise ValueError("an original complete section archive changed")
            archives[source["section_archive"]] = digest
    return parents, archives


@cache
def declared_frames():
    """Retain all branches, with explicit fixed chart and relation row choices."""

    return tuple((name, branch, bounded.BoundedFiberFrame(
        roots.UncertainCoverPoint(configuration, branch, (0, 0, 0), 100, center_bits=100),
        (0, 2), (0, 1, 2),
    )) for name, configuration in zip(("A", "Bx", "Bu"), weights.declared_configurations(),
                                       strict=True) for branch in configuration.root_pairs)


@cache
def original_section(index):
    """Reuse the full original constructor, including both nonsplit corrections."""

    if type(index) is not int or index not in INDICES:
        raise ValueError("one of the explicitly declared original probe indices is required")
    return bounded.fiber.lifts.universal_section(index)


@cache
def section_columns(frame, index):
    """Cache immutable original cochain bounds, never center specializations."""

    return frame._evaluate_section(original_section(index))


def frame_record():
    """Reproduce the complete declared domain set, not a full section matrix."""

    parents, archives = _parents()
    sections = tuple(original_section(i) for i in INDICES)
    records = []
    for name, branch, frame in declared_frames():
        records.append({
            "component": name, "root_pair": list(branch),
            "chart_pivots": list(frame.point.chart),
            "first_pivot_rows": list(frame.first_pivots),
            "second_pivot_rows": list(frame.second_pivots),
            "fiber_basis_labels": list(frame.basis_labels),
            "normalized_cover_bounds": [[roots._ball_record(c) for c in group]
                                        for group in (frame.point.x, frame.point.u, frame.point.p)],
            "relation_minor": roots._ball_record(frame.relation_minor),
            "relations_constant_a0_a1": [bounded._matrix_record(m) for m in frame.relations],
            "projections_constant_a0_a1": [bounded._matrix_record(m) for m in frame.projections],
            "actual_universal_section_probes": [{
                "basis_index": i,
                "coefficient_columns_constant_a0_a1": [
                    bounded._matrix_record(m) for m in section_columns(frame, i)
                ],
            } for i in INDICES],
        })
    if _parents() != (parents, archives):
        raise ValueError("actual source inputs changed during domain/section execution")
    return {
        "schema": "uncertain-cover-frames-v1", "prerequisite_artifact_digests": parents,
        "original_section_archive_sha256": archives,
        "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
        "parameter_basis": ["a0", "a1"], "bound_bits": 100,
        "uncertain_center_bits": 100,
        "center_policy": (
            "explicit dyadic rounding with certified displacement; exact zeros retained"
        ),
        "original_basis_count": 5345, "original_constituent_counts": [2655, 2690],
        "declared_component_branch_counts": [9, 3, 3],
        "domain_law": "declared regression input cells; not independent samples",
        "original_section_probes": [{
            "basis_index": s.basis_index,
            "constant_cochain_digest": bounded.fiber.lifts._cochain_digest(
                (s.first_constant, s.second_constant),
            ),
            "correction_cochain_digests": [bounded.fiber.lifts._cochain_digest((c,))
                                           for c in s.first_coefficients],
            "correction_term_counts": [len(c.terms) for c in s.first_coefficients],
        } for s in sections],
        "actual_domain_probes": records,
        "all_declared_domain_relation_minors_exclude_zero": True,
        "original_full_cochain_probe_bounds_available": True,
        "original_input_and_root_error_retained": True,
        "centers_are_exact_cover_points": False,
        "complete_5345_column_matrix_on_new_domains_available": False,
        "global_input_coverage_available": False,
        "independent_sampling_cloud_available": False,
        "controlled_integral_available": False,
        "ricci_flat_metric_available": False, "hym_metric_available": False,
        "physical_yukawas_available": False, "common_stabilized_vacuum_available": False,
        "extension_point_selected": False, "observations_used": False,
    }


def write_frames(path=OUTPUT):
    """Atomically archive actual executed domains and original section probes."""

    record = frame_record()
    record["artifact_digest"] = roots._digest(record)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return record


def read_frames(path=OUTPUT):
    """Reconstruct all original bounds; a new hash alone cannot alter their scope."""

    record = json.loads(path.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest", None)
    if digest != roots._digest(record) or digest != roots._digest(frame_record()):
        raise ValueError("uncertain-cover frames changed their actual domains, sections, or scope")
    return record


if __name__ == "__main__":
    print(write_frames()["artifact_digest"])
