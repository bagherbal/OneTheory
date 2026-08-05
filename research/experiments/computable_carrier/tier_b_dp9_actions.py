"""Audit dP9 deck actions on Tier B ideal totalizations.

Owns:
    Exact P/T chain maps on the dP9 line-bundle totalizations of the bounded
    monomial Hilbert--Burch resolutions, their induced H1 matrices, and the
    common fixed-subspace diagnostic.

Depends on:
    Tier B monomial resolution lifts, exact dP9 line-bundle cohomology, the
    signed ideal-resolution totalizations, and the published coordinate deck
    substitutions. It does not consume observations or physical parameters.

Must not:
    Identify ideal-resolution H1 with a Serre Ext group, call a fixed vector a
    descended sheaf section, infer a bundle linearization from this action, or
    promote a zero invariant subspace to a global physical no-go.

Phase 0:
    The bounded dP9 presentation actions are exact chain-level diagnostics;
    Serre comparison, global sheafification, quotient descent, and promotion
    remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.homological import ChainMap, CochainComplex, CoordinateVector, LinearMap
from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein

from .dp9_actions import _line_bundle_action, published_coordinate_images
from .tier_b_dp9_ideals import (
    DPSurfaceMonomialIdealResolution,
    tier_b_dp9_monomial_ideal_resolutions,
)
from .tier_b_monomial import MonomialResolutionActionAudit, tier_b_monomial_resolution_actions


def _total_cells(
    resolution: DPSurfaceMonomialIdealResolution,
) -> tuple[tuple[int, int], ...]:
    """Return every signed-totalization cell in deterministic order."""

    cells = {cell for cell, _ in resolution.bicomplex.components}
    cells.update(cell for cell, _ in resolution.bicomplex.horizontal)
    cells.update(cell for cell, _ in resolution.bicomplex.vertical)
    return tuple(sorted(cells))


def _term_action(
    bundles,
    matrix: Matrix,
    sheaf_degree: int,
    images,
) -> LinearMap:
    """Combine a free-term action with exact line-bundle pullback."""

    if matrix.row_count != len(bundles) or matrix.column_count != len(bundles):
        raise ValueError("resolution action rank does not match its dP9 term")
    blocks: list[list[LinearMap]] = []
    for target_index, target_bundle in enumerate(bundles):
        row: list[LinearMap] = []
        for source_index, source_bundle in enumerate(bundles):
            coefficient = matrix[target_index][source_index]
            source_space = source_bundle.complex.spaces.space(sheaf_degree)
            target_space = target_bundle.complex.spaces.space(sheaf_degree)
            if coefficient.is_zero():
                row.append(LinearMap.zero(source_space, target_space))
                continue
            if (
                source_bundle.base_degree != target_bundle.base_degree
                or source_bundle.fiber_degree != target_bundle.fiber_degree
            ):
                raise ValueError("deck action mixes incompatible dP9 line bundles")
            row.append(
                _line_bundle_action(target_bundle, sheaf_degree, images).scale(coefficient)
            )
        blocks.append(row)
    return LinearMap.block(blocks)


def _total_action(
    resolution: DPSurfaceMonomialIdealResolution,
    action_audit: MonomialResolutionActionAudit,
    name: str,
) -> ChainMap:
    """Build one exact degree-preserving action on the signed total complex."""

    total = resolution.total
    action = action_audit.actions.action(name)
    matrices = {-1: action.source_action, 0: action.target_action}
    degree_cells: dict[int, tuple[tuple[int, int], ...]] = {}
    for cell in _total_cells(resolution):
        degree = sum(cell)
        degree_cells[degree] = tuple(sorted((*degree_cells.get(degree, ()), cell)))
    components: dict[int, LinearMap] = {}
    for degree in total.degrees:
        maps = []
        for horizontal_degree, vertical_degree in degree_cells.get(degree, ()):
            bundles = (
                resolution.source_bundles
                if horizontal_degree == -1
                else resolution.target_bundles
            )
            maps.append(
                _term_action(
                    bundles,
                    matrices[horizontal_degree],
                    vertical_degree,
                    published_coordinate_images(name),
                )
            )
        if not maps:
            components[degree] = LinearMap.zero(
                total.spaces.space(degree),
                total.spaces.space(degree),
            )
            continue
        combined = maps[0]
        for map_ in maps[1:]:
            combined = LinearMap.direct_sum(combined, map_)
        if combined.domain != total.spaces.space(degree):
            raise ValueError("dP9 action domain basis does not match totalization")
        if combined.codomain != total.spaces.space(degree):
            raise ValueError("dP9 action codomain basis does not match totalization")
        components[degree] = combined
    return ChainMap(total, total, components)


def _induced_action(
    action: ChainMap,
    complex_: CochainComplex,
    degree: int,
    representatives: tuple[CoordinateVector, ...],
) -> Matrix | None:
    """Express a chain-map action in an exact boundary-plus-representative basis."""

    if not representatives:
        return None
    space = complex_.spaces.space(degree)
    boundaries = complex_.boundaries(degree)
    columns = (*boundaries, *representatives)
    basis_matrix = Matrix(
        tuple(
            tuple(vector.coordinates[column] for vector in columns)
            for column in range(space.dimension)
        ),
        scalar_type=space.scalar_type,
    )
    result_columns = []
    for representative in representatives:
        image = action.component(degree)(representative)
        augmented = Matrix(
            tuple(
                (*row, image.coordinates[row_index])
                for row_index, row in enumerate(basis_matrix.rows)
            ),
            scalar_type=space.scalar_type,
        )
        reduced, pivots = augmented.rref()
        unknown_count = len(columns)
        if any(
            all(reduced[row][column].is_zero() for column in range(unknown_count))
            and not reduced[row][unknown_count].is_zero()
            for row in range(reduced.row_count)
        ):
            raise ValueError("chain-map image is not in the cycle span")
        coordinates = [Eisenstein(0) for _ in columns]
        for row, pivot in enumerate(pivots):
            if pivot < unknown_count:
                coordinates[pivot] = reduced[row][unknown_count]
        result_columns.append(tuple(coordinates[len(boundaries):]))
    return Matrix(
        tuple(
            tuple(result_columns[column][row] for column in range(len(result_columns)))
            for row in range(len(result_columns))
        ),
        scalar_type=space.scalar_type,
    )


def _fixed_representatives(
    representatives: tuple[CoordinateVector, ...],
    p_action: Matrix | None,
    t_action: Matrix | None,
) -> tuple[CoordinateVector, ...]:
    """Return exact common fixed representatives in the total complex."""

    if not representatives or p_action is None or t_action is None:
        return ()
    identity = Matrix.identity(len(representatives), scalar_type=Eisenstein)
    equations = Matrix(
        (*((p_action - identity).rows), *((t_action - identity).rows)),
        scalar_type=Eisenstein,
    )
    vectors = equations.nullspace()
    space = representatives[0].space
    return tuple(
        CoordinateVector(
            space,
            tuple(
                sum(
                    (
                        vector.values[index] * representative.coordinates[row]
                        for index, representative in enumerate(representatives)
                    ),
                    Eisenstein(0),
                )
                for row in range(space.dimension)
            ),
        )
        for vector in vectors
    )


def _matrix_record(matrix: Matrix | None) -> list[list[str]] | None:
    """Serialize an induced matrix without converting exact scalars to floats."""

    return None if matrix is None else [[str(value) for value in row] for row in matrix.rows]


@dataclass(frozen=True, slots=True)
class TierBDPSurfaceDeckActionAudit:
    """One exact deck-action audit for a Tier B ideal totalization."""

    resolution: DPSurfaceMonomialIdealResolution
    p_action: ChainMap
    t_action: ChainMap
    p_induced: Matrix | None
    t_induced: Matrix | None
    invariant_representatives: tuple[CoordinateVector, ...]

    @property
    def total_squared_zero(self) -> bool:
        """Return the underlying signed totalization square-zero gate."""

        return self.resolution.squared_zero

    @property
    def actions_commute(self) -> bool:
        """Return whether P and T commute on the total complex."""

        return self.p_action.compose(self.t_action) == self.t_action.compose(self.p_action)

    @property
    def actions_order_three(self) -> bool:
        """Return whether both total actions have exact order three."""

        identity = ChainMap.identity(self.resolution.total)
        return (
            self.p_action.compose(self.p_action).compose(self.p_action) == identity
            and self.t_action.compose(self.t_action).compose(self.t_action) == identity
        )

    @property
    def invariant_h1_dimension(self) -> int:
        """Return the common fixed dimension of the induced H1 action."""

        return len(self.invariant_representatives)

    def as_record(self) -> dict[str, object]:
        """Serialize chain-level and induced-action gates with their scope."""

        return {
            "scheme": self.resolution.scheme.name,
            "fiber_degree": self.resolution.fiber_degree,
            "total_h1_dimension": self.resolution.total.cohomology_dimension(1),
            "invariant_h1_dimension": self.invariant_h1_dimension,
            "p_induced": _matrix_record(self.p_induced),
            "t_induced": _matrix_record(self.t_induced),
            "total_squared_zero": self.total_squared_zero,
            "actions_commute": self.actions_commute,
            "actions_order_three": self.actions_order_three,
            "status": (
                "exact dP9 ideal-resolution deck action; Serre Ext comparison, "
                "global sheafification, and quotient descent remain unresolved"
            ),
        }


def tier_b_dp9_deck_action_audits(
    resolutions: tuple[DPSurfaceMonomialIdealResolution, ...] | None = None,
    actions: tuple[MonomialResolutionActionAudit, ...] | None = None,
) -> tuple[TierBDPSurfaceDeckActionAudit, ...]:
    """Build exact P/T actions for every bounded Tier B ideal resolution."""

    selected = tier_b_dp9_monomial_ideal_resolutions() if resolutions is None else resolutions
    resolution_actions = (
        tier_b_monomial_resolution_actions() if actions is None else actions
    )
    if len(selected) != len(resolution_actions):
        raise ValueError("Tier B dP9 actions require matching resolution and lift counts")
    results = []
    for resolution, action_audit in zip(selected, resolution_actions, strict=True):
        p_action = _total_action(resolution, action_audit, "P")
        t_action = _total_action(resolution, action_audit, "T")
        representatives = resolution.total.cohomology_representatives(1)
        p_induced = _induced_action(p_action, resolution.total, 1, representatives)
        t_induced = _induced_action(t_action, resolution.total, 1, representatives)
        result = TierBDPSurfaceDeckActionAudit(
            resolution,
            p_action,
            t_action,
            p_induced,
            t_induced,
            _fixed_representatives(representatives, p_induced, t_induced),
        )
        if not result.total_squared_zero or not result.actions_commute:
            raise ValueError("Tier B dP9 deck action failed its exact chain gate")
        results.append(result)
    return tuple(results)


__all__ = ["TierBDPSurfaceDeckActionAudit", "tier_b_dp9_deck_action_audits"]
