"""Independently check a positive auxiliary law on the unchanged actual cover.

Owns:
    Exact mixed masses and mixture weights, independent FS wedge densities,
    actual projective branch equations, enclosure refinement, and scope limits.

Depends on:
    Actual frozen cover points, exact Matrix and polynomial determinants,
    established root certificates, and the positive-law research calculation.

Must not:
    Turn regression points or circle functionals into uniform samples, select
    physical Kahler moduli, infer a global numerical bound, or assert metrics.

Phase 0:
    Auxiliary-law prerequisites only; physical normalization remains open.
"""

import hashlib
import json
from fractions import Fraction
from functools import cache

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from onetheory.math.polynomials import Polynomial, determinant
from research.experiments.scientific_genesis import alternate_metric_positive_measure as positive


def _exact_forms(coordinates, tangent):
    """Exact Hermitian pullbacks, independently of circular-bound operations."""

    def pullback(q, rows):
        norm = Rational(1) + sum((v.norm() for v in q), Rational(0))
        metric = Matrix(tuple(tuple((Eisenstein(norm * int(i == j)) - a * b.conjugate())
                                    / norm**2 for j, b in enumerate(q))
                              for i, a in enumerate(q)), scalar_type=Eisenstein)
        t = Matrix(rows, scalar_type=Eisenstein)
        adjoint = Matrix(tuple(tuple(v.conjugate() for v in col)
                               for col in zip(*rows, strict=True)), scalar_type=Eisenstein)
        return adjoint.matmul(metric).matmul(t)

    s, z, r, w, t = coordinates
    return (pullback((s, z), tangent[:2]), pullback((r, w), tangent[2:4]),
            pullback((t,), tangent[4:]))


def _density(forms):
    total = Matrix(tuple(tuple(sum((form[i][j] for form in forms), Eisenstein(0))
                               for j in range(3)) for i in range(3)), scalar_type=Eisenstein)
    value = total.determinant()
    assert value.b.is_zero()
    return 6 * value.a


def test_masses_and_probabilities_follow_actual_complete_intersection():
    masses, total, probabilities = positive.masses()
    assert masses == (Rational(9), Rational(3), Rational(3))
    assert total == Rational(72)
    assert probabilities == (Rational(3, 4), Rational(1, 8), Rational(1, 8))
    assert sum(probabilities, Rational(0)) == Rational(1)
    # Independent ambient multinomial count for (Hx+Hu+Hp)^3 [X].
    assert total == 6 * 3 * 3 + 3 * 3 + 3 * 3


