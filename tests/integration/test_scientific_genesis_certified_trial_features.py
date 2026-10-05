"""Attack integer disk arithmetic and full projector perturbation certificates.

Owns:
    Independent rational Gaussian witnesses, exact matrix projector comparisons,
    failure gates, mesh identity, and nonphysical scope checks.

Depends on:
    The research disk certification engine, exact scalar/matrix arithmetic, and
    pytest temporary algebra fixtures.

Must not:
    Use generic test matrices as physical sections or infer statistical accuracy.

Phase 0:
    Mathematical certification tests only; HYM and a common vacuum remain open.
"""

import gzip
import json
from dataclasses import FrozenInstanceError
from fractions import Fraction
from itertools import product

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.scientific_genesis import certified_trial_features as module

CERTIFICATE_DIGEST = "dc613f8f9603fd3fad440ce3622a7e03c62561f1925a796b87e74482abdb9fb7"


def _inside(disk, real, imaginary):
    mesh = 1 << disk.bits
    displacement = (real - Fraction(disk.real, mesh)) ** 2 + (
        imaginary - Fraction(disk.imaginary, mesh)
    ) ** 2
    return displacement <= Fraction(disk.radius, mesh) ** 2


@pytest.mark.parametrize("bits", (3, 17, 80, 160))
def test_disk_sum_and_product_contain_independent_exact_gaussian_values(bits):
    a = module.Arithmetic(bits)
    centers = ((Fraction(2, 3), Fraction(-4, 7)), (Fraction(-11, 13), Fraction(5, 17)))
    radius = Fraction(1, 31)
    left, right = (a.gaussian(x, y, radius) for x, y in centers)
    offsets = tuple(
        (radius * x, radius * y)
        for x, y in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (Fraction(1, 2), Fraction(1, 2)))
    )
    for (dx, dy), (ex, ey) in product(offsets, repeat=2):
        x, y = centers[0][0] + dx, centers[0][1] + dy
        u, v = centers[1][0] + ex, centers[1][1] + ey
        assert _inside(left, x, y)
        assert _inside(right, u, v)
        assert _inside(left + right, x + u, y + v)
        assert _inside(left * right, x * u - y * v, x * v + y * u)
        assert _inside(left.conjugate(), x, -y)


def test_exact_gaussian_operations_have_no_fabricated_rounding_radius():
    a = module.Arithmetic(80)
    assert (a.gaussian(3, -2) * a.gaussian(5, 7)).radius == 0
    assert (a.gaussian(3, -2) * a.gaussian(5, 7)).real == 29 * a.mesh
    assert (a.gaussian(3, -2) * a.gaussian(5, 7)).imaginary == 11 * a.mesh
    assert (a.one() * a.one()) == a.one()
    with pytest.raises(FrozenInstanceError):
        a.bits = 1
    with pytest.raises(ValueError, match="same explicit"):
        a.one() * module.Arithmetic(81).one()


@pytest.mark.parametrize("value", (OMEGA, Eisenstein(2, -3), Eisenstein(-5, Fraction(1, 7))))
def test_eisenstein_embedding_is_controlled_by_independent_sqrt_three_brackets(value):
    a = module.Arithmetic(80)
    disk = a.eisenstein(value)
    # Independent high-precision rational brackets on the irrational embedding.
    mesh = 1 << 200
    lower = Fraction(module.math.isqrt(3 * mesh * mesh), mesh)
    upper = lower + Fraction(1, mesh)
    for endpoint in (lower, upper):
        real = Fraction(value.a) - Fraction(value.b) / 2
        imaginary = Fraction(value.b) * endpoint / 2
        assert _inside(disk, real, imaginary)


@pytest.mark.parametrize(
    "value", (complex(1 / 3, -2 / 7), complex(2**-300, 2**-200), complex(0, 0))
)
def test_saved_float_is_an_exact_dyadic_reference_not_a_roundoff_assumption(value):
    disk = module.Arithmetic(160).reference(value)
    assert _inside(disk, Fraction.from_float(value.real), Fraction.from_float(value.imag))


