"""Compute sparse exact outer Hom complexes on the Schoen cover.

Owns:
    Sparse Künneth/Koszul maps, sparse signed totalization, and exact column
    elimination for cover-level outer Hom dimensions of declared presentations.

Depends on:
    The exact Schoen ambient basis, the published equations, and the generic
    polynomial presentation Hom complex. It uses no observations or fits.

Must not:
    Replace quotient-invariant Ext by a cover dimension, select an extension
    from a nonzero space, or infer stability, descent, or physical spectra.

Phase 0:
    Sparse cover-level rank certification is available; quotient action and
    physical promotion remain explicit unresolved gates.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from functools import cache

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry

from .schoen_linebundles import (
    AmbientSchoenSpace,
    SchoenAmbientLineBundle,
    _factor_basis,
    _factor_matrix_for_terms,
    _p1_basis,
    ambient_schoen_line_bundle,
)
from .schoen_outer import (
    SchoenPresentation,
    _factor_matrix,
    _hom_term_lines,
    schoen_presentation,
)
from .tier_b_serre_extensions import TierBSerreExtensionRay

SparseRow = tuple[tuple[int, Eisenstein], ...]


def _freeze_rows(rows: Iterable[dict[int, Eisenstein]]) -> tuple[SparseRow, ...]:
    """Normalize mutable assembly rows into immutable sparse rows."""

    return tuple(
        tuple(
            (column, value)
            for column, value in sorted(row.items())
            if not value.is_zero()
        )
        for row in rows
    )


@dataclass(frozen=True, slots=True)
class SparseMap:
    """An immutable exact sparse map between named finite spaces."""

    domain: VectorSpace
    codomain: VectorSpace
    rows: tuple[SparseRow, ...]

    def __post_init__(self) -> None:
        if len(self.rows) != self.codomain.dimension:
            raise ValueError("sparse map rows do not match its codomain")
        if any(
            column < 0 or column >= self.domain.dimension
            for row in self.rows
            for column, _ in row
        ):
            raise ValueError("sparse map contains an out-of-range column")

    @classmethod
    def zero(cls, domain: VectorSpace, codomain: VectorSpace) -> SparseMap:
        """Construct a typed sparse zero map."""

        return cls(domain, codomain, tuple(() for _ in range(codomain.dimension)))

    @classmethod
    def block(
        cls,
        blocks: tuple[tuple[SparseMap, ...], ...],
    ) -> SparseMap:
        """Assemble a sparse block matrix without materializing zero entries."""

        if not blocks or not blocks[0]:
            raise ValueError("a sparse block matrix must be nonempty")
        column_domains = tuple(blocks[0][column].domain for column in range(len(blocks[0])))
        row_codomains = tuple(blocks[row][0].codomain for row in range(len(blocks)))
        if any(len(row) != len(column_domains) for row in blocks):
            raise ValueError("a sparse block matrix must be rectangular")
        for row in blocks:
            for column, block in enumerate(row):
                if block.domain != column_domains[column]:
                    raise ValueError("sparse block domains are incompatible")
        column_offsets = []
        offset = 0
        for domain in column_domains:
            column_offsets.append(offset)
            offset += domain.dimension
        rows: list[dict[int, Eisenstein]] = []
        for block_row, codomain in zip(blocks, row_codomains, strict=True):
            for local_row in range(codomain.dimension):
                row: dict[int, Eisenstein] = {}
                for block, column_offset in zip(block_row, column_offsets, strict=True):
                    for local_column, value in block.rows[local_row]:
                        row[column_offset + local_column] = value
                rows.append(row)
        domain = column_domains[0]
        for component in column_domains[1:]:
            domain = domain.direct_sum(component)
        codomain = row_codomains[0]
        for component in row_codomains[1:]:
            codomain = codomain.direct_sum(component)
        return cls(domain, codomain, _freeze_rows(rows))

    def scale(self, scalar: object) -> SparseMap:
        """Scale every nonzero sparse entry exactly."""

        factor = Eisenstein.coerce(scalar)
        return SparseMap(
            self.domain,
            self.codomain,
            _freeze_rows(
                {
                    column: factor * value
                    for column, value in row
                }
                for row in self.rows
            ),
        )

    def compose(self, previous: SparseMap) -> SparseMap:
        """Compose this sparse map after a compatible sparse map."""

        if previous.codomain != self.domain:
            raise ValueError("sparse map composition requires matching spaces")
        previous_rows = previous.rows
        rows: list[dict[int, Eisenstein]] = []
        for row in self.rows:
            result: dict[int, Eisenstein] = {}
            for middle, left_value in row:
                for column, right_value in previous_rows[middle]:
                    result[column] = result.get(column, Eisenstein(0)) + (
                        left_value * right_value
                    )
            rows.append(result)
        return SparseMap(previous.domain, self.codomain, _freeze_rows(rows))

    def is_zero(self) -> bool:
        """Return whether every sparse row is empty."""

        return all(not row for row in self.rows)

    def rank(self) -> int:
        """Return exact rank by sparse normalized-column elimination."""

        pivot_vectors: dict[int, dict[int, Eisenstein]] = {}
        rank = 0
        columns: list[dict[int, Eisenstein]] = [
            {} for _ in range(self.domain.dimension)
        ]
        for row_index, row in enumerate(self.rows):
            for column, value in row:
                columns[column][row_index] = value
        for vector in columns:
            while vector:
                pivot = min(vector)
                coefficient = vector[pivot]
                existing = pivot_vectors.get(pivot)
                if existing is None:
                    inverse = Eisenstein(1) / coefficient
                    normalized = {
                        row: value * inverse for row, value in vector.items()
                    }
                    pivot_vectors[pivot] = normalized
                    rank += 1
                    break
                factor = coefficient
                for row, value in existing.items():
                    updated = vector.get(row, Eisenstein(0)) - factor * value
                    if updated.is_zero():
                        vector.pop(row, None)
                    else:
                        vector[row] = updated
        return rank


@cache
def _sparse_factor_map(
    source: AmbientSchoenSpace,
    target: AmbientSchoenSpace,
    polynomial: Polynomial,
    factor: str,
) -> SparseMap:
    """Multiply ambient Künneth bases by one factor polynomial sparsely."""

    if polynomial.is_zero():
        return SparseMap.zero(source.vector_space, target.vector_space)
    target_indices = {label: index for index, label in enumerate(target.labels)}
    position = {"x": 0, "u": 1, "p": 2}[factor]
    local_data = {}
    for x_h, u_h, p_h in {
        (label[0], label[1], label[2]) for label in source.labels
    }:
        h = (x_h, u_h, p_h)
        source_basis = _factor_basis(
            factor,
            source.degrees[position],
            h[position],
        )
        local_data[h] = (
            *_factor_matrix_for_terms(
                factor,
                source.degrees[position],
                target.degrees[position],
                h[position],
                polynomial,
            ),
            {monomial: index for index, monomial in enumerate(source_basis)},
        )
    rows: list[dict[int, Eisenstein]] = [
        {} for _ in target.labels
    ]
    for source_index, label in enumerate(source.labels):
        x_h, u_h, p_h, x_monomial, u_monomial, p_monomial = label
        h = (x_h, u_h, p_h)
        target_basis, factor_rows, source_indices = local_data[h]
        local_source = (x_monomial, u_monomial, p_monomial)[position]
        source_index_local = source_indices[local_source]
        for target_index_local, target_monomial in enumerate(target_basis):
            coefficient = factor_rows[target_index_local][source_index_local]
            if coefficient.is_zero():
                continue
            target_label = (
                x_h,
                u_h,
                p_h,
                target_monomial if factor == "x" else x_monomial,
                target_monomial if factor == "u" else u_monomial,
                target_monomial if factor == "p" else p_monomial,
            )
            target_index = target_indices.get(target_label)
            if target_index is None:
                raise ValueError("sparse factor multiplication escaped its target basis")
            rows[target_index][source_index] = coefficient
    return SparseMap(source.vector_space, target.vector_space, _freeze_rows(rows))


@cache
def _sparse_equation_map(
    source: AmbientSchoenSpace,
    target: AmbientSchoenSpace,
    terms: tuple[tuple[Polynomial, str, Polynomial], ...],
) -> SparseMap:
    """Assemble a separated-factor Schoen equation sparsely."""

    target_indices = {label: index for index, label in enumerate(target.labels)}
    rows: list[dict[int, Eisenstein]] = [{} for _ in target.labels]
    for polynomial, factor, fiber_form in terms:
        position = {"x": 0, "u": 1}[factor]
        local_data = {}
        for x_h, u_h, p_h in {
            (label[0], label[1], label[2]) for label in source.labels
        }:
            h = (x_h, u_h, p_h)
            source_basis = _factor_basis(factor, source.degrees[position], h[position])
            fiber_basis = _p1_basis(source.degrees[2], p_h)
            local_data[h] = (
                _factor_matrix_for_terms(
                    factor,
                    source.degrees[position],
                    target.degrees[position],
                    h[position],
                    polynomial,
                ),
                _factor_matrix_for_terms(
                    "p",
                    source.degrees[2],
                    target.degrees[2],
                    p_h,
                    fiber_form,
                ),
                {monomial: index for index, monomial in enumerate(source_basis)},
                {monomial: index for index, monomial in enumerate(fiber_basis)},
            )
        for source_index, label in enumerate(source.labels):
            x_h, u_h, p_h, x_monomial, u_monomial, p_monomial = label
            h = (x_h, u_h, p_h)
            (
                (factor_basis, factor_rows),
                (fiber_basis, fiber_rows),
                source_indices,
                fiber_indices,
            ) = local_data[h]
            source_local = (x_monomial, u_monomial)[position]
            factor_source = source_indices[source_local]
            fiber_source = fiber_indices[p_monomial]
            for factor_target, factor_monomial in enumerate(factor_basis):
                factor_value = factor_rows[factor_target][factor_source]
                if factor_value.is_zero():
                    continue
                for fiber_target, fiber_monomial in enumerate(fiber_basis):
                    value = factor_value * fiber_rows[fiber_target][fiber_source]
                    if value.is_zero():
                        continue
                    target_label = (
                        x_h,
                        u_h,
                        p_h,
                        factor_monomial if factor == "x" else x_monomial,
                        factor_monomial if factor == "u" else u_monomial,
                        fiber_monomial,
                    )
                    target_index = target_indices.get(target_label)
                    if target_index is None:
                        raise ValueError("sparse equation escaped its target basis")
                    rows[target_index][source_index] = rows[target_index].get(
                        source_index,
                        Eisenstein(0),
                    ) + value
    return SparseMap(source.vector_space, target.vector_space, _freeze_rows(rows))


def _sparse_direct_sum_space(spaces: tuple[VectorSpace, ...]) -> VectorSpace:
    """Build one ordered direct-sum basis."""

    result = spaces[0]
    for space in spaces[1:]:
        result = result.direct_sum(space)
    return result


@dataclass(frozen=True, slots=True)
class SparseLineBundle:
    """A sparse exact Koszul complex for one Schoen cover line bundle."""

    degrees: tuple[int, int, int]
    ambient_k0: SchoenAmbientLineBundle
    ambient_k1_x: SchoenAmbientLineBundle
    ambient_k1_u: SchoenAmbientLineBundle
    ambient_k2: SchoenAmbientLineBundle
    spaces: tuple[tuple[int, VectorSpace], ...]
    differentials: tuple[tuple[int, SparseMap], ...]

    def space(self, degree: int) -> VectorSpace:
        """Return one sparse Koszul cochain space."""

        return dict(self.spaces).get(
            degree,
            VectorSpace(
                f"Sparse O_X{self.degrees}[{degree}]",
                (),
                Eisenstein,
            ),
        )

    def differential(self, degree: int) -> SparseMap:
        """Return one sparse Koszul differential or a typed zero map."""

        selected = dict(self.differentials).get(degree)
        if selected is not None:
            return selected
        return SparseMap.zero(self.space(degree), self.space(degree + 1))

    @property
    def squared_zero(self) -> bool:
        """Return the exact sparse Koszul square-zero gate."""

        return all(
            self.differential(degree + 1).compose(differential).is_zero()
            for degree, differential in self.differentials
        )

    def multiplication(
        self,
        target: SparseLineBundle,
        polynomial: Polynomial,
        factor: str,
    ) -> tuple[tuple[int, SparseMap], ...]:
        """Return sparse multiplication components on the Koszul cone."""

        position = {"x": 0, "u": 1}[factor]
        expected = list(self.degrees)
        expected[position] += polynomial.degree
        if tuple(expected) != target.degrees:
            raise ValueError("sparse multiplication has incompatible line degrees")
        components = []
        for degree in range(4):
            source_blocks = (
                self.ambient_k0.space(degree),
                self.ambient_k1_x.space(degree + 1),
                self.ambient_k1_u.space(degree + 1),
                self.ambient_k2.space(degree + 2),
            )
            target_blocks = (
                target.ambient_k0.space(degree),
                target.ambient_k1_x.space(degree + 1),
                target.ambient_k1_u.space(degree + 1),
                target.ambient_k2.space(degree + 2),
            )
            maps = tuple(
                _sparse_factor_map(source_block, target_block, polynomial, factor)
                for source_block, target_block in zip(source_blocks, target_blocks, strict=True)
            )
            zero_blocks = tuple(
                tuple(
                    selected
                    if row == column
                    else SparseMap.zero(
                        source_blocks[column].vector_space,
                        target_blocks[row].vector_space,
                    )
                    for column, selected in enumerate(maps)
                )
                for row in range(4)
            )
            components.append((degree, SparseMap.block(zero_blocks)))
        return tuple(components)


def _sparse_line_space(
    k0: SchoenAmbientLineBundle,
    k1_x: SchoenAmbientLineBundle,
    k1_u: SchoenAmbientLineBundle,
    k2: SchoenAmbientLineBundle,
    degree: int,
) -> VectorSpace:
    """Build one sparse line-bundle Koszul space."""

    return _sparse_direct_sum_space(
        (
            k0.space(degree).vector_space,
            k1_x.space(degree + 1).vector_space,
            k1_u.space(degree + 1).vector_space,
            k2.space(degree + 2).vector_space,
        )
    )


def _sparse_koszul_block(
    blocks: tuple[tuple[SparseMap, ...], ...],
) -> SparseMap:
    """Assemble one signed four-block Koszul differential."""

    return SparseMap.block(blocks)


@cache
def sparse_line_bundle(x_degree: int, u_degree: int, p_degree: int) -> SparseLineBundle:
    """Construct one exact sparse Schoen line-bundle complex."""

    degrees = (x_degree, u_degree, p_degree)
    k0 = ambient_schoen_line_bundle(*degrees)
    k1_x = ambient_schoen_line_bundle(x_degree - 3, u_degree, p_degree - 1)
    k1_u = ambient_schoen_line_bundle(x_degree, u_degree - 3, p_degree - 1)
    k2 = ambient_schoen_line_bundle(x_degree - 3, u_degree - 3, p_degree - 2)
    spaces = tuple(
        (degree, _sparse_line_space(k0, k1_x, k1_u, k2, degree))
        for degree in range(4)
    )
    differentials = []
    cox = schoen_geometry().cover.cox
    mu = Polynomial.monomial((1, 0), scalar_type=Eisenstein)
    nu = Polynomial.monomial((0, 1), scalar_type=Eisenstein)
    for degree in range(3):
        source_blocks = (
            k0.space(degree).vector_space,
            k1_x.space(degree + 1).vector_space,
            k1_u.space(degree + 1).vector_space,
            k2.space(degree + 2).vector_space,
        )
        target_blocks = (
            k0.space(degree + 1).vector_space,
            k1_x.space(degree + 2).vector_space,
            k1_u.space(degree + 2).vector_space,
            k2.space(degree + 3).vector_space,
        )
        def zero(domain: VectorSpace, codomain: VectorSpace) -> SparseMap:
            """Construct one typed sparse zero block."""

            return SparseMap.zero(domain, codomain)
        one = _sparse_equation_map(
            k1_x.space(degree + 1),
            k0.space(degree + 1),
            ((cox.cubic_f, "x", mu), (cox.cubic_g, "x", nu)),
        )
        two = _sparse_equation_map(
            k1_u.space(degree + 1),
            k0.space(degree + 1),
            ((cox.cubic_f.scale(2), "u", nu), (cox.cubic_g, "u", mu)),
        )
        two_from_k2 = _sparse_equation_map(
            k2.space(degree + 2),
            k1_x.space(degree + 2),
            ((cox.cubic_f.scale(2), "u", nu), (cox.cubic_g, "u", mu)),
        )
        one_from_k2 = _sparse_equation_map(
            k2.space(degree + 2),
            k1_u.space(degree + 2),
            ((cox.cubic_f, "x", mu), (cox.cubic_g, "x", nu)),
        )
        differentials.append(
            (
                degree,
                _sparse_koszul_block(
                    (
                        (
                            zero(source_blocks[0], target_blocks[0]),
                            one,
                            two,
                            zero(source_blocks[3], target_blocks[0]),
                        ),
                        (
                            zero(source_blocks[0], target_blocks[1]),
                            zero(source_blocks[1], target_blocks[1]),
                            zero(source_blocks[2], target_blocks[1]),
                            two_from_k2.scale(-1),
                        ),
                        (
                            zero(source_blocks[0], target_blocks[2]),
                            zero(source_blocks[1], target_blocks[2]),
                            zero(source_blocks[2], target_blocks[2]),
                            one_from_k2,
                        ),
                        (
                            zero(source_blocks[0], target_blocks[3]),
                            zero(source_blocks[1], target_blocks[3]),
                            zero(source_blocks[2], target_blocks[3]),
                            zero(source_blocks[3], target_blocks[3]),
                        ),
                    )
                ),
            )
        )
    return SparseLineBundle(
        degrees,
        k0,
        k1_x,
        k1_u,
        k2,
        spaces,
        tuple(differentials),
    )


def _sparse_rank_data(
    spaces: dict[int, VectorSpace],
    differentials: dict[int, SparseMap],
    degree: int,
) -> int:
    """Return sparse cohomology dimension in one total degree."""

    outgoing = differentials.get(
        degree,
        SparseMap.zero(spaces[degree], spaces.get(degree + 1, VectorSpace("zero", (), Eisenstein))),
    )
    incoming = differentials.get(
        degree - 1,
        SparseMap.zero(spaces.get(degree - 1, VectorSpace("zero", (), Eisenstein)), spaces[degree]),
    )
    return spaces[degree].dimension - outgoing.rank() - incoming.rank()


@dataclass(frozen=True, slots=True)
class SparseOuterHom:
    """Exact sparse signed totalization for one ordered presentation pair."""

    left: SchoenPresentation
    right: SchoenPresentation
    parent: object
    total_spaces: tuple[tuple[int, VectorSpace], ...]
    total_differentials: tuple[tuple[int, SparseMap], ...]

    @property
    def total(self) -> dict[int, VectorSpace]:
        """Return total spaces by cochain degree."""

        return dict(self.total_spaces)

    @property
    def squared_zero(self) -> bool:
        """Return exact square-zero for the sparse total differential."""

        maps = dict(self.total_differentials)
        return all(
            maps[degree + 1].compose(differential).is_zero()
            for degree, differential in self.total_differentials
            if degree + 1 in maps
        )

    @property
    def cover_ext_one_dimension(self) -> int:
        """Return exact degree-one sparse cover cohomology."""

        spaces = dict(self.total_spaces)
        maps = dict(self.total_differentials)
        return _sparse_rank_data(spaces, maps, 1)

    def as_record(self) -> dict[str, object]:
        """Serialize sparse cover dimensions without quotient promotion."""

        return {
            "left_scheme": self.left.candidate.scheme.name,
            "right_scheme": self.right.candidate.scheme.name,
            "total_dimensions": [
                [degree, space.dimension] for degree, space in self.total_spaces
            ],
            "cover_ext_one_dimension": self.cover_ext_one_dimension,
            "squared_zero": self.squared_zero,
            "status": "exact sparse Schoen cover Hom totalization",
        }


@cache
def _sparse_line_sum_space(
    bundles: tuple[SparseLineBundle, ...],
    degree: int,
) -> VectorSpace:
    """Build one sparse direct sum of line-bundle spaces."""

    return _sparse_direct_sum_space(tuple(bundle.space(degree) for bundle in bundles))


@cache
def _sparse_direct_sum_maps(maps: tuple[SparseMap, ...]) -> SparseMap:
    """Build a block-diagonal sparse map."""

    return SparseMap.block(
        tuple(
            tuple(
                map_ if row == column else SparseMap.zero(
                    maps[column].domain,
                    maps[row].codomain,
                )
                for column, map_ in enumerate(maps)
            )
            for row in range(len(maps))
        )
    )


def _sparse_horizontal_map(
    parent,
    degree: int,
    sheaf_degree: int,
    source_bundles: tuple[SparseLineBundle, ...],
    target_bundles: tuple[SparseLineBundle, ...],
    factors: tuple[tuple[str, ...], ...],
) -> SparseMap:
    """Evaluate one polynomial Hom differential sparsely."""

    polynomial_map = parent.differential(degree)
    blocks = []
    for target_index, target_bundle in enumerate(target_bundles):
        row = []
        for source_index, source_bundle in enumerate(source_bundles):
            polynomial = polynomial_map.matrix.rows[target_index][source_index]
            if polynomial.is_zero():
                row.append(
                    SparseMap.zero(
                        source_bundle.space(sheaf_degree),
                        target_bundle.space(sheaf_degree),
                    )
                )
            else:
                row.append(
                    dict(source_bundle.multiplication(
                        target_bundle,
                        polynomial,
                        factors[target_index][source_index],
                    ))[sheaf_degree]
                )
        blocks.append(tuple(row))
    return SparseMap.block(tuple(blocks))


@cache
def sparse_outer_hom(
    left_ray: TierBSerreExtensionRay,
    right_ray: TierBSerreExtensionRay,
    left_factor: int,
    left_twist: tuple[int, int, int],
    right_factor: int,
    right_twist: tuple[int, int, int],
) -> SparseOuterHom:
    """Build one sparse exact cover-level outer Hom totalization."""

    left = schoen_presentation(left_ray, left_factor, left_twist)
    right = schoen_presentation(right_ray, right_factor, right_twist)
    from .polynomial_hom import polynomial_hom_complex

    parent = polynomial_hom_complex(left.candidate, right.candidate)
    lines = _hom_term_lines(left, right)
    bundles = {
        degree: tuple(sparse_line_bundle(*line) for line in line_degrees)
        for degree, line_degrees in lines
    }
    spaces = {
        (parent_degree, sheaf_degree): _sparse_line_sum_space(
            bundles[parent_degree], sheaf_degree
        )
        for parent_degree, _ in lines
        for sheaf_degree in range(4)
    }
    factors = {
        degree: _factor_matrix(parent, degree, left_factor, right_factor)
        for degree, _ in parent.differentials
    }
    horizontal = {
        (degree, sheaf_degree): _sparse_horizontal_map(
            parent,
            degree,
            sheaf_degree,
            bundles[degree],
            bundles[degree + 1],
            factors[degree],
        )
        for degree, _ in parent.differentials
        for sheaf_degree in range(4)
    }
    vertical = {
        (degree, sheaf_degree): _sparse_direct_sum_maps(
            tuple(bundle.differential(sheaf_degree) for bundle in bundles[degree])
        )
        for degree, _ in lines
        for sheaf_degree in range(3)
    }
    degree_cells: dict[int, tuple[tuple[int, int], ...]] = {}
    for cell in spaces:
        degree_cells.setdefault(sum(cell), tuple())
        degree_cells[sum(cell)] = tuple(sorted((*degree_cells[sum(cell)], cell)))
    total_spaces = {
        degree: _sparse_direct_sum_space(
            tuple(spaces[cell] for cell in cells)
        )
        for degree, cells in degree_cells.items()
    }
    total_maps = {}
    for degree, source_cells in degree_cells.items():
        target_cells = degree_cells.get(degree + 1, ())
        blocks = []
        for target_cell in target_cells:
            row = []
            for source_cell in source_cells:
                if target_cell == (source_cell[0] + 1, source_cell[1]):
                    block = horizontal[source_cell]
                elif target_cell == (source_cell[0], source_cell[1] + 1):
                    block = vertical[source_cell].scale(
                        -1 if source_cell[0] % 2 else 1
                    )
                else:
                    block = SparseMap.zero(spaces[source_cell], spaces[target_cell])
                row.append(block)
            blocks.append(tuple(row))
        if target_cells:
            total_maps[degree] = SparseMap.block(tuple(blocks))
        else:
            total_maps[degree] = SparseMap.zero(
                total_spaces[degree],
                VectorSpace("zero", (), Eisenstein),
            )
    return SparseOuterHom(
        left,
        right,
        parent,
        tuple(sorted(total_spaces.items())),
        tuple(sorted(total_maps.items())),
    )


__all__ = [
    "SparseMap",
    "SparseLineBundle",
    "SparseOuterHom",
    "sparse_line_bundle",
    "sparse_outer_hom",
]
