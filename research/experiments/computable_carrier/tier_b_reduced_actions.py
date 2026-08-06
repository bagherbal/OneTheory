"""Search exact deck lifts through reduced orbit Hilbert--Burch resolutions.

Owns:
    The finite target-orientation and cubic-scalar lift search for the four
    reduced length-three orbit resolutions, including chain equations, exact
    orders, termwise commutators, and scoped commuting-pair results.

Depends on:
    Exact Eisenstein matrices and polynomials, the published coordinate
    substitutions, and reduced orbit Hilbert--Burch schemes.

Must not:
    Treat a resolution lift as a sheaf linearization, infer quotient descent,
    construct a Serre extension, or promote a finite presentation no-go to a
    theorem about all equivariant sheaves.

Phase 0:
    The declared finite resolution-lift family is exhaustively audited; the
    full sheaf-level linearization and global descent problems remain open.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein

from .dp9_actions import published_coordinate_images
from .resolution_actions import (
    _left_constant_product,
    _right_constant_product,
    _solve_source_lift,
    _transformed_matrix,
)
from .tier_b_reduced_schemes import (
    _QUADRATIC_MONOMIALS,
    ReducedOrbitScheme,
    _coefficient_vector,
    tier_b_reduced_orbit_schemes,
)

CoordinateImage = tuple[tuple[Eisenstein, tuple[int, ...]], ...]
_CUBIC_ROOTS = (Eisenstein(1), OMEGA, OMEGA2)


def _row_coordinates(
    basis: tuple[tuple[Eisenstein, ...], ...],
    target: tuple[Eisenstein, ...],
) -> tuple[Eisenstein, ...]:
    """Express one exact row vector in an independent row basis."""

    basis_matrix = Matrix(basis, scalar_type=Eisenstein)
    augmented = Matrix(
        tuple(
            (*row, value)
            for row, value in zip(basis_matrix.transpose().rows, target, strict=True)
        ),
        scalar_type=Eisenstein,
    )
    reduced, pivots = augmented.rref()
    if any(
        all(reduced[row][column].is_zero() for column in range(basis_matrix.row_count))
        and not reduced[row][basis_matrix.row_count].is_zero()
        for row in range(reduced.row_count)
    ):
        raise ValueError("transformed quadratic escaped its exact vanishing basis")
    values = [Eisenstein(0) for _ in range(basis_matrix.row_count)]
    for row, pivot in enumerate(pivots):
        if pivot < basis_matrix.row_count:
            values[pivot] = reduced[row][basis_matrix.row_count]
    return tuple(values)


def _target_action(
    scheme: ReducedOrbitScheme,
    images: CoordinateImage,
) -> Matrix:
    """Return the exact coefficient action on the quadratic generator basis."""

    basis = tuple(
        _coefficient_vector(generator, _QUADRATIC_MONOMIALS)
        for generator in scheme.generators
    )
    transformed = tuple(
        _coefficient_vector(generator.substitute_monomials(images), _QUADRATIC_MONOMIALS)
        for generator in scheme.generators
    )
    return Matrix(
        tuple(_row_coordinates(basis, row) for row in transformed),
        scalar_type=Eisenstein,
    )


@dataclass(frozen=True, slots=True)
class ReducedResolutionAction:
    """One exact finite lift through a reduced orbit resolution."""

    scheme: ReducedOrbitScheme
    name: str
    coordinate_images: CoordinateImage
    orientation: str
    scalar: Eisenstein
    target_action: Matrix
    source_action: Matrix

    @property
    def chain_equation(self) -> bool:
        """Return whether the lifted maps commute with the transformed matrix."""

        matrix = self.scheme.resolution.matrix
        transformed = _transformed_matrix(matrix, self.coordinate_images)
        return _right_constant_product(matrix, self.source_action).rows == _left_constant_product(
            self.target_action,
            transformed,
        ).rows

    @property
    def invertible(self) -> bool:
        """Return whether both finite term maps are exact automorphisms."""

        return (
            not self.target_action.determinant().is_zero()
            and not self.source_action.determinant().is_zero()
        )

    @property
    def order_three(self) -> bool:
        """Return whether both finite term maps have exact order three."""

        return (
            self.target_action**3 == Matrix.identity(3, scalar_type=Eisenstein)
            and self.source_action**3 == Matrix.identity(2, scalar_type=Eisenstein)
        )

    @property
    def exact(self) -> bool:
        """Return the finite lift certificate."""

        return self.chain_equation and self.invertible and self.order_three

    def as_record(self) -> dict[str, object]:
        """Serialize the lift without calling it a sheaf linearization."""

        return {
            "scheme": self.scheme.orbit.identifier,
            "name": self.name,
            "orientation": self.orientation,
            "scalar": str(self.scalar),
            "target_action": [[str(value) for value in row] for row in self.target_action.rows],
            "source_action": [[str(value) for value in row] for row in self.source_action.rows],
            "chain_equation": self.chain_equation,
            "invertible": self.invertible,
            "order_three": self.order_three,
            "exact": self.exact,
            "status": "finite Hilbert--Burch lift only; sheaf linearization pending",
        }


@dataclass(frozen=True, slots=True)
class ReducedResolutionActionAudit:
    """Complete finite lift audit for one reduced orbit scheme."""

    scheme: ReducedOrbitScheme
    p_actions: tuple[ReducedResolutionAction, ...]
    t_actions: tuple[ReducedResolutionAction, ...]

    @property
    def exact(self) -> bool:
        """Return whether every enumerated lift passes its local exact gates."""

        return all(action.exact for action in (*self.p_actions, *self.t_actions))

    @property
    def commuting_pairs(self) -> tuple[tuple[int, int], ...]:
        """Return pairs commuting exactly on both resolution terms."""

        return tuple(
            (p_index, t_index)
            for p_index, p_action in enumerate(self.p_actions)
            for t_index, t_action in enumerate(self.t_actions)
            if p_action.target_action @ t_action.target_action
            == t_action.target_action @ p_action.target_action
            and p_action.source_action @ t_action.source_action
            == t_action.source_action @ p_action.source_action
        )

    @property
    def complete_commuting_pair_count(self) -> int:
        """Return the exact number of honest finite commuting lift pairs."""

        return len(self.commuting_pairs)

    @property
    def scoped_no_pair(self) -> bool:
        """Return the scoped finite no-pair result."""

        return self.exact and self.complete_commuting_pair_count == 0

    def as_record(self) -> dict[str, object]:
        """Serialize the finite lift family and its explicit boundary."""

        return {
            "scheme": self.scheme.orbit.identifier,
            "p_action_count": len(self.p_actions),
            "t_action_count": len(self.t_actions),
            "p_actions": [action.as_record() for action in self.p_actions],
            "t_actions": [action.as_record() for action in self.t_actions],
            "exact": self.exact,
            "commuting_pairs": [list(pair) for pair in self.commuting_pairs],
            "complete_commuting_pair_count": self.complete_commuting_pair_count,
            "scoped_no_pair": self.scoped_no_pair,
            "status": (
                "finite reduced-resolution lift audit only; full sheaf-level "
                "linearization and quotient descent remain unresolved"
            ),
        }


def _actions(
    scheme: ReducedOrbitScheme,
    name: str,
) -> tuple[ReducedResolutionAction, ...]:
    """Enumerate all exact order-three target orientations and scalars."""

    images = published_coordinate_images(name)
    matrix = scheme.resolution.matrix
    transformed = _transformed_matrix(matrix, images)
    base = _target_action(scheme, images)
    result = []
    for orientation, target_base in (("base", base), ("transpose", base.transpose())):
        for scalar in _CUBIC_ROOTS:
            target = target_base.scale(scalar)
            source = _solve_source_lift(matrix, transformed, target)
            if source is None:
                continue
            action = ReducedResolutionAction(
                scheme,
                name,
                images,
                orientation,
                scalar,
                target,
                source,
            )
            if action.exact:
                result.append(action)
    return tuple(result)


@cache
def tier_b_reduced_resolution_actions() -> tuple[ReducedResolutionActionAudit, ...]:
    """Audit the complete finite resolution-lift family for reduced schemes."""

    audits = tuple(
        ReducedResolutionActionAudit(scheme, _actions(scheme, "P"), _actions(scheme, "T"))
        for scheme in tier_b_reduced_orbit_schemes()
    )
    if not all(audit.exact for audit in audits):
        raise ValueError("reduced-resolution lift family failed exact gates")
    return audits


__all__ = [
    "ReducedResolutionAction",
    "ReducedResolutionActionAudit",
    "tier_b_reduced_resolution_actions",
]
