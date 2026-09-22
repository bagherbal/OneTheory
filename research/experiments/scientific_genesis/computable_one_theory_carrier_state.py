"""Freeze the first lawful computable Schoen carrier component.

Owns:
    A source-reference record and a separate immutable computational carrier
    component bound to exact algebraic, stability, and spectrum certificates.

Depends on:
    The lawful mixed-family observable-spectrum artifact and published source
    provenance already admitted by the carrier reconstruction.

Must not:
    Select an extension point, equate the lawful P1 with the source P3 ledger,
    claim full DGA representatives, or promote unresolved physical couplings.

Phase 0:
    Research-only carrier-component freeze before common-DGA construction.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT / "data/generated/scientific_genesis/computable_one_theory_carrier_state.json"
)
SPECTRUM_ARTIFACT = (
    ROOT / "data/generated/scientific_genesis/mixed_schoen_observable_spectrum.json"
)


def _verified_spectrum_artifact(
    path: Path,
    schema: str,
    lawful_locus: str,
) -> tuple[str, dict[str, object]]:
    """Validate one lawful spectrum artifact and every selection gate."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError("the lawful spectrum artifact digest does not verify")
    if payload.get("schema") != schema:
        raise ValueError("the lawful spectrum schema changed")
    if payload.get("lawful_physical_locus") != lawful_locus:
        raise ValueError("the lawful physical locus changed")
    if payload.get("entire_stable_family_passes_structural_spectrum") is not True:
        raise ValueError("the lawful family no longer passes the structural spectrum")
    constraints = payload.get("physical_selection_constraints")
    if not isinstance(constraints, dict):
        raise ValueError("the lawful spectrum lacks selection constraints")
    required = (
        "three_families",
        "three_right_handed_neutrinos",
        "one_higgs_pair",
        "zero_anti_families",
        "zero_exotic_massless_blocks",
    )
    if any(constraints.get(key) is not True for key in required):
        raise ValueError("a required structural spectrum gate failed")
    if constraints.get("used_as_construction_inputs") is not False:
        raise ValueError("selection constraints leaked into spectrum construction")
    return digest, cast(dict[str, object], payload)


def _verified_spectrum() -> tuple[str, dict[str, object]]:
    """Validate the original lawful P1 spectrum artifact."""

    return _verified_spectrum_artifact(
        SPECTRUM_ARTIFACT,
        "mixed-schoen-observable-spectrum-v1",
        "P^1(Q(omega)) x K^s",
    )


@dataclass(frozen=True, slots=True)
class PublishedReferenceCarrierState:
    """The selected source carrier kept distinct from executable reconstruction."""

    arxiv_id: str
    version: str
    source_archive_sha256: str
    source_parameter_ledger: str
    epistemic_status: str

    def __post_init__(self) -> None:
        if (
            self.arxiv_id != "hep-th/0512177"
            or self.version != "v3"
            or self.epistemic_status != "SELECTED"
        ):
            raise ValueError("the published reference identity changed")

    def as_record(self) -> dict[str, object]:
        """Serialize the source reference without an equivalence claim."""

        return {
            "arxiv_id": self.arxiv_id,
            "version": self.version,
            "source_archive_sha256": self.source_archive_sha256,
            "source_parameter_ledger": self.source_parameter_ledger,
            "epistemic_status": self.epistemic_status,
            "equated_with_computable_component": False,
        }


