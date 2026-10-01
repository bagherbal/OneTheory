"""Independently attack the actual-pencil importance-weight moment derivation.

Owns:
    Actual critical supports, full-versus-reduced multiplicities, homogeneous
    infinity checks, direct nodal gradients and Hessians, and scientific scope.

Depends on:
    Actual Cox coefficients, exact polynomials and determinants, the research
    moment certificate, and the explicit local analytic derivation.

Must not:
    Present the universal Hesse factorization as the frozen carrier, approximate
    critical roots, infer independent sampling, or claim quantitative errors.

Phase 0:
    Scoped research integrability tests; physical normalization remains open.
"""

import hashlib
import json
from functools import reduce
from operator import mul

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from onetheory.math.polynomials import Polynomial, determinant
from research.experiments.scientific_genesis import alternate_metric_weight_moments as moments


def _value(polynomial, coordinates):
    return Eisenstein.coerce(polynomial.substitute(coordinates).coefficient(()))


def test_critical_supports_match_independent_explicit_coefficients():
    t = moments.measure._variables(1)[0]
    one = Polynomial.one(1, scalar_type=Eisenstein)
    expected = (
        t**6 + (t**3).scale(30 + 60 * OMEGA) - one.scale(243),
        t**6 - (t**3).scale(Eisenstein(Rational(80, 81), Rational(160, 81)))
        - one.scale(Rational(64, 243)),
    )
    for pencil, reference in zip(moments.actual_pencils(), expected, strict=True):
        record, support = moments.critical_certificate(*pencil)
        assert support == reference
        assert support.gcd(support.derivative()).degree == 0
        assert record["axis_nodal_fiber_count"] == 3
        assert record["triangle_fiber_count"] == 3
        assert record["nodal_critical_point_count"] == 12
    assert expected[0].gcd(expected[1]).degree == 0


@pytest.mark.parametrize("side", (0, 1))
def test_reduced_support_is_not_the_full_discriminant(side):
    pure, mixed = moments.actual_pencils()[side]
    record, support = moments.critical_certificate(pure, mixed)
    product = reduce(mul, pure)
    triangle = mixed**3 + product.scale(27)
    full = product * triangle**3
    assert full.degree == 12
    assert full.gcd(full.derivative()).degree == 6
    assert full.monic() != support
    assert record["full_discriminant_monic"] == moments._record(full.monic())


@pytest.mark.parametrize("side", (0, 1))
def test_infinity_is_checked_in_the_actual_homogeneous_equations(side):
    cox = moments.measure.schoen_geometry().cover.cox
    infinity = cox.cubic_f if side == 0 else cox.cubic_g
    abc = reduce(mul, (Eisenstein.coerce(infinity.coefficient(e)) for e in (
        (3, 0, 0), (0, 3, 0), (0, 0, 3),
    )))
    triangle = Eisenstein.coerce(infinity.coefficient((1, 1, 1)))**3 + 27 * abc
    record, _support = moments.critical_certificate(*moments.actual_pencils()[side])
    assert not abc.is_zero() and not triangle.is_zero()
    assert record["infinity_product"] == [str(abc.a), str(abc.b)]
    assert record["infinity_triangle"] == [str(triangle.a), str(triangle.b)]


@pytest.mark.parametrize("side,axis", tuple((side, axis) for side in (0, 1) for axis in range(3)))
def test_actual_axis_nodes_have_nonzero_total_gradient_and_plane_hessian(side, axis):
    # Critical base values are exact Q(omega), not approximate cover points.
    cox = moments.measure.schoen_geometry().cover.cox
    delta = tuple(Eisenstein.coerce(cox.cubic_f.coefficient(e)) for e in (
        (3, 0, 0), (0, 3, 0), (0, 0, 3),
    ))
    psi = Eisenstein.coerce(cox.cubic_g.coefficient((3, 0, 0)))
    t0 = -psi / delta[axis] if side == 0 else -2 * delta[axis] / psi
    equation = (cox.cubic_f.scale(t0) + cox.cubic_g if side == 0
                else cox.cubic_f.scale(2) + cox.cubic_g.scale(t0))
    point = tuple(int(i == axis) for i in range(3))
    assert _value(equation, point).is_zero()
    assert all(_value(equation.derivative(i), point).is_zero() for i in range(3))
    parameter_derivative = cox.cubic_f if side == 0 else cox.cubic_g
    assert not _value(parameter_derivative, point).is_zero()
    free = tuple(i for i in range(3) if i != axis)
    hessian = Matrix(tuple(tuple(_value(equation.derivative(i).derivative(j), point)
                                 for j in free) for i in free), scalar_type=Eisenstein)
    assert not hessian.determinant().is_zero()
    partner = moments.critical_certificate(*moments.actual_pencils()[1 - side])[1]
    assert not _value(partner, (t0,)).is_zero()


