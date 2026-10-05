"""Verify numerical inverse-step algebra against independent exact fixtures.

Owns:
    Exact rational and Eisenstein oracle comparisons, full-coordinate actions,
    explicit scalar conventions, immutable factors and failed admission gates.

Depends on:
    The research discovery solver, exact matrix/scalar mathematics, and pytest.

Must not:
    Treat algebra fixtures as carrier sections, infer statistical confidence,
    or claim that a finite-cloud numerical residual establishes HYM convergence.

Phase 0:
    Mathematical algorithm tests only; physical metrics remain unavailable.
"""

from dataclasses import FrozenInstanceError
from fractions import Fraction

import numpy as np
import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.scientific_genesis import balanced_trial_iteration as module


def _numeric(matrix):
    def value(c):
        if isinstance(c, Eisenstein):
            return complex(float(c.a - c.b / 2), float(c.b) * np.sqrt(3) / 2)
        return complex(float(c))

    return np.array([[value(c) for c in row] for row in matrix])


def _solve(operator, weight, *, rank=1, count=2):
    return module.inverse_step(
        operator,
        mean_weight=weight,
        fiber_rank=rank,
        sample_count=count,
        basis_digest="generic-algebra-oracle",
        minimum_reciprocal_condition=1e-12,
        maximum_inverse_residual=1e-10,
    )


def _operator(samples, n, rank):
    return module.unit_operator(
        iter(samples),
        sample_count=len(samples),
        section_count=n,
        fiber_rank=rank,
        block_size=1,
        maximum_hermitian_residual=1e-12,
    )


@pytest.mark.parametrize("field", (Rational, Eisenstein))
def test_full_inverse_matches_independent_exact_oracle(field):
    if field is Rational:
        rows = (np.array([[1, 1]]), np.array([[1, -1]]))
        exact = Matrix(((1, Rational(-1, 2)), (Rational(-1, 2), 1)))
        weights = (1.0, 3.0)
    else:
        rows = tuple(_numeric(Matrix(((1, c),), scalar_type=Eisenstein)) for c in (OMEGA, OMEGA**2))
        exact = Matrix(
            ((3, OMEGA + 2 * OMEGA**2), (OMEGA**2 + 2 * OMEGA, 3)), scalar_type=Eisenstein
        ) * Rational(1, 4)
        weights = (1.0, 2.0)
    samples = tuple((f"generic-{i}", rows[i], weights[i]) for i in range(2))
    operator, mean, evidence = _operator(samples, 2, 1)
    np.testing.assert_allclose(operator, _numeric(exact), atol=1e-14, rtol=1e-14)
    result = _solve(operator, mean)
    assert result["status"] == "computed_discovery"
    factor = result["factor"]
    expected = exact.inverse() * Rational(mean / 2)
    actual = factor.apply(np.eye(2), basis_digest="generic-algebra-oracle")
    np.testing.assert_allclose(actual, _numeric(expected), atol=1e-14, rtol=1e-14)
    np.testing.assert_allclose(
        factor.fiber_gram(rows[0], basis_digest="generic-algebra-oracle"),
        rows[0] @ _numeric(expected) @ rows[0].conj().T,
        atol=1e-14,
        rtol=1e-14,
    )
    assert factor.coefficient == mean / 2
    assert evidence["ideal_reference_trace"] == str(mean)
    assert evidence["all_original_samples_consumed"] is True
    for flag in (
        "solver_equilibration_is_physical_normalization",
        "reduced_section_basis_used",
        "ridge_or_pseudoinverse_used",
        "numerical_error_bound_certified",
        "sampling_error_bound_useful",
        "controlled_integral_available",
        "ricci_flat_or_hym_metric_available",
        "physical_yukawas_available",
    ):
        assert result[flag] is False


def test_rank_factor_is_explicit_and_all_coordinates_survive():
    first = np.array([[1, 0, 1, 0], [0, 1, 0, 1]])
    second = np.array([[1, 0, -1, 0], [0, 1, 0, -1]])
    operator, mean, evidence = _operator(
        (("generic-0", first, 1.0), ("generic-1", second, 3.0)), 4, 2
    )
    result = _solve(operator, mean, rank=2)
    assert result["status"] == "computed_discovery"
    assert result["factor"].section_count == 4
    assert result["factor"].coefficient == Fraction(1)
    assert evidence["ideal_reference_trace"] == "4"
    expected = np.array([[4, 0, 2, 0], [0, 4, 0, 2], [2, 0, 4, 0], [0, 2, 0, 4]]) / 3
    np.testing.assert_allclose(
        result["factor"].apply(np.eye(4), basis_digest="generic-algebra-oracle"),
        expected,
        atol=1e-14,
    )


