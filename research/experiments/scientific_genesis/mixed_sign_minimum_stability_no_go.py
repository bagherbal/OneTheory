"""Refute the mixed-sign minimum through the lifted right Serre line.

Owns:
    Exact chain-level right-line restriction and positive-slope exclusion for
    every invariant outer extension in candidates 15 and 35.

Depends on:
    The certified necessary chamber, invariant cocycle bases, exact projective
    orbits, descended constituent presentations, and Schoen intersections.

Must not:
    Generalize beyond candidates 15 and 35, select an extension parameter or
    polarization, or call this scoped result a global carrier no-go.

Phase 0:
    The full 72-family mixed-sign minimum is refuted exactly by slope stability.
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
    _side_data,
)
from .mixed_sign_minimum_chamber import OUTPUT as CHAMBER_ARTIFACT
from .mixed_sign_minimum_chamber import mixed_sign_minimum_chamber
from .pair_73_stability_wall import _serre_line_degree, _slope_polynomial

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_sign_minimum_stability_no_go.json"
BLOCKS = ((15, 505, 540), (35, 1225, 1260))
EXPECTED_DIMENSIONS = Counter({18: 36, 24: 36})
EXPECTED_ORBITS = Counter({"P^17(Q(omega))": 36, "P^23(Q(omega))": 36})
RIGHT_LINE_RESTRICTION = (4, 9, 14)
EXPECTED_SUPPORTS = (
    (0, 1, 3, 5, 6, 8, 10, 11, 13),
    (0, 2, 3, 5, 7, 8, 10, 12, 13),
    (0, 1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13),
)


def _minus_one_support(record: dict[str, object]) -> tuple[int, ...]:
    """Return exact parent-Hom support from every invariant cocycle basis."""

    basis = record.get("cocycle_basis")
    if not isinstance(basis, dict) or not isinstance(basis.get("representatives"), list):
        raise ValueError("a mixed-sign pair lacks explicit cocycle representatives")
    support: set[int] = set()
    for representative in basis["representatives"]:
        if not isinstance(representative, dict) or not isinstance(
            representative.get("terms"), list
        ):
            raise ValueError("a mixed-sign cocycle representative is malformed")
        for term in representative["terms"]:
            if not isinstance(term, dict) or not isinstance(
                term.get("basis_coordinate"), list
            ):
                raise ValueError("a mixed-sign cocycle term lacks its coordinate")
            coordinate = term["basis_coordinate"]
            if (
                len(coordinate) != 12
                or coordinate[0] != -1
                or not isinstance(coordinate[2], int)
            ):
                raise ValueError("mixed-sign support left Hom(F0_right,F1_left)")
            support.add(coordinate[2])
    return tuple(sorted(support))


@dataclass(frozen=True, slots=True)
class MixedSignMinimumStabilityNoGo:
    """The exact universal lifted-line obstruction for candidates 15 and 35."""

    block_pair_ranges: tuple[tuple[int, int, int], ...]
    checked_pair_count: int
    dimension_counts: tuple[tuple[int, int], ...]
    orbit_space_counts: tuple[tuple[str, int], ...]
    support_profiles: tuple[tuple[int, ...], ...]
    right_line_restriction_indices: tuple[int, ...]
    first_orientation_right_line_c1: tuple[Rational, ...]
    first_orientation_right_line_slope: Polynomial

    def __post_init__(self) -> None:
        if self.block_pair_ranges != BLOCKS or self.checked_pair_count != 72:
            raise ValueError("the mixed-sign no-go must contain 72 pairs")
        if Counter(dict(self.dimension_counts)) != EXPECTED_DIMENSIONS:
            raise ValueError("the mixed-sign no-go changed Ext dimensions")
        if Counter(dict(self.orbit_space_counts)) != EXPECTED_ORBITS:
            raise ValueError("the mixed-sign no-go changed projective orbits")
        if self.support_profiles != EXPECTED_SUPPORTS:
            raise ValueError("the mixed-sign Hom support profiles changed")
        if self.right_line_restriction_indices != RIGHT_LINE_RESTRICTION:
            raise ValueError("the mixed-sign right-line restriction columns changed")
        if any(
            set(profile) & set(self.right_line_restriction_indices)
            for profile in self.support_profiles
        ):
            raise ValueError("a mixed-sign Ext class restricts to the right line")
        if self.first_orientation_right_line_c1 != (
            Rational(5),
            Rational(1),
            Rational(-2),
        ):
            raise ValueError("the mixed-sign right Serre line Chern class changed")
        expected = Polynomial(
            {
                (2, 0, 0): Rational(1, 3),
                (1, 0, 1): Rational(2),
                (0, 2, 0): Rational(5, 3),
                (0, 1, 1): Rational(10),
            },
            variable_count=3,
        )
        if self.first_orientation_right_line_slope != expected:
            raise ValueError("the mixed-sign lifted-line slope identity failed")
        if any(
            coefficient <= 0
            for _, coefficient in self.first_orientation_right_line_slope.terms
        ):
            raise ValueError("the mixed-sign lifted line is not coefficient-positive")

    def as_record(self) -> dict[str, object]:
        """Serialize the scoped family-wide no-go theorem."""

        return {
            "schema": "mixed-sign-minimum-stability-no-go-v1",
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
            "source_parent_hom_degree": -1,
            "source_parent_hom_type": "Hom(F0_right,F1_left)",
            "source_hom_support_profiles": [
                list(profile) for profile in self.support_profiles
            ],
            "right_line_generator_index": 4,
            "right_line_restriction_indices": list(
                self.right_line_restriction_indices
            ),
            "all_restriction_support_intersections_empty": True,
            "restriction_chain_argument": (
                "precomposition with L_right -> F0_right selects Hom^-1 "
                "indices 4,9,14, absent from every source basis; the structural "
                "differential and Cech contraction preserve precomposition"
            ),
            "pullback_extension_splits_for_every_parameter": True,
            "right_serre_line_lifts_for_every_parameter": True,
            "first_orientation_right_line_c1": [
                str(value) for value in self.first_orientation_right_line_c1
            ],
            "factor_exchanged_right_line_c1": ["1", "5", "-2"],
            "first_orientation_right_line_slope": [
                {"exponents": list(exponents), "coefficient": str(coefficient)}
                for exponents, coefficient in self.first_orientation_right_line_slope.terms
            ],
            "factor_exchanged_slope_rule": "exchange j1 and j2",
            "strictly_positive_on_kahler_cone": True,
            "necessary_forced_chamber_was_not_sufficient": True,
            "every_pair_unstable": True,
            "mixed_sign_minimum_refuted": True,
            "global_computable_carrier_no_go": False,
            "arbitrary_extension_point_selected": False,
            "sampled_polarization_used": False,
            "next_invariant_ext_dimension": 42,
            "next_candidate_blocks": [16, 36],
            "next_required_object": (
                "exact stability classification of the 72 families in "
                "candidate blocks 16 and 36"
            ),
            "status": (
                "exact scoped no-go for all 72 eighteen- and "
                "twenty-four-dimensional families in candidates 15 and 35"
            ),
        }


@cache
def mixed_sign_minimum_stability_no_go() -> MixedSignMinimumStabilityNoGo:
    """Certify vanishing restriction and positive lifted-line slope exactly."""

    stored = json.loads(CHAMBER_ARTIFACT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(stored):
        raise ValueError("the mixed-sign chamber digest does not verify")
    if stored != mixed_sign_minimum_chamber().as_record():
        raise ValueError("the mixed-sign chamber artifact is stale")

    invariant_digest, records = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    actions, _ = _read_partial(AUTOMORPHISM_ARTIFACT, invariant_digest)
    certificates = _constituent_c1_hyperplanes()
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
    supports: set[tuple[int, ...]] = set()
    dimensions: Counter[int] = Counter()
    orbit_spaces: Counter[str] = Counter()
    restriction_profiles: set[tuple[int, ...]] = set()
    line_degrees: list[tuple[int, int, int]] = []
    for candidate, start, end in BLOCKS:
        block = tuple(records[index - 1] for index in range(start, end + 1))
        if any(record.get("candidate_index") != candidate for record in block):
            raise ValueError("mixed-sign no-go candidate indices changed")
        selected.extend(block)

    for record in selected:
        support = _minus_one_support(record)
        supports.add(support)
        invariant = record.get("invariant_subcomplex")
        if not isinstance(invariant, dict) or not isinstance(
            invariant.get("invariant_ext_one_dimension"), int
        ):
            raise ValueError("a mixed-sign pair lacks its invariant dimension")
        dimension = invariant["invariant_ext_one_dimension"]
        dimensions[dimension] += 1
        index = record.get("global_pair_index")
        if not isinstance(index, int) or index not in actions:
            raise ValueError("a mixed-sign pair lacks an automorphism certificate")
        action = actions[index].get("automorphism_action")
        expected_orbit = f"P^{dimension - 1}(Q(omega))"
        if not isinstance(action, dict) or action.get("nonzero_orbit_space") != expected_orbit:
            raise ValueError("a mixed-sign pair lacks its exact projective quotient")
        orbit_spaces[expected_orbit] += 1

        left = _side_data(record, "left")
        right = _side_data(record, "right")
        left_key = (left[3], left[4], left[1])
        right_key = (right[3], right[4], right[1])
        if left_key not in certificates or right_key not in certificates:
            raise ValueError("a mixed-sign pair lacks descended constituents")
        left_certificate = by_key[left_key]
        right_certificate = by_key[right_key]
        right_target_rank = len(right_certificate["target_shifts"])
        left_source_rank = len(left_certificate["source_shifts"])
        restriction = tuple(
            target * right_target_rank + right_target_rank - 1
            for target in range(left_source_rank)
        )
        restriction_profiles.add(restriction)
        if set(support) & set(restriction):
            raise ValueError("a mixed-sign class restricts nontrivially to its right line")
        line_degrees.append(_serre_line_degree(right[0], right[1], right[2]))

    if restriction_profiles != {RIGHT_LINE_RESTRICTION}:
        raise ValueError("mixed-sign presentation ranks changed")
    if set(line_degrees) != {(5, 1, -2), (1, 5, -2)}:
        raise ValueError("mixed-sign right-line factor orientations changed")
    first_c1 = tuple(Rational(value) for value in (5, 1, -2))
    first_slope = _slope_polynomial(
        schoen_geometry().quotient_divisor(first_c1),
        1,
    )
    return MixedSignMinimumStabilityNoGo(
        BLOCKS,
        len(selected),
        tuple(sorted(dimensions.items())),
        tuple(sorted(orbit_spaces.items())),
        tuple(sorted(supports, key=lambda profile: (len(profile), profile))),
        RIGHT_LINE_RESTRICTION,
        first_c1,
        first_slope,
    )


def write_mixed_sign_minimum_stability_no_go(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed mixed-sign no-go atomically."""

    payload = mixed_sign_minimum_stability_no_go().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact mixed-sign minimum no-go artifact."""

    payload = write_mixed_sign_minimum_stability_no_go()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"checked_pair_count: {payload['checked_pair_count']}")
    print(f"mixed_sign_minimum_refuted: {payload['mixed_sign_minimum_refuted']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
