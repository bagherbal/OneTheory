"""Immutable gauge groups and exact representation metadata.

Owns:
    Gauge-group products, nonabelian representation labels, exact abelian charge
    metadata, and typed representations used by concrete particle spectra.

Depends on:
    `onetheory.core.errors` for explicit validation and `onetheory.math.numbers`
    for exact Rational charges; it is independent of concrete models.

Must not:
    Implement a general symbolic Lie-algebra system, choose a Wilson line, import
    the Schoen carrier, fit couplings, or bridge unrelated physical theories.

Phase 0:
    The minimal exact gauge vocabulary is implemented; gauge dynamics and carrier
    constructions remain in their owning layers.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from onetheory.math.numbers import Rational, coerce_rational


@dataclass(frozen=True, slots=True, init=False)
class GaugeGroup:
    """A named product of gauge factors with declared rank and dimensions."""

    name: str
    factors: tuple[str, ...]
    rank: int
    dimensions: tuple[int, ...]

    def __init__(
        self,
        name: str,
        rank: int,
        dimensions: Iterable[int],
        factors: Iterable[str] = (),
    ) -> None:
        factor_names = tuple(factors) or (name,)
        factor_dimensions = tuple(dimensions)
        if not name.strip() or not factor_names:
            raise ValueError("a gauge group requires a nonempty name and factors")
        if len(factor_names) != len(factor_dimensions):
            raise ValueError("gauge factors and dimensions must have equal length")
        if len(set(factor_names)) != len(factor_names):
            raise ValueError("gauge factor names must be unique")
        if isinstance(rank, bool) or not isinstance(rank, int) or rank < 0:
            raise ValueError("gauge-group rank must be a nonnegative integer")
        if any(isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 1
               for dimension in factor_dimensions):
            raise ValueError("gauge-factor dimensions must be positive integers")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "factors", factor_names)
        object.__setattr__(self, "rank", rank)
        object.__setattr__(self, "dimensions", factor_dimensions)

    @classmethod
    def simple(cls, name: str, rank: int, dimension: int) -> GaugeGroup:
        """Construct one simple or abelian factor."""

        return cls(name, rank, (dimension,))

    @classmethod
    def product(cls, *groups: GaugeGroup) -> GaugeGroup:
        """Construct a direct product while retaining factor metadata."""

        if not groups:
            raise ValueError("a gauge product requires at least one factor")
        return cls(
            " × ".join(group.name for group in groups),
            sum(group.rank for group in groups),
            tuple(dimension for group in groups for dimension in group.dimensions),
            tuple(factor for group in groups for factor in group.factors),
        )

    def has_factor(self, factor: str) -> bool:
        """Return whether a named factor is present."""

        return factor in self.factors


@dataclass(frozen=True, slots=True)
class Charge:
    """An exact charge under one named abelian generator."""

    generator: str
    value: Rational

    def __post_init__(self) -> None:
        if not self.generator.strip():
            raise ValueError("a charge requires a generator name")
        object.__setattr__(self, "value", coerce_rational(self.value))


@dataclass(frozen=True, slots=True, init=False)
class Representation:
    """A representation label with exact factor dimensions and charges."""

    name: str
    group: GaugeGroup
    factor_dimensions: tuple[tuple[str, int], ...]
    charges: tuple[Charge, ...]
    conjugate: bool

    def __init__(
        self,
        name: str,
        group: GaugeGroup,
        factor_dimensions: Iterable[tuple[str, int]],
        charges: Iterable[Charge] = (),
        conjugate: bool = False,
    ) -> None:
        dimensions = tuple(factor_dimensions)
        if not name.strip():
            raise ValueError("a representation requires a nonempty name")
        if not dimensions:
            raise ValueError("a representation requires factor dimensions")
        if any(factor not in group.factors for factor, _ in dimensions):
            raise ValueError("representation uses a factor outside its gauge group")
        if any(isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 1
               for _, dimension in dimensions):
            raise ValueError("representation dimensions must be positive integers")
        normalized_charges = tuple(charges)
        if len({charge.generator for charge in normalized_charges}) != len(normalized_charges):
            raise ValueError("representation charge generators must be unique")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "group", group)
        object.__setattr__(self, "factor_dimensions", dimensions)
        object.__setattr__(self, "charges", normalized_charges)
        object.__setattr__(self, "conjugate", conjugate)

    @property
    def dimension(self) -> int:
        """Return the product of declared factor dimensions."""

        result = 1
        for _, dimension in self.factor_dimensions:
            result *= dimension
        return result

    def charge(self, generator: str) -> Rational:
        """Return one exact charge or fail if it was not declared."""

        for charge in self.charges:
            if charge.generator == generator:
                return charge.value
        raise KeyError(f"charge {generator!r} is not declared on {self.name}")
