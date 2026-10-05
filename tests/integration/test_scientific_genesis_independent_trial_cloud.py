"""Attack the full-operator discovery experiment without inventing physical inputs.

Owns:
    Exact generic projector witnesses, explicit row-frame invariance, numerical
    failure gates, and identity-preserving unresolved native sample requests.

Depends on:
    The research trial cloud, exact linear algebra, and pytest.

Must not:
    Treat generic matrix fixtures as physical sections or certify floating errors.

Phase 0:
    Research execution regressions only; physical metrics remain unavailable.
"""

import gzip
import json
import math
import runpy
from fractions import Fraction
from functools import cache
from pathlib import Path

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.scientific_genesis import independent_trial_cloud as module

EXECUTION = "706b323d3d1860767e916755d7b982ec2bd9cc4e6a884d064e67d29b8094b10c"


def _orthonormal(rows):
    return module.orthonormal_rows(rows, orthogonal_tolerance=1e-10,
                                  dependence_tolerance=1e-13)


@pytest.mark.parametrize("scalar_type", (Rational, Eisenstein))
def test_row_projector_matches_an_independent_exact_inverse(scalar_type):
    # Generic algebra fixtures, never used as physical input or cloud samples.
    a = Rational(2, 3) if scalar_type is Rational else OMEGA
    matrix = Matrix(((1, a, 0, 0, 1, 0), (0, 1, 1, 0, 0, 1),
                     (0, 0, 1, 1, 2, 0), (1, 0, 0, 1, 0, 2)), scalar_type=scalar_type)
    adjoint = Matrix(tuple(tuple(c.conjugate() if isinstance(c, Eisenstein) else c
                                 for c in row) for row in matrix.transpose()),
                     scalar_type=scalar_type)
    exact = adjoint @ (matrix @ adjoint).inverse() @ matrix
    rows = tuple(tuple(module.features._complex(Eisenstein.coerce(c)) for c in row)
                 for row in matrix)
    q, diagnostic = _orthonormal(rows)
    assert diagnostic["orthogonality_residual"] <= 1e-14
    assert diagnostic["row_preconditioner_is_physical_normalization"] is False
    for i in range(6):
        for j in range(6):
            discovered = sum(row[i].conjugate()*row[j] for row in q)
            expected = module.features._complex(Eisenstein.coerce(exact[i][j]))
            assert abs(discovered-expected) <= 2e-14
    change = diagnostic["row_change_of_basis"]
    transition = tuple(tuple(complex(float.fromhex(c[0]), float.fromhex(c[1])) for c in row)
                       for row in change)
    for i in range(4):
        for j in range(6):
            assert abs(sum(transition[i][k]*rows[k][j] for k in range(4))-q[i][j]) <= 2e-14


def test_explicit_invertible_fiber_change_does_not_change_full_projector():
    rows = ((1, 2, 0, 0, 1, 0), (0, 1, 1, 0, 0, 1),
            (0, 0, 1, 1, 2, 0), (1, 0, 0, 1, 0, 2))
    transition = ((2, 1, 0, 0), (0, 3, 1, 0), (0, 0, 2, 1), (0, 0, 0, 4))
    changed = tuple(tuple(sum(transition[i][k]*rows[k][j] for k in range(4))
                          for j in range(6)) for i in range(4))
    q0, _ = _orthonormal(rows)
    q1, _ = _orthonormal(changed)
    assert module.overlap(q0, q1) == pytest.approx(4)
    for i in range(6):
        for j in range(6):
            assert abs(sum(row[i].conjugate()*row[j] for row in q0)
                       -sum(row[i].conjugate()*row[j] for row in q1)) < 1e-14


@pytest.mark.parametrize("rows,error", (
    (((1, 0),)*4, ArithmeticError),
    (((0, 0),)*4, ArithmeticError),
    (((1, math.nan),)*4, ValueError),
    (((1,),)*3, ValueError),
    (((1,), (1, 2), (1,), (1,)), ValueError),
))
def test_unresolved_rank_and_invalid_rows_produce_no_fake_kernel(rows, error):
    with pytest.raises(error):
        _orthonormal(rows)


def test_missing_sample_prevents_an_admitted_subset_mean():
    # No fixture kernels are needed: unresolvedness is decided before averaging.
    samples = [{"ordinal": 0, "history": [{"level": 12,
                "kernel_status": "computed_discovery"}]},
               {"ordinal": 1, "history": [{"level": 12, "status": "unresolved"}]}]
    assert module._statistics(samples, 12) == {
        "status": "unresolved", "missing_sample_ordinals": [1], "failed_samples_dropped": False,
    }
    with pytest.raises(ValueError, match="nonempty"):
        module._statistics([], 12)


