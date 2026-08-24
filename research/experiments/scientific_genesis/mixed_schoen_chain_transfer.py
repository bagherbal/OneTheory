"""Transfer the lawful mixed-Schoen chain diagonal through ambient cohomology.

Owns:
    The exact contraction of the grouped four-factor Cech differential and
    homological perturbation transfer of the certified chain diagonal.

Depends on:
    The lawful independent-cover chain diagonal, exact ambient line
    cohomology, and reusable sparse exact linear algebra.

Must not:
    Import retired constituent cones, fit transfer signs, select a deck
    character, or identify a transferred class as a physical Higgs state.

Phase 0:
    Research-only exact transfer at the lawful Higgs frontier.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import cache
from typing import cast

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_sparse_outer import (
    _sparse_direct_sum_space,
)

from .diagonal_schoen_lines import Cell4, Monomial, _ambient_space, _product_cech
from .mixed_schoen_chain_diagonal import (
    ChainDiagonalBasis,
    ChainDiagonalCochain,
    ChainDiagonalComponent,
    ChainDiagonalReducedEntry,
    _components,
    _reduced_entries,
    chain_diagonal_cech_differential,
    chain_diagonal_objects,
    chain_diagonal_perturbation,
)


def _constituent_structural_degrees(
    component: ChainDiagonalComponent,
) -> tuple[int, int]:
    """Return the two local object-minus-Koszul degrees."""

    object_ = chain_diagonal_objects()[component.object_index]
    return (
        object_.first_position - int(0 in component.subset),
        object_.position - object_.first_position - int(1 in component.subset),
    )


def _second_cech_degree(cell: Cell4) -> int:
    """Return the Cech degree on the second constituent's two cover factors."""

    return sum(len(simplex) - 1 for simplex in cell[2:])


def _conjugation_sign(
    component: ChainDiagonalComponent,
    cell: Cell4,
) -> int:
    """Conjugate the grouped raw differential to the standard product Cech one."""

    _first_degree, second_degree = _constituent_structural_degrees(component)
    return -1 if second_degree * _second_cech_degree(cell) % 2 else 1


@cache
def _space(total_degree: int) -> VectorSpace:
    """Return one exact reduced ambient-cohomology space."""

    return _sparse_direct_sum_space(
        tuple(
            _ambient_space(
                component.ambient_degrees,
                total_degree - component.structural_degree,
            ).vector_space
            for component in _components()
        )
    )


def _include(entry: ChainDiagonalReducedEntry) -> ChainDiagonalCochain:
    """Include a reduced coordinate through the grouped-differential conjugation."""

    cech = _product_cech(entry.monomials)
    representative = cech.canonical_representative()
    degree = sum(factor.expected_cohomology_degree or 0 for factor in cech.factors)
    return ChainDiagonalCochain(
        tuple(
            (
                ChainDiagonalBasis(
                    entry.component,
                    entry.monomials,
                    cast(Cell4, cell),
                ),
                cast(Eisenstein, coefficient)
                * _conjugation_sign(entry.component, cast(Cell4, cell)),
            )
            for cell, coefficient in zip(
                cech.cells_at(degree),
                representative.coordinates,
                strict=True,
            )
            if not coefficient.is_zero()
        )
    )


def _homotopy(cochain: ChainDiagonalCochain) -> ChainDiagonalCochain:
    """Contract the grouped raw Cech complex by exact sign conjugation."""

    groups: dict[
        tuple[
            ChainDiagonalComponent,
            tuple[Monomial, Monomial, Monomial, Monomial],
        ],
        dict[Cell4, Eisenstein],
    ] = defaultdict(dict)
    for basis, coefficient in cochain.terms:
        sign = _conjugation_sign(basis.component, basis.cell)
        groups[(basis.component, basis.monomials)][basis.cell] = coefficient * sign
    result = []
    for (component, monomials), values in groups.items():
        cech = _product_cech(monomials)
        degrees = {sum(len(simplex) - 1 for simplex in cell) for cell in values}
        if len(degrees) != 1:
            raise ValueError("one tensor Laurent monomial spans multiple Cech degrees")
        degree = next(iter(degrees))
        if degree == 0:
            continue
        contracted = cech.contracting_homotopy(cech.cochain(degree, values))
        first_degree, _second_degree = _constituent_structural_degrees(component)
        first_sign = -1 if first_degree % 2 else 1
        for cell, coefficient in zip(
            cech.cells_at(degree - 1),
            contracted.coordinates,
            strict=True,
        ):
            if coefficient.is_zero():
                continue
            target_cell = cast(Cell4, cell)
            result.append(
                (
                    ChainDiagonalBasis(component, monomials, target_cell),
                    cast(Eisenstein, coefficient)
                    * first_sign
                    * _conjugation_sign(component, target_cell),
                )
            )
    return ChainDiagonalCochain(tuple(result))


