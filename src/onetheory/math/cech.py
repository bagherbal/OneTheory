"""Exact finite Čech complexes for named chart covers.

Owns:
    Ordered simplex bases, alternating restriction incidence maps for constant
    finite coefficient spaces, typed restricted-section Čech complexes, exact
    cochain complexes, and cohomology bases.

Depends on:
    `onetheory.math.homological` for typed exact cochain complexes and
    `onetheory.math.numbers` through its vector-space implementation.

Must not:
    Pretend constant coefficients are sheaf sections, choose a geometric Cox
    cover, infer bundle cohomology, or attach physical meanings to dimensions.

Phase 0:
    The generic Čech incidence and typed restriction engines are implemented;
    localized section spaces and carrier-specific maps remain explicit inputs.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
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


@dataclass(frozen=True, slots=True)
class RestrictedCechComplex:
    """A Čech complex assembled from explicitly typed simplex restrictions."""

    chart_names: tuple[str, ...]
    section_spaces: tuple[tuple[tuple[int, ...], VectorSpace], ...]
    restrictions: tuple[
        tuple[tuple[int, ...], tuple[int, ...], LinearMap], ...
    ]
    complex: CochainComplex

    def __post_init__(self) -> None:
        if not self.chart_names:
            raise ValueError("Čech complexes require named charts")
        simplices = tuple(simplex for simplex, _ in self.section_spaces)
        if len(set(simplices)) != len(simplices):
            raise ValueError("Čech section simplices must be unique")
        if any(not simplex for simplex in simplices):
            raise ValueError("Čech section simplices must be nonempty")

    def space_on(self, simplex: tuple[int, ...]) -> VectorSpace:
        """Return the exact section space on one ordered simplex."""

        for existing, space in self.section_spaces:
            if existing == simplex:
                return space
        raise KeyError(simplex)

    def restriction(
        self,
        source: tuple[int, ...],
        target: tuple[int, ...],
    ) -> LinearMap:
        """Return one declared restriction from a face to an intersection."""

        for existing_source, existing_target, map_ in self.restrictions:
            if (existing_source, existing_target) == (source, target):
                return map_
        raise KeyError((source, target))

    def cohomology_dimensions(self) -> tuple[tuple[int, int], ...]:
        """Return exact Čech cohomology dimensions of the supplied sections."""

        return tuple(
            (degree, self.complex.cohomology_dimension(degree))
            for degree in self.complex.degrees
        )


def restricted_cech_complex(
    chart_names: Iterable[str],
    section_spaces: Mapping[tuple[int, ...], VectorSpace]
    | Iterable[tuple[tuple[int, ...], VectorSpace]],
    restrictions: Mapping[tuple[tuple[int, ...], tuple[int, ...]], LinearMap]
    | Iterable[tuple[tuple[int, ...], tuple[int, ...], LinearMap]],
) -> RestrictedCechComplex:
    """Build a Čech complex from exact simplex spaces and face maps."""

    charts = tuple(chart_names)
    if not charts or len(set(charts)) != len(charts):
        raise ValueError("Čech complexes require unique chart names")
    space_pairs = (
        tuple(section_spaces.items())
        if isinstance(section_spaces, Mapping)
        else tuple(section_spaces)
    )
    ordered_spaces = tuple(sorted(space_pairs, key=lambda pair: (len(pair[0]), pair[0])))
    if not ordered_spaces:
        raise ValueError("restricted Čech complexes require section spaces")
    chart_count = len(charts)
    for simplex, space in ordered_spaces:
        if not simplex or tuple(sorted(simplex)) != simplex:
            raise ValueError("Čech simplices require sorted nonempty vertices")
        if any(vertex < 0 or vertex >= chart_count for vertex in simplex):
            raise ValueError("Čech simplex vertex is outside the chart cover")
        if not isinstance(space, VectorSpace):
            raise TypeError("Čech section values must be VectorSpace instances")
    restriction_pairs = (
        tuple(
            (source, target, map_)
            for (source, target), map_ in restrictions.items()
        )
        if isinstance(restrictions, Mapping)
        else tuple(restrictions)
    )
    if len({(source, target) for source, target, _ in restriction_pairs}) != len(restriction_pairs):
        raise ValueError("Čech restrictions must use unique face keys")
    space_by_simplex = dict(ordered_spaces)
    restriction_by_face = {(source, target): map_ for source, target, map_ in restriction_pairs}
    scalar_types = {space.scalar_type for _, space in ordered_spaces}
    if len(scalar_types) != 1:
        raise TypeError("all Čech section spaces require one scalar field")
    degrees = tuple(sorted({len(simplex) - 1 for simplex, _ in ordered_spaces}))
    global_spaces = {
        degree: VectorSpace(
            f"Restricted Cech^{degree}",
            tuple(
                f"{simplex}:{label}"
                for simplex, space in ordered_spaces
                if len(simplex) - 1 == degree
                for label in space.basis
            ),
            next(iter(scalar_types)),
        )
        for degree in degrees
    }
    differentials: dict[int, LinearMap] = {}
    for degree in degrees:
        source_records = tuple(
            (simplex, space)
            for simplex, space in ordered_spaces
            if len(simplex) - 1 == degree
        )
        target_records = tuple(
            (simplex, space)
            for simplex, space in ordered_spaces
            if len(simplex) - 1 == degree + 1
        )
        if not target_records:
            continue
        source_offsets: dict[tuple[int, ...], int] = {}
        offset = 0
        for simplex, space in source_records:
            source_offsets[simplex] = offset
            offset += space.dimension
        target_offsets: dict[tuple[int, ...], int] = {}
        offset = 0
        for simplex, space in target_records:
            target_offsets[simplex] = offset
            offset += space.dimension
        rows = [
            [next(iter(scalar_types))(0) for _ in range(global_spaces[degree].dimension)]
            for _ in range(global_spaces[degree + 1].dimension)
        ]
        for target_simplex, target_space in target_records:
            for omitted in range(len(target_simplex)):
                source_simplex = (
                    target_simplex[:omitted] + target_simplex[omitted + 1:]
                )
                if source_simplex not in space_by_simplex:
                    raise ValueError("Čech differential references an absent face space")
                map_ = restriction_by_face.get((source_simplex, target_simplex))
                if map_ is None:
                    raise ValueError("Čech differential is missing a face restriction")
                if map_.domain != space_by_simplex[source_simplex] or map_.codomain != target_space:
                    raise ValueError("Čech restriction has incompatible named spaces")
                sign = 1 if omitted % 2 == 0 else -1
                for local_row, row in enumerate(map_.rows):
                    for local_column, value in enumerate(row):
                        rows[
                            target_offsets[target_simplex] + local_row
                        ][source_offsets[source_simplex] + local_column] += (
                            value if sign == 1 else -value
                        )
        differentials[degree] = LinearMap(
            global_spaces[degree],
            global_spaces[degree + 1],
            rows,
        )
    complex_ = CochainComplex(GradedVectorSpace("restricted Cech", global_spaces), differentials)
    return RestrictedCechComplex(charts, ordered_spaces, restriction_pairs, complex_)


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


__all__ = [
    "CechSimplex",
    "ConstantCechComplex",
    "RestrictedCechComplex",
    "constant_cech_complex",
    "restricted_cech_complex",
]
