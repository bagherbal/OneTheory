"""Evaluate captured auxiliary inputs numerically in their retained root charts.

Owns:
    Binary64 discovery evaluation of existing projective input formulas, actual
    pencil restrictions, parent-seeded roots and the derived conormal weight.

Depends on:
    Captured named prefixes, original native root receipts, actual published
    cubic polynomials and the existing full-section curvature consumer.

Must not:
    Export a native membership certificate, reseed, change charts or selected
    roots, generate entropy, or promote numerical residuals to exact claims.

Phase 0:
    Research discovery coordinates only; independent certification stays separate.
"""

import math
from fractions import Fraction
from functools import cache

import numpy as np

from . import retained_root_refinement as certified
from . import trial_connection_curvature as curvature


def projective_midpoint(address, *, bits):
    """Apply the original sorted-spacing and relative-phase law to fixed cells.

    Spacings are subtracted exactly before conversion, including near ties.
    This evaluates the midpoint parameter, not the exact ideal random point.
    The first phase is zero solely to remove the common projective phase.
    """

    if type(bits) is not int or bits < 1:
        raise ValueError("a positive captured input prefix length is required")

    def midpoint(prefix):
        return Fraction(2*prefix.index(bits) + 1, 1 << (bits + 1))

    ordered = (Fraction(0), *sorted(midpoint(p) for p in address.spacing), Fraction(1))
    spacings = np.asarray([float(b-a) for a, b in zip(ordered[:-1], ordered[1:], strict=True)])
    phases = np.asarray([0, *(2*math.pi*float(midpoint(p)) for p in address.phases)])
    return np.sqrt(spacings)*np.exp(1j*phases)


@cache
def pencil_program():
    """Compile only the actual exact cubic coefficients, not a new geometry."""

    cox = certified.native.schoen_geometry().cover.cox
    return tuple(tuple((powers, curvature.features._complex(c)) for powers, c in p.terms)
                 for p in (cox.cubic_f, cox.cubic_g))


def _value(program, point):
    return sum(c*np.prod(point**np.asarray(powers)) for powers, c in program)


def _gradient(program, point):
    result = np.zeros(3, dtype=np.complex128)
    for powers, coefficient in program:
        for axis, power in enumerate(powers):
            if power:
                reduced = list(powers)
                reduced[axis] -= 1
                result[axis] += power*coefficient*np.prod(point**np.asarray(reduced))
    return result


def _line(covector, frame):
    """Keep the caller's original pivot and parameter-axis order."""

    if not covector[frame.pivot]:
        raise ArithmeticError("the declared numerical line pivot vanishes")
    basis = np.zeros((2, 3), dtype=np.complex128)
    for index, axis in enumerate(frame.axes):
        basis[index, axis] = 1
        basis[index, frame.pivot] = -covector[axis]/covector[frame.pivot]
    if not np.all(np.isfinite(basis)):
        raise ArithmeticError("the declared numerical line frame is unresolved")
    return basis


def _restrict(program, basis):
    coefficients = np.zeros(4, dtype=np.complex128)
    for powers, coefficient in program:
        term = np.asarray([coefficient])
        for axis, power in enumerate(powers):
            for _ in range(power):
                term = np.convolve(term, basis[:, axis])
        coefficients[:len(term)] += term
    return coefficients


def inside_saved_disk(center, disk):
    """Prove only that this floating candidate lies inside the saved complex disk.

    Binary64 real/imaginary parts are exact rationals. An outward bound for
    sqrt(3) bounds the saved Eisenstein center's imaginary part. This does not
    certify a root, actual cover membership, or ideal-input accuracy.
    """

    if not math.isfinite(center.real) or not math.isfinite(center.imag):
        return False
    a, b = (Fraction(value) for value in disk["center"])
    lo, hi = certified.draws.inputs._sqrt_endpoints(certified.Rational(3), 80)
    imaginary = sorted((b*Fraction(lo)/2, b*Fraction(hi)/2))
    real_gap = Fraction(float(center.real)) - a + b/2
    imaginary_gap = max(abs(Fraction(float(center.imag)) - endpoint) for endpoint in imaginary)
    return real_gap**2 + imaginary_gap**2 < Fraction(disk["radius"])**2


