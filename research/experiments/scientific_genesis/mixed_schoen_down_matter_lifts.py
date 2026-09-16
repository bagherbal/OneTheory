"""Lift convention-corrected down-matter sectors into the universal cone.

Owns:
    Constant V1 classes and parameter-linear V2 lifts for the two physical
    down-sector source characters after exact pullback-convention inversion.

Depends on:
    The character-convention correction, strict mixed matter representatives,
    and the lawful two-parameter universal visible extension cone.

Must not:
    Reuse prior physical sector labels, select an extension point, infer a
    Yukawa coefficient, or import masses, mixings, or observational selectors.

Phase 0:
    Research-only universal matter input for the physical down Yukawa sector.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)

from .mixed_schoen_character_convention import (
    OUTPUT as CONVENTION_ARTIFACT,
)
from .mixed_schoen_character_convention import inverse_character
from .mixed_schoen_matter_representatives import (
    OUTPUT as MATTER_ARTIFACT,
)
from .mixed_schoen_matter_representatives import (
    _cochain_digest,
    mixed_schoen_matter_representatives,
)
from .mixed_schoen_outer_universal_cone import (
    OUTPUT as UNIVERSAL_ARTIFACT,
)
from .mixed_schoen_outer_universal_cone import _load_forward_basis
from .mixed_schoen_universal_matter_lifts import (
    UniversalV2MatterLift,
    _initialize_lift_worker,
    _lift_v2_job,
    _source_digest,
    _verified_digest,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/mixed_schoen_down_matter_lifts.json"
)
SOURCE_MATTER_CHARACTERS = ((2, 1), (1, 0))
FORWARD_MATTER_CHARACTERS = tuple(
    inverse_character(character) for character in SOURCE_MATTER_CHARACTERS
)
SOURCE_DOWN_HIGGS_CHARACTER = (0, 2)
FORWARD_DOWN_HIGGS_CHARACTER = inverse_character(SOURCE_DOWN_HIGGS_CHARACTER)


def _convention_digest() -> str:
    """Verify the exact source-to-forward character routing prerequisite."""

    payload = json.loads(CONVENTION_ARTIFACT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError("the character-convention artifact digest failed")
    if (
        payload.get("exact") is not True
        or payload.get("physical_down_higgs_representative_available") is not True
        or payload.get("strict_cochain_source_character")
        != list(SOURCE_DOWN_HIGGS_CHARACTER)
        or payload.get("strict_cochain_forward_character")
        != list(FORWARD_DOWN_HIGGS_CHARACTER)
    ):
        raise ValueError("the physical down-Higgs routing changed")
    return digest


@dataclass(frozen=True, slots=True)
class DownMatterLifts:
    """Universal matter bases for the convention-corrected down sector."""

    parameters: tuple[str, str]
    v1_representatives: tuple[
        tuple[tuple[int, int], SparseOuterCechCochain], ...
    ]
    v2_lifts: tuple[UniversalV2MatterLift, ...]
    convention_artifact_digest: str
    matter_artifact_digest: str
    universal_artifact_digest: str
    source_archive_sha256: str

    @property
    def exact(self) -> bool:
        """Return all character, multiplicity, and universal-lift gates."""

        multiplicities = {
            character: sum(lift.character == character for lift in self.v2_lifts)
            for character in FORWARD_MATTER_CHARACTERS
        }
        return (
            self.parameters == ("a0", "a1")
            and tuple(
                character for character, _cochain in self.v1_representatives
            )
            == FORWARD_MATTER_CHARACTERS
            and len(self.v1_representatives) == 2
            and len(self.v2_lifts) == 4
            and all(lift.exact for lift in self.v2_lifts)
            and set(multiplicities.values()) == {2}
            and all(
                source == inverse_character(forward)
                for source, forward in zip(
                    SOURCE_MATTER_CHARACTERS,
                    FORWARD_MATTER_CHARACTERS,
                    strict=True,
                )
            )
            and self.source_archive_sha256 == _source_digest()
        )

    def as_record(self) -> dict[str, object]:
        """Serialize exact lifts with separate source and forward labels."""

        return {
            "schema": "mixed-schoen-down-matter-lifts-v1",
            "coefficient_field": "Q(omega)",
            "carrier_parameter_basis": list(self.parameters),
            "carrier_locus": "P^1(Q(omega)) x K^s",
            "physical_slice": {
                "matrix": "down-type holomorphic Yukawa",
                "source_matter_character_exponents": [
                    list(character) for character in SOURCE_MATTER_CHARACTERS
                ],
                "forward_matter_character_exponents": [
                    list(character) for character in FORWARD_MATTER_CHARACTERS
                ],
                "source_higgs_character_exponents": list(
                    SOURCE_DOWN_HIGGS_CHARACTER
                ),
                "forward_higgs_character_exponents": list(
                    FORWARD_DOWN_HIGGS_CHARACTER
                ),
                "source_archive_sha256": self.source_archive_sha256,
            },
            "prerequisite_artifact_digests": {
                "character_convention": self.convention_artifact_digest,
                "strict_matter": self.matter_artifact_digest,
                "universal_cone": self.universal_artifact_digest,
            },
            "v1_constant_classes": [
                {
                    "forward_character_exponents": list(character),
                    "source_character_exponents": list(
                        inverse_character(character)
                    ),
                    "term_count": len(cochain.terms),
                    "digest": _cochain_digest((cochain,)),
                }
                for character, cochain in self.v1_representatives
            ],
            "v2_parameter_linear_lifts": [
                {
                    **lift.as_record(),
                    "forward_character_exponents": list(lift.character),
                    "source_character_exponents": list(
                        inverse_character(lift.character)
                    ),
                }
                for lift in self.v2_lifts
            ],
            "universal_visible_family_dimension_per_character": 3,
            "all_coefficientwise_cone_identities_exact": True,
            "all_lifts_strict_in_forward_characters": True,
            "source_characters_obtained_only_by_exact_inversion": True,
            "arbitrary_extension_point_selected": False,
            "observational_inputs_used": False,
            "exact": self.exact,
            "next_required_object": (
                "the complete convention-corrected down tree matrix followed "
                "by every exterior-allowed universal coefficient"
            ),
        }


@cache
def mixed_schoen_down_matter_lifts() -> DownMatterLifts:
    """Construct universal matter lifts for the physical down sector."""

    first, second = mixed_schoen_matter_representatives()
    _action_digest, parameters, extensions = _load_forward_basis()
    if parameters != ("a0", "a1"):
        raise ValueError("the universal extension basis is no longer two-dimensional")
    v1_representatives = []
    v2_jobs = []
    for character in FORWARD_MATTER_CHARACTERS:
        first_sector = next(
            sector for sector in first.sectors if sector.character == character
        )
        second_sector = next(
            sector for sector in second.sectors if sector.character == character
        )
        if len(first_sector.full_representatives) != 1:
            raise ValueError("a selected V1 down-matter sector is not one-dimensional")
        if len(second_sector.full_representatives) != 2:
            raise ValueError("a selected V2 down-matter sector is not two-dimensional")
        v1_representatives.append(
            (character, first_sector.full_representatives[0])
        )
        v2_jobs.extend(
            (character, index, representative)
            for index, representative in enumerate(
                second_sector.full_representatives,
                start=1,
            )
        )
    with ProcessPoolExecutor(
        max_workers=len(v2_jobs),
        initializer=_initialize_lift_worker,
        initargs=(extensions,),
    ) as executor:
        v2_lifts = tuple(executor.map(_lift_v2_job, v2_jobs))
    result = DownMatterLifts(
        ("a0", "a1"),
        tuple(v1_representatives),
        v2_lifts,
        _convention_digest(),
        _verified_digest(
            MATTER_ARTIFACT,
            "all_strict_character_representatives_exact",
            True,
        ),
        _verified_digest(
            UNIVERSAL_ARTIFACT,
            "equivariant_descent_exact",
            True,
        ),
        _source_digest(),
    )
    if not result.exact:
        raise ValueError("the convention-corrected down-matter lifts failed")
    return result


def write_mixed_schoen_down_matter_lifts(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed physical down-matter certificate."""

    payload = mixed_schoen_down_matter_lifts().as_record()
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
    """Regenerate all exact convention-corrected down-matter lifts."""

    payload = write_mixed_schoen_down_matter_lifts()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "v2_parameter_linear_lift_count: "
        f"{len(payload['v2_parameter_linear_lifts'])}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DownMatterLifts",
    "FORWARD_DOWN_HIGGS_CHARACTER",
    "FORWARD_MATTER_CHARACTERS",
    "OUTPUT",
    "SOURCE_DOWN_HIGGS_CHARACTER",
    "SOURCE_MATTER_CHARACTERS",
    "mixed_schoen_down_matter_lifts",
    "write_mixed_schoen_down_matter_lifts",
]
