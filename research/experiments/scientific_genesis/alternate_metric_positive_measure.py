"""Derive a positive auxiliary integration law on the unchanged actual cover.

Owns:
    Exact ambient FS-cube mass, normalized projective mixture components,
    actual base projections and cubic restrictions, and local density bounds.

Depends on:
    The original actual residue and FS conventions, the nodal smoothness proof,
    certified projective roots, and existing circular-bound matrix arithmetic.

Must not:
    Choose physical Kahler moduli, replace the target volume, use rounded
    rational inputs as uniform draws, claim a quantitative global bound, or
    infer numerical metrics, physical Yukawas, or a common vacuum.

Phase 0:
    Research positive-law prerequisites only; the controlled sampler is open.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction

from onetheory.math.numbers import Eisenstein, Rational

from . import alternate_metric_bounded_fibers as matrices
from . import alternate_metric_measure as measure
from . import alternate_metric_weight_moments as moments

bounds, roots = matrices.bounds, matrices.bounds.roots
OUTPUT = measure.OUTPUT.with_name("alternate_metric_positive_measure.json")
PROOF = "research/experiments/scientific_genesis/ALTERNATE_METRIC_POSITIVE_MEASURE_NOTE.md"


def masses():
    """Integrate the actual complete-intersection class, not guessed probabilities."""

    x, u, p = measure._variables(3)
    class_ = (3 * x + p) * (3 * u + p)
    forms = (x * u * p, x**2 * u, x * u**2, (x + u + p)**3)
    values = tuple(Eisenstein.coerce((form * class_).coefficient((2, 2, 1))) for form in forms)
    if any(not value.b.is_zero() or value.a <= 0 for value in values):
        raise ValueError("the declared auxiliary masses must be positive exact rationals")
    a, b, c, total = tuple(value.a for value in values)
    if total != 6 * a + 3 * b + 3 * c:
        raise ValueError("the positive FS cube has incompatible mixed intersection masses")
    return (a, b, c), total, (6 * a / total, 3 * b / total, 3 * c / total)


def projected_base(plane_point, side):
    """Return homogeneous (mu,nu) from one exact plane input; do not sample it."""

    if type(side) is not int or side not in (1, 2):
        raise ValueError("choose the first or second actual plane explicitly")
    point = tuple(Eisenstein.coerce(c) for c in plane_point)
    if len(point) != 3 or all(c.is_zero() for c in point):
        raise ValueError("a nonzero exact projective plane point is required")
    cox = measure.schoen_geometry().cover.cox
    f, g = (measure._value(cubic, point) for cubic in (cox.cubic_f, cox.cubic_g))
    if f.is_zero() and g.is_zero():
        raise ValueError("a base point does not determine the shared projective parameter")
    return (-g, f) if side == 1 else (-2 * f, g)


def partner_roots(plane_point, line, *, side, parameter_pivot, policy):
    """Reuse complete cubic certificates for the partner plane, never root centers."""

    p = projected_base(plane_point, side)
    restriction = roots.restrict_pencil(line, p, 3 - side)
    return p, roots.projective_roots(restriction, parameter_pivot=parameter_pivot, policy=policy)


def _fs_pullback(coordinates, tangent):
    """Enclose the same normalized FS Hermitian form; pi is factored out."""

    zero = coordinates[0]._coerce(0)
    potential = matrices._sum((q * q.conjugate() for q in coordinates), zero) + 1
    inverse_squared = potential**-2
    metric = tuple(tuple((potential * int(i == j) - q * r.conjugate()) * inverse_squared
                         for j, r in enumerate(coordinates)) for i, q in enumerate(coordinates))
    adjoint = tuple(tuple(c.conjugate() for c in column) for column in zip(*tangent, strict=True))
    return matrices._multiply(matrices._multiply(adjoint, metric), tangent)


def _volume_from_tangent(coordinates, tangent, omega_density, *, covering_degree, bits):
    """Reuse the declared positive FS-cube law in any explicitly named free frame."""

    s, z, r, w, t = coordinates
    forms = (_fs_pullback((s, z), tangent[:2]), _fs_pullback((r, w), tangent[2:4]),
             _fs_pullback((t,), tangent[4:]))
    beta = matrices._add(matrices._add(forms[0], forms[1]), forms[2])
    density = matrices._determinant(beta) * 6
    if not density.center.b.is_zero():
        raise ValueError("the Hermitian density center must be an exact real rational")
    interval = bounds.Interval(density.center.a - density.radius,
                               density.center.a + density.radius, bits)
    if interval.lower <= 0:
        raise ValueError("the declared bounds do not certify the positive FS-cube density")
    _components, mass, _probabilities = masses()
    cover = omega_density * mass / interval
    return {"positive_density_times_pi_cubed": interval,
            "cover_weight_without_pi_cubed": cover,
            "quotient_weight_without_pi_cubed": cover / covering_degree}


def bounded_positive_measure(point, chart, *, volume_scale, covering_degree, bits):
    """Bound beta^3 and its weights on an explicitly regular projection chart.

    beta is FS_x+FS_u+FS_p, an auxiliary ambient form, NOT a Ricci-flat
    physical metric. Critical fibers require different projection charts;
    the positivity theorem does not make their enclosures implemented here.
    """

    original = bounds.bounded_local_measure(point, chart, volume_scale=volume_scale,
                                           covering_degree=covering_degree, bits=bits)
    coordinates = original.coordinates
    f, g = measure.projection_polynomials(chart)
    fs, ft = (bounds.polynomial_value(f.derivative(i), coordinates) for i in (0, 4))
    gr, gt = (bounds.polynomial_value(g.derivative(i), coordinates) for i in (2, 4))
    fz, gw = original.projection_jacobians
    zero, one = coordinates[0]._coerce(0), coordinates[0]._coerce(1)
    tangent = ((one, zero, zero), (-fs / fz, zero, -ft / fz),
               (zero, one, zero), (zero, -gr / gw, -gt / gw), (zero, zero, one))
    return _volume_from_tangent(coordinates, tangent, original.omega_density,
                                covering_degree=covering_degree, bits=bits)


def positive_artifact():
    """Certify algebra, bounded regression densities, and the explicitly scoped law."""

    moment_digest, moment = matrices.fiber._verified_payload(moments.OUTPUT)
    root_digest, parent = matrices.fiber._verified_payload(roots.OUTPUT)
    if (moment_digest != "bae6172a3208f92f6bd954c8a4124bfce84da09cf08a2d66dc44e7305165ee41"
        or moment.get("two_critical_supports_gcd_degree") != 0
        or moment.get("critical_infinity_fibers") is not False
        or root_digest != "cc160262ba3ca6d389c28b1ea2b42c49372d5e47ce90af93ab00ab60cab6ebdf"):
        raise ValueError("the actual smooth-cover prerequisite is incompatible")
    component_masses, mass, probabilities = masses()
    policy = roots.RootPolicy(Rational(1, 2**30), 60, 80, 128)
    branches = []
    line = roots.ProjectiveLine((1, 0, 0), (0, 1, 1))
    for side, point in ((1, (1, -1, 0)), (2, (1, 1, 1))):
        base, certified = partner_roots(point, line, side=side, parameter_pivot=0, policy=policy)
        branches.append({"side": side, "exact_plane_point": list(point),
                         "projective_base_mu_nu": [roots._scalar_record(c) for c in base],
                         "partner_line": [list(v) for v in ((1, 0, 0), (0, 1, 1))],
                         "partner_root_certificate": roots._projective_record(certified)})
    configurations = []
    for raw in parent["actual_configurations"]:
        def scalar(pair):
            return Eisenstein(Fraction(pair[0]), Fraction(pair[1]))

        lines = tuple(roots.ProjectiveLine(*(tuple(scalar(c) for c in v) for v in raw[key]))
                      for key in ("first_line", "second_line"))
        intersection = roots.intersection_roots(*lines, tuple(scalar(c) for c in raw["P1_point"]),
            parameter_pivots=(raw["first"]["parameter_pivot"], raw["second"]["parameter_pivot"]),
            policy=policy)
        records = []
        for pair in intersection.root_pairs:
            xp, xs = (1, 0) if pair[0] == "infinity" else (0, 2)
            pp = 0 if raw["name"] == "finite_chart" else 1
            chart = measure.ProjectionChart(xp, xs, 0, 2, pp)
            point = bounds.BoundedCoverPoint(intersection, pair, chart.pivots, 80)
            local = bounded_positive_measure(point, chart, volume_scale=Eisenstein(1),
                                             covering_degree=9, bits=80)
            records.append({"root_pair": list(pair), "chart_pivots": list(chart.pivots),
                            "eliminated_coordinates": [xs, 2],
                            **{key: bounds._interval_record(value)
                               for key, value in local.items()}})
        configurations.append({"name": raw["name"], "all_nine_positive_densities": records})
    payload = {
        "schema": "alternate-metric-positive-measure-v1",
        "moment_artifact_digest": moment_digest, "root_artifact_digest": root_digest,
        "measure_artifact_digest": moment["measure_artifact_digest"],
        "auxiliary_form": "beta = FS_x + FS_u + FS_p; integration only, not physical moduli",
        "normalized_probability_law": "beta^3 / integral_cover beta^3",
        "positive_cover_mass": str(mass),
        "component_forms": ["A=FS_x FS_u FS_p", "Bx=FS_x^2 FS_u", "Bu=FS_x FS_u^2"],
        "component_masses": [str(m) for m in component_masses],
        "component_probabilities": [str(p) for p in probabilities],
        "component_root_counts": [9, 3, 3],
        "component_generation_laws": [
            "independent SU-uniform plane line, P1 point, partner plane line; one of nine roots",
            "SU-uniform first-plane point and independent second-plane line; one of three roots",
            "SU-uniform second-plane point and independent first-plane line; one of three roots",
        ],
        "proof": PROOF,
        "proof_sha256": hashlib.sha256((measure.ROOT / PROOF).read_bytes()).hexdigest(),
        "projective_zero_law_reference": "https://arxiv.org/abs/0712.3563v2",
        "bound_bits": 80, "covering_degree": 9,
        "actual_three_root_branch_probes": branches, "actual_configurations": configurations,
        "positive_auxiliary_law_derived": True,
        "ideal_weight_globally_bounded": True,
        "all_nonnegative_weight_moments_finite": True,
        "regular_chart_positive_density_enclosures_available": True,
        "quantitative_global_weight_bound_available": False,
        "critical_fiber_chart_enclosures_available": False,
        "controlled_numerical_sampling_available": False,
        "numerical_metrics_available": False, "physical_yukawas_available": False,
        "extension_point_selected": False, "vacuum_selected": False,
        "physical_kahler_class_selected": False, "observational_inputs_used": False,
        "next_required_object": (
            "controlled uniform projective proposals, global quantitative bounds "
            "and chart coverage, "
            "complete section throughput, integration error, and Ricci-flat/HYM convergence"
        ),
    }
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    return payload


def write_artifact():
    payload = positive_artifact()
    OUTPUT.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(write_artifact()["artifact_digest"])
