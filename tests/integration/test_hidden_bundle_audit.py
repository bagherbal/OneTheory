"""Test the fail-closed hidden-bundle input boundary.

Owns:
    Evidence that the bounded objective-(28) search does not treat support
    counts, sampled ranks, or topology as bundle existence.

Depends on:
    The research hidden-bundle audit, production hidden status, and pytest.

Must not:
    Fabricate candidate maps, infer global rank from samples, assume descent or
    stability, or select a hidden gauge group.

Phase 0:
    Boundary test only; no hidden bundle or hidden spectrum is promoted.
"""

from pathlib import Path

from research.experiments.hidden_bundle.audit import SOURCE_HASHES, audit_inputs


def test_hidden_audit_stops_at_the_missing_support_records() -> None:
    root = Path(__file__).resolve().parents[2]
    audit = audit_inputs(root)

    assert audit.first_missing_input == (
        "all 44 objective-(28) support-pattern records with exact map data"
    )
    assert not audit.promotable
    assert audit.prerequisite_chain[0] == audit.first_missing_input
    assert audit.published_files == ()
    assert tuple(audit.source_hashes) == SOURCE_HASHES
