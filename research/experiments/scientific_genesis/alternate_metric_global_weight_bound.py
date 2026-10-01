"""Derive global auxiliary weight bounds from exact polynomial certificates.

Owns:
    Homogeneous surface-gradient identities, critical-support separation,
    coefficient norm bounds, and a conservative global conormal lower bound.

Depends on:
    Original cubic pencils, exact Polynomial and Matrix arithmetic, verified
    projection-free weights, and declared unit homogeneous FS representatives.

Must not:
    Replace a global proof by point sampling, fit constants, choose physical
    moduli, infer a numerical sampler, or assert metric convergence or observables.

Phase 0:
    Research polynomial certificates; physical normalization remains unresolved.
"""

from __future__ import annotations

import hashlib
import json
from functools import cache
from itertools import product

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein, Rational
from onetheory.math.polynomials import Polynomial

from . import alternate_metric_projection_free_weights as weights

measure, moments = weights.measure, weights.positive.moments
OUTPUT = weights.OUTPUT.with_name("alternate_metric_global_weight_bound.json")
PROOF = "research/experiments/scientific_genesis/ALTERNATE_METRIC_GLOBAL_WEIGHT_BOUND_NOTE.md"


def _monomials(count, degree):
    return tuple(e for e in product(range(degree + 1), repeat=count) if sum(e) == degree)


def _bimonomials(x_degree, p_degree):
    return tuple(a + b for a in _monomials(3, x_degree) for b in _monomials(2, p_degree))


def modulus_upper(value):
    """Use the exact triangle inequality |a+b omega| <= |a|+|b|."""

    value = Eisenstein.coerce(value)
    return abs(value.a) + abs(value.b)


def coefficient_bound(polynomial):
    """Bound an exact polynomial on unit homogeneous coordinate groups."""

    return sum((modulus_upper(c) for _, c in polynomial.terms), Rational(0))


@cache
def surface_equation(side):
    """Use (x0,x1,x2,mu,nu) and the original factor-two pencil convention."""

    if type(side) is not int or side not in (1, 2):
        raise ValueError("choose the first or second original surface explicitly")
    variables = measure._variables(5)
    cox = measure.schoen_geometry().cover.cox
    f, g = cox.cubic_f.substitute(variables[:3]), cox.cubic_g.substitute(variables[:3])
    mu, nu = variables[3:]
    return mu * f + nu * g if side == 1 else 2 * nu * f + mu * g


def _solve_polynomial_identities(generators, multipliers, targets, basis):
    """Solve a declared finite coefficient system, then verify every full identity."""

    columns = tuple(generator * Polynomial.monomial(exponent, scalar_type=Eisenstein)
                    for generator, exponents in zip(generators, multipliers, strict=True)
                    for exponent in exponents)
    rows = tuple(tuple(poly.coefficient(e) for poly in (*columns, *targets)) for e in basis)
    reduced, pivots = Matrix(rows, scalar_type=Eisenstein).rref()
    if any(p >= len(columns) for p in pivots):
        raise ValueError("the declared polynomial targets have no certificate at this bidegree")
    solutions = []
    for target_index, target in enumerate(targets):
        coefficients = [Eisenstein(0) for _ in columns]
        for row, pivot in enumerate(pivots):
            coefficients[pivot] = reduced.rows[row][len(columns) + target_index]
        grouped = []
        offset = 0
        for exponents in multipliers:
            grouped.append(Polynomial(((e, coefficients[offset + i])
                                       for i, e in enumerate(exponents)),
                                      variable_count=generators[0].variable_count,
                                      scalar_type=Eisenstein))
            offset += len(exponents)
        total = Polynomial.zero(target.variable_count, scalar_type=Eisenstein)
        for generator, coefficient in zip(generators, grouped, strict=True):
            total += generator * coefficient
        if total != target:
            raise ValueError("an exact polynomial certificate failed full multiplication")
        solutions.append(tuple(grouped))
    return len(basis), len(columns), len(pivots), tuple(solutions)


@cache
def surface_certificates(side):
    """Certify all six x_i^4 p_j^2 with the five actual surface derivatives."""

    equation = surface_equation(side)
    generators = tuple(equation.derivative(i) for i in range(5))
    multipliers = (_bimonomials(2, 1),) * 3 + (_bimonomials(1, 2),) * 2
    targets = tuple(Polynomial.monomial(tuple(4 * int(k == i) for k in range(3))
        + tuple(2 * int(k == j) for k in range(2)), scalar_type=Eisenstein)
                    for i in range(3) for j in range(2))
    rows, columns, rank, identities = _solve_polynomial_identities(
        generators, multipliers, targets, _bimonomials(4, 2),
    )
    constants = tuple(sum((coefficient_bound(poly)**2 for poly in identity), Rational(0))
                      for identity in identities)
    maximum = max(constants)
    if maximum <= 0:
        raise ValueError("a positive exact surface certificate coefficient bound is required")
    return {"rows": rows, "columns": columns, "rank": rank,
            "generators": generators, "targets": targets, "identities": identities,
            "coefficient_bounds_squared": constants,
            "surface_gradient_squared_lower_bound": Rational(1) / (324 * maximum)}