def _projection_index(
    basis: ChainDiagonalBasis,
    target_indices: dict[
        tuple[
            ChainDiagonalComponent,
            tuple[Monomial, Monomial, Monomial, Monomial],
        ],
        int,
    ],
) -> tuple[int, int] | None:
    """Project one grouped canonical product cocycle to a reduced coordinate."""

    supports = tuple(
        tuple(index for index, value in enumerate(monomial) if value < 0)
        for monomial in basis.monomials
    )
    sizes = (3, 2, 3, 2)
    if any(
        support and len(support) != size
        for support, size in zip(supports, sizes, strict=True)
    ):
        return None
    pivot = cast(
        Cell4,
        tuple(
            tuple(range(size)) if support else (0,)
            for support, size in zip(supports, sizes, strict=True)
        ),
    )
    if basis.cell != pivot:
        return None
    index = target_indices.get((basis.component, basis.monomials))
    if index is None:
        return None
    return index, _conjugation_sign(basis.component, basis.cell)


def _projected_inclusion(
    cochain: ChainDiagonalCochain,
    total_degree: int,
) -> ChainDiagonalCochain:
    """Apply the grouped projection followed by its canonical inclusion."""

    entries = _reduced_entries(total_degree)
    indices = {
        (entry.component, entry.monomials): entry.index for entry in entries
    }
    values: dict[int, Eisenstein] = {}
    for basis, coefficient in cochain.terms:
        projection = _projection_index(basis, indices)
        if projection is None:
            continue
        index, sign = projection
        values[index] = values.get(index, Eisenstein(0)) + coefficient * sign
    result = ChainDiagonalCochain()
    for index, coefficient in sorted(values.items()):
        if not coefficient.is_zero():
            result = result + _include(entries[index]).scale(coefficient)
    return result


@dataclass(frozen=True, slots=True)
class RawContractionWitness:
    """One exact grouped-Cech contraction-identity witness."""

    degree: int
    source_index: int
    input_term_count: int
    residual_term_count: int

    @property
    def exact(self) -> bool:
        """Return whether the contraction identity closes exactly."""

        return self.residual_term_count == 0


@cache
def raw_contraction_witness(
    degree: int = 0,
    source_index: int = 0,
) -> RawContractionWitness:
    """Check the conjugated contraction on one nontrivial perturbation image."""

    source = _include(_reduced_entries(degree)[source_index])
    cochain = chain_diagonal_perturbation(source)
    left = chain_diagonal_cech_differential(_homotopy(cochain))
    left = left + _homotopy(chain_diagonal_cech_differential(cochain))
    right = cochain + _projected_inclusion(cochain, degree + 1).scale(-1)
    residual = left + right.scale(-1)
    return RawContractionWitness(
        degree,
        source_index,
        len(cochain.terms),
        len(residual.terms),
    )


@dataclass(frozen=True, slots=True)
class TransferredColumn:
    """One exact transferred differential column and its finite path depth."""

    degree: int
    source_index: int
    entries: tuple[tuple[int, Eisenstein], ...]
    path_depth: int


def _transferred_vector(
    total_degree: int,
    coefficients: tuple[tuple[int, Eisenstein], ...],
) -> TransferredColumn:
    """Transfer one arbitrary sparse reduced vector exactly."""

    source_entries = _reduced_entries(total_degree)
    target_entries = _reduced_entries(total_degree + 1)
    target_indices = {
        (entry.component, entry.monomials): entry.index for entry in target_entries
    }
    current = ChainDiagonalCochain()
    for source_index, coefficient in coefficients:
        current = current + _include(source_entries[source_index]).scale(coefficient)
    values: dict[int, Eisenstein] = {}
    depth = 0
    while not current.is_zero():
        image = chain_diagonal_perturbation(current)
        for basis, coefficient in image.terms:
            projection = _projection_index(basis, target_indices)
            if projection is None:
                continue
            target_index, sign = projection
            values[target_index] = values.get(target_index, Eisenstein(0)) + coefficient * sign
        current = _homotopy(image).scale(-1)
        depth += 1
        if depth > 24:
            raise ValueError("lawful chain-diagonal perturbation did not terminate")
    return TransferredColumn(
        total_degree,
        -1,
        tuple(
            (index, coefficient)
            for index, coefficient in sorted(values.items())
            if not coefficient.is_zero()
        ),
        depth,
    )


@cache
def transferred_column(total_degree: int, source_index: int) -> TransferredColumn:
    """Transfer one reduced source coordinate by homological perturbation."""

    result = _transferred_vector(
        total_degree,
        ((source_index, Eisenstein(1)),),
    )
    return TransferredColumn(
        result.degree,
        source_index,
        result.entries,
        result.path_depth,
    )


__all__ = [
    "RawContractionWitness",
    "TransferredColumn",
    "raw_contraction_witness",
    "transferred_column",
]
