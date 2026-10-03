"""Attack the complete original trial kernel with independent exact arithmetic.

Owns:
    Full archived-coordinate Gaussian inverse and action checks, projection
    identities, normalization-safe global bounds and fail-closed scope regressions.

Depends on:
    Original full section archives, the trial-kernel experiment, independent
    Fraction-pair arithmetic and explicit computational parameter witnesses.

Must not:
    Treat disk centers as cover points, substitute probe bases, infer independence,
    select a vacuum or validate a trial integrand as a converged physical metric.

Phase 0:
    Kernel-prerequisite verification only; physical normalization remains open.
"""

import gzip
import json
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
from functools import cache

import pytest

from onetheory.math.numbers import Eisenstein, Rational
from research.experiments.scientific_genesis import alternate_metric_trial_kernel as trial
from tests.integration.test_scientific_genesis_alternate_section_covariance import (
    ZERO,
    _add,
    _conjugate,
    _contains,
    _full_fraction_reference,
    _multiply,
    _sum,
)

ONE = Fraction(1), Fraction(0)


def _inverse_scalar(value):
    a, b = value
    norm = a*a - a*b + b*b
    if not norm:
        raise ZeroDivisionError("independent Gaussian pivot is zero")
    return (a-b) / norm, -b / norm


def _negative(value):
    return -value[0], -value[1]