def numerical_roots(coefficients, saved, *, steps, residual_tolerance):
    """Keep every saved seed and chart; no sorting or nearest-root selection."""

    if (type(steps) is not int or steps < 1 or not math.isfinite(residual_tolerance)
            or not 0 < residual_tolerance < 1):
        raise ValueError("explicit positive Newton work and residual policy required")
    coefficients = np.asarray(coefficients, dtype=np.complex128)
    if coefficients.shape != (4,) or not np.all(np.isfinite(coefficients)):
        raise ArithmeticError("actual binary cubic coefficients are numerically unresolved")
    if len(saved["root_disks"]) != 3:
        raise ValueError("all three original projective root receipts are required")
    parameters, records = [], []
    for disk in saved["root_disks"]:
        pivot = disk["parameter_pivot"]
        if type(pivot) is not int or pivot not in (0, 1):
            raise ValueError("an original parameter chart is required")
        c = coefficients if pivot == 0 else coefficients[::-1]
        a, b = (Fraction(value) for value in disk["center"])
        center = curvature.features._complex(curvature.Eisenstein(a, b))
        for _ in range(steps):
            value, derivative = c[-1], 0j
            for coefficient in reversed(c[:-1]):
                derivative = derivative*center + value
                value = value*center + coefficient
            if not derivative or not np.isfinite(derivative):
                raise ArithmeticError("the retained numerical Newton derivative is unresolved")
            center -= value/derivative
        if not inside_saved_disk(center, disk):
            raise ArithmeticError("the numerical candidate left its original certified root disk")
        powers = center**np.arange(4)
        scale = float(np.sum(np.abs(c*powers)))
        residual = float(abs(np.dot(c, powers)))
        # At a zero root all monomials may vanish; use the coefficient norm,
        # explicitly, not an automatic physical or input normalization.
        scale = max(scale, float(np.max(np.abs(c))))
        if not scale or not math.isfinite(residual/scale) or residual/scale > residual_tolerance:
            raise ArithmeticError("the actual cubic numerical residual exceeds the declared policy")
        parameters.append(np.asarray((1, center) if pivot == 0 else (center, 1)))
        records.append({"parameter_pivot": pivot, "center_real_imag": [center.real, center.imag],
                        "scaled_residual_discovery": residual/scale,
                        "candidate_inside_original_disk_exact": True,
                        "native_root_certificate_available": False})
    return parameters, records


