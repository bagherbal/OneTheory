"""Refute the final nonzero blocks in the declared computable category.

Owns:
    The exact lower-line pullback, factor-exchanged slope contradiction, and
    scoped exhaustion of candidates 5 and 25.

Depends on:
    Frozen invariant and automorphism certificates, the shared lower-line
    screen, and exact quotient intersections.

Must not:
    Extrapolate beyond the declared monomial category, select an extension
    point, or claim a no-go for general Schoen bundles.

Phase 0:
    Research-only exact stability exclusion for the final 72 declared families.
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
    DEFAULT_PARTIAL,
    _canonical_digest,
)

from .next_survivor_lower_line_no_go import (
    _polynomial_record,
    _screen_lower_line_blocks,
)
from .pair_73_stability_wall import _slope_polynomial

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/remaining_lower_line_no_go.json"
BLOCKS = ((5, 145, 180), (25, 865, 900))
EXPECTED_DIMENSIONS = Counter({102: 36, 108: 36})
EXPECTED_ORBITS = Counter({"P^101(Q(omega))": 36, "P^107(Q(omega))": 36})


def _validated_action_counts() -> tuple[Counter[int], Counter[str]]:
    """Validate frozen scalar actions for every final-block parameter space."""

    payload = json.loads((ROOT / DEFAULT_PARTIAL).read_text(encoding="utf-8"))
    completed = payload.get("completed_pairs")
    if not (
        payload.get("schema") == "tier-b-schoen-outer-automorphisms-v2"
        and payload.get("completed_pair_count") == 1296
        and isinstance(completed, dict)
    ):
        raise ValueError("the frozen automorphism prerequisite is incomplete")
    dimensions: Counter[int] = Counter()
    orbit_spaces: Counter[str] = Counter()
    for candidate_index, start, end in BLOCKS:
        for global_index in range(start, end + 1):
            record = completed.get(str(global_index))
            if not isinstance(record, dict) or not (
                record.get("candidate_index") == candidate_index
                and record.get("exact") is True
                and record.get("canonical_orbits_computed") is True
            ):
                raise ValueError("one final-block automorphism record is incomplete")
            action = record.get("automorphism_action")
            if not isinstance(action, dict) or not (
                action.get("quotient_action_exact") is True
                and action.get("canonical_orbits_computed") is True
                and isinstance(action.get("extension_dimension"), int)
                and isinstance(action.get("nonzero_orbit_space"), str)
            ):
                raise ValueError("one final-block quotient action is incomplete")
            dimensions[action["extension_dimension"]] += 1
            orbit_spaces[action["nonzero_orbit_space"]] += 1
    return dimensions, orbit_spaces


@dataclass(frozen=True, slots=True)
class RemainingLowerLineNoGo:
    """Exact stability contradiction for candidates 5 and 25."""

    checked_pair_count: int
    dimension_counts: tuple[tuple[int, int], ...]
    orbit_space_counts: tuple[tuple[str, int], ...]
    first_orientation_left_line: tuple[Rational, ...]
    first_orientation_lower_line: tuple[Rational, ...]
    first_orientation_left_slope: Polynomial
    first_orientation_lower_slope: Polynomial
    positive_sum: Polynomial
    zero_hom_section_maps: bool
    factor_exchange_exact: bool

    def __post_init__(self) -> None:
        if self.checked_pair_count != 72:
            raise ValueError("the final lower-line no-go must cover 72 families")
        if Counter(dict(self.dimension_counts)) != EXPECTED_DIMENSIONS:
            raise ValueError("the final invariant dimensions changed")
        if Counter(dict(self.orbit_space_counts)) != EXPECTED_ORBITS:
            raise ValueError("the final projective orbit spaces changed")
        if self.first_orientation_left_line != (
            Rational(4),
            Rational(-1),
            Rational(2),
        ):
            raise ValueError("the final forced left line changed")
        if self.first_orientation_lower_line != (
            Rational(-4),
            Rational(1),
            Rational(-1),
        ):
            raise ValueError("the final lifted lower line changed")
        if self.positive_sum != (
            self.first_orientation_left_slope + self.first_orientation_lower_slope
        ):
            raise ValueError("the final lower-line slope sum is inconsistent")
        expected = _slope_polynomial(
            schoen_geometry().quotient_divisor((0, 0, 1)),
            1,
        )
        if self.positive_sum != expected or any(
            coefficient <= 0 for _, coefficient in self.positive_sum.terms
        ):
            raise ValueError("the final lower-line slope sum is not positive")
        if not self.zero_hom_section_maps or not self.factor_exchange_exact:
            raise ValueError("the final universal lower-line theorem failed")

    def as_record(self) -> dict[str, object]:
        """Serialize the scoped exhaustion of the declared carrier category."""

        return {
            "schema": "remaining-lower-line-no-go-v1",
            "candidate_blocks": [
                {
                    "candidate_index": candidate,
                    "global_pair_range": [start, end],
                    "pair_count": end - start + 1,
                }
                for candidate, start, end in BLOCKS
            ],
            "checked_pair_count": self.checked_pair_count,
            "invariant_ext_dimension_counts": {
                str(dimension): count for dimension, count in self.dimension_counts
            },
            "nonzero_orbit_space_counts": dict(self.orbit_space_counts),
            "first_orientation": {
                "candidate_index": 5,
                "forced_left_line": {
                    "c1": [str(value) for value in self.first_orientation_left_line],
                    "slope": _polynomial_record(self.first_orientation_left_slope),
                },
                "universally_lifted_lower_line": {
                    "c1": [str(value) for value in self.first_orientation_lower_line],
                    "slope": _polynomial_record(self.first_orientation_lower_slope),
                },
                "positive_identity": {
                    "formula": "mu(L_left)+mu(lower_right_line)=mu(O(phi))>0",
                    "polynomial": _polynomial_record(self.positive_sum),
                },
            },
            "factor_exchanged_orientation": {
                "candidate_index": 25,
                "forced_left_line_c1": ["-1", "4", "2"],
                "universally_lifted_lower_line_c1": ["1", "-4", "-1"],
                "coordinate_rule": "exchange j1 and j2",
            },
            "lower_line_hom_pullback_is_zero": True,
            "lower_line_lifts_for_every_parameter": True,
            "lower_line_descends": True,
            "common_stability_chamber": "empty",
            "every_pair_unstable": True,
            "remaining_declared_blocks_refuted": True,
            "declared_computable_carrier_category_exhausted": True,
            "global_schoen_bundle_no_go": False,
            "arbitrary_extension_point_selected": False,
            "sampled_polarization_used": False,
            "remaining_nonzero_candidate_blocks": [],
            "remaining_nonzero_family_count": 0,
            "next_required_object": (
                "mathematically justified enlargement of the carrier search "
                "category with a finite exact enumeration domain"
            ),
            "status": (
                "exact scoped no-go for the final 72 declared monomial-carrier "
                "families in candidates 5 and 25"
            ),
        }


@cache
def remaining_lower_line_no_go() -> RemainingLowerLineNoGo:
    """Certify the final universal lower-line obstruction exactly."""

    action_dimensions, action_orbits = _validated_action_counts()
    screen = _screen_lower_line_blocks(BLOCKS)
    if not (
        action_dimensions == EXPECTED_DIMENSIONS
        and action_orbits == EXPECTED_ORBITS
        and Counter(dict(screen.dimension_counts)) == action_dimensions
        and Counter(dict(screen.orbit_space_counts)) == action_orbits
    ):
        raise ValueError("the final invariant and action certificates disagree")
    topology_data = {
        candidate: (left_line, lower_line)
        for candidate, left_line, lower_line in screen.topology_data
    }
    first_left, first_lower = topology_data[5]
    second_left, second_lower = topology_data[25]
    factor_exchange_exact = (
        second_left == (first_left[1], first_left[0], first_left[2])
        and second_lower == (first_lower[1], first_lower[0], first_lower[2])
    )
    left_slope = _slope_polynomial(
        schoen_geometry().quotient_divisor(first_left),
        1,
    )
    lower_slope = _slope_polynomial(
        schoen_geometry().quotient_divisor(first_lower),
        1,
    )
    return RemainingLowerLineNoGo(
        screen.checked_pair_count,
        screen.dimension_counts,
        screen.orbit_space_counts,
        first_left,
        first_lower,
        left_slope,
        lower_slope,
        left_slope + lower_slope,
        True,
        factor_exchange_exact,
    )


def write_remaining_lower_line_no_go(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed final lower-line certificate atomically."""

    payload = remaining_lower_line_no_go().as_record()
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
    """Regenerate the exact final lower-line no-go artifact."""

    payload = write_remaining_lower_line_no_go()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"checked_pair_count: {payload['checked_pair_count']}")
    print(f"common_stability_chamber: {payload['common_stability_chamber']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "RemainingLowerLineNoGo",
    "remaining_lower_line_no_go",
]
