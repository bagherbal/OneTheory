"""Check the stability-theorem scope of the retained section polarization.

Owns:
    Exact independent ambient-intersection checks of the nine source bounds,
    their restricted open interval and the frozen twist's applicability gap.

Depends on:
    Trusted generation and alternate-stability artifacts, published Schoen
    geometry, exact polynomial arithmetic and the source stability inequalities.

Must not:
    Infer instability from sufficient bounds, select a physical Kahler class,
    change sections or samples, or claim balanced/HYM convergence or a vacuum.

Phase 0:
    Research theorem-scope test only; physical metric inputs remain unresolved.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from onetheory.math.numbers import Rational, coerce_rational
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from onetheory.models.heterotic_schoen.visible import STABILITY_ROWS

ROOT = Path(__file__).resolve().parents[3]
DIRECTORY = ROOT / "data/generated/scientific_genesis"
OUTPUT = DIRECTORY / "metric_polarization_scope.json"
NOTE = Path(__file__).with_name("METRIC_POLARIZATION_SCOPE_NOTE.md")
GENERATION_DIGEST = "3ca16bfa116c6b5530d73e74486eb196d37dbf9c0f7e75d445e84c41176fe063"
STABILITY_DIGEST = "570132144ddccead002f9e5957de29bce23d0f73fb94d0e97230e34ba706346f"


def _digest(record):
    return hashlib.sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()


def _trusted(name, expected):
    record = json.loads((DIRECTORY / f"{name}.json").read_bytes())
    unsigned = {key: value for key, value in record.items() if key != "artifact_digest"}
    if record.get("artifact_digest") != expected or _digest(unsigned) != expected:
        raise ValueError("the trusted metric prerequisite changed")
    return record


def _sources():
    files = (
        Path(__file__), NOTE,
        ROOT / "src/onetheory/math/numbers.py",
        ROOT / "src/onetheory/math/polynomials.py",
        ROOT / "src/onetheory/math/geometry.py",
        ROOT / "src/onetheory/models/heterotic_schoen/geometry.py",
        ROOT / "src/onetheory/models/heterotic_schoen/visible.py",
        ROOT / "data/published/visible_carrier/source_manifest.json",
        Path(__file__).with_name("ALTERNATE_STABILITY_NOTE.md"),
        Path(__file__).with_name("ALTERNATE_METRIC_QUOTIENT_GENERATION_NOTE.md"),
    )
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files}


def ambient_cover_triple(left, middle, right):
    """Integrate using P2_x x P2_u x P1_p, independently of its tensor table.

    The cover class is (3x+p)(3u+p); the top monomial is x^2 u^2 p.
    Coordinates explicitly order tau1, tau2, phi as x, u, p, not Cox order.
    """

    variables = tuple(Polynomial.monomial(tuple(int(i == j) for j in range(3)))
                      for i in range(3))

    def linear(coordinates):
        coordinates = tuple(coordinates)
        if len(coordinates) != 3:
            raise ValueError("ambient divisors require the three named coordinates")
        return sum((variable.scale(coerce_rational(value)) for variable, value in
                    zip(variables, coordinates, strict=True)), Polynomial.zero(3))

    x, u, p = variables
    result = linear(left) * linear(middle) * linear(right) * (x.scale(3) + p) * (
        u.scale(3) + p
    )
    return dict(result.terms).get((2, 2, 1), Rational(0))


def restricted_sufficient_interval(first, second):
    """Solve all strict source bounds at (first, second, y), y positive.

    Endpoints bound this sufficient theorem, not the actual stability chamber.
    """

    first, second = coerce_rational(first), coerce_rational(second)
    if min(first, second) <= 0:
        raise ValueError("the restricted slice requires positive exact coordinates")
    base = (first, second, Rational(0))
    fiber = (Rational(0), Rational(0), Rational(1))
    lower, upper = Rational(0), None
    rows = []
    for line, _, *_ in STABILITY_ROWS:
        constant = ambient_cover_triple(line, base, base)
        linear = 2 * ambient_cover_triple(line, base, fiber)
        if ambient_cover_triple(line, fiber, fiber) != 0:
            raise ValueError("the source slice acquired a quadratic fiber term")
        rows.append((line, constant, linear))
        if linear < 0:
            lower = max(lower, -constant / linear)
        elif linear > 0:
            bound = -constant / linear
            upper = bound if upper is None else min(upper, bound)
        elif constant >= 0:
            raise ValueError("the sufficient slice is empty")
    if upper is None or upper <= lower:
        raise ValueError("no bounded nonempty sufficient interval was established")
    return lower, upper, tuple(rows)


def build_record():
    """Expose the precise missing hypothesis without replaying cloud geometry."""

    generation = _trusted("alternate_metric_quotient_generation", GENERATION_DIGEST)
    stability = _trusted("alternate_constituent_outer_stability_locus", STABILITY_DIGEST)
    twist = tuple(generation["generating_twist_cover_degree"])
    if twist != (14, 16, 1) or generation["quotient_h0_rank_four_at_generating_twist"] != 5345:
        raise ValueError("the retained original section polarization changed")
    if stability["full_kahler_stability_chamber_computed"] is not False:
        raise ValueError("the source is not merely a sufficient chamber certificate")
    geometry = schoen_geometry()
    degrees = dict(geometry.cover.cox.multidegrees)
    if degrees["p1"] != (3, 1, 0) or degrees["p2"] != (0, 1, 3):
        raise ValueError("the ambient complete-intersection multidegrees changed")
    if geometry.basis.labels != ("tau1", "tau2", "phi") or geometry.quotient.order != 9:
        raise ValueError("the named basis or free covering degree changed")
    source_rows = stability["kahler_chamber"]["inequalities"]
    lower, upper, restricted = restricted_sufficient_interval(*twist[:2])
    rows = []
    units = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    for (line, coefficients, *_), source, (_, constant, linear) in zip(
        STABILITY_ROWS, source_rows, restricted, strict=True,
    ):
        independent = tuple(ambient_cover_triple(line, units[i], units[j]) * factor
                            for i, j, factor in ((0, 0, 1), (0, 1, 2), (0, 2, 2),
                                                 (1, 1, 1), (1, 2, 2)))
        if (independent != coefficients or source["line_class"] != list(line)
                or source["coefficients"] != list(coefficients)):
            raise ValueError("the published slope coefficients do not match intersections")
        cover = ambient_cover_triple(line, twist, twist)
        quotient = geometry.bundle_slope(
            geometry.quotient_divisor(line), geometry.quotient_divisor(twist), 1,
        )
        tensor = geometry.cover_slope(
            geometry.cover_divisor(line), geometry.cover_divisor(twist), 1,
        )
        if cover != tensor or cover != 9 * quotient or cover != constant + linear * twist[2]:
            raise ValueError("the exact slope normalization or restricted polynomial changed")
        rows.append({"line_class": list(line), "cover_line_slope_exact": str(cover),
                     "quotient_line_slope_exact": str(quotient),
                     "slice_constant_exact": str(constant), "slice_linear_exact": str(linear),
                     "strictly_negative_at_retained_twist": cover < 0})
    return {
        "schema": "metric-polarization-scope-v1",
        "status": "PROVED",
        "claim": "the retained twist lies outside the source sufficient stability chamber",
        "prerequisite_digests": {"generation": GENERATION_DIGEST, "stability": STABILITY_DIGEST},
        "published_sources": stability["sources"],
        "normalization": "rank-one line slopes; cover = nine times quotient",
        "ambient_coordinate_order": ["x=tau1", "u=tau2", "p=phi"],
        "retained_twist": list(twist), "original_section_count": 5345,
        "rows": rows,
        "sufficient_chamber_test_passed": all(row["strictly_negative_at_retained_twist"]
                                            for row in rows),
        "restricted_sufficient_interval": {"first": 14, "second": 16,
                                          "lower_exact": str(lower), "upper_exact": str(upper),
                                          "endpoints_excluded": True},
        "every_positive_rescaling_has_the_same_slope_signs": True,
        "rescaling_reason": "each line slope is a homogeneous quadratic in the polarization",
        "scope_failure_is_a_bundle_instability_proof": False,
        "actual_destabilizing_subsheaf_constructed": False,
        "stability_at_retained_polarization_established": False,
        "original_sections_or_cloud_inputs_changed": False,
        "finite_cloud_should_stop_because_of_this_sufficient_test": False,
        "physical_kahler_class_selected": False, "observations_used": False,
        "ricci_flat_or_hym_metric_available": False, "physical_yukawas_available": False,
        "common_stabilized_vacuum_available": False,
        "first_missing_input": (
            "establish actual stability at the retained polarization, or derive a "
            "metric algorithm for an independently declared admissible background; "
            "finite-cloud balance alone cannot supply either hypothesis"
        ),
        "source_files_sha256": _sources(),
    }


def read_certificate(*, expected_digest, path=OUTPUT):
    """Verify trusted scope and independent exact arithmetic, with no new samples."""

    record = json.loads(path.read_bytes())
    unsigned = {key: value for key, value in record.items() if key != "artifact_digest"}
    if record.get("artifact_digest") != expected_digest or _digest(unsigned) != expected_digest:
        raise ValueError("the trusted metric polarization certificate changed")
    if unsigned != build_record():
        raise ValueError("metric polarization scope or independent arithmetic changed")
    return record


def write_certificate(path=OUTPUT):
    record = build_record()
    record["artifact_digest"] = _digest(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return record


if __name__ == "__main__":
    report = write_certificate()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"sufficient_chamber_test_passed: {report['sufficient_chamber_test_passed']}")
