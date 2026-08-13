"""Test the evidence-backed Scientific Genesis governance artifact.

Owns:
    Regression checks for deterministic state generation, epistemic statuses,
    the acyclic dependency graph, and the suspended action frontier.

Depends on:
    The research audit, generated exact carrier artifacts, and pytest.

Must not:
    Treat governance metadata as a carrier, select an extension point, or
    convert a blocked scientific edge into an implemented bridge.

Phase 0:
    State-audit tests only; the rank-four algebraic lawful locus remains pending.
"""

import json
from pathlib import Path

from research.experiments.scientific_genesis.audit import (
    build_state,
    validate_state,
)

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "data/generated/scientific_genesis/scientific_genesis_state.json"


def test_scientific_genesis_state_is_current_and_valid() -> None:
    """The frozen artifact exactly matches a fresh evidence reconstruction."""

    stored = json.loads(STATE.read_text(encoding="utf-8"))
    rebuilt = build_state()

    validate_state(stored)
    assert stored == rebuilt


def test_vertical_path_uses_a_universal_family_without_selecting_a_point() -> None:
    """The scheduler pivots to pair 73 while preserving its open carrier gates."""

    state = build_state()
    path = state["recommended_vertical_path"]
    checkpoint = state["automorphism_checkpoint"]
    claims = {claim["id"]: claim for claim in state["claims"]}

    assert path["candidate_pair"] == 73
    assert path["criteria"]["invariant_ext_dimension"] == 4
    assert path["criteria"]["orbit_parameter_space"] == "P^3(Q(omega))"
    assert path["criteria"]["arbitrary_point_selected"] is False
    assert checkpoint["completed_pairs"] == 1296
    assert checkpoint["suspended"] is True
    assert claims["universal_rank_four_family"]["status"] == "COMPUTED"
    assert claims["algebraic_lawful_locus"]["status"] == "COMPUTED"
    assert claims["necessary_stability_walls"]["status"] == "COMPUTED"
    assert path["selection_status"] == "retired by exact family-wide stability no-go"
    assert claims["stability_chamber"]["status"] == "REFUTED"
    assert claims["genesis_to_uv_bridge"]["status"] == "BLOCKED"
    assert state["fitted_inputs"] == []
