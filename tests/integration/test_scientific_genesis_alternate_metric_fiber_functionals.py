"""Attack transposed evaluation with original section data and full Gaussian quotients.

Owns:
    Archive equality, exact functional linearity, uncertain-zero retention,
    full corrected-cochain checks and fixed-frame/channel cache separation.

Depends on:
    The existing certified frame fixtures, original full cochain constructor,
    independent raw-arrow quotient checks and the transposed research evaluator.

Must not:
    Infer geometric samples from arithmetic witnesses, unit closedness from
    linearity, completed matrices from probes, or physical metric convergence.

Phase 0:
    Research functional verification only; integration and normalization are open.
"""

import gzip
import json
from functools import cache

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.scientific_genesis import alternate_metric_fiber_functionals as module
from tests.integration.test_scientific_genesis_alternate_metric_bounded_support import (
    exact_engine,
)
from tests.integration.test_scientific_genesis_uncertain_cover_frames import (
    _contains,
    _dehomogenized_coefficients,
    _full_boundary,
    _functional,
    _specialize,
)


@cache
def _exact():
    return module.FunctionalEvaluator(exact_engine.__wrapped__().frame)


@pytest.mark.parametrize("index", (0, 1273, 2655, 3790, 5344))
def test_exact_columns_match_independent_original_point_archive(index):
    columns = json.loads(gzip.decompress(module.original.support.regular.MATRIX.read_bytes()))
    actual = _exact().evaluate_basis(index)
    assert [[str(c.center) for row in m for c in row] for m in actual] == (
        [[row[0] for row in m] for m in columns[index]])
    assert all(c.radius == 0 for m in actual for row in m for c in row)


@pytest.mark.parametrize("power", (0, 1, 2))
def test_linear_functional_on_nonclosed_units_preserves_uncertain_zeros(power):
    evaluator = _exact()
    _, streams, _ = module.original.fiber.lifts._inputs()
    candidates = tuple(evaluator._encoded_residual(
        power, 0, (obj, tuple(m[:3]), tuple(m[6:]), chart),
    ) for obj, m, chart, _ in streams[1][0]["terms"])
    for zero in (c for c in candidates if c.is_zero()):
        assert evaluator._apply_residual(power, zero) == ((evaluator.scalar(0),),) * 2
    # Choose a nonzero arithmetic input from the actual source, not a physical
    # point or basis change. Zero-coordinate vanishing is a valid separate case.
    encoded = next(c for c in candidates if not c.is_zero())
    # Unit closure is not an assumption. Compare the exact finite functional
    # on the whole input with its linear extension from the unit columns.
    assert evaluator._apply_residual(power, encoded) == (
        evaluator._residual_functional(power, encoded))
    before = len(evaluator.functional_values)
    assert evaluator._apply_residual(power, encoded.scale(Eisenstein(2, 3))) == (
        tuple(tuple(c * Eisenstein(2, 3) for c in row)
              for row in evaluator._residual_functional(power, encoded)))
    assert len(evaluator.functional_values) == before
    b = encoded.terms[0][0]
    uncertain = module.original.BoundedCoefficients((
        (b, module.original.bounds.Ball(Eisenstein(0), Rational(1, 1024), 80)),
    ), bits=80)
    assert not uncertain.is_zero()
    enclosed = evaluator._apply_residual(power, uncertain)
    assert any(c.radius for row in enclosed for c in row) or all(
        c.center.is_zero() for row in enclosed for c in row)
    for direction in (Eisenstein(1), OMEGA):
        functional = module.original.BoundedCoefficients((
            (b, module.original.bounds.Ball(Eisenstein(Rational(1, 1024)) * direction, 0, 80)),
        ), bits=80)
        expected = evaluator._residual_functional(power, functional)
        assert all(ball.contains(c.center) for row, other in zip(enclosed, expected, strict=True)
                   for ball, c in zip(row, other, strict=True))


