"""Exact finite Čech complexes for named chart covers.

Owns:
    Ordered simplex bases, alternating restriction incidence maps for constant
    finite coefficient spaces, typed restricted-section Čech complexes, exact
    cochain complexes, cohomology bases, and standard-projective-cover
    Laurent-monomial complexes with deterministic exact primitives.

Depends on:
    `onetheory.math.homological` for typed exact cochain complexes and
    `onetheory.math.numbers` through its vector-space implementation.

Must not:
    Pretend constant coefficients are sheaf sections, choose a carrier-specific
    cover, infer physical bundle cohomology, or attach meanings to dimensions.

Phase 0:
    The generic Čech incidence and typed restriction engines are implemented;
    localized section spaces and carrier-specific maps remain explicit inputs.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from itertools import combinations, product

from onetheory.math.homological import (
    CochainComplex,
    CoordinateVector,
    GradedVectorSpace,
    LinearMap,
    VectorSpace,
)
from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein, Rational, coerce_rational

type ScalarType = type[Rational] | type[Eisenstein]


def _coerce_scalar(value: object, scalar_type: ScalarType) -> Rational | Eisenstein:
    """Coerce one exact coefficient into the declared Čech scalar field."""

    if scalar_type is Rational:
        return coerce_rational(value)
    return Eisenstein.coerce(value)


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
        if not self.coefficient_basis or len(set(self.coefficient_basis)) != len(
            self.coefficient_basis
        ):
            raise ValueError("Čech complexes require a named coefficient basis")

    def simplices_at(self, degree: int) -> tuple[CechSimplex, ...]:
        """Return the ordered simplices in one Čech degree."""

        return dict(self.simplices).get(degree, ())

    def cohomology_dimensions(self) -> tuple[tuple[int, int], ...]:
        """Return exact cohomology dimensions in every represented degree."""

        return tuple(
            (degree, self.complex.cohomology_dimension(degree)) for degree in self.complex.degrees
        )


@dataclass(frozen=True, slots=True)
class RestrictedCechComplex:
    """A Čech complex assembled from explicitly typed simplex restrictions."""

    chart_names: tuple[str, ...]
    section_spaces: tuple[tuple[tuple[int, ...], VectorSpace], ...]
    restrictions: tuple[tuple[tuple[int, ...], tuple[int, ...], LinearMap], ...]
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
            (degree, self.complex.cohomology_dimension(degree)) for degree in self.complex.degrees
        )


@dataclass(frozen=True, slots=True)
class ProjectiveMonomialCechComplex:
    """One Laurent monomial's exact Čech complex on a standard projective cover."""

    variable_names: tuple[str, ...]
    twist_degree: int
    exponents: tuple[int, ...]
    negative_support: tuple[int, ...]
    complex: CochainComplex
    simplices: tuple[tuple[int, tuple[CechSimplex, ...]], ...]

    def __post_init__(self) -> None:
        if len(self.variable_names) < 2 or len(set(self.variable_names)) != len(
            self.variable_names
        ):
            raise ValueError("projective covers require at least two unique variables")
        if len(self.exponents) != len(self.variable_names):
            raise ValueError("Laurent exponent count does not match the projective cover")
        if sum(self.exponents) != self.twist_degree:
            raise ValueError("Laurent exponents do not have the declared twist degree")
        expected_support = tuple(
            index for index, exponent in enumerate(self.exponents) if exponent < 0
        )
        if self.negative_support != expected_support:
            raise ValueError("negative support does not match the Laurent monomial")

    def simplices_at(self, degree: int) -> tuple[CechSimplex, ...]:
        """Return intersections on which this monomial is a regular section."""

        return dict(self.simplices).get(degree, ())

    def cochain(
        self,
        degree: int,
        coefficients: Mapping[tuple[int, ...], object],
    ) -> CoordinateVector:
        """Build one exactly based monomial cochain from simplex coefficients."""

        space = self.complex.spaces.space(degree)
        simplices = self.simplices_at(degree)
        simplex_set = {simplex.vertices for simplex in simplices}
        if any(simplex not in simplex_set for simplex in coefficients):
            raise ValueError("cochain coefficient references an unavailable intersection")
        values = tuple(
            _coerce_scalar(coefficients.get(simplex.vertices, 0), space.scalar_type)
            for simplex in simplices
        )
        return CoordinateVector(space, values)

    def primitive(self, cocycle: CoordinateVector) -> CoordinateVector:
        """Return the deterministic exact Čech primitive of a coboundary."""

        degree = next(
            (
                candidate
                for candidate in self.complex.degrees
                if self.complex.spaces.space(candidate) == cocycle.space
            ),
            None,
        )
        if degree is None:
            raise ValueError("cocycle does not use this monomial complex's basis")
        if degree == min(self.complex.degrees):
            raise ValueError("the lowest Čech degree has no incoming differential")
        if not self.complex.differential(degree)(cocycle).is_zero():
            raise ValueError("a Čech primitive requires an exact cocycle")
        incoming = self.complex.differential(degree - 1)
        augmented = Matrix(
            tuple(
                tuple(row) + (cocycle.coordinates[index],)
                for index, row in enumerate(incoming.rows)
            ),
            scalar_type=cocycle.space.scalar_type,
        )
        reduced, pivots = augmented.rref()
        unknown_count = incoming.domain.dimension
        if any(
            all(reduced[row][column].is_zero() for column in range(unknown_count))
            and not reduced[row][unknown_count].is_zero()
            for row in range(reduced.row_count)
        ):
            raise ValueError("cocycle represents nonzero Čech cohomology")
        zero = _coerce_scalar(0, cocycle.space.scalar_type)
        solution = [zero for _ in range(unknown_count)]
        for row, pivot in enumerate(pivots):
            if pivot < unknown_count:
                solution[pivot] = reduced[row][unknown_count]
        primitive = CoordinateVector(incoming.domain, tuple(solution))
        if incoming(primitive) != cocycle:
            raise ValueError("exact Čech primitive failed reconstruction")
        return primitive

    @property
    def expected_cohomology_degree(self) -> int | None:
        """Return the unique possible cohomology degree from negative support."""

        if not self.negative_support:
            return 0
        if len(self.negative_support) == len(self.variable_names):
            return len(self.variable_names) - 1
        return None


