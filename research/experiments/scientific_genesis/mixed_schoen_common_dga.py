"""Compose synchronized full-Schoen cochains and solve exact boundaries.

Owns:
    The signed Alexander--Whitney and Koszul composition of mixed outer-Hom
    cochains, perturbed contraction homotopies, and deterministic primitives.

Depends on:
    The synchronized mixed-complex grading, exact sparse Cech contractions, and
    transferred differentials over the Eisenstein field.

Must not:
    Assign physical sectors, choose carrier parameters, normalize a trace, or
    infer a Yukawa value from cohomology dimensions.

Phase 0:
    Research-only common-DGA operations for the frozen Schoen calculation.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import cache
from typing import cast

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    KOSZUL_DEGREES,
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
    _homotopy,
    _reduced_basis,
)
from research.experiments.computable_carrier.schoen_sparse_outer import SparseMap

from .mixed_schoen_outer_actions import (
    _MixedContraction,
    _perturbed_inclusion,
    _perturbed_projection,
    _reduced_cochain,
)
from .mixed_schoen_outer_transfer import (
    KOSZUL_SUBSETS,
    SUBSET_KOSZUL,
    MixedTransferredOuterHom,
    _cell_cup,
)

Cell = tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]


def _koszul_cup(left: str, right: str) -> tuple[int, str] | None:
    """Exterior-multiply two ordered Schoen equation subsets."""

    left_subset = KOSZUL_SUBSETS[left]
    right_subset = KOSZUL_SUBSETS[right]
    if set(left_subset) & set(right_subset):
        return None
    raw = (*left_subset, *right_subset)
    inversions = sum(
        raw[first] > raw[second]
        for first in range(len(raw))
        for second in range(first + 1, len(raw))
    )
    return (-1 if inversions % 2 else 1), SUBSET_KOSZUL[tuple(sorted(raw))]


def _sum_tuple(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    """Add two fixed-length exponent tuples."""

    return tuple(
        first + second for first, second in zip(left, right, strict=True)
    )


def mixed_outer_cup(
    left: SparseOuterCechCochain,
    right: SparseOuterCechCochain,
) -> SparseOuterCechCochain:
    """Compose ``left`` after ``right`` in the synchronized full complex."""

    right_by_object: dict[
        int,
        list[tuple[OuterCechBasis, Eisenstein]],
    ] = defaultdict(list)
    for basis, coefficient in right.terms:
        right_by_object[basis.component.left_index].append((basis, coefficient))

    @cache
    def compatible(
        left_component: OuterCechComponent,
        left_cell: Cell,
        right_component: OuterCechComponent,
        right_cell: Cell,
    ) -> tuple[int, OuterCechComponent, Cell] | None:
        """Reuse grading and cover checks, never coefficients or monomials."""

        cell_product = _cell_cup(left_cell, right_cell, "left")
        koszul_product = _koszul_cup(
            left_component.koszul_summand,
            right_component.koszul_summand,
        )
        if cell_product is None or koszul_product is None:
            return None
        cell_sign, target_cell = cell_product
        koszul_sign, target_koszul = koszul_product
        crossing_degree = (
            KOSZUL_DEGREES[left_component.koszul_summand] * right_component.object_degree
            + sum(len(simplex) - 1 for simplex in left_cell) * right_component.structural_degree
        )
        sign = cell_sign * koszul_sign
        if crossing_degree % 2:
            sign *= -1
        target_component = OuterCechComponent(
            left_component.left_index,
            right_component.right_index,
            left_component.object_degree + right_component.object_degree,
            cast(tuple[int, int, int], _sum_tuple(
                left_component.line_degree, right_component.line_degree,
            )),
            target_koszul,
        )
        return sign, target_component, target_cell

    result: dict[OuterCechBasis, Eisenstein] = {}
    zero = Eisenstein(0)
    for left_basis, left_coefficient in left.terms:
        left_component = left_basis.component
        for right_basis, right_coefficient in right_by_object.get(
            left_component.right_index,
            (),
        ):
            right_component = right_basis.component
            target = compatible(
                left_component, left_basis.cell, right_component, right_basis.cell,
            )
            if target is None:
                continue
            sign, target_component, target_cell = target
            basis = OuterCechBasis(
                target_component,
                cast(tuple[int, int, int], _sum_tuple(
                    left_basis.x_monomial, right_basis.x_monomial,
                )),
                cast(tuple[int, int, int], _sum_tuple(
                    left_basis.u_monomial, right_basis.u_monomial,
                )),
                cast(tuple[int, int], _sum_tuple(
                    left_basis.p_monomial, right_basis.p_monomial,
                )),
                target_cell,
            )
            result[basis] = result.get(basis, zero) + (
                left_coefficient * right_coefficient * sign
            )
    return SparseOuterCechCochain(tuple(
        (basis, value) for basis, value in result.items() if not value.is_zero()
    ))


def mixed_outer_cup_coefficient(
    left: SparseOuterCechCochain,
    right: SparseOuterCechCochain,
    target: OuterCechBasis,
) -> Eisenstein:
    """Evaluate one exact cup coefficient by inverse monomial lookup.

    The target's ordered cell determines the right suffix from each left
    prefix. Its Koszul subset, homogeneous degrees, and exponents likewise
    determine at most one right basis term. This uses the same declared
    cup signs but a different convolution algorithm. It does not trace a
    noncycle, assert closure, or supply a missing physical input.
    """

    right_values = dict(right.terms)
    target_component = target.component
    target_subset = KOSZUL_SUBSETS[target_component.koszul_summand]

    @cache
    def required_right(
        left_component: OuterCechComponent, left_cell: Cell,
    ) -> tuple[OuterCechComponent, Cell, int] | None:
        if left_component.left_index != target_component.left_index:
            return None
        left_subset = KOSZUL_SUBSETS[left_component.koszul_summand]
        if not set(left_subset).issubset(target_subset):
            return None
        if any(
            simplex != full[:len(simplex)]
            for simplex, full in zip(left_cell, target.cell, strict=True)
        ):
            return None
        right_cell = cast(Cell, tuple(
            full[len(simplex) - 1:]
            for simplex, full in zip(left_cell, target.cell, strict=True)
        ))
        right_koszul = SUBSET_KOSZUL[tuple(
            item for item in target_subset if item not in left_subset
        )]
        cell = _cell_cup(left_cell, right_cell, "left")
        koszul = _koszul_cup(left_component.koszul_summand, right_koszul)
        if cell is None or koszul is None or cell[1] != target.cell:
            return None
        component = OuterCechComponent(
            left_component.right_index, target_component.right_index,
            target_component.object_degree - left_component.object_degree,
            cast(tuple[int, int, int], tuple(
                value - original for value, original in zip(
                    target_component.line_degree, left_component.line_degree, strict=True,
                )
            )),
            right_koszul,
        )
        crossing = (
            KOSZUL_DEGREES[left_component.koszul_summand] * component.object_degree
            + sum(len(simplex) - 1 for simplex in left_cell) * component.structural_degree
        )
        sign = cell[0] * koszul[0] * (-1 if crossing % 2 else 1)
        return component, right_cell, sign

    result = Eisenstein(0)
    for basis, coefficient in left.terms:
        required = required_right(basis.component, basis.cell)
        if required is None:
            continue
        component, cell, sign = required
        exponents = tuple(tuple(
            value - original for value, original in zip(target_values, left_values, strict=True)
        ) for target_values, left_values in zip(
            (target.x_monomial, target.u_monomial, target.p_monomial),
            (basis.x_monomial, basis.u_monomial, basis.p_monomial), strict=True,
        ))
        if any(
            any(index not in simplex for index, value in enumerate(values) if value < 0)
            for values, simplex in zip(exponents, cell, strict=True)
        ):
            # The inverse monomial is not regular on the required suffix,
            # so it cannot occur in the normalized right cochain.
            continue
        right_basis = OuterCechBasis(
            component,
            cast(tuple[int, int, int], exponents[0]),
            cast(tuple[int, int, int], exponents[1]), cast(tuple[int, int], exponents[2]),
            cell,
        )
        value = right_values.get(right_basis)
        if value is not None:
            result += coefficient * value * sign
    return result


def perturbed_homotopy(
    cochain: SparseOuterCechCochain,
    contraction: _MixedContraction,
) -> tuple[SparseOuterCechCochain, int]:
    """Apply the finite ``(1 + h Delta)^-1 h`` contraction series."""

    result = SparseOuterCechCochain()
    current = _homotopy(cochain)
    depth = 0
    while not current.is_zero():
        result = result + current
        current = _homotopy(contraction.perturbation(current)).scale(-1)
        depth += 1
        if depth > 16:
            raise ValueError("mixed perturbed homotopy did not terminate")
    return result, depth


def _columns(map_: SparseMap) -> tuple[dict[int, Eisenstein], ...]:
    """Return sparse columns of one exact map."""

    columns: list[dict[int, Eisenstein]] = [dict() for _ in range(map_.domain.dimension)]
    for row_index, row in enumerate(map_.rows):
        for column, value in row:
            columns[column][row_index] = value
    return tuple(columns)


def _sparse_preimage(
    map_: SparseMap,
    target: dict[int, Eisenstein],
) -> dict[int, Eisenstein]:
    """Return one deterministic exact preimage of a vector in the map image."""

    pivots: dict[
        int,
        tuple[dict[int, Eisenstein], dict[int, Eisenstein]],
    ] = {}
    for column_index, column in enumerate(_columns(map_)):
        vector = dict(column)
        source = {column_index: Eisenstein(1)}
        while vector:
            pivot = min(vector)
            coefficient = vector[pivot]
            existing = pivots.get(pivot)
            if existing is None:
                inverse = Eisenstein(1) / coefficient
                pivots[pivot] = (
                    {row: value * inverse for row, value in vector.items()},
                    {index: value * inverse for index, value in source.items()},
                )
                break
            pivot_vector, pivot_source = existing
            for row, value in pivot_vector.items():
                updated = vector.get(row, Eisenstein(0)) - coefficient * value
                if updated.is_zero():
                    vector.pop(row, None)
                else:
                    vector[row] = updated
            for index, value in pivot_source.items():
                updated = source.get(index, Eisenstein(0)) - coefficient * value
                if updated.is_zero():
                    source.pop(index, None)
                else:
                    source[index] = updated
    vector = dict(target)
    result: dict[int, Eisenstein] = {}
    while vector:
        pivot = min(vector)
        coefficient = vector[pivot]
        existing = pivots.get(pivot)
        if existing is None:
            raise ValueError("declared cocycle is not a transferred boundary")
        pivot_vector, pivot_source = existing
        for row, value in pivot_vector.items():
            updated = vector.get(row, Eisenstein(0)) - coefficient * value
            if updated.is_zero():
                vector.pop(row, None)
            else:
                vector[row] = updated
        for index, value in pivot_source.items():
            updated = result.get(index, Eisenstein(0)) + coefficient * value
            if updated.is_zero():
                result.pop(index, None)
            else:
                result[index] = updated
    return result


@dataclass(frozen=True, slots=True)
class ExactMixedPrimitive:
    """One certified primitive of a full synchronized cocycle."""

    cocycle: SparseOuterCechCochain
    primitive: SparseOuterCechCochain
    projection_depth: int
    inclusion_depth: int
    homotopy_depth: int
    exact: bool


def exact_mixed_primitive(
    cocycle: SparseOuterCechCochain,
    contraction: _MixedContraction,
    transferred: MixedTransferredOuterHom,
    degree: int,
) -> ExactMixedPrimitive:
    """Solve ``D primitive = cocycle`` through the exact mixed contraction."""

    if any(basis.total_degree != degree for basis, _coefficient in cocycle.terms):
        raise ValueError("mixed primitive input occupies the wrong total degree")
    projected, projection_depth = _perturbed_projection(
        cocycle,
        contraction,
        degree,
    )
    incoming = dict(transferred.differentials)[degree - 1]
    source_coordinates = _sparse_preimage(incoming, projected)
    source_entries = _reduced_basis(
        contraction.left_skeleton,
        contraction.right_skeleton,
        degree - 1,
    )
    lifted, inclusion_depth = _perturbed_inclusion(
        _reduced_cochain(source_entries, source_coordinates),
        contraction,
    )
    residual = cocycle + contraction.differential(lifted).scale(-1)
    correction, homotopy_depth = perturbed_homotopy(residual, contraction)
    primitive = lifted + correction
    exact = contraction.differential(primitive) == cocycle
    if not exact:
        raise ValueError("mixed contraction failed to recover an exact primitive")
    return ExactMixedPrimitive(
        cocycle,
        primitive,
        projection_depth,
        inclusion_depth,
        homotopy_depth,
        exact,
    )


__all__ = [
    "ExactMixedPrimitive",
    "exact_mixed_primitive",
    "mixed_outer_cup",
    "perturbed_homotopy",
]
