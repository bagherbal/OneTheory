"""Compare the ordered exterior primitive with the actual two-slot cone action.

Owns:
    The quotient of the first constituent in the mixed Higgs functional,
    the two signed outer-extension slots, and their full Hom composition.

Depends on:
    The certified global Hilbert--Burch quotient, frozen alternate outer
    cochains, reciprocal Higgs covector, and full graded exterior resolution.

Must not:
    Identify an ordered cover formula with a physical Higgs without its
    derived tensor comparison, suppress a scalar defect, or infer rank three.

Phase 0:
    Research-only signed comparison for the complete first-order scalar.
"""

from __future__ import annotations

from functools import cache
from typing import cast

from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
)

from .alternate_constituent_outer_invariants import OUTPUT as INVARIANTS
from .alternate_up_dual_higgs_inputs import alternate_up_dual_higgs_inputs
from .alternate_up_exterior_higgs_action import (
    alternate_up_exterior_context,
    alternate_up_exterior_product,
)
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import _constituent, mixed_schoen_constituents
from .mixed_schoen_common_dga import mixed_outer_cup
from .mixed_schoen_exterior_square import MixedExteriorSquare
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_universal_cone import _representative, _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions

QUOTIENT_LINE = (-1, 1, 1)


def quotient_outer_exterior_action(
    quotient_extension: SparseOuterCechCochain,
    exterior: MixedExteriorSquare,
) -> SparseOuterCechCochain:
    """Apply a degree-one F-to-B map to both graded exterior slots.

    The target is B tensor F, with B written first. On an ordered pair
    (i,j), the first slot has coefficient e_i in target j; the second
    has coefficient -(-1)^(p_i p_j) e_j in target i. This includes
    moving the extension coefficient through the first internal vector.
    Odd diagonal contributions add, rather than being divided by two.
    """

    by_source: dict[int, list[tuple[OuterCechBasis, Eisenstein]]] = {}
    for basis, value in quotient_extension.terms:
        component = basis.component
        index = component.right_index
        if (
            component.left_index != 0
            or index not in range(len(exterior.source_positions))
            or basis.total_degree != 1
            or component.object_degree != -exterior.source_positions[index]
            or component.line_degree != tuple(
                a - b for a, b in zip(QUOTIENT_LINE, exterior.source_lines[index], strict=True)
            )
        ):
            raise ValueError("the two-slot cone action needs the actual F-to-B covector")
        by_source.setdefault(index, []).append((basis, value))
    result = []
    for source, (i, j) in enumerate(exterior.pairs):
        for target, index, sign in (
            (j, i, 1),
            (i, j, 1 if exterior.source_positions[i] * exterior.source_positions[j] % 2 else -1),
        ):
            for basis, value in by_source.get(index, ()):
                component = OuterCechComponent(
                    target, source,
                    exterior.source_positions[target] - exterior.objects[source].position,
                    cast(tuple[int, int, int], tuple(
                        a + b - c for a, b, c in zip(
                            QUOTIENT_LINE, exterior.source_lines[target],
                            exterior.objects[source].line_degree, strict=True,
                        )
                    )),
                    basis.component.koszul_summand,
                )
                result.append((OuterCechBasis(
                    component, basis.x_monomial, basis.u_monomial,
                    basis.p_monomial, basis.cell,
                ), value * sign))
    return SparseOuterCechCochain(tuple(result))


@cache
def alternate_up_higgs_covector_action(parameter_index: int) -> SparseOuterCechCochain:
    """Check the full action equals minus the independently formed wedge."""

    if parameter_index not in (0, 1):
        raise ValueError("the alternate extension parameter index is unavailable")
    exterior, context = alternate_up_exterior_context()
    inputs = alternate_up_dual_higgs_inputs()
    action = mixed_outer_cup(
        inputs.higgs_covector,
        quotient_outer_exterior_action(inputs.outer_covectors[parameter_index], exterior),
    )
    if action != alternate_up_exterior_product(parameter_index).scale(-1):
        raise ValueError("the full two-slot cone action disagrees with the ordered exterior sign")
    if not context.differential(action).is_zero():
        raise ValueError("the full two-slot Higgs action is not closed")
    return action


@cache
def alternate_outer_coefficient(parameter_index: int) -> SparseOuterCechCochain:
    """Load one declared universal coefficient, never an extension point."""

    if parameter_index not in (0, 1):
        raise ValueError("the alternate extension parameter index is unavailable")
    _, record = _verified_payload(INVARIANTS)
    if record.get("schema") != "alternate-constituent-outer-invariants-v1":
        raise ValueError("the alternate outer invariant basis changed")
    raw = record.get("strict_full_cech_representatives")
    if not isinstance(raw, list) or len(raw) != 2:
        raise ValueError("the two alternate outer coefficients are unavailable")
    cochain = _representative(raw[parameter_index])
    second = _constituent(lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1,
    ), "I6-ray-0-1", 2, (1, -1, 0))
    context = _MixedContraction(mixed_schoen_constituents()[0], second)
    if not cochain.terms or any(basis.total_degree != 1 for basis, _ in cochain.terms):
        raise ValueError("the actual outer coefficient has incompatible grading")
    if not context.differential(cochain).is_zero():
        raise ValueError("the actual outer coefficient is not a full cycle")
    return cochain
