"""Attack finite-measure balance conditions with independent exact algebra.

Owns:
    Atomic necessary-condition, interval and scale tests, complete-coordinate
    H1 projector oracles, invalid-input and unresolved numerical-gate checks.

Depends on:
    The research finite-cloud diagnostic, Rational and Eisenstein exact matrix
    mathematics, NumPy and pytest for algorithm comparisons only.

Must not:
    Relabel fixtures as carrier data or finite-cloud imbalance as HYM failure.

Phase 0:
    Generic mathematical algorithm tests only; physical metrics remain absent.
"""

from fractions import Fraction

import numpy as np
import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.scientific_genesis import finite_cloud_balance as module


def test_exact_atomic_obstruction_does_not_require_a_numerical_eigenvalue():
    weights = ((0, Fraction(1), Fraction(1), Fraction(2)),
               (1, Fraction(3), Fraction(3), Fraction(4)))
    record = module.atomic_bound(weights, section_count=4, fiber_rank=1)
    assert record["atomic_multiplier_lower_exact"] == "2"
    assert record["atomic_multiplier_reference_exact"] == "3"
    assert record["operator_norm_balance_residual_lower_exact"] == "1"
    assert record["trace_normalized_frobenius_residual_squared_lower_exact"] == "1/4"
    assert record["balanced_fixed_point_excluded_on_retained_intervals"] is True
    assert record["condition_is_sufficient_for_balance"] is False
    assert record["witness_ordinal"] == 1


def test_wide_intervals_do_not_inherit_the_reference_obstruction():
    record = module.atomic_bound(
        ((0, Fraction(1), Fraction(1), Fraction(4)),
         (1, Fraction(1), Fraction(3), Fraction(4))), section_count=4, fiber_rank=1,
    )
    assert record["atomic_multiplier_lower_exact"] == "1/2"
    assert record["atomic_multiplier_reference_exact"] == "3"
    assert record["balanced_fixed_point_excluded_on_retained_intervals"] is False
    assert record["balanced_fixed_point_excluded_for_reference_weights"] is True
    assert record["operator_norm_balance_residual_lower_exact"] == "0"


def test_atomic_equality_and_rank_floor_are_only_necessary_conditions():
    equal = tuple((i, Fraction(1), Fraction(1), Fraction(1)) for i in range(4))
    record = module.atomic_bound(equal, section_count=4, fiber_rank=1)
    assert record["atomic_multiplier_lower_exact"] == "1"
    assert record["balanced_fixed_point_excluded_on_retained_intervals"] is False
    assert record["condition_is_sufficient_for_balance"] is False
    deficient = module.atomic_bound(equal[:2], section_count=4, fiber_rank=1)
    assert deficient["finite_sample_rank_upper_bound"] == 2
    assert deficient["balanced_fixed_point_excluded_on_retained_intervals"] is True


def test_exact_projector_sum_exhibits_the_atomic_operator_bound():
    """A spanning sample can still have no balanced finite-measure form."""

    first = Matrix(((1, 0, 0, 0), (0, 1, 0, 0)))
    second = Matrix(((0, 0, 1, 0), (0, 0, 0, 1)))
    operator = (first.transpose() * first * 3 + second.transpose() * second) * Rational(1, 2)
    residual = operator - Matrix.identity(4)
    assert residual.rows == (
        (Rational(1, 2), Rational(0), Rational(0), Rational(0)),
        (Rational(0), Rational(1, 2), Rational(0), Rational(0)),
        (Rational(0), Rational(0), Rational(-1, 2), Rational(0)),
        (Rational(0), Rational(0), Rational(0), Rational(-1, 2)),
    )
    record = module.atomic_bound(
        ((0, Fraction(3), Fraction(3), Fraction(3)),
         (1, Fraction(1), Fraction(1), Fraction(1))), section_count=4, fiber_rank=2,
    )
    assert record["finite_sample_rank_upper_bound"] == 4
    assert record["atomic_multiplier_lower_exact"] == "3/2"
    assert record["operator_norm_balance_residual_lower_exact"] == "1/2"
    assert record["trace_normalized_frobenius_residual_squared_lower_exact"] == "1/8"


