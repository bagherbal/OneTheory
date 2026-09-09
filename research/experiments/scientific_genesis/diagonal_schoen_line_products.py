"""Multiply exact line cochains on the diagonal Schoen cover.

Owns:
    The signed Alexander--Whitney and Koszul product for two explicitly
    normalized four-factor line-valued cochains.

Depends on:
    Exact Eisenstein coefficients, the product-cover cell cup product, and the
    diagonal complete-intersection degree convention.

Must not:
    Supply a missing bundle pairing, choose a trace normalization, infer a
    physical Yukawa value, or hide incompatible line degrees.

Phase 0:
    Research-only line-cochain multiplication for certified higher products.
"""

from __future__ import annotations

from typing import cast

from onetheory.math.numbers import Eisenstein

from .diagonal_schoen_lines import (
    LineDegree4,
    Monomial,
    _FullBasis,
    _FullCochain,
    _subtract_degrees,
)
from .mixed_schoen_matter_tensor import _cell_cup


def _add_monomials(left: Monomial, right: Monomial) -> Monomial:
    """Add exponent vectors in one common homogeneous coordinate factor."""

    return tuple(
        left_exponent + right_exponent
        for left_exponent, right_exponent in zip(left, right, strict=True)
    )


def diagonal_line_product(
    left: _FullCochain,
    right: _FullCochain,
    target_degrees: LineDegree4,
) -> _FullCochain:
    """Multiply two homogeneous line cochains with totalization signs."""

    right_by_start: dict[
        tuple[int, int, int, int],
        list[tuple[_FullBasis, Eisenstein]],
    ] = {}
    for basis, coefficient in right.terms:
        start = cast(
            tuple[int, int, int, int],
            tuple(simplex[0] for simplex in basis.cell),
        )
        right_by_start.setdefault(start, []).append((basis, coefficient))
    values: dict[_FullBasis, Eisenstein] = {}
    for left_basis, left_coefficient in left.terms:
        left_cech_degree = sum(
            len(simplex) - 1 for simplex in left_basis.cell
        )
        endpoint = cast(
            tuple[int, int, int, int],
            tuple(simplex[-1] for simplex in left_basis.cell),
        )
        for right_basis, right_coefficient in right_by_start.get(endpoint, ()):
            cell_product = _cell_cup(left_basis.cell, right_basis.cell)
            if cell_product is None:
                continue
            raw_subset = (*left_basis.subset, *right_basis.subset)
            if len(set(raw_subset)) != len(raw_subset):
                continue
            inversions = sum(
                left_equation > right_equation
                for left_equation in left_basis.subset
                for right_equation in right_basis.subset
            )
            subset = tuple(sorted(raw_subset))
            cell_sign, cell = cell_product
            crossing = left_cech_degree * len(right_basis.subset)
            sign = cell_sign * (-1 if (crossing + inversions) % 2 else 1)
            ambient_degrees = _subtract_degrees(target_degrees, subset)
            monomials = cast(
                tuple[Monomial, Monomial, Monomial, Monomial],
                tuple(
                    _add_monomials(left_monomial, right_monomial)
                    for left_monomial, right_monomial in zip(
                        left_basis.monomials,
                        right_basis.monomials,
                        strict=True,
                    )
                ),
            )
            if tuple(sum(item) for item in monomials) != ambient_degrees:
                raise ValueError("a line product changed its target degree")
            target = _FullBasis(subset, ambient_degrees, monomials, cell)
            updated = values.get(target, Eisenstein(0)) + (
                left_coefficient * right_coefficient * sign
            )
            if updated.is_zero():
                values.pop(target, None)
            else:
                values[target] = updated
    return _FullCochain(tuple(values.items()))


__all__ = ["diagonal_line_product"]
