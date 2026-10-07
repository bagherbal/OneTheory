"""Independently check the curvature formula on actual original section values.

Owns:
    A direct derivative-of-inverse comparison and holomorphic line-frame
    invariance, without reusing the producer's orthogonal-complement formula.

Depends on:
    The frozen full original compiler, actual declared regression frames,
    NumPy matrix algebra and the research curvature consumer.

Must not:
    Treat a regression point as an integral, promote binary64 inverse checks
    into certified errors, or report a physical HYM metric.

Phase 0:
    Independent discovery arithmetic checks only.
"""

import json
from functools import cache

import numpy as np
import pytest

from research.experiments.scientific_genesis import audit
from research.experiments.scientific_genesis import row_scaled_trial_curvature as refinement
from research.experiments.scientific_genesis import trial_connection_curvature as module


@cache
def _actual_jets():
    program = module.features.compile_features()
    _, _, frame = module.features.exact.domains.declared_frames()[0]
    coordinates = [module.features._complex(c.center)
                   for group in (frame.point.x, frame.point.u, frame.point.p) for c in group]
    return module.FullSectionJets(program).evaluate(
        coordinates, (1, module.features._complex(module.Eisenstein(0, 1))),
        source_signature=program.source_signature,
    )


def test_direct_derivative_of_inverse_agrees_with_full_fiber_qr_curvature():
    values, derivatives, metric, _ = _actual_jets()
    covariance = values @ values.conj().T
    inverse = np.linalg.inv(covariance)
    background_inverse = np.linalg.inv(metric)
    curvature = np.zeros((4, 4), dtype=complex)
    for i in range(3):
        for j in range(3):
            mixed_second = derivatives[i] @ derivatives[j].conj().T
            first = derivatives[i] @ values.conj().T
            antiholomorphic_first = values @ derivatives[j].conj().T
            curvature += background_inverse[i, j] * (
                mixed_second - first @ inverse @ antiholomorphic_first
            ) @ inverse
    # Convert the endomorphism into a constant unitary fiber frame, independently
    # of the producer's tall QR. This comparison is discovery arithmetic only.
    lower = np.linalg.cholesky(covariance)
    unitary = np.linalg.solve(lower, curvature @ lower)
    trace_free = unitary - np.trace(unitary) / 4 * np.eye(4)
    eigenvalues = np.linalg.eigvalsh((trace_free + trace_free.conj().T) / 2)
    actual = module.trace_free_curvature(values, derivatives, metric)
    assert np.allclose(actual["trace_free_eigenvalues"], eigenvalues, rtol=1e-7, atol=1e-7)
    assert np.isclose(actual["trace_free_l1"], np.sum(np.abs(eigenvalues)), rtol=1e-7)
    assert actual["trace_free_l1"] > 0


def test_holomorphic_line_frame_units_do_not_change_trace_free_curvature():
    values, derivatives, metric, _ = _actual_jets()
    baseline = module.trace_free_curvature(values, derivatives, metric)
    # These are an explicit coordinate-unit transformation, not physical moduli.
    unit = 2 + 3j
    logarithmic_derivative = np.asarray((1 + 2j, 2 - 1j, 3))
    changed_values = unit * values
    changed_derivatives = unit * (
        derivatives + logarithmic_derivative[:, None, None] * values[None]
    )
    changed = module.trace_free_curvature(changed_values, changed_derivatives, metric)
    assert np.allclose(changed["trace_free_eigenvalues"], baseline["trace_free_eigenvalues"],
                       rtol=1e-9, atol=1e-9)


def test_curvature_rejects_reduced_sections_and_nonfinite_values():
    values, derivatives, metric, _ = _actual_jets()
    with pytest.raises(ValueError, match="all original"):
        module.trace_free_curvature(values[:, :4], derivatives[:, :, :4], metric)
    changed = values.copy()
    changed[0, 0] = np.nan
    with pytest.raises(ValueError, match="finite"):
        module.trace_free_curvature(changed, derivatives, metric)


