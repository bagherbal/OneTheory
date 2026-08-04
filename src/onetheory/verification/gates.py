"""Scientific gate states and fail-closed decision vocabulary.

Owns:
    Explicit accepted, failed, unresolved, missing-input, and killed conditions with
    declared scope and consequences for downstream computation.

Depends on:
    Evidence and certificate records and any production object being inspected; it is
    not a dependency of production physics.

Must not:
    Infer a bridge, suppress an unresolved prerequisite, or change a scientific result
    merely to satisfy an execution path.

Phase 0:
    Exact gate records are implemented; they inspect production calculations but
    do not supply unresolved physical inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class _SourceResult(Protocol):
    name: str
    status: str


class GateState(StrEnum):
    """Fail-closed status values for scoped scientific gates."""

    PASS = "PASS"
    FAIL = "FAIL"
    UNRESOLVED = "UNRESOLVED"
    MISSING_INPUT = "MISSING_INPUT"
    KILLED = "KILLED"


@dataclass(frozen=True, slots=True)
class GateResult:
    """An immutable gate result with an explicit scientific scope."""

    name: str
    state: GateState
    statement: str
    scope: str
    prerequisites: tuple[str, ...]

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.name, self.statement, self.scope)):
            raise ValueError("gate results require a name, statement, and scope")
        if any(not prerequisite.strip() for prerequisite in self.prerequisites):
            raise ValueError("gate prerequisites require nonempty names")

    @property
    def passed(self) -> bool:
        """Return whether the gate passed at its declared scope."""

        return self.state is GateState.PASS


def gate_passed(
    name: str,
    statement: str,
    scope: str,
    prerequisites: tuple[str, ...] = (),
) -> GateResult:
    """Construct a passed gate only for a caller-supplied exact result."""

    return GateResult(name, GateState.PASS, statement, scope, prerequisites)


def gate_unresolved(
    name: str,
    statement: str,
    scope: str,
    prerequisites: tuple[str, ...],
) -> GateResult:
    """Construct an unresolved gate without a fallback conclusion."""

    return GateResult(name, GateState.UNRESOLVED, statement, scope, prerequisites)


def gate_missing_input(
    name: str,
    statement: str,
    scope: str,
    prerequisites: tuple[str, ...],
) -> GateResult:
    """Construct a missing-input gate with its exact prerequisite chain."""

    return GateResult(name, GateState.MISSING_INPUT, statement, scope, prerequisites)


def parameterized_law_gate(
    name: str,
    exact_law_structure: bool,
    unresolved_parameters: tuple[str, ...],
    scope: str,
) -> GateResult:
    """Pass structural laws or expose their unresolved physical parameters."""

    if not exact_law_structure:
        return GateResult(name, GateState.FAIL, "exact law structure failed", scope, ())
    return gate_missing_input(
        name,
        "Law structure is established; physical parameter values remain unresolved.",
        scope,
        unresolved_parameters,
    )


def source_classification_gate(results: tuple[_SourceResult, ...]) -> GateResult:
    """Inspect scoped source results without widening any retained hypothesis."""

    if not results:
        return gate_missing_input(
            "source.classification",
            "No source classification was supplied.",
            "nonperturbative source architecture",
            ("explicit source charges",),
        )
    unresolved = tuple(result.name for result in results if result.status == "UNRESOLVED")
    if unresolved:
        return gate_unresolved(
            "source.classification",
            "At least one scoped source result remains unresolved.",
            "declared source-classification scopes",
            unresolved,
        )
    return gate_passed(
        "source.classification",
        "All supplied source scopes have explicit conclusions.",
        "declared source-classification scopes",
    )


def vacuum_control_gate(status: object, prerequisites: tuple[str, ...]) -> GateResult:
    """Convert a control-ledger status into a fail-closed scientific gate."""

    value = getattr(status, "value", status)
    if value == "CONTROLLED":
        return gate_passed(
            "vacuum.control",
            "All declared control criteria pass.",
            "vacuum approximation hierarchy",
        )
    if value == "NUMERICAL_FAILURE":
        return GateResult(
            "vacuum.control",
            GateState.FAIL,
            "Numerical control certification failed.",
            "vacuum approximation hierarchy",
            prerequisites,
        )
    if value == "UNCONTROLLED":
        return GateResult(
            "vacuum.control",
            GateState.FAIL,
            "The candidate is not parametrically controlled.",
            "vacuum approximation hierarchy",
            prerequisites,
        )
    if value == "CONDITIONAL":
        return gate_unresolved(
            "vacuum.control",
            "Control depends on explicit conditional assumptions.",
            "vacuum approximation hierarchy",
            prerequisites,
        )
    return gate_missing_input(
        "vacuum.control",
        "Control criteria are missing physical inputs.",
        "vacuum approximation hierarchy",
        prerequisites,
    )
