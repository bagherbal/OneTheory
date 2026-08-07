"""Construct graded Tier B Serre extension-ray diagnostics.

Owns:
    The fixed-target-line graded dual presentations of the bounded monomial
    resolutions, their exact P/T quotient actions, full extension-map lifts,
    and support-local Fitting filtering.

Depends on:
    Tier B monomial schemes and resolution actions, exact Eisenstein linear
    algebra, and the reusable polynomial pushout relation and Fitting checks.
    It does not consume observations or numerical parameters.

Must not:
    Call a graded dual cokernel a global Ext group, treat a support-local
    Fitting ray as a descended sheaf, hide the fixed target-line convention,
    or claim dP9 gluing, stability, spectrum, or physical promotion.

Phase 0:
    The bounded graded Serre comparison is exact at presentation level; dP9
    chart sheafification, global frame comparison, honest linearization, and
    quotient descent remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.visible import PointScheme

from .resolution_actions import ResolutionAction
from .serre_pushout import _local_fitting_data, _relation_matrix
from .tier_b_monomial import (
    InvariantMonomialScheme,
    MonomialResolutionActionAudit,
    tier_b_invariant_monomial_schemes,
    tier_b_monomial_resolution_actions,
)

Monomial = tuple[int, ...]
BasisLabel = tuple[int, Monomial]
SparseVector = dict[int, Eisenstein]
CHARACTERS = (Eisenstein(1), OMEGA, OMEGA2)


def _monomials(total_degree: int, variable_count: int) -> tuple[Monomial, ...]:
    """Enumerate the exact monomial basis of one homogeneous degree."""

    if total_degree < 0:
        return ()
    return tuple(
        exponents
        for exponents in product(range(total_degree + 1), repeat=variable_count)
        if sum(exponents) == total_degree
    )


def _resolution_degrees(
    scheme: InvariantMonomialScheme,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Recover the homogeneous generator and syzygy shifts exactly."""

    generators = tuple(generator.degree for generator in scheme.ideal.generators)
    syzygies = []
    for column in range(len(scheme.resolution.matrix[0])):
        shifts = {
            generators[row] + scheme.resolution.matrix[row][column].degree
            for row in range(len(generators))
            if not scheme.resolution.matrix[row][column].is_zero()
        }
        if len(shifts) != 1:
            raise ValueError("Hilbert--Burch column has incompatible shifts")
        syzygies.append(next(iter(shifts)))
    return generators, tuple(syzygies)


def _dual_presentation(
    scheme: InvariantMonomialScheme,
    target_line_shift: int,
) -> tuple[
    tuple[int, ...],
    tuple[int, ...],
    tuple[BasisLabel, ...],
    tuple[BasisLabel, ...],
    Matrix | None,
]:
    """Build ``Hom(F_0,O(-e)) -> Hom(F_1,O(-e))`` in exact bases."""

    generator_degrees, syzygy_degrees = _resolution_degrees(scheme)
    variable_count = scheme.ideal.variable_count
    source_basis = tuple(
        (row, monomial)
        for row, degree in enumerate(generator_degrees)
        for monomial in _monomials(degree - target_line_shift, variable_count)
    )
    target_basis = tuple(
        (column, monomial)
        for column, degree in enumerate(syzygy_degrees)
        for monomial in _monomials(degree - target_line_shift, variable_count)
    )
    if not target_basis:
        raise ValueError("the declared Serre target line has no dual target basis")
    if not source_basis:
        return (
            generator_degrees,
            syzygy_degrees,
            source_basis,
            target_basis,
            None,
        )
    rows = []
    for column, target_monomial in target_basis:
        rows.append(
            tuple(
                scheme.resolution.matrix[row][column].coefficient(
                    tuple(
                        target - source
                        for target, source in zip(
                            target_monomial,
                            source_monomial,
                            strict=True,
                        )
                    )
                )
                if all(
                    target >= source
                    for target, source in zip(
                        target_monomial,
                        source_monomial,
                        strict=True,
                    )
                )
                else Eisenstein(0)
                for row, source_monomial in source_basis
            )
        )
    return (
        generator_degrees,
        syzygy_degrees,
        source_basis,
        target_basis,
        Matrix(rows, scalar_type=Eisenstein),
    )


