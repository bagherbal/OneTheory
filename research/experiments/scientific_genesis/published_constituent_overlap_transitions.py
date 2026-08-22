"""Glue the selected affine constituent presentations on all overlaps.

Owns:
    Parent-zero Čech gauges, hypersurface-residual relation comparisons,
    graded middle-generator transitions, inverse checks, and triple cocycles.

Depends on:
    Full selected mixed cocycles, exact affine pushout presentations, the
    cubic-pencil atlas, and homogeneous Laurent matrix arithmetic.

Must not:
    Replace equality modulo the hypersurface by ambient equality, infer deck
    linearization from chart gluing, or identify the outer rank-four bundle.

Phase 0:
    Research-only global cover presentation of W1/W2; descent remains open.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from itertools import permutations
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.math.sheaves import LaurentMatrix, LaurentPolynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pencil import BlowupChart, tier_a_pencil_model

from .published_constituent_chart_presentations import (
    published_constituent_chart_presentations,
)
from .published_constituent_full_cech import (
    PublishedConstituentFullCech,
    published_constituent_full_cech,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/published_constituent_overlap_transitions.json"
)


def _zero() -> LaurentPolynomial:
    """Return zero in the common five-coordinate Laurent ring."""

    return LaurentPolynomial.zero(5, scalar_type=Eisenstein)


def _one() -> LaurentPolynomial:
    """Return one in the common five-coordinate Laurent ring."""

    return LaurentPolynomial.one(5, scalar_type=Eisenstein)


def _laurent_term(
    base_monomial: tuple[int, int, int],
    fiber_monomial: tuple[int, int],
    coefficient: Eisenstein,
) -> LaurentPolynomial:
    """Embed one full-cover term in the common homogeneous Laurent ring."""

    return LaurentPolynomial(
        (((*base_monomial, *fiber_monomial), coefficient),),
        variable_count=5,
        scalar_type=Eisenstein,
    )


def _embed_polynomial(polynomial: Polynomial) -> LaurentPolynomial:
    """Embed one homogeneous P2 polynomial with zero fiber exponents."""

    return LaurentPolynomial(
        tuple(((*exponents, 0, 0), coefficient) for exponents, coefficient in polynomial.terms),
        variable_count=5,
        scalar_type=Eisenstein,
    )


def _fiber_pivot(chart: BlowupChart) -> int:
    """Return zero for the mu chart and one for the nu chart."""

    return 0 if chart.fiber_chart == "mu" else 1


def _chart_cell(chart: BlowupChart) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return the singleton product-cover cell of one affine chart."""

    return (chart.base_pivot,), (_fiber_pivot(chart),)


def _adjacent(source: BlowupChart, target: BlowupChart) -> bool:
    """Return whether exactly one projective-cover factor changes."""

    return (
        int(source.base_pivot != target.base_pivot)
        + int(source.fiber_chart != target.fiber_chart)
        == 1
    )


