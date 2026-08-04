"""Exact SI and natural-unit dimensional language.

Owns:
    Immutable SI dimension vectors, natural mass dimensions, explicit unit systems,
    exact quantities, conversions, and symbolic records for c, hbar, and G.

Depends on:
    Python's exact `Fraction`, dataclass, and enum primitives only; this lowest
    physical policy module does not import other OneTheory layers.

Must not:
    Embed measured numerical constants as defaults, choose a normalization silently,
    import observations, or encode a model-specific physical law.

Phase 0:
    Exact dimensional machinery is implemented; numerical constants remain explicit
    symbolic inputs with provenance.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from typing import Final

from onetheory.core.errors import IncompatibleConvention, InconsistentDimensions

DimensionExponent = Fraction
SI_BASE_COUNT: Final = 7


def _fraction(value: object) -> Fraction:
    if isinstance(value, bool):
        raise TypeError("dimension exponents cannot be boolean")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    raise TypeError("dimension exponents require exact integers or Fractions")


@dataclass(frozen=True, slots=True)
class DimensionVector:
    """An exact SI vector together with a natural-unit mass dimension."""

    si: tuple[Fraction, ...]
    mass_dimension: Fraction = Fraction(0)

    def __init__(self, si: tuple[object, ...] = (), mass_dimension: object = 0) -> None:
        values = tuple(_fraction(value) for value in si)
        if values and len(values) != SI_BASE_COUNT:
            raise ValueError("SI dimensions require seven base exponents")
        object.__setattr__(self, "si", values or (Fraction(0),) * SI_BASE_COUNT)
        object.__setattr__(self, "mass_dimension", _fraction(mass_dimension))

    def __add__(self, other: DimensionVector) -> DimensionVector:
        return DimensionVector(
            tuple(left + right for left, right in zip(self.si, other.si, strict=True)),
            self.mass_dimension + other.mass_dimension,
        )

    def __sub__(self, other: DimensionVector) -> DimensionVector:
        return DimensionVector(
            tuple(left - right for left, right in zip(self.si, other.si, strict=True)),
            self.mass_dimension - other.mass_dimension,
        )

    def scale(self, factor: object) -> DimensionVector:
        scalar = _fraction(factor)
        return DimensionVector(
            tuple(value * scalar for value in self.si),
            self.mass_dimension * scalar,
        )

    @property
    def is_dimensionless(self) -> bool:
        return all(value == 0 for value in self.si) and self.mass_dimension == 0


DIMENSIONLESS = DimensionVector()
LENGTH = DimensionVector((1, 0, 0, 0, 0, 0, 0))
MASS = DimensionVector((0, 1, 0, 0, 0, 0, 0), 1)
TIME = DimensionVector((0, 0, 1, 0, 0, 0, 0))


class UnitSystem(StrEnum):
    """Explicit systems whose conversion rules may not be mixed implicitly."""

    SI = "SI"
    NATURAL = "natural"


@dataclass(frozen=True, slots=True)
class Unit:
    """One named exact unit relative to its declared system base."""

    name: str
    dimension: DimensionVector
    scale: Fraction
    system: UnitSystem

    def __init__(
        self,
        name: str,
        dimension: DimensionVector,
        scale: object = 1,
        system: UnitSystem = UnitSystem.SI,
    ) -> None:
        if not name.strip():
            raise ValueError("units require a nonempty name")
        normalized = _fraction(scale)
        if normalized <= 0:
            raise ValueError("unit scales must be positive")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "dimension", dimension)
        object.__setattr__(self, "scale", normalized)
        object.__setattr__(self, "system", system)


@dataclass(frozen=True, slots=True)
class UnitConversion:
    """An explicit exact conversion between two declared unit systems."""

    source: UnitSystem
    target: UnitSystem
    factor: Fraction
    provenance: str

    def __init__(
        self, source: UnitSystem, target: UnitSystem, factor: object, provenance: str
    ) -> None:
        normalized = _fraction(factor)
        if source is target or normalized <= 0 or not provenance.strip():
            raise ValueError(
                "unit conversions require distinct systems, positive factor, and provenance"
            )
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "factor", normalized)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class Quantity:
    """An exact rational quantity with an explicit unit and conversion path."""

    value: Fraction
    unit: Unit

    def __init__(self, value: object, unit: Unit) -> None:
        object.__setattr__(self, "value", _fraction(value))
        object.__setattr__(self, "unit", unit)

    @property
    def dimension(self) -> DimensionVector:
        return self.unit.dimension

    def convert_to(self, target: Unit, conversion: UnitConversion | None = None) -> Quantity:
        if self.unit.dimension != target.dimension:
            raise InconsistentDimensions("quantity conversion requires equal dimensions")
        system_factor = Fraction(1)
        if self.unit.system is not target.system:
            if conversion is None or (
                conversion.source is not self.unit.system or conversion.target is not target.system
            ):
                raise IncompatibleConvention("unit systems require an explicit conversion record")
            system_factor = conversion.factor
        base_value = self.value * self.unit.scale
        return Quantity(base_value * system_factor / target.scale, target)

    def _check(self, other: Quantity) -> None:
        if self.unit.dimension != other.unit.dimension:
            raise InconsistentDimensions("quantities have incompatible dimensions")
        if self.unit.system is not other.unit.system:
            raise IncompatibleConvention("quantities use different unit systems")

    def __add__(self, other: Quantity) -> Quantity:
        self._check(other)
        converted = other.convert_to(self.unit)
        return Quantity(self.value + converted.value, self.unit)

    def __sub__(self, other: Quantity) -> Quantity:
        self._check(other)
        converted = other.convert_to(self.unit)
        return Quantity(self.value - converted.value, self.unit)

    def scale_by(self, factor: object) -> Quantity:
        return Quantity(self.value * _fraction(factor), self.unit)

    def multiply(self, other: Quantity, unit: Unit) -> Quantity:
        if self.unit.system is not other.unit.system or self.unit.system is not unit.system:
            raise IncompatibleConvention("quantity multiplication requires one unit system")
        if self.dimension + other.dimension != unit.dimension:
            raise InconsistentDimensions("product unit has the wrong dimension")
        return Quantity(
            self.value * other.value * self.unit.scale * other.unit.scale / unit.scale, unit
        )


@dataclass(frozen=True, slots=True)
class SymbolicConstant:
    """A named dimensional constant whose numerical value is an explicit input."""

    name: str
    dimension: DimensionVector
    provenance: str

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.name, self.provenance)):
            raise ValueError("symbolic constants require name and provenance")


@dataclass(frozen=True, slots=True)
class FundamentalConstants:
    """Symbolic c, hbar, and G records with no numerical defaults."""

    speed_of_light: SymbolicConstant
    reduced_planck: SymbolicConstant
    newton: SymbolicConstant

    @classmethod
    def symbolic(cls, provenance: str) -> FundamentalConstants:
        if not provenance.strip():
            raise ValueError("fundamental constants require provenance")
        return cls(
            SymbolicConstant("c", LENGTH - TIME, provenance),
            SymbolicConstant("hbar", MASS + LENGTH + LENGTH - TIME, provenance),
            SymbolicConstant(
                "G",
                LENGTH.scale(3) - MASS - TIME.scale(2),
                provenance,
            ),
        )


__all__ = [
    "DIMENSIONLESS",
    "DimensionVector",
    "FundamentalConstants",
    "LENGTH",
    "MASS",
    "Quantity",
    "SymbolicConstant",
    "TIME",
    "Unit",
    "UnitConversion",
    "UnitSystem",
]
