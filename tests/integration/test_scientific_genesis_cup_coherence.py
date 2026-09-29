"""Verify the higher cover coherence before applying coupled twisting rows.

Owns:
    Independent chain-boundary checks on all cell carriers and complete
    scalar Cech--Koszul identities, including the known Hirsch defect.

Depends on:
    Exact cover-chain witnesses and the derived scalar degree-minus-two map.

Must not:
    Infer carrier or physical pairing evidence from mathematical fixtures.

Phase 0:
    Independent exact mathematical coherence regression tests.
"""

from collections import Counter
from itertools import combinations, product

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis.mixed_schoen_common_dga import mixed_outer_cup as cup
from research.experiments.scientific_genesis.mixed_schoen_cup_coherence import (
    cell_cup_coherence,
    cell_hirsch_defect,
    cell_hirsch_filler,
)
from research.experiments.scientific_genesis.mixed_schoen_cup_coherence import (
    mixed_scalar_cup_coherence as coherence,
)
from research.experiments.scientific_genesis.mixed_schoen_cup_homotopy import (
    mixed_scalar_cup_homotopy as homotopy,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import _MixedContraction
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import mixed_schoen_unit


def _boundary(parts: tuple) -> Counter:
    """Independent boundary of any ordered product of simplex chains."""

    out = Counter()
    prefix = 0
    for i, s in enumerate(parts):
        if len(s) > 1:
            for j in range(len(s)):
                target = list(parts)
                target[i] = s[:j] + s[j + 1:]
                out[tuple(target)] += -1 if (prefix + j) % 2 else 1
        prefix += len(s) - 1
    return out


def _triple_boundary(chain: tuple) -> Counter:
    result = Counter()
    for (a, b, c), value in chain:
        for flat, sign in _boundary((*a, *b, *c)).items():
            result[(flat[:3], flat[3:6], flat[6:])] += sign * value
    return result


def _clean(chain: Counter) -> dict:
    return {k: v for k, v in chain.items() if v}


def test_acyclic_carrier_filler_on_all_147_cells() -> None:
    """Independently check boundary J+J boundary=0 and boundary K-K boundary=J."""

    cells = tuple(product(*(tuple(
        s for n in range(1, size + 1) for s in combinations(range(size), n)
    ) for size in (3, 3, 2))))
    assert len(cells) == 147
    nonzero = 0
    for cell in cells:
        j, k = cell_hirsch_defect(cell), cell_hirsch_filler(cell)
        nonzero += bool(k)
        dj, dk = _triple_boundary(j), _triple_boundary(k)
        for face, sign in _boundary(cell).items():
            for triple, value in cell_hirsch_defect(face):
                dj[triple] += sign * value
            for triple, value in cell_hirsch_filler(face):
                dk[triple] -= sign * value
        assert not _clean(dj), cell
        assert _clean(dk) == dict(j), cell
        for triple, _ in k:
            assert sum(len(s) - 1 for v in triple for s in v) == (
                sum(len(s) - 1 for s in cell) + 2
            )
            assert all(set(s) <= set(t) for v in triple for s, t in zip(v, cell, strict=True))
    assert nonzero > 0


@pytest.mark.parametrize("subsets", tuple(product(("k0", "k1_x", "k1_u", "k2"), repeat=3)))
@pytest.mark.parametrize("cells", (
    (((0,), (0, 1), (0,)), ((0,), (1,), (0, 1)), ((0,), (0,), (0, 1))),
    (((0, 1), (0, 1), (0,)), ((0, 1), (0,), (0,)), ((0,), (0, 1), (0,))),
))
def test_scalar_coherence_with_full_hypersurface_differential(subsets: tuple, cells: tuple) -> None:
    context = _MixedContraction(mixed_schoen_unit(), mixed_schoen_unit())

    def entry(subset: str, cell: tuple, value: Eisenstein):
        component = context.components[(0, 0, subset)]
        x, u, p = component.ambient_degree
        return SparseOuterCechCochain(((OuterCechBasis(
            component,
            tuple(x if i == cell[0][0] else 0 for i in range(3)),
            tuple(u if i == cell[1][0] else 0 for i in range(3)),
            tuple(p if i == cell[2][0] else 0 for i in range(2)), cell,
        ), value),))

    a, b, c = (entry(subset, cell, value) for subset, cell, value in zip(
        subsets, cells, (Eisenstein(2, 1), Eisenstein(1, -1) / 7, Eisenstein(3, 2)), strict=True,
    ))
    p, q, r = (v.terms[0][0].total_degree for v in (a, b, c))
    lhs = (
        context.differential(coherence(a, b, c))
        + coherence(context.differential(a), b, c).scale(-1)
        + coherence(a, context.differential(b), c).scale(1 if p % 2 else -1)
        + coherence(a, b, context.differential(c)).scale(1 if (p + q) % 2 else -1)
    )
    rhs = (
        homotopy(cup(a, b), c)
        + cup(a, homotopy(b, c)).scale(1 if p % 2 else -1)
        + cup(homotopy(a, c), b).scale(1 if q * r % 2 else -1)
    )
    assert lhs == rhs


def test_coherence_refuses_matrix_and_unordered_inputs() -> None:
    v = SparseOuterCechCochain(((OuterCechBasis(
        OuterCechComponent(1, 0, 0, (0, 0, 0), "k0"),
        (0, 0, 0), (0, 0, 0), (0, 0), ((0,), (0,), (0,)),
    ), Eisenstein(1)),))
    with pytest.raises(ValueError, match="cannot commute matrix"):
        coherence(v, v, v)
    with pytest.raises(ValueError, match="ordered cells"):
        cell_cup_coherence(((1, 0), (0,), (0,)), ((0,), (0,), (0,)), ((0,), (0,), (0,)))
