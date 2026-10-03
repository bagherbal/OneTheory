"""Certify actual projective intersections uniformly over admitted input cells.

Owns:
    Explicit bounded line bases, actual cubic coefficient enclosures, uniform
    one-root margins, reciprocal-chart completeness, and coupled cover bounds.

Depends on:
    Existing circular arithmetic, exact root proposals and Taylor witnesses,
    actual Schoen pencils, and controlled auxiliary projective input cells.

Must not:
    Discard input error or infinity roots, resample rejected cells, infer global
    sampling coverage, admit centers as exact cover points, or claim metrics.

Phase 0:
    Research-only admitted-cell root certificates; independent sampling is open.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from itertools import combinations, product
from pathlib import Path

from onetheory.math.numbers import Eisenstein, Rational
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry

from . import alternate_metric_projective_roots as roots
from .alternate_metric_enclosures import Ball, BoundedCoverPoint, polynomial_value

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/projective_uncertain_intersections.json"
PROOF = Path(__file__).with_name("PROJECTIVE_UNCERTAIN_INTERSECTIONS_NOTE.md")


def _balls(values, count):
    values = tuple(values)
    if len(values) != count or any(not isinstance(value, Ball) for value in values):
        raise ValueError("the declared number of circular input bounds is required")
    if any(value.bits != values[0].bits for value in values):
        raise ValueError("input bounds must have the same declared precision")
    return values


def _nonzero(values):
    return any(roots.modulus_bounds(value.center, value.bits)[0] > value.radius
               for value in values)


@dataclass(frozen=True, slots=True)
class BoundedLine:
    """A hyperplane with caller-declared pivot and ordered parameter coordinate axes."""

    covector: tuple[Ball, ...]
    pivot: int
    parameter_axes: tuple[int, int]

    def __post_init__(self):
        covector = _balls(self.covector, 3)
        axes = tuple(self.parameter_axes)
        if (type(self.pivot) is not int or self.pivot not in (0, 1, 2)
            or len(axes) != 2 or any(type(i) is not int for i in axes)
            or set(axes) != set(range(3)) - {self.pivot}):
            raise ValueError("an explicit pivot and ordered complementary axes are required")
        covector[self.pivot].inverse()  # Failure cannot silently select another pivot.
        object.__setattr__(self, "covector", covector)
        object.__setattr__(self, "parameter_axes", axes)

    @property
    def basis(self):
        zero = self.covector[0]._coerce(0)
        one = zero._coerce(1)
        rows = []
        for free in self.parameter_axes:
            column = [zero, zero, zero]
            column[free] = one
            column[self.pivot] = -self.covector[free] / self.covector[self.pivot]
            rows.append(tuple(column))
        return tuple(rows)

    def point_bounds(self, parameter):
        """Propagate line coefficients and root uncertainty in one declared frame."""

        parameter = _balls(parameter, 2)
        if parameter[0].bits != self.covector[0].bits:
            raise ValueError("line and parameter bounds use incompatible precision")
        first, second = self.basis
        return tuple(a * parameter[0] + b * parameter[1]
                     for a, b in zip(first, second, strict=True))


def _multiply_coefficients(left, right):
    zero = left[0]._coerce(0)
    result = [zero for _ in range(len(left) + len(right) - 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] = result[i + j] + a * b
    return tuple(result)


def _restrict_cubic(polynomial, basis):
    """Finite binary coefficient convolution of the original exact monomials."""

    zero = basis[0][0]._coerce(0)
    result = [zero for _ in range(4)]
    for exponents, coefficient in polynomial.terms:
        term = (zero._coerce(coefficient),)
        for axis, exponent in enumerate(exponents):
            for _ in range(exponent):
                term = _multiply_coefficients(term, (basis[0][axis], basis[1][axis]))
        for power, value in enumerate(term):
            result[power] = result[power] + value
    return tuple(result)


@dataclass(frozen=True, slots=True)
class UncertainCubic:
    """All binary cubics in four coefficient disks, ordered by increasing t power."""

    coefficients: tuple[Ball, ...]

    def __post_init__(self):
        coefficients = _balls(self.coefficients, 4)
        if not _nonzero(coefficients):
            raise ValueError("the homogeneous coefficient cell may contain the zero polynomial")
        object.__setattr__(self, "coefficients", coefficients)

    @property
    def center_polynomial(self):
        return Polynomial((((3 - j, j), value.center)
                           for j, value in enumerate(self.coefficients)),
                          variable_count=2, scalar_type=Eisenstein)

    def chart_coefficients(self, pivot):
        if type(pivot) is not int or pivot not in (0, 1):
            raise ValueError("an explicit binary parameter chart is required")
        return self.coefficients if pivot == 0 else tuple(reversed(self.coefficients))


def actual_restriction(line, base, *, side):
    """Enclose the unchanged actual pencil, not a center-only replacement."""

    if not isinstance(line, BoundedLine):
        raise TypeError("an explicitly based bounded projective line is required")
    base = _balls(base, 2)
    if type(side) is not int or side not in (1, 2):
        raise ValueError("the actual first or second pencil must be declared")
    if base[0].bits != line.covector[0].bits or not _nonzero(base):
        raise ValueError("the shared base requires compatible nonzero homogeneous bounds")
    cox = schoen_geometry().cover.cox
    f, g = (_restrict_cubic(polynomial, line.basis)
            for polynomial in (cox.cubic_f, cox.cubic_g))
    return UncertainCubic(tuple(a * base[0] + b * base[1] if side == 1 else
                                a * (base[1] * 2) + b * base[0]
                                for a, b in zip(f, g, strict=True)))


@dataclass(frozen=True, slots=True)
class UniformRootDisk:
    """One simple projective root for every cubic in the same coefficient cell."""

    cubic: UncertainCubic
    parameter_pivot: int
    witness: roots.RootDisk

    def __post_init__(self):
        coefficients = self.cubic.chart_coefficients(self.parameter_pivot)
        center = Polynomial.from_coefficients(tuple(value.center for value in coefficients),
                                               scalar_type=Eisenstein)
        if (not isinstance(self.witness, roots.RootDisk)
            or self.witness.polynomial != center or self.witness.radius <= 0):
            raise ValueError("a positive-radius witness for the actual center cubic is required")
        if self.uniform_margin <= 0:
            raise ValueError("coefficient uncertainty exceeds the strict uniform one-root margin")

    @property
    def coefficient_error_bound(self):
        coefficients = self.cubic.chart_coefficients(self.parameter_pivot)
        maximum = (roots.modulus_bounds(self.witness.center, coefficients[0].bits)[1]
                   + self.witness.radius)
        return sum((value.radius * maximum**j for j, value in enumerate(coefficients)), Rational(0))

    @property
    def uniform_margin(self):
        witness = self.witness
        remainder = witness.modulus_upper[0] + sum((
            witness.modulus_upper[k] * witness.radius**k
            for k in range(2, len(witness.taylor))
        ), Rational(0))
        return witness.modulus_lower[1] * witness.radius - remainder - self.coefficient_error_bound

    @property
    def parameter_bounds(self):
        bits = self.cubic.coefficients[0].bits
        one = Ball(Eisenstein(1), Rational(0), bits)
        variable = Ball(self.witness.center, self.witness.radius, bits)
        return (one, variable) if self.parameter_pivot == 0 else (variable, one)


def _projectively_disjoint(left, right):
    a, b = left.witness, right.witness
    if left.parameter_pivot == right.parameter_pivot:
        return (a.center - b.center).norm() > (a.radius + b.radius)**2
    bits = left.cubic.coefficients[0].bits
    radius = (roots.modulus_bounds(a.center, bits)[1] * b.radius
              + roots.modulus_bounds(b.center, bits)[1] * a.radius + a.radius * b.radius)
    return (a.center * b.center - 1).norm() > radius**2


@dataclass(frozen=True, slots=True)
class CompleteUncertainRoots:
    """Exactly three disjoint root disks uniformly over one nonzero binary cubic cell."""

    cubic: UncertainCubic
    disks: tuple[UniformRootDisk, ...]

    def __post_init__(self):
        disks = tuple(self.disks)
        if len(disks) != 3 or any(disk.cubic != self.cubic for disk in disks):
            raise ValueError("three same-family projective root witnesses are required")
        if any(not _projectively_disjoint(a, b) for a, b in combinations(disks, 2)):
            raise ValueError("uniform root disks overlap on the projective parameter line")
        object.__setattr__(self, "disks", disks)


def _positive_witness(polynomial, center, policy):
    # Exact-center roots must not remain radius zero when coefficients can move.
    taylor = roots._taylor_coefficients(polynomial, center)
    moduli = tuple(roots.modulus_bounds(value, policy.modulus_bits) for value in taylor)
    return roots.RootDisk(polynomial, center, policy.radius, taylor,
                          tuple(v[0] for v in moduli), tuple(v[1] for v in moduli))


def complete_uncertain_roots(cubic, *, parameter_pivot, policy):
    """Reuse exact proposals, then certify the entire input cell without fallback."""

    center = roots.projective_roots(cubic.center_polynomial,
                                    parameter_pivot=parameter_pivot, policy=policy)
    disks = [UniformRootDisk(cubic, parameter_pivot,
                            _positive_witness(center.finite.polynomial, disk.center, policy))
             for disk in center.finite.disks]
    if center.infinity_multiplicity:
        reciprocal = Polynomial.from_coefficients(tuple(value.center for value in
            cubic.chart_coefficients(1 - parameter_pivot)), scalar_type=Eisenstein)
        disks.append(UniformRootDisk(cubic, 1 - parameter_pivot,
                                    _positive_witness(reciprocal, Eisenstein(0), policy)))
    return CompleteUncertainRoots(cubic, tuple(disks))


@dataclass(frozen=True, slots=True)
class LineBaseLineConfiguration:
    """A coupled cover family whose two root sets use the same actual bounded base."""

    first_line: BoundedLine
    second_line: BoundedLine
    base: tuple[Ball, ...]
    first: CompleteUncertainRoots
    second: CompleteUncertainRoots

    def __post_init__(self):
        base = _balls(self.base, 2)
        for side, line, root_set in ((1, self.first_line, self.first),
                                     (2, self.second_line, self.second)):
            if (not isinstance(root_set, CompleteUncertainRoots)
                or root_set.cubic != actual_restriction(line, base, side=side)):
                raise ValueError("the root family is not the actual same-base line restriction")
        object.__setattr__(self, "base", base)

    @property
    def root_pairs(self):
        return tuple(product(range(3), repeat=2))

    @property
    def points(self):
        return tuple((self.first_line.point_bounds(a.parameter_bounds),
                      self.second_line.point_bounds(b.parameter_bounds), self.base)
                     for a, b in product(self.first.disks, self.second.disks))


@dataclass(frozen=True, slots=True)
class PointLineConfiguration:
    """A coupled source-point/partner-root family with its actual derived base."""

    source_point: tuple[Ball, ...]
    source_side: int
    partner_line: BoundedLine
    partner: CompleteUncertainRoots

    def __post_init__(self):
        source = _balls(self.source_point, 3)
        if type(self.source_side) is not int or self.source_side not in (1, 2):
            raise ValueError("the source plane must be explicitly first or second")
        object.__setattr__(self, "source_point", source)
        if (not isinstance(self.partner, CompleteUncertainRoots)
            or self.partner.cubic != actual_restriction(self.partner_line, self.base,
                                                        side=3-self.source_side)):
            raise ValueError("the partner roots are not the actual source-derived base restriction")

    @property
    def base(self):
        cox = schoen_geometry().cover.cox
        f, g = (polynomial_value(polynomial, self.source_point)
                for polynomial in (cox.cubic_f, cox.cubic_g))
        base = (-g, f) if self.source_side == 1 else (-f * 2, g)
        if not _nonzero(base):
            raise ValueError("the source input cell may meet a pencil base point")
        return base

    @property
    def root_pairs(self):
        return tuple(("fixed", i) if self.source_side == 1 else (i, "fixed") for i in range(3))

    @property
    def points(self):
        base = self.base
        return tuple((self.source_point, self.partner_line.point_bounds(d.parameter_bounds), base)
                     if self.source_side == 1 else
                     (self.partner_line.point_bounds(d.parameter_bounds), self.source_point, base)
                     for d in self.partner.disks)


@dataclass(frozen=True, slots=True)
class UncertainCoverPoint(BoundedCoverPoint):
    """One actual coupled cover branch, normalized in caller-declared chart pivots.

    This is the existing bounded cover representation with a uniform native
    family membership certificate. Coordinate centers are never exact points.
    The same monomial, local-cochain and quotient engines consume this subtype.
    """

    intersection: LineBaseLineConfiguration | PointLineConfiguration
    center_bits: int | None = None

    def __post_init__(self):
        configuration = self.intersection
        if not isinstance(configuration, (LineBaseLineConfiguration, PointLineConfiguration)):
            raise TypeError("an actual coupled uncertain cover configuration is required")
        if (not isinstance(self.root_pair, tuple) or len(self.root_pair) != 2
            or any(type(i) is not int and i != "fixed" for i in self.root_pair)
            or self.root_pair not in configuration.root_pairs):
            raise ValueError("an explicit complete-family root pair is required")
        if (not isinstance(self.chart, tuple) or len(self.chart) != 3
            or any(type(i) is not int or not 0 <= i < size
                   for i, size in zip(self.chart, (3, 3, 2), strict=True))):
            raise ValueError("three explicit homogeneous chart pivots are required")
        groups = configuration.points[configuration.root_pairs.index(self.root_pair)]
        if type(self.bits) is not int or self.bits != groups[0][0].bits:
            raise ValueError("point precision must equal the original input/root bound precision")
        if self.center_bits is not None:
            groups = tuple(tuple(Ball(c.center, c.radius, self.bits, self.center_bits)
                                 for c in group) for group in groups)
        self._normalize_groups(groups)


def line_base_line(first_line, second_line, base, *, parameter_pivots, policy):
    """Keep all nine coupled uncertain intersections in explicitly declared charts."""

    base = _balls(base, 2)
    if not isinstance(parameter_pivots, tuple) or len(parameter_pivots) != 2:
        raise ValueError("two explicit ordered parameter pivots are required")
    first, second = (complete_uncertain_roots(actual_restriction(line, base, side=side),
        parameter_pivot=pivot, policy=policy) for side, line, pivot in
        zip((1, 2), (first_line, second_line), parameter_pivots, strict=True))
    configuration = LineBaseLineConfiguration(first_line, second_line, base, first, second)
    return configuration.points, (first, second)


def point_line(source_point, partner_line, *, source_side, parameter_pivot, policy):
    """Retain the actual point/base correlation and all three partner branches."""

    source = _balls(source_point, 3)
    if type(source_side) is not int or source_side not in (1, 2):
        raise ValueError("the source factor must be explicitly first or second")
    cox = schoen_geometry().cover.cox
    f, g = (polynomial_value(polynomial, source) for polynomial in (cox.cubic_f, cox.cubic_g))
    base = (-g, f) if source_side == 1 else (-f * 2, g)
    if not _nonzero(base):
        raise ValueError("the source input cell may meet a pencil base point")
    partner = complete_uncertain_roots(actual_restriction(partner_line, base, side=3-source_side),
                                      parameter_pivot=parameter_pivot, policy=policy)
    configuration = PointLineConfiguration(source, source_side, partner_line, partner)
    return configuration.points, partner


def declared_probes():
    """Execute all mixture components on predeclared nonphysical regression cells."""

    from .projective_uniform_input_cells import InputPolicy, projective_input_cell

    policy = InputPolicy(40, 100, 40, 56)
    x = projective_input_cell((2**38, 3 * 2**38), (2**36, 11 * 2**36), policy=policy)
    u = projective_input_cell((5 * 2**37, 7 * 2**37), (5 * 2**36, 13 * 2**36), policy=policy)
    p = projective_input_cell((3 * 2**38,), (7 * 2**36,), policy=policy)
    hx, hu = (BoundedLine(cell.coordinates, 0, (1, 2)) for cell in (x, u))
    root_policy = roots.RootPolicy(Rational(1, 2**12), 64, 100, 128)
    a = line_base_line(hx, hu, p.coordinates, parameter_pivots=(0, 0), policy=root_policy)
    bx = point_line(x.coordinates, hu, source_side=1, parameter_pivot=0, policy=root_policy)
    bu = point_line(u.coordinates, hx, source_side=2, parameter_pivot=0, policy=root_policy)
    # Original actual leading-zero restriction, now with positive coefficient error.
    def ball(coefficient):
        return Ball(Eisenstein(coefficient), Rational(1, 2**30), 100)
    infinity = complete_uncertain_roots(actual_restriction(
        BoundedLine(tuple(ball(c) for c in (0, 1, 1)), 2, (0, 1)),
        tuple(ball(c) for c in (0, 1)), side=1,
    ), parameter_pivot=0, policy=root_policy)
    return (x, u, p), (a, bx, bu), infinity


def _ball_record(value):
    return {"center": [str(value.center.a), str(value.center.b)], "radius": str(value.radius)}


def _roots_record(root_set):
    return {
        "binary_coefficients": [_ball_record(value) for value in root_set.cubic.coefficients],
        "root_disks": [{
            "parameter_pivot": disk.parameter_pivot,
            "center": [str(disk.witness.center.a), str(disk.witness.center.b)],
            "radius": str(disk.witness.radius),
            "coefficient_error_bound": str(disk.coefficient_error_bound),
            "uniform_margin": str(disk.uniform_margin),
        } for disk in root_set.disks],
    }


def uncertain_intersection_record():
    """Reproduce every admitted-cell witness; preserve all missing physical gates."""

    from .projective_uniform_input_cells import read_input_cells

    parent = read_input_cells()
    parent_digest = _digest(parent)
    if parent_digest != "b8db32fa76846ebbc8fba44ff5fcb67b1a92f9961d05f8b61355141d8fd7cade":
        raise ValueError("the controlled projective input law changed its trusted digest")
    manifest_sha = hashlib.sha256((ROOT / (
        "data/published/visible_carrier/source_manifest.json"
    )).read_bytes()).hexdigest()
    if manifest_sha != "dc7b51776d7b362ae748f2bfde8ff4a90d54c82becb6a55e2a6eafb31bc0c99d":
        raise ValueError("the actual published carrier input provenance changed")
    inputs, components, infinity = declared_probes()
    records = []
    for name, (points, results) in zip(("A", "Bx", "Bu"), components, strict=True):
        root_sets = results if name == "A" else (results,)
        records.append({
            "component": name,
            "complete_root_count": len(points),
            "root_families": [_roots_record(root_set) for root_set in root_sets],
            "coupled_cover_bounds": [[[_ball_record(value) for value in factor] for factor in point]
                                      for point in points],
        })
    return {
        "schema": "projective-uncertain-intersections-v1",
        "input_cell_parent_digest": parent_digest,
        "published_carrier_manifest_sha256": manifest_sha,
        "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
        "actual_equations": ["mu*F(x)+nu*G(x)", "2*nu*F(u)+mu*G(u)"],
        "input_policy": {"cell_bits": 40, "bound_bits": 100,
                         "atan_terms": 40, "taylor_terms": 56},
        "root_policy": {"radius": "1/4096", "coefficient_bits": 64,
                        "modulus_bits": 100, "max_iterations": 128},
        "input_cells": [{"spacing_indices": list(cell.spacing_indices),
                         "phase_indices": list(cell.phase_indices)} for cell in inputs],
        "line_parameter_frames": {"pivot": 0, "ordered_free_axes": [1, 2]},
        "initial_parameter_pivots": [0, 0],
        "all_mixture_component_probes": records,
        "moving_infinity_probe": _roots_record(infinity),
        "admitted_input_cell_root_completeness_available": True,
        "coupled_actual_cover_coordinate_bounds_available": True,
        "centers_are_exact_cover_points": False,
        "independent_cover_sampling_cloud_available": False,
        "global_numeric_input_coverage_certified": False,
        "input_cell_rejection_used_as_resampling": False,
        "new_domain_density_and_section_bounds_available": False,
        "integration_error_control_available": False,
        "numerical_metrics_available": False, "physical_yukawas_available": False,
        "extension_point_selected": False, "vacuum_selected": False,
        "observational_inputs_used": False,
    }


def _digest(record):
    serialized = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(serialized).hexdigest()


def write_uncertain_intersections(path=OUTPUT):
    """Save the actual executed family certificates, never an independent cloud."""

    record = uncertain_intersection_record()
    record["artifact_digest"] = _digest(record)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return record


def read_uncertain_intersections(path=OUTPUT):
    """Recompute actual restrictions, root margins, disjointness, and scope."""

    record = json.loads(path.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest", None)
    if digest != _digest(record) or record != uncertain_intersection_record():
        raise ValueError("the uncertain intersections changed their roots, inputs, proof, or scope")
    return record


if __name__ == "__main__":
    print(write_uncertain_intersections()["artifact_digest"])