@pytest.mark.parametrize("value", (1.2, True, float("nan"), complex(float("inf"), 0)))
def test_invalid_or_inexact_unlabelled_inputs_are_rejected(value):
    a = module.Arithmetic(80)
    with pytest.raises((TypeError, ValueError)):
        a.gaussian(value)
    with pytest.raises(ValueError):
        a.reference(value)


def _fixture(*, perturbation):
    """Generic algebra fixture only; never fed into an actual carrier experiment."""

    a = module.Arithmetic(120)
    q = tuple(tuple(complex(int(i == j)) for j in range(6)) for i in range(4))
    change = tuple(tuple(complex(int(i == j)) for j in range(4)) for i in range(4))
    s = Matrix(
        tuple(
            tuple(
                Rational(int(i == j)) + (perturbation if j == i + 1 or j == 5 else 0)
                for j in range(6)
            )
            for i in range(4)
        )
    )
    columns = tuple(tuple(a.gaussian(s[i][j]) for i in range(4)) for j in range(6))
    return a, q, change, s, columns


@pytest.mark.parametrize("perturbation", (Rational(0), Rational(1, 100), Rational(-1, 20)))
def test_projector_bound_covers_exact_full_matrix_and_weight_error(perturbation):
    a, q, change, s, columns = _fixture(perturbation=perturbation)
    result = module.certify_projector(
        columns,
        q,
        change,
        arithmetic=a,
        weight_interval=("1", "3/2"),
        reference_weight=Fraction(5, 4),
    )
    assert result["status"] == "certified"
    actual = s.transpose() @ (s @ s.transpose()).inverse() @ s
    reference = Matrix(tuple(tuple(int(i == j and i < 4) for j in range(6)) for i in range(6)))
    bound = Fraction(result["projector_frobenius_error_upper"])
    norm_squared = sum(c * c for row in (actual - reference) for c in row)
    assert norm_squared <= bound * bound
    weighted_bound = Fraction(result["weighted_kernel_frobenius_error_upper_without_pi_cubed"])
    for weight in (Rational(1), Rational(3, 2)):
        difference = actual * weight - reference * Rational(5, 4)
        assert sum(c * c for row in difference for c in row) <= weighted_bound**2
    assert result["covers_input_and_arithmetic_error"] is True
    assert result["sampling_error_included"] is False
    assert result["ricci_flat_or_hym_metric_available"] is False


def test_unresolved_perturbation_never_becomes_a_fake_kernel_certificate():
    a, q, change, _, columns = _fixture(perturbation=Rational(3))
    result = module.certify_projector(
        columns, q, change, arithmetic=a, weight_interval=("1", "2"), reference_weight=Fraction(1)
    )
    assert result["status"] == "unresolved"
    assert "projector_frobenius_error_upper" not in result
    assert "rank four" in result["reason"]


def test_preconditioning_must_be_explicit_and_certifiably_invertible():
    a, q, change, _, columns = _fixture(perturbation=Rational(0))
    changed = list(change)
    changed[0] = (0j, 0j, 0j, 0j)
    with pytest.raises(ValueError, match="nonsingular"):
        module.certify_projector(
            columns,
            q,
            changed,
            arithmetic=a,
            weight_interval=("1", "2"),
            reference_weight=Fraction(1),
        )


def _unavailable(*args, **kwargs):
    raise AssertionError("read-only verification must not discover or redraw")


def test_nonorthonormal_complex_reference_includes_the_row_gram_defect():
    a, q, change, _, columns = _fixture(perturbation=Rational(0))
    q = list(q)
    q[0] = (complex(1, 1 / 256), *q[0][1:])
    result = module.certify_projector(
        columns, q, change, arithmetic=a, weight_interval=("1", "1"), reference_weight=Fraction(1)
    )
    assert result["status"] == "certified"
    # Q†Q differs from the true diagonal projector by 1/256**2 at (0,0).
    assert Fraction(result["gram_frobenius_error_upper"]) >= Fraction(1, 65536)
    assert Fraction(result["projector_frobenius_error_upper"]) >= Fraction(1, 65536)


