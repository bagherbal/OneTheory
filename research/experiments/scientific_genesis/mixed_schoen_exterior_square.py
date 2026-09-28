"""Form a signed exterior square of a two-term mixed Schoen resolution.

Owns:
    The graded exterior monomial basis, induced resolution arrows, and
    ordered products of reciprocal line-valued covectors in that basis.

Depends on:
    The existing synchronized mixed differential, Alexander--Whitney cup,
    Koszul signs, and exact sparse Eisenstein cochains.

Must not:
    Assume the noncommutative cover product descends to every exterior
    complex, replace odd squares by divided powers, or claim a Yukawa.

Phase 0:
    Research-only exterior construction; full closure requires exact checks.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cache
from typing import cast

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    KOSZUL_DEGREES,
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
)

from .mixed_constituent_schoen_arrows import (
    Cell,
    MixedConstituentObject,
    MixedExtensionTerm,
    MixedResolutionArrow,
)
from .mixed_schoen_common_dga import _koszul_cup, _sum_tuple
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import MixedSchoenComplex, _cell_cup


def _ordered_pair(
    positions: tuple[int, ...], first: int, second: int
) -> tuple[tuple[int, int], int] | None:
    """Use v_i wedge v_j = -(-1)^(p_i p_j) v_j wedge v_i."""

    if first == second and positions[first] % 2 == 0:
        return None
    if first <= second:
        return (first, second), 1
    sign = 1 if positions[first] * positions[second] % 2 else -1
    return (second, first), sign


@dataclass(frozen=True, slots=True)
class MixedExteriorSquare:
    """An explicit graded exterior resolution, not a cohomology shortcut."""

    name: str
    factor: int
    twist: tuple[int, int, int]
    objects: tuple[MixedConstituentObject, ...]
    resolution_arrows: tuple[MixedResolutionArrow, ...]
    extension_terms: tuple[MixedExtensionTerm, ...]
    pairs: tuple[tuple[int, int], ...]
    source_positions: tuple[int, ...]
    source_lines: tuple[tuple[int, int, int], ...]


def mixed_exterior_square(source: MixedSchoenComplex) -> MixedExteriorSquare:
    """Apply the graded derivation to each slot, without discarding terms.

    For an internal arrow of degree s, the second slot has sign
    (-1)^(p_first s). In particular d(v wedge v)=2 dv wedge v for
    an odd syzygy. A mixed cover differential is only a candidate
    until its square and the required full products are checked.
    """

    positions = tuple(item.position for item in source.objects)
    if not positions or any(position not in (-1, 0) for position in positions):
        raise ValueError("the exterior construction requires a two-term resolution")
    pairs = tuple(
        (first, second)
        for first in range(len(positions))
        for second in range(first, len(positions))
        if first != second or positions[first] % 2
    )
    indices = {pair: index for index, pair in enumerate(pairs)}
    objects = tuple(
        MixedConstituentObject(
            f"{source.objects[first].name} wedge {source.objects[second].name}",
            positions[first] + positions[second],
            cast(tuple[int, int, int], tuple(a + b for a, b in zip(
                source.objects[first].line_degree,
                source.objects[second].line_degree, strict=True,
            ))),
        )
        for first, second in pairs
    )
    polynomials: dict[tuple[int, int, int], Polynomial] = {}
    terms: dict[MixedExtensionTerm, Eisenstein] = {}
    for pair_index, (first, second) in enumerate(pairs):
        for slot, object_index in enumerate((first, second)):
            for arrow in source.resolution_arrows:
                if arrow.source != object_index:
                    continue
                degree = positions[arrow.target] - positions[arrow.source]
                if degree != 1:
                    raise ValueError("a structural arrow must have internal degree one")
                ordered = _ordered_pair(
                    positions,
                    arrow.target if slot == 0 else first,
                    second if slot == 0 else arrow.target,
                )
                if ordered is None:
                    continue
                pair, sign = ordered
                if slot == 1 and positions[first] * degree % 2:
                    sign *= -1
                key = pair_index, indices[pair], arrow.factor
                value = arrow.polynomial.scale(sign)
                polynomials[key] = value if key not in polynomials else polynomials[key] + value
            for term in source.extension_terms:
                if term.source != object_index:
                    continue
                degree = positions[term.target] - positions[term.source]
                if degree != term.parent_degree:
                    raise ValueError("a mixed arrow has an inconsistent internal degree")
                if degree + term.cech_degree - term.koszul_degree != 1:
                    raise ValueError("a mixed arrow must have total degree one")
                ordered = _ordered_pair(
                    positions,
                    term.target if slot == 0 else first,
                    second if slot == 0 else term.target,
                )
                if ordered is None:
                    continue
                pair, sign = ordered
                if slot == 1 and positions[first] * degree % 2:
                    sign *= -1
                term_key = replace(
                    term, source=pair_index, target=indices[pair], coefficient=Eisenstein(1)
                )
                terms[term_key] = terms.get(term_key, Eisenstein(0)) + term.coefficient * sign
    return MixedExteriorSquare(
        f"derived exterior square of {source.name}", source.factor,
        cast(tuple[int, int, int], tuple(2 * item for item in source.twist)), objects,
        tuple(
            MixedResolutionArrow(first, second, polynomial, factor)
            for (first, second, factor), polynomial in sorted(polynomials.items())
            if not polynomial.is_zero()
        ),
        tuple(
            replace(term, coefficient=coefficient)
            for term, coefficient in terms.items() if not coefficient.is_zero()
        ),
        pairs, positions, tuple(item.line_degree for item in source.objects),
    )


def reciprocal_covector_wedge(
    left: SparseOuterCechCochain,
    right: SparseOuterCechCochain,
    exterior: MixedExteriorSquare,
    context: _MixedContraction,
    left_degree: int,
    right_degree: int,
) -> SparseOuterCechCochain:
    """Evaluate the ordered antisymmetrized tensor on exterior monomials.

    The evaluation sign is (-1)^(left_degree p_right), followed by
    graded pair reordering and the external Cech/Koszul cup sign.
    An odd diagonal is evaluated with multiplicity two. No cover
    commutativity or chain-map property is assumed by this function.
    """

    if context.right != exterior or len(context.left.objects) != 1:
        raise ValueError("the exterior covector target must be one declared line")
    target_line = context.left.objects[0].line_degree
    input_lines = []
    for cochain, degree in ((left, left_degree), (right, right_degree)):
        lines = set()
        for basis, _ in cochain.terms:
            component = basis.component
            index = component.right_index
            if component.left_index != 0 or index not in range(len(exterior.source_positions)):
                raise ValueError("an exterior input is not a source covector")
            if (
                basis.total_degree != degree
                or component.object_degree != -exterior.source_positions[index]
            ):
                raise ValueError("an exterior input has incompatible grading")
            lines.add(tuple(a + b for a, b in zip(
                component.line_degree, exterior.source_lines[index], strict=True,
            )))
        if len(lines) != 1:
            raise ValueError("each exterior input must have one declared target line")
        input_lines.append(next(iter(lines)))
    if tuple(a + b for a, b in zip(*input_lines, strict=True)) != target_line:
        raise ValueError("the exterior covector target lines are incompatible")
    indices = {pair: index for index, pair in enumerate(exterior.pairs)}

    @cache
    def compatible(
        i: int, first_cell: Cell, first_koszul: str,
        j: int, second_cell: Cell, second_koszul: str,
    ) -> tuple[int, OuterCechComponent, Cell] | None:
        """Reuse cell compatibility without identifying Laurent monomials."""

        ordered = _ordered_pair(exterior.source_positions, i, j)
        if ordered is None:
            return None
        cell = _cell_cup(first_cell, second_cell, "left")
        koszul = _koszul_cup(first_koszul, second_koszul)
        if cell is None or koszul is None:
            return None
        pair, sign = ordered
        cell_sign, target_cell = cell
        koszul_sign, target_koszul = koszul
        crossing = (
            left_degree * exterior.source_positions[j]
            + sum(len(simplex) - 1 for simplex in first_cell) * KOSZUL_DEGREES[second_koszul]
        )
        if crossing % 2:
            sign *= -1
        if i == j:
            sign *= 2
        return (
            sign * cell_sign * koszul_sign,
            context.components[(0, indices[pair], target_koszul)], target_cell,
        )

    result = []
    for first, first_coefficient in left.terms:
        i = first.component.right_index
        for second, second_coefficient in right.terms:
            j = second.component.right_index
            target = compatible(
                i, first.cell, first.component.koszul_summand,
                j, second.cell, second.component.koszul_summand,
            )
            if target is None:
                continue
            sign, component, target_cell = target
            basis = OuterCechBasis(
                component,
                cast(tuple[int, int, int], _sum_tuple(first.x_monomial, second.x_monomial)),
                cast(tuple[int, int, int], _sum_tuple(first.u_monomial, second.u_monomial)),
                cast(tuple[int, int], _sum_tuple(first.p_monomial, second.p_monomial)), target_cell,
            )
            if basis.total_degree != left_degree + right_degree:
                raise ValueError("the exterior product changed its total degree")
            result.append((
                basis, first_coefficient * second_coefficient * sign
            ))
    return SparseOuterCechCochain(tuple(result))


def resolution_vector_wedge(
    left: SparseOuterCechCochain,
    right: SparseOuterCechCochain,
    exterior: MixedExteriorSquare,
    context: _MixedContraction,
    left_degree: int,
    right_degree: int,
) -> SparseOuterCechCochain:
    """Multiply actual resolution-valued cochains in the exterior basis.

    Moving the first internal vector through the second coefficient
    contributes (-1)^(p_first (right_degree-p_second)). Odd diagonals
    are ordinary monomials, so this forward product has no factor two.
    The ordered cover cup need not make this a chain map on arbitrary
    mixed inputs; closure and Leibniz identities must be checked in
    the complete differential for every scientific use.
    """

    if (
        context.left != exterior
        or len(context.right.objects) != 1
        or context.right.objects[0].position != 0
        or context.right.objects[0].line_degree != (0, 0, 0)
    ):
        raise ValueError("the exterior vector source must be the declared unit")
    for cochain, degree in ((left, left_degree), (right, right_degree)):
        for basis, _ in cochain.terms:
            component = basis.component
            index = component.left_index
            if component.right_index != 0 or index not in range(len(exterior.source_positions)):
                raise ValueError("an exterior input is not a resolution vector")
            if (
                basis.total_degree != degree
                or component.object_degree != exterior.source_positions[index]
                or component.line_degree != exterior.source_lines[index]
            ):
                raise ValueError("an exterior vector has incompatible basis or grading")
    indices = {pair: index for index, pair in enumerate(exterior.pairs)}

    @cache
    def compatible(
        i: int, first_cell: Cell, first_koszul: str,
        j: int, second_cell: Cell, second_koszul: str,
    ) -> tuple[int, OuterCechComponent, Cell] | None:
        ordered = _ordered_pair(exterior.source_positions, i, j)
        if ordered is None:
            return None
        cell = _cell_cup(first_cell, second_cell, "left")
        koszul = _koszul_cup(first_koszul, second_koszul)
        if cell is None or koszul is None:
            return None
        pair, sign = ordered
        cell_sign, target_cell = cell
        koszul_sign, target_koszul = koszul
        crossing = (
            exterior.source_positions[i] * (right_degree - exterior.source_positions[j])
            + sum(len(simplex) - 1 for simplex in first_cell) * KOSZUL_DEGREES[second_koszul]
        )
        if crossing % 2:
            sign *= -1
        return (
            sign * cell_sign * koszul_sign,
            context.components[(indices[pair], 0, target_koszul)], target_cell,
        )

    result = []
    for first, first_coefficient in left.terms:
        for second, second_coefficient in right.terms:
            target = compatible(
                first.component.left_index, first.cell, first.component.koszul_summand,
                second.component.left_index, second.cell, second.component.koszul_summand,
            )
            if target is None:
                continue
            sign, component, target_cell = target
            basis = OuterCechBasis(
                component,
                cast(tuple[int, int, int], _sum_tuple(first.x_monomial, second.x_monomial)),
                cast(tuple[int, int, int], _sum_tuple(first.u_monomial, second.u_monomial)),
                cast(tuple[int, int], _sum_tuple(first.p_monomial, second.p_monomial)), target_cell,
            )
            if basis.total_degree != left_degree + right_degree:
                raise ValueError("the exterior vector product changed its total degree")
            result.append((basis, first_coefficient * second_coefficient * sign))
    return SparseOuterCechCochain(tuple(result))
