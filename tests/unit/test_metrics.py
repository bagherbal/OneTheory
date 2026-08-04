"""Test the fail-closed positive-twist metric gateway.

Owns:
    Exact assertions for the absent extension cocycle, section basis, and metric
    prerequisites exposed by the Schoen metric boundary.

Depends on:
    The assembled reality state, metric verification certificates, gates, and pytest.

Must not:
    Treat dimension metadata as a section basis, run numerical geometry, or create a
    carrier metric from a guessed extension or sampled evaluation matrix.

Phase 0:
    Boundary tests only; the positive-twist section and metric package remain open.
"""

from onetheory.reality import assemble_reality
from onetheory.verification.certificates import (
    certify_metric_boundary,
    metric_input_gate,
)
from onetheory.verification.evidence import EvidenceClass
from onetheory.verification.gates import GateState


def test_metric_boundary_preserves_the_first_missing_input() -> None:
    state = assemble_reality()
    gate = metric_input_gate(state)
    certificates = certify_metric_boundary(state)

    assert gate.state is GateState.MISSING_INPUT
    assert gate.prerequisites[0] == (
        "four local non-split extension cocycles e_A in one common Cech basis"
    )
    assert all(certificate.passed for certificate in certificates)
    assert all(
        certificate.evidence.evidence_class is EvidenceClass.MISSING_INPUT
        for certificate in certificates
    )
    assert certificates[0].evidence.prerequisites == gate.prerequisites