@dataclass(frozen=True, slots=True)
class ProductProjectiveMonomialCechComplex:
    """The signed tensor product of projective Laurent-monomial Čech complexes."""

    factors: tuple[ProjectiveMonomialCechComplex, ...]
    complex: CochainComplex
    basis_cells: tuple[tuple[int, tuple[tuple[tuple[int, ...], ...], ...]], ...]

    def __post_init__(self) -> None:
        if not self.factors:
            raise ValueError("projective product Čech complexes require factors")
        if len({factor.complex.spaces.scalar_type for factor in self.factors}) != 1:
            raise TypeError("projective product factors require one exact scalar field")

    def cells_at(self, degree: int) -> tuple[tuple[tuple[int, ...], ...], ...]:
        """Return the ordered tensor-product simplex cells in one total degree."""

        return dict(self.basis_cells).get(degree, ())

    def cochain(
        self,
        degree: int,
        coefficients: Mapping[tuple[tuple[int, ...], ...], object],
    ) -> CoordinateVector:
        """Build one exactly based product cochain from cell coefficients."""

        space = self.complex.spaces.space(degree)
        cells = self.cells_at(degree)
        cell_set = set(cells)
        if any(cell not in cell_set for cell in coefficients):
            raise ValueError("cochain coefficient references an unavailable product cell")
        return CoordinateVector(
            space,
            tuple(_coerce_scalar(coefficients.get(cell, 0), space.scalar_type) for cell in cells),
        )

    def canonical_representative(self) -> CoordinateVector:
        """Return the tensor product of canonical nonzero factor classes."""

        factor_degrees = tuple(factor.expected_cohomology_degree for factor in self.factors)
        if any(degree is None for degree in factor_degrees):
            raise ValueError("an acyclic factor has no canonical cohomology representative")
        degrees = tuple(degree for degree in factor_degrees if degree is not None)
        total_degree = sum(degrees)
        local_cells = []
        for factor, degree in zip(self.factors, degrees, strict=True):
            simplices = factor.simplices_at(degree)
            if not simplices:
                raise ValueError("a canonical factor degree has no Čech simplex")
            local_cells.append(tuple(simplex.vertices for simplex in simplices))
        return self.cochain(
            total_degree,
            {tuple(cell): 1 for cell in product(*local_cells)},
        )

    def primitive(self, cocycle: CoordinateVector) -> CoordinateVector:
        """Return a deterministic exact primitive in the signed product complex."""

        degree = next(
            (
                candidate
                for candidate in self.complex.degrees
                if self.complex.spaces.space(candidate) == cocycle.space
            ),
            None,
        )
        if degree is None:
            raise ValueError("cocycle does not use this product complex's basis")
        if degree == min(self.complex.degrees):
            raise ValueError("the lowest Čech degree has no incoming differential")
        if not self.complex.differential(degree)(cocycle).is_zero():
            raise ValueError("a Čech primitive requires an exact cocycle")
        acyclic_factor = next(
            (
                index
                for index, factor in enumerate(self.factors)
                if 0 < len(factor.negative_support) < len(factor.variable_names)
            ),
            None,
        )
        if acyclic_factor is None:
            raise ValueError("cocycle represents nonzero product Čech cohomology")
        selected = self.factors[acyclic_factor]
        cone_vertex = next(
            index
            for index in range(len(selected.variable_names))
            if index not in selected.negative_support
        )
        source_values = dict(zip(self.cells_at(degree), cocycle.coordinates, strict=True))
        values = []
        for cell in self.cells_at(degree - 1):
            simplex = cell[acyclic_factor]
            if cone_vertex in simplex:
                values.append(_coerce_scalar(0, cocycle.space.scalar_type))
                continue
            expanded = tuple(sorted((*simplex, cone_vertex)))
            source_cell = list(cell)
            source_cell[acyclic_factor] = expanded
            insertion_sign = -1 if expanded.index(cone_vertex) % 2 else 1
            tensor_degree = sum(len(previous) - 1 for previous in cell[:acyclic_factor])
            tensor_sign = -1 if tensor_degree % 2 else 1
            values.append(source_values[tuple(source_cell)] * insertion_sign * tensor_sign)
        incoming = self.complex.differential(degree - 1)
        primitive = CoordinateVector(incoming.domain, tuple(values))
        if incoming(primitive) != cocycle:
            raise ValueError("exact product Čech primitive failed reconstruction")
        return primitive

    def projected_representative(self, cochain: CoordinateVector) -> CoordinateVector:
        """Project a cochain onto the canonical product-cohomology summand."""

        degree = self._degree_of(cochain)
        values = dict(zip(self.cells_at(degree), cochain.coordinates, strict=True))
        projected: dict[tuple[tuple[int, ...], ...], Rational | Eisenstein] = {
            cell: value
            for cell, value in values.items()
            if not value.is_zero()
        }
        for factor_index, factor in enumerate(self.factors):
            next_values: dict[
                tuple[tuple[int, ...], ...], Rational | Eisenstein
            ] = {}
            for cell, value in projected.items():
                for simplex, coefficient in _factor_projection_image(
                    factor,
                    cell[factor_index],
                ):
                    target = list(cell)
                    target[factor_index] = simplex
                    target_cell = tuple(target)
                    next_values[target_cell] = _add_cech_scalars(
                        next_values.get(target_cell),
                        value * coefficient,
                        cochain.space.scalar_type,
                    )
            projected = next_values
        return self.cochain(degree, projected)

    def contracting_homotopy(self, cochain: CoordinateVector) -> CoordinateVector:
        """Apply the canonical tensor-trick homotopy to any product cochain."""

        degree = self._degree_of(cochain)
        if degree == min(self.complex.degrees):
            return CoordinateVector(
                self.complex.spaces.space(degree - 1),
                (),
            )
        source = dict(zip(self.cells_at(degree), cochain.coordinates, strict=True))
        result: dict[tuple[tuple[int, ...], ...], Rational | Eisenstein] = {}
        for cell, value in source.items():
            if value.is_zero():
                continue
            prefix_images: tuple[tuple[tuple[tuple[int, ...], ...], int], ...] = (
                ((), 1),
            )
            for factor_index, factor in enumerate(self.factors):
                for prefix, prefix_coefficient in prefix_images:
                    for simplex, local_coefficient in _factor_homotopy_image(
                        factor,
                        cell[factor_index],
                    ):
                        target_cell = (*prefix, simplex, *cell[factor_index + 1 :])
                        tensor_sign = -1 if sum(len(item) - 1 for item in prefix) % 2 else 1
                        coefficient = prefix_coefficient * local_coefficient * tensor_sign
                        result[target_cell] = _add_cech_scalars(
                            result.get(target_cell),
                            value * coefficient,
                            cochain.space.scalar_type,
                        )
                next_prefixes: list[tuple[tuple[tuple[int, ...], ...], int]] = []
                for prefix, prefix_coefficient in prefix_images:
                    for simplex, local_coefficient in _factor_projection_image(
                        factor,
                        cell[factor_index],
                    ):
                        next_prefixes.append(
                            ((*prefix, simplex), prefix_coefficient * local_coefficient)
                        )
                prefix_images = tuple(next_prefixes)
                if not prefix_images:
                    break
        return self.cochain(degree - 1, result)

    def _degree_of(self, cochain: CoordinateVector) -> int:
        """Return the unique degree occupied by a typed product cochain."""

        degree = next(
            (
                candidate
                for candidate in self.complex.degrees
                if self.complex.spaces.space(candidate) == cochain.space
            ),
            None,
        )
        if degree is None:
            raise ValueError("cochain does not use this product complex's basis")
        return degree