def test_missing_certificate_reader_does_not_compute_or_redraw(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "compile_disks", _unavailable)
    monkeypatch.setattr(module, "replay_sample", _unavailable)
    monkeypatch.setattr(module.cloud.inputs, "create_inputs", _unavailable)
    with pytest.raises(FileNotFoundError):
        module.read_certificates(expected_digest="0" * 64, path=tmp_path / "missing.json")


def _sample(ordinal):
    return json.loads(gzip.decompress(module._checkpoint_path(ordinal).read_bytes()))


@pytest.mark.parametrize(
    "key,value",
    (
        ("section_count", 5344),
        ("ideal_fiber_rank", 3),
        ("arithmetic_mesh_bits", 159),
        ("covers_input_and_arithmetic_error", False),
        ("sampling_error_included", True),
        ("row_preconditioner_is_physical_normalization", True),
        ("ricci_flat_or_hym_metric_available", True),
        ("physical_yukawas_available", True),
        ("original_checkpoint_digest", "0" * 64),
        ("projector_frobenius_error_upper", "0"),
        ("weighted_kernel_frobenius_error_upper_without_pi_cubed", "0"),
    ),
)
def test_individual_bound_rejects_changed_identity_or_inequality(key, value):
    sample = _sample(0)
    sample[key] = value
    inputs = module.cloud.inputs.read_inputs(expected_digest=module.cloud.INPUT_DIGEST)
    with pytest.raises(ValueError):
        module._check_bound(
            sample, {"arithmetic_mesh_bits": 160, "refinement_level": 24}, 0, inputs
        )


@pytest.mark.parametrize("key", ("root_parent_retained", "frame_parent_retained"))
def test_certificate_cannot_abandon_its_admitted_parent(key):
    sample = _sample(0)
    sample["refinement_history"][key] = False
    inputs = module.cloud.inputs.read_inputs(expected_digest=module.cloud.INPUT_DIGEST)
    with pytest.raises(ValueError, match="identity or scope"):
        module._check_bound(
            sample, {"arithmetic_mesh_bits": 160, "refinement_level": 24}, 0, inputs
        )


def _exact_center_columns(frame, indices):
    """Use raw archive terms and exact field operations, not disk instructions."""

    coordinates = tuple(c.center for c in (*frame.point.x, *frame.point.u, *frame.point.p))
    projections = tuple(
        tuple(tuple(c.center for c in row) for row in matrix) for matrix in frame.projections
    )

    def value(terms):
        total = Eisenstein(0)
        for exponents, pair in terms:
            term = Eisenstein(*map(Fraction, pair))
            for coordinate, exponent in zip(coordinates, exponents, strict=True):
                term = term * coordinate**exponent
            total = total + term
        return total

    result = {}
    with gzip.open(module.features.exact.MATRIX, "rt") as stream:
        for index, line in enumerate(stream):
            if index not in indices:
                continue
            record = json.loads(line)
            assert record["basis_index"] == index
            constant = tuple(value(p) for p in record["constant_generators"])
            corrections = tuple(
                tuple(value(p) for p in group) for group in record["first_parameter_generators"]
            )
            result[index] = tuple(
                sum((projections[0][i][j] * constant[j] for j in range(9)), Eisenstein(0))
                + sum(
                    (
                        parameter
                        * (
                            sum(
                                (projections[0][i][j] * corrections[m][j] for j in range(4)),
                                Eisenstein(0),
                            )
                            + sum(
                                (projections[m + 1][i][j] * constant[j] for j in range(9)),
                                Eisenstein(0),
                            )
                        )
                        for m, parameter in enumerate((Eisenstein(1), OMEGA))
                    ),
                    Eisenstein(0),
                )
                for i in range(4)
            )
    assert set(result) == set(indices)
    return result


