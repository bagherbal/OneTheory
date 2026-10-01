"""Certify critical fibers relevant to actual auxiliary-weight integrability.

Owns:
    Exact critical-value support of the two frozen cubic pencils and the scoped
    analytic moment contract derived in the accompanying local-density proof.

Depends on:
    Actual Schoen Cox cubics, exact polynomial arithmetic, and the previously
    certified residue and normalized auxiliary measure.

Must not:
    Replace the actual pencils by Fermat examples, sample approximate points,
    report quantitative variance bounds or confidence intervals, select moduli,
    or infer Ricci-flat/HYM convergence or physical Yukawas.

Phase 0:
    Research integrability certificate only; controlled sampling remains open.
"""

from __future__ import annotations

import hashlib
import json
from functools import reduce
from operator import mul

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial

from . import alternate_metric_measure as measure

OUTPUT = measure.OUTPUT.with_name("alternate_metric_weight_moments.json")


def _record(polynomial):
    return [[list(exponent), [str(value.a), str(value.b)]]
            for exponent, value in polynomial.terms]


def _coefficients(cubic):
    pure = ((3, 0, 0), (0, 3, 0), (0, 0, 3))
    if any(exponent not in (*pure, (1, 1, 1)) for exponent, _ in cubic.terms):
        raise ValueError("the critical-fiber derivation requires diagonal-plus-xyz cubics")
    return tuple(Eisenstein.coerce(cubic.coefficient(e)) for e in (*pure, (1, 1, 1)))


def actual_pencils():
    """Read the actual equations in the explicit shared chart t = mu/nu."""

    cox = measure.schoen_geometry().cover.cox
    f, g = _coefficients(cox.cubic_f), _coefficients(cox.cubic_g)
    t = measure._variables(1)[0]
    one = Polynomial.one(1, scalar_type=Eisenstein)
    first = tuple(t.scale(a) + one.scale(b) for a, b in zip(f, g, strict=True))
    second = tuple(t.scale(b) + one.scale(2 * a) for a, b in zip(f, g, strict=True))
    return (first[:3], first[3]), (second[:3], second[3])


def critical_certificate(pure, mixed):
    """Verify the exact nondegenerate nodal cases used in the analytic proof.

    A*x^3+B*y^3+C*z^3+D*xyz has critical support ABC*(D^3+27ABC).
    This is the reduced critical-value equation, NOT the full discriminant,
    whose triangular factors have multiplicity three.
    """

    if len(pure) != 3 or any(p.degree != 1 for p in pure):
        raise ValueError("three nonconstant affine pure coefficients are required")
    if mixed.degree > 1 or any(p.scalar_type is not Eisenstein for p in (*pure, mixed)):
        raise ValueError("the pencil requires affine coefficients over Q(omega)")
    if any(p.variable_count != 1 for p in (*pure, mixed)):
        raise ValueError("the shared projective-base chart must have one variable")
    product = reduce(mul, pure)
    triangle = mixed**3 + product.scale(27)
    support = product * triangle
    # Direct homogeneous evaluation at [mu:nu]=[1:0], not finite-chart sampling.
    leading = tuple(p.coefficient((1,)) for p in pure)
    infinity_product = reduce(mul, leading)
    infinity_triangle = mixed.coefficient((1,))**3 + 27 * infinity_product
    if infinity_product.is_zero() or infinity_triangle.is_zero():
        raise ValueError("a critical infinity fiber needs a separate local proof")
    if product.degree != 3 or triangle.degree != 3 or support.degree != 6:
        raise ValueError("the declared six-critical-value nodal category changed")
    if support.gcd(support.derivative()).degree != 0:
        raise ValueError("repeated critical values do not satisfy the nodal proof")
    if support.gcd(mixed).degree != 0:
        raise ValueError("a vanishing mixed coefficient at a critical value is excluded")
    return {
        "pure_coefficient_polynomials": [_record(p) for p in pure],
        "mixed_coefficient_polynomial": _record(mixed),
        "critical_support_monic": _record(support.monic()),
        "full_discriminant_monic": _record((product * triangle**3).monic()),
        "critical_support_degree": support.degree,
        "squarefree_gcd_degree": support.gcd(support.derivative()).degree,
        "pure_triangle_gcd_degree": product.gcd(triangle).degree,
        "critical_mixed_gcd_degree": support.gcd(mixed).degree,
        "infinity_product": [str(infinity_product.a), str(infinity_product.b)],
        "infinity_triangle": [str(infinity_triangle.a), str(infinity_triangle.b)],
        "axis_nodal_fiber_count": product.degree,
        "triangle_fiber_count": triangle.degree,
        "nodal_critical_point_count": product.degree + 3 * triangle.degree,
    }, support.monic()