@pytest.mark.parametrize("complementary", (False, True))
def test_exact_actual_density_equals_independent_mixed_wedge_mixture(complementary):
    x, u, p, pivots = (((1, 1, 1), (1, -1, 0), (1, 0), (0, 0, 0)) if complementary
                       else ((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1)))
    point = positive.measure.CoverPoint(x, u, p, pivots)
    chart = positive.measure.ProjectionChart(0, 2, 0, 2, pivots[2])
    original = positive.measure.local_measure(point, chart, volume_scale=Eisenstein(1),
                                              covering_degree=9)
    forms = _exact_forms(chart.coordinates(point), original.tangent.rows)
    a, b, c = positive.measure._variables(3)
    pencil = tuple(tuple(sum((v.scale(form[i][j]) for v, form in zip((a, b, c), forms,
                                                                 strict=True)),
                            Polynomial.zero(3, scalar_type=Eisenstein))
                         for j in range(3)) for i in range(3))
    mixed = determinant(pencil)
    density_a = Eisenstein.coerce(mixed.coefficient((1, 1, 1))).a
    density_bx = 2 * Eisenstein.coerce(mixed.coefficient((2, 1, 0))).a
    density_bu = 2 * Eisenstein.coerce(mixed.coefficient((1, 2, 0))).a
    assert all(mixed.coefficient(e).is_zero() for e in (
        (3, 0, 0), (0, 3, 0), (0, 0, 3), (2, 0, 1), (0, 2, 1), (1, 0, 2), (0, 1, 2),
    ))
    assert density_a == original.auxiliary_pi3_density
    exact = _density(forms)
    # Separate Cauchy--Binet route: the two plane tangent minors have only
    # (s,t) and (r,t) support. No full Gram determinant enters this formula.
    s, z, r, w, t = chart.coordinates(point)
    zs, zt = original.tangent.rows[1][0], original.tangent.rows[1][2]
    wr, wt = original.tangent.rows[3][1], original.tangent.rows[3][2]
    kx = positive.measure._fs_direction((s, z), (Eisenstein(1), zs))
    ku = positive.measure._fs_direction((r, w), (Eisenstein(1), wr))
    sx, su = 1 + s.norm() + z.norm(), 1 + r.norm() + w.norm()
    assert exact == 6 * (kx * ku / (1 + t.norm())**2
                         + zt.norm() * ku / sx**3 + wt.norm() * kx / su**3)
    assert exact / 72 == density_a / 12 + density_bx / 24 + density_bu / 24
    bounded = positive.bounded_positive_measure(point, chart, volume_scale=Eisenstein(1),
                                                covering_degree=9, bits=80)
    density = bounded["positive_density_times_pi_cubed"]
    assert density.lower == density.upper == exact
    assert bounded["cover_weight_without_pi_cubed"].lower == 72 * original.omega_density / exact
    assert bounded["quotient_weight_without_pi_cubed"].lower == 8 * original.omega_density / exact
    scaled = positive.bounded_positive_measure(point, chart, volume_scale=Eisenstein(2),
                                               covering_degree=9, bits=80)
    assert scaled["positive_density_times_pi_cubed"] == density
    assert scaled["cover_weight_without_pi_cubed"].lower == (
        4 * bounded["cover_weight_without_pi_cubed"].lower
    )


@pytest.mark.parametrize("side,point", ((1, (1, -1, 0)), (2, (1, 1, 1)), (1, (1, 0, 0)),
                                       (2, (0, 1, 0))))
def test_actual_base_projection_equations_and_homogeneous_scaling(side, point):
    p = positive.projected_base(point, side)
    cox = positive.measure.schoen_geometry().cover.cox
    f, g = (positive.measure._value(cubic, point) for cubic in (cox.cubic_f, cox.cubic_g))
    assert (p[0] * f + p[1] * g if side == 1 else 2 * p[1] * f + p[0] * g).is_zero()
    scale = Eisenstein(2, 1)
    assert positive.projected_base(tuple(scale * q for q in point), side) == (
        tuple(scale**3 * q for q in p)
    )


@pytest.mark.parametrize("side", (1, 2))
def test_partner_certificates_use_actual_other_pencil_and_complete_three_roots(side):
    point = (1, -1, 0) if side == 1 else (1, 1, 1)
    line = positive.roots.ProjectiveLine((1, 0, 0), (0, 1, 1))
    policy = positive.roots.RootPolicy(Rational(1, 2**30), 60, 80, 128)
    p, certified = positive.partner_roots(point, line, side=side, parameter_pivot=0, policy=policy)
    assert certified.count == 3
    assert certified.homogeneous == positive.roots.restrict_pencil(line, p, 3 - side)
    cox = positive.measure.schoen_geometry().cover.cox
    s, t = positive.measure._variables(2)
    image = (s, t, t)
    actual = ((cox.cubic_f.substitute(image)).scale(2 * p[1])
              + (cox.cubic_g.substitute(image)).scale(p[0]) if side == 1
              else (cox.cubic_f.substitute(image)).scale(p[0])
              + (cox.cubic_g.substitute(image)).scale(p[1]))
    assert actual == certified.homogeneous


