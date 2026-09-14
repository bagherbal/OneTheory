"""Derive the universal first-order Dirac-neutrino Yukawa matrix.

Owns:
    All eight exact parameter and local-family coefficients, their two
    coefficient matrices, generic rank, and exterior-filtration completion.

Depends on:
    Universal neutrino matter lifts, the strict up-Higgs deformation, exact
    V2 determinant pairings, and the normalized scalar residue contraction.

Must not:
    Select an extension point, infer coefficients by family symmetry, import
    observations, or call holomorphic data canonically normalized or physical.

Phase 0:
    Research-only universal matrix on the Dirac-neutrino flavor path.
"""

from __future__ import annotations

import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, polynomial_determinant
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .mixed_schoen_chain_actions import _parse_eisenstein_text
from .mixed_schoen_diagonal_chain_map import diagonal_chain_map_certificate
from .mixed_schoen_first_higher_product import (
    FirstHigherProductCoefficient,
    higher_product_coefficient_for_sector,
)
from .mixed_schoen_first_order_matrix import filtration_allowed_orders
from .mixed_schoen_higgs_leg_deformation import higgs_leg_deformation
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_neutrino_matter_lifts import (
    NEUTRINO_MATTER_CHARACTERS,
    NeutrinoMatterLifts,
    mixed_schoen_neutrino_matter_lifts,
)
from .mixed_schoen_neutrino_matter_lifts import (
    OUTPUT as MATTER_LIFTS_ARTIFACT,
)
from .mixed_schoen_neutrino_tree_matrix import OUTPUT as TREE_MATRIX_ARTIFACT
from .mixed_schoen_universal_matter_lifts import UniversalV2MatterLift
from .mixed_schoen_v2_pluecker_chain_map import (
    local_v2_pluecker_pairing_for_characters,
)
from .mixed_schoen_yukawa_trace import _full_cochain_digest

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_neutrino_first_order_matrix.json"
)
COEFFICIENT_CACHE_DIRECTORY = (
    ROOT
    / "data/generated/scientific_genesis/"
    ".mixed_schoen_neutrino_coefficient_cache"
)
PARAMETERS = ("a0", "a1")
LOCAL_FAMILY_INDICES = (1, 2)
MAX_COEFFICIENT_WORKERS = 1
FIRST_ORDER_SLOTS = tuple(
    (row, column)
    for row in range(3)
    for column in range(3)
    if filtration_allowed_orders(row, column) == (1,)
)
ALGORITHM_SOURCES = (
    Path(__file__),
    ROOT
    / "research/experiments/scientific_genesis/"
    "mixed_schoen_first_higher_product.py",
    ROOT
    / "research/experiments/scientific_genesis/"
    "mixed_schoen_matter_leg_deformation.py",
    ROOT
    / "research/experiments/scientific_genesis/"
    "mixed_schoen_higgs_leg_deformation.py",
    ROOT
    / "research/experiments/scientific_genesis/"
    "mixed_schoen_v2_pluecker_chain_map.py",
)


def _mapping(raw: object, name: str) -> dict[str, object]:
    """Require one JSON object while decoding a coefficient cache."""

    if not isinstance(raw, dict):
        raise ValueError(f"the cached {name} record is malformed")
    return cast(dict[str, object], raw)


def _integer(raw: dict[str, object], key: str) -> int:
    """Require one non-Boolean integer field from a cache record."""

    value = raw.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"the cached coefficient field {key} is not an integer")
    return value


def _boolean(raw: dict[str, object], key: str) -> bool:
    """Require one Boolean field from a cache record."""

    value = raw.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"the cached coefficient field {key} is not Boolean")
    return value


def _string(raw: dict[str, object], key: str) -> str:
    """Require one string field from a cache record."""

    value = raw.get(key)
    if not isinstance(value, str):
        raise ValueError(f"the cached coefficient field {key} is not text")
    return value


