"""Act on exact line-valued cochains over the diagonal Schoen cover.

Owns:
    Deck pullback with an explicit line-frame character, exact joint-character
    Reynolds projection, and determinant characters derived from resolutions.

Depends on:
    Published Schoen deck substitutions, certified constituent frames, and the
    exact four-factor Cech--Koszul line complex.

Must not:
    Guess a linearization, infer a character from a desired residue, select a
    carrier point, or identify a projected cochain with a physical coupling.

Phase 0:
    Research-only equivariance machinery for determinant-line calculations.
"""

from __future__ import annotations

from functools import cache

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.schoen_sparse_actions import (
    SchoenSparseDeckAction,
    schoen_sparse_deck_actions,
)

from .diagonal_schoen_lines import Cell4, Monomial, _FullBasis, _FullCochain
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_chain_actions import (
    _cell_image,
    _equation_units,
    _transformed_monomials,
)
from .mixed_schoen_outer_actions import _constituent_frame

Character = tuple[int, int]


@cache
def _cached_monomial_image(
    monomials: tuple[Monomial, Monomial, Monomial, Monomial],
    action: SchoenSparseDeckAction,
) -> tuple[Eisenstein, tuple[Monomial, Monomial, Monomial, Monomial]]:
    """Cache one coefficient-free Laurent-monomial deck image."""

    return _transformed_monomials(monomials, action)


@cache
def _cached_cell_image(
    cell: Cell4,
    action: SchoenSparseDeckAction,
) -> tuple[int, Cell4]:
    """Cache one oriented product-cover cell image."""

    return _cell_image(cell, action)


@cache
def _cached_subset_unit(
    subset: tuple[int, ...],
    action: SchoenSparseDeckAction,
) -> Eisenstein:
    """Cache the exact Koszul equation unit of one wedge subset."""

    units = _equation_units(action)
    result = Eisenstein(1)
    for equation in subset:
        result *= units[equation]
    return result


def _character_exponent(value: Eisenstein) -> int:
    """Recover one exact exponent in the cubic-root character group."""

    for exponent in range(3):
        if value == OMEGA**exponent:
            return exponent
    raise ValueError("a determinant frame is not a cubic-root character")


def _principal_block(matrix: Matrix, indices: tuple[int, ...]) -> Matrix:
    """Extract one exact square principal block from a homogeneous frame."""

    scalar_type = type(matrix[0][0])
    return Matrix(
        tuple(
            tuple(matrix[row][column] for column in indices)
            for row in indices
        ),
        scalar_type=scalar_type,
    )


def constituent_determinant_character(factor: int) -> Character:
    """Derive the determinant-line character of one constituent complex."""

    if factor not in {1, 2}:
        raise ValueError("constituent determinant factors are one and two")
    constituent = mixed_schoen_constituents()[factor - 1]
    positions = tuple(sorted({item.position for item in constituent.objects}))
    exponents = []
    for generator in ("P", "T"):
        frame = _constituent_frame(factor, generator)
        scalar = Eisenstein(1)
        for position in positions:
            indices = tuple(
                index
                for index, item in enumerate(constituent.objects)
                if item.position == position
            )
            for row in indices:
                if any(
                    not frame[row][column].is_zero()
                    for column, item in enumerate(constituent.objects)
                    if item.position != position
                ):
                    raise ValueError("a constituent frame mixes complex degrees")
            determinant = _principal_block(frame, indices).determinant()
            scalar *= determinant if position % 2 == 0 else Eisenstein(1) / determinant
        exponents.append(_character_exponent(scalar))
    return exponents[0], exponents[1]


def diagonal_line_full_action(
    cochain: _FullCochain,
    action: SchoenSparseDeckAction,
    frame_character: Character,
) -> _FullCochain:
    """Apply one deck pullback with a declared exact line-frame character."""

    generator_index = {"P": 0, "T": 1}.get(action.name)
    if generator_index is None:
        raise ValueError("line actions are defined for the P and T generators")
    frame_scalar = OMEGA ** frame_character[generator_index]
    terms = []
    for basis, coefficient in cochain.terms:
        monomial_scalar, monomials = _cached_monomial_image(
            basis.monomials,
            action,
        )
        cell_sign, cell = _cached_cell_image(basis.cell, action)
        geometric = (
            monomial_scalar
            * cell_sign
            * _cached_subset_unit(basis.subset, action)
        )
        target = _FullBasis(
            basis.subset,
            basis.ambient_degrees,
            monomials,
            cell,
        )
        terms.append((target, coefficient * geometric * frame_scalar))
    return _FullCochain(tuple(terms))


def line_has_character(
    cochain: _FullCochain,
    character: Character,
    frame_character: Character,
) -> bool:
    """Check both exact deck eigencharacter identities on one full cochain."""

    actions = {action.name: action for action in schoen_sparse_deck_actions()}
    return all(
        diagonal_line_full_action(cochain, actions[generator], frame_character)
        == cochain.scale(OMEGA ** character[index])
        for index, generator in enumerate(("P", "T"))
    )


def project_line_character(
    cochain: _FullCochain,
    character: Character,
    frame_character: Character,
) -> _FullCochain:
    """Apply the normalized order-nine projector for one declared character."""

    actions = {action.name: action for action in schoen_sparse_deck_actions()}
    terms: list[tuple[_FullBasis, Eisenstein]] = []
    p_power = cochain
    for p_exponent in range(3):
        term = p_power
        for t_exponent in range(3):
            weight = OMEGA ** (
                -character[0] * p_exponent
                - character[1] * t_exponent
            )
            terms.extend(
                (basis, coefficient * weight / 9)
                for basis, coefficient in term.terms
            )
            term = diagonal_line_full_action(
                term,
                actions["T"],
                frame_character,
            )
        p_power = diagonal_line_full_action(
            p_power,
            actions["P"],
            frame_character,
        )
    return _FullCochain(tuple(terms))


__all__ = [
    "Character",
    "constituent_determinant_character",
    "diagonal_line_full_action",
    "line_has_character",
    "project_line_character",
]
