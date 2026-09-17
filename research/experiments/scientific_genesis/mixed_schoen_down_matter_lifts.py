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

import gzip
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
from .mixed_schoen_outer_universal_cone import _load_forward_basis, _representative
from .mixed_schoen_universal_matter_lifts import (
    UniversalV2MatterLift,
    _lift_v2_coefficient,
    _source_digest,
    _strict_character,
    _verified_digest,
)
from .published_outer_cech_invariants import _cech_record

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/mixed_schoen_down_matter_lifts.json"
)
CACHE_DIRECTORY = (
    ROOT
    / "data/generated/scientific_genesis/"
    ".mixed_schoen_down_lift_cache"
)
SOURCE_MATTER_CHARACTERS = ((2, 1), (1, 0))
FORWARD_MATTER_CHARACTERS = tuple(
    inverse_character(character) for character in SOURCE_MATTER_CHARACTERS
)
SOURCE_DOWN_HIGGS_CHARACTER = (0, 2)
FORWARD_DOWN_HIGGS_CHARACTER = inverse_character(SOURCE_DOWN_HIGGS_CHARACTER)
_WORKER_EXTENSIONS: tuple[SparseOuterCechCochain, ...] = ()

LiftCoefficient = tuple[
    tuple[int, int],
    int,
    int,
    SparseOuterCechCochain,
    SparseOuterCechCochain,
    bool,
    bool,
    bool,
]
LiftJob = tuple[
    tuple[int, int],
    int,
    SparseOuterCechCochain,
    int,
]


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


def _initialize_workers(
    extensions: tuple[SparseOuterCechCochain, ...],
) -> None:
    """Install immutable extension coefficients in each lift worker."""

    global _WORKER_EXTENSIONS
    _WORKER_EXTENSIONS = extensions


def _cache_path(
    character: tuple[int, int],
    family_index: int,
    parameter_index: int,
) -> Path:
    """Return one deterministic ignored checkpoint path."""

    return CACHE_DIRECTORY / (
        f"chi-{character[0]}-{character[1]}-"
        f"family-{family_index}-a{parameter_index}.json.gz"
    )


def _cache_input_digest(
    character: tuple[int, int],
    family_index: int,
    parameter_index: int,
    representative: SparseOuterCechCochain,
    extension: SparseOuterCechCochain,
) -> str:
    """Fingerprint every exact input determining one down lift."""

    return _canonical_digest(
        {
            "character_exponents": list(character),
            "local_family_index": family_index,
            "parameter_index": parameter_index,
            "v2_representative_digest": _cochain_digest((representative,)),
            "extension_coefficient_digest": _cochain_digest((extension,)),
            "source_archive_sha256": _source_digest(),
        }
    )


