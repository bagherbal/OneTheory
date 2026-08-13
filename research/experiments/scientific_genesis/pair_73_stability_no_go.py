"""Prove the pair-73 slope-stable locus is empty.

Owns:
    Exact restriction of the universal outer Ext family to the right Serre line,
    the resulting lifted line subbundle, and the opposite-slope instability proof.

Depends on:
    The pair-73 source, chain-level presentation structure, algebraic lawful
    locus, necessary slope walls, and exact quotient intersection arithmetic.

Must not:
    Generalize the no-go beyond pair 73, infer proper structure-group reduction,
    select an extension point or polarization, or claim a global carrier no-go.

Phase 0:
    Pair-73 stability is refuted exactly; other computable families remain open.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from onetheory.math.geometry import Divisor
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .pair_73_cech_lift import _pair_structure
from .pair_73_lawful_locus import OUTPUT as LAWFUL_ARTIFACT
from .pair_73_lawful_locus import pair_73_algebraic_locus
from .pair_73_source import OUTPUT as SOURCE_ARTIFACT
from .pair_73_stability_wall import OUTPUT as WALL_ARTIFACT
from .pair_73_stability_wall import (
    PAIR_INDEX,
    _serre_line_degree,
    _slope_polynomial,
    pair_73_stability_wall,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/pair_73_stability_no_go.json"


def _validated_artifact(path: Path) -> dict[str, object]:
    """Return one exact content-addressed JSON artifact."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"artifact digest does not verify: {path.name}")
    return payload


def _right_line(source: dict[str, object]) -> Divisor:
    """Derive the right constituent's Serre line from exact topology data."""

    pair = source.get("pair")
    if not isinstance(pair, dict) or not isinstance(pair.get("topology"), dict):
        raise ValueError("pair-73 source topology is unavailable")
    topology = pair["topology"]
    factor = topology.get("right_factor")
    shift = topology.get("right_target_line_shift")
    twist = topology.get("right_twist")
    if not (
        isinstance(factor, int)
        and isinstance(shift, int)
        and isinstance(twist, list)
        and len(twist) == 3
        and all(isinstance(value, int) for value in twist)
    ):
        raise ValueError("pair-73 right Serre line data have invalid types")
    return schoen_geometry().quotient_divisor(
        _serre_line_degree(factor, shift, tuple(twist))
    )


def _source_hom_support(source: dict[str, object]) -> tuple[int, ...]:
    """Return all degree-zero Hom generators occupied by the Ext basis."""

    pair = source.get("pair")
    if not isinstance(pair, dict) or not isinstance(pair.get("cocycle_basis"), dict):
        raise ValueError("pair-73 cocycle basis is unavailable")
    representatives = pair["cocycle_basis"].get("representatives")
    if not isinstance(representatives, list) or len(representatives) != 4:
        raise ValueError("pair-73 requires four exact representatives")
    support: set[int] = set()
    for representative in representatives:
        if not isinstance(representative, dict) or not isinstance(
            representative.get("terms"), list
        ):
            raise ValueError("pair-73 representative terms are unavailable")
        for term in representative["terms"]:
            if not isinstance(term, dict) or not isinstance(
                term.get("basis_coordinate"), list
            ):
                raise ValueError("pair-73 basis coordinate is unavailable")
            coordinate = term["basis_coordinate"]
            if len(coordinate) != 12 or coordinate[0] != 0 or not isinstance(coordinate[2], int):
                raise ValueError("pair-73 class left the degree-zero Hom summand")
            support.add(coordinate[2])
    return tuple(sorted(support))


