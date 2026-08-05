"""Construct the exact polynomial Hom complex of the Tier A presentations.

Owns:
    The three-term derived Hom complex formed from two explicit rank-two
    free presentations, including its basis shifts, polynomial differentials,
    and exact square-zero certificate.

Depends on:
    Tier A polynomial pushout presentations and reusable exact polynomial
    free-module and map primitives.

Must not:
    Call the presentation Hom complex a global Schoen Ext complex, infer
    invariant classes from dimensions, or silently supply the missing dP9
    sheafification, fiber cohomology, or deck action.

Phase 0:
    The presentation-level derived Hom chain is executable; global
    hypercohomology and quotient descent remain explicit gates.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.polynomials import (
    PolynomialFreeModule,
    PolynomialMap,
    PolynomialMatrix,
)

from .serre_pushout import SerrePushoutCandidate, tier_a_serre_pushouts


@dataclass(frozen=True, slots=True)
class PolynomialHomComplex:
    """A three-term polynomial derived Hom complex with visible bases."""

    left: SerrePushoutCandidate
    right: SerrePushoutCandidate
    terms: tuple[tuple[int, PolynomialFreeModule], ...]
    differentials: tuple[tuple[int, PolynomialMap], ...]

    def __post_init__(self) -> None:
        degrees = tuple(degree for degree, _ in self.terms)
        if degrees != (-1, 0, 1):
            raise ValueError("presentation Hom terms must use degrees -1, 0, and 1")
        if tuple(degree for degree, _ in self.differentials) != (-1, 0):
            raise ValueError("presentation Hom differentials must start at -1 and 0")
        term_map = dict(self.terms)
        for degree, differential in self.differentials:
            if differential.domain != term_map[degree]:
                raise ValueError("Hom differential domain does not match its term")
            if differential.codomain != term_map[degree + 1]:
                raise ValueError("Hom differential codomain does not match its term")
        if not self.differential(0).compose(self.differential(-1)).is_zero():
            raise ValueError("presentation Hom differentials must square to zero")
        if not all(self._map_is_homogeneous(map_) for _, map_ in self.differentials):
            raise ValueError("presentation Hom maps must preserve declared shifts")

    def term(self, degree: int) -> PolynomialFreeModule:
        """Return one explicitly based Hom term."""

        return dict(self.terms)[degree]

    def differential(self, degree: int) -> PolynomialMap:
        """Return the differential leaving one cochain degree."""

        return dict(self.differentials)[degree]

    @property
    def squared_zero(self) -> bool:
        """Return the exact polynomial square-zero certificate."""

        return self.differential(0).compose(self.differential(-1)).is_zero()

    @property
    def homogeneous(self) -> bool:
        """Return whether both polynomial maps preserve every basis shift."""

        return all(self._map_is_homogeneous(map_) for _, map_ in self.differentials)

    @staticmethod
    def _map_is_homogeneous(map_: PolynomialMap) -> bool:
        """Check degree zero for every nonzero matrix entry."""

        for row, target_shift in enumerate(map_.codomain.shifts):
            for column, source_shift in enumerate(map_.domain.shifts):
                entry = map_.matrix.rows[row][column]
                if not entry.is_zero() and entry.degree != source_shift[0] - target_shift[0]:
                    return False
        return True

    def as_record(self) -> dict[str, object]:
        """Serialize exact term shapes and differential certificates."""

        return {
            "left_scheme": self.left.scheme.name,
            "right_scheme": self.right.scheme.name,
            "term_ranks": [[degree, term.rank] for degree, term in self.terms],
            "term_shifts": [
                [degree, [list(shift) for shift in term.shifts]]
                for degree, term in self.terms
            ],
            "differential_shapes": [
                [degree, list(map_.matrix.shape)]
                for degree, map_ in self.differentials
            ],
            "squared_zero": self.squared_zero,
            "homogeneous": self.homogeneous,
            "status": (
                "exact presentation-level derived Hom complex; global dP9 "
                "hypercohomology and quotient descent remain unresolved"
            ),
        }


def _free_module(
    name: str,
    labels: tuple[str, ...],
    shifts: tuple[int, ...],
    variable_count: int,
    scalar_type,
) -> PolynomialFreeModule:
    """Create one shifted free module from integer presentation shifts."""

    return PolynomialFreeModule(
        name,
        labels,
        tuple((shift,) * variable_count for shift in shifts),
        variable_count,
        scalar_type,
    )


def _presentation_map(
    candidate: SerrePushoutCandidate,
    prefix: str,
) -> PolynomialMap:
    """Return the transposed relation map from its shifted modules."""

    relation = candidate.relation
    variable_count = relation.variable_count
    source = _free_module(
        f"{prefix}:F1",
        tuple(f"f1:{index}" for index in range(len(candidate.source_shifts))),
        candidate.source_shifts,
        variable_count,
        relation.scalar_type,
    )
    target = _free_module(
        f"{prefix}:F0",
        tuple(f"f0:{index}" for index in range(len(candidate.target_shifts))),
        candidate.target_shifts,
        variable_count,
        relation.scalar_type,
    )
    matrix = PolynomialMatrix(
        tuple(
            tuple(relation.rows[column][row] for column in range(relation.shape[0]))
            for row in range(relation.shape[1])
        )
    )
    return PolynomialMap(source, target, matrix)


def _hom_module(
    name: str,
    target: PolynomialFreeModule,
    source: PolynomialFreeModule,
) -> PolynomialFreeModule:
    """Build the shifted free module of maps from source to target."""

    labels = tuple(
        f"{target.basis[target_index]}<-{source.basis[source_index]}"
        for target_index in range(target.rank)
        for source_index in range(source.rank)
    )
    shifts = tuple(
        target.shifts[target_index][0] - source.shifts[source_index][0]
        for target_index in range(target.rank)
        for source_index in range(source.rank)
    )
    return _free_module(name, labels, shifts, target.variable_count, target.scalar_type)


def _left_composition(
    left_map: PolynomialMap,
    input_hom: PolynomialFreeModule,
    output_hom: PolynomialFreeModule,
) -> PolynomialMap:
    """Compose Hom maps on the target side."""

    rows = []
    source_rank = input_hom.rank // left_map.domain.rank
    for target_index in range(left_map.codomain.rank):
        for source_index in range(source_rank):
            row = []
            for input_target in range(left_map.domain.rank):
                for input_source in range(source_rank):
                    row.append(
                        left_map.matrix.rows[target_index][input_target]
                        if input_source == source_index
                        else left_map.matrix.rows[target_index][input_target].scale(0)
                    )
            rows.append(tuple(row))
    return PolynomialMap(
        input_hom,
        output_hom,
        PolynomialMatrix(rows),
    )


def _right_composition(
    right_map: PolynomialMap,
    input_hom: PolynomialFreeModule,
    output_hom: PolynomialFreeModule,
) -> PolynomialMap:
    """Compose Hom maps on the source side."""

    rows = []
    target_rank = input_hom.rank // right_map.codomain.rank
    for target_index in range(target_rank):
        for output_source in range(right_map.domain.rank):
            row = []
            for input_target in range(target_rank):
                for input_source in range(right_map.codomain.rank):
                    row.append(
                        right_map.matrix.rows[input_source][output_source]
                        if input_target == target_index
                        else right_map.matrix.rows[input_source][output_source].scale(0)
                    )
            rows.append(tuple(row))
    return PolynomialMap(
        input_hom,
        output_hom,
        PolynomialMatrix(rows),
    )


def _vertical_stack(
    upper: PolynomialMap,
    lower: PolynomialMap,
    domain: PolynomialFreeModule,
    codomain: PolynomialFreeModule,
) -> PolynomialMap:
    """Stack two maps with one common domain."""

    if upper.domain != domain or lower.domain != domain:
        raise ValueError("stacked maps require one common domain")
    return PolynomialMap(
        domain,
        codomain,
        PolynomialMatrix((*upper.matrix.rows, *lower.matrix.rows)),
    )


def _horizontal_concat(
    left: PolynomialMap,
    right: PolynomialMap,
    domain: PolynomialFreeModule,
    codomain: PolynomialFreeModule,
) -> PolynomialMap:
    """Concatenate maps with one common codomain."""

    if left.codomain != codomain or right.codomain != codomain:
        raise ValueError("concatenated maps require one common codomain")
    rows = tuple(
        tuple(left_row) + tuple(right_row)
        for left_row, right_row in zip(
            left.matrix.rows,
            right.matrix.rows,
            strict=True,
        )
    )
    return PolynomialMap(
        domain,
        codomain,
        PolynomialMatrix(rows),
    )


def polynomial_hom_complex(
    left: SerrePushoutCandidate,
    right: SerrePushoutCandidate,
) -> PolynomialHomComplex:
    """Build ``Hom(right presentation, left presentation)`` exactly."""

    left_map = _presentation_map(left, "left")
    right_map = _presentation_map(right, "right")
    c_minus = _hom_module("Hom^-1", left_map.domain, right_map.codomain)
    c_g = _hom_module("Hom^0:g", left_map.codomain, right_map.codomain)
    c_h = _hom_module("Hom^0:h", left_map.domain, right_map.domain)
    c_zero = c_g.direct_sum(c_h, "Hom^0")
    c_plus = _hom_module("Hom^1", left_map.codomain, right_map.domain)

    left_on_cminus = _left_composition(left_map, c_minus, c_g)
    right_on_cminus = _right_composition(right_map, c_minus, c_h)
    differential_minus = _vertical_stack(
        left_on_cminus,
        right_on_cminus,
        c_minus,
        c_zero,
    )
    right_on_g = _right_composition(right_map, c_g, c_plus)
    left_on_h = _left_composition(left_map, c_h, c_plus).scale(-1)
    differential_zero = _horizontal_concat(
        right_on_g,
        left_on_h,
        c_zero,
        c_plus,
    )
    return PolynomialHomComplex(
        left,
        right,
        ((-1, c_minus), (0, c_zero), (1, c_plus)),
        ((-1, differential_minus), (0, differential_zero)),
    )


def tier_a_polynomial_hom_complex() -> PolynomialHomComplex:
    """Build the Tier A I3/I6 presentation Hom complex."""

    left, right = tier_a_serre_pushouts()
    return polynomial_hom_complex(left, right)


__all__ = ["PolynomialHomComplex", "polynomial_hom_complex", "tier_a_polynomial_hom_complex"]
