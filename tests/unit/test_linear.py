"""Test exact immutable matrix and vector operations.

Owns:
    Focused algebraic, validation, and property tests for the exact linear
    algebra foundation over Rational and Eisenstein scalars.

Depends on:
    `onetheory.math.linear`, `onetheory.math.numbers`, Hypothesis, pytest, and
    Python’s standard-library dataclass exceptions.

Must not:
    Test numerical approximations, tensor or polynomial APIs, physical model
    behavior, or import the standalone draft as an implementation dependency.

Phase 0:
    Mathematical foundation tests only; no physical implementation is provided yet.
"""

from __future__ import annotations

import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from onetheory.math.linear import Matrix, Vector, determinant, matrix_power, nullspace, rank
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein, Rational


@st.composite
def rational_matrices(draw, rows: int, columns: int) -> Matrix:
    values = draw(
        st.lists(
            st.integers(min_value=-3, max_value=3),
            min_size=rows * columns,
            max_size=rows * columns,
        )
    )
    return Matrix(
        tuple(
            tuple(values[row * columns + column] for column in range(columns))
            for row in range(rows)
        )
    )


def test_matrix_and_vector_are_immutable_and_rectangular() -> None:
    matrix = Matrix(((1, 2), (3, 4)))
    vector = Vector((1, 2))

    assert matrix.shape == (2, 2)
    assert matrix.rows == ((Rational(1), Rational(2)), (Rational(3), Rational(4)))
    assert vector.values == (Rational(1), Rational(2))

    with pytest.raises(FrozenInstanceError):
        matrix._rows = ()  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        vector._values = ()  # type: ignore[misc]

    with pytest.raises(ValueError):
        Matrix(())
    with pytest.raises(ValueError):
        Matrix(((),))
    with pytest.raises(ValueError):
        Matrix(((1, 2), (3,)))


def test_matrix_products_and_vector_products_are_exact() -> None:
    matrix = Matrix(((1, 2, 3), (4, 5, 6)))
    vector = Vector((1, 0, 2))
    right = Matrix(((1, 2), (0, 1), (2, 0)))

    assert matrix @ vector == Vector((7, 16))
    assert matrix.matvec(vector) == Vector((7, 16))
    assert matrix @ right == Matrix(((7, 4), (16, 13)))
    assert matrix * right == matrix @ right
    assert matrix.transpose() == Matrix(((1, 4), (2, 5), (3, 6)))
    assert 2 * vector == Vector((2, 0, 4))


def test_rref_rank_and_nullspace_are_deterministic() -> None:
    matrix = Matrix(((1, 2, 1), (2, 4, 0), (0, 1, 1)))

    reduced, pivots = matrix.rref()

    assert pivots == (0, 1, 2)
    assert reduced == Matrix.identity(3)
    assert matrix.rank() == 3
    assert matrix.nullspace() == ()


def test_tree_yukawa_rank_and_null_vectors_are_exact() -> None:
    tree_yukawa = Matrix(((0, 2, 3), (5, 0, 0), (7, 0, 0)))
    right_null = Vector((0, -3, 2))
    left_null = Vector((0, -7, 5))

    assert rank(tree_yukawa) == 2
    assert determinant(tree_yukawa) == Rational(0)
    assert (tree_yukawa @ right_null).is_zero()
    assert (tree_yukawa.transpose() @ left_null).is_zero()
    assert len(nullspace(tree_yukawa)) == 1


def test_inverse_determinant_and_integer_powers_are_exact() -> None:
    matrix = Matrix(((2, 1), (1, 1)))
    identity = Matrix.identity(2)

    assert matrix.determinant() == Rational(1)
    assert matrix.inverse() == Matrix(((1, -1), (-1, 2)))
    assert matrix @ matrix.inverse() == identity
    assert matrix**0 == identity
    assert matrix**2 == Matrix(((5, 3), (3, 2)))
    assert matrix_power(matrix, -1) == matrix.inverse()


def test_determinants_support_arbitrary_square_sizes() -> None:
    assert Matrix(((5,),)).determinant() == Rational(5)
    assert Matrix(((1, 2), (3, 4))).determinant() == Rational(-2)
    assert Matrix(((6, 1, 1), (4, -2, 5), (2, 8, 7))).determinant() == Rational(-306)
    assert Matrix(
        ((1, 2, 3, 4), (5, 6, 7, 8), (2, 6, 4, 8), (3, 1, 1, 2))
    ).determinant() == Rational(72)


def test_eisenstein_matrix_identities_use_the_same_algorithms() -> None:
    permutation = Matrix(
        ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
        scalar_type=Eisenstein,
    )
    diagonal = Matrix(
        ((1, 0, 0), (0, OMEGA, 0), (0, 0, OMEGA2)),
        scalar_type=Eisenstein,
    )
    twisted = permutation @ diagonal
    identity = Matrix.identity(3, scalar_type=Eisenstein)

    assert permutation**3 == identity
    assert twisted**3 == identity
    assert permutation @ twisted == (twisted @ permutation).scale(OMEGA)
    assert twisted.inverse() @ twisted == identity


def test_exact_scalar_and_dimension_policy_rejects_invalid_operations() -> None:
    with pytest.raises(TypeError):
        Matrix(((0.5,),))
    with pytest.raises(TypeError):
        Vector((0.5,))

    with pytest.raises(ValueError):
        Matrix(((1, 2),)) @ Vector((1,))
    with pytest.raises(ValueError):
        Matrix(((1, 2),)) @ Matrix(((1,),))
    with pytest.raises(TypeError):
        Matrix(((1,),)).scale(0.5)
    with pytest.raises(TypeError):
        Matrix(((1,),), scalar_type=Eisenstein) + Matrix(((1,),))
    with pytest.raises(ValueError):
        Matrix(((1, 2),)).inverse()
    with pytest.raises(ValueError):
        Matrix(((1, 2), (2, 4))).inverse()
    with pytest.raises(TypeError):
        Matrix(((1,),)) ** 1.5  # type: ignore[operator]


@given(left=rational_matrices(2, 2), middle=rational_matrices(2, 2), right=rational_matrices(2, 2))
def test_matrix_multiplication_is_associative(
    left: Matrix,
    middle: Matrix,
    right: Matrix,
) -> None:
    assert (left @ middle) @ right == left @ (middle @ right)


@given(matrix=rational_matrices(2, 3))
def test_nullspace_basis_has_exact_zero_products_and_correct_dimension(matrix: Matrix) -> None:
    basis = matrix.nullspace()

    assert len(basis) + matrix.rank() == matrix.column_count
    assert all((matrix @ vector).is_zero() for vector in basis)


@given(matrix=rational_matrices(3, 3))
def test_rref_is_idempotent(matrix: Matrix) -> None:
    reduced, pivots = matrix.rref()
    reduced_again, pivots_again = reduced.rref()

    assert reduced_again == reduced
    assert pivots_again == pivots


def test_linear_module_does_not_import_the_standalone_draft() -> None:
    module_path = Path(__import__("onetheory.math.linear", fromlist=["__file__"]).__file__ or "")

    assert module_path.name == "linear.py"
    assert "Experimental_Draft_OneTheory" not in str(module_path)
    assert not any(name.startswith("Experimental_Draft_OneTheory") for name in sys.modules)
