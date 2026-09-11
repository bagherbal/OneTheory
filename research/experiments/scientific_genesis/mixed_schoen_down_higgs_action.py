"""Audit the published down-Higgs character in the current chain action.

Owns:
    Exact dimensions and differential ranks of the lawful chain model in
    character (0,2), compared only afterward with the published multiplicity.

Depends on:
    Source-selected flavor support, the exact mixed-Schoen chain action, and
    the pinned visible-carrier source archive.

Must not:
    Force a missing Higgs representative, repair an inequivalent action by a
    guessed twist, select a carrier point, or import observational data.

Phase 0:
    Research-only fail-closed audit of the down-type Higgs chain prerequisite.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.numbers import OMEGA
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.computable_carrier.schoen_sparse_outer import SparseMap

from .mixed_schoen_chain_actions import (
    Character,
    _character_basis,
    _character_differential,
    _identity,
    _reduced_action_map,
    _scalar_record,
)
from .mixed_schoen_flavor_character_support import OUTPUT as SUPPORT_ARTIFACT
from .mixed_schoen_universal_matter_lifts import _source_digest

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_down_higgs_action.json"
DOWN_HIGGS_CHARACTER: Character = (0, 2)
SOURCE_H1_MULTIPLICITY = 1


def _support_digest() -> str:
    """Verify that exact source routing still requires down character (0,2)."""

    payload = json.loads(SUPPORT_ARTIFACT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError("the flavor-support artifact digest failed")
    if (
        payload.get("selected_next_sector") != "down"
        or payload.get("selected_required_new_higgs_character")
        != list(DOWN_HIGGS_CHARACTER)
    ):
        raise ValueError("the exact down-Higgs support requirement changed")
    return digest


@dataclass(frozen=True, slots=True)
class DownHiggsChainAudit:
    """Exact chain-complex evidence for the missing physical down-Higgs class."""

    character_bases: tuple[tuple[int, SparseMap], ...]
    differentials: tuple[tuple[int, SparseMap], ...]
    path_depths: tuple[tuple[int, int], ...]
    group_relations_exact: bool
    character_bases_exact: bool
    support_artifact_digest: str
    source_archive_sha256: str

    @property
    def transferred_differential_squared_zero(self) -> bool:
        """Return whether the restricted exact maps form a complex."""

        maps = dict(self.differentials)
        return maps[1].compose(maps[0]).is_zero()

    @property
    def character_h1_dimension(self) -> int:
        """Return the exact current-chain H1 dimension in character (0,2)."""

        bases = dict(self.character_bases)
        maps = dict(self.differentials)
        return bases[1].domain.dimension - maps[0].rank() - maps[1].rank()

    @property
    def route_blocked_exact(self) -> bool:
        """Return whether exact chain evidence contradicts source multiplicity."""

        return (
            self.transferred_differential_squared_zero
            and self.group_relations_exact
            and self.character_bases_exact
            and self.character_h1_dimension == 0
            and SOURCE_H1_MULTIPLICITY == 1
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact mismatch without fabricating a representative."""

        return {
            "schema": "mixed-schoen-down-higgs-action-audit-v1",
            "coefficient_field": "Q(omega)",
            "required_character": list(DOWN_HIGGS_CHARACTER),
            "ambient_space_dimensions": {
                str(degree): basis.codomain.dimension
                for degree, basis in self.character_bases
            },
            "character_space_dimensions": {
                str(degree): basis.domain.dimension
                for degree, basis in self.character_bases
            },
            "differential_ranks": {
                str(degree): map_.rank()
                for degree, map_ in self.differentials
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
            "maximum_transfer_path_depths": dict(self.path_depths),
            "transferred_differential_squared_zero": (
                self.transferred_differential_squared_zero
            ),
            "group_relations_exact": self.group_relations_exact,
            "character_bases_exact": self.character_bases_exact,
            "character_h1_dimension": self.character_h1_dimension,
            "source_comparison": {
                "expected_h1_multiplicity": SOURCE_H1_MULTIPLICITY,
                "used_as_rank_input": False,
                "arxiv_id": "hep-th/0512177",
                "version": "v3",
                "source_archive_sha256": self.source_archive_sha256,
                "cohomology_locator": "eq:17",
                "wilson_locator": "eq:19",
            },
            "strict_down_higgs_representative_available": False,
            "route_blocked_exact": self.route_blocked_exact,
            "repair_character_twist_guessed": False,
            "observational_inputs_used": False,
            "arbitrary_extension_point_selected": False,
            "prerequisite_artifact_digests": {
                "flavor_character_support": self.support_artifact_digest,
            },
            "next_required_object": (
                "exact reranking to the Dirac-neutrino sector, which reuses "
                "the certified strict Higgs character (0,1)"
            ),
        }


@cache
def down_higgs_chain_audit() -> DownHiggsChainAudit:
    """Compute the exact down-Higgs character complex and fail closed."""

    actions = {action.name: action for action in schoen_sparse_deck_actions()}
    bases = tuple(
        (degree, _character_basis(degree, DOWN_HIGGS_CHARACTER))
        for degree in (0, 1, 2)
    )
    maps_with_depths = tuple(
        (degree, _character_differential(degree, DOWN_HIGGS_CHARACTER))
        for degree in (0, 1)
    )
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
        character_bases_exact &= p_action.compose(basis) == basis.scale(
            OMEGA ** DOWN_HIGGS_CHARACTER[0]
        ) and t_action.compose(basis) == basis.scale(
            OMEGA ** DOWN_HIGGS_CHARACTER[1]
        )
    result = DownHiggsChainAudit(
        bases,
        tuple((degree, item[0]) for degree, item in maps_with_depths),
        tuple((degree, item[1]) for degree, item in maps_with_depths),
        group_relations,
        character_bases_exact,
        _support_digest(),
        _source_digest(),
    )
    if not result.route_blocked_exact:
        raise ValueError("the exact down-Higgs obstruction changed")
    return result


def write_down_higgs_action(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed down-Higgs obstruction certificate."""

    payload = down_higgs_chain_audit().as_record()
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
    """Regenerate the down-Higgs obstruction and print the exact mismatch."""

    payload = write_down_higgs_action()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"character_h1_dimension: {payload['character_h1_dimension']}")
    print(f"route_blocked_exact: {payload['route_blocked_exact']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DOWN_HIGGS_CHARACTER",
    "DownHiggsChainAudit",
    "OUTPUT",
    "down_higgs_chain_audit",
    "write_down_higgs_action",
]
