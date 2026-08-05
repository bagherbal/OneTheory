"""Derive bounded deck actions on the outer Hom Cech complex.

Owns:
    Exact coordinate substitutions, local split-gauge conjugations, oriented
    simplex actions, closure diagnostics, group-relation checks, and the
    conditional Reynolds projector for a bounded outer-extension complex.

Depends on:
    The bounded Hom Cech complex, exact Laurent matrices, the derived local
    gauge equations, and exact Eisenstein linear algebra. It does not import
    observations or any published bundle artifact.

Must not:
    Treat a finite coefficient window as the full Ext complex, infer an
    invariant class from a dimension count, or report quotient descent when a
    generator action escapes the declared basis or fails a group relation.

Phase 0:
    Bounded outer-action construction is executable; full Ext convergence,
    honest constituent linearization, and carrier promotion remain open.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.homological import CoordinateVector, LinearMap
from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein, Rational
from onetheory.math.sheaves import LaurentMatrix, LaurentPolynomial

from .equivariance import _derived_gauge_lift, _substitute_matrix
from .hom_cech import (
    BoundedHomCech,
    _basis_matrix,
    _matrix_terms,
    tier_a_hom_cech,
)

Monomial = tuple[int, ...]
GeneratorData = tuple[str, tuple[tuple[object, Monomial], ...], tuple[int, int, int]]


def _inverse_unipotent(matrix: LaurentMatrix) -> LaurentMatrix:
    """Invert one exact upper-unipotent local gauge matrix."""

    zero = LaurentPolynomial.zero(3, scalar_type=Eisenstein)
    one = LaurentPolynomial.one(3, scalar_type=Eisenstein)
    if matrix.rows != ((one, matrix.rows[0][1]), (zero, one)):
        raise ValueError("outer-action gauges must be upper unipotent")
    return LaurentMatrix(((one, -matrix.rows[0][1]), (zero, one)))


def _orientation_sign(values: tuple[int, ...]) -> int:
    """Return the sign needed to sort one transported simplex."""

    inversions = sum(
        values[left] > values[right]
        for left in range(len(values))
        for right in range(left + 1, len(values))
    )
    return -1 if inversions % 2 else 1


def _negate_matrix(matrix: LaurentMatrix) -> LaurentMatrix:
    """Negate every entry of one exact Laurent matrix."""

    return LaurentMatrix(
        tuple(tuple(-entry for entry in row) for row in matrix.rows)
    )


def _action_image(
    hom: BoundedHomCech,
    degree: int,
    simplex: tuple[int, ...],
    basis: tuple[int, int, Monomial],
    images: tuple[tuple[object, Monomial], ...],
    permutation: tuple[int, int, int],
    left_gauges: tuple[LaurentMatrix, ...],
    right_gauges: tuple[LaurentMatrix, ...],
) -> tuple[tuple[int, ...], LaurentMatrix]:
    """Transport one based local Hom section to its sorted target simplex."""

    target_unsorted = tuple(permutation[index] for index in simplex)
    target = tuple(sorted(target_unsorted))
    reference = simplex[0]
    transformed = _inverse_unipotent(left_gauges[reference]).compose(
        _substitute_matrix(
            _basis_matrix(
                basis,
                hom.left.cover.charts[0].variable_count,
                Eisenstein,
            ),
            images,
        )
    ).compose(right_gauges[reference])
    transported_reference = permutation[reference]
    if transported_reference != target[0]:
        transformed = hom.left._transition(target[0], transported_reference).compose(
            transformed
        ).compose(
            hom.right._transition(transported_reference, target[0])
        )
    if _orientation_sign(target_unsorted) == -1:
        transformed = _negate_matrix(transformed)
    return target, transformed


def _component_action(
    hom: BoundedHomCech,
    degree: int,
    images: tuple[tuple[object, Monomial], ...],
    permutation: tuple[int, int, int],
    left_gauges: tuple[LaurentMatrix, ...],
    right_gauges: tuple[LaurentMatrix, ...],
) -> tuple[LinearMap | None, int]:
    """Build one degree action, counting terms outside its exact basis."""

    records = hom.basis_by_simplex(degree)
    target_offsets: dict[tuple[int, ...], int] = {}
    target_basis_sets: dict[tuple[int, ...], set[tuple[int, int, Monomial]]] = {}
    offset = 0
    for simplex, basis in records:
        target_offsets[simplex] = offset
        target_basis_sets[simplex] = set(basis)
        offset += len(basis)
    dimension = hom.complex.spaces.space(degree).dimension
    rows = [
        [Eisenstein(0) for _ in range(dimension)]
        for _ in range(dimension)
    ]
    escaped = 0
    source_offset = 0
    for simplex, basis_values in records:
        for local_index, basis in enumerate(basis_values):
            target, image = _action_image(
                hom,
                degree,
                simplex,
                basis,
                images,
                permutation,
                left_gauges,
                right_gauges,
            )
            target_offset = target_offsets[target]
            target_basis = target_basis_sets[target]
            for row, column, exponent in _matrix_terms(image):
                term = (row, column, exponent)
                if term not in target_basis:
                    escaped += 1
                    continue
                local_target = dict(
                    (value, index) for index, value in enumerate(
                        dict(records)[target]
                    )
                )[term]
                rows[target_offset + local_target][source_offset + local_index] += (
                    image.rows[row][column].coefficient(exponent)
                )
        source_offset += len(basis_values)
    if escaped:
        return None, escaped
    space = hom.complex.spaces.space(degree)
    return LinearMap(space, space, rows), 0


def _group_failures(
    p_maps: tuple[LinearMap, ...],
    t_maps: tuple[LinearMap, ...],
) -> tuple[str, ...]:
    """Check exact P cubing, T cubing, and commutation on all degrees."""

    failures: list[str] = []
    for degree, (p_map, t_map) in enumerate(zip(p_maps, t_maps, strict=True)):
        identity = LinearMap.identity(p_map.domain)
        if not p_map.compose(p_map).compose(p_map) == identity:
            failures.append(f"P^3 != identity in degree {degree}")
        if not t_map.compose(t_map).compose(t_map) == identity:
            failures.append(f"T^3 != identity in degree {degree}")
        if p_map.compose(t_map) != t_map.compose(p_map):
            failures.append(f"PT != TP in degree {degree}")
    return tuple(failures)


def _invariant_representatives(
    hom: BoundedHomCech,
    p_map: LinearMap,
    t_map: LinearMap,
) -> tuple[CoordinateVector, ...]:
    """Solve exact invariant-cycle equations modulo exact boundaries."""

    space = hom.complex.spaces.space(1)
    dimension = space.dimension
    boundaries = hom.complex.boundaries(1)
    boundary_count = len(boundaries)
    boundary_matrix = tuple(
        tuple(vector.coordinates[column] for vector in boundaries)
        for column in range(dimension)
    )
    equations: list[tuple[Eisenstein, ...]] = []
    differential = hom.complex.differential(1)
    for row in differential.rows:
        equations.append(tuple(row) + (Eisenstein(0),) * (2 * boundary_count))
    identity = LinearMap.identity(space)
    for action, block in ((p_map - identity, 0), (t_map - identity, 1)):
        for row in range(dimension):
            equations.append(
                tuple(action.rows[row])
                + tuple(
                    -boundary_matrix[row][column]
                    if offset == block
                    else Eisenstein(0)
                    for offset in range(2)
                    for column in range(boundary_count)
                )
            )
    augmented = Matrix(equations, scalar_type=Eisenstein)
    nullspace = augmented.nullspace()
    candidates = tuple(
        CoordinateVector(space, tuple(vector.values[:dimension]))
        for vector in nullspace
        if any(not value.is_zero() for value in vector.values[:dimension])
    )
    selected: list[CoordinateVector] = []

    def rank(values: tuple[CoordinateVector, ...]) -> int:
        if not values:
            return 0
        return Matrix(
            tuple(
                tuple(value.coordinates[row] for value in values)
                for row in range(dimension)
            ),
            scalar_type=Eisenstein,
        ).rank()

    current = rank(boundaries)
    for candidate in candidates:
        next_rank = rank((*boundaries, *selected, candidate))
        if next_rank > current:
            selected.append(candidate)
            current = next_rank
    return tuple(selected)


@dataclass(frozen=True, slots=True)
class BoundedOuterDeckAction:
    """One exact generator action or explicit bounded-window obstruction."""

    generator: str
    bound: int
    chart_permutation: tuple[int, int, int]
    degree_closed: tuple[bool, ...]
    escaped_term_counts: tuple[int, ...]
    differential_compatible: bool
    group_relation_failures: tuple[str, ...]
    invariant_projector_defined: bool
    invariant_representative_count: int

    @property
    def closed(self) -> bool:
        """Return whether every represented cochain degree is closed."""

        return all(self.degree_closed)

    @property
    def group_relations_verified(self) -> bool:
        """Return whether group checks were meaningful and passed."""

        return self.closed and self.differential_compatible and not self.group_relation_failures

    def as_record(self) -> dict[str, object]:
        """Serialize closure and group gates without hiding failures."""

        return {
            "generator": self.generator,
            "bound": self.bound,
            "chart_permutation": list(self.chart_permutation),
            "degree_closed": list(self.degree_closed),
            "escaped_term_counts": list(self.escaped_term_counts),
            "closed": self.closed,
            "differential_compatible": self.differential_compatible,
            "group_relation_failures": list(self.group_relation_failures),
            "group_relations_verified": self.group_relations_verified,
            "invariant_projector_defined": self.invariant_projector_defined,
            "invariant_representative_count": self.invariant_representative_count,
        }


@dataclass(frozen=True, slots=True)
class BoundedOuterActionFrontier:
    """The exact bounded P/T action frontier for the outer Hom complex."""

    hom: BoundedHomCech
    actions: tuple[BoundedOuterDeckAction, ...]
    invariant_projector_defined: bool
    invariant_representatives: tuple[CoordinateVector, ...]
    status: str

    def as_record(self) -> dict[str, object]:
        """Serialize the bounded action frontier and its promotion boundary."""

        return {
            "bound": self.hom.bound,
            "actions": [action.as_record() for action in self.actions],
            "invariant_projector_defined": self.invariant_projector_defined,
            "invariant_representative_count": len(self.invariant_representatives),
            "status": self.status,
        }


def _generator_data() -> tuple[GeneratorData, ...]:
    """Return the exact P and T coordinate actions."""

    return (
        (
            "P",
            ((OMEGA, (0, 1, 0)), (OMEGA2, (0, 0, 1)), (1, (1, 0, 0))),
            (1, 2, 0),
        ),
        (
            "T",
            ((1, (1, 0, 0)), (OMEGA, (0, 1, 0)), (OMEGA2, (0, 0, 1))),
            (0, 1, 2),
        ),
    )


def _compute_action(
    hom: BoundedHomCech,
    name: str,
    images: tuple[tuple[object, Monomial], ...],
    permutation: tuple[int, int, int],
) -> tuple[BoundedOuterDeckAction, tuple[LinearMap, ...] | None]:
    """Compute one generator action and retain maps only when closed."""

    left_gauges = tuple(
        _derived_gauge_lift(hom.left, chart, images, permutation)
        for chart in range(3)
    )
    right_gauges = tuple(
        _derived_gauge_lift(hom.right, chart, images, permutation)
        for chart in range(3)
    )
    results = tuple(
        _component_action(
            hom,
            degree,
            images,
            permutation,
            left_gauges,
            right_gauges,
        )
        for degree in hom.complex.degrees
    )
    maps = tuple(result[0] for result in results)
    closed = all(map_ is not None for map_ in maps)
    typed_maps = tuple(map_ for map_ in maps if map_ is not None)
    differential_compatible = False
    failures: tuple[str, ...] = ()
    if closed:
        differential_compatible = all(
            typed_maps[index + 1].compose(hom.complex.differential(degree))
            == hom.complex.differential(degree).compose(typed_maps[index])
            for index, degree in enumerate(hom.complex.degrees[:-1])
        )
    return (
        BoundedOuterDeckAction(
            name,
            hom.bound,
            permutation,
            tuple(result[0] is not None for result in results),
            tuple(result[1] for result in results),
            differential_compatible,
            failures,
            False,
            0,
        ),
        typed_maps if closed else None,
    )


def bounded_outer_action(
    hom: BoundedHomCech | None = None,
) -> BoundedOuterActionFrontier:
    """Construct the exact bounded P/T outer-action diagnostic."""

    bounded = tier_a_hom_cech() if hom is None else hom
    computed = tuple(
        _compute_action(bounded, name, images, permutation)
        for name, images, permutation in _generator_data()
    )
    actions = [item[0] for item in computed]
    maps_by_generator = {
        action.generator: maps
        for action, maps in computed
        if maps is not None
    }
    if all(action.closed and action.differential_compatible for action in actions):
        p_maps = maps_by_generator["P"]
        t_maps = maps_by_generator["T"]
        failures = _group_failures(p_maps, t_maps)
        actions = [
            BoundedOuterDeckAction(
                action.generator,
                action.bound,
                action.chart_permutation,
                action.degree_closed,
                action.escaped_term_counts,
                action.differential_compatible,
                failures,
                False,
                0,
            )
            for action in actions
        ]
    else:
        failures = ()
    projector_defined = False
    representatives: tuple[CoordinateVector, ...] = ()
    if (
        all(action.closed and action.differential_compatible for action in actions)
        and not failures
    ):
        p_map = maps_by_generator["P"][1]
        t_map = maps_by_generator["T"][1]
        p_sum = LinearMap.identity(p_map.domain) + p_map + p_map.compose(p_map)
        t_sum = LinearMap.identity(t_map.domain) + t_map + t_map.compose(t_map)
        projector = p_sum.compose(t_sum).scale(Rational(1, 9))
        projector_defined = projector.compose(projector) == projector
        representatives = _invariant_representatives(bounded, p_map, t_map)
    return BoundedOuterActionFrontier(
        bounded,
        tuple(actions),
        projector_defined,
        representatives,
        (
            "bounded outer deck-action diagnostic; invariant projector and "
            "cocycles remain unavailable until the declared basis closes"
        ),
    )


__all__ = [
    "BoundedOuterActionFrontier",
    "BoundedOuterDeckAction",
    "bounded_outer_action",
]
