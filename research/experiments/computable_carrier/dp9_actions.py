"""Audit the published deck action on the exact dP9 Hom totalization.

Owns:
    The zero-fiber pullback actions induced by the published Schoen coordinate
    lifts, their typed actions on dP9 line-bundle cohomology, the combined
    presentation-term actions, and the exact invariant degree-one audit.

Depends on:
    The exact dP9 derived-Hom total complex, production Schoen Heisenberg
    lifts, exact Eisenstein linear algebra, and the derived presentation
    actions. It does not consume observations or physical parameters.

Must not:
    Treat an action on the presentation-level totalization as a global Serre
    linearization, infer quotient descent from an invariant dimension, or
    construct a rank-four bundle when the action gate is unresolved.

Phase 0:
    The zero-fiber dP9 action diagnostic is exact when its chain-map checks
    pass; global sheafification, quotient descent, and physical promotion
    remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.homological import ChainMap, CoordinateVector, LinearMap
from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry

from .dp9_homology import DPSurfaceDerivedHom
from .dp9_linebundles import _p2_basis
from .projective_hom_action import _presentation_term_actions
from .resolution_actions import ResolutionActionPair, tier_a_resolution_actions

CoordinateImage = tuple[tuple[Eisenstein, tuple[int, ...]], ...]


def _matrix_coordinate_images(matrix: Matrix) -> CoordinateImage:
    """Convert a monomial three-coordinate lift into substitution data."""

    images: list[tuple[Eisenstein, tuple[int, ...]]] = []
    for row in range(matrix.row_count):
        nonzero = [
            (column, matrix[row][column])
            for column in range(matrix.column_count)
            if not matrix[row][column].is_zero()
        ]
        if len(nonzero) != 1:
            raise ValueError("published deck lift is not monomial")
        column, coefficient = nonzero[0]
        images.append(
            (
                coefficient,
                tuple(1 if index == column else 0 for index in range(matrix.column_count)),
            )
        )
    return tuple(images)


@cache
def published_coordinate_images(name: str) -> CoordinateImage:
    """Return the exact P/T substitutions from the production Heisenberg lifts."""

    geometry = schoen_geometry()
    if name == "P":
        lift = geometry.heisenberg.t
    elif name == "T":
        lift = geometry.heisenberg.p.inverse() @ geometry.heisenberg.t
    else:
        raise KeyError(name)
    images = _matrix_coordinate_images(lift)
    expected = next(
        action.coordinate_images
        for action in tier_a_resolution_actions()[0].actions
        if action.name == name
    )
    if images != expected:
        raise ValueError("production and resolution deck substitutions disagree")
    return images


def _monomial_action(
    basis: tuple[tuple[int, ...], ...],
    images: CoordinateImage,
) -> tuple[tuple[Eisenstein, ...], ...]:
    """Evaluate one exact monomial substitution on an ordered basis."""

    index = {monomial: position for position, monomial in enumerate(basis)}
    rows = [
        [Eisenstein(0) for _ in basis]
        for _ in basis
    ]
    for source_position, source_monomial in enumerate(basis):
        target_monomial = [0] * len(source_monomial)
        scalar = Eisenstein(1)
        for power, (image_scalar, image_exponents) in zip(
            source_monomial,
            images,
            strict=True,
        ):
            scalar *= image_scalar**power
            target_monomial = [
                current + power * exponent
                for current, exponent in zip(
                    target_monomial,
                    image_exponents,
                    strict=True,
                )
            ]
        target_position = index.get(tuple(target_monomial))
        if target_position is None:
            raise ValueError("deck action escaped the exact monomial basis")
        rows[target_position][source_position] += scalar
    return tuple(tuple(row) for row in rows)


def _line_bundle_action(
    bundle,
    degree: int,
    images: CoordinateImage,
) -> LinearMap:
    """Build the zero-fiber action on one restricted line-bundle space."""

    if bundle.fiber_degree != 0:
        raise ValueError("the current dP9 deck audit supports fiber degree zero only")
    space = bundle.complex.spaces.space(degree)
    if space.dimension == 0:
        return LinearMap.zero(space, space)
    if degree == 0:
        basis = _p2_basis(bundle.base_degree, 0)
    elif degree == 2:
        basis = _p2_basis(bundle.base_degree, 2)
    else:
        raise ValueError("nonzero dP9 fiber-zero cohomology has unexpected degree")
    matrix = _monomial_action(basis, images)
    if len(matrix) != space.dimension:
        raise ValueError("line-bundle action basis dimension mismatch")
    return LinearMap(space, space, matrix)


def _term_action(
    homology: DPSurfaceDerivedHom,
    parent_degree: int,
    sheaf_degree: int,
    matrix: Matrix,
    images: CoordinateImage,
) -> LinearMap:
    """Combine generator action and line-bundle pullback in one cell."""

    bundles = dict(homology.bundles)[parent_degree]
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
                raise ValueError("deck action mixes incompatible line-bundle degrees")
            row.append(
                _line_bundle_action(target_bundle, sheaf_degree, images).scale(coefficient)
            )
        blocks.append(row)
    return LinearMap.block(blocks)


def _total_cells(homology: DPSurfaceDerivedHom) -> tuple[tuple[int, int], ...]:
    """Return all bicomplex cells in the totalization order."""

    cells = {cell for cell, _ in homology.bicomplex.components}
    cells.update(cell for cell, _ in homology.bicomplex.horizontal)
    cells.update(cell for cell, _ in homology.bicomplex.vertical)
    return tuple(sorted(cells))


def _total_action(
    homology: DPSurfaceDerivedHom,
    matrices: dict[int, Matrix],
    images: CoordinateImage,
) -> ChainMap:
    """Build and validate one degree-preserving action on the total complex."""

    total = homology.total
    degree_cells: dict[int, tuple[tuple[int, int], ...]] = {}
    for cell in _total_cells(homology):
        degree_cells.setdefault(sum(cell), ())
        degree_cells[sum(cell)] = tuple(sorted((*degree_cells[sum(cell)], cell)))
    components = {}
    for degree in total.degrees:
        cells = degree_cells.get(degree, ())
        maps = tuple(
            _term_action(
                homology,
                parent_degree,
                sheaf_degree,
                matrices[parent_degree],
                images,
            )
            for parent_degree, sheaf_degree in cells
        )
        if not maps:
            components[degree] = LinearMap.zero(
                total.spaces.space(degree),
                total.spaces.space(degree),
            )
            continue
        action = maps[0]
        for map_ in maps[1:]:
            action = LinearMap.direct_sum(action, map_)
        if action.domain != total.spaces.space(degree):
            raise ValueError("total action domain frame mismatch")
        if action.codomain != total.spaces.space(degree):
            raise ValueError("total action codomain frame mismatch")
        components[degree] = action
    return ChainMap(total, total, components)


def _quotient_functionals(
    complex_,
    degree: int,
    representatives: tuple[CoordinateVector, ...],
) -> Matrix:
    """Return exact functionals annihilating boundaries."""

    space = complex_.spaces.space(degree)
    boundaries = complex_.boundaries(degree)
    if boundaries:
        boundary_matrix = Matrix(
            tuple(
                tuple(vector.coordinates[column] for vector in boundaries)
                for column in range(space.dimension)
            ),
            scalar_type=space.scalar_type,
        )
        functionals = boundary_matrix.transpose().nullspace()
    else:
        functionals = tuple(
            Vector(
                (Eisenstein(1) if row == index else Eisenstein(0)
                 for row in range(space.dimension)),
                scalar_type=space.scalar_type,
            )
            for index in range(space.dimension)
        )
    if len(functionals) != len(representatives):
        raise ValueError("boundary annihilator dimension does not match cohomology")
    return Matrix(
        tuple(functional.values for functional in functionals),
        scalar_type=space.scalar_type,
    )


def _induced_matrix(
    action: ChainMap,
    complex_,
    degree: int,
    representatives: tuple[CoordinateVector, ...],
) -> Matrix | None:
    """Induce an exact action on one cohomology basis."""

    if not representatives:
        return None
    space = complex_.spaces.space(degree)
    functionals = _quotient_functionals(complex_, degree, representatives)
    representative_matrix = Matrix(
        tuple(
            tuple(vector.coordinates[column] for vector in representatives)
            for column in range(space.dimension)
        ),
        scalar_type=space.scalar_type,
    )
    normalization = functionals.matmul(representative_matrix).inverse()
    columns = []
    for representative in representatives:
        image = action.component(degree)(representative)
        image_column = Matrix(
            tuple((coordinate,) for coordinate in image.coordinates),
            scalar_type=space.scalar_type,
        )
        coordinates = normalization.matmul(functionals.matmul(image_column))
        columns.append(tuple(coordinates[row][0] for row in range(len(representatives))))
    return Matrix(
        tuple(
            tuple(columns[column][row] for column in range(len(columns)))
            for row in range(len(representatives))
        ),
        scalar_type=space.scalar_type,
    )


def _fixed_representatives(
    representatives: tuple[CoordinateVector, ...],
    p_matrix: Matrix | None,
    t_matrix: Matrix | None,
) -> tuple[CoordinateVector, ...]:
    """Return exact common fixed representatives."""

    if not representatives or p_matrix is None or t_matrix is None:
        return ()
    identity = Matrix.identity(len(representatives), scalar_type=Eisenstein)
    fixed = Matrix(
        (*((p_matrix - identity).rows), *((t_matrix - identity).rows)),
        scalar_type=Eisenstein,
    ).nullspace()
    space = representatives[0].space
    return tuple(
        CoordinateVector(
            space,
            tuple(
                sum(
                    (
                        fixed_vector.values[index] * representatives[index].coordinates[row]
                        for index in range(len(representatives))
                    ),
                    Eisenstein(0),
                )
                for row in range(space.dimension)
            ),
        )
        for fixed_vector in fixed
    )


def _matrix_record(matrix: Matrix | None) -> list[list[str]] | None:
    """Serialize an exact induced matrix."""

    if matrix is None:
        return None
    return [[str(value) for value in row] for row in matrix.rows]


@dataclass(frozen=True, slots=True)
class DPSurfaceDeckActionAudit:
    """Exact zero-fiber deck actions and their total H1 invariant audit."""

    homology: DPSurfaceDerivedHom
    p_action: ChainMap
    t_action: ChainMap
    p_induced: Matrix | None
    t_induced: Matrix | None
    invariants: tuple[CoordinateVector, ...]

    @property
    def invariant_dimension(self) -> int:
        """Return the exact common fixed dimension in total degree one."""

        return len(self.invariants)

    @property
    def actions_commute(self) -> bool:
        """Return whether the two total chain maps commute exactly."""

        return self.p_action.compose(self.t_action) == self.t_action.compose(self.p_action)

    @property
    def actions_order_three(self) -> bool:
        """Return whether both total chain maps have exact order three."""

        identity = ChainMap.identity(self.homology.total)
        return (
            self.p_action.compose(self.p_action).compose(self.p_action) == identity
            and self.t_action.compose(self.t_action).compose(self.t_action) == identity
        )

    def as_record(self) -> dict[str, object]:
        """Serialize exact action gates and sparse invariant representatives."""

        return {
            "left_scheme": self.homology.parent.left.scheme.name,
            "right_scheme": self.homology.parent.right.scheme.name,
            "fiber_degree": self.homology.fiber_degree,
            "total_h1_dimension": self.homology.total_h1_dimension,
            "invariant_h1_dimension": self.invariant_dimension,
            "p_induced": _matrix_record(self.p_induced),
            "t_induced": _matrix_record(self.t_induced),
            "actions_commute": self.actions_commute,
            "actions_order_three": self.actions_order_three,
            "total_squared_zero": self.homology.squared_zero,
            "invariant_representatives": [
                [
                    {"basis": basis, "coefficient": str(coefficient)}
                    for basis, coefficient in zip(
                        representative.space.basis,
                        representative.coordinates,
                        strict=True,
                    )
                    if not coefficient.is_zero()
                ]
                for representative in self.invariants
            ],
            "status": (
                "exact zero-fiber dP9 presentation-totalization action; global "
                "sheafification and quotient descent remain unresolved"
            ),
        }


def dp9_deck_action_audit(
    homology: DPSurfaceDerivedHom,
    resolution_pairs: tuple[ResolutionActionPair, ...] | None = None,
) -> DPSurfaceDeckActionAudit:
    """Build exact P/T actions on one zero-fiber dP9 totalization."""

    if homology.fiber_degree != 0:
        raise ValueError("the current dP9 deck audit supports fiber degree zero only")
    pairs = tier_a_resolution_actions() if resolution_pairs is None else resolution_pairs
    if len(pairs) != 2:
        raise ValueError("dP9 deck actions require I3 and I6 resolution pairs")
    left_pair, right_pair = pairs
    parent = homology.parent
    matrices = {
        name: _presentation_term_actions(
            name,
            left_pair,
            right_pair,
            parent.left.character_pair,
            parent.right.character_pair,
        )
        for name in ("P", "T")
    }
    p_action = _total_action(
        homology,
        matrices["P"],
        published_coordinate_images("P"),
    )
    t_action = _total_action(
        homology,
        matrices["T"],
        published_coordinate_images("T"),
    )
    representatives = homology.total.cohomology_representatives(1)
    p_induced = _induced_matrix(p_action, homology.total, 1, representatives)
    t_induced = _induced_matrix(t_action, homology.total, 1, representatives)
    return DPSurfaceDeckActionAudit(
        homology,
        p_action,
        t_action,
        p_induced,
        t_induced,
        _fixed_representatives(representatives, p_induced, t_induced),
    )


__all__ = [
    "DPSurfaceDeckActionAudit",
    "dp9_deck_action_audit",
    "published_coordinate_images",
]
