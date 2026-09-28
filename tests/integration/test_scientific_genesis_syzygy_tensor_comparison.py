"""Verify the actual odd-object boundary comparison without a scalar solve.

Owns:
    Complete syzygy witnesses, exact boundary identities, and fail-closed
    distinctions between the F comparison and the physical outer product.

Depends on:
    Actual carrier cochains, the full differential, and the saved comparison.

Must not:
    Assign physical couplings from a tensor identity or normalize a trace.

Phase 0:
    Research-only actual-input regression and artifact verification.
"""

from research.experiments.scientific_genesis.alternate_up_exterior_higgs_action import (
    alternate_up_exterior_context,
)
from research.experiments.scientific_genesis.alternate_up_higgs_quotient_cone import (
    alternate_higgs_quotient_models,
)
from research.experiments.scientific_genesis.alternate_up_syzygy_tensor_comparison import (
    OUTPUT,
    alternate_up_syzygy_tensor_comparison,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import _MixedContraction
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import mixed_schoen_unit
from research.experiments.scientific_genesis.mixed_schoen_outer_universal_cone import (
    _representative,
    _verified_payload,
)


def test_actual_syzygy_boundary_comparison_uses_full_differentials() -> None:
    comparison = alternate_up_syzygy_tensor_comparison()
    source, _ = alternate_higgs_quotient_models()
    context = _MixedContraction(source, mixed_schoen_unit())
    exterior, _ = alternate_up_exterior_context()
    out = _MixedContraction(exterior, mixed_schoen_unit())
    assert len(comparison.primitive.terms) == 3
    assert {b.component.object_degree for b, _ in comparison.primitive.terms} == {-1}
    assert len(comparison.boundary.terms) == 27
    assert context.differential(comparison.primitive) == comparison.boundary
    assert context.differential(comparison.boundary).is_zero()
    assert len(comparison.raw_closure_defect.terms) == 489
    assert out.differential(comparison.raw_boundary_wedge) == comparison.raw_closure_defect
    assert len(comparison.corrected_primitive_wedge.terms) == 47
    assert len(comparison.corrected_boundary_wedge.terms) == 294
    assert out.differential(comparison.corrected_primitive_wedge) == (
        comparison.corrected_boundary_wedge
    )
    assert out.differential(comparison.corrected_boundary_wedge).is_zero()
    assert len(comparison.null_wedge.terms) == 2997
    assert out.differential(comparison.null_wedge).is_zero()


def test_syzygy_comparison_artifact_matches_actual_cochains_and_scope() -> None:
    _, record = _verified_payload(OUTPUT)
    comparison = alternate_up_syzygy_tensor_comparison()
    assert record["comparison"] == comparison.as_record()
    for name, cochain in (
        ("primitive", comparison.primitive), ("boundary", comparison.boundary),
        ("raw_boundary_wedge", comparison.raw_boundary_wedge),
        ("raw_closure_defect", comparison.raw_closure_defect),
        ("corrected_primitive_wedge", comparison.corrected_primitive_wedge),
        ("corrected_boundary_wedge", comparison.corrected_boundary_wedge),
    ):
        assert _representative(record["comparison"][name]) == cochain
    assert record["comparison"]["outer_cone_comparison_certified"] is False
    assert record["comparison"]["natural_physical_pairing_certified"] is False
    assert record["complete_tensor_comparison_certified"] is False
    assert record["complete_holomorphic_up_matrix_available"] is False
    assert record["physical_yukawa_matrix_available"] is False
    assert record["extension_point_selected"] is False
    assert record["observational_inputs_used"] is False
