"""Test the exact fail-closed hidden-bundle boundary.

Owns:
    Hidden input status, evidence certificates, and gate prerequisite chains.

Depends on:
    The assembled reality state, hidden production status, verification records,
    and pytest.

Must not:
    Treat candidate-750 metadata as a global bundle proof or assume descent,
    stability, restrictions, spectrum, or a hidden gauge group.

Phase 0:
    Boundary tests only; hidden bundle construction remains unresolved.
"""

from onetheory.reality import assemble_reality
from onetheory.verification.certificates import (
    certify_hidden_boundary,
    hidden_bundle_input_gate,
)
from onetheory.verification.evidence import EvidenceClass
from onetheory.verification.gates import GateState


def test_hidden_boundary_preserves_the_first_missing_input() -> None:
    state = assemble_reality()
    gate = hidden_bundle_input_gate(state)
    certificates = certify_hidden_boundary(state)

    assert gate.state is GateState.MISSING_INPUT
    assert gate.prerequisites[0].startswith("all 44 objective")
    assert all(certificate.passed for certificate in certificates)
    assert all(
        certificate.evidence.evidence_class is EvidenceClass.MISSING_INPUT
        for certificate in certificates
    )
    assert certificates[0].evidence.prerequisites == gate.prerequisites
