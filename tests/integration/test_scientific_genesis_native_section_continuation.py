"""Attack retained native frame and original complete section continuation.

Owns:
    Parent retention, explicit basis and normalization checks, original quotient
    arithmetic and full numeric-stream trial covariance verification.

Depends on:
    Native research continuation and the existing original polynomial archive,
    independent Fraction-pair algebra and pytest for scoped failure attacks.

Must not:
    Call computational section forms physical, centers geometric points or
    regression addresses IID; no sampling or metric convergence is inferred.

Phase 0:
    Research composition tests only; physical normalization remains unresolved.
"""

import copy
import gzip
import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
from functools import cache

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.scientific_genesis import native_section_continuation as module
from tests.integration.test_scientific_genesis_completed_symbolic_columns import (
    PROBES,
)
from tests.integration.test_scientific_genesis_completed_symbolic_columns import (
    _inspection as _polynomial_records,
)
from tests.integration.test_scientific_genesis_completed_symbolic_evaluation import (
    _exact_polynomial,
)
from tests.integration.test_scientific_genesis_uncertain_cover_frames import (
    _full_boundary,
    _functional,
)

DIGEST = "7584936b3d0d5c310b0bb402e1c210ff76df8e01fd9b8a1e0321e06d098bccb1"


@cache
def _continued():
    return module.declared_continuation()


def test_original_frame_continues_same_branch_through_native_work_failure():
    parent, pending, child = _continued()
    assert pending.admitted_parent == child.admitted_parent == parent
    assert pending.draw.admitted_parent == child.draw.admitted_parent == parent.draw
    assert child.draw.address.extends(parent.draw.address)
    assert child.draw.branch == module.draws._continued_branch(
        child.draw.configuration, parent.draw)
    assert parent.frame.basis_labels == child.frame.basis_labels
    assert parent.policy.chart == child.policy.chart == (0, 0, 0)
    assert parent.policy.center_bits == 64 and child.policy.center_bits == 96
    with pytest.raises(FrozenInstanceError):
        child.policy.center_bits = 100


@pytest.mark.parametrize("change", ("chart", "first", "second", "scale", "degree", "precision"))
def test_refinement_rejects_silent_frame_or_normalization_replacement(change):
    parent, _, child = _continued()
    policy = child.policy
    changes = {"chart": {"chart": (1, 0, 0)}, "first": {"first_pivots": (2, 0)},
        "second": {"second_pivots": (1, 0, 2)}, "scale": {"volume_scale": Eisenstein(2)},
        "degree": {"covering_degree": 3}, "precision": {"center_bits": 63}}
    policy = replace(policy, **changes[change])
    with pytest.raises(ValueError, match="keep chart"):
        module.refine_frame(parent, child.draw.address, child.draw.policy, policy,
                            max_cells=20000, max_depth=48, chart_order=(0, 1))


@pytest.mark.parametrize("rows", ((0, 0), (True, 2), (0,), (0, 4)))
def test_frame_policy_rejects_duplicate_aliased_or_foreign_original_rows(rows):
    with pytest.raises(ValueError, match="pivot rows"):
        module.FramePolicy((0, 0, 0), rows, (0, 1, 2), 96, Eisenstein(1), 9)


def test_native_root_success_followed_by_frame_failure_retains_both_parents(monkeypatch):
    parent, _, child = _continued()
    original = module.bounded.BoundedFiberFrame

    def denied(*args, **kwargs):
        raise ZeroDivisionError("explicit frame admission failure probe")

    monkeypatch.setattr(module.bounded, "BoundedFiberFrame", denied)
    pending = module.admit_frame(child.draw, child.policy, parent=parent)
    assert isinstance(pending, module.PendingFrame) and pending.stage == "frame/weight"
    assert pending.draw == child.draw and pending.admitted_parent == parent
    monkeypatch.setattr(module.bounded, "BoundedFiberFrame", original)
    # More declared work and the same exposed address cannot resample a root.
    result = module.refine_frame(pending, child.draw.address, child.draw.policy, child.policy,
                                max_cells=20000, max_depth=48, chart_order=(0, 1))
    assert isinstance(result, module.AdmittedFrame)
    assert result.admitted_parent == parent and result.draw == child.draw
    assert result.frame.basis_labels == parent.frame.basis_labels


def test_foreign_first_admission_cannot_impersonate_a_retained_frame_child():
    parent, _, child = _continued()
    # A new first admission carries no native parent even if it encloses
    # the same limiting input. Its disk index is not a continuation proof.
    foreign = module.roots.attempt_subdivision_draw(child.draw.address, child.draw.policy,
        max_cells=20000, max_depth=48, chart_order=(0, 1))
    frame = module.admit_frame(foreign, child.policy)
    assert isinstance(frame, module.AdmittedFrame)
    with pytest.raises(ValueError, match="native root ancestry"):
        replace(frame, admitted_parent=parent)


