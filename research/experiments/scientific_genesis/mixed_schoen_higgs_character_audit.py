"""Derive the complete Higgs character support of the synchronized chain.

Owns:
    One exact ambient differential transfer, all nine character restrictions,
    their cohomology dimensions, and uniform-shift comparison with the source.

Depends on:
    The certified synchronized chain, its exact deck actions, reusable sparse
    transfer columns, and selected source characters used only after ranks.

Must not:
    Import source multiplicities as rank inputs, fit a character correction,
    relabel generators, or identify a missing physical Higgs representative.

Phase 0:
    Research-only full character audit of the current chain action.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    _SparseSpanSolver,
)
from research.experiments.computable_carrier.schoen_sparse_outer import (
    SparseMap,
    _freeze_rows,
)
from research.experiments.computable_carrier.schoen_sparse_outer_actions import (
    _columns,
)

from .mixed_schoen_chain_actions import Character, _character_basis
from .mixed_schoen_chain_transfer import TransferredColumn, _space, transferred_column
from .mixed_schoen_observable_spectrum import SOURCE_HIGGS_CHARACTERS

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_higgs_character_audit.json"
)
CHARACTERS: tuple[Character, ...] = tuple(
    (first, second) for first in range(3) for second in range(3)
)


def _column_job(job: tuple[int, int]) -> tuple[int, TransferredColumn]:
    """Transfer one ambient basis column in an isolated worker."""

    degree, source_index = job
    return source_index, transferred_column(degree, source_index)


@cache
def _full_differential(degree: int) -> SparseMap:
    """Assemble one full transferred differential without character repeats."""

    source = _space(degree)
    target = _space(degree + 1)
    jobs = tuple((degree, source_index) for source_index in range(source.dimension))
    with ProcessPoolExecutor(max_workers=min(16, len(jobs))) as executor:
        completed = tuple(executor.map(_column_job, jobs, chunksize=4))
    rows: list[dict[int, Eisenstein]] = [dict() for _ in range(target.dimension)]
    for source_index, column in completed:
        for target_index, coefficient in column.entries:
            rows[target_index][source_index] = coefficient
    return SparseMap(source, target, _freeze_rows(rows))


def _restrict_differential(
    differential: SparseMap,
    degree: int,
    character: Character,
) -> SparseMap:
    """Restrict one shared ambient map to an exact character basis."""

    source = _character_basis(degree, character)
    target = _character_basis(degree + 1, character)
    target_columns = tuple(_columns(target))
    solver = _SparseSpanSolver(target_columns)
    coordinate_columns = tuple(
        solver.coordinates(column)
        for column in _columns(differential.compose(source))
    )
    return SparseMap(
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
    )


def _map_digest(map_: SparseMap) -> str:
    """Return a canonical digest of every exact sparse matrix entry."""

    return _canonical_digest(
        {
            "domain": map_.domain.name,
            "domain_dimension": map_.domain.dimension,
            "codomain": map_.codomain.name,
            "codomain_dimension": map_.codomain.dimension,
            "entries": [
                [row, column, str(value)]
                for row, values in enumerate(map_.rows)
                for column, value in values
            ],
        }
    )


@dataclass(frozen=True, slots=True)
class CharacterSector:
    """Exact dimensions and maps for one simultaneous deck character."""

    character: Character
    space_dimensions: tuple[int, int, int]
    incoming: SparseMap
    outgoing: SparseMap

    @property
    def h1_dimension(self) -> int:
        """Return exact middle cohomology dimension."""

        return (
            self.space_dimensions[1]
            - self.incoming.rank()
            - self.outgoing.rank()
        )

    @property
    def squared_zero(self) -> bool:
        """Return whether the two exact restricted maps compose to zero."""

        return self.outgoing.compose(self.incoming).is_zero()

    def as_record(self) -> dict[str, object]:
        """Serialize one exact sector without dumping redundant map entries."""

        return {
            "character": list(self.character),
            "space_dimensions": list(self.space_dimensions),
            "differential_ranks": [self.incoming.rank(), self.outgoing.rank()],
            "differential_nonzero_entries": [
                sum(len(row) for row in self.incoming.rows),
                sum(len(row) for row in self.outgoing.rows),
            ],
            "differential_digests": [
                _map_digest(self.incoming),
                _map_digest(self.outgoing),
            ],
            "differential_squared_zero": self.squared_zero,
            "h1_dimension": self.h1_dimension,
        }


@dataclass(frozen=True, slots=True)
class HiggsCharacterAudit:
    """Complete exact character decomposition of current synchronized H1."""

    ambient_differentials: tuple[SparseMap, SparseMap]
    sectors: tuple[CharacterSector, ...]

    @property
    def character_spaces_exhaust_ambient(self) -> bool:
        """Return whether all character bases span each ambient degree."""

        return all(
            sum(sector.space_dimensions[degree] for sector in self.sectors)
            == _space(degree).dimension
            for degree in range(3)
        )

    @property
    def all_restrictions_exact(self) -> bool:
        """Return whether all character maps form exact two-step complexes."""

        return all(sector.squared_zero for sector in self.sectors)

    @property
    def current_h1_dimension(self) -> int:
        """Return total synchronized H1 from all exact character sectors."""

        return sum(sector.h1_dimension for sector in self.sectors)

    @property
    def current_h1_characters(self) -> tuple[Character, ...]:
        """Expand the current exact H1 character multiset."""

        return tuple(
            sector.character
            for sector in self.sectors
            for _index in range(sector.h1_dimension)
        )

    @property
    def matching_uniform_shifts(self) -> tuple[Character, ...]:
        """Return every global character shift matching the source multiset."""

        source = tuple(sorted(SOURCE_HIGGS_CHARACTERS))
        return tuple(
            shift
            for shift in CHARACTERS
            if tuple(
                sorted(
                    (
                        (character[0] + shift[0]) % 3,
                        (character[1] + shift[1]) % 3,
                    )
                    for character in self.current_h1_characters
                )
            )
            == source
        )

    @property
    def exact(self) -> bool:
        """Return every full-decomposition and fail-closed gate."""

        return (
            len(self.sectors) == 9
            and self.character_spaces_exhaust_ambient
            and self.all_restrictions_exact
            and self.current_h1_dimension == 4
            and self.current_h1_characters != SOURCE_HIGGS_CHARACTERS
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the complete representation and source comparison."""

        return {
            "schema": "mixed-schoen-higgs-character-audit-v1",
            "coefficient_field": "Q(omega)",
            "ambient_space_dimensions": [
                _space(degree).dimension for degree in range(3)
            ],
            "ambient_differential_nonzero_entries": [
                sum(len(row) for row in differential.rows)
                for differential in self.ambient_differentials
            ],
            "ambient_differential_digests": [
                _map_digest(differential)
                for differential in self.ambient_differentials
            ],
            "character_spaces_exhaust_ambient": (
                self.character_spaces_exhaust_ambient
            ),
            "sectors": [sector.as_record() for sector in self.sectors],
            "all_character_restrictions_exact": self.all_restrictions_exact,
            "current_h1_dimension": self.current_h1_dimension,
            "current_h1_characters": [
                list(character) for character in self.current_h1_characters
            ],
            "selected_source_h1_characters": [
                list(character) for character in SOURCE_HIGGS_CHARACTERS
            ],
            "source_characters_used_as_rank_input": False,
            "current_characters_match_source": (
                self.current_h1_characters == SOURCE_HIGGS_CHARACTERS
            ),
            "matching_uniform_character_shifts": [
                list(character) for character in self.matching_uniform_shifts
            ],
            "observational_inputs_used": False,
            "exact": self.exact,
            "next_required_object": (
                "an atlas-derived non-scalar chain action or a proof that the "
                "selected source equivariant structure is unrealizable on the "
                "synchronized complex"
            ),
        }


@cache
def higgs_character_audit() -> HiggsCharacterAudit:
    """Compute every exact character sector from two shared ambient maps."""

    ambient = (_full_differential(0), _full_differential(1))
    sectors = tuple(
        CharacterSector(
            character,
            tuple(
                _character_basis(degree, character).domain.dimension
                for degree in range(3)
            ),
            _restrict_differential(ambient[0], 0, character),
            _restrict_differential(ambient[1], 1, character),
        )
        for character in CHARACTERS
    )
    result = HiggsCharacterAudit(ambient, sectors)
    if not result.exact:
        raise ValueError("the full synchronized Higgs character audit failed")
    return result


def write_higgs_character_audit(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed complete character audit."""

    payload = higgs_character_audit().as_record()
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
    """Regenerate the complete synchronized Higgs character audit."""

    payload = write_higgs_character_audit()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"current_h1_characters: {payload['current_h1_characters']}")
    print(
        "matching_uniform_character_shifts: "
        f"{payload['matching_uniform_character_shifts']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CharacterSector",
    "HiggsCharacterAudit",
    "OUTPUT",
    "higgs_character_audit",
    "write_higgs_character_audit",
]
