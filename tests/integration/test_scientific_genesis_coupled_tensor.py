"""Attack the two-row exterior quotient theorem with exact mathematical gauges.

Owns:
    Full signed noncycle Leibniz checks with coupled targets, syzygies,
    Koszul-dependent gauges, and differential-invariant quotient tests.

Depends on:
    The complete mixed differential and independently verified H/T coherence.

Must not:
    Use split mathematical fixtures as a carrier or physical coupling.

Phase 0:
    Mathematical coupled-comparison regression tests only.
"""

from dataclasses import replace
from functools import cache
from itertools import product

import pytest

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
    MixedExtensionTerm,
    MixedResolutionArrow,
)
from research.experiments.scientific_genesis.mixed_schoen_common_dga import mixed_outer_cup as cup
from research.experiments.scientific_genesis.mixed_schoen_coupled_tensor import (
    _coupled_quotient_wedge,
    coupled_exterior_quotient,
    coupled_quotient_vector_wedge,
    cover_vertex_restriction,
    project_coupled_exterior,
)
from research.experiments.scientific_genesis.mixed_schoen_cup_coherence import (
    cell_diagonal_homotopy,
    cell_hirsch_filler,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import _MixedContraction
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    MixedSchoenUnit,
    _koszul_product,
    mixed_schoen_unit,
)


def _entry(context, index, subset, cell, value=1):
    component = context.components[(index, 0, subset)]
    x, u, p = component.ambient_degree
    return SparseOuterCechCochain(((OuterCechBasis(
        component,
        tuple(x if i == cell[0][0] else 0 for i in range(3)),
        tuple(u if i == cell[1][0] else 0 for i in range(3)),
        tuple(p if i == cell[2][0] else 0 for i in range(2)), cell,
    ), Eisenstein.coerce(value)),))


@cache
def _fixture(koszul_gauge: bool | str):
    unit = mixed_schoen_unit()
    scalar = _MixedContraction(unit, unit)
    eta = (_entry(scalar, 0, "k0", ((0,), (0,), (0,)), Eisenstein(2, 1)),
           _entry(scalar, 0, "k0", ((0,), (1,), (1,)), Eisenstein(1, -1)))
    gamma = _entry(scalar, 0, "k2" if koszul_gauge == "k2" else (
        "k1_x" if koszul_gauge else "k0"
    ), ((0, 1), (0, 1), (0,)) if koszul_gauge == "k2" else (
        ((0, 1), (1,), (0,)) if koszul_gauge else ((0,), (1,), (0,))
    ),
                   Eisenstein(1, 1))
    terms = []

    def row(source, target, coefficient, odd=False):
        for b, c in coefficient.terms:
            subset = b.component.koszul_summand
            terms.append(MixedExtensionTerm(
                source, target, int(odd), {
                    "k0": None, "k1_x": 1, "k1_u": 2, "k2": (1, 2),
                }[subset], b.x_monomial, b.u_monomial, b.p_monomial, b.cell,
                c * (1 if odd else -1),
            ))

    for source, odd, coefficient in ((2, 4, eta[0]), (3, 5, eta[1])):
        alpha = scalar.differential(coefficient)
        row(source, 1, alpha)
        row(odd, 1, coefficient.scale(-1), True)
        row(source, 0, cup(gamma, alpha).scale(-1))
        row(odd, 0, cup(gamma, coefficient), True)
    row(1, 0, scalar.differential(gamma))
    return MixedSchoenUnit(
        "coupled mathematical gauge fixture", 2, (0, 0, 0),
        tuple(MixedConstituentObject(name, p, (0, 0, 0))
              for name, p in (("B", 0), ("A", 0), ("C", 0), ("D", 0), ("s", -1), ("t", -1))),
        tuple(MixedResolutionArrow(i, j, Polynomial.constant(1, 3, scalar_type=Eisenstein), 2)
              for i, j in ((4, 2), (5, 3))), tuple(terms),
    )


