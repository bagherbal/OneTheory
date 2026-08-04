"""Compute finite dual-presentation cokernels of Tier A resolutions.

Owns:
    The lowest graded dual Hilbert--Burch presentations, exact quotient
    representatives, induced semilinear P/T actions, and their projective
    commutator diagnostics for the I3/I6 schemes.

Depends on:
    Exact point schemes and derived Hilbert--Burch resolution actions, plus
    Eisenstein linear algebra. The construction is a chain-level diagnostic.

Must not:
    Call a graded cokernel a sheaf Ext group without the projective comparison,
    identify its representatives with published Serre rays, or infer a bundle
    linearization from a finite quotient action.

Phase 0:
    Exact dual-presentation representatives are available; projective
    sheafification, Serre comparison, and honest descent remain unresolved.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import product

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from onetheory.models.heterotic_schoen.visible import PointScheme

from .resolution_actions import ResolutionAction, tier_a_resolution_actions

Monomial = tuple[int, ...]
BasisLabel = tuple[int, Monomial]
_UNITS = (
    Eisenstein(1),
    OMEGA,
    OMEGA2,
    -Eisenstein(1),
    -OMEGA,
    -OMEGA2,
)


def _monomials(total_degree: int, variable_count: int) -> tuple[Monomial, ...]:
    """Enumerate standard monomials of one exact total degree."""

    if total_degree < 0:
        return ()
    return tuple(
        exponents
        for exponents in product(range(total_degree + 1), repeat=variable_count)
        if sum(exponents) == total_degree
    )


def _presentation(
    scheme: PointScheme,
) -> tuple[int, tuple[BasisLabel, ...], tuple[BasisLabel, ...], Matrix]:
    """Build the lowest graded dual presentation ``F0* -> F1*``."""

    matrix = scheme.resolution.matrix
    generator_degrees = {
        generator.degree for generator in scheme.ideal_generators if not generator.is_zero()
    }
    entry_degrees = {
        entry.degree for row in matrix for entry in row if not entry.is_zero()
    }
    if len(generator_degrees) != 1 or len(entry_degrees) != 1:
        raise ValueError(f"{scheme.name} resolution is not homogeneous")
    generator_degree = next(iter(generator_degrees))
    entry_degree = next(iter(entry_degrees))
    source_degree = 0
    target_degree = source_degree + entry_degree
    source_monomials = _monomials(source_degree, matrix[0][0].variable_count)
    target_monomials = _monomials(target_degree, matrix[0][0].variable_count)
    source_basis = tuple(
        (row, monomial)
        for row in range(len(matrix))
        for monomial in source_monomials
    )
    target_basis = tuple(
        (column, monomial)
        for column in range(len(matrix[0]))
        for monomial in target_monomials
    )
    rows = []
    for column, target_monomial in target_basis:
        rows.append(
            tuple(
                matrix[row][column].coefficient(
                    tuple(target - source for target, source in zip(
                        target_monomial,
                        source_monomial,
                        strict=True,
                    ))
                )
                if all(
                    target >= source
                    for target, source in zip(
                        target_monomial,
                        source_monomial,
                        strict=True,
                    )
                )
                else Eisenstein(0)
                for row, source_monomial in source_basis
            )
        )
    return (
        -generator_degree,
        source_basis,
        target_basis,
        Matrix(rows, scalar_type=Eisenstein),
    )


def _inverse_images(
    images: tuple[tuple[Eisenstein, Monomial], ...],
) -> tuple[tuple[Eisenstein, Monomial], ...]:
    """Invert a monomial coordinate substitution exactly."""

    inverse: list[tuple[Eisenstein, Monomial] | None] = [None] * len(images)
    for source, (scalar, image) in enumerate(images):
        target = image.index(1)
        inverse[target] = (
            Eisenstein(1) / scalar,
            tuple(1 if index == source else 0 for index in range(len(images))),
        )
    if any(image is None for image in inverse):
        raise ValueError("coordinate action is not a permutation monomial map")
    return tuple(image for image in inverse if image is not None)


def _target_action(
    basis: tuple[BasisLabel, ...],
    action: ResolutionAction,
) -> Matrix:
    """Build the inverse-substitution transpose action on ``F1*``."""

    inverse_images = _inverse_images(action.coordinate_images)
    dual = action.source_action.transpose()
    rows = [[Eisenstein(0) for _ in basis] for _ in basis]
    for source_index, (source_label, source_monomial) in enumerate(basis):
        scalar, image_monomial = inverse_images[source_monomial.index(1)]
        for target_label in range(dual.row_count):
            target_index = basis.index((target_label, image_monomial))
            rows[target_index][source_index] += dual[target_label][source_label] * scalar
    return Matrix(rows, scalar_type=Eisenstein)


def _quotient_action(
    presentation: Matrix,
    target_basis: tuple[BasisLabel, ...],
    action: ResolutionAction,
) -> tuple[Matrix, bool, tuple[int, ...]]:
    """Descend one target action to a deterministic cokernel complement."""

    image_columns = presentation.rref()[1]
    pivot_rows = presentation.transpose().rref()[1]
    representatives = tuple(
        index for index in range(presentation.row_count) if index not in pivot_rows
    )
    target_action = _target_action(target_basis, action)
    columns = [
        tuple(presentation[row][column] for row in range(presentation.row_count))
        for column in image_columns
    ]
    columns.extend(
        tuple(
            Eisenstein(1) if row == representative else Eisenstein(0)
            for row in range(presentation.row_count)
        )
        for representative in representatives
    )
    decomposition = Matrix(zip(*columns, strict=True), scalar_type=Eisenstein)
    inverse_decomposition = decomposition.inverse()
    quotient_columns: list[tuple[Eisenstein, ...]] = []
    preserves_relations = True
    for image_column in image_columns:
        image = Matrix(
            (
                (sum(
                    (
                        target_action[row][source] * presentation[source][image_column]
                        for source in range(presentation.row_count)
                    ),
                    Eisenstein(0),
                ),)
                for row in range(presentation.row_count)
            ),
            scalar_type=Eisenstein,
        )
        coordinates = inverse_decomposition @ image
        preserves_relations = preserves_relations and all(
            coordinates[index + len(image_columns)][0].is_zero()
            for index in range(len(representatives))
        )
    for representative in representatives:
        image = Matrix(
            (
                (target_action[row][representative],)
                for row in range(presentation.row_count)
            ),
            scalar_type=Eisenstein,
        )
        coordinates = inverse_decomposition @ image
        quotient_columns.append(
            tuple(
                coordinates[index + len(image_columns)][0]
                for index in range(len(representatives))
            )
        )
    quotient = Matrix(zip(*quotient_columns, strict=True), scalar_type=Eisenstein)
    return quotient, preserves_relations, representatives


def _commutator_scalar(left: Matrix, right: Matrix) -> Eisenstein | None:
    """Return the exact unit relating two projective matrix products."""

    for scalar in _UNITS:
        if left @ right == (right @ left).scale(scalar):
            return scalar
    return None


@dataclass(frozen=True, slots=True)
class DualCokernelAction:
    """One exact action induced on a dual-presentation cokernel."""

    name: str
    matrix: Matrix
    preserves_relations: bool

    def as_record(self) -> dict[str, object]:
        """Serialize the quotient action and its relation certificate."""

        return {
            "name": self.name,
            "matrix": [[str(value) for value in row] for row in self.matrix.rows],
            "preserves_relations": self.preserves_relations,
            "order_three": self.matrix**3 == Matrix.identity(
                self.matrix.row_count,
                scalar_type=Eisenstein,
            ),
        }


@dataclass(frozen=True, slots=True)
class DualResolutionCokernel:
    """A finite graded cokernel with exact representatives and action data."""

    scheme: PointScheme
    degree: int
    source_basis: tuple[BasisLabel, ...]
    target_basis: tuple[BasisLabel, ...]
    presentation: Matrix
    representative_indices: tuple[int, ...]
    actions: tuple[DualCokernelAction, ...]

    @property
    def dimension(self) -> int:
        """Return the exact quotient dimension."""

        return len(self.representative_indices)

    @property
    def action_commutes(self) -> bool:
        """Return whether the induced P/T matrices commute exactly."""

        p = self.action("P").matrix
        t = self.action("T").matrix
        return p @ t == t @ p

    @property
    def commutator_scalar(self) -> Eisenstein | None:
        """Return the exact projective commutator factor, if any."""

        return _commutator_scalar(self.action("P").matrix, self.action("T").matrix)

    def action(self, name: str) -> DualCokernelAction:
        """Return one named induced quotient action."""

        for action in self.actions:
            if action.name == name:
                return action
        raise KeyError(name)

    def as_record(self) -> dict[str, object]:
        """Serialize the exact finite presentation without a sheaf claim."""

        return {
            "scheme": self.scheme.name,
            "graded_degree": self.degree,
            "source_basis": [[row, list(monomial)] for row, monomial in self.source_basis],
            "target_basis": [[column, list(monomial)] for column, monomial in self.target_basis],
            "presentation_shape": list(self.presentation.shape),
            "presentation_rank": self.presentation.rank(),
            "representative_indices": list(self.representative_indices),
            "representative_vectors": [
                [
                    "1" if index == representative else "0"
                    for index in range(self.presentation.row_count)
                ]
                for representative in self.representative_indices
            ],
            "dimension": self.dimension,
            "actions": [action.as_record() for action in self.actions],
            "action_commutes": self.action_commutes,
            "commutator_scalar": (
                None if self.commutator_scalar is None else str(self.commutator_scalar)
            ),
            "status": (
                "dual graded cokernel diagnostic; projective sheaf and Serre "
                "comparison remain unresolved"
            ),
        }


def dual_resolution_cokernel(
    scheme: PointScheme,
    actions: Sequence[ResolutionAction],
) -> DualResolutionCokernel:
    """Construct one finite dual-resolution cokernel and its induced actions."""

    if tuple(action.scheme for action in actions) != (scheme,) * len(actions):
        raise ValueError("cokernel actions must belong to the declared scheme")
    degree, source_basis, target_basis, presentation = _presentation(scheme)
    quotient_actions = []
    representative_indices: tuple[int, ...] | None = None
    for action in actions:
        quotient, preserves_relations, representatives = _quotient_action(
            presentation,
            target_basis,
            action,
        )
        if representative_indices is None:
            representative_indices = representatives
        elif representative_indices != representatives:
            raise ValueError("quotient representatives changed between actions")
        quotient_actions.append(DualCokernelAction(action.name, quotient, preserves_relations))
    if representative_indices is None:
        raise ValueError("a dual cokernel requires at least one action")
    return DualResolutionCokernel(
        scheme,
        degree,
        source_basis,
        target_basis,
        presentation,
        representative_indices,
        tuple(quotient_actions),
    )


def tier_a_dual_cokernels() -> tuple[DualResolutionCokernel, ...]:
    """Build the exact I3/I6 dual-presentation diagnostics."""

    pairs = tier_a_resolution_actions()
    return tuple(
        dual_resolution_cokernel(pair.scheme, pair.actions)
        for pair in pairs
    )


__all__ = [
    "DualCokernelAction",
    "DualResolutionCokernel",
    "dual_resolution_cokernel",
    "tier_a_dual_cokernels",
]
