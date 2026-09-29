"""Compose a two-row tensor comparison into its legitimate exterior quotient.

Owns:
    The quotient killing A wedge B, full coupled-row validation, and
    the exact higher correction for a triangular A-to-B twisting path.

Depends on:
    Explicit graded resolution objects, the complete mixed differential,
    structural-first braiding, and verified scalar H and T coherence.

Must not:
    Apply the construction to other arrow graphs, declare the carrier
    identification without comparison, or assign a physical coefficient.

Phase 0:
    Research-only coupled tensor theorem under explicit structural hypotheses.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cache

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)

from .mixed_constituent_schoen_arrows import Cell, MixedConstituentObject
from .mixed_schoen_common_dga import mixed_outer_cup
from .mixed_schoen_cup_coherence import mixed_scalar_cup_coherence
from .mixed_schoen_cup_homotopy import mixed_scalar_cup_homotopy
from .mixed_schoen_exterior_square import (
    MixedExteriorSquare,
    _ordered_pair,
    mixed_exterior_square,
)
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import MixedSchoenComplex, MixedSchoenUnit, mixed_schoen_unit
from .mixed_schoen_rank_one_tensor import (
    _closed_rank_one_row,
    _components,
    structurally_signed_vector_wedge,
)


@dataclass(frozen=True, slots=True)
class CoupledExteriorQuotient:
    """One explicit quotient presentation and its validated triangular rows."""

    source: MixedSchoenUnit
    exterior: MixedExteriorSquare
    quotient: MixedExteriorSquare
    inner_target: int
    outer_target: int
    inner_row: tuple[tuple[int, SparseOuterCechCochain], ...]
    outer_row: tuple[tuple[int, SparseOuterCechCochain], ...]
    projection: tuple[int | None, ...]


def coupled_exterior_quotient(
    source: MixedSchoenComplex, inner_target: int, outer_target: int,
) -> CoupledExteriorQuotient:
    """Validate explicit A and B targets, then kill the invariant A wedge B."""

    return _coupled_exterior_quotient(MixedSchoenUnit(
        source.name, source.factor, source.twist, source.objects,
        source.resolution_arrows, source.extension_terms,
    ), inner_target, outer_target)


@cache
def _coupled_exterior_quotient(
    source: MixedSchoenUnit, inner: int, outer: int,
) -> CoupledExteriorQuotient:
    if (
        inner == outer or any(i not in range(len(source.objects)) for i in (inner, outer))
        or any(source.objects[i].position != 0 for i in (inner, outer))
        or {t.target for t in source.extension_terms} != {inner, outer}
        or any(t.source == outer or (t.target == inner and t.source == inner)
               for t in source.extension_terms)
        or any(i in (inner, outer) for arrow in source.resolution_arrows
               for i in (arrow.source, arrow.target))
    ):
        raise ValueError(
            "the coupled comparison requires the declared triangular even A-to-B graph"
        )
    inside = replace(source, extension_terms=tuple(
        t for t in source.extension_terms if t.target == inner
    ))
    target, inner_row = _closed_rank_one_row(inside)
    if target != inner:
        raise ValueError("the inner mixed row does not land in the declared A line")
    degree = source.objects[outer].line_degree
    line = MixedSchoenUnit(
        "declared outer target", 0, degree,
        (MixedConstituentObject("declared outer target", 0, degree),),
    )
    context = _MixedContraction(line, inside)
    full = []
    scalars: dict[int, list[tuple[OuterCechBasis, Eisenstein]]] = {}
    for t in source.extension_terms:
        if t.target != outer:
            continue
        p = source.objects[t.source].position
        if t.parent_degree != -p or t.parent_degree + t.cech_degree - t.koszul_degree != 1:
            raise ValueError("the coupled outer row has an inconsistent total degree")
        k = t.koszul_summand
        basis = OuterCechBasis(context.components[(0, t.source, k)],
                               t.x_monomial, t.u_monomial, t.p_monomial, t.cell)
        value = t.coefficient * (-1 if p == 0 else 1)
        full.append((basis, value))
        scalars.setdefault(t.source, []).append((replace(
            basis, component=replace(basis.component, right_index=0, object_degree=0),
        ), value))
    if not context.differential(SparseOuterCechCochain(tuple(full))).is_zero():
        raise ValueError(
            "the coupled outer Hom row is not closed against the complete inner complex"
        )
    exterior = mixed_exterior_square(source)
    pair = tuple(sorted((inner, outer)))
    killed = exterior.pairs.index(pair)
    projection = tuple(None if i == killed else i - int(i > killed)
                       for i in range(len(exterior.pairs)))
    if any(a.source == killed for a in exterior.resolution_arrows) or any(
        t.source == killed for t in exterior.extension_terms
    ):
        raise ValueError("A wedge B is not a differential-invariant quotient relation")
    retained = {i: index for i, index in enumerate(projection) if index is not None}
    quotient = replace(
        exterior, name=f"{exterior.name} modulo the declared A wedge B",
        objects=tuple(o for i, o in enumerate(exterior.objects) if i != killed),
        pairs=tuple(p for i, p in enumerate(exterior.pairs) if i != killed),
        resolution_arrows=tuple(replace(a, source=retained[a.source],
                                        target=retained[a.target])
                                for a in exterior.resolution_arrows if a.target != killed),
        extension_terms=tuple(replace(t, source=retained[t.source],
                                     target=retained[t.target])
                             for t in exterior.extension_terms if t.target != killed),
    )
    return CoupledExteriorQuotient(source, exterior, quotient, inner, outer, inner_row,
                                  tuple((i, SparseOuterCechCochain(tuple(v)))
                                        for i, v in sorted(scalars.items())), projection)


def project_coupled_exterior(
    cochain: SparseOuterCechCochain, model: CoupledExteriorQuotient,
) -> SparseOuterCechCochain:
    """Apply only the declared quotient, with full basis compatibility checks."""

    terms = []
    for b, value in cochain.terms:
        c = b.component
        if c.right_index != 0 or c.left_index not in range(len(model.exterior.objects)):
            raise ValueError("the exterior quotient input is not in its declared source basis")
        obj = model.exterior.objects[c.left_index]
        if c.object_degree != obj.position or c.line_degree != obj.line_degree:
            raise ValueError("the exterior quotient input has an incompatible grading or line")
        index = model.projection[c.left_index]
        if index is not None:
            terms.append((replace(b, component=replace(c, left_index=index)), value))
    return SparseOuterCechCochain(tuple(terms))


def cover_vertex_restriction(
    cochain: SparseOuterCechCochain, vertex: Cell,
) -> SparseOuterCechCochain:
    """Read the local resolution component at a declared cover vertex.

    The differential cannot lower cover degree. At a vertex its positive
    cover arrows disappear; polynomial, vertex and Koszul arrows remain.
    This projection is not a global augmentation or a cohomology solver.
    It supplies the local comparison required in the sheaf criterion.
    """

    if len(vertex) != 3 or any(
        len(simplex) != 1 or simplex[0] not in range(size)
        for simplex, size in zip(vertex, (3, 3, 2), strict=True)
    ):
        raise ValueError("the local comparison requires a vertex of the declared product cover")
    return SparseOuterCechCochain(tuple(
        (basis, value) for basis, value in cochain.terms if basis.cell == vertex
    ))


def coupled_quotient_vector_wedge(
    left: SparseOuterCechCochain, right: SparseOuterCechCochain,
    model: CoupledExteriorQuotient, left_degree: int, right_degree: int,
) -> SparseOuterCechCochain:
    """Use W-N_alpha-N_beta+M in the legitimate A wedge B quotient.

    For a=|u|-p_i, each N has coefficient (-1)^(a p_j) H(row_j,u_i)v_j.
    The new M has coefficient (-1)^(a p_j) T(beta_A,alpha_j,u_i)v_j
    in e_i wedge B. Its differential cancels the full first-slot Hirsch
    defect of the additive correction. All remaining quadratic outputs
    vanish in the declared quotient; syzygy terms cancel by row closure.
    """

    return _coupled_quotient_wedge(left, right, model, left_degree, right_degree, True)


def _coupled_quotient_wedge(
    left: SparseOuterCechCochain, right: SparseOuterCechCochain,
    model: CoupledExteriorQuotient, left_degree: int, right_degree: int, higher: bool,
) -> SparseOuterCechCochain:
    """The false value is solely the explicit additive-shortcut attack."""

    raw = structurally_signed_vector_wedge(left, right, model.exterior,
                                          _MixedContraction(model.exterior, mixed_schoen_unit()),
                                          left_degree, right_degree)
    result = project_coupled_exterior(raw, model)
    a, b = tuple({i: SparseOuterCechCochain(tuple((replace(
        basis, component=replace(basis.component, left_index=0, object_degree=0),
    ), value) for basis, value in group.terms)) for i, group in _components(v).items()}
                 for v in (left, right))
    indices = {pair: i for i, pair in enumerate(model.quotient.pairs)}
    context = _MixedContraction(model.quotient, mixed_schoen_unit())
    terms = []

    def add(
        first: int, second: int, target: int, value: SparseOuterCechCochain, sign: int,
    ) -> None:
        ordered = _ordered_pair(model.exterior.source_positions, first, target)
        if ordered is None or ordered[0] not in indices:
            return
        if (left_degree - model.exterior.source_positions[first]) * (
            model.exterior.source_positions[second]
        ) % 2:
            sign *= -1
        for basis, coefficient in value.terms:
            c = context.components[(indices[ordered[0]], 0, basis.component.koszul_summand)]
            if c.line_degree != basis.component.line_degree:
                raise ValueError("the coupled tensor homotopy changed its declared line")
            image = replace(basis, component=c)
            if image.total_degree != left_degree + right_degree:
                raise ValueError("the coupled tensor homotopy changed its total product degree")
            terms.append((image, coefficient * sign * ordered[1]))

    for target, row in (
        (model.inner_target, model.inner_row), (model.outer_target, model.outer_row),
    ):
        for second, alpha in row:
            if second not in b:
                continue
            for first, u in a.items():
                ordered = _ordered_pair(model.exterior.source_positions, first, target)
                if ordered is None or ordered[0] not in indices:
                    continue
                add(first, second, target, mixed_outer_cup(
                    mixed_scalar_cup_homotopy(alpha, u), b[second],
                ), -1)
    beta_a = dict(model.outer_row).get(model.inner_target)
    if higher and beta_a is not None:
        for second, alpha in model.inner_row:
            if second not in b:
                continue
            for first, u in a.items():
                ordered = _ordered_pair(
                    model.exterior.source_positions, first, model.outer_target,
                )
                if ordered is None or ordered[0] not in indices:
                    continue
                add(first, second, model.outer_target, mixed_outer_cup(
                    mixed_scalar_cup_coherence(beta_a, alpha, u), b[second],
                ), 1)
    return result + SparseOuterCechCochain(tuple(terms))
