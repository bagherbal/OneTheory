"""Refute the dimension-50/52 block by a universally lifted lower line.

Owns:
    The exact lower-line section, its zero pullback on outer Ext, and the
    incompatible slope identity for candidates 4 and 24.

Depends on:
    Sparse Schoen line-Hom complexes, the rank-20 Serre restriction, the
    maximal-generator stratification, and exact quotient intersections.

Must not:
    Extrapolate beyond candidates 4 and 24, infer vanishing from support alone,
    select an extension point, or claim a global Schoen-carrier no-go.

Phase 0:
    The full 72-family dimension-50/52 block is refuted exactly by stability.
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
    _validated_invariant_records,
)
from research.experiments.computable_carrier.schoen_sparse_outer import (
    sparse_line_bundle,
    sparse_outer_hom,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_full import (
    _clear_worker_caches,
    declared_schoen_outer_pairs,
)

from .forced_subobject_stability_screen import (
    _constituent_c1_hyperplanes,
    _forced_subobjects,
    _side_data,
)
from .lower_line_sections import (
    SECTION_DEGREES,
    lower_line_hom_section_map,
    lower_line_section_components,
    sparse_line_hom_complex,
)
from .next_survivor_generator_restrictions import (
    OUTPUT as GENERATOR_ARTIFACT,
)
from .next_survivor_restriction import OUTPUT as RESTRICTION_ARTIFACT
from .pair_73_stability_wall import _serre_line_degree, _slope_polynomial

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/next_survivor_lower_line_no_go.json"
BLOCKS = ((4, 109, 144), (24, 829, 864))
EXPECTED_DIMENSIONS = Counter({50: 36, 52: 36})
EXPECTED_ORBITS = Counter({"P^49(Q(omega))": 36, "P^51(Q(omega))": 36})
EXPECTED_GENERATOR_RANKS = {"36": 36, "38": 36, "40": 216}


def _verified_artifact(path: Path, schema: str) -> dict[str, object]:
    """Read one content-addressed exact prerequisite artifact."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"the prerequisite {schema} digest does not verify")
    if payload.get("schema") != schema:
        raise ValueError(f"the prerequisite {schema} has the wrong schema")
    return payload


def _line_subtract(
    line: tuple[int, int, int],
    section: tuple[int, int, int],
) -> tuple[int, int, int]:
    """Return the domain line of a section into ``line``."""

    return tuple(
        value - shift
        for value, shift in zip(line, section, strict=True)
    )


