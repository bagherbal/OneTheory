"""Test the corrected rank-one product on mathematical even-object fixtures.

Owns:
    Full signed Leibniz identities for the Cech--Koszul differential and
    explicit refusal of unsupported odd-object inputs.

Depends on:
    The independent scalar cup homotopy and the even tensor correction.

Must not:
    Use mathematical fixtures as carrier evidence or certify outer cones.

Phase 0:
    Mathematical regression tests for one scoped tensor-comparison repair.
"""

from dataclasses import replace
from itertools import product

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
    MixedExtensionTerm,
)
from research.experiments.scientific_genesis.mixed_schoen_exterior_square import (
    even_rank_one_vector_wedge,
    mixed_exterior_square,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import _MixedContraction
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import MixedSchoenUnit


def _fixture() -> MixedSchoenUnit:
    """Use one exact nilpotent gauge in a split mathematical line complex."""

    unit = MixedSchoenUnit()
    context = _MixedContraction(unit, unit)
    section = SparseOuterCechCochain(tuple((OuterCechBasis(
        context.components[(0, 0, "k0")], (0, 0, 0), (0, 0, 0), (0, 0),
        ((0,), (u,), (p,)),
    ), Eisenstein(1)) for u, p in product(range(3), range(2))))
    alpha = context.differential(section)
    assert context.differential(alpha).is_zero()
    return MixedSchoenUnit(
        "mathematical nilpotent gauge fixture", 0, (0, 0, 0),
        tuple(MixedConstituentObject(name, 0, (0, 0, 0)) for name in ("A", "B", "C")),
        extension_terms=tuple(MixedExtensionTerm(
            1, 0, 0, None, basis.x_monomial, basis.u_monomial, basis.p_monomial,
            basis.cell, -value,
        ) for basis, value in alpha.terms),
    )


@pytest.mark.parametrize("koszul", tuple(product(("k0", "k1_x", "k1_u", "k2"), repeat=2)))
@pytest.mark.parametrize("left_cell", (((0,), (0,), (0,)), ((0, 1), (0,), (0,))))
def test_even_tensor_homotopy_satisfies_full_signed_leibniz(
    koszul: tuple[str, str], left_cell: tuple,
) -> None:
    """Check noncycles too, so closure alone cannot masquerade as a chain map."""

    source = _fixture()
    unit = MixedSchoenUnit()
    source_context = _MixedContraction(source, unit)
    exterior = mixed_exterior_square(source)
    context = _MixedContraction(exterior, unit)

    def cochain(index: int, subset: str, cell: tuple) -> SparseOuterCechCochain:
        component = source_context.components[(index, 0, subset)]
        x, u, p = component.ambient_degree
        return SparseOuterCechCochain(((OuterCechBasis(
            component, (x, 0, 0), (u, 0, 0), (p, 0), cell,
        ), Eisenstein(2, 1)),))

    a = cochain(2, koszul[0], left_cell)
    b = cochain(1, koszul[1], ((0, 1), (0,), (0,)))
    p = a.terms[0][0].total_degree
    q = b.terms[0][0].total_degree

    def wedge(u: SparseOuterCechCochain, v: SparseOuterCechCochain, i: int, j: int):
        return even_rank_one_vector_wedge(u, v, source, exterior, context, i, j)

    lhs = context.differential(wedge(a, b, p, q))
    rhs = wedge(source_context.differential(a), b, p + 1, q) + wedge(
        a, source_context.differential(b), p, q + 1,
    ).scale(-1 if p % 2 else 1)
    assert lhs == rhs


def test_even_tensor_homotopy_refuses_odd_object_inputs() -> None:
    """The missing syzygy comparison is not an automatic zero correction."""

    source = _fixture()
    source = replace(source, objects=source.objects + (MixedConstituentObject(
        "odd syzygy fixture", -1, (0, 0, 0),
    ),))
    exterior = mixed_exterior_square(source)
    source_context = _MixedContraction(source, MixedSchoenUnit())
    context = _MixedContraction(exterior, MixedSchoenUnit())
    odd = SparseOuterCechCochain(((OuterCechBasis(
        source_context.components[(3, 0, "k0")],
        (0, 0, 0), (0, 0, 0), (0, 0), ((0,), (0,), (0,)),
    ), Eisenstein(1)),))
    with pytest.raises(ValueError, match="cannot omit odd-object comparison"):
        even_rank_one_vector_wedge(odd, odd, source, exterior, context, -1, -1)


def test_even_tensor_homotopy_refuses_a_non_nilpotent_target() -> None:
    """A one-dimensional image alone does not kill correction curvature."""

    source = _fixture()
    source = replace(source, extension_terms=source.extension_terms + (
        replace(source.extension_terms[0], source=0),
    ))
    exterior = mixed_exterior_square(source)
    source_context = _MixedContraction(source, MixedSchoenUnit())
    context = _MixedContraction(exterior, MixedSchoenUnit())
    cochain = SparseOuterCechCochain(((OuterCechBasis(
        source_context.components[(2, 0, "k0")],
        (0, 0, 0), (0, 0, 0), (0, 0), ((0,), (0,), (0,)),
    ), Eisenstein(1)),))
    with pytest.raises(ValueError, match="nilpotent target with no self-arrow"):
        even_rank_one_vector_wedge(cochain, cochain, source, exterior, context, 0, 0)