@cache
def critical_separation():
    """Certify both degree-eleven base monomials from the actual degree-six supports."""

    certificates = tuple(moments.critical_certificate(*p) for p in moments.actual_pencils())
    monic = tuple(p for _, p in certificates)
    supports = tuple(Polynomial((( (e[0], 6 - e[0]), c) for e, c in poly.terms),
                                variable_count=2, scalar_type=Eisenstein) for poly in monic)
    targets = tuple(Polynomial.monomial(e, scalar_type=Eisenstein) for e in ((11, 0), (0, 11)))
    multipliers = (_monomials(2, 5),) * 2
    rows, columns, rank, identities = _solve_polynomial_identities(
        supports, multipliers, targets, _monomials(2, 11),
    )
    maximum = max(coefficient_bound(poly) for identity in identities for poly in identity)
    if maximum <= 0:
        raise ValueError("a positive homogeneous Bezout coefficient bound is required")
    return {"rows": rows, "columns": columns, "rank": rank,
            "supports": supports, "targets": targets, "identities": identities,
            "maximum_coefficient_bound": maximum,
            "critical_support_sum_lower_bound": Rational(1) / (64 * maximum)}


@cache
def fiber_gradient_certificates(side):
    """Certify R_i(mu,nu) x_j^4 in the ideal of the actual three plane derivatives."""

    if type(side) is not int or side not in (1, 2):
        raise ValueError("choose the first or second original surface explicitly")
    pure, mixed = moments.actual_pencils()[side - 1]
    base = tuple(Polynomial((( (e[0], 1 - e[0]), c) for e, c in poly.terms),
                            variable_count=2, scalar_type=Eisenstein)
                 for poly in (*pure, mixed))
    a, b, c, d = base
    raw = a * b * c * (d**3 + (a * b * c).scale(27))
    lead = Eisenstein.coerce(raw.coefficient((6, 0)))
    support = raw.scale(lead.inverse())
    if support != critical_separation()["supports"][side - 1]:
        raise ValueError("the actual homogeneous reduced critical support changed")
    variables = measure._variables(5)
    x = variables[:3]
    embedded = tuple(poly.substitute(variables[3:]) for poly in base)
    pure, mixed = embedded[:3], embedded[3]
    triangle = mixed**3 + (pure[0] * pure[1] * pure[2]).scale(27)
    equation = sum((p * q**3 for p, q in zip(pure, x, strict=True)),
                   Polynomial.zero(5, scalar_type=Eisenstein)) + mixed * x[0] * x[1] * x[2]
    if equation != surface_equation(side):
        raise ValueError("the gradient identity is not attached to the original equation")
    derivatives = tuple(equation.derivative(i) for i in range(3))
    identities = []
    targets = []
    lifted_support = support.substitute(variables[3:])
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        coefficients = [Polynomial.zero(5, scalar_type=Eisenstein) for _ in range(3)]
        multiplier = (pure[j] * pure[k]).scale(lead.inverse() / 3)
        coefficients[i] = multiplier * (triangle * x[i]**2
            - (pure[j] * pure[k] * mixed * x[j] * x[k]).scale(9))
        coefficients[j] = multiplier * (pure[k] * mixed**2 * x[k]**2).scale(3)
        coefficients[k] = -multiplier * mixed**3 * x[i] * x[k]
        target = lifted_support * x[i]**4
        result = sum((p * q for p, q in zip(coefficients, derivatives, strict=True)),
                     Polynomial.zero(5, scalar_type=Eisenstein))
        if result != target:
            raise ValueError("the full critical-support gradient identity failed")
        identities.append(tuple(coefficients))
        targets.append(target)
    constant = 9 * max(sum((coefficient_bound(p) for p in identity), Rational(0))
                       for identity in identities)
    if constant <= 0:
        raise ValueError("a positive exact fiber-gradient coefficient bound is required")
    return {"support": support, "targets": tuple(targets), "identities": tuple(identities),
            "critical_support_over_plane_gradient_upper_bound": constant}


@cache
def conormal_lower_bound():
    """Use exact homogeneous identities to control the entire actual smooth cover."""

    surfaces = tuple(surface_certificates(side) for side in (1, 2))
    fibers = tuple(fiber_gradient_certificates(side) for side in (1, 2))
    separation = critical_separation()["critical_support_sum_lower_bound"]
    gradient_constant = max(p["critical_support_over_plane_gradient_upper_bound"] for p in fibers)
    plane_norm_lower = separation / (2 * gradient_constant)
    surface_norm_squared_lower = min(p["surface_gradient_squared_lower_bound"] for p in surfaces)
    return plane_norm_lower**2 * surface_norm_squared_lower


