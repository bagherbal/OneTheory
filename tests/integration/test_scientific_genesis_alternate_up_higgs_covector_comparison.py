"""Check the dual cone sign by independent slot composition.

Owns:
    Exact even/odd and Cech/Koszul sign fixtures, rejection of incompatible
    quotient data, and full closure of the actual alternate matter wedges.

Depends on:
    The generated graded exterior basis, ordinary Hom composition, and
    the frozen four strict up-sector matter representatives.

Must not:
    Infer a physical Higgs or scalar residue from the local sign fixtures.

Phase 0:
    Exact research regressions for the next full ordered scalar.
"""

from __future__ import annotations

from itertools import product

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis import (
    alternate_constituent_up_matter_representatives as up_matter,
)
from research.experiments.scientific_genesis.alternate_up_exterior_higgs_action import (
    alternate_up_exterior_context,
)
from research.experiments.scientific_genesis.alternate_up_first_order_scalar import (
    OrderedFirstOrderScalar,
    alternate_null_matter,
)
from research.experiments.scientific_genesis.alternate_up_higgs_covector_comparison import (
    QUOTIENT_LINE,
    alternate_up_higgs_covector_action,
    quotient_outer_exterior_action,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
)
from research.experiments.scientific_genesis.mixed_schoen_common_dga import mixed_outer_cup
from research.experiments.scientific_genesis.mixed_schoen_exterior_square import (
    mixed_exterior_square,
    reciprocal_covector_wedge,
    resolution_vector_wedge,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import _MixedContraction
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import MixedSchoenUnit


def _covector(
    context: _MixedContraction, index: int, koszul: str, cell_x: tuple[int, ...],
) -> SparseOuterCechCochain:
    component = context.components[(0, index, koszul)]
    x, u, p = component.ambient_degree
    x_monomial = tuple(x if i == cell_x[0] else 0 for i in range(3))
    return SparseOuterCechCochain(((
        OuterCechBasis(
            component, x_monomial, (u, 0, 0), (p, 0), (cell_x, (0,), (0,)),
        ), Eisenstein(1),
    ),))


@pytest.mark.parametrize(
    "h_index,h_koszul,h_cell,q_index,q_koszul,q_cell",
    (
        (2, "k0", (0,), 2, "k0", (0,)),
        (0, "k0", (0, 1), 2, "k0", (1,)),
        (2, "k0", (0,), 0, "k0", (0, 1)),
        (2, "k1_u", (0, 1), 0, "k0", (1, 2)),
        (2, "k0", (0,), 2, "k1_u", (0, 1)),
    ),
)
def test_two_slot_action_is_negative_ordered_wedge(
    h_index: int, h_koszul: str, h_cell: tuple[int, ...],
    q_index: int, q_koszul: str, q_cell: tuple[int, ...],
) -> None:
    """Compose actual homogeneous maps rather than copying the wedge sign."""

    source = MixedSchoenUnit(
        "split graded sign fixture", 0, (0, 0, 0),
        tuple(MixedConstituentObject(str(i), p, (0, 0, 0)) for i, p in enumerate((0, 0, -1))),
    )
    exterior = mixed_exterior_square(source)
    line = MixedSchoenUnit(
        "quotient fixture", 0, QUOTIENT_LINE,
        (MixedConstituentObject("B", 0, QUOTIENT_LINE),),
    )
    inverse_line = MixedSchoenUnit(
        "inverse quotient fixture", 0, (1, -1, -1),
        (MixedConstituentObject("B inverse", 0, (1, -1, -1)),),
    )
    h = _covector(_MixedContraction(inverse_line, source), h_index, h_koszul, h_cell)
    q = _covector(_MixedContraction(line, source), q_index, q_koszul, q_cell)
    action = mixed_outer_cup(h, quotient_outer_exterior_action(q, exterior))
    wedge = reciprocal_covector_wedge(
        h, q, exterior, _MixedContraction(MixedSchoenUnit(), exterior), 1, 1,
    )
    assert not action.is_zero()
    assert action == wedge.scale(-1)
    if h_index == q_index and h_koszul == q_koszul:
        assert action.terms[0][1] == Eisenstein(2)
    with pytest.raises(ValueError, match="actual F-to-B covector"):
        quotient_outer_exterior_action(h, exterior)


def test_actual_up_matter_wedges_and_null_wedge_are_full_cycles() -> None:
    """Check the full constituent perturbation on the scientific inputs."""

    classes = up_matter.alternate_constituent_up_matter_representatives().classes
    sectors = [
        [item.full_cochain for item in classes if item.character == character]
        for character in ((0, 0), (1, 0))
    ]
    exterior, _ = alternate_up_exterior_context()
    context = _MixedContraction(exterior, MixedSchoenUnit())
    counts = []
    for i, j in product(range(2), repeat=2):
        wedge = resolution_vector_wedge(sectors[0][i], sectors[1][j], exterior, context, 1, 1)
        counts.append(len(wedge.terms))
        assert not wedge.is_zero()
        assert context.differential(wedge).is_zero()
    assert counts == [2169, 2322, 2349, 2211]
    null_wedge = resolution_vector_wedge(*alternate_null_matter(), exterior, context, 1, 1)
    assert len(null_wedge.terms) == 2997
    assert context.differential(null_wedge).is_zero()


def test_nonclosed_screen_cannot_record_a_residue() -> None:
    """Reject a residue even when a caller supplies plausible scalar metadata."""

    unit = MixedSchoenUnit()
    context = _MixedContraction(unit, unit)
    component = context.components[(0, 0, "k0")]
    witness = SparseOuterCechCochain(((
        OuterCechBasis(component, (0, 0, 0), (0, 0, 0), (0, 0), ((0,), (0,), (0,))),
        Eisenstein(1),
    ),))
    zero = SparseOuterCechCochain()
    with pytest.raises(ValueError, match="nonclosed ordered scalar must not carry a residue"):
        OrderedFirstOrderScalar(
            0, zero, zero, zero, witness, zero, witness, witness, Eisenstein(1), 1,
        )
    with pytest.raises(ValueError, match="declared three terms"):
        OrderedFirstOrderScalar(0, zero, zero, zero, zero, zero, witness, witness, None, None)


def test_actual_signed_actions_use_both_full_outer_coefficients() -> None:
    """Reconstruct the two-slot compositions rather than accepting flags."""

    expected = (191628, 169983)
    exterior, context = alternate_up_exterior_context()
    assert len(exterior.pairs) == 31
    for index, count in enumerate(expected):
        action = alternate_up_higgs_covector_action(index)
        assert len(action.terms) == count
        assert all(basis.total_degree == 2 for basis, _ in action.terms)
        assert context.differential(action).is_zero()
    with pytest.raises(ValueError, match="parameter index is unavailable"):
        alternate_up_higgs_covector_action(2)
