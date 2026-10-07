"""Check H1 first-jet curvature against independent full-basis inverse actions.

Owns:
    Actual retained-coordinate covariance and inverse-metric curvature checks,
    explicit scalar/frame invariance, and missing-original-input rejection.

Depends on:
    The trusted full-basis H1 factor, original sample zero and polynomial stream,
    NumPy discovery arithmetic, and the research first-jet consumer.

Must not:
    Substitute random matrices for the carrier, claim a point is an integral,
    or promote a binary64 comparison into certified HYM convergence.

Phase 0:
    Independent discovery checks only; no physical metric is exported.
"""

from fractions import Fraction
from functools import cache
from time import perf_counter

import numpy as np
import pytest

from research.experiments.scientific_genesis import nonunit_connection_curvature as module


@cache
def _actual():
    curvature = module.curvature
    full = curvature.full
    request = full.read_request(expected_digest=curvature.PARENT_REQUEST)
    inputs = full.cloud.inputs.read_inputs(
        expected_digest=request["input_digest"], path=full.INPUTS,
    )
    saved = full._read_sample(request, inputs, 0)
    assert saved["artifact_digest"] == module.refinement._parent()["points"][0][
        "sample_artifact_digest"
    ]
    coordinates = [curvature.features._complex(curvature.Eisenstein(
        Fraction(c["center"][0]), Fraction(c["center"][1]),
    )) for group in saved["history"][-1]["coordinate_bounds"] for c in group]
    program = curvature.features.compile_features()
    parameters = tuple(curvature.features._complex(curvature.Eisenstein(Fraction(a), Fraction(b)))
                       for a, b in request["policy"]["parameters"])
    values, jets, metric, _ = curvature.FullSectionJets(program).evaluate(
        coordinates, parameters, source_signature=program.source_signature,
    )
    record, form = module.inverse.read_result(
        expected_request_digest=module.H1_REQUEST, expected_digest=module.H1,
    )
    assert form is not None
    started = perf_counter()
    transformed = module.inverse_form_jets(
        form, values, jets, basis_digest=curvature.features.BASIS,
    )
    elapsed = perf_counter() - started
    print({"actual_h1_first_jet_action_seconds": elapsed, "original_sample_ordinal": 0})
    combined = np.concatenate((values[None], jets), axis=0).reshape(16, 5345)
    # This independently uses BOTH triangular solves for H1, not the one-solve
    # square-root action under test. Only the 16-by-16 contraction is formed.
    covariance = combined @ form.apply(combined.conj().T, basis_digest=curvature.features.BASIS)
    return record, form, values, jets, metric, transformed, covariance


def test_actual_h1_values_and_all_first_jets_agree_with_two_solve_inverse():
    record, form, _, _, _, (values, jets), covariance = _actual()
    assert record["artifact_digest"] == module.H1
    assert form.section_count == 5345
    combined = np.concatenate((values[None], jets), axis=0).reshape(16, 5345)
    computed = combined @ combined.conj().T
    assert np.linalg.norm(computed - covariance, "fro") / np.linalg.norm(covariance, "fro") < 1e-7
    assert values.shape == (4, 5345)
    assert jets.shape == (3, 4, 5345)


def test_actual_h1_curvature_agrees_with_independent_inverse_metric_derivatives():
    _, _, _, _, metric, transformed, covariance = _actual()
    fiber = covariance[:4, :4]
    inverse = np.linalg.inv(fiber)
    background_inverse = np.linalg.inv(metric)
    direct = np.zeros((4, 4), dtype=complex)
    for i in range(3):
        row = slice(4 * (i + 1), 4 * (i + 2))
        for j in range(3):
            column = slice(4 * (j + 1), 4 * (j + 2))
            direct += background_inverse[i, j] * (
                covariance[row, column] - covariance[row, :4] @ inverse @ covariance[:4, column]
            ) @ inverse
    lower = np.linalg.cholesky((fiber + fiber.conj().T) / 2)
    unitary = np.linalg.solve(lower, direct @ lower)
    trace_free = unitary - np.trace(unitary) / 4 * np.eye(4)
    expected = np.linalg.eigvalsh((trace_free + trace_free.conj().T) / 2)
    values, jets, _ = module.refinement.constant_row_gauge(*transformed)
    actual = module.curvature.trace_free_curvature(values, jets, metric)
    assert np.allclose(actual["trace_free_eigenvalues"], expected, rtol=1e-6, atol=1e-6)
    assert actual["trace_free_l1"] > 0


def test_h1_action_preserves_scalar_and_constant_germ_frame_invariance():
    _, form, values, jets, metric, transformed, _ = _actual()
    original = module.refinement.constant_row_gauge(*transformed)
    baseline = module.curvature.trace_free_curvature(*original[:2], metric)
    frame = np.diag((2, 3, 5, 7)).astype(complex)
    frame[0, 1] = 1j
    changed = module.inverse_form_jets(form, frame @ values, frame @ jets,
                                      basis_digest=module.curvature.features.BASIS)
    changed_values, changed_jets, _ = module.refinement.constant_row_gauge(*changed)
    after = module.curvature.trace_free_curvature(changed_values, changed_jets, metric)
    scaled = module.curvature.trace_free_curvature(original[0] * 7, original[1] * 7, metric)
    assert np.allclose(after["trace_free_eigenvalues"], baseline["trace_free_eigenvalues"],
                       rtol=1e-7, atol=1e-7)
    assert np.allclose(scaled["trace_free_eigenvalues"], baseline["trace_free_eigenvalues"],
                       rtol=1e-9, atol=1e-9)


@pytest.mark.parametrize("missing", ("basis", "columns", "jets", "finite", "form"))
def test_h1_action_rejects_missing_or_changed_original_inputs(missing):
    _, form, values, jets, _, _, _ = _actual()
    basis = module.curvature.features.BASIS
    if missing == "basis":
        basis = "unrelated-basis"
    elif missing == "columns":
        values = values[:, :4]
    elif missing == "jets":
        jets = jets[:2]
    elif missing == "finite":
        values = values.copy()
        values[0, 0] = np.nan
    else:
        form = object()
    with pytest.raises(ValueError, match="named complete original"):
        module.inverse_form_jets(form, values, jets, basis_digest=basis)