@dataclass(frozen=True, slots=True)
class NextSurvivorLowerLineNoGo:
    """The exact lower-line stability contradiction for candidates 4 and 24."""

    checked_pair_count: int
    dimension_counts: tuple[tuple[int, int], ...]
    orbit_space_counts: tuple[tuple[str, int], ...]
    section_degree: tuple[int, int, int]
    section_h0_dimension: int
    first_orientation_left_line: tuple[Rational, ...]
    first_orientation_lower_line: tuple[Rational, ...]
    first_orientation_left_slope: Polynomial
    first_orientation_lower_slope: Polynomial
    positive_sum: Polynomial
    zero_hom_section_maps: bool
    factor_exchange_exact: bool

    def __post_init__(self) -> None:
        if self.checked_pair_count != 72:
            raise ValueError("the lower-line no-go must cover 72 families")
        if Counter(dict(self.dimension_counts)) != EXPECTED_DIMENSIONS:
            raise ValueError("the lower-line no-go dimensions changed")
        if Counter(dict(self.orbit_space_counts)) != EXPECTED_ORBITS:
            raise ValueError("the lower-line no-go orbit spaces changed")
        if self.section_degree != SECTION_DEGREES[1] or self.section_h0_dimension != 1:
            raise ValueError("the lower-line section is no longer unique")
        if self.first_orientation_left_line != (
            Rational(4),
            Rational(-1),
            Rational(1),
        ):
            raise ValueError("the forced left line changed")
        if self.first_orientation_lower_line != (
            Rational(-4),
            Rational(1),
            Rational(0),
        ):
            raise ValueError("the lifted lower line changed")
        if self.positive_sum != (
            self.first_orientation_left_slope + self.first_orientation_lower_slope
        ):
            raise ValueError("the lower-line slope sum is inconsistent")
        expected = _slope_polynomial(
            schoen_geometry().quotient_divisor((0, 0, 1)),
            1,
        )
        if self.positive_sum != expected or any(
            coefficient <= 0 for _, coefficient in self.positive_sum.terms
        ):
            raise ValueError("the lower-line slope sum is not strictly positive")
        if not self.zero_hom_section_maps or not self.factor_exchange_exact:
            raise ValueError("the universal lower-line lifting theorem failed")

    def as_record(self) -> dict[str, object]:
        """Serialize the universal lower-line no-go and next carrier frontier."""

        return {
            "schema": "next-survivor-lower-line-no-go-v1",
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
            "lower_line_section": {
                "degree": list(self.section_degree),
                "h0_dimension": self.section_h0_dimension,
                "canonical_koszul_representative": (
                    "k1_x tensor H^1(P1,O(-2)) generator"
                ),
                "line_complex_chain_map_exact": True,
            },
            "first_orientation": {
                "candidate_index": 4,
                "forced_left_line": {
                    "c1": [str(value) for value in self.first_orientation_left_line],
                    "slope": _polynomial_record(
                        self.first_orientation_left_slope
                    ),
                },
                "universally_lifted_lower_line": {
                    "c1": [str(value) for value in self.first_orientation_lower_line],
                    "slope": _polynomial_record(
                        self.first_orientation_lower_slope
                    ),
                },
                "positive_identity": {
                    "formula": (
                        "mu(L_left)+mu(lower_right_line)=mu(O(phi))>0"
                    ),
                    "polynomial": _polynomial_record(self.positive_sum),
                },
            },
            "factor_exchanged_orientation": {
                "candidate_index": 24,
                "forced_left_line_c1": ["-1", "4", "1"],
                "universally_lifted_lower_line_c1": ["1", "-4", "0"],
                "coordinate_rule": "exchange j1 and j2",
            },
            "right_serre_restriction_composed_with_section_is_zero": True,
            "lower_line_lifts_for_every_parameter": True,
            "lower_line_descends": True,
            "stability_logic": (
                "if both proper subbundles had negative slope, their sum would "
                "be negative, contradicting the strictly positive fiber-class slope"
            ),
            "common_stability_chamber": "empty",
            "every_pair_unstable": True,
            "candidate_blocks_refuted": True,
            "global_computable_carrier_no_go": False,
            "arbitrary_extension_point_selected": False,
            "sampled_polarization_used": False,
            "remaining_nonzero_candidate_blocks": [5, 25],
            "remaining_nonzero_family_count": 72,
            "next_invariant_ext_dimensions": [102, 108],
            "next_candidate_blocks": [5, 25],
            "next_required_object": (
                "exact stability classification of the 72 families in "
                "candidate blocks 5 and 25"
            ),
            "status": (
                "exact scoped no-go for all 72 dimension-50/52 families in "
                "candidates 4 and 24"
            ),
        }


def _polynomial_record(polynomial: Polynomial) -> list[dict[str, object]]:
    """Serialize one exact sparse slope polynomial."""

    return [
        {"exponents": list(exponents), "coefficient": str(coefficient)}
        for exponents, coefficient in polynomial.terms
    ]


