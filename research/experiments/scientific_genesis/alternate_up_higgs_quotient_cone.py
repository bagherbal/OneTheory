"""Construct the natural quotient exterior cone seen by the alternate Higgs.

Owns:
    The B1-twisted Hilbert--Burch quotient of F by its actual A section,
    both full connecting arrows, and the descended-support Higgs covector.

Depends on:
    The actual frozen Serre constituent, global first quotient, graded
    exterior square, full outer coefficients, and exact Hom differential.

Must not:
    Treat an ideal sheaf as a vector bundle, infer a fibrewise quotient
    where a section vanishes, or invent a physical Yukawa coefficient.

Phase 0:
    Research-only quotient construction for a genuine Higgs-cone comparison.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)

from .alternate_up_dual_higgs_inputs import _quotient
from .alternate_up_exterior_higgs_action import OUTPUT as EXTERIOR_WITNESSES
from .alternate_up_exterior_higgs_action import (
    alternate_up_exterior_context,
    alternate_up_exterior_primitive,
)
from .alternate_up_higgs_covector_comparison import (
    QUOTIENT_LINE,
    alternate_outer_coefficient,
    quotient_outer_exterior_action,
)
from .alternate_up_higgs_hom_representative import load_alternate_up_higgs_hom_full_cochain
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
    MixedSchoenConstituent,
    _constituent,
)
from .mixed_schoen_common_dga import mixed_outer_cup
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import MixedSchoenUnit, mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_higgs_quotient_cone.json"


@cache
def alternate_higgs_quotient_models() -> tuple[MixedSchoenConstituent, MixedSchoenUnit]:
    """Use K=B1 tensor (F/A_F), not a fabricated additional bundle.

    The actual Serre exact sequence identifies F/A_F with I6 B2.
    Removing the A object kills all mixed extension terms and leaves
    the complete published Hilbert--Burch ideal resolution. The global
    inclusion A_F-to-F remains injective as a sheaf map at its zeros;
    no fibrewise subbundle assertion is used.
    """

    second = _constituent(lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1,
    ), "I6-ray-0-1", 2, (1, -1, 0))
    if (
        second.objects[0].position != 0
        or any(term.target != 0 for term in second.extension_terms)
        or any(arrow.source == 0 or arrow.target == 0 for arrow in second.resolution_arrows)
    ):
        raise ValueError("the actual A-section quotient presentation changed")
    objects = tuple(MixedConstituentObject(
        f"B1 tensor {item.name}", item.position,
        cast(tuple[int, int, int], tuple(
            a + b for a, b in zip(QUOTIENT_LINE, item.line_degree, strict=True)
        )),
    ) for item in second.objects[1:])
    quotient = MixedSchoenUnit(
        "B1 tensor I6 B2", second.factor,
        cast(tuple[int, int, int], tuple(
            a + b for a, b in zip(QUOTIENT_LINE, second.twist, strict=True)
        )),
        objects,
        tuple(replace(arrow, source=arrow.source - 1, target=arrow.target - 1)
              for arrow in second.resolution_arrows),
    )
    return second, quotient


@cache
def alternate_higgs_quotient_covector() -> SparseOuterCechCochain:
    """Retarget the same Higgs through F-to-F/A_F and verify full closure."""

    return quotient_higgs_covector(load_alternate_up_higgs_hom_full_cochain())


def quotient_higgs_covector(full: SparseOuterCechCochain) -> SparseOuterCechCochain:
    """Retarget an explicitly supplied A-supported Hom cycle on this fixed quotient."""

    _, quotient = alternate_higgs_quotient_models()
    context = _MixedContraction(mixed_schoen_unit(), quotient)
    result = []
    for basis, coefficient in full.terms:
        if basis.component.left_index != 0 or basis.component.right_index == 0:
            raise ValueError("the saved Higgs no longer factors through F/A_F")
        component = context.components[(
            0, basis.component.right_index - 1, basis.component.koszul_summand,
        )]
        if component != replace(basis.component, right_index=basis.component.right_index - 1):
            raise ValueError("the actual ideal-quotient Higgs grading changed")
        result.append((OuterCechBasis(
            component, basis.x_monomial, basis.u_monomial, basis.p_monomial, basis.cell,
        ), coefficient))
    cochain = SparseOuterCechCochain(tuple(result))
    if cochain.is_zero() or not context.differential(cochain).is_zero():
        raise ValueError("the Higgs is not closed on its actual ideal-quotient resolution")
    return cochain


@cache
def alternate_higgs_quotient_connecting_arrow(parameter_index: int) -> SparseOuterCechCochain:
    """Require a genuine closed connecting map from the full exterior F.

    Push out 0-to-E-to-V-to-F-to-0 by E-to-B1 to obtain the rank-three
    bundle R. Its exterior sequence has subobject B1 tensor F. Push
    this sequence out by B1 tensor F-to-K. The resulting coherent Q
    has 0-to-K-to-Q-to-det(F)-to-0. This function constructs its exact
    degree-one arrow, not a speculative relation between domains.
    """

    second, quotient = alternate_higgs_quotient_models()
    exterior, _ = alternate_up_exterior_context()
    b_line = MixedSchoenUnit(
        "B1", 0, QUOTIENT_LINE,
        (MixedConstituentObject("B1", 0, QUOTIENT_LINE),),
    )
    raw = quotient_outer_exterior_action(_quotient(
        alternate_outer_coefficient(parameter_index), _MixedContraction(b_line, second),
    ), exterior)
    context = _MixedContraction(quotient, exterior)
    result = []
    for basis, coefficient in raw.terms:
        if basis.component.left_index == 0:
            continue
        component = context.components[(
            basis.component.left_index - 1,
            basis.component.right_index, basis.component.koszul_summand,
        )]
        if component != replace(basis.component, left_index=basis.component.left_index - 1):
            raise ValueError("the quotient connecting map changed its actual grading")
        result.append((OuterCechBasis(
            component, basis.x_monomial, basis.u_monomial, basis.p_monomial, basis.cell,
        ), coefficient))
    arrow = SparseOuterCechCochain(tuple(result))
    if arrow.is_zero() or not context.differential(arrow).is_zero():
        raise ValueError("the actual quotient connecting arrow is not a nonzero full cycle")
    return arrow


def checked_quotient_higgs_action(parameter_index: int) -> SparseOuterCechCochain:
    """Reuse the pinned full exterior result only after an actual new composition."""

    action = mixed_outer_cup(
        alternate_higgs_quotient_covector(),
        alternate_higgs_quotient_connecting_arrow(parameter_index),
    )
    _, reference = _verified_payload(EXTERIOR_WITNESSES)
    raw = reference.get("witnesses")
    if (
        reference.get("schema") != "alternate-up-exterior-higgs-action-v1"
        or reference.get("outer_parameter_basis") != ["a0", "a1"]
        or not isinstance(raw, list) or len(raw) != 2
    ):
        raise ValueError("the pinned full exterior witness basis changed")
    witnesses = cast(list[dict[str, object]], raw)
    if _cochain_digest((action.scale(-1),)) != witnesses[parameter_index]["product_digest"]:
        raise ValueError(
            "the natural quotient-cone action differs from the checked exterior product"
        )
    return action


@dataclass(frozen=True, slots=True)
class AlternateQuotientHiggsCocycle:
    """The actual universal covector (h, a0 k0+a1 k1) on the quotient cone."""

    covector: SparseOuterCechCochain
    corrections: tuple[SparseOuterCechCochain, SparseOuterCechCochain]


@cache
def alternate_higgs_quotient_cocycle() -> AlternateQuotientHiggsCocycle:
    """Assemble actual cochains only after checking both cone identities."""

    covector = alternate_higgs_quotient_covector()
    _, context = alternate_up_exterior_context()
    corrections = []
    for index in range(2):
        correction = alternate_up_exterior_primitive(index).primitive
        action = checked_quotient_higgs_action(index)
        if not (context.differential(correction) + action).is_zero():
            raise ValueError("the actual quotient Higgs failed its coefficientwise cone identity")
        corrections.append(correction)
    return AlternateQuotientHiggsCocycle(covector, (corrections[0], corrections[1]))


def write_alternate_higgs_quotient_cone(path: Path = OUTPUT) -> dict[str, object]:
    """Certify the natural cone and null comparison, reusing exact primitives.

    This writer does not claim to rerun the primitive solver. Its existing
    full differential identities are explicit content-pinned prerequisites.
    The cocycle factory above reconstructs the cochains when an evaluator
    needs them. No physical scalar is assigned by this construction.
    """

    from .alternate_up_first_order_scalar import alternate_up_ordered_tensor_difference

    prerequisite_digest, reference = _verified_payload(EXTERIOR_WITNESSES)
    raw_witnesses = reference.get("witnesses")
    if (
        reference.get("schema") != "alternate-up-exterior-higgs-action-v1"
        or not isinstance(raw_witnesses, list) or len(raw_witnesses) != 2
        or any(item.get("full_primitive_identity_exact") is not True for item in raw_witnesses)
    ):
        raise ValueError("the exact exterior primitive prerequisites changed")
    _, quotient = alternate_higgs_quotient_models()
    h = alternate_higgs_quotient_covector()
    records = []
    for index, primitive_record in enumerate(raw_witnesses):
        arrow = alternate_higgs_quotient_connecting_arrow(index)
        action = checked_quotient_higgs_action(index)
        difference = alternate_up_ordered_tensor_difference(index)
        if any(basis.component.left_index != 0 for basis, _ in difference.terms):
            raise ValueError("the actual null matter comparison survives the legitimate A quotient")
        records.append({
            "parameter": f"a{index}",
            "connecting_arrow_term_count": len(arrow.terms),
            "connecting_arrow_digest": _cochain_digest((arrow,)),
            "full_connecting_arrow_closed_exact": True,
            "higgs_action_term_count": len(action.terms),
            "higgs_action_digest": _cochain_digest((action,)),
            "negative_action_equals_pinned_primitive_differential": True,
            "primitive_term_count": primitive_record["primitive_term_count"],
            "primitive_digest": primitive_record["primitive_digest"],
            "primitive_solver_reexecuted_by_this_writer": False,
            "raw_null_tensor_difference_term_count": len(difference.terms),
            "raw_null_tensor_difference_digest": _cochain_digest((difference,)),
            "raw_difference_has_only_actual_A_support": True,
            "projected_null_tensor_difference_zero_exact": True,
        })
    payload: dict[str, object] = {
        "schema": "alternate-up-higgs-quotient-cone-v1",
        "coefficient_field": "Q(omega)",
        "outer_parameter_basis": ["a0", "a1"],
        "quotient_ideal_resolution_object_count": len(quotient.objects),
        "quotient_ideal_resolution_arrow_count": len(quotient.resolution_arrows),
        "quotient_ideal_resolution_twist": list(quotient.twist),
        "quotient_is_a_vector_bundle": False,
        "quotient_covector_term_count": len(h.terms),
        "quotient_covector_digest": _cochain_digest((h,)),
        "full_quotient_covector_closed_exact": True,
        "parameter_coefficients": records,
        "universal_triangular_quotient_cone_squared_zero_exact": True,
        "higgs_lift_exists_by_full_pinned_primitive_identities": True,
        "null_matter_quotient_tensor_comparison_exact": True,
        "natural_sheaf_maps": [
            "E to B1 by the certified global signed-minor row",
            "V to R by pushing out the actual outer extension",
            "exterior R to Q by B1 tensor F to B1 tensor I6 B2",
            "exterior V to Q by functorial composition",
        ],
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "complete_holomorphic_up_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "prerequisite_artifact_digests": {"full_exterior_primitives": prerequisite_digest},
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    result = write_alternate_higgs_quotient_cone()
    print(f"artifact_digest: {result['artifact_digest']}")
