"""Lift physical down-matter sectors into the reverse universal cone.

Owns:
    Constant V2 subobject classes and six-parameter V1 quotient lifts for the
    convention-corrected down sector on the frozen reverse carrier component.

Depends on:
    Strict synchronized matter cocycles, exact character inversion, the reverse
    invariant outer basis, signed common-DGA composition, and exact contraction.

Must not:
    Choose a P5 point, reuse forward correction coefficients, infer a Yukawa
    value, or import masses, mixings, or observational selectors.

Phase 0:
    Research-only reverse universal matter inputs for one physical flavor slice.
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
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)

from .computable_one_theory_reverse_carrier_state import (
    OUTPUT as REVERSE_CARRIER_ARTIFACT,
)
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_character_convention import (
    OUTPUT as CONVENTION_ARTIFACT,
)
from .mixed_schoen_character_convention import inverse_character
from .mixed_schoen_common_dga import exact_mixed_primitive, mixed_outer_cup
from .mixed_schoen_down_matter_lifts import (
    SOURCE_DOWN_HIGGS_CHARACTER,
    SOURCE_MATTER_CHARACTERS,
)
from .mixed_schoen_matter_representatives import (
    OUTPUT as MATTER_ARTIFACT,
)
from .mixed_schoen_matter_representatives import (
    _character_project,
    _cochain_digest,
    _matter_contraction,
    mixed_schoen_matter_representatives,
)
from .mixed_schoen_outer_transfer import (
    mixed_schoen_unit,
    mixed_transferred_outer_hom,
)
from .mixed_schoen_outer_universal_cone import (
    _load_orientation_basis,
    _representative,
)
from .mixed_schoen_reverse_outer_universal_cone import (
    OUTPUT as REVERSE_UNIVERSAL_ARTIFACT,
)
from .mixed_schoen_universal_matter_lifts import (
    _source_digest,
    _strict_character,
    _verified_digest,
)
from .published_outer_cech_invariants import _cech_record

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_reverse_down_matter_lifts.json"
)
CACHE_DIRECTORY = (
    ROOT
    / "data/generated/scientific_genesis/"
    ".mixed_schoen_reverse_down_lift_cache"
)
FORWARD_MATTER_CHARACTERS = tuple(
    inverse_character(character) for character in SOURCE_MATTER_CHARACTERS
)
FORWARD_DOWN_HIGGS_CHARACTER = inverse_character(SOURCE_DOWN_HIGGS_CHARACTER)
_WORKER_EXTENSIONS: tuple[SparseOuterCechCochain, ...] = ()

LiftCoefficient = tuple[
    tuple[int, int],
    int,
    SparseOuterCechCochain,
    SparseOuterCechCochain,
    bool,
    bool,
    bool,
]
LiftJob = tuple[
    tuple[int, int],
    SparseOuterCechCochain,
    int,
]


def _verified_payload(path: Path, schema: str) -> str:
    """Verify one content-addressed prerequisite by exact schema."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if (
        not isinstance(digest, str)
        or digest != _canonical_digest(payload)
        or payload.get("schema") != schema
    ):
        raise ValueError(f"reverse matter prerequisite failed: {path.name}")
    return digest


