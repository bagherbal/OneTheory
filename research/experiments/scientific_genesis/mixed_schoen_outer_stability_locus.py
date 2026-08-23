"""Certify stability and genuine SU(4) for the lawful mixed outer family.

Owns:
    Source-bound nontrivial-extension quantifiers, exact slope inequalities, a
    rational chamber witness, and the proper-holonomy-reduction exclusion.

Depends on:
    The lawful universal P1 cone, published extension-stability theorems,
    exact rational arithmetic, and selected Schoen topology.

Must not:
    Reuse the retired P3 representatives, choose an extension coordinate,
    claim a HYM metric has been computed, or infer a physical spectrum.

Phase 0:
    Research-only stable genuine-SU(4) certificate for the lawful family.
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

from .mixed_schoen_outer_universal_cone import OUTPUT as UNIVERSAL_CONE_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_outer_stability_locus.json"
SOURCE_MANIFEST = ROOT / "data/published/visible_carrier/source_manifest.json"
STABILITY_ARXIV_ID = "hep-th/0602073"
STABILITY_SOURCE_SHA256 = (
    "8e38123b9d2de8751deecbf295015497ab2ed891244215455fffe756bebf0aea"
)
BOUNDS_ARXIV_ID = "hep-th/0512205"
BOUNDS_SOURCE_SHA256 = (
    "f3c339b0ea7d5d26747dac8788400c785a3194077d09974eae5e04293f9a4eab"
)


@dataclass(frozen=True, slots=True)
class MixedSchoenOuterStabilityLocus:
    """Exact stable genuine-SU(4) locus of the lawful nonzero family."""

    universal_cone_digest: str
    stability_source_sha256: str
    bounds_source_sha256: str
    inequalities: tuple[StabilityPolynomial, ...]
    anchor: tuple[Rational, Rational, Rational]
    box_radius: Rational
    extension_bound_applies_to_every_nonsplit: bool
    universal_nonzero_locus_is_nonsplit: bool
    rank: int
    quotient_c1: tuple[Rational, Rational, Rational]
    quotient_c3: Rational
    covering_degree: int

    def __post_init__(self) -> None:
        if len(self.inequalities) != 9:
            raise ValueError("the sufficient chamber requires nine inequalities")
        if self.stability_source_sha256 != STABILITY_SOURCE_SHA256:
            raise ValueError("the minimal-bundle stability source changed")
        if self.bounds_source_sha256 != BOUNDS_SOURCE_SHA256:
            raise ValueError("the extension-bound source changed")
        if not (
            self.extension_bound_applies_to_every_nonsplit
            and self.universal_nonzero_locus_is_nonsplit
        ):
            raise ValueError("the stability quantifier does not cover the lawful family")
        if self.rank != 4 or self.quotient_c1 != (Rational(0),) * 3:
            raise ValueError("the lawful family lost rank four or trivial determinant")
        if self.quotient_c3 == 0 or self.covering_degree <= 0:
            raise ValueError("the structure-group exclusion requires nonzero cover c3")
        if min(self.anchor) <= self.box_radius:
            raise ValueError("the witness box leaves the positive Kahler cone")
        if not self.anchor_values_match or not self.box_is_stable:
            raise ValueError("the exact stability chamber witness failed")

    @property
    def anchor_values(self) -> tuple[Rational, ...]:
        """Return the nine exact slopes at the published integral anchor."""

        return tuple(inequality.evaluate(self.anchor) for inequality in self.inequalities)

    @property
    def anchor_values_match(self) -> bool:
        """Return whether all source anchor values reproduce exactly."""

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
        """Return whether all sufficient slopes stay negative in the box."""

        return all(bound < 0 for bound in self.box_upper_bounds)

    @property
    def all_nonzero_parameters_stable_in_chamber(self) -> bool:
        """Return the exact nontrivial-extension quantifier on lawful P1."""

        return (
            self.extension_bound_applies_to_every_nonsplit
            and self.universal_nonzero_locus_is_nonsplit
            and self.box_is_stable
        )

    @property
    def cover_c3(self) -> Rational:
        """Return the third Chern number after pullback to the Schoen cover."""

        return Rational(self.covering_degree) * self.quotient_c3

    @property
    def proper_connected_irreducible_reduction_excluded(self) -> bool:
        """Exclude proper connected irreducible rank-four reductions."""

        return self.cover_c3 != 0

    @property
    def genuine_su4_on_certified_locus(self) -> bool:
        """Return stable irreducibility plus the odd-Chern reduction gate."""

        return (
            self.all_nonzero_parameters_stable_in_chamber
            and self.proper_connected_irreducible_reduction_excluded
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the full lawful stable locus without choosing a point."""

        return {
            "schema": "mixed-schoen-outer-stability-locus-v1",
            "universal_cone_digest": self.universal_cone_digest,
            "sources": [
                {
                    "arxiv_id": STABILITY_ARXIV_ID,
                    "version": "v1",
                    "source_archive_sha256": self.stability_source_sha256,
                    "locators": [
                        "section 3.2, equations 10 and 15",
                        "Proposition 1 and equations 32 through 36",
                    ],
                },
                {
                    "arxiv_id": BOUNDS_ARXIV_ID,
                    "version": "v2",
                    "source_archive_sha256": self.bounds_source_sha256,
                    "locators": [
                        "section 2.1 nontrivial-extension lower bound",
                        "split pair (0,V_R) exclusion",
                    ],
                },
            ],
            "extension_parameter_space": "P^1(Q(omega))",
            "parameter_quantifier": {
                "every_nonzero_parameter": True,
                "reason": (
                    "the sufficient lower stability bound depends only on "
                    "constituent subsheaves and nonsplitting; every P1 point "
                    "is a nontrivial extension"
                ),
                "genericity_assumed": False,
                "retired_P3_embedding_used": False,
                "arbitrary_parameter_selected": False,
            },
            "kahler_chamber": {
                "name": "K^s",
                "ambient": "x1>0, x2>0, y>0",
                "definition": (
                    "all nine source sufficient slope polynomials are negative"
                ),
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
            "certified_stable_locus": "P^1(Q(omega)) x K^s",
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
                    self.proper_connected_irreducible_reduction_excluded
                ),
                "genuine_su4_on_certified_locus": (
                    self.genuine_su4_on_certified_locus
                ),
                "argument": (
                    "stable determinant-trivial bundles have irreducible SU(4) "
                    "HYM holonomy; on the simply connected cover the holonomy "
                    "is connected, while a proper connected irreducible "
                    "subgroup would force the odd Chern classes to be torsion"
                ),
            },
            "source_invariant_ext_dimension": 4,
            "lawful_invariant_ext_dimension": 2,
            "dimension_mismatch_affects_stability_implication": False,
            "arbitrary_extension_point_selected": False,
            "first_missing_input": (
                "Wilson-projected matter and Higgs cohomology from the same "
                "lawful mixed chain family"
            ),
            "status": (
                "every lawful nonzero extension is stable and genuinely SU(4) "
                "throughout the certified Kahler chamber"
            ),
        }


