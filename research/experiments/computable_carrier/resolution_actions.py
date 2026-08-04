"""Derive exact deck actions on the Tier A Hilbert--Burch complexes.

Owns:
    Finite Eisenstein coordinate substitutions, exact lifts through the named
    source and target terms of the I3/I6 Hilbert--Burch resolutions, and the
    resulting order and projective-commutator certificates.

Depends on:
    Exact production point schemes, Eisenstein polynomial arithmetic, and
    finite-dimensional exact matrices. The lift is derived from the displayed
    resolution equation, not imported from a Serre-ray coordinate list.

Must not:
    Treat a resolution action as a Serre linearization, infer an Ext action
    without a derived comparison map, or claim quotient descent or bundle
    equivariance from the chain-level certificates alone.

Phase 0:
    Exact Hilbert--Burch resolution actions are constructed; Serre extension
    identification and induced invariant-ray comparison remain open.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialMatrix
from onetheory.models.heterotic_schoen.visible import PointScheme, point_schemes

CoordinateImage = tuple[tuple[Eisenstein, tuple[int, ...]], ...]
_UNITS = (
    Eisenstein(1),
    OMEGA,
    OMEGA2,
    -Eisenstein(1),
    -OMEGA,
    -OMEGA2,
)


def _coordinate_images(name: str) -> CoordinateImage:
    """Return the declared exact P or T monomial coordinate substitution."""

    if name == "P":
        return (
            (OMEGA, (0, 1, 0)),
            (OMEGA2, (0, 0, 1)),
            (Eisenstein(1), (1, 0, 0)),
        )
    if name == "T":
        return (
            (Eisenstein(1), (1, 0, 0)),
            (OMEGA, (0, 1, 0)),
            (OMEGA2, (0, 0, 1)),
        )
    raise KeyError(name)


def _transformed_matrix(
    matrix: tuple[tuple[Polynomial, ...], ...],
    images: CoordinateImage,
) -> tuple[tuple[Polynomial, ...], ...]:
    """Apply one exact coordinate substitution to a polynomial matrix."""

    return tuple(
        tuple(entry.substitute_monomials(images) for entry in row)
        for row in matrix
    )


def _generator_action(
    scheme: PointScheme,
    images: CoordinateImage,
) -> tuple[tuple[int, ...], tuple[Eisenstein, ...]]:
    """Identify the exact permutation and scalar action on ideal generators."""

    permutation: list[int] = []
    scalars: list[Eisenstein] = []
    for generator in scheme.ideal_generators:
        transformed = generator.substitute_monomials(images)
        match: tuple[int, Eisenstein] | None = None
        for index, target in enumerate(scheme.ideal_generators):
            for exponents, coefficient in transformed.terms:
                target_coefficient = target.coefficient(exponents)
                if target_coefficient.is_zero():
                    continue
                scalar = coefficient / target_coefficient
                if target.scale(scalar) == transformed:
                    match = (index, scalar)
                    break
            if match is not None:
                break
        if match is None:
            raise ValueError(f"{scheme.name} generator action is not monomial")
        permutation.append(match[0])
        scalars.append(match[1])
    if len(set(permutation)) != len(permutation):
        raise ValueError(f"{scheme.name} generator action is not a permutation")
    return tuple(permutation), tuple(scalars)


def _generator_matrix(
    permutation: Sequence[int],
    scalars: Sequence[Eisenstein],
    transpose: bool,
    global_scalar: Eisenstein,
) -> Matrix:
    """Build one deterministic monomial lift on the target term."""

    size = len(permutation)
    rows = [[Eisenstein(0) for _ in range(size)] for _ in range(size)]
    for source, (target, scalar) in enumerate(zip(permutation, scalars, strict=True)):
        if transpose:
            rows[target][source] = global_scalar * scalar
        else:
            rows[source][target] = global_scalar * scalar
    return Matrix(rows, scalar_type=Eisenstein)


def _right_constant_product(
    matrix: tuple[tuple[Polynomial, ...], ...], constant: Matrix,
) -> PolynomialMatrix:
    """Multiply a polynomial matrix by an exact constant matrix on the right."""

    rows = len(matrix)
    columns = constant.column_count
    return PolynomialMatrix(
        tuple(
            tuple(
                sum(
                    (
                        matrix[row][inner].scale(constant[inner][column])
                        for inner in range(constant.row_count)
                    ),
                    Polynomial.zero(
                        matrix[0][0].variable_count,
                        scalar_type=matrix[0][0].scalar_type,
                    ),
                )
                for column in range(columns)
            )
            for row in range(rows)
        )
    )


def _left_constant_product(
    constant: Matrix,
    matrix: tuple[tuple[Polynomial, ...], ...],
) -> PolynomialMatrix:
    """Multiply an exact constant matrix by a polynomial matrix on the left."""

    rows = constant.row_count
    columns = len(matrix[0])
    return PolynomialMatrix(
        tuple(
            tuple(
                sum(
                    (
                        matrix[inner][column].scale(constant[row][inner])
                        for inner in range(constant.column_count)
                    ),
                    Polynomial.zero(
                        matrix[0][0].variable_count,
                        scalar_type=matrix[0][0].scalar_type,
                    ),
                )
                for column in range(columns)
            )
            for row in range(rows)
        )
    )


def _solve_source_lift(
    matrix: tuple[tuple[Polynomial, ...], ...],
    transformed: tuple[tuple[Polynomial, ...], ...],
    target_action: Matrix,
) -> Matrix | None:
    """Solve ``M A_source = A_target h(M)`` over Eisenstein scalars."""

    rows = len(matrix)
    columns = len(matrix[0])
    exponents = sorted({
        exponent
        for polynomial_row in (*matrix, *transformed)
        for polynomial in polynomial_row
        for exponent, _ in polynomial.terms
    })
    equations: list[list[Eisenstein]] = []
    right_hand_side: list[Eisenstein] = []
    for row in range(rows):
        for column in range(columns):
            for exponent in exponents:
                coefficients = [Eisenstein(0) for _ in range(columns * columns)]
                for inner in range(columns):
                    coefficients[inner * columns + column] = matrix[row][inner].coefficient(
                        exponent
                    )
                value = sum(
                    (
                        target_action[row][inner]
                        * transformed[inner][column].coefficient(exponent)
                        for inner in range(rows)
                    ),
                    Eisenstein(0),
                )
                if (
                    any(not coefficient.is_zero() for coefficient in coefficients)
                    or not value.is_zero()
                ):
                    equations.append(coefficients)
                    right_hand_side.append(value)
    augmented = Matrix(
        (
            (*row, value)
            for row, value in zip(equations, right_hand_side, strict=True)
        ),
        scalar_type=Eisenstein,
    )
    reduced, pivots = augmented.rref()
    unknown_count = columns * columns
    if any(
        all(reduced[row][column].is_zero() for column in range(unknown_count))
        and not reduced[row][unknown_count].is_zero()
        for row in range(reduced.row_count)
    ):
        return None
    solution = [Eisenstein(0) for _ in range(unknown_count)]
    for row, pivot in enumerate(pivots):
        if pivot < unknown_count:
            solution[pivot] = reduced[row][unknown_count]
    return Matrix(
        (
            tuple(solution[row * columns + column] for column in range(columns))
            for row in range(columns)
        ),
        scalar_type=Eisenstein,
    )


def _derive_action(scheme: PointScheme, name: str) -> ResolutionAction:
    """Derive one resolution action by finite exact chain-equation search."""

    images = _coordinate_images(name)
    matrix = scheme.resolution.matrix
    transformed = _transformed_matrix(matrix, images)
    permutation, scalars = _generator_action(scheme, images)
    for transpose in (False, True):
        for global_scalar in _UNITS:
            target_action = _generator_matrix(
                permutation,
                scalars,
                transpose,
                global_scalar,
            )
            source_action = _solve_source_lift(matrix, transformed, target_action)
            if source_action is None:
                continue
            if target_action.determinant().is_zero() or source_action.determinant().is_zero():
                continue
            candidate = ResolutionAction(
                scheme,
                name,
                images,
                target_action,
                source_action,
                permutation,
                scalars,
            )
            if candidate.chain_equation:
                return candidate
    raise ValueError(f"no exact Hilbert--Burch lift found for {scheme.name}:{name}")


@dataclass(frozen=True, slots=True)
class ResolutionAction:
    """One exact coordinate action lifted through a Hilbert--Burch matrix."""

    scheme: PointScheme
    name: str
    coordinate_images: CoordinateImage
    target_action: Matrix
    source_action: Matrix
    generator_permutation: tuple[int, ...]
    generator_scalars: tuple[Eisenstein, ...]

    @property
    def chain_equation(self) -> bool:
        """Return whether the lifted source and target maps commute with ``M``."""

        matrix = self.scheme.resolution.matrix
        transformed = _transformed_matrix(matrix, self.coordinate_images)
        left = _right_constant_product(matrix, self.source_action)
        right = _left_constant_product(self.target_action, transformed)
        return left.rows == right.rows

    @property
    def invertible(self) -> bool:
        """Return whether both finite lifts are exact automorphisms."""

        return (
            not self.target_action.determinant().is_zero()
            and not self.source_action.determinant().is_zero()
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact lift without calling it a Serre action."""

        return {
            "scheme": self.scheme.name,
            "name": self.name,
            "coordinate_images": [
                {"coefficient": str(coefficient), "exponents": list(exponents)}
                for coefficient, exponents in self.coordinate_images
            ],
            "generator_permutation": list(self.generator_permutation),
            "generator_scalars": [str(scalar) for scalar in self.generator_scalars],
            "target_action": [[str(value) for value in row] for row in self.target_action.rows],
            "source_action": [[str(value) for value in row] for row in self.source_action.rows],
            "chain_equation": self.chain_equation,
            "invertible": self.invertible,
            "status": "Hilbert--Burch resolution action only; Serre lift pending",
        }


