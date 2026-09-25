"""Transfer deck actions on the selected mixed outer-Hom complexes.

Owns:
    Source-character homogeneous frames, exact full-Cech pullback, perturbed
    action transfer, induced cohomology actions, and strict invariant classes.

Depends on:
    Selected mixed constituent arrows, their exact outer-Hom transfer, the
    published Schoen deck action, and reusable sparse cohomology machinery.

Must not:
    Reuse retired trivial-ray frames, import expected invariant dimensions,
    select an outer extension coordinate, or infer a physical spectrum.

Phase 0:
    Research-only strict deck transfer on lawful mixed cover cohomology.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.homological import VectorSpace
from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.resolution_actions import (
    tier_a_resolution_actions,
)
from research.experiments.computable_carrier.schoen_serre_outer import (
    SchoenSerreConstituent,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    ReducedBasisEntry,
    SparseOuterCechCochain,
    _cech_differential,
    _components,
    _homotopy,
    _include,
    _projection_index,
    _reduced_basis,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    _block_diagonal,
    _cell_image,
    _fixed_coordinates,
    _independent_columns,
    _koszul_unit,
    _matrix_from_columns,
    _sparse_map_from_matrix,
    _SparseSpanSolver,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    SchoenSparseDeckAction,
    _monomial_action,
    schoen_sparse_deck_actions,
)
from research.experiments.computable_carrier.schoen_sparse_outer import (
    SparseMap,
    _freeze_rows,
)
from research.experiments.computable_carrier.schoen_sparse_outer_actions import (
    _cohomology_complement_columns,
    _columns,
    _select_columns,
)

from .mixed_constituent_schoen_arrows import (
    MixedSchoenConstituent,
    mixed_schoen_constituents,
)
from .mixed_schoen_outer_transfer import (
    MixedSchoenComplex,
    MixedTransferredOuterHom,
    _CompatibleTermIndex,
    _mixed_perturbation,
    _skeleton,
    mixed_outer_transfers,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_outer_actions.json"


def _basis_record(basis: OuterCechBasis) -> dict[str, object]:
    """Serialize one full Cech--Koszul basis label exactly."""

    component = basis.component
    return {
        "left_object": component.left_index,
        "right_object": component.right_index,
        "object_degree": component.object_degree,
        "line_degree": list(component.line_degree),
        "koszul_summand": component.koszul_summand,
        "x_monomial": list(basis.x_monomial),
        "u_monomial": list(basis.u_monomial),
        "p_monomial": list(basis.p_monomial),
        "cell": [list(simplex) for simplex in basis.cell],
    }


def _cech_record(
    cochain: SparseOuterCechCochain,
    name: str,
) -> dict[str, object]:
    """Serialize one strict invariant full-complex representative."""

    return {
        "name": name,
        "term_count": len(cochain.terms),
        "terms": [
            {
                "basis": _basis_record(basis),
                "coefficient": str(coefficient),
            }
            for basis, coefficient in cochain.terms
        ],
    }


def _source_character(
    constituent: MixedSchoenConstituent,
    generator: str,
) -> Eisenstein:
    """Return the selected character in the common-factor orientation."""

    index = 0 if generator == "P" else 1
    character = constituent.full.alignment.source_character[index]
    if constituent.factor == 2 and generator == "P":
        character = Eisenstein(1) / character
    return character


@cache
def _constituent_frame(
    factor: int,
    generator: str,
) -> Matrix:
    """Return the exact homogeneous object frame of one mixed constituent."""

    if factor == 0:
        return Matrix.identity(1, scalar_type=Eisenstein)
    constituent = mixed_schoen_constituents()[factor - 1]
    resolution = tier_a_resolution_actions()[factor - 1].action(generator)
    target = resolution.target_action
    source = resolution.source_action
    if constituent.factor == 2:
        target = target.inverse()
        source = source.inverse()
    return _block_diagonal(
        Matrix(
            ((_source_character(constituent, generator),),),
            scalar_type=Eisenstein,
        ),
        target,
        source,
    )


def _full_action(
    cochain: SparseOuterCechCochain,
    left: MixedSchoenComplex,
    right: MixedSchoenComplex,
    action: SchoenSparseDeckAction,
    frames: tuple[Matrix, Matrix] | None = None,
) -> SparseOuterCechCochain:
    """Apply exact pullback and declared frame conjugation on full cochains."""

    if frames is None:
        frames = (
            _constituent_frame(left.factor, action.name),
            _constituent_frame(right.factor, action.name),
        )
    left_frame, right_frame = frames
    right_inverse = right_frame.inverse()
    left_skeleton = _skeleton(left)
    right_skeleton = _skeleton(right)
    lookup = {
        (item.left_index, item.right_index, item.koszul_summand): item
        for item in _components(left_skeleton, right_skeleton)
    }
    result: list[tuple[OuterCechBasis, Eisenstein]] = []
    for basis, coefficient in cochain.terms:
        x_scalar, x_target = _monomial_action(
            basis.x_monomial,
            action.x_images,
        )
        u_scalar, u_target = _monomial_action(
            basis.u_monomial,
            action.u_images,
        )
        p_scalar, p_target = _monomial_action(
            basis.p_monomial,
            action.p_images,
        )
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
            left_coefficient = left_frame[target_left][
                basis.component.left_index
            ]
            if left_coefficient.is_zero():
                continue
            for target_right in range(right_inverse.column_count):
                right_coefficient = right_inverse[
                    basis.component.right_index
                ][target_right]
                if right_coefficient.is_zero():
                    continue
                component = lookup[
                    (
                        target_left,
                        target_right,
                        basis.component.koszul_summand,
                    )
                ]
                result.append(
                    (
                        OuterCechBasis(
                            component,
                            cast(tuple[int, int, int], x_target),
                            cast(tuple[int, int, int], u_target),
                            cast(tuple[int, int], p_target),
                            target_cell,
                        ),
                        geometric * left_coefficient * right_coefficient,
                    )
                )
    return SparseOuterCechCochain(tuple(result))


@dataclass(slots=True)
class _MixedContraction:
    """Reusable exact perturbation data for one mixed outer orientation."""

    left: MixedSchoenComplex
    right: MixedSchoenComplex
    left_skeleton: SchoenSerreConstituent = field(init=False)
    right_skeleton: SchoenSerreConstituent = field(init=False)
    components: dict[tuple[int, int, str], OuterCechComponent] = field(
        init=False
    )
    left_index: _CompatibleTermIndex = field(init=False)
    right_index: _CompatibleTermIndex = field(init=False)

    def __post_init__(self) -> None:
        self.left_skeleton = _skeleton(self.left)
        self.right_skeleton = _skeleton(self.right)
        self.components = {
            (item.left_index, item.right_index, item.koszul_summand): item
            for item in _components(self.left_skeleton, self.right_skeleton)
        }
        self.left_index = _CompatibleTermIndex(self.left)
        self.right_index = _CompatibleTermIndex(self.right)

    def perturbation(
        self,
        cochain: SparseOuterCechCochain,
    ) -> SparseOuterCechCochain:
        """Apply the complete non-Cech mixed perturbation."""

        return _mixed_perturbation(
            cochain,
            self.left,
            self.right,
            self.left_skeleton,
            self.right_skeleton,
            self.components,
            self.left_index,
            self.right_index,
        )

    def differential(
        self,
        cochain: SparseOuterCechCochain,
    ) -> SparseOuterCechCochain:
        """Apply the full mixed outer differential."""

        return _cech_differential(cochain) + self.perturbation(cochain)


def _perturbed_inclusion(
    cochain: SparseOuterCechCochain,
    contraction: _MixedContraction,
) -> tuple[SparseOuterCechCochain, int]:
    """Apply the finite ``(1 + h Delta)^-1`` inclusion series."""

    result = SparseOuterCechCochain()
    current = cochain
    depth = 0
    while not current.is_zero():
        result = result + current
        current = _homotopy(contraction.perturbation(current)).scale(-1)
        depth += 1
        if depth > 16:
            raise ValueError("mixed perturbed inclusion did not terminate")
    return result, depth


def _perturbed_projection(
    cochain: SparseOuterCechCochain,
    contraction: _MixedContraction,
    degree: int,
) -> tuple[dict[int, Eisenstein], int]:
    """Apply the finite ``p (1 + Delta h)^-1`` projection series."""

    entries = _reduced_basis(
        contraction.left_skeleton,
        contraction.right_skeleton,
        degree,
    )
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
            if target is None:
                continue
            value = result.get(target, Eisenstein(0)) + coefficient
            if value.is_zero():
                result.pop(target, None)
            else:
                result[target] = value
        current = contraction.perturbation(_homotopy(current)).scale(-1)
        depth += 1
        if depth > 16:
            raise ValueError("mixed perturbed projection did not terminate")
    return result, depth


def _reduced_cochain(
    entries: tuple[ReducedBasisEntry, ...],
    coefficients: dict[int, Eisenstein],
) -> SparseOuterCechCochain:
    """Include one sparse reduced vector in raw contraction coordinates."""

    result = SparseOuterCechCochain()
    for index, coefficient in coefficients.items():
        result = result + _include(entries[index]).scale(coefficient)
    return result


def _apply_transferred_action(
    coefficients: dict[int, Eisenstein],
    contraction: _MixedContraction,
    degree: int,
    action: SchoenSparseDeckAction,
    frames: tuple[Matrix, Matrix] | None = None,
) -> tuple[dict[int, Eisenstein], tuple[int, int]]:
    """Evaluate exact ``p' g i'`` on one sparse reduced cochain."""

    entries = _reduced_basis(
        contraction.left_skeleton,
        contraction.right_skeleton,
        degree,
    )
    included, inclusion_depth = _perturbed_inclusion(
        _reduced_cochain(entries, coefficients),
        contraction,
    )
    acted = _full_action(
        included,
        contraction.left,
        contraction.right,
        action,
        frames,
    )
    projected, projection_depth = _perturbed_projection(
        acted,
        contraction,
        degree,
    )
    return projected, (inclusion_depth, projection_depth)


def _action_job(
    job: tuple[int, int, str, dict[int, Eisenstein]],
) -> tuple[int, str, dict[int, Eisenstein], tuple[int, int]]:
    """Transfer one independent representative image in a worker process."""

    orientation, column, generator, coefficients = job
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    contraction = _orientation_contraction(orientation)
    image, depths = _apply_transferred_action(
        coefficients,
        contraction,
        1,
        actions[generator],
    )
    return column, generator, image, depths


@cache
def _orientation_contraction(orientation: int) -> _MixedContraction:
    """Return one process-local contraction without hashing constituent data."""

    constituents = mixed_schoen_constituents()
    if orientation == 0:
        return _MixedContraction(*constituents)
    if orientation == 1:
        return _MixedContraction(*tuple(reversed(constituents)))
    raise ValueError("mixed outer orientation is zero or one")


@dataclass(frozen=True, slots=True)
class MixedCohomologyDeckAction:
    """Exact P/T representation on one selected mixed cover cohomology."""

    transferred: MixedTransferredOuterHom
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
        """Return the exact common fixed dimension."""

        return self.invariant_coordinates.column_count

    @property
    def group_relations(self) -> bool:
        """Return exact order-three and commutator gates."""

        identity = Matrix.identity(
            self.p_induced.row_count,
            scalar_type=Eisenstein,
        )
        return (
            self.p_induced @ self.p_induced @ self.p_induced == identity
            and self.t_induced @ self.t_induced @ self.t_induced == identity
            and self.p_induced @ self.t_induced
            == self.t_induced @ self.p_induced
        )

    @property
    def exact(self) -> bool:
        """Return all transferred and strict-representative gates."""

        return (
            self.images_are_cycles
            and self.group_relations
            and self.full_representatives_are_cycles
            and self.full_representatives_are_invariant
        )

    def as_record(self) -> dict[str, object]:
        """Serialize induced matrices and invariant dimensions exactly."""

        def matrix_record(matrix: Matrix) -> list[list[str]]:
            return [[str(value) for value in row] for row in matrix.rows]
        return {
            "left": self.transferred.left,
            "right": self.transferred.right,
            "degree": self.degree,
            "cover_cohomology_dimension": self.representatives.domain.dimension,
            "P": matrix_record(self.p_induced),
            "T": matrix_record(self.t_induced),
            "invariant_dimension": self.invariant_dimension,
            "strict_invariant_representative_count": len(
                self.invariant_full_cech
            ),
            "full_cech_koszul_representatives": [
                _cech_record(cochain, f"invariant:{index}")
                for index, cochain in enumerate(self.invariant_full_cech)
            ],
            "maximum_action_depth": max(
                (max(left, right) for _name, left, right in self.action_depths),
                default=0,
            ),
            "images_are_cycles": self.images_are_cycles,
            "group_relations": self.group_relations,
            "full_representatives_are_cycles": (
                self.full_representatives_are_cycles
            ),
            "full_representatives_are_invariant": (
                self.full_representatives_are_invariant
            ),
            "exact": self.exact,
        }


def _average_full_invariant(
    cochain: SparseOuterCechCochain,
    contraction: _MixedContraction,
    p: SchoenSparseDeckAction,
    t: SchoenSparseDeckAction,
) -> SparseOuterCechCochain:
    """Apply the exact order-nine Reynolds projector on full cochains."""

    total = SparseOuterCechCochain()
    p_power = cochain
    for _ in range(3):
        term = p_power
        for _ in range(3):
            total = total + term
            term = _full_action(term, contraction.left, contraction.right, t)
        p_power = _full_action(
            p_power,
            contraction.left,
            contraction.right,
            p,
        )
    return total.scale(Eisenstein(1) / 9)


def _cohomology_action(
    orientation: int,
    transferred: MixedTransferredOuterHom,
    computed: dict[tuple[int, str], tuple[dict[int, Eisenstein], tuple[int, int]]],
) -> MixedCohomologyDeckAction:
    """Assemble exact induced actions and strict invariant representatives."""

    constituents = mixed_schoen_constituents()
    left, right = (
        constituents
        if orientation == 0
        else tuple(reversed(constituents))
    )
    contraction = _orientation_contraction(orientation)
    spaces = dict(transferred.spaces)
    differentials = dict(transferred.differentials)
    outgoing = differentials[1]
    incoming = differentials[0]
    cycles = outgoing.kernel_inclusion()
    selected = _cohomology_complement_columns(incoming, cycles)
    representatives = _select_columns(cycles, selected, "H1:representatives")
    boundary_columns = _independent_columns(incoming)
    representative_columns = tuple(_columns(representatives))
    solver = _SparseSpanSolver(boundary_columns + representative_columns)
    boundary_dimension = len(boundary_columns)
    induced: dict[str, Matrix] = {}
    depths = []
    images_are_cycles = True
    for generator in ("P", "T"):
        columns = []
        for column in range(len(representative_columns)):
            image, depth = computed[(column, generator)]
            depths.append((generator, *depth))
            cycle_map = SparseMap(
                VectorSpace("one", ("one",), Eisenstein),
                spaces[1],
                _freeze_rows(
                    ({0: image[row]} if row in image else {})
                    for row in range(spaces[1].dimension)
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
        induced[generator] = _matrix_from_columns(
            tuple(columns),
            len(representative_columns),
        )
    p_induced = induced["P"]
    t_induced = induced["T"]
    invariant_coordinates = _fixed_coordinates(p_induced, t_induced)
    representative_matrix = _matrix_from_columns(
        representative_columns,
        spaces[1].dimension,
    )
    invariant_matrix = representative_matrix @ invariant_coordinates
    provisional = _sparse_map_from_matrix(
        invariant_matrix,
        "H1:invariant-provisional",
        spaces[1],
    )
    entries = _reduced_basis(
        contraction.left_skeleton,
        contraction.right_skeleton,
        1,
    )
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    invariant_full = []
    invariant_reduced = []
    for provisional_column in _columns(provisional):
        included, _depth = _perturbed_inclusion(
            _reduced_cochain(entries, provisional_column),
            contraction,
        )
        averaged = _average_full_invariant(
            included,
            contraction,
            actions["P"],
            actions["T"],
        )
        projected, _depth = _perturbed_projection(averaged, contraction, 1)
        invariant_full.append(averaged)
        invariant_reduced.append(projected)
    invariant_representatives = SparseMap(
        VectorSpace(
            "H1:invariant",
            tuple(f"invariant:{index}" for index in range(len(invariant_reduced))),
            Eisenstein,
        ),
        spaces[1],
        _freeze_rows(
            {
                column: values[row]
                for column, values in enumerate(invariant_reduced)
                if row in values
            }
            for row in range(spaces[1].dimension)
        ),
    )
    full_cycles = all(
        contraction.differential(representative).is_zero()
        for representative in invariant_full
    )
    full_invariant = all(
        _full_action(representative, left, right, actions["P"])
        == representative
        and _full_action(representative, left, right, actions["T"])
        == representative
        for representative in invariant_full
    )
    result = MixedCohomologyDeckAction(
        transferred,
        1,
        representatives,
        p_induced,
        t_induced,
        invariant_coordinates,
        invariant_representatives,
        tuple(invariant_full),
        tuple(depths),
        images_are_cycles,
        full_cycles,
        full_invariant,
    )
    if not result.exact:
        raise ValueError("mixed outer cohomology deck-action gate failed")
    return result


@cache
def mixed_outer_cohomology_deck_actions(
) -> tuple[MixedCohomologyDeckAction, MixedCohomologyDeckAction]:
    """Derive strict P/T actions on both lawful mixed Ext-one spaces."""

    transfers = mixed_outer_transfers()
    jobs: list[tuple[int, int, str, dict[int, Eisenstein]]] = []
    for orientation, transferred in enumerate(transfers):
        differentials = dict(transferred.differentials)
        cycles = differentials[1].kernel_inclusion()
        selected = _cohomology_complement_columns(differentials[0], cycles)
        chosen = _select_columns(cycles, selected, "H1:representatives")
        columns = tuple(_columns(chosen))
        jobs.extend(
            (orientation, column, generator, coefficients)
            for column, coefficients in enumerate(columns)
            for generator in ("P", "T")
        )
    with ProcessPoolExecutor(max_workers=min(8, len(jobs))) as executor:
        completed = tuple(executor.map(_action_job, jobs))
    by_orientation: list[
        dict[tuple[int, str], tuple[dict[int, Eisenstein], tuple[int, int]]]
    ] = [{}, {}]
    for job, result in zip(jobs, completed, strict=True):
        orientation = job[0]
        column, generator, image, depths = result
        by_orientation[orientation][(column, generator)] = image, depths
    return tuple(
        _cohomology_action(orientation, transferred, by_orientation[orientation])
        for orientation, transferred in enumerate(transfers)
    )  # type: ignore[return-value]


def write_mixed_outer_actions(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed strict mixed outer action certificate."""

    actions = mixed_outer_cohomology_deck_actions()
    payload: dict[str, object] = {
        "schema": "mixed-schoen-outer-actions-v1",
        "orientations": [item.as_record() for item in actions],
        "all_deck_actions_exact": all(item.exact for item in actions),
        "expected_invariant_dimensions_imported": False,
        "retired_pure_cech_frames_used": False,
        "outer_extension_coordinate_selected": False,
        "next_required_object": (
            "lawful universal rank-four extension over the nonzero mixed "
            "invariant Ext-one locus"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate both strict mixed outer deck-action certificates."""

    payload = write_mixed_outer_actions()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"all_deck_actions_exact: {payload['all_deck_actions_exact']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MixedCohomologyDeckAction",
    "mixed_outer_cohomology_deck_actions",
]
