"""Attack local error bounds independently of root-center residuals.

Owns:
    Exact endpoint/circle perturbation checks, independent FS Gram identities,
    actual Laurent-section comparisons, infinity charts, and error refinement.

Depends on:
    Exact arithmetic, actual geometric certificates and section archives,
    and the research enclosure implementation.

Must not:
    Interpret test perturbations as physical samples, infer bundle metrics,
    accept possible zero denominators, or replace actual section coefficients.

Phase 0:
    Local bound tests only; sampling and universal fiber-frame bounds are open.
"""

import hashlib
import json
from dataclasses import FrozenInstanceError, replace

import pytest

from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from onetheory.math.polynomials import Polynomial
from research.experiments.scientific_genesis import alternate_metric_enclosures as bounds
from research.experiments.scientific_genesis import alternate_metric_fiber_evaluation as fiber
from research.experiments.scientific_genesis.alternate_metric_measure import (
    ProjectionChart,
    local_measure,
    projection_polynomials,
)

roots = bounds.roots


def _intersection(radius_bits=30, infinity=False):
    first = roots.ProjectiveLine((1, 0, 0), (0, 1, -1 if infinity else 1))
    second = roots.ProjectiveLine((1, 1, 0), (0, 0, 1))
    policy = roots.RootPolicy(Rational(1, 2**radius_bits), 2 * radius_bits,
                              2 * radius_bits + 20, 128)
    return roots.intersection_roots(first, second, (0, 1) if infinity else (1, 1),
                                    parameter_pivots=(0, 0), policy=policy)


def _point(intersection, pair):
    xp, xs = (1, 0) if pair[0] == "infinity" else (0, 2)
    pp = 1 if intersection.p[0].is_zero() else 0
    chart = ProjectionChart(xp, xs, 0, 2, pp)
    return bounds.BoundedCoverPoint(intersection, pair, chart.pivots, 120), chart


def _measure(point, chart):
    return bounds.bounded_local_measure(point, chart, volume_scale=Eisenstein(1),
                                        covering_degree=9, bits=point.bits)


def _exact_density(coordinates, chart):
    """Exact ambient-functional check using the Gram formula, not ball operations."""

    def value(polynomial):
        return Eisenstein.coerce(polynomial.substitute(coordinates).coefficient(()))

    f, g = projection_polynomials(chart)
    fs, fz = (value(f.derivative(i)) for i in (0, 1))
    gr, gw = (value(g.derivative(i)) for i in (2, 3))
    s, z, r, w, t = coordinates
    v, q = -fs / fz, -gr / gw

    def gram(a, b, derivative):
        potential = 1 + a.norm() + b.norm()
        length = 1 + derivative.norm()
        inner = a.conjugate() + b.conjugate() * derivative
        return (potential * length - inner.norm()) / potential**2

    auxiliary = gram(s, z, v) * gram(r, w, q) / (1 + t.norm())**2
    residue = Eisenstein(-chart.ambient_sign) / (fz * gw)
    return residue, residue.norm(), auxiliary, residue.norm() / auxiliary


def _circle_points(ball):
    # Exact functionals testing arithmetic inclusion, not geometric samples.
    return tuple(ball.center + Eisenstein(ball.radius) * direction
                 for direction in (Eisenstein(0), Eisenstein(1), OMEGA, OMEGA**2,
                                   Eisenstein(Rational(1, 2), Rational(1, 2))))


@pytest.mark.parametrize("center", (Eisenstein(2, 1), Eisenstein(-3, 2),
                                    Eisenstein(Rational(1, 7), Rational(-3, 11))))
def test_complex_ball_arithmetic_contains_independent_exact_circle_values(center):
    left = bounds.Ball(center, Rational(1, 1024), 80)
    right = bounds.Ball(Eisenstein(3, -1), Rational(1, 512), 80)
    for a in _circle_points(left):
        assert left.contains(a)
        assert left.norm_interval().contains(a.norm())
        assert left.conjugate().contains(a.conjugate())
        assert left.inverse().contains(a.inverse())
        assert (left**-3).contains(a**-3)
        for b in _circle_points(right):
            assert (left + right).contains(a + b)
            assert (left - right).contains(a - b)
            assert (left * right).contains(a * b)
            assert (left / right).contains(a / b)


