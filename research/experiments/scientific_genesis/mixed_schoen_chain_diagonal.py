"""Construct the lawful mixed tensor before restricting to the fiber diagonal.

Owns:
    The independent four-factor Cech tensor of the two lawful mixed
    constituents, the three-equation Koszul diagonal, and exact raw
    differential-square witnesses.

Depends on:
    The selected full constituent Cech cocycles, their exact resolution
    arrows, and the verified diagonal Schoen complete-intersection equations.

Must not:
    Import retired constituent cones, flatten the two fiber covers before the
    diagonal equation, select a Higgs class, or infer physical multiplicities.

Phase 0:
    Research-only chain-diagonal construction for the lawful Higgs frontier.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .diagonal_schoen_lines import (
    _KOSZUL_SUBSETS,
    Cell4,
    LineDegree4,
    Monomial,
    _ambient_space,
    _equation_terms,
    _product_cech,
    _subtract_degrees,
)
from .mixed_constituent_schoen_arrows import (
    MixedResolutionArrow,
    MixedSchoenConstituent,
    mixed_schoen_constituents,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_chain_diagonal.json"


@dataclass(frozen=True, slots=True, order=True)
class ChainDiagonalObject:
    """One ordered pair of lawful constituent resolution objects."""

    first_index: int
    second_index: int
    name: str
    position: int
    first_position: int
    ambient_degrees: LineDegree4


@dataclass(frozen=True, slots=True, order=True)
class ChainDiagonalComponent:
    """One tensor object together with a diagonal Koszul wedge subset."""

    object_index: int
    subset: tuple[int, ...]
    structural_degree: int
    ambient_degrees: LineDegree4


@dataclass(frozen=True, slots=True, order=True)
class ChainDiagonalBasis:
    """One regular Laurent basis term on the four-factor standard cover."""

    component: ChainDiagonalComponent
    monomials: tuple[Monomial, Monomial, Monomial, Monomial]
    cell: Cell4

    @property
    def cech_degree(self) -> int:
        """Return the total product-cover Cech degree."""

        return sum(len(simplex) - 1 for simplex in self.cell)

    @property
    def total_degree(self) -> int:
        """Return structural plus Cech degree."""

        return self.component.structural_degree + self.cech_degree


@dataclass(frozen=True, slots=True)
class ChainDiagonalCochain:
    """One normalized exact sparse cochain in the four-factor tensor."""

    terms: tuple[tuple[ChainDiagonalBasis, Eisenstein], ...]

    def __init__(
        self,
        terms: tuple[tuple[ChainDiagonalBasis, Eisenstein], ...] = (),
    ) -> None:
        values: dict[ChainDiagonalBasis, Eisenstein] = {}
        for basis, coefficient in terms:
            values[basis] = values.get(basis, Eisenstein(0)) + coefficient
        object.__setattr__(
            self,
            "terms",
            tuple(
                (basis, coefficient)
                for basis, coefficient in sorted(values.items())
                if not coefficient.is_zero()
            ),
        )

    @classmethod
    def _from_normalized_terms(
        cls,
        terms: tuple[tuple[ChainDiagonalBasis, Eisenstein], ...],
    ) -> ChainDiagonalCochain:
        """Construct from sorted unique nonzero terms produced internally."""

        result = object.__new__(cls)
        object.__setattr__(result, "terms", terms)
        return result

    def _combine(
        self,
        other: ChainDiagonalCochain,
        other_sign: int,
    ) -> ChainDiagonalCochain:
        """Merge two normalized sparse cochains without a large hash table."""

        left_index = 0
        right_index = 0
        terms: list[tuple[ChainDiagonalBasis, Eisenstein]] = []
        while left_index < len(self.terms) and right_index < len(other.terms):
            left_basis, left_coefficient = self.terms[left_index]
            right_basis, right_coefficient = other.terms[right_index]
            if left_basis < right_basis:
                terms.append((left_basis, left_coefficient))
                left_index += 1
            elif right_basis < left_basis:
                terms.append((right_basis, right_coefficient * other_sign))
                right_index += 1
            else:
                coefficient = left_coefficient + right_coefficient * other_sign
                if not coefficient.is_zero():
                    terms.append((left_basis, coefficient))
                left_index += 1
                right_index += 1
        terms.extend(self.terms[left_index:])
        terms.extend(
            (basis, coefficient * other_sign) for basis, coefficient in other.terms[right_index:]
        )
        return self._from_normalized_terms(tuple(terms))

    def __add__(self, other: ChainDiagonalCochain) -> ChainDiagonalCochain:
        return self._combine(other, 1)

    def __sub__(self, other: ChainDiagonalCochain) -> ChainDiagonalCochain:
        return self._combine(other, -1)

    def scale(self, scalar: int | Eisenstein) -> ChainDiagonalCochain:
        """Scale every sparse coefficient exactly."""

        value = Eisenstein.coerce(scalar)
        return ChainDiagonalCochain(
            tuple((basis, coefficient * value) for basis, coefficient in self.terms)
        )

    def is_zero(self) -> bool:
        """Return whether the normalized support is empty."""

        return not self.terms


@dataclass(frozen=True, slots=True, order=True)
class ChainDiagonalExtensionTerm:
    """One lawful constituent extension term on independent product covers."""

    source: int
    target: int
    parent_degree: int
    koszul_equation: int | None
    monomials: tuple[Monomial, Monomial, Monomial, Monomial]
    cell: Cell4
    coefficient: Eisenstein
    factor: int

    @property
    def cech_degree(self) -> int:
        """Return the total four-factor Cech degree."""

        return sum(len(simplex) - 1 for simplex in self.cell)

    @property
    def koszul_degree(self) -> int:
        """Return whether this term carries a hypersurface wedge."""

        return int(self.koszul_equation is not None)


@dataclass(frozen=True, slots=True)
class ChainDiagonalReducedEntry:
    """One ambient-cohomology coordinate used as an exact square seed."""

    index: int
    component: ChainDiagonalComponent
    monomials: tuple[Monomial, Monomial, Monomial, Monomial]


def _factor_degrees(
    constituent: MixedSchoenConstituent,
    object_index: int,
    fiber_slot: int,
) -> LineDegree4:
    """Place one common-Schoen line degree on an independent fiber factor."""

    x_degree, u_degree, fiber_degree = constituent.objects[object_index].line_degree
    if fiber_slot == 1:
        return x_degree, fiber_degree, u_degree, 0
    if fiber_slot == 3:
        return x_degree, 0, u_degree, fiber_degree
    raise ValueError("independent fiber slots are one and three")


@cache
def chain_diagonal_objects() -> tuple[ChainDiagonalObject, ...]:
    """Return all ordered lawful constituent object pairs."""

    first, second = mixed_schoen_constituents()
    return tuple(
        ChainDiagonalObject(
            first_index,
            second_index,
            f"{first_object.name}*{second_object.name}",
            first_object.position + second_object.position,
            first_object.position,
            cast(
                LineDegree4,
                tuple(
                    left + right
                    for left, right in zip(
                        _factor_degrees(first, first_index, 1),
                        _factor_degrees(second, second_index, 3),
                        strict=True,
                    )
                ),
            ),
        )
        for first_index, first_object in enumerate(first.objects)
        for second_index, second_object in enumerate(second.objects)
    )


@cache
def _object_indices() -> dict[tuple[int, int], int]:
    """Return deterministic indices for all ordered object pairs."""

    return {
        (item.first_index, item.second_index): index
        for index, item in enumerate(chain_diagonal_objects())
    }


@cache
def _components() -> tuple[ChainDiagonalComponent, ...]:
    """Return every object and three-equation Koszul component."""

    return tuple(
        ChainDiagonalComponent(
            object_index,
            subset,
            object_.position - len(subset),
            _subtract_degrees(object_.ambient_degrees, subset),
        )
        for object_index, object_ in enumerate(chain_diagonal_objects())
        for subset in _KOSZUL_SUBSETS
    )


@cache
def _target_component(
    object_index: int,
    subset: tuple[int, ...],
) -> ChainDiagonalComponent:
    """Resolve one adjacent object/Koszul component."""

    return next(
        item
        for item in _components()
        if item.object_index == object_index and item.subset == subset
    )


def _source_index(
    constituent: MixedSchoenConstituent,
    parent_degree: int,
    bundle_index: int,
) -> int:
    """Map a full constituent resolution component to its object index."""

    if parent_degree == 0:
        return 1 + bundle_index
    generator_count = sum(item.name.startswith("F0:") for item in constituent.objects)
    if parent_degree == 1:
        return 1 + generator_count + bundle_index
    raise ValueError("constituent parent degrees are zero and one")


@cache
def chain_diagonal_extension_terms() -> tuple[ChainDiagonalExtensionTerm, ...]:
    """Embed both lawful full extension cocycles on independent covers."""

    first, second = mixed_schoen_constituents()
    indices = _object_indices()
    zero3 = (0, 0, 0)
    zero2 = (0, 0)
    result = []
    for basis, coefficient in first.full.representative.terms:
        source_first = _source_index(
            first,
            basis.component.parent_degree,
            basis.component.bundle_index,
        )
        equation = 0 if basis.component.koszul_degree else None
        for second_index in range(len(second.objects)):
            result.append(
                ChainDiagonalExtensionTerm(
                    indices[(source_first, second_index)],
                    indices[(0, second_index)],
                    basis.component.parent_degree,
                    equation,
                    (basis.base_monomial, basis.fiber_monomial, zero3, zero2),
                    cast(
                        Cell4,
                        (
                            basis.cell[0],
                            basis.cell[1],
                            (0,),
                            (0,),
                        ),
                    ),
                    coefficient,
                    1,
                )
            )
    for basis, coefficient in second.full.representative.terms:
        source_second = _source_index(
            second,
            basis.component.parent_degree,
            basis.component.bundle_index,
        )
        equation = 1 if basis.component.koszul_degree else None
        for first_index, _first_object in enumerate(first.objects):
            result.append(
                ChainDiagonalExtensionTerm(
                    indices[(first_index, source_second)],
                    indices[(first_index, 0)],
                    basis.component.parent_degree,
                    equation,
                    (zero3, zero2, basis.base_monomial, basis.fiber_monomial),
                    cast(
                        Cell4,
                        (
                            (0,),
                            (0,),
                            basis.cell[0],
                            basis.cell[1],
                        ),
                    ),
                    coefficient,
                    2,
                )
            )
    return tuple(result)


@cache
def _extension_terms_from(
    source: int,
) -> tuple[ChainDiagonalExtensionTerm, ...]:
    """Return source-indexed full extension terms."""

    return tuple(term for term in chain_diagonal_extension_terms() if term.source == source)


def _simplex_cup(
    left: tuple[int, ...],
    right: tuple[int, ...],
) -> tuple[int, ...] | None:
    """Return one ordered Alexander--Whitney simplex product."""

    left_degree = len(left) - 1
    right_degree = len(right) - 1
    combined = tuple(sorted(set((*left, *right))))
    if len(combined) != left_degree + right_degree + 1:
        return None
    if left != combined[: left_degree + 1]:
        return None
    if right != combined[left_degree:]:
        return None
    return combined


def _add_polynomial(
    result: list[tuple[ChainDiagonalBasis, Eisenstein]],
    basis: ChainDiagonalBasis,
    coefficient: Eisenstein,
    target: ChainDiagonalComponent,
    polynomial: Polynomial,
    factor_index: int,
) -> None:
    """Append multiplication by one homogeneous base polynomial."""

    for exponents, scalar in polynomial.terms:
        monomials = list(basis.monomials)
        monomials[factor_index] = tuple(
            left + right for left, right in zip(monomials[factor_index], exponents, strict=True)
        )
        result.append(
            (
                ChainDiagonalBasis(
                    target,
                    cast(tuple[Monomial, Monomial, Monomial, Monomial], tuple(monomials)),
                    basis.cell,
                ),
                coefficient * cast(Eisenstein, scalar),
            )
        )


def _add_equation(
    result: list[tuple[ChainDiagonalBasis, Eisenstein]],
    basis: ChainDiagonalBasis,
    coefficient: Eisenstein,
    target: ChainDiagonalComponent,
    equation: int,
) -> None:
    """Append one of the three exact diagonal-presentation equations."""

    for exponents, scalar in _equation_terms(equation):
        monomials = cast(
            tuple[Monomial, Monomial, Monomial, Monomial],
            tuple(
                tuple(left + right for left, right in zip(monomial, exponent, strict=True))
                for monomial, exponent in zip(basis.monomials, exponents, strict=True)
            ),
        )
        result.append((ChainDiagonalBasis(target, monomials, basis.cell), coefficient * scalar))


def _resolution_arrows_from(
    constituent: MixedSchoenConstituent,
    source: int,
) -> tuple[MixedResolutionArrow, ...]:
    """Return source-indexed lawful Hilbert--Burch arrows."""

    return tuple(arrow for arrow in constituent.resolution_arrows if arrow.source == source)


def _local_cell_cup(
    term: ChainDiagonalExtensionTerm,
    basis: ChainDiagonalBasis,
) -> tuple[int, Cell4] | None:
    """Cup one extension term only on the cover factors that own it."""

    slots = (0, 1) if term.factor == 1 else (2, 3)
    target_cell = list(basis.cell)
    products = []
    for slot in slots:
        target = _simplex_cup(term.cell[slot], basis.cell[slot])
        if target is None:
            return None
        products.append(target)
        target_cell[slot] = target
    left_degrees = tuple(len(term.cell[slot]) - 1 for slot in slots)
    right_degrees = tuple(len(basis.cell[slot]) - 1 for slot in slots)
    crossing = left_degrees[1] * right_degrees[0]
    return (-1 if crossing % 2 else 1), cast(Cell4, tuple(target_cell))


def _factor_cech_images(
    basis: ChainDiagonalBasis,
    coefficient: Eisenstein,
    factor: int,
    tensor_sign: int,
) -> ChainDiagonalCochain:
    """Apply one constituent's local two-factor Cech differential."""

    object_ = chain_diagonal_objects()[basis.component.object_index]
    if factor == 1:
        slots = (0, 1)
        position = object_.first_position
        own_koszul = int(0 in basis.component.subset)
    else:
        slots = (2, 3)
        position = object_.position - object_.first_position
        own_koszul = int(1 in basis.component.subset)
    structural_sign = -1 if (position - own_koszul) % 2 else 1
    result = []
    preceding_degree = 0
    sizes = (3, 2, 3, 2)
    for slot in slots:
        simplex = basis.cell[slot]
        for vertex in range(sizes[slot]):
            if vertex in simplex:
                continue
            target_simplex = tuple(sorted((*simplex, vertex)))
            local_sign = -1 if target_simplex.index(vertex) % 2 else 1
            product_sign = -1 if preceding_degree % 2 else 1
            target_cell = list(basis.cell)
            target_cell[slot] = target_simplex
            result.append(
                (
                    ChainDiagonalBasis(
                        basis.component,
                        basis.monomials,
                        cast(Cell4, tuple(target_cell)),
                    ),
                    coefficient * tensor_sign * structural_sign * local_sign * product_sign,
                )
            )
        preceding_degree += len(simplex) - 1
    return ChainDiagonalCochain(tuple(result))


