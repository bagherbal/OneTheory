"""Test the fail-closed physical conic Pfaffian input boundary.

Owns:
    Evidence that explicit seed embeddings are distinguished from conic counts,
    normal-bundle claims, and nonphysical witness quartics.

Depends on:
    The research conic-Pfaffian audit, production instanton status, and pytest.

Must not:
    Construct restriction maps, promote witness polynomials, attach phases, or
    form a scalar orbit sum.

Phase 0:
    Boundary test only; physical seed Pfaffians remain unresolved.
"""

from pathlib import Path

from research.experiments.conic_pfaffians.audit import SOURCE_HASHES, audit_inputs


def test_conic_audit_stops_before_restriction_data() -> None:
    root = Path(__file__).resolve().parents[2]
    audit = audit_inputs(root)

    assert audit.first_missing_input == (
        "explicit embeddings of the two seed conics in frozen Schoen Cox coordinates"
    )
    assert not audit.promotable
    assert audit.prerequisite_chain[0] == (
        "explicit embeddings of the two seed conics in frozen Schoen Cox coordinates"
    )
    assert audit.published_files == ()
    assert tuple(audit.source_hashes) == SOURCE_HASHES
