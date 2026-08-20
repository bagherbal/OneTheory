"""Derive exact matter cohomology of the reconstructed published carrier.

Owns:
    Full-Čech constituent cohomology, deck-character decompositions, the outer
    long-exact-sequence theorem, dual vanishing, and Wilson-projected families.

Depends on:
    The transferred Čech engine, strict constituent linearizations, universal
    outer family, exact finite-group algebra, and published Wilson embedding.

Must not:
    Import published cohomology dimensions as rank inputs, select an extension
    coordinate, claim Higgs representatives, or use measured flavor data.

Phase 0:
    Exact matter-sector cohomology is generated; Higgs cohomology remains next.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer import (
    schoen_unit_constituent,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    TransferredCohomologyDeckAction,
    transferred_outer_cohomology_deck_action,
)

from .published_outer_reduced_mismatch import published_outer_reduced_mismatch
from .published_outer_stability_locus import OUTPUT as STABILITY_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/published_matter_cohomology.json"
SOURCE_MANIFEST = ROOT / "data/published/visible_carrier/source_manifest.json"
SPECTRUM_ARXIV_ID = "hep-th/0512177"
SPECTRUM_SOURCE_SHA256 = (
    "ad4ea10b3d765553ccdd072922a6bda619866ea814c532b8ffe74ddafc7fe73f"
)
CHARACTERS = tuple((first, second) for first in range(3) for second in range(3))


def _artifact_digest(path: Path, expected_key: str, expected_value: object) -> str:
    """Validate one upstream JSON artifact and return its canonical digest."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest does not verify: {path.name}")
    if payload.get(expected_key) != expected_value:
        raise ValueError(f"upstream artifact gate changed: {path.name}")
    return digest


def _source_digest() -> str:
    """Return the declared primary spectrum-source digest."""

    payload = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    sources = payload.get("sources")
    if not isinstance(sources, list):
        raise ValueError("the published source manifest lacks source records")
    matches = [
        source
        for source in sources
        if isinstance(source, dict) and source.get("arxiv_id") == SPECTRUM_ARXIV_ID
    ]
    if len(matches) != 1:
        raise ValueError("the spectrum source must occur exactly once")
    digest = matches[0].get("source_archive_sha256")
    if digest != SPECTRUM_SOURCE_SHA256:
        raise ValueError("the spectrum source archive digest changed")
    return SPECTRUM_SOURCE_SHA256


def _cohomology_dimensions(
    action: TransferredCohomologyDeckAction,
) -> tuple[int, int, int, int]:
    """Return cover cohomology dimensions in geometric degrees zero through three."""

    transferred = action.transferred
    available = {degree for degree, _ in transferred.reduced.total_spaces}
    return tuple(
        transferred.cohomology_dimension(degree) if degree in available else 0
        for degree in range(4)
    )  # type: ignore[return-value]


def _character_multiplicities(
    p_action: Matrix,
    t_action: Matrix,
) -> tuple[tuple[tuple[int, int], int], ...]:
    """Decompose two commuting order-three actions into exact joint eigenspaces."""

    if p_action.shape != t_action.shape or p_action.row_count != p_action.column_count:
        raise ValueError("deck character decomposition requires equal square actions")
    identity = Matrix.identity(p_action.row_count, scalar_type=Eisenstein)
    records = []
    for p_exponent, t_exponent in CHARACTERS:
        equations = Matrix(
            (
                *((p_action - identity.scale(OMEGA**p_exponent)).rows),
                *((t_action - identity.scale(OMEGA**t_exponent)).rows),
            ),
            scalar_type=Eisenstein,
        )
        records.append(((p_exponent, t_exponent), len(equations.nullspace())))
    if sum(multiplicity for _, multiplicity in records) != p_action.row_count:
        raise ValueError("joint character multiplicities do not span cohomology")
    return tuple(records)


def _cochain_digest(action: TransferredCohomologyDeckAction) -> str:
    """Hash all strict invariant full-Čech representatives deterministically."""

    digest = hashlib.sha256()
    for representative in action.invariant_full_cech:
        for basis, coefficient in representative.terms:
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


