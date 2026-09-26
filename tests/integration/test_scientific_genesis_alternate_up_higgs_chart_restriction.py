"""Regress actual strict Hom restrictions on the alternate I6 atlas.

Owns:
    Exact six-chart support and right-factor closure from saved full terms.

Depends on:
    The frozen alternate mixed Hom differential and its persisted cocycle.

Must not:
    Treat local restrictions as glued tensor or cone-level Higgs states.

Phase 0:
    Integration checks for the first actual Hom transport inputs.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_up_higgs_chart_restriction import (
    OUTPUT,
    alternate_up_higgs_chart_restriction,
)


def test_six_actual_hom_restrictions_are_closed() -> None:
    """Every right singleton contains only closed syzygy-dual terms."""

    payload = alternate_up_higgs_chart_restriction()
    records = payload["right_chart_records"]
    assert len(records) == 6
    assert all(item["right_chart_restricted_cycle_exact"] for item in records)
    assert all(item["middle_term_count"] == 0 for item in records)
    assert all(item["syzygy_dual_term_count"] > 0 for item in records)
    assert [item["term_count"] for item in records] == [27, 36, 27, 36, 27, 36]
    assert payload["right_fiber_overlap_term_count"] == 135
    assert payload["right_fiber_overlap_middle_term_count"] == 81
    assert payload["right_fiber_overlap_syzygy_term_count"] == 54
    assert payload["hom_to_tensor_transport_constructed"] is False


def test_restriction_artifact_is_content_addressed() -> None:
    """Saved chart support is pinned to the complete strict Hom cochain."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert payload == alternate_up_higgs_chart_restriction()
    assert payload["exterior_cone_higgs_cocycle_constructed"] is False
