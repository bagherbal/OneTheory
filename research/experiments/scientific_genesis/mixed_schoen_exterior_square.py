"""Form a signed exterior square of a two-term mixed Schoen resolution.

Owns:
    The graded exterior monomial basis, induced resolution arrows, and
    ordered reciprocal covector products, and the derived even-object
    rank-one tensor correction in that basis.

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

from onetheory.math.linear import Matrix
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
from .mixed_schoen_common_dga import _koszul_cup, _sum_tuple, mixed_outer_cup
from .mixed_schoen_cup_homotopy import mixed_scalar_cup_homotopy
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import (
    MixedSchoenComplex,
    MixedSchoenUnit,
    _cell_cup,
    mixed_schoen_unit,
)


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


def graded_exterior_frame(exterior: MixedExteriorSquare, frame: Matrix) -> Matrix:
    """Apply an invertible homogeneous frame to the declared ordinary basis.

    Expand each product of its two actual columns and canonically reorder
    using the internal Koszul sign. Odd diagonals are ordinary symmetric
    monomials: their off-diagonal coefficients add twice. This is a frame
    transformation only, not a claim about an arbitrary twisted tensor cup.
    """

    size = len(exterior.source_positions)
    if frame.row_count != size or frame.column_count != size or frame.rank() != size:
        raise ValueError("the exterior frame needs an invertible source-size matrix")
    if frame.scalar_type is not Eisenstein:
        raise TypeError("the mixed exterior frame requires exact Eisenstein coefficients")
    columns = []
    for source in range(size):
        column = []
        for target in range(size):
            value = Eisenstein.coerce(frame[target][source])
            if value.is_zero():
                continue
            if (
                exterior.source_positions[target] != exterior.source_positions[source]
                or exterior.source_lines[target] != exterior.source_lines[source]
            ):
                raise ValueError("the source frame does not preserve homogeneous objects")
            column.append((target, value))
        columns.append(tuple(column))
    indices = {pair: index for index, pair in enumerate(exterior.pairs)}
    rows = [[Eisenstein(0) for _ in exterior.pairs] for _ in exterior.pairs]
    for index, (first, second) in enumerate(exterior.pairs):
        for a, first_value in columns[first]:
            for b, second_value in columns[second]:
                ordered = _ordered_pair(exterior.source_positions, a, b)
                if ordered is not None:
                    pair, sign = ordered
                    rows[indices[pair]][index] += first_value * second_value * sign
    return Matrix(tuple(tuple(row) for row in rows), scalar_type=Eisenstein)


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


def _even_twisting_coefficients(
    source: MixedSchoenComplex,
) -> tuple[int, tuple[tuple[int, SparseOuterCechCochain], ...]]:
    """Require a single even target and closed scalar even-source arrows."""

    targets = {term.target for term in source.extension_terms}
    if len(targets) != 1:
        raise ValueError("the even tensor correction requires one actual mixed-arrow target")
    target = next(iter(targets))
    if source.objects[target].position != 0:
        raise ValueError("the even tensor correction requires an even rank-one target")
    if any(term.source == target for term in source.extension_terms):
        raise ValueError(
            "the even tensor correction requires a nilpotent target with no self-arrow"
        )
    result = []
    for index, obj in enumerate(source.objects):
        if obj.position != 0:
            continue
        terms = []
        degree = cast(tuple[int, int, int], tuple(
            a - b for a, b in zip(source.objects[target].line_degree, obj.line_degree, strict=True)
        ))
        for term in source.extension_terms:
            if term.source != index:
                continue
            if term.parent_degree != 0:
                raise ValueError("an even twisting coefficient has an unsupported grading")
            koszul = term.koszul_summand
            # The mixed differential stores parent-zero terms with a
            # minus sign in its left action. Alpha here is the actual
            # action coefficient, not the stored extension coefficient.
            terms.append((OuterCechBasis(
                OuterCechComponent(0, 0, 0, degree, koszul),
                term.x_monomial, term.u_monomial, term.p_monomial, term.cell,
            ), term.coefficient * -1))
        if not terms:
            continue
        coefficient = SparseOuterCechCochain(tuple(terms))
        line = MixedSchoenUnit(
            "declared twisting-coefficient line", 0, degree,
            (MixedConstituentObject("twisting-coefficient line", 0, degree),),
        )
        if (
            any(basis.total_degree != 1 for basis, _ in coefficient.terms)
            or not _MixedContraction(line, mixed_schoen_unit()).differential(coefficient).is_zero()
        ):
            raise ValueError("an even twisting coefficient is not a full scalar degree-one cycle")
        result.append((index, coefficient))
    return target, tuple(result)


def even_rank_one_vector_wedge(
    left: SparseOuterCechCochain,
    right: SparseOuterCechCochain,
    source: MixedSchoenComplex,
    exterior: MixedExteriorSquare,
    context: _MixedContraction,
    left_degree: int,
    right_degree: int,
) -> SparseOuterCechCochain:
    """Correct the raw wedge on the even-object rank-one reachable sector.

    With closed scalar arrows alpha_j into one even A, the raw Leibniz
    defect is (alpha_j cup u_i - (-1)^|u| u_i cup alpha_j) cup v_j,
    in e_i wedge A. Subtract H(alpha_j,u_i) cup v_j in that slot.
    The scalar homotopy cancels this defect; terms quadratic in alpha
    land in A wedge A and vanish. Ordinary local degree-zero products
    are unchanged. Odd-object inputs are rejected: no syzygy comparison,
    outer-cone product, or physical Yukawa is certified by this function.
    """

    if exterior != mixed_exterior_square(source):
        raise ValueError("the even tensor correction needs the actual source exterior basis")
    raw = resolution_vector_wedge(left, right, exterior, context, left_degree, right_degree)
    if any(
        basis.component.object_degree != 0
        for cochain in (left, right) for basis, _ in cochain.terms
    ):
        raise ValueError("the even tensor correction cannot omit odd-object comparison terms")
    target, coefficients = _even_twisting_coefficients(source)

    def scalar_components(cochain: SparseOuterCechCochain) -> dict[int, SparseOuterCechCochain]:
        groups: dict[int, list[tuple[OuterCechBasis, Eisenstein]]] = {}
        for basis, value in cochain.terms:
            index = basis.component.left_index
            groups.setdefault(index, []).append((OuterCechBasis(
                replace(basis.component, left_index=0),
                basis.x_monomial, basis.u_monomial, basis.p_monomial, basis.cell,
            ), value))
        return {index: SparseOuterCechCochain(tuple(terms)) for index, terms in groups.items()}

    a = scalar_components(left)
    b = scalar_components(right)
    indices = {pair: index for index, pair in enumerate(exterior.pairs)}
    correction = []
    for second, alpha in coefficients:
        if second not in b:
            continue
        for first, u in a.items():
            ordered = _ordered_pair(exterior.source_positions, first, target)
            if ordered is None:
                continue
            pair, sign = ordered
            value = mixed_outer_cup(mixed_scalar_cup_homotopy(alpha, u), b[second])
            for basis, coefficient in value.terms:
                component = context.components[(indices[pair], 0, basis.component.koszul_summand)]
                if component.line_degree != basis.component.line_degree:
                    raise ValueError("the tensor homotopy changed its actual exterior line")
                correction.append((OuterCechBasis(
                    component, basis.x_monomial, basis.u_monomial, basis.p_monomial, basis.cell,
                ), coefficient * sign))
    return raw + SparseOuterCechCochain(tuple(correction)).scale(-1)
