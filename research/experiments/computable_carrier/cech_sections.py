"""Compute bounded localized Čech complexes from explicit chart windows.

Owns:
    Finite monomial section windows on named Cox charts, exact restriction
    maps, alternating Čech differentials, and deterministic cycle,
    coboundary, and cohomology representatives.

Depends on:
    Generic exact `CochainComplex`, `LinearMap`, `VectorSpace`, and the chart
    localization primitives. This is a bounded research computation, not an
    assertion about the full infinite section spaces.

Must not:
    Treat a finite exponent window as a global-generation proof, infer physical
    Ext dimensions from a truncation, or silently extend a missing basis.

Phase 0:
    Bounded localized Čech computation is available with its cutoff recorded;
    convergence and carrier identification remain explicit gates.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import combinations, product

from onetheory.math.homological import CochainComplex, GradedVectorSpace, LinearMap, VectorSpace
from onetheory.math.numbers import Rational
from onetheory.math.sheaves import CoxChart, CoxChartCover

Monomial = tuple[int, ...]


@dataclass(frozen=True, slots=True)
class BoundedCechSections:
    """An exact bounded-localization Čech complex with visible cutoffs."""

    cover: CoxChartCover
    bound: int
    complex: CochainComplex
    section_bases: tuple[tuple[int, tuple[Monomial, ...]], ...]
    intersection_bases: tuple[tuple[tuple[int, ...], tuple[Monomial, ...]], ...]

    def __post_init__(self) -> None:
        if isinstance(self.bound, bool) or not isinstance(self.bound, int) or self.bound < 0:
            raise ValueError("Čech section bounds must be nonnegative integers")

    def sections_on(self, chart: int) -> tuple[Monomial, ...]:
        """Return the deterministic monomial basis on one chart."""

        return dict(self.section_bases)[chart]

    def sections_on_intersection(self, charts: tuple[int, ...]) -> tuple[Monomial, ...]:
        """Return the deterministic monomial basis on one intersection."""

        return dict(self.intersection_bases)[charts]

    def cohomology_data(self) -> tuple[tuple[int, int, int], ...]:
        """Return degree, cycle dimension, and coboundary dimension."""

        return tuple(
            (
                degree,
                len(self.complex.cycles(degree)),
                len(self.complex.boundaries(degree)),
            )
            for degree in self.complex.degrees
        )


def _monomial_window(chart: CoxChart, bound: int) -> tuple[Monomial, ...]:
    """Enumerate finite Laurent exponents allowed by one principal chart."""

    inverted = {chart.variables.index(variable) for variable in chart.inverted_variables}
    values = range(-bound, bound + 1)
    return tuple(
        exponent
        for exponent in product(values, repeat=chart.variable_count)
        if all(value >= 0 or index in inverted for index, value in enumerate(exponent))
    )


def _intersection_window(
    charts: Iterable[CoxChart],
    bound: int,
) -> tuple[Monomial, ...]:
    """Enumerate a finite monomial basis on a chart intersection."""

    values = tuple(charts)
    inverted = {
        values[0].variables.index(variable)
        for chart in values
        for variable in chart.inverted_variables
    }
    exponents = product(range(-bound, bound + 1), repeat=values[0].variable_count)
    return tuple(
        exponent
        for exponent in exponents
        if all(value >= 0 or index in inverted for index, value in enumerate(exponent))
    )


def bounded_cech_sections(cover: CoxChartCover, bound: int) -> BoundedCechSections:
    """Construct the exact bounded localized Čech complex."""

    if isinstance(bound, bool) or not isinstance(bound, int) or bound < 0:
        raise ValueError("Čech section bounds must be nonnegative integers")
    chart_bases = {index: _monomial_window(chart, bound)
                   for index, chart in enumerate(cover.charts)}
    simplex_bases: dict[int, dict[tuple[int, ...], tuple[Monomial, ...]]] = {}
    for degree in range(len(cover.charts)):
        simplex_bases[degree] = {
            simplex: _intersection_window(
                (cover.charts[index] for index in simplex),
                bound,
            )
            for simplex in combinations(range(len(cover.charts)), degree + 1)
        }
    spaces = {
        degree: VectorSpace(
            f"bounded Cech^{degree}",
            tuple(
                f"{simplex}:{monomial}"
                for simplex, basis in simplex_bases[degree].items()
                for monomial in basis
            ),
            Rational,
        )
        for degree in range(len(cover.charts))
    }
    graded = GradedVectorSpace("bounded localized Cech", spaces)
    differentials: dict[int, LinearMap] = {}
    for degree in range(len(cover.charts) - 1):
        source = tuple(simplex_bases[degree].items())
        target = tuple(simplex_bases[degree + 1].items())
        source_offsets: dict[tuple[int, ...], int] = {}
        offset = 0
        for simplex, basis in source:
            source_offsets[simplex] = offset
            offset += len(basis)
        target_offsets: dict[tuple[int, ...], int] = {}
        offset = 0
        for simplex, basis in target:
            target_offsets[simplex] = offset
            offset += len(basis)
        source_columns = spaces[degree].dimension
        rows = [[Rational(0) for _ in range(source_columns)]
                for _ in range(spaces[degree + 1].dimension)]
        for target_simplex, target_basis in target:
            for omitted in range(len(target_simplex)):
                source_simplex = target_simplex[:omitted] + target_simplex[omitted + 1:]
                sign = Rational(1 if omitted % 2 == 0 else -1)
                source_basis = dict(source)[source_simplex]
                source_index = {monomial: index for index, monomial in enumerate(source_basis)}
                for target_index, monomial in enumerate(target_basis):
                    if monomial not in source_index:
                        continue
                    rows[target_offsets[target_simplex] + target_index][
                        source_offsets[source_simplex] + source_index[monomial]
                    ] += sign
        differentials[degree] = LinearMap(
            spaces[degree],
            spaces[degree + 1],
            rows,
        )
    complex_ = CochainComplex(graded, differentials)
    section_records = tuple(sorted((index, basis) for index, basis in chart_bases.items()))
    intersection_records = tuple(sorted(
        (simplex, basis)
        for degree in range(1, len(cover.charts))
        for simplex, basis in simplex_bases[degree].items()
    ))
    return BoundedCechSections(
        cover,
        bound,
        complex_,
        section_records,
        intersection_records,
    )


__all__ = ["BoundedCechSections", "bounded_cech_sections"]