@pytest.mark.parametrize("scale", (Fraction(9), Fraction(1, 10**500)))
def test_weight_scale_cancels_exactly_even_below_floating_range(scale):
    weights = ((0, Fraction(1), Fraction(1), Fraction(1)),
               (1, Fraction(3), Fraction(3), Fraction(3)))
    first = module.atomic_bound(weights, section_count=2, fiber_rank=1)
    scaled = tuple((i, lo * scale, mid * scale, hi * scale) for i, lo, mid, hi in weights)
    second = module.atomic_bound(scaled, section_count=2, fiber_rank=1)
    for key in ("atomic_multiplier_lower_exact", "operator_norm_balance_residual_lower_exact",
                "trace_normalized_frobenius_residual_squared_lower_exact"):
        assert first[key] == second[key]


@pytest.mark.parametrize("count,rank", ((0, 1), (3, 0), (2, 3), (True, 1), (2, True), (2.0, 1)))
def test_invalid_dimensions_cannot_define_an_atomic_balance_condition(count, rank):
    with pytest.raises(ValueError):
        module.atomic_bound(((0, Fraction(1), Fraction(1), Fraction(1)),),
                            section_count=count, fiber_rank=rank)


@pytest.mark.parametrize("weights", (
    (), ((0, Fraction(1), Fraction(1)),),
    ((0, Fraction(0), Fraction(1), Fraction(1)),),
    ((0, Fraction(2), Fraction(1), Fraction(3)),),
    ((0, Fraction(1), Fraction(4), Fraction(3)),),
    ((True, Fraction(1), Fraction(1), Fraction(1)),),
    ((0, Fraction(1), Fraction(1), Fraction(1)),) * 2,
))
def test_invalid_or_duplicate_atomic_weights_are_rejected(weights):
    with pytest.raises(ValueError):
        module.atomic_bound(weights, section_count=2, fiber_rank=1)


@pytest.mark.parametrize("value", (1, 1.0, True, "1"))
def test_exact_weight_policy_rejects_implicit_coercion(value):
    with pytest.raises(TypeError):
        module.atomic_bound(((0, value, Fraction(1), Fraction(1)),),
                            section_count=2, fiber_rank=1)


def _numeric(matrix):
    def value(c):
        if isinstance(c, Eisenstein):
            return complex(float(c.a - c.b / 2), float(c.b) * np.sqrt(3) / 2)
        return complex(float(c))
    return np.array([[value(c) for c in row] for row in matrix])


def _adjoint(matrix):
    return Matrix(tuple(tuple(value.conjugate() if isinstance(value, Eisenstein) else value
                              for value in row) for row in matrix),
                  scalar_type=matrix.scalar_type).transpose()


@pytest.mark.parametrize("field", (Rational, Eisenstein))
def test_full_h1_projector_agrees_with_independent_exact_field_oracle(field):
    a = Rational(2, 3) if field is Rational else OMEGA
    b = Rational(-3, 5) if field is Rational else Eisenstein(1, 2)
    lower = Matrix(((1, 0, 0), (a, 1, 0), (0, b, 1)), scalar_type=field)
    diagonal_inverse = Matrix(((Rational(1, 2), 0, 0), (0, Rational(1, 3), 0),
                               (0, 0, Rational(1, 5))), scalar_type=field)
    rows = Matrix(((1, a, 0), (0, 1, b)), scalar_type=field)
    form = module.parent.inverse.InverseForm("generic-exact-oracle", np.array([2., 3., 5.]),
                                            _numeric(lower), Fraction(4))
    transformed = rows * diagonal_inverse * _adjoint(lower).inverse() * 2
    exact_projector = (
        _adjoint(transformed) * (transformed * _adjoint(transformed)).inverse() * transformed
    )
    assert exact_projector * exact_projector == exact_projector
    assert exact_projector.rank() == 2
    original = _numeric(rows)
    snapshot = original.copy()
    whitened, record = module.projector_rows(
        form, original, basis_digest=form.basis_digest,
        minimum_condition=1e-12, maximum_residual=1e-10,
    )
    assert whitened.shape == (2, 3)
    assert record["fiber_projector_row_residual_discovery"] < 1e-12
    np.testing.assert_array_equal(snapshot, original)
    np.testing.assert_allclose(whitened.conj().T @ whitened, _numeric(exact_projector), atol=1e-13)
    np.testing.assert_allclose(whitened @ whitened.conj().T, np.eye(2), atol=1e-13)
    # Explicit invertible fiber changes must not alter the full-space projector.
    change = np.array([[2, 1], [0, 3]], dtype=np.complex128)
    other, _ = module.projector_rows(
        form, change @ original, basis_digest=form.basis_digest,
        minimum_condition=1e-12, maximum_residual=1e-10,
    )
    np.testing.assert_allclose(other.conj().T @ other, _numeric(exact_projector), atol=1e-13)


