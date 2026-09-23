"""Check endpoint indexing preserves the exact external matter tensor.

Owns:
    A finite direct comparison between indexed tensor evaluation and the
    underlying signed Čech cup on one-term independent-factor cochains.

Depends on:
    The research four-factor tensor and chain-diagonal basis definitions.

Must not:
    Treat synthetic algebraic cells as physical matter representatives or
    infer a Yukawa coefficient from this implementation regression.

Phase 0:
    Fast exact regression for a computation-preserving research optimization.
"""

from __future__ import annotations

from itertools import product

from onetheory.math.numbers import Eisenstein
from research.experiments.scientific_genesis.mixed_schoen_chain_diagonal import (
    ChainDiagonalBasis,
    ChainDiagonalCochain,
    _object_indices,
    _target_component,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_tensor import (
    IndependentMatterBasis,
    IndependentMatterCochain,
    _cell_cup,
    external_lifted_matter_tensor,
)

ZERO_MONOMIALS = ((0, 0, 0), (0, 0), (0, 0, 0), (0, 0))


def _degree_one_cells() -> tuple[tuple[tuple[int, ...], ...], ...]:
    """Enumerate exact degree-one cells with both singleton pivots."""

    cells = []
    for overlap_factor in range(4):
        other_factors = tuple(index for index in range(4) if index != overlap_factor)
        for pivots in product(range(2), repeat=3):
            cell = [tuple([0, 1]) if index == overlap_factor else (0,) for index in range(4)]
            for index, pivot in zip(other_factors, pivots, strict=True):
                cell[index] = (pivot,)
            cells.append(tuple(cell))
    return tuple(cells)


def _cochain(
    factor: int,
    cell: tuple[tuple[int, ...], ...],
) -> IndependentMatterCochain:
    """Build one homogeneous algebraic test cochain with no physical label."""

    basis = IndependentMatterBasis(factor, 0, (), 0, ZERO_MONOMIALS, cell)
    return IndependentMatterCochain(factor, 1, ((basis, Eisenstein(1)),))


def test_endpoint_index_agrees_with_direct_cech_cup() -> None:
    """All small cell pairs retain the original exact tensor value."""

    target_component = _target_component(_object_indices()[(0, 0)], ())
    cells = _degree_one_cells()
    for left_cell in cells:
        left = _cochain(1, left_cell)
        for right_cell in cells:
            result = external_lifted_matter_tensor(
                left, _cochain(2, right_cell)
            )
            cup = _cell_cup(left_cell, right_cell)
            if cup is None:
                assert result.is_zero()
            else:
                sign, cell = cup
                expected = ChainDiagonalCochain(
                    (
                        (
                            ChainDiagonalBasis(
                                target_component, ZERO_MONOMIALS, cell
                            ),
                            Eisenstein(sign),
                        ),
                    )
                )
                assert result == expected