def evaluate_geometry(address, history, *, bits, steps, residual_tolerance,
                      volume_scale, covering_degree):
    """Return discovery coordinates, original branch data and derived weight."""

    component, _ = address.choices()
    if history["status"] != "admitted" or history["component"] != component:
        raise ValueError("the original admitted input and mixture component are required")
    frames = certified.draws.declared_policy()
    f, g = pencil_program()
    first = projective_midpoint(address.first, bits=bits)
    second = projective_midpoint(address.second, bits=bits)
    roots, families = [], history["all_root_families"]
    branch = history["selected_branch"]

    def solve(line, base, side, saved):
        cf, cg = _restrict(f, line), _restrict(g, line)
        coefficients = (cf*base[0] + cg*base[1] if side == 1 else
                        2*cf*base[1] + cg*base[0])
        parameters, records = numerical_roots(coefficients, saved, steps=steps,
                                             residual_tolerance=residual_tolerance)
        roots.append(records)
        return parameters

    if component == "A":
        if len(families) != 2 or any(type(i) is not int or not 0 <= i < 3 for i in branch):
            raise ValueError("the original A branch and both complete families are required")
        base = projective_midpoint(address.base, bits=bits)
        lx, lu = _line(first, frames.first), _line(second, frames.second)
        x = solve(lx, base, 1, families[0])[branch[0]] @ lx
        u = solve(lu, base, 2, families[1])[branch[1]] @ lu
    else:
        source, covector, frame, side, index = (
            (first, second, frames.second, 1, branch[1]) if component == "Bx" else
            (second, first, frames.first, 2, branch[0]))
        if (len(families) != 1 or type(index) is not int or not 0 <= index < 3
                or branch[0 if side == 1 else 1] != "fixed"):
            raise ValueError("the original fixed-point branch and complete family are required")
        fv, gv = _value(f, source), _value(g, source)
        base = np.asarray((-gv, fv) if side == 1 else (-2*fv, gv))
        line = _line(covector, frame)
        partner = solve(line, base, 3-side, families[0])[index] @ line
        x, u = (source, partner) if side == 1 else (partner, source)
    normalized = []
    for group, pivot in zip((x, u, base), history["frame_policy"]["chart"], strict=True):
        if not group[pivot]:
            raise ArithmeticError("the retained numerical homogeneous chart pivot vanishes")
        values = group/group[pivot]
        values[pivot] = 1  # The declared projective chart identity is exact by convention.
        normalized.extend(values)
    coordinates = np.asarray(normalized, dtype=np.complex128)
    if not np.all(np.isfinite(coordinates)):
        raise ArithmeticError("the retained normalized discovery coordinates are unresolved")
    weight, residuals = homogeneous_weight((x, u, base), volume_scale=volume_scale,
                                         covering_degree=covering_degree)
    if max(residuals) > residual_tolerance:
        raise ArithmeticError("actual numerical cover equation residual exceeds policy")
    return coordinates, weight, {"component": component, "selected_branch": branch,
        "root_families_discovery": roots, "cover_equation_residuals_discovery": residuals,
        "native_cover_membership_certified": False, "floating_mantissa_bits": 53,
        "input_prefix_bits": bits}


def homogeneous_weight(point, *, volume_scale, covering_degree):
    """Numerically consume the existing positive homogeneous conormal identity.

    The same derived rule as uncertain_cover_weights is 12*norm(scale)/(9*D)
    for degree nine; the caller declares degree and scale. Pi cubed is excluded.
    No weights are calibrated against volume or curvature targets.
    """

    if type(covering_degree) is not int or covering_degree < 1 or not volume_scale:
        raise ValueError("explicit nonzero volume scale and positive covering degree required")
    x, u, p = (np.asarray(group, dtype=np.complex128) for group in point)
    f, g = pencil_program()
    nx, nu, np_ = (float(np.vdot(group, group).real) for group in (x, u, p))
    if min(nx, nu, np_) <= 0:
        raise ArithmeticError("homogeneous coordinate norms are numerically unresolved")
    fx, gx, fu, gu = (_value(f, x), _value(g, x), _value(f, u), _value(g, u))
    dx = p[0]*_gradient(f, x) + p[1]*_gradient(g, x)
    du = p[0]*_gradient(g, u) + 2*p[1]*_gradient(f, u)
    ex, eu = float(np.vdot(dx, dx).real)/(nx**2*np_), float(np.vdot(du, du).real)/(nu**2*np_)
    hx, hu = (abs(fx)**2 + abs(gx)**2)/nx**3, (abs(gu)**2 + 4*abs(fu)**2)/nu**3
    denominator = ex*eu + ex*hu + eu*hx
    weight = 12*abs(volume_scale)**2/(covering_degree*denominator)
    equation_residuals = [abs(p[0]*fx + p[1]*gx)/(np_**0.5*nx**1.5),
                          abs(p[0]*gu + 2*p[1]*fu)/(np_**0.5*nu**1.5)]
    if not math.isfinite(weight) or weight <= 0 or not all(map(math.isfinite, equation_residuals)):
        raise ArithmeticError("the unchanged conormal weight is numerically unresolved")
    return float(weight), [float(value) for value in equation_residuals]
