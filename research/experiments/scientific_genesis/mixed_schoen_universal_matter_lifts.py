"""Lift the minimum physical matter sectors into the universal visible cone.

Owns:
    Parameter-linear V1 corrections for the V2 matter classes needed by the
    first up-type Yukawa matrix and exact universal-cone cocycle identities.

Depends on:
    Strict mixed matter character classes, the lawful universal outer cocycle,
    signed common-DGA composition, and the exact mixed contraction.

Must not:
    Choose a point of the carrier P1, infer a Higgs lift, normalize a trace, or
    import measured masses, mixings, or a published Yukawa texture as input.

Phase 0:
    Research-only universal-cone lifts for the minimum matter character sectors.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.numbers import OMEGA
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)

from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_common_dga import exact_mixed_primitive, mixed_outer_cup
from .mixed_schoen_matter_representatives import (
    OUTPUT as MATTER_ARTIFACT,
)
from .mixed_schoen_matter_representatives import (
    _character_project,
    _cochain_digest,
    _matter_contraction,
    mixed_schoen_matter_representatives,
)
from .mixed_schoen_outer_actions import _full_action
from .mixed_schoen_outer_transfer import (
    mixed_schoen_unit,
    mixed_transferred_outer_hom,
)
from .mixed_schoen_outer_universal_cone import (
    OUTPUT as UNIVERSAL_ARTIFACT,
)
from .mixed_schoen_outer_universal_cone import _load_forward_basis

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/mixed_schoen_universal_matter_lifts.json"
)
SOURCE_MANIFEST = ROOT / "data/published/visible_carrier/source_manifest.json"
SPECTRUM_ARXIV_ID = "hep-th/0512177"
SPECTRUM_SOURCE_SHA256 = (
    "ad4ea10b3d765553ccdd072922a6bda619866ea814c532b8ffe74ddafc7fe73f"
)
UP_MATTER_CHARACTERS = ((2, 1), (1, 1))
UP_HIGGS_CHARACTER = (0, 1)
_WORKER_EXTENSIONS: tuple[SparseOuterCechCochain, ...] = ()


def _verified_digest(path: Path, gate: str, expected: object) -> str:
    """Verify one content-addressed prerequisite and its required gate."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest failed: {path.name}")
    if payload.get(gate) != expected:
        raise ValueError(f"upstream artifact gate changed: {path.name}")
    return digest


def _source_digest() -> str:
    """Verify the source archive that fixes the Wilson character assignment."""

    payload = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    sources = payload.get("sources")
    if not isinstance(sources, list):
        raise ValueError("the visible-carrier source manifest is malformed")
    matches = [
        source
        for source in sources
        if isinstance(source, dict) and source.get("arxiv_id") == SPECTRUM_ARXIV_ID
    ]
    if (
        len(matches) != 1
        or matches[0].get("source_archive_sha256") != SPECTRUM_SOURCE_SHA256
    ):
        raise ValueError("the spectrum source archive digest changed")
    return SPECTRUM_SOURCE_SHA256


def _strict_character(
    cochain: SparseOuterCechCochain,
    character: tuple[int, int],
    factor: int,
) -> bool:
    """Check the declared joint deck character on one strict cochain."""

    contraction = _matter_contraction(factor)
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    return all(
        _full_action(
            cochain,
            contraction.left,
            contraction.right,
            actions[generator],
        )
        == cochain.scale(OMEGA ** character[index])
        for index, generator in enumerate(("P", "T"))
    )