def _inverse_images(
    images: tuple[tuple[Eisenstein, Monomial], ...],
) -> tuple[tuple[Eisenstein, Monomial], ...]:
    """Invert a monomial coordinate substitution exactly."""

    inverse: list[tuple[Eisenstein, Monomial] | None] = [None] * len(images)
    for source, (scalar, image) in enumerate(images):
        target = image.index(1)
        inverse[target] = (
            Eisenstein(1) / scalar,
            tuple(1 if index == source else 0 for index in range(len(images))),
        )
    if any(item is None for item in inverse):
        raise ValueError("coordinate action is not a permutation monomial map")
    return tuple(item for item in inverse if item is not None)


def _sparse_target_images(
    basis: tuple[BasisLabel, ...],
    action: ResolutionAction,
) -> tuple[SparseVector, ...]:
    """Return sparse inverse-substitution images of the dual target basis."""

    inverse_images = _inverse_images(action.coordinate_images)
    dual = action.source_action.transpose()
    index = {label: position for position, label in enumerate(basis)}
    images = []
    for source_label, monomial in basis:
        scalar = Eisenstein(1)
        image_monomial = [0] * len(monomial)
        for variable, power in enumerate(monomial):
            variable_scalar, variable_image = inverse_images[variable]
            scalar *= variable_scalar**power
            image_monomial = [
                current + power * exponent
                for current, exponent in zip(
                    image_monomial,
                    variable_image,
                    strict=True,
                )
            ]
        target_monomial = tuple(image_monomial)
        image: SparseVector = {}
        for target_label in range(dual.row_count):
            target_index = index.get((target_label, target_monomial))
            if target_index is None:
                raise ValueError("dual deck action escaped its graded target basis")
            value = dual[target_label][source_label] * scalar
            if not value.is_zero():
                image[target_index] = value
        images.append(image)
    return tuple(images)


def _target_action(
    basis: tuple[BasisLabel, ...],
    action: ResolutionAction,
) -> Matrix:
    """Build the inverse-substitution transpose action on the dual target."""

    images = _sparse_target_images(basis, action)
    rows = [[Eisenstein(0) for _ in basis] for _ in basis]
    for source_index, image in enumerate(images):
        for target_index, value in image.items():
            rows[target_index][source_index] = value
    return Matrix(rows, scalar_type=Eisenstein)


def _sparse_reduce(
    vector: SparseVector,
    image_basis: dict[int, SparseVector],
) -> SparseVector:
    """Reduce one target vector by a normalized sparse image basis."""

    result = dict(vector)
    for pivot in sorted(image_basis):
        coefficient = result.get(pivot, Eisenstein(0))
        if coefficient.is_zero():
            continue
        for index, value in image_basis[pivot].items():
            updated = result.get(index, Eisenstein(0)) - coefficient * value
            if updated.is_zero():
                result.pop(index, None)
            else:
                result[index] = updated
    return result


def _sparse_presentation_basis(presentation: Matrix) -> dict[int, SparseVector]:
    """Construct a normalized sparse basis for the presentation image."""

    image_basis: dict[int, SparseVector] = {}
    for column in range(presentation.column_count):
        vector = {
            row: presentation[row][column]
            for row in range(presentation.row_count)
            if not presentation[row][column].is_zero()
        }
        reduced = _sparse_reduce(vector, image_basis)
        if not reduced:
            continue
        pivot = min(reduced)
        leading = reduced[pivot]
        image_basis[pivot] = {
            index: value / leading for index, value in reduced.items()
        }
    return image_basis


def _apply_sparse_action(
    vector: SparseVector,
    basis_images: tuple[SparseVector, ...],
) -> SparseVector:
    """Apply a sparse target action to one sparse coordinate vector."""

    result: SparseVector = {}
    for source, coefficient in vector.items():
        for target, value in basis_images[source].items():
            updated = result.get(target, Eisenstein(0)) + coefficient * value
            if updated.is_zero():
                result.pop(target, None)
            else:
                result[target] = updated
    return result


