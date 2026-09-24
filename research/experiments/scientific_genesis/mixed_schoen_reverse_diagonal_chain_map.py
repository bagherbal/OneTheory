"""Compare second-constituent common cochains with the independent diagonal.

Owns:
    The local first-pencil comparison on both first-fiber charts and its
    overlap Koszul homotopy for reverse matter corrections.

Depends on:
    Exact Schoen cubics, common-Schoen outer cochains, and the lawful
    independent-fiber tensor presentation.

Must not:
    Identify the two fiber coordinates globally, reuse the asymmetric
    first-constituent comparison, or claim a reverse Yukawa coefficient.

Phase 0:
    Research-only exact local chain-map candidate pending full verification.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import cast

from onetheory.math.numbers import Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)

from .diagonal_schoen_lines import Cell4, Monomial, _subtract_degrees
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_chain_diagonal import (
    ChainDiagonalBasis,
    ChainDiagonalCochain,
    _factor_degrees,
    _object_indices,
    _target_component,
)
from .mixed_schoen_matter_tensor import (
    IndependentMatterBasis,
    IndependentMatterCochain,
)

ZERO3: Monomial = (0, 0, 0)
ZERO2: Monomial = (0, 0)


@dataclass(frozen=True, slots=True)
class ReverseDiagonalPiece:
    """One regular first-pencil local map or overlap-homotopy term."""

    target_subset: tuple[int, ...]
    x_shift: Monomial
    p_shift: Monomial
    q_shift: Monomial
    p_cell: tuple[int, ...]
    coefficient: Eisenstein

    @property
    def regular_on_cell(self) -> bool:
        """Require every first-fiber denominator to be covered locally."""

        return all(
            exponent >= 0 or index in self.p_cell
            for index, exponent in enumerate(self.p_shift)
        )


def _piece(
    subset: tuple[int, ...],
    *,
    x: Monomial = ZERO3,
    p: Monomial = ZERO2,
    q: Monomial = ZERO2,
    cell: tuple[int, ...],
    coefficient: object = 1,
) -> ReverseDiagonalPiece:
    """Construct one exactly typed reverse local comparison piece."""

    return ReverseDiagonalPiece(
        subset, x, p, q, cell, Eisenstein.coerce(coefficient)
    )


@cache
def reverse_diagonal_comparison_pieces(
    source_summand: str,
) -> tuple[ReverseDiagonalPiece, ...]:
    """Express the common first pencil through F_p and the diagonal."""

    if source_summand in {"k0", "k1_u"}:
        subset = () if source_summand == "k0" else (1,)
        return tuple(_piece(subset, cell=(vertex,)) for vertex in range(2))
    if source_summand not in {"k1_x", "k2"}:
        raise ValueError("unknown common-Schoen Koszul summand")

    top = source_summand == "k2"
    pencil_subset = (0, 1) if top else (0,)
    diagonal_subset = (1, 2) if top else (2,)
    overlap_subset = (0, 1, 2) if top else (0, 2)
    wedge_sign = -1 if top else 1
    cox = schoen_geometry().cover.cox
    return (
        _piece(pencil_subset, p=(-1, 0), q=(1, 0), cell=(0,)),
        *(
            _piece(
                diagonal_subset,
                x=cast(Monomial, exponents),
                p=(-1, 0),
                cell=(0,),
                coefficient=cast(Eisenstein, coefficient) * wedge_sign,
            )
            for exponents, coefficient in cox.cubic_g.terms
        ),
        _piece(pencil_subset, p=(0, -1), q=(0, 1), cell=(1,)),
        *(
            _piece(
                diagonal_subset,
                x=cast(Monomial, exponents),
                p=(0, -1),
                cell=(1,),
                coefficient=-cast(Eisenstein, coefficient) * wedge_sign,
            )
            for exponents, coefficient in cox.cubic_f.terms
        ),
        _piece(
            overlap_subset,
            p=(-1, -1),
            cell=(0, 1),
            coefficient=wedge_sign,
        ),
    )


def _add_monomials(left: Monomial, right: Monomial) -> Monomial:
    """Add exact Laurent exponents in one named coordinate block."""

    return tuple(a + b for a, b in zip(left, right, strict=True))


def reverse_diagonal_compare_common_matter(
    cochain: SparseOuterCechCochain,
) -> IndependentMatterCochain:
    """Lift one homogeneous V2 correction with explicit first-fiber charts."""

    degrees = {basis.total_degree for basis, _coefficient in cochain.terms}
    if len(degrees) != 1:
        raise ValueError("the reverse diagonal comparison requires homogeneity")
    second = mixed_schoen_constituents()[1]
    terms: list[tuple[IndependentMatterBasis, Eisenstein]] = []
    for basis, coefficient in cochain.terms:
        component = basis.component
        if component.right_index != 0:
            raise ValueError("reverse matter corrections must start at the unit")
        x_degree, u_degree, q_degree = (
            len(simplex) - 1 for simplex in basis.cell
        )
        for piece in reverse_diagonal_comparison_pieces(
            component.koszul_summand
        ):
            if not piece.regular_on_cell:
                raise ValueError("a reverse local coefficient has an uncovered pole")
            monomials = (
                _add_monomials(basis.x_monomial, piece.x_shift),
                piece.p_shift,
                basis.u_monomial,
                _add_monomials(basis.p_monomial, piece.q_shift),
            )
            cell: Cell4 = (
                basis.cell[0],
                piece.p_cell,
                basis.cell[1],
                basis.cell[2],
            )
            expected_degrees = _subtract_degrees(
                _factor_degrees(second, component.left_index, 3),
                piece.target_subset,
            )
            if tuple(sum(monomial) for monomial in monomials) != expected_degrees:
                raise ValueError("the reverse comparison changed ambient degrees")
            p_degree = len(piece.p_cell) - 1
            crossing = (u_degree + q_degree + component.object_degree) * p_degree
            crossing += component.object_degree * x_degree
            if component.koszul_summand in {"k1_x", "k2"}:
                crossing += component.object_degree
            if component.koszul_summand in {"k1_u", "k2"}:
                crossing += x_degree
            if 2 in piece.target_subset and len(piece.p_cell) == 1:
                crossing += component.object_degree + x_degree + u_degree + q_degree
            terms.append(
                (
                    IndependentMatterBasis(
                        2,
                        component.left_index,
                        piece.target_subset,
                        component.object_degree,
                        monomials,
                        cell,
                    ),
                    coefficient
                    * piece.coefficient
                    * (-1 if crossing % 2 else 1),
                )
            )
    result = IndependentMatterCochain(2, next(iter(degrees)), tuple(terms))
    if any(
        basis.structural_degree + basis.cech_degree != result.total_degree
        for basis, _coefficient in result.terms
    ):
        raise ValueError("the reverse comparison changed total degree")
    return result


def embed_compared_second_factor(
    cochain: IndependentMatterCochain,
) -> ChainDiagonalCochain:
    """Place a compared second-factor cochain beside the first unit object."""

    if cochain.factor != 2:
        raise ValueError("the reverse embedding requires the second factor")
    objects = _object_indices()
    result = ChainDiagonalCochain(
        tuple(
            (
                ChainDiagonalBasis(
                    _target_component(
                        objects[(0, basis.object_index)], basis.subset
                    ),
                    basis.monomials,
                    basis.cell,
                ),
                coefficient,
            )
            for basis, coefficient in cochain.terms
        )
    )
    if any(
        basis.total_degree != cochain.total_degree
        for basis, _coefficient in result.terms
    ):
        raise ValueError("the reverse embedding changed total degree")
    return result


__all__ = [
    "ReverseDiagonalPiece",
    "embed_compared_second_factor",
    "reverse_diagonal_compare_common_matter",
    "reverse_diagonal_comparison_pieces",
]
