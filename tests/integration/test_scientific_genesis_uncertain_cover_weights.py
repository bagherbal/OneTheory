"""Independently verify auxiliary weights on coupled uncertain cover families.

Owns:
    Full FS matrix determinant checks, homogeneous rescaling, admitted-domain
    interval checks, source-coupling rejection, refinement, and explicit errors.

Depends on:
    Original actual equations and exact points, exact matrix algebra, certified
    uncertain root families, and the existing auxiliary weight convention.

Must not:
    Treat coordinate functionals as cover points, sample or select physical
    moduli, infer integrals from probes, or claim physical normalization.

Phase 0:
    Integration weight tests only; sampling and metric convergence remain open.
"""

import json
from dataclasses import replace
from fractions import Fraction
from functools import cache
from itertools import product

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.scientific_genesis import alternate_metric_measure as measure
from research.experiments.scientific_genesis import projective_uncertain_intersections as roots
from research.experiments.scientific_genesis import uncertain_cover_weights as weights
from research.experiments.scientific_genesis.projective_uniform_input_cells import (
    InputPolicy,
    projective_input_cell,
)


def _balls(values):
    return tuple(roots.Ball(Eisenstein.coerce(value), Rational(0), 100) for value in values)


@cache
def _configurations():
    return weights.declared_configurations()


def _adjoint(matrix):
    return Matrix(tuple(tuple(c.conjugate() for c in column)
                        for column in zip(*matrix.rows, strict=True)), scalar_type=Eisenstein)


def _full_ambient_denominator(point, chart):
    """A separate 5x5 ambient inverse and 2x2 Gram determinant, not the sparse sum."""

    q = chart.coordinates(point)
    f, g = measure.projection_polynomials(chart)
    jacobian = Matrix(tuple(tuple(measure._value(equation.derivative(i), q)
                                  for i in range(5)) for equation in (f, g)),
                      scalar_type=Eisenstein)
    entries = [[Eisenstein(0) for _ in range(5)] for _ in range(5)]
    for indices in ((0, 1), (2, 3), (4,)):
        norm = Rational(1) + sum((q[i].norm() for i in indices), Rational(0))
        for i in indices:
            for j in indices:
                entries[i][j] = (Eisenstein(norm * int(i == j))
                                  - q[i] * q[j].conjugate()) / norm**2
    metric = Matrix(entries, scalar_type=Eisenstein)
    conormal = jacobian @ metric.inverse() @ _adjoint(jacobian)
    value = metric.determinant() * conormal.determinant()
    assert value.b.is_zero()
    return value.a


@pytest.mark.parametrize("x,u,p", (
    ((1, -1, 0), (1, 1, 1), (0, 1)),
    ((1, 1, 1), (1, -1, 0), (1, 0)),
    ((1, -OMEGA, 0), (1, OMEGA, OMEGA**2), (0, 1)),
    ((1, OMEGA, OMEGA**2), (1, -OMEGA, 0), (1, 0)),
))
def test_exact_actual_weight_matches_full_fs_determinant_in_every_valid_chart(x, u, p):
    actual = weights._weight_bounds(tuple(_balls(group) for group in (x, u, p)),
                                    volume_scale=1, covering_degree=9)
    count = 0
    for xp, up, pp in product(range(3), range(3), range(2)):
        if x[xp] == 0 or u[up] == 0 or p[pp] == 0:
            continue
        point = measure.CoverPoint(x, u, p, (xp, up, pp))
        xs, us = max(set(range(3)) - {xp}), max(set(range(3)) - {up})
        chart = measure.ProjectionChart(xp, xs, up, us, pp)
        expected = _full_ambient_denominator(point, chart)
        assert actual.denominator.lower == actual.denominator.upper == expected
        assert actual.cover_weight_without_pi_cubed.lower == 12 / expected
        assert actual.quotient_weight_without_pi_cubed.lower == Rational(4, 3) / expected
        count += 1
    assert count == 6


