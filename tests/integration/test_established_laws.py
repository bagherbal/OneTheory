"""Test the separate established-law and carrier composition roots.

Owns:
    Established four-dimensional law assembly, carrier reuse of the same Standard
    Model object, external certificates, and unresolved physical-instance gating.

Depends on:
    `onetheory.reality`, verification audit/certificates/gates, and pytest.

Must not:
    Add adapters between theories, import source documents, or present unresolved
    couplings, Yukawa entries, or gravitational normalization as values.

Phase 0:
    Parameterized established laws are executable; physical parameter admission is
    fail-closed.
"""

import pytest

from onetheory.core.errors import MissingPhysicalInput
from onetheory.reality import (
    PHYSICAL_4D_MISSING_CHAIN,
    established_4d_laws,
    one_theory_carrier_state,
    request_physical_four_dimensional_model,
)
from onetheory.verification.audit import audit_established_4d_laws
from onetheory.verification.certificates import certify_established_4d_laws
from onetheory.verification.gates import GateState, parameterized_law_gate


def test_established_laws_are_exactly_checked_and_carrier_reuses_same_model_object() -> None:
    state = one_theory_carrier_state()
    certificates = certify_established_4d_laws(state.laws)
    audit = audit_established_4d_laws(state.laws)

    assert state.laws.exact_law_certificates_pass
    assert state.laws.standard_model.electric_charge_assignments_valid
    assert all(certificate.passed for certificate in certificates)
    assert audit.exact_structure
    assert not audit.source_documents_read
    assert not audit.observations_used
    assert state.laws.standard_model is state.carrier.value("standard_model")


def test_physical_instance_and_parameter_gate_remain_fail_closed() -> None:
    laws = established_4d_laws()
    gate = parameterized_law_gate(
        "four-dimensional-physical-instance",
        laws.exact_law_certificates_pass,
        laws.unresolved_parameters,
        "established four-dimensional laws",
    )

    assert gate.state is GateState.MISSING_INPUT
    assert gate.prerequisites == PHYSICAL_4D_MISSING_CHAIN[1:]
    with pytest.raises(MissingPhysicalInput) as error:
        request_physical_four_dimensional_model()
    assert error.value.chain == (
        "physical four-dimensional model",
        *PHYSICAL_4D_MISSING_CHAIN,
    )
