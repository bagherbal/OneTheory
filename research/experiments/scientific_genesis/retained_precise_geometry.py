"""Evaluate retained input geometry with explicitly declared multiprecision.

Owns:
    The unchanged midpoint, named line-frame, saved-root and conormal formulas
    evaluated at a caller-declared precision before binary64 consumer conversion.

Depends on:
    Actual exact pencil coefficients, original native receipts, captured inputs
    and an isolated mpmath context; no new model or measured quantity.

Must not:
    Change an input, root, chart, residual threshold or H1, claim a rounding
    certificate, hide consumer conversion or substitute successful cases.

Phase 0:
    Research arithmetic refinement only; global accuracy remains unresolved.
"""

import math
from fractions import Fraction

import numpy as np
from mpmath import __version__, mp

from . import retained_numerical_geometry as original


def _rational(ctx, value):
    value = Fraction(value) if isinstance(value, (str, int)) else value
    return ctx.mpf(value.numerator)/value.denominator


def _eisenstein(ctx, value):
    a, b = _rational(ctx, value.a), _rational(ctx, value.b)
    return ctx.mpc(a-b/2, b*ctx.sqrt(3)/2)


def _exact_real(ctx, value):
    """Recover a context value's actual dyadic number, not decimal rounding."""

    if not ctx.isfinite(value):
        raise ArithmeticError("a finite multiprecision candidate is required")
    mantissa, exponent = ctx.frexp(value)
    numerator = int(ctx.ldexp(mantissa, ctx.prec))
    shift = ctx.prec-exponent
    return Fraction(numerator, 1 << shift) if shift >= 0 else Fraction(numerator*(1 << -shift))


def projective_midpoint(ctx, address, *, bits):
    if type(bits) is not int or bits < 1:
        raise ValueError("a positive captured input prefix length is required")

    def midpoint(prefix):
        return Fraction(2*prefix.index(bits)+1, 1 << (bits+1))

    ordered = (Fraction(0), *sorted(midpoint(p) for p in address.spacing), Fraction(1))
    phases = (ctx.zero, *(2*ctx.pi*_rational(ctx, midpoint(p)) for p in address.phases))
    return tuple(ctx.sqrt(_rational(ctx, b-a))*ctx.exp(ctx.j*phase)
                 for a, b, phase in zip(ordered[:-1], ordered[1:], phases, strict=True))


def _programs(ctx):
    cox = original.certified.native.schoen_geometry().cover.cox
    return tuple(tuple((powers, _eisenstein(ctx, c)) for powers, c in polynomial.terms)
                 for polynomial in (cox.cubic_f, cox.cubic_g))


def _value(ctx, program, point):
    return ctx.fsum(c*ctx.fprod(value**power for value, power in zip(point, powers, strict=True))
                    for powers, c in program)


def _gradient(ctx, program, point):
    return tuple(ctx.fsum(coefficient*powers[axis]*ctx.fprod(
        point[j]**(power-int(j == axis)) for j, power in enumerate(powers))
        for powers, coefficient in program if powers[axis]) for axis in range(3))


def _line(ctx, covector, frame):
    if not covector[frame.pivot]:
        raise ArithmeticError("the original multiprecision line pivot vanishes")
    basis = [[ctx.zero]*3 for _ in range(2)]
    for row, axis in enumerate(frame.axes):
        basis[row][axis] = ctx.one
        basis[row][frame.pivot] = -covector[axis]/covector[frame.pivot]
    return basis


def _restrict(ctx, program, basis):
    result = [ctx.zero]*4
    for powers, coefficient in program:
        term = [coefficient]
        for axis, power in enumerate(powers):
            for _ in range(power):
                next_term = [ctx.zero]*(len(term)+1)
                for j, c in enumerate(term):
                    next_term[j] += c*basis[0][axis]
                    next_term[j+1] += c*basis[1][axis]
                term = next_term
        for j, c in enumerate(term):
            result[j] += c
    return result