def _character(raw: dict[str, object], key: str) -> tuple[int, int]:
    """Require one pair of exact cubic character exponents."""

    value = raw.get(key)
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(isinstance(entry, bool) or not isinstance(entry, int) for entry in value)
    ):
        raise ValueError(f"the cached coefficient field {key} is not a character")
    return value[0], value[1]


def _coefficient_from_record(raw: object) -> FirstHigherProductCoefficient:
    """Rehydrate one exact coefficient from its canonical evidence record."""

    record = _mapping(raw, "coefficient")
    correction_product = _mapping(
        record.get("correction_product"),
        "correction product",
    )
    action_product = _mapping(record.get("action_product"), "action product")
    residual = _mapping(record.get("comparison_residual"), "comparison residual")
    raw_primitive = _mapping(
        record.get("raw_comparison_primitive"),
        "raw comparison primitive",
    )
    strict_primitive = _mapping(
        record.get("strict_comparison_primitive"),
        "strict comparison primitive",
    )
    complete = _mapping(
        record.get("complete_scalar_cochain"),
        "complete scalar cochain",
    )
    result = FirstHigherProductCoefficient(
        _string(record, "parameter"),
        _integer(record, "row_local_family_index"),
        _integer(record, "column_local_family_index"),
        _character(record, "v1_determinant_character_exponents"),
        _character(record, "v2_determinant_character_exponents"),
        _character(record, "scalar_frame_character_exponents"),
        _integer(record, "matter_scalar_term_count"),
        _boolean(record, "matter_scalar_character_exact"),
        _integer(record, "bottom_pairing_term_count"),
        _integer(record, "higgs_correction_term_count"),
        _boolean(record, "higgs_correction_character_exact"),
        _integer(correction_product, "term_count"),
        _string(correction_product, "digest"),
        _integer(action_product, "term_count"),
        _string(action_product, "digest"),
        _boolean(record, "leibniz_identity_exact"),
        _integer(residual, "term_count"),
        _string(residual, "digest"),
        _boolean(residual, "is_cycle"),
        _integer(raw_primitive, "term_count"),
        _string(raw_primitive, "digest"),
        _integer(raw_primitive, "depth"),
        _boolean(raw_primitive, "identity_exact"),
        _integer(strict_primitive, "term_count"),
        _string(strict_primitive, "digest"),
        _boolean(strict_primitive, "character_exact"),
        _boolean(strict_primitive, "identity_exact"),
        _integer(complete, "term_count"),
        _string(complete, "digest"),
        _boolean(complete, "is_cycle"),
        _parse_eisenstein_text(_string(complete, "residue")),
        _integer(complete, "projection_depth"),
    )
    if not result.exact or result.as_record() != record:
        raise ValueError("the cached coefficient failed canonical reconstruction")
    return result


@cache
def _algorithm_digest() -> str:
    """Hash every source file whose logic determines a cached coefficient."""

    digest = hashlib.sha256()
    for path in ALGORITHM_SOURCES:
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _selected_lift(
    universal: NeutrinoMatterLifts,
    character: tuple[int, int],
    family_index: int,
) -> UniversalV2MatterLift:
    """Return one unique neutrino lift for cache input fingerprinting."""

    matches = tuple(
        lift
        for lift in universal.v2_lifts
        if lift.character == character and lift.local_family_index == family_index
    )
    if len(matches) != 1:
        raise ValueError("the coefficient cache input lift is not unique")
    return matches[0]