@dataclass(frozen=True, slots=True)
class ConstituentMatterCohomology:
    """One constituent's exact transferred cohomology and deck representation."""

    name: str
    action: TransferredCohomologyDeckAction
    dimensions: tuple[int, int, int, int]
    character_multiplicities: tuple[tuple[tuple[int, int], int], ...]

    def __post_init__(self) -> None:
        if not self.action.exact or self.action.degree != 1:
            raise ValueError("constituent matter action is not an exact H1 action")
        if self.dimensions[1] != self.action.representatives.domain.dimension:
            raise ValueError("constituent H1 basis and dimension disagree")
        if any(self.dimensions[degree] for degree in (0, 2, 3)):
            raise ValueError("the matter long exact sequence requires pure H1 constituents")

    @property
    def invariant_dimension(self) -> int:
        """Return the quotient-invariant constituent H1 dimension."""

        return self.action.invariant_dimension

    @property
    def strict_representative_term_counts(self) -> tuple[int, ...]:
        """Return sparse sizes of the strict invariant full-Čech representatives."""

        return tuple(len(item.terms) for item in self.action.invariant_full_cech)


@dataclass(frozen=True, slots=True)
class PublishedMatterCohomology:
    """Parameter-independent matter cohomology of the universal stable family."""

    stability_artifact_digest: str
    source_archive_sha256: str
    first: ConstituentMatterCohomology
    second: ConstituentMatterCohomology

    def __post_init__(self) -> None:
        if self.first.dimensions != (0, 9, 0, 0):
            raise ValueError("V1 cover cohomology changed")
        if self.second.dimensions != (0, 18, 0, 0):
            raise ValueError("V2 cover cohomology changed")
        if any(value != 1 for _, value in self.first.character_multiplicities):
            raise ValueError("V1 H1 is no longer one regular representation")
        if any(value != 2 for _, value in self.second.character_multiplicities):
            raise ValueError("V2 H1 is no longer two regular representations")
        if self.source_archive_sha256 != SPECTRUM_SOURCE_SHA256:
            raise ValueError("the matter source digest changed")

    @property
    def visible_dimensions(self) -> tuple[int, int, int, int]:
        """Return H*(V) from the parameter-independent long exact sequence."""

        return tuple(
            left + right
            for left, right in zip(
                self.first.dimensions,
                self.second.dimensions,
                strict=True,
            )
        )  # type: ignore[return-value]

    @property
    def dual_dimensions(self) -> tuple[int, int, int, int]:
        """Return H*(V dual) by exact Calabi-Yau Serre duality."""

        return tuple(reversed(self.visible_dimensions))  # type: ignore[return-value]

    @property
    def visible_character_multiplicities(
        self,
    ) -> tuple[tuple[tuple[int, int], int], ...]:
        """Return the semisimple deck representation on H1(V)."""

        return tuple(
            (character, left + right)
            for (character, left), (other, right) in zip(
                self.first.character_multiplicities,
                self.second.character_multiplicities,
                strict=True,
            )
            if character == other
        )

    @property
    def wilson_projected_multiplicity(self) -> int:
        """Return each 16-weight's invariant multiplicity after Wilson projection."""

        multiplicities = {
            character: value
            for character, value in self.visible_character_multiplicities
        }
        if set(multiplicities) != set(CHARACTERS):
            raise ValueError("the visible H1 representation lacks a deck character")
        values = set(multiplicities.values())
        if len(values) != 1:
            raise ValueError("Wilson projection does not give uniform family multiplicity")
        return next(iter(values))

    def as_record(self) -> dict[str, object]:
        """Serialize generated matter cohomology without claiming Higgs closure."""

        def constituent_record(item: ConstituentMatterCohomology) -> dict[str, object]:
            return {
                "name": item.name,
                "cover_cohomology_h0_to_h3": list(item.dimensions),
                "h1_dimension": item.action.representatives.domain.dimension,
                "character_multiplicities": [
                    {"character_exponents": list(character), "multiplicity": multiplicity}
                    for character, multiplicity in item.character_multiplicities
                ],
                "invariant_h1_dimension": item.invariant_dimension,
                "strict_invariant_representative_term_counts": list(
                    item.strict_representative_term_counts
                ),
                "strict_invariant_representative_digest": _cochain_digest(item.action),
                "deck_group_relations": item.action.group_relations,
                "full_representatives_are_cycles": (
                    item.action.full_representatives_are_cycles
                ),
                "full_representatives_are_invariant": (
                    item.action.full_representatives_are_invariant
                ),
            }

        family_count = self.wilson_projected_multiplicity
        return {
            "schema": "published-matter-cohomology-v1",
            "coefficient_field": "Q(omega)",
            "stability_artifact_digest": self.stability_artifact_digest,
            "source": {
                "arxiv_id": SPECTRUM_ARXIV_ID,
                "version": "v3",
                "source_archive_sha256": self.source_archive_sha256,
                "comparison_locators": ["eq:9", "eq:14", "eq:burt2", "eq:burt3"],
                "published_dimensions_used_as_rank_inputs": False,
            },
            "constituents": [
                constituent_record(self.first),
                constituent_record(self.second),
            ],
            "outer_long_exact_sequence": {
                "sequence": "0 -> V1 -> V(a) -> V2 -> 0",
                "reason_parameter_independent": (
                    "both constituent complexes have cohomology only in degree one, "
                    "so every connecting map has zero domain or codomain"
                ),
                "all_extension_parameters": True,
                "visible_cover_cohomology_h0_to_h3": list(self.visible_dimensions),
                "dual_cover_cohomology_h0_to_h3": list(self.dual_dimensions),
                "visible_h1_representation": "3 Reg(Z3 x Z3)",
                "visible_h1_character_multiplicities": [
                    {"character_exponents": list(character), "multiplicity": multiplicity}
                    for character, multiplicity in self.visible_character_multiplicities
                ],
                "dual_h1_vanishes": self.dual_dimensions[1] == 0,
            },
            "wilson_projection": {
                "embedding_source": "hep-th/0512177 eq:burt4",
                "multiplicity_per_spin10_16_weight": family_count,
                "families": family_count,
                "right_handed_neutrinos": family_count,
                "anti_families": 0,
                "matter_exotic_blocks": 0,
                "selection_constraint_used_as_rank_input": False,
            },
            "full_universal_visible_h1_chain_lifts_computed": False,
            "next_required_object": (
                "parameter-dependent H1(wedge^2 V(a)) complex, deck characters, "
                "and Higgs jumping locus"
            ),
            "arbitrary_extension_point_selected": False,
            "status": (
                "exact parameter-independent three-family matter cohomology and "
                "Wilson projection from generated constituent Cech complexes"
            ),
        }


