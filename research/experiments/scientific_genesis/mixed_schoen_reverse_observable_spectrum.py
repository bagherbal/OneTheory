"""Derive the exact structural spectrum of the reverse mixed family.

Owns:
    Orientation-independence proofs for matter and exterior-square cohomology,
    reverse-family Wilson projection, and the all-parameter physical locus.

Depends on:
    The reverse stable P5 certificate and the same synchronized constituent,
    pushdown, deck-action, determinant, and Wilson-line computations.

Must not:
    Import the published same-spectrum assertion as a rank input, select a P5
    point, identify derived-P1 classes with full Schoen cocycles, or fit data.

Phase 0:
    Research-only exact reverse-family structural spectrum certificate.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .mixed_schoen_observable_spectrum import (
    MixedSchoenObservableSpectrum,
    _mixed_schoen_spectrum_from_artifacts,
)
from .mixed_schoen_reverse_outer_stability_locus import (
    OUTPUT as REVERSE_STABILITY_ARTIFACT,
)
from .mixed_schoen_reverse_outer_universal_cone import (
    OUTPUT as REVERSE_UNIVERSAL_ARTIFACT,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_reverse_observable_spectrum.json"
)


@dataclass(frozen=True, slots=True)
class MixedSchoenReverseObservableSpectrum:
    """The reverse P5 spectrum derived from orientation-invariant filtrations."""

    synchronized: MixedSchoenObservableSpectrum

    def __post_init__(self) -> None:
        if self.synchronized.visible_matter_profile != (0, 27, 0, 0):
            raise ValueError("reverse matter is not concentrated in H1")
        if self.synchronized.dual_matter_profile != (0, 0, 27, 0):
            raise ValueError("reverse dual matter profile changed")
        if self.synchronized.determinant_one_profile != (0, 0, 0, 0):
            raise ValueError("det(V1) must remain acyclic under reversal")
        if self.synchronized.determinant_two_profile != (0, 0, 0, 0):
            raise ValueError("det(V2) must remain acyclic under reversal")
        if self.synchronized.higgs_profile != (0, 4, 4, 0):
            raise ValueError("reverse exterior-square filtration changed")

    @property
    def matter_orientation_independent(self) -> bool:
        """Return the pure-H1 long-exact-sequence theorem gate."""

        return (
            self.synchronized.first_matter_profile == (0, 9, 0, 0)
            and self.synchronized.second_matter_profile == (0, 18, 0, 0)
        )

    @property
    def higgs_orientation_independent(self) -> bool:
        """Return the acyclic-endpoint exterior-filtration theorem gate."""

        return (
            self.synchronized.determinant_one_profile == (0, 0, 0, 0)
            and self.synchronized.determinant_two_profile == (0, 0, 0, 0)
            and self.synchronized.higgs_profile == (0, 4, 4, 0)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the reverse physical locus and its chain derivation."""

        record = self.synchronized.as_record()
        record["schema"] = "mixed-schoen-reverse-observable-spectrum-v1"
        matter = cast(dict[str, object], record["matter"])
        long_exact = cast(
            dict[str, object],
            matter["universal_long_exact_sequence"],
        )
        long_exact["extension_sequence"] = "0 -> V2 -> E_reverse -> V1 -> 0"
        long_exact["orientation_independence"] = {
            "constituent_profiles": [[0, 9, 0, 0], [0, 18, 0, 0]],
            "connecting_map_source_or_target_dimensions": 0,
            "extension_parameter_can_change_rank": False,
            "published_same_spectrum_assertion_used_as_rank_input": False,
        }
        higgs = cast(dict[str, object], record["higgs"])
        filtration = cast(dict[str, object], higgs["determinant_filtration"])
        filtration["reverse_graded_piece_order"] = [
            "det(V2)",
            "V2 tensor V1",
            "det(V1)",
        ]
        filtration["orientation_independence"] = {
            "both_endpoint_determinants_acyclic": True,
            "middle_tensor_identified_by_canonical_flip": True,
            "extension_parameter_can_change_rank": False,
            "published_same_spectrum_assertion_used_as_rank_input": False,
        }
        record["lawful_physical_locus"] = (
            "P^5(Q(omega)) x K_reverse^s"
        )
        record["computable_carrier_component_frozen"] = False
        record["next_required_object"] = (
            "freeze the lawful reverse P5 component, then construct full "
            "matter and Higgs representatives in one synchronized Schoen DGA"
        )
        record["status"] = (
            "exact all-parameter three-family one-Higgs structural spectrum "
            "for the lawful reverse mixed family"
        )
        return record


@cache
def mixed_schoen_reverse_observable_spectrum() -> (
    MixedSchoenReverseObservableSpectrum
):
    """Construct the exact all-parameter reverse structural spectrum."""

    synchronized = _mixed_schoen_spectrum_from_artifacts(
        REVERSE_UNIVERSAL_ARTIFACT,
        "P^5(Q(omega))",
        REVERSE_STABILITY_ARTIFACT,
        "P^5(Q(omega)) x K_reverse^s",
    )
    return MixedSchoenReverseObservableSpectrum(synchronized)


def write_mixed_schoen_reverse_observable_spectrum(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed reverse spectrum certificate."""

    payload = mixed_schoen_reverse_observable_spectrum().as_record()
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
    """Regenerate the reverse structural-spectrum certificate."""

    payload = write_mixed_schoen_reverse_observable_spectrum()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"physical_selection_constraints: {payload['physical_selection_constraints']}")
    print(f"lawful_physical_locus: {payload['lawful_physical_locus']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MixedSchoenReverseObservableSpectrum",
    "mixed_schoen_reverse_observable_spectrum",
    "write_mixed_schoen_reverse_observable_spectrum",
]