def test_scope_declaration_is_not_complete_execution_or_physical_normalization():
    parent, pending, child = _continued()
    record = module._scope(parent, pending, child)
    assert record["original_section_basis_digest"] == (
        "71f9c2f46c1f7a69087e8f3aab1ed98f4474cf76cf66db5bf2c902f4f372621c")
    assert record["continued_frame"]["fiber_basis_labels"] == list(child.frame.basis_labels)
    assert "section_count" not in record and "artifact_digest" not in record
    for field in ("unit_form_is_physical_or_canonical", "all_components_or_domains_executed",
                  "point_dependent_stream_is_global_section_identity",
                  "independent_cover_cloud_available", "controlled_integral_available",
                  "ricci_flat_or_hym_metric_available", "physical_yukawas_available",
                  "common_stabilized_vacuum_available", "extension_parameters_specialized"):
        assert record[field] is False


def _plus(a, b):
    return a[0]+b[0], a[1]+b[1]


def _times(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]-a[1]*b[1]


def _conjugate(a):
    return a[0]-a[1], -a[1]


def _scalar(record):
    assert set(record) == {"center", "radius"} and len(record["center"]) == 2
    values = (*record["center"], record["radius"])
    assert all(type(c) is str for c in values)
    a, b, radius = map(Fraction, values)
    assert tuple(map(str, (a, b, radius))) == values
    assert radius >= 0 and (radius*2**96).denominator == 1
    return (a, b), radius


def _contains(record, value):
    center, radius = _scalar(record)
    a, b = value[0]-center[0], value[1]-center[1]
    assert a*a-a*b+b*b <= radius*radius


@cache
def _numeric_reference():
    """Read ALL original indices, using no producer column or covariance parser."""

    zero = Fraction(0), Fraction(0)
    accum = {(m, n): [[zero for _ in range(4)] for _ in range(4)]
             for m in range(3) for n in range(3)}
    selected, count, uncertain, largest = {}, 0, 0, Fraction(0)
    digest = hashlib.sha256()
    with gzip.open(module.MATRIX, "rb") as stream:
        for line in stream:
            record = json.loads(line)
            assert set(record) == {"basis_index", "coefficient_columns_constant_a0_a1"}
            assert type(record["basis_index"]) is int and record["basis_index"] == count
            assert line == json.dumps(record, sort_keys=True, separators=(",", ":")).encode()+b"\n"
            matrices = record["coefficient_columns_constant_a0_a1"]
            assert len(matrices) == 3
            values = []
            for matrix in matrices:
                assert len(matrix) == 4 and all(len(row) == 1 for row in matrix)
                entries = []
                for row in matrix:
                    center, radius = _scalar(row[0])
                    entries.append(center)
                    uncertain += int(radius > 0)
                    largest = max(largest, radius)
                values.append(entries)
            forbidden = ((*values[0][2:], *values[1], *values[2]) if count < 2655 else
                         (*values[0][:2], *values[1][2:], *values[2][2:]))
            assert all(c == zero for c in forbidden)
            for (m, n), block in accum.items():
                for r in range(4):
                    for c in range(4):
                        block[r][c] = _plus(block[r][c], _times(
                            values[m][r], _conjugate(values[n][c])))
            if count in PROBES:
                selected[count] = matrices
            digest.update(line)
            count += 1
    assert count == 5345 and set(selected) == set(PROBES)
    return accum, selected, uncertain, largest, digest.hexdigest()


def test_complete_numeric_stream_and_trial_covariance_have_independent_fraction_checks():
    record = json.loads(module.OUTPUT.read_text())
    accum, _, uncertain, largest, stream_digest = _numeric_reference()
    assert record["section_count"] == 5345 and record["coefficient_entry_count"] == 64140
    assert record["exact_column_stream_sha256"] == stream_digest
    assert record["matrix_archive_sha256"] == hashlib.sha256(module.MATRIX.read_bytes()).hexdigest()
    assert record["uncertain_entry_count"] == uncertain
    assert Fraction(record["largest_coefficient_radius"]) == largest
    assert record["bound_bits"] == record["uncertain_center_bits"] == 96
    for (m, n), block in accum.items():
        for r in range(4):
            for c in range(4):
                _contains(record["unweighted_blocks"][m][n][r][c], block[r][c])
                assert accum[n, m][c][r] == _conjugate(block[r][c])
                for domain in ("cover", "quotient"):
                    lo, hi = map(Fraction, record["continued_frame"][
                        f"{domain}_weight_without_pi_cubed"])
                    assert 0 < lo <= hi
                    # Exact arithmetic witness, not a midpoint estimate of a
                    # physical integral or assertion that centers lie on cover.
                    value = _times(block[r][c], ((lo+hi)/2, Fraction(0)))
                    _contains(record[f"weighted_{domain}_blocks_without_pi_cubed"][m][n][r][c],
                              value)


