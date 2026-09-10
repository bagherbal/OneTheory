"""Test source-pinned Wilson support for every Yukawa sector.

Owns:
    Regression gates for published multiplet characters, invariant Yukawa
    triples, and the exact minimum-work selection of the next flavor sector.

Depends on:
    The content-addressed flavor-character support artifact and exact source
    locators fixed by the visible-carrier manifest.

Must not:
    Infer support from observations, treat a character as a Yukawa value, or
    claim that selecting a sector computes its holomorphic matrix.

Phase 0:
    Integration tests for exact post-up-no-go flavor routing.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_flavor_character_support import (
    OUTPUT,
)


def _payload() -> dict[str, object]:
    """Load the routing artifact after checking its content digest."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    return payload


def test_published_characters_form_all_four_invariant_triples() -> None:
    """Source Wilson characters fix exact quotient-invariant couplings."""

    payload = _payload()
    multiplets = {
        record["name"]: record["required_cohomology_character_exponents"]
        for record in payload["multiplets"]
    }
    sectors = {record["name"]: record for record in payload["sectors"]}

    assert payload["source"] == {
        "arxiv_id": "hep-th/0512177",
        "version": "v3",
        "source_archive_sha256": (
            "ad4ea10b3d765553ccdd072922a6bda6"
            "19866ea814c532b8ffe74ddafc7fe73f"
        ),
        "matter_wilson_locator": "eq:burt4",
        "higgs_wilson_locator": "eq:19",
    }
    assert multiplets == {
        "Q": [2, 1],
        "u^c": [1, 1],
        "d^c": [1, 0],
        "L": [0, 0],
        "e^c": [0, 1],
        "nu^c": [0, 2],
        "H_u": [0, 1],
        "H_d": [0, 2],
    }
    assert set(sectors) == {
        "up",
        "down",
        "charged_lepton",
        "dirac_neutrino",
    }
    assert all(
        sector["character_product_is_invariant"] is True
        for sector in sectors.values()
    )


def test_exact_chain_workload_selects_the_down_sector() -> None:
    """Existing up inputs make down the least new exact-chain workload."""

    payload = _payload()
    sectors = {record["name"]: record for record in payload["sectors"]}

    assert {
        name: sector["minimum_new_chain_object_count"]
        for name, sector in sectors.items()
    } == {
        "up": 0,
        "down": 7,
        "charged_lepton": 11,
        "dirac_neutrino": 8,
    }
    assert payload["selected_next_sector"] == "down"
    assert payload["selected_required_new_matter_character"] == [1, 0]
    assert payload["selected_required_new_higgs_character"] == [0, 2]
    assert payload["selected_minimum_new_chain_object_count"] == 7
    assert payload["observational_inputs_used"] is False
    assert payload["extension_point_selected"] is False
    assert payload["yukawa_coefficient_computed"] is False
