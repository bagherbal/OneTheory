"""Verify null Yoneda homotopies in their actual line subobject.

Owns:
    Full line differential identities for the two saved null primitives,
    line-cohomology indeterminacy, Hom(det F,K), and the remaining H2(K)
    matter-product ambiguity for the natural quotient.

Depends on:
    Actual null matter classes, pinned strict Higgs and Yoneda cochains,
    the Serre ideal quotient, and existing exact Schoen Hom machinery.

Must not:
    Infer a line boundary from an E-valued boundary, discard comparison
    homotopies, or assign a physical Yukawa from vanishing ambiguity groups.

Phase 0:
    Research-only structural inputs to the natural null-product comparison.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import cast

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import _reduced_basis

from .alternate_constituent_up_matter_representatives import OUTPUT as MATTER
from .alternate_up_first_order_scalar import alternate_null_matter
from .alternate_up_higgs_covector_comparison import QUOTIENT_LINE
from .alternate_up_higgs_hom_representative import FULL_OUTPUT as HIGGS
from .alternate_up_higgs_hom_representative import load_alternate_up_higgs_hom_full_cochain
from .alternate_up_higgs_quotient_cone import OUTPUT as QUOTIENT
from .alternate_up_higgs_quotient_cone import alternate_higgs_quotient_models
from .alternate_up_null_channel import OUTPUT as NULL_CHANNELS
from .alternate_up_null_channel import NullYonedaChannel, alternate_up_null_channels
from .mixed_constituent_schoen_arrows import MixedConstituentObject
from .mixed_schoen_common_dga import mixed_outer_cup
from .mixed_schoen_outer_actions import _basis_record, _MixedContraction
from .mixed_schoen_outer_transfer import (
    MixedSchoenUnit,
    mixed_schoen_unit,
    mixed_transferred_outer_hom,
)
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_null_line_homotopies.json"


def inverse_quotient_line() -> MixedSchoenUnit:
    """Declare B1 inverse using the already fixed quotient normalization."""

    degree = cast(tuple[int, int, int], tuple(-value for value in QUOTIENT_LINE))
    return MixedSchoenUnit(
        "B1 inverse", 0, degree, (MixedConstituentObject("B1 inverse", 0, degree),),
    )


@cache
def null_line_homotopies() -> tuple[NullYonedaChannel, NullYonedaChannel]:
    """Check the actual support and differential rather than assuming them."""

    _, pinned = _verified_payload(NULL_CHANNELS)
    channels = alternate_up_null_channels()
    if (
        pinned.get("schema") != "alternate-up-null-channel-v1"
        or [channel.as_record() for channel in channels] != pinned.get("null_channels")
    ):
        raise ValueError("the exact null Yoneda primitives differ from their pinned input")
    line = inverse_quotient_line()
    context = _MixedContraction(line, mixed_schoen_unit())
    h = load_alternate_up_higgs_hom_full_cochain()
    for channel, matter in zip(channels, alternate_null_matter(), strict=True):
        for cochain in (channel.null_evaluation, channel.primitive):
            if any(
                basis.component.left_index != 0 or basis.component.right_index != 0
                or context.components[(0, 0, basis.component.koszul_summand)] != basis.component
                for basis, _ in cochain.terms
            ):
                raise ValueError("a null Yoneda witness does not lie in the actual line subobject")
        if mixed_outer_cup(h, matter) != channel.null_evaluation:
            raise ValueError("the line null evaluation differs from the actual ordered Higgs cup")
        if context.differential(channel.primitive) != channel.null_evaluation:
            raise ValueError("the saved Yoneda primitive is not a full line primitive")
        if not context.differential(channel.null_evaluation).is_zero():
            raise ValueError("the null line evaluation is not a full cycle")
    return channels


def null_line_cohomology_dimensions() -> tuple[int, ...]:
    """Use the complete ambient support, not a selected-character zero."""

    context = _MixedContraction(inverse_quotient_line(), mixed_schoen_unit())
    dimensions = {
        degree: len(_reduced_basis(context.left_skeleton, context.right_skeleton, degree))
        for degree in range(-2, 6)
    }
    # One object and a length-two Koszul resolution exhaust this range.
    # With just one nonzero ambient degree, no spectral-sequence
    # differential can enter or leave it.
    if {degree for degree, dimension in dimensions.items() if dimension} != {2}:
        raise ValueError("the inverse quotient line no longer has single-degree ambient support")
    return tuple(dimensions[degree] for degree in range(4))


def quotient_map_indeterminacy() -> tuple[tuple[tuple[int, int], ...], int]:
    """Compute Hom(det F,K), not the unrelated matter-product H2 ambiguity."""

    second, quotient = alternate_higgs_quotient_models()
    signs = tuple(-1 if item.position % 2 else 1 for item in second.objects)
    if sum(signs) != 2:
        raise ValueError("the actual determinant endpoint is not from a rank-two constituent")
    degree = cast(tuple[int, int, int], tuple(sum(
        sign * item.line_degree[coordinate]
        for sign, item in zip(signs, second.objects, strict=True)
    ) for coordinate in range(3)))
    determinant = MixedSchoenUnit(
        "det F", 0, degree, (MixedConstituentObject("det F", 0, degree),),
    )
    context = _MixedContraction(quotient, determinant)
    ambient = tuple((degree, len(_reduced_basis(
        context.left_skeleton, context.right_skeleton, degree,
    ))) for degree in range(-3, 6))
    transferred = mixed_transferred_outer_hom(quotient, determinant)
    return ambient, transferred.cohomology_dimension(0)


def quotient_product_indeterminacy() -> tuple[tuple[tuple[int, int], ...], tuple[int, ...]]:
    """Compute the actual K cohomology without assigning a product lift.

    The degree-zero Hom group above controls fixed-endpoint sheaf maps.
    Differences of degree-two closed matter-product lifts instead live
    in H2(K); they cannot be discarded by the former vanishing statement.
    """

    _, quotient = alternate_higgs_quotient_models()
    unit = mixed_schoen_unit()
    context = _MixedContraction(quotient, unit)
    ambient = tuple((degree, len(_reduced_basis(
        context.left_skeleton, context.right_skeleton, degree,
    ))) for degree in range(-3, 6))
    transferred = mixed_transferred_outer_hom(quotient, unit)
    return ambient, tuple(transferred.cohomology_dimension(degree) for degree in range(4))


def write_null_line_homotopies(path: Path = OUTPUT) -> dict[str, object]:
    """Persist the actual short homotopies without a physical-product claim."""

    prerequisites = {
        name: _verified_payload(source)[0]
        for name, source in (
            ("null_channels", NULL_CHANNELS), ("strict_higgs", HIGGS),
            ("actual_matter", MATTER), ("natural_quotient", QUOTIENT),
        )
    }
    channels = null_line_homotopies()
    dimensions = null_line_cohomology_dimensions()
    ambient, hom_dimension = quotient_map_indeterminacy()
    product_ambient, product_dimensions = quotient_product_indeterminacy()
    if dimensions != (0, 0, 9, 0) or hom_dimension != 0 or product_dimensions != (0, 5, 5, 0):
        raise ValueError("the declared null-line indeterminacy groups changed")
    payload: dict[str, object] = {
        "schema": "alternate-up-null-line-homotopies-v1",
        "coefficient_field": "Q(omega)",
        "line_degree": list(inverse_quotient_line().twist),
        "line_h0_to_h3": list(dimensions),
        "hom_detF_to_K_ambient_space_dimensions": [list(item) for item in ambient],
        "hom_detF_to_K_dimension": hom_dimension,
        "K_ambient_space_dimensions": [list(item) for item in product_ambient],
        "K_h0_to_h3": list(product_dimensions),
        "remaining_matter_product_H2K_dimension": product_dimensions[2],
        "null_line_witnesses": [dict(
            channel.as_record(),
            primitive_has_only_line_support=True,
            full_line_primitive_identity_exact=True,
            ordered_higgs_null_matter_evaluation_exact=True,
            full_primitive_terms=[
                {"basis": _basis_record(basis), "coefficient": str(value)}
                for basis, value in channel.primitive.terms
            ],
        ) for channel in channels],
        "line_primitive_unique_modulo_boundaries": True,
        "identity_endpoint_extension_map_unique_if_it_exists": True,
        "natural_matter_product_comparison_certified": False,
        "complete_comparison_indeterminacy_eliminated": False,
        "physical_null_coefficients_computed": False,
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
    record = write_null_line_homotopies()
    print(f"artifact_digest: {record['artifact_digest']}")