@pytest.mark.parametrize("scales", ((2, 3, 5), (OMEGA, Eisenstein(2, 1), Eisenstein(-1, 2))))
def test_homogeneous_rescaling_does_not_select_a_normalization(scales):
    point = tuple(_balls(group) for group in ((1, -1, 0), (1, 1, 1), (0, 1)))
    original = weights._weight_bounds(point, volume_scale=1, covering_degree=9)
    scaled = tuple(tuple(value * scale for value in group)
                   for group, scale in zip(point, scales, strict=True))
    actual = weights._weight_bounds(scaled, volume_scale=1, covering_degree=9)
    assert actual.denominator == original.denominator
    assert actual.cover_weight_without_pi_cubed == original.cover_weight_without_pi_cubed


@pytest.mark.parametrize("component,count", ((0, 9), (1, 3), (2, 3)))
def test_all_coupled_component_branches_have_positive_weight_intervals(component, count):
    values = weights.configuration_weights(_configurations()[component],
                                            volume_scale=1, covering_degree=9)
    assert len(values) == count
    for value in values:
        assert all(norm.lower > 0 for norm in value.homogeneous_squared_norms)
        assert value.denominator.lower > 0
        assert value.cover_weight_without_pi_cubed.lower > 0
        quotient = value.quotient_weight_without_pi_cubed
        cover = value.cover_weight_without_pi_cubed
        assert quotient.lower <= cover.lower / 9
        assert quotient.upper >= cover.upper / 9


def test_declared_scale_and_covering_degree_are_separate_from_geometry():
    config = _configurations()[1]
    original = weights.configuration_weights(config, volume_scale=1, covering_degree=9)
    scaled = weights.configuration_weights(config, volume_scale=Eisenstein(2, 1), covering_degree=3)
    for a, b in zip(original, scaled, strict=True):
        assert a.denominator == b.denominator
        # Compare to exact endpoint quotients, not rescaled already-rounded
        # intervals: two sound outward roundings need not contain one another.
        for interval, numerator in (
            (a.cover_weight_without_pi_cubed, Rational(12)),
            (a.quotient_weight_without_pi_cubed, Rational(4, 3)),
            (b.cover_weight_without_pi_cubed, Rational(36)),
            (b.quotient_weight_without_pi_cubed, Rational(12)),
        ):
            assert interval.lower <= numerator / a.denominator.upper
            assert interval.upper >= numerator / a.denominator.lower


def test_axis_critical_family_requires_no_individual_plane_gradient_inverse():
    source = _balls((1, 0, 0))
    line = roots.BoundedLine(_balls((0, -1, 1)), 2, (0, 1))
    _, partner = roots.point_line(source, line, source_side=1, parameter_pivot=0,
        policy=roots.roots.RootPolicy(Rational(1, 4096), 64, 100, 128))
    configuration = roots.PointLineConfiguration(source, 1, line, partner)
    actual = weights.configuration_weights(configuration, volume_scale=1, covering_degree=9)
    assert len(actual) == 3
    for value in actual:
        ex, eu, hx, _hu = value.normalized_conormal_terms
        assert ex.lower == ex.upper == 0
        assert eu.lower > 0 and hx.lower > 0
        assert value.denominator.lower > 0


def test_refined_original_input_prefix_and_root_radius_contract_weights():
    config = _configurations()[1]
    x, u, _p = roots.declared_probes()[0]
    policy = InputPolicy(44, 100, 40, 56)
    refined = tuple(projective_input_cell(tuple(k * 16 + 7 for k in cell.spacing_indices),
        tuple(k * 16 + 7 for k in cell.phase_indices), policy=policy) for cell in (x, u))
    line = roots.BoundedLine(refined[1].coordinates, 0, (1, 2))
    _, partner = roots.point_line(refined[0].coordinates, line, source_side=1, parameter_pivot=0,
        policy=roots.roots.RootPolicy(Rational(1, 2**16), 72, 100, 128))
    finer = roots.PointLineConfiguration(refined[0].coordinates, 1, line, partner)
    coarse_weights = weights.configuration_weights(config, volume_scale=1, covering_degree=9)
    fine_weights = weights.configuration_weights(finer, volume_scale=1, covering_degree=9)
    for coarse, fine in zip(coarse_weights, fine_weights, strict=True):
        old, new = coarse.cover_weight_without_pi_cubed, fine.cover_weight_without_pi_cubed
        assert new.width < old.width / 8
        assert new.lower >= old.lower
        assert new.upper <= old.upper