def _factor_structural_images(
    basis: ChainDiagonalBasis,
    coefficient: Eisenstein,
    factor: int,
    tensor_sign: int,
) -> ChainDiagonalCochain:
    """Apply one lawful constituent's local structural superconnection."""

    first, second = mixed_schoen_constituents()
    constituent = first if factor == 1 else second
    equation = 0 if factor == 1 else 1
    polynomial_slot = 0 if factor == 1 else 2
    objects = chain_diagonal_objects()
    object_ = objects[basis.component.object_index]
    local_index = object_.first_index if factor == 1 else object_.second_index
    other_index = object_.second_index if factor == 1 else object_.first_index
    local_position = (
        object_.first_position if factor == 1 else object_.position - object_.first_position
    )
    result: list[tuple[ChainDiagonalBasis, Eisenstein]] = []
    if equation in basis.component.subset:
        target_subset = tuple(item for item in basis.component.subset if item != equation)
        target = _target_component(basis.component.object_index, target_subset)
        local_sign = -1 if local_position % 2 else 1
        _add_equation(
            result,
            basis,
            coefficient * tensor_sign * local_sign,
            target,
            equation,
        )
    for arrow in _resolution_arrows_from(constituent, local_index):
        pair = (arrow.target, other_index) if factor == 1 else (other_index, arrow.target)
        target = _target_component(
            _object_indices()[pair],
            basis.component.subset,
        )
        _add_polynomial(
            result,
            basis,
            coefficient * tensor_sign,
            target,
            arrow.polynomial,
            polynomial_slot,
        )
    own_koszul = int(equation in basis.component.subset)
    local_object_sign = -1 if local_position % 2 else 1
    local_koszul_sign = -1 if own_koszul else 1
    for term in _extension_terms_from(basis.component.object_index):
        if term.factor != factor:
            continue
        cell_product = _local_cell_cup(term, basis)
        if cell_product is None:
            continue
        if term.koszul_equation is not None and equation in basis.component.subset:
            continue
        cell_sign, target_cell = cell_product
        target_subset = (
            basis.component.subset
            if term.koszul_equation is None
            else tuple(sorted((*basis.component.subset, equation)))
        )
        target = _target_component(term.target, target_subset)
        internal_degree = term.cech_degree - term.koszul_degree
        sign = cell_sign * tensor_sign
        if internal_degree % 2:
            sign *= local_koszul_sign * local_object_sign
        if term.parent_degree == 0:
            sign *= -1
        monomials = cast(
            tuple[Monomial, Monomial, Monomial, Monomial],
            tuple(
                tuple(
                    left + right
                    for left, right in zip(
                        basis_monomial,
                        term_monomial,
                        strict=True,
                    )
                )
                for basis_monomial, term_monomial in zip(
                    basis.monomials,
                    term.monomials,
                    strict=True,
                )
            ),
        )
        result.append(
            (
                ChainDiagonalBasis(target, monomials, target_cell),
                coefficient * term.coefficient * sign,
            )
        )
    return ChainDiagonalCochain(tuple(result))