def _coefficient_input_digest(
    universal: NeutrinoMatterLifts,
    parameter_index: int,
    row: int,
    column: int,
) -> str:
    """Fingerprint exact cochains and algorithms determining one coefficient."""

    row_lift = _selected_lift(
        universal,
        NEUTRINO_MATTER_CHARACTERS[0],
        row,
    )
    column_lift = _selected_lift(
        universal,
        NEUTRINO_MATTER_CHARACTERS[1],
        column,
    )
    higgs = higgs_leg_deformation(parameter_index)
    bottom = local_v2_pluecker_pairing_for_characters(
        *NEUTRINO_MATTER_CHARACTERS,
        row,
        column,
    )
    return _canonical_digest(
        {
            "algorithm_digest": _algorithm_digest(),
            "parameter": PARAMETERS[parameter_index],
            "row_character": list(NEUTRINO_MATTER_CHARACTERS[0]),
            "column_character": list(NEUTRINO_MATTER_CHARACTERS[1]),
            "row_local_family_index": row,
            "column_local_family_index": column,
            "row_v2_digest": _cochain_digest((row_lift.v2_representative,)),
            "column_v2_digest": _cochain_digest((column_lift.v2_representative,)),
            "row_correction_digest": _cochain_digest(
                (row_lift.v1_corrections[parameter_index],)
            ),
            "column_correction_digest": _cochain_digest(
                (column_lift.v1_corrections[parameter_index],)
            ),
            "higgs_action_digest": _full_cochain_digest(higgs.canonical_action),
            "higgs_correction_digest": _full_cochain_digest(
                higgs.canonical_correction
            ),
            "bottom_pairing_digest": _full_cochain_digest(
                bottom.equivariant_pairing
            ),
        }
    )


def _coefficient_cache_path(
    parameter_index: int,
    row: int,
    column: int,
) -> Path:
    """Return one deterministic ignored higher-product checkpoint path."""

    return COEFFICIENT_CACHE_DIRECTORY / (
        f"a{parameter_index}-row-{row}-column-{column}.json"
    )


