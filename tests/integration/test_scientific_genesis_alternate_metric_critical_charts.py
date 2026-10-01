"""Attack signed base-eliminating charts on the unchanged actual cover.

Owns:
    Independent full wedge determinants, tangent identities, FS densities,
    overlap Jacobians, actual axis-root membership, and scope rejection.

Depends on:
    Exact Matrix arithmetic and the existing certified root and density engines.

Must not:
    Treat functional disk perturbations as cover points or uniform samples,
    certify unprovided triangle inputs, or infer a global atlas or physical metric.

Phase 0:
    Critical-coordinate research regressions; physical normalization is open.
"""

import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from functools import cache

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.scientific_genesis import alternate_metric_critical_charts as critical

positive, bounds, roots, measure = (
    critical.positive, critical.bounds, critical.roots, critical.measure,
)


@cache
def _configuration(side, axis, refined=False):
    policy = roots.RootPolicy(Rational(1, 2**(36 if refined else 30)),
                              72 if refined else 60, 80, 128)
    return critical.configuration(tuple(int(i == axis) for i in range(3)),
        roots.ProjectiveLine((1, 0, 0), (0, 1, 1)), source_side=side,
        parameter_pivot=0, policy=policy)


def _chart(side, axis):
    remaining = tuple(i for i in range(3) if i != axis)
    return (measure.ProjectionChart(axis, remaining[1], 0, 2, 0) if side == 1
            else measure.ProjectionChart(0, 2, axis, remaining[1], 0))


def _exact(chart, coordinates, side):
    """Independent exact full ambient Jacobian, solved tangent, and FS Gram."""

    f, g = measure.projection_polynomials(chart)
    gradients = tuple(tuple(measure._value(poly.derivative(i), coordinates) for i in range(5))
                      for poly in (f, g))
    fs, fz, _, _, ft = gradients[0]
    _, _, gr, gw, gt = gradients[1]
    if side == 1:
        ts, tz = -fs / ft, -fz / ft
        tangent = ((1, 0, 0), (0, 1, 0), (0, 0, 1),
                   (-gt * ts / gw, -gt * tz / gw, -gr / gw), (ts, tz, 0))
        free = (0, 1, 2)
    else:
        tr, tw = -gr / gt, -gw / gt
        tangent = ((0, 0, 1), (-ft * tr / fz, -ft * tw / fz, -fs / fz),
                   (1, 0, 0), (0, 1, 0), (tr, tw, 0))
        free = (2, 3, 0)
    tangent = Matrix(tangent, scalar_type=Eisenstein)
    wedge = Matrix((*gradients, *(tuple(int(i == j) for i in range(5)) for j in free)),
                   scalar_type=Eisenstein).determinant()
    assert wedge == (-ft * gw if side == 1 else fz * gt)
    assert Matrix(gradients, scalar_type=Eisenstein).matmul(tangent).is_zero()
    h = Eisenstein(chart.ambient_sign) / wedge
    density = _exact_density(coordinates, tangent.rows)
    return wedge, h, density, tangent, free


def _exact_density(coordinates, tangent):
    """Build one exact ambient block metric before its tangent pullback."""

    ambient = [[Eisenstein(0) for _ in range(5)] for _ in range(5)]
    for indices in ((0, 1), (2, 3), (4,)):
        norm = Rational(1) + sum((coordinates[i].norm() for i in indices), Rational(0))
        for i in indices:
            for j in indices:
                ambient[i][j] = (Eisenstein(norm * int(i == j))
                                 - coordinates[i] * coordinates[j].conjugate()) / norm**2
    t = Matrix(tangent, scalar_type=Eisenstein)
    adjoint = Matrix(tuple(tuple(v.conjugate() for v in col)
                           for col in zip(*tangent, strict=True)), scalar_type=Eisenstein)
    determinant = adjoint.matmul(Matrix(ambient, scalar_type=Eisenstein)).matmul(t).determinant()
    assert determinant.b.is_zero()
    assert determinant.a > 0
    return 6 * determinant.a


