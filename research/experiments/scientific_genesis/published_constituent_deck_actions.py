"""Align derived dP9 Serre actions with the published equivariant structures.

Owns:
    Exact joint-character comparison, the unique source-bound linearization
    twist, conjugacy certificates, and explicit invariant total cocycles for
    the two published constituent extension spaces.

Depends on:
    Derived natural dP9 chain actions and the published Serre representation
    matrices used strictly as immutable comparison data.

Must not:
    Call the source-selected character a geometric derivation, invent an
    equivariant ray when no exact fixed line exists, or claim the outer SU(4)
    extension has been reconstructed.

Phase 0:
    Constituent deck-linearized Ext representatives are reconstructed exactly;
    their mapping cones and synchronized outer Hom remain unresolved.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.homological import ChainMap, CoordinateVector
from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from onetheory.models.heterotic_schoen.visible import SerreKernelAction, serre_data
from research.experiments.computable_carrier.dp9_serre_actions import (
    DPSurfaceSerreDeckAction,
    published_constituent_serre_actions,
)
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.tier_b_dp9_actions import (
    _fixed_representatives,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/published_constituent_deck_actions.json"
CHARACTERS = (Eisenstein(1), OMEGA, OMEGA2)


def _simultaneous_eigenspace(
    p: Matrix,
    t: Matrix,
    p_character: Eisenstein,
    t_character: Eisenstein,
):
    """Return one exact joint eigenspace in matrix coordinates."""

    identity = Matrix.identity(p.row_count, scalar_type=Eisenstein)
    return Matrix(
        (
            *((p - identity.scale(p_character)).rows),
            *((t - identity.scale(t_character)).rows),
        ),
        scalar_type=Eisenstein,
    ).nullspace()


def _character_multiplicities(
    p: Matrix,
    t: Matrix,
) -> tuple[tuple[tuple[Eisenstein, Eisenstein], int], ...]:
    """Return the nonzero joint-character multiplicities deterministically."""

    return tuple(
        ((p_character, t_character), len(eigenspace))
        for p_character in CHARACTERS
        for t_character in CHARACTERS
        if (
            eigenspace := _simultaneous_eigenspace(
                p,
                t,
                p_character,
                t_character,
            )
        )
    )


def _matching_twists(
    derived: DPSurfaceSerreDeckAction,
    published: SerreKernelAction,
) -> tuple[tuple[Eisenstein, Eisenstein], ...]:
    """Find all one-dimensional characters matching the published spectrum."""

    target = _character_multiplicities(published.p, published.t)
    return tuple(
        (p_twist, t_twist)
        for p_twist in CHARACTERS
        for t_twist in CHARACTERS
        if _character_multiplicities(
            derived.p_induced.scale(p_twist),
            derived.t_induced.scale(t_twist),
        )
        == target
    )


def _eigenbasis(
    p: Matrix,
    t: Matrix,
) -> tuple[Matrix, tuple[tuple[Eisenstein, Eisenstein], ...]]:
    """Return a joint eigenbasis ordered by exact characters."""

    vectors = []
    characters = []
    for p_character in CHARACTERS:
        for t_character in CHARACTERS:
            for vector in _simultaneous_eigenspace(
                p,
                t,
                p_character,
                t_character,
            ):
                vectors.append(vector)
                characters.append((p_character, t_character))
    if len(vectors) != p.row_count:
        raise ValueError("commuting deck actions lack a complete joint eigenbasis")
    return (
        Matrix(
            tuple(
                tuple(vector.values[column] for vector in vectors)
                for column in range(p.row_count)
            ),
            scalar_type=Eisenstein,
        ),
        tuple(characters),
    )


def _intertwiner(
    derived_p: Matrix,
    derived_t: Matrix,
    published_p: Matrix,
    published_t: Matrix,
) -> Matrix:
    """Construct an exact simultaneous conjugacy from joint eigenbases."""

    derived_basis, derived_characters = _eigenbasis(derived_p, derived_t)
    published_basis, published_characters = _eigenbasis(published_p, published_t)
    if derived_characters != published_characters:
        raise ValueError("joint-character order does not match after linearization")
    comparison = published_basis @ derived_basis.inverse()
    if published_p @ comparison != comparison @ derived_p:
        raise ValueError("P intertwining equation failed")
    if published_t @ comparison != comparison @ derived_t:
        raise ValueError("T intertwining equation failed")
    return comparison


def _scale_chain_map(action: ChainMap, scalar: Eisenstein) -> ChainMap:
    """Tensor a chain action with one one-dimensional character."""

    return ChainMap(
        action.source,
        action.target,
        {
            degree: action.component(degree).scale(scalar)
            for degree in action.degrees
        },
    )


def _sparse_vector(vector: CoordinateVector) -> list[dict[str, str]]:
    """Serialize one exact total cocycle without zero coordinates."""

    return [
        {"basis": basis, "coefficient": str(coefficient)}
        for basis, coefficient in zip(
            vector.space.basis,
            vector.coordinates,
            strict=True,
        )
        if not coefficient.is_zero()
    ]


@dataclass(frozen=True, slots=True)
class PublishedConstituentDeckAction:
    """Source-aligned constituent chain action with exact comparison gates."""

    derived: DPSurfaceSerreDeckAction
    published: SerreKernelAction
    p_twist: Eisenstein
    t_twist: Eisenstein
    p_action: ChainMap
    t_action: ChainMap
    p_induced: Matrix
    t_induced: Matrix
    intertwiner: Matrix
    invariant_representatives: tuple[CoordinateVector, ...]

    @property
    def invariant_dimension(self) -> int:
        """Return the exact common fixed dimension after source alignment."""

        return len(self.invariant_representatives)

    @property
    def chain_relations(self) -> bool:
        """Return exact order-three and commuting chain-action gates."""

        identity = ChainMap.identity(self.derived.extension.total)
        return (
            self.p_action.compose(self.t_action)
            == self.t_action.compose(self.p_action)
            and self.p_action.compose(self.p_action).compose(self.p_action)
            == identity
            and self.t_action.compose(self.t_action).compose(self.t_action)
            == identity
        )

    @property
    def conjugate_to_published(self) -> bool:
        """Return both exact simultaneous intertwining equations."""

        return (
            self.published.p @ self.intertwiner
            == self.intertwiner @ self.p_induced
            and self.published.t @ self.intertwiner
            == self.intertwiner @ self.t_induced
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the exact comparison while preserving epistemic scope."""

        return {
            "scheme": self.derived.extension.scheme.name,
            "published_constituent": self.published.name,
            "linearization_character": {
                "P": str(self.p_twist),
                "T": str(self.t_twist),
                "status": "uniquely selected by published equivariant data",
            },
            "natural_character_multiplicities": [
                {
                    "P": str(character[0]),
                    "T": str(character[1]),
                    "multiplicity": multiplicity,
                }
                for character, multiplicity in _character_multiplicities(
                    self.derived.p_induced,
                    self.derived.t_induced,
                )
            ],
            "aligned_character_multiplicities": [
                {
                    "P": str(character[0]),
                    "T": str(character[1]),
                    "multiplicity": multiplicity,
                }
                for character, multiplicity in _character_multiplicities(
                    self.p_induced,
                    self.t_induced,
                )
            ],
            "chain_relations": self.chain_relations,
            "conjugate_to_published": self.conjugate_to_published,
            "intertwiner_determinant": str(self.intertwiner.determinant()),
            "invariant_dimension": self.invariant_dimension,
            "invariant_representatives": [
                _sparse_vector(representative)
                for representative in self.invariant_representatives
            ],
            "status": (
                "exact constituent deck-linearized cocycle with a source-bound "
                "equivariant character; mapping cone remains pending"
            ),
        }


