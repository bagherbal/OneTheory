"""Check all three ordered first-order terms in the alternate null channel.

Owns:
    Actual null matter combinations, their exact cone corrections, the
    two matter-leg contractions, and the reciprocal Higgs-leg contraction.

Depends on:
    The frozen alternate matter basis, global first quotient, signed
    two-slot action, checked exterior primitives, and full scalar trace.

Must not:
    Trace a nonclosed cochain, silently commute ordered cover factors,
    assign a full Yukawa matrix, or assert a derived tensor comparison.

Phase 0:
    Research-only closure screen for the complete first-order scalar.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
)
from research.experiments.computable_carrier.schoen_sparse_actions import schoen_sparse_deck_actions

from .alternate_constituent_hom_actions import _common_frame
from .alternate_constituent_up_matter_representatives import OUTPUT as UP_MATTER
from .alternate_constituent_up_matter_representatives import (
    _project,
    _strict,
    alternate_constituent_up_matter_representatives,
)
from .alternate_up_dual_higgs_inputs import _quotient, alternate_up_dual_higgs_inputs
from .alternate_up_exterior_higgs_action import (
    OUTPUT as EXTERIOR_WITNESSES,
)
from .alternate_up_exterior_higgs_action import (
    alternate_up_exterior_context,
    alternate_up_exterior_primitive,
)
from .alternate_up_higgs_covector_comparison import (
    QUOTIENT_LINE,
    alternate_outer_coefficient,
    alternate_up_higgs_covector_action,
    quotient_outer_exterior_action,
)
from .alternate_up_higgs_hom_representative import load_alternate_up_higgs_hom_full_cochain
from .alternate_up_mixed_scalar_trace import _scalar_context
from .alternate_up_null_channel import OUTPUT as NULL_CHANNELS
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
    _constituent,
    mixed_schoen_constituents,
)
from .mixed_schoen_chain_actions import _parse_eisenstein_text
from .mixed_schoen_common_dga import exact_mixed_primitive, mixed_outer_cup
from .mixed_schoen_exterior_square import resolution_vector_wedge
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction, _perturbed_projection
from .mixed_schoen_outer_transfer import (
    MixedSchoenUnit,
    mixed_schoen_unit,
    mixed_transferred_outer_hom,
)
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_first_order_scalar.json"
Character = tuple[int, int]


@cache
def alternate_null_matter() -> tuple[SparseOuterCechCochain, SparseOuterCechCochain]:
    """Use the declared determinant null combinations, not fitted directions."""

    _, record = _verified_payload(NULL_CHANNELS)
    if record.get("schema") != "alternate-up-null-channel-v1":
        raise ValueError("the determinant null-channel record changed")
    raw = record.get("null_channels")
    if not isinstance(raw, list) or len(raw) != 2:
        raise ValueError("both determinant null directions are required")
    actual_matter = alternate_constituent_up_matter_representatives()
    _, stored_matter = _verified_payload(UP_MATTER)
    if actual_matter.as_record() != stored_matter:
        raise ValueError("the actual matter cochains differ from their pinned artifact")
    classes = actual_matter.classes
    result = []
    for character, channel in zip(((0, 0), (1, 0)), raw, strict=True):
        selected = [item for item in classes if item.character == character]
        if (
            [item.seed_index for item in selected] != [0, 5]
            or channel.get("matter_character") != list(character)
            or channel.get("null_matter_combination") != "seed5 - ratio * seed0"
        ):
            raise ValueError("the exact null matter basis changed")
        ratio = _parse_eisenstein_text(channel["seed5_over_seed0"])
        result.append(selected[1].full_cochain + selected[0].full_cochain.scale(-ratio))
    return result[0], result[1]


def even_vector_line_product(
    line: SparseOuterCechCochain,
    vector: SparseOuterCechCochain,
    *,
    reverse: bool = False,
) -> SparseOuterCechCochain:
    """Tensor a B-valued cochain with an actual even F-vector in declared order.

    In the reverse order F is explicitly retargeted from B to B tensor F;
    its Hom grading and coefficients are unchanged by this common twist.
    In the forward order the B coefficient acts diagonally from F to
    B tensor F. Odd F objects are rejected, not silently assigned a sign.
    """

    if any(
        basis.component.left_index != 0
        or basis.component.right_index != 0
        or basis.component.object_degree != 0
        or basis.component.line_degree != QUOTIENT_LINE
        for basis, _ in line.terms
    ):
        raise ValueError("the ordered tensor product needs the actual quotient line")
    exterior, _ = alternate_up_exterior_context()
    if any(
        basis.component.right_index != 0
        or basis.component.left_index not in range(len(exterior.source_positions))
        or basis.component.object_degree != 0
        or exterior.source_positions[basis.component.left_index] != 0
        or basis.component.line_degree != exterior.source_lines[basis.component.left_index]
        for basis, _ in vector.terms
    ):
        raise ValueError("the ordered tensor product needs the actual even F support")
    if reverse:
        return mixed_outer_cup(vector, line)
    indices = sorted({basis.component.left_index for basis, _ in vector.terms})
    diagonal = SparseOuterCechCochain(tuple(
        (
            OuterCechBasis(
                OuterCechComponent(index, index, 0, QUOTIENT_LINE, basis.component.koszul_summand),
                basis.x_monomial, basis.u_monomial, basis.p_monomial, basis.cell,
            ), value,
        )
        for index in indices for basis, value in line.terms
    ))
    return mixed_outer_cup(diagonal, vector)


def null_matter_correction(
    matter: SparseOuterCechCochain,
    character: Character,
    extension: SparseOuterCechCochain,
) -> SparseOuterCechCochain:
    """Use the same linear solve and character average as the saved matter lifts."""

    first = mixed_schoen_constituents()[0]
    unit = mixed_schoen_unit()
    context = _MixedContraction(first, unit)
    product = mixed_outer_cup(extension, matter)
    if not context.differential(product).is_zero():
        raise ValueError("the actual outer/null-matter product is not closed")
    solution = exact_mixed_primitive(
        product, context, mixed_transferred_outer_hom(first, unit), 2
    )
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    frames = {
        name: (_common_frame(first, action), Matrix.identity(1, scalar_type=Eisenstein))
        for name, action in actions.items()
    }
    correction = _project(solution.primitive, character, context, actions, frames).scale(-1)
    if context.differential(correction) != product.scale(-1):
        raise ValueError("the exact null-matter cone correction identity failed")
    if not _strict(correction, character, context, actions, frames):
        raise ValueError("the exact null-matter cone correction lost its character")
    return correction


@cache
def alternate_up_ordered_tensor_difference(parameter_index: int) -> SparseOuterCechCochain:
    """Compare the two tensor evaluations before the Higgs annihilator.

    This is (q(e)bL) tensor bR + bL tensor (q(e)bR) minus the
    actual two-slot action on bL wedge bR. A zero scalar obtained after
    applying h must not conceal a nonzero intermediate comparison.
    """

    exterior, _ = alternate_up_exterior_context()
    second = _constituent(lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1,
    ), "I6-ray-0-1", 2, (1, -1, 0))
    b_line = MixedSchoenUnit(
        "B1", 0, QUOTIENT_LINE,
        (MixedConstituentObject("B1", 0, QUOTIENT_LINE),),
    )
    quotient = _quotient(
        alternate_outer_coefficient(parameter_index), _MixedContraction(b_line, second)
    )
    left, right = alternate_null_matter()
    wedge = resolution_vector_wedge(
        left, right, exterior, _MixedContraction(exterior, mixed_schoen_unit()), 1, 1,
    )
    quotient_left = mixed_outer_cup(quotient, left)
    quotient_right = mixed_outer_cup(quotient, right)
    separate_slots = even_vector_line_product(
        quotient_left, right
    ) + even_vector_line_product(quotient_right, left, reverse=True)
    simultaneous = mixed_outer_cup(quotient_outer_exterior_action(quotient, exterior), wedge)
    return separate_slots + simultaneous.scale(-1)


@cache
def alternate_up_ordered_tensor_defect(parameter_index: int) -> SparseOuterCechCochain:
    """Calculate the primitive-free scalar defect without assuming comparison."""

    h = load_alternate_up_higgs_hom_full_cochain()
    if any(basis.component.right_index == 0 for basis, _ in h.terms):
        raise ValueError("the Higgs no longer annihilates the constituent A target")
    return mixed_outer_cup(h, alternate_up_ordered_tensor_difference(parameter_index))


@dataclass(frozen=True, slots=True)
class OrderedFirstOrderScalar:
    """An explicit closure screen; a failed candidate carries no residue."""

    parameter_index: int
    wedge: SparseOuterCechCochain
    left_correction: SparseOuterCechCochain
    right_correction: SparseOuterCechCochain
    matter_term: SparseOuterCechCochain
    higgs_term: SparseOuterCechCochain
    scalar: SparseOuterCechCochain
    defect: SparseOuterCechCochain
    residue: Eisenstein | None
    projection_depth: int | None

    def __post_init__(self) -> None:
        if self.scalar != self.matter_term + self.higgs_term:
            raise ValueError("the ordered scalar does not contain the declared three terms")
        if self.defect.is_zero():
            if self.residue is None or self.projection_depth is None:
                raise ValueError("a closed ordered scalar needs its actual residue calculation")
        elif self.residue is not None or self.projection_depth is not None:
            raise ValueError("a nonclosed ordered scalar must not carry a residue")

    def as_record(self) -> dict[str, object]:
        """Record an ordered calculation without a full physical Higgs claim."""

        return {
            "parameter": f"a{self.parameter_index}",
            "null_wedge_term_count": len(self.wedge.terms),
            "null_wedge_digest": _cochain_digest((self.wedge,)),
            "left_matter_correction_term_count": len(self.left_correction.terms),
            "right_matter_correction_term_count": len(self.right_correction.terms),
            "combined_matter_leg_term_count": len(self.matter_term.terms),
            "combined_matter_leg_digest": _cochain_digest((self.matter_term,)),
            "higgs_leg_term_count": len(self.higgs_term.terms),
            "higgs_leg_digest": _cochain_digest((self.higgs_term,)),
            "scalar_term_count": len(self.scalar.terms),
            "scalar_digest": _cochain_digest((self.scalar,)),
            "scalar_defect_term_count": len(self.defect.terms),
            "scalar_defect_digest": _cochain_digest((self.defect,)),
            "ordered_scalar_closed_exact": self.defect.is_zero(),
            "ordered_cover_residue": None if self.residue is None else str(self.residue),
            "projection_depth": self.projection_depth,
            "physical_null_coefficient_assigned": False,
        }


@cache
def alternate_up_first_order_scalar(parameter_index: int) -> OrderedFirstOrderScalar:
    """Combine both matter legs and the checked positive exterior primitive.

    The mixed functional is h applied after the global E-to-B quotient.
    Its cone action is minus h wedge q(e), so the primitive enters with
    positive sign. All coefficient orders are retained literally.
    """

    action = alternate_up_higgs_covector_action(parameter_index)
    primitive = alternate_up_exterior_primitive(parameter_index)
    if primitive.product != action.scale(-1):
        raise ValueError("the chosen Higgs primitive has the wrong signed cone action")
    exterior, _ = alternate_up_exterior_context()
    unit = mixed_schoen_unit()
    vector_context = _MixedContraction(exterior, unit)
    left, right = alternate_null_matter()
    wedge = resolution_vector_wedge(left, right, exterior, vector_context, 1, 1)
    if wedge.is_zero() or not vector_context.differential(wedge).is_zero():
        raise ValueError("the actual null matter wedge is not a nonzero full cycle")
    extension = alternate_outer_coefficient(parameter_index)
    left_correction = null_matter_correction(left, (0, 0), extension)
    right_correction = null_matter_correction(right, (1, 0), extension)
    b_line = MixedSchoenUnit(
        "B1", 0, QUOTIENT_LINE,
        (MixedConstituentObject("B1", 0, QUOTIENT_LINE),),
    )
    quotient_context = _MixedContraction(b_line, unit)
    left_quotient = _quotient(left_correction, quotient_context)
    right_quotient = _quotient(right_correction, quotient_context)
    cross = even_vector_line_product(left_quotient, right) + even_vector_line_product(
        right_quotient, left, reverse=True
    ).scale(-1)
    matter_term = mixed_outer_cup(alternate_up_dual_higgs_inputs().higgs_covector, cross)
    higgs_term = mixed_outer_cup(primitive.primitive, wedge)
    scalar = matter_term + higgs_term
    if any(basis.total_degree != 3 for basis, _ in scalar.terms):
        raise ValueError("the ordered three-term scalar has an incompatible total degree")
    context = _scalar_context()
    defect = context.differential(scalar)
    if defect != alternate_up_ordered_tensor_defect(parameter_index):
        raise ValueError("the full scalar defect is not the actual ordered tensor Leibniz defect")
    residue, depth = None, None
    if defect.is_zero():
        coordinates, depth = _perturbed_projection(scalar, context, 3)
        if set(coordinates) - {0}:
            raise ValueError("the ordered scalar has an undeclared residue basis")
        residue = coordinates.get(0, Eisenstein(0))
    return OrderedFirstOrderScalar(
        parameter_index, wedge, left_correction, right_correction,
        matter_term, higgs_term, scalar, defect, residue, depth,
    )


def write_alternate_up_first_order_scalar(path: Path = OUTPUT) -> dict[str, object]:
    """Persist exact ordered screens, including any nonzero closure defects."""

    null_digest, _ = _verified_payload(NULL_CHANNELS)
    exterior_digest, exterior_record = _verified_payload(EXTERIOR_WITNESSES)
    records = []
    for index in range(2):
        calculation = alternate_up_first_order_scalar(index)
        records.append(calculation.as_record())
        actual = alternate_up_exterior_primitive(index).as_record()
        expected = cast(list[dict[str, object]], exterior_record["witnesses"])[index]
        if actual != expected:
            raise ValueError("the actual exterior primitive differs from its pinned witness")
    payload: dict[str, object] = {
        "schema": "alternate-up-first-order-scalar-screen-v1",
        "coefficient_field": "Q(omega)",
        "outer_parameter_basis": ["a0", "a1"],
        "scalar_order": "h cup (q(xL) tensor bR - bL tensor q(xR)) + k cup (bL wedge bR)",
        "signed_two_slot_cone_actions_exact": True,
        "higgs_primitive_sign": "positive, because the dual cone action is minus h wedge q(e)",
        "parameter_coefficients": records,
        "derived_tensor_comparison_certified": False,
        "physical_null_coefficients_computed": False,
        "rank_three_established": False,
        "complete_holomorphic_up_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "null_channels": null_digest, "exterior_primitives": exterior_digest,
        },
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    result = write_alternate_up_first_order_scalar()
    print(f"artifact_digest: {result['artifact_digest']}")
