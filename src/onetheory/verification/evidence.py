"""External provenance and evidence records for production results.

Owns:
    Immutable evidence classes, source provenance, claim scope, and records that
    distinguish published inputs, exact project identities, open obligations, and
    missing physical inputs.

Depends on:
    Python standard-library enums and immutable records; verification may inspect
    production but production must not import this module.

Must not:
    Create physical objects, fill missing inputs, let observations select upstream
    structure, or turn an exact internal identity into a published claim.

Phase 0:
    Evidence and provenance records are implemented; scientific certification is
    still external to the production dependency graph.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EvidenceClass(StrEnum):
    """Evidence-status vocabulary used by external certificates."""

    PUBLISHED_INPUT = "published_input"
    EXACT_THEOREM = "exact_theorem"
    CONTROLLED_NUMERICAL = "controlled_numerical"
    CONDITIONAL = "conditional"
    OPEN = "open"
    MISSING_INPUT = "missing_input"
    KILLED = "killed"


@dataclass(frozen=True, slots=True)
class Provenance:
    """Traceability record for one claim or calculation artifact."""

    identifier: str
    citation: str
    locator: str
    artifact_digest: str

    def __post_init__(self) -> None:
        if any(not value.strip() for value in
               (self.identifier, self.citation, self.locator, self.artifact_digest)):
            raise ValueError("provenance records require complete traceability")


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """A scoped claim classification with immutable provenance."""

    claim: str
    evidence_class: EvidenceClass
    statement: str
    provenance: tuple[Provenance, ...]
    scope: str

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.claim, self.statement, self.scope)):
            raise ValueError("evidence records require claim, statement, and scope")


PUBLISHED_CARRIER = Provenance(
    "schoen_quotient_2004",
    "Braun, Ovrut, Pantev, and Reinbacher, Elliptic Calabi-Yau Threefolds "
    "with Z3 x Z3 Wilson Lines",
    "https://arxiv.org/abs/hep-th/0410055",
    "published-input",
)
EXACT_PROJECT = Provenance(
    "onetheory_exact_carrier_slice",
    "OneTheory exact carrier calculations",
    "production source and deterministic tests",
    "runtime-certificate",
)