def test_constant_row_gauge_preserves_actual_connection_not_a_new_section_form():
    values, jets, metric, _ = _actual_jets()
    before = module.trace_free_curvature(values, jets, metric)
    scaled_values, scaled_jets, scales = refinement.constant_row_gauge(values, jets)
    after = module.trace_free_curvature(scaled_values, scaled_jets, metric)
    assert scaled_values.shape == (4, 5345)
    assert scaled_jets.shape == (3, 4, 5345)
    assert np.array_equal(scales, np.max(np.abs(values), axis=1))
    assert np.allclose(after["trace_free_eigenvalues"], before["trace_free_eigenvalues"],
                       rtol=1e-8, atol=1e-8)
    assert np.array_equal(values, scaled_values * scales[:, None]) or np.allclose(
        values, scaled_values * scales[:, None], rtol=1e-15,
    )


def test_constant_gauge_rejects_missing_rows_and_reduced_sections():
    values, jets, _, _ = _actual_jets()
    changed = values.copy()
    changed[0] = 0
    with pytest.raises(ArithmeticError, match="unresolved"):
        refinement.constant_row_gauge(changed, jets)
    with pytest.raises(ValueError, match="all finite original"):
        refinement.constant_row_gauge(values[:, :4], jets[:, :, :4])


def test_pinned_whole_population_failure_keeps_physical_gate_closed():
    summary = audit._trial_curvature_summary()
    assert summary["point_records_reference"]["resolved_count"] == 2042
    assert summary["unresolved_ordinals"] == [632, 956, 1007, 1161, 1637, 1962]
    assert summary["complete_original_workload_available"] is False
    assert summary["admitted_subset_mean_available"] is False
    claims = {node["id"]: node for node in audit._nodes()}
    assert claims["trial_connection_curvature"]["status"] == "BLOCKED"
    assert claims["visible_metrics"]["status"] == "BLOCKED"
    assert claims["physical_yukawas"]["status"] == "BLOCKED"
    state = {"claims": audit._nodes(), "dependencies": audit._edges(), "fitted_inputs": []}
    state["artifact_digest"] = audit._canonical_digest(state)
    audit.validate_state(state)


def _edited_packet(tmp_path, monkeypatch, edit):
    record = json.loads(module.OUTPUT.read_bytes())
    edit(record)
    path = tmp_path / "curvature.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    # Model a self-consistent rehash to check scientific scope independently of
    # checksum rejection. The actual verifier never accepts arbitrary digests.
    original_digest = audit._canonical_digest

    def consistent_digest(payload):
        if isinstance(payload, dict) and payload.get("schema") == record["schema"]:
            return record["artifact_digest"]
        return original_digest(payload)

    monkeypatch.setattr(audit, "_canonical_digest", consistent_digest)
    return path


@pytest.mark.parametrize("flag", (
    "complete_original_workload_available", "admitted_subset_mean_available",
    "old_validation_is_blind", "numerical_and_sampling_error_certified",
    "reference_background_is_ricci_flat", "hym_convergence_established",
    "determinant_normalized_su4_metric_exported", "matter_or_higgs_metrics_available",
    "physical_yukawas_available", "common_stabilized_vacuum_available", "observations_used",
))
def test_curvature_packet_cannot_inflate_physical_or_integral_scope(tmp_path, monkeypatch, flag):
    path = _edited_packet(tmp_path, monkeypatch, lambda record: record.__setitem__(flag, True))
    with pytest.raises(ValueError, match="physical boundary"):
        audit._trial_curvature_summary(path)


@pytest.mark.parametrize("key", (
    "full_population_tau_discovery", "empirical_reference_volume_discovery", "role_tau_discovery",
))
def test_failed_population_cannot_export_an_aggregate(tmp_path, monkeypatch, key):
    path = _edited_packet(tmp_path, monkeypatch, lambda record: record.__setitem__(key, 1))
    with pytest.raises(ValueError, match="physical boundary"):
        audit._trial_curvature_summary(path)


def test_failed_curvature_point_cannot_be_removed(tmp_path, monkeypatch):
    path = _edited_packet(tmp_path, monkeypatch, lambda record: record["points"].pop(632))
    with pytest.raises(ValueError, match="physical boundary"):
        audit._trial_curvature_summary(path)


def test_curvature_record_requires_unchanged_source_bytes(tmp_path, monkeypatch):
    def alter(record):
        name = next(iter(record["source_files_sha256"]))
        record["source_files_sha256"][name] = "0" * 64

    path = _edited_packet(tmp_path, monkeypatch, alter)
    with pytest.raises(ValueError, match="sources changed"):
        audit._trial_curvature_summary(path)
