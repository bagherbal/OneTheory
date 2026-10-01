"""Certify all projective roots of the actual Schoen sampling configurations.

Owns:
    Exact line restrictions, declared omega-lattice root proposals, rational
    Rouche inclusion certificates, disjointness, and the root at infinity.

Depends on:
    Existing exact Eisenstein norms and polynomial derivatives/GCDs, actual
    frozen cubic pencils, and the explicit projective integration law.

Must not:
    Treat proposal centers as exact cover points, discard an infinite root,
    accept small residuals instead of a certificate, select physical moduli,
    or infer sampling accuracy or Ricci-flat/HYM convergence.

Phase 0:
    Research-only certified intersection roots; controlled sampling is open.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from itertools import combinations, product
from math import factorial, isqrt
from pathlib import Path

from onetheory.core.errors import FailedConvergence
from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational, coerce_rational
from onetheory.math.polynomials import Polynomial, gcd
from onetheory.models.heterotic_schoen.geometry import schoen_geometry

from .alternate_metric_measure import OUTPUT as MEASURE_OUTPUT
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_metric_projective_roots.json"


def modulus_bounds(value, bits):
    """Enclose |value| rationally using integer square roots, without floats."""

    if type(bits) is not int or bits < 1:
        raise ValueError("modulus bounds require a positive integer bit count")
    norm = Eisenstein.coerce(value).norm()
    scale = 1 << bits
    radicand = norm.numerator * norm.denominator * scale**2
    floor = isqrt(radicand)
    lower = Rational(floor, norm.denominator * scale)
    upper = (lower if floor**2 == radicand
             else Rational(floor + 1, norm.denominator * scale))
    return lower, upper


@dataclass(frozen=True, slots=True)
class RootPolicy:
    """Explicit error radius, coefficient mesh, bound precision, and work cap.

    Proposals are rounded to the mesh 2^-coefficient_bits in the declared
    ordered scalar basis (1,omega), with ties to even. Seeds are the shifted
    Cauchy radius times the first n entries of (1,2omega,3omega^2).
    Unequal radii avoid trapping real polynomials in conjugation-symmetric
    proposal sets. This policy is fixed; a failure never triggers reseeding.
    These are computational proposals, not chosen points in physical moduli.
    """

    radius: Rational
    coefficient_bits: int
    modulus_bits: int
    max_iterations: int

    def __post_init__(self):
        radius = coerce_rational(self.radius)
        for bits in (self.coefficient_bits, self.modulus_bits, self.max_iterations):
            if type(bits) is not int or bits < 1:
                raise ValueError("root policy work limits must be positive integers")
        if radius <= Rational(8, 1 << self.coefficient_bits):
            raise ValueError("the radius must exceed eight coefficient-mesh units")
        object.__setattr__(self, "radius", radius)


def _value(polynomial, center):
    return Eisenstein.coerce(polynomial.substitute((center,)).coefficient(()))


def _taylor_coefficients(polynomial, center):
    result = []
    derivative = polynomial
    for order in range(polynomial.degree + 1):
        result.append(_value(derivative, center) / factorial(order))
        derivative = derivative.derivative()
    return tuple(result)


@dataclass(frozen=True, slots=True)
class RootDisk:
    """An exact algebraic root description, not a point equal to its center.

    For positive radius, |linear| exceeds the sum of all other Taylor terms
    on the boundary. Rouche therefore gives exactly one simple enclosed root.
    Radius zero is permitted only for an exactly evaluated simple field root.
    """

    polynomial: Polynomial
    center: Eisenstein
    radius: Rational
    taylor: tuple[Eisenstein, ...]
    modulus_lower: tuple[Rational, ...]
    modulus_upper: tuple[Rational, ...]

    def __post_init__(self):
        if (self.polynomial.variable_count != 1 or self.polynomial.scalar_type is not Eisenstein
            or not 1 <= self.polynomial.degree <= 3):
            raise ValueError("a root certificate requires degree one through three")
        center = Eisenstein.coerce(self.center)
        radius = coerce_rational(self.radius)
        taylor = tuple(Eisenstein.coerce(c) for c in self.taylor)
        lower = tuple(coerce_rational(c) for c in self.modulus_lower)
        upper = tuple(coerce_rational(c) for c in self.modulus_upper)
        if taylor != _taylor_coefficients(self.polynomial, center):
            raise ValueError("the certificate Taylor coefficients are not actual coefficients")
        if len(lower) != len(taylor) or len(upper) != len(taylor):
            raise ValueError("every Taylor coefficient requires an explicit modulus enclosure")
        for value, lo, hi in zip(taylor, lower, upper, strict=True):
            if not 0 <= lo <= hi or not lo**2 <= value.norm() <= hi**2:
                raise ValueError("a rational modulus bound does not enclose its exact value")
        if radius < 0:
            raise ValueError("root disks cannot have negative radius")
        if radius == 0:
            if not taylor[0].is_zero() or taylor[1].is_zero():
                raise ValueError("a zero-radius certificate requires an exact simple root")
        elif lower[1] * radius <= (upper[0] + sum(
            (upper[k] * radius**k for k in range(2, len(taylor))), Rational(0),
        )):
            raise ValueError("the exact Rouche dominance inequality is not strict")
        for name, value in (("center", center), ("radius", radius), ("taylor", taylor),
                            ("modulus_lower", lower), ("modulus_upper", upper)):
            object.__setattr__(self, name, value)


def certify_disk(polynomial, center, radius, modulus_bits):
    """Certify a supplied center and radius; guesses are never returned as roots."""

    if (polynomial.variable_count != 1 or polynomial.scalar_type is not Eisenstein
        or not 1 <= polynomial.degree <= 3):
        raise ValueError("the certificate requires a nonconstant Q(omega) polynomial of degree <=3")
    center = Eisenstein.coerce(center)
    taylor = _taylor_coefficients(polynomial, center)
    bounds = tuple(modulus_bounds(value, modulus_bits) for value in taylor)
    if taylor[0].is_zero() and not taylor[1].is_zero():
        radius = Rational(0)
    return RootDisk(polynomial, center, radius, taylor,
                    tuple(pair[0] for pair in bounds), tuple(pair[1] for pair in bounds))


def _disjoint(disks):
    return all((left.center - right.center).norm() > (left.radius + right.radius)**2
               for left, right in combinations(disks, 2))


def _quantize(value, bits):
    scale = 1 << bits
    return Eisenstein(Rational(round(value.a * scale), scale),
                      Rational(round(value.b * scale), scale))


@dataclass(frozen=True, slots=True)
class CompleteRoots:
    """A complete, pairwise disjoint set of simple finite roots."""

    polynomial: Polynomial
    disks: tuple[RootDisk, ...]
    policy: RootPolicy
    iterations: int

    def __post_init__(self):
        disks = tuple(self.disks)
        if (self.polynomial.variable_count != 1 or self.polynomial.scalar_type is not Eisenstein
            or not 1 <= self.polynomial.degree <= 3):
            raise ValueError("complete roots require an exact polynomial of degree 1 through 3")
        if len(disks) != self.polynomial.degree:
            raise ValueError("the root count does not exhaust the actual polynomial degree")
        if any(d.polynomial != self.polynomial or d.radius > self.policy.radius for d in disks):
            raise ValueError("root disks use a different polynomial or exceed the requested radius")
        if not _disjoint(disks):
            raise ValueError("root disks must be strictly pairwise disjoint")
        if (type(self.iterations) is not int
            or not 0 <= self.iterations <= self.policy.max_iterations):
            raise ValueError("root iteration count exceeds its explicit work policy")
        object.__setattr__(self, "disks", disks)


def complete_roots(polynomial, policy):
    """Bounded simultaneous proposals, accepted only by exact complete certificates."""

    if (polynomial.variable_count != 1 or polynomial.scalar_type is not Eisenstein
        or not 1 <= polynomial.degree <= 3):
        raise ValueError("root isolation requires a Q(omega) polynomial of degree 1 through 3")
    if gcd(polynomial, polynomial.derivative()).degree != 0:
        raise ValueError("the intersection polynomial has a repeated root; transversality fails")
    monic = polynomial.monic()
    degree = monic.degree
    if degree == 1:
        center = -Eisenstein.coerce(monic.coefficient((0,)))
        return CompleteRoots(polynomial, (certify_disk(polynomial, center, policy.radius,
                                                      policy.modulus_bits),), policy, 0)
    coefficients = tuple(Eisenstein.coerce(monic.coefficient((i,))) for i in range(degree))
    radius = Rational(1) + max(modulus_bounds(c, policy.modulus_bits)[1] for c in coefficients)
    shift = -coefficients[-1] / degree
    phases = (Eisenstein(1), 2 * OMEGA, 3 * OMEGA**2)[:degree]
    centers = tuple(shift + phase * radius for phase in phases)
    for iteration in range(policy.max_iterations + 1):
        candidates = []
        for center in centers:
            try:
                candidates.append(certify_disk(polynomial, center, policy.radius,
                                               policy.modulus_bits))
            except ValueError:
                break  # An uncertified proposal is never exported.
        if len(candidates) == degree and _disjoint(candidates):
            return CompleteRoots(polynomial, tuple(candidates), policy, iteration)
        if iteration == policy.max_iterations:
            break
        next_centers = []
        for i, center in enumerate(centers):
            denominator = Eisenstein(1)
            for j, other in enumerate(centers):
                if i != j:
                    denominator *= center - other
            if denominator.is_zero():
                raise FailedConvergence("root proposals collided; no automatic seed fallback")
            next_centers.append(_quantize(center - _value(monic, center) / denominator,
                                           policy.coefficient_bits))
        centers = tuple(next_centers)
    raise FailedConvergence("no complete disjoint root certificate within the declared work cap")


@dataclass(frozen=True, slots=True)
class ProjectiveLine:
    """An exact plane line with caller-supplied ordered parameter basis (s,t)."""

    first: tuple[Eisenstein, ...]
    second: tuple[Eisenstein, ...]

    def __post_init__(self):
        first = tuple(Eisenstein.coerce(c) for c in self.first)
        second = tuple(Eisenstein.coerce(c) for c in self.second)
        if len(first) != 3 or len(second) != 3:
            raise ValueError("each line parameter vector must have three coordinates")
        if Matrix(tuple(zip(first, second, strict=True)), scalar_type=Eisenstein).rank() != 2:
            raise ValueError("the explicit projective line basis is dependent")
        object.__setattr__(self, "first", first)
        object.__setattr__(self, "second", second)


def restrict_pencil(line, p, factor):
    """Restrict the ACTUAL homogeneous cubic pencil to an explicitly based line."""

    p = tuple(Eisenstein.coerce(c) for c in p)
    if len(p) != 2 or all(c.is_zero() for c in p):
        raise ValueError("a nonzero exact P1 point is required")
    if type(factor) is not int or factor not in (1, 2):
        raise ValueError("choose the first or second actual pencil explicitly")
    s = Polynomial.monomial((1, 0), scalar_type=Eisenstein)
    t = Polynomial.monomial((0, 1), scalar_type=Eisenstein)
    images = tuple(s * a + t * b for a, b in zip(line.first, line.second, strict=True))
    cox = schoen_geometry().cover.cox
    f, g = cox.cubic_f.substitute(images), cox.cubic_g.substitute(images)
    return f * p[0] + g * p[1] if factor == 1 else f * (2 * p[1]) + g * p[0]


@dataclass(frozen=True, slots=True)
class ProjectiveRoots:
    """All roots in a declared parameter chart, including its missing point."""

    homogeneous: Polynomial
    parameter_pivot: int
    finite: CompleteRoots
    infinity_multiplicity: int

    def __post_init__(self):
        if self.homogeneous.variable_count != 2 or self.homogeneous.scalar_type is not Eisenstein:
            raise ValueError("projective roots require an exact binary polynomial")
        if type(self.parameter_pivot) is not int or self.parameter_pivot not in (0, 1):
            raise ValueError("a caller-supplied projective parameter chart is required")
        if not self.homogeneous.terms or any(sum(m) != 3 for m, _ in self.homogeneous.terms):
            raise ValueError("the homogeneous pencil restriction must be a nonzero cubic")
        variable = Polynomial.monomial((1,), scalar_type=Eisenstein)
        expected = self.homogeneous.substitute(
            (1, variable) if self.parameter_pivot == 0 else (variable, 1),
        )
        if expected != self.finite.polynomial:
            raise ValueError("the finite root polynomial does not use the declared parameter chart")
        if (type(self.infinity_multiplicity) is not int
            or self.infinity_multiplicity != 3 - expected.degree
            or self.infinity_multiplicity not in (0, 1)):
            raise ValueError("the projective root at infinity is missing, repeated, or miscounted")

    @property
    def count(self):
        return len(self.finite.disks) + self.infinity_multiplicity


def projective_roots(homogeneous, *, parameter_pivot, policy):
    """Retain the exact infinite root rather than dropping a leading-zero branch."""

    if type(parameter_pivot) is not int or parameter_pivot not in (0, 1):
        raise ValueError("a caller-supplied projective parameter chart is required")
    if (homogeneous.variable_count != 2 or homogeneous.scalar_type is not Eisenstein
        or not homogeneous.terms
        or any(sum(m) != 3 for m, _ in homogeneous.terms)):
        raise ValueError("the line restriction must be a nonzero homogeneous cubic")
    variable = Polynomial.monomial((1,), scalar_type=Eisenstein)
    finite = homogeneous.substitute((1, variable) if parameter_pivot == 0 else (variable, 1))
    infinity = 3 - finite.degree
    if infinity not in (0, 1):
        raise ValueError("the intersection at infinity is repeated; transversality fails")
    return ProjectiveRoots(homogeneous, parameter_pivot, complete_roots(finite, policy), infinity)


@dataclass(frozen=True, slots=True)
class IntersectionRoots:
    """All nine algebraic intersection points; no center is declared a cover point."""

    first_line: ProjectiveLine
    second_line: ProjectiveLine
    p: tuple[Eisenstein, ...]
    first: ProjectiveRoots
    second: ProjectiveRoots

    def __post_init__(self):
        p = tuple(Eisenstein.coerce(c) for c in self.p)
        if (restrict_pencil(self.first_line, p, 1) != self.first.homogeneous
            or restrict_pencil(self.second_line, p, 2) != self.second.homogeneous):
            raise ValueError("root certificates are not restrictions of the actual Schoen pencils")
        if self.first.count != 3 or self.second.count != 3:
            raise ValueError("the transverse configuration must retain all nine intersection roots")
        object.__setattr__(self, "p", p)

    @property
    def root_pairs(self):
        """Use original finite disk indices plus an explicit infinity marker."""

        first = tuple(range(len(self.first.finite.disks))) + (
            ("infinity",) if self.first.infinity_multiplicity else ()
        )
        second = tuple(range(len(self.second.finite.disks))) + (
            ("infinity",) if self.second.infinity_multiplicity else ()
        )
        return tuple(product(first, second))


def intersection_roots(first_line, second_line, p, *, parameter_pivots, policy):
    """Certify a supplied exact projective configuration, not its sampling law."""

    if not isinstance(parameter_pivots, tuple) or len(parameter_pivots) != 2:
        raise ValueError("two explicit ordered parameter pivots are required")
    p = tuple(Eisenstein.coerce(c) for c in p)
    first = projective_roots(restrict_pencil(first_line, p, 1),
                             parameter_pivot=parameter_pivots[0], policy=policy)
    second = projective_roots(restrict_pencil(second_line, p, 2),
                              parameter_pivot=parameter_pivots[1], policy=policy)
    return IntersectionRoots(first_line, second_line, p, first, second)


def _scalar_record(value):
    value = Eisenstein.coerce(value)
    return [str(value.a), str(value.b)]


def _polynomial_record(polynomial):
    return [[list(monomial), _scalar_record(coefficient)]
            for monomial, coefficient in polynomial.terms]


def _projective_record(result):
    return {
        "homogeneous_cubic": _polynomial_record(result.homogeneous),
        "parameter_pivot": result.parameter_pivot,
        "finite_polynomial": _polynomial_record(result.finite.polynomial),
        "iterations": result.finite.iterations,
        "infinity_multiplicity": result.infinity_multiplicity,
        "total_root_count": result.count,
        "finite_disks": [{
            "center": _scalar_record(disk.center), "radius": str(disk.radius),
            "taylor": [_scalar_record(c) for c in disk.taylor],
            "modulus_lower": [str(value) for value in disk.modulus_lower],
            "modulus_upper": [str(value) for value in disk.modulus_upper],
        } for disk in result.finite.disks],
    }


def root_artifact():
    """Archive reproducible actual-geometry certificates, not integration samples."""

    measure_digest, parent = _verified_payload(MEASURE_OUTPUT)
    if parent.get("schema") != "alternate-metric-measure-v1":
        raise ValueError("the declared projective integration method is missing")
    policy = RootPolicy(Rational(1, 2**30), 60, 80, 128)
    configurations = []
    for name, first_line, second_line, p, pivots in (
        ("finite_chart", ProjectiveLine((1, 0, 0), (0, 1, 1)),
         ProjectiveLine((1, 1, 0), (0, 0, 1)), (1, 1), (0, 0)),
        ("infinity_branch", ProjectiveLine((1, 0, 0), (0, 1, -1)),
         ProjectiveLine((1, 1, 0), (0, 0, 1)), (0, 1), (0, 0)),
    ):
        actual = intersection_roots(first_line, second_line, p,
                                    parameter_pivots=pivots, policy=policy)
        configurations.append({
            "name": name,
            "first_line": [[_scalar_record(c) for c in vector]
                           for vector in (first_line.first, first_line.second)],
            "second_line": [[_scalar_record(c) for c in vector]
                            for vector in (second_line.first, second_line.second)],
            "P1_point": [_scalar_record(c) for c in actual.p],
            "first": _projective_record(actual.first),
            "second": _projective_record(actual.second),
            "all_nine_root_pairs": [list(pair) for pair in actual.root_pairs],
        })
    payload = {
        "schema": "alternate-metric-projective-roots-v1",
        "measure_artifact_digest": measure_digest,
        "coefficient_field": "Q(omega), omega^2+omega+1=0",
        "coordinate_convention": "line(s,t)=s*first+t*second; pivot is set to one",
        "root_policy": {
            "requested_radius": str(policy.radius),
            "coefficient_bits": policy.coefficient_bits,
            "modulus_bound_bits": policy.modulus_bits,
            "max_iterations": policy.max_iterations,
            "rounding": "nearest 2^-coefficient_bits in (1,omega), ties to even",
            "seeds": "shifted Cauchy bound times first n entries of (1,2omega,3omega^2)",
        },
        "inclusion_proof": (
            "lower(|f'(c)|)*r > upper(|f(c)|) + sum(k=2..degree) "
            "upper(|f^(k)(c)/k!|)*r^k; Rouche against f'(c)(z-c) gives one root"
        ),
        "completeness_proof": (
            "pairwise disjoint one-root disks exhaust the exact finite degree; "
            "3 minus finite degree is retained as the projective infinity multiplicity"
        ),
        "generic_verified_inclusion_reference": "https://www.tuhh.de/ti3/paper/rump/RuOi09a.pdf",
        "actual_configurations": configurations,
        "configuration_law": "declared exact regression probes, not SU-uniform samples",
        "exact_Qomega_input_intersection_roots_certified": True,
        "centers_are_exact_cover_points": False,
        "projective_uniform_sampling_law_implemented": False,
        "controlled_numerical_sampling_available": False,
        "bounded_section_and_density_evaluation_available": False,
        "numerical_metrics_available": False,
        "physical_yukawas_available": False,
        "extension_point_selected": False,
        "vacuum_selected": False,
        "observational_inputs_used": False,
        "next_required_object": (
            "propagate certified root uncertainty through explicit cover charts, "
            "section values and measure densities; implement the declared SU-uniform "
            "proposal law with precision and integration-error control"
        ),
    }
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    return payload


def write_artifact():
    """Write the exact root certificates only after full projective validation."""

    payload = root_artifact()
    OUTPUT.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = write_artifact()
    print(f"artifact_digest: {result['artifact_digest']}")
