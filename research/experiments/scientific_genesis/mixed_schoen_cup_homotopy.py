"""Homotope coefficient cup orders on the declared product cover.

Owns:
    The signed diagonal homotopy on ordered P2/P2/P1 cells and its
    degree-minus-one operation on exact scalar Koszul cochains.

Depends on:
    Existing ordered Alexander--Whitney cells, Koszul coefficient products,
    Laurent regularity, and exact sparse cochains.

Must not:
    Commute matrix factors, infer a twisted exterior product from a scalar
    identity, or use a homotopy to choose a physical coupling.

Phase 0:
    Research-only cover coherence for the demonstrated raw-cup deficiency.
"""

from __future__ import annotations

from functools import cache
from typing import cast

from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
)

from .mixed_constituent_schoen_arrows import Cell
from .mixed_schoen_common_dga import _koszul_cup, _sum_tuple
from .mixed_schoen_outer_transfer import _simplex_cup


def _local_homotopy_sign(
    left: tuple[int, ...], right: tuple[int, ...], target: tuple[int, ...],
) -> int:
    """Read the explicit local diagonal homotopy, not a fitted sign table.

    H[i,j]=-[i,j] tensor [i,j]. For a triangle,
    H[i,j,k]=[i,j,k] tensor ([i,j]+[j,k])
              -[i,k] tensor [i,j,k].
    These follow from contraction to the first ordered vertex and satisfy
    boundary H + H boundary = AW - flip AW.
    """

    if len(target) == 2 and left == right == target:
        return -1
    if len(target) == 3:
        if left == target and right in (target[:2], target[1:]):
            return 1
        if left == (target[0], target[2]) and right == target:
            return -1
    return 0


@cache
def cell_cup_homotopy(left: Cell, right: Cell) -> tuple[int, Cell] | None:
    """Return the degree-minus-one coefficient kernel in the fixed ordering.

    On product chains the homotopy is Hx tensor AWu tensor AWp,
    plus flip AWx tensor Hu tensor AWp, plus flip AWx tensor flip
    AWu tensor Hp. Retain both the tensor-operator and output-braiding
    signs. This is not a strict commutativity assertion.
    """

    for cell in (left, right):
        if len(cell) != 3 or any(
            not simplex or tuple(sorted(set(simplex))) != simplex
            or any(vertex not in range(size) for vertex in simplex)
            for simplex, size in zip(cell, (3, 3, 2), strict=True)
        ):
            raise ValueError("the cup homotopy needs ordered cells of the declared cover")
    target = cast(Cell, tuple(tuple(sorted(set(a) | set(b))) for a, b in zip(
        left, right, strict=True,
    )))
    a_degrees = tuple(len(simplex) - 1 for simplex in left)
    b_degrees = tuple(len(simplex) - 1 for simplex in right)
    if sum(len(simplex) - 1 for simplex in target) != sum(a_degrees) + sum(b_degrees) - 1:
        return None
    braiding = sum(b_degrees[i] * a_degrees[j] for i in range(3) for j in range(i + 1, 3))
    result = 0
    for factor in range(3):
        local = _local_homotopy_sign(left[factor], right[factor], target[factor])
        if not local or any(
            _simplex_cup(right[i], left[i]) != target[i] for i in range(factor)
        ) or any(
            _simplex_cup(left[i], right[i]) != target[i] for i in range(factor + 1, 3)
        ):
            continue
        preceding = sum(len(target[i]) - 1 for i in range(factor))
        flips = sum(a_degrees[i] * b_degrees[i] for i in range(factor))
        result += local * (-1 if (preceding + flips + braiding) % 2 else 1)
    return None if not result else (result, target)


def mixed_scalar_cup_homotopy(
    left: SparseOuterCechCochain, right: SparseOuterCechCochain,
) -> SparseOuterCechCochain:
    """Homotope exact scalar coefficient products, including Koszul signs.

    For homogeneous scalar inputs, dH(a,b)+H(da,b)+(-1)^|a|H(a,db)
    equals a cup b - (-1)^(|a||b|) b cup a. The differential may
    include the ambient Koszul equations, but not a matrix twist.
    Scalar line degrees may be nonzero; no trace or normalization is used.
    """

    if any(
        basis.component.left_index != 0 or basis.component.right_index != 0
        or basis.component.object_degree != 0
        for cochain in (left, right) for basis, _ in cochain.terms
    ):
        raise ValueError("the scalar cup homotopy cannot commute matrix or shifted-object factors")
    result = []
    for a, a_value in left.terms:
        for b, b_value in right.terms:
            cell = cell_cup_homotopy(a.cell, b.cell)
            koszul = _koszul_cup(a.component.koszul_summand, b.component.koszul_summand)
            if cell is None or koszul is None:
                continue
            cell_sign, target_cell = cell
            koszul_sign, target_koszul = koszul
            # Extending the Cech homotopy to the structurally signed
            # total differential adds the total structural-degree sign.
            crossing = (
                a.component.structural_degree + b.component.structural_degree
                + a.cech_degree * b.component.structural_degree
            )
            sign = cell_sign * koszul_sign * (-1 if crossing % 2 else 1)
            component = OuterCechComponent(
                0, 0, 0,
                cast(tuple[int, int, int], _sum_tuple(
                    a.component.line_degree, b.component.line_degree,
                )),
                target_koszul,
            )
            result.append((OuterCechBasis(
                component,
                cast(tuple[int, int, int], _sum_tuple(a.x_monomial, b.x_monomial)),
                cast(tuple[int, int, int], _sum_tuple(a.u_monomial, b.u_monomial)),
                cast(tuple[int, int], _sum_tuple(a.p_monomial, b.p_monomial)), target_cell,
            ), a_value * b_value * sign))
    return SparseOuterCechCochain(tuple(result))
