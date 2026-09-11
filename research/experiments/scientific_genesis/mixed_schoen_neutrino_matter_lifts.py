"""Derive universal matter lifts for the selected Dirac-neutrino sector.

Owns:
    Constant V1 classes and parameter-linear V2 lifts in characters (0,0) and
    (0,2), with exact cycle, correction, and strict-character certificates.

Depends on:
    The post-obstruction flavor frontier, strict mixed matter representatives,
    and the lawful two-parameter universal visible extension cone.

Must not:
    Select an extension point, infer a Yukawa coefficient, normalize a trace,
    or import masses, mixings, fitted parameters, or observational selectors.

Phase 0:
    Research-only universal matter input for the Dirac-neutrino Yukawa sector.
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

from .mixed_schoen_flavor_frontier import OUTPUT as FRONTIER_ARTIFACT
from .mixed_schoen_matter_representatives import (
    OUTPUT as MATTER_ARTIFACT,
)
from .mixed_schoen_matter_representatives import (
    _cochain_digest,
    mixed_schoen_matter_representatives,
)
from .mixed_schoen_outer_universal_cone import OUTPUT as UNIVERSAL_ARTIFACT
from .mixed_schoen_outer_universal_cone import _load_forward_basis
from .mixed_schoen_universal_matter_lifts import (
    UniversalV2MatterLift,
    _lift_v2_coefficient,
    _source_digest,
    _strict_character,
    _verified_digest,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_neutrino_matter_lifts.json"
)
NEUTRINO_MATTER_CHARACTERS = ((0, 0), (0, 2))
_WORKER_EXTENSIONS: tuple[SparseOuterCechCochain, ...] = ()


def _frontier_digest() -> str:
    """Verify that the exact frontier still selects these neutrino characters."""

    payload = json.loads(FRONTIER_ARTIFACT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError("the flavor-frontier artifact digest failed")
    if (
        payload.get("selected_next_sector") != "dirac_neutrino"
        or payload.get("selected_required_new_matter_characters")
        != [list(character) for character in NEUTRINO_MATTER_CHARACTERS]
    ):
        raise ValueError("the exact neutrino-matter frontier changed")
    return digest


def _initialize_workers(
    extensions: tuple[SparseOuterCechCochain, ...],
) -> None:
    """Install the two immutable extension coefficients in each worker."""

    global _WORKER_EXTENSIONS
    _WORKER_EXTENSIONS = extensions


def _coefficient_job(
    job: tuple[
        tuple[int, int],
        int,
        SparseOuterCechCochain,
        int,
    ],
) -> tuple[
    tuple[int, int],
    int,
    int,
    SparseOuterCechCochain,
    SparseOuterCechCochain,
    bool,
    bool,
    bool,
]:
    """Solve one character, family, and parameter coefficient exactly."""

    character, family_index, representative, parameter_index = job
    if len(_WORKER_EXTENSIONS) != 2:
        raise ValueError("the universal extension basis is unavailable")
    product, correction, cycle, identity, strict = _lift_v2_coefficient(
        character,
        representative,
        _WORKER_EXTENSIONS[parameter_index],
    )
    return (
        character,
        family_index,
        parameter_index,
        product,
        correction,
        cycle,
        identity,
        strict,
    )


@dataclass(frozen=True, slots=True)
class NeutrinoMatterLifts:
    """The exact universal matter bases required by Dirac neutrinos."""

    parameters: tuple[str, str]
    v1_representatives: tuple[
        tuple[tuple[int, int], SparseOuterCechCochain], ...
    ]
    v2_lifts: tuple[UniversalV2MatterLift, ...]
    frontier_artifact_digest: str
    matter_artifact_digest: str
    universal_artifact_digest: str
    source_archive_sha256: str

    @property
    def exact(self) -> bool:
        """Return whether every neutrino-matter lift gate closes exactly."""

        v1_exact = all(
            _strict_character(representative, character, 1)
            for character, representative in self.v1_representatives
        )
        multiplicities = {
            character: sum(
                lift.character == character for lift in self.v2_lifts
            )
            for character in NEUTRINO_MATTER_CHARACTERS
        }
        return (
            self.parameters == ("a0", "a1")
            and tuple(
                character for character, _representative in self.v1_representatives
            )
            == NEUTRINO_MATTER_CHARACTERS
            and v1_exact
            and multiplicities == {
                character: 2 for character in NEUTRINO_MATTER_CHARACTERS
            }
            and all(lift.exact for lift in self.v2_lifts)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize exact lifts without choosing a carrier parameter."""

        return {
            "schema": "mixed-schoen-neutrino-matter-lifts-v1",
            "coefficient_field": "Q(omega)",
            "selected_sector": "dirac_neutrino",
            "carrier_parameter_basis": list(self.parameters),
            "matter_character_exponents": [
                list(character) for character in NEUTRINO_MATTER_CHARACTERS
            ],
            "source_archive_sha256": self.source_archive_sha256,
            "prerequisite_artifact_digests": {
                "flavor_frontier": self.frontier_artifact_digest,
                "strict_matter": self.matter_artifact_digest,
                "universal_cone": self.universal_artifact_digest,
            },
            "v1_constant_classes": [
                {
                    "character_exponents": list(character),
                    "term_count": len(representative.terms),
                    "digest": _cochain_digest((representative,)),
                    "strict_character_exact": True,
                }
                for character, representative in self.v1_representatives
            ],
            "v2_parameter_linear_lifts": [
                lift.as_record() for lift in self.v2_lifts
            ],
            "universal_visible_family_dimension_per_character": 3,
            "new_matter_parameter_correction_count": 8,
            "all_coefficientwise_cone_identities_exact": True,
            "all_lifts_strict_in_declared_characters": True,
            "all_neutrino_matter_lifts_exact": self.exact,
            "arbitrary_extension_point_selected": False,
            "observational_inputs_used": False,
            "yukawa_coefficient_computed": False,
            "next_required_object": (
                "complete carrier-derived tree-level Dirac-neutrino matrix"
            ),
        }


