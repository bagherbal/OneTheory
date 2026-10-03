"""Enclose unchanged auxiliary weights on actual coupled uncertain cover families.

Owns:
    Certified family membership gates, homogeneous norm and gradient bounds,
    positive conormal denominators, and explicit cover/quotient weight conventions.

Depends on:
    Actual same-base root certificates, the established homogeneous weight
    identity, original cubic equations, and outward exact interval arithmetic.

Must not:
    Admit bare balls or centers as cover points, choose physical moduli,
    duplicate physics, infer independent sampling, or report converged metrics.

Phase 0:
    Research integration weights only; physical normalization remains unresolved.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from onetheory.math.numbers import Eisenstein, Rational
from onetheory.models.heterotic_schoen.geometry import schoen_geometry

from . import projective_uncertain_intersections as intersections
from .alternate_metric_enclosures import Interval, polynomial_value

ROOT = intersections.ROOT
OUTPUT = ROOT / "data/generated/scientific_genesis/uncertain_cover_weights.json"
PROOF = Path(__file__).with_name("UNCERTAIN_COVER_WEIGHTS_NOTE.md")


@dataclass(frozen=True, slots=True)
class HomogeneousWeight:
    """Weight intervals without a tangent frame or hidden homogeneous normalization."""

    coordinates: tuple
    homogeneous_squared_norms: tuple[Interval, ...]
    normalized_conormal_terms: tuple[Interval, ...]
    denominator: Interval
    cover_weight_without_pi_cubed: Interval
    quotient_weight_without_pi_cubed: Interval


def _norm(values):
    return sum((value.norm_interval() for value in values),
               Interval(Rational(0), Rational(0), values[0].bits))


def _weight_bounds(point, *, volume_scale, covering_degree):
    """Arithmetic on coordinate enclosures; this alone does NOT certify membership."""

    if type(covering_degree) is not int or covering_degree < 1:
        raise ValueError("an explicit positive integer covering degree is required")
    scale = Eisenstein.coerce(volume_scale)
    if scale.is_zero():
        raise ValueError("an explicit nonzero residue scale is required")
    x, u, p = (intersections._balls(values, count)
               for values, count in zip(point, (3, 3, 2), strict=True))
    if x[0].bits != u[0].bits or x[0].bits != p[0].bits:
        raise ValueError("all homogeneous groups must use the same declared precision")
    nx, nu, np = (_norm(values) for values in (x, u, p))
    if any(value.lower <= 0 for value in (nx, nu, np)):
        raise ValueError("the bounds do not certify nonzero homogeneous coordinate groups")
    cox = schoen_geometry().cover.cox
    fx, gx = (polynomial_value(polynomial, x) for polynomial in (cox.cubic_f, cox.cubic_g))
    fu, gu = (polynomial_value(polynomial, u) for polynomial in (cox.cubic_f, cox.cubic_g))
    dx = tuple(polynomial_value(cox.cubic_f.derivative(i), x) * p[0]
               + polynomial_value(cox.cubic_g.derivative(i), x) * p[1] for i in range(3))
    du = tuple(polynomial_value(cox.cubic_f.derivative(i), u) * (p[1] * 2)
               + polynomial_value(cox.cubic_g.derivative(i), u) * p[0] for i in range(3))
    ex, eu = _norm(dx) / (nx**2 * np), _norm(du) / (nu**2 * np)
    hx, hu = _norm((fx, gx)) / nx**3, _norm((gu, fu * 2)) / nu**3
    denominator = ex * eu + ex * hu + eu * hx
    if denominator.lower <= 0:
        raise ValueError("the bounds do not certify a positive full conormal denominator")
    cover = denominator._coerce(12 * scale.norm()) / denominator
    return HomogeneousWeight((x, u, p), (nx, nu, np), (ex, eu, hx, hu), denominator,
                             cover, cover / covering_degree)


def configuration_weights(configuration, *, volume_scale, covering_degree):
    """Consume actual coupled root families; never promote a coordinate tuple to a point."""

    if not isinstance(configuration, (intersections.LineBaseLineConfiguration,
                                      intersections.PointLineConfiguration)):
        raise TypeError("an actual coupled uncertain intersection configuration is required")
    return tuple(_weight_bounds(point, volume_scale=volume_scale, covering_degree=covering_degree)
                 for point in configuration.points)


def declared_configurations():
    """Reuse the original admitted input cells and all certified mixture branches."""

    inputs, components, _ = intersections.declared_probes()
    x, u, p = inputs
    hx, hu = (intersections.BoundedLine(cell.coordinates, 0, (1, 2)) for cell in (x, u))
    return (
        intersections.LineBaseLineConfiguration(hx, hu, p.coordinates, *components[0][1]),
        intersections.PointLineConfiguration(x.coordinates, 1, hu, components[1][1]),
        intersections.PointLineConfiguration(u.coordinates, 2, hx, components[2][1]),
    )


def _interval_record(value):
    return {"lower": str(value.lower), "upper": str(value.upper), "bits": value.bits}


def weight_record():
    """Execute unchanged weights on admitted families, retaining every error and gate."""

    from .mixed_schoen_outer_universal_cone import _verified_payload

    parent = intersections.read_uncertain_intersections()
    parent_digest = intersections._digest(parent)
    if parent_digest != "97981cfe6a6d67fd40287c8902a99f4ce3a73729fea6a64b4f133fdce82c0d26":
        raise ValueError("the actual uncertain-root prerequisites changed")
    weight_digest, _ = _verified_payload(OUTPUT.with_name(
        "alternate_metric_projection_free_weights.json",
    ))
    if weight_digest != "cb4eb886edf94ab72b737bc8e3c23a25d2355243557fee40dfe62d24c7cf1e97":
        raise ValueError("the established auxiliary weight convention changed")
    identity_digest, identity = _verified_payload(OUTPUT.with_name(
        "alternate_metric_global_weight_bound.json",
    ))
    identity_sha = hashlib.sha256((ROOT / identity["proof"]).read_bytes()).hexdigest()
    if (identity_digest != "96e3d216aa6157dab686069b095e304de5f7e9600348f42c00fff0691986c0f4"
        or identity_sha != identity["proof_sha256"]):
        raise ValueError("the homogeneous conormal identity or its verified proof changed")
    components = []
    for name, configuration in zip(("A", "Bx", "Bu"), declared_configurations(), strict=True):
        values = configuration_weights(configuration, volume_scale=1, covering_degree=9)
        components.append({
            "component": name,
            "complete_branch_count": len(values),
            "weights": [{
                "coupled_cover_bounds": [[intersections._ball_record(b) for b in group]
                                         for group in value.coordinates],
                "homogeneous_squared_norms": [_interval_record(v)
                                              for v in value.homogeneous_squared_norms],
                "normalized_conormal_terms": [_interval_record(v)
                                               for v in value.normalized_conormal_terms],
                "denominator": _interval_record(value.denominator),
                "cover_weight_without_pi_cubed": _interval_record(
                    value.cover_weight_without_pi_cubed,
                ),
                "quotient_weight_without_pi_cubed": _interval_record(
                    value.quotient_weight_without_pi_cubed,
                ),
            } for value in values],
        })
    return {
        "schema": "uncertain-cover-weights-v1",
        "uncertain_root_parent_digest": parent_digest,
        "established_weight_parent_digest": weight_digest,
        "homogeneous_identity_parent_digest": identity_digest,
        "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
        "homogeneous_identity_proof_sha256": identity_sha,
        "auxiliary_law": "beta^3/72; beta=FS_x+FS_u+FS_p",
        "volume_scale": ["1", "0"],
        "covering_degree": 9,
        "pi_cubed": "symbolic; not numerically substituted",
        "components": components,
        "actual_coupled_family_membership_checked": True,
        "all_norms_and_denominators_certified_positive": True,
        "original_input_and_root_error_retained": True,
        "global_input_coverage_available": False,
        "independent_sampling_cloud_available": False,
        "section_and_frame_bounds_on_new_domains_available": False,
        "controlled_integral_available": False,
        "ricci_flat_metric_available": False,
        "hym_metric_available": False,
        "physical_yukawas_available": False,
        "common_stabilized_vacuum_available": False,
        "observations_used": False,
    }


def write_weights(path=OUTPUT):
    """Atomically save executed admitted-family bounds, never an inferred metric."""

    record = weight_record()
    record["artifact_digest"] = intersections._digest(record)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return record


def read_weights(path=OUTPUT):
    """Recompute actual coupling, every interval, normalizations, parents and scope."""

    record = json.loads(path.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest", None)
    if digest != intersections._digest(record) or record != weight_record():
        raise ValueError("uncertain-cover weights changed their coupling, bounds, inputs or scope")
    return record


if __name__ == "__main__":
    print(write_weights()["artifact_digest"])