def global_bounds(*, volume_scale, covering_degree):
    """Return coefficients with pi^3/pi^6 explicitly factored out, not numerical draws."""

    if type(covering_degree) is not int or covering_degree < 1:
        raise ValueError("an explicit positive integer covering degree is required")
    scale = Eisenstein.coerce(volume_scale)
    if scale.is_zero():
        raise ValueError("an explicit nonzero residue scale is required")
    lower = conormal_lower_bound()
    if lower <= 0:
        raise ValueError("the global conormal certificate is not strictly positive")
    cover = 12 * scale.norm() / lower
    quotient = cover / covering_degree
    return {"conormal_lower_bound": lower, "cover_weight_upper_without_pi_cubed": cover,
            "quotient_weight_upper_without_pi_cubed": quotient,
            "ideal_cover_weight_variance_upper_without_pi_to_six": cover**2 / 4,
            "ideal_quotient_weight_variance_upper_without_pi_to_six": quotient**2 / 4}


def _polynomial_record(poly):
    return [[list(e), [str(c.a), str(c.b)]] for e, c in poly.terms]


def _certificate_record(record):
    result = {}
    for key, value in record.items():
        if key in ("generators", "targets", "supports"):
            result[key] = [_polynomial_record(poly) for poly in value]
        elif key == "support":
            result[key] = _polynomial_record(value)
        elif key == "identities":
            result[key] = [[_polynomial_record(poly) for poly in row] for row in value]
        elif isinstance(value, Rational):
            result[key] = str(value)
        elif isinstance(value, tuple):
            result[key] = [str(v) for v in value]
        else:
            result[key] = value
    return result


def bound_artifact():
    """Record full exact certificate polynomials before any global-bound claim."""

    digest, parent = weights.positive.matrices.fiber._verified_payload(weights.OUTPUT)
    if digest != "cb4eb886edf94ab72b737bc8e3c23a25d2355243557fee40dfe62d24c7cf1e97":
        raise ValueError("the actual projection-free normalization prerequisite changed")
    payload = {
        "schema": "alternate-metric-global-weight-bound-v1",
        "projection_free_weight_artifact_digest": digest,
        "moment_artifact_digest": parent["moment_artifact_digest"],
        "surface_coordinate_order": ["x0", "x1", "x2", "mu", "nu"],
        "base_coordinate_order": ["mu", "nu"],
        "certificate_convention": "lexicographic monomials; nonpivot coefficients set to zero",
        "coefficient_norm_bound": "sum(abs(a)+abs(b)) for coefficients a+b*omega",
        "unit_groups": "sum |x_i|^2 = sum |u_i|^2 = |mu|^2+|nu|^2 = 1",
        "surface_certificates": [_certificate_record(surface_certificates(s)) for s in (1, 2)],
        "fiber_gradient_certificates": [_certificate_record(fiber_gradient_certificates(s))
                                        for s in (1, 2)],
        "base_separation_certificate": _certificate_record(critical_separation()),
        "normalized_volume_scale": ["1", "0"], "covering_degree": 9,
        **{k: str(v) for k, v in global_bounds(volume_scale=1, covering_degree=9).items()},
        "proof": PROOF,
        "proof_sha256": hashlib.sha256((measure.ROOT / PROOF).read_bytes()).hexdigest(),
        "full_polynomial_identities_verified": True,
        "quantitative_global_weight_bound_available": True,
        "quantitative_ideal_weight_variance_bound_available": True,
        "point_grid_used_as_proof": False,
        "practical_sampling_cost_certified": False,
        "controlled_numerical_sampling_available": False,
        "complete_global_input_coverage_certified": False,
        "matrix_integrand_bounds_available": False,
        "numerical_metrics_available": False, "physical_yukawas_available": False,
        "extension_point_selected": False, "physical_kahler_class_selected": False,
        "vacuum_selected": False, "observational_inputs_used": False,
        "next_required_object": (
            "controlled independent positive-law proposals with certified numeric inputs, "
            "actual matrix integrand bounds, practical section throughput, integration errors "
            "and Ricci-flat/HYM convergence"
        ),
    }
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    return payload


def write_artifact():
    payload = bound_artifact()
    OUTPUT.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = write_artifact()
    print(payload["artifact_digest"])
    print("conormal_lower_bound", payload["conormal_lower_bound"])
    print("cover_weight_upper_without_pi_cubed", payload["cover_weight_upper_without_pi_cubed"])
