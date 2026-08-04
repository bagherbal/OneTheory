"""Test the exact fail-closed conic Pfaffian boundary.

Owns:
    Immutable status reporting for seed conics, relative-duality maps,
    determinant lines, and the lawful instanton-sum boundary.

Depends on:
    The generic instanton boundary contract, verification records, the assembled
    reality state, and pytest.

Must not:
    Treat orbit counts as embeddings, promote witness quartics, invent phases,
    or construct hidden restricted determinants.

Phase 0:
    Boundary tests only; physical Pfaffians and determinant-line maps are absent.
"""

from onetheory.reality import assemble_reality
from onetheory.verification.certificates import (
    certify_instanton_boundary,
    conic_pfaffian_input_gate,
)
from onetheory.verification.evidence import EvidenceClass
from onetheory.verification.gates import GateState


def test_instanton_boundary_preserves_the_first_missing_input() -> None:
    state = assemble_reality()
    gate = conic_pfaffian_input_gate(state)
    certificates = certify_instanton_boundary(state)

    assert gate.state is GateState.MISSING_INPUT
    assert gate.prerequisites[0].startswith("explicit embeddings")
    assert all(certificate.passed for certificate in certificates)
    assert all(
        certificate.evidence.evidence_class is EvidenceClass.MISSING_INPUT
        for certificate in certificates
    )
    assert certificates[0].evidence.prerequisites == gate.prerequisites
