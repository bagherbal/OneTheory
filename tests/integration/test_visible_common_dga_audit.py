"""Test the research-side physical common-DGA sufficiency boundary.

Owns:
    Evidence that the active reconstruction audit reports absent carrier inputs
    without creating a synthetic replacement.

Depends on:
    The local research audit, production contracts, and pytest.

Must not:
    Treat dimensions or expected residues as inputs, import observations, or
    promote an unresolved common-DGA package into production.

Phase 0:
    Boundary test only; physical common-DGA reconstruction remains unresolved.
"""

from pathlib import Path

from research.experiments.visible_common_dga.audit import (
    SOURCE_HASHES,
    audit_inputs,
)


def test_common_dga_audit_stops_at_the_first_absent_input() -> None:
    root = Path(__file__).resolve().parents[2]
    audit = audit_inputs(root)

    assert audit.first_missing_input == (
        "carrier-specific V1/V2 resolutions in a synchronized common Cech-Koszul basis"
    )
    assert not audit.promotable
    assert audit.prerequisite_chain[0] == audit.first_missing_input
    assert audit.published_files == ()
    assert tuple(audit.source_hashes) == SOURCE_HASHES
