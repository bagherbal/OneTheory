"""Attack graded rank-one tensor coherence with exact mathematical fixtures.

Owns:
    Full noncycle Leibniz checks for syzygies, Koszul subsets, ordinary odd
    diagonals, coupled row closure, and incompatible twisting targets.

Depends on:
    The existing full differential and independently signed tensor comparison.

Must not:
    Interpret split line fixtures as carrier data or certify the outer cone.

Phase 0:
    Mathematical comparison tests, with no physical interpretation.
"""

from dataclasses import replace
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
from research.experiments.scientific_genesis.mixed_schoen_exterior_square import (
    mixed_exterior_square,
    resolution_vector_wedge,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import _MixedContraction
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import MixedSchoenUnit
from research.experiments.scientific_genesis.mixed_schoen_rank_one_tensor import (
    rank_one_vector_wedge,
    structurally_signed_vector_wedge,
)


def _cochain(context: _MixedContraction, index: int, subset: str, cell: tuple):
    component = context.components[(index, 0, subset)]
    x, u, p = component.ambient_degree
    return SparseOuterCechCochain(((OuterCechBasis(
        component, (x, 0, 0), (u, 0, 0), (p, 0), cell,
    ), Eisenstein(2, 1)),))


def _fixture(koszul_gauge: bool) -> MixedSchoenUnit:
    """Build a gauge-transformed split polynomial complex, not fitted data."""

    unit = MixedSchoenUnit()
    scalar = _MixedContraction(unit, unit)
    beta = SparseOuterCechCochain(((OuterCechBasis(
        scalar.components[(0, 0, "k1_x" if koszul_gauge else "k0")],
        (-3, 0, 0) if koszul_gauge else (0, 0, 0), (0, 0, 0),
        (-1, 0) if koszul_gauge else (0, 0),
        ((0, 1), (0,), (0,)) if koszul_gauge else ((0,), (0,), (0,)),
    ), Eisenstein(1, 1)),))
    alpha = scalar.differential(beta)
    # ds=u0 B, dt=(2+omega)u0 C makes polynomial naturality nontrivial.
    objects = tuple(MixedConstituentObject(name, degree, line) for name, degree, line in (
        ("A", 0, (0, 1, 0)), ("B", 0, (0, 1, 0)), ("C", 0, (0, 1, 0)),
        ("s", -1, (0, 0, 0)), ("t", -1, (0, 0, 0)),
    ))
    polynomial = Polynomial({(1, 0, 0): Eisenstein(1)}, scalar_type=Eisenstein)
    arrows = tuple(MixedResolutionArrow(i, j, polynomial.scale(value), 2)
                   for i, j, value in ((3, 1, Eisenstein(1)), (4, 2, Eisenstein(2, 1))))
    terms = []
    for index, odd, value in ((1, False, Eisenstein(1)), (2, False, Eisenstein(2)),
                              (3, True, Eisenstein(1)), (4, True, Eisenstein(4, 2))):
        coefficient = beta if odd else alpha
        for basis, c in coefficient.terms:
            terms.append(MixedExtensionTerm(
                index, 0, int(odd), None if basis.component.koszul_summand == "k0" else 1,
                basis.x_monomial,
                tuple(a + b for a, b in zip(basis.u_monomial,
                      (1, 0, 0) if odd else (0, 0, 0), strict=True)),
                basis.p_monomial, basis.cell, -c * value,
            ))
    return MixedSchoenUnit("graded gauge fixture", 2, (0, 0, 0), objects, arrows, tuple(terms))


@pytest.mark.parametrize("indices", ((0, 3), (3, 0), (1, 4), (4, 1), (3, 4), (3, 3)))
@pytest.mark.parametrize("subsets", tuple(product(("k0", "k1_x", "k1_u", "k2"), repeat=2)))
@pytest.mark.parametrize("koszul_gauge", (False, True))
def test_rank_one_tensor_full_syzygy_leibniz(
    indices: tuple[int, int], subsets: tuple[str, str], koszul_gauge: bool,
) -> None:
    """Differentiate noncycles on both slots, including odd diagonals."""

    source = _fixture(koszul_gauge)
    unit = MixedSchoenUnit()
    context = _MixedContraction(source, unit)
    exterior = mixed_exterior_square(source)
    out = _MixedContraction(exterior, unit)
    a = _cochain(context, indices[0], subsets[0], ((0, 1), (0,), (0,)))
    b = _cochain(context, indices[1], subsets[1], ((0, 1), (0,), (0,)))
    p, q = a.terms[0][0].total_degree, b.terms[0][0].total_degree

    def wedge(u, v, i, j):
        return rank_one_vector_wedge(u, v, source, exterior, out, i, j)

    assert context.differential(context.differential(a)).is_zero()
    assert context.differential(context.differential(b)).is_zero()
    assert out.differential(wedge(a, b, p, q)) == (
        wedge(context.differential(a), b, p + 1, q)
        + wedge(a, context.differential(b), p, q + 1).scale(-1 if p % 2 else 1)
    )


def test_structural_first_braiding_repairs_the_split_odd_counterexample() -> None:
    """The historical raw wedge already fails without a mixed arrow."""

    source = replace(_fixture(False), extension_terms=())
    context = _MixedContraction(source, MixedSchoenUnit())
    exterior = mixed_exterior_square(source)
    out = _MixedContraction(exterior, MixedSchoenUnit())
    a = _cochain(context, 3, "k0", ((0,), (0,), (0,)))
    b = _cochain(context, 1, "k0", ((0, 1), (0,), (0,)))
    p, q = -1, 1

    def defect(operation):
        def wedge(u, v, i, j):
            return operation(u, v, exterior, out, i, j)
        return out.differential(wedge(a, b, p, q)) + (
            wedge(context.differential(a), b, p + 1, q)
            + wedge(a, context.differential(b), p, q + 1).scale(-1)
        ).scale(-1)

    assert not defect(resolution_vector_wedge).is_zero()
    assert defect(structurally_signed_vector_wedge).is_zero()


def test_odd_coefficients_need_coupled_row_closure_not_scalar_closure() -> None:
    """Removing the odd comparison term must fail closed."""

    source = _fixture(False)
    bad = replace(source, extension_terms=tuple(t for t in source.extension_terms if t.source != 3))
    context = _MixedContraction(bad, MixedSchoenUnit())
    exterior = mixed_exterior_square(bad)
    out = _MixedContraction(exterior, MixedSchoenUnit())
    a = _cochain(context, 3, "k0", ((0,), (0,), (0,)))
    with pytest.raises(ValueError, match="full rank-one mixed row is not closed"):
        rank_one_vector_wedge(a, a, bad, exterior, out, -1, -1)


def test_rank_one_tensor_rejects_multiple_targets() -> None:
    source = _fixture(False)
    bad = replace(source, extension_terms=source.extension_terms + (
        replace(source.extension_terms[0], target=2),
    ))
    exterior = mixed_exterior_square(bad)
    out = _MixedContraction(exterior, MixedSchoenUnit())
    with pytest.raises(ValueError, match="one actual mixed-arrow target"):
        rank_one_vector_wedge(SparseOuterCechCochain(), SparseOuterCechCochain(),
                              bad, exterior, out, 0, 0)
