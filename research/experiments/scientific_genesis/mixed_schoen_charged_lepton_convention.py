"""Relabel the exact forward-sector matrix as physical charged leptons.

Owns:
    The source-to-forward character identification proving that the existing
    `(0,0)` by `(0,2)` matrix is the physical charged-lepton Yukawa matrix.

Depends on:
    The exact pullback convention, universal forward-sector matter lifts, tree
    matrix, and complete first-order matrix with exterior-filtration closure.

Must not:
    Recompute cochains, preserve the withdrawn Dirac-neutrino interpretation,
    select a carrier point, or call holomorphic data physically normalized.

Phase 0:
    Research-only convention correction for the last current-carrier sector.
"""

from __future__ import annotations

import json
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .mixed_schoen_character_convention import OUTPUT as CONVENTION_ARTIFACT
from .mixed_schoen_character_convention import inverse_character
from .mixed_schoen_neutrino_first_order_matrix import (
    OUTPUT as UNIVERSAL_MATRIX_ARTIFACT,
)
from .mixed_schoen_neutrino_matter_lifts import OUTPUT as MATTER_LIFTS_ARTIFACT
from .mixed_schoen_neutrino_tree_matrix import OUTPUT as TREE_MATRIX_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_charged_lepton_convention.json"
)
SOURCE_MATTER_CHARACTERS = ((0, 0), (0, 1))
FORWARD_MATTER_CHARACTERS = tuple(
    inverse_character(character) for character in SOURCE_MATTER_CHARACTERS
)
SOURCE_HIGGS_CHARACTER = (0, 2)
FORWARD_HIGGS_CHARACTER = inverse_character(SOURCE_HIGGS_CHARACTER)


