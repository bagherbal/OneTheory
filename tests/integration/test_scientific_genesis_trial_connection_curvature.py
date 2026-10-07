"""Check analytic full-section jets and invariant trial-curvature conventions.

Owns:
    Independent exact derivative probes, original projection checks and
    coordinate/frame covariance tests on the unchanged regression domains.

Depends on:
    The frozen polynomial archive, actual named bounded frames, exact arithmetic,
    NumPy and the research derivative consumer.

Must not:
    Substitute fixture matrices for a carrier, redraw roots or infer physical
    normalization, integration accuracy or HYM convergence from local checks.

Phase 0:
    Discovery regression tests only; physical metric gates remain unresolved.
"""

import gzip
import json
from functools import cache

import numpy as np
import pytest

from research.experiments.scientific_genesis import trial_connection_curvature as module


@cache
def _consumer():
    return module.FullSectionJets(module.features.compile_features())


@cache
def _probe():
    _, _, frame = module.features.exact.domains.declared_frames()[0]
    coordinates = tuple(c.center for group in (frame.point.x, frame.point.u, frame.point.p)
                        for c in group)
    numeric = np.asarray([module.features._complex(c) for c in coordinates])
    parameters = (1, module.features._complex(module.Eisenstein(0, 1)))
    consumer = _consumer()
    result = consumer.evaluate(
        numeric, parameters, source_signature=consumer.program.source_signature,
    )
    return frame, coordinates, numeric, parameters, result


def test_zero_coordinate_derivatives_do_not_divide_by_the_coordinate():
    exponents = ((0, 1, 0, 0, 0, 0, 0, 0), (0, 2, 0, 0, 0, 0, 0, 0))
    coordinates = np.ones(8)
    coordinates[1] = 0
    tangent = np.zeros((8, 3))
    tangent[1] = (2, 3, 5)
    assert np.array_equal(module.monomial_jets(exponents, coordinates, tangent),
                          ((0, 2, 3, 5), (0, 0, 0, 0)))


def test_projection_value_preserves_the_original_frame_and_differentiates_relations():
    frame, _, numeric, parameters, _ = _probe()
    tangent, _, _ = module.tangent_background(numeric)
    projection = module.projection_jets(numeric, tangent, parameters)
    original = sum(coefficient * np.asarray([[module.features._complex(c.center) for c in row]
                                            for row in matrix])
                   for coefficient, matrix in zip((1, *parameters), frame.projections, strict=True))
    assert np.allclose(projection[:, :, 0], original, rtol=1e-10, atol=1e-10)
    inclusion = np.eye(9)[:, list(module.FREE)]
    assert np.allclose(projection[:, :, 0] @ inclusion, np.eye(4), atol=1e-13)
    assert np.allclose(projection[:, :, 1:].transpose(2, 0, 1) @ inclusion, 0, atol=1e-13)
    # Independent ordinary matrix calculus of B_p^-1, rather than the quotient helper.
    first, second, outer = module.relation_polynomials()
    b = np.zeros((9, 5, 4), dtype=np.complex128)
    for col, polynomials in enumerate(first):
        for row, polynomial in enumerate(polynomials):
            b[row, col] = module.polynomial_jets(polynomial, numeric, tangent)
    for col, polynomials in enumerate(second):
        for row, polynomial in enumerate(polynomials):
            b[row + 4, col + 2] = module.polynomial_jets(polynomial, numeric, tangent)
    for parameter, channel in zip(parameters, outer, strict=True):
        for col, polynomials in enumerate(channel):
            for row, polynomial in enumerate(polynomials):
                b[row, col + 2] += parameter * module.polynomial_jets(polynomial, numeric, tangent)
    assert np.allclose(projection[:, :, 0] @ b[:, :, 0], 0, atol=1e-10)
    for direction in range(3):
        residual = (projection[:, :, direction + 1] @ b[:, :, 0]
                    + projection[:, :, 0] @ b[:, :, direction + 1])
        assert np.allclose(residual, 0, atol=1e-10)


