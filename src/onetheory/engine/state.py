"""Immutable physical state containers shared by execution and simulation.

Owns:
    Named state entries, established-state status, explicit unresolved-output
    declarations, deterministic lookup, and fail-closed output requirements.

Depends on:
    `onetheory.core.errors` only; state remains generic and imports no concrete
    model, engine solver, reality, verification, research, or observation data.

Must not:
    Supply default values, claim unresolved physics is complete, store a second
    simplified simulation universe, or hide basis and normalization metadata.

Phase 0:
    Immutable state storage and unresolved-output behavior are implemented; lawful
    state evolution remains outside this exact reality slice.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from onetheory.core.errors import MissingPhysicalInput


@dataclass(frozen=True, slots=True)
class StateEntry:
    """One immutable named value in a physical state."""

    name: str
    value: object

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("state entries require nonempty names")


@dataclass(frozen=True, slots=True, init=False)
class PhysicalState:
    """An immutable established state with explicit unresolved outputs."""

    model_name: str
    entries: tuple[StateEntry, ...]
    unresolved: tuple[str, ...]
    established: bool

    def __init__(
        self,
        model_name: str,
        entries: Iterable[StateEntry],
        unresolved: Iterable[str],
        established: bool,
    ) -> None:
        values = tuple(entries)
        open_outputs = tuple(unresolved)
        if not model_name.strip():
            raise ValueError("physical states require a model name")
        if len({entry.name for entry in values}) != len(values):
            raise ValueError("state entry names must be unique")
        if any(not output.strip() for output in open_outputs):
            raise ValueError("unresolved outputs require nonempty names")
        object.__setattr__(self, "model_name", model_name)
        object.__setattr__(self, "entries", values)
        object.__setattr__(self, "unresolved", open_outputs)
        object.__setattr__(self, "established", established)

    @property
    def names(self) -> tuple[str, ...]:
        """Return deterministic state-entry names."""

        return tuple(entry.name for entry in self.entries)

    def value(self, name: str) -> object:
        """Return one established value or raise a missing-input error."""

        for entry in self.entries:
            if entry.name == name:
                return entry.value
        raise MissingPhysicalInput(name, self.unresolved)

    def require(self, output: str) -> object:
        """Require an output that may be explicitly unresolved."""

        if output in self.unresolved:
            raise MissingPhysicalInput(output, self.unresolved)
        return self.value(output)
