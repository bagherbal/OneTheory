"""Test exact deck actions and products on diagonal Schoen line cochains.

Owns:
    Regression gates for the scalar unit, Reynolds normalization, signed line
    multiplication, and the direct sparse Cech differential.

Depends on:
    The exact diagonal line contraction and published Schoen deck action.

Must not:
    Introduce bundle pairings, choose a carrier point, or infer a Yukawa value.

Phase 0:
    Integration tests for reusable research-only line-cochain algebra.
"""

from __future__ import annotations

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.scientific_genesis.diagonal_schoen_line_actions import (
    diagonal_line_full_action,
    line_has_character,
    project_line_character,
)
from research.experiments.scientific_genesis.diagonal_schoen_line_contraction import (
    strict_line_inclusion,
)
from research.experiments.scientific_genesis.diagonal_schoen_line_products import (
    diagonal_line_product,
)
from research.experiments.scientific_genesis.diagonal_schoen_lines import (
    _FullBasis,
    _FullCochain,
)
from research.experiments.scientific_genesis.mixed_schoen_yukawa_trace import (
    scalar_full_differential,
)


def test_scalar_unit_is_invariant_and_multiplicative() -> None:
    """The strict scalar unit is fixed by Reynolds projection and cup product."""

    unit, inclusion_depth = strict_line_inclusion(
        (0, 0, 0, 0),
        0,
        ((0, Eisenstein(1)),),
    )

    assert inclusion_depth == 1
    assert len(unit.terms) == 36
    assert scalar_full_differential(unit).is_zero()
    assert line_has_character(unit, (0, 0), (0, 0))
    assert project_line_character(unit, (0, 0), (0, 0)) == unit
    assert diagonal_line_product(unit, unit, (0, 0, 0, 0)) == unit


def test_line_product_intertwines_deck_actions() -> None:
    """Deck pullback respects the signed product and summed line frame."""

    cell = ((0,), (0,), (0,), (0,))
    monomials = ((0, 0, 0), (0, 0), (0, 0, 0), (0, 0))
    left = _FullCochain(
        ((_FullBasis((0,), (0, 0, 0, 0), monomials, cell), Eisenstein(1)),)
    )
    right = _FullCochain(
        ((_FullBasis((1,), (0, 0, 0, 0), monomials, cell), Eisenstein(1)),)
    )
    product = diagonal_line_product(left, right, (3, 1, 3, 1))

    for action in schoen_sparse_deck_actions():
        expected = diagonal_line_product(
            diagonal_line_full_action(left, action, (1, 0)),
            diagonal_line_full_action(right, action, (1, 1)),
            (3, 1, 3, 1),
        )
        assert diagonal_line_full_action(product, action, (2, 1)) == expected


def test_character_projection_commutes_with_scalar_differential() -> None:
    """A non-pure exact boundary need not equal its projected boundary."""

    source = _FullCochain(
        ((
            _FullBasis(
                (), (0, 0, 0, 0),
                ((0, 0, 0), (0, 0), (0, 0, 0), (0, 0)),
                ((0,), (0,), (0,), (0,)),
            ),
            Eisenstein(1),
        ),)
    )
    boundary = scalar_full_differential(source)
    frame = (2, 1)
    projected_source = project_line_character(source, (0, 0), frame)
    projected_boundary = project_line_character(boundary, (0, 0), frame)

    assert not boundary.is_zero()
    assert scalar_full_differential(projected_source) == projected_boundary
    assert projected_boundary != boundary
