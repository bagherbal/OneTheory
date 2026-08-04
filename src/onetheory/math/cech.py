"""Exact finite Čech complexes for named chart covers.

Owns:
    Ordered simplex bases, alternating restriction incidence maps for constant
    finite coefficient spaces, exact cochain complexes, and cohomology bases.

Depends on:
    `onetheory.math.homological` for typed exact cochain complexes and
    `onetheory.math.numbers` through its vector-space implementation.

Must not:
    Pretend constant coefficients are sheaf sections, choose a geometric Cox
    cover, infer bundle cohomology, or attach physical meanings to dimensions.

Phase 0:
    The generic Čech incidence engine is implemented; localized sheaf sections
    and carrier-specific restriction maps remain explicit inputs.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import combinations

from onetheory.math.homological import CochainComplex, GradedVectorSpace, LinearMap, VectorSpace
from onetheory.math.numbers import Rational


@dataclass(frozen=True, slots=True)
class CechSimplex:
    """An ordered nonempty simplex of chart indices."""

    vertices: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.vertices or tuple(sorted(self.vertices)) != self.vertices:
            raise ValueError("Čech simplices require nonempty sorted vertices")
        if len(set(self.vertices)) != len(self.vertices):
            raise ValueError("Čech simplex vertices must be distinct")


@dataclass(frozen=True, slots=True)
class ConstantCechComplex:
    """A deterministic Čech incidence complex for constant coefficients."""

    chart_names: tuple[str, ...]
    coefficient_basis: tuple[str, ...]
    complex: CochainComplex
    simplices: tuple[tuple[int, tuple[CechSimplex, ...]], ...]

    def __post_init__(self) -> None:
        if len(set(self.chart_names)) != len(self.chart_names) or not self.chart_names:
            raise ValueError("Čech complexes require uniquely named charts")
        if (
            not self.coefficient_basis
            or len(set(self.coefficient_basis)) != len(self.coefficient_basis)
        ):
            raise ValueError("Čech complexes require a named coefficient basis")

    def simplices_at(self, degree: int) -> tuple[CechSimplex, ...]:
        """Return the ordered simplices in one Čech degree."""

        return dict(self.simplices).get(degree, ())

    def cohomology_dimensions(self) -> tuple[tuple[int, int], ...]:
        """Return exact cohomology dimensions in every represented degree."""

        return tuple((degree, self.complex.cohomology_dimension(degree))
                     for degree in self.complex.degrees)


def constant_cech_complex(
    chart_names: Iterable[str],
    coefficient_basis: Iterable[str],
) -> ConstantCechComplex:
    """Build the alternating Čech incidence complex exactly."""

    charts = tuple(chart_names)
    coefficients = tuple(coefficient_basis)
    if not charts or not coefficients:
        raise ValueError("Čech complexes require nonempty chart and coefficient bases")
    simplex_data = tuple(
        (
            degree,
            tuple(
                CechSimplex(simplex)
                for simplex in combinations(range(len(charts)), degree + 1)
            ),
        )
        for degree in range(len(charts))
    )
    spaces = {
        degree: VectorSpace(
            f"Cech^{degree}",
            tuple(
                f"{simplex.vertices}:{basis}"
                for simplex in simplices
                for basis in coefficients
            ),
            Rational,
        )
        for degree, simplices in simplex_data
    }
    graded = GradedVectorSpace("constant Čech complex", spaces)
    differentials: dict[int, LinearMap] = {}
    coefficient_dimension = len(coefficients)
    for degree, simplices in simplex_data[:-1]:
        target_simplices = dict(simplex_data)[degree + 1]
        source_index = {simplex.vertices: index for index, simplex in enumerate(simplices)}
        rows = [[Rational(0) for _ in spaces[degree].basis] for _ in spaces[degree + 1].basis]
        for target_simplex_index, simplex in enumerate(target_simplices):
            for omitted in range(len(simplex.vertices)):
                source_vertices = simplex.vertices[:omitted] + simplex.vertices[omitted + 1:]
                if source_vertices not in source_index:
                    continue
                source_simplex_index = source_index[source_vertices]
                sign = Rational(1 if omitted % 2 == 0 else -1)
                for coefficient_index in range(coefficient_dimension):
                    rows[target_simplex_index * coefficient_dimension + coefficient_index][
                        source_simplex_index * coefficient_dimension + coefficient_index
                    ] = sign
        differentials[degree] = LinearMap(
            spaces[degree],
            spaces[degree + 1],
            rows,
        )
    complex_ = CochainComplex(graded, differentials)
    return ConstantCechComplex(charts, coefficients, complex_, simplex_data)


__all__ = ["CechSimplex", "ConstantCechComplex", "constant_cech_complex"]
