"""Transfer exact deck actions through the full Serre outer Čech contraction.

Owns:
    Source-linearized constituent frames, oriented standard-cover pullback, and
    finite perturbed inclusion/projection formulas for transferred outer actions.

Depends on:
    Published constituent linearizations, exact Schoen coordinate actions, and
    the certified full-Čech homological perturbation contraction.

Must not:
    Select a relative character from expected outer dimensions, treat fixed
    cover classes as physical extensions, or bypass an equivariance gate.

Phase 0:
    Research-only derivation of deck actions on transferred outer complexes.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import cast

from onetheory.math.homological import VectorSpace
from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein

from .dp9_serre_actions import _fiber_coordinate_images
from .resolution_actions import tier_a_resolution_actions
from .schoen_serre_outer import SchoenSerreConstituent
from .schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
    TransferredOuterHom,
    _components,
    _freeze_rows,
    _full_differential,
    _homotopy,
    _include,
    _perturbation,
    _projection_index,
    _reduced_basis,
    transferred_schoen_serre_outer_hom,
)
from .schoen_sparse_actions import (
    CoordinateImage,
    SchoenSparseDeckAction,
    _inverse_images,
    _monomial_action,
    schoen_sparse_deck_actions,
)
from .schoen_sparse_outer import SparseMap
from .schoen_sparse_outer_actions import (
    _cohomology_complement_columns,
    _columns,
    _select_columns,
)

Cell = tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]


def _block_diagonal(*blocks: Matrix) -> Matrix:
    """Return an exact block diagonal matrix in declared object order."""

    size = sum(block.row_count for block in blocks)
    rows = [[Eisenstein(0) for _ in range(size)] for _ in range(size)]
    offset = 0
    for block in blocks:
        if block.row_count != block.column_count:
            raise ValueError("constituent frame blocks must be square")
        for row in range(block.row_count):
            for column in range(block.column_count):
                rows[offset + row][offset + column] = block[row][column]
        offset += block.row_count
    return Matrix(tuple(tuple(row) for row in rows), scalar_type=Eisenstein)


@cache
def _constituent_frame(
    constituent: SchoenSerreConstituent,
    generator: str,
) -> Matrix:
    """Return the source-bound frame action on one constituent cone."""

    pair = tier_a_resolution_actions()[constituent.factor - 1]
    resolution = pair.action(generator)
    character = Eisenstein(1)
    if constituent.factor == 2:
        target = resolution.target_action.inverse()
        source = resolution.source_action.inverse()
    else:
        target = resolution.target_action
        source = resolution.source_action
    if generator == "P":
        source_character = Eisenstein(0, 1)
        source_fiber_images = _fiber_coordinate_images(
            generator,
            constituent.factor,
        )
        if constituent.factor == 2:
            source_character = Eisenstein(1) / source_character
            source_fiber_images = _inverse_images(source_fiber_images)
        source_overlap, _ = _monomial_action((-1, -1), source_fiber_images)
        schoen_action = next(
            action
            for action in schoen_sparse_deck_actions()
            if action.name == generator
        )
        schoen_overlap, _ = _monomial_action((-1, -1), schoen_action.p_images)
        character = source_character * source_overlap / schoen_overlap
    frame = _block_diagonal(
        Matrix(((character,),), scalar_type=Eisenstein),
        target,
        source,
    )
    if frame.row_count != len(constituent.objects):
        raise ValueError("constituent frame does not match its cone objects")
    return frame


def _coordinate_permutation(images: CoordinateImage) -> tuple[int, ...]:
    """Return the target coordinate index of each monomial substitution."""

    permutation = tuple(exponents.index(1) for _, exponents in images)
    if sorted(permutation) != list(range(len(images))):
        raise ValueError("Čech pullback requires a coordinate permutation")
    return permutation


def _permutation_sign(values: tuple[int, ...]) -> int:
    """Return the sign required to sort one tuple of distinct indices."""

    inversions = sum(
        values[left] > values[right]
        for left in range(len(values))
        for right in range(left + 1, len(values))
    )
    return -1 if inversions % 2 else 1


def _cell_image(
    cell: Cell,
    action: SchoenSparseDeckAction,
) -> tuple[int, Cell]:
    """Pull one oriented product-cover cell through a deck permutation."""

    permutations = tuple(
        _coordinate_permutation(images)
        for images in (action.x_images, action.u_images, action.p_images)
    )
    sign = 1
    target = []
    for simplex, permutation in zip(cell, permutations, strict=True):
        image = tuple(permutation[index] for index in simplex)
        sign *= _permutation_sign(image)
        target.append(tuple(sorted(image)))
    return sign, cast(Cell, tuple(target))


def _koszul_unit(component: OuterCechComponent, action: SchoenSparseDeckAction) -> Eisenstein:
    """Return the equation-character correction of one Koszul summand."""

    units = {
        "k0": Eisenstein(1),
        "k1_x": action.first_equation_unit,
        "k1_u": action.second_equation_unit,
        "k2": action.first_equation_unit * action.second_equation_unit,
    }
    return units[component.koszul_summand]


def _full_action(
    cochain: SparseOuterCechCochain,
    left: SchoenSerreConstituent,
    right: SchoenSerreConstituent,
    action: SchoenSparseDeckAction,
) -> SparseOuterCechCochain:
    """Apply exact pullback and frame conjugation on full outer Čech cochains."""

    left_frame = _constituent_frame(left, action.name)
    right_inverse = _constituent_frame(right, action.name).inverse()
    lookup = {
        (component.left_index, component.right_index, component.koszul_summand): component
        for component in _components(left, right)
    }
    result: list[tuple[OuterCechBasis, Eisenstein]] = []
    for basis, coefficient in cochain.terms:
        x_scalar, x_target = _monomial_action(basis.x_monomial, action.x_images)
        u_scalar, u_target = _monomial_action(basis.u_monomial, action.u_images)
        p_scalar, p_target = _monomial_action(basis.p_monomial, action.p_images)
        cell_sign, target_cell = _cell_image(basis.cell, action)
        geometric = (
            coefficient
            * x_scalar
            * u_scalar
            * p_scalar
            * cell_sign
            * _koszul_unit(basis.component, action)
        )
        for target_left in range(left_frame.row_count):
            left_coefficient = left_frame[target_left][basis.component.left_index]
            if left_coefficient.is_zero():
                continue
            for target_right in range(right_inverse.column_count):
                right_coefficient = right_inverse[
                    basis.component.right_index
                ][target_right]
                if right_coefficient.is_zero():
                    continue
                target_component = lookup[
                    (
                        target_left,
                        target_right,
                        basis.component.koszul_summand,
                    )
                ]
                result.append(
                    (
                        OuterCechBasis(
                            target_component,
                            cast(tuple[int, int, int], x_target),
                            cast(tuple[int, int, int], u_target),
                            cast(tuple[int, int], p_target),
                            target_cell,
                        ),
                        geometric * left_coefficient * right_coefficient,
                    )
                )
    return SparseOuterCechCochain(tuple(result))


def _perturbed_inclusion(
    cochain: SparseOuterCechCochain,
    left: SchoenSerreConstituent,
    right: SchoenSerreConstituent,
) -> tuple[SparseOuterCechCochain, int]:
    """Apply ``(1 + h Δ)^-1`` to a raw contraction inclusion."""

    result = SparseOuterCechCochain()
    current = cochain
    depth = 0
    while not current.is_zero():
        result = result + current
        current = _homotopy(_perturbation(current, left, right)).scale(-1)
        depth += 1
        if depth > 12:
            raise ValueError("perturbed Čech inclusion did not terminate")
    return result, depth


def _perturbed_projection(
    cochain: SparseOuterCechCochain,
    left: SchoenSerreConstituent,
    right: SchoenSerreConstituent,
    degree: int,
) -> tuple[dict[int, Eisenstein], int]:
    """Apply ``p (1 + Δ h)^-1`` into one reduced total degree."""

    entries = _reduced_basis(left, right, degree)
    target_indices = {
        (
            entry.component,
            entry.x_monomial,
            entry.u_monomial,
            entry.p_monomial,
        ): entry.index
        for entry in entries
    }
    result: dict[int, Eisenstein] = {}
    current = cochain
    depth = 0
    while not current.is_zero():
        for basis, coefficient in current.terms:
            target = _projection_index(basis, target_indices)
            if target is not None:
                value = result.get(target, Eisenstein(0)) + coefficient
                if value.is_zero():
                    result.pop(target, None)
                else:
                    result[target] = value
        current = _perturbation(
            _homotopy(current),
            left,
            right,
        ).scale(-1)
        depth += 1
        if depth > 12:
            raise ValueError("perturbed Čech projection did not terminate")
    return result, depth


def _reduced_cochain(
    entries,
    coefficients: dict[int, Eisenstein],
) -> SparseOuterCechCochain:
    """Include a sparse reduced vector in the raw contraction coordinates."""

    result = SparseOuterCechCochain()
    for index, coefficient in coefficients.items():
        result = result + _include(entries[index]).scale(coefficient)
    return result


def _apply_transferred_action(
    coefficients: dict[int, Eisenstein],
    left: SchoenSerreConstituent,
    right: SchoenSerreConstituent,
    degree: int,
    action: SchoenSparseDeckAction,
) -> tuple[dict[int, Eisenstein], tuple[int, int]]:
    """Evaluate ``p' g i'`` on one sparse reduced cochain."""

    entries = _reduced_basis(left, right, degree)
    included, inclusion_depth = _perturbed_inclusion(
        _reduced_cochain(entries, coefficients),
        left,
        right,
    )
    acted = _full_action(included, left, right, action)
    projected, projection_depth = _perturbed_projection(
        acted,
        left,
        right,
        degree,
    )
    return projected, (inclusion_depth, projection_depth)


def _independent_columns(map_: SparseMap) -> tuple[dict[int, Eisenstein], ...]:
    """Return a deterministic exact basis for one sparse column image."""

    pivots: dict[int, dict[int, Eisenstein]] = {}
    selected = []
    for column in sorted(_columns(map_), key=len):
        vector = dict(column)
        while vector:
            pivot = min(vector)
            coefficient = vector[pivot]
            existing = pivots.get(pivot)
            if existing is None:
                inverse = Eisenstein(1) / coefficient
                pivots[pivot] = {
                    row: value * inverse for row, value in vector.items()
                }
                selected.append(dict(column))
                break
            for row, value in existing.items():
                updated = vector.get(row, Eisenstein(0)) - coefficient * value
                if updated.is_zero():
                    vector.pop(row, None)
                else:
                    vector[row] = updated
    return tuple(selected)


class _SparseSpanSolver:
    """Exact sparse coordinate solver for one declared independent basis."""

    def __init__(self, columns: tuple[dict[int, Eisenstein], ...]) -> None:
        pivots: dict[int, tuple[dict[int, Eisenstein], dict[int, Eisenstein]]] = {}
        for index, column in enumerate(columns):
            vector = dict(column)
            coordinates = {index: Eisenstein(1)}
            while vector:
                pivot = min(vector)
                coefficient = vector[pivot]
                existing = pivots.get(pivot)
                if existing is None:
                    inverse = Eisenstein(1) / coefficient
                    pivots[pivot] = (
                        {row: value * inverse for row, value in vector.items()},
                        {
                            coordinate: value * inverse
                            for coordinate, value in coordinates.items()
                        },
                    )
                    break
                pivot_vector, pivot_coordinates = existing
                for row, value in pivot_vector.items():
                    updated = vector.get(row, Eisenstein(0)) - coefficient * value
                    if updated.is_zero():
                        vector.pop(row, None)
                    else:
                        vector[row] = updated
                for coordinate, value in pivot_coordinates.items():
                    updated = coordinates.get(coordinate, Eisenstein(0)) - coefficient * value
                    if updated.is_zero():
                        coordinates.pop(coordinate, None)
                    else:
                        coordinates[coordinate] = updated
            if not vector:
                raise ValueError("sparse span basis contains a dependent column")
        self._pivots = pivots

    def coordinates(self, column: dict[int, Eisenstein]) -> dict[int, Eisenstein]:
        """Resolve one sparse vector in the initialized exact basis."""

        vector = dict(column)
        result: dict[int, Eisenstein] = {}
        while vector:
            pivot = min(vector)
            coefficient = vector[pivot]
            existing = self._pivots.get(pivot)
            if existing is None:
                raise ValueError("transferred deck image escaped the cycle span")
            pivot_vector, pivot_coordinates = existing
            for row, value in pivot_vector.items():
                updated = vector.get(row, Eisenstein(0)) - coefficient * value
                if updated.is_zero():
                    vector.pop(row, None)
                else:
                    vector[row] = updated
            for coordinate, value in pivot_coordinates.items():
                updated = result.get(coordinate, Eisenstein(0)) + coefficient * value
                if updated.is_zero():
                    result.pop(coordinate, None)
                else:
                    result[coordinate] = updated
        return result


def _matrix_from_columns(
    columns: tuple[dict[int, Eisenstein], ...],
    row_count: int,
) -> Matrix:
    """Convert exact sparse columns into a dense small matrix."""

    return Matrix(
        tuple(
            tuple(column.get(row, Eisenstein(0)) for column in columns)
            for row in range(row_count)
        ),
        scalar_type=Eisenstein,
    )


def _sparse_map_from_matrix(
    matrix: Matrix,
    name: str,
    codomain: VectorSpace,
) -> SparseMap:
    """Convert one exact matrix into a named sparse map."""

    domain = VectorSpace(
        f"{name}:domain",
        tuple(f"{name}:{index}" for index in range(matrix.column_count)),
        Eisenstein,
    )
    if matrix.row_count != codomain.dimension:
        raise ValueError("matrix rows do not match the declared sparse codomain")
    return SparseMap(
        domain,
        codomain,
        _freeze_rows(
            {
                column: matrix[row][column]
                for column in range(matrix.column_count)
                if not matrix[row][column].is_zero()
            }
            for row in range(matrix.row_count)
        ),
    )


@dataclass(frozen=True, slots=True)
class TransferredCohomologyDeckAction:
    """Exact deck representation on one transferred outer cohomology space."""

    transferred: TransferredOuterHom
    degree: int
    representatives: SparseMap
    p_induced: Matrix
    t_induced: Matrix
    invariant_coordinates: Matrix
    invariant_representatives: SparseMap
    invariant_full_cech: tuple[SparseOuterCechCochain, ...]
    action_depths: tuple[tuple[str, int, int], ...]
    images_are_cycles: bool
    full_representatives_are_cycles: bool
    full_representatives_are_invariant: bool

    @property
    def invariant_dimension(self) -> int:
        """Return the common fixed cohomology dimension."""

        return self.invariant_coordinates.column_count

    @property
    def group_relations(self) -> bool:
        """Return exact order-three and commutator gates on cohomology."""

        identity = Matrix.identity(self.p_induced.row_count, scalar_type=Eisenstein)
        return (
            self.p_induced @ self.p_induced @ self.p_induced == identity
            and self.t_induced @ self.t_induced @ self.t_induced == identity
            and self.p_induced @ self.t_induced == self.t_induced @ self.p_induced
        )

    @property
    def exact(self) -> bool:
        """Return whether cycle and finite-group gates both close."""

        return (
            self.images_are_cycles
            and self.group_relations
            and self.full_representatives_are_cycles
            and self.full_representatives_are_invariant
        )


def _fixed_coordinates(p: Matrix, t: Matrix) -> Matrix:
    """Return an exact basis of common fixed cohomology coordinates."""

    identity = Matrix.identity(p.row_count, scalar_type=Eisenstein)
    equations = Matrix(
        (*((p - identity).rows), *((t - identity).rows)),
        scalar_type=Eisenstein,
    )
    vectors = equations.nullspace()
    return Matrix(
        tuple(
            tuple(vector.values[column] for vector in vectors)
            for column in range(p.row_count)
        ),
        scalar_type=Eisenstein,
    )


def _average_full_invariant(
    cochain: SparseOuterCechCochain,
    left: SchoenSerreConstituent,
    right: SchoenSerreConstituent,
    p: SchoenSparseDeckAction,
    t: SchoenSparseDeckAction,
) -> SparseOuterCechCochain:
    """Apply the exact order-nine Reynolds projector on full Čech cochains."""

    total = SparseOuterCechCochain()
    p_power = cochain
    for _ in range(3):
        term = p_power
        for _ in range(3):
            total = total + term
            term = _full_action(term, left, right, t)
        p_power = _full_action(p_power, left, right, p)
    return total.scale(Eisenstein(1) / 9)


@cache
def transferred_outer_cohomology_deck_action(
    left: SchoenSerreConstituent,
    right: SchoenSerreConstituent,
    degree: int = 1,
) -> TransferredCohomologyDeckAction:
    """Derive both deck generators and explicit invariant full-Čech classes."""

    transferred = transferred_schoen_serre_outer_hom(left, right)
    spaces = dict(transferred.reduced.total_spaces)
    differentials = dict(transferred.differentials)
    outgoing = differentials[degree]
    incoming = differentials[degree - 1]
    cycles = outgoing.kernel_inclusion()
    selected = _cohomology_complement_columns(incoming, cycles)
    representatives = _select_columns(cycles, selected, f"H{degree}:representatives")
    boundary_columns = _independent_columns(incoming)
    representative_columns = tuple(_columns(representatives))
    solver = _SparseSpanSolver(boundary_columns + representative_columns)
    boundary_dimension = len(boundary_columns)
    actions = {action.name: action for action in schoen_sparse_deck_actions()}
    induced: dict[str, Matrix] = {}
    depths: list[tuple[str, int, int]] = []
    images_are_cycles = True
    for name, action in actions.items():
        columns = []
        for source in representative_columns:
            image, depth = _apply_transferred_action(
                source,
                left,
                right,
                degree,
                action,
            )
            depths.append((name, *depth))
            cycle_map = SparseMap(
                VectorSpace("one", ("one",), Eisenstein),
                spaces[degree],
                _freeze_rows(
                    ({0: image[row]} if row in image else {})
                    for row in range(spaces[degree].dimension)
                ),
            )
            if not outgoing.compose(cycle_map).is_zero():
                images_are_cycles = False
            coordinates = solver.coordinates(image)
            columns.append(
                {
                    index - boundary_dimension: value
                    for index, value in coordinates.items()
                    if index >= boundary_dimension
                }
            )
        induced[name] = _matrix_from_columns(tuple(columns), len(representative_columns))
    p_induced = induced["P"]
    t_induced = induced["T"]
    invariant_coordinates = _fixed_coordinates(p_induced, t_induced)
    representative_matrix = _matrix_from_columns(
        representative_columns,
        spaces[degree].dimension,
    )
    invariant_matrix = representative_matrix @ invariant_coordinates
    provisional_representatives = _sparse_map_from_matrix(
        invariant_matrix,
        f"H{degree}:invariant-provisional",
        spaces[degree],
    )
    entries = _reduced_basis(left, right, degree)
    invariant_full_cech = []
    invariant_reduced_columns = []
    p = actions["P"]
    t = actions["T"]
    for column in _columns(provisional_representatives):
        included, _ = _perturbed_inclusion(
            _reduced_cochain(entries, column),
            left,
            right,
        )
        averaged = _average_full_invariant(included, left, right, p, t)
        projected, _ = _perturbed_projection(
            averaged,
            left,
            right,
            degree,
        )
        invariant_full_cech.append(averaged)
        invariant_reduced_columns.append(projected)
    invariant_representatives = SparseMap(
        VectorSpace(
            f"H{degree}:invariant",
            tuple(
                f"invariant:{index}"
                for index in range(len(invariant_reduced_columns))
            ),
            Eisenstein,
        ),
        spaces[degree],
        _freeze_rows(
            {
                column: values[row]
                for column, values in enumerate(invariant_reduced_columns)
                if row in values
            }
            for row in range(spaces[degree].dimension)
        ),
    )
    full_cycles = all(
        _full_differential(representative, left, right).is_zero()
        for representative in invariant_full_cech
    )
    full_invariant = all(
        _full_action(representative, left, right, p) == representative
        and _full_action(representative, left, right, t) == representative
        for representative in invariant_full_cech
    )
    result = TransferredCohomologyDeckAction(
        transferred,
        degree,
        representatives,
        p_induced,
        t_induced,
        invariant_coordinates,
        invariant_representatives,
        tuple(invariant_full_cech),
        tuple(depths),
        images_are_cycles,
        full_cycles,
        full_invariant,
    )
    if not result.exact:
        raise ValueError(
            "transferred outer cohomology deck-action gate failed: "
            f"images_are_cycles={images_are_cycles}, "
            f"group_relations={result.group_relations}, "
            f"full_cycles={full_cycles}, full_invariant={full_invariant}"
        )
    return result


@dataclass(frozen=True, slots=True)
class FullOuterDeckGate:
    """Exact full-Čech action gate for both deck generators."""

    p_equivariant: bool
    t_equivariant: bool
    p_order_three: bool
    t_order_three: bool
    commute: bool

    @property
    def exact(self) -> bool:
        """Return whether all checked full-action identities hold."""

        return all(
            (
                self.p_equivariant,
                self.t_equivariant,
                self.p_order_three,
                self.t_order_three,
                self.commute,
            )
        )


__all__ = [
    "FullOuterDeckGate",
    "TransferredCohomologyDeckAction",
    "transferred_outer_cohomology_deck_action",
]