def test_bare_coordinate_balls_are_not_membership_certificates():
    point = _configurations()[0].points[0]
    with pytest.raises(TypeError, match="actual coupled"):
        weights.configuration_weights(point, volume_scale=1, covering_degree=9)


def test_recombining_incompatible_root_and_base_families_fails():
    config = _configurations()[0]
    changed = tuple(value * 2 if i == 0 else value for i, value in enumerate(config.base))
    with pytest.raises(ValueError, match="actual same-base"):
        replace(config, base=changed)
    with pytest.raises(ValueError, match="source-derived"):
        replace(_configurations()[1], partner=config.first)


@pytest.mark.parametrize("scale,degree", ((0, 9), (1, 0), (1, -1), (1, True)))
def test_invalid_explicit_normalization_fails(scale, degree):
    with pytest.raises(ValueError):
        weights.configuration_weights(
            _configurations()[1], volume_scale=scale, covering_degree=degree,
        )


def test_uncertified_homogeneous_norm_cannot_be_inverted():
    zero = _balls((0, 0, 0))
    with pytest.raises(ValueError, match="nonzero homogeneous"):
        weights._weight_bounds((zero, _balls((1, 1, 1)), _balls((0, 1))),
                               volume_scale=1, covering_degree=9)


def test_coarse_conormal_bounds_fail_without_automatic_precision_or_fallback():
    point = tuple(tuple(roots.Ball(Eisenstein(value), Rational(0 if i == anchor else 20), 16)
                        for i, value in enumerate(group))
                  for group, anchor in zip(((1, -1, 0), (1, 1, 1), (0, 1)), (0, 0, 1),
                                            strict=True))
    with pytest.raises(ValueError, match="positive full conormal denominator"):
        weights._weight_bounds(point, volume_scale=1, covering_degree=9)
    assert all(value.bits == 16 for group in point for value in group)


def _fraction(value):
    return Fraction(value.numerator, value.denominator)


def _pair(value):
    return _fraction(value.a), _fraction(value.b)


def _add(a, b):
    return a[0] + b[0], a[1] + b[1]


def _multiply(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0] - a[1] * b[1]


def _scale(a, scalar):
    return a[0] * scalar, a[1] * scalar


def _sum(values):
    result = Fraction(0), Fraction(0)
    for value in values:
        result = _add(result, value)
    return result


def _norm_pair(value):
    return value[0]**2 - value[0] * value[1] + value[1]**2


def _literal_pencil(values):
    """Independent original coefficient stencil: no Polynomial, Ball or derivatives."""

    fc = ((-3, -3), (3, 0), (0, 3))
    gc, mixed = (-3, -6), (36, 18)
    square = tuple(_multiply(value, value) for value in values)
    cube = tuple(_multiply(value, value2) for value, value2 in zip(values, square, strict=True))
    f = _sum(_multiply(c, value) for c, value in zip(fc, cube, strict=True))
    g = _add(_multiply(gc, _sum(cube)),
             _multiply(mixed, _multiply(_multiply(values[0], values[1]), values[2])))
    df = tuple(_scale(_multiply(c, value), 3) for c, value in zip(fc, square, strict=True))
    dg = tuple(_add(_scale(_multiply(gc, square[i]), 3),
                    _multiply(mixed, _multiply(values[(i + 1) % 3], values[(i + 2) % 3])))
               for i in range(3))
    return f, g, df, dg


