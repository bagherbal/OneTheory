"""Derive the unavoidable slope walls for the pair-73 extension family.

Owns:
    Exact slope polynomials for the universal rank-two subbundle, its Serre
    line subbundle, and the rank-three preimage forced by the right constituent.

Depends on:
    The content-addressed pair-73 algebraic locus, exact constituent
    presentations, and the published quotient intersection tensor.

Must not:
    Identify the positive coordinate sector with the full Kahler cone, infer
    sufficiency from necessary inequalities, select a polarization or extension
    point, or claim slope stability and genuine SU(4) structure.

Phase 0:
    Necessary stability walls are exact; a sufficient chamber remains blocked
    by Kahler-cone membership and unclassified saturated subsheaves.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from onetheory.math.geometry import Divisor
from onetheory.math.numbers import Rational
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .pair_73_lawful_locus import OUTPUT as LAWFUL_ARTIFACT
from .pair_73_lawful_locus import PAIR_INDEX, pair_73_algebraic_locus
from .pair_73_source import OUTPUT as SOURCE_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/pair_73_stability_wall.json"
PUBLISHED_ANCHOR = (Rational(6), Rational(9), Rational(3))


def _variables() -> tuple[Polynomial, Polynomial, Polynomial]:
    """Return the ordered exact polarization coordinates."""

    return cast(
        tuple[Polynomial, Polynomial, Polynomial],
        tuple(
            Polynomial.monomial(
                tuple(int(position == index) for position in range(3)),
                scalar_type=Rational,
            )
            for index in range(3)
        ),
    )


def _slope_polynomial(first_chern: Divisor, rank: int) -> Polynomial:
    """Contract one exact first Chern class with the symbolic polarization."""

    if isinstance(rank, bool) or not isinstance(rank, int) or rank <= 0:
        raise ValueError("a slope polynomial requires positive integral rank")
    geometry = schoen_geometry()
    if first_chern.basis != geometry.basis:
        raise ValueError("the slope class must use the Schoen quotient basis")
    variables = _variables()
    result = Polynomial.zero(3, scalar_type=Rational)
    for first, first_value in enumerate(first_chern.coordinates):
        for second, second_variable in enumerate(variables):
            for third, third_variable in enumerate(variables):
                coefficient = geometry.quotient_intersections.coefficient(
                    first, second, third
                )
                result += (second_variable * third_variable).scale(
                    first_value * coefficient / rank
                )
    return result


def _polynomial_record(polynomial: Polynomial) -> list[dict[str, object]]:
    """Serialize one exact sparse polynomial in the pinned coordinate order."""

    return [
        {"exponents": list(exponents), "coefficient": str(coefficient)}
        for exponents, coefficient in polynomial.terms
    ]


def _serre_line_degree(
    factor: int,
    target_line_shift: int,
    twist: tuple[int, int, int],
) -> tuple[int, int, int]:
    """Derive the pushed-out line summand's exact Schoen divisor degree."""

    if factor not in (1, 2):
        raise ValueError("Schoen constituent factors are indexed by one and two")
    position = factor - 1
    return tuple(
        twist[index] - target_line_shift * int(index == position)
        for index in range(3)
    )


@dataclass(frozen=True, slots=True)
class Pair73StabilityWall:
    """Necessary slope inequalities forced by the pair-73 exact sequences."""

    left_slope: Polynomial
    left_line_slope: Polynomial
    right_preimage_slope: Polynomial
    published_anchor_left_slope: Rational
    published_anchor_left_line_slope: Rational

    def __post_init__(self) -> None:
        x, y, z = _variables()
        common = (y - x) * (x + y + z.scale(6))
        expected_left = common.scale(Rational(1, 3))
        expected_preimage = common.scale(Rational(1, 9))
        expected_line = (
            -(x**2)
            + (x * y).scale(6)
            + (y**2).scale(4)
            - (x * z).scale(6)
            + (y * z).scale(24)
        ).scale(Rational(1, 3))
        if self.left_slope != expected_left:
            raise ValueError("the pair-73 rank-two slope identity failed")
        if self.right_preimage_slope != expected_preimage:
            raise ValueError("the pair-73 rank-three slope identity failed")
        if self.left_line_slope != expected_line:
            raise ValueError("the pair-73 Serre-line slope identity failed")
        if self.published_anchor_left_slope != Rational(33):
            raise ValueError("the published anchor no longer destabilizes pair 73")
        if self.published_anchor_left_line_slope != Rational(384):
            raise ValueError("the Serre line has an unexpected published-anchor slope")

    def as_record(self) -> dict[str, object]:
        """Serialize exact necessary walls without asserting sufficiency."""

        return {
            "schema": "pair-73-necessary-stability-walls-v1",
            "global_pair_index": PAIR_INDEX,
            "polarization_coordinates": ["j1", "j2", "j3"],
            "exact_sequences": [
                "0 -> V_left -> V(a) -> V_right -> 0",
                "0 -> L_left -> V_left -> I_left tensor M_left -> 0",
                "0 -> V_left -> preimage(L_right) -> L_right -> 0",
            ],
            "forced_subobjects": [
                {
                    "name": "V_left",
                    "rank": 2,
                    "c1": ["2", "-2", "0"],
                    "slope": _polynomial_record(self.left_slope),
                    "factorization": "(j2-j1)(j1+j2+6*j3)/3",
                },
                {
                    "name": "L_left",
                    "rank": 1,
                    "c1": ["4", "-1", "0"],
                    "slope": _polynomial_record(self.left_line_slope),
                    "factorization": (
                        "(-j1^2+6*j1*j2+4*j2^2-6*j1*j3+24*j2*j3)/3"
                    ),
                },
                {
                    "name": "preimage(L_right)",
                    "rank": 3,
                    "c1": ["1", "-1", "0"],
                    "slope": _polynomial_record(self.right_preimage_slope),
                    "factorization": "(j2-j1)(j1+j2+6*j3)/9",
                },
            ],
            "necessary_inequalities": [
                "(j2-j1)(j1+j2+6*j3) < 0",
                "-j1^2+6*j1*j2+4*j2^2-6*j1*j3+24*j2*j3 < 0",
            ],
            "positive_coordinate_consequence": {
                "assumption": "j1 > 0, j2 > 0, j3 > 0",
                "rank_two_condition": "j1 > j2",
                "serre_line_condition": (
                    "j1^2-6*j1*j2-4*j2^2+6*j1*j3-24*j2*j3 > 0"
                ),
                "algebraically_nonempty": True,
                "nonemptiness_certificate": (
                    "in the exact family (j1,j2,j3)=(t,1,1), every integer t>=6 "
                    "makes both forced-subobject slopes negative"
                ),
                "full_kahler_cone_membership_proved": False,
            },
            "published_anchor": {
                "coordinates": [str(value) for value in PUBLISHED_ANCHOR],
                "V_left_slope": str(self.published_anchor_left_slope),
                "L_left_slope": str(self.published_anchor_left_line_slope),
                "pair_73_stable_there": False,
            },
            "parameter_dependence": "none; the forced sequences occur over the full family",
            "arbitrary_extension_point_selected": False,
            "arbitrary_polarization_selected": False,
            "necessary_wall_computed": True,
            "sufficient_stability_chamber_computed": False,
            "genuine_su4_locus_computed": False,
            "first_missing_prerequisite": (
                "exact Kahler-cone intersection and exclusion of every other "
                "saturated destabilizing subsheaf"
            ),
            "status": (
                "exact unavoidable slope walls; pair 73 is excluded at the "
                "published anchor, while a sufficient stable chamber remains unresolved"
            ),
        }


