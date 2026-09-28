"""Regress the primitive-only shortcut of the alternate up null channel.

Owns:
    The global A-line chain pairing and its exact full Leibniz defect
    for the a0 null-primitive screen.

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
from research.experiments.scientific_genesis.alternate_up_mixed_scalar_trace import (
    _a_line_pairing,
)
from research.experiments.scientific_genesis.alternate_up_null_shortcut_screen import (
    OUTPUT,
    alternate_up_null_shortcut_screen,
)


def test_direct_null_primitive_term_obeys_leibniz_but_does_not_close() -> None:
    """The nonclosed primitive, not omitted syzygies, explains this defect."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert alternate_up_null_shortcut_screen() == payload
    assert payload["extension_cup_exact_cycle"] is True
    assert payload["syzygy_term_count"] > 0
    assert payload["full_cup_evaluated_by_exact_a_line_chain_map"] is True
    assert payload["a_line_syzygy_annihilation_exact"] is True
    assert payload["primitive_only_scalar_differential_term_count"] > 0
    assert payload["primitive_only_scalar_closed"] is False
    assert payload["actual_full_leibniz_identity_exact"] is True
    assert payload["primitive_differential_accounts_for_entire_defect"] is True
    assert payload["null_to_null_coefficient_computed"] is False
    assert payload["rank_three_established"] is False


def test_a_line_map_is_global_without_minor_inversion() -> None:
    """Exact Hilbert--Burch annihilation agrees with all six chart forms."""

    pairings = _a_line_pairing()
    assert len(pairings) == 3
    assert all(pairing.terms for pairing in pairings)
    assert all(
        exponents[3:] == (0, 0)
        for pairing in pairings for exponents, _ in pairing.terms
    )