@pytest.mark.parametrize("index", PROBES)
def test_continued_full_output_contains_independent_polynomial_and_gaussian_witnesses(index):
    raw = _polynomial_records()[index]
    _, selected, _, _, _ = _numeric_reference()
    saved = tuple(tuple(_scalar(row[0]) for row in matrix) for matrix in selected[index])
    frame = _continued()[2].frame
    for offset in (0, 1):
        values = _functional(frame, offset)
        constant = tuple(_exact_polynomial(p, values) for p in raw["constant_generators"])
        parameters = tuple(tuple(_exact_polynomial(p, values) for p in group)+(Eisenstein(0),)*5
                           for group in raw["first_parameter_generators"])
        for a0, a1, factors in ((Eisenstein(1), OMEGA, (1, 1)),
                                (OMEGA, Eisenstein(2, -1), (1, 3))):
            _, quotient = _full_boundary(values, frame, a0, a1)
            ambient = Matrix(tuple((c+a0*x+a1*y,) for c, x, y in zip(
                constant, *parameters, strict=True)), scalar_type=Eisenstein)
            expected = quotient.matmul(ambient)
            for row, value in enumerate(expected):
                centers = tuple(Eisenstein(*saved[m][row][0]) for m in range(3))
                center = centers[0]+a0*centers[1]+a1*centers[2]
                radius = saved[0][row][1]+factors[0]*saved[1][row][1]+factors[1]*saved[2][row][1]
                assert (value[0]-center).norm() <= radius**2


def test_completed_output_reconstructs_all_native_frames_and_full_trial_contractions():
    packet = json.loads(module.OUTPUT.read_text())
    assert packet["artifact_digest"] == DIGEST
    actual = module.read_complete_continuation(expected_digest=DIGEST)
    assert actual == packet
    assert actual["all_original_columns_consumed"] is True
    assert actual["native_same_root_frame_continuation_executed"] is True
    assert actual["full_trial_covariance_integrands_executed"] is True
    assert actual["retained_failed_refinement"]["status"] == "unresolved"
    assert actual["continued_frame"]["admitted_frame_parent_retained"] is True
    assert actual["original_section_basis_digest"] != actual["exact_column_stream_sha256"]
    for field in ("unit_form_is_physical_or_canonical", "line_twist_removed",
                  "full_inverse_trial_kernel_executed", "requested_numerical_accuracy_certified",
                  "independent_cover_cloud_available", "controlled_integral_available",
                  "ricci_flat_or_hym_metric_available", "physical_yukawas_available",
                  "common_stabilized_vacuum_available", "extension_parameters_specialized"):
        assert actual[field] is False


@pytest.mark.parametrize("field", (
    "source_files_sha256", "original_section_basis_digest", "continued_frame",
    "unit_form_is_physical_or_canonical", "full_inverse_trial_kernel_executed",
    "requested_numerical_accuracy_certified", "physical_yukawas_available",
))
def test_rehashed_output_cannot_rewrite_trusted_execution_or_scientific_scope(
    field, tmp_path, monkeypatch,
):
    original = json.loads(module.OUTPUT.read_text())
    changed = copy.deepcopy(original)
    changed[field] = not changed[field] if type(changed[field]) is bool else "changed"
    changed.pop("artifact_digest")
    changed["artifact_digest"] = module.roots._digest(changed)
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(changed))
    monkeypatch.setattr(module, "OUTPUT", path)
    with pytest.raises(ValueError, match="trusted execution"):
        module.read_complete_continuation(expected_digest=DIGEST)


def test_new_digest_does_not_disable_fresh_scope_reconstruction(tmp_path, monkeypatch):
    changed = json.loads(module.OUTPUT.read_text())
    changed["full_inverse_trial_kernel_executed"] = True
    changed.pop("artifact_digest")
    changed["artifact_digest"] = module.roots._digest(changed)
    path = tmp_path / "new-expectation.json"
    path.write_text(json.dumps(changed))
    monkeypatch.setattr(module, "OUTPUT", path)
    with pytest.raises(ValueError, match="scientific scope"):
        module.read_complete_continuation(expected_digest=changed["artifact_digest"])


def test_missing_full_output_is_not_replaced_by_a_probe_stream(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "OUTPUT", tmp_path / "missing.json")
    with pytest.raises(FileNotFoundError):
        module.read_complete_continuation(expected_digest="0"*64)
    assert not module.OUTPUT.exists()
