"""Freeze the viable alternate I6 carrier component without choosing a point.

Owns:
    A content-addressed computable-carrier component state kept distinct from
    the selected published reference carrier.

Depends on:
    The alternate all-parameter structural spectrum, cone, stability, and
    Hom-action certificates plus the existing immutable carrier-state type.

Must not:
    Freeze an extension coordinate, equate the alternate component with the
    source P3 ledger, or claim explicit cocycles or Yukawa matrices.

Phase 0:
    Research-only component freeze for the next common-DGA vertical slice.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .computable_one_theory_carrier_state import (
    ComputableOneTheoryCarrierState,
    PublishedReferenceCarrierState,
    published_reference_carrier_state,
)
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
GENERATED = ROOT / "data/generated/scientific_genesis"
OUTPUT = GENERATED / "alternate_constituent_carrier_state.json"
SPECTRUM = GENERATED / "alternate_constituent_structural_spectrum.json"
CONE = GENERATED / "alternate_constituent_outer_universal_cone.json"
STABILITY = GENERATED / "alternate_constituent_outer_stability_locus.json"


def alternate_constituent_carrier_state() -> tuple[
    PublishedReferenceCarrierState,
    ComputableOneTheoryCarrierState,
]:
    """Freeze only the exact component that passes charged-spectrum gates."""

    spectrum_digest, spectrum = _verified_payload(SPECTRUM)
    cone_digest, cone = _verified_payload(CONE)
    stability_digest, stability = _verified_payload(STABILITY)
    prerequisites = cast(dict[str, str], spectrum["prerequisite_artifact_digests"])
    projection = cast(dict[str, object], spectrum["observable_wilson_projection"])
    chern = cast(dict[str, object], cone["chern_classes"])
    structure = cast(dict[str, object], stability["structure_group"])
    if (
        spectrum.get("schema") != "alternate-constituent-structural-spectrum-v1"
        or spectrum.get("parameter_locus") != "P^1(Q(omega)) x K^s"
        or spectrum.get("every_nonzero_extension_parameter") is not True
        or spectrum.get("arbitrary_extension_point_selected") is not False
        or spectrum.get("observable_charged_structural_spectrum_passes") is not True
        or spectrum.get("explicit_cone_matter_cocycles_computed") is not False
        or spectrum.get("explicit_cone_higgs_cocycles_computed") is not False
        or prerequisites.get("alternate_cone") != cone_digest
        or prerequisites.get("alternate_stability") != stability_digest
        or not prerequisites.get("alternate_hom_actions")
        or projection
        != {
            "families": 3,
            "right_handed_neutrinos": 3,
            "anti_families": 0,
            "higgs_pairs": 1,
            "massless_color_triplets": 0,
            "charged_exotic_blocks_from_16_and_10": 0,
        }
        or cone.get("rank") != 4
        or cone.get("quotient_determinant_trivial_exact") is not True
        or chern.get("c3") != "-6"
        or structure.get("cover_c3") != "-54"
        or structure.get("genuine_su4_on_certified_locus") is not True
    ):
        raise ValueError("the alternate component has not passed its freeze gates")
    reference = published_reference_carrier_state(prerequisites["published_wilson_source"])
    computable = ComputableOneTheoryCarrierState(
        "alternate-i6-ray-0-1-P1",
        "P^1(Q(omega))",
        "K^s",
        "Q(omega)",
        spectrum_digest,
        cone_digest,
        stability_digest,
        "",
        4,
        "trivial",
        -54,
        -6,
        "SU(4)",
        (
            "the only current stable determinant-trivial component passing "
            "the fixed structural-spectrum gates; retain its whole P1 "
            "without ranking extension coordinates"
        ),
        True,
        False,
        "COMPUTED",
        prerequisites["alternate_hom_actions"],
    )
    return reference, computable


def write_alternate_constituent_carrier_state(path: Path = OUTPUT) -> dict[str, object]:
    """Write the reference-separated, content-addressed component freeze."""

    reference, computable = alternate_constituent_carrier_state()
    payload: dict[str, object] = {
        "schema": "alternate-constituent-carrier-state-v1",
        "published_reference_carrier_state": reference.as_record(),
        "computable_one_theory_carrier_state": computable.as_record(),
        "states_are_distinct": True,
        "source_p3_to_alternate_p1_equivalence_claimed": False,
        "selected_constraints_not_predictions": True,
        "physical_yukawas_available": False,
        "full_vacuum_consistency_established": False,
        "status": "alternate structural carrier component frozen for chain-level work",
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_constituent_carrier_state()
    print(f"artifact_digest: {report['artifact_digest']}")
    print("component_id: alternate-i6-ray-0-1-P1")