@pytest.mark.parametrize("domain_index", (0, 9, 12))
def test_each_native_mixture_component_contains_independent_full_corrected_cochains(domain_index):
    _, _, frame = module.domains.declared_frames()[domain_index]
    section = module.domains.original_section(2655)
    coefficients = module.FunctionalEvaluator(frame).evaluate_basis(2655)
    contexts = (module.original.fiber.lifts.first._context()[0],
                module.original.fiber.lifts.second._context()[0])
    for offset in (0, 1):
        values = _functional(frame, offset)
        constant = (_dehomogenized_coefficients(section.first_constant, values,
                                                frame.point, contexts[0])
                    + _dehomogenized_coefficients(section.second_constant, values,
                                                  frame.point, contexts[1]))
        corrections = tuple(_dehomogenized_coefficients(c, values, frame.point, contexts[0])
                            + (Eisenstein(0),) * 5 for c in section.first_coefficients)
        for a0, a1 in ((Eisenstein(1), OMEGA), (OMEGA, Eisenstein(2, -1))):
            _, quotient = _full_boundary(values, frame, a0, a1)
            column = Matrix(tuple((c + a0*x + a1*y,) for c, x, y in zip(
                constant, *corrections, strict=True)), scalar_type=Eisenstein)
            _contains(_specialize(coefficients, a0, a1), quotient.matmul(column))


@pytest.mark.parametrize("invalid", (-1, 3, True, 0.0))
def test_channels_cannot_be_aliased_or_silently_changed(invalid):
    with pytest.raises(ValueError, match="degree-one"):
        _exact()._apply_residual(invalid, module.original.BoundedCoefficients(bits=80))


def test_original_basis_order_and_frame_type_still_fail_closed():
    for invalid in (-1, 5345, True, 0.0):
        with pytest.raises(ValueError, match="basis index"):
            _exact().evaluate_basis(invalid)
    with pytest.raises(TypeError, match="bounded fiber frame"):
        module.FunctionalEvaluator(object())


def test_completed_new_domain_is_full_original_basis_not_sampling_or_metrics():
    record = module.verify_completed_domain(expected_digest=module.EXECUTION_DIGEST)
    assert record["section_count"] == 5345
    assert record["functional_unit_count"] == 39087
    assert record["original_unit_residual_key_count"] == 11832
    assert record["complete_5345_column_matrix_on_declared_new_domain_available"] is True
    assert record["all_15_domains_executed"] is False
    assert record["individual_units_asserted_closed"] is False
    assert record["practical_multi_point_throughput_certified"] is False
    assert record["independent_cloud_available"] is False
    assert record["controlled_integral_available"] is False
    assert record["physical_yukawas_available"] is False


@pytest.mark.parametrize("field", (
    "parameter_order", "fiber_basis_labels", "normalized_cover_bounds", "root_pair",
    "matrix_archive_sha256", "section_count", "proof_sha256", "domain_role",
    "all_15_domains_executed", "individual_units_asserted_closed",
    "practical_multi_point_throughput_certified", "controlled_integral_available",
    "physical_yukawas_available", "observations_used",
))
def test_rehashed_completed_output_cannot_change_the_trusted_execution(
    field, tmp_path, monkeypatch,
):
    record = json.loads(module.OUTPUT.read_text())
    value = record[field]
    record[field] = not value if type(value) is bool else "changed"
    record.pop("artifact_digest")
    record["artifact_digest"] = module.hashlib.sha256(module.archive._canonical(record)).hexdigest()
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(record))
    monkeypatch.setattr(module, "OUTPUT", path)
    with pytest.raises(ValueError, match="trusted digest"):
        module.verify_completed_domain(expected_digest=module.EXECUTION_DIGEST)


def test_changed_stream_and_proof_cannot_hide_behind_cached_frames(monkeypatch):
    module.domains.declared_frames()
    original_digest = module.archive._file_digest
    with monkeypatch.context() as attack:
        attack.setattr(module.archive, "_file_digest",
                       lambda path: "0" * 64 if path == module.MATRIX else original_digest(path))
        with pytest.raises(ValueError, match="scientific scope"):
            module.verify_completed_domain(expected_digest=module.EXECUTION_DIGEST)
    original_bytes = module.Path.read_bytes
    monkeypatch.setattr(module.Path, "read_bytes", lambda path: original_bytes(path) + b"changed"
                        if path == module.PROOF else original_bytes(path))
    with pytest.raises(ValueError, match="scientific scope"):
        module.verify_completed_domain(expected_digest=module.EXECUTION_DIGEST)
