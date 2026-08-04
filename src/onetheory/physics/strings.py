"""Minimal exact heterotic compactification and published-input types.

Owns:
    Immutable compactification-space metadata, bundle descriptors, Wilson-line
    metadata, and traceable published physical input records.

Depends on:
    `onetheory.core.errors` for explicit validation and `onetheory.math.numbers`
    for exact topological coordinates; it remains independent of the Schoen model.

Must not:
    Claim a hidden bundle from a required topological class, implement metrics or
    instantons, select a compactification from observations, or import research.

Phase 0:
    Minimal exact string-theory vocabulary is implemented; unresolved dynamical
    constructions remain unavailable rather than represented by placeholders.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from onetheory.math.numbers import Rational, coerce_rational
from onetheory.physics.gauge import GaugeGroup


@dataclass(frozen=True, slots=True)
class PublishedPhysicalInput:
    """A traceable published input without executable source-document imports."""

    identifier: str
    citation: str
    locator: str
    statement: str

    def __post_init__(self) -> None:
        if any(not value.strip() for value in
               (self.identifier, self.citation, self.locator, self.statement)):
            raise ValueError("published physical inputs require complete provenance")


@dataclass(frozen=True, slots=True, init=False)
class CompactificationSpace:
    """Exact topological metadata for a compactification space."""

    name: str
    complex_dimension: int
    cover_degree: int
    fundamental_group_order: int
    input_record: PublishedPhysicalInput

    def __init__(
        self,
        name: str,
        complex_dimension: int,
        cover_degree: int,
        fundamental_group_order: int,
        input_record: PublishedPhysicalInput,
    ) -> None:
        if not name.strip():
            raise ValueError("a compactification requires a name")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 1
               for value in (complex_dimension, cover_degree, fundamental_group_order)):
            raise ValueError("compactification dimensions and orders must be positive")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "complex_dimension", complex_dimension)
        object.__setattr__(self, "cover_degree", cover_degree)
        object.__setattr__(self, "fundamental_group_order", fundamental_group_order)
        object.__setattr__(self, "input_record", input_record)


class BundleStatus(StrEnum):
    """Status labels that prevent required classes from becoming bundles."""

    PUBLISHED = "published"
    EXACT_CARRIER_RESULT = "exact_carrier_result"
    REQUIRED_TOPOLOGICAL_CLASS = "required_topological_class"


@dataclass(frozen=True, slots=True, init=False)
class Bundle:
    """A typed bundle descriptor with explicit status and Chern coordinates."""

    name: str
    rank: int
    structure_group: GaugeGroup
    c1: tuple[Rational, ...]
    c2: tuple[Rational, ...]
    c3: Rational
    status: BundleStatus

    def __init__(
        self,
        name: str,
        rank: int,
        structure_group: GaugeGroup,
        c1: Iterable[object],
        c2: Iterable[object],
        c3: object,
        status: BundleStatus,
    ) -> None:
        first = tuple(coerce_rational(value) for value in c1)
        second = tuple(coerce_rational(value) for value in c2)
        if not name.strip() or not first or len(first) != len(second):
            raise ValueError("bundle Chern coordinates must be nonempty and parallel")
        if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1:
            raise ValueError("bundle rank must be positive")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "rank", rank)
        object.__setattr__(self, "structure_group", structure_group)
        object.__setattr__(self, "c1", first)
        object.__setattr__(self, "c2", second)
        object.__setattr__(self, "c3", coerce_rational(c3))
        object.__setattr__(self, "status", status)


@dataclass(frozen=True, slots=True, init=False)
class WilsonLine:
    """A finite exact Wilson-line character assignment."""

    name: str
    gauge_group: GaugeGroup
    order: int
    characters: tuple[tuple[str, int], ...]

    def __init__(
        self,
        name: str,
        gauge_group: GaugeGroup,
        order: int,
        characters: Iterable[tuple[str, int]],
    ) -> None:
        values = tuple(characters)
        if not name.strip() or isinstance(order, bool) or not isinstance(order, int) or order < 2:
            raise ValueError("a Wilson line requires a name and order at least two")
        if len({label for label, _ in values}) != len(values):
            raise ValueError("Wilson-line labels must be unique")
        if any(not label.strip() or isinstance(character, bool) or not isinstance(character, int)
               or not 0 <= character < order for label, character in values):
            raise ValueError("Wilson-line characters must be canonical integers modulo order")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "gauge_group", gauge_group)
        object.__setattr__(self, "order", order)
        object.__setattr__(self, "characters", values)

    def character(self, label: str) -> int:
        """Return one declared character."""

        for candidate, value in self.characters:
            if candidate == label:
                return value
        raise KeyError(label)
