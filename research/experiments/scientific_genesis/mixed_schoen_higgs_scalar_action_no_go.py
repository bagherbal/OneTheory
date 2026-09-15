"""Refute scalar atlas repairs of the synchronized down-Higgs action.

Owns:
    The exact W1/P line-frame ratio, the non-chain-map witness for an isolated
    line replacement, and the shifted-sector cohomology for uniform repair.

Depends on:
    Content-addressed atlas-obstruction and chain-action certificates plus the
    exact synchronized chain differential over the Eisenstein field.

Must not:
    Treat a scalar character as an atlas comparison, guess an off-diagonal
    gauge, relabel deck generators, or claim that a down-Higgs class exists.

Phase 0:
    Research-only scoped no-go for constant scalar frame corrections.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA2, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.computable_carrier.schoen_sparse_outer import SparseMap

from . import mixed_schoen_chain_actions as chain_actions
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_chain_actions import (
    Character,
    _character_basis,
    _character_differential,
    _constituent_frame,
    _scalar_record,
)
from .mixed_schoen_chain_diagonal import (
    _reduced_entries,
    full_chain_diagonal_differential,
)
from .mixed_schoen_chain_transfer import _include

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_higgs_scalar_action_no_go.json"
)
OBSTRUCTION_ARTIFACT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_higgs_equivariant_obstruction.json"
)
CHAIN_ACTION_ARTIFACT = (
    ROOT / "data/generated/scientific_genesis/mixed_schoen_chain_actions.json"
)
TARGET_CHARACTER: Character = (0, 2)
LEGACY_SHIFTED_CHARACTER: Character = (1, 2)


def _artifact_digest(path: Path, schema: str) -> str:
    """Verify one prerequisite artifact and return its content digest."""

    payload = cast(dict[str, object], json.loads(path.read_text(encoding="utf-8")))
    digest = payload.pop("artifact_digest", None)
    if (
        not isinstance(digest, str)
        or digest != _canonical_digest(payload)
        or payload.get("schema") != schema
    ):
        raise ValueError(f"prerequisite artifact failed: {path.name}")
    return digest


def _w1_resolution_connected() -> bool:
    """Check that nonzero W1 arrows connect every resolution object."""

    constituent = mixed_schoen_constituents()[0]
    adjacency = {index: set() for index in range(len(constituent.objects))}
    for arrow in constituent.resolution_arrows:
        adjacency[arrow.source].add(arrow.target)
        adjacency[arrow.target].add(arrow.source)
    for term in constituent.extension_terms:
        adjacency[term.source].add(term.target)
        adjacency[term.target].add(term.source)
    reached = {0}
    frontier = [0]
    while frontier:
        source = frontier.pop()
        for target in adjacency[source] - reached:
            reached.add(target)
            frontier.append(target)
    return len(reached) == len(constituent.objects)


def _a_only_frame(factor: int, generator: str) -> Matrix:
    """Replace only the discrepant W1/P line entry by its atlas value."""

    frame = _constituent_frame(factor, generator)
    if factor != 1 or generator != "P":
        return frame
    rows = [list(row) for row in frame.rows]
    rows[0][0] = Eisenstein(1)
    return Matrix(tuple(tuple(row) for row in rows), scalar_type=Eisenstein)


def _isolated_line_residual_term_count() -> int:
    """Return an exact commutator witness for the isolated A-line change."""

    action = next(item for item in schoen_sparse_deck_actions() if item.name == "P")
    source = _include(_reduced_entries(0)[0])
    original = chain_actions._constituent_frame
    chain_actions._constituent_frame = _a_only_frame
    try:
        acted_then_differentiated = full_chain_diagonal_differential(
            chain_actions._full_action(source, action)
        )
        differentiated_then_acted = chain_actions._full_action(
            full_chain_diagonal_differential(source),
            action,
        )
    finally:
        chain_actions._constituent_frame = original
    return len((acted_then_differentiated - differentiated_then_acted).terms)


@dataclass(frozen=True, slots=True)
class HiggsScalarActionNoGo:
    """Exact failure certificate for both constant scalar repair routes."""

    character_bases: tuple[tuple[int, SparseMap], ...]
    differentials: tuple[tuple[int, SparseMap], ...]
    path_depths: tuple[tuple[int, int], ...]
    isolated_line_residual_term_count: int
    w1_resolution_connected: bool
    prerequisite_artifact_digests: tuple[tuple[str, str], ...]

    @property
    def shifted_character_h1_dimension(self) -> int:
        """Return H1 of the legacy sector induced by the uniform twist."""

        bases = dict(self.character_bases)
        maps = dict(self.differentials)
        return bases[1].domain.dimension - maps[0].rank() - maps[1].rank()

    @property
    def differential_squared_zero(self) -> bool:
        """Return whether the shifted exact sector remains a complex."""

        maps = dict(self.differentials)
        return maps[1].compose(maps[0]).is_zero()

    @property
    def exact(self) -> bool:
        """Return whether both scalar routes fail under exact gates."""

        return (
            self.isolated_line_residual_term_count > 0
            and self.w1_resolution_connected
            and self.differential_squared_zero
            and self.shifted_character_h1_dimension == 0
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the scalar no-go and its exact restricted maps."""

        return {
            "schema": "mixed-schoen-higgs-scalar-action-no-go-v1",
            "coefficient_field": "Q(omega)",
            "target_character": list(TARGET_CHARACTER),
            "discrepant_constituent_generator": ["W1", "P"],
            "legacy_extension_line_character": "omega",
            "synchronized_atlas_line_character": "1",
            "forced_uniform_scalar": str(OMEGA2),
            "w1_resolution_connected": self.w1_resolution_connected,
            "isolated_line_replacement_is_chain_map": False,
            "isolated_line_commutator_term_count": (
                self.isolated_line_residual_term_count
            ),
            "uniform_scalar_action_is_chain_map": True,
            "uniform_scalar_action_group_laws_exact": True,
            "legacy_shifted_character": list(LEGACY_SHIFTED_CHARACTER),
            "character_space_dimensions": {
                str(degree): basis.domain.dimension
                for degree, basis in self.character_bases
            },
            "differential_ranks": {
                str(degree): differential.rank()
                for degree, differential in self.differentials
            },
            "differentials": [
                {
                    "degree": degree,
                    "entries": [
                        [row, column, *_scalar_record(value)]
                        for row, values in enumerate(differential.rows)
                        for column, value in values
                    ],
                }
                for degree, differential in self.differentials
            ],
            "maximum_transfer_path_depths": dict(self.path_depths),
            "differential_squared_zero": self.differential_squared_zero,
            "shifted_character_h1_dimension": (
                self.shifted_character_h1_dimension
            ),
            "scalar_action_repairs_refuted": self.exact,
            "character_twist_fitted": False,
            "observational_inputs_used": False,
            "prerequisite_artifact_digests": dict(
                self.prerequisite_artifact_digests
            ),
            "next_required_object": (
                "a non-scalar local-semilinear W1/P chain comparison derived "
                "from the exact overlap gauges"
            ),
        }


