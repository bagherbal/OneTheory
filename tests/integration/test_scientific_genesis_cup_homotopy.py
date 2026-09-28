"""Verify the diagonal homotopy independently before any twisted use.

Owns:
    Exhaustive finite cell-chain identities and full scalar Koszul signs.

Depends on:
    Ordered product-cover cells, exact scalar cochains, and the new
    coefficient homotopy kernel.

Must not:
    Treat scalar homotopy tests as certification of a physical tensor map.

Phase 0:
    Mathematical research tests for the raw exterior-cup deficiency.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations, product

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis.mixed_schoen_common_dga import mixed_outer_cup
from research.experiments.scientific_genesis.mixed_schoen_cup_homotopy import (
    cell_cup_homotopy,
    mixed_scalar_cup_homotopy,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import _MixedContraction
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import mixed_schoen_unit


def _degree(cell: tuple[tuple[int, ...], ...]) -> int:
    return sum(len(simplex) - 1 for simplex in cell)


def _boundary(cell: tuple[tuple[int, ...], ...]) -> Counter:
    """Independent product-chain boundary, with no cochain differential call."""

    output = Counter()
    preceding = 0
    for factor, simplex in enumerate(cell):
        if len(simplex) > 1:
            for deleted in range(len(simplex)):
                target = list(cell)
                target[factor] = simplex[:deleted] + simplex[deleted + 1:]
                output[tuple(target)] += (-1) ** (preceding + deleted)
        preceding += len(simplex) - 1
    return output


def _diagonal(cell: tuple[tuple[int, ...], ...]) -> Counter:
    """Enumerate all cuts directly, independently of the homotopy kernel."""

    output = Counter()
    for cuts in product(*(range(len(simplex)) for simplex in cell)):
        left = tuple(simplex[:cut + 1] for simplex, cut in zip(cell, cuts, strict=True))
        right = tuple(simplex[cut:] for simplex, cut in zip(cell, cuts, strict=True))
        sign = sum(
            (len(right[i]) - 1) * (len(left[j]) - 1)
            for i in range(3) for j in range(i + 1, 3)
        )
        output[(left, right)] += (-1) ** sign
    return output


def _clean(chain: Counter) -> dict:
    return {basis: coefficient for basis, coefficient in chain.items() if coefficient}


def test_diagonal_homotopy_on_every_product_cell() -> None:
    """Check boundary H + H boundary = AW - flip AW on all 147 cells."""

    simplices = tuple(tuple(
        simplex for size in range(1, count + 1)
        for simplex in combinations(range(count), size)
    ) for count in (3, 3, 2))
    cells = tuple(product(*simplices))
    assert len(cells) == 147
    homotopies = {cell: Counter() for cell in cells}
    for left, right in product(cells, repeat=2):
        entry = cell_cup_homotopy(left, right)
        if entry is not None:
            sign, target = entry
            homotopies[target][(left, right)] += sign
    for cell in cells:
        rhs = _diagonal(cell)
        for (left, right), value in _diagonal(cell).items():
            rhs[(right, left)] -= value * (-1) ** (_degree(left) * _degree(right))
        lhs = Counter()
        for (left, right), value in homotopies[cell].items():
            for face, coefficient in _boundary(left).items():
                lhs[(face, right)] += value * coefficient
            for face, coefficient in _boundary(right).items():
                lhs[(left, face)] += value * coefficient * (-1) ** _degree(left)
        for face, coefficient in _boundary(cell).items():
            for pair, value in homotopies[face].items():
                lhs[pair] += value * coefficient
        assert _clean(lhs) == _clean(rhs), cell


@pytest.mark.parametrize("first,second", tuple(product(("k0", "k1_x", "k1_u", "k2"), repeat=2)))
@pytest.mark.parametrize("cells", (
    (((0, 1), (0,), (0,)), ((0, 1), (0, 1), (0,))),
    (((0,), (0,), (0, 1)), ((0, 1), (0,), (0, 1))),
))
def test_full_scalar_koszul_commutator_homotopy(
    first: str, second: str, cells: tuple,
) -> None:
    """Include the equation perturbation, not just the Cech differential."""

    unit = mixed_schoen_unit()
    context = _MixedContraction(unit, unit)

    def entry(koszul: str, cell: tuple, value: Eisenstein) -> SparseOuterCechCochain:
        component = context.components[(0, 0, koszul)]
        x, u, p = component.ambient_degree
        return SparseOuterCechCochain(((OuterCechBasis(
            component, (x, 0, 0), (u, 0, 0), (p, 0), cell,
        ), value),))

    a = entry(first, cells[0], Eisenstein(2, -1))
    b = entry(second, cells[1], Eisenstein(-3, 2) / 7)
    a_degree = a.terms[0][0].total_degree
    b_degree = b.terms[0][0].total_degree
    homotopy = mixed_scalar_cup_homotopy(a, b)
    lhs = (
        context.differential(homotopy)
        + mixed_scalar_cup_homotopy(context.differential(a), b)
        + mixed_scalar_cup_homotopy(a, context.differential(b)).scale(-1 if a_degree % 2 else 1)
    )
    rhs = mixed_outer_cup(a, b) + mixed_outer_cup(b, a).scale(1 if a_degree * b_degree % 2 else -1)
    assert lhs == rhs


def test_scalar_homotopy_refuses_matrix_components() -> None:
    """Matrix order cannot be reversed by a scalar coefficient operation."""

    basis = OuterCechBasis(
        OuterCechComponent(1, 0, 0, (0, 0, 0), "k0"),
        (0, 0, 0), (0, 0, 0), (0, 0), ((0,), (0,), (0,)),
    )
    cochain = SparseOuterCechCochain(((basis, Eisenstein(1)),))
    with pytest.raises(ValueError, match="cannot commute matrix"):
        mixed_scalar_cup_homotopy(cochain, cochain)


def test_cell_homotopy_refuses_unordered_cells() -> None:
    with pytest.raises(ValueError, match="ordered cells"):
        cell_cup_homotopy(((1, 0), (0,), (0,)), ((0,), (0,), (0,)))


def test_product_cover_homotopy_is_not_a_strict_first_slot_hirsch_derivation() -> None:
    """The coupled outer row needs more than repeating the rank-one proof."""

    component = OuterCechComponent(0, 0, 0, (0, 0, 0), "k0")

    def entry(cell: tuple) -> SparseOuterCechCochain:
        return SparseOuterCechCochain(((OuterCechBasis(
            component, (0, 0, 0), (0, 0, 0), (0, 0), cell,
        ), Eisenstein(1)),))

    a = entry(((0,), (0, 1), (0,)))
    b = entry(((0,), (1,), (0, 1)))
    c = entry(((0,), (0,), (0, 1)))
    assert {x.total_degree for v in (a, b, c) for x, _ in v.terms} == {1}
    # The proposed rule is H(ab,c)=(-1)^|a| a H(b,c)
    # +(-1)^(|b||c|) H(a,c)b. All three degrees are one.
    defect = (
        mixed_scalar_cup_homotopy(mixed_outer_cup(a, b), c)
        + mixed_outer_cup(a, mixed_scalar_cup_homotopy(b, c))
        + mixed_outer_cup(mixed_scalar_cup_homotopy(a, c), b)
    )
    assert defect == entry(((0,), (0, 1), (0, 1)))