@pytest.mark.parametrize("side,axis", tuple((s, a) for s in (1, 2) for a in range(3)))
def test_all_actual_axis_fibers_have_complete_nonvanishing_critical_charts(side, axis):
    configuration = _configuration(side, axis)
    chart = _chart(side, axis)
    assert configuration.partner.count == 3
    assert len(configuration.root_pairs) == 3
    assert configuration.partner.homogeneous == roots.restrict_pencil(
        configuration.partner_line, configuration.p, 3 - side,
    )
    for pair in configuration.root_pairs:
        point = bounds.BoundedCoverPoint(configuration, pair, chart.pivots, 80)
        result = critical.local_measure(point, chart, source_side=side, volume_scale=1,
                                         covering_degree=9, bits=80)
        f, g = measure.projection_polynomials(chart)
        source = f if side == 1 else g
        indices = (0, 1) if side == 1 else (2, 3)
        assert all(bounds.polynomial_value(source.derivative(i), result.coordinates).radius == 0
                   and bounds.polynomial_value(source.derivative(i), result.coordinates).center
                   == Eisenstein(0) for i in indices)
        base = bounds.polynomial_value(source.derivative(4), result.coordinates)
        assert base.radius == 0 and not base.center.is_zero()
        assert result.positive_density_times_pi_cubed.lower > 0
        with pytest.raises(ZeroDivisionError):
            positive.bounded_positive_measure(point, chart, volume_scale=1,
                                               covering_degree=9, bits=80)
        # Centers and circular perturbations are FUNCTIONALS, not cover inputs.
        for direction in (Eisenstein(0), Eisenstein(1), OMEGA, OMEGA**2):
            coordinates = tuple(c.center + direction * c.radius for c in result.coordinates)
            wedge, h, density, tangent, free = _exact(chart, coordinates, side)
            # Separate positive Gram-minor identity: at an axis node the
            # source FS block is I_2 and the base tangent is zero. Only the
            # partner curve norm enters; no 3x3 determinant is used here.
            i, j = (2, 3) if side == 1 else (0, 1)
            q, v = coordinates[i], coordinates[j]
            derivative = tangent.rows[j][2]
            curve = (1 + derivative.norm() + (q * derivative - v).norm()) / (
                1 + q.norm() + v.norm()
            )**2
            assert density == 6 * curve
            assert free == result.free_coordinate_indices
            assert result.wedge_jacobian.contains(wedge)
            assert result.residue.contains(h)
            assert result.omega_density.contains(h.norm())
            assert result.positive_density_times_pi_cubed.contains(density)
            assert result.cover_weight_without_pi_cubed.contains(72 * h.norm() / density)
            assert result.quotient_weight_without_pi_cubed.contains(8 * h.norm() / density)


@pytest.mark.parametrize("side", (1, 2))
def test_regular_overlap_uses_named_jacobian_and_same_weight(side):
    policy = roots.RootPolicy(Rational(1, 2**30), 60, 80, 128)
    intersection = roots.intersection_roots(
        roots.ProjectiveLine((1, 0, 0), (0, 1, 1)),
        roots.ProjectiveLine((1, 1, 0), (0, 0, 1)), (1, 1),
        parameter_pivots=(0, 0), policy=policy)
    chart = measure.ProjectionChart(0, 2, 0, 2, 0)
    point = bounds.BoundedCoverPoint(intersection, (0, 0), chart.pivots, 80)
    result = critical.local_measure(point, chart, source_side=side, volume_scale=1,
                                     covering_degree=9, bits=80)
    regular = positive.bounded_positive_measure(point, chart, volume_scale=1,
                                                 covering_degree=9, bits=80)
    coordinates = tuple(c.center for c in result.coordinates)
    _, h, density, _, free = _exact(chart, coordinates, side)
    f, g = measure.projection_polynomials(chart)
    fs, fz, ft = (measure._value(f.derivative(i), coordinates) for i in (0, 1, 4))
    gr, gw, gt = (measure._value(g.derivative(i), coordinates) for i in (2, 3, 4))
    old_t = ((1, 0, 0), (-fs / fz, 0, -ft / fz), (0, 1, 0),
             (0, -gr / gw, -gt / gw), (0, 0, 1))
    jacobian = Matrix(tuple(old_t[i] for i in free), scalar_type=Eisenstein).determinant()
    old_h = Eisenstein(-chart.ambient_sign) / (fz * gw)
    old_density = _exact_density(coordinates, old_t)
    assert h * jacobian == old_h
    assert density * jacobian.norm() == old_density
    weight = 72 * h.norm() / density
    assert weight == 72 * old_h.norm() / old_density
    assert result.cover_weight_without_pi_cubed.contains(weight)
    assert regular["cover_weight_without_pi_cubed"].contains(weight)


