"""Test the raw exterior cup on a homologous actual matter representative.

Owns:
    A strict-character exact boundary, the resulting nonclosed exterior
    product, and a full Leibniz defect on the frozen alternate constituent.

Depends on:
    Actual null matter classes, exact native deck frames, the complete
    constituent differential, and the existing ordered exterior cup.

Must not:
    Refute the carrier from a failed cochain operation, assign a residue
    to a noncycle, or replace the natural product by an arbitrary lift.

Phase 0:
    Research-only attack on the unresolved physical tensor comparison.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.computable_carrier.schoen_sparse_actions import schoen_sparse_deck_actions

from .alternate_constituent_hom_actions import _common_frame
from .alternate_constituent_up_matter_representatives import OUTPUT as MATTER
from .alternate_constituent_up_matter_representatives import _project, _strict
from .alternate_up_exterior_higgs_action import OUTPUT as EXTERIOR
from .alternate_up_exterior_higgs_action import alternate_up_exterior_context
from .alternate_up_first_order_scalar import alternate_null_matter
from .alternate_up_higgs_quotient_cone import alternate_higgs_quotient_models
from .alternate_up_null_channel import OUTPUT as NULL_CHANNELS
from .mixed_schoen_exterior_square import even_rank_one_vector_wedge, resolution_vector_wedge
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _basis_record, _MixedContraction
from .mixed_schoen_outer_transfer import mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_exterior_boundary_attack.json"


def _record(cochain: SparseOuterCechCochain) -> dict[str, object]:
    """Keep complete small witnesses, not just declarations of failure."""

    return {
        "term_count": len(cochain.terms),
        "cochain_digest": _cochain_digest((cochain,)),
        "terms": [
            {"basis": _basis_record(basis), "coefficient": str(value)}
            for basis, value in cochain.terms
        ],
    }


@dataclass(frozen=True, slots=True)
class ExteriorBoundaryAttack:
    """An explicit counterexample to the raw product's cycle preservation."""

    boundary_primitive: SparseOuterCechCochain
    boundary: SparseOuterCechCochain
    original_wedge: SparseOuterCechCochain
    boundary_wedge: SparseOuterCechCochain
    closure_defect: SparseOuterCechCochain
    primitive_wedge: SparseOuterCechCochain
    leibniz_defect: SparseOuterCechCochain
    corrected_boundary_wedge: SparseOuterCechCochain
    corrected_null_wedge: SparseOuterCechCochain

    def as_record(self) -> dict[str, object]:
        """Distinguish an operation failure from a physical no-go claim."""

        exterior, _ = alternate_up_exterior_context()
        return {
            "matter_character": [0, 0],
            "other_matter_character": [1, 0],
            "boundary_primitive": _record(self.boundary_primitive),
            "exact_boundary": _record(self.boundary),
            "boundary_wedge": _record(self.boundary_wedge),
            "closure_defect": _record(self.closure_defect),
            "primitive_wedge": _record(self.primitive_wedge),
            "leibniz_defect": _record(self.leibniz_defect),
            "corrected_boundary_wedge": _record(self.corrected_boundary_wedge),
            "corrected_null_wedge_term_count": len(self.corrected_null_wedge.terms),
            "corrected_null_wedge_digest": _cochain_digest((self.corrected_null_wedge,)),
            "original_null_wedge_term_count": len(self.original_wedge.terms),
            "original_null_wedge_digest": _cochain_digest((self.original_wedge,)),
            "closure_defect_exterior_pairs": [list(pair) for pair in sorted({
                exterior.pairs[basis.component.left_index]
                for basis, _ in self.closure_defect.terms
            })],
            "strict_boundary_primitive_character_exact": True,
            "strict_boundary_character_exact": True,
            "full_boundary_cycle_exact": True,
            "original_null_wedge_closed_exact": True,
            "modified_matter_class_unchanged_exact": True,
            "modified_matter_representative_closed_exact": True,
            "modified_matter_character_exact": True,
            "modified_exterior_wedge_closed_exact": False,
            "raw_exterior_cup_is_all_input_chain_map": False,
            "full_leibniz_defect_differential_is_negative_closure_defect": True,
            "corrected_even_boundary_wedge_is_full_primitive_differential": True,
            "corrected_even_boundary_wedge_closed_exact": True,
            "original_null_wedge_unchanged_by_even_correction": True,
            "complete_tensor_comparison_certified": False,
            "original_ordered_scalar_screens_refuted": False,
            "carrier_refuted": False,
            "physical_null_coefficient_assigned": False,
        }