def _source_digest(arxiv_id: str, expected: str) -> str:
    """Read one exact source-archive digest from the immutable manifest."""

    payload = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    sources = payload.get("sources")
    if not isinstance(sources, list):
        raise ValueError("the published source manifest lacks source records")
    matches = [
        source
        for source in sources
        if isinstance(source, dict) and source.get("arxiv_id") == arxiv_id
    ]
    if len(matches) != 1 or matches[0].get("source_archive_sha256") != expected:
        raise ValueError(f"source manifest mismatch for {arxiv_id}")
    return cast(str, matches[0]["source_archive_sha256"])


def _universal_digest() -> str:
    """Validate the lawful universal family and return its digest."""

    payload = json.loads(UNIVERSAL_CONE_ARTIFACT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError("the lawful universal cone digest does not verify")
    if (
        payload.get("projective_non_split_space") != "P^1(Q(omega))"
        or payload.get("equivariant_descent_exact") is not True
        or payload.get("local_freeness_locus") != "all A^2(Q(omega))"
        or payload.get("genuine_su4_locus_computed") is not False
    ):
        raise ValueError("the lawful universal cone has not closed its algebraic gates")
    return digest


@cache
def mixed_schoen_outer_stability_locus() -> MixedSchoenOuterStabilityLocus:
    """Construct the exact stable genuine-SU(4) certificate on lawful P1."""

    bundle = visible_bundle(schoen_geometry()).bundle
    inequalities = tuple(
        StabilityPolynomial(line_class, coefficients, anchor_value)
        for line_class, coefficients, anchor_value, _, _ in STABILITY_ROWS
    )
    return MixedSchoenOuterStabilityLocus(
        _universal_digest(),
        _source_digest(STABILITY_ARXIV_ID, STABILITY_SOURCE_SHA256),
        _source_digest(BOUNDS_ARXIV_ID, BOUNDS_SOURCE_SHA256),
        inequalities,
        (Rational(6), Rational(9), Rational(3)),
        Rational(1, 32),
        True,
        True,
        bundle.rank,
        bundle.c1,
        bundle.c3,
        SCHOEN_COVERING_DEGREE,
    )


def write_mixed_schoen_outer_stability_locus(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed lawful stability certificate."""

    payload = mixed_schoen_outer_stability_locus().as_record()
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
    """Regenerate the lawful stable genuine-SU(4) certificate."""

    payload = write_mixed_schoen_outer_stability_locus()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"certified_stable_locus: {payload['certified_stable_locus']}")
    print(
        "genuine_su4: "
        f"{payload['structure_group']['genuine_su4_on_certified_locus']}"
    )
    print(f"first_missing_input: {payload['first_missing_input']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MixedSchoenOuterStabilityLocus",
    "mixed_schoen_outer_stability_locus",
]