@cache
def mixed_schoen_neutrino_matter_lifts() -> NeutrinoMatterLifts:
    """Construct both source-selected neutrino matter bases exactly."""

    first, second = mixed_schoen_matter_representatives()
    _action_digest, parameters, extensions = _load_forward_basis()
    v1_representatives = []
    v2_representatives = []
    for character in NEUTRINO_MATTER_CHARACTERS:
        first_sector = next(
            sector for sector in first.sectors if sector.character == character
        )
        second_sector = next(
            sector for sector in second.sectors if sector.character == character
        )
        if len(first_sector.full_representatives) != 1:
            raise ValueError("a selected neutrino V1 character changed dimension")
        if len(second_sector.full_representatives) != 2:
            raise ValueError("a selected neutrino V2 character changed dimension")
        v1_representatives.append(
            (character, first_sector.full_representatives[0])
        )
        v2_representatives.extend(
            (character, family_index, representative)
            for family_index, representative in enumerate(
                second_sector.full_representatives,
                start=1,
            )
        )
    jobs = tuple(
        (character, family_index, representative, parameter_index)
        for character, family_index, representative in v2_representatives
        for parameter_index in range(2)
    )
    with ProcessPoolExecutor(
        max_workers=len(jobs),
        initializer=_initialize_workers,
        initargs=(extensions,),
    ) as executor:
        coefficients = tuple(executor.map(_coefficient_job, jobs))
    lifts = []
    for character, family_index, representative in v2_representatives:
        family = sorted(
            (
                coefficient
                for coefficient in coefficients
                if coefficient[:2] == (character, family_index)
            ),
            key=lambda coefficient: coefficient[2],
        )
        lift = UniversalV2MatterLift(
            character,
            family_index,
            representative,
            tuple(coefficient[4] for coefficient in family),
            tuple(coefficient[3] for coefficient in family),
            all(coefficient[5] for coefficient in family),
            all(coefficient[6] for coefficient in family),
            _strict_character(representative, character, 2)
            and all(coefficient[7] for coefficient in family),
        )
        if not lift.exact:
            raise ValueError("one universal neutrino V2 matter lift failed")
        lifts.append(lift)
    result = NeutrinoMatterLifts(
        parameters,
        tuple(v1_representatives),
        tuple(lifts),
        _frontier_digest(),
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
        raise ValueError("the selected neutrino matter bases failed")
    return result


def write_neutrino_matter_lifts(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed neutrino-matter lift certificate."""

    payload = mixed_schoen_neutrino_matter_lifts().as_record()
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
    """Regenerate neutrino matter lifts and print their exact gate."""

    payload = write_neutrino_matter_lifts()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "all_neutrino_matter_lifts_exact: "
        f"{payload['all_neutrino_matter_lifts_exact']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "NEUTRINO_MATTER_CHARACTERS",
    "NeutrinoMatterLifts",
    "OUTPUT",
    "mixed_schoen_neutrino_matter_lifts",
    "write_neutrino_matter_lifts",
]