@cache
def _certified_lift_records() -> (
    dict[tuple[tuple[int, int], int, int], dict[str, object]]
):
    """Index exact coefficient evidence from the aggregate certificate."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("the aggregate down-lift artifact is malformed")
    digest = payload.pop("artifact_digest", None)
    prerequisites = payload.get("prerequisite_artifact_digests")
    physical_slice = payload.get("physical_slice")
    if (
        not isinstance(digest, str)
        or digest != _canonical_digest(payload)
        or payload.get("schema") != "mixed-schoen-down-matter-lifts-v1"
        or payload.get("all_coefficientwise_cone_identities_exact") is not True
        or payload.get("all_lifts_strict_in_forward_characters") is not True
        or payload.get("exact") is not True
        or not isinstance(prerequisites, dict)
        or prerequisites.get("character_convention") != _convention_digest()
        or prerequisites.get("strict_matter")
        != _verified_digest(
            MATTER_ARTIFACT,
            "all_strict_character_representatives_exact",
            True,
        )
        or prerequisites.get("universal_cone")
        != _verified_digest(
            UNIVERSAL_ARTIFACT,
            "equivariant_descent_exact",
            True,
        )
        or not isinstance(physical_slice, dict)
        or physical_slice.get("source_archive_sha256") != _source_digest()
        or physical_slice.get("forward_matter_character_exponents")
        != [list(character) for character in FORWARD_MATTER_CHARACTERS]
    ):
        raise ValueError("the aggregate down-lift certificate failed")
    raw_lifts = payload.get("v2_parameter_linear_lifts")
    if not isinstance(raw_lifts, list):
        raise ValueError("the aggregate down-lift records are missing")
    records: dict[tuple[tuple[int, int], int, int], dict[str, object]] = {}
    for raw_lift in raw_lifts:
        if not isinstance(raw_lift, dict):
            raise ValueError("an aggregate down-lift record is malformed")
        raw_character = raw_lift.get("forward_character_exponents")
        family_index = raw_lift.get("local_family_index")
        raw_coefficients = raw_lift.get("parameter_coefficients")
        if (
            not isinstance(raw_character, list)
            or len(raw_character) != 2
            or not all(isinstance(value, int) for value in raw_character)
            or not isinstance(family_index, int)
            or not isinstance(raw_coefficients, list)
            or raw_lift.get("exact") is not True
        ):
            raise ValueError("an aggregate down-lift basis record is invalid")
        character = raw_character[0], raw_character[1]
        for parameter_index, raw_coefficient in enumerate(raw_coefficients):
            if (
                not isinstance(raw_coefficient, dict)
                or raw_coefficient.get("parameter") != f"a{parameter_index}"
            ):
                raise ValueError("an aggregate down coefficient record is invalid")
            key = character, family_index, parameter_index
            if key in records:
                raise ValueError("an aggregate down coefficient is duplicated")
            records[key] = {
                "v2_term_count": raw_lift.get("v2_term_count"),
                "v2_digest": raw_lift.get("v2_digest"),
                **raw_coefficient,
            }
    expected = {
        (character, family_index, parameter_index)
        for character in FORWARD_MATTER_CHARACTERS
        for family_index in (1, 2)
        for parameter_index in (0, 1)
    }
    if set(records) != expected:
        raise ValueError("the aggregate down-lift coefficient basis is incomplete")
    return records


def _write_coefficient_cache(
    result: LiftCoefficient,
    representative: SparseOuterCechCochain,
    extension: SparseOuterCechCochain,
) -> None:
    """Atomically checkpoint one exact lift without promoting cache data."""

    character, family_index, parameter_index, product, correction, cycle, identity, strict = (
        result
    )
    payload: dict[str, object] = {
        "schema": "mixed-schoen-down-lift-cache-v1",
        "character_exponents": list(character),
        "local_family_index": family_index,
        "parameter_index": parameter_index,
        "input_digest": _cache_input_digest(
            character,
            family_index,
            parameter_index,
            representative,
            extension,
        ),
        "product": _cech_record(product, "product"),
        "product_digest": _cochain_digest((product,)),
        "correction": _cech_record(correction, "correction"),
        "correction_digest": _cochain_digest((correction,)),
        "product_cycle_exact": cycle,
        "correction_identity_exact": identity,
        "strict_characters_exact": strict,
    }
    payload["cache_digest"] = _canonical_digest(payload)
    path = _cache_path(character, family_index, parameter_index)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with gzip.open(temporary, "wt", encoding="utf-8") as stream:
        json.dump(payload, stream, sort_keys=True, separators=(",", ":"))
    temporary.replace(path)


def _load_coefficient_cache(
    job: LiftJob,
    extensions: tuple[SparseOuterCechCochain, ...],
) -> LiftCoefficient | None:
    """Load a checkpoint only after input and aggregate-evidence gates pass."""

    character, family_index, representative, parameter_index = job
    path = _cache_path(character, family_index, parameter_index)
    if not path.is_file():
        return None
    try:
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            payload = json.load(stream)
        if not isinstance(payload, dict):
            return None
        cache_digest = payload.pop("cache_digest", None)
        if not isinstance(cache_digest, str) or cache_digest != _canonical_digest(
            payload
        ):
            return None
        if (
            payload.get("schema") != "mixed-schoen-down-lift-cache-v1"
            or payload.get("character_exponents") != list(character)
            or payload.get("local_family_index") != family_index
            or payload.get("parameter_index") != parameter_index
            or payload.get("input_digest")
            != _cache_input_digest(
                character,
                family_index,
                parameter_index,
                representative,
                extensions[parameter_index],
            )
            or payload.get("product_cycle_exact") is not True
            or payload.get("correction_identity_exact") is not True
            or payload.get("strict_characters_exact") is not True
        ):
            return None
        product = _representative(payload.get("product"))
        correction = _representative(payload.get("correction"))
        certified = _certified_lift_records()[
            (character, family_index, parameter_index)
        ]
        if (
            payload.get("product_digest") != _cochain_digest((product,))
            or payload.get("correction_digest") != _cochain_digest((correction,))
            or certified.get("v2_term_count") != len(representative.terms)
            or certified.get("v2_digest") != _cochain_digest((representative,))
            or certified.get("product_term_count") != len(product.terms)
            or certified.get("product_digest") != payload.get("product_digest")
            or certified.get("correction_term_count") != len(correction.terms)
            or certified.get("correction_digest")
            != payload.get("correction_digest")
        ):
            return None
        return (
            character,
            family_index,
            parameter_index,
            product,
            correction,
            True,
            True,
            True,
        )
    except (EOFError, KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return None


def _coefficient_job(job: LiftJob) -> LiftCoefficient:
    """Solve and checkpoint one character, family, and parameter lift."""

    character, family_index, representative, parameter_index = job
    if len(_WORKER_EXTENSIONS) != 2:
        raise ValueError("the universal extension basis is unavailable")
    product, correction, cycle, identity, strict = _lift_v2_coefficient(
        character,
        representative,
        _WORKER_EXTENSIONS[parameter_index],
    )
    result: LiftCoefficient = (
        character,
        family_index,
        parameter_index,
        product,
        correction,
        cycle,
        identity,
        strict,
    )
    _write_coefficient_cache(
        result,
        representative,
        _WORKER_EXTENSIONS[parameter_index],
    )
    print(
        "checkpointed down lift "
        f"chi={character} family={family_index} a{parameter_index}",
        flush=True,
    )
    return result


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
    v1_representatives: list[
        tuple[tuple[int, int], SparseOuterCechCochain]
    ] = []
    v2_representatives: list[
        tuple[tuple[int, int], int, SparseOuterCechCochain]
    ] = []
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
    cached = tuple(
        cached_result
        for job in jobs
        if (cached_result := _load_coefficient_cache(job, extensions)) is not None
    )
    for character, family_index, parameter_index, *_remainder in cached:
        print(
            "reused down lift "
            f"chi={character} family={family_index} a{parameter_index}",
            flush=True,
        )
    cached_keys = {result[:3] for result in cached}
    pending = tuple(
        job
        for job in jobs
        if (job[0], job[1], job[3]) not in cached_keys
    )
    computed: tuple[LiftCoefficient, ...] = ()
    if pending:
        with ProcessPoolExecutor(
            max_workers=len(pending),
            initializer=_initialize_workers,
            initargs=(extensions,),
        ) as executor:
            computed = tuple(executor.map(_coefficient_job, pending))
    coefficients = cached + computed
    lifts: list[UniversalV2MatterLift] = []
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
            raise ValueError("one universal down V2 matter lift failed")
        lifts.append(lift)
    result = DownMatterLifts(
        ("a0", "a1"),
        tuple(v1_representatives),
        tuple(lifts),
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
    raw_lifts = payload["v2_parameter_linear_lifts"]
    if not isinstance(raw_lifts, list):
        raise TypeError("the serialized down-lift basis is invalid")
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "v2_parameter_linear_lift_count: "
        f"{len(raw_lifts)}"
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