def _edge_cell(
    source: BlowupChart,
    target: BlowupChart,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return the sorted Čech one-cell of an adjacent ordered pair."""

    if not _adjacent(source, target):
        raise ValueError("a direct Čech gauge requires adjacent product charts")
    base = (
        tuple(sorted((source.base_pivot, target.base_pivot)))
        if source.base_pivot != target.base_pivot
        else (source.base_pivot,)
    )
    source_fiber = _fiber_pivot(source)
    target_fiber = _fiber_pivot(target)
    fiber = (
        tuple(sorted((source_fiber, target_fiber)))
        if source_fiber != target_fiber
        else (source_fiber,)
    )
    return base, fiber


def _orientation(source: BlowupChart, target: BlowupChart) -> int:
    """Return the sign from the sorted Čech edge to the ordered overlap."""

    if source.base_pivot != target.base_pivot:
        return 1 if source.base_pivot < target.base_pivot else -1
    return 1 if _fiber_pivot(source) < _fiber_pivot(target) else -1


def _component_vector(
    result: PublishedConstituentFullCech,
    parent_degree: int,
    koszul_degree: int,
    cell: tuple[tuple[int, ...], tuple[int, ...]],
    count: int,
) -> tuple[LaurentPolynomial, ...]:
    """Extract one component vector on a fixed product-cover cell."""

    values = []
    for bundle_index in range(count):
        value = _zero()
        for basis, coefficient in result.representative.terms:
            if (
                basis.component.parent_degree == parent_degree
                and basis.component.bundle_index == bundle_index
                and basis.component.koszul_degree == koszul_degree
                and basis.cell == cell
            ):
                value += _laurent_term(
                    basis.base_monomial,
                    basis.fiber_monomial,
                    coefficient,
                )
        values.append(value)
    return tuple(values)


def _extension_vector(
    result: PublishedConstituentFullCech,
    chart: BlowupChart,
) -> tuple[LaurentPolynomial, ...]:
    """Return the homogeneous parent-one pushout map on one chart."""

    count = len(result.alignment.action.derived.extension.syzygy_bundles)
    return _component_vector(result, 1, 0, _chart_cell(chart), count)


def _adjacent_data(
    result: PublishedConstituentFullCech,
    source: BlowupChart,
    target: BlowupChart,
) -> tuple[tuple[LaurentPolynomial, ...], tuple[LaurentPolynomial, ...]]:
    """Return oriented parent-zero gauge and hypersurface homotopy vectors."""

    sign = _orientation(source, target)
    cell = _edge_cell(source, target)
    extension = result.alignment.action.derived.extension
    gauge = _component_vector(
        result,
        0,
        0,
        cell,
        len(extension.generator_bundles),
    )
    homotopy = _component_vector(
        result,
        1,
        1,
        cell,
        len(extension.syzygy_bundles),
    )
    return (
        tuple(value.scale(sign) for value in gauge),
        tuple(value.scale(sign) for value in homotopy),
    )


def _add_vectors(
    left: tuple[LaurentPolynomial, ...],
    right: tuple[LaurentPolynomial, ...],
) -> tuple[LaurentPolynomial, ...]:
    """Add two equally typed Laurent vectors."""

    if len(left) != len(right):
        raise ValueError("overlap gauge vectors have incompatible lengths")
    return tuple(a + b for a, b in zip(left, right, strict=True))


def _zero_vector(length: int) -> tuple[LaurentPolynomial, ...]:
    """Return one typed zero Laurent vector."""

    return tuple(_zero() for _ in range(length))


def _overlap_data(
    result: PublishedConstituentFullCech,
    source: BlowupChart,
    target: BlowupChart,
    charts: dict[tuple[int, str], BlowupChart],
) -> tuple[tuple[LaurentPolynomial, ...], tuple[LaurentPolynomial, ...], bool]:
    """Compose adjacent gauges and certify rectangle path independence."""

    extension = result.alignment.action.derived.extension
    if source == target:
        return (
            _zero_vector(len(extension.generator_bundles)),
            _zero_vector(len(extension.syzygy_bundles)),
            True,
        )
    if _adjacent(source, target):
        gauge, homotopy = _adjacent_data(result, source, target)
        return gauge, homotopy, True
    base_first = charts[(target.base_pivot, source.fiber_chart)]
    fiber_first = charts[(source.base_pivot, target.fiber_chart)]
    first_left = _adjacent_data(result, source, base_first)
    first_right = _adjacent_data(result, base_first, target)
    second_left = _adjacent_data(result, source, fiber_first)
    second_right = _adjacent_data(result, fiber_first, target)
    first = (
        _add_vectors(first_left[0], first_right[0]),
        _add_vectors(first_left[1], first_right[1]),
    )
    second = (
        _add_vectors(second_left[0], second_right[0]),
        _add_vectors(second_left[1], second_right[1]),
    )
    return first[0], first[1], first == second


def _hypersurface_equation(
    result: PublishedConstituentFullCech,
) -> LaurentPolynomial:
    """Return the homogeneous equation of the selected dP9 factor."""

    cox = schoen_geometry().cover.cox
    factor = result.alignment.action.derived.extension.surface_factor
    terms = (
        (cox.cubic_f, (1, 0), Eisenstein(1)),
        (cox.cubic_g, (0, 1), Eisenstein(1)),
    ) if factor == 1 else (
        (cox.cubic_f, (0, 1), Eisenstein(2)),
        (cox.cubic_g, (1, 0), Eisenstein(1)),
    )
    equation = _zero()
    for polynomial, fiber_monomial, prefactor in terms:
        for base_monomial, coefficient in polynomial.terms:
            equation += _laurent_term(
                cast(tuple[int, int, int], base_monomial),
                fiber_monomial,
                cast(Eisenstein, coefficient) * prefactor,
            )
    return equation


def _transition(gauge: tuple[LaurentPolynomial, ...]) -> LaurentMatrix:
    """Return the unipotent middle-generator change induced by one gauge."""

    size = len(gauge) + 1
    rows = []
    for row in range(size):
        values = []
        for column in range(size):
            if row < size - 1:
                values.append(_one() if row == column else _zero())
            elif column < size - 1:
                values.append(gauge[column])
            else:
                values.append(_one())
        rows.append(tuple(values))
    return LaurentMatrix(tuple(rows))


def _determinant(matrix: LaurentMatrix) -> LaurentPolynomial:
    """Return one exact Laurent determinant by the Leibniz formula."""

    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("determinants require square Laurent matrices")
    value = _zero()
    for permutation in permutations(range(matrix.shape[0])):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(len(permutation))
            for right in range(left + 1, len(permutation))
        )
        term = _one().scale(-1 if inversions % 2 else 1)
        for row, column in enumerate(permutation):
            term *= matrix.rows[row][column]
        value += term
    return value


def _relation_columns(
    result: PublishedConstituentFullCech,
    chart: BlowupChart,
) -> LaurentMatrix:
    """Return the homogeneous pushout relation as middle-by-source columns."""

    extension = result.alignment.action.derived.extension
    extension_map = _extension_vector(result, chart)
    rows = [
        tuple(_embed_polynomial(entry) for entry in matrix_row)
        for matrix_row in extension.scheme.resolution.matrix
    ]
    rows.append(tuple(-value for value in extension_map))
    return LaurentMatrix(tuple(rows))


@dataclass(frozen=True, slots=True)
class ConstituentOverlapTransition:
    """One ordered overlap comparison of selected affine presentations."""

    constituent: str
    source: BlowupChart
    target: BlowupChart
    gauge: tuple[LaurentPolynomial, ...]
    hypersurface_homotopy: tuple[LaurentPolynomial, ...]
    transition: LaurentMatrix
    rectangle_path_independent: bool
    relation_compatible_mod_hypersurface: bool

    def as_record(self) -> dict[str, object]:
        """Serialize one overlap gauge and exact gluing gates."""

        def vector_record(
            vector: tuple[LaurentPolynomial, ...],
        ) -> list[list[dict[str, object]]]:
            return [
                [
                    {"exponents": list(exponents), "coefficient": str(coefficient)}
                    for exponents, coefficient in item.terms
                ]
                for item in vector
            ]

        return {
            "constituent": self.constituent,
            "source": self.source.name,
            "target": self.target.name,
            "gauge": vector_record(self.gauge),
            "hypersurface_homotopy": vector_record(self.hypersurface_homotopy),
            "transition_determinant_one": _determinant(self.transition) == _one(),
            "rectangle_path_independent": self.rectangle_path_independent,
            "relation_compatible_mod_hypersurface": (
                self.relation_compatible_mod_hypersurface
            ),
        }


@dataclass(frozen=True, slots=True)
class PublishedConstituentOverlapAtlas:
    """All ordered transitions for one selected constituent presentation."""

    constituent: str
    transitions: tuple[ConstituentOverlapTransition, ...]

    @property
    def all_determinant_one(self) -> bool:
        """Return whether every middle-generator transition has determinant one."""

        return all(_determinant(item.transition) == _one() for item in self.transitions)

    @property
    def all_relations_compatible(self) -> bool:
        """Return every hypersurface-residual presentation comparison gate."""

        return all(
            item.relation_compatible_mod_hypersurface
            and item.rectangle_path_independent
            for item in self.transitions
        )

    @property
    def inverse_consistent(self) -> bool:
        """Return exact inverse identities on all ordered overlaps."""

        by_pair = {
            (item.source.name, item.target.name): item.transition
            for item in self.transitions
        }
        return all(
            item.transition.compose(by_pair[(item.target.name, item.source.name)]).is_identity()
            for item in self.transitions
        )

    @property
    def cocycle_consistent(self) -> bool:
        """Return every ordered triple-overlap transition identity."""

        by_pair = {
            (item.source.name, item.target.name): item.transition
            for item in self.transitions
        }
        names = tuple(sorted({item.source.name for item in self.transitions}))
        return all(
            by_pair[(source, middle)].compose(by_pair[(middle, target)])
            == by_pair[(source, target)]
            for source in names
            for middle in names
            for target in names
            if len({source, middle, target}) == 3
        )

    @property
    def exact(self) -> bool:
        """Return all presentation-gluing identities."""

        return (
            len(self.transitions) == 30
            and self.all_determinant_one
            and self.all_relations_compatible
            and self.inverse_consistent
            and self.cocycle_consistent
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the global cover atlas and retain the descent boundary."""

        return {
            "constituent": self.constituent,
            "transition_count": len(self.transitions),
            "transitions": [item.as_record() for item in self.transitions],
            "all_determinant_one": self.all_determinant_one,
            "all_relations_compatible": self.all_relations_compatible,
            "inverse_consistent": self.inverse_consistent,
            "cocycle_consistent": self.cocycle_consistent,
            "exact": self.exact,
            "deck_linearization_constructed": False,
        }


def _relation_compatible(
    result: PublishedConstituentFullCech,
    source: BlowupChart,
    target: BlowupChart,
    transition: LaurentMatrix,
    homotopy: tuple[LaurentPolynomial, ...],
) -> bool:
    """Check relation comparison with the exact hypersurface residual."""

    transformed = transition.compose(_relation_columns(result, target))
    source_relation = _relation_columns(result, source)
    equation = _hypersurface_equation(result)
    expected_rows = list(source_relation.rows)
    expected_rows[-1] = tuple(
        value + equation * correction
        for value, correction in zip(
            expected_rows[-1],
            homotopy,
            strict=True,
        )
    )
    return transformed == LaurentMatrix(tuple(expected_rows))


def _atlas(result: PublishedConstituentFullCech) -> PublishedConstituentOverlapAtlas:
    """Construct all ordered overlap transitions for one selected constituent."""

    charts_tuple = tier_a_pencil_model().blowup_atlas.charts
    charts = {(chart.base_pivot, chart.fiber_chart): chart for chart in charts_tuple}
    records = []
    for source in charts_tuple:
        for target in charts_tuple:
            if source == target:
                continue
            gauge, homotopy, path_independent = _overlap_data(
                result,
                source,
                target,
                charts,
            )
            transition = _transition(gauge)
            records.append(
                ConstituentOverlapTransition(
                    result.alignment.action.derived.extension.scheme.name,
                    source,
                    target,
                    gauge,
                    homotopy,
                    transition,
                    path_independent,
                    _relation_compatible(
                        result,
                        source,
                        target,
                        transition,
                        homotopy,
                    ),
                )
            )
    atlas = PublishedConstituentOverlapAtlas(
        result.alignment.action.derived.extension.scheme.name,
        tuple(records),
    )
    if not atlas.exact:
        raise ValueError("a selected constituent overlap atlas failed")
    return atlas


@cache
def published_constituent_overlap_atlases(
) -> tuple[PublishedConstituentOverlapAtlas, ...]:
    """Glue both selected constituent presentations on the six-chart cover."""

    presentations = published_constituent_chart_presentations()
    if len(presentations) != 12 or not all(item.exact for item in presentations):
        raise ValueError("overlap gluing requires all affine presentations")
    return tuple(_atlas(result) for result in published_constituent_full_cech())


def write_published_constituent_overlap_atlases(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed global constituent cover atlases."""

    atlases = published_constituent_overlap_atlases()
    payload: dict[str, object] = {
        "schema": "published-constituent-overlap-transitions-v1",
        "atlases": [atlas.as_record() for atlas in atlases],
        "all_global_cover_presentations_exact": all(atlas.exact for atlas in atlases),
        "selected_mixed_cocycles_used": True,
        "deck_linearizations_constructed": False,
        "next_required_object": (
            "exact P/T comparison maps on the two global constituent atlases, "
            "followed by the mixed-cone Schoen outer transfer"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate both selected global constituent cover atlases."""

    payload = write_published_constituent_overlap_atlases()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "all_global_cover_presentations_exact: "
        f"{payload['all_global_cover_presentations_exact']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ConstituentOverlapTransition",
    "PublishedConstituentOverlapAtlas",
    "published_constituent_overlap_atlases",
]