def _commutator_scalar(left: Matrix, right: Matrix) -> Eisenstein | None:
    """Return the exact unit ``c`` with ``left right = c right left``."""

    product_left = left @ right
    product_right = right @ left
    for scalar in _UNITS:
        if product_left == product_right.scale(scalar):
            return scalar
    return None


@dataclass(frozen=True, slots=True)
class ResolutionActionPair:
    """The exact P/T action pair for one Hilbert--Burch resolution."""

    scheme: PointScheme
    actions: tuple[ResolutionAction, ResolutionAction]

    def action(self, name: str) -> ResolutionAction:
        """Return the named P or T resolution action."""

        for action in self.actions:
            if action.name == name:
                return action
        raise KeyError(name)

    @property
    def order_three(self) -> bool:
        """Return the exact order-three result on both complex terms."""

        return all(
            action.target_action**3 == Matrix.identity(
                action.target_action.row_count,
                scalar_type=Eisenstein,
            )
            and action.source_action**3 == Matrix.identity(
                action.source_action.row_count,
                scalar_type=Eisenstein,
            )
            for action in self.actions
        )

    @property
    def target_commutator_scalar(self) -> Eisenstein | None:
        """Return the target-term projective commutator scalar."""

        return _commutator_scalar(
            self.action("P").target_action,
            self.action("T").target_action,
        )

    @property
    def source_commutator_scalar(self) -> Eisenstein | None:
        """Return the source-term projective commutator scalar."""

        return _commutator_scalar(
            self.action("P").source_action,
            self.action("T").source_action,
        )

    def as_record(self) -> dict[str, object]:
        """Serialize exact resolution actions and their relation checks."""

        return {
            "scheme": self.scheme.name,
            "actions": [action.as_record() for action in self.actions],
            "chain_equations": all(action.chain_equation for action in self.actions),
            "invertible": all(action.invertible for action in self.actions),
            "order_three": self.order_three,
            "target_commutator_scalar": (
                None if self.target_commutator_scalar is None
                else str(self.target_commutator_scalar)
            ),
            "source_commutator_scalar": (
                None if self.source_commutator_scalar is None
                else str(self.source_commutator_scalar)
            ),
            "status": "resolution-level action; Serre linearization pending",
        }


def tier_a_resolution_actions() -> tuple[ResolutionActionPair, ...]:
    """Derive exact P/T actions for the I3 and I6 resolutions."""

    return tuple(
        ResolutionActionPair(
            scheme,
            (_derive_action(scheme, "P"), _derive_action(scheme, "T")),
        )
        for scheme in point_schemes()
    )


__all__ = [
    "ResolutionAction",
    "ResolutionActionPair",
    "tier_a_resolution_actions",
]
