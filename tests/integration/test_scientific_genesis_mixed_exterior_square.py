"""Check the graded exterior signs independently on exact small resolutions.

Owns:
    Odd-square multiplicities, polynomial differential squares, signed
    covector Leibniz identities, and incompatible-input rejection.

Depends on:
    The research exterior construction and synchronized full differential.

Must not:
    Treat these synthetic mathematical fixtures as carrier evidence or
    infer a Higgs primitive from a two-term basis count.

Phase 0:
    Exact regression tests for the exterior-square research calculation.
"""

from __future__ import annotations

from itertools import product

import pytest

from onetheory.math.numbers import OMEGA, Eisenstein
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.schoen_serre_outer import schoen_serre_outer_hom
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis import alternate_up_exterior_higgs_action as experiment
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
    MixedResolutionArrow,
)
from research.experiments.scientific_genesis.mixed_schoen_exterior_square import (
    mixed_exterior_square,
    reciprocal_covector_wedge,
    resolution_vector_wedge,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import (
    _MixedContraction,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    MixedSchoenUnit,
)


def _fixture() -> MixedSchoenUnit:
    """Use a split exact line relation, never physical input data."""

    return MixedSchoenUnit(
        "exact sign fixture", 2, (0, 0, 0),
        tuple(
            MixedConstituentObject(str(index), position, (0, 0, 0))
            for index, position in enumerate((0, 0, -1))
        ),
        tuple(
            MixedResolutionArrow(
                2, index, Polynomial.constant(value, 3, scalar_type=Eisenstein), 2
            )
            for index, value in enumerate((Eisenstein(1), OMEGA))
        ),
    )


def _section(context: _MixedContraction, index: int) -> SparseOuterCechCochain:
    """Use the actual constant section on all product-cover vertices."""

    return SparseOuterCechCochain(tuple(
        (
            OuterCechBasis(
                context.components[(0, index, "k0")],
                (0, 0, 0), (0, 0, 0), (0, 0), ((x,), (u,), (p,)),
            ),
            Eisenstein(1),
        )
        for x, u, p in product(range(3), range(3), range(2))
    ))


def test_odd_squares_are_not_divided_powers() -> None:
    """The ordinary graded exterior basis fixes both factors of two."""

    exterior = mixed_exterior_square(_fixture())
    assert exterior.pairs == ((0, 1), (0, 2), (1, 2), (2, 2))
    arrows = {(a.source, a.target): a.polynomial for a in exterior.resolution_arrows}
    assert arrows[(3, 1)] == Polynomial.constant(2, 3, scalar_type=Eisenstein)
    assert arrows[(3, 2)] == Polynomial.constant(2 * OMEGA, 3, scalar_type=Eisenstein)
    assert arrows[(1, 0)] == Polynomial.constant(OMEGA, 3, scalar_type=Eisenstein)
    assert arrows[(2, 0)] == Polynomial.constant(-1, 3, scalar_type=Eisenstein)
    context = _MixedContraction(MixedSchoenUnit(), exterior)
    for index in range(4):
        cochain = _section(context, index)
        assert context.differential(context.differential(cochain)).is_zero()


def test_covector_leibniz_checks_odd_diagonal_evaluation() -> None:
    """Independent differentiation detects a missing diagonal factor two."""

    source = _fixture()
    exterior = mixed_exterior_square(source)
    source_context = _MixedContraction(MixedSchoenUnit(), source)
    context = _MixedContraction(MixedSchoenUnit(), exterior)
    left, right = _section(source_context, 0), _section(source_context, 2)
    wedge = reciprocal_covector_wedge(left, right, exterior, context, 0, 1)
    differentiated_left = reciprocal_covector_wedge(
        source_context.differential(left), right, exterior, context, 1, 1
    )
    assert source_context.differential(right).is_zero()
    assert context.differential(wedge) == differentiated_left
    assert {coefficient for _, coefficient in differentiated_left.terms} == {Eisenstein(2)}


def test_external_koszul_crossing_satisfies_full_leibniz() -> None:
    """One Cech degree crossing one Koszul generator changes the sign."""

    source = _fixture()
    exterior = mixed_exterior_square(source)
    source_context = _MixedContraction(MixedSchoenUnit(), source)
    context = _MixedContraction(MixedSchoenUnit(), exterior)
    left = SparseOuterCechCochain(((
        OuterCechBasis(
            source_context.components[(0, 2, "k1_x")],
            (-1, -2, 0), (0, 0, 0), (-1, 0), ((0, 1), (0,), (0,)),
        ), Eisenstein(1),
    ),))
    right = SparseOuterCechCochain(((
        OuterCechBasis(
            source_context.components[(0, 0, "k1_u")],
            (0, 0, 0), (-1, -2, 0), (-1, 0), ((1,), (0, 1), (0,)),
        ), Eisenstein(1),
    ),))
    wedge = reciprocal_covector_wedge(left, right, exterior, context, 1, 0)
    assert len(wedge.terms) == 1
    assert wedge.terms[0][1] == Eisenstein(1)
    expected = reciprocal_covector_wedge(
        source_context.differential(left), right, exterior, context, 2, 0
    ) + reciprocal_covector_wedge(
        left, source_context.differential(right), exterior, context, 1, 1
    ).scale(-1)
    assert context.differential(wedge) == expected


def test_covectors_reject_wrong_basis_degree_and_reciprocal_line() -> None:
    """The product must not silently retarget a mismatched input."""

    source = _fixture()
    exterior = mixed_exterior_square(source)
    source_context = _MixedContraction(MixedSchoenUnit(), source)
    context = _MixedContraction(MixedSchoenUnit(), exterior)
    left, right = _section(source_context, 0), _section(source_context, 1)
    with pytest.raises(ValueError, match="incompatible grading"):
        reciprocal_covector_wedge(left, right, exterior, context, 1, 0)
    wrong_line = MixedSchoenUnit(
        "wrong line", 0, (1, 0, 0), (MixedConstituentObject("wrong", 0, (1, 0, 0)),)
    )
    with pytest.raises(ValueError, match="target lines are incompatible"):
        reciprocal_covector_wedge(
            left, right, exterior, _MixedContraction(wrong_line, exterior), 0, 0
        )
    with pytest.raises(ValueError, match="one declared line"):
        reciprocal_covector_wedge(left, right, exterior, source_context, 0, 0)


def test_even_repetition_vanishes_but_odd_repetition_does_not() -> None:
    """Exterior antisymmetry applies to internal degree, not object labels."""

    source = _fixture()
    exterior = mixed_exterior_square(source)
    source_context = _MixedContraction(MixedSchoenUnit(), source)
    context = _MixedContraction(MixedSchoenUnit(), exterior)
    even, odd = _section(source_context, 0), _section(source_context, 2)
    assert reciprocal_covector_wedge(even, even, exterior, context, 0, 0).is_zero()
    square = reciprocal_covector_wedge(odd, odd, exterior, context, 1, 1)
    assert len(square.terms) == 18
    assert {coefficient for _, coefficient in square.terms} == {Eisenstein(-2)}


def test_a_candidate_preimage_cannot_bypass_the_full_primitive_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An erroneous solver result must not fabricate a checked primitive."""

    source = _fixture()
    exterior = mixed_exterior_square(source)
    source_context = _MixedContraction(MixedSchoenUnit(), source)
    context = _MixedContraction(MixedSchoenUnit(), exterior)
    odd = _section(source_context, 2)
    square = reciprocal_covector_wedge(odd, odd, exterior, context, 1, 1)
    incoming = dict(schoen_serre_outer_hom(
        context.left_skeleton, context.right_skeleton
    ).total_differentials)[1]
    monkeypatch.setattr(experiment, "alternate_up_exterior_product", lambda _index: square)
    monkeypatch.setattr(experiment, "alternate_up_exterior_context", lambda: (exterior, context))
    monkeypatch.setattr(experiment, "_incoming_candidate", lambda: (incoming, 0))
    monkeypatch.setattr(experiment, "_sparse_preimage", lambda _map, _vector: {})
    with pytest.raises(ValueError, match="failed its full identity"):
        experiment.alternate_up_exterior_primitive.__wrapped__(0)


def test_forward_odd_square_has_no_divided_power_factor() -> None:
    """Forward multiplication and covector evaluation have distinct factors."""

    source = _fixture()
    exterior = mixed_exterior_square(source)
    source_context = _MixedContraction(source, MixedSchoenUnit())
    context = _MixedContraction(exterior, MixedSchoenUnit())
    odd = SparseOuterCechCochain(tuple(
        (
            OuterCechBasis(
                source_context.components[(2, 0, "k0")],
                (0, 0, 0), (0, 0, 0), (0, 0), ((x,), (u,), (p,)),
            ), Eisenstein(1),
        )
        for x, u, p in product(range(3), range(3), range(2))
    ))
    square = resolution_vector_wedge(odd, odd, exterior, context, -1, -1)
    assert len(square.terms) == 18
    assert {value for _, value in square.terms} == {Eisenstein(1)}
    differentiated = source_context.differential(odd)
    expected = resolution_vector_wedge(
        differentiated, odd, exterior, context, 0, -1
    ) + resolution_vector_wedge(
        odd, differentiated, exterior, context, -1, 0
    ).scale(-1)
    assert context.differential(square) == expected
    assert {value for _, value in expected.terms} == {Eisenstein(2), 2 * OMEGA}
    with pytest.raises(ValueError, match="incompatible basis or grading"):
        resolution_vector_wedge(odd, odd, exterior, context, 0, -1)
    with pytest.raises(ValueError, match="source must be the declared unit"):
        resolution_vector_wedge(odd, odd, exterior, source_context, -1, -1)
