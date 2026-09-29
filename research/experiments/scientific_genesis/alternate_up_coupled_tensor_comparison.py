"""Compare the derived two-row quotient with the actual alternate carrier cone.

Owns:
    Full-Koszul pushout presentations for both universal outer coefficients,
    exact agreement with the existing K/exterior-F cone, and actual Leibniz checks.

Depends on:
    The fixed published-input constituent, global signed-minor quotient,
    strict outer coefficients, actual matter, and derived H/T tensor coherence.

Must not:
    Choose an extension point, conflate an ideal quotient with a bundle,
    assign a physical matrix, or alter existing ordered scalar witnesses.

Phase 0:
    Research-only actual coupled-product comparison, prior to scalar evaluation.
"""

from __future__ import annotations

import json
from dataclasses import replace
from functools import cache
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)

from .alternate_up_dual_higgs_inputs import _quotient
from .alternate_up_exterior_higgs_action import alternate_up_exterior_context
from .alternate_up_first_order_scalar import alternate_null_matter
from .alternate_up_higgs_covector_comparison import QUOTIENT_LINE, alternate_outer_coefficient
from .alternate_up_higgs_quotient_cone import OUTPUT as QUOTIENT_CONE
from .alternate_up_higgs_quotient_cone import (
    alternate_higgs_quotient_connecting_arrow,
    alternate_higgs_quotient_models,
)
from .alternate_up_syzygy_tensor_comparison import OUTPUT as SYZYGY
from .mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
    MixedExtensionTerm,
    MixedResolutionArrow,
)
from .mixed_schoen_coupled_tensor import (
    CoupledExteriorQuotient,
    coupled_exterior_quotient,
    coupled_quotient_vector_wedge,
)
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import MixedSchoenUnit, mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _representative, _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_coupled_tensor_comparison.json"


@cache
def alternate_coupled_quotient(parameter_index: int) -> CoupledExteriorQuotient:
    """Build a coefficient presentation, never a selected extension point."""

    if parameter_index not in (0, 1):
        raise ValueError("the universal alternate outer coefficient is unavailable")
    source, _ = alternate_higgs_quotient_models()
    line = MixedSchoenUnit(
        "actual B1 pushout line", 0, QUOTIENT_LINE,
        (MixedConstituentObject("actual B1 pushout line", 0, QUOTIENT_LINE),),
    )
    beta = _quotient(alternate_outer_coefficient(parameter_index), _MixedContraction(line, source))
    terms = []
    for b, v in beta.terms:
        c = b.component
        if c.left_index != 0 or b.total_degree != 1:
            raise ValueError("the actual pushout row has incompatible orientation or degree")
        subset: int | tuple[int, int] | None = {
            "k0": None, "k1_x": 1, "k1_u": 2, "k2": (1, 2),
        }[c.koszul_summand]
        terms.append(MixedExtensionTerm(
            c.right_index + 1, 0, c.object_degree, subset,
            b.x_monomial, b.u_monomial, b.p_monomial, b.cell,
            v * (-1 if c.object_degree == 0 else 1),
        ))
    pushed = MixedSchoenUnit(
        f"actual B1 pushout coefficient a{parameter_index}", source.factor, (0, 0, 0),
        line.objects + source.objects,
        tuple(replace(a, source=a.source + 1, target=a.target + 1)
              for a in source.resolution_arrows),
        tuple(replace(t, source=t.source + 1, target=t.target + 1)
              for t in source.extension_terms) + tuple(terms),
    )
    return coupled_exterior_quotient(pushed, 1, 0)


@cache
def alternate_coupled_presentation_check(parameter_index: int) -> dict[str, object]:
    """Compare every actual object, polynomial arrow, and mixed arrow block."""

    model = alternate_coupled_quotient(parameter_index)
    _, ideal = alternate_higgs_quotient_models()
    exterior, _ = alternate_up_exterior_context()
    indices = {p: i for i, p in enumerate(exterior.pairs)}
    blocks = {}
    for i, (a, b) in enumerate(model.quotient.pairs):
        blocks[i] = ("K", b - 2) if a == 0 else ("F", indices[(a - 1, b - 1)])
        kind, index = blocks[i]
        obj = (ideal if kind == "K" else exterior).objects[index]
        actual = model.quotient.objects[i]
        if (actual.position, actual.line_degree) != (obj.position, obj.line_degree):
            raise ValueError("the actual quotient object disagrees with the existing cone basis")
    poly: dict[str, list[MixedResolutionArrow]] = {"K": [], "F": []}
    inner = []
    cross = []
    context = _MixedContraction(ideal, exterior)
    for arrow in model.quotient.resolution_arrows:
        first, i = blocks[arrow.source]
        second, j = blocks[arrow.target]
        if first != second:
            raise ValueError("the actual quotient has an unexpected cross-block polynomial")
        poly[first].append(replace(arrow, source=i, target=j))
    for term in model.quotient.extension_terms:
        first, i = blocks[term.source]
        second, j = blocks[term.target]
        if first == second == "F":
            inner.append(replace(term, source=i, target=j))
        elif first == "F" and second == "K":
            component = context.components[(j, i, term.koszul_summand)]
            if component.object_degree != term.parent_degree:
                raise ValueError("the actual quotient connecting arrow changed internal degree")
            cross.append((OuterCechBasis(component, term.x_monomial, term.u_monomial,
                                         term.p_monomial, term.cell),
                          term.coefficient * (-1 if term.parent_degree == 0 else 1)))
        else:
            raise ValueError("the actual quotient has an unexpected mixed-arrow block")
    delta = SparseOuterCechCochain(tuple(cross))
    if (
        set(poly["K"]) != set(ideal.resolution_arrows)
        or set(poly["F"]) != set(exterior.resolution_arrows)
        or set(inner) != set(exterior.extension_terms)
        or delta != alternate_higgs_quotient_connecting_arrow(parameter_index)
        or not context.differential(delta).is_zero()
    ):
        raise ValueError("the derived coupled presentation differs from the actual quotient cone")
    return {
        "parameter": f"a{parameter_index}",
        "source_object_count": len(model.source.objects),
        "quotient_object_count": len(model.quotient.objects),
        "source_k2_arrow_term_count": sum(
            t.koszul_degree == 2 for t in model.source.extension_terms
        ),
        "quotient_mixed_arrow_term_count": len(model.quotient.extension_terms),
        "connecting_arrow_term_count": len(delta.terms),
        "connecting_arrow_digest": _cochain_digest((delta,)),
        "complete_outer_row_closed_against_inner_complex": True,
        "all_objects_and_polynomial_blocks_equal_exact": True,
        "complete_inner_mixed_block_equal_exact": True,
        "complete_connecting_arrow_equal_exact": True,
        "legitimate_A_wedge_B_relation_differential_invariant": True,
        "quotient_is_a_vector_bundle": False,
    }