def test_small_work_cap_preserves_actual_original_streams_and_both_prefixes():
    # This is a read-only failure attack on an actual captured sample, not a redraw.
    record = module.inputs.read_inputs(expected_digest=module.INPUT_DIGEST)

    class RejectEvaluation:
        def evaluate(self, *args, **kwargs):
            pytest.fail("pending geometry must not be evaluated")

    sample = module.process_sample(record, 0, RejectEvaluation(),
                                   parameters=(Eisenstein(1), OMEGA), levels=(12, 16),
                                   max_cells=1)
    identity = module.inputs.sample_identity(record, 0)
    assert {k: sample[k] for k in identity} == identity
    assert [h["level"] for h in sample["history"]] == [12, 16]
    for h in sample["history"]:
        assert h["status"] == "unresolved"
        assert h["reason"]
        assert "kernel_rows" not in h
        expected = module.roots.refinement_address(module.inputs.address(record, 0), h["level"])
        assert h["address"] == module.draws._address_record(expected)


@pytest.mark.parametrize("count,alpha", ((0, Fraction(1, 20)), (True, Fraction(1, 20)),
                                      (1, Fraction(0)), (1, Fraction(1)), (1, 0.05)))
def test_invalid_statistical_bound_inputs_are_rejected(count, alpha):
    with pytest.raises(ValueError):
        module._ideal_statistical_bound(count, alpha)


def test_ideal_bound_uses_exact_bounded_positive_law_not_numerical_error():
    bound = module._ideal_statistical_bound(16, Fraction(1, 20))
    b = Fraction(bound["weight_upper_bound_without_pi_cubed"])
    assert Fraction(bound["ideal_mean_operator_frobenius_radius_squared"]) == 5*b*b
    assert bound["covers_discovery_numerical_error"] is False
    assert "ideal kernels" in bound["conditional_on"]


def test_missing_cloud_is_neither_resampled_nor_evaluated(tmp_path, monkeypatch):
    monkeypatch.setattr(module.inputs.os, "getrandom", lambda n: pytest.fail("new bits"))
    monkeypatch.setattr(module.features, "compile_features", lambda: pytest.fail("recompile"))
    with pytest.raises(FileNotFoundError):
        module.read_cloud(expected_digest="0"*64, path=tmp_path / "missing.json")


def test_sample_archive_installation_is_immutable_and_deterministic(tmp_path):
    # IO fixture, not a physical kernel or entropy input.
    record = {"fixture": "archive identity"}
    first, second = tmp_path / "first.gz", tmp_path / "second.gz"
    module._install_sample(first, record)
    module._install_sample(second, record)
    before = first.read_bytes()
    assert before == second.read_bytes()
    module._install_sample(first, record)
    assert first.read_bytes() == before
    with pytest.raises((ValueError, FileExistsError)):
        module._install_sample(first, {"fixture": "replacement"})
    assert first.read_bytes() == before
    assert not list(tmp_path.glob(".cloud_sample_*"))


def test_complete_cloud_reader_is_read_only_and_checks_full_operator(monkeypatch):
    monkeypatch.setattr(module.inputs.os, "getrandom", lambda n: pytest.fail("new entropy"))
    monkeypatch.setattr(module.features, "compile_features", lambda: pytest.fail("recompile"))
    record = module.read_cloud(expected_digest=EXECUTION)
    assert record["component_counts"] == {"A": 12, "Bx": 1, "Bu": 3}
    assert len(record["same_sample_refinement_diagnostics"]) == 16
    assert record["global_trial_operator_estimate_available"] is True
    assert record["conditional_independent_cloud_available"] is True
    assert record["entropy_assumption_status"] == "ASSUMED"
    for s in record["global_statistics"].values():
        assert s["sample_count"] == s["kernel_count"] == 16
        assert s["sample_operator_rank_upper_bound"] == 64
        assert s["minimum_samples_necessary_for_invertibility"] == 1337
        assert s["full_sample_operator_invertibility_possible_by_rank"] is False
        assert len(s["full_operator_diagonal_without_pi_cubed"]) == 5345
        assert math.fsum(s["full_operator_diagonal_without_pi_cubed"]) == pytest.approx(
            s["global_operator_trace_without_pi_cubed"], rel=1e-14,
        )
        assert s["global_operator_trace_without_pi_cubed"] == pytest.approx(
            4*s["mean_quotient_weight_without_pi_cubed"], rel=1e-14,
        )


