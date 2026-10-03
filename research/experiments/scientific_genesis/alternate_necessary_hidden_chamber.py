"""Apply the published necessary hidden HYM wall to the frozen alternate cone.

Owns:
    Source-pinned rational Chern subtraction, exact common open-box bounds,
    and symbolic sufficient-visible versus necessary-hidden chamber slices.

Depends on:
    The two certified alternate cone/stability artifacts, published Schoen
    topology, exact class and polynomial arithmetic, and existing slope bounds.

Must not:
    Construct a hidden bundle, infer integral anomaly cancellation, claim
    positivity suffices for stability, or select moduli, metrics or a vacuum.

Phase 0:
    Conditional research constraint only; hidden existence remains unresolved.
"""

from __future__ import annotations

import json
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

from onetheory.math.numbers import Rational, coerce_rational
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import (
    SCHOEN_COVERING_DEGREE,
    schoen_geometry,
)
from onetheory.models.heterotic_schoen.visible import STABILITY_ROWS
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.stability import StabilityPolynomial

from .alternate_constituent_outer_stability_locus import OUTPUT as STABILITY
from .alternate_constituent_outer_universal_cone import OUTPUT as CONE
from .mixed_schoen_outer_stability_locus import (
    STABILITY_ARXIV_ID,
    STABILITY_SOURCE_SHA256,
    _source_digest,
)
from .mixed_schoen_outer_universal_cone import _verified_payload

OUTPUT = CONE.with_name("alternate_necessary_hidden_chamber.json")
NOTE = Path(__file__).with_name("ALTERNATE_NECESSARY_HIDDEN_CHAMBER_NOTE.md")
CONE_DIGEST = "b7c4327d8c1ee197f431cf05eebb38f38746a2a4eaf21440ac4338b051ce3fca"
STABILITY_DIGEST = "570132144ddccead002f9e5957de29bce23d0f73fb94d0e97230e34ba706346f"


