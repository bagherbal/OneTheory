"""Canonicalize both oriented diagonal fiber-line twists exactly.

Owns:
    The Cech-local maps from lines carrying degree (0,1,0,-1) or (0,-1,0,1)
    to their canonical diagonal restrictions with explicit Koszul homotopies.

Depends on:
    The exact four-factor diagonal line complex, Alexander--Whitney products,
    and the explicit diagonal equation p0*q1-p1*q0.

Must not:
    Identify the two projective-line factors globally, alter a determinant
    normalization silently, pair bundle constituents, or infer a Yukawa value.

Phase 0:
    Research-only chain isomorphism for a certified diagonal line twist.
"""

from __future__ import annotations

from collections import defaultdict
from typing import cast

from onetheory.math.numbers import Eisenstein

from .diagonal_schoen_lines import (
    Cell4,
    LineDegree4,
    Monomial,
    _FullBasis,
    _FullCochain,
    _subtract_degrees,
)
from .mixed_schoen_matter_tensor import _cell_cup

P_MINUS_Q_TWIST: LineDegree4 = (0, 1, 0, -1)
Q_MINUS_P_TWIST: LineDegree4 = (0, -1, 0, 1)
_ZERO3: Monomial = (0, 0, 0)


def _add_monomials(left: Monomial, right: Monomial) -> Monomial:
    """Add two exponent vectors in the same homogeneous coordinate basis."""

    return tuple(a + b for a, b in zip(left, right, strict=True))


def _subtract_line_degrees(
    left: LineDegree4,
    right: LineDegree4,
) -> LineDegree4:
    """Subtract two four-factor line degrees componentwise."""

    return cast(
        LineDegree4,
        tuple(a - b for a, b in zip(left, right, strict=True)),
    )


def _validate_source(
    cochain: _FullCochain,
    source_degrees: LineDegree4,
) -> None:
    """Reject terms outside the declared source line normalization."""

    for basis, _coefficient in cochain.terms:
        if basis.ambient_degrees != _subtract_degrees(
            source_degrees,
            basis.subset,
        ):
            raise ValueError("a diagonal twist term occupies the wrong source line")


def diagonal_twist_local_identity_exact() -> bool:
    """Verify q0/p0-q1/p1=-delta/(p0*p1) as Laurent monomials."""

    values: defaultdict[
        tuple[Monomial, Monomial],
        Eisenstein,
    ] = defaultdict(lambda: Eisenstein(0))
    values[((-1, 0), (1, 0))] += Eisenstein(1)
    values[((0, -1), (0, 1))] -= Eisenstein(1)

    expected: defaultdict[
        tuple[Monomial, Monomial],
        Eisenstein,
    ] = defaultdict(lambda: Eisenstein(0))
    expected[((0, -1), (0, 1))] -= Eisenstein(1)
    expected[((-1, 0), (1, 0))] += Eisenstein(1)
    return dict(values) == dict(expected)