def _target_vector_image(
    values: tuple[Eisenstein, ...],
    target_basis: tuple[BasisLabel, ...],
    action: ResolutionAction,
) -> tuple[Eisenstein, ...]:
    """Apply one exact target action without materializing a dense matrix."""

    vector = {
        index: value for index, value in enumerate(values) if not value.is_zero()
    }
    image = _apply_sparse_action(
        vector,
        _sparse_target_images(target_basis, action),
    )
    return tuple(image.get(index, Eisenstein(0)) for index in range(len(values)))


def _quotient_action(
    presentation: Matrix | None,
    target_basis: tuple[BasisLabel, ...],
    action: ResolutionAction,
) -> tuple[Matrix, bool, tuple[int, ...]]:
    """Descend one exact target action to a deterministic cokernel complement."""

    target_images = _sparse_target_images(target_basis, action)
    if presentation is None:
        representatives = tuple(range(len(target_basis)))
        return _target_action(target_basis, action), True, representatives
    image_basis = _sparse_presentation_basis(presentation)
    pivot_rows = tuple(sorted(image_basis))
    representatives = tuple(
        index
        for index in range(presentation.row_count)
        if index not in pivot_rows
    )
    quotient_columns: list[tuple[Eisenstein, ...]] = []
    preserves_relations = all(
        not _sparse_reduce(
            _apply_sparse_action(vector, target_images),
            image_basis,
        )
        for vector in image_basis.values()
    )
    for representative in representatives:
        reduced = _sparse_reduce(
            target_images[representative],
            image_basis,
        )
        quotient_columns.append(
            tuple(
                reduced.get(index, Eisenstein(0)) for index in representatives
            )
        )
    quotient = Matrix(zip(*quotient_columns, strict=True), scalar_type=Eisenstein)
    return quotient, preserves_relations, representatives


def _stacked_character_equations(
    left: Matrix,
    right: Matrix,
    left_character: Eisenstein,
    right_character: Eisenstein,
) -> Matrix:
    """Build exact simultaneous-character equations."""

    identity = Matrix.identity(left.row_count, scalar_type=Eisenstein)
    return Matrix(
        (
            *((left - identity.scale(left_character)).rows),
            *((right - identity.scale(right_character)).rows),
        ),
        scalar_type=Eisenstein,
    )


def _extension_map(
    target_basis: tuple[BasisLabel, ...],
    representative_indices: tuple[int, ...],
    quotient_vector: tuple[Eisenstein, ...],
) -> tuple[Polynomial, ...]:
    """Lift one quotient vector to its explicit graded extension map."""

    values = [Eisenstein(0) for _ in target_basis]
    for value, index in zip(quotient_vector, representative_indices, strict=True):
        values[index] = value
    column_count = max(label[0] for label in target_basis) + 1
    return tuple(
        Polynomial(
            tuple(
                (monomial, values[index])
                for index, (column, monomial) in enumerate(target_basis)
                if column == target_column and not values[index].is_zero()
            ),
            variable_count=3,
            scalar_type=Eisenstein,
        )
        for target_column in range(column_count)
    )


@dataclass(frozen=True, slots=True)
class TierBSerreDualAction:
    """One exact P/T action on a graded dual presentation quotient."""

    name: str
    matrix: Matrix
    preserves_relations: bool

    def as_record(self) -> dict[str, object]:
        """Serialize the quotient action and its finite group check."""

        return {
            "name": self.name,
            "matrix": [[str(value) for value in row] for row in self.matrix.rows],
            "preserves_relations": self.preserves_relations,
            "order_three": self.matrix**3
            == Matrix.identity(self.matrix.row_count, scalar_type=Eisenstein),
        }


