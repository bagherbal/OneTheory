"""Independently check exact integration conventions on the actual Schoen cover.

Owns:
    Residue orientation, tangent and chart identities, mixed FS wedge densities,
    topological normalization, quotient degree, and fail-closed chart handling.

Depends on:
    Actual frozen cover points and equations, the research measure construction,
    and separate determinant and Hermitian pullback calculations.

Must not:
    Treat algebraic probes as sampling evidence, choose physical moduli, or
    claim convergence of metrics, integrals, or canonically normalized Yukawas.

Phase 0:
    Exact geometric integration prerequisites only; numerical sampling is open.
"""

import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from itertools import product

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from onetheory.math.polynomials import Polynomial, determinant, gcd
from research.experiments.scientific_genesis import alternate_metric_measure as measure


def _point(complementary=False, chart=None):
    x, u, p, pivots = (((1, 1, 1), (1, -1, 0), (1, 0), (0, 0, 0)) if complementary
                       else ((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1)))
    return measure.CoverPoint(x, u, p, pivots if chart is None else chart.pivots)


def _local(point, chart, scale=1, degree=9):
    return measure.local_measure(point, chart, volume_scale=scale, covering_degree=degree)


@pytest.mark.parametrize("complementary", (False, True))
def test_residue_orientation_and_tangent_use_actual_equations(complementary):
    point = _point(complementary)
    chart = measure.ProjectionChart(0, 2, 0, 2, point.chart[2])
    local = _local(point, chart)
    coordinates = chart.coordinates(point)
    polynomials = measure.projection_polynomials(chart)
    assert all(p.substitute(coordinates).is_zero() for p in polynomials)
    jacobian = Matrix(tuple(tuple(Eisenstein.coerce(p.derivative(i).substitute(coordinates)
                             .coefficient(())) for i in range(5)) for p in polynomials),
                      scalar_type=Eisenstein)
    assert jacobian.matmul(local.tangent).is_zero()
    # df, dg, ds, dr, dt in the fixed ambient coordinate order (s,z,r,w,t).
    wedge = Matrix((*jacobian.rows, (1, 0, 0, 0, 0), (0, 0, 1, 0, 0), (0, 0, 0, 0, 1)),
                   scalar_type=Eisenstein).determinant()
    assert wedge * local.residue == Eisenstein(chart.ambient_sign)
    expected = (Eisenstein(Rational(-1, 243), Rational(-1, 486)) if complementary
                else Eisenstein(Rational(1, 486), Rational(1, 972)))
    assert local.residue == expected
    cubics = measure.fiber_polynomials(chart, (coordinates[0], coordinates[2], coordinates[4]))
    for polynomial, root in zip(cubics, (coordinates[1], coordinates[3]), strict=True):
        assert polynomial.degree == 3
        assert polynomial.substitute((root,)).is_zero()
        assert gcd(polynomial, polynomial.derivative()).degree == 0


def _adjoint(matrix):
    return Matrix(tuple(tuple(value.conjugate() for value in column)
                        for column in zip(*matrix.rows, strict=True)), scalar_type=Eisenstein)


def _fs_pullback(coordinates, tangent):
    """Pull back the full ambient Hermitian form, independently of factorization."""

    norm = Rational(1) + sum((value.norm() for value in coordinates), Rational(0))
    ambient = Matrix(tuple(tuple((Eisenstein(norm * int(i == j))
                                  - coordinates[i] * coordinates[j].conjugate()) / norm**2
                                 for j in range(len(coordinates)))
                           for i in range(len(coordinates))), scalar_type=Eisenstein)
    return _adjoint(tangent).matmul(ambient).matmul(tangent)


