"""Test the first executable established-reality slice.

Owns:
    Composition through the exact graph, immutable established state, external
    exact certificates, provenance classes, and explicit unresolved outputs.

Depends on:
    `onetheory.reality`, `onetheory.verification`, core errors, and pytest.

Must not:
    Trigger metrics, instantons, hidden-bundle construction, vacuum stabilization,
    physical normalization, simulation, or low-energy prediction code.

Phase 0:
    Integration tests for the established carrier slice only.
"""

from __future__ import annotations

import pytest

from onetheory.core.errors import MissingPhysicalInput
from onetheory.reality import (
    assemble_reality,
    request_hidden_bundle,
    request_instanton_amplitudes,
    request_low_energy_predictions,
    request_metrics,
    request_physical_yukawas,
    request_vacuum,
)
from onetheory.verification.certificates import certify_established_carrier
from onetheory.verification.evidence import EvidenceClass


def test_reality_composes_only_established_carrier_objects() -> None:
    state = assemble_reality()

    assert state.established
    assert state.model_name == "published one-Higgs heterotic Schoen carrier"
    assert state.names == (
        "standard_model",
        "geometry",
        "visible_bundle",
        "tree_level_flavor",
        "topological_consistency",
    )
    assert "hidden bundle" in state.unresolved
    assert "physical Yukawa matrices" in state.unresolved


def test_external_certificates_pass_for_the_assembled_state() -> None:
    certificates = certify_established_carrier(assemble_reality())

    assert len(certificates) == 6
    assert all(certificate.passed for certificate in certificates)
    assert any(
        certificate.evidence.evidence_class is EvidenceClass.PUBLISHED_INPUT
        for certificate in certificates
    )
    assert all(len(certificate.digest) == 64 for certificate in certificates)


@pytest.mark.parametrize(
    "request_fn",
    (
        request_metrics,
        request_physical_yukawas,
        request_instanton_amplitudes,
        request_hidden_bundle,
        request_vacuum,
        request_low_energy_predictions,
    ),
)
def test_unresolved_reality_outputs_fail_closed(request_fn: object) -> None:
    with pytest.raises(MissingPhysicalInput):
        request_fn()  # type: ignore[operator]
