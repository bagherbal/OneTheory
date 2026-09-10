"""Evaluate the first parameter-linear matter-leg deformation contribution.

Owns:
    The family-symmetric first-order product of two universal V2 matter lifts,
    its exact grouped HPL transfer, and its partial determinant residue.

Depends on:
    Source-derived universal matter corrections, the certified common-to-
    diagonal chain map, exact character projection, and the determinant trace.

Must not:
    Treat the noncycle matter-leg term as a full higher product, omit the Higgs-
    leg correction, select an extension point, or report a Yukawa coefficient.

Phase 0:
    Research-only certificate for one scoped deformation contribution.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .diagonal_schoen_lines import _FullCochain
from .mixed_schoen_chain_actions import (
    _perturbed_inclusion,
    mixed_schoen_higgs_deck_action,
)
from .mixed_schoen_chain_diagonal import full_chain_diagonal_differential
from .mixed_schoen_diagonal_chain_map import (
    diagonal_chain_map_certificate,
    diagonal_compare_common_matter,
)
from .mixed_schoen_matter_comparison import (
    _character_project,
    _cochain_digest,
    _has_character,
    _perturbed_projection_inclusion,
)
from .mixed_schoen_matter_tensor import (
    external_lifted_matter_tensor,
    lift_matter_cochain,
)
from .mixed_schoen_universal_matter_lifts import (
    UP_MATTER_CHARACTERS,
    UniversalV2MatterLift,
    mixed_schoen_universal_matter_lifts,
)
from .mixed_schoen_yukawa_trace import (
    _full_cochain_digest,
    contract_with_strict_higgs,
    scalar_full_differential,
    scalar_residue,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_matter_leg_deformation.json"
PRODUCT_CHARACTER = (0, 2)


def _selected_lift(
    lifts: tuple[UniversalV2MatterLift, ...],
    character: tuple[int, int],
    local_family_index: int,
) -> UniversalV2MatterLift:
    """Select one source-derived lift by its exact character and local index."""

    matches = tuple(
        lift
        for lift in lifts
        if lift.character == character and lift.local_family_index == local_family_index
    )
    if len(matches) != 1:
        raise ValueError("the requested universal matter lift is not unique")
    return matches[0]


def _matter_leg_terms(
    row: UniversalV2MatterLift,
    column: UniversalV2MatterLift,
    parameter_index: int,
):
    """Return both ordered first-order terms in canonical V1-V2 order."""

    try:
        row_correction = row.v1_corrections[parameter_index]
        column_correction = column.v1_corrections[parameter_index]
    except IndexError as error:
        raise ValueError("the carrier parameter index is unavailable") from error
    first = external_lifted_matter_tensor(
        diagonal_compare_common_matter(row_correction),
        lift_matter_cochain(column.v2_representative, 2),
    )
    second = external_lifted_matter_tensor(
        diagonal_compare_common_matter(column_correction),
        lift_matter_cochain(row.v2_representative, 2),
    )
    return first, second


@dataclass(frozen=True, slots=True)
class MatterLegDeformationWitness:
    """One exact but incomplete first-order transferred flavor contribution."""

    parameter: str
    row_character: tuple[int, int]
    column_character: tuple[int, int]
    row_local_family_index: int
    column_local_family_index: int
    exchange_sign: int
    raw_exchange_symmetric: bool
    raw_term_count: int
    raw_digest: str
    projection_depth: int
    projected_term_count: int
    inclusion_depth: int
    strict_term_count: int
    equivariant_term_count: int
    equivariant_digest: str
    equivariant_residual_term_count: int
    equivariant_residual_digest: str
    character_exact: bool
    scalar: _FullCochain
    scalar_residual: _FullCochain
    scalar_term_count: int
    scalar_digest: str
    scalar_residual_term_count: int
    scalar_residual_digest: str
    scalar_residue_value: Eisenstein
    scalar_projection_depth: int
    diagonal_chain_map_exact: bool

    @property
    def scoped_result_exact(self) -> bool:
        """Return whether every claimed partial-result gate is exact."""

        return (
            self.parameter == "a0"
            and self.exchange_sign == 1
            and self.raw_exchange_symmetric
            and self.raw_term_count > 0
            and self.projected_term_count > 0
            and self.strict_term_count > 0
            and self.equivariant_term_count > 0
            and self.equivariant_residual_term_count > 0
            and self.character_exact
            and self.scalar_term_count > 0
            and self.scalar_residual_term_count > 0
            and self.scalar_residue_value.is_zero()
            and self.diagonal_chain_map_exact
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact scoped result and unresolved higher-product leg."""

        return {
            "parameter": self.parameter,
            "row_character_exponents": list(self.row_character),
            "column_character_exponents": list(self.column_character),
            "row_local_family_index": self.row_local_family_index,
            "column_local_family_index": self.column_local_family_index,
            "family_exchange_sign": self.exchange_sign,
            "family_exchange_sign_derivation": (
                "minus from exchanging two degree-one Cech classes times minus "
                "from exchanging the two bundle factors"
            ),
            "raw_exchange_symmetric": self.raw_exchange_symmetric,
            "raw_product": {
                "term_count": self.raw_term_count,
                "digest": self.raw_digest,
            },
            "grouped_hpl": {
                "projection_depth": self.projection_depth,
                "projected_term_count": self.projected_term_count,
                "inclusion_depth": self.inclusion_depth,
                "strict_term_count": self.strict_term_count,
            },
            "equivariant_projection": {
                "character_exponents": list(PRODUCT_CHARACTER),
                "term_count": self.equivariant_term_count,
                "digest": self.equivariant_digest,
                "residual_term_count": self.equivariant_residual_term_count,
                "residual_digest": self.equivariant_residual_digest,
                "is_cycle": False,
                "character_exact": self.character_exact,
            },
            "partial_scalar_trace": {
                "term_count": self.scalar_term_count,
                "digest": self.scalar_digest,
                "residual_term_count": self.scalar_residual_term_count,
                "residual_digest": self.scalar_residual_digest,
                "is_cycle": False,
                "residue": str(self.scalar_residue_value),
                "projection_depth": self.scalar_projection_depth,
            },
            "diagonal_chain_map_exact": self.diagonal_chain_map_exact,
            "scoped_result_exact": self.scoped_result_exact,
            "classification": "SCOPED_MATTER_LEG_VANISHING",
            "full_higher_product_available": False,
            "holomorphic_yukawa_entry_available": False,
            "extension_point_selected": False,
            "observational_inputs_used": False,
            "first_missing_input": (
                "the full local Pluecker chain map pairing two V2 matter "
                "representatives into the inverse determinant line"
            ),
        }