def test_fresh_full_original_pipeline_and_independent_exact_field_witnesses():
    """Recompute sample zero; inspect held-out raw polynomials independently."""

    saved = _sample(0)
    program = module.compile_disks(bits=160)
    admission = module.replay_sample(0, levels=(12, 16, 24))
    assert isinstance(admission, module.cloud.continuation.AdmittedFrame)
    assert module.cloud._history(admission, 24) == saved["refinement_history"]
    columns = program.evaluate(admission.frame, (Eisenstein(1), OMEGA))
    original = json.loads(gzip.decompress(module.cloud._checkpoint_path(0).read_bytes()))
    final = original["history"][-1]
    transition = tuple(
        tuple(complex(float.fromhex(c[0]), float.fromhex(c[1])) for c in row)
        for row in final["kernel_diagnostics"]["row_change_of_basis"]
    )
    fresh = module.certify_projector(
        columns,
        module.cloud._decode_rows(final["kernel_rows"]),
        transition,
        arithmetic=program.arithmetic,
        weight_interval=saved["refinement_history"]["quotient_weight_without_pi_cubed"],
        reference_weight=Fraction.from_float(
            float.fromhex(final["weight_midpoint_without_pi_cubed"])
        ),
    )
    assert all(saved[key] == value for key, value in fresh.items())
    assert len(columns) == 5345
    mesh = 1 << 240
    lower = Fraction(module.math.isqrt(3 * mesh * mesh), mesh)
    for index, column in _exact_center_columns(admission.frame, (407, 3089, 5017)).items():
        for disk, value in zip(columns[index], column, strict=True):
            for root in (lower, lower + Fraction(1, mesh)):
                assert _inside(
                    disk, Fraction(value.a) - Fraction(value.b) / 2, Fraction(value.b) * root / 2
                )


def test_saved_reader_verifies_all_original_samples_without_recalculation(monkeypatch):
    monkeypatch.setattr(module, "compile_disks", _unavailable)
    monkeypatch.setattr(module, "replay_sample", _unavailable)
    monkeypatch.setattr(module.cloud.inputs, "create_inputs", _unavailable)
    result = module.read_certificates(expected_digest=CERTIFICATE_DIGEST)
    assert result["finite_cloud_numerical_error_bound_available"] is True
    assert result["unresolved_sample_ordinals"] == []
    assert result["sample_count"] == 16
    samples = tuple(_sample(i) for i in range(16))
    assert all(s["status"] == "certified" and s["section_count"] == 5345 for s in samples)
    raw = (
        sum(Fraction(s["weighted_kernel_frobenius_error_upper_without_pi_cubed"]) for s in samples)
        / 16
    )
    rounded = Fraction(result["finite_cloud_mean_operator_frobenius_error_upper_without_pi_cubed"])
    assert raw <= rounded < raw + Fraction(1, 1 << 160)


@pytest.mark.parametrize(
    "flag",
    (
        "roundoff_assumptions_used",
        "original_discovery_references_overwritten",
        "sampling_error_included",
        "failed_samples_dropped",
        "controlled_integral_available",
        "nonunit_h_iteration_executed",
        "ricci_flat_or_hym_metric_available",
        "physical_yukawas_available",
        "common_stabilized_vacuum_available",
        "observations_used",
    ),
)
def test_rehashed_physical_or_statistical_scope_inflation_is_rejected(flag, tmp_path):
    changed = json.loads(module.OUTPUT.read_bytes())
    changed.pop("artifact_digest")
    changed[flag] = True
    changed["artifact_digest"] = module.cloud.inputs._digest(changed)
    path = tmp_path / "inflated.json"
    path.write_bytes(module.cloud.inputs._canonical(changed))
    with pytest.raises(ValueError, match="cannot be promoted"):
        module.read_certificates(expected_digest=changed["artifact_digest"], path=path)