def _factor_total_degree(basis: ChainDiagonalBasis, factor: int) -> int:
    """Return one constituent's live object--Koszul--Cech total degree."""

    object_ = chain_diagonal_objects()[basis.component.object_index]
    if factor == 1:
        position = object_.first_position
        koszul = int(0 in basis.component.subset)
        slots = (0, 1)
    else:
        position = object_.position - object_.first_position
        koszul = int(1 in basis.component.subset)
        slots = (2, 3)
    cech = sum(len(basis.cell[slot]) - 1 for slot in slots)
    return position - koszul + cech


def chain_diagonal_cech_differential(
    cochain: ChainDiagonalCochain,
) -> ChainDiagonalCochain:
    """Apply the grouped raw Cech differential on both constituent covers."""

    values: dict[ChainDiagonalBasis, Eisenstein] = {}
    for basis, coefficient in cochain.terms:
        first_degree = _factor_total_degree(basis, 1)
        second_sign = -1 if first_degree % 2 else 1
        _accumulate_terms(
            values,
            _factor_cech_images(basis, coefficient, 1, 1).terms,
        )
        _accumulate_terms(
            values,
            _factor_cech_images(
                basis,
                coefficient,
                2,
                second_sign,
            ).terms,
        )
    return ChainDiagonalCochain._from_normalized_terms(tuple(sorted(values.items())))


