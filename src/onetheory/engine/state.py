"""Immutable physical and numerical state containers.

Owns:
    Named physical state entries, unresolved-output declarations, numerical states,
    immutable trajectories, convergence records, and conservation diagnostics.

Depends on:
    `onetheory.core.errors` only; state remains generic and imports no concrete
    model, engine solver, reality, verification, research, or observation data.

Must not:
    Supply default values, claim unresolved physics is complete, store a second
    simplified simulation universe, or hide basis and normalization metadata.

    Phase 0:
    Immutable state storage and controlled numerical trajectory records are
    implemented; rendering remains external.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
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
    unresolved_chains: tuple[tuple[str, tuple[str, ...]], ...]
    established: bool

    def __init__(
        self,
        model_name: str,
        entries: Iterable[StateEntry],
        unresolved: Iterable[str],
        established: bool,
        unresolved_chains: Mapping[str, Iterable[str]] | None = None,
    ) -> None:
        values = tuple(entries)
        open_outputs = tuple(unresolved)
        if not model_name.strip():
            raise ValueError("physical states require a model name")
        if len({entry.name for entry in values}) != len(values):
            raise ValueError("state entry names must be unique")
        if any(not output.strip() for output in open_outputs):
            raise ValueError("unresolved outputs require nonempty names")
        chains = tuple((name, tuple(chain)) for name, chain in (unresolved_chains or {}).items())
        if any(name not in open_outputs for name, _ in chains):
            raise ValueError("unresolved prerequisite chains must name unresolved outputs")
        if any(any(not item.strip() for item in chain) for _, chain in chains):
            raise ValueError("unresolved prerequisite chains require nonempty names")
        object.__setattr__(self, "model_name", model_name)
        object.__setattr__(self, "entries", values)
        object.__setattr__(self, "unresolved", open_outputs)
        object.__setattr__(self, "unresolved_chains", tuple(sorted(chains)))
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
            chain = dict(self.unresolved_chains).get(output)
            if chain is not None:
                raise MissingPhysicalInput(output, chain)
            remaining = tuple(item for item in self.unresolved if item != output)
            raise MissingPhysicalInput(output, remaining)
        return self.value(output)


@dataclass(frozen=True, slots=True)
class SimulationState:
    """One immutable numerical state at an explicit time coordinate."""

    time: float
    values: tuple[float, ...]
    labels: tuple[str, ...]

    def __init__(self, time: float, values: Iterable[float], labels: Iterable[str]) -> None:
        coordinates = tuple(float(value) for value in values)
        names = tuple(labels)
        if len(coordinates) != len(names) or not names or any(not name.strip() for name in names):
            raise ValueError("simulation states require matching nonempty labels")
        object.__setattr__(self, "time", float(time))
        object.__setattr__(self, "values", coordinates)
        object.__setattr__(self, "labels", names)


@dataclass(frozen=True, slots=True)
class Trajectory:
    """An ordered immutable trajectory suitable for external animation consumers."""

    model_name: str
    states: tuple[SimulationState, ...]
    step_size: float

    def __init__(
        self, model_name: str, states: Iterable[SimulationState], step_size: float
    ) -> None:
        values = tuple(states)
        if not model_name.strip() or len(values) < 2 or step_size <= 0:
            raise ValueError(
                "trajectories require a name, at least two states, and a positive step"
            )
        if any(
            right.time <= left.time for left, right in zip(values[:-1], values[1:], strict=True)
        ):
            raise ValueError("trajectory times must increase strictly")
        object.__setattr__(self, "model_name", model_name)
        object.__setattr__(self, "states", values)
        object.__setattr__(self, "step_size", float(step_size))


@dataclass(frozen=True, slots=True)
class ConservationDiagnostic:
    """A deterministic drift check for a named conserved quantity."""

    name: str
    initial: float
    final: float
    absolute_drift: float
    tolerance: float
    passed: bool

    def __init__(self, name: str, initial: float, final: float, tolerance: float) -> None:
        if not name.strip() or tolerance < 0:
            raise ValueError("conservation diagnostics require a name and nonnegative tolerance")
        drift = abs(float(final) - float(initial))
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "initial", float(initial))
        object.__setattr__(self, "final", float(final))
        object.__setattr__(self, "absolute_drift", drift)
        object.__setattr__(self, "tolerance", float(tolerance))
        object.__setattr__(self, "passed", drift <= tolerance)


@dataclass(frozen=True, slots=True)
class ConvergenceRecord:
    """A refinement comparison that explicitly records convergence evidence."""

    step_sizes: tuple[float, ...]
    endpoint_errors: tuple[float, ...]
    tolerance: float
    converged: bool

    def __init__(
        self, step_sizes: Iterable[float], endpoint_errors: Iterable[float], tolerance: float
    ) -> None:
        sizes = tuple(float(value) for value in step_sizes)
        errors = tuple(float(value) for value in endpoint_errors)
        if not sizes or len(errors) != max(0, len(sizes) - 1) or any(value <= 0 for value in sizes):
            raise ValueError("convergence records require refinement step sizes and pair errors")
        if tolerance < 0:
            raise ValueError("convergence tolerance must be nonnegative")
        object.__setattr__(self, "step_sizes", sizes)
        object.__setattr__(self, "endpoint_errors", errors)
        object.__setattr__(self, "tolerance", float(tolerance))
        object.__setattr__(self, "converged", all(error <= tolerance for error in errors))


@dataclass(frozen=True, slots=True)
class SimulationResult:
    """A trajectory with convergence and conservation evidence."""

    trajectory: Trajectory
    convergence: ConvergenceRecord
    diagnostics: tuple[ConservationDiagnostic, ...]

    def __post_init__(self) -> None:
        if not self.convergence.converged:
            raise ValueError("simulation results require a converged refinement record")