@cache
def alternate_up_exterior_boundary_attack() -> ExteriorBoundaryAttack:
    """Use an exact boundary in the physical native character, not a new class."""

    second, _ = alternate_higgs_quotient_models()
    unit = mixed_schoen_unit()
    context = _MixedContraction(second, unit)
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    frames = {
        name: (_common_frame(second, action), Matrix.identity(1, scalar_type=Eisenstein))
        for name, action in actions.items()
    }
    # This explicit local section is a test of the representation, not a
    # geometric selector. Reynolds projection retains the actual sector.
    component = context.components[(1, 0, "k0")]
    raw = SparseOuterCechCochain(((OuterCechBasis(
        component, (0, 1, 0), (-4, 0, 0), (1, 0), ((0,), (0,), (0,)),
    ), Eisenstein(1)),))
    primitive = _project(raw, (0, 0), context, actions, frames)
    boundary = context.differential(primitive)
    left, right = alternate_null_matter()
    modified = left + boundary
    if (
        primitive.is_zero() or boundary.is_zero()
        or not _strict(primitive, (0, 0), context, actions, frames)
        or not _strict(boundary, (0, 0), context, actions, frames)
        or not _strict(modified, (0, 0), context, actions, frames)
        or not context.differential(boundary).is_zero()
        or not context.differential(modified).is_zero()
    ):
        raise ValueError(
            "the representative attack needs a nonzero exact strict-character boundary"
        )
    exterior, _ = alternate_up_exterior_context()
    wedge_context = _MixedContraction(exterior, unit)
    original = resolution_vector_wedge(left, right, exterior, wedge_context, 1, 1)
    variation = resolution_vector_wedge(boundary, right, exterior, wedge_context, 1, 1)
    changed = resolution_vector_wedge(modified, right, exterior, wedge_context, 1, 1)
    if changed != original + variation or not wedge_context.differential(original).is_zero():
        raise ValueError("the actual raw wedge did not preserve its pinned linear comparison")
    defect = wedge_context.differential(variation)
    if defect.is_zero() or wedge_context.differential(changed) != defect:
        raise ValueError("the declared raw exterior representative counterexample disappeared")
    primitive_wedge = resolution_vector_wedge(primitive, right, exterior, wedge_context, 0, 1)
    leibniz = wedge_context.differential(primitive_wedge) + variation.scale(-1)
    if wedge_context.differential(leibniz) != defect.scale(-1):
        raise ValueError("the full exterior Leibniz defect identity failed")
    corrected = even_rank_one_vector_wedge(
        boundary, right, second, exterior, wedge_context, 1, 1,
    )
    corrected_null = even_rank_one_vector_wedge(
        left, right, second, exterior, wedge_context, 1, 1,
    )
    if (
        corrected != wedge_context.differential(primitive_wedge)
        or not wedge_context.differential(corrected).is_zero()
        or corrected_null != original
    ):
        raise ValueError(
            "the derived even-sector tensor correction failed its actual boundary test"
        )
    return ExteriorBoundaryAttack(
        primitive, boundary, original, variation, defect, primitive_wedge, leibniz,
        corrected, corrected_null,
    )


def write_exterior_boundary_attack(path: Path = OUTPUT) -> dict[str, object]:
    """Persist the failure without modifying any existing scalar evidence."""

    prerequisites = {
        name: _verified_payload(source)[0]
        for name, source in (
            ("actual_matter", MATTER), ("null_channels", NULL_CHANNELS),
            ("exterior_construction", EXTERIOR),
        )
    }
    attack = alternate_up_exterior_boundary_attack()
    payload: dict[str, object] = {
        "schema": "alternate-up-exterior-boundary-attack-v1",
        "coefficient_field": "Q(omega)",
        "attack": attack.as_record(),
        "scope": "raw ordered exterior cup on the frozen alternate F resolution",
        "natural_product_comparison_certified": False,
        "complete_holomorphic_up_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": prerequisites,
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    record = write_exterior_boundary_attack()
    print(f"artifact_digest: {record['artifact_digest']}")
