"""Test exact prime-field structures and finite group actions.

Owns:
    Unit and property tests for prime fields, finite vectors and matrices,
    quadratic and polar forms, isotropic enumeration, and deterministic orbits.

Depends on:
    `onetheory.math.finite`, Hypothesis, pytest, and Python’s standard library.

Must not:
    Assign physical meaning to finite classifications, import draft code, or
    introduce approximate arithmetic or model-specific structures.

Phase 0:
    Mathematical foundation tests only; no physical implementation is provided yet.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest
from hypothesis import given
from hypothesis import strategies as st

from onetheory.math.finite import (
    FiniteMatrix,
    FiniteVector,
    PrimeField,
    QuadraticForm,
    enumerate_binary_quadratic_forms,
    enumerate_invertible_matrices,
    enumerate_vectors,
    nondegenerate_binary_quadratic_forms,
    orbit_decomposition,
    quadratic_form_orbits,
)


def test_prime_field_and_finite_linear_algebra_are_exact() -> None:
    field = PrimeField(3)
    matrix = FiniteMatrix(((1, 2), (0, 1)), field)
    vector = FiniteVector((2, 1), field)

    assert field.elements == (0, 1, 2)
    assert field(-1) == 2
    assert field.divide(1, 2) == 2
    assert matrix @ vector == FiniteVector((1, 1), field)
    assert matrix.inverse() @ matrix == FiniteMatrix.identity(2, field)
    assert matrix**3 == FiniteMatrix(((1, 0), (0, 1)), field)

    with pytest.raises(ZeroDivisionError):
        field.inverse(0)
    with pytest.raises(TypeError):
        field(0.5)
    with pytest.raises(ValueError):
        PrimeField(4)


def test_finite_vectors_and_matrices_are_immutable() -> None:
    field = PrimeField(5)
    vector = FiniteVector((1, 2), field)
    matrix = FiniteMatrix(((1, 0), (0, 1)), field)

    with pytest.raises(FrozenInstanceError):
        vector._values = ()  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        matrix._rows = ()  # type: ignore[misc]
    assert len(enumerate_vectors(field, 2)) == 25
    assert vector.dot(vector) == 0


def test_binary_quadratic_forms_over_f3_split_into_12_plus_6() -> None:
    field = PrimeField(3)
    split = QuadraticForm.binary(field, 0, 1, 0)
    anisotropic = QuadraticForm.binary(field, 1, 0, 1)
    all_forms = enumerate_binary_quadratic_forms(field)
    nondegenerate = nondegenerate_binary_quadratic_forms(field)
    linear_maps = enumerate_invertible_matrices(field, 2)
    orbits = quadratic_form_orbits(nondegenerate, linear_maps)

    assert len(all_forms) == 27
    assert len(nondegenerate) == 18
    assert len(linear_maps) == 48
    assert len(split.isotropic_vectors()) == 5
    assert split.polar_matrix().rows == ((0, 1), (1, 0))
    assert split.polar_matrix().determinant() == 2
    assert sorted(len(orbit) for orbit in orbits) == [6, 12]

    split_orbit = next(orbit for orbit in orbits if split in orbit)
    anisotropic_orbit = next(orbit for orbit in orbits if anisotropic in orbit)
    assert len(split_orbit) == 12
    assert len(anisotropic_orbit) == 6
    assert set(split_orbit).isdisjoint(anisotropic_orbit)
    assert len(split_orbit) + len(anisotropic_orbit) == len(nondegenerate)


def test_split_plane_isotropic_vectors_and_polar_form() -> None:
    field = PrimeField(3)
    form = QuadraticForm.binary(field, 0, 1, 0)

    isotropic = tuple(vector.values for vector in form.isotropic_vectors())

    assert isotropic == (
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (2, 0),
    )
    assert form.polar(
        FiniteVector((1, 0), field),
        FiniteVector((0, 1), field),
    ) == 1


def test_generic_orbit_decomposition_is_deterministic_and_closed() -> None:
    def shift(value: int) -> int:
        return (value + 1) % 4

    orbits = orbit_decomposition((0, 1, 2, 3), (shift,), key=lambda value: value)

    assert orbits == ((0, 1, 2, 3),)
    with pytest.raises(ValueError):
        orbit_decomposition((0, 1), (shift,), key=lambda value: value)


@given(
    left=st.integers(min_value=0, max_value=2),
    middle=st.integers(min_value=0, max_value=2),
    right=st.integers(min_value=0, max_value=2),
)
def test_prime_field_distributivity(left: int, middle: int, right: int) -> None:
    field = PrimeField(3)

    assert field.multiply(left, field.add(middle, right)) == field.add(
        field.multiply(left, middle),
        field.multiply(left, right),
    )
