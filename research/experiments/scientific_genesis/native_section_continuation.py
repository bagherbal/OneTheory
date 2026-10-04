"""Carry retained native roots through original full-section trial covariances.

Owns:
    Same-stream named-frame admission, retained failures and complete original
    polynomial-column contraction without replacing the section or fiber engine.

Depends on:
    Native subdivision continuation, original bounded quotient frames, trusted
    complete polynomial compilation and the existing exact covariance machinery.

Must not:
    Replace unresolved inputs, change bases silently, choose physical moduli,
    call a trial form canonical or infer integration or Ricci-flat/HYM convergence.

Phase 0:
    Research composition only; physical metrics and a common vacuum remain open.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from dataclasses import dataclass, replace
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import perf_counter

from onetheory.math.numbers import Eisenstein, Rational

from . import alternate_metric_symbolic_columns as symbolic
from . import alternate_section_covariance as covariance
from . import projective_subdivision_roots as roots

draws, native = roots.draws, roots.native
bounded = symbolic.original.bounded
archive = symbolic.archive
ROOT = roots.ROOT
OUTPUT = roots.OUTPUT.with_name("native_section_continuation.json")
MATRIX = OUTPUT.with_suffix(".columns.jsonl.gz")
PROOF = Path(__file__).with_name("NATIVE_SECTION_CONTINUATION_NOTE.md")
COMPILATION = "63dcc3ff50a8cf3aadbd896dd20a732774efbc460d714daeb2ee8ce41c44a488"
ROOT_ADMISSION = "27169bb7b404a863bee7791512169e03ab9ad3790596cd3baf1736c0f58ff768"


@dataclass(frozen=True, slots=True)
class FramePolicy:
    """Caller-declared normalized chart, ordered quotient rows and arithmetic."""

    chart: tuple[int, int, int]
    first_pivots: tuple[int, int]
    second_pivots: tuple[int, int, int]
    center_bits: int
    volume_scale: Eisenstein
    covering_degree: int

    def __post_init__(self):
        if (not isinstance(self.chart, tuple) or len(self.chart) != 3
            or any(type(i) is not int or not 0 <= i < n
                   for i, n in zip(self.chart, (3, 3, 2), strict=True))):
            raise ValueError("an explicit normalized cover chart is required")
        for rows, size, count in ((self.first_pivots, 4, 2), (self.second_pivots, 5, 3)):
            if (not isinstance(rows, tuple) or len(rows) != count
                or any(type(i) is not int or not 0 <= i < size for i in rows)
                or len(set(rows)) != count):
                raise ValueError("distinct ordered original quotient pivot rows required")
        bounded.bounds._bits(self.center_bits)
        scale = Eisenstein.coerce(self.volume_scale)
        if scale.is_zero() or type(self.covering_degree) is not int or self.covering_degree < 1:
            raise ValueError("explicit nonzero volume scale and covering degree required")
        object.__setattr__(self, "volume_scale", scale)

    def extends(self, old):
        return (isinstance(old, FramePolicy) and self.center_bits >= old.center_bits
                and replace(self, center_bits=old.center_bits) == old)


def _retains_root(draw, ancestor):
    current = draw if isinstance(draw, draws.CoupledDraw) else draw.admitted_parent
    while current is not None:
        if current == ancestor:
            return True
        current = current.admitted_parent
    return False


@dataclass(frozen=True, slots=True)
class AdmittedFrame:
    """Original named quotient and homogeneous weight on one retained draw."""

    draw: draws.CoupledDraw
    policy: FramePolicy
    frame: bounded.BoundedFiberFrame
    weight: draws.weights.HomogeneousWeight
    admitted_parent: AdmittedFrame | None = None

    def __post_init__(self):
        if (not isinstance(self.draw, draws.CoupledDraw)
            or not isinstance(self.policy, FramePolicy)
            or not isinstance(self.frame, bounded.BoundedFiberFrame)
            or not isinstance(self.weight, draws.weights.HomogeneousWeight)
            or self.frame.point.intersection != self.draw.configuration
            or self.frame.point.root_pair != self.draw.branch
            or self.frame.point.chart != self.policy.chart
            or self.frame.point.center_bits != self.policy.center_bits
            or self.frame.first_pivots != self.policy.first_pivots
            or self.frame.second_pivots != self.policy.second_pivots
            or self.weight.coordinates != self.draw.coordinates):
            raise ValueError("native branch, original frame and explicit conventions disagree")
        if self.weight != draws.selected_weight(self.draw, volume_scale=self.policy.volume_scale,
                                                covering_degree=self.policy.covering_degree):
            raise ValueError("the weight must reproduce the explicit normalization conventions")
        if self.admitted_parent is not None:
            parent = self.admitted_parent
            if (not isinstance(parent, AdmittedFrame)
                or not self.policy.extends(parent.policy)
                or not self.draw.address.extends(parent.draw.address)
                or self.frame.basis_labels != parent.frame.basis_labels):
                raise ValueError("same named frame and extending native parent required")
            if not _retains_root(self.draw, parent.draw):
                raise ValueError("the original frame parent must be in the native root ancestry")


@dataclass(frozen=True, slots=True)
class PendingFrame:
    """Original unresolved request with its most recent admitted frame retained."""

    draw: draws.CoupledDraw | draws.PendingDraw
    policy: FramePolicy
    stage: str
    reason: str
    admitted_parent: AdmittedFrame | None = None

    def __post_init__(self):
        if (not isinstance(self.draw, (draws.CoupledDraw, draws.PendingDraw))
            or not isinstance(self.policy, FramePolicy) or not self.reason
            or self.stage not in ("root", "frame/weight")):
            raise ValueError("a native unresolved request and explicit failure required")
        if self.admitted_parent is not None and (
            not isinstance(self.admitted_parent, AdmittedFrame)
            or not self.policy.extends(self.admitted_parent.policy)
            or not self.draw.address.extends(self.admitted_parent.draw.address)
            or not _retains_root(self.draw, self.admitted_parent.draw)
        ):
            raise ValueError("the unresolved frame must retain its compatible parent")


def admit_frame(draw, policy, *, parent=None):
    """Use original frame and weight certificates, never midpoint membership."""

    if not isinstance(policy, FramePolicy):
        raise TypeError("an explicit original frame policy is required")
    if isinstance(draw, draws.PendingDraw):
        return PendingFrame(draw, policy, "root", draw.reason, parent)
    if not isinstance(draw, draws.CoupledDraw):
        raise TypeError("a native admitted or pending draw is required")
    try:
        point = native.UncertainCoverPoint(draw.configuration, draw.branch, policy.chart,
                                          draw.policy.input.bound_bits,
                                          center_bits=policy.center_bits)
        frame = bounded.BoundedFiberFrame(point, policy.first_pivots, policy.second_pivots)
        weight = draws.selected_weight(draw, volume_scale=policy.volume_scale,
                                       covering_degree=policy.covering_degree)
    except (ValueError, ZeroDivisionError) as error:
        return PendingFrame(draw, policy, "frame/weight", str(error), parent)
    return AdmittedFrame(draw, policy, frame, weight, parent)


def refine_frame(previous, address, draw_policy, frame_policy, *, max_cells, max_depth,
                 chart_order):
    """Refine the SAME branch without dropping a failed root or frame request."""

    if not isinstance(previous, (AdmittedFrame, PendingFrame)):
        raise TypeError("an original admitted or pending frame request required")
    if not isinstance(frame_policy, FramePolicy) or not frame_policy.extends(previous.policy):
        raise ValueError("keep chart, pivot order, scale and degree; precision cannot decrease")
    parent = previous if isinstance(previous, AdmittedFrame) else previous.admitted_parent
    if (isinstance(previous.draw, draws.CoupledDraw) and address == previous.draw.address
        and draw_policy == previous.draw.policy):
        # A frame-only retry retains the ALREADY certified root family. Asking
        # equal-radius disks to be strictly inside themselves is not refinement.
        draw = previous.draw
    else:
        draw = roots.refine_subdivision_draw(previous.draw, address, draw_policy,
            max_cells=max_cells, max_depth=max_depth, chart_order=chart_order)
    return admit_frame(draw, frame_policy, parent=parent)


def declared_continuation():
    """Predeclared A regression, not a cloud or a selected physical modulus."""

    roots.read_subdivision(expected_digest=ROOT_ADMISSION)
    geometric = draws.declared_policy()
    available = draws.declared_addresses()[0]
    coarse, work0 = roots.refinement_policy(8, first_frame=geometric.first,
                                           second_frame=geometric.second)
    fine, work1 = roots.refinement_policy(12, first_frame=geometric.first,
                                          second_frame=geometric.second)
    policy0 = FramePolicy((0, 0, 0), (0, 2), (0, 1, 2), 64, Eisenstein(1), 9)
    policy1 = replace(policy0, center_bits=96)
    address0, address1 = (roots.refinement_address(available, j) for j in (8, 12))
    parent = admit_frame(roots.attempt_subdivision_draw(address0, coarse, **work0), policy0)
    if not isinstance(parent, AdmittedFrame):
        raise ValueError("the declared original parent frame remains pending")
    pending = refine_frame(parent, address1, fine, policy1, **{**work1, "max_cells": 1})
    if not isinstance(pending, PendingFrame) or pending.admitted_parent != parent:
        raise ValueError("failed work did not retain the original frame parent")
    child = refine_frame(pending, address1, fine, policy1, **work1)
    if not isinstance(child, AdmittedFrame) or child.admitted_parent != parent:
        raise ValueError("the declared original child frame remains pending")
    return parent, pending, child


def _sources():
    paths = (Path(__file__), PROOF, Path(roots.__file__), roots.PROOF,
             Path(symbolic.__file__), symbolic.PROOF, Path(bounded.__file__),
             Path(bounded.bounds.__file__), Path(covariance.__file__), covariance.PROOF,
             Path(draws.__file__), Path(native.__file__), Path(draws.weights.__file__))
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def _frame_record(admission):
    record = {"draw": draws._draw_record(admission.draw),
        "chart_pivots": list(admission.policy.chart),
        "first_pivot_rows": list(admission.policy.first_pivots),
        "second_pivot_rows": list(admission.policy.second_pivots),
        "center_bits": admission.policy.center_bits,
        "volume_scale": [str(admission.policy.volume_scale.a),
                         str(admission.policy.volume_scale.b)],
        "covering_degree": admission.policy.covering_degree,
        "admitted_frame_parent_retained": admission.admitted_parent is not None}
    if isinstance(admission, PendingFrame):
        return {**record, "status": "unresolved", "stage": admission.stage,
                "reason": admission.reason}
    return {**record, "status": "admitted",
        "fiber_basis_labels": list(admission.frame.basis_labels),
        "normalized_coordinate_bounds": [[native._ball_record(c) for c in group]
            for group in (admission.frame.point.x, admission.frame.point.u,
                          admission.frame.point.p)],
        "relation_minor": native._ball_record(admission.frame.relation_minor),
        "cover_weight_without_pi_cubed": bounded.bounds._interval_record(
            admission.weight.cover_weight_without_pi_cubed),
        "quotient_weight_without_pi_cubed": bounded.bounds._interval_record(
            admission.weight.quotient_weight_without_pi_cubed)}


def _scope(parent, pending, child):
    return {"schema": "native-section-continuation-v1", "source_files_sha256": _sources(),
        "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
        "root_admission_parent_digest": ROOT_ADMISSION, "compilation_parent_digest": COMPILATION,
        "original_section_basis_digest": symbolic.section_basis_identity()["artifact_digest"],
        "original_source_signature": symbolic._source_signature(),
        "parent_frame": _frame_record(parent), "retained_failed_refinement": _frame_record(pending),
        "continued_frame": _frame_record(child), "parameter_order": ["constant", "a0", "a1"],
        "matrix_archive": str(MATRIX.relative_to(ROOT)),
        "domain_role": "one predeclared same-stream A regression, not IID evidence",
        "section_form_kind": "explicit computational unit-H trial input, not canonical physics",
        "twist_cover_degree": [14, 16, 1], "line_twist_removed": False,
        "unit_form_is_physical_or_canonical": False,
        "point_dependent_stream_is_global_section_identity": False,
        "all_components_or_domains_executed": False,
        "independent_all_column_cochain_replay": False,
        "independent_cover_cloud_available": False, "controlled_integral_available": False,
        "ricci_flat_or_hym_metric_available": False, "physical_yukawas_available": False,
        "common_stabilized_vacuum_available": False, "extension_parameters_specialized": False,
        "observations_used": False}


def write_complete_continuation(*, progress=None):
    """Consume every original compiled column on the continued actual frame."""

    before = _sources(), symbolic._source_signature()
    parent, pending, child = declared_continuation()
    columns = symbolic.read_completed_columns(expected_digest=COMPILATION)
    basis = symbolic.section_basis_identity()["artifact_digest"]
    form = covariance.SectionForm(basis, tuple(range(5345)), (Rational(1),)*5345, ())
    bits, center_bits = child.draw.policy.input.bound_bits, child.policy.center_bits
    started = perf_counter()
    with NamedTemporaryFile(dir=OUTPUT.parent, prefix=".native_section_", delete=False) as raw:
        temporary = Path(raw.name)
    try:
        with temporary.open("wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw,
                                                       mtime=0) as stream:
            def values():
                for column in columns:
                    matrices = column.evaluate(child.frame, source_signature=before[1])
                    record = {"basis_index": column.basis_index,
                        "coefficient_columns_constant_a0_a1": [bounded._matrix_record(m)
                                                               for m in matrices]}
                    stream.write(archive._canonical(record)+b"\n")
                    if progress is not None and (column.basis_index % 500 == 0
                                                 or column.basis_index == 5344):
                        progress({"last_original_index": column.basis_index,
                                  "elapsed_seconds": perf_counter()-started})
                    yield column.basis_index, tuple(tuple(row[0] for row in m) for m in matrices)

            actual = covariance.contract_columns(values(), form, basis_digest=basis,
                fiber_labels=child.frame.basis_labels, bits=bits, center_bits=center_bits)
        verified = archive.verify_archive(temporary, bits=bits)
        if (_sources(), symbolic._source_signature()) != before:
            raise ValueError("an original source or continuation proof changed during execution")
        blocks = [[covariance._matrix_record(m) for m in row] for row in actual.blocks]
        cover = covariance.weighted_blocks(actual, child.weight.cover_weight_without_pi_cubed)
        quotient = covariance.weighted_blocks(actual, child.weight.quotient_weight_without_pi_cubed)
        record = {**_scope(parent, pending, child), **verified,
            "matrix_archive_sha256": archive._file_digest(temporary),
            "matrix_archive_bytes": temporary.stat().st_size,
            "bound_bits": bits, "uncertain_center_bits": center_bits,
            "all_original_columns_consumed": True,
            "native_same_root_frame_continuation_executed": True,
            "full_trial_covariance_integrands_executed": True,
            "unweighted_blocks": blocks,
            "weighted_cover_blocks_without_pi_cubed": [[covariance._matrix_record(m) for m in row]
                                                        for row in cover],
            "weighted_quotient_blocks_without_pi_cubed": [
                [covariance._matrix_record(m) for m in row] for row in quotient],
            "full_inverse_trial_kernel_executed": False,
            "requested_numerical_accuracy_certified": False}
        record["artifact_digest"] = roots._digest(record)
        archive._install_unchanged_or_new(temporary, MATRIX)
        with NamedTemporaryFile(dir=OUTPUT.parent, prefix=".native_section_meta_",
                                delete=False) as raw:
            metadata = Path(raw.name)
        try:
            metadata.write_text(json.dumps(record, sort_keys=True, indent=2)+"\n")
            archive._install_unchanged_or_new(metadata, OUTPUT)
        finally:
            metadata.unlink(missing_ok=True)
        return record
    finally:
        temporary.unlink(missing_ok=True)


def read_complete_continuation(*, expected_digest):
    """Verify trusted full execution and replay every numeric trial contraction.

    The stream is an executed output, not a new source of section identities.
    This does not repeat all polynomial evaluations or claim a fresh full
    independent cochain derivation. Critical independent algebra is tested
    from the numeric stream and selected original exact coefficients.
    """

    before = _sources(), symbolic._source_signature()
    digest, record = symbolic.original.fiber._verified_payload(OUTPUT)
    if digest != expected_digest:
        raise ValueError("native section output differs from its trusted execution digest")
    symbolic.verify_completed_chart(expected_digest=COMPILATION)
    parent, pending, child = declared_continuation()
    bits, center_bits = child.draw.policy.input.bound_bits, child.policy.center_bits
    form = covariance.SectionForm(symbolic.section_basis_identity()["artifact_digest"],
                                  tuple(range(5345)), (Rational(1),)*5345, ())
    stream_digest = archive._file_digest(MATRIX)
    verified = archive.verify_archive(MATRIX, bits=bits)

    def columns():
        with gzip.open(MATRIX, "rb") as stream:
            for line in stream:
                yield covariance.decode_column(json.loads(line), bits=bits, center_bits=center_bits)

    actual = covariance.contract_columns(columns(), form, basis_digest=form.basis_digest,
        fiber_labels=child.frame.basis_labels, bits=bits, center_bits=center_bits)
    cover = covariance.weighted_blocks(actual, child.weight.cover_weight_without_pi_cubed)
    quotient = covariance.weighted_blocks(actual, child.weight.quotient_weight_without_pi_cubed)
    required = {**_scope(parent, pending, child), **verified,
        "matrix_archive_sha256": stream_digest, "matrix_archive_bytes": MATRIX.stat().st_size,
        "bound_bits": bits, "uncertain_center_bits": center_bits,
        "all_original_columns_consumed": True, "native_same_root_frame_continuation_executed": True,
        "full_trial_covariance_integrands_executed": True,
        "unweighted_blocks": [[covariance._matrix_record(m) for m in row] for row in actual.blocks],
        "weighted_cover_blocks_without_pi_cubed": [[covariance._matrix_record(m) for m in row]
                                                    for row in cover],
        "weighted_quotient_blocks_without_pi_cubed": [[covariance._matrix_record(m) for m in row]
                                                       for row in quotient],
        "full_inverse_trial_kernel_executed": False,
        "requested_numerical_accuracy_certified": False}
    archive._require_scope(record, required)
    if ((_sources(), symbolic._source_signature()) != before
        or archive._file_digest(MATRIX) != stream_digest):
        raise ValueError(
            "an original source, proof or complete numeric stream changed during replay")
    return {"artifact_digest": digest, **record}


if __name__ == "__main__":
    print(write_complete_continuation(progress=lambda r: print(json.dumps(r), flush=True))[
        "artifact_digest"], flush=True)