def test_universal_triangle_factorization_and_all_three_node_hessians():
    # A universal algebraic identity, not a substitution for the actual pencils.
    x, y, z = moments.measure._variables(3)
    cubic = x**3 + y**3 + z**3 - 3 * x * y * z
    assert ((x + y + z) * (x + y.scale(OMEGA) + z.scale(OMEGA**2))
            * (x + y.scale(OMEGA**2) + z.scale(OMEGA))) == cubic
    normal_matrix = Matrix(((1, 1, 1), (1, OMEGA, OMEGA**2), (1, OMEGA**2, OMEGA)),
                           scalar_type=Eisenstein)
    assert not normal_matrix.determinant().is_zero()  # No concurrent triple point.
    for k in range(3):
        point = (Eisenstein(1), OMEGA**k, OMEGA**(2 * k))
        assert all(_value(cubic.derivative(i), point).is_zero() for i in range(3))
        hessian = Matrix(tuple(tuple(_value(cubic.derivative(i).derivative(j), point)
                                     for j in (1, 2)) for i in (1, 2)), scalar_type=Eisenstein)
        assert hessian.determinant() == Eisenstein(27)


@pytest.mark.parametrize("side", (0, 1))
def test_parameter_derivative_identity_is_symbolic_not_a_root_probe(side):
    pure, mixed = moments.actual_pencils()[side]
    product = reduce(mul, pure)
    triangle = mixed**3 + product.scale(27)
    log_numerator = sum((p.derivative() * reduce(mul, (q for j, q in enumerate(pure) if j != i))
                         for i, p in enumerate(pure)), Polynomial.zero(1, scalar_type=Eisenstein))
    # Mod H: H' = 3 D^2(D' - D/3 sum(c_i'/c_i)). Clear denominators first.
    residual = (triangle.derivative() * product - 3 * mixed**2 * mixed.derivative() * product
                + mixed**3 * log_numerator)
    assert residual == triangle * log_numerator


@pytest.mark.parametrize("z,w", ((1, 0), (0, 1), (1, OMEGA), (0, 0)))
def test_local_mixed_wedge_has_quadratic_transverse_order(z, w):
    # Universal local tangent algebra, not sampled geometry or a physical metric.
    # For t=zw, dt=(w,z,0); the partner one-form is dy+lambda*dt.
    z, w = Eisenstein.coerce(z), Eisenstein.coerce(w)
    base = (w, z, Eisenstein(0))
    partner = (OMEGA * w, OMEGA * z, Eisenstein(1))
    a, b, c = moments.measure._variables(3)
    entries = tuple(tuple(
        a.scale(int(i == j and i < 2))
        + b.scale(partner[i].conjugate() * partner[j])
        + c.scale(base[i].conjugate() * base[j])
        for j in range(3)) for i in range(3))
    assert determinant(entries).coefficient((1, 1, 1)) == Eisenstein(z.norm() + w.norm())


@pytest.mark.parametrize("change,error", (
    ("repeat", "repeated critical values"), ("zero_mixed", "repeated critical values"),
    ("infinity", "critical infinity fiber"),
))
def test_degenerate_categories_fail_closed(change, error):
    t = moments.measure._variables(1)[0]
    one = Polynomial.one(1, scalar_type=Eisenstein)
    if change == "repeat":
        pure, mixed = (t, t, t), one
    elif change == "zero_mixed":
        pure, mixed = (t, t + one, t + 2 * one), Polynomial.zero(1, scalar_type=Eisenstein)
    else:
        # D^3 cancels the leading 27ABC term: an infinity critical value.
        pure, mixed = (t, t + one, t + 2 * one), -3 * t + one
    with pytest.raises(ValueError, match=error):
        moments.critical_certificate(pure, mixed)


def test_saved_moment_result_and_proof_scope_are_reproducible():
    payload = moments.moment_artifact()
    assert json.loads(moments.OUTPUT.read_text()) == payload
    proof = moments.measure.ROOT / payload["proof"]
    assert hashlib.sha256(proof.read_bytes()).hexdigest() == payload["proof_sha256"]
    assert payload["weight_second_moment_finite"] is True
    assert payload["weight_third_moment_finite"] is False
    assert payload["radial_q_moment_power"] == "5 - 2*q"
    assert payload["nonnegative_moment_integrability"] == "finite exactly for 0 <= q < 3"
    for flag in ("quantitative_variance_bound_available", "controlled_numerical_sampling_available",
                 "numerical_metrics_available", "physical_yukawas_available",
                 "extension_point_selected",
                 "vacuum_selected", "observational_inputs_used"):
        assert payload[flag] is False
