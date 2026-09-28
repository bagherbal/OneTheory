"""Check the graded tensor comparison on an actual syzygy boundary.

Owns:
    A strict-character degree-zero syzygy primitive in the frozen alternate
    F resolution and its complete corrected exterior boundary identity.

Depends on:
    Actual null matter, inherited deck frames, the full constituent
    differential, and the derived closed rank-one tensor comparison.

Must not:
    Select a geometric or extension parameter, assign a scalar residue to
    the failed raw product, or certify the outer carrier pairing.

Phase 0:
    Research-only actual-input verification of the syzygy comparison.
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
from .alternate_up_exterior_boundary_attack import OUTPUT as EVEN_ATTACK
from .alternate_up_exterior_boundary_attack import _record
from .alternate_up_exterior_higgs_action import alternate_up_exterior_context
from .alternate_up_first_order_scalar import alternate_null_matter
from .alternate_up_higgs_quotient_cone import alternate_higgs_quotient_models
from .alternate_up_null_channel import OUTPUT as NULL_CHANNELS
from .mixed_schoen_exterior_square import resolution_vector_wedge
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload
from .mixed_schoen_rank_one_tensor import _closed_rank_one_row, rank_one_vector_wedge

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_syzygy_tensor_comparison.json"


@dataclass(frozen=True, slots=True)
class SyzygyTensorComparison:
    """Small full-cochain witnesses, with no claimed physical coupling."""

    primitive: SparseOuterCechCochain
    boundary: SparseOuterCechCochain
    raw_boundary_wedge: SparseOuterCechCochain
    raw_closure_defect: SparseOuterCechCochain
    corrected_primitive_wedge: SparseOuterCechCochain
    corrected_boundary_wedge: SparseOuterCechCochain
    null_wedge: SparseOuterCechCochain

    def as_record(self) -> dict[str, object]:
        return {
            "matter_character": [0, 0],
            "other_matter_character": [1, 0],
            "primitive": _record(self.primitive),
            "boundary": _record(self.boundary),
            "raw_boundary_wedge": _record(self.raw_boundary_wedge),
            "raw_closure_defect": _record(self.raw_closure_defect),
            "corrected_primitive_wedge": _record(self.corrected_primitive_wedge),
            "corrected_boundary_wedge": _record(self.corrected_boundary_wedge),
            "original_null_wedge_term_count": len(self.null_wedge.terms),
            "original_null_wedge_digest": _cochain_digest((self.null_wedge,)),
            "primitive_internal_support": [-1],
            "full_rank_one_row_closed_exact": True,
            "primitive_and_boundary_strict_character_exact": True,
            "boundary_is_nonzero_exact_cycle": True,
            "raw_boundary_wedge_closed_exact": False,
            "corrected_boundary_wedge_is_full_primitive_differential": True,
            "corrected_boundary_wedge_closed_exact": True,
            "original_null_wedge_unchanged_exact": True,
            "all_input_F_tensor_identity_derived_under_rank_one_hypotheses": True,
            "outer_cone_comparison_certified": False,
            "natural_physical_pairing_certified": False,
        }


@cache
def alternate_up_syzygy_tensor_comparison() -> SyzygyTensorComparison:
    """Add an exact syzygy boundary, not another matter class or input ray."""

    source, _ = alternate_higgs_quotient_models()
    unit = mixed_schoen_unit()
    context = _MixedContraction(source, unit)
    _closed_rank_one_row(source)
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    frames = {
        name: (_common_frame(source, action), Matrix.identity(1, scalar_type=Eisenstein))
        for name, action in actions.items()
    }
    # An explicit local x1 u0^-5 p0 on a u-edge has total degree zero
    # in the first odd Hilbert--Burch object. It is solely a boundary test.
    raw = SparseOuterCechCochain(((OuterCechBasis(
        context.components[(5, 0, "k0")],
        (0, 1, 0), (-5, 0, 0), (1, 0), ((0,), (0, 1), (0,)),
    ), Eisenstein(1)),))
    primitive = _project(raw, (0, 0), context, actions, frames)
    boundary = context.differential(primitive)
    left, right = alternate_null_matter()
    if (
        primitive.is_zero() or boundary.is_zero()
        or {b.component.object_degree for b, _ in primitive.terms} != {-1}
        or not _strict(primitive, (0, 0), context, actions, frames)
        or not _strict(boundary, (0, 0), context, actions, frames)
        or not context.differential(boundary).is_zero()
        or not context.differential(left + boundary).is_zero()
    ):
        raise ValueError("the actual syzygy attack needs a nonzero strict exact boundary")
    exterior, _ = alternate_up_exterior_context()
    out = _MixedContraction(exterior, unit)
    raw_wedge = resolution_vector_wedge(boundary, right, exterior, out, 1, 1)
    defect = out.differential(raw_wedge)
    corrected_primitive = rank_one_vector_wedge(
        primitive, right, source, exterior, out, 0, 1,
    )
    corrected = rank_one_vector_wedge(boundary, right, source, exterior, out, 1, 1)
    original = resolution_vector_wedge(left, right, exterior, out, 1, 1)
    null = rank_one_vector_wedge(left, right, source, exterior, out, 1, 1)
    changed = rank_one_vector_wedge(left + boundary, right, source, exterior, out, 1, 1)
    if (
        defect.is_zero() or corrected != out.differential(corrected_primitive)
        or not out.differential(corrected).is_zero()
        or null != original or changed != null + corrected
        or not out.differential(changed).is_zero()
    ):
        raise ValueError(
            "the complete syzygy tensor comparison failed its actual boundary identity"
        )
    return SyzygyTensorComparison(
        primitive, boundary, raw_wedge, defect, corrected_primitive, corrected, null,
    )


def write_syzygy_tensor_comparison(path: Path = OUTPUT) -> dict[str, object]:
    """Persist the graded comparison without altering any scalar witnesses."""

    payload: dict[str, object] = {
        "schema": "alternate-up-syzygy-tensor-comparison-v1",
        "coefficient_field": "Q(omega)",
        "scope": "closed rank-one mixed row on the frozen alternate F resolution",
        "comparison": alternate_up_syzygy_tensor_comparison().as_record(),
        "complete_tensor_comparison_certified": False,
        "complete_holomorphic_up_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            name: _verified_payload(source)[0]
            for name, source in (
                ("actual_matter", MATTER), ("null_channels", NULL_CHANNELS),
                ("even_boundary_attack", EVEN_ATTACK),
            )
        },
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    record = write_syzygy_tensor_comparison()
    print(f"artifact_digest: {record['artifact_digest']}")
