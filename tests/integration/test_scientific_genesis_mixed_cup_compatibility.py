"""Compare compatibility reuse with independent exact Hom composition.

Owns:
    Coefficient cancellation across reused cover data and independent
    Cech/Koszul sign checks for the sparse common-cover product.

Depends on:
    Existing matrix-frame-checked Yoneda composition and exact cochains.

Must not:
    Interpret polynomial sign fixtures as physical carrier quantities.

Phase 0:
    Exact regression tests for research product memory reduction.
"""

from __future__ import annotations

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
)
from research.experiments.scientific_genesis.mixed_outer_yoneda import compose_outer_cochains
from research.experiments.scientific_genesis.mixed_schoen_common_dga import mixed_outer_cup
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import _MixedContraction
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import MixedSchoenUnit


def _line(name: str, degree: tuple[int, int, int]) -> MixedSchoenUnit:
    return MixedSchoenUnit(name, 0, degree, (MixedConstituentObject(name, 0, degree),))


def test_compatibility_reuse_preserves_exact_coefficient_cancellation() -> None:
    """Two distinct monomial products can cancel on one cached cover cell."""

    left_line, middle, right_line = (
        _line("left", (2, 0, 0)), MixedSchoenUnit(), _line("right", (-2, 0, 0)),
    )
    left_context = _MixedContraction(left_line, middle)
    right_context = _MixedContraction(middle, right_line)
    target = _MixedContraction(left_line, right_line)
    cell = ((0,), (0,), (0,))
    left = SparseOuterCechCochain(tuple(
        (OuterCechBasis(left_context.components[(0, 0, "k0")], x, (0, 0, 0), (0, 0), cell), value)
        for x, value in (((2, 0, 0), Eisenstein(1)), ((1, 1, 0), Eisenstein(-1)))
    ))
    right = SparseOuterCechCochain(tuple(
        (
            OuterCechBasis(right_context.components[(0, 0, "k0")], x, (0, 0, 0), (0, 0), cell),
            Eisenstein(1),
        )
        for x in ((0, 2, 0), (1, 1, 0))
    ))
    actual = mixed_outer_cup(left, right)
    independent = compose_outer_cochains(
        left, right, target.components, left_middle=middle, right_middle=middle,
    )
    assert actual == independent
    assert {basis.x_monomial: value for basis, value in actual.terms} == {
        (3, 1, 0): Eisenstein(1), (1, 3, 0): Eisenstein(-1),
    }
    assert mixed_outer_cup(left, right + right.scale(-1)).is_zero()


def test_compatibility_reuse_preserves_external_and_koszul_crossings() -> None:
    """The independent composer retains signs and rejects repeated generators."""

    left_line, middle, right_line = _line("left", (3, 3, 2)), MixedSchoenUnit(), MixedSchoenUnit()
    left_context = _MixedContraction(left_line, middle)
    right_context = _MixedContraction(middle, right_line)
    target = _MixedContraction(left_line, right_line)
    left = SparseOuterCechCochain(((
        OuterCechBasis(
            left_context.components[(0, 0, "k1_x")],
            (0, 0, 0), (3, 0, 0), (1, 0), ((0, 1), (0,), (0,)),
        ), Eisenstein(1),
    ),))
    right = SparseOuterCechCochain(((
        OuterCechBasis(
            right_context.components[(0, 0, "k1_u")],
            (0, 0, 0), (-1, -1, -1), (-1, 0), ((1,), (0, 1, 2), (0,)),
        ), Eisenstein(1),
    ),))
    actual = mixed_outer_cup(left, right)
    independent = compose_outer_cochains(
        left, right, target.components, left_middle=middle, right_middle=middle,
    )
    assert actual == independent
    assert len(actual.terms) == 1
    assert actual.terms[0][1] == Eisenstein(-1)
    assert mixed_outer_cup(left, left).is_zero()