@dataclass(frozen=True, slots=True)
class TierBSerreDualCokernel:
    """A fixed-target-line graded dual cokernel with exact representatives."""

    scheme: InvariantMonomialScheme
    target_line_shift: int
    generator_degrees: tuple[int, ...]
    syzygy_degrees: tuple[int, ...]
    source_basis: tuple[BasisLabel, ...]
    target_basis: tuple[BasisLabel, ...]
    presentation: Matrix | None
    representative_indices: tuple[int, ...]
    actions: tuple[TierBSerreDualAction, ...]

    @property
    def dimension(self) -> int:
        """Return the exact quotient dimension."""

        return len(self.representative_indices)

    def action(self, name: str) -> TierBSerreDualAction:
        """Return the named induced quotient action."""

        for action in self.actions:
            if action.name == name:
                return action
        raise KeyError(name)

    @property
    def actions_commute(self) -> bool:
        """Return whether the induced P/T actions commute exactly."""

        return self.action("P").matrix @ self.action("T").matrix == (
            self.action("T").matrix @ self.action("P").matrix
        )

    @property
    def relations_preserved(self) -> bool:
        """Return whether both actions preserve the graded relations."""

        return all(action.preserves_relations for action in self.actions)

    def as_record(self) -> dict[str, object]:
        """Serialize the graded comparison without a sheaf-level claim."""

        return {
            "scheme": self.scheme.name,
            "target_line_shift": self.target_line_shift,
            "generator_degrees": list(self.generator_degrees),
            "syzygy_degrees": list(self.syzygy_degrees),
            "source_basis": [[row, list(monomial)] for row, monomial in self.source_basis],
            "target_basis": [[column, list(monomial)] for column, monomial in self.target_basis],
            "presentation_shape": (
                None
                if self.presentation is None
                else list(self.presentation.shape)
            ),
            "presentation_rank": (
                0 if self.presentation is None else self.presentation.rank()
            ),
            "representative_indices": list(self.representative_indices),
            "dimension": self.dimension,
            "actions": [action.as_record() for action in self.actions],
            "relations_preserved": self.relations_preserved,
            "actions_commute": self.actions_commute,
            "status": (
                "exact fixed-target-line graded Serre comparison; global dP9 "
                "Ext, frame gluing, and quotient descent remain unresolved"
            ),
        }


