"""Test the exact diagonal p-minus-q line isomorphism.

Owns:
    Regression gates for the local Laurent identity, normalization checks, and
    the full Cech--Koszul chain-map law on independent exact generators.

Depends on:
    The diagonal line isomorphism and exact scalar full differential.

Must not:
    Use carrier cochains, identify projective-line factors globally, or select
    a determinant normalization by a numerical output.

Phase 0:
    Integration tests for the determinant-line normalization map.
"""

from __future__ import annotations

from itertools import product

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.scientific_genesis.diagonal_schoen_line_isomorphism import (
    canonicalize_p_minus_q_twist,
    diagonal_twist_local_identity_exact,
)
from research.experiments.scientific_genesis.diagonal_schoen_lines import (
    _FullBasis,
    _FullCochain,
    _subtract_degrees,
)
from research.experiments.scientific_genesis.mixed_schoen_yukawa_trace import (
    scalar_full_differential,
)

SOURCE_DEGREES = (0, 1, 0, -1)
TARGET_DEGREES = (0, 0, 0, 0)


def _generator(pivot_p: int, pivot_q: int) -> _FullCochain:
    """Return one regular local generator of the twisted diagonal line."""

    p_monomial = (1, 0) if pivot_p == 0 else (0, 1)
    q_monomial = (-1, 0) if pivot_q == 0 else (0, -1)
    return _FullCochain(
        (
            (
                _FullBasis(
                    (),
                    SOURCE_DEGREES,
                    ((0, 0, 0), p_monomial, (0, 0, 0), q_monomial),
                    ((0,), (pivot_p,), (0,), (pivot_q,)),
                ),
                Eisenstein(1),
            ),
        )
    )


def test_diagonal_twist_uses_the_exact_local_laurent_identity() -> None:
    """The overlap correction is fixed by the diagonal equation."""

    assert diagonal_twist_local_identity_exact()
    with pytest.raises(ValueError, match="do not differ"):
        canonicalize_p_minus_q_twist(
            _generator(0, 0),
            SOURCE_DEGREES,
            (0, 0, 0, 1),
        )


def test_diagonal_twist_map_commutes_with_the_full_differential() -> None:
    """All four affine vertex generators satisfy the chain-map identity."""

    for pivot_p, pivot_q in product(range(2), repeat=2):
        source = _generator(pivot_p, pivot_q)
        source_image = scalar_full_differential(source)
        mapped_source = canonicalize_p_minus_q_twist(
            source,
            SOURCE_DEGREES,
            TARGET_DEGREES,
        )
        mapped_image = canonicalize_p_minus_q_twist(
            source_image,
            SOURCE_DEGREES,
            TARGET_DEGREES,
        )
        assert scalar_full_differential(mapped_source) == mapped_image
        assert all(
            basis.ambient_degrees
            == _subtract_degrees(TARGET_DEGREES, basis.subset)
            for basis, _coefficient in mapped_source.terms
        )
