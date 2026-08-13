"""Classify stability of the current minimum computable topology blocks.

Owns:
    An exact forced-left-line slope exclusion for all outer-extension families
    in candidates 8 and 28, including both invariant-Ext dimensions present.

Depends on:
    Complete invariant and automorphism artifacts, certified descended Serre
    constituents, exact Schoen intersections, and the published Kahler cone.

Must not:
    Generalize beyond candidates 8 and 28, select an Ext point, infer a global
    carrier no-go, or replace symbolic positivity with sampled polarizations.

Phase 0:
    The current 72-family minimum block is refuted exactly by slope stability.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
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

from .minimal_block_stability_no_go import _topology_tuple
from .pair_73_stability_wall import _serre_line_degree, _slope_polynomial

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/current_minimum_stability_no_go.json"
CARRIER_ARTIFACT = ROOT / "data/generated/computable_carrier/computable_carrier_artifact.json"
BLOCKS = ((8, 253, 288), (28, 973, 1008))
EXPECTED_DIMENSIONS = Counter({8: 36, 10: 36})
EXPECTED_TOPOLOGIES = (
    (1, (-1, 1, 0), -6, 1, (-2, -1, 0), 0),
    (2, (1, -1, 0), -6, 2, (-1, -2, 0), 0),
)


def _coefficient_positive_left_line_slope() -> Polynomial:
    """Return the exact forced-line slope in the first factor orientation."""

    line = schoen_geometry().quotient_divisor((5, 1, 0))
    return _slope_polynomial(line, 1)


def _exchange_first_two_variables(polynomial: Polynomial) -> Polynomial:
    """Exchange the two Schoen factor coordinates in an exact polynomial."""

    return Polynomial(
        {
            (exponents[1], exponents[0], exponents[2]): coefficient
            for exponents, coefficient in polynomial.terms
        },
        variable_count=3,
    )


def _certified_constituents() -> set[tuple[str, tuple[str, ...], int]]:
    """Read exact locally-free descended constituent identities."""

    artifact = json.loads(CARRIER_ARTIFACT.read_text(encoding="utf-8"))
    inputs = artifact.get("tier_a_chain_inputs")
    if not isinstance(inputs, dict):
        raise ValueError("the computable-carrier chain inputs are unavailable")
    frontier = inputs.get("tier_b_monomial_constituent_descent_frontier")
    if not isinstance(frontier, dict) or not isinstance(frontier.get("lines"), list):
        raise ValueError("the monomial constituent descent frontier is unavailable")
    certified: set[tuple[str, tuple[str, ...], int]] = set()
    for line in frontier["lines"]:
        if not isinstance(line, dict):
            raise ValueError("a constituent certificate is malformed")
        scheme = line.get("scheme")
        characters = line.get("character_pair")
        shift = line.get("target_line_shift")
        if not (
            isinstance(scheme, str)
            and isinstance(characters, list)
            and all(isinstance(character, str) for character in characters)
            and isinstance(shift, int)
        ):
            raise ValueError("a constituent certificate lacks its exact identity")
        if not (
            line.get("exact") is True
            and line.get("rank") == 2
            and line.get("locally_free_sheaf_verified") is True
            and line.get("internal_descent_certificate") is True
        ):
            raise ValueError("a declared monomial constituent lacks a closed exact gate")
        certified.add((scheme, tuple(characters), shift))
    return certified


@dataclass(frozen=True, slots=True)
class CurrentMinimumStabilityNoGo:
    """The exact forced-left-line exclusion for candidates 8 and 28."""

    block_pair_ranges: tuple[tuple[int, int, int], ...]
    checked_pair_count: int
    dimension_counts: tuple[tuple[int, int], ...]
    orbit_space_counts: tuple[tuple[str, int], ...]
    topologies: tuple[tuple[object, ...], ...]
    first_orientation_line_c1: tuple[Rational, ...]
    first_orientation_slope: Polynomial

    def __post_init__(self) -> None:
        if self.block_pair_ranges != BLOCKS or self.checked_pair_count != 72:
            raise ValueError("the current minimum block must contain 72 pairs")
        if Counter(dict(self.dimension_counts)) != EXPECTED_DIMENSIONS:
            raise ValueError("the current minimum block changed Ext dimensions")
        if dict(self.orbit_space_counts) != {
            "P^7(Q(omega))": 36,
            "P^9(Q(omega))": 36,
        }:
            raise ValueError("the current minimum block changed orbit spaces")
        if self.topologies != EXPECTED_TOPOLOGIES:
            raise ValueError("the current minimum block changed topology")
        if self.first_orientation_line_c1 != (
            Rational(5),
            Rational(1),
            Rational(0),
        ):
            raise ValueError("the current minimum block changed its forced line")
        expected = Polynomial(
            {
                (2, 0, 0): Rational(1, 3),
                (1, 1, 0): Rational(4),
                (1, 0, 1): Rational(2),
                (0, 2, 0): Rational(5, 3),
                (0, 1, 1): Rational(10),
            },
            variable_count=3,
        )
        if self.first_orientation_slope != expected:
            raise ValueError("the current minimum forced-line slope identity failed")
        if any(coefficient <= 0 for _, coefficient in self.first_orientation_slope.terms):
            raise ValueError("the current minimum forced-line slope is not positive")

    def as_record(self) -> dict[str, object]:
        """Serialize the scoped no-go without choosing a family or parameter."""

        exchanged = _exchange_first_two_variables(self.first_orientation_slope)
        return {
            "schema": "current-minimum-stability-block-no-go-v1",
            "candidate_blocks": [
                {
                    "candidate_index": candidate,
                    "global_pair_range": [start, end],
                    "pair_count": end - start + 1,
                    "topology": {
                        "left_factor": topology[0],
                        "left_twist": list(topology[1]),
                        "left_target_line_shift": topology[2],
                        "right_factor": topology[3],
                        "right_twist": list(topology[4]),
                        "right_target_line_shift": topology[5],
                    },
                }
                for (candidate, start, end), topology in zip(
                    self.block_pair_ranges, self.topologies, strict=True
                )
            ],
            "checked_pair_count": self.checked_pair_count,
            "invariant_ext_dimension_counts": {
                str(dimension): count for dimension, count in self.dimension_counts
            },
            "nonzero_orbit_space_counts": dict(self.orbit_space_counts),
            "constituent_sequence": (
                "0 -> L_left -> V_left -> I_left tensor M_left -> 0"
            ),
            "outer_sequence": "0 -> V_left -> V_E -> V_right -> 0",
            "forced_subbundle_composition": "L_left -> V_left -> V_E",
            "forced_line_descends_for_every_pair": True,
            "first_orientation_left_line_c1": [
                str(value) for value in self.first_orientation_line_c1
            ],
            "factor_exchanged_left_line_c1": ["1", "5", "0"],
            "first_orientation_left_line_slope": [
                {"exponents": list(exponents), "coefficient": str(coefficient)}
                for exponents, coefficient in self.first_orientation_slope.terms
            ],
            "factor_exchanged_left_line_slope": [
                {"exponents": list(exponents), "coefficient": str(coefficient)}
                for exponents, coefficient in exchanged.terms
            ],
            "strictly_positive_on_kahler_cone": True,
            "positivity_proof": (
                "every exact slope coefficient is positive and the published "
                "Kahler cone has j1,j2,j3 > 0"
            ),
            "extension_parameter_dependence": "none",
            "right_line_restriction_required": False,
            "every_pair_unstable": True,
            "current_minimum_and_companion_block_refuted": True,
            "global_computable_carrier_no_go": False,
            "arbitrary_pair_selected": False,
            "arbitrary_extension_point_selected": False,
            "sampled_polarization_used": False,
            "next_required_object": (
                "stability classification of the 72 ten-dimensional "
                "invariant-Ext families in candidate blocks 18 and 38"
            ),
            "status": (
                "exact scoped no-go for all 72 eight- and ten-dimensional "
                "invariant-Ext families in candidates 8 and 28"
            ),
        }


def current_minimum_stability_no_go() -> CurrentMinimumStabilityNoGo:
    """Certify the forced positive-slope line across both factor orientations."""

    invariant_digest, records = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    actions, _ = _read_partial(AUTOMORPHISM_ARTIFACT, invariant_digest)
    constituents = _certified_constituents()
    selected: list[dict[str, object]] = []
    topologies: list[tuple[object, ...]] = []
    dimensions: Counter[int] = Counter()
    orbit_spaces: Counter[str] = Counter()
    geometry = schoen_geometry()

    for candidate, start, end in BLOCKS:
        block = tuple(records[index - 1] for index in range(start, end + 1))
        if any(record.get("candidate_index") != candidate for record in block):
            raise ValueError("current-minimum candidate indices changed")
        profiles = {_topology_tuple(record) for record in block}
        if len(profiles) != 1:
            raise ValueError("one current-minimum block spans multiple topologies")
        topologies.append(next(iter(profiles)))
        selected.extend(block)

    for record in selected:
        invariant = record.get("invariant_subcomplex")
        if not isinstance(invariant, dict) or not isinstance(
            invariant.get("invariant_ext_one_dimension"), int
        ):
            raise ValueError("one current-minimum pair lacks its invariant dimension")
        if not (
            invariant.get("exact") is True
            and invariant.get("deck_action_exact") is True
            and invariant.get("restrictions_exact") is True
            and invariant.get("squared_zero") is True
        ):
            raise ValueError("one current-minimum invariant Ext gate is not exact")
        dimension = invariant["invariant_ext_one_dimension"]
        dimensions[dimension] += 1

        index = record.get("global_pair_index")
        if not isinstance(index, int) or index not in actions:
            raise ValueError("one current-minimum pair lacks an automorphism certificate")
        action = actions[index].get("automorphism_action")
        expected_orbit = f"P^{dimension - 1}(Q(omega))"
        if not (
            isinstance(action, dict)
            and action.get("exact") is True
            and action.get("nonzero_orbit_space") == expected_orbit
        ):
            raise ValueError("one current-minimum pair lacks its exact projective quotient")
        orbit_spaces[expected_orbit] += 1

        topology = record.get("topology")
        if not isinstance(topology, dict) or topology.get(
            "individual_line_twists_descend"
        ) is not True:
            raise ValueError("one current-minimum forced line does not descend")
        factor = topology.get("left_factor")
        shift = topology.get("left_target_line_shift")
        twist = topology.get("left_twist")
        scheme = record.get("left_scheme")
        characters = record.get("left_character_pair")
        if not (
            isinstance(factor, int)
            and isinstance(shift, int)
            and isinstance(twist, list)
            and len(twist) == 3
            and all(isinstance(value, int) for value in twist)
            and isinstance(scheme, str)
            and isinstance(characters, list)
            and all(isinstance(character, str) for character in characters)
        ):
            raise ValueError("one current-minimum left constituent is malformed")
        if (scheme, tuple(characters), shift) not in constituents:
            raise ValueError("one current-minimum left constituent lacks exact descent")
        line_degree = _serre_line_degree(factor, shift, tuple(twist))
        slope = _slope_polynomial(geometry.quotient_divisor(line_degree), 1)
        if any(coefficient <= 0 for _, coefficient in slope.terms):
            raise ValueError("one current-minimum forced line is not strictly positive")

    first_line = geometry.quotient_divisor((5, 1, 0))
    return CurrentMinimumStabilityNoGo(
        BLOCKS,
        len(selected),
        tuple(sorted(dimensions.items())),
        tuple(sorted(orbit_spaces.items())),
        tuple(topologies),
        first_line.coordinates,
        _coefficient_positive_left_line_slope(),
    )


def write_current_minimum_stability_no_go(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed current-minimum no-go atomically."""

    payload = current_minimum_stability_no_go().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact current-minimum stability no-go artifact."""

    payload = write_current_minimum_stability_no_go()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"checked_pair_count: {payload['checked_pair_count']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