def test_h1_probe_rejects_wrong_basis_missing_columns_and_unresolved_conditioning():
    form = module.parent.inverse.InverseForm("full-oracle", np.ones(3), np.eye(3), Fraction(1))
    policy = {"basis_digest": "full-oracle", "minimum_condition": 1e-12,
              "maximum_residual": 1e-10}
    with pytest.raises(ValueError, match="original-basis"):
        module.projector_rows(form, [[1, 0]], **policy)
    with pytest.raises(ValueError, match="original-basis"):
        module.projector_rows(form, [[1, 0, 0]], **{**policy, "basis_digest": "other"})
    with pytest.raises(ArithmeticError, match="conditioning"):
        module.projector_rows(form, [[1, 0, 0], [0, 1e-9, 0]], **policy)
    with pytest.raises((ArithmeticError, np.linalg.LinAlgError)):
        module.projector_rows(form, [[1, 0, 0], [1, 0, 0]], **policy)


@pytest.mark.parametrize("value", (0.0, -1.0, 1.0, True, float("nan"), float("inf")))
def test_h1_probe_requires_explicit_finite_admission_gates(value):
    form = module.parent.inverse.InverseForm("full-oracle", np.ones(2), np.eye(2), Fraction(1))
    with pytest.raises(ValueError):
        module.projector_rows(form, [[1, 0]], basis_digest=form.basis_digest,
                              minimum_condition=value, maximum_residual=1e-10)


def test_actual_retained_weight_certificate_preserves_every_original_ordinal():
    """Actual finite weights, not algebra fixtures, supply the scoped no-go."""

    record = module.read_certificate(expected_digest=(
        "1a60352d1c7b4287621e5eb53e8b7902f7bf7f1c3bf37cce2bb1fd35e3100288"
    ))
    assert [row["ordinal"] for row in record["weights"]] == list(range(2048))
    assert (record["training"]["sample_count"], record["validation"]["sample_count"]) == (1536, 512)
    assert record["section_count"] == 5345
    assert record["training"]["witness_ordinal"] == 78
    assert Fraction(record["training"]["atomic_multiplier_lower_exact"]) > Fraction(3225, 1000)
    assert record["training"]["balanced_fixed_point_excluded_on_retained_intervals"] is True
    assert record["weight_enclosures_independently_replayed"] is False
    assert record["continuum_bundle_instability_proved"] is False
    assert record["ricci_flat_or_hym_metric_available"] is False
    assert record["physical_yukawas_available"] is False


@pytest.mark.parametrize("flag", (
    "weight_enclosures_independently_replayed", "numerical_kernel_error_bound_certified",
    "sampling_error_bound_useful", "continuum_bundle_instability_proved",
    "ricci_flat_or_hym_metric_available", "physical_yukawas_available",
    "common_stabilized_vacuum_available", "observations_used",
))
def test_recomputed_certificate_digest_does_not_admit_scope_inflation(flag, tmp_path, monkeypatch):
    record = module.read_certificate(expected_digest=(
        "1a60352d1c7b4287621e5eb53e8b7902f7bf7f1c3bf37cce2bb1fd35e3100288"
    ))
    record[flag] = True
    unsigned = {key: value for key, value in record.items() if key != "artifact_digest"}
    record["artifact_digest"] = module.full.cloud.inputs._digest(unsigned)
    path = tmp_path / "invalid-certificate.json"
    path.write_bytes(module.full.cloud.inputs._canonical(record))
    monkeypatch.setattr(module, "OUTPUT", path)
    with pytest.raises(ValueError, match="scope changed"):
        module.read_certificate(expected_digest=record["artifact_digest"])
