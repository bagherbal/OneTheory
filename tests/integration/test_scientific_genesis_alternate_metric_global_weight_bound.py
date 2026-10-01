"""Independently check global auxiliary bounds from full polynomial identities.

Owns:
    Fraction-pair coefficient convolution, all saved certificates, conservative
    coefficient inequalities, homogeneous normalization, and scope rejection.

Depends on:
    Original cover equations, actual saved certificate data, standard Fraction
    arithmetic, and the projection-free regression evaluator.

Must not:
    Treat point checks as a global proof, select moduli, infer controlled draws,
    physical metrics, physical couplings, or a stabilized vacuum.

Phase 0:
    Conditional research theorem verification; physical normalization stays open.
"""

import hashlib
import json
from fractions import Fraction as F
from itertools import product

import pytest

from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.scientific_genesis import alternate_metric_global_weight_bound as bound

ZERO = (F(0), F(0))


def _add(a, b):
    return a[0] + b[0], a[1] + b[1]


def _mul(a, b):
    # Independent Q(omega) reduction using omega^2=-1-omega.
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0] - a[1] * b[1]


def _parse(record):
    result = {tuple(e): (F(c[0]), F(c[1])) for e, c in record}
    assert len(result) == len(record) and all(c != ZERO for c in result.values())
    return result


def _sum(polynomials):
    result = {}
    for polynomial in polynomials:
        for e, c in polynomial.items():
            result[e] = _add(result.get(e, ZERO), c)
    return {e: c for e, c in result.items() if c != ZERO}


def _product(a, b):
    result = {}
    for ea, ca in a.items():
        for eb, cb in b.items():
            e = tuple(x + y for x, y in zip(ea, eb, strict=True))
            result[e] = _add(result.get(e, ZERO), _mul(ca, cb))
    return {e: c for e, c in result.items() if c != ZERO}


def _derivative(polynomial, i):
    result = {}
    for e, c in polynomial.items():
        if e[i]:
            result[tuple(v - int(k == i) for k, v in enumerate(e))] = (
                c[0] * e[i], c[1] * e[i],
            )
    return result


def _original_equation(side):
    # Original coefficients, independently reduced to pairs of Fractions.
    delta = ((-3, -3), (3, 0), (0, 3))
    psi, mixed = (-3, -6), (36, 18)
    result = {}
    for i, d in enumerate(delta):
        plane = tuple(3 * int(k == i) for k in range(3))
        result[plane + (1, 0)] = tuple(F(v) for v in (d if side == 1 else psi))
        result[plane + (0, 1)] = tuple(F(v) for v in (psi if side == 1 else (2*d[0], 2*d[1])))
    result[(1, 1, 1) + ((0, 1) if side == 1 else (1, 0))] = tuple(F(v) for v in mixed)
    return result


def _coefficient_bound(polynomial):
    return sum((abs(a) + abs(b) for a, b in polynomial.values()), F(0))


def _verify_identity(generators, multipliers, target):
    assert _sum(_product(g, c) for g, c in zip(generators, multipliers, strict=True)) == target


@pytest.fixture(scope="module")
def artifact():
    return json.loads(bound.OUTPUT.read_text())


@pytest.mark.parametrize("side", (1, 2))
def test_all_surface_identities_by_independent_fraction_convolution(artifact, side):
    record = artifact["surface_certificates"][side - 1]
    generators = tuple(_parse(g) for g in record["generators"])
    equation = _original_equation(side)
    assert generators == tuple(_derivative(equation, i) for i in range(5))
    assert (record["rows"], record["columns"], record["rank"]) == (45, 54, 45)
    assert len(record["identities"]) == 6
    constants = []
    for n, (raw, target) in enumerate(zip(record["identities"], record["targets"], strict=True)):
        multipliers = tuple(_parse(p) for p in raw)
        i, j = divmod(n, 2)
        expected = {tuple(4 * int(k == i) for k in range(3))
                    + tuple(2 * int(k == j) for k in range(2)): (F(1), F(0))}
        assert _parse(target) == expected
        _verify_identity(generators, multipliers, expected)
        for k, poly in enumerate(multipliers):
            assert all((sum(e[:3]), sum(e[3:])) == ((2, 1) if k < 3 else (1, 2))
                       for e in poly)
        constants.append(sum((_coefficient_bound(p)**2 for p in multipliers), F(0)))
    assert constants == [F(c) for c in record["coefficient_bounds_squared"]]
    tau = 1 / (324 * max(constants))
    assert tau == F(record["surface_gradient_squared_lower_bound"])
    assert tau == (F(1, 296) if side == 1 else F(6561, 397600))