def test_interval_arithmetic_covers_signed_endpoints_and_rejects_possible_zero():
    left = bounds.Interval(Rational(-2), Rational(3), 40)
    right = bounds.Interval(Rational(4), Rational(5), 40)
    for a in (-2, 0, 3):
        for b in (4, 5):
            assert (left + right).contains(a + b)
            assert (left - right).contains(a - b)
            assert (left * right).contains(a * b)
            assert (left / right).contains(Rational(a, b))
        assert (left**2).contains(a**2)
        assert (left**3).contains(a**3)
    assert (left**2).lower == 0
    negative = bounds.Interval(Rational(-5), Rational(-2), 40)
    assert negative.inverse().contains(Rational(-1, 3))
    with pytest.raises(ZeroDivisionError, match="may contain zero"):
        left.inverse()
    with pytest.raises(ZeroDivisionError, match="may contain zero"):
        bounds.Ball(Eisenstein(1), Rational(1), 80).inverse()


def test_error_rounding_is_outward_but_exact_inputs_are_not_approximated():
    exact = bounds.Ball(Eisenstein(Rational(1, 7), Rational(3, 11)), Rational(0), 8)
    assert (exact**-2).radius == 0
    assert (exact**-2).center == exact.center**-2
    assert exact.norm_interval().lower == exact.center.norm()
    rounded = bounds.Ball(Eisenstein(1), Rational(1, 7), 8)
    assert rounded.radius >= Rational(1, 7)
    interval = bounds.Interval(Rational(-1, 7), Rational(1, 11), 8)
    assert interval.lower <= Rational(-1, 7)
    assert interval.upper >= Rational(1, 11)
    assert interval.width < Rational(1, 7) + Rational(1, 11) + Rational(2, 256)
    singleton = bounds.Interval(Rational(1, 7), Rational(1, 7), 8)
    assert singleton.lower == singleton.upper == Rational(1, 7)


@pytest.mark.parametrize("infinity", (False, True))
def test_all_actual_branches_have_bounded_positive_densities_and_nonzero_jacobians(infinity):
    intersection = _intersection(infinity=infinity)
    assert len(intersection.root_pairs) == 9
    for pair in intersection.root_pairs:
        point, chart = _point(intersection, pair)
        measure = _measure(point, chart)
        assert measure.omega_density.lower > 0
        assert measure.auxiliary_pi3_density.lower > 0
        assert measure.quotient_weight_pi3_removed.lower > 0
        for value in measure.projection_jacobians:
            assert value.center.norm() > value.radius**2
        # This residual check is not the membership proof: membership comes
        # from the exact actual-pencil root certificates held by point.
        for equation in projection_polynomials(chart):
            assert bounds.polynomial_value(equation, measure.coordinates).contains(0)
        for k in range(5):
            coordinates = tuple(_circle_points(value)[(k + i) % 5]
                                for i, value in enumerate(measure.coordinates))
            residue, omega, auxiliary, quotient = _exact_density(coordinates, chart)
            assert measure.residue.contains(residue)
            assert measure.omega_density.contains(omega)
            assert measure.auxiliary_pi3_density.contains(auxiliary)
            assert measure.quotient_weight_pi3_removed.contains(quotient)
        for group, pivot in zip((point.x, point.u, point.p), point.chart, strict=True):
            assert group[pivot].center == Eisenstein(1)
            assert group[pivot].radius == 0


def test_refinement_reduces_density_errors_not_merely_center_residuals():
    coarse, fine = _intersection(25), _intersection(50)
    for pair in coarse.root_pairs:
        first, chart = _point(coarse, pair)
        second, second_chart = _point(fine, pair)
        outer, inner = _measure(first, chart), _measure(second, second_chart)
        # Confirm the root correspondence before comparing the output bounds.
        for large, small, index in ((coarse.first, fine.first, pair[0]),
                                    (coarse.second, fine.second, pair[1])):
            a, b = large.finite.disks[index], small.finite.disks[index]
            assert (a.center - b.center).norm() < (a.radius - b.radius)**2
        for name in ("omega_density", "auxiliary_pi3_density", "quotient_weight_pi3_removed"):
            a, b = getattr(outer, name), getattr(inner, name)
            assert b.width < a.width / 1000
            assert a.lower <= b.lower <= b.upper <= a.upper


