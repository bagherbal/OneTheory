"""Derive deck characters on the unreduced diagonal Higgs candidate space.

Owns:
    Exact deck chain maps on the transferred diagonal tensor complex and the
    induced simultaneous-character decomposition of its degree-one cohomology.

Depends on:
    The synchronized diagonal transfer, source-aligned constituent frames,
    and sparse exact quotient elimination.

Must not:
    Select four classes from character labels when multiplicities are larger,
    identify excess cone cohomology with physical Higgs states, or fit an
    action from the published character table.

Phase 0:
    Research-only character diagnostic for the current diagonal cone tensor.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    _constituent_frame,
    _independent_columns,
    _matrix_from_columns,
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

from .diagonal_higgs_transfer import (
    DiagonalHiggsTransfer,
    _object_indices,
    _published_constituents,
    _reduced_entries,
    _space,
    _target_component,
    _tensor_objects,
    _transferred_map,
)

CharacterExponent = tuple[int, int]

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/diagonal_higgs_actions.json"


def _identity(space) -> SparseMap:
    """Return the exact sparse identity on one named space."""

    return SparseMap(
        space,
        space,
        _freeze_rows({index: Eisenstein(1)} for index in range(space.dimension)),
    )


@cache
def _diagonal_action_map(
    degree: int,
    action: SchoenSparseDeckAction,
) -> SparseMap:
    """Act on one reduced diagonal cochain degree before taking cohomology."""

    entries = _reduced_entries(degree)
    indices = {
        (entry.component, entry.monomials): entry.index for entry in entries
    }
    objects = _tensor_objects()
    object_indices = _object_indices()
    first, second = _published_constituents()
    first_frame = _constituent_frame(first, action.name)
    second_frame = _constituent_frame(second, action.name)
    diagonal_unit = action.p_images[0][0] * action.p_images[1][0]
    equation_units = (
        action.first_equation_unit,
        action.second_equation_unit,
        diagonal_unit,
    )
    rows: list[dict[int, Eisenstein]] = [dict() for _ in entries]
    for entry in entries:
        source_object = objects[entry.component.object_index]
        transformed_monomials = []
        geometric_scalar = Eisenstein(1)
        for monomial, images in zip(
            entry.monomials,
            (
                action.x_images,
                action.p_images,
                action.u_images,
                action.p_images,
            ),
            strict=True,
        ):
            scalar, transformed = _monomial_action(monomial, images)
            geometric_scalar *= scalar
            transformed_monomials.append(transformed)
        for equation in entry.component.subset:
            geometric_scalar *= equation_units[equation]
        for first_index in range(first_frame.row_count):
            first_scalar = first_frame[first_index][source_object.first_index]
            if first_scalar.is_zero():
                continue
            for second_index in range(second_frame.row_count):
                second_scalar = second_frame[second_index][source_object.second_index]
                if second_scalar.is_zero():
                    continue
                target_component = _target_component(
                    object_indices[(first_index, second_index)],
                    entry.component.subset,
                )
                target = indices[(target_component, tuple(transformed_monomials))]
                rows[target][entry.index] = rows[target].get(
                    entry.index,
                    Eisenstein(0),
                ) + geometric_scalar * first_scalar * second_scalar
    return SparseMap(_space(degree), _space(degree), _freeze_rows(rows))


def _simultaneous_multiplicity(
    first: Matrix,
    second: Matrix,
    first_value: Eisenstein,
    second_value: Eisenstein,
) -> int:
    """Return one exact simultaneous eigenspace dimension."""

    identity = Matrix.identity(first.row_count, scalar_type=Eisenstein)
    equations = Matrix(
        (
            *((first - identity.scale(first_value)).rows),
            *((second - identity.scale(second_value)).rows),
        ),
        scalar_type=Eisenstein,
    )
    return len(equations.nullspace())


@dataclass(frozen=True, slots=True)
class DiagonalHiggsDeckAudit:
    """Exact cohomological deck representation of the current diagonal tensor."""

    transfer: DiagonalHiggsTransfer
    representatives: SparseMap
    p_cohomology: Matrix
    t_cohomology: Matrix
    character_multiplicities: tuple[tuple[CharacterExponent, int], ...]
    chain_maps_exact: bool
    group_relations_exact: bool

    @property
    def dimension(self) -> int:
        """Return the current degree-one cone cohomology dimension."""

        return self.representatives.domain.dimension

    @property
    def lawful_character_multiplicities(
        self,
    ) -> tuple[tuple[CharacterExponent, int], ...]:
        """Return multiplicities at the four source-required characters."""

        required = {(0, 1), (0, 2), (1, 2), (2, 1)}
        return tuple(
            item for item in self.character_multiplicities if item[0] in required
        )

    @property
    def characters_isolate_four_classes(self) -> bool:
        """Return whether the four lawful characters each occur exactly once."""

        return self.lawful_character_multiplicities == (
            ((0, 1), 1),
            ((0, 2), 1),
            ((1, 2), 1),
            ((2, 1), 1),
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact decomposition and its fail-closed conclusion."""

        return {
            "current_cone_h1_dimension": self.dimension,
            "character_multiplicities": [
                [list(character), multiplicity]
                for character, multiplicity in self.character_multiplicities
            ],
            "source_required_characters": [[0, 1], [0, 2], [1, 2], [2, 1]],
            "lawful_character_multiplicities": [
                [list(character), multiplicity]
                for character, multiplicity in self.lawful_character_multiplicities
            ],
            "chain_maps_exact": self.chain_maps_exact,
            "group_relations_exact": self.group_relations_exact,
            "characters_isolate_four_classes": self.characters_isolate_four_classes,
            "character_projection_promoted": False,
            "status": (
                "scoped no-go: deck characters do not isolate the four derived "
                "P1 Higgs classes inside the current excess cone cohomology"
            ),
        }


