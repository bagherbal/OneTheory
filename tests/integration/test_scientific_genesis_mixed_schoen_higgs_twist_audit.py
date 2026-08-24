"""Integration tests for the determinant-twist Higgs obstruction audit."""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_higgs_twist_audit import (
    OUTPUT,
    _uniform_character_shift_exists,
)


def test_higgs_character_mismatch_has_no_scalar_shift_repair() -> None:
    """No determinant scalar character aligns the raw and physical actions."""

    raw = ((1, 0), (1, 1), (2, 0), (2, 1))
    physical = ((0, 1), (0, 2), (1, 2), (2, 1))

    assert not _uniform_character_shift_exists(raw, physical)


def test_higgs_twist_artifact_is_exact_and_fail_closed() -> None:
    """The committed certificate binds the exact obstruction boundary."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    characters = payload["raw_hom_character_multiplicities"]

    assert digest == _canonical_digest(payload)
    assert payload["geometric_cohomology_h0_to_h3"] == [0, 4, 4, 0]
    assert payload["all_hom_transfer_gates_exact"] is True
    assert payload["uniform_character_shift_exists"] is False
    assert payload["equivariant_tensor_identification_available"] is False
    assert payload["physical_higgs_representative_available"] is False
    assert payload["route_blocked_exact"] is True
    assert [item["character_exponents"] for item in characters] == [
        [1, 0],
        [1, 1],
        [2, 0],
        [2, 1],
    ]
    assert payload["source_tensor_character_comparison"]["matches"] is False
    assert "equivariant chain comparison" in payload["first_missing_input"]