@pytest.mark.parametrize("complementary", (False, True))
def test_auxiliary_density_matches_an_independent_mixed_wedge_determinant(complementary):
    point = _point(complementary)
    chart = measure.ProjectionChart(0, 2, 0, 2, point.chart[2])
    local = _local(point, chart)
    s, z, r, w, t = chart.coordinates(point)
    tangent = local.tangent
    forms = (_fs_pullback((s, z), Matrix(tangent.rows[:2], scalar_type=Eisenstein)),
             _fs_pullback((r, w), Matrix(tangent.rows[2:4], scalar_type=Eisenstein)),
             _fs_pullback((t,), Matrix(tangent.rows[4:], scalar_type=Eisenstein)))
    ring_variables = tuple(Polynomial.monomial(tuple(int(i == j) for j in range(3)),
                                              scalar_type=Eisenstein) for i in range(3))
    pencil = tuple(tuple(sum((variable * form[i][j] for variable, form in
                             zip(ring_variables, forms, strict=True)),
                            Polynomial.zero(3, scalar_type=Eisenstein)) for j in range(3))
                   for i in range(3))
    mixed_density = determinant(pencil).coefficient((1, 1, 1))
    assert mixed_density == Eisenstein(local.auxiliary_pi3_density)
    assert local.auxiliary_pi3_density == Rational(1, 8)
    assert local.auxiliary_cover_mass == Rational(3 * 3)
    assert local.cover_weight_pi3_removed == 9 * local.quotient_weight_pi3_removed
    assert local.quotient_weight_pi3_removed == local.omega_density / Rational(1, 8)


def _transition(old_chart, old_point, old_tangent, new_chart):
    """Differentiate new homogeneous coordinate ratios by the quotient rule."""

    rows = []
    zero = (Eisenstein(0),) * 3
    for group, pivot, solve, free, free_row, solve_row, new_free, new_pivot in (
        (old_point.x, old_chart.x_pivot, old_chart.x_solve, old_chart.free_indices[0],
         0, 1, new_chart.free_indices[0], new_chart.x_pivot),
        (old_point.u, old_chart.u_pivot, old_chart.u_solve, old_chart.free_indices[1],
         2, 3, new_chart.free_indices[1], new_chart.u_pivot),
        (old_point.p, old_chart.p_pivot, old_chart.free_indices[2], old_chart.free_indices[2],
         4, 4, new_chart.free_indices[2], new_chart.p_pivot),
    ):
        affine = tuple(c / group[pivot] for c in group)
        derivatives = {pivot: zero, free: old_tangent.rows[free_row],
                       solve: old_tangent.rows[solve_row]}
        rows.append(tuple((derivatives[new_free][i] * affine[new_pivot]
                           - affine[new_free] * derivatives[new_pivot][i])
                          / affine[new_pivot]**2 for i in range(3)))
    return Matrix(rows, scalar_type=Eisenstein)


def test_chart_changes_preserve_the_volume_and_importance_weight():
    base_chart = measure.ProjectionChart(0, 2, 0, 2, 1)
    base_point = _point(chart=base_chart)
    base = _local(base_point, base_chart)
    for x_pivot, u_pivot in product((0, 1), range(3)):
        for u_solve in (i for i in range(3) if i != u_pivot):
            chart = measure.ProjectionChart(x_pivot, 2, u_pivot, u_solve, 1)
            point = _point(chart=chart)
            local = _local(point, chart)
            jacobian = _transition(base_chart, base_point, base.tangent, chart).determinant()
            assert base.residue == local.residue * jacobian
            assert base.omega_density == local.omega_density * jacobian.norm()
            assert base.auxiliary_pi3_density == local.auxiliary_pi3_density * jacobian.norm()
            assert base.quotient_weight_pi3_removed == local.quotient_weight_pi3_removed


def test_p1_overlap_identity_holds_as_a_polynomial_not_just_at_a_probe():
    nu_chart = measure.ProjectionChart(0, 2, 0, 2, 1)
    mu_chart = measure.ProjectionChart(0, 2, 0, 2, 0)
    nu_f, nu_g = measure.projection_polynomials(nu_chart)
    mu_f, mu_g = measure.projection_polynomials(mu_chart)
    mu_jacobian = mu_f.derivative(1) * mu_g.derivative(3)
    # t^2 J_mu(1/t); clearing the denominator retains every coefficient.
    transformed = Polynomial((((*powers[:4], 2 - powers[4]), value)
                              for powers, value in mu_jacobian.terms),
                             variable_count=5, scalar_type=Eisenstein)
    assert transformed == nu_f.derivative(1) * nu_g.derivative(3)
    assert nu_chart.ambient_sign == -mu_chart.ambient_sign
    # dt_mu/dt_nu = -1/t_nu^2 accounts for precisely that sign.