@cache
def higgs_scalar_action_no_go() -> HiggsScalarActionNoGo:
    """Compute both exact scalar-repair failures."""

    bases = tuple(
        (degree, _character_basis(degree, LEGACY_SHIFTED_CHARACTER))
        for degree in (0, 1, 2)
    )
    maps_with_depths = tuple(
        (degree, _character_differential(degree, LEGACY_SHIFTED_CHARACTER))
        for degree in (0, 1)
    )
    result = HiggsScalarActionNoGo(
        bases,
        tuple((degree, item[0]) for degree, item in maps_with_depths),
        tuple((degree, item[1]) for degree, item in maps_with_depths),
        _isolated_line_residual_term_count(),
        _w1_resolution_connected(),
        (
            (
                "higgs_equivariant_obstruction",
                _artifact_digest(
                    OBSTRUCTION_ARTIFACT,
                    "mixed-schoen-higgs-equivariant-obstruction-v1",
                ),
            ),
            (
                "legacy_chain_action",
                _artifact_digest(
                    CHAIN_ACTION_ARTIFACT,
                    "mixed-schoen-chain-actions-v1",
                ),
            ),
        ),
    )
    if not result.exact:
        raise ValueError("the scalar atlas-action no-go failed")
    return result


def write_higgs_scalar_action_no_go(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed scalar-action no-go certificate."""

    payload = higgs_scalar_action_no_go().as_record()
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
    """Regenerate the exact scalar-action no-go certificate."""

    payload = write_higgs_scalar_action_no_go()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "shifted_character_h1_dimension: "
        f"{payload['shifted_character_h1_dimension']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "HiggsScalarActionNoGo",
    "OUTPUT",
    "higgs_scalar_action_no_go",
    "write_higgs_scalar_action_no_go",
]
