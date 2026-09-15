"""Normalize synchronized deck characters to the source section action.

Owns:
    The exact inversion from forward pullback eigencharacters to the source
    action on sections and the resulting physical Higgs-sector routing.

Depends on:
    The complete synchronized character audit, its strict full cochain, and
    the pinned one-Higgs source convention.

Must not:
    Alter a chain map, fit a character shift, preserve a superseded physical
    sector label, or claim a Yukawa matrix from character support alone.

Phase 0:
    Research-only correction of the deck-character comparison convention.
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
    "mixed_schoen_character_convention.json"
)
CHARACTER_AUDIT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_higgs_character_audit.json"
)
CHAIN_ACTION = (
    ROOT / "data/generated/scientific_genesis/mixed_schoen_chain_actions.json"
)

Character = tuple[int, int]
SOURCE_UP_HIGGS: Character = (0, 1)
SOURCE_DOWN_HIGGS: Character = (0, 2)


def _verified_artifact(path: Path, schema: str) -> tuple[dict[str, object], str]:
    """Load one prerequisite and verify its schema and content digest."""

    payload = cast(dict[str, object], json.loads(path.read_text(encoding="utf-8")))
    digest = payload.pop("artifact_digest", None)
    if payload.get("schema") != schema:
        raise ValueError(f"prerequisite schema failed: {path.name}")
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"prerequisite digest failed: {path.name}")
    return payload, digest


def inverse_character(character: Character) -> Character:
    """Return the character of the inverse order-three deck action."""

    return (-character[0]) % 3, (-character[1]) % 3


@dataclass(frozen=True, slots=True)
class ConventionSector:
    """One forward-pullback sector with its source-action character."""

    forward_character: Character
    source_character: Character
    space_dimensions: tuple[int, int, int]
    differential_ranks: tuple[int, int]
    h1_dimension: int

    @property
    def exact(self) -> bool:
        """Return whether inversion and the cohomology rank identity hold."""

        return (
            self.source_character == inverse_character(self.forward_character)
            and self.h1_dimension
            == self.space_dimensions[1]
            - self.differential_ranks[0]
            - self.differential_ranks[1]
        )

    def as_record(self) -> dict[str, object]:
        """Serialize one convention-normalized exact character sector."""

        return {
            "forward_pullback_character": list(self.forward_character),
            "source_section_character": list(self.source_character),
            "space_dimensions": list(self.space_dimensions),
            "differential_ranks": list(self.differential_ranks),
            "h1_dimension": self.h1_dimension,
            "exact": self.exact,
        }


@dataclass(frozen=True, slots=True)
class MixedSchoenCharacterConvention:
    """Exact physical routing induced by inverse pullback on sections."""

    sectors: tuple[ConventionSector, ...]
    strict_forward_character: Character
    strict_cochain_term_count: int
    strict_cochain_is_cycle: bool
    strict_cochain_has_forward_character: bool
    prerequisite_artifact_digests: tuple[tuple[str, str], ...]

    def source_h1_dimension(self, character: Character) -> int:
        """Return exact H1 multiplicity in one source-action character."""

        return sum(
            sector.h1_dimension
            for sector in self.sectors
            if sector.source_character == character
        )

    @property
    def source_h1_characters(self) -> tuple[Character, ...]:
        """Expand the convention-corrected source-action H1 multiset."""

        return tuple(
            sorted(
                sector.source_character
                for sector in self.sectors
                for _index in range(sector.h1_dimension)
            )
        )

    @property
    def strict_source_character(self) -> Character:
        """Return the source-action character of the existing strict cochain."""

        return inverse_character(self.strict_forward_character)

    @property
    def exact(self) -> bool:
        """Return every inversion, rank, and strict-cochain routing gate."""

        return (
            len(self.sectors) == 9
            and all(sector.exact for sector in self.sectors)
            and sum(sector.h1_dimension for sector in self.sectors) == 4
            and self.strict_forward_character == SOURCE_UP_HIGGS
            and self.strict_source_character == SOURCE_DOWN_HIGGS
            and self.source_h1_dimension(SOURCE_DOWN_HIGGS) == 1
            and self.source_h1_dimension(SOURCE_UP_HIGGS) == 0
            and self.strict_cochain_term_count == 27
            and self.strict_cochain_is_cycle
            and self.strict_cochain_has_forward_character
            and len(self.prerequisite_artifact_digests) == 2
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the corrected physical routing and invalidated claims."""

        return {
            "schema": "mixed-schoen-character-convention-v1",
            "coefficient_field": "Q(omega)",
            "forward_pullback_definition": (
                "substitute the declared deck coordinate images in cochains"
            ),
            "source_section_action_definition": (
                "act on sections by the inverse deck pullback"
            ),
            "character_conversion": "source=(-forward) mod 3 factorwise",
            "sectors": [sector.as_record() for sector in self.sectors],
            "forward_h1_characters": [
                list(character)
                for character in sorted(
                    sector.forward_character
                    for sector in self.sectors
                    for _index in range(sector.h1_dimension)
                )
            ],
            "source_action_h1_characters": [
                list(character) for character in self.source_h1_characters
            ],
            "source_up_higgs_character": list(SOURCE_UP_HIGGS),
            "source_up_higgs_h1_dimension": self.source_h1_dimension(
                SOURCE_UP_HIGGS
            ),
            "source_down_higgs_character": list(SOURCE_DOWN_HIGGS),
            "source_down_higgs_h1_dimension": self.source_h1_dimension(
                SOURCE_DOWN_HIGGS
            ),
            "strict_cochain_forward_character": list(
                self.strict_forward_character
            ),
            "strict_cochain_source_character": list(self.strict_source_character),
            "strict_cochain_term_count": self.strict_cochain_term_count,
            "strict_cochain_is_cycle": self.strict_cochain_is_cycle,
            "strict_cochain_has_declared_forward_character": (
                self.strict_cochain_has_forward_character
            ),
            "physical_down_higgs_representative_available": True,
            "physical_up_higgs_representative_available": False,
            "prior_up_and_neutrino_physical_routing_valid": False,
            "prior_down_higgs_obstruction_valid": False,
            "chain_maps_changed": False,
            "character_shift_fitted": False,
            "observational_inputs_used": False,
            "prerequisite_artifact_digests": dict(
                self.prerequisite_artifact_digests
            ),
            "exact": self.exact,
            "next_required_object": (
                "reuse the certified 27-term source-action H_d cochain with "
                "convention-corrected matter sectors and recompute the down "
                "holomorphic Yukawa matrix"
            ),
        }


