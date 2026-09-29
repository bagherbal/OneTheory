"""Compare graded tensor products with a rank-one twisted exterior complex.

Owns:
    Structural-first vector braiding and the coefficient diagonal homotopy
    for a closed mixed row into an isolated even line, including syzygies.

Depends on:
    The exact full mixed differential, ordinary graded exterior basis,
    ordered scalar cup, and explicitly derived product-cover homotopy.

Must not:
    Apply the formula to multiple twisting targets, silently drop syzygy
    arrows, identify the outer carrier product, or assign physical Yukawas.

Phase 0:
    Research-only tensor comparison under explicit rank-one hypotheses.
"""

from __future__ import annotations

from dataclasses import replace

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)

from .mixed_constituent_schoen_arrows import MixedConstituentObject
from .mixed_schoen_common_dga import mixed_outer_cup
from .mixed_schoen_cup_homotopy import mixed_scalar_cup_homotopy
from .mixed_schoen_exterior_square import (
    MixedExteriorSquare,
    _ordered_pair,
    mixed_exterior_square,
    resolution_vector_wedge,
)
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import MixedSchoenComplex, MixedSchoenUnit


def _components(cochain: SparseOuterCechCochain) -> dict[int, SparseOuterCechCochain]:
    """Split actual vector indices without changing their internal degrees."""

    groups: dict[int, list[tuple[OuterCechBasis, Eisenstein]]] = {}
    for basis, value in cochain.terms:
        groups.setdefault(basis.component.left_index, []).append((basis, value))
    return {index: SparseOuterCechCochain(tuple(terms)) for index, terms in groups.items()}


def structurally_signed_vector_wedge(
    left: SparseOuterCechCochain,
    right: SparseOuterCechCochain,
    exterior: MixedExteriorSquare,
    context: _MixedContraction,
    left_degree: int,
    right_degree: int,
) -> SparseOuterCechCochain:
    """Use the structural-first tensor convention of the full differential.

    For e_i tensor u_i and e_j tensor v_j, move u_i past e_j,
    giving (-1)^((|u|-p_i) p_j), not (-1)^(p_i (|v|-p_j)).
    This alone handles split polynomial resolutions. Mixed cover arrows
    still need a coefficient-order homotopy; this raw product is not
    claimed to be a chain map in an arbitrary twisted complex.
    """

    # Retain validation even if one input is zero, without changing the
    # historical raw operation or its content-addressed counterexample.
    resolution_vector_wedge(
        left, SparseOuterCechCochain(), exterior, context, left_degree, right_degree,
    )
    resolution_vector_wedge(
        SparseOuterCechCochain(), right, exterior, context, left_degree, right_degree,
    )
    result = SparseOuterCechCochain()
    for first, a in _components(left).items():
        for second, b in _components(right).items():
            p, q = exterior.source_positions[first], exterior.source_positions[second]
            crossing = (left_degree - p) * q + p * (right_degree - q)
            result = result + resolution_vector_wedge(
                a, b, exterior, context, left_degree, right_degree,
            ).scale(-1 if crossing % 2 else 1)
    return result


