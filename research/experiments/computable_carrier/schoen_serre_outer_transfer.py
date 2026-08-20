"""Transfer Serre-cone outer Hom differentials through the standard Čech cover.

Owns:
    Exact canonical inclusion, projection, tensor contraction, and finite
    homological-perturbation paths for outer Homs of declared Schoen Serre cones.

Depends on:
    The generic projective-product Čech contraction, exact published Schoen
    equations, certified constituent cocycles, and sparse reduced outer spaces.

Must not:
    Import published outer dimensions, fit a missing rank, infer quotient
    invariants, or promote a transferred cover calculation as physical input.

Phase 0:
    Research-only full-Čech transfer; quotient action and physical carrier gates
    remain separate calculations.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import cache
from typing import cast

from onetheory.math.cech import (
    ProductProjectiveMonomialCechComplex,
    product_projective_monomial_cech_complex,
    projective_monomial_cech_complex,
)
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry

from .schoen_serre_outer import (
    SchoenSerreConstituent,
    SchoenSerreOuterHom,
    schoen_serre_outer_hom,
)
from .schoen_sparse_outer import SparseMap, _freeze_rows

Monomial3 = tuple[int, int, int]
Monomial2 = tuple[int, int]
Cell = tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]
KOSZUL_DEGREES = {"k0": 0, "k1_x": -1, "k1_u": -1, "k2": -2}
KOSZUL_SHIFTS = {
    "k0": (0, 0, 0),
    "k1_x": (-3, 0, -1),
    "k1_u": (0, -3, -1),
    "k2": (-3, -3, -2),
}
KOSZUL_ORDER = ("k0", "k1_x", "k1_u", "k2")


@dataclass(frozen=True, slots=True, order=True)
class OuterCechComponent:
    """One object-pair and Koszul summand in a full outer Čech complex."""

    left_index: int
    right_index: int
    object_degree: int
    line_degree: tuple[int, int, int]
    koszul_summand: str

    @property
    def structural_degree(self) -> int:
        """Return the object-Hom plus Koszul degree."""

        return self.object_degree + KOSZUL_DEGREES[self.koszul_summand]

    @property
    def ambient_degree(self) -> tuple[int, int, int]:
        """Return the ambient line degree of this summand."""

        shift = KOSZUL_SHIFTS[self.koszul_summand]
        return tuple(
            value + offset
            for value, offset in zip(self.line_degree, shift, strict=True)
        )  # type: ignore[return-value]


@dataclass(frozen=True, slots=True, order=True)
class OuterCechBasis:
    """One regular Laurent monomial on one product-cover cell."""

    component: OuterCechComponent
    x_monomial: Monomial3
    u_monomial: Monomial3
    p_monomial: Monomial2
    cell: Cell

    def __post_init__(self) -> None:
        if (
            sum(self.x_monomial),
            sum(self.u_monomial),
            sum(self.p_monomial),
        ) != self.component.ambient_degree:
            raise ValueError("outer Čech monomial has an incompatible ambient degree")
        if any(
            any(index not in simplex for index, exponent in enumerate(monomial) if exponent < 0)
            for monomial, simplex in zip(
                (self.x_monomial, self.u_monomial, self.p_monomial),
                self.cell,
                strict=True,
            )
        ):
            raise ValueError("outer Čech monomial is not regular on its cover cell")

    @property
    def cech_degree(self) -> int:
        """Return the total product-cover Čech degree."""

        return sum(len(simplex) - 1 for simplex in self.cell)

    @property
    def total_degree(self) -> int:
        """Return the total outer-Hom degree."""

        return self.component.structural_degree + self.cech_degree


@dataclass(frozen=True, slots=True)
class SparseOuterCechCochain:
    """An exact normalized sparse cochain in the full outer Čech complex."""

    terms: tuple[tuple[OuterCechBasis, Eisenstein], ...]

    def __init__(
        self,
        terms: tuple[tuple[OuterCechBasis, Eisenstein], ...] = (),
    ) -> None:
        values: dict[OuterCechBasis, Eisenstein] = {}
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

    def __add__(self, other: SparseOuterCechCochain) -> SparseOuterCechCochain:
        return SparseOuterCechCochain(self.terms + other.terms)

    def scale(self, scalar: Eisenstein | int) -> SparseOuterCechCochain:
        """Scale every exact coefficient."""

        value = Eisenstein.coerce(scalar)
        return SparseOuterCechCochain(
            tuple((basis, coefficient * value) for basis, coefficient in self.terms)
        )

    def is_zero(self) -> bool:
        """Return whether the normalized cochain vanishes."""

        return not self.terms


@dataclass(frozen=True, slots=True)
class ReducedBasisEntry:
    """One reduced ambient-cohomology coordinate and its full Čech label."""

    index: int
    component: OuterCechComponent
    x_monomial: Monomial3
    u_monomial: Monomial3
    p_monomial: Monomial2


@dataclass(frozen=True, slots=True)
class TransferredOuterHom:
    """One exact outer Hom after full standard-cover Čech transfer."""

    reduced: SchoenSerreOuterHom
    differentials: tuple[tuple[int, SparseMap], ...]
    path_depths: tuple[tuple[int, int], ...]

    @property
    def squared_zero(self) -> bool:
        """Return whether consecutive transferred maps compose to zero."""

        maps = dict(self.differentials)
        return all(
            maps[degree + 1].compose(map_).is_zero()
            for degree, map_ in self.differentials
            if degree + 1 in maps
        )

    def cohomology_dimension(self, degree: int) -> int:
        """Return exact cohomology dimension in one total degree."""

        spaces = dict(self.reduced.total_spaces)
        maps = dict(self.differentials)
        outgoing = maps.get(degree)
        incoming = maps.get(degree - 1)
        return spaces[degree].dimension - (
            0 if outgoing is None else outgoing.rank()
        ) - (0 if incoming is None else incoming.rank())


def _line_difference(
    left: tuple[int, int, int],
    right: tuple[int, int, int],
) -> tuple[int, int, int]:
    """Return exact coordinate difference of two line classes."""

    return tuple(a - b for a, b in zip(left, right, strict=True))  # type: ignore[return-value]


@cache
def _components(
    left: SchoenSerreConstituent,
    right: SchoenSerreConstituent,
) -> tuple[OuterCechComponent, ...]:
    """Return every object-pair/Koszul component in deterministic order."""

    return tuple(
        OuterCechComponent(
            left_index,
            right_index,
            left_object.position - right_object.position,
            _line_difference(left_object.line_degree, right_object.line_degree),
            koszul,
        )
        for left_index, left_object in enumerate(left.objects)
        for right_index, right_object in enumerate(right.objects)
        for koszul in KOSZUL_ORDER
    )


@cache
def _reduced_basis(
    left: SchoenSerreConstituent,
    right: SchoenSerreConstituent,
    total_degree: int,
) -> tuple[ReducedBasisEntry, ...]:
    """Recover the compact reduced basis with its exact ambient labels."""

    reduced = schoen_serre_outer_hom(left, right)
    selected = tuple(
        component
        for component in reduced.components
        if component.total_degree == total_degree
    )
    entries: list[ReducedBasisEntry] = []
    index = 0
    for hom_component in selected:
        ambient_blocks = (
            hom_component.bundle.ambient_k0.space(hom_component.sheaf_degree),
            hom_component.bundle.ambient_k1_x.space(hom_component.sheaf_degree + 1),
            hom_component.bundle.ambient_k1_u.space(hom_component.sheaf_degree + 1),
            hom_component.bundle.ambient_k2.space(hom_component.sheaf_degree + 2),
        )
        for koszul, ambient in zip(KOSZUL_ORDER, ambient_blocks, strict=True):
            component = OuterCechComponent(
                hom_component.left_index,
                hom_component.right_index,
                hom_component.structural_degree,
                hom_component.bundle.degrees,
                koszul,
            )
            for label in ambient.labels:
                _x_h, _u_h, _p_h, x_monomial, u_monomial, p_monomial = label
                entries.append(
                    ReducedBasisEntry(
                        index,
                        component,
                        cast(Monomial3, x_monomial),
                        cast(Monomial3, u_monomial),
                        cast(Monomial2, p_monomial),
                    )
                )
                index += 1
    expected = dict(reduced.total_spaces)[total_degree].dimension
    if index != expected:
        raise ValueError("recovered reduced basis does not match its compact space")
    return tuple(entries)


@cache
def _product_cech_support(
    x_support: tuple[int, ...],
    u_support: tuple[int, ...],
    p_support: tuple[int, ...],
) -> ProductProjectiveMonomialCechComplex:
    """Return one cached product complex for a Laurent negative support."""

    return product_projective_monomial_cech_complex(
        (
            projective_monomial_cech_complex(
                ("x0", "x1", "x2"),
                tuple(-1 if index in x_support else 0 for index in range(3)),
                scalar_type=Eisenstein,
            ),
            projective_monomial_cech_complex(
                ("u0", "u1", "u2"),
                tuple(-1 if index in u_support else 0 for index in range(3)),
                scalar_type=Eisenstein,
            ),
            projective_monomial_cech_complex(
                ("p0", "p1"),
                tuple(-1 if index in p_support else 0 for index in range(2)),
                scalar_type=Eisenstein,
            ),
        )
    )


def _product_cech(
    basis: OuterCechBasis | ReducedBasisEntry,
) -> ProductProjectiveMonomialCechComplex:
    """Return the product complex selected by one Laurent monomial."""

    return _product_cech_support(
        tuple(index for index, value in enumerate(basis.x_monomial) if value < 0),
        tuple(index for index, value in enumerate(basis.u_monomial) if value < 0),
        tuple(index for index, value in enumerate(basis.p_monomial) if value < 0),
    )


def _include(entry: ReducedBasisEntry) -> SparseOuterCechCochain:
    """Include one ambient-cohomology basis class by its canonical cocycle."""

    cech = _product_cech(entry)
    representative = cech.canonical_representative()
    degree = entry.index * 0 + sum(
        factor.expected_cohomology_degree or 0 for factor in cech.factors
    )
    return SparseOuterCechCochain(
        tuple(
            (
                OuterCechBasis(
                    entry.component,
                    entry.x_monomial,
                    entry.u_monomial,
                    entry.p_monomial,
                    cast(Cell, cell),
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


def _homotopy(cochain: SparseOuterCechCochain) -> SparseOuterCechCochain:
    """Apply the signed tensor contraction for the raw total Čech differential."""

    groups: dict[
        tuple[OuterCechComponent, Monomial3, Monomial3, Monomial2],
        dict[Cell, Eisenstein],
    ] = defaultdict(dict)
    for basis, coefficient in cochain.terms:
        key = (
            basis.component,
            basis.x_monomial,
            basis.u_monomial,
            basis.p_monomial,
        )
        groups[key][basis.cell] = coefficient
    result: list[tuple[OuterCechBasis, Eisenstein]] = []
    for (component, x_monomial, u_monomial, p_monomial), values in groups.items():
        sample = OuterCechBasis(
            component,
            x_monomial,
            u_monomial,
            p_monomial,
            next(iter(values)),
        )
        cech = _product_cech(sample)
        degrees = {sum(len(simplex) - 1 for simplex in cell) for cell in values}
        if len(degrees) != 1:
            raise ValueError("one Laurent monomial occupies multiple Čech degrees")
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
                        OuterCechBasis(
                            component,
                            x_monomial,
                            u_monomial,
                            p_monomial,
                            cast(Cell, cell),
                        ),
                        cast(Eisenstein, coefficient) * sign,
                    )
                )
    return SparseOuterCechCochain(tuple(result))


def _cech_differential(cochain: SparseOuterCechCochain) -> SparseOuterCechCochain:
    """Apply the structurally signed product-cover Čech differential."""

    result: list[tuple[OuterCechBasis, Eisenstein]] = []
    for basis, coefficient in cochain.terms:
        preceding_degree = 0
        structural_sign = -1 if basis.component.structural_degree % 2 else 1
        for factor_index, (simplex, size) in enumerate(
            zip(basis.cell, (3, 3, 2), strict=True)
        ):
            for vertex in range(size):
                if vertex in simplex:
                    continue
                target_simplex = tuple(sorted((*simplex, vertex)))
                local_sign = -1 if target_simplex.index(vertex) % 2 else 1
                tensor_sign = -1 if preceding_degree % 2 else 1
                target_cell = list(basis.cell)
                target_cell[factor_index] = target_simplex
                result.append(
                    (
                        OuterCechBasis(
                            basis.component,
                            basis.x_monomial,
                            basis.u_monomial,
                            basis.p_monomial,
                            cast(Cell, tuple(target_cell)),
                        ),
                        coefficient * structural_sign * local_sign * tensor_sign,
                    )
                )
            preceding_degree += len(simplex) - 1
    return SparseOuterCechCochain(tuple(result))


def _full_differential(
    cochain: SparseOuterCechCochain,
    left: SchoenSerreConstituent,
    right: SchoenSerreConstituent,
) -> SparseOuterCechCochain:
    """Apply the exact raw Čech plus structural outer differential."""

    return _cech_differential(cochain) + _perturbation(cochain, left, right)


def _projection_index(
    basis: OuterCechBasis,
    target_indices: dict[
        tuple[OuterCechComponent, Monomial3, Monomial3, Monomial2],
        int,
    ],
) -> int | None:
    """Return the reduced coordinate selected by canonical Čech projection."""

    supports = tuple(
        tuple(index for index, value in enumerate(monomial) if value < 0)
        for monomial in (basis.x_monomial, basis.u_monomial, basis.p_monomial)
    )
    sizes = (3, 3, 2)
    if any(support and len(support) != size for support, size in zip(supports, sizes, strict=True)):
        return None
    pivot = cast(
        Cell,
        tuple(
            tuple(range(size)) if support else (0,)
            for support, size in zip(supports, sizes, strict=True)
        ),
    )
    if basis.cell != pivot:
        return None
    return target_indices.get(
        (
            basis.component,
            basis.x_monomial,
            basis.u_monomial,
            basis.p_monomial,
        )
    )


def _add_polynomial_images(
    result: list[tuple[OuterCechBasis, Eisenstein]],
    basis: OuterCechBasis,
    coefficient: Eisenstein,
    target: OuterCechComponent,
    polynomial: Polynomial,
    factor: str,
    p_exponents: Monomial2 = (0, 0),
) -> None:
    """Append exact global-polynomial images without changing the cover cell."""

    for exponents, scalar in polynomial.terms:
        x_monomial = basis.x_monomial
        u_monomial = basis.u_monomial
        if factor == "x":
            x_monomial = cast(
                Monomial3,
                tuple(a + b for a, b in zip(x_monomial, exponents, strict=True)),
            )
        elif factor == "u":
            u_monomial = cast(
                Monomial3,
                tuple(a + b for a, b in zip(u_monomial, exponents, strict=True)),
            )
        else:
            raise ValueError("outer factor polynomials require x or u")
        p_monomial = cast(
            Monomial2,
            tuple(a + b for a, b in zip(basis.p_monomial, p_exponents, strict=True)),
        )
        result.append(
            (
                OuterCechBasis(
                    target,
                    x_monomial,
                    u_monomial,
                    p_monomial,
                    basis.cell,
                ),
                coefficient * cast(Eisenstein, scalar),
            )
        )


def _add_equation_images(
    result: list[tuple[OuterCechBasis, Eisenstein]],
    basis: OuterCechBasis,
    coefficient: Eisenstein,
    target: OuterCechComponent,
    equation: int,
) -> None:
    """Append one published Schoen equation as separated exact factors."""

    terms = _equation_terms(equation)
    for polynomial, factor, p_exponents, prefactor in terms:
        _add_polynomial_images(
            result,
            basis,
            coefficient * prefactor,
            target,
            polynomial,
            factor,
            p_exponents,
        )


@cache
def _equation_terms(
    equation: int,
) -> tuple[tuple[Polynomial, str, Monomial2, Eisenstein], ...]:
    """Cache the separated terms of one verified Schoen equation."""

    cox = schoen_geometry().cover.cox
    if equation == 1:
        return (
            (cox.cubic_f, "x", (1, 0), Eisenstein(1)),
            (cox.cubic_g, "x", (0, 1), Eisenstein(1)),
        )
    if equation == 2:
        return (
            (cox.cubic_f, "u", (0, 1), Eisenstein(2)),
            (cox.cubic_g, "u", (1, 0), Eisenstein(1)),
        )
    raise ValueError("Schoen equations are numbered one and two")


def _add_extension_images(
    result: list[tuple[OuterCechBasis, Eisenstein]],
    basis: OuterCechBasis,
    coefficient: Eisenstein,
    target: OuterCechComponent,
    polynomial: Polynomial,
    factor: str,
    composition: str,
) -> None:
    """Cup with the canonical ``1/(mu nu)`` cocycle in declared composition order."""

    p_cell = basis.cell[2]
    required_vertex = 1 if composition == "left" else 0
    if p_cell != (required_vertex,):
        return
    target_cell = cast(Cell, (basis.cell[0], basis.cell[1], (0, 1)))
    p_monomial = cast(
        Monomial2,
        tuple(value - 1 for value in basis.p_monomial),
    )
    for exponents, scalar in polynomial.terms:
        x_monomial = basis.x_monomial
        u_monomial = basis.u_monomial
        if factor == "x":
            x_monomial = cast(
                Monomial3,
                tuple(a + b for a, b in zip(x_monomial, exponents, strict=True)),
            )
        elif factor == "u":
            u_monomial = cast(
                Monomial3,
                tuple(a + b for a, b in zip(u_monomial, exponents, strict=True)),
            )
        else:
            raise ValueError("extension polynomials require x or u")
        result.append(
            (
                OuterCechBasis(
                    target,
                    x_monomial,
                    u_monomial,
                    p_monomial,
                    target_cell,
                ),
                coefficient * cast(Eisenstein, scalar),
            )
        )


def _target_component(
    components: dict[tuple[int, int, str], OuterCechComponent],
    left_index: int,
    right_index: int,
    koszul_summand: str,
) -> OuterCechComponent:
    """Resolve one structurally adjacent full-Čech component."""

    return components[(left_index, right_index, koszul_summand)]


def _perturbation(
    cochain: SparseOuterCechCochain,
    left: SchoenSerreConstituent,
    right: SchoenSerreConstituent,
    component_lookup: dict[tuple[int, int, str], OuterCechComponent] | None = None,
) -> SparseOuterCechCochain:
    """Apply every non-Čech differential in the outer twisted complex."""

    components = component_lookup
    if components is None:
        components = {
            (component.left_index, component.right_index, component.koszul_summand): component
            for component in _components(left, right)
        }
    result: list[tuple[OuterCechBasis, Eisenstein]] = []
    for basis, coefficient in cochain.terms:
        component = basis.component
        object_sign = -1 if component.object_degree % 2 else 1
        koszul = component.koszul_summand
        if koszul == "k2":
            _add_equation_images(
                result,
                basis,
                coefficient * object_sign * -1,
                _target_component(
                    components,
                    component.left_index,
                    component.right_index,
                    "k1_x",
                ),
                2,
            )
            _add_equation_images(
                result,
                basis,
                coefficient * object_sign,
                _target_component(
                    components,
                    component.left_index,
                    component.right_index,
                    "k1_u",
                ),
                1,
            )
        elif koszul == "k1_x":
            _add_equation_images(
                result,
                basis,
                coefficient * object_sign,
                _target_component(
                    components,
                    component.left_index,
                    component.right_index,
                    "k0",
                ),
                1,
            )
        elif koszul == "k1_u":
            _add_equation_images(
                result,
                basis,
                coefficient * object_sign,
                _target_component(
                    components,
                    component.left_index,
                    component.right_index,
                    "k0",
                ),
                2,
            )
        koszul_sign = -1 if KOSZUL_DEGREES[koszul] % 2 else 1
        for arrow in left.arrows:
            if component.left_index != arrow.source:
                continue
            target = _target_component(
                components,
                arrow.target,
                component.right_index,
                koszul,
            )
            if arrow.cech_degree:
                _add_extension_images(
                    result,
                    basis,
                    coefficient * koszul_sign * object_sign,
                    target,
                    arrow.polynomial,
                    arrow.factor,
                    "left",
                )
            else:
                _add_polynomial_images(
                    result,
                    basis,
                    coefficient,
                    target,
                    arrow.polynomial,
                    arrow.factor,
                )
        for arrow in right.arrows:
            if component.right_index != arrow.target:
                continue
            target = _target_component(
                components,
                component.left_index,
                arrow.source,
                koszul,
            )
            right_sign = -object_sign
            if arrow.cech_degree:
                _add_extension_images(
                    result,
                    basis,
                    coefficient * right_sign * koszul_sign,
                    target,
                    arrow.polynomial,
                    arrow.factor,
                    "right",
                )
            else:
                _add_polynomial_images(
                    result,
                    basis,
                    coefficient * right_sign,
                    target,
                    arrow.polynomial,
                    arrow.factor,
                )
    return SparseOuterCechCochain(tuple(result))


def _transfer_map(
    left: SchoenSerreConstituent,
    right: SchoenSerreConstituent,
    degree: int,
) -> tuple[SparseMap, int]:
    """Compute one exact finite perturbation series between reduced spaces."""

    reduced = schoen_serre_outer_hom(left, right)
    spaces = dict(reduced.total_spaces)
    source_entries = _reduced_basis(left, right, degree)
    target_entries = _reduced_basis(left, right, degree + 1)
    target_indices = {
        (
            entry.component,
            entry.x_monomial,
            entry.u_monomial,
            entry.p_monomial,
        ): entry.index
        for entry in target_entries
    }
    component_lookup = {
        (component.left_index, component.right_index, component.koszul_summand): component
        for component in _components(left, right)
    }
    rows: list[dict[int, Eisenstein]] = [dict() for _ in target_entries]
    maximum_depth = 0
    for source in source_entries:
        current = _include(source)
        depth = 0
        while not current.is_zero():
            image = _perturbation(current, left, right, component_lookup)
            for basis, coefficient in image.terms:
                target_index = _projection_index(basis, target_indices)
                if target_index is not None:
                    rows[target_index][source.index] = rows[target_index].get(
                        source.index,
                        Eisenstein(0),
                    ) + coefficient
            current = _homotopy(image).scale(-1)
            depth += 1
            if depth > 12:
                raise ValueError("outer Čech perturbation series did not terminate")
        maximum_depth = max(maximum_depth, depth)
    return (
        SparseMap(spaces[degree], spaces[degree + 1], _freeze_rows(rows)),
        maximum_depth,
    )


@cache
def transferred_schoen_serre_outer_hom(
    left: SchoenSerreConstituent,
    right: SchoenSerreConstituent,
) -> TransferredOuterHom:
    """Transfer one declared outer Hom through the full standard Čech cover."""

    reduced = schoen_serre_outer_hom(left, right)
    spaces = dict(reduced.total_spaces)
    maps: list[tuple[int, SparseMap]] = []
    depths: list[tuple[int, int]] = []
    for degree, space in reduced.total_spaces:
        target = spaces.get(degree + 1)
        if target is None:
            maps.append(
                (
                    degree,
                    SparseMap.zero(
                        space,
                        type(space)("zero", (), Eisenstein),
                    ),
                )
            )
            depths.append((degree, 0))
            continue
        map_, depth = _transfer_map(left, right, degree)
        maps.append((degree, map_))
        depths.append((degree, depth))
    result = TransferredOuterHom(reduced, tuple(maps), tuple(depths))
    if not result.squared_zero:
        raise ValueError("transferred outer Čech differential is not square zero")
    return result


__all__ = ["TransferredOuterHom", "transferred_schoen_serre_outer_hom"]