def _literal_terms(point):
    x, u, p = point
    fx, gx, dfx, dgx = _literal_pencil(x)
    fu, gu, dfu, dgu = _literal_pencil(u)
    nx, nu, np = (sum((_norm_pair(value) for value in group), Fraction(0))
                  for group in point)
    dx = tuple(_add(_multiply(a, p[0]), _multiply(b, p[1]))
               for a, b in zip(dfx, dgx, strict=True))
    du = tuple(_add(_multiply(a, _scale(p[1], 2)), _multiply(b, p[0]))
               for a, b in zip(dfu, dgu, strict=True))
    ex = sum((_norm_pair(v) for v in dx), Fraction(0)) / (nx**2 * np)
    eu = sum((_norm_pair(v) for v in du), Fraction(0)) / (nu**2 * np)
    hx = (_norm_pair(fx) + _norm_pair(gx)) / nx**3
    hu = (_norm_pair(gu) + 4 * _norm_pair(fu)) / nu**3
    return (nx, nu, np), (ex, eu, hx, hu), ex * eu + ex * hu + eu * hx


@pytest.mark.parametrize("direction", ((1, 0), (-1, 0), (0, 1), (0, -1)))
def test_fraction_pair_coordinate_functionals_stay_in_all_propagated_bounds(direction):
    """Off-cover corners test arithmetic only; no corner is admitted as a cover point."""

    for configuration in _configurations():
        for bounded in weights.configuration_weights(configuration, volume_scale=1,
                                                       covering_degree=9):
            point = tuple(tuple(_add(_pair(value.center),
                _scale(direction, _fraction(value.radius))) for value in group)
                          for group in bounded.coordinates)
            norms, terms, denominator = _literal_terms(point)
            expected = (*norms, *terms, denominator, 12 / denominator,
                        Fraction(4, 3) / denominator)
            intervals = (*bounded.homogeneous_squared_norms, *bounded.normalized_conormal_terms,
                         bounded.denominator, bounded.cover_weight_without_pi_cubed,
                         bounded.quotient_weight_without_pi_cubed)
            for interval, value in zip(intervals, expected, strict=True):
                assert _fraction(interval.lower) <= value <= _fraction(interval.upper)


def test_saved_weight_packet_recomputes_the_actual_membership_and_all_bounds():
    record = weights.read_weights()
    assert tuple(c["complete_branch_count"] for c in record["components"]) == (9, 3, 3)
    assert record["actual_coupled_family_membership_checked"]
    assert not record["controlled_integral_available"]
    assert not record["physical_yukawas_available"]


def test_governing_dag_keeps_actual_weights_separate_from_missing_metric_requirements():
    from research.experiments.scientific_genesis import audit

    nodes = {node["id"]: node for node in audit._nodes()}
    node = nodes["uncertain_cover_weights"]
    assert node["status"] == "COMPUTED"
    assert nodes["visible_metrics"]["status"] == "BLOCKED"
    pairs = {(edge["source"], edge["target"]) for edge in audit._edges()}
    assert ("projective_uncertain_intersections", "uncertain_cover_weights") in pairs
    assert ("alternate_metric_projection_free_weights", "uncertain_cover_weights") in pairs
    assert ("alternate_metric_global_weight_bound", "uncertain_cover_weights") in pairs
    assert ("uncertain_cover_weights", "visible_metrics") in pairs


@pytest.mark.parametrize("attack", ("scope", "bound", "coordinate", "degree", "parent"))
def test_rehashed_weight_scope_or_scientific_input_changes_are_rejected(tmp_path, attack):
    record = json.loads(weights.OUTPUT.read_text(encoding="utf-8"))
    record.pop("artifact_digest")
    if attack == "scope":
        record["physical_yukawas_available"] = True
    elif attack == "bound":
        record["components"][0]["weights"][0]["denominator"]["lower"] = "1"
    elif attack == "coordinate":
        record["components"][0]["weights"][0]["coupled_cover_bounds"][0][0]["radius"] = "0"
    elif attack == "degree":
        record["covering_degree"] = 1
    else:
        record["uncertain_root_parent_digest"] = "0" * 64
    record["artifact_digest"] = roots._digest(record)
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="coupling, bounds, inputs or scope"):
        weights.read_weights(path)