def chain_diagonal_perturbation(
    cochain: ChainDiagonalCochain,
) -> ChainDiagonalCochain:
    """Apply constituent structural maps and the fiber-diagonal equation."""

    values: dict[ChainDiagonalBasis, Eisenstein] = {}
    for basis, coefficient in cochain.terms:
        first_degree = _factor_total_degree(basis, 1)
        second_degree = _factor_total_degree(basis, 2)
        second_sign = -1 if first_degree % 2 else 1
        _accumulate_terms(
            values,
            _factor_structural_images(basis, coefficient, 1, 1).terms,
        )
        _accumulate_terms(
            values,
            _factor_structural_images(
                basis,
                coefficient,
                2,
                second_sign,
            ).terms,
        )
        if 2 in basis.component.subset:
            target_subset = tuple(item for item in basis.component.subset if item != 2)
            target = _target_component(basis.component.object_index, target_subset)
            diagonal_sign = -1 if (first_degree + second_degree) % 2 else 1
            diagonal_terms: list[tuple[ChainDiagonalBasis, Eisenstein]] = []
            _add_equation(
                diagonal_terms,
                basis,
                coefficient * diagonal_sign,
                target,
                2,
            )
            _accumulate_terms(values, tuple(diagonal_terms))
    return ChainDiagonalCochain._from_normalized_terms(tuple(sorted(values.items())))