@cache
def _intersection(refined=False):
    policy = positive.roots.RootPolicy(Rational(1, 2**(36 if refined else 30)),
                                       72 if refined else 60, 80, 128)
    return positive.roots.intersection_roots(
        positive.roots.ProjectiveLine((1, 0, 0), (0, 1, 1)),
        positive.roots.ProjectiveLine((1, 1, 0), (0, 0, 1)), (1, 1),
        parameter_pivots=(0, 0), policy=policy,
    )


def test_bounds_enclose_independent_exact_functionals_and_refine():
    chart = positive.measure.ProjectionChart(0, 2, 0, 2, 0)
    point = positive.bounds.BoundedCoverPoint(_intersection(), (0, 0), chart.pivots, 80)
    result = positive.bounded_positive_measure(point, chart, volume_scale=Eisenstein(1),
                                               covering_degree=9, bits=80)
    original = positive.bounds.bounded_local_measure(point, chart, volume_scale=Eisenstein(1),
                                                     covering_degree=9, bits=80)
    # Exact circle functionals are arithmetic attacks, not actual cover samples.
    for direction in (Eisenstein(0), Eisenstein(1), OMEGA, OMEGA**2):
        coordinates = tuple(q.center + direction * q.radius for q in original.coordinates)
        f, g = positive.measure.projection_polynomials(chart)
        def value(polynomial, coordinates=coordinates):
            return positive.measure._value(polynomial, coordinates)

        fs, fz, ft = (value(f.derivative(i)) for i in (0, 1, 4))
        gr, gw, gt = (value(g.derivative(i)) for i in (2, 3, 4))
        tangent = ((1, 0, 0), (-fs / fz, 0, -ft / fz), (0, 1, 0),
                   (0, -gr / gw, -gt / gw), (0, 0, 1))
        density = _density(_exact_forms(coordinates, tangent))
        assert result["positive_density_times_pi_cubed"].contains(density)
    smaller = positive.bounds.BoundedCoverPoint(_intersection(True), (0, 0), chart.pivots, 80)
    refined = positive.bounded_positive_measure(smaller, chart, volume_scale=Eisenstein(1),
                                                covering_degree=9, bits=80)
    assert refined["positive_density_times_pi_cubed"].width < (
        result["positive_density_times_pi_cubed"].width
    )


@pytest.mark.parametrize("point,side", (((0, 0, 0), 1), ((1, 0), 1), ((1, 0, 0), False),
                                       ((1, 0, 0), 0)))
def test_invalid_projective_inputs_do_not_get_fallback_bases(point, side):
    with pytest.raises(ValueError):
        positive.projected_base(point, side)


def test_base_point_projection_refuses_to_invent_a_projective_parameter(monkeypatch):
    # Error-path fixture only: no actual base point is claimed by this fixture.
    monkeypatch.setattr(positive.measure, "_value", lambda *_: Eisenstein(0))
    with pytest.raises(ValueError, match="base point does not determine"):
        positive.projected_base((1, 0, 0), 1)


def test_scoped_positive_artifact_and_all_actual_root_enclosures_reproduce():
    payload = positive.positive_artifact()
    assert payload == json.loads(positive.OUTPUT.read_text())
    assert hashlib.sha256((positive.measure.ROOT / payload["proof"]).read_bytes()).hexdigest() == (
        payload["proof_sha256"]
    )
    assert payload["component_probabilities"] == ["3/4", "1/8", "1/8"]
    assert payload["ideal_weight_globally_bounded"] is True
    assert payload["all_nonnegative_weight_moments_finite"] is True
    for configuration in payload["actual_configurations"]:
        records = configuration["all_nine_positive_densities"]
        assert len(records) == 9
        assert all(Rational(Fraction(record["positive_density_times_pi_cubed"][0])) > 0
                   for record in records)
    for flag in ("quantitative_global_weight_bound_available",
                 "critical_fiber_chart_enclosures_available",
                 "controlled_numerical_sampling_available", "numerical_metrics_available",
                 "physical_yukawas_available", "physical_kahler_class_selected", "vacuum_selected"):
        assert payload[flag] is False