def test_common_weight_scale_cancels_without_inserting_a_physical_volume():
    samples = (("generic-0", np.array([[1, 1]]), 1.0), ("generic-1", np.array([[1, -1]]), 3.0))
    operator, mean, _ = _operator(samples, 2, 1)
    first = _solve(operator, mean)["factor"]
    second = _solve(operator * 9, mean * 9)["factor"]
    np.testing.assert_allclose(
        first.apply(np.eye(2), basis_digest=first.basis_digest),
        second.apply(np.eye(2), basis_digest=second.basis_digest),
        rtol=1e-14,
        atol=1e-14,
    )


def test_solver_equilibration_does_not_change_the_original_form():
    operator = np.diag([1.0, 1e-24]).astype(np.complex128)
    result = _solve(operator, Fraction(1))
    assert result["status"] == "computed_discovery"
    assert result["original_diagonal_ratio_discovery"] > 1e23
    assert result["equilibrated_reciprocal_condition_estimate"] == 1
    factor = result["factor"]
    expected = np.diag([0.5, 0.5e24])
    np.testing.assert_allclose(
        factor.apply(np.eye(2), basis_digest=factor.basis_digest), expected, rtol=1e-14
    )
    with pytest.raises(ValueError, match="original named"):
        factor.apply(np.ones(2), basis_digest="a-reduced-or-renamed-space")
    with pytest.raises(ValueError, match="original section"):
        factor.apply(np.ones(1), basis_digest=factor.basis_digest)
    with pytest.raises(FrozenInstanceError):
        factor.basis_digest = "changed"
    with pytest.raises(ValueError):
        factor.lower.setflags(write=True)
    with pytest.raises(ValueError):
        factor.diagonal[0] = 100


@pytest.mark.parametrize(
    "operator,rank,count,reason",
    (
        (np.eye(3), 1, 2, "rank bound"),
        (np.diag([1.0, 0.0]), 1, 2, "coordinate"),
        (np.ones((2, 2)), 1, 2, "Cholesky"),
        (np.array([[1.0, 2.0], [2.0, 1.0]]), 1, 2, "Cholesky"),
        (np.array([[1.0, 1 - 1e-14], [1 - 1e-14, 1.0]]), 1, 2, "conditioning"),
    ),
)
def test_unresolved_global_operator_never_manufactures_an_update(operator, rank, count, reason):
    result = _solve(operator.astype(np.complex128), Fraction(1), rank=rank, count=count)
    assert result["status"] == "unresolved"
    assert reason in result["reason"]
    assert "factor" not in result
    assert result["nonunit_h_iteration_executed"] is False
    assert result["ridge_or_pseudoinverse_used"] is False


def test_partial_or_duplicate_samples_do_not_produce_a_global_mean():
    row = np.array([[1, 1]])
    for samples in ((("generic-0", row, 1.0),), (("generic-0", row, 1.0), ("generic-0", row, 1.0))):
        with pytest.raises(ValueError):
            module.unit_operator(
                iter(samples),
                sample_count=2,
                section_count=2,
                fiber_rank=1,
                block_size=1,
                maximum_hermitian_residual=1e-12,
            )


def test_positive_weight_underflow_is_not_a_silent_zero_sample():
    with pytest.raises(ArithmeticError, match="underflow"):
        _operator(
            (
                ("generic-0", np.array([[1, 0]]), float.fromhex("0x0.0000000000001p-1022")),
                ("generic-1", np.array([[0, 1]]), 1.0),
            ),
            2,
            1,
        )


def test_failed_inverse_residual_does_not_supply_a_form(monkeypatch):
    monkeypatch.setattr(module, "cho_solve", lambda *a, **kw: np.zeros((2, 2)))
    result = _solve(np.eye(2, dtype=np.complex128), Fraction(1))
    assert result["status"] == "unresolved"
    assert "residual" in result["reason"]
    assert result["equilibrated_inverse_residual_infinity_norm"] == 1
    assert result["positive_full_basis_form_available"] is False
    assert "factor" not in result