def grouped_chain_diagonal_differential(
    cochain: ChainDiagonalCochain,
) -> ChainDiagonalCochain:
    """Apply the strict tensor differential followed by the diagonal Koszul map."""

    return chain_diagonal_cech_differential(cochain) + chain_diagonal_perturbation(cochain)


def _accumulate_terms(
    values: dict[ChainDiagonalBasis, Eisenstein],
    terms: tuple[tuple[ChainDiagonalBasis, Eisenstein], ...],
) -> None:
    """Accumulate normalized sparse terms with immediate exact cancellation."""

    for basis, coefficient in terms:
        updated = values.get(basis, Eisenstein(0)) + coefficient
        if updated.is_zero():
            values.pop(basis, None)
        else:
            values[basis] = updated


def full_chain_diagonal_differential(
    cochain: ChainDiagonalCochain,
) -> ChainDiagonalCochain:
    """Apply the grouped differential with eager exact cancellation."""

    values: dict[ChainDiagonalBasis, Eisenstein] = {}

    for basis, coefficient in cochain.terms:
        first_degree = _factor_total_degree(basis, 1)
        second_degree = _factor_total_degree(basis, 2)
        second_sign = -1 if first_degree % 2 else 1
        _accumulate_terms(
            values,
            _factor_cech_images(basis, coefficient, 1, 1).terms,
        )
        _accumulate_terms(values, _factor_cech_images(basis, coefficient, 2, second_sign).terms)
        _accumulate_terms(values, _factor_structural_images(basis, coefficient, 1, 1).terms)
        _accumulate_terms(
            values,
            _factor_structural_images(
                basis,
                coefficient,
                2,
                second_sign,
            ).terms,
        )
        if 2 in basis.component.subset:
            target_subset = tuple(item for item in basis.component.subset if item != 2)
            target = _target_component(basis.component.object_index, target_subset)
            diagonal_sign = -1 if (first_degree + second_degree) % 2 else 1
            diagonal_terms: list[tuple[ChainDiagonalBasis, Eisenstein]] = []
            _add_equation(
                diagonal_terms,
                basis,
                coefficient * diagonal_sign,
                target,
                2,
            )
            _accumulate_terms(values, tuple(diagonal_terms))
    return ChainDiagonalCochain._from_normalized_terms(tuple(sorted(values.items())))


