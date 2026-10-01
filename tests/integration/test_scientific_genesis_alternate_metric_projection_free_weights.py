"""Independently verify projection-free weights on the unchanged actual cover.

Owns:
    Exact Schur-complement identities, full ambient inverse/determinant checks,
    all declared regular and axis-critical weights, precision and scope attacks.

Depends on:
    Exact Matrix arithmetic, original root certificates and chart densities,
    and the projection-free research calculation.

Must not:
    Interpret linear-algebra fixtures or disk functionals as physical points,
    infer uniform sampling, certify missing triangle inputs, or assert metrics.

Phase 0:
    Research structural and enclosure tests; physical normalization stays open.
"""

import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from functools import cache
from itertools import product

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.scientific_genesis import (
    alternate_metric_projection_free_weights as weights,
)

positive, critical, bounds, roots, measure = (
    weights.positive, weights.critical, weights.bounds, weights.roots, weights.measure,
)


def _adjoint(matrix):
    def conjugate(c):
        return c.conjugate() if isinstance(c, Eisenstein) else c

    return Matrix(tuple(tuple(conjugate(c) for c in col)
                        for col in zip(*matrix.rows, strict=True)), scalar_type=matrix.scalar_type)


@pytest.mark.parametrize("field", (Rational, Eisenstein))
@pytest.mark.parametrize("free", ((2, 3, 4), (0, 3, 4), (4, 3, 2)))
def test_general_hermitian_schur_identity_for_different_free_covectors(field, free):
    # Declared algebra fixtures only, never used as physical matrices.
    u = Rational(2) if field is Rational else OMEGA
    j = Matrix(((1, u, 0, 1, 0), (0, 1, 3, 0, u)), scalar_type=field)
    g = Matrix(tuple(tuple(i + 1 if i == k else 0 for k in range(5)) for i in range(5)),
               scalar_type=field)
    k = Matrix(tuple(tuple(int(i == n) for i in range(5)) for n in free), scalar_type=field)
    frame = Matrix(j.rows + k.rows, scalar_type=field)
    t = Matrix(tuple(row[2:] for row in frame.inverse().rows), scalar_type=field)
    assert j.matmul(t).is_zero()
    assert k.matmul(t) == Matrix(((1, 0, 0), (0, 1, 0), (0, 0, 1)), scalar_type=field)
    gram = _adjoint(t).matmul(g).matmul(t)
    conormal = j.matmul(g.inverse()).matmul(_adjoint(j))
    jacobian = frame.determinant()
    norm = jacobian.norm() if isinstance(jacobian, Eisenstein) else jacobian**2
    assert gram.determinant() * norm == g.determinant() * conormal.determinant()


def _full_determinants(chart, coordinates):
    """Use the full 5x5 inverse and 2x2 determinant, not the sparse positive sum."""

    f, g = measure.projection_polynomials(chart)
    j = Matrix(tuple(tuple(measure._value(p.derivative(i), coordinates) for i in range(5))
                     for p in (f, g)), scalar_type=Eisenstein)
    ambient = [[Eisenstein(0) for _ in range(5)] for _ in range(5)]
    for indices in ((0, 1), (2, 3), (4,)):
        norm = Rational(1) + sum((coordinates[i].norm() for i in indices), Rational(0))
        for i in indices:
            for k in indices:
                ambient[i][k] = (Eisenstein(norm * int(i == k))
                                 - coordinates[i] * coordinates[k].conjugate()) / norm**2
    metric = Matrix(ambient, scalar_type=Eisenstein)
    conormal = j.matmul(metric.inverse()).matmul(_adjoint(j))
    d, c = metric.determinant(), conormal.determinant()
    assert d.b.is_zero() and c.b.is_zero()
    assert d.a > 0 and c.a > 0
    return d.a, c.a, d.a * c.a


@cache
def _regular(name, refined=False):
    return weights.regular_configuration(name, roots.RootPolicy(
        Rational(1, 2**(36 if refined else 30)), 72 if refined else 60, 80, 128,
    ))


@cache
def _critical(side, axis):
    return critical.configuration(tuple(int(i == axis) for i in range(3)),
        roots.ProjectiveLine((1, 0, 0), (0, 1, 1)), source_side=side,
        parameter_pivot=0, policy=roots.RootPolicy(Rational(1, 2**30), 60, 80, 128))


