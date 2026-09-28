"""Verify the quotient's inherited linearization before Higgs identification.

Owns:
    Global minor-row equivariance, unchanged native Higgs character,
    and covariance of both full quotient connecting arrows.

Depends on:
    Exact native bundle frames and induced ordinary graded exterior frames.

Must not:
    Pick a flat character to fit a spectrum or declare normalized Yukawas.

Phase 0:
    Research regressions for a necessary physical Higgs comparison.
"""

from __future__ import annotations

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import _reduced_basis
from research.experiments.computable_carrier.schoen_sparse_actions import schoen_sparse_deck_actions
from research.experiments.scientific_genesis.alternate_up_exterior_higgs_action import (
    alternate_up_exterior_context,
)
from research.experiments.scientific_genesis.alternate_up_higgs_quotient_cone import (
    alternate_higgs_quotient_connecting_arrow,
    alternate_higgs_quotient_covector,
    alternate_higgs_quotient_models,
)
from research.experiments.scientific_genesis.alternate_up_quotient_equivariance import (
    global_first_quotient_cochain,
    quotient_deck_frames,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
    mixed_schoen_constituents,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import (
    _full_action,
    _MixedContraction,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    MixedSchoenUnit,
    mixed_schoen_unit,
)


def test_global_quotient_induces_its_unique_line_character() -> None:
    """The 54-term polynomial row forces the phase, not an observational fit."""

    q = global_first_quotient_cochain()
    assert len(q.terms) == 54
    assert all(basis.total_degree == 0 for basis, _ in q.terms)
    assert quotient_deck_frames("P")[0] == OMEGA
    assert quotient_deck_frames("T")[0] == Eisenstein(1)
    with pytest.raises(ValueError, match="deck generator is unavailable"):
        quotient_deck_frames("unavailable")


def test_actual_quotient_higgs_retains_its_native_character() -> None:
    """Check all coefficients after deriving the K frame from B1 and F."""

    _, quotient = alternate_higgs_quotient_models()
    h = alternate_higgs_quotient_covector()
    unit = mixed_schoen_unit()
    for action in schoen_sparse_deck_actions():
        _, frame, _ = quotient_deck_frames(action.name)
        image = _full_action(h, unit, quotient, action, (
            Matrix.identity(1, scalar_type=Eisenstein), frame,
        ))
        assert image == h.scale(OMEGA**(2 if action.name == "P" else 0))


def test_actual_quotient_connecting_arrows_are_strictly_deck_fixed() -> None:
    """Check actual full cochains, not only a determinant character table."""

    _, quotient = alternate_higgs_quotient_models()
    exterior, _ = alternate_up_exterior_context()
    for action in schoen_sparse_deck_actions():
        _, quotient_frame, exterior_frame = quotient_deck_frames(action.name)
        for index in range(2):
            arrow = alternate_higgs_quotient_connecting_arrow(index)
            assert _full_action(
                arrow, quotient, exterior, action, (quotient_frame, exterior_frame),
            ) == arrow


def test_actual_determinant_endpoints_have_no_ambient_cohomology() -> None:
    """Derive the lines from objects; all spectral-sequence terms vanish."""

    constituents = (
        mixed_schoen_constituents()[0], alternate_higgs_quotient_models()[0],
    )
    degrees = []
    for constituent in constituents:
        signs = [(-1 if item.position % 2 else 1) for item in constituent.objects]
        assert sum(signs) == 2
        degrees.append(tuple(sum(
            sign * item.line_degree[coordinate]
            for sign, item in zip(signs, constituent.objects, strict=True)
        ) for coordinate in range(3)))
    assert degrees == [(-2, 2, 0), (2, -2, 0)]
    unit = mixed_schoen_unit()
    for degree in degrees:
        line = MixedSchoenUnit(
            "actual determinant", 0, degree,
            (MixedConstituentObject("actual determinant", 0, degree),),
        )
        context = _MixedContraction(line, unit)
        assert all(
            not _reduced_basis(context.left_skeleton, context.right_skeleton, total_degree)
            for total_degree in range(-2, 6)
        )
    # The same machinery detects the nonacyclic unit; this is not a
    # fixture that always assigns zero cohomology to a declared line.
    context = _MixedContraction(unit, unit)
    assert [len(_reduced_basis(
        context.left_skeleton, context.right_skeleton, total_degree,
    )) for total_degree in (0, 3)] == [1, 1]
