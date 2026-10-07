"""Verify the direct full-factor inverse law against exact mathematical oracles.

Owns:
    Complete original-coordinate inverse comparisons, explicit row phases,
    full-column residual gates and refusal of ambiguous numerical policies.

Depends on:
    Exact rational/Eisenstein matrices, the research triangular inverse,
    the frozen immutable inverse form, NumPy and pytest.

Must not:
    Treat mathematical fixtures as a carrier, alter the old Gram policy,
    hide rank loss or infer a physical normalization from a numerical form.

Phase 0:
    Algorithm verification only; physical metrics and the common vacuum stay missing.
"""

from fractions import Fraction

import numpy as np
import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.scientific_genesis import factored_trial_inverse as module


def _numeric(matrix):
    def value(coefficient):
        if isinstance(coefficient, Eisenstein):
            return complex(
                float(coefficient.a - coefficient.b / 2), float(coefficient.b) * np.sqrt(3) / 2
            )
        return complex(float(coefficient))

    return np.array([[value(coefficient) for coefficient in row] for row in matrix])


@pytest.mark.parametrize("field", (Rational, Eisenstein))
@pytest.mark.parametrize("block_size", (1, 2, 8))
def test_full_triangular_inverse_matches_exact_original_basis_oracle(field, block_size):
    off_diagonal = Rational(1, 2) if field is Rational else OMEGA
    exact_r = Matrix(((-2, off_diagonal), (0, 3)), scalar_type=field)
    adjoint = Matrix(
        tuple(
            tuple(value.conjugate() if isinstance(value, Eisenstein) else value for value in column)
            for column in zip(*exact_r, strict=True)
        ),
        scalar_type=field,
    )
    exact_d = Matrix(((Rational(1, 16), 0), (0, 16)), scalar_type=field)
    exact_operator = exact_d @ adjoint @ exact_r @ exact_d
    upper = _numeric(exact_r)
    before = upper.copy()
    lower, phases, record = module.admitted_upper(
        upper,
        minimum_reciprocal_condition=1e-12,
        maximum_triangular_inverse_residual=1e-6,
        block_size=block_size,
    )
    np.testing.assert_array_equal(upper, before)
    np.testing.assert_array_equal(phases, (-1, 1))
    np.testing.assert_allclose(lower @ lower.conj().T, _numeric(adjoint @ exact_r))
    coefficient = Fraction(7, 11)
    form = module.inverse.InverseForm(
        "exact-algebra-fixture", np.array([1 / 16, 16]), lower, coefficient
    )
    expected = exact_operator.inverse() * Rational(coefficient)
    np.testing.assert_allclose(
        form.apply(np.eye(2), basis_digest="exact-algebra-fixture"),
        _numeric(expected),
        rtol=1e-13,
        atol=1e-13,
    )
    assert record["status"] == "computed_discovery"
    assert record["inverse_check_columns"] == 2
    assert record["positive_full_basis_form_available"] is True
    assert record["inverse_step_executed"] is True
    assert record["triangular_inverse_residual_infinity_norm"] < 1e-13


@pytest.mark.parametrize(
    "upper",
    (
        np.zeros((0, 0)),
        np.ones((2, 3)),
        np.array([1, 2]),
        np.array([[1, 0], [1, 1]]),
        np.array([[0, 0], [0, 1]]),
        np.array([[1j, 0], [0, 1]]),
        np.array([[np.inf, 0], [0, 1]]),
        np.array([[np.nan, 0], [0, 1]]),
    ),
)
def test_invalid_full_factor_never_supplies_a_form(upper):
    with pytest.raises(ValueError):
        module.admitted_upper(
            upper,
            minimum_reciprocal_condition=1e-12,
            maximum_triangular_inverse_residual=1e-6,
            block_size=1,
        )


def test_unresolved_triangular_condition_exports_no_form():
    lower, _, record = module.admitted_upper(
        np.diag([1.0, 1e-20]),
        minimum_reciprocal_condition=1e-12,
        maximum_triangular_inverse_residual=1e-6,
        block_size=1,
    )
    assert lower is None
    assert record["status"] == "unresolved"
    assert record["positive_full_basis_form_available"] is False
    assert record["inverse_step_executed"] is False
    assert "conditioning" in record["reason"]


def test_inverse_residual_gate_accumulates_every_column_not_just_block_maxima(monkeypatch):
    def inaccurate_solve(upper, rhs, **kwargs):
        return rhs + 0.4

    monkeypatch.setattr(module, "solve_triangular", inaccurate_solve)
    lower, _, record = module.admitted_upper(
        np.eye(3),
        minimum_reciprocal_condition=1e-12,
        maximum_triangular_inverse_residual=0.8,
        block_size=1,
    )
    assert lower is None
    assert record["inverse_check_columns"] == 3
    assert record["triangular_inverse_residual_infinity_norm"] == pytest.approx(1.2)
    assert record["positive_full_basis_form_available"] is False
    assert "residual" in record["reason"]


@pytest.mark.parametrize("block", (True, 0, -1, 1.5))
def test_ambiguous_policy_fails_before_reading_any_original_factor(block, tmp_path, monkeypatch):
    monkeypatch.setattr(module, "REQUEST", tmp_path / "missing.json")
    monkeypatch.setattr(module, "read_factor", lambda *args: pytest.fail("no factor read"))
    with pytest.raises(ValueError):
        module.create_request(
            expected_factor_digest="unused",
            minimum_reciprocal_condition=1e-12,
            maximum_triangular_inverse_residual=1e-6,
            block_size=block,
        )


def test_original_factor_inverse_policy_cannot_be_replaced(tmp_path, monkeypatch):
    request = tmp_path / "retained.json"
    request.write_text("retained mathematical fixture", encoding="utf-8")
    monkeypatch.setattr(module, "REQUEST", request)
    monkeypatch.setattr(module, "read_factor", lambda *args: pytest.fail("no replacement"))
    with pytest.raises(FileExistsError, match="preserve"):
        module.create_request(
            expected_factor_digest="unused",
            minimum_reciprocal_condition=1e-12,
            maximum_triangular_inverse_residual=1e-6,
            block_size=128,
        )
