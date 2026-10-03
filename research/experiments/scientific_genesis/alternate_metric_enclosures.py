"""Propagate certified intersection uncertainty into actual local geometry.

Owns:
    Rational circular enclosures, explicit projective normalization, Laurent
    coefficient evaluation, and bounded residue/auxiliary importance densities.

Depends on:
    Exact field norms, certified projective roots, the frozen projection
    polynomials, and the declared residue and Fubini--Study conventions.

Must not:
    Admit disk centers as exact cover points, invert a possible zero, silently
    change charts, select moduli, or infer sampling or metric convergence.

Phase 0:
    Research-only local enclosures; universal fiber bounds are supplied separately.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from onetheory.math.numbers import Eisenstein, Rational, coerce_rational

from . import alternate_metric_projective_roots as roots
from .alternate_metric_fiber_evaluation import CoverPoint
from .alternate_metric_measure import auxiliary_cover_mass, projection_polynomials
from .mixed_schoen_outer_universal_cone import _verified_payload

OUTPUT = roots.OUTPUT.with_name("alternate_metric_enclosures.json")


def _bits(bits):
    if type(bits) is not int or bits < 1:
        raise ValueError("an explicit positive integer bound precision is required")


def _down(value, bits):
    scaled = value * (1 << bits)
    return Rational(scaled.numerator // scaled.denominator, 1 << bits)


def _up(value, bits):
    return -_down(-value, bits)


@dataclass(frozen=True, slots=True)
class Interval:
    """Closed rational interval with outward dyadic endpoint rounding.

    Exact singleton values are never rounded. Only uncertain endpoints are
    rounded, at the declared precision; precision is never increased silently.
    """

    lower: Rational
    upper: Rational
    bits: int

    def __post_init__(self):
        _bits(self.bits)
        lo, hi = coerce_rational(self.lower), coerce_rational(self.upper)
        if lo > hi:
            raise ValueError("interval endpoints must be ordered")
        if lo != hi:
            lo, hi = _down(lo, self.bits), _up(hi, self.bits)
        object.__setattr__(self, "lower", lo)
        object.__setattr__(self, "upper", hi)

    def _coerce(self, other):
        if isinstance(other, Interval):
            if other.bits != self.bits:
                raise ValueError("incompatible declared bound precisions")
            return other
        value = coerce_rational(other)
        return Interval(value, value, self.bits)

    def __add__(self, other):
        other = self._coerce(other)
        return Interval(self.lower + other.lower, self.upper + other.upper, self.bits)

    def __neg__(self):
        return Interval(-self.upper, -self.lower, self.bits)

    def __sub__(self, other):
        return self + -self._coerce(other)

    def __mul__(self, other):
        other = self._coerce(other)
        corners = tuple(a * b for a in (self.lower, self.upper)
                        for b in (other.lower, other.upper))
        return Interval(min(corners), max(corners), self.bits)

    def inverse(self):
        if self.lower <= 0 <= self.upper:
            raise ZeroDivisionError("the denominator interval may contain zero")
        return Interval(Rational(1) / self.upper, Rational(1) / self.lower, self.bits)

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()

    def __pow__(self, exponent):
        if type(exponent) is not int:
            raise TypeError("interval powers must be integers")
        if exponent < 0:
            return self.inverse() ** -exponent
        if exponent == 0:
            return Interval(Rational(1), Rational(1), self.bits)
        endpoints = self.lower**exponent, self.upper**exponent
        lower = (Rational(0) if exponent % 2 == 0 and self.lower <= 0 <= self.upper
                 else min(endpoints))
        return Interval(lower, max(endpoints), self.bits)

    def contains(self, value):
        value = coerce_rational(value)
        return self.lower <= value <= self.upper

    @property
    def width(self):
        return self.upper - self.lower


@dataclass(frozen=True, slots=True)
class Ball:
    """Circular complex enclosure with exact Q(omega) center and rational radius.

    Center arithmetic is exact by default. An explicit center_bits policy
    rounds uncertain centers to that dyadic mesh and adds the certified norm
    of the displacement to the radius. Radius-zero values stay exact.
    """

    center: Eisenstein
    radius: Rational
    bits: int
    center_bits: int | None = None

    def __post_init__(self):
        _bits(self.bits)
        radius = coerce_rational(self.radius)
        if radius < 0:
            raise ValueError("ball radii must be nonnegative")
        center = Eisenstein.coerce(self.center)
        if self.center_bits is not None:
            _bits(self.center_bits)
            if radius:
                mesh = 1 << self.center_bits
                rounded = Eisenstein(Rational(round(center.a * mesh), mesh),
                                     Rational(round(center.b * mesh), mesh))
                displacement = roots.modulus_bounds(center - rounded, self.bits)[1]
                center, radius = rounded, radius + displacement
        object.__setattr__(self, "center", center)
        object.__setattr__(self, "radius", _up(radius, self.bits))

    def _coerce(self, other):
        if isinstance(other, Ball):
            if other.bits != self.bits:
                raise ValueError("incompatible declared bound precisions")
            if other.center_bits != self.center_bits:
                if other.radius == 0:
                    return Ball(other.center, other.radius, self.bits, self.center_bits)
                if self.radius != 0 or self.center_bits is not None:
                    raise ValueError("incompatible declared uncertain-center precisions")
            return other
        return Ball(Eisenstein.coerce(other), Rational(0), self.bits, self.center_bits)

    def __add__(self, other):
        other = self._coerce(other)
        policy = self.center_bits if self.center_bits is not None else other.center_bits
        return Ball(self.center + other.center, self.radius + other.radius, self.bits, policy)

    def __neg__(self):
        return Ball(-self.center, self.radius, self.bits, self.center_bits)

    def __sub__(self, other):
        return self + -self._coerce(other)

    def __mul__(self, other):
        other = self._coerce(other)
        left = roots.modulus_bounds(self.center, self.bits)[1]
        right = roots.modulus_bounds(other.center, self.bits)[1]
        radius = left * other.radius + right * self.radius + self.radius * other.radius
        policy = self.center_bits if self.center_bits is not None else other.center_bits
        return Ball(self.center * other.center, radius, self.bits, policy)

    def inverse(self):
        if self.radius == 0:
            return Ball(self.center.inverse(), Rational(0), self.bits, self.center_bits)
        lower = roots.modulus_bounds(self.center, self.bits)[0]
        if lower <= self.radius:
            raise ZeroDivisionError("the denominator ball may contain zero")
        radius = self.radius / (lower * (lower - self.radius))
        return Ball(self.center.inverse(), radius, self.bits, self.center_bits)

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()

    def __pow__(self, exponent):
        if type(exponent) is not int:
            raise TypeError("ball powers must be integers")
        if exponent < 0:
            return self.inverse() ** -exponent
        result = self._coerce(1)
        base = self
        while exponent:
            if exponent % 2:
                result = result * base
            base = base * base
            exponent //= 2
        return result

    def conjugate(self):
        return Ball(self.center.conjugate(), self.radius, self.bits, self.center_bits)

    def norm_interval(self):
        if self.radius == 0:
            norm = self.center.norm()
            return Interval(norm, norm, self.bits)
        lo, hi = roots.modulus_bounds(self.center, self.bits)
        return Interval(max(Rational(0), lo - self.radius)**2,
                        (hi + self.radius)**2, self.bits)

    def contains(self, value):
        return (self.center - Eisenstein.coerce(value)).norm() <= self.radius**2


def polynomial_value(polynomial, coordinates):
    """Enclose a declared exact polynomial; do not substitute enclosure centers."""

    coordinates = tuple(coordinates)
    if not coordinates or len(coordinates) != polynomial.variable_count:
        raise ValueError("polynomial coordinates must match the declared variable count")
    if any(not isinstance(c, Ball) for c in coordinates):
        raise TypeError("polynomial bounds require explicit coordinate balls")
    if any(c.bits != coordinates[0].bits for c in coordinates):
        raise ValueError("incompatible declared bound precisions")
    result = coordinates[0]._coerce(0)
    for exponents, coefficient in polynomial.terms:
        term = result._coerce(coefficient)
        for value, exponent in zip(coordinates, exponents, strict=True):
            term = term * value**exponent
        result = result + term
    return result


def _line_point(line, projective, index, bits):
    if index == "infinity":
        if not projective.infinity_multiplicity:
            raise ValueError("this certified root list has no infinity branch")
        vector = line.second if projective.parameter_pivot == 0 else line.first
        return tuple(Ball(c, Rational(0), bits) for c in vector)
    if type(index) is not int or not 0 <= index < len(projective.finite.disks):
        raise ValueError("a certified root index is required")
    disk = projective.finite.disks[index]
    root = Ball(disk.center, disk.radius, bits)
    fixed, variable = ((line.first, line.second) if projective.parameter_pivot == 0
                       else (line.second, line.first))
    return tuple(root * b + a for a, b in zip(fixed, variable, strict=True))


@dataclass(frozen=True, slots=True)
class BoundedCoverPoint:
    """A certified algebraic cover point enclosed in explicit homogeneous charts.

    Membership follows from the actual restriction certificates, not a small
    equation residual. Stored coordinate balls are normalized enclosures.
    """

    intersection: roots.IntersectionRoots | roots.PointLineRoots
    root_pair: tuple
    chart: tuple[int, int, int]
    bits: int
    x: tuple[Ball, ...] = field(init=False)
    u: tuple[Ball, ...] = field(init=False)
    p: tuple[Ball, ...] = field(init=False)

    def __post_init__(self):
        _bits(self.bits)
        if not isinstance(self.intersection, (roots.IntersectionRoots, roots.PointLineRoots)):
            raise TypeError("an actual certified projective intersection is required")
        if (not isinstance(self.root_pair, tuple) or len(self.root_pair) != 2
            or any(type(i) is not int and i not in ("infinity", "fixed") for i in self.root_pair)
            or self.root_pair not in self.intersection.root_pairs):
            raise ValueError("the root pair is absent from the complete certified intersection")
        if (not isinstance(self.chart, tuple) or len(self.chart) != 3
            or any(type(i) is not int or not 0 <= i < size
                   for i, size in zip(self.chart, (3, 3, 2), strict=True))):
            raise ValueError("three explicit homogeneous chart pivots are required")
        if isinstance(self.intersection, roots.PointLineRoots):
            source = tuple(Ball(c, Rational(0), self.bits) for c in self.intersection.source_point)
            partner = _line_point(self.intersection.partner_line, self.intersection.partner,
                                  self.root_pair[1 if self.intersection.source_side == 1 else 0],
                                  self.bits)
            planes = (source, partner) if self.intersection.source_side == 1 else (partner, source)
        else:
            planes = (
                _line_point(self.intersection.first_line, self.intersection.first,
                            self.root_pair[0], self.bits),
                _line_point(self.intersection.second_line, self.intersection.second,
                            self.root_pair[1], self.bits),
            )
        groups = (*planes, tuple(Ball(c, Rational(0), self.bits) for c in self.intersection.p))
        self._normalize_groups(groups)

    def _normalize_groups(self, groups):
        """Reuse explicit chart normalization after actual membership is certified."""

        for name, group, pivot in zip(("x", "u", "p"), groups, self.chart, strict=True):
            # The normalized pivot is identically one, not an uncertain q/q.
            inverse = group[pivot].inverse()
            normalized = tuple(group[0]._coerce(1) if i == pivot else c * inverse
                               for i, c in enumerate(group))
            object.__setattr__(self, name, normalized)

    @property
    def cell(self):
        return tuple((i,) for i in self.chart)

    def monomial(self, exponents):
        if len(exponents) != 8:
            raise ValueError("a cover Laurent monomial needs eight exponents")
        result = self.x[0]._coerce(1)
        for group, pivot, powers in zip((self.x, self.u, self.p), self.chart,
                                        (exponents[:3], exponents[3:6], exponents[6:]),
                                        strict=True):
            for i, (value, exponent) in enumerate(zip(group, powers, strict=True)):
                if type(exponent) is not int or (exponent < 0 and i != pivot):
                    raise ValueError("a Laurent pole escaped the explicitly inverted pivot")
                result = result * value**exponent
        return result


def local_cochain_coordinates(cochain, point, context):
    """Enclose actual local generator coefficients, not a rank-four fiber quotient.

    The normalized homogeneous pivots are one, so all declared line frames
    equal one. All extension coefficients remain separate symbolic blocks.
    """

    if not isinstance(point, BoundedCoverPoint):
        raise TypeError("local coefficient bounds require a certified bounded cover point")
    values = [point.x[0]._coerce(0) for o in context.left.objects if o.position == 0]
    for basis, coefficient in cochain.terms:
        component = basis.component
        key = component.left_index, component.right_index, component.koszul_summand
        if context.components.get(key) != component:
            raise ValueError("an incompatible actual cochain basis was supplied")
        if (basis.cell == point.cell and component.koszul_summand == "k0"
            and context.left.objects[component.left_index].position == 0):
            monomial = point.monomial(basis.x_monomial + basis.u_monomial + basis.p_monomial)
            values[component.left_index] = values[component.left_index] + monomial * coefficient
    return tuple(values)


def _fs_direction(s, z, derivative):
    # Gram determinant identity avoids cancellation of positive quantities:
    # (1+|s|^2+|z|^2)(1+|v|^2)-|conj(s)+conj(z)v|^2
    # = 1+|v|^2+|s*v-z|^2, with v=dz/ds.
    numerator = derivative.norm_interval() + 1 + (s * derivative - z).norm_interval()
    denominator = s.norm_interval() + z.norm_interval() + 1
    return numerator / denominator**2


@dataclass(frozen=True, slots=True)
class BoundedMeasure:
    """Positive density/weight intervals; pi cubed remains explicitly removed."""

    coordinates: tuple[Ball, ...]
    projection_jacobians: tuple[Ball, Ball]
    residue: Ball
    omega_density: Interval
    auxiliary_pi3_density: Interval
    cover_weight_pi3_removed: Interval
    quotient_weight_pi3_removed: Interval


def _chart_coordinates(point, chart, bits):
    """Normalize one certified point in its caller-declared projection chart."""

    _bits(bits)
    if not isinstance(point, (CoverPoint, BoundedCoverPoint)):
        raise TypeError("a certified exact or bounded actual cover point is required")
    if point.chart != chart.pivots:
        raise ValueError("point and projection must have identical explicit chart pivots")
    if isinstance(point, BoundedCoverPoint):
        if point.bits != bits:
            raise ValueError("incompatible declared bound precisions")
        xf, uf, pf = chart.free_indices
        coordinates = (point.x[xf], point.x[chart.x_solve], point.u[uf],
                       point.u[chart.u_solve], point.p[pf])
    else:
        coordinates = tuple(Ball(c, Rational(0), bits) for c in chart.coordinates(point))
    return coordinates


def bounded_local_measure(point, chart, *, volume_scale, covering_degree, bits):
    """Propagate root errors through the SAME actual residue and FS geometry."""

    coordinates = _chart_coordinates(point, chart, bits)
    scale = Eisenstein.coerce(volume_scale)
    if scale.is_zero():
        raise ValueError("an explicit nonzero volume-form scale is required")
    if type(covering_degree) is not int or covering_degree < 1:
        raise ValueError("an explicit positive integer covering degree is required")
    f, g = projection_polynomials(chart)
    fs, fz = (polynomial_value(f.derivative(i), coordinates) for i in (0, 1))
    gr, gw = (polynomial_value(g.derivative(i), coordinates) for i in (2, 3))
    # Inversion proves the complete enclosure avoids projection ramification.
    zs, wr = -fs / fz, -gr / gw
    s, z, r, w, t = coordinates
    auxiliary = _fs_direction(s, z, zs) * _fs_direction(r, w, wr)
    auxiliary = auxiliary / (t.norm_interval() + 1)**2
    residue = coordinates[0]._coerce(-chart.ambient_sign * scale) / (fz * gw)
    omega = residue.norm_interval()
    if omega.lower <= 0 or auxiliary.lower <= 0:
        raise ValueError("the declared bounds do not certify positive local densities")
    cover = omega * auxiliary_cover_mass() / auxiliary
    return BoundedMeasure(coordinates, (fz, gw), residue, omega, auxiliary,
                          cover, cover / covering_degree)


def _interval_record(interval):
    return [str(interval.lower), str(interval.upper)]


def _ball_record(ball):
    return {"center": [str(ball.center.a), str(ball.center.b)], "radius": str(ball.radius)}


def enclosure_artifact():
    """Record all nine bounded densities for both certified regression probes."""

    digest, parent = _verified_payload(roots.OUTPUT)
    if parent != {k: v for k, v in roots.root_artifact().items() if k != "artifact_digest"}:
        raise ValueError("the complete actual root certificates do not reproduce")
    from .alternate_metric_measure import ProjectionChart
    from .alternate_metric_outer_lifts import _compact, _inputs, first, second

    bits = 80
    policy = roots.RootPolicy(Rational(1, 2**30), 60, bits, 128)
    section_parents, streams, _extensions = _inputs()
    section_sources = tuple(
        (label, index, module._context()[0], module.expand_section(_compact(streams[block][index])))
        for block, module, label, indices in (
            (0, first, "V1 injection", (0, 1273)),
            (1, second, "V2 constituent, not its universal outer lift", (15, 1318)),
        ) for index in indices
    )
    configurations = []
    for raw in parent["actual_configurations"]:
        def scalar(pair):
            from fractions import Fraction

            return Eisenstein(Fraction(pair[0]), Fraction(pair[1]))

        lines = tuple(roots.ProjectiveLine(*(tuple(scalar(c) for c in v) for v in raw[key]))
                      for key in ("first_line", "second_line"))
        intersection = roots.intersection_roots(
            *lines, tuple(scalar(c) for c in raw["P1_point"]),
            parameter_pivots=(raw["first"]["parameter_pivot"], raw["second"]["parameter_pivot"]),
            policy=policy,
        )
        records = []
        for pair in intersection.root_pairs:
            # Declared charts for these probes only, not automatic chart fallback.
            x_pivot, x_solve = (1, 0) if pair[0] == "infinity" else (0, 2)
            p_pivot = 0 if raw["name"] == "finite_chart" else 1
            chart = ProjectionChart(x_pivot, x_solve, 0, 2, p_pivot)
            point = BoundedCoverPoint(intersection, pair, chart.pivots, bits)
            measure = bounded_local_measure(point, chart, volume_scale=Eisenstein(1),
                                            covering_degree=9, bits=bits)
            records.append({
                "root_pair": list(pair), "chart_pivots": list(chart.pivots),
                "eliminated_coordinates": [chart.x_solve, chart.u_solve],
                "coordinates_s_z_r_w_t": [_ball_record(c) for c in measure.coordinates],
                "projection_jacobians": [_ball_record(c) for c in measure.projection_jacobians],
                "residue": _ball_record(measure.residue),
                "omega_density": _interval_record(measure.omega_density),
                "auxiliary_density_times_pi_cubed": _interval_record(measure.auxiliary_pi3_density),
                "quotient_weight_without_pi_cubed": _interval_record(
                    measure.quotient_weight_pi3_removed,
                ),
            })
        probe_pair = ((0, 0) if raw["name"] == "finite_chart" else ("infinity", 0))
        probe_chart = (0, 0, 0) if raw["name"] == "finite_chart" else (1, 0, 1)
        probe_point = BoundedCoverPoint(intersection, probe_pair, probe_chart, bits)
        coefficient_probes = [{
            "block": label, "constituent_basis_index": index,
            "generator_coordinates": [_ball_record(c) for c in local_cochain_coordinates(
                cochain, probe_point, context,
            )],
        } for label, index, context, cochain in section_sources]
        configurations.append({
            "name": raw["name"], "all_nine_bounded_densities": records,
            "constituent_coefficient_probe": {
                "root_pair": list(probe_pair), "chart_pivots": list(probe_chart),
                "actual_constituent_coefficients": coefficient_probes,
                "scope": "ambient local generators, not the universal rank-four quotient",
            },
        })
    payload = {
        "schema": "alternate-metric-enclosures-v1", "root_artifact_digest": digest,
        "bound_bits": bits, "rounding": "outward dyadic errors; exact centers and singletons",
        "probe_volume_scale": "1 (declared form convention, not physical moduli)",
        "covering_degree": 9, "configuration_law": "regression probes, not SU-uniform samples",
        "actual_configurations": configurations,
        "section_prerequisite_artifact_digests": section_parents,
        "certified_chart_and_density_enclosures_available": True,
        "laurent_coefficient_enclosure_engine_available": True,
        "bounded_universal_fiber_frame_available": False,
        "centers_are_exact_cover_points": False,
        "bounded_section_and_density_evaluation_available": False,
        "controlled_numerical_sampling_available": False,
        "numerical_metrics_available": False, "physical_yukawas_available": False,
        "extension_point_selected": False, "vacuum_selected": False,
        "observational_inputs_used": False,
        "next_required_object": (
            "bound the actual universal quotient frames and complete section evaluator; "
            "control SU-uniform proposal precision and integration error, then metric convergence"
        ),
    }
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    return payload


def write_artifact():
    payload = enclosure_artifact()
    OUTPUT.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = write_artifact()
    print(f"artifact_digest: {result['artifact_digest']}")