def _convention_digest() -> str:
    """Verify the source-to-forward character convention for physical H_d."""

    payload = json.loads(CONVENTION_ARTIFACT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if (
        not isinstance(digest, str)
        or digest != _canonical_digest(payload)
        or payload.get("exact") is not True
        or payload.get("physical_down_higgs_representative_available") is not True
        or payload.get("strict_cochain_source_character")
        != list(SOURCE_DOWN_HIGGS_CHARACTER)
        or payload.get("strict_cochain_forward_character")
        != list(FORWARD_DOWN_HIGGS_CHARACTER)
    ):
        raise ValueError("the physical down-sector character routing changed")
    return digest


def _cache_path(character: tuple[int, int], parameter_index: int) -> Path:
    """Return one deterministic ignored reverse-lift checkpoint path."""

    return CACHE_DIRECTORY / (
        f"chi-{character[0]}-{character[1]}-b{parameter_index}.json.gz"
    )


def _cache_input_digest(
    character: tuple[int, int],
    parameter_index: int,
    representative: SparseOuterCechCochain,
    extension: SparseOuterCechCochain,
) -> str:
    """Fingerprint every exact input determining one reverse coefficient."""

    return _canonical_digest(
        {
            "character_exponents": list(character),
            "parameter_index": parameter_index,
            "v1_representative_digest": _cochain_digest((representative,)),
            "reverse_extension_digest": _cochain_digest((extension,)),
            "source_archive_sha256": _source_digest(),
        }
    )


def _lift_v1_coefficient(
    character: tuple[int, int],
    v1_representative: SparseOuterCechCochain,
    extension: SparseOuterCechCochain,
) -> tuple[
    SparseOuterCechCochain,
    SparseOuterCechCochain,
    bool,
    bool,
    bool,
]:
    """Solve one V2 correction coefficient for a reverse V1 quotient class."""

    _first, second = mixed_schoen_constituents()
    contraction = _matter_contraction(2)
    transferred = mixed_transferred_outer_hom(second, mixed_schoen_unit())
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    product = mixed_outer_cup(extension, v1_representative)
    product_cycle = contraction.differential(product).is_zero()
    strict = _strict_character(product, character, 2)
    primitive = exact_mixed_primitive(
        product,
        contraction,
        transferred,
        2,
    ).primitive
    correction = _character_project(
        primitive,
        contraction,
        actions,
        character,
    ).scale(-1)
    correction_identity = (
        contraction.differential(correction) + product
    ).is_zero()
    strict = strict and _strict_character(correction, character, 2)
    return product, correction, product_cycle, correction_identity, strict


def _write_cache(
    result: LiftCoefficient,
    representative: SparseOuterCechCochain,
    extension: SparseOuterCechCochain,
) -> None:
    """Atomically checkpoint one exact reverse coefficient."""

    character, parameter_index, product, correction, cycle, identity, strict = result
    payload: dict[str, object] = {
        "schema": "mixed-schoen-reverse-down-lift-cache-v1",
        "character_exponents": list(character),
        "parameter_index": parameter_index,
        "input_digest": _cache_input_digest(
            character,
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
        "strict_character_exact": strict,
    }
    payload["cache_digest"] = _canonical_digest(payload)
    path = _cache_path(character, parameter_index)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with gzip.open(temporary, "wt", encoding="utf-8") as stream:
        json.dump(payload, stream, sort_keys=True, separators=(",", ":"))
    temporary.replace(path)


def _load_cache(
    job: LiftJob,
    extensions: tuple[SparseOuterCechCochain, ...],
) -> LiftCoefficient | None:
    """Load one checkpoint only after rechecking all exact identities."""

    character, representative, parameter_index = job
    extension = extensions[parameter_index]
    path = _cache_path(character, parameter_index)
    if not path.is_file():
        return None
    try:
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            payload = json.load(stream)
        if not isinstance(payload, dict):
            return None
        cache_digest = payload.pop("cache_digest", None)
        if (
            not isinstance(cache_digest, str)
            or cache_digest != _canonical_digest(payload)
            or payload.get("schema")
            != "mixed-schoen-reverse-down-lift-cache-v1"
            or payload.get("character_exponents") != list(character)
            or payload.get("parameter_index") != parameter_index
            or payload.get("input_digest")
            != _cache_input_digest(
                character,
                parameter_index,
                representative,
                extension,
            )
        ):
            return None
        product = _representative(payload.get("product"))
        correction = _representative(payload.get("correction"))
        contraction = _matter_contraction(2)
        exact_product = mixed_outer_cup(extension, representative)
        cycle = contraction.differential(product).is_zero()
        identity = (contraction.differential(correction) + product).is_zero()
        strict = (
            _strict_character(representative, character, 1)
            and _strict_character(product, character, 2)
            and _strict_character(correction, character, 2)
        )
        if (
            product != exact_product
            or payload.get("product_digest") != _cochain_digest((product,))
            or payload.get("correction_digest") != _cochain_digest((correction,))
            or not cycle
            or not identity
            or not strict
        ):
            return None
        return character, parameter_index, product, correction, cycle, identity, strict
    except (EOFError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return None


def _initialize_workers(
    extensions: tuple[SparseOuterCechCochain, ...],
) -> None:
    """Install immutable reverse extension coefficients in each worker."""

    global _WORKER_EXTENSIONS
    _WORKER_EXTENSIONS = extensions


def _coefficient_job(job: LiftJob) -> LiftCoefficient:
    """Compute and checkpoint one reverse matter coefficient."""

    character, representative, parameter_index = job
    if len(_WORKER_EXTENSIONS) != 6:
        raise ValueError("the reverse extension basis is unavailable")
    extension = _WORKER_EXTENSIONS[parameter_index]
    product, correction, cycle, identity, strict = _lift_v1_coefficient(
        character,
        representative,
        extension,
    )
    result: LiftCoefficient = (
        character,
        parameter_index,
        product,
        correction,
        cycle,
        identity,
        strict,
    )
    _write_cache(result, representative, extension)
    print(
        f"checkpointed reverse down lift chi={character} b{parameter_index}",
        flush=True,
    )
    return result


@dataclass(frozen=True, slots=True)
class UniversalV1MatterLift:
    """One reverse quotient class with six V2 correction coefficients."""

    character: tuple[int, int]
    v1_representative: SparseOuterCechCochain
    v2_corrections: tuple[SparseOuterCechCochain, ...]
    products: tuple[SparseOuterCechCochain, ...]
    product_cycles_exact: bool
    correction_identities_exact: bool
    strict_characters_exact: bool

    @property
    def exact(self) -> bool:
        """Return every reverse universal-cone lift gate."""

        return (
            len(self.v2_corrections) == 6
            and len(self.products) == 6
            and self.product_cycles_exact
            and self.correction_identities_exact
            and self.strict_characters_exact
        )

    def as_record(self) -> dict[str, object]:
        """Serialize exact sparse coefficient evidence."""

        return {
            "forward_character_exponents": list(self.character),
            "source_character_exponents": list(inverse_character(self.character)),
            "v1_term_count": len(self.v1_representative.terms),
            "v1_digest": _cochain_digest((self.v1_representative,)),
            "parameter_coefficients": [
                {
                    "parameter": f"b{index}",
                    "product_term_count": len(product.terms),
                    "product_digest": _cochain_digest((product,)),
                    "correction_term_count": len(correction.terms),
                    "correction_digest": _cochain_digest((correction,)),
                }
                for index, (product, correction) in enumerate(
                    zip(self.products, self.v2_corrections, strict=True)
                )
            ],
            "product_cycles_exact": self.product_cycles_exact,
            "correction_identities_exact": self.correction_identities_exact,
            "strict_characters_exact": self.strict_characters_exact,
            "exact": self.exact,
        }


@dataclass(frozen=True, slots=True)
class ReverseDownMatterLifts:
    """Minimum exact down-sector matter basis over the reverse P5."""

    parameters: tuple[str, ...]
    v2_constant_representatives: tuple[
        tuple[tuple[int, int], int, SparseOuterCechCochain], ...
    ]
    v1_lifts: tuple[UniversalV1MatterLift, ...]
    convention_artifact_digest: str
    matter_artifact_digest: str
    universal_artifact_digest: str
    carrier_artifact_digest: str
    source_archive_sha256: str

    @property
    def exact(self) -> bool:
        """Return all reverse matter basis and provenance gates."""

        constant_multiplicities = {
            character: sum(
                item_character == character
                for item_character, _index, _cochain in self.v2_constant_representatives
            )
            for character in FORWARD_MATTER_CHARACTERS
        }
        return (
            self.parameters == tuple(f"b{index}" for index in range(6))
            and len(self.v2_constant_representatives) == 4
            and set(constant_multiplicities.values()) == {2}
            and tuple(lift.character for lift in self.v1_lifts)
            == FORWARD_MATTER_CHARACTERS
            and all(lift.exact for lift in self.v1_lifts)
            and self.source_archive_sha256 == _source_digest()
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the reverse down-sector universal matter certificate."""

        return {
            "schema": "mixed-schoen-reverse-down-matter-lifts-v1",
            "coefficient_field": "Q(omega)",
            "carrier_parameter_basis": list(self.parameters),
            "carrier_locus": "P^5(Q(omega)) x K_reverse^s",
            "extension_sequence": "0 -> V2 -> E_reverse -> V1 -> 0",
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
                "reverse_universal_cone": self.universal_artifact_digest,
                "reverse_carrier": self.carrier_artifact_digest,
            },
            "v2_constant_classes": [
                {
                    "forward_character_exponents": list(character),
                    "source_character_exponents": list(
                        inverse_character(character)
                    ),
                    "local_family_index": family_index,
                    "term_count": len(cochain.terms),
                    "digest": _cochain_digest((cochain,)),
                }
                for character, family_index, cochain in self.v2_constant_representatives
            ],
            "v1_parameter_linear_lifts": [
                lift.as_record() for lift in self.v1_lifts
            ],
            "universal_visible_family_dimension_per_character": 3,
            "all_coefficientwise_cone_identities_exact": True,
            "all_lifts_strict_in_forward_characters": True,
            "source_characters_obtained_only_by_exact_inversion": True,
            "arbitrary_extension_point_selected": False,
            "observational_inputs_used": False,
            "exact": self.exact,
            "next_required_object": (
                "a strict reverse universal H_d lift in forward character (0,1)"
            ),
        }


@cache
def mixed_schoen_reverse_down_matter_lifts() -> ReverseDownMatterLifts:
    """Construct the minimum physical down matter basis over reverse P5."""

    first, second = mixed_schoen_matter_representatives()
    _action_digest, parameters, extensions = _load_orientation_basis(
        "V2",
        "V1",
        "b",
    )
    if parameters != tuple(f"b{index}" for index in range(6)):
        raise ValueError("the reverse parameter basis changed")
    v2_constants = []
    v1_representatives = []
    for character in FORWARD_MATTER_CHARACTERS:
        first_sector = next(
            sector for sector in first.sectors if sector.character == character
        )
        second_sector = next(
            sector for sector in second.sectors if sector.character == character
        )
        if len(first_sector.full_representatives) != 1:
            raise ValueError("one reverse quotient matter class was expected")
        if len(second_sector.full_representatives) != 2:
            raise ValueError("two reverse subobject matter classes were expected")
        v1_representatives.append((character, first_sector.full_representatives[0]))
        v2_constants.extend(
            (character, family_index, representative)
            for family_index, representative in enumerate(
                second_sector.full_representatives,
                start=1,
            )
        )
    jobs = tuple(
        (character, representative, parameter_index)
        for character, representative in v1_representatives
        for parameter_index in range(6)
    )
    cached = tuple(
        result
        for job in jobs
        if (result := _load_cache(job, extensions)) is not None
    )
    cached_keys = {(item[0], item[1]) for item in cached}
    pending = tuple(
        job for job in jobs if (job[0], job[2]) not in cached_keys
    )
    computed: tuple[LiftCoefficient, ...] = ()
    if pending:
        with ProcessPoolExecutor(
            max_workers=min(4, len(pending)),
            initializer=_initialize_workers,
            initargs=(extensions,),
        ) as executor:
            computed = tuple(executor.map(_coefficient_job, pending))
    coefficients = cached + computed
    lifts = []
    for character, representative in v1_representatives:
        family = sorted(
            (item for item in coefficients if item[0] == character),
            key=lambda item: item[1],
        )
        lift = UniversalV1MatterLift(
            character,
            representative,
            tuple(item[3] for item in family),
            tuple(item[2] for item in family),
            all(item[4] for item in family),
            all(item[5] for item in family),
            _strict_character(representative, character, 1)
            and all(item[6] for item in family),
        )
        if not lift.exact:
            raise ValueError("one reverse universal V1 matter lift failed")
        lifts.append(lift)
    result = ReverseDownMatterLifts(
        parameters,
        tuple(v2_constants),
        tuple(lifts),
        _convention_digest(),
        _verified_digest(
            MATTER_ARTIFACT,
            "all_strict_character_representatives_exact",
            True,
        ),
        _verified_digest(
            REVERSE_UNIVERSAL_ARTIFACT,
            "equivariant_descent_exact",
            True,
        ),
        _verified_payload(
            REVERSE_CARRIER_ARTIFACT,
            "computable-one-theory-reverse-carrier-state-v1",
        ),
        _source_digest(),
    )
    if not result.exact:
        raise ValueError("the reverse down-matter lift certificate failed")
    return result


def write_mixed_schoen_reverse_down_matter_lifts(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed reverse down-matter certificate."""

    payload = mixed_schoen_reverse_down_matter_lifts().as_record()
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
    """Regenerate the exact reverse down-matter lift certificate."""

    payload = write_mixed_schoen_reverse_down_matter_lifts()
    raw_lifts = payload["v1_parameter_linear_lifts"]
    if not isinstance(raw_lifts, list):
        raise TypeError("the reverse serialized matter basis is invalid")
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"v1_parameter_linear_lift_count: {len(raw_lifts)}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "FORWARD_DOWN_HIGGS_CHARACTER",
    "FORWARD_MATTER_CHARACTERS",
    "ReverseDownMatterLifts",
    "UniversalV1MatterLift",
    "mixed_schoen_reverse_down_matter_lifts",
    "write_mixed_schoen_reverse_down_matter_lifts",
]
