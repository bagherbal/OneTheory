"""Close factorwise linearization repairs of the synchronized Higgs action.

Owns:
    Exact constituent self-Hom degree-zero ranks, simplicity certificates, and
    the character-torsor obstruction for alternative deck linearizations.

Depends on:
    The selected mixed constituent complexes, their exact self-Hom transfer,
    certified deck atlases, and the complete Higgs character audit.

Must not:
    Treat resolution frames as bundle automorphisms, fit a deck character,
    exclude unrelated constituent realizations, or fabricate a Higgs class.

Phase 0:
    Research-only scoped no-go for the same selected simple constituents.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer import (
    schoen_serre_outer_hom,
)
from research.experiments.computable_carrier.schoen_sparse_outer import SparseMap

from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_outer_transfer import _skeleton, _transfer_map

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_higgs_linearization_no_go.json"
)
CHARACTER_AUDIT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_higgs_character_audit.json"
)
PREREQUISITES: tuple[tuple[str, Path, str, str], ...] = (
    (
        "mixed_constituent_arrows",
        ROOT
        / "data/generated/scientific_genesis/"
        "mixed_constituent_schoen_arrows.json",
        "mixed-constituent-schoen-arrows-v1",
        "all_common_schoen_arrows_exact",
    ),
    (
        "constituent_deck_atlases",
        ROOT
        / "data/generated/scientific_genesis/"
        "published_constituent_deck_atlases.json",
        "published-constituent-deck-atlases-v1",
        "all_constituent_deck_atlases_exact",
    ),
    (
        "current_chain_action",
        ROOT
        / "data/generated/scientific_genesis/"
        "mixed_schoen_chain_actions.json",
        "mixed-schoen-chain-actions-v1",
        "group_relations_exact",
    ),
    (
        "complete_higgs_character_audit",
        CHARACTER_AUDIT,
        "mixed-schoen-higgs-character-audit-v1",
        "exact",
    ),
)


def _verified_artifact(path: Path, schema: str, exact_key: str) -> dict[str, object]:
    """Read one content-addressed exact prerequisite."""

    payload = cast(dict[str, object], json.loads(path.read_text(encoding="utf-8")))
    digest = payload.pop("artifact_digest", None)
    if (
        not isinstance(digest, str)
        or digest != _canonical_digest(payload)
        or payload.get("schema") != schema
        or payload.get(exact_key) is not True
    ):
        raise ValueError(f"prerequisite artifact failed: {path.name}")
    payload["artifact_digest"] = digest
    return payload


def _map_digest(map_: SparseMap) -> str:
    """Digest every exact entry of one transferred self-Hom map."""

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
class ConstituentSimplicityAudit:
    """Exact degree-zero derived endomorphism audit for one constituent."""

    constituent: str
    negative_space_dimensions: tuple[int, int, int]
    degree_zero_space_dimension: int
    degree_one_space_dimension: int
    differential: SparseMap
    transfer_path_depth: int

    @property
    def differential_rank(self) -> int:
        """Return the exact outgoing rank from self-Hom degree zero."""

        return self.differential.rank()

    @property
    def h0_dimension(self) -> int:
        """Return the exact scalar endomorphism-space dimension."""

        return self.degree_zero_space_dimension - self.differential_rank

    @property
    def simple(self) -> bool:
        """Return whether the exact endomorphism space is the scalar field."""

        return (
            self.negative_space_dimensions == (0, 0, 0)
            and self.differential.domain.dimension
            == self.degree_zero_space_dimension
            and self.differential.codomain.dimension
            == self.degree_one_space_dimension
            and self.h0_dimension == 1
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact rank certificate without hiding its matrix."""

        return {
            "constituent": self.constituent,
            "negative_self_hom_space_dimensions": list(
                self.negative_space_dimensions
            ),
            "degree_zero_space_dimension": self.degree_zero_space_dimension,
            "degree_one_space_dimension": self.degree_one_space_dimension,
            "degree_zero_differential_rank": self.differential_rank,
            "degree_zero_differential_nonzero_entries": sum(
                len(row) for row in self.differential.rows
            ),
            "degree_zero_differential_digest": _map_digest(self.differential),
            "transfer_path_depth": self.transfer_path_depth,
            "h0_endomorphism_dimension": self.h0_dimension,
            "simple_over_q_omega": self.simple,
        }


def _simplicity_job(index: int) -> ConstituentSimplicityAudit:
    """Compute one constituent's degree-zero self-Hom differential exactly."""

    constituent = mixed_schoen_constituents()[index]
    reduced = schoen_serre_outer_hom(
        _skeleton(constituent),
        _skeleton(constituent),
    )
    spaces = dict(reduced.total_spaces)
    differential, depth = _transfer_map(constituent, constituent, 0)
    return ConstituentSimplicityAudit(
        constituent.name,
        tuple(spaces[degree].dimension for degree in (-3, -2, -1)),
        spaces[0].dimension,
        spaces[1].dimension,
        differential,
        depth,
    )


