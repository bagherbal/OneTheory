"""Compose exact outer Čech--Koszul morphisms in the common Schoen cover.

Owns:
    Signed Alexander--Whitney composition of compatible full mixed-Hom
    cochains, retaining object and Koszul degrees and exact Laurent terms.

Depends on:
    The established sparse outer basis and the mixed constituent grading.

Must not:
    Infer an exterior-cone Higgs representative or a Yukawa coefficient from
    composition alone, or identify incompatible line and object frames.

Phase 0:
    Research-only composition needed for direct derived-Hom evaluation.
"""

from __future__ import annotations

from typing import cast

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    KOSZUL_DEGREES,
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
)

from .mixed_schoen_outer_transfer import (
    KOSZUL_SUBSETS,
    SUBSET_KOSZUL,
    MixedSchoenComplex,
    _simplex_cup,
)


def _cup_cells(
    left: OuterCechBasis, right: OuterCechBasis
) -> tuple[int, tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]] | None:
    """Cup three ordered cover factors with their tensor-product sign."""

    cells = tuple(
        _simplex_cup(source, target)
        for source, target in zip(left.cell, right.cell, strict=True)
    )
    if any(cell is None for cell in cells):
        return None
    left_degrees = tuple(len(simplex) - 1 for simplex in left.cell)
    right_degrees = tuple(len(simplex) - 1 for simplex in right.cell)
    crossings = sum(
        left_degrees[later] * right_degrees[earlier]
        for earlier in range(3)
        for later in range(earlier + 1, 3)
    )
    return (-1 if crossings % 2 else 1), cast(
        tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]], cells
    )


def compose_outer_cochains(
    left: SparseOuterCechCochain,
    right: SparseOuterCechCochain,
    components: dict[tuple[int, int, str], OuterCechComponent],
    *,
    left_middle: MixedSchoenComplex,
    right_middle: MixedSchoenComplex,
) -> SparseOuterCechCochain:
    """Return ``left ∘ right`` in declared object and line frames.

    The total order is object-Hom, hypersurface Koszul, then the three
    Čech factors. The Koszul sign below moves the right object map past
    the left Koszul and Čech factors, then moves the right Koszul form
    past the left Čech factors.
    """

    if left_middle is not right_middle:
        raise ValueError("outer composition needs one identical middle complex")
    terms: list[tuple[OuterCechBasis, Eisenstein]] = []
    for left_basis, left_coefficient in left.terms:
        left_component = left_basis.component
        left_subset = KOSZUL_SUBSETS[left_component.koszul_summand]
        for right_basis, right_coefficient in right.terms:
            right_component = right_basis.component
            if left_component.right_index != right_component.left_index:
                continue
            cup = _cup_cells(left_basis, right_basis)
            if cup is None:
                continue
            right_subset = KOSZUL_SUBSETS[right_component.koszul_summand]
            if set(left_subset).intersection(right_subset):
                continue
            raw_subset = (*left_subset, *right_subset)
            subset = tuple(sorted(raw_subset))
            key = (
                left_component.left_index,
                right_component.right_index,
                SUBSET_KOSZUL[subset],
            )
            target = components.get(key)
            if target is None:
                raise ValueError("outer composition has no target object component")
            expected_line = tuple(
                first + second
                for first, second in zip(
                    left_component.line_degree,
                    right_component.line_degree,
                    strict=True,
                )
            )
            expected_object = (
                left_component.object_degree + right_component.object_degree
            )
            if target.line_degree != expected_line or target.object_degree != expected_object:
                raise ValueError("outer composition crosses incompatible object frames")
            cover_sign, cell = cup
            koszul_inversions = sum(
                first > second for first in left_subset for second in right_subset
            )
            crossing_degree = (
                (KOSZUL_DEGREES[left_component.koszul_summand]
                 + left_basis.cech_degree) * right_component.object_degree
                + left_basis.cech_degree
                * KOSZUL_DEGREES[right_component.koszul_summand]
            )
            sign = -1 if (koszul_inversions + crossing_degree) % 2 else 1
            x_monomial = tuple(
                first + second
                for first, second in zip(
                    left_basis.x_monomial, right_basis.x_monomial, strict=True
                )
            )
            u_monomial = tuple(
                first + second
                for first, second in zip(
                    left_basis.u_monomial, right_basis.u_monomial, strict=True
                )
            )
            p_monomial = tuple(
                first + second
                for first, second in zip(
                    left_basis.p_monomial, right_basis.p_monomial, strict=True
                )
            )
            terms.append((
                OuterCechBasis(
                    target,
                    cast(tuple[int, int, int], x_monomial),
                    cast(tuple[int, int, int], u_monomial),
                    cast(tuple[int, int], p_monomial),
                    cell,
                ),
                left_coefficient * right_coefficient * sign * cover_sign,
            ))
    return SparseOuterCechCochain(tuple(terms))
