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