@dataclass(frozen=True, slots=True)
class HiggsLinearizationNoGo:
    """Scoped obstruction to repairing Higgs characters by relinearization."""

    constituents: tuple[ConstituentSimplicityAudit, ...]
    current_characters: tuple[tuple[int, int], ...]
    source_characters: tuple[tuple[int, int], ...]
    matching_uniform_shifts: tuple[tuple[int, int], ...]
    prerequisite_artifact_digests: tuple[tuple[str, str], ...]

    @property
    def all_constituents_simple(self) -> bool:
        """Return whether both selected factors have only scalar automorphisms."""

        return len(self.constituents) == 2 and all(
            constituent.simple for constituent in self.constituents
        )

    @property
    def exact(self) -> bool:
        """Return all hypotheses and the exhaustive character obstruction."""

        return (
            self.all_constituents_simple
            and self.current_characters != self.source_characters
            and not self.matching_uniform_shifts
            and len(self.prerequisite_artifact_digests) == len(PREREQUISITES)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the simplicity theorem and its scoped consequence."""

        return {
            "schema": "mixed-schoen-higgs-linearization-no-go-v1",
            "coefficient_field": "Q(omega)",
            "constituent_self_hom_audits": [
                constituent.as_record() for constituent in self.constituents
            ],
            "all_selected_constituents_simple": self.all_constituents_simple,
            "linearization_difference_theorem": (
                "two linearizations of one simple object differ by a group "
                "character"
            ),
            "proof_steps": [
                "compose the second lift with the inverse of the first lift",
                "simplicity makes each resulting automorphism scalar",
                "the linearization cocycle law makes those scalars a character",
                "factor characters multiply to one uniform tensor character",
            ],
            "current_h1_characters": [
                list(character) for character in self.current_characters
            ],
            "selected_source_h1_characters": [
                list(character) for character in self.source_characters
            ],
            "matching_uniform_character_shifts": [
                list(character) for character in self.matching_uniform_shifts
            ],
            "non_scalar_resolution_comparison_can_repair_cohomology": False,
            "same_constituent_factorwise_linearization_repair_available": False,
            "selected_source_equivariance_realized_by_current_complex": False,
            "physical_h_d_representative_available": False,
            "scope": (
                "the same selected V1 and V2 objects with factorwise deck "
                "linearizations; unrelated constituent realizations are not excluded"
            ),
            "character_twist_fitted": False,
            "observational_inputs_used": False,
            "prerequisite_artifact_digests": dict(
                self.prerequisite_artifact_digests
            ),
            "exact": self.exact,
            "next_required_object": (
                "a direct atlas cohomology derivation of the Higgs characters "
                "or a different exact constituent realization"
            ),
        }


@cache
def higgs_linearization_no_go() -> HiggsLinearizationNoGo:
    """Prove simplicity and apply the exact linearization torsor theorem."""

    prerequisites = tuple(
        (
            name,
            _verified_artifact(path, schema, exact_key),
        )
        for name, path, schema, exact_key in PREREQUISITES
    )
    audit = dict(prerequisites)["complete_higgs_character_audit"]
    with ProcessPoolExecutor(max_workers=2) as executor:
        constituents = tuple(executor.map(_simplicity_job, range(2)))
    result = HiggsLinearizationNoGo(
        constituents,
        tuple(tuple(item) for item in cast(list[list[int]], audit["current_h1_characters"])),
        tuple(
            tuple(item)
            for item in cast(list[list[int]], audit["selected_source_h1_characters"])
        ),
        tuple(
            tuple(item)
            for item in cast(
                list[list[int]],
                audit["matching_uniform_character_shifts"],
            )
        ),
        tuple(
            (name, cast(str, payload["artifact_digest"]))
            for name, payload in prerequisites
        ),
    )
    if not result.exact:
        raise ValueError("the same-constituent linearization no-go failed")
    return result


def write_higgs_linearization_no_go(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed factorwise linearization no-go."""

    payload = higgs_linearization_no_go().as_record()
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
    """Regenerate the exact linearization no-go certificate."""

    payload = write_higgs_linearization_no_go()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "h0_endomorphism_dimensions: "
        f"{[item['h0_endomorphism_dimension'] for item in payload['constituent_self_hom_audits']]}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ConstituentSimplicityAudit",
    "HiggsLinearizationNoGo",
    "OUTPUT",
    "higgs_linearization_no_go",
    "write_higgs_linearization_no_go",
]
