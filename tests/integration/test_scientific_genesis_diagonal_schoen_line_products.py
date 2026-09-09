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
from research.experiments.scientific_genesis.diagonal_schoen_line_actions import (
    line_has_character,
    project_line_character,
)
from research.experiments.scientific_genesis.diagonal_schoen_line_contraction import (
    strict_line_inclusion,
)
from research.experiments.scientific_genesis.diagonal_schoen_line_products import (
    diagonal_line_product,
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
