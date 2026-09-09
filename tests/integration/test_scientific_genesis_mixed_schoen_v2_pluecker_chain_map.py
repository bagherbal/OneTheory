"""Test the first exact equivariant V2 determinant pairing.

Owns:
    Regression gates for closure, graded exchange, determinant linearization,
    strict character projection, and fail-closed higher-product status.

Depends on:
    The committed content-addressed V2 Pluecker chain-map artifact.

Must not:
    Supply the missing grouped-chain homotopy or report a Yukawa coefficient.

Phase 0:
    Integration tests for the scoped bottom-matter pairing certificate.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_v2_pluecker_chain_map import (
    OUTPUT,
)


def test_v2_pluecker_pairing_artifact_is_exact_and_fail_closed() -> None:
    """The source-derived pairing closes without fabricating the next homotopy."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")

    assert digest == _canonical_digest(payload)
    assert payload["determinant_ambient_degrees"] == [2, 0, -2, 0]
    assert payload["target_character_exponents"] == [0, 2]
    assert payload["determinant_frame_character_exponents"] == [1, 1]
    assert payload["pairing_term_count"] == 8_592
    assert payload["reverse_pairing_term_count"] == 8_586
    assert payload["pairing_is_cycle"] is True
    assert payload["reverse_pairing_is_cycle"] is True
    assert payload["pairing_reduced_coordinate_count"] == 0
    assert payload["reverse_reduced_coordinate_count"] == 0
    assert payload["projection_depth"] == 2
    assert payload["reverse_projection_depth"] == 2
    assert payload["exchange_primitive_term_count"] == 3_900
    assert payload["exchange_identity_exact"] is True
    assert payload["equivariant_pairing_term_count"] == 11_340
    assert payload["equivariant_pairing_is_cycle"] is True
    assert payload["equivariant_character_exact"] is True
    assert payload["exact"] is True
    assert payload["f1_extension_defined"] is False
    assert payload["holomorphic_yukawa_entry_available"] is False
    assert payload["extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert "chain homotopy" in payload["first_missing_input"]
