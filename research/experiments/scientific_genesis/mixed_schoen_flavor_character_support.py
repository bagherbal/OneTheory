"""Derive exact Wilson-character support for every Yukawa sector.

Owns:
    Source-pinned matter and Higgs Wilson characters, invariant Yukawa triples,
    current strict-chain coverage, and deterministic next-sector workload.

Depends on:
    The verified published source manifest, exact mixed matter sectors, the
    strict up Higgs class, universal up lifts, and the completed up no-go.

Must not:
    Infer a character from observed masses, invent a family identification,
    choose an extension point, or claim a Yukawa coefficient from support alone.

Phase 0:
    Research-only flavor-sector routing from published Wilson data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .mixed_schoen_chain_actions import OUTPUT as STRICT_HIGGS_ARTIFACT
from .mixed_schoen_matter_representatives import OUTPUT as STRICT_MATTER_ARTIFACT
from .mixed_schoen_observable_spectrum import OUTPUT as SPECTRUM_ARTIFACT
from .mixed_schoen_universal_matter_lifts import (
    OUTPUT as UNIVERSAL_MATTER_ARTIFACT,
)
from .mixed_schoen_up_yukawa_no_go import OUTPUT as UP_NO_GO_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_flavor_character_support.json"
SOURCE_MANIFEST = ROOT / "data/published/visible_carrier/source_manifest.json"
SOURCE_ARXIV_ID = "hep-th/0512177"
SOURCE_VERSION = "v3"
SOURCE_SHA256 = "ad4ea10b3d765553ccdd072922a6bda619866ea814c532b8ffe74ddafc7fe73f"
PARAMETER_COUNT = 2
LOCAL_V2_DIMENSION = 2

type Character = tuple[int, int]


def _inverse(character: Character) -> Character:
    """Return the inverse character of Z3 x Z3."""

    return (-character[0]) % 3, (-character[1]) % 3


def _sum_characters(*characters: Character) -> Character:
    """Add exact character exponents in Z3 x Z3."""

    return (
        sum(character[0] for character in characters) % 3,
        sum(character[1] for character in characters) % 3,
    )


def _verified_payload(path: Path, gate: str) -> tuple[str, dict[str, object]]:
    """Load one generated prerequisite after digest and gate verification."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest failed: {path.name}")
    if payload.get(gate) is not True:
        raise ValueError(f"upstream artifact gate failed: {path.name}")
    return digest, payload


def _source_digest() -> str:
    """Verify the source archive record fixing the Wilson embedding."""

    payload = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    sources = payload.get("sources")
    if not isinstance(sources, list):
        raise ValueError("the published source manifest lacks source records")
    matches = [
        source
        for source in sources
        if isinstance(source, dict)
        and source.get("arxiv_id") == SOURCE_ARXIV_ID
        and source.get("version") == SOURCE_VERSION
    ]
    if len(matches) != 1:
        raise ValueError("the Wilson source record must be unique")
    if matches[0].get("source_archive_sha256") != SOURCE_SHA256:
        raise ValueError("the Wilson source archive digest changed")
    return SOURCE_SHA256


@dataclass(frozen=True, slots=True)
class WilsonMultiplet:
    """One published Wilson character and its invariant cohomology character."""

    name: str
    representation: str
    wilson_character: Character

    @property
    def cohomology_character(self) -> Character:
        """Return the cover-cohomology character surviving the quotient."""

        return _inverse(self.wilson_character)

    def as_record(self) -> dict[str, object]:
        """Serialize the source character without physical numerical inputs."""

        return {
            "name": self.name,
            "representation": self.representation,
            "wilson_character_exponents": list(self.wilson_character),
            "required_cohomology_character_exponents": list(
                self.cohomology_character
            ),
        }


@dataclass(frozen=True, slots=True)
class YukawaCharacterSector:
    """One gauge-invariant Yukawa triple and its remaining chain workload."""

    name: str
    left: WilsonMultiplet
    right: WilsonMultiplet
    higgs: WilsonMultiplet
    missing_matter_characters: tuple[Character, ...]
    missing_higgs_characters: tuple[Character, ...]

    @property
    def invariant(self) -> bool:
        """Return whether the three required cohomology characters multiply to one."""

        return _sum_characters(
            self.left.cohomology_character,
            self.right.cohomology_character,
            self.higgs.cohomology_character,
        ) == (0, 0)

    @property
    def new_matter_correction_count(self) -> int:
        """Count exact parameter coefficients needed for new lifted matter."""

        return (
            len(self.missing_matter_characters)
            * LOCAL_V2_DIMENSION
            * PARAMETER_COUNT
        )

    @property
    def new_higgs_chain_object_count(self) -> int:
        """Count each missing strict Higgs class plus its parameter corrections."""

        return len(self.missing_higgs_characters) * (1 + PARAMETER_COUNT)

    @property
    def new_chain_object_count(self) -> int:
        """Return the deterministic minimum source-chain workload."""

        return self.new_matter_correction_count + self.new_higgs_chain_object_count

    def as_record(self) -> dict[str, object]:
        """Serialize exact support and the uncomputed chain frontier."""

        return {
            "name": self.name,
            "coupling": [self.left.name, self.right.name, self.higgs.name],
            "required_cohomology_characters": [
                list(self.left.cohomology_character),
                list(self.right.cohomology_character),
                list(self.higgs.cohomology_character),
            ],
            "character_product_is_invariant": self.invariant,
            "missing_matter_characters": [
                list(character) for character in self.missing_matter_characters
            ],
            "missing_higgs_characters": [
                list(character) for character in self.missing_higgs_characters
            ],
            "new_matter_parameter_correction_count": (
                self.new_matter_correction_count
            ),
            "new_higgs_chain_object_count": self.new_higgs_chain_object_count,
            "minimum_new_chain_object_count": self.new_chain_object_count,
        }