def _check_functionals(result, chart):
    # Actual points are certified by roots. These perturbations are arithmetic
    # FUNCTIONALS only, not asserted cover points or Monte Carlo draws.
    for direction in (Eisenstein(0), Eisenstein(1), OMEGA, OMEGA**2):
        coordinates = tuple(c.center + direction * c.radius for c in result.coordinates)
        ambient, conormal, denominator = _full_determinants(chart, coordinates)
        assert result.ambient_determinant.contains(ambient)
        assert result.conormal_determinant.contains(conormal)
        assert result.denominator.contains(denominator)
        assert result.cover_weight_without_pi_cubed.contains(12 / denominator)
        assert result.quotient_weight_without_pi_cubed.contains(Rational(4, 3) / denominator)


@pytest.mark.parametrize("name", ("finite_chart", "infinity_branch"))
def test_all_original_regular_domains_match_original_positive_weights(name):
    configuration = _regular(name)
    assert len(configuration.root_pairs) == 9
    for pair in configuration.root_pairs:
        xp, xs = (1, 0) if pair[0] == "infinity" else (0, 2)
        chart = measure.ProjectionChart(xp, xs, 0, 2, 0 if name == "finite_chart" else 1)
        point = bounds.BoundedCoverPoint(configuration, pair, chart.pivots, 80)
        result = weights.local_weight(point, chart, volume_scale=1, covering_degree=9, bits=80)
        original = positive.bounded_positive_measure(point, chart, volume_scale=1,
                                                     covering_degree=9, bits=80)
        left = result.cover_weight_without_pi_cubed
        right = original["cover_weight_without_pi_cubed"]
        assert max(left.lower, right.lower) <= min(left.upper, right.upper)
        _check_functionals(result, chart)


@pytest.mark.parametrize("side,axis", tuple((s, a) for s in (1, 2) for a in range(3)))
def test_all_axis_critical_domains_match_signed_chart_weights_without_plane_inverses(side, axis):
    configuration = _critical(side, axis)
    remaining = tuple(i for i in range(3) if i != axis)
    chart = (measure.ProjectionChart(axis, remaining[1], 0, 2, 0) if side == 1
             else measure.ProjectionChart(0, 2, axis, remaining[1], 0))
    for pair in configuration.root_pairs:
        point = bounds.BoundedCoverPoint(configuration, pair, chart.pivots, 80)
        result = weights.local_weight(point, chart, volume_scale=1, covering_degree=9, bits=80)
        original = critical.local_measure(point, chart, source_side=side, volume_scale=1,
                                           covering_degree=9, bits=80)
        zero_plane = result.conormal_terms[0 if side == 1 else 1]
        assert zero_plane.lower == zero_plane.upper == 0
        assert result.denominator.lower > 0
        left, right = result.cover_weight_without_pi_cubed, original.cover_weight_without_pi_cubed
        assert max(left.lower, right.lower) <= min(left.upper, right.upper)
        _check_functionals(result, chart)


@pytest.mark.parametrize("complementary", (False, True))
def test_exact_actual_points_preserve_exact_singletons_and_normalization(complementary):
    x, u, p = (((1, 1, 1), (1, -1, 0), (1, 0)) if complementary
               else ((1, -1, 0), (1, 1, 1), (0, 1)))
    pivots = (0, 0, 0 if complementary else 1)
    point = measure.CoverPoint(x, u, p, pivots)
    chart = measure.ProjectionChart(0, 2, 0, 2, pivots[2])
    result = weights.local_weight(point, chart, volume_scale=1, covering_degree=9, bits=80)
    original = positive.bounded_positive_measure(point, chart, volume_scale=1,
                                                 covering_degree=9, bits=80)
    assert result.cover_weight_without_pi_cubed == original["cover_weight_without_pi_cubed"]
    assert result.cover_weight_without_pi_cubed.width == 0
    scaled = weights.local_weight(point, chart, volume_scale=2, covering_degree=1, bits=80)
    assert scaled.cover_weight_without_pi_cubed == result.cover_weight_without_pi_cubed * 4
    assert scaled.quotient_weight_without_pi_cubed == scaled.cover_weight_without_pi_cubed
    with pytest.raises(FrozenInstanceError):
        result.coordinates = ()