def _factor_projection_image(
    factor: ProjectiveMonomialCechComplex,
    simplex: tuple[int, ...],
) -> tuple[tuple[tuple[int, ...], int], ...]:
    """Return the factorwise ``i p`` image of one simplex basis cochain."""

    support = factor.negative_support
    vertex_count = len(factor.variable_names)
    if not support:
        if simplex != (0,):
            return ()
        return tuple(((vertex,), 1) for vertex in range(vertex_count))
    if len(support) == vertex_count:
        return ((simplex, 1),)
    return ()


def _factor_homotopy_image(
    factor: ProjectiveMonomialCechComplex,
    simplex: tuple[int, ...],
) -> tuple[tuple[tuple[int, ...], int], ...]:
    """Return the standard cone homotopy image of one simplex cochain."""

    support = factor.negative_support
    if len(support) == len(factor.variable_names):
        return ()
    cone_vertex = next(
        index
        for index in range(len(factor.variable_names))
        if index not in support
    )
    if cone_vertex not in simplex or len(simplex) == 1:
        return ()
    position = simplex.index(cone_vertex)
    reduced = simplex[:position] + simplex[position + 1 :]
    return ((reduced, -1 if position % 2 else 1),)


def _add_cech_scalars(
    current: Rational | Eisenstein | None,
    value: Rational | Eisenstein,
    scalar_type: ScalarType,
) -> Rational | Eisenstein:
    """Add exact scalar values while preserving the declared coefficient field."""

    if scalar_type is Rational:
        return coerce_rational(0 if current is None else current) + coerce_rational(value)
    return Eisenstein.coerce(0 if current is None else current) + Eisenstein.coerce(value)


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
        tuple((source, target, map_) for (source, target), map_ in restrictions.items())
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
            (simplex, space) for simplex, space in ordered_spaces if len(simplex) - 1 == degree
        )
        target_records = tuple(
            (simplex, space) for simplex, space in ordered_spaces if len(simplex) - 1 == degree + 1
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
                source_simplex = target_simplex[:omitted] + target_simplex[omitted + 1 :]
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
                        rows[target_offsets[target_simplex] + local_row][
                            source_offsets[source_simplex] + local_column
                        ] += value if sign == 1 else -value
        differentials[degree] = LinearMap(
            global_spaces[degree],
            global_spaces[degree + 1],
            rows,
        )
    complex_ = CochainComplex(GradedVectorSpace("restricted Cech", global_spaces), differentials)
    return RestrictedCechComplex(charts, ordered_spaces, restriction_pairs, complex_)


def projective_monomial_cech_complex(
    variable_names: Iterable[str],
    exponents: Iterable[int],
    *,
    scalar_type: ScalarType = Rational,
) -> ProjectiveMonomialCechComplex:
    """Build one exact Laurent-monomial subcomplex of a standard projective cover.

    A Laurent monomial is regular on the intersection indexed by ``simplex``
    exactly when every negative exponent belongs to that simplex. Restriction
    maps preserve the monomial, so its Čech differential is the signed simplex
    incidence map on this upward-closed set of intersections.
    """

    variables = tuple(variable_names)
    powers = tuple(exponents)
    if len(variables) < 2 or len(set(variables)) != len(variables):
        raise ValueError("projective covers require at least two unique variables")
    if len(powers) != len(variables):
        raise ValueError("Laurent exponent count does not match the projective cover")
    if any(isinstance(exponent, bool) or not isinstance(exponent, int) for exponent in powers):
        raise TypeError("Laurent exponents must be integers")
    if scalar_type not in (Rational, Eisenstein):
        raise TypeError("projective Čech coefficients require Rational or Eisenstein")
    negative_support = tuple(index for index, exponent in enumerate(powers) if exponent < 0)
    simplex_data = tuple(
        (
            degree,
            tuple(
                CechSimplex(simplex)
                for simplex in combinations(range(len(variables)), degree + 1)
                if set(negative_support).issubset(simplex)
            ),
        )
        for degree in range(len(variables))
    )
    spaces = {
        degree: VectorSpace(
            f"Cech O({sum(powers)})[{powers}]^{degree}",
            tuple(str(simplex.vertices) for simplex in simplices),
            scalar_type,
        )
        for degree, simplices in simplex_data
    }
    differentials: dict[int, LinearMap] = {}
    for degree, simplices in simplex_data[:-1]:
        targets = dict(simplex_data)[degree + 1]
        source_index = {simplex.vertices: index for index, simplex in enumerate(simplices)}
        rows = [
            [scalar_type(0) for _ in range(spaces[degree].dimension)]
            for _ in range(spaces[degree + 1].dimension)
        ]
        for target_index, target in enumerate(targets):
            for omitted in range(len(target.vertices)):
                source = target.vertices[:omitted] + target.vertices[omitted + 1 :]
                column = source_index.get(source)
                if column is not None:
                    rows[target_index][column] = scalar_type(1 if omitted % 2 == 0 else -1)
        differentials[degree] = LinearMap(
            spaces[degree],
            spaces[degree + 1],
            rows,
        )
    complex_ = CochainComplex(
        GradedVectorSpace(f"projective monomial {powers}", spaces),
        differentials,
    )
    return ProjectiveMonomialCechComplex(
        variables,
        sum(powers),
        powers,
        negative_support,
        complex_,
        simplex_data,
    )


def product_projective_monomial_cech_complex(
    factors: Iterable[ProjectiveMonomialCechComplex],
) -> ProductProjectiveMonomialCechComplex:
    """Build the exact signed total Čech complex for a projective product."""

    selected = tuple(factors)
    if not selected:
        raise ValueError("projective product Čech complexes require factors")
    scalar_types = {factor.complex.spaces.scalar_type for factor in selected}
    if len(scalar_types) != 1:
        raise TypeError("projective product factors require one exact scalar field")
    scalar_type = next(iter(scalar_types))
    degree_cells: dict[int, list[tuple[tuple[int, ...], ...]]] = {}
    factor_degree_cells = tuple(
        tuple(
            (degree, tuple(simplex.vertices for simplex in factor.simplices_at(degree)))
            for degree in factor.complex.degrees
        )
        for factor in selected
    )
    for degree_records in product(*factor_degree_cells):
        degree_tuple = tuple(degree for degree, _ in degree_records)
        simplex_sets = tuple(cells for _, cells in degree_records)
        total_degree = sum(degree_tuple)
        degree_cells.setdefault(total_degree, []).extend(product(*simplex_sets))
    ordered_cells = {degree: tuple(cells) for degree, cells in sorted(degree_cells.items())}
    spaces = {
        degree: VectorSpace(
            f"product projective Cech^{degree}",
            tuple(str(cell) for cell in cells),
            scalar_type,
        )
        for degree, cells in ordered_cells.items()
    }
    differentials: dict[int, LinearMap] = {}
    for degree, source_cells in ordered_cells.items():
        target_cells = ordered_cells.get(degree + 1)
        if target_cells is None:
            continue
        target_index = {cell: index for index, cell in enumerate(target_cells)}
        rows = [[scalar_type(0) for _ in source_cells] for _ in target_cells]
        for column, source_cell in enumerate(source_cells):
            preceding_degree = 0
            for factor_index, (factor, simplex) in enumerate(
                zip(selected, source_cell, strict=True)
            ):
                factor_degree = len(simplex) - 1
                local_source = factor.simplices_at(factor_degree)
                local_target = factor.simplices_at(factor_degree + 1)
                local_source_index = {
                    item.vertices: index for index, item in enumerate(local_source)
                }
                local_column = local_source_index[simplex]
                local_map = factor.complex.differential(factor_degree)
                tensor_sign = -1 if preceding_degree % 2 else 1
                for local_row, coefficient_row in enumerate(local_map.rows):
                    coefficient = coefficient_row[local_column]
                    if coefficient.is_zero():
                        continue
                    changed = list(source_cell)
                    changed[factor_index] = local_target[local_row].vertices
                    row = target_index[tuple(changed)]
                    rows[row][column] += coefficient * tensor_sign
                preceding_degree += factor_degree
        differentials[degree] = LinearMap(
            spaces[degree],
            spaces[degree + 1],
            rows,
        )
    complex_ = CochainComplex(
        GradedVectorSpace("product projective monomial Čech", spaces),
        differentials,
    )
    return ProductProjectiveMonomialCechComplex(
        selected,
        complex_,
        tuple(sorted(ordered_cells.items())),
    )


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
            tuple(CechSimplex(simplex) for simplex in combinations(range(len(charts)), degree + 1)),
        )
        for degree in range(len(charts))
    )
    spaces = {
        degree: VectorSpace(
            f"Cech^{degree}",
            tuple(f"{simplex.vertices}:{basis}" for simplex in simplices for basis in coefficients),
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
                source_vertices = simplex.vertices[:omitted] + simplex.vertices[omitted + 1 :]
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
    "ProjectiveMonomialCechComplex",
    "ProductProjectiveMonomialCechComplex",
    "RestrictedCechComplex",
    "constant_cech_complex",
    "projective_monomial_cech_complex",
    "product_projective_monomial_cech_complex",
    "restricted_cech_complex",
]
