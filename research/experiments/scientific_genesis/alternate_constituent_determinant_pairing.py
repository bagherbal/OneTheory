"""Certify the determinant pairing of the frozen alternate I6 constituent.

Owns:
    Complementary-minor forms on its six affine charts and their exact
    hypersurface-corrected overlap covariance.

Depends on:
    The frozen alternate ray, certified atlas, and exact Laurent arithmetic.

Must not:
    Reuse the selected I6 pairing, identify a Hom cochain with a tensor
    cocycle, or claim an exterior-cone Higgs lift or Yukawa entry.

Phase 0:
    Research-only local input to the unresolved rank-two chain map.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA
from onetheory.math.sheaves import LaurentMatrix
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .alternate_constituent_deck_atlases import OUTPUT as ATLAS
from .alternate_constituent_outer_universal_cone import OUTPUT as CONE
from .alternate_constituent_up_matter_representatives import CARRIER
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_schoen_determinant_pairing import (
    _adjusted_relation,
    _is_zero,
    _matrix_difference,
    _matrix_digest,
    _matrix_scale,
    _pairing_hypersurface_quotient,
    _transpose,
    plucker_pairing,
)
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions
from .published_constituent_full_cech import published_constituent_full_cech
from .published_constituent_overlap_transitions import (
    _atlas,
    _hypersurface_equation,
    _relation_columns,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_constituent_determinant_pairing.json"


def alternate_constituent_determinant_pairing() -> dict[str, object]:
    """Check the actual alternate quotient form on every chart and overlap."""

    carrier_digest, carrier = _verified_payload(CARRIER)
    cone_digest, _cone = _verified_payload(CONE)
    atlas_digest, atlas_record = _verified_payload(ATLAS)
    state = cast(dict[str, object], carrier["computable_one_theory_carrier_state"])
    certificates = cast(dict[str, object], state["certificate_digests"])
    cases = cast(list[dict[str, object]], atlas_record["cases"])
    matching = [
        case for case in cases if case["ray_character_exponents"] == [0, 1]
    ]
    if (
        carrier.get("schema") != "alternate-constituent-carrier-state-v1"
        or state.get("component_id") != "alternate-i6-ray-0-1-P1"
        or state.get("frozen") is not True
        or certificates.get("universal_cone") != cone_digest
        or atlas_record.get("schema") != "alternate-constituent-deck-atlases-v1"
        or atlas_record.get("alternate_constituent_atlases_exact") is not True
        or len(matching) != 1
        or matching[0]["overlap_exact"] is not True
    ):
        raise ValueError("the frozen alternate determinant premises changed")

    alternate = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    atlas = _atlas(alternate)
    if matching[0]["overlap_digest"] != _canonical_digest(atlas.as_record()):
        raise ValueError("the alternate local pairing uses a different atlas")
    selected = published_constituent_full_cech()[1]
    charts = {item.source.name: item.source for item in atlas.transitions}
    pairings: dict[str, LaurentMatrix] = {}
    different_from_selected = 0
    for name, chart in sorted(charts.items()):
        relation = _relation_columns(alternate, chart)
        pairing = plucker_pairing(relation)
        if relation.shape != (5, 3) or pairing.shape != (5, 5):
            raise ValueError("the alternate rank-two presentation changed")
        if all(not entry.terms for row in pairing.rows for entry in row):
            raise ValueError("the alternate determinant pairing vanished on a chart")
        if not _is_zero(_transpose(relation).compose(pairing)):
            raise ValueError("the alternate pairing does not annihilate relations")
        if any(
            pairing.rows[row][column] != -pairing.rows[column][row]
            for row in range(5) for column in range(5)
        ):
            raise ValueError("the alternate pairing is not alternating")
        different_from_selected += pairing != plucker_pairing(
            _relation_columns(selected, chart)
        )
        pairings[name] = pairing

    equation = _hypersurface_equation(alternate)
    for transition in atlas.transitions:
        source_relation = _relation_columns(alternate, transition.source)
        target_relation = _relation_columns(alternate, transition.target)
        adjusted = _adjusted_relation(source_relation, transition, equation)
        quotient = _pairing_hypersurface_quotient(source_relation, transition)
        source_pairing = pairings[transition.source.name]
        target_pairing = pairings[transition.target.name]
        if (
            transition.transition.compose(target_relation) != adjusted
            or _matrix_difference(plucker_pairing(adjusted), source_pairing)
            != _matrix_scale(quotient, equation)
            or _transpose(transition.transition)
            .compose(plucker_pairing(adjusted))
            .compose(transition.transition) != target_pairing
        ):
            raise ValueError("the alternate pairing fails corrected overlap covariance")
    if len(charts) != 6 or len(atlas.transitions) != 30 or not different_from_selected:
        raise ValueError("the alternate pairing did not separate from the selected ray")

    return {
        "schema": "alternate-constituent-determinant-pairing-v1",
        "coefficient_field": "Q(omega)",
        "ray_character_exponents": [0, 1],
        "middle_rank": 5,
        "relation_rank": 3,
        "chart_count": len(charts),
        "overlap_count": len(atlas.transitions),
        "charts_different_from_selected_ray": different_from_selected,
        "chart_pairing_digests": {
            name: _matrix_digest(pairing) for name, pairing in sorted(pairings.items())
        },
        "relation_annihilation_exact": True,
        "alternating_exact": True,
        "hypersurface_factorization_exact": True,
        "corrected_overlap_covariance_exact": True,
        "prerequisite_artifact_digests": {
            "frozen_carrier": carrier_digest,
            "universal_cone": cone_digest,
            "alternate_atlas": atlas_digest,
        },
        "hom_to_tensor_chain_map_constructed": False,
        "exterior_cone_higgs_cocycle_constructed": False,
        "next_required_object": (
            "an Alexander-Whitney-compatible rank-two Hom-to-tensor chain map "
            "using this alternate determinant pairing"
        ),
    }


def write_alternate_constituent_determinant_pairing(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the exact local pairing audit with content-addressed provenance."""

    payload = alternate_constituent_determinant_pairing()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    record = write_alternate_constituent_determinant_pairing()
    print(f"artifact_digest: {record['artifact_digest']}")
    print(f"charts_different_from_selected_ray: {record['charts_different_from_selected_ray']}")