def _inside(ctx, candidate, disk):
    a, b = map(Fraction, disk["center"])
    lo, hi = original.certified.draws.inputs._sqrt_endpoints(original.certified.Rational(3), 80)
    imaginary = (b*Fraction(lo)/2, b*Fraction(hi)/2)
    real_gap = _exact_real(ctx, candidate.real)-a+b/2
    imaginary_gap = max(abs(_exact_real(ctx, candidate.imag)-bound) for bound in imaginary)
    return real_gap**2+imaginary_gap**2 < Fraction(disk["radius"])**2


def _roots(ctx, coefficients, saved, *, steps, residual_tolerance):
    if len(saved["root_disks"]) != 3:
        raise ValueError("all three original root receipts are required")
    parameters, records = [], []
    for disk in saved["root_disks"]:
        pivot = disk["parameter_pivot"]
        if type(pivot) is not int or pivot not in (0, 1):
            raise ValueError("the original parameter chart is required")
        c = coefficients if pivot == 0 else coefficients[::-1]
        seed = original.curvature.Eisenstein(*(Fraction(v) for v in disk["center"]))
        center = _eisenstein(ctx, seed)
        for _ in range(steps):
            value, derivative = c[-1], ctx.zero
            for coefficient in reversed(c[:-1]):
                derivative = derivative*center+value
                value = value*center+coefficient
            if not derivative or not ctx.isfinite(derivative):
                raise ArithmeticError("the retained multiprecision Newton derivative is unresolved")
            center -= value/derivative
        if not _inside(ctx, center, disk):
            raise ArithmeticError("the multiprecision candidate left its original native disk")
        terms = [coefficient*center**j for j, coefficient in enumerate(c)]
        scale = max(ctx.fsum(abs(term) for term in terms), max(map(abs, c)))
        residual = abs(ctx.fsum(terms))/scale if scale else ctx.inf
        if not ctx.isfinite(residual) or residual > _rational(ctx, Fraction(residual_tolerance)):
            raise ArithmeticError("the actual multiprecision cubic residual exceeds policy")
        parameters.append((ctx.one, center) if pivot == 0 else (center, ctx.one))
        records.append({"parameter_pivot": pivot,
            "candidate_center_exact_dyadic": [str(_exact_real(ctx, part))
                                              for part in (center.real, center.imag)],
            "scaled_residual_discovery": float(residual),
            "candidate_inside_original_disk_exact": True,
            "native_root_certificate_available": False})
    return parameters, records


def _weight(ctx, programs, point, *, volume_scale, covering_degree):
    f, g = programs
    x, u, p = point
    nx, nu, np_ = (ctx.fsum(abs(c)**2 for c in group) for group in point)
    if min(nx, nu, np_) <= 0:
        raise ArithmeticError("the multiprecision homogeneous norms are unresolved")
    fx, gx, fu, gu = (_value(ctx, program, group) for group, program in
                      ((x, f), (x, g), (u, f), (u, g)))
    dx = [p[0]*a+p[1]*b for a, b in zip(_gradient(ctx, f, x), _gradient(ctx, g, x), strict=True)]
    du = [p[0]*b+2*p[1]*a for a, b in zip(_gradient(ctx, f, u), _gradient(ctx, g, u), strict=True)]
    ex = ctx.fsum(abs(c)**2 for c in dx)/(nx**2*np_)
    eu = ctx.fsum(abs(c)**2 for c in du)/(nu**2*np_)
    hx, hu = (abs(fx)**2+abs(gx)**2)/nx**3, (abs(gu)**2+4*abs(fu)**2)/nu**3
    denominator = ex*eu+ex*hu+eu*hx
    if not denominator or not ctx.isfinite(denominator):
        raise ArithmeticError("the unchanged multiprecision conormal denominator is unresolved")
    weight = 12*abs(volume_scale)**2/(covering_degree*denominator)
    residuals = [abs(p[0]*fx+p[1]*gx)/(ctx.sqrt(np_)*nx**ctx.mpf('1.5')),
                 abs(p[0]*gu+2*p[1]*fu)/(ctx.sqrt(np_)*nu**ctx.mpf('1.5'))]
    return weight, residuals


