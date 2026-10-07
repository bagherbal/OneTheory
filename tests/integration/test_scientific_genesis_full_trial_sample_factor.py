"""Verify complete sample-factor diagnostics against independent exact algebra.

Owns:
    Rational and Eisenstein Gram oracles, full coordinate retention, bounded
    reconstruction blocks, input preservation and diagnostic-only boundaries.

Depends on:
    Exact production scalar/matrix machinery, the research sample-factor
    algorithm, NumPy and pytest; no physical test samples are invented.

Must not:
    Interpret these mathematical fixtures as carrier data, prove sample rank
    from floating pivots or export a metric from a diagnostic factor.

Phase 0:
    Numerical algorithm checks only; the actual physical metric stays unavailable.
"""

import numpy as np
import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.scientific_genesis import full_trial_sample_factor as module


def _numeric(matrix):
    def coefficient(value):
        if isinstance(value, Eisenstein):
            return complex(float(value.a - value.b / 2), float(value.b) * np.sqrt(3) / 2)
        return complex(float(value))

    return np.array([[coefficient(value) for value in row] for row in matrix])


@pytest.mark.parametrize("field", (Rational, Eisenstein))
@pytest.mark.parametrize("block_size", (1, 2, 7))
def test_full_factor_matches_exact_gram_without_mutating_input(field, block_size):
    phase = Rational(1, 2) if field is Rational else OMEGA
    exact = Matrix(((1, phase), (0, 1), (1, 0)), scalar_type=field)
    adjoint = Matrix(
        tuple(
            tuple(value.conjugate() if isinstance(value, Eisenstein) else value for value in column)
            for column in zip(*exact, strict=True)
        ),
        scalar_type=field,
    )
    inverse_d = Matrix(((2**20, 0), (0, Rational(1, 2**20))), scalar_type=field)
    expected = inverse_d @ adjoint @ exact @ inverse_d
    matrix = _numeric(exact)
    original = matrix.copy()
    scales = np.array([2.0**-20, 2.0**20])
    upper, record = module.factor_diagnostic(matrix, scales, block_size=block_size)
    np.testing.assert_array_equal(matrix, original)
    np.testing.assert_allclose(upper.conj().T @ upper, _numeric(expected), rtol=1e-13, atol=1e-13)
    assert upper.shape == (2, 2)
    assert np.all(np.tril(upper, -1) == 0)
    assert record["sample_factor_shape"] == [3, 2]
    assert record["upper_factor_shape"] == [2, 2]
    assert record["reconstruction_columns_checked"] == 2
    assert record["reconstruction_block_size"] == block_size
    assert record["original_column_order_retained"] is True
    assert record["pivoting_used"] is False
    assert record["qr_relative_reconstruction_residual_discovery"] < 1e-13
    assert 0 < record["triangular_reciprocal_condition_estimate_one_norm"] <= 1


@pytest.mark.parametrize(
    "matrix, scales, block",
    (
        (np.zeros((0, 0)), np.zeros(0), 1),
        (np.ones((1, 2)), np.ones(2), 1),
        (np.array([1, 2]), np.ones(2), 1),
        (np.ones((3, 2)), np.ones(1), 1),
        (np.array([[np.inf], [1]]), np.ones(1), 1),
        (np.array([[np.nan], [1]]), np.ones(1), 1),
        (np.ones((3, 2)), np.array([1, 0]), 1),
        (np.ones((3, 2)), np.array([1, -1]), 1),
        (np.ones((3, 2)), np.array([1, np.inf]), 1),
        (np.ones((3, 2)), np.array([1, np.nan]), 1),
        (np.ones((3, 2)), np.ones(2), True),
        (np.ones((3, 2)), np.ones(2), 0),
        (np.ones((3, 2)), np.ones(2), 1.5),
    ),
)
def test_invalid_factor_policy_does_not_produce_a_condition_estimate(matrix, scales, block):
    with pytest.raises(ValueError):
        module.factor_diagnostic(matrix, scales, block_size=block)


def test_duplicate_columns_remain_in_the_full_diagnostic_not_a_reduced_basis():
    matrix = np.array([[1, 1], [2, 2], [3, 3]], dtype=complex)
    upper, record = module.factor_diagnostic(matrix, np.ones(2), block_size=1)
    assert upper.shape == (2, 2)
    assert record["reconstruction_columns_checked"] == 2
    assert record["triangular_reciprocal_condition_estimate_one_norm"] < 1e-14
    assert record["original_column_order_retained"] is True
    assert "positive_full_basis_form_available" not in record
    assert "factor" not in record


def test_existing_output_cannot_trigger_entropy_geometry_or_replacement(tmp_path, monkeypatch):
    output = tmp_path / "existing.json"
    output.write_text("retained mathematical fixture", encoding="utf-8")
    monkeypatch.setattr(module, "OUTPUT", output)
    monkeypatch.setattr(module.inverse, "read_step", lambda **kwargs: pytest.fail("no replay"))
    with pytest.raises(FileExistsError, match="preserve"):
        module.run(expected_request_digest="unused", expected_step_digest="unused", block_size=64)


@pytest.mark.parametrize("block", (True, 0, -1, 1.5))
def test_invalid_runtime_policy_fails_before_consuming_any_cloud(block, tmp_path, monkeypatch):
    monkeypatch.setattr(module, "OUTPUT", tmp_path / "missing.json")
    monkeypatch.setattr(module.inverse, "read_step", lambda **kwargs: pytest.fail("no cloud read"))
    with pytest.raises(ValueError, match="block size"):
        module.run(
            expected_request_digest="unused", expected_step_digest="unused", block_size=block
        )