@pytest.mark.parametrize("side", (1, 2))
def test_all_fiber_gradient_identities_by_independent_fraction_convolution(artifact, side):
    record = artifact["fiber_gradient_certificates"][side - 1]
    support = _parse(record["support"])
    assert support == _parse(artifact["base_separation_certificate"]["supports"][side - 1])
    expected_middle = (F(30), F(60)) if side == 1 else (-F(80, 81), -F(160, 81))
    expected_constant = -F(243) if side == 1 else -F(64, 243)
    assert support == {(6, 0): (F(1), F(0)), (3, 3): expected_middle,
                       (0, 6): (expected_constant, F(0))}
    derivatives = tuple(_derivative(_original_equation(side), i) for i in range(3))
    constants = []
    assert len(record["identities"]) == 3
    for i, (raw, target) in enumerate(zip(record["identities"], record["targets"], strict=True)):
        expected = {tuple(4 * int(k == i) for k in range(3)) + e: c
                    for e, c in support.items()}
        assert _parse(target) == expected
        multipliers = tuple(_parse(p) for p in raw)
        _verify_identity(derivatives, multipliers, expected)
        constants.append(sum((_coefficient_bound(p) for p in multipliers), F(0)))
    assert 9 * max(constants) == F(record["critical_support_over_plane_gradient_upper_bound"])
    assert 9 * max(constants) == (F(1260) if side == 1 else F(2689, 243))


def test_base_separation_and_final_bounds_recomputed_independently(artifact):
    base = artifact["base_separation_certificate"]
    assert (base["rows"], base["columns"], base["rank"]) == (12, 12, 12)
    supports = tuple(_parse(r) for r in base["supports"])
    maximum = F(0)
    for n, (raw, target) in enumerate(zip(base["identities"], base["targets"], strict=True)):
        expected = {((11, 0) if n == 0 else (0, 11)): (F(1), F(0))}
        assert _parse(target) == expected
        multipliers = tuple(_parse(p) for p in raw)
        _verify_identity(supports, multipliers, expected)
        assert all(sum(e) == 5 for p in multipliers for e in p)
        maximum = max(maximum, *(_coefficient_bound(p) for p in multipliers))
    assert maximum == F(base["maximum_coefficient_bound"])
    separation = 1 / (64 * maximum)
    assert separation == F(base["critical_support_sum_lower_bound"]) == F(3856615, 788999616)
    delta = (separation / (2 * F(1260)))**2 * F(1, 296)
    assert delta == F(12141615721, 955235133932696537923584)
    assert delta == F(artifact["conormal_lower_bound"]) > 0
    cover = 12 / delta
    assert cover == F(artifact["cover_weight_upper_without_pi_cubed"])
    assert cover / 9 == F(artifact["quotient_weight_upper_without_pi_cubed"])
    assert cover**2 / 4 == F(artifact["ideal_cover_weight_variance_upper_without_pi_to_six"])
    assert cover**2 / 324 == F(artifact["ideal_quotient_weight_variance_upper_without_pi_to_six"])


def test_coefficient_triangle_bound_is_exact_not_a_float_estimate():
    for a, b in product((F(-4, 3), F(0), F(7, 5)), repeat=2):
        assert a*a - a*b + b*b <= (abs(a) + abs(b))**2
        assert F(str(bound.modulus_upper(Eisenstein(a, b)))) == abs(a) + abs(b)