def _write_coefficient_cache(
    result: FirstHigherProductCoefficient,
    input_digest: str,
) -> None:
    """Atomically persist one exact higher-product coefficient certificate."""

    payload: dict[str, object] = {
        "schema": "mixed-schoen-neutrino-coefficient-cache-v1",
        "input_digest": input_digest,
        "coefficient": result.as_record(),
    }
    payload["cache_digest"] = _canonical_digest(payload)
    parameter_index = PARAMETERS.index(result.parameter)
    path = _coefficient_cache_path(
        parameter_index,
        result.row_local_family_index,
        result.column_local_family_index,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _load_coefficient_cache(
    universal: NeutrinoMatterLifts,
    job: tuple[int, int, int],
) -> FirstHigherProductCoefficient | None:
    """Load one higher-product checkpoint only after every cache gate passes."""

    parameter_index, row, column = job
    path = _coefficient_cache_path(parameter_index, row, column)
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return None
        cache_digest = payload.pop("cache_digest", None)
        if not isinstance(cache_digest, str) or cache_digest != _canonical_digest(
            payload
        ):
            return None
        if (
            payload.get("schema")
            != "mixed-schoen-neutrino-coefficient-cache-v1"
            or payload.get("input_digest")
            != _coefficient_input_digest(universal, parameter_index, row, column)
        ):
            return None
        result = _coefficient_from_record(payload.get("coefficient"))
        if (
            result.parameter != PARAMETERS[parameter_index]
            or result.row_local_family_index != row
            or result.column_local_family_index != column
        ):
            return None
        return result
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return None


def _verified_digest(path: Path, gate: str) -> str:
    """Return an upstream digest only after its exact gate passes."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest failed: {path.name}")
    if payload.get(gate) is not True:
        raise ValueError(f"upstream artifact gate failed: {path.name}")
    return digest


def _polynomial_record(polynomial: Polynomial) -> list[dict[str, object]]:
    """Serialize one exact parameter polynomial in sparse canonical order."""

    return [
        {"exponents": list(exponents), "coefficient": str(coefficient)}
        for exponents, coefficient in polynomial.terms
    ]


def _coefficient_job(
    job: tuple[int, int, int],
) -> FirstHigherProductCoefficient:
    """Derive one parameter and local-family coefficient in isolation."""

    parameter_index, row, column = job
    universal = mixed_schoen_neutrino_matter_lifts()
    result = higher_product_coefficient_for_sector(
        universal.parameters,
        universal.v2_lifts,
        *NEUTRINO_MATTER_CHARACTERS,
        parameter_index,
        row,
        column,
    )
    _write_coefficient_cache(
        result,
        _coefficient_input_digest(universal, parameter_index, row, column),
    )
    print(
        f"checkpointed neutrino coefficient a{parameter_index} "
        f"row={row} column={column}",
        flush=True,
    )
    return result


@dataclass(frozen=True, slots=True)
class FirstOrderNeutrinoMatrix:
    """The complete universal Dirac-neutrino matrix through allowed order."""

    coefficients: tuple[FirstHigherProductCoefficient, ...]

    def __post_init__(self) -> None:
        expected = tuple(
            (parameter, row, column)
            for parameter in PARAMETERS
            for row, column in FIRST_ORDER_SLOTS
        )
        actual = tuple(
            (
                coefficient.parameter,
                coefficient.row_local_family_index,
                coefficient.column_local_family_index,
            )
            for coefficient in self.coefficients
        )
        if actual != expected:
            raise ValueError("the neutrino coefficient basis is incomplete")

    def coefficient_matrix(self, parameter: str) -> Matrix:
        """Return one exact three-family parameter coefficient matrix."""

        if parameter not in PARAMETERS:
            raise ValueError("the carrier parameter is unavailable")
        values = {
            (
                coefficient.row_local_family_index,
                coefficient.column_local_family_index,
            ): coefficient.residue
            for coefficient in self.coefficients
            if coefficient.parameter == parameter
        }
        return Matrix(
            tuple(
                tuple(
                    values.get((row, column), Eisenstein(0))
                    for column in range(3)
                )
                for row in range(3)
            ),
            scalar_type=Eisenstein,
        )

    @property
    def universal_matrix(self) -> tuple[tuple[Polynomial, ...], ...]:
        """Return the full exact matrix over Q(omega)[a0,a1]."""

        variables = tuple(
            Polynomial.monomial(
                (int(index == 0), int(index == 1)),
                scalar_type=Eisenstein,
            )
            for index in range(2)
        )
        coefficient_matrices = tuple(
            self.coefficient_matrix(parameter) for parameter in PARAMETERS
        )
        return tuple(
            tuple(
                sum(
                    (
                        variables[index].scale(matrix[row][column])
                        for index, matrix in enumerate(coefficient_matrices)
                    ),
                    start=Polynomial.zero(2, scalar_type=Eisenstein),
                )
                for column in range(3)
            )
            for row in range(3)
        )

    @property
    def universal_lower_determinant(self) -> Polynomial:
        """Return the exact determinant of the only potentially nonzero block."""

        return polynomial_determinant(
            tuple(
                tuple(self.universal_matrix[row][column] for column in (1, 2))
                for row in (1, 2)
            )
        )

    @property
    def generic_rank(self) -> int:
        """Return the exact generic rank over the parameter function field."""

        if not self.universal_lower_determinant.is_zero():
            return 2
        if any(
            not coefficient.residue.is_zero()
            for coefficient in self.coefficients
        ):
            return 1
        return 0

    @property
    def exact(self) -> bool:
        """Return whether all coefficients and the all-orders truncation close."""

        allowed_orders = {
            filtration_allowed_orders(row, column)
            for row in range(3)
            for column in range(3)
        }
        return (
            len(self.coefficients) == 8
            and all(coefficient.exact for coefficient in self.coefficients)
            and allowed_orders <= {(), (0,), (1,)}
            and self.generic_rank in (0, 1, 2)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize every coefficient and the complete universal rank."""

        matrices = {
            parameter: [
                [
                    str(self.coefficient_matrix(parameter)[row][column])
                    for column in range(3)
                ]
                for row in range(3)
            ]
            for parameter in PARAMETERS
        }
        universal = [
            [
                _polynomial_record(self.universal_matrix[row][column])
                for column in range(3)
            ]
            for row in range(3)
        ]
        return {
            "parameter_basis": list(PARAMETERS),
            "matrix_expansion": "Y_nu(a)=a0 M0+a1 M1",
            "first_order_slots": [list(slot) for slot in FIRST_ORDER_SLOTS],
            "coefficient_matrices": matrices,
            "universal_matrix": universal,
            "universal_lower_determinant": _polynomial_record(
                self.universal_lower_determinant
            ),
            "coefficients": [
                coefficient.as_record() for coefficient in self.coefficients
            ],
            "generic_rank": self.generic_rank,
            "nontrivial": self.generic_rank > 0,
            "maximum_exterior_allowed_parameter_order": 1,
            "higher_orders_structurally_zero": True,
            "all_eight_coefficients_exact": self.exact,
        }


@cache
def mixed_schoen_neutrino_first_order_matrix() -> FirstOrderNeutrinoMatrix:
    """Compute all universal neutrino coefficients independently in parallel."""

    universal = mixed_schoen_neutrino_matter_lifts()
    diagonal_chain_map_certificate()
    for parameter_index in range(2):
        higgs_leg_deformation(parameter_index)
    for row, column in FIRST_ORDER_SLOTS:
        local_v2_pluecker_pairing_for_characters(
            *NEUTRINO_MATTER_CHARACTERS,
            row,
            column,
        )
    jobs = tuple(
        (parameter_index, row, column)
        for parameter_index in range(2)
        for row, column in FIRST_ORDER_SLOTS
    )
    cached = tuple(
        coefficient
        for job in jobs
        if (coefficient := _load_coefficient_cache(universal, job)) is not None
    )
    cached_keys = {
        (
            PARAMETERS.index(coefficient.parameter),
            coefficient.row_local_family_index,
            coefficient.column_local_family_index,
        )
        for coefficient in cached
    }
    for parameter_index, row, column in sorted(cached_keys):
        print(
            f"reused neutrino coefficient a{parameter_index} "
            f"row={row} column={column}",
            flush=True,
        )
    pending = tuple(job for job in jobs if job not in cached_keys)
    computed: tuple[FirstHigherProductCoefficient, ...] = ()
    if pending:
        with ProcessPoolExecutor(
            max_workers=min(MAX_COEFFICIENT_WORKERS, len(pending))
        ) as executor:
            computed = tuple(executor.map(_coefficient_job, pending))
    by_key = {
        (
            PARAMETERS.index(coefficient.parameter),
            coefficient.row_local_family_index,
            coefficient.column_local_family_index,
        ): coefficient
        for coefficient in cached + computed
    }
    coefficients = tuple(by_key[job] for job in jobs)
    result = FirstOrderNeutrinoMatrix(coefficients)
    if not result.exact:
        raise ValueError("the universal Dirac-neutrino matrix failed")
    return result


def write_neutrino_first_order_matrix(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed universal neutrino matrix certificate."""

    result = mixed_schoen_neutrino_first_order_matrix()
    payload: dict[str, object] = {
        "schema": "mixed-schoen-neutrino-first-order-matrix-v1",
        "coefficient_field": "Q(omega)[a0,a1]",
        "prerequisite_artifact_digests": {
            "tree_matrix": _verified_digest(
                TREE_MATRIX_ARTIFACT,
                "complete_tree_level_neutrino_matrix_available",
            ),
            "universal_matter_lifts": _verified_digest(
                MATTER_LIFTS_ARTIFACT,
                "all_neutrino_matter_lifts_exact",
            ),
        },
        **result.as_record(),
        "complete_universal_holomorphic_neutrino_matrix_available": True,
        "physical_yukawa_matrix_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "next_required_object": (
            "a nontrivial carrier-derived holomorphic Yukawa matrix in another "
            "available flavor route"
            if result.generic_rank == 0
            else "matter and Higgs Kahler metrics at one stabilized common vacuum"
        ),
    }
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
    """Regenerate the universal neutrino matrix and print its exact rank."""

    payload = write_neutrino_first_order_matrix()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"generic_rank: {payload['generic_rank']}")
    print(f"nontrivial: {payload['nontrivial']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "FIRST_ORDER_SLOTS",
    "FirstOrderNeutrinoMatrix",
    "OUTPUT",
    "mixed_schoen_neutrino_first_order_matrix",
    "write_neutrino_first_order_matrix",
]
