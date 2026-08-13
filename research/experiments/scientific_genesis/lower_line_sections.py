"""Construct the unique lower-line section on sparse Schoen Koszul complexes.

Owns:
    The canonical ``H^1(P1,O(-2))`` Koszul representative of the unique
    ``O(3*tau1-phi)`` section and its exact line-complex multiplication maps.

Depends on:
    Sparse Schoen line bundles, ambient Künneth bases, and exact Eisenstein
    linear algebra.

Must not:
    Call a section map a constituent subbundle, infer a lifted outer extension,
    or bypass chain-map validation.

Phase 0:
    Research-only sparse multiplication by the lower-line section is executable.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_linebundles import (
    AmbientSchoenSpace,
)
from research.experiments.computable_carrier.schoen_sparse_outer import (
    SparseLineBundle,
    SparseMap,
    SparseOuterHom,
    _freeze_rows,
    _sparse_direct_sum_maps,
    _sparse_direct_sum_space,
    _sparse_line_sum_space,
    sparse_line_bundle,
)

SECTION_DEGREES = {1: (3, 0, -1), 2: (0, 3, -1)}


def _ambient_section_map(
    source: AmbientSchoenSpace,
    target: AmbientSchoenSpace,
) -> SparseMap:
    """Multiply ambient cohomology by the canonical ``H1(O(-2))`` class."""

    target_indices = {label: index for index, label in enumerate(target.labels)}
    rows: list[dict[int, Eisenstein]] = [
        {} for _ in range(target.vector_space.dimension)
    ]
    for source_index, label in enumerate(source.labels):
        x_h, u_h, p_h, x_monomial, u_monomial, p_monomial = label
        if p_h != 0 or p_monomial != (0, 0):
            continue
        target_label = (
            x_h,
            u_h,
            1,
            x_monomial,
            u_monomial,
            (-1, -1),
        )
        target_index = target_indices.get(target_label)
        if target_index is not None:
            rows[target_index][source_index] = Eisenstein(1)
    return SparseMap(
        source.vector_space,
        target.vector_space,
        _freeze_rows(rows),
    )


def _zero(domain: VectorSpace, codomain: VectorSpace) -> SparseMap:
    """Return one typed sparse zero map."""

    return SparseMap.zero(domain, codomain)


def _section_component(
    source: SparseLineBundle,
    target: SparseLineBundle,
    degree: int,
    lower_sign: int,
    factor: int,
) -> SparseMap:
    """Return one total-degree component of multiplication by the section."""

    source_blocks = (
        source.ambient_k0.space(degree),
        source.ambient_k1_x.space(degree + 1),
        source.ambient_k1_u.space(degree + 1),
        source.ambient_k2.space(degree + 2),
    )
    target_blocks = (
        target.ambient_k0.space(degree),
        target.ambient_k1_x.space(degree + 1),
        target.ambient_k1_u.space(degree + 1),
        target.ambient_k2.space(degree + 2),
    )
    if factor == 1:
        k0_target = 1
        other_source = 2
    elif factor == 2:
        k0_target = 2
        other_source = 1
    else:
        raise ValueError("lower-line sections require Schoen factor one or two")
    k0_to_k1 = _ambient_section_map(
        source_blocks[0],
        target_blocks[k0_target],
    )
    other_to_k2 = _ambient_section_map(
        source_blocks[other_source],
        target_blocks[3],
    ).scale(lower_sign)
    return SparseMap.block(
        (
            tuple(
                _zero(block.vector_space, target_blocks[0].vector_space)
                for block in source_blocks
            ),
            (
                k0_to_k1 if factor == 1 else _zero(
                    source_blocks[0].vector_space,
                    target_blocks[1].vector_space,
                ),
                _zero(source_blocks[1].vector_space, target_blocks[1].vector_space),
                _zero(source_blocks[2].vector_space, target_blocks[1].vector_space),
                _zero(source_blocks[3].vector_space, target_blocks[1].vector_space),
            ),
            (
                k0_to_k1 if factor == 2 else _zero(
                    source_blocks[0].vector_space,
                    target_blocks[2].vector_space,
                ),
                _zero(source_blocks[1].vector_space, target_blocks[2].vector_space),
                _zero(source_blocks[2].vector_space, target_blocks[2].vector_space),
                _zero(source_blocks[3].vector_space, target_blocks[2].vector_space),
            ),
            (
                _zero(source_blocks[0].vector_space, target_blocks[3].vector_space),
                other_to_k2 if factor == 2 else _zero(
                    source_blocks[1].vector_space,
                    target_blocks[3].vector_space,
                ),
                other_to_k2 if factor == 1 else _zero(
                    source_blocks[2].vector_space,
                    target_blocks[3].vector_space,
                ),
                _zero(source_blocks[3].vector_space, target_blocks[3].vector_space),
            ),
        )
    )


def lower_line_section_components(
    source: SparseLineBundle,
    factor: int = 1,
) -> tuple[tuple[int, SparseMap], ...]:
    """Return the exact chain map multiplying by ``O(3*tau1-phi)``."""

    if factor not in SECTION_DEGREES:
        raise ValueError("lower-line sections require Schoen factor one or two")
    section_degree = SECTION_DEGREES[factor]
    target_degree = tuple(
        value + shift
        for value, shift in zip(source.degrees, section_degree, strict=True)
    )
    target = sparse_line_bundle(*target_degree)
    for lower_sign in (1, -1):
        components = tuple(
            (
                degree,
                _section_component(source, target, degree, lower_sign, factor),
            )
            for degree in range(4)
        )
        by_degree = dict(components)
        if all(
            target.differential(degree).compose(component)
            == by_degree[degree + 1].compose(source.differential(degree))
            for degree, component in components
            if degree + 1 in by_degree
        ):
            return components
    raise ValueError("the canonical lower-line section failed its chain-map gate")


def _line_difference(
    target: tuple[int, int, int],
    source: tuple[int, int, int],
) -> tuple[int, int, int]:
    """Return the divisor degree of one line-bundle Hom."""

    return tuple(
        target_value - source_value
        for target_value, source_value in zip(target, source, strict=True)
    )


def _horizontal_map(
    outer: SparseOuterHom,
    source_bundles: tuple[SparseLineBundle, ...],
    target_bundles: tuple[SparseLineBundle, ...],
    sheaf_degree: int,
) -> SparseMap:
    """Apply the left presentation differential to line-Hom summands."""

    relation = outer.left.candidate.relation
    factor = outer.left.polynomial_factor
    blocks = []
    for target_index, target_bundle in enumerate(target_bundles):
        row = []
        for source_index, source_bundle in enumerate(source_bundles):
            polynomial = relation.rows[source_index][target_index]
            if polynomial.is_zero():
                row.append(
                    SparseMap.zero(
                        source_bundle.space(sheaf_degree),
                        target_bundle.space(sheaf_degree),
                    )
                )
            else:
                row.append(
                    dict(
                        source_bundle.multiplication(
                            target_bundle,
                            polynomial,
                            factor,
                        )
                    )[sheaf_degree]
                )
        blocks.append(tuple(row))
    return SparseMap.block(tuple(blocks))


@dataclass(frozen=True, slots=True)
class SparseLineHomComplex:
    """The exact total complex ``RHom(line, V_left)`` on the Schoen cover."""

    outer: SparseOuterHom
    line_degree: tuple[int, int, int]
    bundles: tuple[tuple[int, tuple[SparseLineBundle, ...]], ...]
    spaces: tuple[tuple[int, VectorSpace], ...]
    differentials: tuple[tuple[int, SparseMap], ...]
    squared_zero: bool

    @property
    def total(self) -> dict[int, VectorSpace]:
        """Return total cochain spaces by degree."""

        return dict(self.spaces)


def sparse_line_hom_complex(
    outer: SparseOuterHom,
    line_degree: tuple[int, int, int],
) -> SparseLineHomComplex:
    """Build ``RHom(line,V_left)`` from the exact left presentation."""

    if len(line_degree) != 3:
        raise ValueError("a Schoen line degree requires three coordinates")
    bundle_degrees = {
        -1: tuple(
            _line_difference(degree, line_degree)
            for degree in outer.left.source_line_degrees
        ),
        0: tuple(
            _line_difference(degree, line_degree)
            for degree in outer.left.target_line_degrees
        ),
    }
    bundles = {
        parent_degree: tuple(sparse_line_bundle(*degree) for degree in degrees)
        for parent_degree, degrees in bundle_degrees.items()
    }
    cells = tuple(
        (parent_degree, sheaf_degree)
        for parent_degree in (-1, 0)
        for sheaf_degree in range(4)
    )
    cell_spaces = {
        cell: _sparse_line_sum_space(
            bundles[cell[0]],
            cell[1],
        )
        for cell in cells
    }
    horizontal = {
        sheaf_degree: _horizontal_map(
            outer,
            bundles[-1],
            bundles[0],
            sheaf_degree,
        )
        for sheaf_degree in range(4)
    }
    vertical = {
        cell: _sparse_direct_sum_maps(
            tuple(
                bundle.differential(cell[1])
                for bundle in bundles[cell[0]]
            )
        )
        for cell in cells
        if cell[1] < 3
    }
    degree_cells: dict[int, tuple[tuple[int, int], ...]] = {}
    for cell in cells:
        degree_cells.setdefault(sum(cell), tuple())
        degree_cells[sum(cell)] = tuple(
            sorted((*degree_cells[sum(cell)], cell))
        )
    total_spaces = {
        degree: _sparse_direct_sum_space(
            tuple(cell_spaces[cell] for cell in selected_cells)
        )
        for degree, selected_cells in degree_cells.items()
    }
    total_maps = {}
    for degree, source_cells in degree_cells.items():
        target_cells = degree_cells.get(degree + 1, ())
        if not target_cells:
            total_maps[degree] = SparseMap.zero(
                total_spaces[degree],
                VectorSpace(f"line-Hom-zero:{degree + 1}", (), Eisenstein),
            )
            continue
        rows = []
        for target_cell in target_cells:
            row = []
            for source_cell in source_cells:
                if target_cell == (source_cell[0] + 1, source_cell[1]):
                    block = horizontal[source_cell[1]]
                elif target_cell == (source_cell[0], source_cell[1] + 1):
                    block = vertical[source_cell].scale(
                        -1 if source_cell[0] % 2 else 1
                    )
                else:
                    block = SparseMap.zero(
                        cell_spaces[source_cell],
                        cell_spaces[target_cell],
                    )
                row.append(block)
            rows.append(tuple(row))
        total_maps[degree] = SparseMap.block(tuple(rows))
    squared_zero = all(
        total_maps[degree + 1].compose(differential).is_zero()
        for degree, differential in total_maps.items()
        if degree + 1 in total_maps
    )
    return SparseLineHomComplex(
        outer,
        line_degree,
        tuple(sorted(bundles.items())),
        tuple(sorted(total_spaces.items())),
        tuple(sorted(total_maps.items())),
        squared_zero,
    )


def lower_line_hom_section_map(
    source: SparseLineHomComplex,
    factor: int = 1,
) -> tuple[SparseLineHomComplex, tuple[tuple[int, SparseMap], ...]]:
    """Multiply ``RHom(G,V_left)`` into ``RHom(G-S,V_left)`` exactly."""

    if factor not in SECTION_DEGREES:
        raise ValueError("lower-line sections require Schoen factor one or two")
    section_degree = SECTION_DEGREES[factor]
    lower_degree = tuple(
        value - shift
        for value, shift in zip(source.line_degree, section_degree, strict=True)
    )
    target = sparse_line_hom_complex(source.outer, lower_degree)
    source_bundles = dict(source.bundles)
    target_bundles = dict(target.bundles)
    cell_maps = {
        (parent_degree, sheaf_degree): SparseMap.block(
            tuple(
                tuple(
                    dict(
                        lower_line_section_components(source_bundle, factor)
                    )[sheaf_degree]
                    if row == column
                    else SparseMap.zero(
                        source_bundles[parent_degree][column].space(sheaf_degree),
                        target_bundles[parent_degree][row].space(sheaf_degree),
                    )
                    for column, source_bundle in enumerate(
                        source_bundles[parent_degree]
                    )
                )
                for row in range(len(target_bundles[parent_degree]))
            )
        )
        for parent_degree in (-1, 0)
        for sheaf_degree in range(4)
    }
    cells_by_degree: dict[int, tuple[tuple[int, int], ...]] = {}
    for cell in cell_maps:
        cells_by_degree.setdefault(sum(cell), tuple())
        cells_by_degree[sum(cell)] = tuple(
            sorted((*cells_by_degree[sum(cell)], cell))
        )
    components = {}
    for degree, cells in cells_by_degree.items():
        blocks = tuple(
            tuple(
                cell_maps[target_cell]
                if target_cell == source_cell
                else SparseMap.zero(
                    cell_maps[source_cell].domain,
                    cell_maps[target_cell].codomain,
                )
                for source_cell in cells
            )
            for target_cell in cells
        )
        components[degree] = SparseMap.block(blocks)
        if components[degree].domain != source.total[degree] or (
            components[degree].codomain != target.total[degree]
        ):
            raise ValueError("a lower-line section component has incompatible totals")
    source_differentials = dict(source.differentials)
    target_differentials = dict(target.differentials)
    if not all(
        target_differentials[degree].compose(component)
        == components[degree + 1].compose(source_differentials[degree])
        for degree, component in components.items()
        if degree + 1 in components
    ):
        raise ValueError("the lower-line Hom section failed its total chain-map gate")
    return target, tuple(sorted(components.items()))


__all__ = [
    "SECTION_DEGREES",
    "SparseLineHomComplex",
    "lower_line_hom_section_map",
    "lower_line_section_components",
    "sparse_line_hom_complex",
]