def _gaussian_inverse(matrix):
    """Use row elimination, not determinant or adjugate signs from the producer."""

    size = len(matrix)
    rows = [list(row) + [ONE if i == j else ZERO for j in range(size)]
            for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next(i for i in range(column, size) if rows[i][column] != ZERO)
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scalar = _inverse_scalar(rows[column][column])
        rows[column] = [_multiply(scalar, c) for c in rows[column]]
        for i in range(size):
            if i != column:
                factor = rows[i][column]
                rows[i] = [_add(c, _negative(_multiply(factor, p)))
                           for c, p in zip(rows[i], rows[column], strict=True)]
    assert all(rows[i][j] == (ONE if i == j else ZERO)
               for i in range(size) for j in range(size))
    return tuple(tuple(row[size:]) for row in rows)


def _matmul(left, right):
    return tuple(tuple(_sum(_multiply(a, b) for a, b in zip(row, column, strict=True))
                       for column in zip(*right, strict=True)) for row in left)


def _adjoint(matrix):
    return tuple(tuple(_conjugate(c) for c in column) for column in zip(*matrix, strict=True))


def _reference_gram(parameters):
    eta = (ONE, *parameters)
    blocks = _full_fraction_reference()
    return tuple(tuple(_sum(_multiply(_multiply(blocks[m, n][i][j], eta[m]),
        _conjugate(eta[n])) for m in range(3) for n in range(3))
        for j in range(4)) for i in range(4))


@cache
def _original_columns():
    """Parse every archive coefficient independently of the kernel decoder."""

    columns = []
    mesh = 1 << 80
    with gzip.open(trial.covariance.completed.MATRIX, "rb") as stream:
        for line in stream:
            raw = json.loads(line)
            assert raw["basis_index"] == len(columns)
            values = []
            for matrix in raw["coefficient_columns_constant_a0_a1"]:
                coefficients = []
                for row in matrix:
                    center = tuple(Fraction(v) for v in row[0]["center"])
                    if Fraction(row[0]["radius"]):
                        center = tuple(Fraction(round(v * mesh), mesh) for v in center)
                    coefficients.append(center)
                values.append(tuple(coefficients))
            columns.append(tuple(values))
    assert len(columns) == 5345
    return tuple(columns)


def _section_matrix(parameters):
    eta = (ONE, *parameters)
    columns = tuple(tuple(_sum(_multiply(values[m][r], eta[m]) for m in range(3))
                          for r in range(4)) for values in _original_columns())
    return tuple(zip(*columns, strict=True))


@cache
def _kernel():
    parameters = (trial.Ball(Eisenstein(0), Rational(1), 80, 80),) * 2
    return trial.build_kernel(parameters)


@cache
def _record():
    return trial.kernel_record()


@pytest.mark.parametrize("parameters", (
    (ZERO, ZERO), (ONE, ZERO), ((Fraction(0), Fraction(1)), ONE),
    ((Fraction(0), Fraction(1)), (Fraction(1), Fraction(1))),
))
def test_whole_parameter_region_contains_independent_full_archive_gaussian_inverse(parameters):
    # Arithmetic-only attacks within the declared unit disks, never selected
    # physical points or claims that rounded section centers are cover points.
    kernel = _kernel()
    gram = _reference_gram(parameters)
    inverse = _gaussian_inverse(gram)
    identity = tuple(tuple(ONE if i == j else ZERO for j in range(4)) for i in range(4))
    assert _matmul(gram, inverse) == identity
    assert _matmul(inverse, gram) == identity
    for i in range(4):
        for j in range(4):
            assert _contains(kernel.gram[i][j], gram[i][j])
            assert _contains(kernel.inverse[i][j], inverse[i][j])
    assert kernel.denominator.lower > 0
    assert trial.covariance._adjoint(kernel.inverse) == kernel.inverse


def test_all_5345_action_coordinates_and_projection_identities_by_fraction_gaussian_elimination():
    parameters = ((Fraction(0), Fraction(1)), (Fraction(1), Fraction(1)))
    sections = _section_matrix(parameters)
    gram = _matmul(sections, _adjoint(sections))
    assert gram == _reference_gram(parameters)
    inverse = _gaussian_inverse(gram)
    input_column = tuple((row[0],) for row in sections)
    action = _matmul(_adjoint(sections), _matmul(inverse, input_column))
    record = _record()
    assert len(record["complete_action"]) == 5345
    cover_interval = trial.covariance.covariance_record()["cover_weight_without_pi_cubed"]
    quotient_interval = trial.covariance.covariance_record()["quotient_weight_without_pi_cubed"]
    for index, (value,) in enumerate(action):
        for field, weights in (("complete_action", (Fraction(1),)),
            ("cover_weighted_complete_action_without_pi_cubed", map(Fraction, cover_interval)),
            ("quotient_weighted_complete_action_without_pi_cubed",
             map(Fraction, quotient_interval))):
            ball = trial.covariance._ball(record[field][index], bits=80, center_bits=80)
            assert all(_contains(ball, _multiply(value, (weight, Fraction(0))))
                       for weight in weights)
    # Verify P^2 e0=P e0 through the complete S, not a subset or a dense fake P.
    assert _matmul(sections, action) == input_column
    assert _matmul(_adjoint(sections), _matmul(inverse, _matmul(sections, action))) == action
    assert _sum(_matmul(inverse, gram)[i][i] for i in range(4)) == (Fraction(4), Fraction(0))
    norm = _sum(_multiply(_conjugate(row[0]), row[0]) for row in action)
    assert norm == action[0][0]
    assert norm[1] == 0 and 0 <= norm[0] <= 1
    assert all(_multiply(_conjugate(row[0]), row[0])[0] <= Fraction(1, 4)
               for row in action[1:])


def test_nonunitary_fiber_change_cancels_without_rechoosing_the_section_form():
    parameters = ((Fraction(0), Fraction(1)), ONE)
    gram = _reference_gram(parameters)
    inverse = _gaussian_inverse(gram)
    # Explicit coordinate-change witness, not a model input or physical matrix.
    change = ((ONE, (Fraction(0), Fraction(1)), ZERO, ZERO),
              (ZERO, (Fraction(2), Fraction(0)), ZERO, ZERO),
              (ZERO, ZERO, ONE, ZERO), (ZERO, ZERO, ZERO, ONE))
    changed_gram = _matmul(_matmul(change, gram), _adjoint(change))
    changed_inverse = _gaussian_inverse(changed_gram)
    assert _matmul(_matmul(_adjoint(change), changed_inverse), change) == inverse


def test_mixed_injected_and_lifted_inputs_use_every_original_output_coordinate():
    """Complex input coefficients exercise both original constituent blocks."""

    parameters = ((Fraction(0), Fraction(1)), (Fraction(1), Fraction(1)))
    sections = _section_matrix(parameters)
    inverse = _gaussian_inverse(_matmul(sections, _adjoint(sections)))
    entries = {
        0: (Fraction(1), Fraction(1)),
        1273: (Fraction(-2), Fraction(1)),
        2655: (Fraction(0), Fraction(1)),
        5344: (Fraction(3), Fraction(-2)),
    }
    # Mathematical coordinate witnesses only, not selected physical sections.
    independent_input = tuple((entries.get(i, ZERO),) for i in range(5345))
    image = _matmul(sections, independent_input)
    expected = _matmul(_adjoint(sections), _matmul(inverse, image))
    assert _matmul(sections, expected) == image
    assert _matmul(_adjoint(sections), _matmul(inverse, _matmul(sections, expected))) == expected
    kernel = _kernel()
    coordinates = tuple(Eisenstein(*row[0]) for row in independent_input)
    actual = kernel.apply(coordinates, basis_digest=kernel.actual.form.basis_digest,
                          indices=kernel.actual.form.indices)
    assert len(actual) == 5345
    assert all(_contains(ball, row[0]) for ball, row in zip(actual, expected, strict=True))
    norm = _sum(_multiply(_conjugate(row[0]), row[0]) for row in expected)
    inner = _sum(_multiply(_conjugate(v[0]), w[0])
                 for v, w in zip(independent_input, expected, strict=True))
    input_norm = _sum(_multiply(_conjugate(row[0]), row[0]) for row in independent_input)
    assert norm == inner and norm[1] == input_norm[1] == 0
    assert 0 <= norm[0] <= input_norm[0]


def test_structural_global_bounds_follow_the_actual_weight_and_rank_not_sample_extrema():
    record = _record()
    _, weight = trial.covariance.completed.fiber._verified_payload(trial.global_weight.OUTPUT)
    for region in ("cover", "quotient"):
        b = Fraction(weight[f"{region}_weight_upper_without_pi_cubed"])
        result = record["global_unit_kernel_bounds"][region]
        assert Fraction(result["operator_norm_upper_without_pi_cubed"]) == b
        assert Fraction(result["diagonal_upper_without_pi_cubed"]) == b
        assert Fraction(result["off_diagonal_modulus_upper_without_pi_cubed"]) == b / 2
        assert Fraction(result["frobenius_squared_upper_without_pi_to_six"]) == 4*b*b
        assert Fraction(result[
            "conditional_sample_mean_squared_frobenius_error_numerator_without_pi_to_six"
        ]) == 4*b*b
        assert Fraction(result[
            "conditional_real_coordinate_variance_upper_without_pi_to_six"
        ]) == b*b/4
    cover, quotient = record["global_unit_kernel_bounds"].values()
    assert Fraction(cover["operator_norm_upper_without_pi_cubed"]) == 9 * Fraction(
        quotient["operator_norm_upper_without_pi_cubed"])
    assert Fraction(cover["frobenius_squared_upper_without_pi_to_six"]) == 81 * Fraction(
        quotient["frobenius_squared_upper_without_pi_to_six"])


def test_current_full_packet_reproduces_and_keeps_physical_gates_false():
    record = trial.read_kernel()
    assert trial.covariance.completed._canonical(record) == trial.covariance.completed._canonical(
        _record())
    assert record["section_count"] == 5345 and record["fiber_rank"] == 4
    assert record["all_original_action_coordinates_produced"] is True
    assert record["global_unit_kernel_integrand_bound_available"] is True
    assert record["line_metric_required_for_trial_kernel"] is False
    assert record["independent_cloud_available"] is False
    assert record["controlled_integral_available"] is False
    assert record["ricci_flat_or_hym_metric_available"] is False
    assert record["physical_yukawas_available"] is False
    assert record["common_stabilized_vacuum_available"] is False
    assert "independent draws" in record["conditional_error_assumptions"]
    assert record["uniform_simultaneous_parameter_family_probability_bound_available"] is False
    assert Fraction(record["exact_arithmetic_denominator_scale"]) == Fraction(
        record["admitted_real_determinant_interval"][1])


@pytest.mark.parametrize("parameters", ((), (0, 0), (Eisenstein(0), Eisenstein(1)),
    (trial.Ball(Eisenstein(0), 1, 79, 80),) * 2,
    (trial.Ball(Eisenstein(0), 1, 80, 79),) * 2))
def test_parameters_require_explicit_compatible_complex_enclosures(parameters):
    with pytest.raises(ValueError, match="explicit original-precision"):
        trial.build_kernel(parameters)


@pytest.mark.parametrize("attack", (
    "missing", "foreign", "reordered", "bool", "float", "bool_coordinate",
))
def test_kernel_actions_cannot_hide_incomplete_or_incompatible_vector_bases(attack):
    kernel = _kernel()
    indices = kernel.actual.form.indices
    basis = kernel.actual.form.basis_digest
    coordinates = (Eisenstein(1),) + (Eisenstein(0),) * 5344
    if attack == "missing":
        coordinates = coordinates[:-1]
    elif attack == "foreign":
        basis = "0" * 64
    elif attack == "reordered":
        indices = tuple(reversed(indices))
    elif attack == "bool":
        indices = (False, *indices[1:])
    elif attack == "float":
        coordinates = (0.0, *coordinates[1:])
    else:
        coordinates = (True, *coordinates[1:])
    with pytest.raises((TypeError, ValueError)):
        kernel.apply(coordinates, basis_digest=basis, indices=indices)


def test_kernel_is_deeply_immutable_and_rejects_fabricated_inverse_entries():
    kernel = _kernel()
    with pytest.raises(FrozenInstanceError):
        kernel.inverse = ()
    mutable = [[c for c in row] for row in kernel.inverse]
    reconstructed = replace(kernel, inverse=mutable)
    mutable[0][0] = None
    assert reconstructed.inverse == kernel.inverse
    changed = [list(row) for row in kernel.inverse]
    changed[0][0] = trial.Ball(Eisenstein(0), 0, 80, 80)
    with pytest.raises(ValueError, match="reproduce"):
        replace(kernel, inverse=changed)
    with pytest.raises(ValueError, match="original complete"):
        replace(kernel, columns=kernel.columns[:-1])


def test_conflicting_structural_denominator_is_not_a_fallback(monkeypatch):
    kernel = _kernel()
    certificate = trial.covariance.unit_determinant_certificate(kernel.actual)
    certificate["all_complex_parameter_determinant_lower_bound"] = str(kernel.denominator.upper * 2)
    monkeypatch.setattr(trial.covariance, "unit_determinant_certificate",
                        lambda actual: certificate)
    with pytest.raises(ValueError, match="contradicts"):
        trial._inverse_with_unit_certificate(kernel.actual, kernel.parameters)


def test_original_archive_change_cannot_hide_behind_full_kernel_cache(monkeypatch):
    kernel = _kernel()
    _, source = trial.covariance.completed.fiber._verified_payload(
        trial.covariance.completed.fiber.lifts.first.OUTPUT)
    target = trial.ROOT / source["section_archive"]
    original = trial.covariance.Path.read_bytes

    def changed(self):
        raw = original(self)
        return raw + b"changed" if self == target else raw

    monkeypatch.setattr(trial.covariance.Path, "read_bytes", changed)
    with pytest.raises(ValueError, match="original complete section archive changed"):
        kernel.apply((Eisenstein(0),) * 5345, basis_digest=kernel.actual.form.basis_digest,
                     indices=kernel.actual.form.indices)


@pytest.mark.parametrize("name", (
    "ALTERNATE_SECTION_COVARIANCE_NOTE.md",
    "ALTERNATE_METRIC_QUOTIENT_GENERATION_NOTE.md",
    "ALTERNATE_METRIC_LIFT_OPERATOR_CERTIFICATE_NOTE.md",
))
def test_parent_proof_change_cannot_hide_behind_cached_full_execution(name, monkeypatch):
    _record()
    target = trial.PROOF.with_name(name)
    original = trial.Path.read_bytes

    def changed(self):
        raw = original(self)
        return raw + b"changed" if self == target else raw

    monkeypatch.setattr(trial.Path, "read_bytes", changed)
    with pytest.raises(ValueError, match="changed|source, action, bounds or scope"):
        trial.kernel_record()


@pytest.mark.parametrize("field", (
    "section_basis_digest", "section_count", "fiber_basis_labels", "parameter_regions",
    "admitted_real_determinant_interval", "exact_arithmetic_denominator_scale", "inverse_rule",
    "inverse", "gram", "complete_action", "proof_sha256", "source_identity",
    "global_unit_kernel_bounds", "conditional_error_assumptions", "section_form",
    "cover_weighted_complete_action_without_pi_cubed",
    "quotient_weighted_complete_action_without_pi_cubed", "projection_rank",
    "all_original_columns_consumed", "all_original_action_coordinates_produced",
    "line_metric_required_for_trial_kernel", "extension_point_selected",
    "unit_form_is_physical_or_canonical", "new_geometric_domain_section_calculation_performed",
    "new_all_column_cochain_replay_performed", "independent_cloud_available",
    "practical_sample_cost_certified", "controlled_integral_available",
    "balanced_iteration_performed", "ricci_flat_or_hym_metric_available", "line_twist_removed",
    "harmonic_matter_or_higgs_metrics_available", "physical_yukawas_available",
    "common_stabilized_vacuum_available", "observations_used",
    "uniform_simultaneous_parameter_family_probability_bound_available",
    "generation_and_lift_proof_sha256", "action_input",
))
def test_rehashed_full_action_and_scope_changes_fail_closed(field, tmp_path, monkeypatch):
    original = _record()
    changed = json.loads(json.dumps(original))
    value = changed[field]
    changed[field] = not value if type(value) is bool else "changed"
    changed["artifact_digest"] = trial.hashlib.sha256(
        trial.covariance.completed._canonical(changed)).hexdigest()
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(changed), encoding="utf-8")
    monkeypatch.setattr(trial, "kernel_record", lambda: original)
    with pytest.raises(ValueError, match="source, action, bounds or scope"):
        trial.read_kernel(path)
