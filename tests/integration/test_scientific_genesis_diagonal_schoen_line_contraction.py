"""Test exact primitives in the diagonal-Schoen line presentation.

Owns:
    Regression evidence for line-degree validation and exact full-complex
    reconstruction in an acyclic determinant line.

Depends on:
    The diagonal Cech--Koszul differential and its finite HPL contraction.

Must not:
    Infer a Higgs lift, choose a carrier parameter, or evaluate a Yukawa entry.

Phase 0:
    Integration tests for the line-valued contraction frontier.
"""

from __future__ import annotations

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.scientific_genesis.diagonal_schoen_line_contraction import (
    exact_diagonal_line_primitive,
)
from research.experiments.scientific_genesis.diagonal_schoen_lines import (
    _FullBasis,
    _FullCochain,
)
from research.experiments.scientific_genesis.mixed_schoen_yukawa_trace import (
    scalar_full_differential,
)


def _determinant_line_seed() -> _FullCochain:
    """Return one regular degree-one cochain in det(V1)."""

    basis = _FullBasis(
        (),
        (-2, 0, 2, 0),
        ((-1, -1, 0), (0, 0), (2, 0, 0), (0, 0)),
        ((0, 1), (0,), (0,), (0,)),
    )
    return _FullCochain(((basis, Eisenstein(1)),))


def test_acyclic_determinant_line_recovers_an_exact_primitive() -> None:
    """The finite contraction reconstructs a nonzero determinant-line boundary."""

    cocycle = scalar_full_differential(_determinant_line_seed())
    result = exact_diagonal_line_primitive(cocycle, (-2, 2, 0), 2)

    assert len(cocycle.terms) == 5
    assert scalar_full_differential(cocycle).is_zero()
    assert result.projection_depth == 1
    assert result.inclusion_depth == 0
    assert result.homotopy_depth == 1
    assert scalar_full_differential(result.primitive) == cocycle
    assert result.exact


def test_line_contraction_rejects_a_mismatched_normalization() -> None:
    """A cochain cannot be silently reinterpreted in another determinant line."""

    cocycle = scalar_full_differential(_determinant_line_seed())
    with pytest.raises(ValueError, match="wrong diagonal line"):
        exact_diagonal_line_primitive(cocycle, (2, -2, 0), 2)