@cache
def diagonal_higgs_deck_audit() -> DiagonalHiggsDeckAudit:
    """Derive the exact deck representation without importing expected ranks."""

    maps_with_depths = tuple(
        (degree, _transferred_map(degree)) for degree in (0, 1)
    )
    transfer = DiagonalHiggsTransfer(
        tuple((degree, _space(degree)) for degree in (0, 1, 2)),
        tuple((degree, item[0]) for degree, item in maps_with_depths),
        tuple((degree, item[1]) for degree, item in maps_with_depths),
    )
    if not transfer.squared_zero:
        raise ValueError("the degree-one diagonal transfer is not square zero")
    maps = dict(transfer.differentials)
    degree = 1
    incoming = maps[degree - 1]
    outgoing = maps[degree]
    cycles = outgoing.kernel_inclusion()
    selected = _cohomology_complement_columns(incoming, cycles)
    representatives = _select_columns(cycles, selected, "diagonal-H1")
    boundary_columns = _independent_columns(incoming)
    representative_columns = tuple(_columns(representatives))
    solver = _SparseSpanSolver(boundary_columns + representative_columns)
    boundary_dimension = len(boundary_columns)

    cohomology_actions = {}
    chain_maps_exact = True
    group_relations_exact = True
    for action in schoen_sparse_deck_actions():
        action_maps = {
            item_degree: _diagonal_action_map(item_degree, action)
            for item_degree in (0, 1, 2)
        }
        chain_maps_exact &= (
            maps[0].compose(action_maps[0])
            == action_maps[1].compose(maps[0])
            and maps[1].compose(action_maps[1])
            == action_maps[2].compose(maps[1])
        )
        group_relations_exact &= (
            action_maps[1].compose(action_maps[1]).compose(action_maps[1])
            == _identity(action_maps[1].domain)
        )
        columns = []
        for source in representative_columns:
            source_map = SparseMap(
                representatives.domain.__class__("one", ("one",), Eisenstein),
                representatives.codomain,
                _freeze_rows(
                    ({0: source[row]} if row in source else {})
                    for row in range(representatives.codomain.dimension)
                ),
            )
            image = next(iter(_columns(action_maps[1].compose(source_map))))
            coordinates = solver.coordinates(image)
            columns.append(
                {
                    index - boundary_dimension: value
                    for index, value in coordinates.items()
                    if index >= boundary_dimension
                }
            )
        cohomology_actions[action.name] = _matrix_from_columns(
            tuple(columns),
            len(representative_columns),
        )

    p_cohomology = cohomology_actions["P"]
    t_cohomology = cohomology_actions["T"]
    group_relations_exact &= (
        p_cohomology @ t_cohomology == t_cohomology @ p_cohomology
        and p_cohomology**3
        == Matrix.identity(p_cohomology.row_count, scalar_type=Eisenstein)
        and t_cohomology**3
        == Matrix.identity(t_cohomology.row_count, scalar_type=Eisenstein)
    )
    character_values = (Eisenstein(1), OMEGA, OMEGA2)
    multiplicities = tuple(
        ((first, second), multiplicity)
        for first, first_value in enumerate(character_values)
        for second, second_value in enumerate(character_values)
        if (
            multiplicity := _simultaneous_multiplicity(
                p_cohomology,
                t_cohomology,
                first_value,
                second_value,
            )
        )
    )
    result = DiagonalHiggsDeckAudit(
        transfer,
        representatives,
        p_cohomology,
        t_cohomology,
        multiplicities,
        chain_maps_exact,
        group_relations_exact,
    )
    if not result.chain_maps_exact or not result.group_relations_exact:
        raise ValueError("the diagonal Higgs deck action failed an exact gate")
    return result


def write_diagonal_higgs_deck_audit(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed exact character diagnostic."""

    payload: dict[str, object] = {
        "schema": "diagonal-higgs-actions-v1",
        **diagonal_higgs_deck_audit().as_record(),
        "published_character_table_used_as_action_input": False,
        "full_higgs_representatives_constructed": False,
        "next_required_object": (
            "a twist-natural relative chain correction and its lift through "
            "the diagonal Schoen Cech-Koszul contraction"
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
    """Regenerate the exact diagonal Higgs character diagnostic."""

    payload = write_diagonal_higgs_deck_audit()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"character_multiplicities: {payload['character_multiplicities']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DiagonalHiggsDeckAudit",
    "OUTPUT",
    "diagonal_higgs_deck_audit",
    "write_diagonal_higgs_deck_audit",
]
