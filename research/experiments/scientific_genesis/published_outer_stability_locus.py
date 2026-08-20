"""Certify the generic stable SU(4) locus of the published outer family.

Owns:
    Exact evaluation of the nine published slope inequalities, a rational
    open-box witness, and the source-scoped generic stability and structure-
    group consequences for the reconstructed universal outer extension.

Depends on:
    The content-addressed universal cone, published stability metadata, exact
    rational arithmetic, and the selected Schoen carrier topology.

Must not:
    Select an extension coordinate, claim every nonzero class is stable,
    invent equations for the exceptional parameter locus, or solve HYM fields.

Phase 0:
    Research-only generic stability certificate; no metric is constructed.
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

from .published_outer_universal_cone import (
    OUTPUT as UNIVERSAL_CONE_ARTIFACT,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/published_outer_stability_locus.json"
SOURCE_MANIFEST = ROOT / "data/published/visible_carrier/source_manifest.json"
STABILITY_ARXIV_ID = "hep-th/0602073"
STABILITY_SOURCE_SHA256 = (
    "8e38123b9d2de8751deecbf295015497ab2ed891244215455fffe756bebf0aea"
)


@dataclass(frozen=True, slots=True)
class StabilityPolynomial:
    """One exact quadratic slope inequality in the published divisor basis."""

    line_class: tuple[int, int, int]
    coefficients: tuple[int, int, int, int, int]
    published_anchor_value: int

    def evaluate(self, point: tuple[Rational, Rational, Rational]) -> Rational:
        """Evaluate the slope at ``(x1, x2, y)`` exactly."""

        x1, x2, y = point
        a, b, c, d, e = (Rational(value) for value in self.coefficients)
        return (
            a * x1 * x1
            + b * x1 * x2
            + c * x1 * y
            + d * x2 * x2
            + e * x2 * y
        )

    def box_upper_bound(
        self,
        center: tuple[Rational, Rational, Rational],
        radius: Rational,
    ) -> Rational:
        """Bound the polynomial above on a common coordinate box.

        The exact Taylor expansion has a linear term bounded by the one-norm
        of the gradient times ``radius`` and a quadratic remainder bounded by
        the one-norm of the five displayed coefficients times ``radius**2``.
        """

        x1, x2, y = center
        a, b, c, d, e = (Rational(value) for value in self.coefficients)
        gradient = (
            Rational(2) * a * x1 + b * x2 + c * y,
            b * x1 + Rational(2) * d * x2 + e * y,
            c * x1 + e * x2,
        )
        linear_bound = sum((abs(value) for value in gradient), Rational(0))
        quadratic_bound = sum(
            (abs(value) for value in (a, b, c, d, e)),
            Rational(0),
        )
        return (
            self.evaluate(center)
            + linear_bound * radius
            + quadratic_bound * radius * radius
        )


@dataclass(frozen=True, slots=True)
class PublishedOuterStabilityLocus:
    """The exact certified part of the published stable outer-family locus."""

    universal_cone_digest: str
    source_archive_sha256: str
    inequalities: tuple[StabilityPolynomial, ...]
    anchor: tuple[Rational, Rational, Rational]
    box_radius: Rational
    rank: int
    quotient_c1: tuple[Rational, Rational, Rational]
    quotient_c3: Rational
    covering_degree: int

    def __post_init__(self) -> None:
        if len(self.inequalities) != 9:
            raise ValueError("the published sufficient chamber requires nine inequalities")
        if self.source_archive_sha256 != STABILITY_SOURCE_SHA256:
            raise ValueError("the stability source archive digest changed")
        if self.rank != 4 or self.quotient_c1 != (Rational(0),) * 3:
            raise ValueError("the reconstructed family lost rank four or trivial determinant")
        if self.quotient_c3 == 0 or self.covering_degree <= 0:
            raise ValueError("the structure-group certificate requires nonzero c3 and a cover")
        if min(self.anchor) <= self.box_radius:
            raise ValueError("the certified box must remain inside the positive Kahler cone")
        if not self.anchor_values_match or not self.box_is_stable:
            raise ValueError("the published stability witness failed exact recomputation")

    @property
    def anchor_values(self) -> tuple[Rational, ...]:
        """Return all exact slopes at the published integral anchor."""

        return tuple(inequality.evaluate(self.anchor) for inequality in self.inequalities)

    @property
    def anchor_values_match(self) -> bool:
        """Return whether the source's nine anchor values reproduce exactly."""

        return self.anchor_values == tuple(
            Rational(inequality.published_anchor_value)
            for inequality in self.inequalities
        )

    @property
    def box_upper_bounds(self) -> tuple[Rational, ...]:
        """Return rigorous upper bounds throughout the rational witness box."""

        return tuple(
            inequality.box_upper_bound(self.anchor, self.box_radius)
            for inequality in self.inequalities
        )

    @property
    def box_is_stable(self) -> bool:
        """Return whether every sufficient slope is negative on the whole box."""

        return all(bound < 0 for bound in self.box_upper_bounds)

    @property
    def cover_c3(self) -> Rational:
        """Return the third Chern number after pullback to the Schoen cover."""

        return Rational(self.covering_degree) * self.quotient_c3

    @property
    def proper_connected_irreducible_reduction_excluded(self) -> bool:
        """Exclude proper connected irreducible rank-four holonomy reductions.

        Proper connected irreducible subgroups of SU(4) preserve a symmetric or
        alternating bilinear form in the defining four-dimensional
        representation. Such a reduction makes the bundle self-dual and forces
        its odd Chern classes to be two-torsion. The nonzero integral cover c3
        rules this out.
        """

        return self.cover_c3 != 0

    @property
    def generic_genuine_su4_locus_certified(self) -> bool:
        """Return the exact source-conditioned generic SU(4) conclusion."""

        return self.box_is_stable and self.proper_connected_irreducible_reduction_excluded

    def as_record(self) -> dict[str, object]:
        """Serialize the stable generic locus without fabricating its complement."""

        return {
            "schema": "published-outer-stability-locus-v1",
            "universal_cone_digest": self.universal_cone_digest,
            "source": {
                "arxiv_id": STABILITY_ARXIV_ID,
                "version": "v1",
                "source_archive_sha256": self.source_archive_sha256,
                "locators": [
                    "eq:Vdef",
                    "sec:ext",
                    "prop:stable",
                    "eq:inequalities",
                    "eq:omega",
                ],
            },
            "extension_parameter_space": "P^3(Q(omega))",
            "certified_parameter_locus": {
                "name": "U_pub",
                "description": (
                    "the nonempty Zariski-open locus of generic published "
                    "nonsplit invariant extensions"
                ),
                "nonempty": True,
                "open": True,
                "every_nonzero_parameter_claimed": False,
                "exceptional_locus_ideal_computed": False,
                "arbitrary_parameter_selected": False,
            },
            "kahler_chamber": {
                "name": "K^s",
                "ambient": "x1>0, x2>0, y>0",
                "definition": "all nine listed slope polynomials are strictly negative",
                "inequalities": [
                    {
                        "line_class": list(inequality.line_class),
                        "coefficient_order": [
                            "x1^2",
                            "x1*x2",
                            "x1*y",
                            "x2^2",
                            "x2*y",
                        ],
                        "coefficients": list(inequality.coefficients),
                    }
                    for inequality in self.inequalities
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
            "certified_stable_locus": "U_pub x K^s",
            "slope_stable": True,
            "equivariantly_stable_and_descended": True,
            "structure_group": {
                "rank": self.rank,
                "determinant_trivial": self.quotient_c1 == (Rational(0),) * 3,
                "stable_hym_irreducible": True,
                "schoen_cover_simply_connected": True,
                "cover_c3": str(self.cover_c3),
                "proper_connected_irreducible_reduction_excluded": (
                    self.proper_connected_irreducible_reduction_excluded
                ),
                "genuine_su4_on_certified_locus": (
                    self.generic_genuine_su4_locus_certified
                ),
                "argument": (
                    "stable determinant-trivial bundles have irreducible SU(4) "
                    "HYM holonomy; on the simply connected cover the holonomy "
                    "is connected, while every proper connected irreducible "
                    "subgroup preserves a bilinear form and would force 2*c3=0"
                ),
            },
            "full_parameterwise_stability_classification": False,
            "unresolved_parameter_data": (
                "equations for the proper exceptional subset P^3 minus U_pub"
            ),
            "arbitrary_extension_point_selected": False,
            "status": (
                "nonempty generic stable descended genuine-SU(4) locus "
                "certified over the exact published Kahler chamber"
            ),
        }


def _source_digest(path: Path = SOURCE_MANIFEST) -> str:
    """Read the declared stability source digest from the immutable manifest."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    sources = payload.get("sources")
    if not isinstance(sources, list):
        raise ValueError("the published source manifest lacks source records")
    matches = [
        source
        for source in sources
        if isinstance(source, dict) and source.get("arxiv_id") == STABILITY_ARXIV_ID
    ]
    if len(matches) != 1:
        raise ValueError("the stability source must occur exactly once")
    return cast(str, matches[0]["source_archive_sha256"])


def _universal_digest(path: Path = UNIVERSAL_CONE_ARTIFACT) -> str:
    """Validate and return the upstream universal-cone artifact digest."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError("the universal outer cone artifact digest does not verify")
    if payload.get("projective_non_split_space") != "P^3(Q(omega))":
        raise ValueError("the stability theorem requires the published projective family")
    return digest


@cache
def published_outer_stability_locus() -> PublishedOuterStabilityLocus:
    """Construct the exact generic stability certificate."""

    bundle = visible_bundle(schoen_geometry()).bundle
    inequalities = tuple(
        StabilityPolynomial(line_class, coefficients, anchor_value)
        for line_class, coefficients, anchor_value, _, _ in STABILITY_ROWS
    )
    return PublishedOuterStabilityLocus(
        _universal_digest(),
        _source_digest(),
        inequalities,
        (Rational(6), Rational(9), Rational(3)),
        Rational(1, 32),
        bundle.rank,
        bundle.c1,
        bundle.c3,
        SCHOEN_COVERING_DEGREE,
    )


def write_published_outer_stability_locus(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed generic stability certificate."""

    payload = published_outer_stability_locus().as_record()
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
    """Regenerate the generic published stability artifact."""

    payload = write_published_outer_stability_locus()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"certified_stable_locus: {payload['certified_stable_locus']}")
    print(
        "genuine_su4: "
        f"{payload['structure_group']['genuine_su4_on_certified_locus']}"
    )
    print(f"next_missing: {payload['unresolved_parameter_data']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PublishedOuterStabilityLocus",
    "StabilityPolynomial",
    "published_outer_stability_locus",
]