@cache
def _reduced_entries(total_degree: int) -> tuple[ChainDiagonalReducedEntry, ...]:
    """Return compact ambient-cohomology coordinates in one total degree."""

    entries = []
    index = 0
    for component in _components():
        ambient_degree = total_degree - component.structural_degree
        ambient = _ambient_space(component.ambient_degrees, ambient_degree)
        for _factor_degrees_value, monomials in ambient.labels:
            entries.append(ChainDiagonalReducedEntry(index, component, monomials))
            index += 1
    return tuple(entries)


def _include(entry: ChainDiagonalReducedEntry) -> ChainDiagonalCochain:
    """Include one ambient class as a canonical four-factor Cech cocycle."""

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
                cast(Eisenstein, coefficient),
            )
            for cell, coefficient in zip(
                cech.cells_at(degree),
                representative.coordinates,
                strict=True,
            )
            if not coefficient.is_zero()
        )
    )


@dataclass(frozen=True, slots=True)
class ChainDiagonalSquareWitness:
    """One deterministic exact raw differential-square audit."""

    degree: int
    reduced_index: int
    seed_term_count: int
    first_image_term_count: int
    square_term_count: int

    @property
    def squared_zero(self) -> bool:
        """Return whether this exact seed has zero differential square."""

        return self.square_term_count == 0


@cache
def chain_diagonal_square_witness(
    degree: int = 0,
    reduced_index: int = 0,
) -> ChainDiagonalSquareWitness:
    """Evaluate the raw square on one deterministic reduced seed."""

    entry = _reduced_entries(degree)[reduced_index]
    seed = _include(entry)
    first = full_chain_diagonal_differential(seed)
    square = full_chain_diagonal_differential(first)
    return ChainDiagonalSquareWitness(
        degree,
        reduced_index,
        len(seed.terms),
        len(first.terms),
        len(square.terms),
    )