def evaluate_geometry(address, history, *, bits, steps, residual_tolerance,
                      volume_scale, covering_degree, precision_bits):
    """Retain the original geometry law with explicit arithmetic/consumer precision."""

    if (type(precision_bits) is not int or precision_bits < bits
            or type(steps) is not int or steps < 1
            or type(covering_degree) is not int or covering_degree < 1
            or not math.isfinite(residual_tolerance) or not 0 < residual_tolerance < 1
            or not volume_scale):
        raise ValueError(
            "explicit compatible arithmetic, root, residual and quotient policies required")
    component, _ = address.choices()
    if history["status"] != "admitted" or history["component"] != component:
        raise ValueError("the original admitted mixture component is required")
    ctx = mp.clone()
    ctx.prec = precision_bits
    programs = f, g = _programs(ctx)
    frames = original.certified.draws.declared_policy()
    first = projective_midpoint(ctx, address.first, bits=bits)
    second = projective_midpoint(ctx, address.second, bits=bits)
    families, branch, roots = history["all_root_families"], history["selected_branch"], []

    def solve(line, base, side, saved):
        cf, cg = _restrict(ctx, f, line), _restrict(ctx, g, line)
        coefficients = [a*base[0]+b*base[1] if side == 1 else 2*a*base[1]+b*base[0]
                        for a, b in zip(cf, cg, strict=True)]
        parameters, records = _roots(ctx, coefficients, saved, steps=steps,
                                    residual_tolerance=residual_tolerance)
        roots.append(records)
        return [tuple(ctx.fsum(parameter[i]*line[i][axis] for i in range(2)) for axis in range(3))
                for parameter in parameters]

    if component == "A":
        base = projective_midpoint(ctx, address.base, bits=bits)
        x = solve(_line(ctx, first, frames.first), base, 1, families[0])[branch[0]]
        u = solve(_line(ctx, second, frames.second), base, 2, families[1])[branch[1]]
    else:
        source, covector, frame, side, index = (
            (first, second, frames.second, 1, branch[1]) if component == "Bx" else
            (second, first, frames.first, 2, branch[0]))
        if len(families) != 1 or branch[0 if side == 1 else 1] != "fixed":
            raise ValueError("the original fixed-point branch and family are required")
        fv, gv = _value(ctx, f, source), _value(ctx, g, source)
        base = (-gv, fv) if side == 1 else (-2*fv, gv)
        partner = solve(_line(ctx, covector, frame), base, 3-side, families[0])[index]
        x, u = (source, partner) if side == 1 else (partner, source)
    coordinates = []
    for group, pivot in zip((x, u, base), history["frame_policy"]["chart"], strict=True):
        if not group[pivot]:
            raise ArithmeticError("the original multiprecision projective chart pivot vanishes")
        coordinates.extend(c/group[pivot] for c in group)
    weight, residuals = _weight(ctx, programs, (x, u, base),
                              volume_scale=ctx.mpc(volume_scale), covering_degree=covering_degree)
    tolerance = _rational(ctx, Fraction(residual_tolerance))
    if any(not ctx.isfinite(r) or r > tolerance for r in residuals):
        raise ArithmeticError("actual multiprecision cover equation residual exceeds policy")
    converted = np.asarray([complex(float(c.real), float(c.imag)) for c in coordinates])
    converted_weight = float(weight)
    if (not np.all(np.isfinite(converted)) or not math.isfinite(converted_weight)
            or converted_weight <= 0):
        raise ArithmeticError("binary64 full-section consumer conversion is unresolved")
    return converted, converted_weight, {"component": component, "selected_branch": branch,
        "root_families_discovery": roots,
        "cover_equation_residuals_discovery": list(map(float, residuals)),
        "coordinates_exact_dyadic_discovery": [[str(_exact_real(ctx, c.real)),
                                               str(_exact_real(ctx, c.imag))] for c in coordinates],
        "native_cover_membership_certified": False, "floating_mantissa_bits": 53,
        "geometry_working_precision_bits": precision_bits, "input_prefix_bits": bits,
        "mpmath_version": __version__, "numerical_error_bound_certified": False}