@dataclass(frozen=True, slots=True)
class UniversalV2MatterLift:
    """One V2 class with parameter-linear V1 correction coefficients."""

    character: tuple[int, int]
    local_family_index: int
    v2_representative: SparseOuterCechCochain
    v1_corrections: tuple[SparseOuterCechCochain, ...]
    products: tuple[SparseOuterCechCochain, ...]
    product_cycles_exact: bool
    correction_identities_exact: bool
    strict_characters_exact: bool

    @property
    def exact(self) -> bool:
        """Return all universal-cone lift gates."""

        return (
            len(self.v1_corrections) == 2
            and len(self.products) == 2
            and self.product_cycles_exact
            and self.correction_identities_exact
            and self.strict_characters_exact
        )

    def as_record(self) -> dict[str, object]:
        """Serialize sparse sizes and exact coefficientwise certificates."""

        return {
            "character_exponents": list(self.character),
            "local_family_index": self.local_family_index,
            "v2_term_count": len(self.v2_representative.terms),
            "v2_digest": _cochain_digest((self.v2_representative,)),
            "parameter_coefficients": [
                {
                    "parameter": f"a{index}",
                    "product_term_count": len(product.terms),
                    "product_digest": _cochain_digest((product,)),
                    "correction_term_count": len(correction.terms),
                    "correction_digest": _cochain_digest((correction,)),
                }
                for index, (product, correction) in enumerate(
                    zip(self.products, self.v1_corrections, strict=True)
                )
            ],
            "product_cycles_exact": self.product_cycles_exact,
            "correction_identities_exact": self.correction_identities_exact,
            "strict_characters_exact": self.strict_characters_exact,
            "exact": self.exact,
        }


@dataclass(frozen=True, slots=True)
class UniversalMatterSectorLifts:
    """Minimum exact matter basis for the first up-type Yukawa sector."""

    parameters: tuple[str, str]
    v1_representatives: tuple[
        tuple[tuple[int, int], SparseOuterCechCochain], ...
    ]
    v2_lifts: tuple[UniversalV2MatterLift, ...]
    matter_artifact_digest: str
    universal_artifact_digest: str
    source_archive_sha256: str

    def __post_init__(self) -> None:
        if self.parameters != ("a0", "a1"):
            raise ValueError("the frozen universal carrier parameter basis changed")
        if tuple(character for character, _cochain in self.v1_representatives) != (
            *UP_MATTER_CHARACTERS,
        ):
            raise ValueError("the minimum V1 matter character order changed")
        if len(self.v2_lifts) != 4 or not all(
            lift.exact for lift in self.v2_lifts
        ):
            raise ValueError("the minimum universal V2 matter lifts are incomplete")
        multiplicities = {
            character: sum(lift.character == character for lift in self.v2_lifts)
            for character in UP_MATTER_CHARACTERS
        }
        if set(multiplicities.values()) != {2}:
            raise ValueError("each up-type matter sector requires two V2 lifts")
        if self.source_archive_sha256 != SPECTRUM_SOURCE_SHA256:
            raise ValueError("the up-type Wilson source digest changed")

    def as_record(self) -> dict[str, object]:
        """Serialize the exact parameter-linear universal matter certificate."""

        return {
            "schema": "mixed-schoen-universal-matter-lifts-v1",
            "coefficient_field": "Q(omega)",
            "carrier_parameter_basis": list(self.parameters),
            "carrier_locus": "P^1(Q(omega)) x K^s",
            "physical_slice": {
                "matrix": "up-type holomorphic Yukawa",
                "matter_character_exponents": [
                    list(character) for character in UP_MATTER_CHARACTERS
                ],
                "required_higgs_character_exponents": list(UP_HIGGS_CHARACTER),
                "source": {
                    "arxiv_id": SPECTRUM_ARXIV_ID,
                    "version": "v3",
                    "source_archive_sha256": self.source_archive_sha256,
                    "locator": "eq:burt4; eq:19",
                },
            },
            "prerequisite_artifact_digests": {
                "strict_matter": self.matter_artifact_digest,
                "universal_cone": self.universal_artifact_digest,
            },
            "v1_constant_classes": [
                {
                    "character_exponents": list(character),
                    "term_count": len(cochain.terms),
                    "digest": _cochain_digest((cochain,)),
                }
                for character, cochain in self.v1_representatives
            ],
            "v2_parameter_linear_lifts": [
                lift.as_record() for lift in self.v2_lifts
            ],
            "universal_visible_family_dimension_per_character": 3,
            "all_coefficientwise_cone_identities_exact": True,
            "all_lifts_strict_in_declared_characters": True,
            "arbitrary_extension_point_selected": False,
            "higgs_lift_computed": False,
            "next_required_object": (
                "one strict full-Schoen Higgs representative in character (0,1)"
            ),
            "status": (
                "exact parameter-linear universal matter basis for the first "
                "up-type Yukawa matrix"
            ),
        }


