"""Carrier-specific stabilization and vacuum construction.

Owns:
    The Schoen carrier’s superpotential, threshold functions, moduli stabilization,
    controlled vacuum conditions, and stability evidence once upstream data exist.

Depends on:
    Core precision and units, reusable mathematics, general vacuum, gravity, string,
    gauge, and matter physics, and established Schoen sectors and consistency data.

Must not:
    Insert racetrack coefficients, select a vacuum from observations, hide omitted
    corrections, or report conditional stabilization as an existing vacuum.

Phase 0:
    The carrier boundary and source scopes are implemented; carrier-specific vacuum
    coefficients, equations, and control evidence remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NoReturn

from onetheory.core.errors import MissingPhysicalInput
from onetheory.physics.vacuum import (
    PhysicalInputRequirement,
    ScopedSourceResult,
    scoped_source_classifications,
)

SCHOEN_VACUUM_MISSING_CHAIN = (
    "complete Kähler potential",
    "visible and hidden gauge kinetic functions",
    "stable hidden bundle and hidden spectrum",
    "hidden beta-function coefficients",
    "allowed condensates",
    "physical instanton determinant sections",
    "threshold corrections",
    "anomaly and flux consistency",
    "complete D-term data",
    "solved F/D equations",
    "canonically normalized Hessian",
    "controlled correction hierarchy",
)


@dataclass(frozen=True, slots=True)
class VacuumInputRequirements:
    """The complete fail-closed input ledger for a Schoen vacuum."""

    requirements: tuple[PhysicalInputRequirement, ...]
    provenance: str

    def __post_init__(self) -> None:
        if not self.requirements or not self.provenance.strip():
            raise ValueError("vacuum input requirements need named entries and provenance")
        if len({item.name for item in self.requirements}) != len(self.requirements):
            raise ValueError("vacuum input requirements must be unique")

    @property
    def complete(self) -> bool:
        """Return whether every carrier input is explicitly available."""

        return all(item.available for item in self.requirements)

    @property
    def earliest_missing(self) -> str | None:
        """Return the first unresolved input in the declared dependency order."""

        return next((item.name for item in self.requirements if not item.available), None)

    @property
    def missing_chain(self) -> tuple[str, ...]:
        """Return the unresolved suffix beginning at the first missing input."""

        missing = self.earliest_missing
        if missing is None:
            return ()
        index = tuple(item.name for item in self.requirements).index(missing)
        return tuple(item.name for item in self.requirements[index:])


def schoen_vacuum_input_requirements() -> VacuumInputRequirements:
    """Return carrier requirements with no fabricated availability defaults."""

    return VacuumInputRequirements(
        tuple(PhysicalInputRequirement(name) for name in SCHOEN_VACUUM_MISSING_CHAIN),
        "published carrier boundary and nonperturbative vacuum objective",
    )


@dataclass(frozen=True, slots=True)
class SchoenVacuumBoundary:
    """The source-classification boundary before carrier-specific vacuum data exist."""

    requirements: VacuumInputRequirements
    source_classifications: tuple[ScopedSourceResult, ...]
    conditional_racetrack: str
    provenance: str

    @property
    def complete(self) -> bool:
        """Return whether a controlled carrier vacuum may be reported."""

        return self.requirements.complete

    @property
    def earliest_missing(self) -> str | None:
        """Return the earliest missing physical carrier input."""

        return self.requirements.earliest_missing


def schoen_vacuum_boundary() -> SchoenVacuumBoundary:
    """Expose exact source scopes while keeping the carrier vacuum unavailable."""

    return SchoenVacuumBoundary(
        schoen_vacuum_input_requirements(),
        scoped_source_classifications(),
        "same hidden gauge kinetic function with carrier-derived positive unequal exponents",
        "published one-Higgs heterotic Schoen carrier boundary",
    )


def request_schoen_vacuum() -> NoReturn:
    """Reject carrier-vacuum requests at the earliest unresolved prerequisite."""

    boundary = schoen_vacuum_boundary()
    chain = boundary.requirements.missing_chain
    raise MissingPhysicalInput(chain[0], chain[1:])


__all__ = [
    "SCHOEN_VACUUM_MISSING_CHAIN",
    "SchoenVacuumBoundary",
    "VacuumInputRequirements",
    "request_schoen_vacuum",
    "schoen_vacuum_boundary",
    "schoen_vacuum_input_requirements",
]