@pytest.mark.parametrize("side", (1, 2))
def test_refinement_scaling_degree_and_immutability_are_explicit(side):
    chart = _chart(side, 0)
    pair = _configuration(side, 0).root_pairs[0]
    point = bounds.BoundedCoverPoint(_configuration(side, 0), pair, chart.pivots, 80)
    result = critical.local_measure(point, chart, source_side=side, volume_scale=1,
                                     covering_degree=9, bits=80)
    finer = bounds.BoundedCoverPoint(_configuration(side, 0, True), pair, chart.pivots, 80)
    refined = critical.local_measure(finer, chart, source_side=side, volume_scale=1,
                                      covering_degree=9, bits=80)
    assert refined.positive_density_times_pi_cubed.width < (
        result.positive_density_times_pi_cubed.width
    )
    scaled = critical.local_measure(point, chart, source_side=side, volume_scale=2,
                                     covering_degree=1, bits=80)
    assert scaled.positive_density_times_pi_cubed == result.positive_density_times_pi_cubed
    assert scaled.residue.center == 2 * result.residue.center
    _, h, density, _, _ = _exact(chart, tuple(c.center for c in result.coordinates), side)
    # Outward dyadic rounding need not commute with multiplication by four.
    assert scaled.omega_density.contains(4 * h.norm())
    assert scaled.cover_weight_without_pi_cubed.contains(288 * h.norm() / density)
    assert scaled.quotient_weight_without_pi_cubed == scaled.cover_weight_without_pi_cubed
    with pytest.raises(FrozenInstanceError):
        result.source_side = 3
    with pytest.raises(FrozenInstanceError):
        point.intersection.source_side = 3


@pytest.mark.parametrize("side", (1, 2))
def test_base_pivot_transition_preserves_signed_residue_and_weight(side):
    configuration = _configuration(side, 0)
    chart = _chart(side, 0)
    other_chart = replace(chart, p_pivot=1)
    pair = configuration.root_pairs[0]
    local = critical.local_measure(
        bounds.BoundedCoverPoint(configuration, pair, chart.pivots, 80), chart,
        source_side=side, volume_scale=1, covering_degree=9, bits=80)
    other = critical.local_measure(
        bounds.BoundedCoverPoint(configuration, pair, other_chart.pivots, 80), other_chart,
        source_side=side, volume_scale=1, covering_degree=9, bits=80)
    coordinates = tuple(c.center for c in local.coordinates)
    other_coordinates = tuple(c.center for c in other.coordinates)
    assert other_coordinates[:4] == coordinates[:4]
    assert other_coordinates[4] * coordinates[4] == Eisenstein(1)
    _, h, density, _, _ = _exact(chart, coordinates, side)
    _, other_h, other_density, _, _ = _exact(other_chart, other_coordinates, side)
    assert other_h == h
    assert other_density == density
    assert other.residue.contains(h)
    assert other.quotient_weight_without_pi_cubed.contains(8 * h.norm() / density)


