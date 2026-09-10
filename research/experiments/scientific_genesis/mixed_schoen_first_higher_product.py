"""Assemble the first complete parameter-linear Yukawa coefficient.

Owns:
    The source-derived a0 lower-(1,1) matter and Higgs legs, their exact
    grouped-to-Pluecker comparison primitive, and the descended scalar residue.

Depends on:
    The certified matter leg, canonical Higgs correction, equivariant V2
    Pluecker pairing, determinant-line actions, and fixed Cech contraction.

Must not:
    Select an extension point, choose a primitive from a desired residue,
    generalize one coefficient to a matrix, or call a holomorphic value physical.

Phase 0:
    Research-only first complete coefficient in the lawful higher-product path.
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

from .diagonal_schoen_line_actions import (
    Character,
    constituent_determinant_character,
    line_has_character,
    project_line_character,
)
from .diagonal_schoen_line_products import diagonal_line_product
from .diagonal_schoen_lines import _FullCochain
from .mixed_schoen_higgs_leg_deformation import (
    OUTPUT as HIGGS_ARTIFACT,
)
from .mixed_schoen_higgs_leg_deformation import first_higgs_leg_deformation
from .mixed_schoen_matter_leg_deformation import (
    OUTPUT as MATTER_ARTIFACT,
)
from .mixed_schoen_matter_leg_deformation import first_matter_leg_deformation
from .mixed_schoen_v2_pluecker_chain_map import (
    OUTPUT as PLUECKER_ARTIFACT,
)
from .mixed_schoen_v2_pluecker_chain_map import first_v2_pluecker_pairing
from .mixed_schoen_yukawa_trace import (
    _full_cochain_digest,
    scalar_full_differential,
    scalar_primitive,
    scalar_residue,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_first_higher_product.json"
SCALAR_AMBIENT_DEGREES = (0, 0, 0, 0)
HIGGS_CHARACTER: Character = (0, 1)
SCALAR_CHARACTER: Character = (0, 0)


def _add(left: _FullCochain, right: _FullCochain) -> _FullCochain:
    """Add two normalized scalar cochains exactly."""

    return _FullCochain(left.terms + right.terms)


def _sum_character(left: Character, right: Character) -> Character:
    """Add two cubic character exponents."""

    return (left[0] + right[0]) % 3, (left[1] + right[1]) % 3


def _verified_artifact(path: Path, gate: str) -> str:
    """Return one prerequisite digest after its exact gate is verified."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest failed: {path.name}")
    if payload.get(gate) is not True:
        raise ValueError(f"upstream artifact gate failed: {path.name}")
    return digest