@pytest.mark.parametrize("key", (
    "randomness_certificate_available", "numerical_error_bound_certified",
    "input_radii_propagated_into_kernel", "failed_samples_dropped", "controlled_integral_available",
    "nonunit_h_iteration_executed", "ricci_flat_or_hym_metric_available",
    "physical_yukawas_available", "common_stabilized_vacuum_available", "observations_used",
))
def test_rehashed_cloud_cannot_inflate_scientific_scope(key, tmp_path):
    record = json.loads(module.OUTPUT.read_bytes())
    record.pop("artifact_digest")
    record[key] = True
    digest = module.inputs._digest(record)
    path = tmp_path / "inflated.json"
    path.write_bytes(module.inputs._canonical({**record, "artifact_digest": digest}))
    with pytest.raises(ValueError, match="trusted integration cloud"):
        module.read_cloud(expected_digest=EXECUTION, path=path)
    with pytest.raises(ValueError, match="uncertified trial execution"):
        module.read_cloud(expected_digest=digest, path=path)


@cache
def _independent_witness_helpers():
    # Reuse the independent stdlib Fraction-pair oracle, not the sparse evaluator.
    return runpy.run_path(str(Path(__file__).with_name(
        "test_scientific_genesis_compiled_section_features.py"
    )))


@pytest.mark.parametrize("ordinal", (0, 2, 3))
def test_new_actual_sample_columns_match_exact_center_oracle_and_bounds(ordinal):
    # These original ordinals span A/Bx/Bu. This is test coverage, not a
    # conditioned integration subset: the experiment retains all sixteen samples.
    record = module.inputs.read_inputs(expected_digest=module.INPUT_DIGEST)
    sample = json.loads(gzip.decompress(module._checkpoint_path(ordinal).read_bytes()))
    frames = module.draws.declared_policy()
    available = module.inputs.address(record, ordinal)
    admission = None
    for level in (12, 16):
        address = module.roots.refinement_address(available, level)
        policy, work = module.roots.refinement_policy(level, first_frame=frames.first,
                                                    second_frame=frames.second)
        frame_policy = module.continuation.FramePolicy((0, 0, 0), (0, 2), (0, 1, 2),
                                                       8*level, Eisenstein(1), 9)
        work["max_cells"] = 65536
        if admission is None:
            draw = module.roots.attempt_subdivision_draw(address, policy, **work)
            admission = module.continuation.admit_frame(draw, frame_policy)
        else:
            admission = module.continuation.refine_frame(admission, address, policy,
                                                        frame_policy, **work)
    assert isinstance(admission, module.continuation.AdmittedFrame)
    final = sample["history"][-1]
    assert module._history(admission, 16) == {
        k: v for k, v in final.items() if k not in (
            "kernel_status", "kernel_rows", "weight_midpoint_without_pi_cubed",
            "kernel_diagnostics", "complete_original_sections_consumed", "floating_mantissa_bits",
        )
    }
    q = module._decode_rows(final["kernel_rows"])
    assert max(abs(module._dot(a, b)-int(i == j)) for i, a in enumerate(q)
               for j, b in enumerate(q)) < 1e-14
    assert final["root_parent_retained"] is True
    assert final["frame_parent_retained"] is True
    helpers = _independent_witness_helpers()
    transition = tuple(tuple(complex(float.fromhex(c[0]), float.fromhex(c[1])) for c in row)
                       for row in final["kernel_diagnostics"]["row_change_of_basis"])
    signature = module.features._sources()[0]
    eta = (1, 1, module.features._complex(OMEGA))
    for index, column in helpers["_records"]().items():
        witness = helpers["_independent_center_columns"](column, admission.frame)
        bounded = module.features.exact.parse_column(column, index=index, chart=(0, 0, 0),
                                                    source_signature=signature).evaluate(
            admission.frame, source_signature=signature,
        )
        for m in range(3):
            for i in range(4):
                enclosure = bounded[m][i][0]
                assert abs(witness[m][i]-module.features._complex(enclosure.center)) <= (
                    float(enclosure.radius)+1e-10*max(1, abs(witness[m][i]))
                )
        section = tuple(sum(witness[m][i]*eta[m] for m in range(3)) for i in range(4))
        for i in range(4):
            expected = sum(transition[i][j]*section[j] for j in range(4))
            assert abs(q[i][index]-expected) < 1e-10*max(1, abs(expected))