def test_point_line_infinity_branch_remains_an_actual_projective_root():
    policy = roots.RootPolicy(Rational(1, 2**30), 60, 80, 128)
    configuration = critical.configuration((1, 1, 1),
        roots.ProjectiveLine((1, 0, 0), (0, 1, -1)), source_side=1,
        parameter_pivot=0, policy=policy)
    assert configuration.partner.count == 3
    assert configuration.partner.infinity_multiplicity == 1
    assert ("fixed", "infinity") in configuration.root_pairs
    chart = measure.ProjectionChart(0, 2, 1, 0, 0)
    point = bounds.BoundedCoverPoint(configuration, ("fixed", "infinity"), chart.pivots, 80)
    assert all(c.radius == 0 for c in (*point.x, *point.u, *point.p))
    exact = measure.CoverPoint(tuple(c.center for c in point.x),
                              tuple(c.center for c in point.u),
                              tuple(c.center for c in point.p), chart.pivots)
    result = critical.local_measure(point, chart, source_side=1, volume_scale=1,
                                     covering_degree=9, bits=80)
    _, h, density, _, _ = _exact(chart, chart.coordinates(exact), 1)
    assert result.residue.center == h and result.residue.radius == 0
    assert result.positive_density_times_pi_cubed.lower == density
    assert result.positive_density_times_pi_cubed.upper == density


@pytest.mark.parametrize("side", (1, 2))
def test_exact_source_and_actual_partner_membership_cannot_be_forged(side):
    original = _configuration(side, 0)
    with pytest.raises(TypeError, match="immutable explicitly based partner line"):
        replace(original, partner_line=object())
    with pytest.raises(ValueError, match="actual cover equation"):
        replace(original, p=(Eisenstein(1), Eisenstein(1)))
    with pytest.raises(ValueError, match="other-pencil restriction"):
        replace(original, partner=_configuration(3 - side, 0).partner)
    with pytest.raises(ValueError, match="root pair is absent"):
        bounds.BoundedCoverPoint(original, (0, 0), _chart(side, 0).pivots, 80)
    chart = _chart(side, 0)
    point = bounds.BoundedCoverPoint(original, original.root_pairs[0], chart.pivots, 80)
    with pytest.raises(ValueError, match="identical explicit chart pivots"):
        critical.local_measure(point, replace(chart, p_pivot=1), source_side=side,
                               volume_scale=1, covering_degree=9, bits=80)
    with pytest.raises(ValueError, match="incompatible declared bound precisions"):
        critical.local_measure(point, chart, source_side=side, volume_scale=1,
                               covering_degree=9, bits=72)
    with pytest.raises(TypeError, match="certified exact or bounded"):
        critical.local_measure(tuple(c.center for c in point.x), chart, source_side=side,
                               volume_scale=1, covering_degree=9, bits=80)


@pytest.mark.parametrize("argument,value", (("source_side", False), ("source_side", 0),
    ("covering_degree", True), ("covering_degree", 0), ("volume_scale", 0)))
def test_invalid_normalization_never_gets_a_fallback(argument, value):
    chart = _chart(1, 0)
    configuration = _configuration(1, 0)
    point = bounds.BoundedCoverPoint(configuration, configuration.root_pairs[0], chart.pivots, 80)
    kwargs = dict(source_side=1, volume_scale=1, covering_degree=9, bits=80)
    kwargs[argument] = value
    with pytest.raises(ValueError):
        critical.local_measure(point, chart, **kwargs)


def test_actual_artifact_reproduces_without_inflating_global_scope():
    payload = critical.critical_artifact()
    assert payload == json.loads(critical.OUTPUT.read_text())
    assert payload["schema"] == "alternate-metric-critical-charts-v1"
    assert hashlib.sha256((measure.ROOT / payload["proof"]).read_bytes()).hexdigest() == (
        payload["proof_sha256"]
    )
    assert [(p["source_side"], p["source_axis"]) for p in payload["actual_axis_fiber_probes"]] == (
        [(s, a) for s in (1, 2) for a in range(3)]
    )
    assert all(len(p["all_three_critical_chart_records"]) == 3
               for p in payload["actual_axis_fiber_probes"])
    for flag in ("all_triangle_node_inputs_certified", "complete_global_atlas_coverage_certified",
                 "quantitative_global_weight_bound_available",
                 "controlled_numerical_sampling_available",
                 "numerical_metrics_available", "physical_yukawas_available", "vacuum_selected",
                 "physical_kahler_class_selected", "extension_point_selected",
                 "observational_inputs_used"):
        assert payload[flag] is False
