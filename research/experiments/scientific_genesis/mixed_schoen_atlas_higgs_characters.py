"""Derive Higgs characters forced by the certified constituent atlases.

Owns:
    Full-summand atlas-to-synchronized character ratios, their tensor
    product, and the induced character decomposition of Higgs cohomology.

Depends on:
    Certified constituent deck atlases, exact simplicity, the normalized
    common-Schoen chain-frame comparison, and full-chain Higgs characters.

Must not:
    Import pushdown character labels as construction input, relabel deck
    generators, fit a twist, or claim that the selected source spectrum holds.

Phase 0:
    Research-only atlas-induced Higgs representation certificate.
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

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_atlas_higgs_characters.json"
)
PREREQUISITES: tuple[tuple[str, Path, str, str], ...] = (
    (
        "constituent_deck_atlases",
        ROOT
        / "data/generated/scientific_genesis/"
        "published_constituent_deck_atlases.json",
        "published-constituent-deck-atlases-v1",
        "all_constituent_deck_atlases_exact",
    ),
    (
        "chain_frame_comparison",
        ROOT
        / "data/generated/scientific_genesis/"
        "mixed_schoen_atlas_frame_comparison.json",
        "mixed-schoen-atlas-frame-comparison-v1",
        "full_chain_comparison_exact",
    ),
    (
        "complete_character_audit",
        ROOT
        / "data/generated/scientific_genesis/"
        "mixed_schoen_higgs_character_audit.json",
        "mixed-schoen-higgs-character-audit-v1",
        "exact",
    ),
    (
        "source_action_convention",
        ROOT
        / "data/generated/scientific_genesis/"
        "mixed_schoen_character_convention.json",
        "mixed-schoen-character-convention-v1",
        "exact",
    ),
    (
        "simplicity_no_go",
        ROOT
        / "data/generated/scientific_genesis/"
        "mixed_schoen_higgs_linearization_no_go.json",
        "mixed-schoen-higgs-linearization-no-go-v1",
        "exact",
    ),
)

type Character = tuple[int, int]


def _verified_artifact(path: Path, schema: str, exact_key: str) -> dict[str, object]:
    """Read one content-addressed prerequisite with an explicit exact gate."""

    payload = cast(dict[str, object], json.loads(path.read_text(encoding="utf-8")))
    digest = payload.pop("artifact_digest", None)
    if (
        not isinstance(digest, str)
        or digest != _canonical_digest(payload)
        or payload.get("schema") != schema
        or payload.get(exact_key) is not True
    ):
        raise ValueError(f"prerequisite artifact failed: {path.name}")
    payload["artifact_digest"] = digest
    return payload


def _shift(character: Character, shift: Character) -> Character:
    """Multiply two Z3 x Z3 characters in exponent notation."""

    return ((character[0] + shift[0]) % 3, (character[1] + shift[1]) % 3)


@dataclass(frozen=True, slots=True)
class ConstituentLinearizationRatio:
    """One factor's atlas character relative to the synchronized lift."""

    constituent: str
    ratio: Character

    def as_record(self) -> dict[str, object]:
        """Serialize one exact two-generator character ratio."""

        return {
            "constituent": self.constituent,
            "atlas_over_synchronized_character": list(self.ratio),
        }