def _closed_rank_one_row(
    source: MixedSchoenComplex,
) -> tuple[int, tuple[tuple[int, SparseOuterCechCochain], ...]]:
    """Validate the whole Hom row, not separate closed odd coefficients."""

    targets = {term.target for term in source.extension_terms}
    if len(targets) != 1:
        raise ValueError("the tensor comparison requires one actual mixed-arrow target")
    target = next(iter(targets))
    if (
        source.objects[target].position != 0
        or any(term.source == target for term in source.extension_terms)
        or any(target in (arrow.source, arrow.target) for arrow in source.resolution_arrows)
    ):
        raise ValueError("the tensor comparison requires an isolated even nilpotent target")
    skeleton = MixedSchoenUnit(
        source.name + " polynomial skeleton", source.factor, source.twist,
        source.objects, source.resolution_arrows,
    )
    line_degree = source.objects[target].line_degree
    line = MixedSchoenUnit(
        "actual rank-one image", 0, line_degree,
        (MixedConstituentObject("actual rank-one image", 0, line_degree),),
    )
    hom = _MixedContraction(line, skeleton)
    row_terms = []
    scalar_terms: dict[int, list[tuple[OuterCechBasis, Eisenstein]]] = {}
    for term in source.extension_terms:
        position = source.objects[term.source].position
        if (
            position not in (-1, 0) or term.parent_degree != -position
            or term.parent_degree + term.cech_degree - term.koszul_degree != 1
        ):
            raise ValueError("the mixed tensor row has incompatible internal or total grading")
        koszul = term.koszul_summand
        component = hom.components[(0, term.source, koszul)]
        basis = OuterCechBasis(
            component, term.x_monomial, term.u_monomial, term.p_monomial, term.cell,
        )
        # These are actual left-action coefficients: parent zero has a
        # minus sign; parent one has none. Their scalar degrees are 1+p_j.
        value = term.coefficient * (-1 if position == 0 else 1)
        row_terms.append((basis, value))
        scalar_terms.setdefault(term.source, []).append((replace(
            basis, component=replace(component, right_index=0, object_degree=0),
        ), value))
    if not hom.differential(SparseOuterCechCochain(tuple(row_terms))).is_zero():
        raise ValueError(
            "the full rank-one mixed row is not closed against its polynomial skeleton"
        )
    return target, tuple(
        (index, SparseOuterCechCochain(tuple(terms)))
        for index, terms in sorted(scalar_terms.items())
    )


def rank_one_vector_wedge(
    left: SparseOuterCechCochain,
    right: SparseOuterCechCochain,
    source: MixedSchoenComplex,
    exterior: MixedExteriorSquare,
    context: _MixedContraction,
    left_degree: int,
    right_degree: int,
) -> SparseOuterCechCochain:
    """Correct all internal degrees for one closed row into an even line.

    Write a=|u|-p_i, t_j=1+p_j. The raw defect in e_i wedge A is
    (-1)^(p_i+a p_j) (alpha_j cup u_i
    - (-1)^(a t_j) u_i cup alpha_j) cup v_j. Subtract
    (-1)^(a p_j) H(alpha_j,u_i) cup v_j in that slot.
    The full row identity d alpha_odd = -alpha_even d_polynomial
    cancels the syzygy terms; global polynomial coefficients commute
    strictly with H. Quadratic corrections vanish in A wedge A.
    This does not construct the carrier's outer-cone comparison.
    """

    if exterior != mixed_exterior_square(source):
        raise ValueError("the tensor comparison needs the actual source exterior basis")
    raw = structurally_signed_vector_wedge(
        left, right, exterior, context, left_degree, right_degree,
    )
    target, coefficients = _closed_rank_one_row(source)

    def scalars(cochain: SparseOuterCechCochain) -> dict[int, SparseOuterCechCochain]:
        return {index: SparseOuterCechCochain(tuple((replace(
            basis, component=replace(basis.component, left_index=0, object_degree=0),
        ), value) for basis, value in group.terms))
                for index, group in _components(cochain).items()}

    a, b = scalars(left), scalars(right)
    indices = {pair: index for index, pair in enumerate(exterior.pairs)}
    terms = []
    for second, alpha in coefficients:
        if second not in b:
            continue
        for first, u in a.items():
            ordered = _ordered_pair(exterior.source_positions, first, target)
            if ordered is None:
                continue
            pair, sign = ordered
            if (
                (left_degree - exterior.source_positions[first])
                * exterior.source_positions[second]
            ) % 2:
                sign *= -1
            correction = mixed_outer_cup(mixed_scalar_cup_homotopy(alpha, u), b[second])
            for basis, value in correction.terms:
                component = context.components[(indices[pair], 0, basis.component.koszul_summand)]
                if component.line_degree != basis.component.line_degree:
                    raise ValueError("the tensor comparison changed the actual exterior line")
                image = replace(basis, component=component)
                if image.total_degree != left_degree + right_degree:
                    raise ValueError("the tensor comparison changed the total product degree")
                terms.append((image, value * sign))
    return raw + SparseOuterCechCochain(tuple(terms)).scale(-1)
