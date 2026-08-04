"""Test exact basis-aware geometric quantities.

Owns:
    Reproduction tests for the declared intersection tensor, divisor squares,
    characteristic-class arithmetic, quotient/cover scaling, and slopes.

Depends on:
    `onetheory.math.geometry`, `onetheory.math.numbers`, pytest, Hypothesis, and
    Python’s standard-library dataclass exceptions.

Must not:
    Put Schoen constants in production, implement bundles or sheaves, test
    cohomology or physics, or use numerical geometry.

Phase 0:
    Mathematical foundation tests only; no physical implementation is provided yet.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest
from hypothesis import given
from hypothesis import strategies as st

from onetheory.math.geometry import (
    Basis,
    CharacteristicClass,
    Divisor,
    Normalization,
    TripleIntersectionTensor,
    cover_to_quotient,
    divisor_square,
    quotient_to_cover,
    slope,
    triple_product,
    volume,
)
from onetheory.math.numbers import Rational


def quotient_geometry() -> tuple[Basis, Normalization, TripleIntersectionTensor]:
    basis = Basis("quotient", ("J1", "J2", "J3"))
    normalization = Normalization("quotient")
    tensor = TripleIntersectionTensor(
        basis,
        {
            (0, 0, 1): Rational(1, 3),
            (0, 1, 1): Rational(1, 3),
            (0, 1, 2): Rational(1),
        },
        normalization,
    )
    return basis, normalization, tensor


def test_named_basis_and_exact_intersection_tensor() -> None:
    basis, normalization, tensor = quotient_geometry()
    j1 = Divisor(basis, (1, 0, 0), normalization)
    j2 = Divisor(basis, (0, 1, 0), normalization)
    j3 = Divisor(basis, (0, 0, 1), normalization)

    assert tensor.coefficient(0, 0, 1) == Rational(1, 3)
    assert tensor.coefficient(1, 0, 0) == Rational(1, 3)
    assert triple_product(tensor, j1, j1, j2) == Rational(1, 3)
    assert triple_product(tensor, j1, j2, j3) == Rational(1)
    assert triple_product(tensor, j3, j2, j1) == Rational(1)
    assert volume(tensor, j1 + j2 + j3) == Rational(8)
    assert tensor.entries == (
        ((0, 0, 1), Rational(1, 3)),
        ((0, 1, 1), Rational(1, 3)),
        ((0, 1, 2), Rational(1)),
    )

    with pytest.raises(FrozenInstanceError):
        j1._coordinates = ()  # type: ignore[misc]
    with pytest.raises(ValueError):
        Basis("invalid", ("J1", "J1"))


def test_divisor_square_matches_the_exact_coordinate_identity() -> None:
    basis, normalization, tensor = quotient_geometry()
    divisor = Divisor(basis, (1, 2, -1), normalization)

    square = divisor_square(tensor, divisor)

    assert square.coordinates == (
        Rational(-4, 3),
        Rational(-1, 3),
        Rational(4),
    )
    assert square.basis == basis
    assert square.normalization == normalization


def test_characteristic_classes_add_exactly() -> None:
    basis, normalization, _ = quotient_geometry()
    tangent = CharacteristicClass(basis, (4, 4, 0), 2, normalization)
    visible = CharacteristicClass(basis, (Rational(8, 3), Rational(5, 3), 4), 2, normalization)
    hidden = CharacteristicClass(basis, (Rational(4, 3), Rational(7, 3), -4), 2, normalization)

    assert visible + hidden == tangent
    assert (tangent - visible) == hidden
    assert hidden.scale(3).coordinates == (Rational(4), Rational(7), Rational(-12))


def test_slopes_scale_from_quotient_to_ninefold_cover() -> None:
    basis, normalization, tensor = quotient_geometry()
    first_chern = Divisor(basis, (-2, 2, 0), normalization)
    kahler = Divisor(basis, (6, 9, 3), normalization)

    quotient_slope = slope(tensor, first_chern, kahler, rank=2)
    cover_tensor = tensor.to_cover(9)
    cover_slope = slope(
        cover_tensor,
        first_chern.to_cover(9),
        kahler.to_cover(9),
        rank=2,
    )

    assert quotient_slope == Rational(-33)
    assert cover_slope == Rational(-297)
    assert cover_to_quotient(cover_tensor, 9) == tensor
    assert quotient_to_cover(first_chern, 9).normalization == Normalization("cover")


def test_incompatible_bases_and_normalizations_are_rejected() -> None:
    basis, normalization, tensor = quotient_geometry()
    other_basis = Basis("other", basis.labels)
    divisor = Divisor(basis, (1, 0, 0), normalization)
    other_divisor = Divisor(other_basis, (1, 0, 0), normalization)
    cover_divisor = divisor.to_cover(9)
    class_quotient = CharacteristicClass(basis, (1, 2, 3), 2, normalization)
    class_cover = class_quotient.to_cover(9)

    with pytest.raises(ValueError):
        divisor + other_divisor
    with pytest.raises(ValueError):
        tensor.triple_product(divisor, cover_divisor, divisor)
    with pytest.raises(ValueError):
        class_quotient + class_cover
    with pytest.raises(TypeError):
        quotient_to_cover(divisor)  # type: ignore[call-arg]
    with pytest.raises(ValueError):
        tensor.to_cover(0)
    with pytest.raises(TypeError):
        Divisor(basis, (0.5, 0, 0), normalization)


@given(
    first=st.integers(min_value=-4, max_value=4),
    second=st.integers(min_value=-4, max_value=4),
    third=st.integers(min_value=-4, max_value=4),
)
def test_divisor_addition_preserves_named_basis_and_normalization(
    first: int,
    second: int,
    third: int,
) -> None:
    basis, normalization, _ = quotient_geometry()
    left = Divisor(basis, (first, second, third), normalization)
    right = Divisor(basis, (1, -2, 3), normalization)

    assert (left + right).basis == basis
    assert (left + right).normalization == normalization
    assert (left + right) - right == left
