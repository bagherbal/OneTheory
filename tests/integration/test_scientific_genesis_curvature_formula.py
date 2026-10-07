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

from functools import cache

import numpy as np
import pytest

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