def _push_f_vector(
    cochain: SparseOuterCechCochain, model: CoupledExteriorQuotient,
) -> SparseOuterCechCochain:
    context = _MixedContraction(model.source, mixed_schoen_unit())
    result = []
    for b, v in cochain.terms:
        c = context.components[(b.component.left_index + 1, 0, b.component.koszul_summand)]
        if (c.object_degree, c.line_degree) != (b.component.object_degree, b.component.line_degree):
            raise ValueError("the actual F inclusion into R changed its homogeneous line or degree")
        result.append((replace(b, component=c), v))
    return SparseOuterCechCochain(tuple(result))


@cache
def alternate_coupled_leibniz_check(parameter_index: int) -> dict[str, object]:
    """Use an actual syzygy and null matter; neither is assumed closed in R."""

    model = alternate_coupled_quotient(parameter_index)
    _, stored = _verified_payload(SYZYGY)
    if stored.get("schema") != "alternate-up-syzygy-tensor-comparison-v1":
        raise ValueError("the actual syzygy witness prerequisite changed")
    comparison = stored.get("comparison")
    if not isinstance(comparison, dict) or not isinstance(comparison.get("primitive"), dict):
        raise ValueError("the actual syzygy primitive is missing from its explicit archive")
    primitive = _push_f_vector(_representative(comparison["primitive"]), model)
    other = _push_f_vector(alternate_null_matter()[1], model)
    context = _MixedContraction(model.source, mixed_schoen_unit())
    out = _MixedContraction(model.quotient, mixed_schoen_unit())
    dp, db = context.differential(primitive), context.differential(other)
    if primitive.is_zero() or other.is_zero() or db.is_zero():
        raise ValueError("the actual coupled attack needs its nonzero outer matter image")
    product = coupled_quotient_vector_wedge(primitive, other, model, 0, 1)
    first = coupled_quotient_vector_wedge(dp, other, model, 1, 1)
    second = coupled_quotient_vector_wedge(primitive, db, model, 0, 2)
    image = out.differential(product)
    if (
        image != first + second or not context.differential(dp).is_zero()
        or not context.differential(db).is_zero()
    ):
        raise ValueError(
            "the actual coupled tensor product failed its complete signed Leibniz identity"
        )
    return {
        "parameter": f"a{parameter_index}",
        "syzygy_primitive_term_count": len(primitive.terms),
        "right_null_matter_term_count": len(other.terms),
        "source_primitive_image_term_count": len(dp.terms),
        "source_right_matter_image_term_count": len(db.terms),
        "product_term_count": len(product.terms),
        "product_digest": _cochain_digest((product,)),
        "first_differentiated_slot_term_count": len(first.terms),
        "second_differentiated_slot_term_count": len(second.terms),
        "full_product_differential_term_count": len(image.terms),
        "full_product_differential_digest": _cochain_digest((image,)),
        "full_signed_leibniz_identity_exact": True,
        "source_differential_squares_checked_exact": True,
        "constituent_null_matter_assumed_closed_in_R": False,
        "physical_scalar_evaluated": False,
    }


def write_coupled_tensor_comparison(path: Path = OUTPUT) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema": "alternate-up-coupled-tensor-comparison-v1",
        "coefficient_field": "Q(omega)",
        "outer_parameter_basis": ["a0", "a1"],
        "presentations": [alternate_coupled_presentation_check(i) for i in range(2)],
        "actual_leibniz_checks": [alternate_coupled_leibniz_check(i) for i in range(2)],
        "derived_coupled_R_to_Q_tensor_identity": True,
        "full_carrier_scalar_pairing_evaluated": False,
        "complete_holomorphic_up_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "existing_quotient_cone": _verified_payload(QUOTIENT_CONE)[0],
            "actual_syzygy_comparison": _verified_payload(SYZYGY)[0],
        },
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)
    return payload


if __name__ == "__main__":
    record = write_coupled_tensor_comparison()
    print(f"artifact_digest: {record['artifact_digest']}")
