"""Derive the exact deck action on projective Hom hypercohomology.

Owns:
    Pullback-and-conjugation actions on the finite H0/H2 presentation Hom
    complexes, exact Z3 x Z3 group maps, trivial-character projectors, and
    explicit invariant representatives.

Depends on:
    The Tier A pushout presentation, projective Hom hypercohomology, derived
    Hilbert--Burch actions, and generic finite-complex action machinery.

Must not:
    Call a projective presentation action a global dP9 linearization, infer
    quotient descent from its invariant dimension, or identify its cocycles
    with the published carrier.

Phase 0:
    Presentation-level deck actions and invariant representatives are exact;
    dP9 sheafification, global comparison, and physical promotion remain open.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.homological import (
    ChainMap,
    CoordinateVector,
    LinearMap,
)
from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import Eisenstein

from .projective_hyperhom import (
    ProjectiveHomCohomology,
    ProjectiveHomHypercohomology,
    tier_a_projective_hom_hypercohomology,
)
from .pushout_linearization import _middle_action
from .resolution_actions import ResolutionActionPair, tier_a_resolution_actions
from .serre_pushout import SerrePushoutCandidate, tier_a_serre_pushouts


def _hom_action_matrix(left: Matrix, right: Matrix) -> Matrix:
    """Return ``f -> left f right^-1`` in matrix-unit order."""

    right_inverse = right.inverse()
    return Matrix(
        tuple(
            tuple(
                left[target_left][source_left]
                * right_inverse[source_right][target_right]
                for source_left in range(left.column_count)
                for source_right in range(right.column_count)
            )
            for target_left in range(left.row_count)
            for target_right in range(right.row_count)
        ),
        scalar_type=Eisenstein,
    )


def _block_diagonal(left: Matrix, right: Matrix) -> Matrix:
    """Assemble a constant block-diagonal matrix exactly."""

    zero = Eisenstein(0)
    rows = []
    for row in range(left.row_count):
        rows.append(
            tuple(left[row][column] for column in range(left.column_count))
            + tuple(zero for _ in range(right.column_count))
        )
    for row in range(right.row_count):
        rows.append(
            tuple(zero for _ in range(left.column_count))
            + tuple(right[row][column] for column in range(right.column_count))
        )
    return Matrix(tuple(rows), scalar_type=Eisenstein)


def _presentation_term_actions(
    name: str,
    left_pair: ResolutionActionPair,
    right_pair: ResolutionActionPair,
    left_character: tuple[Eisenstein, Eisenstein],
    right_character: tuple[Eisenstein, Eisenstein],
) -> dict[int, Matrix]:
    """Return the constant action on each Hom presentation term."""

    generator_index = {"P": 0, "T": 1}[name]
    left_action = left_pair.action(name)
    right_action = right_pair.action(name)
    left_middle = _middle_action(
        left_action,
        left_character[generator_index],
    ).transpose()
    right_middle = _middle_action(
        right_action,
        right_character[generator_index],
    ).transpose()
    left_relation = left_action.source_action
    right_relation = right_action.source_action
    return {
        -1: _hom_action_matrix(left_relation, right_middle),
        0: _block_diagonal(
            _hom_action_matrix(left_middle, right_middle),
            _hom_action_matrix(left_relation, right_relation),
        ),
        1: _hom_action_matrix(left_middle, right_relation),
    }


def _cohomology_action_map(
    cohomology: ProjectiveHomCohomology,
    degree: int,
    matrix: Matrix,
    coordinate_images: tuple[tuple[Eisenstein, tuple[int, ...]], ...],
) -> LinearMap:
    """Evaluate pullback-and-conjugation on one finite cohomology term."""

    basis = cohomology.basis(degree)
    index = {label: position for position, label in enumerate(basis)}
    rows = [[Eisenstein(0) for _ in basis] for _ in basis]
    for source_position, (source_generator, source_monomial) in enumerate(basis):
        image_monomial = [0] * len(source_monomial)
        image_scalar = Eisenstein(1)
        for power, (scalar, exponents) in zip(
            source_monomial,
            coordinate_images,
            strict=True,
        ):
            image_scalar *= scalar**power
            image_monomial = [
                current + power * image
                for current, image in zip(image_monomial, exponents, strict=True)
            ]
        target_monomial = tuple(image_monomial)
        for target_generator in range(matrix.row_count):
            coefficient = matrix[target_generator][source_generator] * image_scalar
            if coefficient.is_zero():
                continue
            target_position = index.get((target_generator, target_monomial))
            if target_position is None:
                raise ValueError("presentation action escaped its cohomology basis")
            rows[target_position][source_position] += coefficient
    space = cohomology.complex.spaces.space(degree)
    return LinearMap(space, space, rows)


def _chain_action(
    cohomology: ProjectiveHomCohomology,
    term_actions: dict[int, Matrix],
    coordinate_images: tuple[tuple[Eisenstein, tuple[int, ...]], ...],
) -> ChainMap:
    """Build one exact chain map on H0 or H2 presentation cohomology."""

    return ChainMap(
        cohomology.complex,
        cohomology.complex,
        {
            degree: _cohomology_action_map(
                cohomology,
                degree,
                term_actions[degree],
                coordinate_images,
            )
            for degree in cohomology.complex.degrees
        },
    )


def _quotient_functionals(
    complex_: ProjectiveHomCohomology,
    degree: int,
    representatives: tuple[CoordinateVector, ...],
) -> Matrix:
    """Return exact functionals annihilating boundaries in one degree."""

    space = complex_.complex.spaces.space(degree)
    boundaries = complex_.complex.boundaries(degree)
    if boundaries:
        boundary_matrix = Matrix(
            tuple(
                tuple(vector.coordinates[column] for vector in boundaries)
                for column in range(space.dimension)
            ),
            scalar_type=space.scalar_type,
        )
        functionals = boundary_matrix.transpose().nullspace()
    else:
        functionals = tuple(
            Vector(
                tuple(
                    Eisenstein(1) if row == index else Eisenstein(0)
                    for row in range(space.dimension)
                ),
                scalar_type=space.scalar_type,
            )
            for index in range(space.dimension)
        )
    expected = len(representatives)
    if len(functionals) != expected:
        raise ValueError("boundary annihilator dimension does not match cohomology")
    return Matrix(
        tuple(functional.values for functional in functionals),
        scalar_type=space.scalar_type,
    )


def _induced_cohomology_matrix(
    action: ChainMap,
    complex_: ProjectiveHomCohomology,
    degree: int,
    representatives: tuple[CoordinateVector, ...],
) -> Matrix | None:
    """Induce an action using a small quotient solve, not subset enumeration."""

    if not representatives:
        return None
    space = complex_.complex.spaces.space(degree)
    functionals = _quotient_functionals(complex_, degree, representatives)
    representative_matrix = Matrix(
        tuple(
            tuple(vector.coordinates[column] for vector in representatives)
            for column in range(space.dimension)
        ),
        scalar_type=space.scalar_type,
    )
    normalization = functionals.matmul(representative_matrix).inverse()
    columns = []
    for representative in representatives:
        image = action.component(degree)(representative)
        image_column = Matrix(
            tuple((coordinate,) for coordinate in image.coordinates),
            scalar_type=space.scalar_type,
        )
        coordinates = normalization.matmul(functionals.matmul(image_column))
        columns.append(tuple(coordinates[row][0] for row in range(len(representatives))))
    return Matrix(
        tuple(
            tuple(columns[column][row] for column in range(len(columns)))
            for row in range(len(representatives))
        ),
        scalar_type=space.scalar_type,
    )


def _fixed_representatives(
    representatives: tuple[CoordinateVector, ...],
    p_matrix: Matrix | None,
    t_matrix: Matrix | None,
) -> tuple[CoordinateVector, ...]:
    """Solve the exact trivial-character equations on cohomology coordinates."""

    if not representatives or p_matrix is None or t_matrix is None:
        return ()
    identity = Matrix.identity(len(representatives), scalar_type=Eisenstein)
    equations = Matrix(
        (*((p_matrix - identity).rows), *((t_matrix - identity).rows)),
        scalar_type=Eisenstein,
    )
    fixed = equations.nullspace()
    space = representatives[0].space
    return tuple(
        CoordinateVector(
            space,
            tuple(
                sum(
                    (
                        vector.values[index] * representatives[index].coordinates[row]
                        for index, vector in enumerate(fixed)
                    ),
                    Eisenstein(0),
                )
                for row in range(space.dimension)
            ),
        )
        for vector in fixed
    )


def _matrix_record(matrix: Matrix | None) -> list[list[str]] | None:
    """Serialize one exact matrix, preserving ``None`` for zero cohomology."""

    if matrix is None:
        return None
    return [[str(value) for value in row] for row in matrix.rows]


def _sparse_map_matrix_record(
    rows: tuple[tuple[object, ...], ...],
    column_count: int,
) -> dict[str, object]:
    """Serialize a typed map matrix by shape and nonzero entries."""

    return {
        "shape": [len(rows), column_count],
        "entries": [
            {
                "row": row,
                "column": column,
                "coefficient": str(value),
            }
            for row, values in enumerate(rows)
            for column, value in enumerate(values)
            if not value.is_zero()
        ],
    }


def _linear_map_record(map_: LinearMap) -> dict[str, object]:
    """Serialize one exact typed linear map with both ordered bases."""

    return {
        "domain": {
            "name": map_.domain.name,
            "basis": list(map_.domain.basis),
        },
        "codomain": {
            "name": map_.codomain.name,
            "basis": list(map_.codomain.basis),
        },
        "matrix": _sparse_map_matrix_record(
            map_.rows,
            map_.domain.dimension,
        ),
    }


def _chain_map_record(map_: ChainMap) -> dict[str, object]:
    """Serialize every component of one exact complex action."""

    return {
        "source_degrees": list(map_.source.degrees),
        "target_degrees": list(map_.target.degrees),
        "components": [
            {
                "degree": degree,
                "map": _linear_map_record(component),
            }
            for degree, component in map_.components
        ],
    }


def _reynolds_projector(
    p_matrix: Matrix | None,
    t_matrix: Matrix | None,
) -> Matrix | None:
    """Return the exact trivial-character projector when H¹ is nonzero."""

    if p_matrix is None or t_matrix is None:
        return None
    identity = Matrix.identity(p_matrix.row_count, scalar_type=Eisenstein)
    p_sum = identity + p_matrix + p_matrix.matmul(p_matrix)
    t_sum = identity + t_matrix + t_matrix.matmul(t_matrix)
    return p_sum.matmul(t_sum).scale(Eisenstein(1) / Eisenstein(9))


@dataclass(frozen=True, slots=True)
class ProjectiveHomDeckAudit:
    """Exact finite-group action and invariant audit for projective Hom data."""

    hypercohomology: ProjectiveHomHypercohomology
    h0_action_p: ChainMap
    h0_action_t: ChainMap
    h2_action_p: ChainMap
    h2_action_t: ChainMap
    h0_induced_p: Matrix | None
    h0_induced_t: Matrix | None
    h2_induced_p: Matrix | None
    h2_induced_t: Matrix | None
    h0_invariant_projector: Matrix | None
    h2_invariant_projector: Matrix | None
    h0_ext_representatives: tuple[CoordinateVector, ...]
    h2_ext_representatives: tuple[CoordinateVector, ...]
    h0_invariants: tuple[CoordinateVector, ...]
    h2_invariants: tuple[CoordinateVector, ...]

    @property
    def invariant_ext_one_dimension(self) -> int:
        """Return the trivial-character degree-one dimension."""

        return len(self.h0_invariants) + len(self.h2_invariants)

    @property
    def reynolds_projectors_idempotent(self) -> bool:
        """Return whether every defined trivial-character projector is exact."""

        return all(
            projector is None
            or projector.matmul(projector) == projector
            for projector in (
                self.h0_invariant_projector,
                self.h2_invariant_projector,
            )
        )

    @property
    def p_t_commute(self) -> bool:
        """Return the exact P/T commutation result on both complexes."""

        return all(
            left.compose(right) == right.compose(left)
            for left, right in (
                (self.h0_action_p, self.h0_action_t),
                (self.h2_action_p, self.h2_action_t),
            )
        )

    @property
    def p_order_three(self) -> bool:
        """Return the exact order-three result on both complexes."""

        return all(
            action.compose(action).compose(action) == ChainMap.identity(action.source)
            for action in (
                self.h0_action_p,
                self.h0_action_t,
                self.h2_action_p,
                self.h2_action_t,
            )
        )

    def _representative_record(
        self,
        representative: CoordinateVector,
    ) -> list[dict[str, str]]:
        """Serialize one sparse invariant representative."""

        return [
            {"basis": basis, "coefficient": str(coefficient)}
            for basis, coefficient in zip(
                representative.space.basis,
                representative.coordinates,
                strict=True,
            )
            if not coefficient.is_zero()
        ]

    def as_record(self) -> dict[str, object]:
        """Serialize exact action gates and invariant representatives."""

        return {
            "left_scheme": self.hypercohomology.parent.left.scheme.name,
            "right_scheme": self.hypercohomology.parent.right.scheme.name,
            "group_order": 9,
            "h0_ext1_dimension": len(self.h0_ext_representatives),
            "h2_ext_minus1_dimension": len(self.h2_ext_representatives),
            "invariant_ext1_dimension": self.invariant_ext_one_dimension,
            "invariant_h0_representative_count": len(self.h0_invariants),
            "invariant_h2_representative_count": len(self.h2_invariants),
            "h0_action_p": _chain_map_record(self.h0_action_p),
            "h0_action_t": _chain_map_record(self.h0_action_t),
            "h2_action_p": _chain_map_record(self.h2_action_p),
            "h2_action_t": _chain_map_record(self.h2_action_t),
            "h0_induced_p": _matrix_record(self.h0_induced_p),
            "h0_induced_t": _matrix_record(self.h0_induced_t),
            "h2_induced_p": _matrix_record(self.h2_induced_p),
            "h2_induced_t": _matrix_record(self.h2_induced_t),
            "h0_invariant_projector": _matrix_record(self.h0_invariant_projector),
            "h2_invariant_projector": _matrix_record(self.h2_invariant_projector),
            "reynolds_projectors_idempotent": self.reynolds_projectors_idempotent,
            "invariant_h0_representatives": [
                self._representative_record(item) for item in self.h0_invariants
            ],
            "invariant_h2_representatives": [
                self._representative_record(item) for item in self.h2_invariants
            ],
            "p_order_three": self.p_order_three,
            "p_t_commute": self.p_t_commute,
            "status": (
                "exact projective-presentation Z3 x Z3 invariant audit; dP9 "
                "sheafification and quotient descent remain unresolved"
            ),
        }


def projective_hom_deck_audit(
    hypercohomology: ProjectiveHomHypercohomology,
    left_candidate: SerrePushoutCandidate | None = None,
    right_candidate: SerrePushoutCandidate | None = None,
    resolution_pairs: tuple[ResolutionActionPair, ...] | None = None,
) -> ProjectiveHomDeckAudit:
    """Audit exact P/T actions on both projective Hom complexes.

    Optional candidates and resolution actions make the same exact audit
    reusable for every declared Tier A eigenray pair. The defaults preserve
    the original selected I3/I6 presentation route.
    """

    if (left_candidate is None) != (right_candidate is None):
        raise ValueError("both projective Hom candidates must be supplied together")
    if left_candidate is None:
        candidates = tier_a_serre_pushouts()
        left, right = candidates
    else:
        left, right = left_candidate, right_candidate
    pairs = tier_a_resolution_actions() if resolution_pairs is None else resolution_pairs
    if len(pairs) != 2:
        raise ValueError("projective Hom actions require I3 and I6 resolution pairs")
    left_pair, right_pair = pairs
    h0_action_p = _chain_action(
        hypercohomology.h0,
        _presentation_term_actions(
            "P", left_pair, right_pair, left.character_pair, right.character_pair
        ),
        left_pair.action("P").coordinate_images,
    )
    h0_action_t = _chain_action(
        hypercohomology.h0,
        _presentation_term_actions(
            "T", left_pair, right_pair, left.character_pair, right.character_pair
        ),
        left_pair.action("T").coordinate_images,
    )
    h2_action_p = _chain_action(
        hypercohomology.h2,
        _presentation_term_actions(
            "P", left_pair, right_pair, left.character_pair, right.character_pair
        ),
        left_pair.action("P").coordinate_images,
    )
    h2_action_t = _chain_action(
        hypercohomology.h2,
        _presentation_term_actions(
            "T", left_pair, right_pair, left.character_pair, right.character_pair
        ),
        left_pair.action("T").coordinate_images,
    )
    h0_ext_representatives = hypercohomology.h0.representatives(1)
    h2_ext_representatives = hypercohomology.h2.representatives(-1)
    h0_induced_p = _induced_cohomology_matrix(
        h0_action_p, hypercohomology.h0, 1, h0_ext_representatives
    )
    h0_induced_t = _induced_cohomology_matrix(
        h0_action_t, hypercohomology.h0, 1, h0_ext_representatives
    )
    h2_induced_p = _induced_cohomology_matrix(
        h2_action_p, hypercohomology.h2, -1, h2_ext_representatives
    )
    h2_induced_t = _induced_cohomology_matrix(
        h2_action_t, hypercohomology.h2, -1, h2_ext_representatives
    )
    return ProjectiveHomDeckAudit(
        hypercohomology=hypercohomology,
        h0_action_p=h0_action_p,
        h0_action_t=h0_action_t,
        h2_action_p=h2_action_p,
        h2_action_t=h2_action_t,
        h0_induced_p=h0_induced_p,
        h0_induced_t=h0_induced_t,
        h2_induced_p=h2_induced_p,
        h2_induced_t=h2_induced_t,
        h0_invariant_projector=_reynolds_projector(h0_induced_p, h0_induced_t),
        h2_invariant_projector=_reynolds_projector(h2_induced_p, h2_induced_t),
        h0_ext_representatives=h0_ext_representatives,
        h2_ext_representatives=h2_ext_representatives,
        h0_invariants=_fixed_representatives(
            h0_ext_representatives, h0_induced_p, h0_induced_t
        ),
        h2_invariants=_fixed_representatives(
            h2_ext_representatives, h2_induced_p, h2_induced_t
        ),
    )


def tier_a_projective_hom_deck_audit() -> ProjectiveHomDeckAudit:
    """Build the Tier A projective Hom action and invariant audit."""

    return projective_hom_deck_audit(tier_a_projective_hom_hypercohomology())


__all__ = [
    "ProjectiveHomDeckAudit",
    "projective_hom_deck_audit",
    "tier_a_projective_hom_deck_audit",
]
