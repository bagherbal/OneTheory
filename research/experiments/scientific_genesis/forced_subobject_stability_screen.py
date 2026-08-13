"""Compress the carrier stability search by forced constituent subobjects.

Owns:
    A topology-level theorem and exhaustive exact screen using the left Serre
    line, left rank-two constituent, and inverse image of the right Serre line.

Depends on:
    Complete invariant-Ext topology data, certified descended constituents,
    exact Schoen intersections, and the published positive Kahler cone.

Must not:
    Treat a mixed-sign slope as stable, infer a global Schoen-bundle no-go,
    select extension parameters, or require unfinished automorphism orbits.

Phase 0:
    Coefficient-positive forced subobjects exactly refute a scoped topology class.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
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

from .pair_73_stability_wall import _serre_line_degree, _slope_polynomial

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/forced_subobject_stability_screen.json"
CARRIER_ARTIFACT = ROOT / "data/generated/computable_carrier/computable_carrier_artifact.json"
EXPECTED_ZERO_EXT_CANDIDATES = (1, 2, 11, 12, 13, 21, 22, 31, 32, 33)
EXPECTED_NO_GO_CANDIDATES = (
    6,
    7,
    8,
    9,
    10,
    17,
    18,
    19,
    20,
    26,
    27,
    28,
    29,
    30,
    37,
    38,
    39,
    40,
)
EXPECTED_MIXED_SIGN_CANDIDATES = (3, 4, 5, 14, 15, 16, 23, 24, 25, 34, 35, 36)
INDEPENDENTLY_RETIRED_CANDIDATES = (3, 14, 23, 34)
EXPECTED_REMAINING_CANDIDATES = (4, 5, 15, 16, 24, 25, 35, 36)
EXPECTED_NO_GO_DIMENSIONS = Counter(
    {
        8: 36,
        10: 108,
        18: 36,
        22: 36,
        24: 72,
        30: 36,
        36: 36,
        38: 36,
        40: 36,
        66: 72,
        110: 36,
        116: 36,
        126: 72,
    }
)
EXPECTED_REMAINING_DIMENSIONS = Counter(
    {18: 36, 24: 36, 42: 36, 48: 36, 50: 36, 52: 36, 102: 36, 108: 36}
)


@dataclass(frozen=True, slots=True)
class ForcedSubobject:
    """One unavoidable proper subbundle and its exact slope polynomial."""

    name: str
    rank: int
    first_chern: tuple[Rational, ...]
    slope: Polynomial

    def __post_init__(self) -> None:
        if self.name not in {"L_left", "V_left", "preimage(L_right)"}:
            raise ValueError("unknown forced constituent subobject")
        if self.rank not in (1, 2, 3) or len(self.first_chern) != 3:
            raise ValueError("a forced subobject has invalid rank or Chern data")
        if self.slope.variable_count != 3 or self.slope.is_zero():
            raise ValueError("a forced subobject requires a nonzero three-variable slope")

    @property
    def coefficient_nonnegative(self) -> bool:
        """Return whether positivity on the open orthant follows coefficientwise."""

        return all(coefficient >= 0 for _, coefficient in self.slope.terms)

    def as_record(self) -> dict[str, object]:
        """Serialize the exact subobject witness."""

        return {
            "name": self.name,
            "rank": self.rank,
            "c1": [str(value) for value in self.first_chern],
            "slope": [
                {"exponents": list(exponents), "coefficient": str(coefficient)}
                for exponents, coefficient in self.slope.terms
            ],
            "all_coefficients_nonnegative": self.coefficient_nonnegative,
            "slope_strictly_positive_on_open_kahler_cone": (
                self.coefficient_nonnegative
            ),
        }


@dataclass(frozen=True, slots=True)
class RefutedTopologyBlock:
    """One 36-family topology block excluded by a forced subbundle."""

    candidate_index: int
    global_pair_range: tuple[int, int]
    invariant_dimension_counts: tuple[tuple[int, int], ...]
    witness: ForcedSubobject

    def __post_init__(self) -> None:
        start, end = self.global_pair_range
        if end - start + 1 != 36 or sum(dict(self.invariant_dimension_counts).values()) != 36:
            raise ValueError("a refuted topology block must contain 36 families")
        if not self.witness.coefficient_nonnegative:
            raise ValueError("a refuted topology block lacks a positive witness")

    def as_record(self) -> dict[str, object]:
        """Serialize one exact topology-level exclusion."""

        return {
            "candidate_index": self.candidate_index,
            "global_pair_range": list(self.global_pair_range),
            "pair_count": 36,
            "invariant_ext_dimension_counts": {
                str(dimension): count for dimension, count in self.invariant_dimension_counts
            },
            "witness": self.witness.as_record(),
        }


@dataclass(frozen=True, slots=True)
class ForcedSubobjectStabilityScreen:
    """The exact coefficient-positive classification of all 40 topology blocks."""

    checked_candidate_count: int
    checked_pair_count: int
    zero_ext_candidates: tuple[int, ...]
    refuted_blocks: tuple[RefutedTopologyBlock, ...]
    mixed_sign_candidates: tuple[int, ...]
    refuted_dimension_counts: tuple[tuple[int, int], ...]
    remaining_candidates: tuple[int, ...]
    remaining_dimension_counts: tuple[tuple[int, int], ...]

    def __post_init__(self) -> None:
        if self.checked_candidate_count != 40 or self.checked_pair_count != 1440:
            raise ValueError("the forced-subobject screen must cover the declared category")
        if self.zero_ext_candidates != EXPECTED_ZERO_EXT_CANDIDATES:
            raise ValueError("the zero-Ext topology partition changed")
        if tuple(block.candidate_index for block in self.refuted_blocks) != (
            EXPECTED_NO_GO_CANDIDATES
        ):
            raise ValueError("the coefficient-positive topology partition changed")
        if self.mixed_sign_candidates != EXPECTED_MIXED_SIGN_CANDIDATES:
            raise ValueError("the mixed-sign topology partition changed")
        if Counter(dict(self.refuted_dimension_counts)) != EXPECTED_NO_GO_DIMENSIONS:
            raise ValueError("the forced-subobject dimension counts changed")
        if self.remaining_candidates != EXPECTED_REMAINING_CANDIDATES:
            raise ValueError("the combined exact stability frontier changed")
        if Counter(dict(self.remaining_dimension_counts)) != EXPECTED_REMAINING_DIMENSIONS:
            raise ValueError("the remaining invariant dimensions changed")

    def as_record(self) -> dict[str, object]:
        """Serialize the structural screen and its exact scope boundary."""

        return {
            "schema": "forced-subobject-stability-screen-v1",
            "declared_category": {
                "candidate_count": self.checked_candidate_count,
                "pair_count": self.checked_pair_count,
                "families_per_candidate": 36,
            },
            "theorem": {
                "outer_sequence": "0 -> V_left -> V_E -> V_right -> 0",
                "left_serre_sequence": (
                    "0 -> L_left -> V_left -> I_left tensor M_left -> 0"
                ),
                "right_serre_sequence": (
                    "0 -> L_right -> V_right -> I_right tensor M_right -> 0"
                ),
                "forced_proper_subbundles": [
                    "L_left -> V_left -> V_E",
                    "V_left -> V_E",
                    "preimage(L_right) -> V_E",
                ],
                "stability_implication": (
                    "because det(V_E) is trivial, any forced subbundle with "
                    "nonnegative slope violates strict slope stability"
                ),
                "coefficient_criterion": (
                    "a nonzero slope polynomial with nonnegative coefficients "
                    "is strictly positive when j1,j2,j3 > 0"
                ),
            },
            "zero_invariant_ext_candidates": list(self.zero_ext_candidates),
            "coefficient_positive_no_go_blocks": [
                block.as_record() for block in self.refuted_blocks
            ],
            "coefficient_positive_no_go_candidate_count": len(self.refuted_blocks),
            "coefficient_positive_no_go_family_count": sum(
                end - start + 1 for start, end in (
                    block.global_pair_range for block in self.refuted_blocks
                )
            ),
            "coefficient_positive_no_go_dimension_counts": {
                str(dimension): count for dimension, count in self.refuted_dimension_counts
            },
            "mixed_sign_candidates_unresolved_by_this_criterion": list(
                self.mixed_sign_candidates
            ),
            "independently_retired_mixed_sign_candidates": list(
                INDEPENDENTLY_RETIRED_CANDIDATES
            ),
            "remaining_candidates_after_all_exact_stability_no_gos": list(
                self.remaining_candidates
            ),
            "remaining_family_count": 36 * len(self.remaining_candidates),
            "remaining_invariant_ext_dimension_counts": {
                str(dimension): count for dimension, count in self.remaining_dimension_counts
            },
            "next_invariant_ext_dimension": 18,
            "next_candidate_blocks": [15, 35],
            "next_required_object": (
                "exact common-chamber classification for the 72 families in "
                "candidate blocks 15 and 35"
            ),
            "automorphism_quotient_required": False,
            "explicit_extension_representative_required": False,
            "sampled_polarization_used": False,
            "global_computable_carrier_no_go": False,
            "status": (
                "exact scoped no-go for 648 families in 18 topology blocks; "
                "eight nonzero blocks remain after prior exact exclusions"
            ),
        }


def _constituent_c1_hyperplanes() -> dict[tuple[str, tuple[str, ...], int], Rational]:
    """Return exact constituent identities and untwisted first Chern values."""

    artifact = json.loads(CARRIER_ARTIFACT.read_text(encoding="utf-8"))
    inputs = artifact.get("tier_a_chain_inputs")
    if not isinstance(inputs, dict):
        raise ValueError("the computable-carrier chain inputs are unavailable")
    frontier = inputs.get("tier_b_monomial_constituent_descent_frontier")
    if not isinstance(frontier, dict) or not isinstance(frontier.get("lines"), list):
        raise ValueError("the monomial constituent descent frontier is unavailable")
    result: dict[tuple[str, tuple[str, ...], int], Rational] = {}
    for line in frontier["lines"]:
        if not isinstance(line, dict):
            raise ValueError("a constituent certificate is malformed")
        scheme = line.get("scheme")
        characters = line.get("character_pair")
        shift = line.get("target_line_shift")
        chern = line.get("chern_character")
        if not (
            isinstance(scheme, str)
            and isinstance(characters, list)
            and all(isinstance(character, str) for character in characters)
            and isinstance(shift, int)
            and isinstance(chern, dict)
            and isinstance(chern.get("c1_hyperplane"), int)
        ):
            raise ValueError("a constituent certificate lacks exact Chern identity")
        if not (
            line.get("exact") is True
            and line.get("rank") == 2
            and line.get("locally_free_sheaf_verified") is True
            and line.get("internal_descent_certificate") is True
        ):
            raise ValueError("a monomial constituent has an open exact gate")
        result[(scheme, tuple(characters), shift)] = Rational(chern["c1_hyperplane"])
    return result


def _typed_topology(record: dict[str, object]) -> dict[str, object]:
    """Return one validated determinant-trivial topology record."""

    topology = record.get("topology")
    if not isinstance(topology, dict):
        raise ValueError("an invariant record lacks topology")
    if not (
        topology.get("determinant_cancels") is True
        and topology.get("individual_line_twists_descend") is True
    ):
        raise ValueError("a screened topology lacks determinant or line descent")
    return topology


def _side_data(
    record: dict[str, object],
    side: str,
) -> tuple[int, int, tuple[int, int, int], str, tuple[str, ...]]:
    """Return typed constituent identity data for one side of an outer pair."""

    topology = _typed_topology(record)
    factor = topology.get(f"{side}_factor")
    shift = topology.get(f"{side}_target_line_shift")
    twist = topology.get(f"{side}_twist")
    scheme = record.get(f"{side}_scheme")
    characters = record.get(f"{side}_character_pair")
    if not (
        factor in (1, 2)
        and isinstance(shift, int)
        and isinstance(twist, list)
        and len(twist) == 3
        and all(isinstance(value, int) for value in twist)
        and isinstance(scheme, str)
        and isinstance(characters, list)
        and all(isinstance(character, str) for character in characters)
    ):
        raise ValueError("an outer pair has malformed constituent identity data")
    return factor, shift, tuple(twist), scheme, tuple(characters)


def _forced_subobjects(
    record: dict[str, object],
    c1_hyperplanes: dict[tuple[str, tuple[str, ...], int], Rational],
) -> tuple[ForcedSubobject, ...]:
    """Derive every extension-independent proper subbundle exactly."""

    left_factor, left_shift, left_twist, left_scheme, left_characters = _side_data(
        record, "left"
    )
    right_factor, right_shift, right_twist, right_scheme, right_characters = _side_data(
        record, "right"
    )
    left_key = (left_scheme, left_characters, left_shift)
    right_key = (right_scheme, right_characters, right_shift)
    if left_key not in c1_hyperplanes or right_key not in c1_hyperplanes:
        raise ValueError("an outer pair lacks a certified descended constituent")
    left_hyperplane = c1_hyperplanes[left_key]
    left_c1 = tuple(
        left_hyperplane * int(index == left_factor - 1) + Rational(2 * value)
        for index, value in enumerate(left_twist)
    )
    left_line = tuple(
        Rational(value)
        for value in _serre_line_degree(left_factor, left_shift, left_twist)
    )
    right_line = tuple(
        Rational(value)
        for value in _serre_line_degree(right_factor, right_shift, right_twist)
    )
    preimage = tuple(
        left_value + right_value
        for left_value, right_value in zip(left_c1, right_line, strict=True)
    )
    geometry = schoen_geometry()
    return tuple(
        ForcedSubobject(
            name,
            rank,
            first_chern,
            _slope_polynomial(geometry.quotient_divisor(first_chern), rank),
        )
        for name, rank, first_chern in (
            ("L_left", 1, left_line),
            ("V_left", 2, left_c1),
            ("preimage(L_right)", 3, preimage),
        )
    )


@cache
def forced_subobject_stability_screen() -> ForcedSubobjectStabilityScreen:
    """Classify every declared topology by coefficient-positive forced slopes."""

    _, records = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    c1_hyperplanes = _constituent_c1_hyperplanes()
    grouped: defaultdict[int, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        candidate = record.get("candidate_index")
        if not isinstance(candidate, int):
            raise ValueError("an invariant record lacks a candidate index")
        grouped[candidate].append(record)
    if tuple(sorted(grouped)) != tuple(range(1, 41)):
        raise ValueError("the declared topology candidate range changed")

    zero: list[int] = []
    refuted: list[RefutedTopologyBlock] = []
    mixed: list[int] = []
    refuted_dimensions: Counter[int] = Counter()
    dimensions_by_candidate: dict[int, Counter[int]] = {}
    for candidate in sorted(grouped):
        block = grouped[candidate]
        if len(block) != 36:
            raise ValueError("each topology candidate must contain 36 character pairs")
        dimensions: Counter[int] = Counter()
        profiles: set[tuple[ForcedSubobject, ...]] = set()
        for record in block:
            invariant = record.get("invariant_subcomplex")
            if not isinstance(invariant, dict) or not isinstance(
                invariant.get("invariant_ext_one_dimension"), int
            ):
                raise ValueError("an invariant record lacks its exact Ext dimension")
            if not (
                invariant.get("exact") is True
                and invariant.get("deck_action_exact") is True
                and invariant.get("squared_zero") is True
            ):
                raise ValueError("an invariant Ext certificate is not exact")
            dimensions[invariant["invariant_ext_one_dimension"]] += 1
            profiles.add(_forced_subobjects(record, c1_hyperplanes))
        dimensions_by_candidate[candidate] = dimensions
        if set(dimensions) == {0}:
            zero.append(candidate)
            continue
        if 0 in dimensions:
            raise ValueError("one topology mixes zero and nonzero invariant Ext")
        if len(profiles) != 1:
            raise ValueError("forced subobject data varies inside one topology block")
        subobjects = next(iter(profiles))
        witness = next(
            (subobject for subobject in subobjects if subobject.coefficient_nonnegative),
            None,
        )
        if witness is None:
            mixed.append(candidate)
            continue
        start = min(int(record["global_pair_index"]) for record in block)
        end = max(int(record["global_pair_index"]) for record in block)
        refuted.append(
            RefutedTopologyBlock(
                candidate,
                (start, end),
                tuple(sorted(dimensions.items())),
                witness,
            )
        )
        refuted_dimensions.update(dimensions)

    remaining = tuple(
        candidate
        for candidate in mixed
        if candidate not in INDEPENDENTLY_RETIRED_CANDIDATES
    )
    remaining_dimensions: Counter[int] = Counter()
    for candidate in remaining:
        remaining_dimensions.update(dimensions_by_candidate[candidate])
    return ForcedSubobjectStabilityScreen(
        len(grouped),
        len(records),
        tuple(zero),
        tuple(refuted),
        tuple(mixed),
        tuple(sorted(refuted_dimensions.items())),
        remaining,
        tuple(sorted(remaining_dimensions.items())),
    )


def write_forced_subobject_stability_screen(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed structural stability screen atomically."""

    payload = forced_subobject_stability_screen().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact forced-subobject stability screen."""

    payload = write_forced_subobject_stability_screen()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "coefficient_positive_no_go_family_count: "
        f"{payload['coefficient_positive_no_go_family_count']}"
    )
    print(f"remaining_family_count: {payload['remaining_family_count']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
