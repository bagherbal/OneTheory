"""Lift lawful constituent matter classes to strict common-Schoen cocycles.

Owns:
    Exact deck-action transfer on synchronized constituent matter complexes,
    joint-character projectors, and strict full Cech--Koszul representatives.

Depends on:
    The selected mixed constituent arrows, their finite perturbation
    contractions, exact Schoen deck actions, and sparse linear algebra.

Must not:
    Choose an outer-extension point, identify constituent classes with classes
    of the universal cone, import expected character counts, or evaluate Yukawas.

Phase 0:
    Research-only strict matter representatives before universal-cone lifting.
"""

from __future__ import annotations

import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.homological import VectorSpace
from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
    _reduced_basis,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    _independent_columns,
    _matrix_from_columns,
    _SparseSpanSolver,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    SchoenSparseDeckAction,
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

from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_outer_actions import (
    _apply_transferred_action,
    _full_action,
    _MixedContraction,
    _perturbed_inclusion,
    _perturbed_projection,
    _reduced_cochain,
)
from .mixed_schoen_outer_transfer import (
    MixedTransferredOuterHom,
    mixed_schoen_unit,
    mixed_transferred_outer_hom,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/mixed_schoen_matter_representatives.json"
)
CHARACTERS = tuple((first, second) for first in range(3) for second in range(3))
Character = tuple[int, int]


def _cochain_digest(cochains: tuple[SparseOuterCechCochain, ...]) -> str:
    """Hash ordered exact full-complex representatives deterministically."""

    digest = hashlib.sha256()
    for cochain in cochains:
        for basis, coefficient in cochain.terms:
            record = (
                basis.component.left_index,
                basis.component.right_index,
                basis.component.object_degree,
                basis.component.line_degree,
                basis.component.koszul_summand,
                basis.x_monomial,
                basis.u_monomial,
                basis.p_monomial,
                basis.cell,
                coefficient.a.numerator,
                coefficient.a.denominator,
                coefficient.b.numerator,
                coefficient.b.denominator,
            )
            digest.update(repr(record).encode("ascii"))
            digest.update(b"\0")
        digest.update(b"\xff")
    return digest.hexdigest()


def _matrix_from_sparse_columns(
    columns: tuple[dict[int, Eisenstein], ...],
    row_count: int,
) -> Matrix:
    """Build one exact matrix from sparse columns."""

    return Matrix(
        tuple(
            tuple(column.get(row, Eisenstein(0)) for column in columns)
            for row in range(row_count)
        ),
        scalar_type=Eisenstein,
    )


def _character_coordinates(
    p_action: Matrix,
    t_action: Matrix,
    character: Character,
) -> Matrix:
    """Return the exact simultaneous eigenspace for one deck character."""

    identity = Matrix.identity(p_action.row_count, scalar_type=Eisenstein)
    equations = Matrix(
        (
            *((p_action - identity.scale(OMEGA ** character[0])).rows),
            *((t_action - identity.scale(OMEGA ** character[1])).rows),
        ),
        scalar_type=Eisenstein,
    )
    vectors = equations.nullspace()
    return Matrix(
        tuple(
            tuple(vector[row] for vector in vectors)
            for row in range(p_action.row_count)
        ),
        scalar_type=Eisenstein,
    )


def _character_project(
    cochain: SparseOuterCechCochain,
    contraction: _MixedContraction,
    actions: dict[str, SchoenSparseDeckAction],
    character: Character,
) -> SparseOuterCechCochain:
    """Apply the normalized exact projector for one joint character."""

    total = SparseOuterCechCochain()
    p_power = cochain
    for p_exponent in range(3):
        term = p_power
        for t_exponent in range(3):
            weight = OMEGA ** (
                -character[0] * p_exponent - character[1] * t_exponent
            )
            total = total + term.scale(weight)
            term = _full_action(
                term,
                contraction.left,
                contraction.right,
                actions["T"],
            )
        p_power = _full_action(
            p_power,
            contraction.left,
            contraction.right,
            actions["P"],
        )
    return total.scale(Eisenstein(1) / 9)


@cache
def _matter_contraction(factor: int) -> _MixedContraction:
    """Return one process-local synchronized constituent contraction."""

    if factor not in (1, 2):
        raise ValueError("matter constituent factor must be one or two")
    return _MixedContraction(
        mixed_schoen_constituents()[factor - 1],
        mixed_schoen_unit(),
    )


def _matter_action_job(
    job: tuple[int, int, str, dict[int, Eisenstein]],
) -> tuple[int, str, dict[int, Eisenstein], tuple[int, int]]:
    """Transfer one constituent representative image in a worker process."""

    factor, column, generator, coefficients = job
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    image, depths = _apply_transferred_action(
        coefficients,
        _matter_contraction(factor),
        1,
        actions[generator],
    )
    return column, generator, image, depths