@pytest.mark.parametrize("complementary", (False, True))
def test_projective_pivots_and_homogeneous_scalings_preserve_exact_weight(complementary):
    x, u, p = (((1, 1, 1), (1, -1, 0), (1, 0)) if complementary
               else ((1, -1, 0), (1, 1, 1), (0, 1)))
    p_pivot = 0 if complementary else 1
    values = []
    # All nonzero pivots, with explicitly ascending remaining coordinate order.
    for xp, up in product(tuple(i for i, q in enumerate(x) if q),
                          tuple(i for i, q in enumerate(u) if q)):
        xs = tuple(i for i in range(3) if i != xp)[1]
        us = tuple(i for i in range(3) if i != up)[1]
        chart = measure.ProjectionChart(xp, xs, up, us, p_pivot)
        point = measure.CoverPoint(x, u, p, chart.pivots)
        value = weights.local_weight(point, chart, volume_scale=1, covering_degree=9, bits=80)
        values.append(value.cover_weight_without_pi_cubed)
        scale_x, scale_u, scale_p = Eisenstein(2, 1), Eisenstein(1, 2), OMEGA
        rescaled = measure.CoverPoint(tuple(scale_x * q for q in x),
                                      tuple(scale_u * q for q in u),
                                      tuple(scale_p * q for q in p), chart.pivots)
        assert weights.local_weight(rescaled, chart, volume_scale=1,
                                     covering_degree=9, bits=80) == value
    assert len(values) == 6
    assert all(v == values[0] for v in values)


def test_refinement_and_explicit_projective_plane_order():
    chart = measure.ProjectionChart(0, 2, 0, 2, 0)
    point = bounds.BoundedCoverPoint(_regular("finite_chart"), (0, 0), chart.pivots, 80)
    fine = bounds.BoundedCoverPoint(_regular("finite_chart", True), (0, 0), chart.pivots, 80)
    original = weights.local_weight(point, chart, volume_scale=1, covering_degree=9, bits=80)
    refined = weights.local_weight(fine, chart, volume_scale=1, covering_degree=9, bits=80)
    assert refined.cover_weight_without_pi_cubed.width < (
        original.cover_weight_without_pi_cubed.width
    )
    reordered = weights.local_weight(point, replace(chart, x_solve=1, u_solve=1),
                                      volume_scale=1, covering_degree=9, bits=80)
    assert reordered.cover_weight_without_pi_cubed == original.cover_weight_without_pi_cubed
    assert reordered.denominator == original.denominator


@pytest.mark.parametrize("argument,value", (("covering_degree", False), ("covering_degree", 0),
    ("volume_scale", 0), ("bits", True), ("bits", 0)))
def test_invalid_precision_or_normalization_fails_closed(argument, value):
    chart = measure.ProjectionChart(0, 2, 0, 2, 0)
    point = bounds.BoundedCoverPoint(_regular("finite_chart"), (0, 0), chart.pivots, 80)
    kwargs = dict(volume_scale=1, covering_degree=9, bits=80)
    kwargs[argument] = value
    with pytest.raises(ValueError):
        weights.local_weight(point, chart, **kwargs)


def test_membership_and_positivity_are_not_replaced_by_centers_or_fallback(monkeypatch):
    chart = measure.ProjectionChart(0, 2, 0, 2, 0)
    point = bounds.BoundedCoverPoint(_regular("finite_chart"), (0, 0), chart.pivots, 80)
    with pytest.raises(TypeError, match="certified exact or bounded"):
        weights.local_weight(tuple(c.center for c in point.x), chart,
                             volume_scale=1, covering_degree=9, bits=80)
    with pytest.raises(ValueError, match="identical explicit chart pivots"):
        weights.local_weight(point, replace(chart, p_pivot=1),
                             volume_scale=1, covering_degree=9, bits=80)
    # Deliberate failed-Jacobian attack, not an alternative physical equation.
    monkeypatch.setattr(bounds, "polynomial_value", lambda *_: bounds.Ball(Eisenstein(0),
                                                                        Rational(0), 80))
    with pytest.raises(ValueError, match="positive full conormal determinant"):
        weights.local_weight(point, chart, volume_scale=1, covering_degree=9, bits=80)


def test_saved_projection_free_artifact_reproduces_without_global_scope_inflation():
    payload = weights.weight_artifact()
    assert payload == json.loads(weights.OUTPUT.read_text())
    assert payload["actual_domain_count"] == 36
    assert sum(len(p["records"]) for p in payload["actual_domain_probes"]) == 36
    assert payload["projection_free_weight_identity_derived"] is True
    assert payload["individual_projection_inverses_required"] is False
    assert hashlib.sha256((measure.ROOT / payload["proof"]).read_bytes()).hexdigest() == (
        payload["proof_sha256"]
    )
    for flag in ("all_triangle_node_inputs_certified", "complete_global_input_coverage_certified",
                 "quantitative_global_weight_bound_available",
                 "controlled_numerical_sampling_available",
                 "numerical_metrics_available", "physical_yukawas_available", "vacuum_selected",
                 "physical_kahler_class_selected", "extension_point_selected",
                 "observational_inputs_used"):
        assert payload[flag] is False
