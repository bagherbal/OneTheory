"""Deterministic certificates inspected outside production physics.

Owns:
    Exact equality certificates, deterministic value digests, and certificate
    collections for the established Schoen carrier state.

Depends on:
    `onetheory.verification.evidence`, immutable production state, and established
    carrier objects solely as inspection targets. Production never imports this
    module.

Must not:
    Supply a missing result, certify guessed coefficients, or make a required
    hidden class into an existing hidden bundle.

Phase 0:
    Exact certificate construction is implemented for the vertical slice; no
    numerical convergence certificate is claimed.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import cast

from onetheory.engine.state import PhysicalState
from onetheory.models.heterotic_schoen.consistency import TopologicalConsistency
from onetheory.models.heterotic_schoen.flavor import TreeLevelFlavorResult
from onetheory.models.heterotic_schoen.geometry import SchoenGeometry
from onetheory.models.heterotic_schoen.visible import ObservableBundle
from onetheory.verification.evidence import (
    EXACT_PROJECT,
    PUBLISHED_CARRIER,
    EvidenceClass,
    EvidenceRecord,
    Provenance,
)


@dataclass(frozen=True, slots=True)
class ExactCertificate:
    """A deterministic equality certificate with a traceable evidence record."""

    identifier: str
    expected: object
    observed: object
    passed: bool
    evidence: EvidenceRecord
    digest: str


def exact_certificate(
    identifier: str,
    expected: object,
    observed: object,
    *,
    evidence_class: EvidenceClass = EvidenceClass.EXACT_THEOREM,
    statement: str,
    provenance: tuple[Provenance, ...] = (EXACT_PROJECT,),
    scope: str = "established carrier vertical slice",
) -> ExactCertificate:
    """Create a deterministic exact equality certificate."""

    passed = observed == expected
    payload = f"{identifier}|{expected!r}|{observed!r}|{passed!r}".encode()
    digest = sha256(payload).hexdigest()
    record = EvidenceRecord(identifier, evidence_class, statement, provenance, scope)
    return ExactCertificate(identifier, expected, observed, passed, record, digest)


def certify_established_carrier(state: PhysicalState) -> tuple[ExactCertificate, ...]:
    """Certify the established geometry, visible spectrum, flavor, and topology."""

    geometry = cast(SchoenGeometry, state.value("geometry"))
    visible = cast(ObservableBundle, state.value("visible_bundle"))
    flavor = cast(TreeLevelFlavorResult, state.value("tree_level_flavor"))
    topology = cast(TopologicalConsistency, state.value("topological_consistency"))
    certificates = (
        exact_certificate(
            "carrier.quotient.order", 9, geometry.quotient.order,
            statement="The established carrier uses a free order-nine quotient.",
            provenance=(PUBLISHED_CARRIER, EXACT_PROJECT),
        ),
        exact_certificate(
            "carrier.spectrum.families", 3, visible.spectrum.families,
            evidence_class=EvidenceClass.PUBLISHED_INPUT,
            statement="Wilson-line projection leaves three observable families.",
            provenance=(PUBLISHED_CARRIER,),
        ),
        exact_certificate(
            "carrier.spectrum.higgs_pairs", 1, visible.spectrum.higgs_pairs,
            evidence_class=EvidenceClass.PUBLISHED_INPUT,
            statement="The selected visible carrier has one Higgs pair.",
            provenance=(PUBLISHED_CARRIER,),
        ),
        exact_certificate(
            "carrier.flavor.det_zero", True, flavor.up.determinant.is_zero(),
            statement="The holomorphic tree-level determinant vanishes identically.",
        ),
        exact_certificate(
            "carrier.topology.bianchi", True, topology.bianchi_identity,
            statement="Visible plus required hidden Chern data match the tangent target.",
        ),
        exact_certificate(
            "carrier.topology.cover_slope", -297, topology.cover_slope,
            statement="The visible constituent slope uses the ninefold cover normalization.",
        ),
    )
    return certificates
