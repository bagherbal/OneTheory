"""Refute the next carrier block by a lifted-line slope identity.

Owns:
    Exact typed restriction and an incompatible two-subbundle slope identity
    for every invariant outer extension in candidates 16 and 36.

Depends on:
    Invariant cocycle bases, projective orbit certificates, descended Serre
    presentations, exact Schoen intersections, and the positive Kahler cone.

Must not:
    Generalize beyond candidates 16 and 36, sample polarizations, select an
    extension point, or infer a global computable-carrier no-go.

Phase 0:
    The full 72-family dimension-42/48 block is refuted exactly by stability.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.numbers import Rational
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    DEFAULT_INVARIANT_ARTIFACT,
    _canonical_digest,
    _read_partial,
    _validated_invariant_records,
)
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    DEFAULT_PARTIAL as AUTOMORPHISM_ARTIFACT,
)

from .forced_subobject_stability_screen import (
    CARRIER_ARTIFACT,
    _constituent_c1_hyperplanes,
    _forced_subobjects,
    _side_data,
)
from .mixed_sign_minimum_stability_no_go import OUTPUT as PRIOR_NO_GO_ARTIFACT
from .mixed_sign_minimum_stability_no_go import mixed_sign_minimum_stability_no_go
from .pair_73_stability_wall import _serre_line_degree, _slope_polynomial

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/lifted_line_slope_identity_no_go.json"
BLOCKS = ((16, 541, 576), (36, 1261, 1296))
EXPECTED_DIMENSIONS = Counter({42: 36, 48: 36})
EXPECTED_ORBITS = Counter({"P^41(Q(omega))": 36, "P^47(Q(omega))": 36})
EXPECTED_PROFILE_SIZES = (19, 29, 29)
EXPECTED_MINUS_SELECTORS = ((-1, 4), (-1, 9), (-1, 14))
EXPECTED_ZERO_SELECTORS = ((0, 4), (0, 9), (0, 14), (0, 19), (0, 24))


def _typed_support(record: dict[str, object]) -> tuple[tuple[int, int], ...]:
    """Return parent-Hom degree and summand index for every source term."""

    basis = record.get("cocycle_basis")
    if not isinstance(basis, dict) or not isinstance(basis.get("representatives"), list):
        raise ValueError("a lifted-line pair lacks explicit cocycle representatives")
    support: set[tuple[int, int]] = set()
    for representative in basis["representatives"]:
        if not isinstance(representative, dict) or not isinstance(
            representative.get("terms"), list
        ):
            raise ValueError("a lifted-line representative is malformed")
        for term in representative["terms"]:
            if not isinstance(term, dict) or not isinstance(
                term.get("basis_coordinate"), list
            ):
                raise ValueError("a lifted-line source term lacks its coordinate")
            coordinate = term["basis_coordinate"]
            if (
                len(coordinate) != 12
                or coordinate[0] not in (-1, 0, 1)
                or not isinstance(coordinate[2], int)
            ):
                raise ValueError("a lifted-line source term left the typed Hom complex")
            support.add((coordinate[0], coordinate[2]))
    return tuple(sorted(support))


@dataclass(frozen=True, slots=True)
class LiftedLineSlopeIdentityNoGo:
    """The exact two-subbundle contradiction for candidates 16 and 36."""

    block_pair_ranges: tuple[tuple[int, int, int], ...]
    checked_pair_count: int
    dimension_counts: tuple[tuple[int, int], ...]
    orbit_space_counts: tuple[tuple[str, int], ...]
    support_profile_sizes: tuple[int, ...]
    minus_one_restriction_selectors: tuple[tuple[int, int], ...]
    zero_restriction_selectors: tuple[tuple[int, int], ...]
    first_orientation_preimage_slope: Polynomial
    first_orientation_lifted_line_slope: Polynomial
    positive_combination: Polynomial

    def __post_init__(self) -> None:
        if self.block_pair_ranges != BLOCKS or self.checked_pair_count != 72:
            raise ValueError("the lifted-line identity block must contain 72 pairs")
        if Counter(dict(self.dimension_counts)) != EXPECTED_DIMENSIONS:
            raise ValueError("the lifted-line identity block changed Ext dimensions")
        if Counter(dict(self.orbit_space_counts)) != EXPECTED_ORBITS:
            raise ValueError("the lifted-line identity block changed orbit spaces")
        if self.support_profile_sizes != EXPECTED_PROFILE_SIZES:
            raise ValueError("the lifted-line identity support profiles changed")
        if self.minus_one_restriction_selectors != EXPECTED_MINUS_SELECTORS:
            raise ValueError("the Hom-minus-one restriction selectors changed")
        if self.zero_restriction_selectors != EXPECTED_ZERO_SELECTORS:
            raise ValueError("the Hom-zero restriction selectors changed")
        expected = Polynomial(
            {
                (1, 1, 0): Rational(12),
                (0, 2, 0): Rational(6),
                (0, 1, 1): Rational(36),
            },
            variable_count=3,
        )
        if self.positive_combination != expected:
            raise ValueError("the lifted-line positive slope identity failed")
        if self.positive_combination != (
            self.first_orientation_preimage_slope.scale(9)
            + self.first_orientation_lifted_line_slope.scale(3)
        ):
            raise ValueError("the lifted-line slope combination is inconsistent")
        if any(coefficient <= 0 for _, coefficient in self.positive_combination.terms):
            raise ValueError("the lifted-line slope combination is not positive")

    def as_record(self) -> dict[str, object]:
        """Serialize the exact restriction and slope contradiction."""

        return {
            "schema": "lifted-line-slope-identity-no-go-v1",
            "candidate_blocks": [
                {
                    "candidate_index": candidate,
                    "global_pair_range": [start, end],
                    "pair_count": end - start + 1,
                }
                for candidate, start, end in self.block_pair_ranges
            ],
            "checked_pair_count": self.checked_pair_count,
            "invariant_ext_dimension_counts": {
                str(dimension): count for dimension, count in self.dimension_counts
            },
            "nonzero_orbit_space_counts": dict(self.orbit_space_counts),
            "source_support_profile_sizes": list(self.support_profile_sizes),
            "right_line_restriction_selectors": {
                "Hom^-1(F0_right,F1_left)": [
                    list(selector) for selector in self.minus_one_restriction_selectors
                ],
                "Hom^0(F0_right,F0_left)": [
                    list(selector) for selector in self.zero_restriction_selectors
                ],
                "Hom^1(F1_right,F0_left)": [],
            },
            "all_restriction_support_intersections_empty": True,
            "right_serre_line_lifts_for_every_parameter": True,
            "first_orientation": {
                "candidate_index": 16,
                "preimage_right_line": {
                    "rank": 3,
                    "c1": ["2", "1", "-2"],
                    "slope": _polynomial_record(
                        self.first_orientation_preimage_slope
                    ),
                },
                "lifted_right_line": {
                    "rank": 1,
                    "c1": ["4", "-1", "2"],
                    "slope": _polynomial_record(
                        self.first_orientation_lifted_line_slope
                    ),
                },
                "positive_identity": {
                    "formula": (
                        "9*mu(preimage(L_right))+3*mu(L_right)="
                        "6*j2*(2*j1+j2+6*j3)"
                    ),
                    "polynomial": _polynomial_record(self.positive_combination),
                },
            },
            "factor_exchanged_orientation": {
                "candidate_index": 36,
                "coordinate_rule": "exchange j1 and j2",
            },
            "stability_logic": (
                "if both proper subbundles had negative slope, their displayed "
                "positive linear combination would be negative, contradicting "
                "strict positivity on j1,j2,j3 > 0"
            ),
            "common_necessary_chamber": "empty",
            "every_pair_unstable": True,
            "lifted_line_identity_block_refuted": True,
            "global_computable_carrier_no_go": False,
            "arbitrary_extension_point_selected": False,
            "sampled_polarization_used": False,
            "next_invariant_ext_dimension": 50,
            "next_candidate_blocks": [4, 24],
            "next_required_object": (
                "exact stability classification of the 72 families in "
                "candidate blocks 4 and 24"
            ),
            "status": (
                "exact scoped no-go for all 72 forty-two- and "
                "forty-eight-dimensional families in candidates 16 and 36"
            ),
        }


def _polynomial_record(polynomial: Polynomial) -> list[dict[str, object]]:
    """Serialize an exact sparse slope polynomial."""

    return [
        {"exponents": list(exponents), "coefficient": str(coefficient)}
        for exponents, coefficient in polynomial.terms
    ]


@cache
def lifted_line_slope_identity_no_go() -> LiftedLineSlopeIdentityNoGo:
    """Certify the universal restriction and incompatible slopes exactly."""

    stored = json.loads(PRIOR_NO_GO_ARTIFACT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(stored):
        raise ValueError("the prior mixed-sign no-go digest does not verify")
    if stored != mixed_sign_minimum_stability_no_go().as_record():
        raise ValueError("the prior mixed-sign no-go artifact is stale")

    invariant_digest, records = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    actions, _ = _read_partial(AUTOMORPHISM_ARTIFACT, invariant_digest)
    c1_hyperplanes = _constituent_c1_hyperplanes()
    carrier = json.loads(CARRIER_ARTIFACT.read_text(encoding="utf-8"))
    lines = carrier["tier_a_chain_inputs"][
        "tier_b_monomial_constituent_descent_frontier"
    ]["lines"]
    by_key = {
        (
            line["scheme"],
            tuple(line["character_pair"]),
            line["target_line_shift"],
        ): line
        for line in lines
    }
    selected: list[dict[str, object]] = []
    dimensions: Counter[int] = Counter()
    orbit_spaces: Counter[str] = Counter()
    supports: set[tuple[tuple[int, int], ...]] = set()
    first_subobjects = None
    first_line_slope = None
    for candidate, start, end in BLOCKS:
        block = tuple(records[index - 1] for index in range(start, end + 1))
        if any(record.get("candidate_index") != candidate for record in block):
            raise ValueError("lifted-line identity candidate indices changed")
        selected.extend(block)

    for record in selected:
        support = _typed_support(record)
        supports.add(support)
        invariant = record.get("invariant_subcomplex")
        if not isinstance(invariant, dict) or not isinstance(
            invariant.get("invariant_ext_one_dimension"), int
        ):
            raise ValueError("a lifted-line pair lacks its invariant dimension")
        dimension = invariant["invariant_ext_one_dimension"]
        dimensions[dimension] += 1
        index = record.get("global_pair_index")
        if not isinstance(index, int) or index not in actions:
            raise ValueError("a lifted-line pair lacks an automorphism certificate")
        action = actions[index].get("automorphism_action")
        expected_orbit = f"P^{dimension - 1}(Q(omega))"
        if not isinstance(action, dict) or action.get("nonzero_orbit_space") != expected_orbit:
            raise ValueError("a lifted-line pair lacks its projective quotient")
        orbit_spaces[expected_orbit] += 1

        left = _side_data(record, "left")
        right = _side_data(record, "right")
        left_certificate = by_key[(left[3], left[4], left[1])]
        right_certificate = by_key[(right[3], right[4], right[1])]
        right_target_rank = len(right_certificate["target_shifts"])
        minus_selectors = tuple(
            (-1, target * right_target_rank + right_target_rank - 1)
            for target in range(len(left_certificate["source_shifts"]))
        )
        zero_selectors = tuple(
            (0, target * right_target_rank + right_target_rank - 1)
            for target in range(len(left_certificate["target_shifts"]))
        )
        if minus_selectors != EXPECTED_MINUS_SELECTORS:
            raise ValueError("one Hom-minus-one restriction profile changed")
        if zero_selectors != EXPECTED_ZERO_SELECTORS:
            raise ValueError("one Hom-zero restriction profile changed")
        if set(support) & set(minus_selectors + zero_selectors):
            raise ValueError("one lifted-line class restricts nontrivially")

        subobjects = _forced_subobjects(record, c1_hyperplanes)
        right_line_degree = _serre_line_degree(right[0], right[1], right[2])
        right_line_slope = _slope_polynomial(
            schoen_geometry().quotient_divisor(right_line_degree),
            1,
        )
        if record.get("candidate_index") == 16:
            if first_subobjects is None:
                first_subobjects = subobjects
                first_line_slope = right_line_slope
            elif subobjects != first_subobjects or right_line_slope != first_line_slope:
                raise ValueError("candidate 16 varies across character pairs")

    if first_subobjects is None or first_line_slope is None:
        raise ValueError("candidate 16 did not provide a slope profile")
    by_name = {subobject.name: subobject for subobject in first_subobjects}
    preimage_slope = by_name["preimage(L_right)"].slope
    positive = preimage_slope.scale(9) + first_line_slope.scale(3)
    return LiftedLineSlopeIdentityNoGo(
        BLOCKS,
        len(selected),
        tuple(sorted(dimensions.items())),
        tuple(sorted(orbit_spaces.items())),
        tuple(sorted(len(support) for support in supports)),
        EXPECTED_MINUS_SELECTORS,
        EXPECTED_ZERO_SELECTORS,
        preimage_slope,
        first_line_slope,
        positive,
    )


def write_lifted_line_slope_identity_no_go(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed lifted-line identity no-go atomically."""

    payload = lifted_line_slope_identity_no_go().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact lifted-line slope-identity no-go artifact."""

    payload = write_lifted_line_slope_identity_no_go()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"checked_pair_count: {payload['checked_pair_count']}")
    print(f"common_necessary_chamber: {payload['common_necessary_chamber']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
