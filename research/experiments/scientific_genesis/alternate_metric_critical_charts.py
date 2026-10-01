"""Enclose the actual residue and positive density across critical fiber charts.

Owns:
    Certified point-line configurations, explicit base-eliminating coordinate
    frames, signed residues, and positive densities at actual axis-node fibers.

Depends on:
    Exact original pencils, complete partner-root certificates, existing
    point enclosures, and the unchanged positive FS-cube integration law.

Must not:
    Treat disk centers as cover points, hide coordinate or sign choices,
    extrapolate axis probes to all triangle-node input certificates, select
    physical moduli, or assert a sampler, global bound, or converged metric.

Phase 0:
    Research critical-coordinate engine; global numerical coverage remains open.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from onetheory.math.numbers import Eisenstein, Rational

from . import alternate_metric_positive_measure as positive

bounds, roots, measure = positive.bounds, positive.roots, positive.measure
OUTPUT = positive.OUTPUT.with_name("alternate_metric_critical_charts.json")
PROOF = "research/experiments/scientific_genesis/ALTERNATE_METRIC_CRITICAL_CHARTS_NOTE.md"


def configuration(plane_point, line, *, source_side, parameter_pivot, policy):
    """Construct the actual three-point component without introducing a sampler."""

    p, certified = positive.partner_roots(plane_point, line, side=source_side,
                                          parameter_pivot=parameter_pivot, policy=policy)
    return roots.PointLineRoots(source_side, tuple(plane_point), line, p, certified)


@dataclass(frozen=True, slots=True)
class CriticalMeasure:
    """Bounds in a named free-coordinate order, never the old frame by default."""

    source_side: int
    free_coordinate_indices: tuple[int, int, int]
    coordinates: tuple
    tangent: tuple
    wedge_jacobian: bounds.Ball
    residue: bounds.Ball
    omega_density: bounds.Interval
    positive_density_times_pi_cubed: bounds.Interval
    cover_weight_without_pi_cubed: bounds.Interval
    quotient_weight_without_pi_cubed: bounds.Interval


def local_measure(point, chart, *, source_side, volume_scale, covering_degree, bits):
    """Use free (s,z,r) or (r,w,s) in the SAME ambient order (s,z,r,w,t)."""

    if type(source_side) is not int or source_side not in (1, 2):
        raise ValueError("the base-eliminating source factor must be explicitly first or second")
    if type(covering_degree) is not int or covering_degree < 1:
        raise ValueError("an explicit positive integer covering degree is required")
    scale = Eisenstein.coerce(volume_scale)
    if scale.is_zero():
        raise ValueError("an explicit nonzero residue scale is required")
    coordinates = bounds._chart_coordinates(point, chart, bits)
    f, g = measure.projection_polynomials(chart)
    fs, fz, ft = (bounds.polynomial_value(f.derivative(i), coordinates) for i in (0, 1, 4))
    gr, gw, gt = (bounds.polynomial_value(g.derivative(i), coordinates) for i in (2, 3, 4))
    zero, one = coordinates[0]._coerce(0), coordinates[0]._coerce(1)
    if source_side == 1:
        ts, tz = -fs / ft, -fz / ft
        tangent = ((one, zero, zero), (zero, one, zero), (zero, zero, one),
                   (-gt * ts / gw, -gt * tz / gw, -gr / gw), (ts, tz, zero))
        free = (0, 1, 2)
        # df,dg,ds,dz,dr in ambient order: det = -f_t*g_w.
        jacobian = positive.matrices._determinant(((zero, ft), (gw, gt)))
    else:
        tr, tw = -gr / gt, -gw / gt
        tangent = ((zero, zero, one), (-ft * tr / fz, -ft * tw / fz, -fs / fz),
                   (one, zero, zero), (zero, one, zero), (tr, tw, zero))
        free = (2, 3, 0)
        # df,dg,dr,dw,ds in the same ambient order: det = f_z*g_t.
        jacobian = positive.matrices._determinant(((fz, ft), (zero, gt)))
    residue = one * (chart.ambient_sign * scale) / jacobian
    omega = residue.norm_interval()
    if omega.lower <= 0:
        raise ValueError("the declared bounds do not certify a nonzero residue")
    volume = positive._volume_from_tangent(coordinates, tangent, omega,
                                           covering_degree=covering_degree, bits=bits)
    return CriticalMeasure(source_side, free, coordinates, tangent, jacobian, residue,
                           omega, **volume)


def critical_artifact():
    """Check all six actual axis fibers, not a synthetic local normal form."""

    digest, parent = positive.matrices.fiber._verified_payload(positive.OUTPUT)
    if digest != "c95486f83301f30fe55906ae773981d3a18d5662b56587de769f9744638cd66e":
        raise ValueError("the actual positive-law prerequisite changed")
    policy = roots.RootPolicy(Rational(1, 2**30), 60, 80, 128)
    line = roots.ProjectiveLine((1, 0, 0), (0, 1, 1))
    probes = []
    for side in (1, 2):
        for axis in range(3):
            source = tuple(int(i == axis) for i in range(3))
            result = configuration(source, line, source_side=side, parameter_pivot=0, policy=policy)
            remaining = tuple(i for i in range(3) if i != axis)
            # Explicit ascending source-coordinate order; no physical basis selection.
            chart = (measure.ProjectionChart(axis, remaining[1], 0, 2, 0) if side == 1
                     else measure.ProjectionChart(0, 2, axis, remaining[1], 0))
            records = []
            for pair in result.root_pairs:
                point = bounds.BoundedCoverPoint(result, pair, chart.pivots, 80)
                local = local_measure(point, chart, source_side=side, volume_scale=Eisenstein(1),
                                       covering_degree=9, bits=80)
                records.append({
                    "root_pair": list(pair),
                    "free_coordinate_indices": list(local.free_coordinate_indices),
                    "wedge_jacobian": bounds._ball_record(local.wedge_jacobian),
                    "residue": bounds._ball_record(local.residue),
                    "omega_density": bounds._interval_record(local.omega_density),
                    "positive_density_times_pi_cubed": bounds._interval_record(
                        local.positive_density_times_pi_cubed,
                    ),
                    "quotient_weight_without_pi_cubed": bounds._interval_record(
                        local.quotient_weight_without_pi_cubed,
                    ),
                })
            probes.append({"source_side": side, "source_axis": axis,
                           "source_point": list(source), "chart_pivots": list(chart.pivots),
                           "source_coordinate_order": list(remaining),
                           "partner_solve_coordinate": 2,
                           "projective_base_mu_nu": [roots._scalar_record(c) for c in result.p],
                           "partner_root_certificate": roots._projective_record(result.partner),
                           "all_three_critical_chart_records": records})
    payload = {
        "schema": "alternate-metric-critical-charts-v1", "positive_measure_artifact_digest": digest,
        "moment_artifact_digest": parent["moment_artifact_digest"],
        "ambient_coordinate_order": ["s", "z", "r", "w", "t"],
        "free_coordinate_orders": {"1": ["s", "z", "r"], "2": ["r", "w", "s"]},
        "wedge_jacobian_rules": {"1": "-f_t*g_w", "2": "f_z*g_t"},
        "partner_line": [[1, 0, 0], [0, 1, 1]],
        "root_policy": {"requested_radius": str(policy.radius),
                        "coefficient_bits": policy.coefficient_bits,
                        "modulus_bound_bits": policy.modulus_bits,
                        "max_iterations": policy.max_iterations,
                        "parameter_pivot": 0},
        "actual_axis_fiber_probes": probes,
        "proof": PROOF,
        "proof_sha256": hashlib.sha256((measure.ROOT / PROOF).read_bytes()).hexdigest(),
        "bound_bits": 80, "covering_degree": 9,
        "point_line_cover_membership_certified": True,
        "declared_critical_fiber_chart_enclosures_available": True,
        "all_triangle_node_inputs_certified": False,
        "complete_global_atlas_coverage_certified": False,
        "quantitative_global_weight_bound_available": False,
        "controlled_numerical_sampling_available": False,
        "numerical_metrics_available": False, "physical_yukawas_available": False,
        "extension_point_selected": False, "physical_kahler_class_selected": False,
        "vacuum_selected": False, "observational_inputs_used": False,
        "next_required_object": (
            "global certified input/chart coverage, controlled uniform proposals, quantitative "
            "weights and integration errors, section throughput, and Ricci-flat/HYM convergence"
        ),
    }
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    return payload


def write_artifact():
    payload = critical_artifact()
    OUTPUT.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(write_artifact()["artifact_digest"])
