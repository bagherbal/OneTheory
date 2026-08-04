"""Test fail-closed scientific evidence and gate construction.

Owns:
    Exact certificate evidence and missing-input gate behavior for the physical
    common-DGA boundary.

Depends on:
    The assembled production state, verification certificates, verification
    gates, and pytest.

Must not:
    Promote missing representatives, infer physical traces, or use observations
    to select a carrier input.

Phase 0:
    Verification boundary tests only; no physical common-DGA package exists.
"""

from onetheory.reality import assemble_reality
from onetheory.verification.certificates import (
    common_dga_input_gate,
    unresolved_frontier_evidence,
)
from onetheory.verification.evidence import EvidenceClass
from onetheory.verification.gates import GateState


def test_common_dga_gate_and_evidence_preserve_the_same_chain() -> None:
    gate = common_dga_input_gate(assemble_reality())
    evidence = unresolved_frontier_evidence()[0]

    assert gate.state is GateState.MISSING_INPUT
    assert not gate.passed
    assert gate.prerequisites[0].startswith("carrier-specific V1/V2")
    assert evidence.evidence_class is EvidenceClass.MISSING_INPUT
    assert "carrier-specific V1/V2" in evidence.statement