@pytest.mark.parametrize("complementary", (False, True))
def test_homogeneous_gradient_norms_match_intrinsic_denominator_on_actual_points(complementary):
    measure, weights = bound.measure, bound.weights
    x, u, p = (((1, 1, 1), (1, -1, 0), (1, 0)) if complementary
               else ((1, -1, 0), (1, 1, 1), (0, 1)))
    scale_x, scale_u, scale_p = Eisenstein(2, 1), Eisenstein(1, 2), OMEGA
    x = tuple(scale_x * c for c in x)
    u = tuple(scale_u * c for c in u)
    p = tuple(scale_p * c for c in p)
    norms = []
    for side, plane in ((1, x), (2, u)):
        equation = bound.surface_equation(side)
        assert measure._value(equation, plane + p).is_zero()
        values = tuple(measure._value(equation.derivative(i), plane + p) for i in range(5))
        assert sum((c * q for c, q in zip(plane, values[:3], strict=True)), Eisenstein(0)).is_zero()
        assert sum((c * q for c, q in zip(p, values[3:], strict=True)), Eisenstein(0)).is_zero()
        nx = sum((c.norm() for c in plane), Rational(0))
        np = sum((c.norm() for c in p), Rational(0))
        norms.append((sum((c.norm() for c in values[:3]), Rational(0)) / (nx**2 * np),
                      sum((c.norm() for c in values[3:]), Rational(0)) / nx**3))
    (ex, ax), (eu, au) = norms
    delta = ex * eu + ex * au + eu * ax
    assert delta >= bound.conormal_lower_bound()
    for xp, up in product(tuple(i for i, c in enumerate(x) if not c.is_zero()),
                          tuple(i for i, c in enumerate(u) if not c.is_zero())):
        chart = measure.ProjectionChart(xp, tuple(i for i in range(3) if i != xp)[1],
                                       up, tuple(i for i in range(3) if i != up)[1],
                                       0 if complementary else 1)
        point = measure.CoverPoint(x, u, p, chart.pivots)
        result = weights.local_weight(point, chart, volume_scale=1, covering_degree=9, bits=80)
        assert result.denominator.lower == result.denominator.upper == delta


@pytest.mark.parametrize("side", (False, 0, 3, 1.0, "1"))
def test_invalid_surface_labels_are_not_replaced_by_default_pencils(side):
    for function in (bound.surface_equation, bound.surface_certificates,
                     bound.fiber_gradient_certificates):
        with pytest.raises(ValueError, match="explicitly"):
            function(side)


@pytest.mark.parametrize("kwargs", (dict(volume_scale=0, covering_degree=9),
                                   dict(volume_scale=1, covering_degree=0),
                                   dict(volume_scale=1, covering_degree=False)))
def test_invalid_normalization_has_no_fallback(kwargs):
    with pytest.raises(ValueError):
        bound.global_bounds(**kwargs)


def test_exact_scale_and_covering_degree_are_explicit():
    original = bound.global_bounds(volume_scale=1, covering_degree=9)
    changed = bound.global_bounds(volume_scale=Eisenstein(2, 1), covering_degree=3)
    assert changed["conormal_lower_bound"] == original["conormal_lower_bound"]
    assert changed["cover_weight_upper_without_pi_cubed"] == (
        3 * original["cover_weight_upper_without_pi_cubed"]
    )
    assert changed["quotient_weight_upper_without_pi_cubed"] == (
        9 * original["quotient_weight_upper_without_pi_cubed"]
    )
    assert changed["ideal_cover_weight_variance_upper_without_pi_to_six"] == (
        9 * original["ideal_cover_weight_variance_upper_without_pi_to_six"]
    )


def test_full_artifact_reproduces_with_unresolved_physics_and_sampling(artifact):
    assert artifact == bound.bound_artifact()
    record = dict(artifact)
    digest = record.pop("artifact_digest")
    assert digest == hashlib.sha256(json.dumps(record, sort_keys=True,
                                               separators=(",", ":")).encode()).hexdigest()
    assert artifact["proof_sha256"] == hashlib.sha256(
        (bound.measure.ROOT / bound.PROOF).read_bytes(),
    ).hexdigest()
    for field in ("full_polynomial_identities_verified",
                  "quantitative_global_weight_bound_available",
                  "quantitative_ideal_weight_variance_bound_available"):
        assert artifact[field] is True
    for field in ("point_grid_used_as_proof", "practical_sampling_cost_certified",
                  "controlled_numerical_sampling_available",
                  "complete_global_input_coverage_certified",
                  "matrix_integrand_bounds_available", "numerical_metrics_available",
                  "physical_yukawas_available", "extension_point_selected",
                  "physical_kahler_class_selected", "vacuum_selected", "observational_inputs_used"):
        assert artifact[field] is False
