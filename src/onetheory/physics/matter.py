"""Immutable particle multiplets and exact spectra.

Owns:
    Chirality labels, particle multiplets, multiplicity metadata, spectrum
    validation, and exact lookup operations independent of a chosen carrier.

Depends on:
    `onetheory.physics.gauge` for representation metadata and the standard
    library for immutable records; it does not import models or observations.

Must not:
    Insert measured masses, mixing angles, fitted couplings, synthetic particles,
    normalized Yukawa values, or ultraviolet geometry selectors.

Phase 0:
    Minimal exact matter metadata is implemented; dynamical fields and physical
    observables remain separate concerns.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from onetheory.physics.gauge import Representation


class Chirality(StrEnum):
    """Chirality metadata for a left-handed Weyl description."""

    LEFT = "left"
    RIGHT = "right"
    SCALAR = "scalar"


@dataclass(frozen=True, slots=True, init=False)
class ParticleMultiplet:
    """A named multiplet with representation and exact multiplicity metadata."""

    name: str
    representation: Representation
    chirality: Chirality
    multiplicity: int
    sector: str

    def __init__(
        self,
        name: str,
        representation: Representation,
        chirality: Chirality,
        multiplicity: int,
        sector: str,
    ) -> None:
        if not name.strip() or not sector.strip():
            raise ValueError("particle multiplets require names and sectors")
        if isinstance(multiplicity, bool) or not isinstance(multiplicity, int) or multiplicity < 1:
            raise ValueError("multiplicity must be a positive integer")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "representation", representation)
        object.__setattr__(self, "chirality", chirality)
        object.__setattr__(self, "multiplicity", multiplicity)
        object.__setattr__(self, "sector", sector)


@dataclass(frozen=True, slots=True, init=False)
class Spectrum:
    """A deterministic collection of distinct particle multiplets."""

    multiplets: tuple[ParticleMultiplet, ...]

    def __init__(self, multiplets: Iterable[ParticleMultiplet]) -> None:
        values = tuple(multiplets)
        if len({multiplet.name for multiplet in values}) != len(values):
            raise ValueError("spectrum multiplet names must be unique")
        object.__setattr__(self, "multiplets", values)

    def by_name(self, name: str) -> ParticleMultiplet:
        """Return a named multiplet or fail explicitly."""

        for multiplet in self.multiplets:
            if multiplet.name == name:
                return multiplet
        raise KeyError(name)

    @property
    def total_multiplicity(self) -> int:
        """Return the sum of declared multiplet multiplicities."""

        return sum(multiplet.multiplicity for multiplet in self.multiplets)

    def sector(self, name: str) -> tuple[ParticleMultiplet, ...]:
        """Return all multiplets in one declared sector."""

        return tuple(multiplet for multiplet in self.multiplets if multiplet.sector == name)