def moment_artifact():
    """Record exact algebra plus the human-readable, explicitly scoped proof."""

    parent = json.loads(measure.OUTPUT.read_text(encoding="utf-8"))
    parent_digest = parent.pop("artifact_digest")
    def canonical(record):
        return json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    if (hashlib.sha256(canonical(parent)).hexdigest() != parent_digest
        or parent_digest != "eefa94d3f7b368cc13f4bad2659393129063345ef97097a9e7e0db32ad1ac488"):
        raise ValueError("the actual normalized auxiliary measure prerequisite changed")
    certificates = tuple(critical_certificate(*pencil) for pencil in actual_pencils())
    coprime = certificates[0][1].gcd(certificates[1][1])
    if coprime.degree != 0:
        raise ValueError("simultaneous critical fibers invalidate the smooth local model")
    payload = {
        "schema": "alternate-metric-weight-moments-v1",
        "measure_artifact_digest": parent_digest,
        "base_chart": "t = mu/nu",
        "actual_equations": ["mu*F(x)+nu*G(x)", "2*nu*F(u)+mu*G(u)"],
        "pencils": [certificate for certificate, _ in certificates],
        "two_critical_supports_gcd_degree": coprime.degree,
        "critical_infinity_fibers": False,
        "proof": "research/experiments/scientific_genesis/ALTERNATE_METRIC_WEIGHT_MOMENTS_NOTE.md",
        "proof_sha256": hashlib.sha256((measure.ROOT / (
            "research/experiments/scientific_genesis/ALTERNATE_METRIC_WEIGHT_MOMENTS_NOTE.md"
        )).read_bytes()).hexdigest(),
        "reference_for_triangle_factorization": "https://arxiv.org/abs/math/0611590",
        "normalized_probability_law": "A/9; A = FS_x wedge FS_u wedge FS_p",
        "target_volume": "nonzero smooth residue volume on the actual compact cover",
        "critical_locus_complex_codimension": 2,
        "auxiliary_density_transverse_order": 2,
        "weight_transverse_order": -2,
        "radial_q_moment_power": "5 - 2*q",
        "nonnegative_moment_integrability": "finite exactly for 0 <= q < 3",
        "weight_second_moment_finite": True,
        "weight_third_moment_finite": False,
        "quantitative_variance_bound_available": False,
        "standard_finite_third_absolute_moment_error_bound_applicable_to_weight": False,
        "controlled_numerical_sampling_available": False,
        "numerical_metrics_available": False,
        "physical_yukawas_available": False,
        "extension_point_selected": False,
        "vacuum_selected": False,
        "observational_inputs_used": False,
        "next_required_object": (
            "correct controlled projective proposal law, quantitative second-moment or "
            "truncation bounds, integration error, and Ricci-flat/HYM convergence"
        ),
    }
    payload["artifact_digest"] = hashlib.sha256(canonical(payload)).hexdigest()
    return payload


def write_artifact():
    payload = moment_artifact()
    OUTPUT.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(write_artifact()["artifact_digest"])
