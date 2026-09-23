"""Lift common-Schoen matter cochains through the diagonal presentation.

Owns:
    The two-chart Koszul comparison, overlap chain homotopy, and exact sparse
    application to common-Schoen matter cochains with an explicit target
    constituent label on the independent-fiber cover.

Depends on:
    The certified local pencil identities, lawful mixed outer cochain labels,
    and the independent-fiber chain-diagonal basis.

Must not:
    Replace local Laurent coefficients by global polynomials, omit the overlap
    homotopy, identify fibers by substitution, or infer a Yukawa coefficient.

Phase 0:
    Research-only chain map for the first lawful deformation contribution.
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

from .diagonal_schoen_lines import Cell4, Monomial
from .mixed_schoen_chain_diagonal import (
    ChainDiagonalBasis,
    ChainDiagonalCochain,
    _object_indices,
    _target_component,
)
from .mixed_schoen_diagonal_comparison import mixed_schoen_diagonal_comparison
from .mixed_schoen_matter_tensor import (
    IndependentMatterBasis,
    IndependentMatterCochain,
)

ZERO3: Monomial = (0, 0, 0)
ZERO2: Monomial = (0, 0)


@dataclass(frozen=True, slots=True)
class DiagonalComparisonPiece:
    """One Laurent-monomial component of the local Koszul chain map."""

    target_subset: tuple[int, ...]
    p_shift: Monomial
    u_shift: Monomial
    q_shift: Monomial
    q_cell: tuple[int, ...]
    coefficient: Eisenstein

    @property
    def total_shift_degree(self) -> tuple[int, int, int]:
        """Return the multiplier multidegree in u, p, and q."""

        return (sum(self.u_shift), sum(self.p_shift), sum(self.q_shift))

    @property
    def regular_on_cell(self) -> bool:
        """Return whether every q denominator is invertible on its Cech cell."""

        return all(
            exponent >= 0 or index in self.q_cell
            for index, exponent in enumerate(self.q_shift)
        )


def _piece(
    subset: tuple[int, ...],
    *,
    p: Monomial = ZERO2,
    u: Monomial = ZERO3,
    q: Monomial = ZERO2,
    cell: tuple[int, ...],
    coefficient: object = 1,
) -> DiagonalComparisonPiece:
    """Construct one exactly typed local comparison piece."""

    return DiagonalComparisonPiece(
        subset,
        p,
        u,
        q,
        cell,
        Eisenstein.coerce(coefficient),
    )


@cache
def diagonal_comparison_pieces(
    source_summand: str,
) -> tuple[DiagonalComparisonPiece, ...]:
    """Return the local map and overlap-homotopy pieces for one source wedge."""

    if source_summand in {"k0", "k1_x"}:
        subset = () if source_summand == "k0" else (0,)
        return tuple(_piece(subset, cell=(vertex,)) for vertex in range(2))
    if source_summand not in {"k1_u", "k2"}:
        raise ValueError("unknown common-Schoen Koszul summand")

    has_first = source_summand == "k2"
    u_subset = (0, 1) if has_first else (1,)
    diagonal_subset = (0, 2) if has_first else (2,)
    overlap_subset = (0, 1, 2) if has_first else (1, 2)
    cox = schoen_geometry().cover.cox
    pieces = [
        _piece(u_subset, p=(1, 0), q=(-1, 0), cell=(0,)),
        *(
            _piece(
                diagonal_subset,
                u=cast(Monomial, exponents),
                q=(-1, 0),
                cell=(0,),
                coefficient=cast(Eisenstein, coefficient) * -2,
            )
            for exponents, coefficient in cox.cubic_f.terms
        ),
        _piece(u_subset, p=(0, 1), q=(0, -1), cell=(1,)),
        *(
            _piece(
                diagonal_subset,
                u=cast(Monomial, exponents),
                q=(0, -1),
                cell=(1,),
                coefficient=cast(Eisenstein, coefficient),
            )
            for exponents, coefficient in cox.cubic_g.terms
        ),
        _piece(
            overlap_subset,
            q=(-1, -1),
            cell=(0, 1),
            coefficient=-1,
        ),
    ]
    return tuple(pieces)


def _add_monomials(left: Monomial, right: Monomial) -> Monomial:
    """Add two equally based Laurent exponent vectors."""

    return tuple(a + b for a, b in zip(left, right, strict=True))


def diagonal_compare_common_matter(
    cochain: SparseOuterCechCochain,
    target_factor: int = 1,
) -> IndependentMatterCochain:
    """Compare a homogeneous common cochain in either constituent target."""

    if target_factor not in (1, 2):
        raise ValueError("the diagonal target factor must be one or two")

    degrees = {basis.total_degree for basis, _coefficient in cochain.terms}
    if len(degrees) != 1:
        raise ValueError("the common-Schoen comparison requires a homogeneous cochain")
    terms: list[tuple[IndependentMatterBasis, Eisenstein]] = []
    for basis, coefficient in cochain.terms:
        component = basis.component
        if component.right_index != 0:
            raise ValueError("matter corrections must be maps from the unit object")
        x_degree, u_degree, p_degree = (
            len(simplex) - 1 for simplex in basis.cell
        )
        contains_second_pencil = component.koszul_summand in {"k1_u", "k2"}
        for piece in diagonal_comparison_pieces(component.koszul_summand):
            if not piece.regular_on_cell:
                raise ValueError("a local comparison coefficient has an uncovered pole")
            diagonal_only = 2 in piece.target_subset and 1 not in piece.target_subset
            totalization_exponent = (
                u_degree * p_degree
                + contains_second_pencil * (x_degree + p_degree)
                + diagonal_only * u_degree
            )
            totalization_sign = -1 if totalization_exponent % 2 else 1
            monomials = (
                basis.x_monomial,
                _add_monomials(basis.p_monomial, piece.p_shift),
                _add_monomials(basis.u_monomial, piece.u_shift),
                piece.q_shift,
            )
            cell: Cell4 = (
                basis.cell[0],
                basis.cell[2],
                basis.cell[1],
                piece.q_cell,
            )
            terms.append(
                (
                    IndependentMatterBasis(
                        target_factor,
                        component.left_index,
                        piece.target_subset,
                        component.object_degree,
                        monomials,
                        cell,
                    ),
                    coefficient * piece.coefficient * totalization_sign,
                )
            )
    result = IndependentMatterCochain(target_factor, next(iter(degrees)), tuple(terms))
    if any(
        basis.structural_degree + basis.cech_degree != result.total_degree
        for basis, _coefficient in result.terms
    ):
        raise ValueError("the local diagonal comparison changed total degree")
    return result


def embed_compared_first_factor(
    cochain: IndependentMatterCochain,
) -> ChainDiagonalCochain:
    """Embed one compared first-factor cochain beside the exact unit object."""

    if cochain.factor != 1:
        raise ValueError("only first-factor comparison cochains can be embedded")
    objects = _object_indices()
    result = ChainDiagonalCochain(
        tuple(
            (
                ChainDiagonalBasis(
                    _target_component(
                        objects[(basis.object_index, 0)],
                        basis.subset,
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
        raise ValueError("the compared first-factor embedding changed total degree")
    return result


@dataclass(frozen=True, slots=True)
class DiagonalChainMapCertificate:
    """Finite exact identities proving the local Koszul map and homotopy signs."""

    local_chain_maps_exact: bool
    generator_overlap_homotopy_exact: bool
    top_wedge_overlap_homotopy_exact: bool
    all_pieces_regular: bool

    @property
    def exact(self) -> bool:
        """Return whether every local-map and overlap gate passes."""

        return (
            self.local_chain_maps_exact
            and self.generator_overlap_homotopy_exact
            and self.top_wedge_overlap_homotopy_exact
            and self.all_pieces_regular
        )


@cache
def diagonal_chain_map_certificate() -> DiagonalChainMapCertificate:
    """Recompute the chain-map and overlap-homotopy equations exactly."""

    local = mixed_schoen_diagonal_comparison()
    generator_overlap = next(
        piece
        for piece in diagonal_comparison_pieces("k1_u")
        if piece.q_cell == (0, 1)
    )
    top_overlap = next(
        piece
        for piece in diagonal_comparison_pieces("k2")
        if piece.q_cell == (0, 1)
    )
    all_pieces = tuple(
        piece
        for summand in ("k0", "k1_x", "k1_u", "k2")
        for piece in diagonal_comparison_pieces(summand)
    )
    return DiagonalChainMapCertificate(
        local.q0_cross_identity and local.q1_cross_identity,
        local.overlap_syzygy_identity
        and generator_overlap.target_subset == (1, 2)
        and generator_overlap.coefficient == Eisenstein(-1),
        local.overlap_syzygy_identity
        and top_overlap.target_subset == (0, 1, 2)
        and top_overlap.coefficient == Eisenstein(-1),
        all(piece.regular_on_cell for piece in all_pieces),
    )


__all__ = [
    "DiagonalChainMapCertificate",
    "DiagonalComparisonPiece",
    "diagonal_chain_map_certificate",
    "diagonal_compare_common_matter",
    "diagonal_comparison_pieces",
    "embed_compared_first_factor",
]
