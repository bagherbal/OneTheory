"""Certify the obstruction to the current equivariant Higgs comparison.

Owns:
    The isotypic-cohomology no-go for the current synchronized chain action,
    both determinant-Hom orientation failures, and the exact atlas/frame gap.

Depends on:
    Content-addressed Higgs spectrum, down-character, determinant-Hom, and
    constituent deck-atlas certificates plus exact Eisenstein arithmetic.

Must not:
    Relabel deck generators, guess a character twist, transport source classes
    without a chain map, or claim that the physical down-Higgs class exists.

Phase 0:
    Research-only scoped no-go and constructive frontier certificate.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .mixed_schoen_outer_actions import _constituent_frame
from .published_constituent_deck_atlases import (
    published_constituent_deck_atlases,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_higgs_equivariant_obstruction.json"
)
SPECTRUM_ARTIFACT = (
    ROOT / "data/generated/scientific_genesis/mixed_schoen_observable_spectrum.json"
)
DOWN_ACTION_ARTIFACT = (
    ROOT / "data/generated/scientific_genesis/mixed_schoen_down_higgs_action.json"
)
HOM_ARTIFACT = (
    ROOT / "data/generated/scientific_genesis/mixed_schoen_higgs_twist_audit.json"
)
ATLAS_ARTIFACT = (
    ROOT
    / "data/generated/scientific_genesis/published_constituent_deck_atlases.json"
)
REQUIRED_CHARACTER = (0, 2)


def _load_artifact(path: Path) -> tuple[dict[str, object], str]:
    """Load one exact artifact and verify its content digest."""

    payload = cast(dict[str, object], json.loads(path.read_text(encoding="utf-8")))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest failed: {path.name}")
    return payload, digest


def _source_character_multiplicity(payload: dict[str, object]) -> int:
    """Read the exact derived-pushdown multiplicity at character (0,2)."""

    higgs = payload.get("higgs")
    if not isinstance(higgs, dict):
        raise ValueError("the spectrum artifact lacks its Higgs record")
    raw_characters = higgs.get("deck_characters")
    if not isinstance(raw_characters, list):
        raise ValueError("the spectrum artifact lacks Higgs characters")
    matches = [
        item
        for item in raw_characters
        if isinstance(item, dict)
        and item.get("character_exponents") == list(REQUIRED_CHARACTER)
    ]
    if len(matches) != 1 or not isinstance(matches[0].get("multiplicity"), int):
        raise ValueError("the source-derived H_d character multiplicity is invalid")
    return cast(int, matches[0]["multiplicity"])


@dataclass(frozen=True, slots=True)
class FrameCharacterComparison:
    """One exact comparison of a legacy block frame with its atlas line."""

    constituent: str
    factor: int
    generator: str
    legacy_character: Eisenstein
    atlas_character: Eisenstein

    @property
    def matches(self) -> bool:
        """Return whether the synchronized frame uses the atlas character."""

        return self.legacy_character == self.atlas_character

    def as_record(self) -> dict[str, object]:
        """Serialize one exact frame-character comparison."""

        return {
            "constituent": self.constituent,
            "factor": self.factor,
            "generator": self.generator,
            "legacy_character": str(self.legacy_character),
            "atlas_character": str(self.atlas_character),
            "matches": self.matches,
        }


def _frame_character_comparisons() -> tuple[FrameCharacterComparison, ...]:
    """Compare synchronized extension-line blocks with exact atlas actions."""

    comparisons = []
    for factor, atlas in enumerate(published_constituent_deck_atlases(), start=1):
        for generator in ("P", "T"):
            atlas_values = {
                item.extension_line_character
                for item in atlas.comparisons
                if item.generator == generator
            }
            if len(atlas_values) != 1:
                raise ValueError("an atlas extension line lacks a unique character")
            comparisons.append(
                FrameCharacterComparison(
                    atlas.constituent,
                    factor,
                    generator,
                    _constituent_frame(factor, generator)[0][0],
                    next(iter(atlas_values)),
                )
            )
    return tuple(comparisons)


@dataclass(frozen=True, slots=True)
class HiggsEquivariantObstruction:
    """Exact no-go for the current source-to-chain equivariant comparison."""

    source_character_dimension: int
    current_chain_character_dimension: int
    current_chain_exact: bool
    determinant_hom_orientations_blocked: bool
    constituent_atlases_exact: bool
    frame_comparisons: tuple[FrameCharacterComparison, ...]
    prerequisite_artifact_digests: tuple[tuple[str, str], ...]

    @property
    def isotypic_dimension_mismatch(self) -> bool:
        """Return the exact obstruction on character-(0,2) cohomology."""

        return self.source_character_dimension != self.current_chain_character_dimension

    @property
    def legacy_frame_matches_atlas(self) -> bool:
        """Return whether every synchronized line block equals its atlas value."""

        return all(item.matches for item in self.frame_comparisons)

    @property
    def equivariant_quasi_isomorphism_available(self) -> bool:
        """Return whether isotypic cohomology permits the requested comparison."""

        return not self.isotypic_dimension_mismatch

    @property
    def exact(self) -> bool:
        """Return whether every scoped obstruction gate is certified."""

        return (
            self.source_character_dimension == 1
            and self.current_chain_character_dimension == 0
            and self.current_chain_exact
            and self.determinant_hom_orientations_blocked
            and self.constituent_atlases_exact
            and len(self.frame_comparisons) == 4
            and not self.legacy_frame_matches_atlas
            and not self.equivariant_quasi_isomorphism_available
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the theorem, evidence, and next constructive dependency."""

        return {
            "schema": "mixed-schoen-higgs-equivariant-obstruction-v1",
            "coefficient_field": "Q(omega)",
            "required_character": list(REQUIRED_CHARACTER),
            "source_derived_p1_h1_dimension": self.source_character_dimension,
            "current_chain_h1_dimension": self.current_chain_character_dimension,
            "isotypic_dimension_mismatch": self.isotypic_dimension_mismatch,
            "theorem": (
                "an equivariant quasi-isomorphism induces an isomorphism on "
                "each character-isotypic cohomology group"
            ),
            "equivariant_quasi_isomorphism_available": (
                self.equivariant_quasi_isomorphism_available
            ),
            "both_determinant_hom_orientations_blocked": (
                self.determinant_hom_orientations_blocked
            ),
            "constituent_atlases_exact": self.constituent_atlases_exact,
            "legacy_frame_atlas_comparisons": [
                item.as_record() for item in self.frame_comparisons
            ],
            "legacy_frame_matches_atlas": self.legacy_frame_matches_atlas,
            "current_comparison_route_refuted": self.exact,
            "character_twist_guessed": False,
            "deck_generators_relabelled": False,
            "observational_inputs_used": False,
            "prerequisite_artifact_digests": dict(
                self.prerequisite_artifact_digests
            ),
            "next_required_object": (
                "the full local-semilinear constituent deck action transferred "
                "through the synchronized Schoen chain, including overlap gauges"
            ),
            "status": (
                "scoped no-go for the current synchronized action; the source "
                "H_d class remains unavailable until the atlas action is transferred"
            ),
        }


