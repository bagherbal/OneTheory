"""Derive the actual down-Higgs covector on the frozen natural quotient cone.

Owns:
    Retargeting the pinned down-Higgs Hom class through the actual ideal
    quotient, both coefficient actions, and exact full exterior primitives.

Depends on:
    The unchanged global quotient and exterior engines, actual universal
    outer coefficients, pinned down-Higgs input, and original full differential.

Must not:
    Relabel up-sector primitives, invent a Higgs correction, select a moduli
    point, assign a Yukawa entry, or infer metrics, masses, or a common vacuum.

Phase 0:
    Conditional heterotic research calculation; the remaining flavor sectors
    require their own actual matter products and scalar traces.
"""

from . import alternate_down_higgs_hom_representative as hom
from .alternate_up_dual_higgs_inputs import _quotient
from .alternate_up_exterior_higgs_action import (
    alternate_up_exterior_context,
    exact_exterior_primitive,
)
from .alternate_up_ff_entries import _write_witnesses
from .alternate_up_higgs_covector_comparison import QUOTIENT_LINE, alternate_outer_coefficient
from .alternate_up_higgs_quotient_cone import (
    alternate_higgs_quotient_connecting_arrow,
    alternate_higgs_quotient_models,
    quotient_higgs_covector,
)
from .mixed_constituent_schoen_arrows import MixedConstituentObject
from .mixed_schoen_common_dga import mixed_outer_cup
from .mixed_schoen_exterior_square import reciprocal_covector_wedge
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import MixedSchoenUnit
from .mixed_schoen_outer_universal_cone import _verified_payload

OUTPUT = hom.ROOT / "data/generated/scientific_genesis/alternate_down_higgs_quotient_cone.json"
HOM_DIGEST = "476e48e981ab66382b43d2510d7a271b2fa3f82468f885b7050edb9af3cd9276"


def write_down_higgs_quotient_cone(path=OUTPUT):
    """Compute both real correction coefficients; no saved up value is substituted."""

    record, full = hom.load_down_higgs_hom(expected_digest=HOM_DIGEST)
    second, quotient = alternate_higgs_quotient_models()
    exterior, context = alternate_up_exterior_context()
    b = MixedSchoenUnit("B1", 0, QUOTIENT_LINE, (
        MixedConstituentObject("B1", 0, QUOTIENT_LINE),
    ))
    inverse_line = tuple(-value for value in QUOTIENT_LINE)
    inverse_b = MixedSchoenUnit("B1 inverse", 0, inverse_line, (
        MixedConstituentObject("B1 inverse", 0, inverse_line),
    ))
    inverse_context = _MixedContraction(inverse_b, second)
    if (any(basis.component != inverse_context.components[(
        0, basis.component.right_index, basis.component.koszul_summand,
    )] for basis, _ in full.terms) or not inverse_context.differential(full).is_zero()):
        raise ValueError("the down-Higgs Hom input does not define the actual reciprocal covector")
    h = quotient_higgs_covector(full)
    witnesses, coefficients = {"quotient_covector": h}, []
    for index in (0, 1):
        print(f"down Higgs a{index}: forming the actual quotient action", flush=True)
        action = mixed_outer_cup(h, alternate_higgs_quotient_connecting_arrow(index))
        product = reciprocal_covector_wedge(full, _quotient(
            alternate_outer_coefficient(index), _MixedContraction(b, second),
        ), exterior, context, 1, 1)
        if action != product.scale(-1) or not context.differential(action).is_zero():
            raise ValueError("the actual down action differs from its independent signed wedge")
        print(f"down Higgs a{index}: solving its full exterior identity", flush=True)
        primitive = exact_exterior_primitive(index, product)
        if not (context.differential(primitive.primitive) + action).is_zero():
            raise ValueError("the down-Higgs coefficient fails its full cone equation")
        coefficients.append({
            **primitive.as_record(), "negative_action_equals_ordered_wedge_exact": True,
            "full_down_higgs_cone_identity_exact": True,
        })
        witnesses[f"action_a{index}"] = action
        witnesses[f"ordered_product_a{index}"] = product
        witnesses[f"correction_a{index}"] = primitive.primitive
        print(f"down Higgs a{index}: full identity verified", flush=True)
    return _write_witnesses(path, {
        "schema": "alternate-down-higgs-quotient-cone-v1",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "coefficient_field": "Q(omega)", "outer_parameter_basis": ["a0", "a1"],
        "native_hom_character": [2, 2], "repaired_higgs_forward_character": [0, 1],
        "source": record["source"], "higgs_input_proof_sha256": record["proof_sha256"],
        "quotient_is_a_vector_bundle": False, "quotient_object_count": len(quotient.objects),
        "scalar_order": "Higgs first; unchanged original quotient and determinant frames",
        "full_quotient_covector_closed_exact": True, "coefficient_identities": coefficients,
        "quotient_higgs_lift_computed": True, "up_sector_primitive_values_reused": False,
        "full_exterior_square_higgs_constructed": False,
        "complete_down_matrix_available": False, "complete_charged_lepton_matrix_available": False,
        "physical_yukawas_available": False, "extension_point_selected": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "actual_down_higgs_hom": HOM_DIGEST,
            "frozen_carrier": record["prerequisite_artifact_digests"]["frozen_carrier"],
            "outer_invariants": _verified_payload(hom.ROOT / (
                "data/generated/scientific_genesis/alternate_constituent_outer_invariants.json"
            ))[0],
        },
        "next_required_object": (
            "independently replay both primitives, then compute actual down and "
            "charged-lepton matter products and complete scalar traces"
        ),
    }, witnesses)


if __name__ == "__main__":
    result = write_down_higgs_quotient_cone()
    print(result["artifact_digest"], result["witnesses"], flush=True)
