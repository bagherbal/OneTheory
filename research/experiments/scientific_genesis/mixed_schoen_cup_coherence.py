"""Fill the first-slot product defect of the cover diagonal homotopy.

Owns:
    A deterministic degree-two chain filler and its degree-minus-two
    scalar Koszul operation for coupled triangular tensor comparisons.

Depends on:
    The fixed ordered cover, Alexander--Whitney cuts, the verified
    diagonal homotopy, and contraction to the first ordered vertex.

Must not:
    Replace the failed strict Hirsch rule by an assertion, commute
    matrix factors, or identify a physical Yukawa from scalar coherence.

Phase 0:
    Research-only higher coefficient coherence with exact chain witnesses.
"""

from __future__ import annotations

from collections import Counter
from functools import cache
from itertools import combinations, product
from typing import cast

from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
)

from .mixed_constituent_schoen_arrows import Cell
from .mixed_schoen_common_dga import _koszul_cup, _sum_tuple
from .mixed_schoen_cup_homotopy import cell_cup_homotopy

type TripleCell = tuple[Cell, Cell, Cell]


def _degree(cell: Cell) -> int:
    return sum(len(s) - 1 for s in cell)


@cache
def cell_boundary(cell: Cell) -> tuple[tuple[Cell, int], ...]:
    """The signed product-chain boundary, with no cochain machinery."""

    result = []
    prefix = 0
    for factor, simplex in enumerate(cell):
        if len(simplex) > 1:
            for index in range(len(simplex)):
                target = list(cell)
                target[factor] = simplex[:index] + simplex[index + 1:]
                result.append((cast(Cell, tuple(target)), -1 if (prefix + index) % 2 else 1))
        prefix += len(simplex) - 1
    return tuple(result)


@cache
def cell_diagonal(cell: Cell) -> tuple[tuple[tuple[Cell, Cell], int], ...]:
    """Enumerate actual ordered cuts and their output-braiding signs."""

    result = []
    for cuts in product(*(range(len(s)) for s in cell)):
        left = cast(Cell, tuple(s[:i + 1] for s, i in zip(cell, cuts, strict=True)))
        right = cast(Cell, tuple(s[i:] for s, i in zip(cell, cuts, strict=True)))
        sign = sum((len(right[i]) - 1) * (len(left[j]) - 1)
                   for i in range(3) for j in range(i + 1, 3))
        result.append(((left, right), -1 if sign % 2 else 1))
    return tuple(result)


@cache
def cell_diagonal_homotopy(cell: Cell) -> tuple[tuple[tuple[Cell, Cell], int], ...]:
    """Read the established kernel on all subcells of this one carrier."""

    subcells = tuple(cast(Cell, parts) for parts in product(*(tuple(
        face for n in range(1, len(s) + 1) for face in combinations(s, n)
    ) for s in cell)))
    result = []
    for first, second in product(subcells, repeat=2):
        entry = cell_cup_homotopy(first, second)
        if entry is not None and entry[1] == cell:
            result.append(((first, second), entry[0]))
    return tuple(result)


@cache
def cell_hirsch_defect(cell: Cell) -> tuple[tuple[TripleCell, int], ...]:
    """J=(Delta tensor id)H-(id tensor H)Delta-flip23(H tensor id)Delta."""

    result: Counter[TripleCell] = Counter()
    for (left, right), value in cell_diagonal_homotopy(cell):
        for (a, b), sign in cell_diagonal(left):
            result[(a, b, right)] += value * sign
    for (left, right), value in cell_diagonal(cell):
        for (b, c), sign in cell_diagonal_homotopy(right):
            result[(left, b, c)] -= value * sign * (-1 if _degree(left) % 2 else 1)
        for (a, c), sign in cell_diagonal_homotopy(left):
            result[(a, right, c)] -= value * sign * (
                -1 if _degree(right) * _degree(c) % 2 else 1
            )
    return tuple(sorted((key, value) for key, value in result.items() if value))


def _contract_triple(triple: TripleCell, carrier: Cell) -> tuple[tuple[TripleCell, int], ...]:
    """Contract the nine-factor output chain to the first carrier vertex.

    Tensor the ordinary simplex cone with the preceding vertex
    projections. Those projections kill every preceding positive degree,
    so the surviving tensor-operator signs are all positive.
    """

    parts = (*triple[0], *triple[1], *triple[2])
    roots = (*tuple(s[0] for s in carrier),) * 3
    result = []
    for index, (simplex, root) in enumerate(zip(parts, roots, strict=True)):
        if any(len(s) != 1 for s in parts[:index]):
            break
        if root in simplex:
            continue
        output = tuple((roots[i],) for i in range(index)) + ((root, *simplex),) + parts[index + 1:]
        result.append((cast(TripleCell, (output[:3], output[3:6], output[6:])), 1))
    return tuple(result)


