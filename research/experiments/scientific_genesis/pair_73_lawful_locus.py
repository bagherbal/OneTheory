"""Certify the algebraic lawful locus currently implied for pair 73.

Owns:
    Family-wide local freeness, invariant descent, determinant and Chern data,
    and the exact boundary between algebraic closure and genuine SU(4) status.

Depends on:
    The exact pair-73 chain lift, descended rank-two constituent certificates,
    universal Ext split locus, and published quotient intersection tensor.

Must not:
    Infer stability from local freeness, call a reducible or unstable extension
    genuinely SU(4), select a projective extension point, or fit observations.

Phase 0:
    Algebraic family gates are exact; the genuine SU(4) locus remains tied to
    the unresolved stability chamber.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from onetheory.math.geometry import Curve, divisor_square
from onetheory.math.numbers import Rational
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .pair_73_cech_lift import OUTPUT as LIFT_ARTIFACT
from .pair_73_cech_lift import PAIR_INDEX
from .pair_73_source import OUTPUT as SOURCE_ARTIFACT
from .pair_73_universal import OUTPUT as UNIVERSAL_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/pair_73_algebraic_locus.json"
CONSTITUENT_ARTIFACT = ROOT / "data/generated/computable_carrier/computable_carrier_artifact.json"


@dataclass(frozen=True, slots=True)
class Pair73AlgebraicLocus:
    """The exact parameter locus passing currently established algebraic gates."""

    left_first_chern: tuple[Rational, ...]
    right_first_chern: tuple[Rational, ...]
    second_chern: tuple[Rational, ...]
    third_chern_integral: Rational
    constituent_local_freeness_exact: bool
    extension_local_freeness_exact: bool
    invariant_descent_exact: bool
    determinant_trivial: bool
    non_split_locus_exact: bool

    def __post_init__(self) -> None:
        if self.left_first_chern != tuple(-value for value in self.right_first_chern):
            raise ValueError("pair-73 constituent determinants do not cancel")
        if not all(
            (
                self.constituent_local_freeness_exact,
                self.extension_local_freeness_exact,
                self.invariant_descent_exact,
                self.determinant_trivial,
                self.non_split_locus_exact,
            )
        ):
            raise ValueError("pair-73 algebraic family failed an exact gate")

    def as_record(self) -> dict[str, object]:
        """Serialize closure without claiming stability or genuine SU(4)."""

        return {
            "schema": "pair-73-algebraic-lawful-locus-v1",
            "global_pair_index": PAIR_INDEX,
            "parameter_space": "A^4(Q(omega))",
            "automorphism_quotient": "P^3(Q(omega))",
            "split_locus": "the affine origin",
            "non_split_locus": "A^4(Q(omega)) minus the origin",
            "algebraic_lawful_locus": "A^4(Q(omega)) minus the origin",
            "projective_algebraic_lawful_locus": "P^3(Q(omega))",
            "local_freeness_excluded_locus": "empty",
            "descent_excluded_locus": "empty",
            "constituent_local_freeness_exact": self.constituent_local_freeness_exact,
            "extension_local_freeness_exact": self.extension_local_freeness_exact,
            "local_freeness_theorem": (
                "an extension of locally free sheaves is locally free because "
                "the quotient is projective on every local stalk"
            ),
            "invariant_descent_exact": self.invariant_descent_exact,
            "descent_theorem": (
                "for a finite group in characteristic zero, invariants are exact; "
                "invariant Ext classes of linearized constituents are equivariant "
                "extensions and descend along the free quotient"
            ),
            "rank": 4,
            "determinant_trivial": self.determinant_trivial,
            "chern_classes": {
                "c1_left": [str(value) for value in self.left_first_chern],
                "c1_right": [str(value) for value in self.right_first_chern],
                "c1_total": ["0", "0", "0"],
                "c2_total": [str(value) for value in self.second_chern],
                "integral_c3_total": str(self.third_chern_integral),
                "quotient_index": str(self.third_chern_integral / 2),
                "parameter_independent": True,
            },
            "non_split_locus_exact": self.non_split_locus_exact,
            "arbitrary_extension_point_selected": False,
            "genuine_su4_locus_computed": False,
            "genuine_su4_first_missing_input": (
                "exact stability chamber and exclusion of proper structure-group reduction"
            ),
            "status": (
                "exact non-split locally free descended determinant-trivial rank-four "
                "family; genuine SU(4) remains conditional on stability"
            ),
        }


def _pair_constituents() -> tuple[dict[str, object], dict[str, object]]:
    """Return the two exact pair-73 constituent descent certificates."""

    artifact = json.loads(CONSTITUENT_ARTIFACT.read_text(encoding="utf-8"))
    frontier = artifact["tier_a_chain_inputs"]["tier_b_monomial_constituent_descent_frontier"]
    selected = tuple(
        line
        for line in frontier["lines"]
        if line["scheme"] == "B-monomial-coordinate-orbit-1"
        and line["character_pair"] == ["-1-omega", "-1-omega"]
        and line["target_line_shift"] in (-6, 0)
    )
    if len(selected) != 2:
        raise ValueError("pair-73 constituent certificates are not unique")
    by_shift = {line["target_line_shift"]: line for line in selected}
    return by_shift[-6], by_shift[0]


def _curve_product(left, right) -> Curve:
    """Return the exact divisor product from polarization."""

    geometry = schoen_geometry()
    return (
        divisor_square(geometry.quotient_intersections, left + right)
        - divisor_square(geometry.quotient_intersections, left)
        - divisor_square(geometry.quotient_intersections, right)
    ).scale(Rational(1, 2))


def pair_73_algebraic_locus() -> Pair73AlgebraicLocus:
    """Construct the exact family-wide algebraic locus certificate."""

    source = json.loads(SOURCE_ARTIFACT.read_text(encoding="utf-8"))
    source_digest = source.pop("artifact_digest", None)
    if not isinstance(source_digest, str) or source_digest != _canonical_digest(source):
        raise ValueError("pair-73 source artifact digest does not verify")
    lift = json.loads(LIFT_ARTIFACT.read_text(encoding="utf-8"))
    lift_digest = lift.pop("artifact_digest", None)
    if not isinstance(lift_digest, str) or lift_digest != _canonical_digest(lift):
        raise ValueError("pair-73 lift artifact digest does not verify")
    universal = json.loads(UNIVERSAL_ARTIFACT.read_text(encoding="utf-8"))
    universal_digest = universal.pop("artifact_digest", None)
    if not isinstance(universal_digest, str) or universal_digest != _canonical_digest(universal):
        raise ValueError("pair-73 universal artifact digest does not verify")
    left, right = _pair_constituents()
    constituent_exact = all(
        line["locally_free_sheaf_verified"] is True and line["internal_descent_certificate"] is True
        for line in (left, right)
    )

    geometry = schoen_geometry()
    hyperplane = geometry.quotient_divisor((1, 0, 0))
    left_twist = geometry.quotient_divisor((-2, -1, 0))
    right_twist = geometry.quotient_divisor((-1, 1, 0))
    left_untwisted_c1 = hyperplane.scale(left["chern_character"]["c1_hyperplane"])
    right_untwisted_c1 = hyperplane.scale(right["chern_character"]["c1_hyperplane"])
    left_c1 = left_untwisted_c1 + left_twist.scale(2)
    right_c1 = right_untwisted_c1 + right_twist.scale(2)
    left_c2 = (
        divisor_square(geometry.quotient_intersections, hyperplane).scale(6)
        + _curve_product(left_untwisted_c1, left_twist)
        + divisor_square(geometry.quotient_intersections, left_twist)
    )
    right_c2 = (
        divisor_square(geometry.quotient_intersections, hyperplane).scale(6)
        + _curve_product(right_untwisted_c1, right_twist)
        + divisor_square(geometry.quotient_intersections, right_twist)
    )
    total_c2 = left_c2 + right_c2 + _curve_product(left_c1, right_c1)
    raw_index = source["pair"]["topology"]["quotient_index"]
    if raw_index != "-3":
        raise ValueError("pair-73 quotient index no longer equals minus three")
    quotient_index = Rational(-3)
    return Pair73AlgebraicLocus(
        left_c1.coordinates,
        right_c1.coordinates,
        total_c2.coordinates,
        quotient_index * 2,
        constituent_exact,
        constituent_exact and lift["mapping_cone_squared_zero"] is True,
        constituent_exact and source["pair"]["cocycle_basis"]["exact"] is True,
        left_c1 + right_c1 == geometry.quotient_divisor((0, 0, 0)),
        universal["split_locus"]["description"] == "the affine origin only",
    )


def write_pair_73_algebraic_locus(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed algebraic-locus certificate atomically."""

    payload = pair_73_algebraic_locus().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact pair-73 algebraic lawful-locus artifact."""

    payload = write_pair_73_algebraic_locus()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"algebraic_lawful_locus: {payload['algebraic_lawful_locus']}")
    print(f"c2_total: {payload['chern_classes']['c2_total']}")
    print(f"genuine_su4_locus_computed: {payload['genuine_su4_locus_computed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
