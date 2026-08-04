"""Exact chiral matter, scalar multiplets, and interaction records.

Owns:
    Chirality labels, repeated generations, Weyl fields, Dirac and Majorana
    eligibility, scalar multiplets, symbolic Yukawa maps, Lorentz contractions,
    gauge-singlet interaction checks, and exact spectra.

Depends on:
    Gauge representations, exact rational dimensions, and no concrete model or
    observation data.

Must not:
    Insert measured masses, mixing angles, fitted couplings, synthetic particles,
    normalized Yukawa values, or ultraviolet geometry selectors.

Phase 0:
    The structural matter-law layer is implemented; all coupling entries remain
    symbolic unresolved parameters.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from onetheory.core.errors import InconsistentDimensions
from onetheory.math.numbers import Rational, coerce_rational
from onetheory.physics.gauge import Representation, gauge_singlet


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


@dataclass(frozen=True, slots=True)
class WeylField:
    """One left- or right-handed Weyl field with explicit generation number."""

    name: str
    representation: Representation
    chirality: Chirality
    generation: int
    mass_dimension: Rational
    lorentz_invariant: bool

    def __init__(
        self,
        name: str,
        representation: Representation,
        chirality: Chirality,
        generation: int,
    ) -> None:
        if chirality not in (Chirality.LEFT, Chirality.RIGHT):
            raise ValueError("Weyl fields require left or right chirality")
        if (
            not name.strip()
            or isinstance(generation, bool)
            or not isinstance(generation, int)
            or generation < 1
        ):
            raise ValueError("Weyl fields require a name and positive generation")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "representation", representation)
        object.__setattr__(self, "chirality", chirality)
        object.__setattr__(self, "generation", generation)
        object.__setattr__(self, "mass_dimension", Rational(3, 2))

    def conjugate(self) -> WeylField:
        """Return the conjugate Weyl field with opposite chirality."""

        chirality = Chirality.RIGHT if self.chirality is Chirality.LEFT else Chirality.LEFT
        return WeylField(
            f"{self.name}†",
            self.representation.conjugate_representation(),
            chirality,
            self.generation,
        )


@dataclass(frozen=True, slots=True)
class ScalarMultiplet:
    """A bosonic scalar multiplet with exact representation metadata."""

    name: str
    representation: Representation
    mass_dimension: Rational

    def __init__(self, name: str, representation: Representation) -> None:
        if not name.strip():
            raise ValueError("scalar multiplets require a name")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "representation", representation)
        object.__setattr__(self, "mass_dimension", Rational(1))


@dataclass(frozen=True, slots=True)
class DiracPairing:
    """A Lorentz scalar pairing of opposite-chirality Weyl fields."""

    left: WeylField
    right: WeylField
    gauge_invariant: bool
    mass_dimension: Rational

    def __init__(self, left: WeylField, right: WeylField) -> None:
        if left.chirality is right.chirality:
            raise ValueError("Dirac pairings require opposite chiralities")
        object.__setattr__(self, "left", left)
        object.__setattr__(self, "right", right)
        object.__setattr__(
            self, "gauge_invariant", gauge_singlet((left.representation, right.representation))
        )
        object.__setattr__(self, "mass_dimension", left.mass_dimension + right.mass_dimension)


@dataclass(frozen=True, slots=True)
class MajoranaEligibility:
    """An explicit test of whether a Weyl representation can pair with itself."""

    field: WeylField
    eligible: bool
    reason: str

    @classmethod
    def evaluate(cls, field: WeylField) -> MajoranaEligibility:
        charges_zero = all(charge.value == 0 for charge in field.representation.charges)
        real_label = not field.representation.conjugate
        eligible = charges_zero and real_label
        reason = (
            "representation is self-conjugate"
            if eligible
            else "representation is not self-conjugate"
        )
        return cls(field, eligible, reason)


@dataclass(frozen=True, slots=True)
class MajoranaMassOperator:
    """An optional symbolic Majorana operator with explicit B-L status."""

    field: ParticleMultiplet
    coefficient: SymbolicLinearMap
    gauged_b_minus_l: bool
    allowed: bool
    reason: str
    mass_dimension: Rational

    def __init__(
        self,
        field: ParticleMultiplet,
        coefficient: SymbolicLinearMap,
        gauged_b_minus_l: bool,
    ) -> None:
        if field.chirality is Chirality.SCALAR:
            raise ValueError("Majorana operators require a chiral matter multiplet")
        hypercharge_zero = field.representation.charge("Y") == 0
        b_minus_l_zero = field.representation.charge("B-L") == 0
        allowed = hypercharge_zero and (not gauged_b_minus_l or b_minus_l_zero)
        reason = (
            "operator is gauge singlet"
            if allowed
            else "B-L charge requires the extension to be ungauged or explicitly broken"
        )
        object.__setattr__(self, "field", field)
        object.__setattr__(self, "coefficient", coefficient)
        object.__setattr__(self, "gauged_b_minus_l", gauged_b_minus_l)
        object.__setattr__(self, "allowed", allowed)
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "mass_dimension", Rational(4))


@dataclass(frozen=True, slots=True)
class SymbolicLinearMap:
    """A symbolic generation-space linear map without guessed entries."""

    name: str
    rows: int
    columns: int
    provenance: str
    mass_dimension: Rational

    def __init__(
        self,
        name: str,
        rows: int,
        columns: int,
        provenance: str,
        mass_dimension: object = 0,
    ) -> None:
        if not name.strip() or not provenance.strip() or rows < 1 or columns < 1:
            raise ValueError("symbolic maps require positive dimensions and provenance")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "rows", rows)
        object.__setattr__(self, "columns", columns)
        object.__setattr__(self, "provenance", provenance)
        object.__setattr__(self, "mass_dimension", coerce_rational(mass_dimension))


@dataclass(frozen=True, slots=True)
class YukawaTensor:
    """A symbolic Yukawa map with exact Lorentz and gauge admissibility."""

    name: str
    left: ParticleMultiplet
    right: ParticleMultiplet
    scalar: ScalarMultiplet
    coefficient: SymbolicLinearMap
    gauge_invariant: bool
    lorentz_scalar: bool
    lorentz_invariant: bool
    mass_dimension: Rational

    def __init__(
        self,
        name: str,
        left: ParticleMultiplet,
        right: ParticleMultiplet,
        scalar: ScalarMultiplet,
        coefficient: SymbolicLinearMap,
    ) -> None:
        if coefficient.rows != left.multiplicity or coefficient.columns != right.multiplicity:
            raise ValueError("Yukawa map dimensions must match explicit generation counts")
        gauge_ok = gauge_singlet((left.representation, right.representation, scalar.representation))
        lorentz_ok = left.chirality is Chirality.LEFT and right.chirality is Chirality.LEFT
        if not gauge_ok:
            raise ValueError("Yukawa factors are not a declared gauge singlet")
        if not lorentz_ok:
            raise ValueError("Yukawa tensors require two left-handed Weyl multiplets")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "left", left)
        object.__setattr__(self, "right", right)
        object.__setattr__(self, "scalar", scalar)
        object.__setattr__(self, "coefficient", coefficient)
        object.__setattr__(self, "gauge_invariant", gauge_ok)
        object.__setattr__(self, "lorentz_scalar", lorentz_ok)
        object.__setattr__(self, "lorentz_invariant", lorentz_ok)
        object.__setattr__(self, "mass_dimension", Rational(4))


@dataclass(frozen=True, slots=True)
class InteractionTerm:
    """A fully checked local matter interaction record."""

    name: str
    representations: tuple[Representation, ...]
    fermion_count: int
    gauge_invariant: bool
    lorentz_scalar: bool
    lorentz_invariant: bool
    mass_dimension: Rational
    coefficient: SymbolicLinearMap | None
    provenance: str

    def __init__(
        self,
        name: str,
        factors: Iterable[WeylField | ScalarMultiplet],
        coefficient: SymbolicLinearMap | None,
        provenance: str,
    ) -> None:
        values = tuple(factors)
        if not values or not name.strip() or not provenance.strip():
            raise ValueError("interaction terms require factors, names, and provenance")
        representations = tuple(value.representation for value in values)
        fermions = sum(isinstance(value, WeylField) for value in values)
        if fermions % 2:
            raise ValueError("Lorentz scalar fermion products require an even count")
        dimensions = sum((value.mass_dimension for value in values), Rational(0))
        if coefficient is not None:
            dimensions += coefficient.mass_dimension
        if dimensions != 4:
            raise InconsistentDimensions(
                "renormalizable matter interactions must have mass dimension four"
            )
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "representations", representations)
        object.__setattr__(self, "fermion_count", fermions)
        object.__setattr__(self, "gauge_invariant", gauge_singlet(representations))
        object.__setattr__(self, "lorentz_scalar", True)
        object.__setattr__(self, "lorentz_invariant", True)
        object.__setattr__(self, "mass_dimension", dimensions)
        object.__setattr__(self, "coefficient", coefficient)
        object.__setattr__(self, "provenance", provenance)


def generation_fields(multiplet: ParticleMultiplet) -> tuple[WeylField, ...]:
    """Expand explicit multiplicity metadata into named generation fields."""

    if multiplet.chirality is Chirality.SCALAR:
        raise ValueError("scalar multiplets do not expand into Weyl fields")
    return tuple(
        WeylField(
            f"{multiplet.name}_{generation}",
            multiplet.representation,
            multiplet.chirality,
            generation,
        )
        for generation in range(1, multiplet.multiplicity + 1)
    )


__all__ = [
    "Chirality",
    "DiracPairing",
    "InteractionTerm",
    "MajoranaEligibility",
    "MajoranaMassOperator",
    "ParticleMultiplet",
    "ScalarMultiplet",
    "Spectrum",
    "SymbolicLinearMap",
    "WeylField",
    "YukawaTensor",
    "generation_fields",
]
