"""Compute a cohomology-reduced outer model from published Serre cones.

Owns:
    Twisted-complex models of the two published constituents, exact cup maps
    for the canonical ``1/(mu nu)`` Čech class, and the sparse Schoen
    Koszul/Hom totalization after ambient Čech cohomology reduction.

Depends on:
    Certified constituent Čech cocycles, sparse Schoen line-bundle complexes,
    Hilbert--Burch maps, and exact Eisenstein elimination.

Must not:
    Identify the reduced model with full Čech hypercohomology, import published
    outer dimensions into rank calculations, or replace missing transferred
    differentials with fitted maps.

Phase 0:
    Research-only reduced outer model; full Čech contraction and transferred
    differential remain explicit gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial

from .dp9_serre_cech import DPSurfaceSerreCechCocycle
from .schoen_linebundles import (
    _KOSZUL_TOTAL_DEGREES,
    AmbientSchoenSpace,
    _factor_basis,
    _factor_matrix_for_terms,
)
from .schoen_sparse_outer import (
    SparseLineBundle,
    SparseMap,
    _freeze_rows,
    _sparse_direct_sum_space,
    _sparse_rank_data,
    sparse_line_bundle,
)

LineDegree = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class SerreObject:
    """One line-bundle object in a constituent twisted complex."""

    name: str
    position: int
    line_degree: LineDegree


@dataclass(frozen=True, slots=True)
class SerreArrow:
    """One total-degree-one polynomial or Čech constituent arrow."""

    source: int
    target: int
    polynomial: Polynomial
    factor: str
    cech_degree: int

    def __post_init__(self) -> None:
        if self.factor not in {"x", "u"}:
            raise ValueError("Serre arrows live on the x or u factor")
        if self.cech_degree not in {0, 1}:
            raise ValueError("Serre arrows have Čech degree zero or one")


@dataclass(frozen=True, slots=True)
class SchoenSerreConstituent:
    """A fiber-sensitive constituent twisted complex on the Schoen cover."""

    name: str
    factor: int
    twist: LineDegree
    cocycle: DPSurfaceSerreCechCocycle | None
    objects: tuple[SerreObject, ...]
    arrows: tuple[SerreArrow, ...]


def schoen_unit_constituent() -> SchoenSerreConstituent:
    """Return the trivially linearized structure sheaf as a one-object complex."""

    return SchoenSerreConstituent(
        "O_X",
        0,
        (0, 0, 0),
        None,
        (SerreObject("O_X", 0, (0, 0, 0)),),
        (),
    )


def schoen_serre_constituent(
    name: str,
    factor: int,
    twist: LineDegree,
    cocycle: DPSurfaceSerreCechCocycle,
) -> SchoenSerreConstituent:
    """Embed one certified dP9 Serre cone in the common Schoen grading."""

    if factor != cocycle.extension.surface_factor:
        raise ValueError("constituent and cocycle use different Schoen factors")
    if len(twist) != 3:
        raise ValueError("Schoen twists require three integral degrees")
    position = factor - 1

    def line(base_shift: int, fiber_shift: int) -> LineDegree:
        values = list(twist)
        values[position] -= base_shift
        values[2] += fiber_shift
        return tuple(values)  # type: ignore[return-value]

    objects = [SerreObject("A", 0, line(0, -1))]
    objects.extend(
        SerreObject(f"F0:{index}", 0, line(degree, 1))
        for index, degree in enumerate(cocycle.extension.generator_degrees)
    )
    objects.extend(
        SerreObject(f"F1:{index}", -1, line(degree, 1))
        for index, degree in enumerate(cocycle.extension.syzygy_degrees)
    )
    generator_offset = 1
    syzygy_offset = 1 + len(cocycle.extension.generator_degrees)
    factor_name = "x" if factor == 1 else "u"
    arrows = []
    for row, matrix_row in enumerate(cocycle.extension.scheme.resolution.matrix):
        for column, polynomial in enumerate(matrix_row):
            if not polynomial.is_zero():
                arrows.append(
                    SerreArrow(
                        syzygy_offset + column,
                        generator_offset + row,
                        polynomial,
                        factor_name,
                        0,
                    )
                )
    for index, polynomial in enumerate(cocycle.generator_polynomials):
        if not polynomial.is_zero():
            arrows.append(
                SerreArrow(
                    generator_offset + index,
                    0,
                    polynomial,
                    factor_name,
                    1,
                )
            )
    return SchoenSerreConstituent(
        name,
        factor,
        twist,
        cocycle,
        tuple(objects),
        tuple(arrows),
    )


@cache
def _sparse_cech_ambient_map(
    source: AmbientSchoenSpace,
    target: AmbientSchoenSpace,
    polynomial: Polynomial,
    factor: str,
) -> SparseMap:
    """Cup with a base polynomial times the canonical ``H1(O(-2))`` class."""

    position = {"x": 0, "u": 1}[factor]
    expected = list(source.degrees)
    expected[position] += polynomial.degree
    expected[2] -= 2
    if tuple(expected) != target.degrees:
        raise ValueError("Čech cup map has incompatible ambient degrees")
    target_indices = {label: index for index, label in enumerate(target.labels)}
    local_data = {}
    for x_h, u_h, p_h in {
        (label[0], label[1], label[2]) for label in source.labels
    }:
        local_data[(x_h, u_h, p_h)] = (
            *_factor_matrix_for_terms(
                factor,
                source.degrees[position],
                target.degrees[position],
                (x_h, u_h)[position],
                polynomial,
            ),
            {
                monomial: index
                for index, monomial in enumerate(
                    _factor_basis(
                        factor,
                        source.degrees[position],
                        (x_h, u_h)[position],
                    )
                )
            },
        )
    rows: list[dict[int, Eisenstein]] = [{} for _ in target.labels]
    for source_index, label in enumerate(source.labels):
        x_h, u_h, p_h, x_monomial, u_monomial, p_monomial = label
        if source.degrees[2] != 0 or p_h != 0 or p_monomial != (0, 0):
            continue
        h = (x_h, u_h, p_h)
        target_basis, factor_rows, source_indices = local_data[h]
        source_monomial = (x_monomial, u_monomial)[position]
        local_source = source_indices[source_monomial]
        for local_target, target_monomial in enumerate(target_basis):
            coefficient = factor_rows[local_target][local_source]
            if coefficient.is_zero():
                continue
            target_label = (
                x_h,
                u_h,
                1,
                target_monomial if factor == "x" else x_monomial,
                target_monomial if factor == "u" else u_monomial,
                (-1, -1),
            )
            target_index = target_indices.get(target_label)
            if target_index is None:
                raise ValueError("Čech cup map escaped its ambient target basis")
            rows[target_index][source_index] = coefficient
    return SparseMap(source.vector_space, target.vector_space, _freeze_rows(rows))


@cache
def _sparse_cech_line_map(
    source: SparseLineBundle,
    target: SparseLineBundle,
    polynomial: Polynomial,
    factor: str,
) -> tuple[tuple[int, SparseMap], ...]:
    """Lift the odd Čech cup map through the signed Schoen Koszul complex."""

    position = {"x": 0, "u": 1}[factor]
    expected = list(source.degrees)
    expected[position] += polynomial.degree
    expected[2] -= 2
    if tuple(expected) != target.degrees:
        raise ValueError("Čech line map has incompatible line degrees")
    results = []
    signs = (1, -1, -1, 1)
    for degree in _KOSZUL_TOTAL_DEGREES:
        source_blocks = (
            source.ambient_k0.space(degree),
            source.ambient_k1_x.space(degree + 1),
            source.ambient_k1_u.space(degree + 1),
            source.ambient_k2.space(degree + 2),
        )
        target_blocks = (
            target.ambient_k0.space(degree + 1),
            target.ambient_k1_x.space(degree + 2),
            target.ambient_k1_u.space(degree + 2),
            target.ambient_k2.space(degree + 3),
        )
        diagonal = tuple(
            _sparse_cech_ambient_map(source_block, target_block, polynomial, factor).scale(
                signs[index]
            )
            for index, (source_block, target_block) in enumerate(
                zip(source_blocks, target_blocks, strict=True)
            )
        )
        blocks = tuple(
            tuple(
                diagonal[row]
                if row == column
                else SparseMap.zero(
                    source_blocks[column].vector_space,
                    target_blocks[row].vector_space,
                )
                for column in range(4)
            )
            for row in range(4)
        )
        assembled = SparseMap.block(blocks)
        if (
            assembled.domain.dimension != source.space(degree).dimension
            or assembled.codomain.dimension != target.space(degree + 1).dimension
        ):
            raise ValueError("Čech line map block dimensions do not match line spaces")
        results.append(
            (
                degree,
                SparseMap(
                    source.space(degree),
                    target.space(degree + 1),
                    assembled.rows,
                ),
            )
        )
    for degree, map_ in results[:-1]:
        left = target.differential(degree + 1).compose(map_)
        right = dict(results)[degree + 1].compose(source.differential(degree))
        if not (left + right).is_zero():
            raise ValueError("Čech cup map does not anticommute with the Koszul differential")
    return tuple(results)


@dataclass(frozen=True, slots=True)
class HomComponent:
    """One line-bundle summand of a twisted-complex outer Hom."""

    left_index: int
    right_index: int
    structural_degree: int
    sheaf_degree: int
    bundle: SparseLineBundle

    @property
    def total_degree(self) -> int:
        """Return structural plus sheaf cohomological degree."""

        return self.structural_degree + self.sheaf_degree


@dataclass(frozen=True, slots=True)
class SchoenSerreOuterHom:
    """Sparse synchronized outer RHom of two constituent twisted complexes."""

    left: SchoenSerreConstituent
    right: SchoenSerreConstituent
    components: tuple[HomComponent, ...]
    total_spaces: tuple[tuple[int, VectorSpace], ...]
    total_differentials: tuple[tuple[int, SparseMap], ...]

    @property
    def squared_zero(self) -> bool:
        """Return whether every consecutive sparse differential composes to zero."""

        maps = dict(self.total_differentials)
        return all(
            maps[degree + 1].compose(map_).is_zero()
            for degree, map_ in self.total_differentials
            if degree + 1 in maps
        )

    def cohomology_dimension(self, degree: int) -> int:
        """Return one exact sparse outer-Hom cohomology dimension."""

        return _sparse_rank_data(
            dict(self.total_spaces),
            dict(self.total_differentials),
            degree,
        )

    def as_record(self) -> dict[str, object]:
        """Serialize dimensions and exact gates without a quotient claim."""

        return {
            "left": self.left.name,
            "right": self.right.name,
            "total_dimensions": [
                [degree, space.dimension] for degree, space in self.total_spaces
            ],
            "cohomology_dimensions": [
                [degree, self.cohomology_dimension(degree)]
                for degree, _ in self.total_spaces
            ],
            "squared_zero": self.squared_zero,
            "status": (
                "exact ambient-cohomology-reduced Schoen outer model; full "
                "Cech transfer and quotient deck action remain unresolved"
            ),
        }


def _line_difference(left: LineDegree, right: LineDegree) -> LineDegree:
    """Return the line degree of ``Hom(right,left)``."""

    return tuple(
        left_value - right_value
        for left_value, right_value in zip(left, right, strict=True)
    )  # type: ignore[return-value]


def _component_map(
    source: HomComponent,
    target: HomComponent,
    left: SchoenSerreConstituent,
    right: SchoenSerreConstituent,
) -> SparseMap:
    """Assemble all internal and twisted-complex contributions between two cells."""

    result = SparseMap.zero(
        source.bundle.space(source.sheaf_degree),
        target.bundle.space(target.sheaf_degree),
    )
    if (
        source.left_index == target.left_index
        and source.right_index == target.right_index
        and target.sheaf_degree == source.sheaf_degree + 1
    ):
        result = result + source.bundle.differential(source.sheaf_degree).scale(
            -1 if source.structural_degree % 2 else 1
        )
    for arrow in left.arrows:
        if (
            source.left_index == arrow.source
            and target.left_index == arrow.target
            and source.right_index == target.right_index
            and target.sheaf_degree == source.sheaf_degree + arrow.cech_degree
        ):
            if arrow.cech_degree:
                map_ = dict(
                    _sparse_cech_line_map(
                        source.bundle,
                        target.bundle,
                        arrow.polynomial,
                        arrow.factor,
                    )
                )[source.sheaf_degree]
            else:
                map_ = dict(
                    source.bundle.multiplication(
                        target.bundle,
                        arrow.polynomial,
                        arrow.factor,
                    )
                )[source.sheaf_degree]
            result = result + map_
    for arrow in right.arrows:
        if (
            source.right_index == arrow.target
            and target.right_index == arrow.source
            and source.left_index == target.left_index
            and target.sheaf_degree == source.sheaf_degree + arrow.cech_degree
        ):
            if arrow.cech_degree:
                map_ = dict(
                    _sparse_cech_line_map(
                        source.bundle,
                        target.bundle,
                        arrow.polynomial,
                        arrow.factor,
                    )
                )[source.sheaf_degree]
            else:
                map_ = dict(
                    source.bundle.multiplication(
                        target.bundle,
                        arrow.polynomial,
                        arrow.factor,
                    )
                )[source.sheaf_degree]
            sign = -1 if source.structural_degree % 2 == 0 else 1
            result = result + map_.scale(sign)
    return result


@cache
def schoen_serre_outer_hom(
    left: SchoenSerreConstituent,
    right: SchoenSerreConstituent,
) -> SchoenSerreOuterHom:
    """Build the cohomology-reduced sparse ``RHom(right,left)`` model."""

    components = tuple(
        HomComponent(
            left_index,
            right_index,
            left_object.position - right_object.position,
            sheaf_degree,
            sparse_line_bundle(
                *_line_difference(left_object.line_degree, right_object.line_degree)
            ),
        )
        for left_index, left_object in enumerate(left.objects)
        for right_index, right_object in enumerate(right.objects)
        for sheaf_degree in _KOSZUL_TOTAL_DEGREES
    )
    by_degree = {
        degree: tuple(component for component in components if component.total_degree == degree)
        for degree in sorted({component.total_degree for component in components})
    }
    spaces = {
        degree: _sparse_direct_sum_space(
            tuple(component.bundle.space(component.sheaf_degree) for component in selected)
        )
        for degree, selected in by_degree.items()
    }
    maps = {}
    for degree, source_components in by_degree.items():
        target_components = by_degree.get(degree + 1, ())
        if not target_components:
            maps[degree] = SparseMap.zero(
                spaces[degree],
                VectorSpace("zero", (), Eisenstein),
            )
            continue
        maps[degree] = SparseMap.block(
            tuple(
                tuple(
                    _component_map(source, target, left, right)
                    for source in source_components
                )
                for target in target_components
            )
        )
    result = SchoenSerreOuterHom(
        left,
        right,
        components,
        tuple(sorted(spaces.items())),
        tuple(sorted(maps.items())),
    )
    if not result.squared_zero:
        raise ValueError("cohomology-reduced Schoen outer model is not square zero")
    return result


__all__ = [
    "SchoenSerreConstituent",
    "SchoenSerreOuterHom",
    "schoen_serre_constituent",
    "schoen_serre_outer_hom",
    "schoen_unit_constituent",
]