@pytest.mark.parametrize("x,u,p,pivots", (
    ((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1)),
    ((1, 1, 1), (1, -1, 0), (1, 0), (0, 0, 0)),
))
def test_exact_input_recovers_existing_measure_without_numerical_fallback(x, u, p, pivots):
    point = fiber.CoverPoint(x, u, p, pivots)
    chart = ProjectionChart(pivots[0], 2, pivots[1], 2, pivots[2])
    exact = local_measure(point, chart, volume_scale=Eisenstein(2, 1), covering_degree=9)
    result = bounds.bounded_local_measure(point, chart, volume_scale=Eisenstein(2, 1),
                                          covering_degree=9, bits=16)
    assert result.residue.center == exact.residue
    assert result.residue.radius == 0
    for name in ("omega_density", "auxiliary_pi3_density", "cover_weight_pi3_removed",
                 "quotient_weight_pi3_removed"):
        interval = getattr(result, name)
        assert interval.lower == interval.upper == getattr(exact, name)


def _exact_probe_enclosure():
    """Certify the old exact probe in the new actual-intersection representation."""

    policy = roots.RootPolicy(Rational(1, 2**30), 60, 80, 128)
    intersection = roots.intersection_roots(
        roots.ProjectiveLine((1, -1, 0), (0, 0, 1)),
        roots.ProjectiveLine((1, 1, 0), (0, 0, 1)), (0, 1),
        parameter_pivots=(0, 0), policy=policy,
    )
    exact_indices = []
    for side, value in ((intersection.first, Eisenstein(0)),
                        (intersection.second, Eisenstein(1))):
        indices = tuple(i for i, disk in enumerate(side.finite.disks)
                        if (disk.center - value).norm() <= disk.radius**2)
        assert len(indices) == 1
        index = indices[0]
        disks = list(side.finite.disks)
        disks[index] = roots.certify_disk(side.finite.polynomial, value, Rational(0), 80)
        certified = replace(side, finite=replace(side.finite, disks=tuple(disks)))
        intersection = replace(intersection, **{
            "first" if value.is_zero() else "second": certified,
        })
        exact_indices.append(index)
    return bounds.BoundedCoverPoint(intersection, tuple(exact_indices), (0, 0, 1), 80)


def test_actual_constituent_cochains_match_archived_exact_generator_coordinates():
    point = _exact_probe_enclosure()
    exact = fiber.CoverPoint((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1))
    streams = fiber.lifts._inputs()[1]
    for module, stream, indices in ((fiber.lifts.first, streams[0], (0, 1273)),
                                     (fiber.lifts.second, streams[1], (15, 1318))):
        context = module._context()[0]
        for index in indices:
            cochain = module.expand_section(fiber.lifts._compact(stream[index]))
            enclosure = bounds.local_cochain_coordinates(cochain, point, context)
            expected = fiber.compact_coordinates(stream[index], exact, context)
            assert tuple(value.center for value in enclosure) == expected
            assert all(value.radius == 0 for value in enclosure)
        incompatible = (fiber.lifts.second if module is fiber.lifts.first else fiber.lifts.first)
        with pytest.raises(ValueError, match="incompatible actual cochain basis"):
            bounds.local_cochain_coordinates(cochain, point, incompatible._context()[0])


def test_actual_laurent_coefficients_enclose_nonzero_error_functionals():
    streams = fiber.lifts._inputs()[1]
    for intersection, pair in ((_intersection(), (0, 0)),
                                (_intersection(infinity=True), ("infinity", 0))):
        point, _chart = _point(intersection, pair)
        for module, stream, index in ((fiber.lifts.first, streams[0], 1273),
                                      (fiber.lifts.second, streams[1], 1318)):
            context = module._context()[0]
            record = stream[index]
            cochain = module.expand_section(fiber.lifts._compact(record))
            enclosure = bounds.local_cochain_coordinates(cochain, point, context)
            for offset in range(5):
                values = tuple(_circle_points(c)[(offset + i) % 5]
                               for i, c in enumerate((*point.x, *point.u, *point.p)))
                # Independent compact archive evaluation. These exact ambient
                # functionals are not asserted to be cover points or samples.
                expected = [Eisenstein(0)] * len(enclosure)
                for obj, powers, chart, pair in record["terms"]:
                    if chart != point.chart[2]:
                        continue
                    term = Eisenstein(*pair)
                    for value, exponent in zip(values, powers, strict=True):
                        term *= value**exponent
                    expected[obj] += term
                assert all(ball.contains(value) for ball, value in zip(enclosure, expected,
                                                                        strict=True))


