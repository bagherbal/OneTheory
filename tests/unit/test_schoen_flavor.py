"""Test the exact holomorphic tree-level flavor theorem.

Owns:
    Symbolic determinant zero, generic rank two, exact null vectors, common
    one-plus-two support, explicit coefficient admission, and CP obstruction.

Depends on:
    `onetheory.models.heterotic_schoen.flavor`, exact Rational values, and pytest.

Must not:
    Treat coefficients as measured masses, construct physical Yukawas, normalize
    matter metrics, or import observations into the carrier.

Phase 0:
    Holomorphic support tests only; canonical normalization and physical mixing
    remain unresolved.
"""

from __future__ import annotations

import pytest

from onetheory.core.errors import MissingPhysicalInput
from onetheory.math.linear import Vector
from onetheory.models.heterotic_schoen.flavor import (
    tree_level_flavor,
    tree_yukawa_texture,
)


def test_tree_level_flavor_is_symbolically_rank_two_with_exact_nulls() -> None:
    result = tree_level_flavor()
    matrix = tree_yukawa_texture(2, 3, 5, 7)
    right, left = result.up.exact_null_vectors({"a": 2, "b": 3, "c": 5, "d": 7})

    assert result.up.determinant.is_zero()
    assert result.down.determinant.is_zero()
    assert result.up.generic_rank == 2
    assert result.up.family_block_sizes == (1, 2)
    assert matrix @ right == Vector((0, 0, 0))
    assert matrix.transpose() @ left == Vector((0, 0, 0))


def test_tree_level_flavor_remains_holomorphic_and_fail_closed() -> None:
    result = tree_level_flavor()

    assert not result.physical
    assert result.ckm_cp_obstructed
    with pytest.raises(MissingPhysicalInput):
        result.up.evaluate({"a": 1, "b": 2, "c": 3})
    with pytest.raises(TypeError):
        tree_yukawa_texture(0.5, 1, 2, 3)