@pytest.mark.parametrize("indices", ((2, 3), (4, 2), (2, 4), (4, 5), (4, 4), (1, 4)))
@pytest.mark.parametrize("subsets", tuple(product(("k0", "k1_x", "k1_u", "k2"), repeat=2)))
@pytest.mark.parametrize("gauge", (False, True, "k2"))
def test_full_coupled_quotient_leibniz(indices: tuple, subsets: tuple, gauge: bool) -> None:
    source = _fixture(gauge)
    model = coupled_exterior_quotient(source, 1, 0)
    context = _MixedContraction(source, mixed_schoen_unit())
    out = _MixedContraction(model.quotient, mixed_schoen_unit())
    a = _entry(context, indices[0], subsets[0], ((0,), (0, 1), (0,)))
    b = _entry(context, indices[1], subsets[1], ((0,), (0,), (0, 1)))
    p, q = a.terms[0][0].total_degree, b.terms[0][0].total_degree
    assert context.differential(context.differential(a)).is_zero()
    assert context.differential(context.differential(b)).is_zero()
    wedge = coupled_quotient_vector_wedge(a, b, model, p, q)
    assert out.differential(wedge) == (
        coupled_quotient_vector_wedge(context.differential(a), b, model, p + 1, q)
        + coupled_quotient_vector_wedge(a, context.differential(b), model, p, q + 1).scale(
            -1 if p % 2 else 1
        )
    )
    assert out.differential(out.differential(wedge)).is_zero()


def test_the_killed_pair_is_a_differential_invariant_relation() -> None:
    source = _fixture(False)
    model = coupled_exterior_quotient(source, 1, 0)
    context = _MixedContraction(model.exterior, mixed_schoen_unit())
    index = model.exterior.pairs.index((0, 1))
    pair = _entry(context, index, "k0", ((0,), (0,), (0,)))
    assert project_coupled_exterior(pair, model).is_zero()
    assert project_coupled_exterior(context.differential(pair), model).is_zero()


def test_an_unclosed_outer_row_cannot_supply_a_quotient_product() -> None:
    source = _fixture(False)
    broken = replace(source, extension_terms=tuple(
        t for t in source.extension_terms if t.source != 4
    ))
    with pytest.raises(ValueError, match="mixed row is not closed"):
        coupled_exterior_quotient(broken, 1, 0)


def test_the_additive_shortcut_fails_but_higher_coherence_repairs_it() -> None:
    source = _fixture(False)
    model = coupled_exterior_quotient(source, 1, 0)
    context = _MixedContraction(source, mixed_schoen_unit())
    out = _MixedContraction(model.quotient, mixed_schoen_unit())
    a = _entry(context, 2, "k0", ((0,), (0,), (0, 1)))
    b = _entry(context, 3, "k0", ((0, 1), (1,), (1,)))

    def defect(higher):
        def wedge(a, b, p, q):
            return _coupled_quotient_wedge(a, b, model, p, q, higher)
        return out.differential(wedge(a, b, 1, 1)) + (
            wedge(context.differential(a), b, 2, 1)
            + wedge(a, context.differential(b), 1, 2).scale(-1)
        ).scale(-1)

    assert len(defect(False).terms) == 1
    assert defect(True).is_zero()


@pytest.mark.parametrize("equation,subset", (
    (None, "k0"), (1, "k1_x"), (2, "k1_u"), ((1, 2), "k2"),
))
@pytest.mark.parametrize("right", ("k0", "k1_x", "k1_u", "k2"))
@pytest.mark.parametrize("side", ("left", "right"))
def test_complete_ordered_koszul_arrow_product(equation, subset, right, side) -> None:
    from research.experiments.scientific_genesis.mixed_schoen_common_dga import _koszul_cup

    expected = _koszul_cup(subset, right) if side == "left" else _koszul_cup(right, subset)
    assert _koszul_product(equation, right, side) == expected


def test_a_reversed_equation_subset_cannot_be_silently_normalized() -> None:
    with pytest.raises(ValueError, match="complete ordered equation subset"):
        _koszul_product((2, 1), "k0", "left")


