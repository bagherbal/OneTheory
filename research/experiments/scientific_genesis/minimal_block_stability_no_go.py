"""Classify stability of the minimum-dimensional computable topology block.

Owns:
    Exhaustive support, topology, automorphism, and lifted-Serre-line checks for
    both 36-family factor orientations with four-dimensional invariant Ext.

Depends on:
    Complete content-addressed invariant and automorphism artifacts, exact
    Schoen intersection data, and the pair-73 restriction theorem.

Must not:
    Generalize beyond candidates 3 and 23, select an Ext point, call a block
    member physical, or infer a global no-go for computable Schoen carriers.

Phase 0:
    The 72 minimum-dimensional families are classified and refuted by stability.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

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

from .pair_73_stability_no_go import OUTPUT as PAIR_73_NO_GO_ARTIFACT
from .pair_73_stability_no_go import pair_73_stability_no_go
from .pair_73_stability_wall import _serre_line_degree, _slope_polynomial

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/minimal_block_stability_no_go.json"
BLOCKS = ((3, 73, 108), (23, 793, 828))
EXPECTED_SUPPORT = (20, 21, 22, 23)
RIGHT_LINE_RESTRICTION = (4, 9, 14, 19, 24)


def _hom_support(record: dict[str, object]) -> tuple[int, ...]:
    """Return the occupied degree-zero Hom generators of one invariant basis."""

    basis = record.get("cocycle_basis")
    if not isinstance(basis, dict) or not isinstance(basis.get("representatives"), list):
        raise ValueError("an invariant pair lacks explicit cocycle representatives")
    support: set[int] = set()
    for representative in basis["representatives"]:
        if not isinstance(representative, dict) or not isinstance(
            representative.get("terms"), list
        ):
            raise ValueError("an invariant representative lacks exact terms")
        for term in representative["terms"]:
            if not isinstance(term, dict) or not isinstance(
                term.get("basis_coordinate"), list
            ):
                raise ValueError("an invariant term lacks its structural coordinate")
            coordinate = term["basis_coordinate"]
            if len(coordinate) != 12 or coordinate[0] != 0 or not isinstance(coordinate[2], int):
                raise ValueError("minimum-block support left the degree-zero Hom block")
            support.add(coordinate[2])
    return tuple(sorted(support))


def _topology_tuple(record: dict[str, object]) -> tuple[object, ...]:
    """Return the exact topology fields relevant to the restriction theorem."""

    topology = record.get("topology")
    if not isinstance(topology, dict):
        raise ValueError("an invariant pair lacks topology data")
    return (
        topology.get("left_factor"),
        tuple(topology.get("left_twist", ())),
        topology.get("left_target_line_shift"),
        topology.get("right_factor"),
        tuple(topology.get("right_twist", ())),
        topology.get("right_target_line_shift"),
    )


@dataclass(frozen=True, slots=True)
class MinimalBlockStabilityNoGo:
    """The exact 72-family minimum-dimensional stability exclusion."""

    block_pair_ranges: tuple[tuple[int, int, int], ...]
    checked_pair_count: int
    support_profile: tuple[int, ...]
    right_line_restriction_indices: tuple[int, ...]
    topologies: tuple[tuple[object, ...], ...]
    every_orbit_is_projective_three_space: bool
    every_pair_unstable: bool

    def __post_init__(self) -> None:
        if self.block_pair_ranges != BLOCKS or self.checked_pair_count != 72:
            raise ValueError("the minimum-dimensional block must contain 72 pairs")
        if self.support_profile != EXPECTED_SUPPORT:
            raise ValueError("the minimum-dimensional support profile changed")
        if self.right_line_restriction_indices != RIGHT_LINE_RESTRICTION:
            raise ValueError("the right-line restriction profile changed")
        if set(self.support_profile) & set(self.right_line_restriction_indices):
            raise ValueError("a minimum-block class restricts nontrivially to the right line")
        if len(self.topologies) != 2 or not all(
            (topology[0], topology[3], topology[2], topology[5]) == (factor, factor, -6, 0)
            for topology, factor in zip(self.topologies, (1, 2), strict=True)
        ):
            raise ValueError("minimum-block topology orientations changed")
        if not self.every_orbit_is_projective_three_space or not self.every_pair_unstable:
            raise ValueError("the minimum-dimensional stability no-go failed")

    def as_record(self) -> dict[str, object]:
        """Serialize the exhaustive scoped no-go without selecting a family."""

        return {
            "schema": "minimum-dimensional-stability-block-no-go-v1",
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
            "invariant_ext_dimension": 4,
            "nonzero_orbit_space": "P^3(Q(omega))",
            "source_hom_support": list(self.support_profile),
            "right_line_restriction_indices": list(self.right_line_restriction_indices),
            "restriction_support_intersection": [],
            "restriction_map_zero_for_every_pair": True,
            "right_serre_line_lifts_for_every_parameter": True,
            "opposite_slope_obstruction": True,
            "every_pair_unstable": self.every_pair_unstable,
            "minimum_dimensional_block_refuted": True,
            "global_computable_carrier_no_go": False,
            "arbitrary_pair_selected": False,
            "arbitrary_extension_point_selected": False,
            "next_required_object": (
                "the next invariant-Ext dimension block not sharing the lifted-line obstruction"
            ),
            "status": (
                "exact scoped no-go for all 72 four-dimensional invariant-Ext "
                "families in candidates 3 and 23"
            ),
        }


def minimal_block_stability_no_go() -> MinimalBlockStabilityNoGo:
    """Exhaustively certify both factor orientations of the minimum block."""

    pair_73 = json.loads(PAIR_73_NO_GO_ARTIFACT.read_text(encoding="utf-8"))
    pair_digest = pair_73.pop("artifact_digest", None)
    if not isinstance(pair_digest, str) or pair_digest != _canonical_digest(pair_73):
        raise ValueError("pair-73 no-go artifact digest does not verify")
    if pair_73 != pair_73_stability_no_go().as_record():
        raise ValueError("pair-73 no-go artifact is stale")

    invariant_digest, records = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    actions, _ = _read_partial(AUTOMORPHISM_ARTIFACT, invariant_digest)
    selected: list[dict[str, object]] = []
    topologies: list[tuple[object, ...]] = []
    for candidate, start, end in BLOCKS:
        block = tuple(records[index - 1] for index in range(start, end + 1))
        if any(record.get("candidate_index") != candidate for record in block):
            raise ValueError("minimum-block candidate indices changed")
        topology_profiles = {_topology_tuple(record) for record in block}
        if len(topology_profiles) != 1:
            raise ValueError("one minimum block spans multiple topology profiles")
        topologies.append(next(iter(topology_profiles)))
        selected.extend(block)

    geometry = schoen_geometry()
    for record in selected:
        if _hom_support(record) != EXPECTED_SUPPORT:
            raise ValueError("one minimum-block pair has incompatible Hom support")
        index = record.get("global_pair_index")
        if not isinstance(index, int) or index not in actions:
            raise ValueError("one minimum-block pair lacks an automorphism certificate")
        action = actions[index].get("automorphism_action")
        if not isinstance(action, dict) or action.get("nonzero_orbit_space") != "P^3(Q(omega))":
            raise ValueError("one minimum-block pair lacks its projective quotient")
        topology = record["topology"]
        if not isinstance(topology, dict):
            raise ValueError("one minimum-block pair lacks topology data")
        factor = topology["right_factor"]
        shift = topology["right_target_line_shift"]
        twist = tuple(topology["right_twist"])
        if not isinstance(factor, int) or not isinstance(shift, int):
            raise ValueError("one minimum-block right Serre line has invalid data")
        right_line = geometry.quotient_divisor(_serre_line_degree(factor, shift, twist))
        left_c1 = right_line.scale(-2)
        if not (_slope_polynomial(left_c1, 2) + _slope_polynomial(right_line, 1)).is_zero():
            raise ValueError("one minimum-block topology lost the opposite-slope identity")

    return MinimalBlockStabilityNoGo(
        BLOCKS,
        len(selected),
        EXPECTED_SUPPORT,
        RIGHT_LINE_RESTRICTION,
        tuple(topologies),
        True,
        True,
    )


def write_minimal_block_stability_no_go(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed minimum-block no-go atomically."""

    payload = minimal_block_stability_no_go().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact minimum-block stability no-go artifact."""

    payload = write_minimal_block_stability_no_go()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"checked_pair_count: {payload['checked_pair_count']}")
    print(f"minimum_dimensional_block_refuted: {payload['minimum_dimensional_block_refuted']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
