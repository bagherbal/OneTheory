"""Compute Schoen line cohomology through the diagonal fiber-product model.

Owns:
    The exact three-equation Koszul complex on
    ``P2_x x P1_p x P2_u x P1_q`` and its line-bundle cohomology.

Depends on:
    Exact Eisenstein arithmetic, sparse linear maps, the published cubic
    pencils, and reusable projective-space cohomology bases.

Must not:
    Identify the two P1 factors before imposing the diagonal equation, attach
    bundle data, or infer physical Higgs representatives from line cohomology.

Phase 0:
    Research-only diagonal complete-intersection line calculation.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import combinations, product
from typing import cast

from onetheory.math.cech import (
    ProductProjectiveMonomialCechComplex,
    product_projective_monomial_cech_complex,
    projective_monomial_cech_complex,
)
from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.schoen_linebundles import (
    _factor_basis,
    _factor_matrix_for_terms,
)
from research.experiments.computable_carrier.schoen_sparse_outer import (
    SparseMap,
    _freeze_rows,
    _sparse_direct_sum_space,
)

Monomial = tuple[int, ...]
LineDegree4 = tuple[int, int, int, int]
AmbientLabel = tuple[
    tuple[int, int, int, int],
    tuple[Monomial, Monomial, Monomial, Monomial],
]
Cell4 = tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...], tuple[int, ...]]
EquationTerm = tuple[
    tuple[Monomial, Monomial, Monomial, Monomial],
    Eisenstein,
]

_FACTOR_KINDS = ("x", "p", "u", "p")
_FACTOR_COHOMOLOGY = ((0, 2), (0, 1), (0, 2), (0, 1))
_EQUATION_DEGREES: tuple[LineDegree4, ...] = (
    (3, 1, 0, 0),
    (0, 0, 3, 1),
    (0, 1, 0, 1),
)
_KOSZUL_SUBSETS = tuple(
    subset
    for size in range(4)
    for subset in combinations(range(3), size)
)
_TOTAL_DEGREES = tuple(range(-3, 7))
_DIFFERENTIAL_DEGREES = tuple(range(-3, 6))


@dataclass(frozen=True, slots=True, order=True)
class _FullBasis:
    """One Laurent monomial on a four-factor product-cover cell."""

    subset: tuple[int, ...]
    ambient_degrees: LineDegree4
    monomials: tuple[Monomial, Monomial, Monomial, Monomial]
    cell: Cell4


@dataclass(frozen=True, slots=True)
class _FullCochain:
    """One normalized sparse cochain in the full diagonal ambient cover."""

    terms: tuple[tuple[_FullBasis, Eisenstein], ...]

    def __init__(self, terms: tuple[tuple[_FullBasis, Eisenstein], ...] = ()) -> None:
        values: dict[_FullBasis, Eisenstein] = {}
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

    def scale(self, scalar: int | Eisenstein) -> _FullCochain:
        """Scale every coefficient exactly."""

        value = Eisenstein.coerce(scalar)
        return _FullCochain(
            tuple((basis, coefficient * value) for basis, coefficient in self.terms)
        )

    def is_zero(self) -> bool:
        """Return whether the normalized cochain has no support."""

        return not self.terms


@dataclass(frozen=True, slots=True)
class _ReducedEntry:
    """One compact ambient-cohomology coordinate with full Laurent labels."""

    index: int
    subset: tuple[int, ...]
    ambient_degrees: LineDegree4
    monomials: tuple[Monomial, Monomial, Monomial, Monomial]


@dataclass(frozen=True, slots=True)
class DiagonalAmbientSpace:
    """One exact Künneth cohomology space in the four-factor ambient variety."""

    degrees: LineDegree4
    cohomology_degree: int
    vector_space: VectorSpace
    labels: tuple[AmbientLabel, ...]


@cache
def _ambient_space(
    degrees: LineDegree4,
    cohomology_degree: int,
) -> DiagonalAmbientSpace:
    """Build one finite four-factor ambient Künneth basis."""

    labels: list[AmbientLabel] = []
    for factor_degrees in product(*_FACTOR_COHOMOLOGY):
        if sum(factor_degrees) != cohomology_degree:
            continue
        bases = tuple(
            _factor_basis(kind, degree, factor_degree)
            for kind, degree, factor_degree in zip(
                _FACTOR_KINDS,
                degrees,
                factor_degrees,
                strict=True,
            )
        )
        labels.extend(
            (
                cast(tuple[int, int, int, int], factor_degrees),
                cast(tuple[Monomial, Monomial, Monomial, Monomial], monomials),
            )
            for monomials in product(*bases)
        )
    vector_space = VectorSpace(
        f"Diagonal ambient O{degrees}:H^{cohomology_degree}",
        tuple(str(label) for label in labels),
        Eisenstein,
    )
    return DiagonalAmbientSpace(
        degrees,
        cohomology_degree,
        vector_space,
        tuple(labels),
    )


def _subtract_degrees(
    degrees: LineDegree4,
    subset: tuple[int, ...],
) -> LineDegree4:
    """Subtract the multidegrees of a Koszul wedge subset."""

    return cast(
        LineDegree4,
        tuple(
            value - sum(_EQUATION_DEGREES[index][factor] for index in subset)
            for factor, value in enumerate(degrees)
        ),
    )


@cache
def _factor_monomial_data(
    kind: str,
    source_degree: int,
    target_degree: int,
    cohomology_degree: int,
    exponent: Monomial,
) -> tuple[tuple[Monomial, ...], tuple[tuple[Eisenstein, ...], ...], dict[Monomial, int]]:
    """Return one exact factor multiplication and its source coordinates."""

    polynomial = Polynomial.monomial(exponent, scalar_type=Eisenstein)
    target_basis, rows = _factor_matrix_for_terms(
        kind,
        source_degree,
        target_degree,
        cohomology_degree,
        polynomial,
    )
    source_basis = _factor_basis(kind, source_degree, cohomology_degree)
    return target_basis, rows, {
        monomial: index for index, monomial in enumerate(source_basis)
    }


@cache
def _ambient_equation_map(
    source: DiagonalAmbientSpace,
    target: DiagonalAmbientSpace,
    terms: tuple[EquationTerm, ...],
) -> SparseMap:
    """Multiply ambient Künneth classes by one multihomogeneous equation."""

    if source.cohomology_degree != target.cohomology_degree:
        raise ValueError("ambient equation maps preserve cohomological degree")
    target_indices = {label: index for index, label in enumerate(target.labels)}
    rows: list[dict[int, Eisenstein]] = [dict() for _ in target.labels]
    for source_index, (factor_degrees, source_monomials) in enumerate(source.labels):
        for exponents, scalar in terms:
            factor_data = tuple(
                _factor_monomial_data(
                    kind,
                    source_degree,
                    target_degree,
                    factor_degree,
                    exponent,
                )
                for kind, source_degree, target_degree, factor_degree, exponent in zip(
                    _FACTOR_KINDS,
                    source.degrees,
                    target.degrees,
                    factor_degrees,
                    exponents,
                    strict=True,
                )
            )
            source_positions = tuple(
                data[2][monomial]
                for data, monomial in zip(factor_data, source_monomials, strict=True)
            )
            for target_positions in product(
                *(range(len(data[0])) for data in factor_data)
            ):
                coefficient = scalar
                for data, target_position, source_position in zip(
                    factor_data,
                    target_positions,
                    source_positions,
                    strict=True,
                ):
                    coefficient *= data[1][target_position][source_position]
                if coefficient.is_zero():
                    continue
                target_monomials = cast(
                    tuple[Monomial, Monomial, Monomial, Monomial],
                    tuple(
                        data[0][target_position]
                        for data, target_position in zip(
                            factor_data,
                            target_positions,
                            strict=True,
                        )
                    ),
                )
                target_index = target_indices.get((factor_degrees, target_monomials))
                if target_index is None:
                    raise ValueError("diagonal equation escaped its ambient basis")
                rows[target_index][source_index] = rows[target_index].get(
                    source_index,
                    Eisenstein(0),
                ) + coefficient
    return SparseMap(source.vector_space, target.vector_space, _freeze_rows(rows))


@cache
def _equation_terms(equation: int) -> tuple[EquationTerm, ...]:
    """Expand one of the two pencils or the diagonal equation exactly."""

    zero3 = (0, 0, 0)
    zero2 = (0, 0)
    cox = schoen_geometry().cover.cox
    if equation == 0:
        return tuple(
            ((x_exp, p_exp, zero3, zero2), cast(Eisenstein, coefficient))
            for polynomial, p_exp in (
                (cox.cubic_f, (1, 0)),
                (cox.cubic_g, (0, 1)),
            )
            for x_exp, coefficient in polynomial.terms
        )
    if equation == 1:
        return tuple(
            ((zero3, zero2, u_exp, q_exp), prefactor * cast(Eisenstein, coefficient))
            for polynomial, q_exp, prefactor in (
                (cox.cubic_f, (0, 1), Eisenstein(2)),
                (cox.cubic_g, (1, 0), Eisenstein(1)),
            )
            for u_exp, coefficient in polynomial.terms
        )
    if equation == 2:
        return (
            ((zero3, (1, 0), zero3, (0, 1)), Eisenstein(1)),
            ((zero3, (0, 1), zero3, (1, 0)), Eisenstein(-1)),
        )
    raise ValueError("diagonal Schoen equations are indexed zero through two")


@cache
def _product_cech_support(
    supports: tuple[tuple[int, ...], ...],
) -> ProductProjectiveMonomialCechComplex:
    """Return the exact product Čech contraction for four negative supports."""

    names = (
        ("x0", "x1", "x2"),
        ("p0", "p1"),
        ("u0", "u1", "u2"),
        ("q0", "q1"),
    )
    return product_projective_monomial_cech_complex(
        tuple(
            projective_monomial_cech_complex(
                factor_names,
                tuple(-1 if index in support else 0 for index in range(len(factor_names))),
                scalar_type=Eisenstein,
            )
            for factor_names, support in zip(names, supports, strict=True)
        )
    )


def _product_cech(
    monomials: tuple[Monomial, Monomial, Monomial, Monomial],
) -> ProductProjectiveMonomialCechComplex:
    """Select a product contraction from one Laurent monomial tuple."""

    return _product_cech_support(
        tuple(
            tuple(index for index, value in enumerate(monomial) if value < 0)
            for monomial in monomials
        )
    )


@cache
def _reduced_entries(
    degrees: LineDegree4,
    total_degree: int,
) -> tuple[_ReducedEntry, ...]:
    """Recover the compact E1 basis in deterministic Koszul order."""

    entries = []
    index = 0
    for subset in _KOSZUL_SUBSETS:
        ambient_degrees = _subtract_degrees(degrees, subset)
        ambient = _ambient_space(ambient_degrees, total_degree + len(subset))
        for _factor_degrees, monomials in ambient.labels:
            entries.append(_ReducedEntry(index, subset, ambient_degrees, monomials))
            index += 1
    if index != _line_space(degrees, total_degree).dimension:
        raise ValueError("diagonal reduced basis does not match its compact space")
    return tuple(entries)


def _include(entry: _ReducedEntry) -> _FullCochain:
    """Include one ambient cohomology class by its canonical Čech cocycle."""

    cech = _product_cech(entry.monomials)
    representative = cech.canonical_representative()
    degree = sum(factor.expected_cohomology_degree or 0 for factor in cech.factors)
    return _FullCochain(
        tuple(
            (
                _FullBasis(
                    entry.subset,
                    entry.ambient_degrees,
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


def _homotopy(cochain: _FullCochain) -> _FullCochain:
    """Apply the signed product-cover contraction at fixed Koszul component."""

    groups: dict[
        tuple[
            tuple[int, ...],
            LineDegree4,
            tuple[Monomial, Monomial, Monomial, Monomial],
        ],
        dict[Cell4, Eisenstein],
    ] = defaultdict(dict)
    for basis, coefficient in cochain.terms:
        groups[(basis.subset, basis.ambient_degrees, basis.monomials)][basis.cell] = (
            coefficient
        )
    result = []
    for (subset, ambient_degrees, monomials), values in groups.items():
        cech = _product_cech(monomials)
        degrees = {
            sum(len(simplex) - 1 for simplex in cell)
            for cell in values
        }
        if len(degrees) != 1:
            raise ValueError("one diagonal Laurent monomial spans multiple Čech degrees")
        degree = next(iter(degrees))
        contracted = cech.contracting_homotopy(cech.cochain(degree, values))
        structural_sign = -1 if len(subset) % 2 else 1
        for cell, coefficient in zip(
            cech.cells_at(degree - 1),
            contracted.coordinates,
            strict=True,
        ):
            if not coefficient.is_zero():
                result.append(
                    (
                        _FullBasis(
                            subset,
                            ambient_degrees,
                            monomials,
                            cast(Cell4, cell),
                        ),
                        cast(Eisenstein, coefficient) * structural_sign,
                    )
                )
    return _FullCochain(tuple(result))


def _perturbation(cochain: _FullCochain) -> _FullCochain:
    """Apply the three exact Koszul equation maps on full Čech cochains."""

    result = []
    for basis, coefficient in cochain.terms:
        for position, equation in enumerate(basis.subset):
            target_subset = tuple(
                index for index in basis.subset if index != equation
            )
            target_degrees = cast(
                LineDegree4,
                tuple(
                    value + shift
                    for value, shift in zip(
                        basis.ambient_degrees,
                        _EQUATION_DEGREES[equation],
                        strict=True,
                    )
                ),
            )
            sign = -1 if position % 2 else 1
            for exponents, scalar in _equation_terms(equation):
                target_monomials = cast(
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
                        _FullBasis(
                            target_subset,
                            target_degrees,
                            target_monomials,
                            basis.cell,
                        ),
                        coefficient * scalar * sign,
                    )
                )
    return _FullCochain(tuple(result))


def _projection_index(
    basis: _FullBasis,
    target_indices: dict[
        tuple[tuple[int, ...], tuple[Monomial, Monomial, Monomial, Monomial]],
        int,
    ],
) -> int | None:
    """Project one canonical Laurent cocycle to its reduced coordinate."""

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
    return target_indices.get((basis.subset, basis.monomials))


@cache
def _transferred_differential(
    degrees: LineDegree4,
    total_degree: int,
) -> SparseMap:
    """Transfer the full diagonal Koszul perturbation to ambient cohomology."""

    source_entries = _reduced_entries(degrees, total_degree)
    target_entries = _reduced_entries(degrees, total_degree + 1)
    source_space = _line_space(degrees, total_degree)
    target_space = _line_space(degrees, total_degree + 1)
    target_indices = {
        (entry.subset, entry.monomials): entry.index for entry in target_entries
    }
    rows: list[dict[int, Eisenstein]] = [dict() for _ in target_entries]
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
            if depth > 12:
                raise ValueError("diagonal Koszul perturbation did not terminate")
    return SparseMap(source_space, target_space, _freeze_rows(rows))


def _line_space(
    degrees: LineDegree4,
    total_degree: int,
) -> VectorSpace:
    """Assemble every Koszul wedge summand in one total degree."""

    return _sparse_direct_sum_space(
        tuple(
            _ambient_space(
                _subtract_degrees(degrees, subset),
                total_degree + len(subset),
            ).vector_space
            for subset in _KOSZUL_SUBSETS
        )
    )


def _koszul_differential(
    degrees: LineDegree4,
    total_degree: int,
) -> SparseMap:
    """Build one signed three-equation Koszul differential."""

    source_spaces = tuple(
        _ambient_space(
            _subtract_degrees(degrees, subset),
            total_degree + len(subset),
        )
        for subset in _KOSZUL_SUBSETS
    )
    target_spaces = tuple(
        _ambient_space(
            _subtract_degrees(degrees, subset),
            total_degree + 1 + len(subset),
        )
        for subset in _KOSZUL_SUBSETS
    )
    blocks = []
    for target_subset, target_space in zip(
        _KOSZUL_SUBSETS,
        target_spaces,
        strict=True,
    ):
        row = []
        for source_subset, source_space in zip(
            _KOSZUL_SUBSETS,
            source_spaces,
            strict=True,
        ):
            removed = tuple(index for index in source_subset if index not in target_subset)
            if (
                len(removed) == 1
                and tuple(index for index in source_subset if index != removed[0])
                == target_subset
            ):
                equation = removed[0]
                sign = -1 if source_subset.index(equation) % 2 else 1
                row.append(
                    _ambient_equation_map(
                        source_space,
                        target_space,
                        _equation_terms(equation),
                    ).scale(sign)
                )
            else:
                row.append(
                    SparseMap.zero(
                        source_space.vector_space,
                        target_space.vector_space,
                    )
                )
        blocks.append(tuple(row))
    return SparseMap.block(tuple(blocks))


@dataclass(frozen=True, slots=True)
class DiagonalSchoenLineBundle:
    """One immutable exact line complex in the diagonal Schoen presentation."""

    schoen_degrees: tuple[int, int, int]
    ambient_degrees: LineDegree4
    spaces: tuple[tuple[int, VectorSpace], ...]
    differentials: tuple[tuple[int, SparseMap], ...]

    def space(self, degree: int) -> VectorSpace:
        """Return one total cochain space or its typed zero space."""

        return dict(self.spaces).get(
            degree,
            VectorSpace(f"Diagonal O{self.schoen_degrees}[{degree}]", (), Eisenstein),
        )

    def differential(self, degree: int) -> SparseMap:
        """Return one exact differential or its typed edge zero map."""

        return dict(self.differentials).get(
            degree,
            SparseMap.zero(self.space(degree), self.space(degree + 1)),
        )

    @property
    def squared_zero(self) -> bool:
        """Return the exact three-equation Koszul identity."""

        return all(
            self.differential(degree + 1).compose(map_).is_zero()
            for degree, map_ in self.differentials
        )

    def cohomology_dimension(self, degree: int) -> int:
        """Return one exact cohomology dimension."""

        return (
            self.space(degree).dimension
            - self.differential(degree - 1).rank()
            - self.differential(degree).rank()
        )

    @property
    def geometric_dimensions(self) -> tuple[int, int, int, int]:
        """Return cohomology in geometric degrees zero through three."""

        return cast(
            tuple[int, int, int, int],
            tuple(self.cohomology_dimension(degree) for degree in range(4)),
        )


@cache
def diagonal_schoen_line_bundle(
    x_degree: int,
    u_degree: int,
    p_degree: int,
) -> DiagonalSchoenLineBundle:
    """Construct ``O_X(x,u,p)`` using two pencils and the exact diagonal."""

    schoen_degrees = (x_degree, u_degree, p_degree)
    ambient_degrees = (x_degree, p_degree, u_degree, 0)
    return DiagonalSchoenLineBundle(
        schoen_degrees,
        ambient_degrees,
        tuple(
            (degree, _line_space(ambient_degrees, degree))
            for degree in _TOTAL_DEGREES
        ),
        tuple(
            (degree, _transferred_differential(ambient_degrees, degree))
            for degree in _DIFFERENTIAL_DEGREES
        ),
    )


__all__ = ["DiagonalSchoenLineBundle", "diagonal_schoen_line_bundle"]