def flavor_character_support() -> dict[str, object]:
    """Derive every sector and choose the least new exact chain workload."""

    strict_matter_digest, strict_matter = _verified_payload(
        STRICT_MATTER_ARTIFACT,
        "all_strict_character_representatives_exact",
    )
    spectrum_digest, _spectrum = _verified_payload(
        SPECTRUM_ARTIFACT,
        "entire_stable_family_passes_structural_spectrum",
    )
    universal_digest, universal = _verified_payload(
        UNIVERSAL_MATTER_ARTIFACT,
        "all_coefficientwise_cone_identities_exact",
    )
    higgs_digest, strict_higgs = _verified_payload(
        STRICT_HIGGS_ARTIFACT,
        "physical_higgs_representative_available",
    )
    no_go_digest, _no_go = _verified_payload(UP_NO_GO_ARTIFACT, "exact")
    matter_characters = {
        tuple(record["character_exponents"])
        for record in universal["v2_parameter_linear_lifts"]
    }
    higgs_characters = {tuple(strict_higgs["required_character"])}
    strict_character_sets = {
        factor["factor"]: {
            tuple(sector["character_exponents"])
            for sector in factor["character_sectors"]
        }
        for factor in strict_matter["constituents"]
    }
    all_characters = {
        (first, second) for first in range(3) for second in range(3)
    }
    if any(
        characters != all_characters
        for characters in strict_character_sets.values()
    ):
        raise ValueError("strict matter representatives do not cover every character")

    multiplets = {
        "Q": WilsonMultiplet("Q", "(3,2,1,1)", (1, 2)),
        "u^c": WilsonMultiplet("u^c", "(bar3,1,-4,-1)", (2, 2)),
        "d^c": WilsonMultiplet("d^c", "(bar3,1,2,-1)", (2, 0)),
        "L": WilsonMultiplet("L", "(1,2,-3,-3)", (0, 0)),
        "e^c": WilsonMultiplet("e^c", "(1,1,6,3)", (0, 2)),
        "nu^c": WilsonMultiplet("nu^c", "(1,1,0,3)", (0, 1)),
        "H_u": WilsonMultiplet("H_u", "(1,2,3,0)", (0, 2)),
        "H_d": WilsonMultiplet("H_d", "(1,bar2,-3,0)", (0, 1)),
    }
    declarations = (
        ("up", "Q", "u^c", "H_u"),
        ("down", "Q", "d^c", "H_d"),
        ("charged_lepton", "L", "e^c", "H_d"),
        ("dirac_neutrino", "L", "nu^c", "H_u"),
    )
    sectors = []
    for name, left_name, right_name, higgs_name in declarations:
        left = multiplets[left_name]
        right = multiplets[right_name]
        higgs = multiplets[higgs_name]
        required_matter = {left.cohomology_character, right.cohomology_character}
        required_higgs = {higgs.cohomology_character}
        sectors.append(
            YukawaCharacterSector(
                name,
                left,
                right,
                higgs,
                tuple(sorted(required_matter - matter_characters)),
                tuple(sorted(required_higgs - higgs_characters)),
            )
        )
    if not all(sector.invariant for sector in sectors):
        raise ValueError("a published Yukawa character triple is not invariant")
    candidates = tuple(sector for sector in sectors if sector.name != "up")
    selected = min(
        candidates,
        key=lambda sector: (sector.new_chain_object_count, sector.name),
    )
    if selected.name != "down":
        raise ValueError("the exact chain workload no longer selects the down sector")
    payload: dict[str, object] = {
        "schema": "mixed-schoen-flavor-character-support-v1",
        "coefficient_field": "Q(omega)",
        "source": {
            "arxiv_id": SOURCE_ARXIV_ID,
            "version": SOURCE_VERSION,
            "source_archive_sha256": _source_digest(),
            "matter_wilson_locator": "eq:burt4",
            "higgs_wilson_locator": "eq:19",
        },
        "prerequisite_artifact_digests": {
            "strict_matter": strict_matter_digest,
            "observable_spectrum": spectrum_digest,
            "universal_up_matter": universal_digest,
            "strict_up_higgs": higgs_digest,
            "universal_up_no_go": no_go_digest,
        },
        "multiplets": [multiplet.as_record() for multiplet in multiplets.values()],
        "sectors": [sector.as_record() for sector in sectors],
        "all_character_products_invariant": True,
        "selection_rule": (
            "minimize new source-chain objects after reusing certified matter "
            "and Higgs characters"
        ),
        "selected_next_sector": selected.name,
        "selected_required_new_matter_character": list(
            selected.missing_matter_characters[0]
        ),
        "selected_required_new_higgs_character": list(
            selected.missing_higgs_characters[0]
        ),
        "selected_minimum_new_chain_object_count": selected.new_chain_object_count,
        "observational_inputs_used": False,
        "extension_point_selected": False,
        "yukawa_coefficient_computed": False,
        "next_required_object": (
            "universal matter lifts in character (1,0) and a strict Higgs "
            "representative in character (0,2)"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    return payload


def write_flavor_character_support(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed all-sector character support ledger."""

    payload = flavor_character_support()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate exact flavor support and print the selected next sector."""

    payload = write_flavor_character_support()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"selected_next_sector: {payload['selected_next_sector']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "OUTPUT",
    "WilsonMultiplet",
    "YukawaCharacterSector",
    "flavor_character_support",
    "write_flavor_character_support",
]