@cache
def next_survivor_lower_line_no_go() -> NextSurvivorLowerLineNoGo:
    """Certify universal lower-line lifting and incompatible slopes exactly."""

    restriction = _verified_artifact(
        RESTRICTION_ARTIFACT,
        "next-survivor-right-line-restriction-v1",
    )
    generators = _verified_artifact(
        GENERATOR_ARTIFACT,
        "next-survivor-generator-restrictions-v1",
    )
    if not (
        restriction.get("checked_pair_count") == 72
        and restriction.get("induced_restriction_rank") == 20
        and restriction.get("nonzero_orbit_space_counts")
        == dict(EXPECTED_ORBITS)
        and generators.get("checked_restriction_count") == 288
        and generators.get("induced_rank_counts") == EXPECTED_GENERATOR_RANKS
        and generators.get("finite_union_complement_nonempty") is True
    ):
        raise ValueError("the prior next-survivor strata are incomplete")

    section_dimensions = []
    for factor, section_degree in SECTION_DEGREES.items():
        section_bundle = sparse_line_bundle(*section_degree)
        section_components = lower_line_section_components(
            sparse_line_bundle(0, 0, 0),
            factor,
        )
        section_h0_dimension = (
            section_bundle.space(0).dimension
            - section_bundle.differential(0).rank()
        )
        if not (
            section_bundle.squared_zero
            and section_h0_dimension == 1
            and dict(section_components)[0].rank() == 1
        ):
            raise ValueError("one lower-line section lacks its unique nonzero class")
        section_dimensions.append(section_h0_dimension)

    _, records = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    pairs = declared_schoen_outer_pairs()
    c1_hyperplanes = _constituent_c1_hyperplanes()
    dimensions: Counter[int] = Counter()
    orbit_spaces: Counter[str] = Counter()
    topology_data: dict[int, tuple[tuple[Rational, ...], tuple[Rational, ...], bool]] = {}
    for candidate_index, start, end in BLOCKS:
        try:
            for global_index in range(start, end + 1):
                record = records[global_index - 1]
                pair_candidate, candidate, left_ray, right_ray = pairs[
                    global_index - 1
                ]
                if pair_candidate != candidate_index or record.get(
                    "candidate_index"
                ) != candidate_index:
                    raise ValueError("the lower-line no-go block order changed")
                invariant = record.get("invariant_subcomplex")
                if not isinstance(invariant, dict) or not isinstance(
                    invariant.get("invariant_ext_one_dimension"), int
                ):
                    raise ValueError("a lower-line pair lacks its invariant dimension")
                dimension = invariant["invariant_ext_one_dimension"]
                dimensions[dimension] += 1
                orbit_spaces[f"P^{dimension - 1}(Q(omega))"] += 1

                outer = sparse_outer_hom(
                    left_ray,
                    right_ray,
                    candidate.left_factor,
                    candidate.left_twist,
                    candidate.right_factor,
                    candidate.right_twist,
                )
                right = _side_data(record, "right")
                right_line = _serre_line_degree(right[0], right[1], right[2])
                section_degree = SECTION_DEGREES[candidate.right_factor]
                source_hom = sparse_line_hom_complex(outer, right_line)
                lower_hom, section_maps = lower_line_hom_section_map(
                    source_hom,
                    candidate.right_factor,
                )
                lower_line = _line_subtract(right_line, section_degree)
                if not (
                    source_hom.squared_zero
                    and lower_hom.squared_zero
                    and lower_hom.line_degree == lower_line
                    and all(map_.is_zero() for _, map_ in section_maps)
                ):
                    raise ValueError("one lower-line Hom pullback is not identically zero")

                subobjects = {
                    item.name: item
                    for item in _forced_subobjects(record, c1_hyperplanes)
                }
                left_line = subobjects["L_left"].first_chern
                typed_lower = tuple(Rational(value) for value in lower_line)
                if (left_line[0] + left_line[1]) % 3 != 0 or (
                    typed_lower[0] + typed_lower[1]
                ) % 3 != 0:
                    raise ValueError("one lower-line slope witness does not descend")
                current = (left_line, typed_lower, True)
                if candidate_index in topology_data and topology_data[
                    candidate_index
                ] != current:
                    raise ValueError("lower-line topology varies within one block")
                topology_data[candidate_index] = current
        finally:
            _clear_worker_caches()

    first_left, first_lower, first_zero = topology_data[4]
    second_left, second_lower, second_zero = topology_data[24]
    factor_exchange_exact = (
        section_dimensions == [1, 1]
        and
        second_left == (first_left[1], first_left[0], first_left[2])
        and second_lower == (first_lower[1], first_lower[0], first_lower[2])
        and first_zero
        and second_zero
    )
    left_slope = _slope_polynomial(
        schoen_geometry().quotient_divisor(first_left),
        1,
    )
    lower_slope = _slope_polynomial(
        schoen_geometry().quotient_divisor(first_lower),
        1,
    )
    return NextSurvivorLowerLineNoGo(
        72,
        tuple(sorted(dimensions.items())),
        tuple(sorted(orbit_spaces.items())),
        SECTION_DEGREES[1],
        section_dimensions[0],
        first_left,
        first_lower,
        left_slope,
        lower_slope,
        left_slope + lower_slope,
        first_zero and second_zero,
        factor_exchange_exact,
    )


def write_next_survivor_lower_line_no_go(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed lower-line no-go artifact atomically."""

    payload = next_survivor_lower_line_no_go().as_record()
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
    """Regenerate the exact lower-line no-go artifact."""

    payload = write_next_survivor_lower_line_no_go()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"checked_pair_count: {payload['checked_pair_count']}")
    print(f"common_stability_chamber: {payload['common_stability_chamber']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "NextSurvivorLowerLineNoGo",
    "next_survivor_lower_line_no_go",
]
