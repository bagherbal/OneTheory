"""Certify a necessary Kähler chamber for the next surviving carrier block.

Owns:
    Exact forced-subobject slope profiles, their factor exchange, and a
    rational chamber witness for candidates 4 and 24.

Depends on:
    The rank-20 restriction artifact, invariant carrier records, exact Schoen
    intersections, and descended constituent Chern data.

Must not:
    Promote a necessary chamber to stability, select a physical polarization,
    or infer that the nonlifting extension locus contains a stable bundle.

Phase 0:
    Research-only necessary-chamber certification is executable.
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
    _validated_invariant_records,
)

from .forced_subobject_stability_screen import (
    ForcedSubobject,
    _constituent_c1_hyperplanes,
    _forced_subobjects,
)
from .mixed_sign_minimum_chamber import (
    _exchange_first_two_variables,
    _polynomial_record,
)
from .next_survivor_restriction import OUTPUT as RESTRICTION_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/next_survivor_forced_chamber.json"
BLOCKS = ((4, 109, 144), (24, 829, 864))
EXPECTED_DIMENSIONS = Counter({50: 36, 52: 36})
WITNESS = (Rational(5), Rational(1), Rational(7))
EXPECTED_WITNESS_VALUES = (Rational(-1), Rational(-54), Rational(-18))


def _evaluate(polynomial: Polynomial, point: tuple[Rational, ...]) -> Rational:
    """Evaluate one exact rational slope polynomial at a rational point."""

    specialized = polynomial.substitute(point)
    if specialized.variable_count != 0:
        raise ValueError("a forced slope specialization retained variables")
    value = specialized.coefficient(())
    if not isinstance(value, Rational):
        raise ValueError("a forced slope left the rational coefficient field")
    return value


@dataclass(frozen=True, slots=True)
class NextSurvivorForcedChamber:
    """The exact necessary forced-subobject chamber in candidates 4 and 24."""

    checked_pair_count: int
    dimension_counts: tuple[tuple[int, int], ...]
    left_line_slope: Polynomial
    left_constituent_slope: Polynomial
    right_line_preimage_slope: Polynomial
    witness: tuple[Rational, ...]
    witness_values: tuple[Rational, ...]
    factor_exchange_exact: bool

    def __post_init__(self) -> None:
        if self.checked_pair_count != 72:
            raise ValueError("the next-survivor chamber must cover 72 families")
        if Counter(dict(self.dimension_counts)) != EXPECTED_DIMENSIONS:
            raise ValueError("the next-survivor chamber dimensions changed")
        if self.left_constituent_slope != self.right_line_preimage_slope.scale(3):
            raise ValueError("the forced rank-two/rank-three slope ratio changed")
        if self.witness != WITNESS or self.witness_values != EXPECTED_WITNESS_VALUES:
            raise ValueError("the next-survivor rational witness changed")
        if any(value >= 0 for value in self.witness_values):
            raise ValueError("the next-survivor witness is not strictly negative")
        if not self.factor_exchange_exact:
            raise ValueError("the next-survivor factor exchange failed")

    def as_record(self) -> dict[str, object]:
        """Serialize the necessary chamber while preserving the stability gap."""

        return {
            "schema": "next-survivor-forced-chamber-v1",
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
            "first_orientation": {
                "candidate_index": 4,
                "forced_subobjects": [
                    {
                        "name": "L_left",
                        "rank": 1,
                        "c1": ["4", "-1", "1"],
                        "slope": _polynomial_record(self.left_line_slope),
                    },
                    {
                        "name": "V_left",
                        "rank": 2,
                        "c1": ["2", "-2", "2"],
                        "slope": _polynomial_record(self.left_constituent_slope),
                    },
                    {
                        "name": "preimage(L_right)",
                        "rank": 3,
                        "c1": ["1", "-1", "1"],
                        "slope": _polynomial_record(
                            self.right_line_preimage_slope
                        ),
                    },
                ],
                "exact_forced_chamber": (
                    "j1,j2,j3>0; mu(L_left)<0; "
                    "mu(preimage(L_right))<0"
                ),
                "certified_subchamber": (
                    "j1>4*j2>0 and j3>max(0,"
                    "(-j1^2+12*j1*j2+4*j2^2)/(6*(j1-4*j2)),"
                    "(-j1^2+6*j1*j2+j2^2)/(6*(j1-j2)))"
                ),
            },
            "factor_exchanged_orientation": {
                "candidate_index": 24,
                "coordinate_rule": "exchange j1 and j2",
                "left_line_slope": _polynomial_record(
                    _exchange_first_two_variables(self.left_line_slope)
                ),
                "right_line_preimage_slope": _polynomial_record(
                    _exchange_first_two_variables(
                        self.right_line_preimage_slope
                    )
                ),
            },
            "slope_relation": "mu(V_left)=3*mu(preimage(L_right))",
            "rational_witness": {
                "candidate_4_polarization": [
                    str(value) for value in self.witness
                ],
                "candidate_24_polarization": ["1", "5", "7"],
                "candidate_4_forced_slopes": [
                    str(value) for value in self.witness_values
                ],
                "candidate_24_forced_slopes": ["-1", "-54", "-18"],
            },
            "common_forced_subobject_chamber_nonempty": True,
            "nonlifting_open_complement_nonempty": True,
            "full_slope_stability_proved": False,
            "additional_saturated_subsheaves_classified": False,
            "arbitrary_extension_point_selected": False,
            "physical_polarization_selected": False,
            "sampled_positivity_used": False,
            "first_missing_prerequisite": (
                "classification of additional saturated subsheaves on the "
                "nonlifting open complements"
            ),
            "next_required_object": (
                "generic stability theorem or exact destabilizing stratum for "
                "the candidate-4/24 nonlifting complements"
            ),
            "status": (
                "exact nonempty necessary chamber for all 72 candidate-4/24 "
                "families; full stability remains unresolved"
            ),
        }


def _profile(record: dict[str, object], c1_hyperplanes) -> tuple[ForcedSubobject, ...]:
    """Return one exact forced profile with its invariant dimension."""

    invariant = record.get("invariant_subcomplex")
    if not isinstance(invariant, dict) or invariant.get("exact") is not True:
        raise ValueError("a next-survivor pair lacks an exact invariant complex")
    return _forced_subobjects(record, c1_hyperplanes)


@cache
def next_survivor_forced_chamber() -> NextSurvivorForcedChamber:
    """Certify the common forced chamber and its rational witness."""

    restriction = json.loads(RESTRICTION_ARTIFACT.read_text(encoding="utf-8"))
    restriction_digest = restriction.pop("artifact_digest", None)
    if not isinstance(restriction_digest, str) or restriction_digest != _canonical_digest(
        restriction
    ):
        raise ValueError("the next-survivor restriction digest does not verify")
    if not (
        restriction.get("checked_pair_count") == 72
        and restriction.get("induced_restriction_rank") == 20
        and restriction.get("kernel_contains_no_stable_extension") is True
        and restriction.get("nonlifting_open_complement_nonempty") is True
    ):
        raise ValueError("the restriction artifact does not expose the live complement")

    _, records = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    c1_hyperplanes = _constituent_c1_hyperplanes()
    dimensions: Counter[int] = Counter()
    profiles: dict[int, set[tuple[ForcedSubobject, ...]]] = {4: set(), 24: set()}
    for candidate, start, end in BLOCKS:
        for index in range(start, end + 1):
            record = records[index - 1]
            if record.get("candidate_index") != candidate:
                raise ValueError("the next-survivor chamber block order changed")
            invariant = record.get("invariant_subcomplex")
            if not isinstance(invariant, dict) or not isinstance(
                invariant.get("invariant_ext_one_dimension"), int
            ):
                raise ValueError("a next-survivor pair lacks its Ext dimension")
            dimensions[invariant["invariant_ext_one_dimension"]] += 1
            profiles[candidate].add(_profile(record, c1_hyperplanes))
    if any(len(candidate_profiles) != 1 for candidate_profiles in profiles.values()):
        raise ValueError("forced slopes vary within a next-survivor topology block")
    first = next(iter(profiles[4]))
    second = next(iter(profiles[24]))
    first_by_name = {subobject.name: subobject for subobject in first}
    second_by_name = {subobject.name: subobject for subobject in second}
    factor_exchange_exact = all(
        second_by_name[name].slope
        == _exchange_first_two_variables(first_by_name[name].slope)
        for name in first_by_name
    )
    slopes = (
        first_by_name["L_left"].slope,
        first_by_name["V_left"].slope,
        first_by_name["preimage(L_right)"].slope,
    )
    witness_values = tuple(_evaluate(slope, WITNESS) for slope in slopes)
    return NextSurvivorForcedChamber(
        72,
        tuple(sorted(dimensions.items())),
        *slopes,
        WITNESS,
        witness_values,
        factor_exchange_exact,
    )


def write_next_survivor_forced_chamber(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed forced-chamber artifact atomically."""

    payload = next_survivor_forced_chamber().as_record()
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
    """Regenerate the exact next-survivor forced-chamber artifact."""

    payload = write_next_survivor_forced_chamber()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"checked_pair_count: {payload['checked_pair_count']}")
    print(
        "common_forced_subobject_chamber_nonempty: "
        f"{payload['common_forced_subobject_chamber_nonempty']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "NextSurvivorForcedChamber",
    "next_survivor_forced_chamber",
]