@cache
def first_matter_leg_deformation() -> MatterLegDeformationWitness:
    """Derive the first `a0` lower-block matter-leg contribution exactly."""

    universal = mixed_schoen_universal_matter_lifts()
    row = _selected_lift(universal.v2_lifts, UP_MATTER_CHARACTERS[0], 1)
    column = _selected_lift(universal.v2_lifts, UP_MATTER_CHARACTERS[1], 1)
    first, second = _matter_leg_terms(row, column, 0)
    raw = first + second
    raw_exchange_symmetric = raw == second + first
    projected, projection_depth = _perturbed_projection_inclusion(raw, 2)
    strict, inclusion_depth = _perturbed_inclusion(projected)
    equivariant = _character_project(strict, PRODUCT_CHARACTER)
    equivariant_residual = full_chain_diagonal_differential(equivariant)
    higgs = mixed_schoen_higgs_deck_action().required_full_cochain
    scalar = contract_with_strict_higgs(equivariant, higgs)
    scalar_residual = scalar_full_differential(scalar)
    residue, scalar_depth = scalar_residue(scalar)
    result = MatterLegDeformationWitness(
        universal.parameters[0],
        row.character,
        column.character,
        row.local_family_index,
        column.local_family_index,
        1,
        raw_exchange_symmetric,
        len(raw.terms),
        _cochain_digest(raw),
        projection_depth,
        len(projected.terms),
        inclusion_depth,
        len(strict.terms),
        len(equivariant.terms),
        _cochain_digest(equivariant),
        len(equivariant_residual.terms),
        _cochain_digest(equivariant_residual),
        _has_character(equivariant, PRODUCT_CHARACTER),
        scalar,
        scalar_residual,
        len(scalar.terms),
        _full_cochain_digest(scalar),
        len(scalar_residual.terms),
        _full_cochain_digest(scalar_residual),
        residue,
        scalar_depth,
        diagonal_chain_map_certificate().exact,
    )
    if not result.scoped_result_exact:
        raise ValueError("the first matter-leg deformation certificate failed")
    return result


def write_matter_leg_deformation(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed scoped deformation certificate."""

    payload: dict[str, object] = {
        "schema": "mixed-schoen-matter-leg-deformation-v1",
        "coefficient_field": "Q(omega)",
        **first_matter_leg_deformation().as_record(),
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
    """Regenerate the first exact matter-leg deformation certificate."""

    payload = write_matter_leg_deformation()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"classification: {payload['classification']}")
    print(f"first_missing_input: {payload['first_missing_input']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MatterLegDeformationWitness",
    "OUTPUT",
    "first_matter_leg_deformation",
    "write_matter_leg_deformation",
]