@cache
def cell_hirsch_filler(cell: Cell) -> tuple[tuple[TripleCell, int], ...]:
    """Define K(c)=C(J(c)+K(boundary c)), so boundary K-K boundary=J.

    J has degree one and boundary J+J boundary=0. Its recursive right
    side is a positive-degree cycle in a contractible cell carrier.
    The first-vertex contraction therefore fills it exactly. This is
    acyclic-carrier construction, not coefficient fitting or a solver.
    """

    cycle: Counter[TripleCell] = Counter(dict(cell_hirsch_defect(cell)))
    for face, sign in cell_boundary(cell):
        for triple, value in cell_hirsch_filler(face):
            cycle[triple] += sign * value
    result: Counter[TripleCell] = Counter()
    for triple, value in cycle.items():
        if value:
            for target, sign in _contract_triple(triple, cell):
                result[target] += sign * value
    return tuple(sorted((key, value) for key, value in result.items() if value))


@cache
def cell_cup_coherence(first: Cell, second: Cell, third: Cell) -> tuple[int, Cell] | None:
    """Dualize minus K to a degree-minus-two coefficient kernel."""

    # Reuse the original cell validator, including singleton cells.
    for cell in (first, second, third):
        cell_cup_homotopy(cell, cell)
    carrier = cast(Cell, tuple(tuple(sorted(set(a) | set(b) | set(c)))
                   for a, b, c in zip(first, second, third, strict=True)))
    if _degree(carrier) != _degree(first) + _degree(second) + _degree(third) - 2:
        return None
    value = dict(cell_hirsch_filler(carrier)).get((first, second, third), 0)
    return None if not value else (-value, carrier)


def mixed_scalar_cup_coherence(
    first: SparseOuterCechCochain,
    second: SparseOuterCechCochain,
    third: SparseOuterCechCochain,
) -> SparseOuterCechCochain:
    """Satisfy dT-T(d inputs)=H(ab,c)-(-1)^|a|aH(b,c)-(-1)^(|b||c|)H(a,c)b.

    This degree-minus-two operation has the usual threefold Koszul
    crossing sign. Its even degree contributes no extra total structural
    sign. The identity includes the ambient hypersurface differential;
    matrix and internally shifted inputs are explicitly refused.
    """

    if any(b.component.left_index or b.component.right_index or b.component.object_degree
           for v in (first, second, third) for b, _ in v.terms):
        raise ValueError("the scalar cup coherence cannot commute matrix or shifted factors")
    result = []
    for a, av in first.terms:
        for b, bv in second.terms:
            ab = _koszul_cup(a.component.koszul_summand, b.component.koszul_summand)
            if ab is None:
                continue
            for c, cv in third.terms:
                abc = _koszul_cup(ab[1], c.component.koszul_summand)
                cell = cell_cup_coherence(a.cell, b.cell, c.cell)
                if abc is None or cell is None:
                    continue
                crossing = (
                    a.cech_degree * b.component.structural_degree
                    + (a.cech_degree + b.cech_degree) * c.component.structural_degree
                )
                degree = cast(tuple[int, int, int], _sum_tuple(_sum_tuple(
                    a.component.line_degree, b.component.line_degree,
                ), c.component.line_degree))
                image = OuterCechBasis(
                    OuterCechComponent(0, 0, 0, degree, abc[1]),
                    cast(tuple[int, int, int], _sum_tuple(_sum_tuple(
                        a.x_monomial, b.x_monomial), c.x_monomial)),
                    cast(tuple[int, int, int], _sum_tuple(_sum_tuple(
                        a.u_monomial, b.u_monomial), c.u_monomial)),
                    cast(tuple[int, int], _sum_tuple(_sum_tuple(
                        a.p_monomial, b.p_monomial), c.p_monomial)), cell[1],
                )
                result.append((image, av * bv * cv * ab[0] * abc[0] * cell[0]
                               * (-1 if crossing % 2 else 1)))
    return SparseOuterCechCochain(tuple(result))