@dataclass(frozen=True, slots=True)
class FirstHigherProductCoefficient:
    """One exact descended coefficient and all nontrivial comparison gates."""

    parameter: str
    row_local_family_index: int
    column_local_family_index: int
    v1_determinant_character: Character
    v2_determinant_character: Character
    scalar_frame_character: Character
    matter_scalar_term_count: int
    matter_scalar_character_exact: bool
    bottom_pairing_term_count: int
    higgs_correction_term_count: int
    higgs_correction_character_exact: bool
    correction_product_term_count: int
    correction_product_digest: str
    action_product_term_count: int
    action_product_digest: str
    leibniz_identity_exact: bool
    comparison_residual_term_count: int
    comparison_residual_digest: str
    comparison_residual_is_cycle: bool
    raw_comparison_primitive_term_count: int
    raw_comparison_primitive_digest: str
    raw_comparison_depth: int
    raw_comparison_identity_exact: bool
    strict_comparison_primitive_term_count: int
    strict_comparison_primitive_digest: str
    strict_comparison_character_exact: bool
    strict_comparison_identity_exact: bool
    complete_cochain_term_count: int
    complete_cochain_digest: str
    complete_cochain_is_cycle: bool
    residue: Eisenstein
    residue_projection_depth: int

    @property
    def exact(self) -> bool:
        """Return whether this scoped coefficient is fully certified."""

        return (
            self.parameter == "a0"
            and self.row_local_family_index == 1
            and self.column_local_family_index == 1
            and self.v1_determinant_character == (1, 0)
            and self.v2_determinant_character == (1, 1)
            and self.scalar_frame_character == (2, 1)
            and self.matter_scalar_term_count > 0
            and self.matter_scalar_character_exact
            and self.bottom_pairing_term_count > 0
            and self.higgs_correction_term_count > 0
            and self.higgs_correction_character_exact
            and self.correction_product_term_count > 0
            and self.action_product_term_count > 0
            and self.leibniz_identity_exact
            and self.comparison_residual_term_count > 0
            and self.comparison_residual_is_cycle
            and self.raw_comparison_primitive_term_count > 0
            and self.raw_comparison_identity_exact
            and self.strict_comparison_primitive_term_count > 0
            and self.strict_comparison_character_exact
            and self.strict_comparison_identity_exact
            and self.complete_cochain_term_count > 0
            and self.complete_cochain_is_cycle
            and self.residue.is_zero()
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact scoped vanishing and remaining matrix frontier."""

        return {
            "parameter": self.parameter,
            "row_local_family_index": self.row_local_family_index,
            "column_local_family_index": self.column_local_family_index,
            "v1_determinant_character_exponents": list(
                self.v1_determinant_character
            ),
            "v2_determinant_character_exponents": list(
                self.v2_determinant_character
            ),
            "scalar_frame_character_exponents": list(
                self.scalar_frame_character
            ),
            "matter_scalar_term_count": self.matter_scalar_term_count,
            "matter_scalar_character_exact": self.matter_scalar_character_exact,
            "bottom_pairing_term_count": self.bottom_pairing_term_count,
            "higgs_correction_term_count": self.higgs_correction_term_count,
            "higgs_correction_character_exact": (
                self.higgs_correction_character_exact
            ),
            "correction_product": {
                "term_count": self.correction_product_term_count,
                "digest": self.correction_product_digest,
            },
            "action_product": {
                "term_count": self.action_product_term_count,
                "digest": self.action_product_digest,
            },
            "leibniz_identity_exact": self.leibniz_identity_exact,
            "comparison_residual": {
                "term_count": self.comparison_residual_term_count,
                "digest": self.comparison_residual_digest,
                "is_cycle": self.comparison_residual_is_cycle,
            },
            "raw_comparison_primitive": {
                "term_count": self.raw_comparison_primitive_term_count,
                "digest": self.raw_comparison_primitive_digest,
                "depth": self.raw_comparison_depth,
                "identity_exact": self.raw_comparison_identity_exact,
            },
            "strict_comparison_primitive": {
                "term_count": self.strict_comparison_primitive_term_count,
                "digest": self.strict_comparison_primitive_digest,
                "character_exact": self.strict_comparison_character_exact,
                "identity_exact": self.strict_comparison_identity_exact,
            },
            "complete_scalar_cochain": {
                "term_count": self.complete_cochain_term_count,
                "digest": self.complete_cochain_digest,
                "is_cycle": self.complete_cochain_is_cycle,
                "residue": str(self.residue),
                "projection_depth": self.residue_projection_depth,
            },
            "classification": "SCOPED_FIRST_ORDER_ENTRY_VANISHING",
            "exact": self.exact,
            "input_level_comparison_primitive_available": True,
            "general_chain_homotopy_available": False,
            "complete_first_order_matrix_available": False,
            "holomorphic_yukawa_matrix_available": False,
            "extension_point_selected": False,
            "observational_inputs_used": False,
            "first_missing_input": (
                "the remaining local-family and a1 first-order coefficients, "
                "preferably compressed by multilinearity or symmetry"
            ),
        }


@cache
def first_higher_product_coefficient() -> FirstHigherProductCoefficient:
    """Derive the first complete a0 lower-(1,1) coefficient from source data."""

    matter = first_matter_leg_deformation()
    higgs = first_higgs_leg_deformation()
    bottom = first_v2_pluecker_pairing()
    v1_character = constituent_determinant_character(1)
    v2_character = constituent_determinant_character(2)
    scalar_frame = _sum_character(v1_character, v2_character)
    higgs_correction = project_line_character(
        higgs.canonical_correction,
        HIGGS_CHARACTER,
        v1_character,
    )
    higgs_correction_character = line_has_character(
        higgs_correction,
        HIGGS_CHARACTER,
        v1_character,
    )
    if scalar_full_differential(higgs_correction) != (
        higgs.canonical_action.scale(-1)
    ):
        raise ValueError("the strict Higgs correction lost its boundary identity")
    matter_character = line_has_character(
        matter.scalar,
        SCALAR_CHARACTER,
        scalar_frame,
    )
    correction_product = diagonal_line_product(
        bottom.equivariant_pairing,
        higgs_correction,
        SCALAR_AMBIENT_DEGREES,
    )
    action_product = diagonal_line_product(
        bottom.equivariant_pairing,
        higgs.canonical_action,
        SCALAR_AMBIENT_DEGREES,
    )
    correction_differential = scalar_full_differential(correction_product)
    leibniz = correction_differential == action_product.scale(-1)
    comparison_residual = _add(
        matter.scalar_residual,
        action_product.scale(-1),
    )
    comparison_cycle = scalar_full_differential(
        comparison_residual
    ).is_zero()
    raw_primitive, raw_depth = scalar_primitive(comparison_residual)
    raw_identity = scalar_full_differential(raw_primitive) == comparison_residual
    strict_primitive = project_line_character(
        raw_primitive,
        SCALAR_CHARACTER,
        scalar_frame,
    )
    strict_character = line_has_character(
        strict_primitive,
        SCALAR_CHARACTER,
        scalar_frame,
    )
    strict_identity = (
        scalar_full_differential(strict_primitive) == comparison_residual
    )
    complete = _add(
        _add(matter.scalar, correction_product),
        strict_primitive.scale(-1),
    )
    complete_cycle = scalar_full_differential(complete).is_zero()
    residue, residue_depth = scalar_residue(complete)
    result = FirstHigherProductCoefficient(
        matter.parameter,
        matter.row_local_family_index,
        matter.column_local_family_index,
        v1_character,
        v2_character,
        scalar_frame,
        len(matter.scalar.terms),
        matter_character,
        len(bottom.equivariant_pairing.terms),
        len(higgs_correction.terms),
        higgs_correction_character,
        len(correction_product.terms),
        _full_cochain_digest(correction_product),
        len(action_product.terms),
        _full_cochain_digest(action_product),
        leibniz,
        len(comparison_residual.terms),
        _full_cochain_digest(comparison_residual),
        comparison_cycle,
        len(raw_primitive.terms),
        _full_cochain_digest(raw_primitive),
        raw_depth,
        raw_identity,
        len(strict_primitive.terms),
        _full_cochain_digest(strict_primitive),
        strict_character,
        strict_identity,
        len(complete.terms),
        _full_cochain_digest(complete),
        complete_cycle,
        residue,
        residue_depth,
    )
    if not result.exact:
        raise ValueError("the first complete higher-product coefficient failed")
    return result


def write_first_higher_product(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed first complete coefficient certificate."""

    payload: dict[str, object] = {
        "schema": "mixed-schoen-first-higher-product-v1",
        "coefficient_field": "Q(omega)",
        "prerequisite_artifact_digests": {
            "matter_leg": _verified_artifact(
                MATTER_ARTIFACT,
                "scoped_result_exact",
            ),
            "higgs_leg": _verified_artifact(HIGGS_ARTIFACT, "exact"),
            "v2_pluecker": _verified_artifact(PLUECKER_ARTIFACT, "exact"),
        },
        **first_higher_product_coefficient().as_record(),
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
    """Regenerate the first exact complete higher-product coefficient."""

    payload = write_first_higher_product()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"classification: {payload['classification']}")
    print(f"first_missing_input: {payload['first_missing_input']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "FirstHigherProductCoefficient",
    "OUTPUT",
    "first_higher_product_coefficient",
    "write_first_higher_product",
]
