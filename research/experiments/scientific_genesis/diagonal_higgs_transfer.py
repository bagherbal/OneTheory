"""Transfer the published constituent tensor through the diagonal Schoen cover.

Owns:
    The ordered tensor of the two published Serre cones with independent base
    Čech degrees, the three-equation diagonal Koszul perturbation, and its exact
    ambient-cohomology transfer.

Depends on:
    The certified constituent cocycles and the verified diagonal Schoen line
    presentation. No Higgs dimension is supplied to a rank calculation.

Must not:
    Collapse the two P1 covers before the diagonal equation, fit a differential,
    or identify transferred dimensions with physical states before deck descent.

Phase 0:
    Research-only synchronized constituent tensor transfer.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import cache
from typing import cast

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.schoen_serre_outer import (
    SchoenSerreConstituent,
    SerreArrow,
    schoen_serre_constituent,
)
from research.experiments.computable_carrier.schoen_sparse_outer import (
    SparseMap,
    _freeze_rows,
    _sparse_direct_sum_space,
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
from .published_constituent_mapping_cones import published_constituent_mapping_cones


@dataclass(frozen=True, slots=True, order=True)
class TensorObject:
    """One ordered pair of constituent objects before diagonal restriction."""

    first_index: int
    second_index: int
    name: str
    position: int
    first_position: int
    ambient_degrees: LineDegree4


@dataclass(frozen=True, slots=True, order=True)
class TensorComponent:
    """One tensor object and diagonal Koszul wedge summand."""

    object_index: int
    subset: tuple[int, ...]
    structural_degree: int
    ambient_degrees: LineDegree4


@dataclass(frozen=True, slots=True)
class TensorReducedEntry:
    """One compact ambient-cohomology coordinate of the tensor complex."""

    index: int
    component: TensorComponent
    monomials: tuple[Monomial, Monomial, Monomial, Monomial]


@dataclass(frozen=True, slots=True, order=True)
class TensorFullBasis:
    """One tensor Laurent monomial on a four-factor product-cover cell."""

    component: TensorComponent
    monomials: tuple[Monomial, Monomial, Monomial, Monomial]
    cell: Cell4


@dataclass(frozen=True, slots=True)
class TensorFullCochain:
    """One normalized sparse cochain in the full tensor Čech complex."""

    terms: tuple[tuple[TensorFullBasis, Eisenstein], ...]

    def __init__(
        self,
        terms: tuple[tuple[TensorFullBasis, Eisenstein], ...] = (),
    ) -> None:
        values: dict[TensorFullBasis, Eisenstein] = {}
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

    def __add__(self, other: TensorFullCochain) -> TensorFullCochain:
        return TensorFullCochain(self.terms + other.terms)

    def scale(self, scalar: int | Eisenstein) -> TensorFullCochain:
        """Scale all coefficients exactly."""

        value = Eisenstein.coerce(scalar)
        return TensorFullCochain(
            tuple((basis, coefficient * value) for basis, coefficient in self.terms)
        )

    def is_zero(self) -> bool:
        """Return whether the normalized cochain has no terms."""

        return not self.terms


def _factor_degrees(
    constituent: SchoenSerreConstituent,
    object_index: int,
    base_slot: int,
) -> LineDegree4:
    """Place one common-base line degree on its own P1 factor."""

    x_degree, u_degree, p_degree = constituent.objects[object_index].line_degree
    if base_slot == 1:
        return (x_degree, p_degree, u_degree, 0)
    if base_slot == 3:
        return (x_degree, 0, u_degree, p_degree)
    raise ValueError("constituent base slots are one or three")


@cache
def _published_constituents(
) -> tuple[SchoenSerreConstituent, SchoenSerreConstituent]:
    """Return the two source-selected constituent cones in separate gradings."""

    first_cone, second_cone = published_constituent_mapping_cones()
    return (
        schoen_serre_constituent("V1", 1, (-1, 1, 0), first_cone.cocycle),
        schoen_serre_constituent("V2", 2, (1, -1, 0), second_cone.cocycle),
    )


@cache
def _tensor_objects() -> tuple[TensorObject, ...]:
    """Build the ordered external tensor objects before diagonal restriction."""

    first, second = _published_constituents()
    return tuple(
        TensorObject(
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
    """Index ordered constituent-object pairs deterministically."""

    return {
        (item.first_index, item.second_index): index
        for index, item in enumerate(_tensor_objects())
    }


@cache
def _components() -> tuple[TensorComponent, ...]:
    """Return all tensor-object and diagonal-Koszul components."""

    return tuple(
        TensorComponent(
            object_index,
            subset,
            object_.position - len(subset),
            _subtract_degrees(object_.ambient_degrees, subset),
        )
        for object_index, object_ in enumerate(_tensor_objects())
        for subset in _KOSZUL_SUBSETS
    )


@cache
def _reduced_entries(total_degree: int) -> tuple[TensorReducedEntry, ...]:
    """Build one exact compact E1 basis for the synchronized tensor."""

    entries = []
    index = 0
    for component in _components():
        ambient_degree = total_degree - component.structural_degree
        ambient = _ambient_space(component.ambient_degrees, ambient_degree)
        for _factor_degrees_value, monomials in ambient.labels:
            entries.append(TensorReducedEntry(index, component, monomials))
            index += 1
    return tuple(entries)


@cache
def _space(total_degree: int) -> VectorSpace:
    """Return one compact synchronized tensor cochain space."""

    return _sparse_direct_sum_space(
        tuple(
            _ambient_space(
                component.ambient_degrees,
                total_degree - component.structural_degree,
            ).vector_space
            for component in _components()
        )
    )


def _include(entry: TensorReducedEntry) -> TensorFullCochain:
    """Include one ambient cohomology coordinate as a canonical Čech cocycle."""

    cech = _product_cech(entry.monomials)
    representative = cech.canonical_representative()
    degree = sum(factor.expected_cohomology_degree or 0 for factor in cech.factors)
    return TensorFullCochain(
        tuple(
            (
                TensorFullBasis(entry.component, entry.monomials, cast(Cell4, cell)),
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


def _homotopy(cochain: TensorFullCochain) -> TensorFullCochain:
    """Contract raw product Čech cochains at fixed tensor/Koszul component."""

    groups: dict[
        tuple[TensorComponent, tuple[Monomial, Monomial, Monomial, Monomial]],
        dict[Cell4, Eisenstein],
    ] = defaultdict(dict)
    for basis, coefficient in cochain.terms:
        groups[(basis.component, basis.monomials)][basis.cell] = coefficient
    result = []
    for (component, monomials), values in groups.items():
        cech = _product_cech(monomials)
        degrees = {
            sum(len(simplex) - 1 for simplex in cell)
            for cell in values
        }
        if len(degrees) != 1:
            raise ValueError("one tensor Laurent monomial spans multiple Čech degrees")
        degree = next(iter(degrees))
        contracted = cech.contracting_homotopy(cech.cochain(degree, values))
        sign = -1 if component.structural_degree % 2 else 1
        for cell, coefficient in zip(
            cech.cells_at(degree - 1),
            contracted.coordinates,
            strict=True,
        ):
            if not coefficient.is_zero():
                result.append(
                    (
                        TensorFullBasis(component, monomials, cast(Cell4, cell)),
                        cast(Eisenstein, coefficient) * sign,
                    )
                )
    return TensorFullCochain(tuple(result))


@cache
def _target_component(
    object_index: int,
    subset: tuple[int, ...],
) -> TensorComponent:
    """Resolve one adjacent tensor/Koszul component."""

    return next(
        component
        for component in _components()
        if component.object_index == object_index and component.subset == subset
    )


@cache
def _arrows_from(
    constituent_index: int,
    source_index: int,
) -> tuple[SerreArrow, ...]:
    """Return source-indexed arrows for one published constituent."""

    constituent = _published_constituents()[constituent_index]
    return tuple(
        arrow for arrow in constituent.arrows if arrow.source == source_index
    )


def _add_global_images(
    result: list[tuple[TensorFullBasis, Eisenstein]],
    basis: TensorFullBasis,
    coefficient: Eisenstein,
    target: TensorComponent,
    polynomial: Polynomial,
    factor_index: int,
) -> None:
    """Append multiplication by one x- or u-factor polynomial."""

    for exponents, scalar in polynomial.terms:
        monomials = list(basis.monomials)
        monomials[factor_index] = tuple(
            left + right
            for left, right in zip(
                monomials[factor_index],
                exponents,
                strict=True,
            )
        )
        result.append(
            (
                TensorFullBasis(
                    target,
                    cast(tuple[Monomial, Monomial, Monomial, Monomial], tuple(monomials)),
                    basis.cell,
                ),
                coefficient * cast(Eisenstein, scalar),
            )
        )


def _add_extension_images(
    result: list[tuple[TensorFullBasis, Eisenstein]],
    basis: TensorFullBasis,
    coefficient: Eisenstein,
    target: TensorComponent,
    arrow: SerreArrow,
    base_factor: int,
    polynomial_factor: int,
) -> None:
    """Cup with one constituent cocycle on its independent P1 cover."""

    if basis.cell[base_factor] != (1,):
        return
    cells = list(basis.cell)
    cells[base_factor] = (0, 1)
    monomials = list(basis.monomials)
    monomials[base_factor] = tuple(
        value - 1 for value in monomials[base_factor]
    )
    preceding_degree = sum(
        len(simplex) - 1 for simplex in basis.cell[:base_factor]
    )
    tensor_sign = -1 if preceding_degree % 2 else 1
    seed = TensorFullBasis(
        target,
        cast(tuple[Monomial, Monomial, Monomial, Monomial], tuple(monomials)),
        cast(Cell4, tuple(cells)),
    )
    _add_global_images(
        result,
        seed,
        coefficient * tensor_sign,
        target,
        arrow.polynomial,
        polynomial_factor,
    )


def _add_equation_images(
    result: list[tuple[TensorFullBasis, Eisenstein]],
    basis: TensorFullBasis,
    coefficient: Eisenstein,
    target: TensorComponent,
    equation: int,
) -> None:
    """Append one diagonal-presentation equation on a fixed cover cell."""

    for exponents, scalar in _equation_terms(equation):
        monomials = cast(
            tuple[Monomial, Monomial, Monomial, Monomial],
            tuple(
                tuple(left + right for left, right in zip(monomial, exponent, strict=True))
                for monomial, exponent in zip(
                    basis.monomials,
                    exponents,
                    strict=True,
                )
            ),
        )
        result.append(
            (
                TensorFullBasis(target, monomials, basis.cell),
                coefficient * scalar,
            )
        )


def _perturbation(cochain: TensorFullCochain) -> TensorFullCochain:
    """Apply tensor arrows and all three Koszul equations exactly."""

    objects = _tensor_objects()
    indices = _object_indices()
    result = []
    for basis, coefficient in cochain.terms:
        component = basis.component
        object_ = objects[component.object_index]
        object_sign = -1 if object_.position % 2 else 1
        first_object_sign = -1 if object_.first_position % 2 else 1
        koszul_sign = -1 if len(component.subset) % 2 else 1
        for position, equation in enumerate(component.subset):
            target_subset = tuple(
                index for index in component.subset if index != equation
            )
            target = _target_component(component.object_index, target_subset)
            orientation = -1 if position % 2 else 1
            equation_sign = (
                first_object_sign
                if equation == 0
                else object_sign * orientation
            )
            _add_equation_images(
                result,
                basis,
                coefficient * equation_sign,
                target,
                equation,
            )
        for arrow in _arrows_from(0, object_.first_index):
            target = _target_component(
                indices[(arrow.target, object_.second_index)],
                component.subset,
            )
            if arrow.cech_degree:
                _add_extension_images(
                    result,
                    basis,
                    coefficient * object_sign * koszul_sign,
                    target,
                    arrow,
                    1,
                    0,
                )
            else:
                _add_global_images(
                    result,
                    basis,
                    coefficient,
                    target,
                    arrow.polynomial,
                    0,
                )
        for arrow in _arrows_from(1, object_.second_index):
            target = _target_component(
                indices[(object_.first_index, arrow.target)],
                component.subset,
            )
            if arrow.cech_degree:
                _add_extension_images(
                    result,
                    basis,
                    coefficient * object_sign * koszul_sign,
                    target,
                    arrow,
                    3,
                    2,
                )
            else:
                first_koszul_degree = int(0 in component.subset)
                first_sign = (
                    -1
                    if (object_.first_position + first_koszul_degree) % 2
                    else 1
                )
                _add_global_images(
                    result,
                    basis,
                    coefficient * first_sign,
                    target,
                    arrow.polynomial,
                    2,
                )
    return TensorFullCochain(tuple(result))


def _projection_index(
    basis: TensorFullBasis,
    target_indices: dict[
        tuple[TensorComponent, tuple[Monomial, Monomial, Monomial, Monomial]],
        int,
    ],
) -> int | None:
    """Project one canonical product cocycle to a reduced tensor coordinate."""

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
    return target_indices.get((basis.component, basis.monomials))


@cache
def _transferred_map(total_degree: int) -> tuple[SparseMap, int]:
    """Transfer one synchronized tensor differential through full Čech data."""

    source_entries = _reduced_entries(total_degree)
    target_entries = _reduced_entries(total_degree + 1)
    target_indices = {
        (entry.component, entry.monomials): entry.index for entry in target_entries
    }
    rows: list[dict[int, Eisenstein]] = [dict() for _ in target_entries]
    maximum_depth = 0
    for source in source_entries:
        current = _include(source)
        depth = 0
        while not current.is_zero():
            image = _perturbation(current)
            for basis, coefficient in image.terms:
                target_index = _projection_index(basis, target_indices)
                if target_index is not None:
                    rows[target_index][source.index] = rows[target_index].get(
                        source.index,
                        Eisenstein(0),
                    ) + coefficient
            current = _homotopy(image).scale(-1)
            depth += 1
            if depth > 16:
                raise ValueError("diagonal tensor perturbation did not terminate")
        maximum_depth = max(maximum_depth, depth)
    return (
        SparseMap(_space(total_degree), _space(total_degree + 1), _freeze_rows(rows)),
        maximum_depth,
    )


@dataclass(frozen=True, slots=True)
class DiagonalHiggsTransfer:
    """The exact transferred tensor of the currently reconstructed cones."""

    spaces: tuple[tuple[int, VectorSpace], ...]
    differentials: tuple[tuple[int, SparseMap], ...]
    path_depths: tuple[tuple[int, int], ...]

    @property
    def squared_zero(self) -> bool:
        """Return whether every consecutive transferred map composes to zero."""

        maps = dict(self.differentials)
        return all(
            maps[degree + 1].compose(map_).is_zero()
            for degree, map_ in self.differentials
            if degree + 1 in maps
        )

    def cohomology_dimension(self, degree: int) -> int:
        """Return one exact transferred cohomology dimension."""

        spaces = dict(self.spaces)
        maps = dict(self.differentials)
        return (
            spaces[degree].dimension
            - (maps[degree - 1].rank() if degree - 1 in maps else 0)
            - (maps[degree].rank() if degree in maps else 0)
        )

    @property
    def geometric_dimensions(self) -> tuple[int, int, int, int]:
        """Return exact dimensions in geometric degrees zero through three."""

        return cast(
            tuple[int, int, int, int],
            tuple(self.cohomology_dimension(degree) for degree in range(4)),
        )

    @property
    def matches_published_higgs_cohomology(self) -> bool:
        """Return whether this cone tensor reproduces the source cover result."""

        return self.geometric_dimensions == (0, 4, 4, 0)


@cache
def diagonal_higgs_transfer() -> DiagonalHiggsTransfer:
    """Construct the synchronized tensor without identifying it as published."""

    structural_degrees = tuple(component.structural_degree for component in _components())
    degrees = tuple(
        range(min(structural_degrees), max(structural_degrees) + 7)
    )
    spaces = tuple((degree, _space(degree)) for degree in degrees)
    maps_with_depths = tuple(
        (degree, _transferred_map(degree)) for degree in degrees[:-1]
    )
    result = DiagonalHiggsTransfer(
        spaces,
        tuple((degree, item[0]) for degree, item in maps_with_depths),
        tuple((degree, item[1]) for degree, item in maps_with_depths),
    )
    if not result.squared_zero:
        raise ValueError("diagonal Higgs transfer differential is not square zero")
    return result


__all__ = ["DiagonalHiggsTransfer", "diagonal_higgs_transfer"]