def _square_job(job: tuple[int, int]) -> ChainDiagonalSquareWitness:
    """Evaluate one independent transfer-basis square in a worker process."""

    return chain_diagonal_square_witness(*job)


@dataclass(frozen=True, slots=True)
class ChainDiagonalSquareAudit:
    """The exhaustive exact square gate on the finite transfer basis."""

    degree_dimensions: tuple[tuple[int, int], ...]
    witnesses: tuple[ChainDiagonalSquareWitness, ...]

    @property
    def nonzero_witnesses(self) -> tuple[ChainDiagonalSquareWitness, ...]:
        """Return every transfer seed with a nonzero differential square."""

        return tuple(item for item in self.witnesses if not item.squared_zero)

    @property
    def squared_zero(self) -> bool:
        """Return whether all finite transfer seeds have exact zero square."""

        return not self.nonzero_witnesses

    def as_record(self) -> dict[str, object]:
        """Serialize the finite exhaustive square certificate."""

        return {
            "degree_dimensions": [list(item) for item in self.degree_dimensions],
            "witness_count": len(self.witnesses),
            "nonzero_witnesses": [
                {
                    "degree": item.degree,
                    "reduced_index": item.reduced_index,
                    "square_term_count": item.square_term_count,
                }
                for item in self.nonzero_witnesses
            ],
            "all_transfer_seed_squares_zero": self.squared_zero,
        }


@cache
def chain_diagonal_square_audit() -> ChainDiagonalSquareAudit:
    """Exhaust every nonzero ambient-cohomology transfer seed in parallel."""

    degree_dimensions = tuple((degree, len(_reduced_entries(degree))) for degree in range(5))
    jobs = tuple(
        (degree, index) for degree, dimension in degree_dimensions for index in range(dimension)
    )
    with ProcessPoolExecutor(max_workers=min(16, len(jobs))) as executor:
        witnesses = tuple(executor.map(_square_job, jobs, chunksize=8))
    result = ChainDiagonalSquareAudit(degree_dimensions, witnesses)
    if not result.squared_zero:
        first = result.nonzero_witnesses[0]
        raise ValueError(
            "the chain diagonal has a nonzero square at "
            f"degree {first.degree}, index {first.reduced_index}"
        )
    return result


def write_chain_diagonal_audit(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed lawful chain-diagonal certificate."""

    audit = chain_diagonal_square_audit()
    constituents = mixed_schoen_constituents()
    payload: dict[str, object] = {
        "schema": "mixed-schoen-chain-diagonal-v1",
        "construction": {
            "object_count": len(chain_diagonal_objects()),
            "full_extension_term_count": len(chain_diagonal_extension_terms()),
            "independent_cover_factor_count": 4,
            "diagonal_equation_count": 3,
            "signed_tensor_totalization": True,
        },
        "constituent_inputs": {
            "all_full_cech_cocycles_exact": all(item.full.exact for item in constituents),
            "retired_constituent_cones_used": False,
            "shared_cover_flattening_used": False,
        },
        "square_audit": audit.as_record(),
        "physical_higgs_representative_available": False,
        "next_required_object": (
            "exact ambient-cohomology transfer of the lawful chain diagonal, "
            "followed by strict P/T action and Higgs representative extraction"
        ),
        "status": (
            "lawful independent-cover tensor and fiber-diagonal Koszul complex "
            "constructed; every finite transfer seed has exact zero differential square"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the lawful chain-diagonal certificate."""

    payload = write_chain_diagonal_audit()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "all_transfer_seed_squares_zero: "
        f"{payload['square_audit']['all_transfer_seed_squares_zero']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ChainDiagonalCochain",
    "ChainDiagonalSquareAudit",
    "ChainDiagonalSquareWitness",
    "OUTPUT",
    "chain_diagonal_cech_differential",
    "chain_diagonal_extension_terms",
    "chain_diagonal_objects",
    "chain_diagonal_perturbation",
    "chain_diagonal_square_audit",
    "chain_diagonal_square_witness",
    "full_chain_diagonal_differential",
    "write_chain_diagonal_audit",
]