def _lift_v2_class(
    character: tuple[int, int],
    local_family_index: int,
    v2_representative: SparseOuterCechCochain,
    extensions: tuple[SparseOuterCechCochain, ...],
) -> UniversalV2MatterLift:
    """Solve both universal parameter coefficients for one strict V2 class."""

    first, _second = mixed_schoen_constituents()
    unit = mixed_schoen_unit()
    contraction = _matter_contraction(1)
    transferred = mixed_transferred_outer_hom(first, unit)
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    products = []
    corrections = []
    product_cycles = True
    correction_identities = True
    strict_characters = _strict_character(v2_representative, character, 2)
    for extension in extensions:
        product = mixed_outer_cup(extension, v2_representative)
        product_cycles = product_cycles and contraction.differential(product).is_zero()
        strict_characters = strict_characters and _strict_character(
            product,
            character,
            1,
        )
        primitive = exact_mixed_primitive(
            product,
            contraction,
            transferred,
            2,
        ).primitive
        strict_primitive = _character_project(
            primitive,
            contraction,
            actions,
            character,
        )
        correction = strict_primitive.scale(-1)
        correction_identities = correction_identities and (
            contraction.differential(correction) + product
        ).is_zero()
        strict_characters = strict_characters and _strict_character(
            correction,
            character,
            1,
        )
        products.append(product)
        corrections.append(correction)
    result = UniversalV2MatterLift(
        character,
        local_family_index,
        v2_representative,
        tuple(corrections),
        tuple(products),
        product_cycles,
        correction_identities,
        strict_characters,
    )
    if not result.exact:
        raise ValueError("one universal V2 matter lift failed")
    return result


def _initialize_lift_worker(
    extensions: tuple[SparseOuterCechCochain, ...],
) -> None:
    """Install the immutable universal extension basis in one worker."""

    global _WORKER_EXTENSIONS
    _WORKER_EXTENSIONS = extensions


def _lift_v2_job(
    job: tuple[tuple[int, int], int, SparseOuterCechCochain],
) -> UniversalV2MatterLift:
    """Compute one independent universal V2 lift in a worker process."""

    if len(_WORKER_EXTENSIONS) != 2:
        raise ValueError("universal extension basis is unavailable in the worker")
    character, index, representative = job
    return _lift_v2_class(
        character,
        index,
        representative,
        _WORKER_EXTENSIONS,
    )


@cache
def mixed_schoen_universal_matter_lifts() -> UniversalMatterSectorLifts:
    """Construct the two matter sectors needed by the first up-type matrix."""

    first, second = mixed_schoen_matter_representatives()
    _action_digest, parameters, extensions = _load_forward_basis()
    if parameters != ("a0", "a1"):
        raise ValueError("the universal extension basis is no longer two-dimensional")
    v1_representatives = []
    v2_jobs = []
    for character in UP_MATTER_CHARACTERS:
        first_sector = next(
            sector for sector in first.sectors if sector.character == character
        )
        second_sector = next(
            sector for sector in second.sectors if sector.character == character
        )
        if len(first_sector.full_representatives) != 1:
            raise ValueError("the selected V1 character is not one-dimensional")
        if len(second_sector.full_representatives) != 2:
            raise ValueError("the selected V2 character is not two-dimensional")
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
    result = UniversalMatterSectorLifts(
        ("a0", "a1"),
        tuple(v1_representatives),
        v2_lifts,
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
    return result


def write_mixed_schoen_universal_matter_lifts(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed universal matter-lift certificate."""

    payload = mixed_schoen_universal_matter_lifts().as_record()
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
    """Regenerate the minimum universal matter-lift certificate."""

    payload = write_mixed_schoen_universal_matter_lifts()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "all_coefficientwise_cone_identities_exact: "
        f"{payload['all_coefficientwise_cone_identities_exact']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "UniversalMatterSectorLifts",
    "UniversalV2MatterLift",
    "mixed_schoen_universal_matter_lifts",
    "write_mixed_schoen_universal_matter_lifts",
]