def necessary_hidden_chamber() -> dict[str, object]:
    """Derive the entire declared box and slice without choosing any point."""

    cone_digest, cone = _verified_payload(CONE)
    stability_digest, _ = _verified_payload(STABILITY)
    if cone_digest != CONE_DIGEST or stability_digest != STABILITY_DIGEST:
        raise ValueError("the necessary hidden chamber changed its trusted parents")
    source = _source_digest(STABILITY_ARXIV_ID, STABILITY_SOURCE_SHA256)
    # Parent pins retain the published sufficient chamber and normalization.
    geometry = schoen_geometry()
    visible = geometry.quotient_class(
        (Rational(Fraction(value)) for value in cone["chern_classes"]["c2"]), 2,
    )
    tangent = geometry.quotient_class((4, 4, 0), 2)
    residual = tangent - visible
    coordinates = residual.coordinates
    if not any(coordinates):
        raise ValueError("strict hidden HYM positivity requires nonzero real c2")
    anchor = (Rational(6), Rational(9), Rational(3))
    radius = Rational(1, 32)
    pairing_at_anchor = sum(
        (c * x for c, x in zip(coordinates, anchor, strict=True)), Rational(0),
    )
    lower = pairing_at_anchor - radius * sum(map(abs, coordinates), Rational(0))
    inequalities = tuple(
        StabilityPolynomial(line, coefficients, value)
        for line, coefficients, value, _, _ in STABILITY_ROWS
    )
    box_upper = tuple(row.box_upper_bound(anchor, radius) for row in inequalities)
    if lower <= 0 or min(anchor) <= radius or any(value >= 0 for value in box_upper):
        raise ValueError("the common necessary open box failed")

    t = Polynomial.monomial((1,), scalar_type=Rational)
    three = Polynomial.constant(3, variable_count=1, scalar_type=Rational)
    four = Polynomial.constant(4, variable_count=1, scalar_type=Rational)
    monomials = ((2, 0, 0), (1, 1, 0), (1, 0, 1), (0, 2, 0), (0, 1, 1))
    slice_rows = tuple(
        Polynomial(zip(monomials, row.coefficients, strict=True), scalar_type=Rational)
        .substitute((three, four, t))
        for row in inequalities
    )
    interval_lower = Rational(0)
    upper_bounds: list[Rational] = []
    affine_rows = []
    for row in slice_rows:
        constant = coerce_rational(row.coefficient((0,)))
        linear = coerce_rational(row.coefficient((1,)))
        affine_rows.append([str(constant), str(linear)])
        if linear < 0:
            interval_lower = max(interval_lower, -constant / linear)
        elif linear > 0:
            upper_bounds.append(-constant / linear)
        elif constant >= 0:
            raise ValueError("a constant slice inequality excludes the entire family")
    interval_upper = min(upper_bounds)
    hidden_constant = 3 * coordinates[0] + 4 * coordinates[1]
    hidden_linear = coordinates[2]
    if hidden_linear >= 0:
        raise ValueError("the declared slice lost its hidden upper wall")
    hidden_upper = -hidden_constant / hidden_linear
    if not interval_lower < hidden_upper < interval_upper:
        raise ValueError("the visible slice no longer straddles the necessary hidden wall")
    return {
        "schema": "alternate-necessary-hidden-chamber-v1",
        "prerequisite_artifact_digests": {"cone": cone_digest, "stability": stability_digest},
        "proof_sha256": sha256(NOTE.read_bytes()).hexdigest(),
        "source": {"arxiv_id": STABILITY_ARXIV_ID, "version": "v1",
                   "source_archive_sha256": source, "equations": [39, 40, 41, 42, 43, 44]},
        "assumptions": ["compact Kahler threefold", "no additional Bianchi sources",
                        "determinant-trivial unitary hidden HYM bundle", "nonzero real c2"],
        "divisor_basis": list(geometry.basis.labels),
        "c2_coordinate_convention": "dual to divisor basis under quotient integration",
        "c2_visible": list(map(str, visible.coordinates)),
        "c2_tangent": list(map(str, tangent.coordinates)),
        "required_rational_hidden_c2": list(map(str, coordinates)),
        "covering_degree": SCHOEN_COVERING_DEGREE,
        "cover_pairing_multiplier": SCHOEN_COVERING_DEGREE,
        "quotient_pairing_coefficients": list(map(str, coordinates)),
        "necessary_wall": "4*x1+7*x2-12*y > 0",
        "common_open_box": {
            "center": list(map(str, anchor)), "coordinate_radius": str(radius),
            "hidden_quotient_pairing_at_center": str(pairing_at_anchor),
            "hidden_quotient_pairing_lower_bound": str(lower),
            "visible_cover_slope_upper_bounds": list(map(str, box_upper)),
            "all_nonzero_outer_parameters": True, "physical_polarization_selected": False,
        },
        "symbolic_slice": {
            "definition": "J=s*(3,4,t), s>0", "parameters": ["s", "t"],
            "squared_scale_removed_from_visible_slopes": True,
            "visible_affine_coefficients_constant_linear": affine_rows,
            "visible_sufficient_interval_open": [str(interval_lower), str(interval_upper)],
            "hidden_pairing_coefficients_after_scale_removed": [
                str(hidden_constant), str(hidden_linear)],
            "necessary_common_interval_open": [str(interval_lower), str(hidden_upper)],
            "excluded_visible_stable_interval": {
                "lower_inclusive": str(hidden_upper), "upper_exclusive": str(interval_upper)},
        },
        "hidden_bundle_constructed": False,
        "hidden_stability_proved": False,
        "integral_or_torsion_anomaly_cancelled": False,
        "full_common_stability_chamber_computed": False,
        "numerical_metrics_available": False,
        "vacuum_selected": False,
        "extension_point_selected": False,
        "physical_yukawas_available": False,
        "observational_inputs_used": False,
        "status": "necessary conditional chamber constraint only; hidden existence unresolved",
    }


def read_hidden_chamber(path: Path = OUTPUT) -> dict[str, object]:
    """Reject forged scope or arithmetic even after an output is rehashed."""

    _, record = _verified_payload(path)
    if record != necessary_hidden_chamber():
        raise ValueError("the necessary hidden chamber differs from its exact derivation")
    return record


def write_hidden_chamber(path: Path = OUTPUT) -> dict[str, object]:
    """Write the small reproducible conditional certificate atomically."""

    payload = necessary_hidden_chamber()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_hidden_chamber()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"necessary_wall: {report['necessary_wall']}")
