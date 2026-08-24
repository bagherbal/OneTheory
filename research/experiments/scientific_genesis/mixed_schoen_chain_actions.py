"""Derive strict deck characters on the lawful mixed-Schoen chain transfer.

Owns:
    Exact P/T chain maps on the certified reduced transfer, its degree-one
    character decomposition, and strict full-complex Higgs representatives.

Depends on:
    The content-addressed lawful chain transfer, source-aligned constituent
    frames, published deck actions, and the verified Wilson character source.

Must not:
    Recompute a retired cone, fit an action, select geometry from observed
    flavor data, normalize a Yukawa trace, or infer a physical mass.

Phase 0:
    Research-only strict Higgs representative extraction.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    _independent_columns,
    _SparseSpanSolver,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    CoordinateImage,
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

from .diagonal_schoen_lines import Cell4, Monomial
from .mixed_schoen_chain_diagonal import (
    ChainDiagonalBasis,
    ChainDiagonalCochain,
    _object_indices,
    _reduced_entries,
    _target_component,
    chain_diagonal_objects,
    full_chain_diagonal_differential,
)
from .mixed_schoen_chain_transfer import (
    TransferredColumn,
    _homotopy,
    _include,
    _space,
    transferred_column,
)
from .mixed_schoen_outer_actions import _constituent_frame
from .mixed_schoen_universal_matter_lifts import (
    UP_HIGGS_CHARACTER,
    _source_digest,
)

Character = tuple[int, int]

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_chain_actions.json"


def _scalar_record(value: Eisenstein) -> list[int]:
    """Serialize one exact Eisenstein coefficient in rational coordinates."""

    return [
        value.a.numerator,
        value.a.denominator,
        value.b.numerator,
        value.b.denominator,
    ]


def _coordinate_permutation(images: CoordinateImage) -> tuple[int, ...]:
    """Return the target coordinate index of each monomial substitution."""

    permutation = tuple(exponents.index(1) for _scalar, exponents in images)
    if sorted(permutation) != list(range(len(images))):
        raise ValueError("the chain-diagonal cell action is not a permutation")
    return permutation


def _permutation_sign(values: tuple[int, ...]) -> int:
    """Return the orientation sign needed to sort distinct indices."""

    inversions = sum(
        values[left] > values[right]
        for left in range(len(values))
        for right in range(left + 1, len(values))
    )
    return -1 if inversions % 2 else 1


def _cell_image(
    cell: Cell4,
    action: SchoenSparseDeckAction,
) -> tuple[int, Cell4]:
    """Pull a four-factor oriented product-cover cell through one deck action."""

    permutations = tuple(
        _coordinate_permutation(images)
        for images in (
            action.x_images,
            action.p_images,
            action.u_images,
            action.p_images,
        )
    )
    sign = 1
    target = []
    for simplex, permutation in zip(cell, permutations, strict=True):
        image = tuple(permutation[index] for index in simplex)
        sign *= _permutation_sign(image)
        target.append(tuple(sorted(image)))
    return sign, cast(Cell4, tuple(target))


def _equation_units(action: SchoenSparseDeckAction) -> tuple[Eisenstein, ...]:
    """Return exact characters of both cubics and the fiber diagonal."""

    diagonal = action.p_images[0][0] * action.p_images[1][0]
    return action.first_equation_unit, action.second_equation_unit, diagonal


def _transformed_monomials(
    monomials: tuple[Monomial, Monomial, Monomial, Monomial],
    action: SchoenSparseDeckAction,
) -> tuple[Eisenstein, tuple[Monomial, Monomial, Monomial, Monomial]]:
    """Apply one exact deck substitution to all four Laurent monomials."""

    scalar = Eisenstein(1)
    transformed = []
    for monomial, images in zip(
        monomials,
        (
            action.x_images,
            action.p_images,
            action.u_images,
            action.p_images,
        ),
        strict=True,
    ):
        factor, target = _monomial_action(monomial, images)
        scalar *= factor
        transformed.append(target)
    return scalar, cast(
        tuple[Monomial, Monomial, Monomial, Monomial],
        tuple(transformed),
    )


@cache
def _reduced_action_map(
    degree: int,
    action: SchoenSparseDeckAction,
) -> SparseMap:
    """Act exactly on one reduced ambient-cohomology degree."""

    entries = _reduced_entries(degree)
    indices = {
        (entry.component, entry.monomials): entry.index for entry in entries
    }
    objects = chain_diagonal_objects()
    object_indices = _object_indices()
    first_frame = _constituent_frame(1, action.name)
    second_frame = _constituent_frame(2, action.name)
    equation_units = _equation_units(action)
    rows: list[dict[int, Eisenstein]] = [dict() for _ in entries]
    for entry in entries:
        source_object = objects[entry.component.object_index]
        geometric, transformed = _transformed_monomials(entry.monomials, action)
        for equation in entry.component.subset:
            geometric *= equation_units[equation]
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
                target = indices.get((target_component, transformed))
                if target is None:
                    raise ValueError("a deck action escaped the reduced transfer basis")
                rows[target][entry.index] = rows[target].get(
                    entry.index,
                    Eisenstein(0),
                ) + geometric * first_scalar * second_scalar
    space = _space(degree)
    return SparseMap(space, space, _freeze_rows(rows))


def _full_action(
    cochain: ChainDiagonalCochain,
    action: SchoenSparseDeckAction,
) -> ChainDiagonalCochain:
    """Apply exact pullback and constituent frames to a full chain cochain."""

    objects = chain_diagonal_objects()
    object_indices = _object_indices()
    first_frame = _constituent_frame(1, action.name)
    second_frame = _constituent_frame(2, action.name)
    equation_units = _equation_units(action)
    result = []
    for basis, coefficient in cochain.terms:
        source_object = objects[basis.component.object_index]
        geometric, transformed = _transformed_monomials(basis.monomials, action)
        cell_sign, target_cell = _cell_image(basis.cell, action)
        geometric *= cell_sign
        for equation in basis.component.subset:
            geometric *= equation_units[equation]
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
                    basis.component.subset,
                )
                result.append(
                    (
                        ChainDiagonalBasis(target_component, transformed, target_cell),
                        coefficient * geometric * first_scalar * second_scalar,
                    )
                )
    return ChainDiagonalCochain(tuple(result))


def _raw_reduced_cochain(
    degree: int,
    coefficients: dict[int, Eisenstein],
) -> ChainDiagonalCochain:
    """Include sparse reduced coordinates in the raw grouped contraction."""

    entries = _reduced_entries(degree)
    result = ChainDiagonalCochain()
    for index, coefficient in sorted(coefficients.items()):
        result = result + _include(entries[index]).scale(coefficient)
    return result


def _perturbed_inclusion(
    cochain: ChainDiagonalCochain,
) -> tuple[ChainDiagonalCochain, int]:
    """Apply the finite ``(1 + h Delta)^-1`` chain inclusion series."""

    from .mixed_schoen_chain_diagonal import chain_diagonal_perturbation

    result = ChainDiagonalCochain()
    current = cochain
    depth = 0
    while not current.is_zero():
        result = result + current
        current = _homotopy(chain_diagonal_perturbation(current)).scale(-1)
        depth += 1
        if depth > 24:
            raise ValueError("the strict Higgs inclusion did not terminate")
    return result, depth


def _identity(space: VectorSpace) -> SparseMap:
    """Return the exact sparse identity on one reduced space."""

    return SparseMap(
        space,
        space,
        _freeze_rows({index: Eisenstein(1)} for index in range(space.dimension)),
    )


@cache
def _character_basis(degree: int, character: Character) -> SparseMap:
    """Derive one exact simultaneous-character basis by Reynolds projection."""

    actions = {action.name: action for action in schoen_sparse_deck_actions()}
    p_action = _reduced_action_map(degree, actions["P"])
    t_action = _reduced_action_map(degree, actions["T"])
    projector = p_action.scale(0)
    p_power = _identity(p_action.domain)
    for p_exponent in range(3):
        term = p_power
        for t_exponent in range(3):
            character_factor = OMEGA ** (
                -character[0] * p_exponent - character[1] * t_exponent
            )
            projector = projector + term.scale(character_factor)
            term = t_action.compose(term)
        p_power = p_action.compose(p_power)
    projector = projector.scale(Eisenstein(1) / 9)
    columns = _independent_columns(projector)
    domain = VectorSpace(
        f"character-{character[0]}-{character[1]}-degree-{degree}",
        tuple(f"e{index}" for index in range(len(columns))),
        Eisenstein,
    )
    return SparseMap(
        domain,
        projector.codomain,
        _freeze_rows(
            {
                column: values[row]
                for column, values in enumerate(columns)
                if row in values
            }
            for row in range(projector.codomain.dimension)
        ),
    )


def _character_transfer_job(
    job: tuple[int, int],
) -> tuple[int, TransferredColumn]:
    """Transfer one ambient support coordinate in a worker process."""

    degree, source_index = job
    return source_index, transferred_column(degree, source_index)


@cache
def _character_differential(
    degree: int,
    character: Character,
) -> tuple[SparseMap, int]:
    """Transfer one differential only on a verified deck-character sector."""

    source = _character_basis(degree, character)
    target = _character_basis(degree + 1, character)
    source_columns = tuple(_columns(source))
    target_columns = tuple(_columns(target))
    solver = _SparseSpanSolver(target_columns)
    support_indices = tuple(
        sorted({index for column in source_columns for index in column})
    )
    jobs = tuple((degree, index) for index in support_indices)
    with ProcessPoolExecutor(max_workers=min(16, len(jobs))) as executor:
        completed = tuple(executor.map(_character_transfer_job, jobs, chunksize=4))
    transferred_by_source = dict(completed)
    coordinate_columns = []
    maximum_depth = 0
    for source_column in source_columns:
        ambient_values: dict[int, Eisenstein] = {}
        for source_index, source_coefficient in source_column.items():
            transferred = transferred_by_source[source_index]
            maximum_depth = max(maximum_depth, transferred.path_depth)
            for target_index, coefficient in transferred.entries:
                ambient_values[target_index] = ambient_values.get(
                    target_index,
                    Eisenstein(0),
                ) + source_coefficient * coefficient
        coordinate_columns.append(
            solver.coordinates(
                {
                    index: coefficient
                    for index, coefficient in ambient_values.items()
                    if not coefficient.is_zero()
                }
            )
        )
    return (
        SparseMap(
            source.domain,
            target.domain,
            _freeze_rows(
                {
                    column: values[row]
                    for column, values in enumerate(coordinate_columns)
                    if row in values
                }
                for row in range(target.domain.dimension)
            ),
        ),
        maximum_depth,
    )


def _strict_higgs_representative(
    representatives: SparseMap,
    character_basis: SparseMap,
) -> tuple[ChainDiagonalCochain, int]:
    """Lift the unique character-sector H1 class to the full lawful complex."""

    if representatives.domain.dimension != 1:
        raise ValueError("the required Higgs character cohomology is not one-dimensional")
    ambient = character_basis.compose(representatives)
    values = next(iter(_columns(ambient)))
    return _perturbed_inclusion(_raw_reduced_cochain(1, values))


def _cochain_record(cochain: ChainDiagonalCochain) -> dict[str, object]:
    """Serialize one strict full-complex representative exactly."""

    objects = chain_diagonal_objects()
    return {
        "term_count": len(cochain.terms),
        "terms": [
            {
                "object_pair": [
                    objects[basis.component.object_index].first_index,
                    objects[basis.component.object_index].second_index,
                ],
                "koszul_subset": list(basis.component.subset),
                "monomials": [list(monomial) for monomial in basis.monomials],
                "cell": [list(simplex) for simplex in basis.cell],
                "coefficient": str(coefficient),
            }
            for basis, coefficient in cochain.terms
        ],
    }


@dataclass(frozen=True, slots=True)
class MixedSchoenHiggsDeckAction:
    """The exact deck representation and strict required Higgs cocycle."""

    character_bases: tuple[tuple[int, SparseMap], ...]
    differentials: tuple[tuple[int, SparseMap], ...]
    path_depths: tuple[tuple[int, int], ...]
    representatives: SparseMap
    required_character: Character
    required_full_cochain: ChainDiagonalCochain
    inclusion_depth: int
    group_relations_exact: bool
    character_bases_exact: bool
    full_representative_is_cycle: bool
    full_representative_has_strict_character: bool
    source_archive_sha256: str

    @property
    def transferred_differential_squared_zero(self) -> bool:
        """Return whether the exact character-sector maps compose to zero."""

        maps = dict(self.differentials)
        return maps[1].compose(maps[0]).is_zero()

    @property
    def character_h1_dimension(self) -> int:
        """Return exact H1 dimension in the source-required character sector."""

        bases = dict(self.character_bases)
        maps = dict(self.differentials)
        return bases[1].domain.dimension - maps[0].rank() - maps[1].rank()

    @property
    def exact(self) -> bool:
        """Return whether every chain, group, cycle, and character gate closes."""

        return (
            self.transferred_differential_squared_zero
            and self.group_relations_exact
            and self.character_bases_exact
            and self.full_representative_is_cycle
            and self.full_representative_has_strict_character
        )

    @property
    def physical_higgs_representative_available(self) -> bool:
        """Return whether the source-required strict cover class is available."""

        return self.exact and self.character_h1_dimension == 1

    def as_record(self) -> dict[str, object]:
        """Serialize the exact character decomposition and strict cocycle."""

        return {
            "required_character": list(self.required_character),
            "ambient_space_dimensions": {
                str(degree): basis.codomain.dimension for degree, basis in self.character_bases
            },
            "character_space_dimensions": {
                str(degree): basis.domain.dimension for degree, basis in self.character_bases
            },
            "differential_ranks": {
                str(degree): map_.rank() for degree, map_ in self.differentials
            },
            "differentials": [
                {
                    "degree": degree,
                    "entries": [
                        [row, column, *_scalar_record(value)]
                        for row, values in enumerate(map_.rows)
                        for column, value in values
                    ],
                }
                for degree, map_ in self.differentials
            ],
            "character_h1_dimension": self.character_h1_dimension,
            "required_full_cochain": _cochain_record(self.required_full_cochain),
            "maximum_inclusion_depth": self.inclusion_depth,
            "maximum_transfer_path_depths": dict(self.path_depths),
            "transferred_differential_squared_zero": (
                self.transferred_differential_squared_zero
            ),
            "group_relations_exact": self.group_relations_exact,
            "character_bases_exact": self.character_bases_exact,
            "full_representative_is_cycle": self.full_representative_is_cycle,
            "full_representative_has_strict_character": (
                self.full_representative_has_strict_character
            ),
            "source_archive_sha256": self.source_archive_sha256,
            "physical_higgs_representative_available": (
                self.physical_higgs_representative_available
            ),
        }


@cache
def mixed_schoen_higgs_deck_action() -> MixedSchoenHiggsDeckAction:
    """Derive and gate the source-required lawful full Higgs representative."""

    actions = {action.name: action for action in schoen_sparse_deck_actions()}
    bases = tuple(
        (degree, _character_basis(degree, UP_HIGGS_CHARACTER))
        for degree in (0, 1, 2)
    )
    maps_with_depths = tuple(
        (degree, _character_differential(degree, UP_HIGGS_CHARACTER))
        for degree in (0, 1)
    )
    maps = {degree: item[0] for degree, item in maps_with_depths}
    cycles = maps[1].kernel_inclusion()
    selected = _cohomology_complement_columns(maps[0], cycles)
    representatives = _select_columns(cycles, selected, "required-Higgs-H1")
    full, depth = _strict_higgs_representative(representatives, dict(bases)[1])
    group_relations = True
    character_bases_exact = True
    for degree, basis in bases:
        p_action = _reduced_action_map(degree, actions["P"])
        t_action = _reduced_action_map(degree, actions["T"])
        identity = _identity(p_action.domain)
        group_relations &= (
            p_action.compose(p_action).compose(p_action) == identity
            and t_action.compose(t_action).compose(t_action) == identity
            and p_action.compose(t_action) == t_action.compose(p_action)
        )
        character_bases_exact &= (
            p_action.compose(basis)
            == basis.scale(OMEGA ** UP_HIGGS_CHARACTER[0])
            and t_action.compose(basis)
            == basis.scale(OMEGA ** UP_HIGGS_CHARACTER[1])
        )
    cycle = full_chain_diagonal_differential(full).is_zero()
    strict = all(
        _full_action(full, actions[name])
        == full.scale(OMEGA ** UP_HIGGS_CHARACTER[index])
        for index, name in enumerate(("P", "T"))
    )
    result = MixedSchoenHiggsDeckAction(
        bases,
        tuple((degree, item[0]) for degree, item in maps_with_depths),
        tuple((degree, item[1]) for degree, item in maps_with_depths),
        representatives,
        UP_HIGGS_CHARACTER,
        full,
        depth,
        group_relations,
        character_bases_exact,
        cycle,
        strict,
        _source_digest(),
    )
    if not result.physical_higgs_representative_available:
        raise ValueError("the strict source-required Higgs representative gate failed")
    return result


def write_chain_actions(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed strict Higgs representative certificate."""

    result = mixed_schoen_higgs_deck_action()
    payload: dict[str, object] = {
        "schema": "mixed-schoen-chain-actions-v1",
        **result.as_record(),
        "observational_inputs_used": False,
        "arbitrary_extension_point_selected": False,
        "yukawa_trace_normalized": False,
        "next_required_object": (
            "the restricted common-DGA product hull and exact cyclic trace for "
            "the two universal matter sectors and this strict Higgs cocycle"
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
    """Regenerate the strict lawful Higgs representative certificate."""

    payload = write_chain_actions()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "physical_higgs_representative_available: "
        f"{payload['physical_higgs_representative_available']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MixedSchoenHiggsDeckAction",
    "OUTPUT",
    "mixed_schoen_higgs_deck_action",
    "write_chain_actions",
]