@dataclass(frozen=True, slots=True)
class MatterCharacterSector:
    """Strict full-complex basis for one constituent deck character."""

    character: Character
    reduced_coordinates: Matrix
    full_representatives: tuple[SparseOuterCechCochain, ...]

    @property
    def dimension(self) -> int:
        """Return the exact multiplicity of this character."""

        return self.reduced_coordinates.column_count


@dataclass(frozen=True, slots=True)
class MixedConstituentMatterRepresentatives:
    """Exact H1 action and strict character representatives for one constituent."""

    factor: int
    transferred: MixedTransferredOuterHom
    representatives: SparseMap
    p_induced: Matrix
    t_induced: Matrix
    sectors: tuple[MatterCharacterSector, ...]
    action_depths: tuple[tuple[str, int, int], ...]
    images_are_cycles: bool
    full_representatives_are_cycles: bool
    full_representatives_have_declared_characters: bool

    @property
    def group_relations(self) -> bool:
        """Return exact order-three and commutator gates."""

        identity = Matrix.identity(
            self.p_induced.row_count,
            scalar_type=Eisenstein,
        )
        return (
            self.p_induced**3 == identity
            and self.t_induced**3 == identity
            and self.p_induced @ self.t_induced
            == self.t_induced @ self.p_induced
        )

    @property
    def exact(self) -> bool:
        """Return every action, cycle, character, and spanning gate."""

        return (
            self.images_are_cycles
            and self.group_relations
            and self.full_representatives_are_cycles
            and self.full_representatives_have_declared_characters
            and sum(sector.dimension for sector in self.sectors)
            == self.representatives.domain.dimension
        )

    def as_record(self) -> dict[str, object]:
        """Serialize dimensions and strict representative certificates."""

        all_representatives = tuple(
            representative
            for sector in self.sectors
            for representative in sector.full_representatives
        )
        return {
            "constituent": self.transferred.left,
            "factor": self.factor,
            "cohomology_degree": 1,
            "h1_dimension": self.representatives.domain.dimension,
            "character_sectors": [
                {
                    "character_exponents": list(sector.character),
                    "multiplicity": sector.dimension,
                    "strict_representative_term_counts": [
                        len(representative.terms)
                        for representative in sector.full_representatives
                    ],
                }
                for sector in self.sectors
            ],
            "strict_representative_digest": _cochain_digest(all_representatives),
            "maximum_action_depth": max(
                (max(left, right) for _name, left, right in self.action_depths),
                default=0,
            ),
            "images_are_cycles": self.images_are_cycles,
            "group_relations": self.group_relations,
            "full_representatives_are_cycles": self.full_representatives_are_cycles,
            "full_representatives_have_declared_characters": (
                self.full_representatives_have_declared_characters
            ),
            "exact": self.exact,
        }