def _independent_local_wedge(a, b, model):
    """Compute the local graded exterior product without the cover kernels."""

    out = _MixedContraction(model.quotient, mixed_schoen_unit())
    pairs = {pair: i for i, pair in enumerate(model.quotient.pairs)}
    subsets = {"k0": (), "k1_x": (0,), "k1_u": (1,), "k2": (0, 1)}
    names = {subset: name for name, subset in subsets.items()}
    terms = []
    for u, av in a.terms:
        for v, bv in b.terms:
            assert u.cell == v.cell and u.cech_degree == v.cech_degree == 0
            i, j = u.component.left_index, v.component.left_index
            p, q = model.source.objects[i].position, model.source.objects[j].position
            if (i == j and p % 2 == 0) or tuple(sorted((i, j))) not in pairs:
                continue
            first, second = subsets[u.component.koszul_summand], subsets[v.component.koszul_summand]
            if set(first) & set(second):
                continue
            # Move u's coefficient past the second internal generator,
            # then order the two generators and the exterior Koszul set.
            exponent = (u.total_degree - p) * q + sum(x > y for x in first for y in second)
            if i > j:
                exponent += 1 + p * q
            component = out.components[(
                pairs[tuple(sorted((i, j)))], 0, names[tuple(sorted((*first, *second)))],
            )]
            image = OuterCechBasis(component,
                tuple(x + y for x, y in zip(u.x_monomial, v.x_monomial, strict=True)),
                tuple(x + y for x, y in zip(u.u_monomial, v.u_monomial, strict=True)),
                tuple(x + y for x, y in zip(u.p_monomial, v.p_monomial, strict=True)), u.cell,
            )
            terms.append((image, av * bv * (-1 if exponent % 2 else 1)))
    return SparseOuterCechCochain(tuple(terms))


@pytest.mark.parametrize("indices", ((2, 3), (4, 2), (2, 4), (4, 5), (4, 4), (1, 4)))
@pytest.mark.parametrize("subsets", tuple(product(("k0", "k1_x", "k1_u", "k2"), repeat=2)))
@pytest.mark.parametrize("gauge", (False, True, "k2"))
def test_coupled_product_restricts_to_the_ordinary_local_exterior_map(indices, subsets, gauge):
    """Compare literal local components to an independent Koszul sign formula."""

    model = coupled_exterior_quotient(_fixture(gauge), 1, 0)
    context = _MixedContraction(model.source, mixed_schoen_unit())
    vertex, other = ((0,), (1,), (0,)), ((2,), (2,), (1,))
    left, right = tuple(
        _entry(context, i, subset, vertex, Eisenstein(2, 1))
        + _entry(context, i, subset, other, Eisenstein(1, -1))
        for i, subset in zip(indices, subsets, strict=True)
    )
    p, q = left.terms[0][0].total_degree, right.terms[0][0].total_degree
    full = coupled_quotient_vector_wedge(left, right, model, p, q)
    assert cover_vertex_restriction(full, vertex) == _independent_local_wedge(
        cover_vertex_restriction(left, vertex), cover_vertex_restriction(right, vertex), model,
    )


@pytest.mark.parametrize("vertex", tuple(
    tuple((i,) for i in indices) for indices in product(range(3), range(3), range(2))
))
def test_vertex_projection_retains_the_local_differential_and_kills_coherences(vertex):
    """Keep all local syzygy and Koszul arrows, not just degree-zero scalars."""

    model = coupled_exterior_quotient(_fixture("k2"), 1, 0)
    source = _MixedContraction(model.source, mixed_schoen_unit())
    out = _MixedContraction(model.quotient, mixed_schoen_unit())
    for context, index in ((source, 4), (out, 0)):
        value = _entry(context, index, "k1_x", vertex)
        edge = ((0, 1), (0,), (0,))
        full = value + _entry(context, index, "k0", edge)
        assert cover_vertex_restriction(context.differential(full), vertex) == (
            cover_vertex_restriction(context.differential(value), vertex)
        )
    assert cell_diagonal_homotopy(vertex) == ()
    assert cell_hirsch_filler(vertex) == ()


@pytest.mark.parametrize("bad", (
    ((0,), (0,)), ((0, 1), (0,), (0,)), ((3,), (0,), (0,)), ((0,), (0,), (2,)),
))
def test_local_projection_refuses_an_undeclared_cover_vertex(bad):
    with pytest.raises(ValueError, match="vertex of the declared product cover"):
        cover_vertex_restriction(SparseOuterCechCochain(), bad)