def test_full_section_values_and_held_out_exact_derivatives_agree():
    frame, coordinates, numeric, parameters, (values, derivatives, _, _) = _probe()
    consumer = _consumer()
    original = consumer.program.evaluate(frame, source_signature=consumer.program.source_signature)
    expected = np.asarray([
        np.asarray(column[0]) + parameters[0] * np.asarray(column[1])
        + parameters[1] * np.asarray(column[2]) for column in original.columns
    ]).T
    assert values.shape == (4, 5345)
    assert derivatives.shape == (3, 4, 5345)
    assert np.allclose(values, expected, rtol=1e-9, atol=1e-9)
    tangent, _, _ = module.tangent_background(numeric)
    projection = module.projection_jets(numeric, tangent, parameters)
    selected = {407, 3089, 5017}
    with gzip.open(module.features.exact.MATRIX, "rb") as stream:
        records = {i: json.loads(line) for i, line in enumerate(stream) if i in selected}
    for index, record in records.items():
        column = module.features.exact.parse_column(
            record, index=index, chart=(0, 0, 0),
            source_signature=consumer.program.source_signature,
        )
        polynomials = list(column.constant_generators)
        # Parameters are fixed; multiply only after exact polynomial evaluation.
        def exact_jets(polynomial):
            value = module.features._complex(polynomial.substitute(coordinates).coefficient(()))
            gradient = np.asarray([module.features._complex(
                polynomial.derivative(axis).substitute(coordinates).coefficient(()),
            ) for axis in range(8)])
            return np.r_[value, gradient @ tangent]
        ambient = np.asarray([exact_jets(p) for p in polynomials])
        for parameter, correction in zip(
            parameters, column.first_parameter_generators, strict=True,
        ):
            ambient[:4] += parameter * np.asarray([exact_jets(p) for p in correction])
        for direction in range(3):
            exact = (projection[:, :, direction + 1] @ ambient[:, 0]
                     + projection[:, :, 0] @ ambient[:, direction + 1])
            assert np.allclose(derivatives[direction, :, index], exact, rtol=1e-8, atol=1e-8)


def test_curvature_is_invariant_under_constant_fiber_and_complex_coordinate_changes():
    _, _, _, _, (values, derivatives, metric, _) = _probe()
    baseline = module.trace_free_curvature(values, derivatives, metric)
    # Explicit invertible changes of coordinates, not alternative physical sections.
    frame_change = np.diag((2, 3, 5, 7)).astype(complex)
    frame_change[0, 1] = 1j
    changed = module.trace_free_curvature(frame_change @ values,
                                         frame_change @ derivatives, metric)
    coordinate_change = np.asarray(((2, 1j, 0), (0, 3, 1), (0, 0, 5)), dtype=complex)
    changed_jets = np.einsum("ia,irn->arn", coordinate_change, derivatives)
    changed_metric = coordinate_change.conj().T @ metric @ coordinate_change
    rebased = module.trace_free_curvature(values, changed_jets, changed_metric)
    assert np.allclose(changed["trace_free_eigenvalues"], baseline["trace_free_eigenvalues"],
                       rtol=1e-9, atol=1e-9)
    assert np.allclose(rebased["trace_free_eigenvalues"], baseline["trace_free_eigenvalues"],
                       rtol=1e-9, atol=1e-9)
    assert abs(sum(baseline["trace_free_eigenvalues"])) < 1e-10


def test_original_source_identity_and_chart_are_not_implicit():
    _, _, numeric, parameters, _ = _probe()
    with pytest.raises(ValueError, match="identity"):
        _consumer().evaluate(numeric, parameters, source_signature=())
    with pytest.raises(ValueError, match="normalized"):
        module.tangent_background(numeric * 2)
    with pytest.raises(TypeError, match="complete"):
        module.FullSectionJets(object())