@dataclass(frozen=True, slots=True)
class AtlasHiggsCharacterAudit:
    """Exact Higgs representation induced by the certified local atlases."""

    constituent_ratios: tuple[ConstituentLinearizationRatio, ...]
    synchronized_characters: tuple[Character, ...]
    atlas_characters: tuple[Character, ...]
    source_characters: tuple[Character, ...]
    prerequisite_artifact_digests: tuple[tuple[str, str], ...]

    @property
    def tensor_ratio(self) -> Character:
        """Return the product of both constituent linearization characters."""

        first = sum(item.ratio[0] for item in self.constituent_ratios) % 3
        second = sum(item.ratio[1] for item in self.constituent_ratios) % 3
        return first, second

    @property
    def atlas_source_action_characters(self) -> tuple[Character, ...]:
        """Invert forward pullback characters to the published section action."""

        return tuple(sorted(((-a) % 3, (-b) % 3) for a, b in self.atlas_characters))

    @property
    def exact(self) -> bool:
        """Return all same-object atlas-representation gates."""

        return (
            tuple(item.constituent for item in self.constituent_ratios)
            == ("W1", "W2")
            and self.atlas_characters
            == tuple(
                sorted(
                    _shift(character, self.tensor_ratio)
                    for character in self.synchronized_characters
                )
            )
            and self.atlas_source_action_characters != self.source_characters
            and len(self.prerequisite_artifact_digests) == len(PREREQUISITES)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the forced atlas representation and incompatibility."""

        return {
            "schema": "mixed-schoen-atlas-higgs-characters-v2",
            "coefficient_field": "Q(omega)",
            "constituent_linearization_ratios": [
                item.as_record() for item in self.constituent_ratios
            ],
            "tensor_atlas_over_synchronized_character": list(self.tensor_ratio),
            "synchronized_h1_characters": [
                list(character) for character in self.synchronized_characters
            ],
            "atlas_induced_h1_characters": [
                list(character) for character in self.atlas_characters
            ],
            "atlas_source_action_h1_characters": [
                list(character) for character in self.atlas_source_action_characters
            ],
            "selected_source_h1_characters": [
                list(character) for character in self.source_characters
            ],
            "atlas_characters_match_selected_source": (
                self.atlas_source_action_characters == self.source_characters
            ),
            "source_action_convention_applied": True,
            "source_and_atlas_character_assignments_compatible": False,
            "derivation": (
                "homogeneous-lift-normalized full-chain ratio plus constituent "
                "simplicity, the complete synchronized cohomology "
                "representation, and inverse-pullback section convention"
            ),
            "homogeneous_lift_normalization_included": True,
            "raw_extension_line_ratio_used_as_tensor_character": False,
            "source_pushdown_characters_used_as_construction_input": False,
            "deck_generators_relabelled": False,
            "character_twist_fitted": False,
            "observational_inputs_used": False,
            "physical_h_d_representative_available": False,
            "scope": (
                "the certified selected constituent atlases and their induced "
                "factorwise tensor linearization"
            ),
            "prerequisite_artifact_digests": dict(
                self.prerequisite_artifact_digests
            ),
            "exact": self.exact,
            "next_required_object": (
                "derive every relative-pushdown line character from the local "
                "atlas action and locate the first source-convention mismatch"
            ),
        }


def _constituent_ratios(
    frame_artifact: dict[str, object],
) -> tuple[ConstituentLinearizationRatio, ...]:
    """Invert the exact common-over-atlas characters on full summands."""

    if frame_artifact.get("full_chain_comparison_exact") is not True:
        raise ValueError("the atlas/common full-chain comparison is missing")
    return tuple(
        ConstituentLinearizationRatio(
            name,
            tuple((-value) % 3 for value in cast(list[int], frame_artifact[key])),
        )
        for name, key in (
            ("W1", "first_constituent_uniform_twist"),
            ("W2", "second_constituent_uniform_twist"),
        )
    )


@cache
def atlas_higgs_character_audit() -> AtlasHiggsCharacterAudit:
    """Derive the local-atlas Higgs representation without source fitting."""

    prerequisites = tuple(
        (name, _verified_artifact(path, schema, exact_key))
        for name, path, schema, exact_key in PREREQUISITES
    )
    by_name = dict(prerequisites)
    frames = by_name["chain_frame_comparison"]
    characters = by_name["complete_character_audit"]
    ratios = _constituent_ratios(frames)
    if by_name["simplicity_no_go"].get("all_selected_constituents_simple") is not True:
        raise ValueError("the constituent simplicity gate failed")
    synchronized = tuple(
        tuple(item)
        for item in cast(list[Character], characters["current_h1_characters"])
    )
    source = tuple(
        tuple(item)
        for item in cast(list[Character], characters["selected_source_h1_characters"])
    )
    convention = by_name["source_action_convention"]
    if (
        convention.get("character_conversion")
        != "source=(-forward) mod 3 factorwise"
        or convention.get("source_action_h1_characters")
        != [
            list(character)
            for character in sorted(((-a) % 3, (-b) % 3) for a, b in synchronized)
        ]
    ):
        raise ValueError("the source section convention is inconsistent")
    tensor_ratio = (
        sum(item.ratio[0] for item in ratios) % 3,
        sum(item.ratio[1] for item in ratios) % 3,
    )
    atlas = tuple(sorted(_shift(character, tensor_ratio) for character in synchronized))
    result = AtlasHiggsCharacterAudit(
        ratios,
        synchronized,
        atlas,
        source,
        tuple(
            (name, cast(str, payload["artifact_digest"]))
            for name, payload in prerequisites
        ),
    )
    if not result.exact:
        raise ValueError("the atlas-induced Higgs character audit failed")
    return result


def write_atlas_higgs_character_audit(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed atlas Higgs representation."""

    payload = atlas_higgs_character_audit().as_record()
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
    """Regenerate the exact atlas-induced Higgs character certificate."""

    payload = write_atlas_higgs_character_audit()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"atlas_induced_h1_characters: {payload['atlas_induced_h1_characters']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "AtlasHiggsCharacterAudit",
    "ConstituentLinearizationRatio",
    "OUTPUT",
    "atlas_higgs_character_audit",
    "write_atlas_higgs_character_audit",
]
