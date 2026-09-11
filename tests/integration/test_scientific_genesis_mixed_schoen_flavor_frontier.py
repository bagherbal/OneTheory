"""Test fail-closed reranking of the exact flavor frontier.

Owns:
    Regression gates for excluding unavailable up/down routes and selecting
    the minimum remaining source-supported Yukawa sector.

Depends on:
    The content-addressed post-obstruction flavor frontier artifact.

Must not:
    Rank by observations, erase scoped failure reasons, or treat workload
    selection as a computed Yukawa matrix.

Phase 0:
    Integration tests for exact flavor scheduling after chain obstructions.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_flavor_frontier import (
    OUTPUT,
)


def test_post_obstruction_frontier_selects_dirac_neutrinos() -> None:
    """The reusable up Higgs makes neutrinos the minimum available sector."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")

    assert digest == _canonical_digest(payload)
    assert payload["excluded_sectors"] == [
        {
            "name": "up",
            "exact_reason": (
                "complete universal holomorphic matrix has exact rank zero"
            ),
        },
        {
            "name": "down",
            "exact_reason": (
                "required strict Higgs character has exact chain H1 dimension zero"
            ),
        },
    ]
    assert payload["remaining_sector_workloads"] == {
        "charged_lepton": 11,
        "dirac_neutrino": 8,
    }
    assert payload["selected_next_sector"] == "dirac_neutrino"
    assert payload["selected_coupling"] == ["L", "nu^c", "H_u"]
    assert payload["selected_required_new_matter_characters"] == [
        [0, 0],
        [0, 2],
    ]
    assert payload["selected_reused_higgs_character"] == [0, 1]
    assert payload["selected_minimum_new_chain_object_count"] == 8
    assert payload["selection_exact"] is True
    assert payload["observational_inputs_used"] is False
    assert payload["arbitrary_extension_point_selected"] is False
    assert payload["yukawa_coefficient_computed"] is False