def _sector(raw: dict[str, object]) -> ConventionSector:
    """Convert one verified forward sector to the source section action."""

    forward = cast(list[int], raw["character"])
    dimensions = cast(list[int], raw["space_dimensions"])
    ranks = cast(list[int], raw["differential_ranks"])
    character = (forward[0], forward[1])
    return ConventionSector(
        character,
        inverse_character(character),
        (dimensions[0], dimensions[1], dimensions[2]),
        (ranks[0], ranks[1]),
        cast(int, raw["h1_dimension"]),
    )


@cache
def mixed_schoen_character_convention() -> MixedSchoenCharacterConvention:
    """Derive the physical character routing without changing chain maps."""

    audit, audit_digest = _verified_artifact(
        CHARACTER_AUDIT,
        "mixed-schoen-higgs-character-audit-v1",
    )
    chain, chain_digest = _verified_artifact(
        CHAIN_ACTION,
        "mixed-schoen-chain-actions-v1",
    )
    if (
        audit.get("exact") is not True
        or audit.get("all_character_restrictions_exact") is not True
        or chain.get("character_h1_dimension") != 1
        or chain.get("full_representative_is_cycle") is not True
        or chain.get("full_representative_has_strict_character") is not True
    ):
        raise ValueError("the synchronized character prerequisites failed")
    strict_character = cast(list[int], chain["required_character"])
    cochain = cast(dict[str, object], chain["required_full_cochain"])
    result = MixedSchoenCharacterConvention(
        tuple(_sector(item) for item in cast(list[dict[str, object]], audit["sectors"])),
        (strict_character[0], strict_character[1]),
        cast(int, cochain["term_count"]),
        cast(bool, chain["full_representative_is_cycle"]),
        cast(bool, chain["full_representative_has_strict_character"]),
        (
            ("complete_forward_character_audit", audit_digest),
            ("strict_forward_character_cochain", chain_digest),
        ),
    )
    if not result.exact:
        raise ValueError("the source-action character convention audit failed")
    return result


def write_mixed_schoen_character_convention(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed character-convention correction."""

    payload = mixed_schoen_character_convention().as_record()
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
    """Regenerate the exact source-action character correction."""

    payload = write_mixed_schoen_character_convention()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "source_down_higgs_h1_dimension: "
        f"{payload['source_down_higgs_h1_dimension']}"
    )
    print(
        "physical_down_higgs_representative_available: "
        f"{payload['physical_down_higgs_representative_available']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CHARACTER_AUDIT",
    "CHAIN_ACTION",
    "ConventionSector",
    "MixedSchoenCharacterConvention",
    "OUTPUT",
    "SOURCE_DOWN_HIGGS",
    "SOURCE_UP_HIGGS",
    "inverse_character",
    "mixed_schoen_character_convention",
    "write_mixed_schoen_character_convention",
]
