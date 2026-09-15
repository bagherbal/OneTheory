"""Test source-action routing of synchronized deck characters.

Owns:
    Regression gates for exact character inversion, physical Higgs support,
    and reuse of the existing strict cochain without altering chain maps.

Depends on:
    The content-addressed synchronized character-convention correction.

Must not:
    Preserve superseded up-sector labels, fit a character shift, or infer a
    Yukawa value from a one-dimensional Higgs sector.

Phase 0:
    Integration tests for physical character-convention routing only.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_character_convention import (
    OUTPUT,
    inverse_character,
    mixed_schoen_character_convention,
    write_mixed_schoen_character_convention,
)


def test_source_action_is_exact_inverse_pullback() -> None:
    """Every forward sector maps factorwise to its inverse source character."""

    result = mixed_schoen_character_convention()

    assert result.exact
    assert len(result.sectors) == 9
    assert all(
        sector.source_character == inverse_character(sector.forward_character)
        for sector in result.sectors
    )
    assert result.source_h1_characters == (
        (0, 0),
        (0, 2),
        (1, 0),
        (1, 2),
    )


def test_strict_forward_cochain_routes_to_physical_down_higgs() -> None:
    """The existing strict class is H_d, while the H_u prerequisite is absent."""

    result = mixed_schoen_character_convention()

    assert result.strict_forward_character == (0, 1)
    assert result.strict_source_character == (0, 2)
    assert result.source_h1_dimension((0, 2)) == 1
    assert result.source_h1_dimension((0, 1)) == 0
    assert result.strict_cochain_term_count == 27
    assert result.strict_cochain_is_cycle
    assert result.strict_cochain_has_forward_character


def test_character_convention_artifact_is_content_addressed() -> None:
    """The frozen correction reproduces exactly without fitted inputs."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    fresh = write_mixed_schoen_character_convention()

    assert digest == _canonical_digest(stored)
    assert fresh["artifact_digest"] == digest
    assert stored["physical_down_higgs_representative_available"] is True
    assert stored["physical_up_higgs_representative_available"] is False
    assert stored["prior_up_and_neutrino_physical_routing_valid"] is False
    assert stored["prior_down_higgs_obstruction_valid"] is False
    assert stored["chain_maps_changed"] is False
    assert stored["character_shift_fitted"] is False
    assert stored["observational_inputs_used"] is False