def _assemble_constituent(
    factor: int,
    transferred: MixedTransferredOuterHom,
    computed: dict[tuple[int, str], tuple[dict[int, Eisenstein], tuple[int, int]]],
) -> MixedConstituentMatterRepresentatives:
    """Assemble induced actions and strict character lifts for one constituent."""

    contraction = _matter_contraction(factor)
    spaces = dict(transferred.spaces)
    differentials = dict(transferred.differentials)
    outgoing = differentials[1]
    incoming = differentials[0]
    cycles = outgoing.kernel_inclusion()
    selected = _cohomology_complement_columns(incoming, cycles)
    representatives = _select_columns(cycles, selected, "H1:matter-representatives")
    independent_boundaries = _independent_columns(incoming)
    representative_columns = tuple(_columns(representatives))
    solver = _SparseSpanSolver(independent_boundaries + representative_columns)
    boundary_dimension = len(independent_boundaries)
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
    representative_matrix = _matrix_from_sparse_columns(
        representative_columns,
        spaces[1].dimension,
    )
    entries = _reduced_basis(
        contraction.left_skeleton,
        contraction.right_skeleton,
        1,
    )
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    sectors = []
    full_cycles = True
    full_characters = True
    for character in CHARACTERS:
        coordinates = _character_coordinates(p_induced, t_induced, character)
        reduced_matrix = representative_matrix @ coordinates
        reduced_columns = tuple(
            {
                row: reduced_matrix[row][column]
                for row in range(reduced_matrix.row_count)
                if not reduced_matrix[row][column].is_zero()
            }
            for column in range(reduced_matrix.column_count)
        )
        cohomology_columns = tuple(
            {
                row: coordinates[row][column]
                for row in range(coordinates.row_count)
                if not coordinates[row][column].is_zero()
            }
            for column in range(coordinates.column_count)
        )
        strict = []
        for reduced_column, cohomology_column in zip(
            reduced_columns,
            cohomology_columns,
            strict=True,
        ):
            included, _depth = _perturbed_inclusion(
                _reduced_cochain(entries, reduced_column),
                contraction,
            )
            projected = _character_project(
                included,
                contraction,
                actions,
                character,
            )
            projected_reduced, _depth = _perturbed_projection(
                projected,
                contraction,
                1,
            )
            projected_coordinates = solver.coordinates(projected_reduced)
            projected_cohomology = {
                index - boundary_dimension: value
                for index, value in projected_coordinates.items()
                if index >= boundary_dimension
            }
            if projected_cohomology != cohomology_column:
                raise ValueError("strict character projector changed the H1 class")
            full_cycles = full_cycles and contraction.differential(projected).is_zero()
            full_characters = full_characters and all(
                _full_action(
                    projected,
                    contraction.left,
                    contraction.right,
                    actions[generator],
                )
                == projected.scale(OMEGA ** character[index])
                for index, generator in enumerate(("P", "T"))
            )
            strict.append(projected)
        sectors.append(MatterCharacterSector(character, coordinates, tuple(strict)))
    result = MixedConstituentMatterRepresentatives(
        factor,
        transferred,
        representatives,
        p_induced,
        t_induced,
        tuple(sectors),
        tuple(depths),
        images_are_cycles,
        full_cycles,
        full_characters,
    )
    if not result.exact:
        raise ValueError("mixed constituent matter representative gate failed")
    return result


@cache
def mixed_schoen_matter_representatives(
) -> tuple[
    MixedConstituentMatterRepresentatives,
    MixedConstituentMatterRepresentatives,
]:
    """Derive strict joint-character representatives for both constituents."""

    unit = mixed_schoen_unit()
    constituents = mixed_schoen_constituents()
    transfers = tuple(
        mixed_transferred_outer_hom(constituent, unit)
        for constituent in constituents
    )
    jobs: list[tuple[int, int, str, dict[int, Eisenstein]]] = []
    for factor, transferred in enumerate(transfers, start=1):
        differentials = dict(transferred.differentials)
        cycles = differentials[1].kernel_inclusion()
        selected = _cohomology_complement_columns(differentials[0], cycles)
        representatives = _select_columns(cycles, selected, "H1:matter-representatives")
        columns = tuple(_columns(representatives))
        jobs.extend(
            (factor, column, generator, coefficients)
            for column, coefficients in enumerate(columns)
            for generator in ("P", "T")
        )
    with ProcessPoolExecutor(max_workers=min(8, len(jobs))) as executor:
        completed = tuple(executor.map(_matter_action_job, jobs))
    by_factor: dict[
        int,
        dict[tuple[int, str], tuple[dict[int, Eisenstein], tuple[int, int]]],
    ] = {1: {}, 2: {}}
    for job, completed_job in zip(jobs, completed, strict=True):
        factor = job[0]
        column, generator, image, depths = completed_job
        by_factor[factor][(column, generator)] = image, depths
    return cast(
        tuple[
            MixedConstituentMatterRepresentatives,
            MixedConstituentMatterRepresentatives,
        ],
        tuple(
            _assemble_constituent(factor, transfer, by_factor[factor])
            for factor, transfer in enumerate(transfers, start=1)
        ),
    )


def write_mixed_schoen_matter_representatives(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed strict matter representative certificate."""

    representatives = mixed_schoen_matter_representatives()
    payload: dict[str, object] = {
        "schema": "mixed-schoen-matter-representatives-v1",
        "coefficient_field": "Q(omega)",
        "constituents": [item.as_record() for item in representatives],
        "all_strict_character_representatives_exact": all(
            item.exact for item in representatives
        ),
        "universal_cone_matter_lifts_computed": False,
        "outer_extension_coordinate_selected": False,
        "expected_character_multiplicities_imported": False,
        "next_required_object": (
            "parameter-dependent correction lifting the V2 character classes "
            "into the universal visible cone"
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
    """Regenerate the strict synchronized matter representative certificate."""

    payload = write_mixed_schoen_matter_representatives()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "all_strict_character_representatives_exact: "
        f"{payload['all_strict_character_representatives_exact']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MatterCharacterSector",
    "MixedConstituentMatterRepresentatives",
    "mixed_schoen_matter_representatives",
    "write_mixed_schoen_matter_representatives",
]