def test_positive_projective_scale_cannot_silently_underflow():
    result = _solve(np.eye(2, dtype=np.complex128), Fraction(1, 10**400))
    assert result["status"] == "unresolved"
    assert "scale" in result["reason"]
    assert result["inverse_step_executed"] is False
    assert "factor" not in result


def test_full_cloud_calculation_refuses_incomplete_population_before_allocating(monkeypatch):
    monkeypatch.setattr(module, "read_request", lambda **kw: {"cloud_request_digest": "scheduler"})
    monkeypatch.setattr(
        module.full,
        "read_cloud",
        lambda **kw: {
            "complete_original_workload_available": False,
        },
    )

    def unavailable(*a, **kw):
        raise AssertionError("incomplete cloud must not be summed or inverted")

    monkeypatch.setattr(module, "unit_operator", unavailable)
    monkeypatch.setattr(module, "inverse_step", unavailable)
    with pytest.raises(ValueError, match="training and validation"):
        module.run_full_cloud(
            expected_request_digest="scheduler", expected_cloud_digest="scheduler"
        )


def test_array_artifacts_are_deterministic_non_pickle_and_immutable(tmp_path, monkeypatch):
    # Small exact-algebra oracle only; never a carrier output.
    monkeypatch.setattr(module, "ROOT", tmp_path)
    path = tmp_path / "generic-algebra.npy"
    array = np.array([[1, 2j], [-2j, 5]], dtype=np.complex128)
    first = module._install_array(path, array, "<c16")
    assert module._install_array(path, array, "<c16") == first
    assert first["numpy_pickle_used"] is False
    np.testing.assert_array_equal(np.load(path, allow_pickle=False), array)
    with pytest.raises(FileExistsError, match="preserve"):
        module._install_array(path, array * 2, "<c16")
    assert not tuple(tmp_path.glob(".balanced-array-*"))


def _request(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "REQUEST", tmp_path / "policy.json")
    return module.create_request(
        expected_cloud_request_digest=(
            "9e13a565bc13a2bd27320e5746d3fbf2104c3290f8792efc97d8d3316bc8a5b5"
        ),
        block_size=16,
        maximum_hermitian_residual=1e-12,
        minimum_reciprocal_condition=1e-12,
        maximum_inverse_residual=1e-6,
    )


def test_inverse_policy_is_predeclared_without_geometry_or_entropy(tmp_path, monkeypatch):
    def unavailable(*a, **kw):
        raise AssertionError("policy inspection cannot redraw or solve")

    monkeypatch.setattr(module.full.cloud.inputs, "create_inputs", unavailable)
    monkeypatch.setattr(module, "unit_operator", unavailable)
    monkeypatch.setattr(module, "inverse_step", unavailable)
    record = _request(tmp_path, monkeypatch)
    assert (
        module.read_request(expected_digest=record["artifact_digest"], path=module.REQUEST)
        == record
    )
    assert record["training_count"] == 1536
    assert record["validation_count"] == 512
    assert record["update_count"] == 1
    with pytest.raises(FileExistsError):
        _request(tmp_path, monkeypatch)


@pytest.mark.parametrize(
    "key,value",
    (
        ("training_count", 1337),
        ("required_population", "admitted subset"),
        ("initial_form", "fitted diagonal metric"),
        ("observations_used", True),
        ("parameter_point_status", "DERIVED"),
        ("entropy_assumption_status", "PROVED"),
        ("source_files_sha256", {}),
        ("projective_scale_convention", "canonical physical normalization"),
    ),
)
def test_rehashed_inverse_request_cannot_inflate_scope_or_change_population(
    key,
    value,
    tmp_path,
    monkeypatch,
):
    record = _request(tmp_path, monkeypatch)
    record[key] = value
    record.pop("artifact_digest")
    record["artifact_digest"] = module.full.cloud.inputs._digest(record)
    attacked = tmp_path / "attacked.json"
    module.full._install_json(attacked, record)
    with pytest.raises(ValueError, match="population, policy or scientific scope"):
        module.read_request(expected_digest=record["artifact_digest"], path=attacked)
