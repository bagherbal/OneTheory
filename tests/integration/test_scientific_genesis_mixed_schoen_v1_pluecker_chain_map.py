"""Guard the exact V1 determinant pairing on the reverse down slice.

Owns:
    Content-addressed checks for closure, graded exchange, and strict deck
    routing of the physical-character first-constituent pairing.

Depends on:
    The generated research certificate and deterministic artifact hashing.

Must not:
    Recompute the large source representatives during routine tests or infer
    a central Yukawa value from the determinant pairing alone.

Phase 0:
    Integration tests for one research-only V1 pairing prerequisite.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_v1_pluecker_chain_map import (
    OUTPUT,
)

EXPECTED_DIGEST = (
    "a55b9bf4af56a3aa04c59d743a31521fad54e86a8af0415a5e58cef80f8690f8"
)


def test_physical_v1_pairing_is_exact_without_yukawa_claim() -> None:
    """The source-derived pairing closes in both orders and descends strictly."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == EXPECTED_DIGEST
    assert digest == _canonical_digest(payload)
    assert payload["schema"] == "mixed-schoen-v1-pluecker-chain-map-v1"
    assert payload["forward_matter_character_exponents"] == [[1, 2], [2, 0]]
    assert payload["target_character_exponents"] == [0, 2]
    assert payload["determinant_frame_character_exponents"] == [1, 0]
    assert payload["determinant_ambient_degrees"] == [-2, 0, 2, 0]
    assert payload["pairing_term_count"] == 8892
    assert payload["reverse_pairing_term_count"] == 8886
    assert payload["pairing_reduced_coordinate_count"] == 0
    assert payload["reverse_reduced_coordinate_count"] == 0
    assert payload["exchange_primitive_term_count"] == 6984
    assert payload["equivariant_pairing_term_count"] == 13968
    assert payload["pairing_is_cycle"] is True
    assert payload["reverse_pairing_is_cycle"] is True
    assert payload["exchange_identity_exact"] is True
    assert payload["equivariant_pairing_is_cycle"] is True
    assert payload["equivariant_character_exact"] is True
    assert payload["exact"] is True
    assert payload["holomorphic_yukawa_entry_available"] is False
    assert payload["extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
