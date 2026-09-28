"""Guard the actual representative-independence counterexample's scope.

Owns:
    The full strict-character boundary and raw-wedge failure witnesses.

Depends on:
    Actual alternate carrier inputs and the boundary-attack experiment.

Must not:
    Turn a cochain-operation failure into a carrier or physical no-go.

Phase 0:
    Research-only regressions for a necessary tensor-comparison gate.
"""

from research.experiments.scientific_genesis.alternate_up_exterior_boundary_attack import (
    OUTPUT,
    alternate_up_exterior_boundary_attack,
)
from research.experiments.scientific_genesis.alternate_up_exterior_higgs_action import (
    alternate_up_exterior_context,
)
from research.experiments.scientific_genesis.alternate_up_first_order_scalar import (
    alternate_null_matter,
)
from research.experiments.scientific_genesis.alternate_up_higgs_quotient_cone import (
    alternate_higgs_quotient_models,
)
from research.experiments.scientific_genesis.mixed_schoen_exterior_square import (
    even_rank_one_vector_wedge,
    resolution_vector_wedge,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import _MixedContraction
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import mixed_schoen_unit
from research.experiments.scientific_genesis.mixed_schoen_outer_universal_cone import (
    _representative,
    _verified_payload,
)


def test_actual_boundary_preserves_the_matter_class_but_not_raw_wedge_closure() -> None:
    """Use the complete differential and the unchanged actual other input."""

    attack = alternate_up_exterior_boundary_attack()
    second, _ = alternate_higgs_quotient_models()
    unit = mixed_schoen_unit()
    context = _MixedContraction(second, unit)
    assert len(attack.boundary_primitive.terms) == 3
    assert len(attack.boundary.terms) == 15
    assert context.differential(attack.boundary_primitive) == attack.boundary
    left, right = alternate_null_matter()
    assert context.differential(left + attack.boundary).is_zero()
    exterior, _ = alternate_up_exterior_context()
    wedge_context = _MixedContraction(exterior, unit)
    assert wedge_context.differential(attack.original_wedge).is_zero()
    changed = resolution_vector_wedge(left + attack.boundary, right, exterior, wedge_context, 1, 1)
    assert wedge_context.differential(changed) == attack.closure_defect
    assert len(attack.closure_defect.terms) == 124
    assert not attack.closure_defect.is_zero()


def test_full_leibniz_defect_has_the_declared_differential() -> None:
    """A hypothetical repair cannot silently set the 48-term defect to zero."""

    attack = alternate_up_exterior_boundary_attack()
    exterior, _ = alternate_up_exterior_context()
    context = _MixedContraction(exterior, mixed_schoen_unit())
    assert len(attack.leibniz_defect.terms) == 48
    assert (
        context.differential(attack.primitive_wedge) + attack.boundary_wedge.scale(-1)
        == attack.leibniz_defect
    )
    assert context.differential(attack.leibniz_defect) == attack.closure_defect.scale(-1)


def test_attack_artifact_retains_exact_witnesses_without_refuting_physics() -> None:
    """A failure of one operation does not negate the checked original screens."""

    _, record = _verified_payload(OUTPUT)
    attack = alternate_up_exterior_boundary_attack()
    assert record["attack"] == attack.as_record()
    for name, cochain in (
        ("boundary_primitive", attack.boundary_primitive), ("exact_boundary", attack.boundary),
        ("closure_defect", attack.closure_defect), ("leibniz_defect", attack.leibniz_defect),
        ("corrected_boundary_wedge", attack.corrected_boundary_wedge),
    ):
        assert _representative(record["attack"][name]) == cochain
    for field in (
        "carrier_refuted", "original_ordered_scalar_screens_refuted",
        "physical_null_coefficient_assigned",
    ):
        assert record["attack"][field] is False
    assert record["natural_product_comparison_certified"] is False
    assert record["complete_holomorphic_up_matrix_available"] is False


def test_derived_even_correction_restores_the_actual_boundary_identity() -> None:
    """The correction is a coefficient homotopy, not a changed scalar residue."""

    attack = alternate_up_exterior_boundary_attack()
    second, _ = alternate_higgs_quotient_models()
    exterior, _ = alternate_up_exterior_context()
    context = _MixedContraction(exterior, mixed_schoen_unit())
    left, right = alternate_null_matter()
    assert len(attack.corrected_boundary_wedge.terms) == 302
    assert attack.corrected_boundary_wedge == context.differential(attack.primitive_wedge)
    assert context.differential(attack.corrected_boundary_wedge).is_zero()
    assert attack.corrected_null_wedge == attack.original_wedge
    changed = even_rank_one_vector_wedge(
        left + attack.boundary, right, second, exterior, context, 1, 1,
    )
    assert changed == attack.corrected_null_wedge + attack.corrected_boundary_wedge
    assert context.differential(changed).is_zero()