@cache
def published_matter_cohomology() -> PublishedMatterCohomology:
    """Generate both constituent actions and derive universal matter cohomology."""

    reduced = published_outer_reduced_mismatch()
    first_constituent = reduced.forward.left
    second_constituent = reduced.forward.right
    unit = schoen_unit_constituent()
    first_action = transferred_outer_cohomology_deck_action(
        first_constituent,
        unit,
        1,
    )
    second_action = transferred_outer_cohomology_deck_action(
        second_constituent,
        unit,
        1,
    )
    return PublishedMatterCohomology(
        _artifact_digest(
            STABILITY_ARTIFACT,
            "certified_stable_locus",
            "U_pub x K^s",
        ),
        _source_digest(),
        ConstituentMatterCohomology(
            "V1",
            first_action,
            _cohomology_dimensions(first_action),
            _character_multiplicities(
                first_action.p_induced,
                first_action.t_induced,
            ),
        ),
        ConstituentMatterCohomology(
            "V2",
            second_action,
            _cohomology_dimensions(second_action),
            _character_multiplicities(
                second_action.p_induced,
                second_action.t_induced,
            ),
        ),
    )


def write_published_matter_cohomology(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed exact matter-cohomology artifact."""

    payload = published_matter_cohomology().as_record()
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
    """Regenerate the exact matter-cohomology artifact."""

    payload = write_published_matter_cohomology()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "visible_cover_cohomology: "
        f"{payload['outer_long_exact_sequence']['visible_cover_cohomology_h0_to_h3']}"
    )
    print(f"wilson_projection: {payload['wilson_projection']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ConstituentMatterCohomology",
    "PublishedMatterCohomology",
    "published_matter_cohomology",
]