def canonicalize_p_minus_q_twist(
    cochain: _FullCochain,
    source_degrees: LineDegree4,
    target_degrees: LineDegree4,
) -> _FullCochain:
    """Map one explicit p-minus-q twist to the canonical diagonal line."""

    if _subtract_line_degrees(source_degrees, target_degrees) != P_MINUS_Q_TWIST:
        raise ValueError("the declared lines do not differ by the p-minus-q twist")
    if not diagonal_twist_local_identity_exact():
        raise ValueError("the local diagonal line identity failed")
    _validate_source(cochain, source_degrees)
    terms: list[tuple[_FullBasis, Eisenstein]] = []
    for basis, coefficient in cochain.terms:
        pivot = basis.cell[1][0]
        ratio_p: Monomial = (-1, 0) if pivot == 0 else (0, -1)
        ratio_q: Monomial = (1, 0) if pivot == 0 else (0, 1)
        ratio_monomials = (_ZERO3, ratio_p, _ZERO3, ratio_q)
        terms.append(
            (
                _FullBasis(
                    basis.subset,
                    _subtract_degrees(target_degrees, basis.subset),
                    cast(
                        tuple[Monomial, Monomial, Monomial, Monomial],
                        tuple(
                            _add_monomials(source, ratio)
                            for source, ratio in zip(
                                basis.monomials,
                                ratio_monomials,
                                strict=True,
                            )
                        ),
                    ),
                    basis.cell,
                ),
                coefficient,
            )
        )
        if 2 in basis.subset or basis.cell[1] != (1,):
            continue
        map_cell: Cell4 = (
            (basis.cell[0][0],),
            (0, 1),
            (basis.cell[2][0],),
            (basis.cell[3][0],),
        )
        product = _cell_cup(map_cell, basis.cell)
        if product is None:
            raise ValueError("the diagonal overlap homotopy has no Cech cup")
        cell_sign, target_cell = product
        target_subset = tuple(sorted((*basis.subset, 2)))
        terms.append(
            (
                _FullBasis(
                    target_subset,
                    _subtract_degrees(target_degrees, target_subset),
                    (
                        basis.monomials[0],
                        _add_monomials(basis.monomials[1], (-1, -1)),
                        basis.monomials[2],
                        basis.monomials[3],
                    ),
                    target_cell,
                ),
                coefficient * -cell_sign,
            )
        )
    return _FullCochain(tuple(terms))


def canonicalize_q_minus_p_twist(
    cochain: _FullCochain,
    source_degrees: LineDegree4,
    target_degrees: LineDegree4,
) -> _FullCochain:
    """Map the inverse diagonal fiber twist with its exact overlap homotopy."""

    if _subtract_line_degrees(source_degrees, target_degrees) != Q_MINUS_P_TWIST:
        raise ValueError("the declared lines do not differ by the q-minus-p twist")
    _validate_source(cochain, source_degrees)
    terms: list[tuple[_FullBasis, Eisenstein]] = []
    for basis, coefficient in cochain.terms:
        pivot = basis.cell[3][0]
        ratio_p: Monomial = (1, 0) if pivot == 0 else (0, 1)
        ratio_q: Monomial = (-1, 0) if pivot == 0 else (0, -1)
        ratio_monomials = (_ZERO3, ratio_p, _ZERO3, ratio_q)
        terms.append(
            (
                _FullBasis(
                    basis.subset,
                    _subtract_degrees(target_degrees, basis.subset),
                    cast(
                        tuple[Monomial, Monomial, Monomial, Monomial],
                        tuple(
                            _add_monomials(source, ratio)
                            for source, ratio in zip(
                                basis.monomials,
                                ratio_monomials,
                                strict=True,
                            )
                        ),
                    ),
                    basis.cell,
                ),
                coefficient,
            )
        )
        if 2 in basis.subset or basis.cell[3] != (1,):
            continue
        map_cell: Cell4 = (
            (basis.cell[0][0],),
            (basis.cell[1][0],),
            (basis.cell[2][0],),
            (0, 1),
        )
        product = _cell_cup(map_cell, basis.cell)
        if product is None:
            raise ValueError("the inverse diagonal overlap homotopy has no cup")
        cell_sign, target_cell = product
        target_subset = tuple(sorted((*basis.subset, 2)))
        terms.append(
            (
                _FullBasis(
                    target_subset,
                    _subtract_degrees(target_degrees, target_subset),
                    (
                        basis.monomials[0],
                        basis.monomials[1],
                        basis.monomials[2],
                        _add_monomials(basis.monomials[3], (-1, -1)),
                    ),
                    target_cell,
                ),
                coefficient * cell_sign,
            )
        )
    return _FullCochain(tuple(terms))


__all__ = [
    "P_MINUS_Q_TWIST",
    "Q_MINUS_P_TWIST",
    "canonicalize_p_minus_q_twist",
    "canonicalize_q_minus_p_twist",
    "diagonal_twist_local_identity_exact",
]
