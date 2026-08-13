"""Classify stability of the next computable topology block.

Owns:
    Exhaustive lifted-right-line and positive-slope checks for the 72 six- and
    eight-dimensional invariant-Ext families in candidates 14 and 34.

Depends on:
    Complete invariant and automorphism artifacts, the published Kahler cone,
    exact Schoen intersections, and the chain-level restriction theorem.

Must not:
    Generalize beyond candidates 14 and 34, select an Ext point, infer a global
    carrier no-go, or replace exact positivity with sampled polarizations.

Phase 0:
    The next 72-family topology block is refuted exactly by slope stability.
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

from .minimal_block_stability_no_go import (
    _topology_tuple,
)
from .pair_73_stability_wall import _serre_line_degree, _slope_polynomial

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/next_block_stability_no_go.json"
BLOCKS = ((14, 469, 504), (34, 1189, 1224))
EXPECTED_DIMENSIONS = Counter({6: 36, 8: 36})
PARENT_DEGREE = -1
RIGHT_LINE_RESTRICTION = (4, 9, 14, 19)
EXPECTED_SUPPORTS = (
    (0, 1, 3, 5, 6, 8, 10, 11, 13),
    (0, 2, 3, 5, 7, 8, 10, 12, 13),
    (0, 1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13),
)


def _parent_minus_one_support(record: dict[str, object]) -> tuple[int, ...]:
    """Return the typed Hom-minus-one support of one invariant Ext basis."""

    basis = record.get("cocycle_basis")
    if not isinstance(basis, dict) or not isinstance(basis.get("representatives"), list):
        raise ValueError("a next-block pair lacks explicit cocycle representatives")
    support: set[int] = set()
    for representative in basis["representatives"]:
        if not isinstance(representative, dict) or not isinstance(
            representative.get("terms"), list
        ):
            raise ValueError("a next-block representative lacks exact terms")
        for term in representative["terms"]:
            if not isinstance(term, dict) or not isinstance(
                term.get("basis_coordinate"), list
            ):
                raise ValueError("a next-block term lacks its structural coordinate")
            coordinate = term["basis_coordinate"]
            if (
                len(coordinate) != 12
                or coordinate[0] != PARENT_DEGREE
                or not isinstance(coordinate[2], int)
            ):
                raise ValueError("next-block support left the typed Hom-minus-one block")
            support.add(coordinate[2])
    return tuple(sorted(support))


def _positive_right_line_slope() -> Polynomial:
    """Return the exact common slope polynomial in the first factor orientation."""

    geometry = schoen_geometry()
    right_line = geometry.quotient_divisor((5, 1, -1))
    return _slope_polynomial(right_line, 1)


@dataclass(frozen=True, slots=True)
class NextBlockStabilityNoGo:
    """The exact positive-slope exclusion for candidates 14 and 34."""

    block_pair_ranges: tuple[tuple[int, int, int], ...]
    checked_pair_count: int
    dimension_counts: tuple[tuple[int, int], ...]
    support_profiles: tuple[tuple[int, ...], ...]
    right_line_restriction_indices: tuple[int, ...]
    topologies: tuple[tuple[object, ...], ...]
    first_orientation_slope: Polynomial

    def __post_init__(self) -> None:
        if self.block_pair_ranges != BLOCKS or self.checked_pair_count != 72:
            raise ValueError("the next topology block must contain 72 pairs")
        if Counter(dict(self.dimension_counts)) != EXPECTED_DIMENSIONS:
            raise ValueError("the next topology block changed Ext dimensions")
        if self.support_profiles != EXPECTED_SUPPORTS:
            raise ValueError("the next topology block changed Hom support profiles")
        if self.right_line_restriction_indices != RIGHT_LINE_RESTRICTION:
            raise ValueError("the next topology block changed restriction columns")
        if any(
            set(support) & set(self.right_line_restriction_indices)
            for support in self.support_profiles
        ):
            raise ValueError("a next-block class restricts nontrivially to its right line")
        expected = Polynomial(
            {
                (2, 0, 0): Rational(1, 3),
                (1, 1, 0): Rational(2),
                (1, 0, 1): Rational(2),
                (0, 2, 0): Rational(5, 3),
                (0, 1, 1): Rational(10),
            },
            variable_count=3,
        )
        if self.first_orientation_slope != expected:
            raise ValueError("the next-block right-line slope identity failed")
        if any(coefficient <= 0 for _, coefficient in self.first_orientation_slope.terms):
            raise ValueError("the next-block right-line slope is not coefficient-positive")

    def as_record(self) -> dict[str, object]:
        """Serialize the exhaustive block no-go without a sampled polarization."""

        return {
            "schema": "next-topology-block-stability-no-go-v1",
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
            "source_hom_support_profiles": [list(profile) for profile in self.support_profiles],
            "source_parent_hom_degree": PARENT_DEGREE,
            "source_parent_hom_type": "Hom(F0_right,F1_left)",
            "right_line_restriction_indices": list(self.right_line_restriction_indices),
            "all_restriction_support_intersections_empty": True,
            "right_serre_line_lifts_for_every_parameter": True,
            "restriction_chain_argument": (
                "precomposition with L_right -> F0_right selects Hom^-1 indices "
                "4,9,14,19, absent from every source basis; the structural "
                "differential commutes with precomposition and the Cech "
                "contraction preserves Hom components"
            ),
            "first_orientation_right_line_c1": ["5", "1", "-1"],
            "factor_exchanged_right_line_c1": ["1", "5", "-1"],
            "first_orientation_right_line_slope": [
                {"exponents": list(exponents), "coefficient": str(coefficient)}
                for exponents, coefficient in self.first_orientation_slope.terms
            ],
            "factor_exchanged_slope_rule": "exchange j1 and j2",
            "strictly_positive_on_kahler_cone": True,
            "positivity_proof": (
                "every displayed coefficient is positive and the published "
                "Kahler cone has j1,j2,j3 > 0"
            ),
            "every_pair_unstable": True,
            "next_topology_block_refuted": True,
            "global_computable_carrier_no_go": False,
            "arbitrary_pair_selected": False,
            "arbitrary_extension_point_selected": False,
            "sampled_polarization_used": False,
            "status": (
                "exact scoped no-go for all 72 six- and eight-dimensional "
                "invariant-Ext families in candidates 14 and 34"
            ),
        }


def next_block_stability_no_go() -> NextBlockStabilityNoGo:
    """Exhaustively certify the next two factor-exchanged topology blocks."""

    invariant_digest, records = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    actions, _ = _read_partial(AUTOMORPHISM_ARTIFACT, invariant_digest)
    selected: list[dict[str, object]] = []
    topologies: list[tuple[object, ...]] = []
    supports: set[tuple[int, ...]] = set()
    dimensions: Counter[int] = Counter()
    for candidate, start, end in BLOCKS:
        block = tuple(records[index - 1] for index in range(start, end + 1))
        if any(record.get("candidate_index") != candidate for record in block):
            raise ValueError("next-block candidate indices changed")
        topology_profiles = {_topology_tuple(record) for record in block}
        if len(topology_profiles) != 1:
            raise ValueError("one next block spans multiple topology profiles")
        topologies.append(next(iter(topology_profiles)))
        selected.extend(block)

    geometry = schoen_geometry()
    for record in selected:
        support = _parent_minus_one_support(record)
        supports.add(support)
        invariant = record.get("invariant_subcomplex")
        if not isinstance(invariant, dict) or not isinstance(
            invariant.get("invariant_ext_one_dimension"), int
        ):
            raise ValueError("one next-block pair lacks its invariant dimension")
        dimensions[invariant["invariant_ext_one_dimension"]] += 1
        index = record.get("global_pair_index")
        if not isinstance(index, int) or index not in actions:
            raise ValueError("one next-block pair lacks an automorphism certificate")
        action = actions[index].get("automorphism_action")
        expected_orbit = f"P^{invariant['invariant_ext_one_dimension'] - 1}(Q(omega))"
        if not isinstance(action, dict) or action.get("nonzero_orbit_space") != expected_orbit:
            raise ValueError("one next-block pair lacks its exact projective quotient")
        topology = record.get("topology")
        if not isinstance(topology, dict):
            raise ValueError("one next-block pair lacks topology data")
        factor = topology.get("right_factor")
        shift = topology.get("right_target_line_shift")
        twist = topology.get("right_twist")
        if not (
            isinstance(factor, int)
            and isinstance(shift, int)
            and isinstance(twist, list)
            and len(twist) == 3
        ):
            raise ValueError("one next-block right Serre line has invalid data")
        line = geometry.quotient_divisor(_serre_line_degree(factor, shift, tuple(twist)))
        slope = _slope_polynomial(line, 1)
        if any(coefficient <= 0 for _, coefficient in slope.terms):
            raise ValueError("one next-block right-line slope is not strictly positive")

    return NextBlockStabilityNoGo(
        BLOCKS,
        len(selected),
        tuple(sorted(dimensions.items())),
        tuple(sorted(supports, key=lambda profile: (len(profile), profile))),
        RIGHT_LINE_RESTRICTION,
        tuple(topologies),
        _positive_right_line_slope(),
    )


def write_next_block_stability_no_go(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed next-block no-go atomically."""

    payload = next_block_stability_no_go().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact next-block stability no-go artifact."""

    payload = write_next_block_stability_no_go()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"checked_pair_count: {payload['checked_pair_count']}")
    print(f"next_topology_block_refuted: {payload['next_topology_block_refuted']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
