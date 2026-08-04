"""Test the fail-closed visible positive-twist metric audit.

Owns:
    Evidence that generic section machinery does not substitute for carrier section
    artifacts, extension cocycles, lifts, or metric certificates.

Depends on:
    The research visible-metrics audit, production metric boundary, and pytest.

Must not:
    Promote dimension ledgers, fabricate Cech data, or treat numerical benchmarks as
    carrier evidence.

Phase 0:
    Audit test only; the earliest carrier input remains unavailable.
"""

from pathlib import Path

from research.experiments.visible_metrics.audit import SOURCE_HASHES, audit_inputs


def test_visible_metrics_audit_stops_at_the_extension_cocycle() -> None:
    root = Path(__file__).resolve().parents[2]
    audit = audit_inputs(root)

    assert audit.first_missing_input == (
        "four local non-split extension cocycles e_A in one common Cech basis"
    )
    assert not audit.promotable
    assert audit.prerequisite_chain[0] == audit.first_missing_input
    assert audit.published_files == ()
    assert tuple(audit.source_hashes) == tuple(
        entry for entry in SOURCE_HASHES if entry[1]
    )
