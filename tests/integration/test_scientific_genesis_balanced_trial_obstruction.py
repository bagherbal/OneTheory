"""Check whole-matrix numerical obstruction diagnostics against exact algebra.

Owns:
    Full-coordinate diagnostic eigenpairs, explicit congruence, phase choices,
    and rejection of malformed operator inputs using mathematical fixtures.

Depends on:
    The research diagnostic and exact scalar mathematics, NumPy and pytest.

Must not:
    Treat these fixtures as carrier samples, supply a metric, claim certified
    eigenvalue error or replace the original full scientific workload.

Phase 0:
    Algorithm regressions only; physical metric prerequisites remain unresolved.
"""

import json

import numpy as np
import pytest

from onetheory.math.numbers import OMEGA
from research.experiments.scientific_genesis import balanced_trial_obstruction as module


@pytest.mark.parametrize("phase", (1, OMEGA))
@pytest.mark.parametrize("off_diagonal", (0.5, 1.0, 2.0))
def test_complete_diagnostic_matches_exact_eigenpair(phase, off_diagonal):
    if phase != 1:
        phase = complex(float(phase.a - phase.b / 2), float(phase.b) * np.sqrt(3) / 2)
    # An explicit invertible congruence tests original-coordinate retention.
    scales = np.array([2.0**-30, 2.0**30])
    normalized = np.array(
        [[1, off_diagonal * phase], [off_diagonal * complex(phase).conjugate(), 1]], dtype=complex
    )
    operator = scales[:, None] * normalized * scales[None, :]
    direction, actual_scales, result = module.smallest_direction(operator)
    assert direction.shape == (2,)
    np.testing.assert_allclose(actual_scales, scales)
    assert result["smallest_eigenvalue_discovery"] == pytest.approx(1 - off_diagonal, abs=1e-14)
    original = direction / actual_scales
    assert np.vdot(original, operator @ original).real == pytest.approx(
        1 - off_diagonal,
        abs=1e-14,
    )
    assert result["eigenpair_relative_residual_discovery"] < 1e-14
    assert result["normalized_direction_norm_discovery"] == pytest.approx(1)
    pivot = result["diagnostic_phase_pivot"]
    assert direction[pivot].real > 0
    assert abs(direction[pivot].imag) < 1e-14
    assert result["hermitian_rounding_projection_explicit"] is True


@pytest.mark.parametrize(
    "operator",
    (
        np.zeros((0, 0)),
        np.ones((2, 3)),
        np.array([1, 2]),
        np.array([[1, 1], [0, 1]]),
        np.array([[0, 0], [0, 1]]),
        np.array([[np.inf, 0], [0, 1]]),
        np.array([[np.nan, 0], [0, 1]]),
    ),
)
def test_malformed_operator_cannot_supply_a_direction(operator):
    with pytest.raises(ValueError):
        module.smallest_direction(operator)


def test_existing_diagnostic_never_reexecutes_the_failed_trial(tmp_path, monkeypatch):
    output = tmp_path / "retained.json"
    output.write_text("retained mathematical fixture", encoding="utf-8")
    monkeypatch.setattr(module, "OUTPUT", output)
    monkeypatch.setattr(module.inverse, "read_step", lambda **kwargs: pytest.fail("no replay"))
    with pytest.raises(FileExistsError, match="preserve"):
        module.run(expected_request_digest="unused", expected_step_digest="unused")


@pytest.fixture(scope="module")
def actual_cloud():
    """Revalidate all actual checkpoints once, without entropy or geometric replay."""

    return module.full.read_cloud(
        expected_request_digest="9e13a565bc13a2bd27320e5746d3fbf2104c3290f8792efc97d8d3316bc8a5b5",
        expected_digest="3138e6d6eb4c17fb977714f78069cc704e09f3eab45fb73e1b8d16d540cd29cc",
    )


def _reuse_validated_cloud(actual_cloud, monkeypatch):
    def read(**kwargs):
        assert kwargs["expected_request_digest"] == actual_cloud["request_digest"]
        assert kwargs["expected_digest"] == actual_cloud["artifact_digest"]
        return actual_cloud

    monkeypatch.setattr(module.full, "read_cloud", read)


def test_actual_failed_step_reader_retains_the_whole_operator(actual_cloud, monkeypatch):
    _reuse_validated_cloud(actual_cloud, monkeypatch)
    record, form = module.inverse.read_step(
        expected_request_digest="5a7953df972ee465e28c0bec9db09173b3fa81e20409503f171d7da280c37bfc",
        expected_digest="bc7f9c9819829269b9978823e4d3c99119bce97ef548a26014d6a333a8b89001",
    )
    assert form is None
    assert record["status"] == "unresolved"
    assert record["section_count"] == 5345
    assert record["sample_count"] == 1536
    assert set(record["arrays"]) == {"operator"}


@pytest.mark.parametrize(
    "flag",
    (
        "positive_full_basis_form_available",
        "inverse_step_executed",
        "nonunit_h_iteration_executed",
        "solver_equilibration_is_physical_normalization",
        "reduced_section_basis_used",
        "ridge_or_pseudoinverse_used",
        "numerical_error_bound_certified",
        "sampling_error_bound_useful",
        "controlled_integral_available",
        "ricci_flat_or_hym_metric_available",
        "physical_yukawas_available",
        "common_stabilized_vacuum_available",
        "validation_samples_used_to_select_h1",
        "observations_used",
    ),
)
def test_rehashed_real_failure_cannot_inflate_scope(flag, actual_cloud, monkeypatch, tmp_path):
    _reuse_validated_cloud(actual_cloud, monkeypatch)
    record = json.loads(module.inverse.OUTPUT.read_bytes())
    record[flag] = True
    unsigned = {k: v for k, v in record.items() if k != "artifact_digest"}
    record["artifact_digest"] = module.full.cloud.inputs._digest(unsigned)
    path = tmp_path / "rehashed.json"
    path.write_bytes(module.full.cloud.inputs._canonical(record))
    with pytest.raises(ValueError, match="scientific scope"):
        module.inverse.read_step(
            expected_request_digest=record["inverse_request_digest"],
            expected_digest=record["artifact_digest"],
            path=path,
        )