def _verified_payload(path: Path) -> tuple[str, dict[str, object]]:
    """Load one content-addressed prerequisite without trusting its filename."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"upstream artifact is malformed: {path.name}")
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest failed: {path.name}")
    return digest, payload


def _verified_convention() -> tuple[str, dict[str, object]]:
    """Require exact inverse-pullback routing for the physical H_d class."""

    digest, payload = _verified_payload(CONVENTION_ARTIFACT)
    if (
        payload.get("exact") is not True
        or payload.get("prior_up_and_neutrino_physical_routing_valid") is not False
        or payload.get("physical_down_higgs_representative_available") is not True
        or payload.get("strict_cochain_source_character")
        != list(SOURCE_HIGGS_CHARACTER)
        or payload.get("strict_cochain_forward_character")
        != list(FORWARD_HIGGS_CHARACTER)
        or any(
            source != inverse_character(forward)
            for source, forward in zip(
                SOURCE_MATTER_CHARACTERS,
                FORWARD_MATTER_CHARACTERS,
                strict=True,
            )
        )
    ):
        raise ValueError("the charged-lepton character convention failed")
    return digest, payload


def _verified_matter_lifts() -> tuple[str, dict[str, object]]:
    """Require the exact forward matter sectors used by charged leptons."""

    digest, payload = _verified_payload(MATTER_LIFTS_ARTIFACT)
    if (
        payload.get("all_neutrino_matter_lifts_exact") is not True
        or payload.get("matter_character_exponents")
        != [list(character) for character in FORWARD_MATTER_CHARACTERS]
        or payload.get("arbitrary_extension_point_selected") is not False
        or payload.get("observational_inputs_used") is not False
    ):
        raise ValueError("the charged-lepton forward matter lifts failed")
    return digest, payload


def _verified_tree_matrix() -> tuple[str, dict[str, object]]:
    """Require the exact rank-zero forward-sector tree matrix."""

    digest, payload = _verified_payload(TREE_MATRIX_ARTIFACT)
    matrix = payload.get("dirac_neutrino_tree_matrix")
    if (
        payload.get("complete_tree_level_neutrino_matrix_available") is not True
        or not isinstance(matrix, dict)
        or matrix.get("row_matter_character_exponents")
        != list(FORWARD_MATTER_CHARACTERS[0])
        or matrix.get("column_matter_character_exponents")
        != list(FORWARD_MATTER_CHARACTERS[1])
        or matrix.get("higgs_character_exponents")
        != list(FORWARD_HIGGS_CHARACTER)
        or matrix.get("matrix_rank") != 0
        or matrix.get("exact") is not True
        or matrix.get("all_zero_entries_have_exact_primitives") is not True
    ):
        raise ValueError("the charged-lepton forward tree matrix failed")
    return digest, payload


def _verified_universal_matrix(
    matter_digest: str,
    tree_digest: str,
) -> tuple[str, dict[str, object]]:
    """Require all exterior-allowed coefficients and their exact rank."""

    digest, payload = _verified_payload(UNIVERSAL_MATRIX_ARTIFACT)
    prerequisites = payload.get("prerequisite_artifact_digests")
    if (
        payload.get("complete_universal_holomorphic_neutrino_matrix_available")
        is not True
        or payload.get("all_eight_coefficients_exact") is not True
        or payload.get("generic_rank") != 0
        or payload.get("maximum_exterior_allowed_parameter_order") != 1
        or payload.get("higher_orders_structurally_zero") is not True
        or payload.get("extension_point_selected") is not False
        or payload.get("observational_inputs_used") is not False
        or not isinstance(prerequisites, dict)
        or prerequisites.get("tree_matrix") != tree_digest
        or prerequisites.get("universal_matter_lifts") != matter_digest
    ):
        raise ValueError("the charged-lepton universal matrix failed")
    return digest, payload


def build_charged_lepton_convention() -> dict[str, object]:
    """Build the exact physical relabeling without recomputing chain data."""

    convention_digest, convention = _verified_convention()
    matter_digest, _matter = _verified_matter_lifts()
    tree_digest, tree = _verified_tree_matrix()
    universal_digest, universal = _verified_universal_matrix(
        matter_digest,
        tree_digest,
    )
    tree_matrix = tree["dirac_neutrino_tree_matrix"]
    if not isinstance(tree_matrix, dict):
        raise TypeError("the verified tree matrix record is invalid")
    payload: dict[str, object] = {
        "schema": "mixed-schoen-charged-lepton-convention-v1",
        "coefficient_field": "Q(omega)[a0,a1]",
        "physical_slice": {
            "matrix": "charged-lepton holomorphic Yukawa",
            "source_matter_character_exponents": [
                list(character) for character in SOURCE_MATTER_CHARACTERS
            ],
            "forward_matter_character_exponents": [
                list(character) for character in FORWARD_MATTER_CHARACTERS
            ],
            "source_higgs_character_exponents": list(SOURCE_HIGGS_CHARACTER),
            "forward_higgs_character_exponents": list(FORWARD_HIGGS_CHARACTER),
        },
        "prerequisite_artifact_digests": {
            "character_convention": convention_digest,
            "forward_matter_lifts": matter_digest,
            "forward_tree_matrix": tree_digest,
            "forward_universal_matrix": universal_digest,
        },
        "source_action_is_inverse_forward_pullback": (
            convention.get("character_conversion")
            == "source=(-forward) mod 3 factorwise"
        ),
        "prior_dirac_neutrino_physical_assignment_valid": False,
        "physical_charged_lepton_assignment_exact": True,
        "tree_matrix_rank": tree_matrix["matrix_rank"],
        "coefficient_matrices": universal["coefficient_matrices"],
        "complete_first_order_coefficient_count": len(universal["coefficients"]),
        "maximum_exterior_allowed_parameter_order": universal[
            "maximum_exterior_allowed_parameter_order"
        ],
        "higher_orders_structurally_zero": universal[
            "higher_orders_structurally_zero"
        ],
        "complete_universal_holomorphic_charged_lepton_matrix_available": True,
        "generic_rank": universal["generic_rank"],
        "classification": "SCOPED_ALL_ORDERS_CHARGED_LEPTON_NO_GO",
        "physical_yukawa_matrix_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "exact": True,
        "next_required_object": (
            "an exact replacement constituent or carrier realization with a "
            "nontrivial holomorphic Yukawa matrix"
        ),
    }
    return payload


def write_charged_lepton_convention(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed physical charged-lepton certificate."""

    payload = build_charged_lepton_convention()
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
    """Regenerate the charged-lepton convention certificate."""

    payload = write_charged_lepton_convention()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"generic_rank: {payload['generic_rank']}")
    print(f"classification: {payload['classification']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "FORWARD_HIGGS_CHARACTER",
    "FORWARD_MATTER_CHARACTERS",
    "OUTPUT",
    "SOURCE_HIGGS_CHARACTER",
    "SOURCE_MATTER_CHARACTERS",
    "build_charged_lepton_convention",
    "write_charged_lepton_convention",
]