@cache
def higgs_equivariant_obstruction() -> HiggsEquivariantObstruction:
    """Construct the exact obstruction from independently certified inputs."""

    spectrum, spectrum_digest = _load_artifact(SPECTRUM_ARTIFACT)
    down, down_digest = _load_artifact(DOWN_ACTION_ARTIFACT)
    hom, hom_digest = _load_artifact(HOM_ARTIFACT)
    atlas, atlas_digest = _load_artifact(ATLAS_ARTIFACT)
    if spectrum.get("schema") != "mixed-schoen-observable-spectrum-v1":
        raise ValueError("the lawful spectrum artifact schema changed")
    current_chain_exact = (
        down.get("schema") == "mixed-schoen-down-higgs-action-audit-v1"
        and down.get("required_character") == list(REQUIRED_CHARACTER)
        and down.get("transferred_differential_squared_zero") is True
        and down.get("group_relations_exact") is True
        and down.get("character_bases_exact") is True
        and down.get("route_blocked_exact") is True
    )
    chain_dimension = down.get("character_h1_dimension")
    if not isinstance(chain_dimension, int):
        raise ValueError("the current H_d chain dimension is invalid")
    result = HiggsEquivariantObstruction(
        _source_character_multiplicity(spectrum),
        chain_dimension,
        current_chain_exact,
        hom.get("all_determinant_hom_orientations_blocked") is True,
        atlas.get("all_constituent_deck_atlases_exact") is True,
        _frame_character_comparisons(),
        (
            ("lawful_spectrum", spectrum_digest),
            ("current_down_action", down_digest),
            ("determinant_hom", hom_digest),
            ("constituent_deck_atlases", atlas_digest),
        ),
    )
    if not result.exact:
        raise ValueError("the equivariant Higgs obstruction gate failed")
    return result


def write_higgs_equivariant_obstruction(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed scoped no-go certificate."""

    payload = higgs_equivariant_obstruction().as_record()
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
    """Regenerate the exact equivariant-comparison obstruction."""

    payload = write_higgs_equivariant_obstruction()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "current_comparison_route_refuted: "
        f"{payload['current_comparison_route_refuted']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "FrameCharacterComparison",
    "HiggsEquivariantObstruction",
    "OUTPUT",
    "higgs_equivariant_obstruction",
    "write_higgs_equivariant_obstruction",
]
