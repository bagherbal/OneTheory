"""Solve the forced-subobject chamber for the mixed-sign minimum blocks.

Owns:
    Exact necessary slope inequalities and a rational nonempty chamber family
    for all invariant outer extensions in candidates 15 and 35.

Depends on:
    The forced-subobject topology theorem, exact projective orbit certificates,
    Schoen intersections, and the published positive Kahler cone.

Must not:
    Promote necessary inequalities to full stability, select a physical
    polarization or Ext point, or generalize beyond candidates 15 and 35.

Phase 0:
    The common forced-subobject chamber is classified and proved nonempty.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.numbers import Rational
from onetheory.math.polynomials import Polynomial
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
    OUTPUT as FORCED_SCREEN_ARTIFACT,
)
from .forced_subobject_stability_screen import (
    _constituent_c1_hyperplanes,
    _forced_subobjects,
    forced_subobject_stability_screen,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_sign_minimum_chamber.json"
BLOCKS = ((15, 505, 540), (35, 1225, 1260))
EXPECTED_DIMENSIONS = Counter({18: 36, 24: 36})
EXPECTED_ORBITS = Counter({"P^17(Q(omega))": 36, "P^23(Q(omega))": 36})
WITNESS = (Rational(2), Rational(1), Rational(4))


def _exchange_first_two_variables(polynomial: Polynomial) -> Polynomial:
    """Exchange the exact factor-polarization coordinates."""

    return Polynomial(
        {
            (exponents[1], exponents[0], exponents[2]): coefficient
            for exponents, coefficient in polynomial.terms
        },
        variable_count=3,
    )


def _evaluate(polynomial: Polynomial, point: tuple[Rational, ...]) -> Rational:
    """Evaluate one exact slope polynomial at a rational polarization."""

    return polynomial.substitute(point).coefficient(())


@dataclass(frozen=True, slots=True)
class MixedSignMinimumChamber:
    """The exact common necessary chamber for candidates 15 and 35."""

    block_pair_ranges: tuple[tuple[int, int, int], ...]
    checked_pair_count: int
    dimension_counts: tuple[tuple[int, int], ...]
    orbit_space_counts: tuple[tuple[str, int], ...]
    left_line_slope: Polynomial
    left_constituent_slope: Polynomial
    right_line_preimage_slope: Polynomial
    witness: tuple[Rational, ...]
    witness_values: tuple[Rational, ...]

    def __post_init__(self) -> None:
        if self.block_pair_ranges != BLOCKS or self.checked_pair_count != 72:
            raise ValueError("the mixed-sign minimum must contain 72 pairs")
        if Counter(dict(self.dimension_counts)) != EXPECTED_DIMENSIONS:
            raise ValueError("the mixed-sign minimum changed Ext dimensions")
        if Counter(dict(self.orbit_space_counts)) != EXPECTED_ORBITS:
            raise ValueError("the mixed-sign minimum changed projective orbits")
        expected_line = Polynomial(
            {
                (2, 0, 0): Rational(-1, 3),
                (1, 1, 0): Rational(2),
                (1, 0, 1): Rational(-2),
                (0, 2, 0): Rational(-2, 3),
                (0, 1, 1): Rational(-4),
            },
            variable_count=3,
        )
        expected_preimage = Polynomial(
            {
                (2, 0, 0): Rational(-1, 9),
                (1, 1, 0): Rational(4, 3),
                (1, 0, 1): Rational(-2, 3),
                (0, 2, 0): Rational(1, 9),
                (0, 1, 1): Rational(2, 3),
            },
            variable_count=3,
        )
        if self.left_line_slope != expected_line:
            raise ValueError("the candidate-15 Serre-line slope identity failed")
        if self.left_constituent_slope != self.left_line_slope:
            raise ValueError("the left line and rank-two slopes must coincide")
        if self.right_line_preimage_slope != expected_preimage:
            raise ValueError("the candidate-15 preimage slope identity failed")
        if self.witness != WITNESS or self.witness_values != (
            Rational(-30),
            Rational(-30),
            Rational(-1, 3),
        ):
            raise ValueError("the exact common-chamber witness changed")
        if any(value >= 0 for value in self.witness_values):
            raise ValueError("the declared common-chamber witness is not strict")

    def as_record(self) -> dict[str, object]:
        """Serialize the exact necessary chamber without asserting stability."""

        exchanged_line = _exchange_first_two_variables(self.left_line_slope)
        exchanged_preimage = _exchange_first_two_variables(
            self.right_line_preimage_slope
        )
        return {
            "schema": "mixed-sign-minimum-forced-chamber-v1",
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
            "first_orientation": {
                "candidate_index": 15,
                "forced_subobjects": [
                    {
                        "name": "L_left",
                        "rank": 1,
                        "c1": ["-2", "-1", "2"],
                        "slope": _polynomial_record(self.left_line_slope),
                    },
                    {
                        "name": "V_left",
                        "rank": 2,
                        "c1": ["-4", "-2", "4"],
                        "slope": _polynomial_record(self.left_constituent_slope),
                    },
                    {
                        "name": "preimage(L_right)",
                        "rank": 3,
                        "c1": ["1", "-1", "2"],
                        "slope": _polynomial_record(self.right_line_preimage_slope),
                    },
                ],
                "exact_common_chamber": (
                    "j1>j2>0 and j3>max(0,"
                    "(-j1^2+6*j1*j2-2*j2^2)/(6*(j1+2*j2)),"
                    "(-j1^2+12*j1*j2+j2^2)/(6*(j1-j2)))"
                ),
                "one_parameter_certificate": {
                    "polarization": "(j1,j2,j3)=(2,1,t)",
                    "condition": "t>7/2",
                    "L_left_slope": "2-8*t",
                    "V_left_slope": "2-8*t",
                    "preimage_L_right_slope": "(7-2*t)/3",
                },
            },
            "factor_exchanged_orientation": {
                "candidate_index": 35,
                "coordinate_rule": "exchange j1 and j2",
                "left_line_slope": _polynomial_record(exchanged_line),
                "right_line_preimage_slope": _polynomial_record(exchanged_preimage),
                "exact_common_chamber": (
                    "j2>j1>0 with the candidate-15 bounds after j1<->j2"
                ),
                "one_parameter_certificate": {
                    "polarization": "(j1,j2,j3)=(1,2,t)",
                    "condition": "t>7/2",
                },
            },
            "rational_witness": {
                "candidate_15_polarization": [str(value) for value in self.witness],
                "candidate_35_polarization": ["1", "2", "4"],
                "candidate_15_forced_slopes": [
                    str(value) for value in self.witness_values
                ],
                "candidate_35_forced_slopes": ["-30", "-30", "-1/3"],
            },
            "common_forced_subobject_chamber_nonempty": True,
            "full_slope_stability_proved": False,
            "additional_saturated_subsheaves_classified": False,
            "arbitrary_extension_point_selected": False,
            "physical_polarization_selected": False,
            "sampled_positivity_used": False,
            "first_missing_prerequisite": (
                "classification of all additional saturated destabilizing subsheaves"
            ),
            "next_required_object": (
                "minimum-complexity universal family among the 36 "
                "eighteen-dimensional projective extension spaces"
            ),
            "status": (
                "exact nonempty necessary chamber for all 72 families in "
                "candidates 15 and 35; full stability remains unresolved"
            ),
        }


def _polynomial_record(polynomial: Polynomial) -> list[dict[str, object]]:
    """Serialize an exact sparse slope polynomial."""

    return [
        {"exponents": list(exponents), "coefficient": str(coefficient)}
        for exponents, coefficient in polynomial.terms
    ]


@cache
def mixed_sign_minimum_chamber() -> MixedSignMinimumChamber:
    """Derive and certify the common forced-subobject chamber exactly."""

    stored = json.loads(FORCED_SCREEN_ARTIFACT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(stored):
        raise ValueError("the forced-subobject screen digest does not verify")
    if stored != forced_subobject_stability_screen().as_record():
        raise ValueError("the forced-subobject screen artifact is stale")

    invariant_digest, records = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    actions, _ = _read_partial(AUTOMORPHISM_ARTIFACT, invariant_digest)
    c1_hyperplanes = _constituent_c1_hyperplanes()
    selected: list[dict[str, object]] = []
    dimensions: Counter[int] = Counter()
    orbit_spaces: Counter[str] = Counter()
    profiles: dict[int, set[tuple[object, ...]]] = {15: set(), 35: set()}
    for candidate, start, end in BLOCKS:
        block = tuple(records[index - 1] for index in range(start, end + 1))
        if any(record.get("candidate_index") != candidate for record in block):
            raise ValueError("mixed-sign minimum candidate indices changed")
        selected.extend(block)
        for record in block:
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
            if not (
                isinstance(action, dict)
                and action.get("exact") is True
                and action.get("action_proof") == "exact equality on cover cocycles"
                and action.get("nonzero_orbit_space") == expected_orbit
            ):
                raise ValueError("a mixed-sign pair lacks its direct scalar quotient")
            orbit_spaces[expected_orbit] += 1
            profiles[candidate].add(_forced_subobjects(record, c1_hyperplanes))

    if any(len(candidate_profiles) != 1 for candidate_profiles in profiles.values()):
        raise ValueError("forced subobjects vary inside a mixed-sign topology block")
    first = next(iter(profiles[15]))
    second = next(iter(profiles[35]))
    first_by_name = {subobject.name: subobject for subobject in first}
    second_by_name = {subobject.name: subobject for subobject in second}
    if any(
        second_by_name[name].slope != _exchange_first_two_variables(subobject.slope)
        for name, subobject in first_by_name.items()
    ):
        raise ValueError("the mixed-sign factor-exchange identity failed")
    slopes = (
        first_by_name["L_left"].slope,
        first_by_name["V_left"].slope,
        first_by_name["preimage(L_right)"].slope,
    )
    values = tuple(_evaluate(slope, WITNESS) for slope in slopes)
    return MixedSignMinimumChamber(
        BLOCKS,
        len(selected),
        tuple(sorted(dimensions.items())),
        tuple(sorted(orbit_spaces.items())),
        slopes[0],
        slopes[1],
        slopes[2],
        WITNESS,
        values,
    )


def write_mixed_sign_minimum_chamber(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed necessary chamber atomically."""

    payload = mixed_sign_minimum_chamber().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact mixed-sign minimum chamber artifact."""

    payload = write_mixed_sign_minimum_chamber()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "common_forced_subobject_chamber_nonempty: "
        f"{payload['common_forced_subobject_chamber_nonempty']}"
    )
    print(f"full_slope_stability_proved: {payload['full_slope_stability_proved']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