def test_chart_poles_precision_and_types_cannot_be_hidden():
    intersection = _intersection(infinity=True)
    with pytest.raises(ZeroDivisionError):
        bounds.BoundedCoverPoint(intersection, ("infinity", 0), (0, 0, 1), 80)
    point, chart = _point(intersection, (0, 0))
    with pytest.raises(ValueError, match="Laurent pole escaped"):
        point.monomial((0, -1, 0, 0, 0, 0, 0, 0))
    with pytest.raises(ValueError, match="chart pivots"):
        _measure(point, replace(chart, x_pivot=1))
    with pytest.raises(ValueError, match="bound precisions"):
        bounds.bounded_local_measure(point, chart, volume_scale=1, covering_degree=9, bits=80)
    with pytest.raises(ValueError, match="bound precisions"):
        bounds.Ball(Eisenstein(1), Rational(0), 40) + bounds.Ball(Eisenstein(1), Rational(0), 80)
    with pytest.raises(ValueError, match="root pair"):
        bounds.BoundedCoverPoint(intersection, (False, 0), chart.pivots, 80)
    with pytest.raises(TypeError):
        bounds.Ball(1.0, Rational(0), 80)
    with pytest.raises(ValueError, match="positive integer"):
        bounds.Ball(1, Rational(0), True)
    with pytest.raises(TypeError, match="must be integers"):
        bounds.Ball(1, Rational(0), 80)**True
    with pytest.raises(FrozenInstanceError):
        point.x = ()


def test_ramified_projection_is_rejected_without_changing_the_declared_chart():
    policy = roots.RootPolicy(Rational(1, 2**30), 60, 80, 128)
    intersection = roots.intersection_roots(
        roots.ProjectiveLine((1, 0, 0), (0, 0, 1)),
        roots.ProjectiveLine((1, 1, 0), (0, 0, 1)), (1, 0),
        parameter_pivots=(0, 0), policy=policy,
    )
    point = bounds.BoundedCoverPoint(intersection, (0, 0), (0, 0, 0), 120)
    # x1 is identically zero; the actual F derivative in x1 therefore
    # vanishes although the derivative in x2 is nonzero. This is a chart
    # obstruction, not a singular cover or a physical no-go.
    ramified = ProjectionChart(0, 1, 0, 2, 0)
    with pytest.raises(ZeroDivisionError):
        _measure(point, ramified)
    assert _measure(point, ProjectionChart(0, 2, 0, 2, 0)).omega_density.lower > 0


def test_complementary_parameter_charts_enclose_the_same_nine_actual_points():
    original = _intersection()
    alternative = roots.intersection_roots(
        original.first_line, original.second_line, original.p,
        parameter_pivots=(1, 1), policy=original.first.finite.policy,
    )
    first_points = tuple(_point(original, pair)[0] for pair in original.root_pairs)
    second_points = tuple(_point(alternative, pair)[0] for pair in alternative.root_pairs)
    matches = []
    for first in first_points:
        possible = []
        for index, second in enumerate(second_points):
            if all((a.center - b.center).norm() <= (a.radius + b.radius)**2
                   for a, b in zip((*first.x, *first.u), (*second.x, *second.u), strict=True)):
                possible.append(index)
        assert len(possible) == 1
        matches.extend(possible)
    assert len(set(matches)) == 9


def test_polynomial_enclosures_include_independently_expanded_values():
    x = Polynomial.monomial((1, 0), scalar_type=Eisenstein)
    y = Polynomial.monomial((0, 1), scalar_type=Eisenstein)
    polynomial = (x - 2 * y)**3 + x * OMEGA + y**2
    coordinates = (bounds.Ball(Eisenstein(2, 1), Rational(1, 512), 80),
                   bounds.Ball(Eisenstein(3, -1), Rational(1, 512), 80))
    result = bounds.polynomial_value(polynomial, coordinates)
    for a in _circle_points(coordinates[0]):
        for b in _circle_points(coordinates[1]):
            assert result.contains((a - 2 * b)**3 + a * OMEGA + b**2)


def test_saved_enclosures_reproduce_without_claiming_sampling_or_metrics():
    saved = json.loads(bounds.OUTPUT.read_text())
    assert saved == bounds.enclosure_artifact()
    digest = saved.pop("artifact_digest")
    assert digest == hashlib.sha256(json.dumps(saved, sort_keys=True, separators=(",", ":"))
                                    .encode()).hexdigest()
    for configuration in saved["actual_configurations"]:
        assert len(configuration["all_nine_bounded_densities"]) == 9
    for flag in ("bounded_universal_fiber_frame_available",
                 "centers_are_exact_cover_points",
                 "bounded_section_and_density_evaluation_available",
                 "controlled_numerical_sampling_available", "numerical_metrics_available",
                 "physical_yukawas_available", "extension_point_selected", "vacuum_selected",
                 "observational_inputs_used"):
        assert saved[flag] is False
