"""Certify derived mapping cones for the published constituent extensions.

Owns:
    Exact sparse Čech lifts of the two invariant constituent Ext classes and
    their block-differential square-zero mapping-cone certificates.

Depends on:
    Source-aligned invariant dP9 cocycles and the generic projective Čech
    monomial engine.

Must not:
    Replace a derived cone certificate with uncomputed local transition
    matrices, infer local freeness independently of the published theorem, or
    claim the Schoen outer extension has been reconstructed.

Phase 0:
    W1/W2 have exact derived Čech cone inputs; synchronized Schoen outer Hom
    remains the next unresolved computation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from research.experiments.computable_carrier.dp9_serre_cech import (
    DPSurfaceSerreCechCocycle,
    dp9_serre_cech_cocycle,
)
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .published_constituent_deck_actions import (
    PublishedConstituentDeckAction,
    published_constituent_deck_actions,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/published_constituent_mapping_cones.json"


@dataclass(frozen=True, slots=True)
class PublishedConstituentMappingCone:
    """One invariant constituent class and its exact derived cone identity."""

    action: PublishedConstituentDeckAction
    cocycle: DPSurfaceSerreCechCocycle

    @property
    def chain_fixed(self) -> bool:
        """Return whether the chosen cocycle is fixed before taking cohomology."""

        representative = self.cocycle.source_representative
        return (
            self.action.p_action.component(1)(representative) == representative
            and self.action.t_action.component(1)(representative) == representative
        )

    @property
    def exact(self) -> bool:
        """Return every exact gate available for the derived constituent cone."""

        return (
            self.cocycle.total_closed
            and self.cocycle.derived_cone_squared_zero
            and self.chain_fixed
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the derived cone and its explicit implementation boundary."""

        return {
            "constituent": self.action.published.name,
            "cech_hypercocycle": self.cocycle.as_record(),
            "chain_fixed_under_deck_group": self.chain_fixed,
            "derived_mapping_cone_available": self.exact,
            "published_local_freeness_theorem_required": True,
            "local_transition_matrices_materialized": False,
            "status": (
                "exact invariant derived Cech mapping-cone input; local "
                "transition matrices and synchronized Schoen lift remain open"
            ),
        }


@cache
def published_constituent_mapping_cones(
) -> tuple[PublishedConstituentMappingCone, ...]:
    """Build both exact invariant constituent derived-cone certificates."""

    results = tuple(
        PublishedConstituentMappingCone(
            action,
            dp9_serre_cech_cocycle(
                action.derived.extension,
                action.invariant_representatives[0],
            ),
        )
        for action in published_constituent_deck_actions()
    )
    if not all(result.exact for result in results):
        raise ValueError("a published constituent mapping-cone gate failed")
    return results


def write_published_constituent_mapping_cones(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed derived constituent-cone certificate."""

    payload: dict[str, object] = {
        "schema": "published-constituent-mapping-cones-v1",
        "constituents": [
            result.as_record() for result in published_constituent_mapping_cones()
        ],
        "all_derived_cones_exact": True,
        "schoen_outer_extension_reconstructed": False,
        "next_required_object": (
            "synchronized Schoen Cech-Koszul total complexes for the two "
            "derived constituent cones and their outer RHom"
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
    """Regenerate the exact constituent derived-cone artifact."""

    payload = write_published_constituent_mapping_cones()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"all_derived_cones_exact: {payload['all_derived_cones_exact']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PublishedConstituentMappingCone",
    "published_constituent_mapping_cones",
]
