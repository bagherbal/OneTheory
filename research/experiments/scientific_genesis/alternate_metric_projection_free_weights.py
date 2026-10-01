"""Enclose positive-law weights using the full ambient conormal Gram.

Owns:
    Projection-free residue-to-FS-cube ratios, positive sparse conormal sums,
    declared exact normalization, and actual regular/critical regression domains.

Depends on:
    Original equations and chart coordinates, certified root membership,
    existing outward interval arithmetic, and the unchanged auxiliary FS law.

Must not:
    Invert individual projection gradients, fabricate input certificates,
    interpret centers as cover points, claim a global numerical bound or sampler,
    choose physical moduli, or infer Ricci-flat/HYM metrics or observables.

Phase 0:
    Research structural weight identity; quantitative integration remains open.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction

from onetheory.math.numbers import Eisenstein, Rational

from . import alternate_metric_critical_charts as critical

positive, bounds, roots, measure = (
    critical.positive, critical.bounds, critical.roots, critical.measure,
)
OUTPUT = positive.OUTPUT.with_name("alternate_metric_projection_free_weights.json")
PROOF = "research/experiments/scientific_genesis/ALTERNATE_METRIC_PROJECTION_FREE_WEIGHTS_NOTE.md"


@dataclass(frozen=True, slots=True)
class Weight:
    """Certified intrinsic ratio with declared coordinates and no free tangent frame."""

    coordinates: tuple
    conormal_terms: tuple[bounds.Interval, ...]
    ambient_determinant: bounds.Interval
    conormal_determinant: bounds.Interval
    denominator: bounds.Interval
    cover_weight_without_pi_cubed: bounds.Interval
    quotient_weight_without_pi_cubed: bounds.Interval


def local_weight(point, chart, *, volume_scale, covering_degree, bits):
    """Use the original equations; require a positive full Gram interval, not f_z/g_w."""

    if not isinstance(chart, measure.ProjectionChart):
        raise TypeError("an explicitly ordered original projective chart is required")
    if type(covering_degree) is not int or covering_degree < 1:
        raise ValueError("an explicit positive integer covering degree is required")
    scale = Eisenstein.coerce(volume_scale)
    if scale.is_zero():
        raise ValueError("an explicit nonzero residue scale is required")
    coordinates = bounds._chart_coordinates(point, chart, bits)
    s, z, r, w, t = coordinates
    f, g = measure.projection_polynomials(chart)
    fs, fz, ft = (bounds.polynomial_value(f.derivative(i), coordinates) for i in (0, 1, 4))
    gr, gw, gt = (bounds.polynomial_value(g.derivative(i), coordinates) for i in (2, 3, 4))
    sx = s.norm_interval() + z.norm_interval() + 1
    su = r.norm_interval() + w.norm_interval() + 1
    sp = t.norm_interval() + 1
    ax = sx * (fs.norm_interval() + fz.norm_interval() + (fs * s + fz * z).norm_interval())
    au = su * (gr.norm_interval() + gw.norm_interval() + (gr * r + gw * w).norm_interval())
    ap, bp = sp**2 * ft.norm_interval(), sp**2 * gt.norm_interval()
    conormal = ax * au + ax * bp + au * ap
    ambient = bounds.Interval(Rational(1), Rational(1), bits) / (sx**3 * su**3 * sp**2)
    denominator = ambient * conormal
    if denominator.lower <= 0:
        raise ValueError(
            "the declared bounds do not certify the positive full conormal determinant"
        )
    _, mass, _ = positive.masses()
    cover = denominator._coerce(scale.norm() * mass) / (denominator * 6)
    return Weight(coordinates, (ax, au, ap, bp), ambient, conormal, denominator,
                  cover, cover / covering_degree)


def regular_configuration(name, policy):
    """Reconstruct named actual root inputs without introducing a sampling law."""

    _, parent = positive.matrices.fiber._verified_payload(roots.OUTPUT)
    matches = tuple(p for p in parent["actual_configurations"] if p["name"] == name)
    if name not in ("finite_chart", "infinity_branch") or len(matches) != 1:
        raise ValueError("an explicit original regression configuration is required")
    raw = matches[0]

    def scalar(pair):
        return Eisenstein(Fraction(pair[0]), Fraction(pair[1]))

    lines = tuple(roots.ProjectiveLine(*(tuple(scalar(c) for c in v) for v in raw[key]))
                  for key in ("first_line", "second_line"))
    return roots.intersection_roots(*lines, tuple(scalar(c) for c in raw["P1_point"]),
        parameter_pivots=(raw["first"]["parameter_pivot"], raw["second"]["parameter_pivot"]),
        policy=policy)


def weight_artifact():
    """Certify the unchanged 36 declared domains, not global input coverage."""

    positive_digest, parent = positive.matrices.fiber._verified_payload(positive.OUTPUT)
    critical_digest, critical_parent = positive.matrices.fiber._verified_payload(critical.OUTPUT)
    if (positive_digest != "c95486f83301f30fe55906ae773981d3a18d5662b56587de769f9744638cd66e"
        or critical_digest != "b40ff532135437c7e0ff1bb041a1cd26696303ea721e3ed108c6a04c029a7504"):
        raise ValueError("the actual positive-law and critical-domain prerequisites changed")
    policy = roots.RootPolicy(Rational(1, 2**30), 60, 80, 128)
    probes = []

    def record(point, chart):
        value = local_weight(point, chart, volume_scale=1, covering_degree=9, bits=80)
        return {"root_pair": list(point.root_pair), "chart_pivots": list(chart.pivots),
                "coordinate_orders": [chart.free_indices[0], chart.x_solve,
                                      chart.free_indices[1], chart.u_solve, chart.free_indices[2]],
                "positive_denominator": bounds._interval_record(value.denominator),
                "conormal_terms_Ax_Au_Ap_Bp": [bounds._interval_record(c)
                                               for c in value.conormal_terms],
                "cover_weight_without_pi_cubed": bounds._interval_record(
                    value.cover_weight_without_pi_cubed,
                )}

    for raw in parent["actual_configurations"]:
        name = raw["name"]
        intersection = regular_configuration(name, policy)
        records = []
        for pair in intersection.root_pairs:
            xp, xs = (1, 0) if pair[0] == "infinity" else (0, 2)
            chart = measure.ProjectionChart(xp, xs, 0, 2, 0 if name == "finite_chart" else 1)
            point = bounds.BoundedCoverPoint(intersection, pair, chart.pivots, 80)
            records.append(record(point, chart))
        probes.append({"kind": name, "records": records})
    line = roots.ProjectiveLine((1, 0, 0), (0, 1, 1))
    for raw in critical_parent["actual_axis_fiber_probes"]:
        side, axis = raw["source_side"], raw["source_axis"]
        source = tuple(int(i == axis) for i in range(3))
        intersection = critical.configuration(source, line, source_side=side,
                                              parameter_pivot=0, policy=policy)
        remaining = tuple(i for i in range(3) if i != axis)
        chart = (measure.ProjectionChart(axis, remaining[1], 0, 2, 0) if side == 1
                 else measure.ProjectionChart(0, 2, axis, remaining[1], 0))
        probes.append({"kind": "axis_critical", "source_side": side, "source_axis": axis,
                       "records": [record(bounds.BoundedCoverPoint(intersection, pair,
                                                                   chart.pivots, 80), chart)
                                   for pair in intersection.root_pairs]})
    payload = {
        "schema": "alternate-metric-projection-free-weights-v1",
        "positive_measure_artifact_digest": positive_digest,
        "critical_chart_artifact_digest": critical_digest,
        "moment_artifact_digest": parent["moment_artifact_digest"],
        "proof": PROOF,
        "proof_sha256": hashlib.sha256((measure.ROOT / PROOF).read_bytes()).hexdigest(),
        "source_convention_reference": "https://arxiv.org/html/0712.3563v2",
        "ambient_coordinate_order": ["s", "z", "r", "w", "t"],
        "denominator_rule": "D=det(G)*det(J*inverse(G)*adjoint(J))",
        "positive_conormal_rule": "Ax*Au+Ax*Bp+Au*Ap",
        "cover_weight_rule": "72*norm(scale)/(6*D); pi^3 factored out",
        "bound_bits": 80, "covering_degree": 9,
        "actual_domain_count": 36, "actual_domain_probes": probes,
        "projection_free_weight_identity_derived": True,
        "weight_formula_valid_on_all_smooth_cover_charts": True,
        "individual_projection_inverses_required": False,
        "declared_projection_free_weight_enclosures_available": True,
        "all_triangle_node_inputs_certified": False,
        "complete_global_input_coverage_certified": False,
        "quantitative_global_weight_bound_available": False,
        "controlled_numerical_sampling_available": False,
        "numerical_metrics_available": False, "physical_yukawas_available": False,
        "extension_point_selected": False, "physical_kahler_class_selected": False,
        "vacuum_selected": False, "observational_inputs_used": False,
        "next_required_object": (
            "quantitative global conormal lower bound, controlled independent projective "
            "proposals and certified inputs, complete section throughput, integration errors "
            "and Ricci-flat/HYM convergence"
        ),
    }
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    return payload


def write_artifact():
    payload = weight_artifact()
    OUTPUT.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(write_artifact()["artifact_digest"])
