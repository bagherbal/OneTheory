"""Check the actual ordered exterior products of alternate Higgs covectors.

Owns:
    The frozen F exterior resolution, full signed reciprocal products,
    explicit differential-square witnesses, and exact primitive checks.

Depends on:
    The certified alternate covectors, graded exterior monomials, and
    existing full-cover inclusion, projection, and homotopy machinery.

Must not:
    Infer a complete exterior-cone Higgs representative, a null-to-null
    scalar, rank three, quotient trace normalization, or a physical Yukawa.

Phase 0:
    Research-only exterior calculation on the frozen two-parameter family.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer import schoen_serre_outer_hom
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
    _include,
    _projection_index,
    _reduced_basis,
)
from research.experiments.computable_carrier.schoen_sparse_outer import SparseMap, _freeze_rows

from .alternate_up_dual_higgs_inputs import OUTPUT as INPUTS
from .alternate_up_dual_higgs_inputs import alternate_up_dual_higgs_inputs
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import _constituent
from .mixed_schoen_common_dga import _sparse_preimage, perturbed_homotopy
from .mixed_schoen_exterior_square import (
    MixedExteriorSquare,
    mixed_exterior_square,
    reciprocal_covector_wedge,
)
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import (
    _MixedContraction,
    _perturbed_inclusion,
    _perturbed_projection,
    _reduced_cochain,
)
from .mixed_schoen_outer_transfer import mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_exterior_higgs_action.json"


@cache
def alternate_up_exterior_context() -> tuple[MixedExteriorSquare, _MixedContraction]:
    """Use only the frozen alternate F, with its single even A target."""

    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    second = _constituent(ray, "I6-ray-0-1", 2, (1, -1, 0))
    if (
        second.objects[0].position != 0
        or any(term.target != 0 for term in second.extension_terms)
        or not second.full.full_closed
    ):
        raise ValueError("the rank-one A-supported curvature argument changed")
    exterior = mixed_exterior_square(second)
    return exterior, _MixedContraction(mixed_schoen_unit(), exterior)


@cache
def exterior_square_witness_count() -> int:
    """Check one regular local generator in every object/Koszul component."""

    exterior, context = alternate_up_exterior_context()
    count = 0
    for index in range(len(exterior.objects)):
        for koszul in ("k0", "k1_x", "k1_u", "k2"):
            component = context.components[(0, index, koszul)]
            x, u, p = component.ambient_degree
            basis = OuterCechBasis(
                component, (x, 0, 0), (u, 0, 0), (p, 0), ((0,), (0,), (0,))
            )
            cochain = SparseOuterCechCochain(((basis, Eisenstein(1)),))
            if not context.differential(context.differential(cochain)).is_zero():
                raise ValueError("an actual exterior differential-square witness failed")
            count += 1
    return count


@cache
def alternate_up_exterior_product(parameter_index: int) -> SparseOuterCechCochain:
    """Require full closure, not merely the expected determinant-line degree."""

    if parameter_index not in (0, 1):
        raise ValueError("the alternate extension parameter index is unavailable")
    exterior, context = alternate_up_exterior_context()
    inputs = alternate_up_dual_higgs_inputs()
    if any(basis.component.right_index == 0 for basis, _ in inputs.higgs_covector.terms):
        raise ValueError("the strict Higgs no longer annihilates A")
    product = reciprocal_covector_wedge(
        inputs.higgs_covector, inputs.outer_covectors[parameter_index],
        exterior, context, 1, 1,
    )
    if product.is_zero() or not context.differential(product).is_zero():
        raise ValueError("the actual ordered exterior product is not a nonzero full cycle")
    return product


@cache
def _incoming_candidate() -> tuple[SparseMap, int]:
    """Use the compact backbone plus actual transfer of A-supported columns.

    This matrix is a preimage search aid, not a certificate of the full
    transferred operator. Every proposed primitive is independently
    checked in the full differential before it can be returned.
    """

    exterior, context = alternate_up_exterior_context()
    backbone = dict(schoen_serre_outer_hom(
        context.left_skeleton, context.right_skeleton
    ).total_differentials)[1]
    rows = [dict(row) for row in backbone.rows]
    sources = _reduced_basis(context.left_skeleton, context.right_skeleton, 1)
    targets = _reduced_basis(context.left_skeleton, context.right_skeleton, 2)
    indices = {
        (entry.component, entry.x_monomial, entry.u_monomial, entry.p_monomial): entry.index
        for entry in targets
    }
    count = 0
    for source in sources:
        if 0 not in exterior.pairs[source.component.right_index]:
            continue
        for row in rows:
            row.pop(source.index, None)
        lifted, _ = _perturbed_inclusion(_include(source), context)
        for basis, coefficient in context.differential(lifted).terms:
            target = _projection_index(basis, indices)
            if target is not None:
                rows[target][source.index] = (
                    rows[target].get(source.index, Eisenstein(0)) + coefficient
                )
        count += 1
    return SparseMap(backbone.domain, backbone.codomain, _freeze_rows(rows)), count


@dataclass(frozen=True, slots=True)
class ExteriorPrimitive:
    """An independently checked full identity D primitive = product."""

    parameter_index: int
    product: SparseOuterCechCochain
    primitive: SparseOuterCechCochain
    projection_depth: int
    inclusion_depth: int
    homotopy_depth: int
    reduced_preimage_support: int
    directly_transferred_candidate_columns: int

    def as_record(self) -> dict[str, object]:
        """State the precise identity, without assigning a matrix coefficient."""

        return {
            "parameter": f"a{self.parameter_index}",
            "product_term_count": len(self.product.terms),
            "product_digest": _cochain_digest((self.product,)),
            "full_product_cycle_exact": True,
            "primitive_term_count": len(self.primitive.terms),
            "primitive_digest": _cochain_digest((self.primitive,)),
            "full_primitive_identity_exact": True,
            "primitive_sign_convention": "D primitive = ordered h wedge q(e)",
            "projection_depth": self.projection_depth,
            "inclusion_depth": self.inclusion_depth,
            "homotopy_depth": self.homotopy_depth,
            "reduced_preimage_support": self.reduced_preimage_support,
            "directly_transferred_candidate_columns": self.directly_transferred_candidate_columns,
            "candidate_operator_globally_certified": False,
        }


@cache
def alternate_up_exterior_primitive(parameter_index: int) -> ExteriorPrimitive:
    """Solve only the needed products, then verify each full identity."""

    product = alternate_up_exterior_product(parameter_index)
    return exact_exterior_primitive(parameter_index, product)


def exact_exterior_primitive(
    parameter_index: int, product: SparseOuterCechCochain,
) -> ExteriorPrimitive:
    """Reuse the fixed exterior preimage engine for an explicitly supplied product.

    No sector, covector, or scalar is inferred from the parameter index. The
    compact candidate operator is only a search aid; the original full
    differential must verify the returned primitive exactly.
    """

    if (not isinstance(parameter_index, int) or isinstance(parameter_index, bool)
        or parameter_index not in (0, 1)):
        raise ValueError("the alternate extension parameter index is unavailable")
    _, context = alternate_up_exterior_context()
    if (product.is_zero() or any(basis.total_degree != 2 for basis, _ in product.terms)
        or not context.differential(product).is_zero()):
        raise ValueError("the declared exterior product must be a nonzero full degree-two cycle")
    projected, projection_depth = _perturbed_projection(product, context, 2)
    candidate, count = _incoming_candidate()
    source_coordinates = _sparse_preimage(candidate, projected)
    source_entries = _reduced_basis(context.left_skeleton, context.right_skeleton, 1)
    lifted, inclusion_depth = _perturbed_inclusion(
        _reduced_cochain(source_entries, source_coordinates), context
    )
    residual = product + context.differential(lifted).scale(-1)
    correction, homotopy_depth = perturbed_homotopy(residual, context)
    primitive = lifted + correction
    if context.differential(primitive) != product:
        raise ValueError("the proposed exterior primitive failed its full identity")
    return ExteriorPrimitive(
        parameter_index, product, primitive, projection_depth,
        inclusion_depth, homotopy_depth, len(source_coordinates), count,
    )


def write_alternate_up_exterior_higgs_action(path: Path = OUTPUT) -> dict[str, object]:
    """Persist only identities reconstructed and checked from the actual inputs."""

    input_digest, input_record = _verified_payload(INPUTS)
    if input_record.get("schema") != "alternate-up-dual-higgs-inputs-v1":
        raise ValueError("the reciprocal covector prerequisites changed")
    if input_record != alternate_up_dual_higgs_inputs().as_record():
        raise ValueError("the actual reciprocal covectors differ from their pinned artifact")
    exterior, _ = alternate_up_exterior_context()
    witnesses = tuple(alternate_up_exterior_primitive(index) for index in range(2))
    payload: dict[str, object] = {
        "schema": "alternate-up-exterior-higgs-action-v1",
        "coefficient_field": "Q(omega)",
        "outer_parameter_basis": ["a0", "a1"],
        "ordered_product": "h wedge q(e)",
        "exterior_object_count": len(exterior.objects),
        "exterior_resolution_arrow_count": len(exterior.resolution_arrows),
        "exterior_extension_term_count": len(exterior.extension_terms),
        "even_even_object_count": sum(item.position == 0 for item in exterior.objects),
        "even_odd_object_count": sum(item.position == -1 for item in exterior.objects),
        "odd_odd_object_count": sum(item.position == -2 for item in exterior.objects),
        "odd_square_convention": "ordinary exterior monomials, not divided powers",
        "full_differential_square_witness_count": exterior_square_witness_count(),
        "determinant_target_degree": [-degree for degree in exterior.twist],
        "witnesses": [item.as_record() for item in witnesses],
        "prerequisite_artifact_digests": {"reciprocal_covectors": input_digest},
        "minor_inversion_used": False,
        "complete_exterior_cone_higgs_cocycle_constructed": False,
        "null_to_null_coefficients_computed": False,
        "rank_three_established": False,
        "complete_holomorphic_up_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "next_required_object": (
            "identify the ordered primitive with the signed full Higgs-cone "
            "correction and combine all three first-order scalar terms"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    result = write_alternate_up_exterior_higgs_action()
    print(f"artifact_digest: {result['artifact_digest']}")
