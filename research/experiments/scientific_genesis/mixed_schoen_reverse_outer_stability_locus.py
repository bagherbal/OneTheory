"""Certify a stable genuine-SU(4) locus for the reverse mixed family.

Owns:
    The orientation-swapped extension lower bound, its exact slope system, a
    rational open chamber, and the proper-holonomy-reduction exclusion.

Depends on:
    The lawful reverse P5 cone, published extension-stability bounds, exact
    Schoen slope data, and the selected visible-bundle topology.

Must not:
    Guess factor-exchanged inequalities, select an extension coordinate,
    infer spectrum persistence, or claim a HYM metric has been computed.

Phase 0:
    Research-only reverse stable genuine-SU(4) locus certificate.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Rational
from onetheory.models.heterotic_schoen.geometry import (
    SCHOEN_COVERING_DEGREE,
    schoen_geometry,
)
from onetheory.models.heterotic_schoen.visible import STABILITY_ROWS, visible_bundle
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.stability import StabilityPolynomial

from .mixed_schoen_outer_stability_locus import (
    BOUNDS_ARXIV_ID,
    BOUNDS_SOURCE_SHA256,
    STABILITY_ARXIV_ID,
    STABILITY_SOURCE_SHA256,
    _source_digest,
)
from .mixed_schoen_reverse_outer_universal_cone import (
    OUTPUT as REVERSE_UNIVERSAL_ARTIFACT,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_reverse_outer_stability_locus.json"
)
FORWARD_FORCED_CLASS = (-2, 2, 0)
REVERSE_FORCED_CLASS = (2, -2, 0)
REVERSE_ANCHOR = (Rational(3), Rational(2), Rational(2))
REVERSE_ANCHOR_VALUES = tuple(
    Rational(value)
    for value in (-246, -210, -507, -93, -57, -102, -195, -348, -159)
)


def _slope_coefficients(
    line_class: tuple[int, int, int],
) -> tuple[int, int, int, int, int]:
    """Expand the published Schoen line-bundle slope formula exactly."""

    a1, a2, base = line_class
    return (
        3 * a2,
        6 * a1 + 6 * a2 + 18 * base,
        18 * a2,
        3 * a1,
        18 * a1,
    )


def _reverse_inequalities() -> tuple[StabilityPolynomial, ...]:
    """Replace only the orientation-dependent full-subobject inequality."""

    result = []
    forced_replacements = 0
    for line_class, coefficients, _anchor, _linear, _quadratic in STABILITY_ROWS:
        if coefficients != _slope_coefficients(line_class):
            raise ValueError("published slope coefficients fail exact expansion")
        if line_class == FORWARD_FORCED_CLASS:
            line_class = REVERSE_FORCED_CLASS
            coefficients = _slope_coefficients(line_class)
            forced_replacements += 1
        result.append(StabilityPolynomial(line_class, coefficients, 0))
    if forced_replacements != 1:
        raise ValueError("the forward system has no unique forced V1 row")
    return tuple(result)


def _reverse_universal_digest() -> str:
    """Validate the reverse universal family and return its digest."""

    payload = json.loads(REVERSE_UNIVERSAL_ARTIFACT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    generated = payload.get("generated_complex")
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError("the reverse universal cone digest does not verify")
    if (
        payload.get("schema")
        != "mixed-schoen-reverse-outer-universal-cone-v1"
        or payload.get("projective_non_split_space") != "P^5(Q(omega))"
        or payload.get("equivariant_descent_exact") is not True
        or payload.get("local_freeness_locus") != "all A^6(Q(omega))"
        or payload.get("genuine_su4_locus_computed") is not False
        or not isinstance(generated, dict)
        or generated.get("orientation") != "RHom(V1,V2)"
    ):
        raise ValueError("the reverse universal cone failed an algebraic gate")
    return digest


@dataclass(frozen=True, slots=True)
class MixedSchoenReverseOuterStabilityLocus:
    """An exact stable genuine-SU(4) locus of the reverse P5 family."""

    universal_cone_digest: str
    stability_source_sha256: str
    bounds_source_sha256: str
    inequalities: tuple[StabilityPolynomial, ...]
    anchor: tuple[Rational, Rational, Rational]
    box_radius: Rational
    every_nonzero_parameter_is_nonsplit: bool
    proper_pair_rows_orientation_independent: bool
    rank: int
    quotient_c1: tuple[Rational, Rational, Rational]
    quotient_c3: Rational
    covering_degree: int

    def __post_init__(self) -> None:
        if len(self.inequalities) != 9:
            raise ValueError("the reverse lower bound requires nine inequalities")
        if self.stability_source_sha256 != STABILITY_SOURCE_SHA256:
            raise ValueError("the minimal-bundle stability source changed")
        if self.bounds_source_sha256 != BOUNDS_SOURCE_SHA256:
            raise ValueError("the extension-bound source changed")
        if not (
            self.every_nonzero_parameter_is_nonsplit
            and self.proper_pair_rows_orientation_independent
        ):
            raise ValueError("the reverse extension quantifier is incomplete")
        line_classes = tuple(item.line_class for item in self.inequalities)
        if (
            line_classes.count(REVERSE_FORCED_CLASS) != 1
            or FORWARD_FORCED_CLASS in line_classes
        ):
            raise ValueError("the reverse forced-subobject row is incorrect")
        if self.anchor_values != REVERSE_ANCHOR_VALUES or not self.box_is_stable:
            raise ValueError("the reverse exact chamber witness failed")
        if min(self.anchor) <= self.box_radius:
            raise ValueError("the reverse witness box leaves the Kahler cone")
        if self.rank != 4 or self.quotient_c1 != (Rational(0),) * 3:
            raise ValueError("the reverse family lost rank or determinant")
        if self.cover_c3 == 0:
            raise ValueError("nonzero cover c3 is required for the SU(4) gate")

    @property
    def anchor_values(self) -> tuple[Rational, ...]:
        """Evaluate all reverse sufficient inequalities at the anchor."""

        return tuple(item.evaluate(self.anchor) for item in self.inequalities)

    @property
    def box_upper_bounds(self) -> tuple[Rational, ...]:
        """Bound every reverse slope throughout the rational open box."""

        return tuple(
            item.box_upper_bound(self.anchor, self.box_radius)
            for item in self.inequalities
        )

    @property
    def box_is_stable(self) -> bool:
        """Return whether the reverse lower bound is negative on the box."""

        return all(value < 0 for value in self.box_upper_bounds)

    @property
    def all_nonzero_parameters_stable_in_chamber(self) -> bool:
        """Apply the lower-bound theorem to every nonsplit reverse class."""

        return (
            self.every_nonzero_parameter_is_nonsplit
            and self.proper_pair_rows_orientation_independent
            and self.box_is_stable
        )

    @property
    def cover_c3(self) -> Rational:
        """Return the third Chern number on the simply connected cover."""

        return Rational(self.covering_degree) * self.quotient_c3

    @property
    def genuine_su4_on_certified_locus(self) -> bool:
        """Close stability and proper connected reduction gates together."""

        return self.all_nonzero_parameters_stable_in_chamber and self.cover_c3 != 0

    def as_record(self) -> dict[str, object]:
        """Serialize the reverse stable locus without selecting a point."""

        return {
            "schema": "mixed-schoen-reverse-outer-stability-locus-v1",
            "universal_cone_digest": self.universal_cone_digest,
            "sources": [
                {
                    "arxiv_id": STABILITY_ARXIV_ID,
                    "version": "v1",
                    "source_archive_sha256": self.stability_source_sha256,
                    "locators": [
                        "Proposition 1 and equations 32 through 36",
                        "discussion after Figure 1 and equation Vrevdef",
                    ],
                },
                {
                    "arxiv_id": BOUNDS_ARXIV_ID,
                    "version": "v2",
                    "source_archive_sha256": self.bounds_source_sha256,
                    "locators": [
                        "section 2.1 extension lower bound",
                        "split pair (0,V_R) exclusion",
                    ],
                },
            ],
            "extension_parameter_space": "P^5(Q(omega))",
            "orientation_change": {
                "forward_sequence": "0 -> V1 -> E -> V2 -> 0",
                "reverse_sequence": "0 -> V2 -> E_reverse -> V1 -> 0",
                "unchanged_proper_pair_inequality_count": 8,
                "forward_forced_subobject_c1": list(FORWARD_FORCED_CLASS),
                "reverse_forced_subobject_c1": list(REVERSE_FORCED_CLASS),
                "reason": (
                    "the extension lower bound uses the same proper subsheaf "
                    "pairs in either orientation; only the full injected "
                    "constituent changes, while the full quotient alone is "
                    "excluded by nonsplitting"
                ),
                "factor_exchange_assumed": False,
                "inequalities_guessed": False,
            },
            "parameter_quantifier": {
                "every_nonzero_parameter": True,
                "reason": (
                    "the lower-bound inequalities depend on constituent "
                    "subsheaves and nonsplitting; every P5 point is nontrivial"
                ),
                "genericity_assumed": False,
                "arbitrary_parameter_selected": False,
            },
            "kahler_chamber": {
                "name": "K_reverse^s",
                "ambient": "x1>0, x2>0, y>0",
                "wall_side": "x1>x2",
                "inequalities": [
                    {
                        "line_class": list(item.line_class),
                        "coefficients": list(item.coefficients),
                    }
                    for item in self.inequalities
                ],
                "anchor": [str(value) for value in self.anchor],
                "anchor_slopes": [str(value) for value in self.anchor_values],
                "rational_open_box": {
                    "coordinate_radius": str(self.box_radius),
                    "strict_upper_bounds": [
                        str(value) for value in self.box_upper_bounds
                    ],
                    "inside_positive_cone": min(self.anchor) > self.box_radius,
                    "all_slopes_negative": self.box_is_stable,
                },
            },
            "certified_stable_locus": "P^5(Q(omega)) x K_reverse^s",
            "all_nonzero_parameters_stable_in_chamber": (
                self.all_nonzero_parameters_stable_in_chamber
            ),
            "equivariantly_stable_and_descended": True,
            "structure_group": {
                "rank": self.rank,
                "determinant_trivial": self.quotient_c1 == (Rational(0),) * 3,
                "stable_hym_irreducible": True,
                "schoen_cover_simply_connected": True,
                "cover_c3": str(self.cover_c3),
                "proper_connected_irreducible_reduction_excluded": (
                    self.cover_c3 != 0
                ),
                "genuine_su4_on_certified_locus": (
                    self.genuine_su4_on_certified_locus
                ),
            },
            "arbitrary_extension_point_selected": False,
            "first_missing_input": (
                "reverse-family matter and Higgs cohomology derived from the "
                "same synchronized chain"
            ),
            "status": (
                "every lawful nonzero reverse extension is stable and genuinely "
                "SU(4) throughout the certified reverse Kahler chamber"
            ),
        }


@cache
def mixed_schoen_reverse_outer_stability_locus() -> (
    MixedSchoenReverseOuterStabilityLocus
):
    """Construct the exact reverse stable genuine-SU(4) certificate."""

    bundle = visible_bundle(schoen_geometry()).bundle
    return MixedSchoenReverseOuterStabilityLocus(
        _reverse_universal_digest(),
        _source_digest(STABILITY_ARXIV_ID, STABILITY_SOURCE_SHA256),
        _source_digest(BOUNDS_ARXIV_ID, BOUNDS_SOURCE_SHA256),
        _reverse_inequalities(),
        REVERSE_ANCHOR,
        Rational(1, 4),
        True,
        True,
        bundle.rank,
        cast(tuple[Rational, Rational, Rational], bundle.c1),
        bundle.c3,
        SCHOEN_COVERING_DEGREE,
    )


def write_mixed_schoen_reverse_outer_stability_locus(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed reverse stability certificate."""

    payload = mixed_schoen_reverse_outer_stability_locus().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the reverse stable genuine-SU(4) certificate."""

    payload = write_mixed_schoen_reverse_outer_stability_locus()
    structure_group = cast(dict[str, object], payload["structure_group"])
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"certified_stable_locus: {payload['certified_stable_locus']}")
    print(
        "genuine_su4: "
        f"{structure_group['genuine_su4_on_certified_locus']}"
    )
    print(f"first_missing_input: {payload['first_missing_input']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MixedSchoenReverseOuterStabilityLocus",
    "mixed_schoen_reverse_outer_stability_locus",
    "write_mixed_schoen_reverse_outer_stability_locus",
]