@dataclass(frozen=True, slots=True)
class TierBSerreExtensionRay:
    """One full-action eigenray passing the support-local Fitting gate."""

    cokernel: TierBSerreDualCokernel
    character_pair: tuple[Eisenstein, Eisenstein]
    extension_map: tuple[Polynomial, ...]
    local_fitting: tuple[tuple[str, bool, tuple[int, ...]], ...]
    full_target_eigenvector: bool

    @property
    def locally_free_at_support(self) -> bool:
        """Return whether every declared support point has a unit minor."""

        return self.full_target_eigenvector and all(
            item[1] for item in self.local_fitting
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact extension map and local Fitting certificate."""

        return {
            "scheme": self.cokernel.scheme.name,
            "target_line_shift": self.cokernel.target_line_shift,
            "character_pair": [str(value) for value in self.character_pair],
            "extension_map": [
                {
                    "terms": [
                        {
                            "exponents": list(exponents),
                            "coefficient": str(coefficient),
                        }
                        for exponents, coefficient in polynomial.terms
                    ]
                }
                for polynomial in self.extension_map
            ],
            "local_fitting": [
                {
                    "point": point,
                    "unit_minor_exists": unit,
                    "unit_minor_indices": list(indices),
                }
                for point, unit, indices in self.local_fitting
            ],
            "full_target_eigenvector": self.full_target_eigenvector,
            "locally_free_at_support": self.locally_free_at_support,
            "status": (
                "support-local graded Serre eigenray; global dP9 sheafification, "
                "linearization, and quotient descent remain unresolved"
            ),
        }


def tier_b_serre_dual_cokernel(
    scheme: InvariantMonomialScheme,
    actions: MonomialResolutionActionAudit,
    target_line_shift: int = 3,
) -> TierBSerreDualCokernel:
    """Construct one exact fixed-target-line dual comparison."""

    if isinstance(target_line_shift, bool) or not isinstance(target_line_shift, int):
        raise TypeError("the target-line shift must be an integer")
    point_scheme = PointScheme(
        scheme.name,
        tuple(scheme.ideal.generators),
        scheme.resolution,
    )
    generator_degrees, syzygy_degrees, source_basis, target_basis, presentation = (
        _dual_presentation(scheme, target_line_shift)
    )
    quotient_actions = []
    representative_indices: tuple[int, ...] | None = None
    for resolution_action in actions.actions.actions:
        quotient, preserves_relations, representatives = _quotient_action(
            presentation,
            target_basis,
            resolution_action,
        )
        if representative_indices is None:
            representative_indices = representatives
        elif representative_indices != representatives:
            raise ValueError("P/T quotient complements are not identical")
        quotient_actions.append(
            TierBSerreDualAction(
                resolution_action.name,
                quotient,
                preserves_relations,
            )
        )
    if representative_indices is None:
        raise ValueError("a graded dual comparison requires P and T actions")
    result = TierBSerreDualCokernel(
        scheme,
        target_line_shift,
        generator_degrees,
        syzygy_degrees,
        source_basis,
        target_basis,
        presentation,
        representative_indices,
        tuple(quotient_actions),
    )
    if point_scheme.resolution.scheme_length != scheme.length:
        raise ValueError("Tier B point-scheme wrapper changed the exact length")
    return result


def tier_b_serre_dual_cokernels(
    schemes: tuple[InvariantMonomialScheme, ...] | None = None,
    actions: tuple[MonomialResolutionActionAudit, ...] | None = None,
    target_line_shift: int = 3,
) -> tuple[TierBSerreDualCokernel, ...]:
    """Construct graded dual comparisons for every bounded monomial scheme."""

    selected = tier_b_invariant_monomial_schemes() if schemes is None else schemes
    resolution_actions = (
        tier_b_monomial_resolution_actions(selected) if actions is None else actions
    )
    if len(selected) != len(resolution_actions):
        raise ValueError("Tier B dual comparisons require matching scheme and action counts")
    return tuple(
        tier_b_serre_dual_cokernel(scheme, action, target_line_shift)
        for scheme, action in zip(selected, resolution_actions, strict=True)
    )


def tier_b_serre_eigenrays(
    schemes: tuple[InvariantMonomialScheme, ...] | None = None,
    actions: tuple[MonomialResolutionActionAudit, ...] | None = None,
    target_line_shift: int = 3,
) -> tuple[TierBSerreExtensionRay, ...]:
    """Enumerate exact full-action rays passing support-local Fitting tests."""

    selected = tier_b_invariant_monomial_schemes() if schemes is None else schemes
    resolution_actions = (
        tier_b_monomial_resolution_actions(selected) if actions is None else actions
    )
    if len(selected) != len(resolution_actions):
        raise ValueError("Tier B eigenrays require matching scheme and action counts")
    actions_by_scheme = {
        scheme.name: action
        for scheme, action in zip(selected, resolution_actions, strict=True)
    }
    cokernels = tier_b_serre_dual_cokernels(
        selected,
        resolution_actions,
        target_line_shift,
    )
    results = []
    for cokernel in cokernels:
        p_action = cokernel.action("P").matrix
        t_action = cokernel.action("T").matrix
        for p_character in CHARACTERS:
            for t_character in CHARACTERS:
                equations = _stacked_character_equations(
                    p_action,
                    t_action,
                    p_character,
                    t_character,
                )
                for vector in equations.nullspace():
                    extension_map = _extension_map(
                        cokernel.target_basis,
                        cokernel.representative_indices,
                        vector.values,
                    )
                    point_scheme = PointScheme(
                        cokernel.scheme.name,
                        tuple(cokernel.scheme.ideal.generators),
                        cokernel.scheme.resolution,
                    )
                    full_vector = [Eisenstein(0) for _ in cokernel.target_basis]
                    for value, index in zip(
                        vector.values,
                        cokernel.representative_indices,
                        strict=True,
                    ):
                        full_vector[index] = value
                    full_target_eigenvector = all(
                        _target_vector_image(
                            tuple(full_vector),
                            cokernel.target_basis,
                            action,
                        )
                        == tuple(value * character for value in full_vector)
                        for action, character in zip(
                            actions_by_scheme[
                                cokernel.scheme.name
                            ].actions.actions,
                            (p_character, t_character),
                            strict=True,
                        )
                    )
                    local_fitting = _local_fitting_data(
                        _relation_matrix(point_scheme, extension_map),
                    )
                    result = TierBSerreExtensionRay(
                        cokernel,
                        (p_character, t_character),
                        extension_map,
                        local_fitting,
                        full_target_eigenvector,
                    )
                    if result.locally_free_at_support:
                        results.append(result)
    return tuple(results)


__all__ = [
    "TierBSerreDualAction",
    "TierBSerreDualCokernel",
    "TierBSerreExtensionRay",
    "tier_b_serre_dual_cokernel",
    "tier_b_serre_dual_cokernels",
    "tier_b_serre_eigenrays",
]