def _align_action(
    derived: DPSurfaceSerreDeckAction,
    published: SerreKernelAction,
) -> PublishedConstituentDeckAction:
    """Apply the unique source-bound character and certify conjugacy."""

    twists = _matching_twists(derived, published)
    if twists != ((OMEGA, Eisenstein(1)),):
        raise ValueError("published constituent linearization is not uniquely identified")
    p_twist, t_twist = twists[0]
    p_induced = derived.p_induced.scale(p_twist)
    t_induced = derived.t_induced.scale(t_twist)
    representatives = derived.extension.ext_one_representatives
    return PublishedConstituentDeckAction(
        derived,
        published,
        p_twist,
        t_twist,
        _scale_chain_map(derived.p_action, p_twist),
        _scale_chain_map(derived.t_action, t_twist),
        p_induced,
        t_induced,
        _intertwiner(
            p_induced,
            t_induced,
            published.p,
            published.t,
        ),
        _fixed_representatives(representatives, p_induced, t_induced),
    )


@cache
def published_constituent_deck_actions(
) -> tuple[PublishedConstituentDeckAction, ...]:
    """Return both exact source-aligned constituent action certificates."""

    results = tuple(
        _align_action(derived, published)
        for derived, published in zip(
            published_constituent_serre_actions(),
            serre_data().actions,
            strict=True,
        )
    )
    if not all(
        result.chain_relations
        and result.conjugate_to_published
        and result.invariant_dimension == 1
        for result in results
    ):
        raise ValueError("a published constituent deck-action gate failed")
    return results


def write_published_constituent_deck_actions(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed constituent action certificate."""

    payload: dict[str, object] = {
        "schema": "published-constituent-deck-actions-v1",
        "constituents": [
            result.as_record() for result in published_constituent_deck_actions()
        ],
        "common_linearization_character": {"P": "omega", "T": "1"},
        "linearization_status": (
            "source-bound selection from published equivariant representations; "
            "not a fundamental derivation"
        ),
        "outer_extension_reconstructed": False,
        "next_required_object": (
            "mapping-cone presentations of W1 and W2 from the certified "
            "invariant constituent cocycles"
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
    """Regenerate the exact constituent deck-action artifact."""

    payload = write_published_constituent_deck_actions()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"common_linearization_character: {payload['common_linearization_character']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PublishedConstituentDeckAction",
    "published_constituent_deck_actions",
]