def pair_73_stability_wall() -> Pair73StabilityWall:
    """Construct the exact pair-73 necessary stability-wall certificate."""

    stored = json.loads(LAWFUL_ARTIFACT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(stored):
        raise ValueError("pair-73 algebraic-locus artifact digest does not verify")
    lawful = pair_73_algebraic_locus()
    if stored != lawful.as_record():
        raise ValueError("pair-73 algebraic-locus artifact is stale")
    source = json.loads(SOURCE_ARTIFACT.read_text(encoding="utf-8"))
    source_digest = source.pop("artifact_digest", None)
    if not isinstance(source_digest, str) or source_digest != _canonical_digest(source):
        raise ValueError("pair-73 source artifact digest does not verify")
    pair = source.get("pair")
    if not isinstance(pair, dict) or not isinstance(pair.get("topology"), dict):
        raise ValueError("pair-73 source topology is unavailable")
    topology = pair["topology"]
    left_factor = topology.get("left_factor")
    left_shift = topology.get("left_target_line_shift")
    left_twist = topology.get("left_twist")
    right_factor = topology.get("right_factor")
    right_shift = topology.get("right_target_line_shift")
    right_twist = topology.get("right_twist")
    if not (
        isinstance(left_factor, int)
        and isinstance(left_shift, int)
        and isinstance(left_twist, list)
        and all(isinstance(value, int) for value in left_twist)
        and isinstance(right_factor, int)
        and isinstance(right_shift, int)
        and isinstance(right_twist, list)
        and all(isinstance(value, int) for value in right_twist)
    ):
        raise ValueError("pair-73 Serre line data have invalid types")
    left_twist_tuple = tuple(left_twist)
    right_twist_tuple = tuple(right_twist)
    if len(left_twist_tuple) != 3 or len(right_twist_tuple) != 3:
        raise ValueError("pair-73 Serre twists must have three coordinates")

    geometry = schoen_geometry()
    left = geometry.quotient_divisor(lawful.left_first_chern)
    left_line = geometry.quotient_divisor(
        _serre_line_degree(left_factor, left_shift, left_twist_tuple)
    )
    right_line = geometry.quotient_divisor(
        _serre_line_degree(right_factor, right_shift, right_twist_tuple)
    )
    right_preimage = left + right_line
    anchor = geometry.quotient_divisor(PUBLISHED_ANCHOR)
    return Pair73StabilityWall(
        _slope_polynomial(left, 2),
        _slope_polynomial(left_line, 1),
        _slope_polynomial(right_preimage, 3),
        geometry.bundle_slope(left, anchor, 2),
        geometry.bundle_slope(left_line, anchor, 1),
    )


def write_pair_73_stability_wall(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed necessary-wall certificate atomically."""

    payload = pair_73_stability_wall().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact pair-73 necessary stability-wall artifact."""

    payload = write_pair_73_stability_wall()
    anchor = payload["published_anchor"]
    if not isinstance(anchor, dict):
        raise ValueError("pair-73 anchor record is invalid")
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"published_anchor_left_slope: {anchor['V_left_slope']}")
    print(
        "sufficient_stability_chamber_computed: "
        f"{payload['sufficient_stability_chamber_computed']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
