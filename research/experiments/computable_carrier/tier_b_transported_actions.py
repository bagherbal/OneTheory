"""Audit resolution lifts for the transported Tier B scheme category.

Owns:
    Exact degree-block target actions, source-lift solving, order-three checks,
    and commuting-pair enumeration for all 24 transported invariant scheme
    presentations.

Depends on:
    Exact Eisenstein matrices, polynomial substitutions, published deck lifts,
    and transported Hilbert--Burch scheme presentations.

Must not:
    Call a presentation lift a sheaf linearization, construct a Serre object,
    infer quotient descent, or promote a finite mixed-degree no-go beyond its
    declared resolution family.

Phase 0:
    The transported resolution-lift family is audited exactly; global sheaf
    equivariance, Serre construction, and quotient descent remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from itertools import product

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein

from .dp9_actions import published_coordinate_images
from .resolution_actions import (
    _left_constant_product,
    _right_constant_product,
    _solve_source_lift,
    _transformed_matrix,
)
from .tier_b_reduced_actions import _row_coordinates
from .tier_b_reduced_thickenings import (
    TransportedInvariantScheme,
    tier_b_transported_invariant_schemes,
)

CoordinateImage = tuple[tuple[Eisenstein, tuple[int, ...]], ...]
_CUBIC_ROOTS = (Eisenstein(1), OMEGA, OMEGA2)


def _monomials(degree: int) -> tuple[tuple[int, int, int], ...]:
    """Enumerate the exact three-variable monomial basis of one degree."""

    return tuple(
        sorted(
            ((a, b, degree - a - b) for a in range(degree + 1) for b in range(degree + 1 - a)),
            reverse=True,
        )
    )


def _target_blocks(
    scheme: TransportedInvariantScheme,
    images: CoordinateImage,
) -> tuple[tuple[tuple[int, ...], Matrix], ...]:
    """Build the exact transformed-generator action degree by degree."""

    blocks = []
    for degree in sorted({generator.degree for generator in scheme.generators}):
        indices = tuple(
            index
            for index, generator in enumerate(scheme.generators)
            if generator.degree == degree
        )
        monomials = _monomials(degree)
        basis = tuple(
            tuple(scheme.generators[index].coefficient(monomial) for monomial in monomials)
            for index in indices
        )
        rows = tuple(
            _row_coordinates(
                basis,
                tuple(
                    scheme.generators[index]
                    .substitute_monomials(images)
                    .coefficient(monomial)
                    for monomial in monomials
                ),
            )
            for index in indices
        )
        blocks.append((indices, Matrix(rows, scalar_type=Eisenstein)))
    return tuple(blocks)


def _assemble_target(
    generator_count: int,
    blocks: tuple[tuple[tuple[int, ...], Matrix], ...],
    orientations: tuple[bool, ...],
    scalars: tuple[Eisenstein, ...],
) -> Matrix:
    """Assemble one exact block-diagonal target action."""

    rows = [[Eisenstein(0) for _ in range(generator_count)] for _ in range(generator_count)]
    for (indices, base), transpose, scalar in zip(
        blocks,
        orientations,
        scalars,
        strict=True,
    ):
        block = (base.transpose() if transpose else base).scale(scalar)
        for row, global_row in enumerate(indices):
            for column, global_column in enumerate(indices):
                rows[global_row][global_column] = block[row][column]
    return Matrix(rows, scalar_type=Eisenstein)


@dataclass(frozen=True, slots=True)
class TransportedResolutionAction:
    """One exact finite lift through a transported mixed-degree resolution."""

    scheme: TransportedInvariantScheme
    name: str
    coordinate_images: CoordinateImage
    orientations: tuple[bool, ...]
    scalars: tuple[Eisenstein, ...]
    target_action: Matrix
    source_action: Matrix

    @property
    def chain_equation(self) -> bool:
        """Return whether the two term maps satisfy the transformed chain equation."""

        matrix = self.scheme.resolution.matrix
        transformed = _transformed_matrix(matrix, self.coordinate_images)
        return _right_constant_product(matrix, self.source_action).rows == _left_constant_product(
            self.target_action,
            transformed,
        ).rows

    @property
    def invertible(self) -> bool:
        """Return whether both resolution-term actions are invertible."""

        return (
            not self.target_action.determinant().is_zero()
            and not self.source_action.determinant().is_zero()
        )

    @property
    def order_three(self) -> bool:
        """Return whether both resolution-term actions have order three."""

        return (
            self.target_action**3 == Matrix.identity(
                self.target_action.row_count,
                scalar_type=Eisenstein,
            )
            and self.source_action**3 == Matrix.identity(
                self.source_action.row_count,
                scalar_type=Eisenstein,
            )
        )

    @property
    def exact(self) -> bool:
        """Return the complete finite lift certificate."""

        return self.chain_equation and self.invertible and self.order_three

    def as_record(self) -> dict[str, object]:
        """Serialize the exact lift and its unresolved sheaf boundary."""

        return {
            "scheme": self.scheme.name,
            "name": self.name,
            "orientations": list(self.orientations),
            "scalars": [str(value) for value in self.scalars],
            "target_action": [[str(value) for value in row] for row in self.target_action.rows],
            "source_action": [[str(value) for value in row] for row in self.source_action.rows],
            "chain_equation": self.chain_equation,
            "invertible": self.invertible,
            "order_three": self.order_three,
            "exact": self.exact,
            "status": "finite transported-resolution lift only; sheaf linearization pending",
        }


@dataclass(frozen=True, slots=True)
class TransportedResolutionActionAudit:
    """Complete finite lift audit for one transported scheme."""

    scheme: TransportedInvariantScheme
    p_actions: tuple[TransportedResolutionAction, ...]
    t_actions: tuple[TransportedResolutionAction, ...]

    @property
    def exact(self) -> bool:
        """Return whether all enumerated P/T lifts pass exact gates."""

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
        """Return the exact number of complete finite commuting pairs."""

        return len(self.commuting_pairs)

    @property
    def scoped_no_pair(self) -> bool:
        """Return the scoped finite no-pair result."""

        return self.exact and self.complete_commuting_pair_count == 0

    def as_record(self) -> dict[str, object]:
        """Serialize the action family and explicit scope boundary."""

        return {
            "scheme": self.scheme.name,
            "length": self.scheme.length,
            "p_action_count": len(self.p_actions),
            "t_action_count": len(self.t_actions),
            "p_actions": [item.as_record() for item in self.p_actions],
            "t_actions": [item.as_record() for item in self.t_actions],
            "exact": self.exact,
            "complete_commuting_pair_count": self.complete_commuting_pair_count,
            "scoped_no_pair": self.scoped_no_pair,
            "status": (
                "finite transported-resolution lift audit only; full sheaf "
                "linearization and quotient descent remain unresolved"
            ),
        }


def _actions(
    scheme: TransportedInvariantScheme,
    name: str,
) -> tuple[TransportedResolutionAction, ...]:
    """Enumerate all degree-block orientations and cubic-root scalars."""

    images = published_coordinate_images(name)
    matrix = scheme.resolution.matrix
    transformed = _transformed_matrix(matrix, images)
    blocks = _target_blocks(scheme, images)
    result = []
    for orientations in product((False, True), repeat=len(blocks)):
        for scalars in product(_CUBIC_ROOTS, repeat=len(blocks)):
            target = _assemble_target(len(scheme.generators), blocks, orientations, scalars)
            source = _solve_source_lift(matrix, transformed, target)
            if source is None:
                continue
            action = TransportedResolutionAction(
                scheme,
                name,
                images,
                orientations,
                scalars,
                target,
                source,
            )
            if action.exact:
                result.append(action)
    return tuple(result)


@cache
def tier_b_transported_resolution_actions() -> tuple[TransportedResolutionActionAudit, ...]:
    """Audit finite resolution lifts for every transported Tier B scheme."""

    audits = tuple(
        TransportedResolutionActionAudit(scheme, _actions(scheme, "P"), _actions(scheme, "T"))
        for scheme in tier_b_transported_invariant_schemes()
    )
    if not all(audit.exact for audit in audits):
        raise ValueError("transported resolution-lift family failed exact gates")
    return audits


__all__ = [
    "TransportedResolutionAction",
    "TransportedResolutionActionAudit",
    "tier_b_transported_resolution_actions",
]
