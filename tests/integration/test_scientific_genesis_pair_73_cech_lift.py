"""Test the pair-73 chain-level hypercocycle certificate.

Owns:
    Pair-local source binding, exact descent support, total-cycle closure, and
    fail-closed carrier boundaries for the universal pair-73 Ext family.

Depends on:
    Content-addressed Scientific Genesis artifacts and the deterministic
    pair-73 chain-lift reconstruction.

Must not:
    Select an extension point, infer local freeness or quotient descent, or
    call the derived mapping cone a stable physical carrier.

Phase 0:
    Chain-level extension tests only; algebraic lawful loci remain open.
"""

import json
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.pair_73_cech_lift import (
    OUTPUT,
    PAIR_INDEX,
    PARTIAL,
    SOURCE,
    pair_73_cech_lift,
)

ROOT = Path(__file__).resolve().parents[2]


def test_pair_73_source_slice_is_bound_to_its_parent_certificate() -> None:
    """The compact source preserves exact pair and parent content addresses."""

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    digest = source.pop("artifact_digest")
    pair = source["pair"]

    assert digest == _canonical_digest(source)
    assert pair["global_pair_index"] == PAIR_INDEX
    assert pair["certificate_digest"] == source["pair_certificate_digest"]
    assert pair["exact"] is True
    assert pair["cocycle_basis"]["dimension"] == 4


def test_pair_73_all_chain_lifts_close_without_selecting_a_point() -> None:
    """Every invariant basis class closes through the full Čech resolution."""

    lift = pair_73_cech_lift()
    record = lift.as_record()

    assert lift.lifted_term_counts == ((36, 504, 1764, 0),) * 4
    assert len(set(lift.lifted_term_digests)) == 4
    assert all(len(digest) == 64 for digest in lift.lifted_term_digests)
    assert lift.source_cycle_exact
    assert lift.total_cycles_exact
    assert lift.universal_linearity_exact
    assert record["chain_level_lift_constructed"] is True
    assert record["derived_mapping_cone_available"] is True
    assert record["mapping_cone_constructed"] is True
    assert record["mapping_cone_squared_zero"] is True
    assert record["arbitrary_extension_point_selected"] is False
    assert record["local_freeness_locus_computed"] is False
    assert record["quotient_descent_computed"] is False
    assert record["structure_group_locus_computed"] is False


def test_pair_73_chain_lift_artifacts_are_complete_and_current() -> None:
    """The resumable checkpoint and final certificate agree exactly."""

    checkpoint = json.loads(PARTIAL.read_text(encoding="utf-8"))
    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert checkpoint["schema"].endswith("v2")
    assert set(checkpoint["completed_classes"]) == {"0", "1", "2", "3"}
    assert stored == pair_73_cech_lift().as_record()
    assert digest == _canonical_digest(stored)
    assert OUTPUT.is_relative_to(ROOT)