@dataclass(frozen=True, slots=True)
class Pair73StabilityNoGo:
    """The family-wide lifted-line and opposite-slope obstruction."""

    source_hom_support: tuple[int, ...]
    right_line_restriction_indices: tuple[int, ...]
    left_slope: Polynomial
    lifted_right_line_slope: Polynomial

    def __post_init__(self) -> None:
        if self.source_hom_support != (20, 21, 22, 23):
            raise ValueError("pair-73 Ext support has changed")
        if self.right_line_restriction_indices != (4, 9, 14, 19, 24):
            raise ValueError("pair-73 right-line restriction columns have changed")
        if set(self.source_hom_support) & set(self.right_line_restriction_indices):
            raise ValueError("pair-73 unexpectedly restricts nontrivially to the right line")
        if not (self.left_slope + self.lifted_right_line_slope).is_zero():
            raise ValueError("the forced pair-73 subbundles no longer have opposite slopes")

    def as_record(self) -> dict[str, object]:
        """Serialize the exact scoped no-go and its fail-closed boundary."""

        return {
            "schema": "pair-73-stability-no-go-v1",
            "global_pair_index": PAIR_INDEX,
            "outer_extension_sequence": "0 -> V_left -> V(a) -> V_right -> 0",
            "right_serre_sequence": (
                "0 -> L_right -> V_right -> I_right tensor M_right -> 0"
            ),
            "right_line_first_chern": ["-1", "1", "0"],
            "right_presentation_target_rank": 5,
            "right_line_generator_index": 4,
            "right_line_restriction_indices": list(self.right_line_restriction_indices),
            "source_hom_support": list(self.source_hom_support),
            "restriction_support_intersection": [],
            "restriction_map_zero_on_every_ext_basis_class": True,
            "restriction_map_zero_on_universal_family": True,
            "restriction_chain_argument": (
                "precomposition with the right Serre line keeps only Hom^0 "
                "columns 4,9,14,19,24; every source class uses columns "
                "20,21,22,23, and Cech/Koszul descent preserves those Hom^0 "
                "indices while Hom^1 terms vanish under the line inclusion"
            ),
            "pullback_extension_splits_for_all_parameters": True,
            "lifted_subbundle": "L_right -> V(a)",
            "opposite_slope_identity": "mu(L_right) = -mu(V_left)",
            "stability_logic": (
                "if mu(V_left)>0 then V_left destabilizes; if mu(V_left)<0 "
                "then lifted L_right destabilizes; if mu(V_left)=0 strict "
                "slope stability fails"
            ),
            "affine_slope_stable_locus": "empty",
            "projective_slope_stable_locus": "empty",
            "all_pair_73_parameters_unstable": True,
            "pair_73_computable_carrier_route_refuted": True,
            "proper_structure_group_reduction_computed": False,
            "global_schoen_carrier_no_go": False,
            "arbitrary_extension_point_selected": False,
            "arbitrary_polarization_selected": False,
            "status": (
                "exact scoped no-go: pair 73 has no slope-stable parameter at "
                "any Kahler polarization"
            ),
        }


def pair_73_stability_no_go() -> Pair73StabilityNoGo:
    """Construct the exact pair-73 family-wide instability certificate."""

    source = _validated_artifact(SOURCE_ARTIFACT)
    lawful = _validated_artifact(LAWFUL_ARTIFACT)
    wall = _validated_artifact(WALL_ARTIFACT)
    if lawful != pair_73_algebraic_locus().as_record():
        raise ValueError("pair-73 lawful-locus artifact is stale")
    if wall != pair_73_stability_wall().as_record():
        raise ValueError("pair-73 stability-wall artifact is stale")

    structure = _pair_structure()
    right_target_rank = len(structure.parent.right.target_shifts)
    left_target_rank = len(structure.parent.left.target_shifts)
    if right_target_rank != 5 or left_target_rank != 5:
        raise ValueError("pair-73 target presentations no longer have rank five")
    right_line_index = right_target_rank - 1
    restriction_indices = tuple(
        target * right_target_rank + right_line_index
        for target in range(left_target_rank)
    )
    source_support = _source_hom_support(source)
    if any(index >= left_target_rank * right_target_rank for index in source_support):
        raise ValueError("pair-73 source support left the Hom^0 target block")

    left = schoen_geometry().quotient_divisor(
        pair_73_algebraic_locus().left_first_chern
    )
    right_line = _right_line(source)
    return Pair73StabilityNoGo(
        source_support,
        restriction_indices,
        _slope_polynomial(left, 2),
        _slope_polynomial(right_line, 1),
    )


def write_pair_73_stability_no_go(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed pair-73 no-go certificate atomically."""

    payload = pair_73_stability_no_go().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact pair-73 stability no-go artifact."""

    payload = write_pair_73_stability_no_go()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"projective_slope_stable_locus: {payload['projective_slope_stable_locus']}")
    print(f"global_schoen_carrier_no_go: {payload['global_schoen_carrier_no_go']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
