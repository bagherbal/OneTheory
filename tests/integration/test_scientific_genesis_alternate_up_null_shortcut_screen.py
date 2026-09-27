"""Regress the failed direct truncation of the alternate up null channel.

Owns:
    Exact extension-cup support and scalar-closure checks for the a0 screen.

Depends on:
    The research-only screen and its content-addressed generated artifact.

Must not:
    Interpret a noncycle as a Yukawa, infer rank three, or discard the
    missing same-cone Higgs correction.

Phase 0:
    Research-only negative test of a tempting shortcut.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_up_null_shortcut_screen import (
    OUTPUT,
    alternate_up_null_shortcut_screen,
)


def test_direct_null_primitive_truncation_does_not_close() -> None:
    """A projected scalar without syzygies cannot decide the up rank."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert alternate_up_null_shortcut_screen() == payload
    assert payload["extension_cup_exact_cycle"] is True
    assert payload["syzygy_term_count"] > 0
    assert payload["full_cup_rejected_by_scoped_contraction"] is True
    assert payload["truncated_scalar_differential_term_count"] > 0
    assert payload["truncated_scalar_closed"] is False
    assert payload["null_to_null_coefficient_computed"] is False
    assert payload["rank_three_established"] is False