@dataclass(frozen=True, slots=True)
class ComputableOneTheoryCarrierState:
    """The frozen connected family accepted for vertical computation."""

    component_id: str
    parameter_component: str
    kahler_chamber: str
    coefficient_field: str
    spectrum_artifact_digest: str
    universal_cone_artifact_digest: str
    stability_artifact_digest: str
    pushdown_artifact_digest: str
    rank: int
    determinant: str
    cover_c3: int
    quotient_c3: int
    structure_group: str
    freeze_rule: str
    frozen: bool
    representative_selected: bool
    epistemic_status: str

    def __post_init__(self) -> None:
        valid_components = {
            (
                "lawful-mixed-schoen-P1",
                "P^1(Q(omega))",
                "K^s",
            ),
            (
                "lawful-mixed-schoen-reverse-P5",
                "P^5(Q(omega))",
                "K_reverse^s",
            ),
        }
        if (
            (self.component_id, self.parameter_component, self.kahler_chamber)
            not in valid_components
            or self.coefficient_field != "Q(omega)"
            or not self.freeze_rule
        ):
            raise ValueError("the frozen computational component changed")
        if (
            self.rank != 4
            or self.determinant != "trivial"
            or self.cover_c3 != -54
            or self.quotient_c3 != -6
            or self.structure_group != "SU(4)"
        ):
            raise ValueError("the frozen carrier topology or structure group changed")
        if not self.frozen or self.representative_selected:
            raise ValueError("freeze the component without selecting a point")
        if self.epistemic_status != "COMPUTED":
            raise ValueError("the computable carrier must retain COMPUTED status")
        if not all(
            (
                self.spectrum_artifact_digest,
                self.universal_cone_artifact_digest,
                self.stability_artifact_digest,
                self.pushdown_artifact_digest,
            )
        ):
            raise ValueError("the computable carrier requires all certificate digests")

    def as_record(self) -> dict[str, object]:
        """Serialize the frozen component and its remaining computational boundary."""

        return {
            "component_id": self.component_id,
            "parameter_component": self.parameter_component,
            "kahler_chamber": self.kahler_chamber,
            "coefficient_field": self.coefficient_field,
            "certificate_digests": {
                "observable_spectrum": self.spectrum_artifact_digest,
                "universal_cone": self.universal_cone_artifact_digest,
                "stable_su4_locus": self.stability_artifact_digest,
                "relative_pushdowns": self.pushdown_artifact_digest,
            },
            "rank": self.rank,
            "determinant": self.determinant,
            "chern_data": {"cover_c3": self.cover_c3, "quotient_c3": self.quotient_c3},
            "structure_group": self.structure_group,
            "structural_spectrum": {
                "families": 3,
                "right_handed_neutrinos": 3,
                "higgs_pairs": 1,
                "anti_families": 0,
                "massless_color_triplets": 0,
                "exotic_massless_blocks": 0,
            },
            "freeze_rule": self.freeze_rule,
            "frozen": self.frozen,
            "representative_selected": self.representative_selected,
            "epistemic_status": self.epistemic_status,
            "conditional_on": [
                "selected heterotic UV framework",
                "selected published Schoen geometry and Wilson embedding",
            ],
            "full_common_dga_representatives_available": False,
            "next_required_object": (
                "parameter-dependent matter and Higgs lifts in one common Schoen DGA"
            ),
        }


def published_reference_carrier_state(
    source_archive_sha256: str,
) -> PublishedReferenceCarrierState:
    """Return the selected published reference ledger."""

    return PublishedReferenceCarrierState(
        "hep-th/0512177",
        "v3",
        source_archive_sha256,
        "generic nonzero invariant Ext in source P^3 ledger",
        "SELECTED",
    )


def computable_one_theory_carrier_state() -> tuple[
    PublishedReferenceCarrierState,
    ComputableOneTheoryCarrierState,
]:
    """Freeze the lawful physical P1 component from verified certificates."""

    spectrum_digest, spectrum = _verified_spectrum()
    source = cast(dict[str, object], spectrum["source"])
    prerequisites = cast(
        dict[str, str],
        spectrum["prerequisite_artifact_digests"],
    )
    reference = published_reference_carrier_state(
        cast(str, source["source_archive_sha256"])
    )
    computable = ComputableOneTheoryCarrierState(
        "lawful-mixed-schoen-P1",
        "P^1(Q(omega))",
        "K^s",
        "Q(omega)",
        spectrum_digest,
        prerequisites["universal_cone"],
        prerequisites["stable_su4_locus"],
        prerequisites["relative_pushdowns"],
        4,
        "trivial",
        -54,
        -6,
        "SU(4)",
        (
            "the unique currently derived lawful physical connected component; "
            "no phenomenological ranking among extension points"
        ),
        True,
        False,
        "COMPUTED",
    )
    return reference, computable


def write_computable_one_theory_carrier_state(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed frozen carrier-component state."""

    reference, computable = computable_one_theory_carrier_state()
    payload: dict[str, object] = {
        "schema": "computable-one-theory-carrier-state-v1",
        "published_reference_carrier_state": reference.as_record(),
        "computable_one_theory_carrier_state": computable.as_record(),
        "states_are_distinct": True,
        "source_p3_to_lawful_p1_equivalence_claimed": False,
        "status": "first lawful physical carrier component frozen for vertical computation",
    }
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
    """Regenerate the frozen computable carrier-component artifact."""

    payload = write_computable_one_theory_carrier_state()
    state = cast(dict[str, object], payload["computable_one_theory_carrier_state"])
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"component_id: {state['component_id']}")
    print(f"next_required_object: {state['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ComputableOneTheoryCarrierState",
    "PublishedReferenceCarrierState",
    "computable_one_theory_carrier_state",
    "published_reference_carrier_state",
    "write_computable_one_theory_carrier_state",
]