def test_scale_rescaling_and_quotient_degree_are_not_silent():
    chart = measure.ProjectionChart(0, 2, 0, 2, 1)
    point = _point(chart=chart)
    local = _local(point, chart)
    rescaled = measure.CoverPoint(tuple(2 * c for c in point.x),
                                 tuple(OMEGA * c for c in point.u),
                                 tuple(5 * c for c in point.p), point.chart)
    assert _local(rescaled, chart) == local
    scale = Eisenstein(2, 3)
    scaled = _local(point, chart, scale)
    assert scaled.residue == scale * local.residue
    assert scaled.omega_density == scale.norm() * local.omega_density
    assert scaled.quotient_weight_pi3_removed == scale.norm() * local.quotient_weight_pi3_removed
    assert _local(point, chart, degree=1).quotient_weight_pi3_removed == (
        local.cover_weight_pi3_removed
    )
    with pytest.raises(FrozenInstanceError):
        local.covering_degree = 1
    for degree in (0, -1, True, 9.0):
        with pytest.raises(ValueError, match="covering degree"):
            _local(point, chart, degree=degree)
    with pytest.raises(ValueError, match="nonzero volume"):
        _local(point, chart, scale=0)
    with pytest.raises(TypeError):
        _local(point, chart, scale=1.0)
    with pytest.raises(ValueError, match="identical explicit pivots"):
        _local(point, measure.ProjectionChart(1, 2, 0, 2, 1))


def test_ramified_projection_fails_closed_without_claiming_a_singular_cover(monkeypatch):
    chart = measure.ProjectionChart(0, 2, 0, 2, 1)
    # Deliberately inject a degenerate projection operator, not a physical point.
    z = Polynomial.monomial((0, 1, 0, 0, 0), scalar_type=Eisenstein)
    w = Polynomial.monomial((0, 0, 0, 1, 0), scalar_type=Eisenstein)
    monkeypatch.setattr(measure, "projection_polynomials", lambda _: (z**2, w))
    with pytest.raises(ValueError, match="projection is ramified"):
        _local(_point(chart=chart), chart)


def test_actual_deck_units_give_invariant_residue_and_fs_forms(monkeypatch):
    assert measure.residue_deck_characters() == {"P": Eisenstein(1), "T": Eisenstein(1)}
    actions = measure.schoen_sparse_deck_actions()
    broken = (replace(actions[0], first_equation_unit=Eisenstein(1)), actions[1])
    monkeypatch.setattr(measure, "schoen_sparse_deck_actions", lambda: broken)
    with pytest.raises(ValueError, match="equation units disagree"):
        measure.residue_deck_characters()


def test_saved_measure_artifact_is_reproducible_and_not_a_metric_or_sampler():
    stored = json.loads(measure.OUTPUT.read_text(encoding="utf-8"))
    assert stored == measure.measure_artifact()
    digest = stored.pop("artifact_digest")
    assert digest == hashlib.sha256(json.dumps(stored, sort_keys=True, separators=(",", ":"))
                                    .encode()).hexdigest()
    for flag in ("controlled_numerical_sampling_available", "numerical_metrics_available",
                 "physical_yukawas_available", "extension_point_selected", "vacuum_selected",
                 "observational_inputs_used"):
        assert stored[flag] is False
    assert stored["exact_residue_and_auxiliary_measure_available"] is True


@pytest.mark.parametrize("indices", ((0, 0, 0, 2, 1), (True, 2, 0, 2, 1),
                                   (0, 2, 3, 2, 1), (0, 2, 0, 2, 2)))
def test_projection_charts_reject_invalid_or_hidden_coordinate_choices(indices):
    with pytest.raises(ValueError):
        measure.ProjectionChart(*indices)
