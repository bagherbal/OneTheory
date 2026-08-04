"""Exact gauge groups, connections, representations, and anomaly metadata.

Owns:
    Gauge-group products, Lie-algebra metadata when explicitly supplied, exact
    abelian charges, conjugate representations, connections, covariant derivatives,
    field strengths, gauge transformations, kinetic terms, and anomaly indices.

Depends on:
    Core errors, exact Rational charges, and spacetime conventions; it is independent
    of concrete models and does not import field or matter implementations.

Must not:
    Implement a general symbolic Lie-algebra system, choose a Wilson line, import
    the Schoen carrier, fit couplings, or bridge unrelated physical theories.

Phase 0:
    Exact general gauge-law records are implemented; numerical gauge solutions and
    carrier-specific connections remain unresolved inputs.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from onetheory.core.errors import IncompatibleConvention
from onetheory.math.numbers import Rational, coerce_rational
from onetheory.physics.spacetime import LorentzianSpacetime


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
        if any(
            isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 1
            for dimension in factor_dimensions
        ):
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
    quadratic_indices: tuple[tuple[str, Rational], ...]
    cubic_indices: tuple[tuple[str, Rational], ...]

    def __init__(
        self,
        name: str,
        group: GaugeGroup,
        factor_dimensions: Iterable[tuple[str, int]],
        charges: Iterable[Charge] = (),
        conjugate: bool = False,
        quadratic_indices: Mapping[str, object] | None = None,
        cubic_indices: Mapping[str, object] | None = None,
    ) -> None:
        dimensions = tuple(factor_dimensions)
        if not name.strip():
            raise ValueError("a representation requires a nonempty name")
        if not dimensions:
            raise ValueError("a representation requires factor dimensions")
        if any(factor not in group.factors for factor, _ in dimensions):
            raise ValueError("representation uses a factor outside its gauge group")
        if any(
            isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 1
            for _, dimension in dimensions
        ):
            raise ValueError("representation dimensions must be positive integers")
        normalized_charges = tuple(charges)
        if len({charge.generator for charge in normalized_charges}) != len(normalized_charges):
            raise ValueError("representation charge generators must be unique")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "group", group)
        object.__setattr__(self, "factor_dimensions", dimensions)
        object.__setattr__(self, "charges", normalized_charges)
        object.__setattr__(self, "conjugate", conjugate)
        object.__setattr__(
            self,
            "quadratic_indices",
            tuple(
                sorted(
                    (factor, coerce_rational(value))
                    for factor, value in (quadratic_indices or {}).items()
                )
            ),
        )
        object.__setattr__(
            self,
            "cubic_indices",
            tuple(
                sorted(
                    (factor, coerce_rational(value))
                    for factor, value in (cubic_indices or {}).items()
                )
            ),
        )

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

    def conjugate_representation(self) -> Representation:
        """Return the exact conjugate representation with negated abelian charges."""

        return Representation(
            f"{self.name}*",
            self.group,
            self.factor_dimensions,
            tuple(Charge(charge.generator, -charge.value) for charge in self.charges),
            not self.conjugate,
            dict(self.quadratic_indices),
            dict(self.cubic_indices),
        )

    def dimension_of_factor(self, factor: str) -> int:
        """Return a declared factor dimension, using one for a singlet."""

        for candidate, dimension in self.factor_dimensions:
            if candidate == factor:
                return dimension
        if factor in self.group.factors:
            return 1
        raise KeyError(factor)

    def quadratic_index(self, factor: str) -> Rational:
        """Return explicit Dynkin-index metadata for a factor."""

        return dict(self.quadratic_indices).get(factor, Rational(0))

    def cubic_index(self, factor: str) -> Rational:
        """Return explicit cubic-index metadata for a factor."""

        return dict(self.cubic_indices).get(factor, Rational(0))


@dataclass(frozen=True, slots=True)
class LieGenerator:
    """One explicitly supplied Lie-algebra generator record."""

    factor: str
    label: str
    normalization: Rational

    def __init__(self, factor: str, label: str, normalization: object = 1) -> None:
        if not factor.strip() or not label.strip():
            raise ValueError("Lie generators require factor and label")
        object.__setattr__(self, "factor", factor)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "normalization", coerce_rational(normalization))


@dataclass(frozen=True, slots=True)
class StructureConstants:
    """Sparse exact structure constants in one declared generator basis."""

    factor: str
    values: tuple[tuple[tuple[str, str, str], Rational], ...]

    def __init__(
        self,
        factor: str,
        values: Mapping[tuple[str, str, str], object],
    ) -> None:
        if not factor.strip():
            raise ValueError("structure constants require a factor")
        object.__setattr__(self, "factor", factor)
        object.__setattr__(
            self,
            "values",
            tuple(sorted((key, coerce_rational(value)) for key, value in values.items())),
        )


@dataclass(frozen=True, slots=True)
class GaugeConnection:
    """A gauge connection record on one spacetime and group."""

    spacetime: LorentzianSpacetime
    group: GaugeGroup
    components: tuple[Any, ...]
    coupling_name: str

    def __init__(
        self,
        spacetime: LorentzianSpacetime,
        group: GaugeGroup,
        components: Iterable[Any],
        coupling_name: str,
    ) -> None:
        values = tuple(components)
        if len(values) != spacetime.dimension:
            raise ValueError("a connection requires one component per spacetime direction")
        if not coupling_name.strip():
            raise ValueError("a connection requires an explicit coupling name")
        object.__setattr__(self, "spacetime", spacetime)
        object.__setattr__(self, "group", group)
        object.__setattr__(self, "components", values)
        object.__setattr__(self, "coupling_name", coupling_name)


@dataclass(frozen=True, slots=True)
class CovariantDerivative:
    """A covariant derivative contract for a field representation."""

    connection: GaugeConnection
    representation: Representation
    ordinary_derivative: Any
    gauge_action: Any

    def __post_init__(self) -> None:
        if self.representation.group != self.connection.group:
            raise IncompatibleConvention("field representation and connection use different groups")

    @property
    def expression(self) -> tuple[Any, Any, Any]:
        return (self.ordinary_derivative, self.connection, self.gauge_action)

    def transforms_covariantly(self, transformed_field: Any, transformed_connection: Any) -> bool:
        """Return true only when both transformation records target this derivative."""

        if isinstance(transformed_connection, GaugeTransformation):
            return (
                transformed_connection.group == self.connection.group
                and transformed_field is not None
            )
        return transformed_field is not None and transformed_connection is not None


@dataclass(frozen=True, slots=True)
class FieldStrength:
    """The antisymmetric curvature contract F=dA+g A∧A."""

    connection: GaugeConnection
    components: tuple[tuple[int, int, Any], ...]

    def __init__(
        self, connection: GaugeConnection, components: Iterable[tuple[int, int, Any]]
    ) -> None:
        values = tuple(components)
        if any(
            left == right or not 0 <= left < 4 or not 0 <= right < 4 for left, right, _ in values
        ):
            raise ValueError("field-strength indices must be distinct four-dimensional directions")
        if any((right, left, value) in values for left, right, value in values):
            raise ValueError("field-strength components must use one orientation")
        object.__setattr__(self, "connection", connection)
        object.__setattr__(self, "components", values)

    def component(self, left: int, right: int) -> Any:
        def negate(value: Any) -> Any:
            if isinstance(value, (int, float, Rational)):
                return -value
            return f"-{value}"

        for candidate_left, candidate_right, value in self.components:
            if (left, right) == (candidate_left, candidate_right):
                return value
            if (left, right) == (candidate_right, candidate_left):
                return negate(value)
        return 0

    def transforms_covariantly(self, transformation: GaugeTransformation) -> bool:
        return transformation.group == self.connection.group


@dataclass(frozen=True, slots=True)
class GaugeTransformation:
    """A local group transformation record with explicit parameter data."""

    group: GaugeGroup
    parameter: str
    infinitesimal: bool

    def __post_init__(self) -> None:
        if not self.parameter.strip():
            raise ValueError("gauge transformations require a parameter name")


@dataclass(frozen=True, slots=True)
class GaugeKineticTerm:
    """A gauge kinetic term retaining its normalization and field strength."""

    field_strength: FieldStrength
    coupling_name: str
    trace_convention: str
    mass_dimension: Rational

    def __init__(
        self, field_strength: FieldStrength, coupling_name: str, trace_convention: str = "Tr"
    ) -> None:
        if not coupling_name.strip() or not trace_convention.strip():
            raise ValueError("gauge kinetic terms require coupling and trace conventions")
        object.__setattr__(self, "field_strength", field_strength)
        object.__setattr__(self, "coupling_name", coupling_name)
        object.__setattr__(self, "trace_convention", trace_convention)
        object.__setattr__(self, "mass_dimension", Rational(4))


@dataclass(frozen=True, slots=True)
class AnomalyVector:
    """Exact anomaly coefficients for one left-handed chiral spectrum."""

    coefficients: tuple[tuple[str, Rational], ...]

    def __init__(self, coefficients: Mapping[str, object]) -> None:
        object.__setattr__(
            self,
            "coefficients",
            tuple(sorted((name, coerce_rational(value)) for name, value in coefficients.items())),
        )

    def value(self, name: str) -> Rational:
        return dict(self.coefficients).get(name, Rational(0))

    @property
    def cancels(self) -> bool:
        return all(value == 0 for _, value in self.coefficients)


def _factor_multiplicity(representation: Representation, factor: str) -> int:
    result = 1
    for candidate, dimension in representation.factor_dimensions:
        if candidate != factor:
            result *= dimension
    return result


def _nonabelian_index(dimension: int) -> Rational:
    return Rational(1, 2) if dimension == 2 or dimension == 3 else Rational(0)


def anomaly_vector(
    multiplets: Iterable[Any], generators: Iterable[str] | None = None
) -> AnomalyVector:
    """Compute exact cubic, mixed, gravitational, and nonabelian anomaly rows."""

    items = tuple(multiplets)
    chosen_generators = (
        tuple(generators)
        if generators is not None
        else tuple(
            sorted({charge.generator for item in items for charge in item.representation.charges})
        )
    )
    rows: dict[str, Rational] = {}
    for generator in chosen_generators:
        rows[f"{generator}^3"] = Rational(0)
        rows[f"grav-{generator}"] = Rational(0)
        for other in chosen_generators:
            if other != generator:
                rows[f"{generator}^2-{other}"] = Rational(0)
    groups = {factor for item in items for factor, _ in item.representation.factor_dimensions}
    for factor in groups:
        if factor.startswith("SU("):
            if factor != "SU(2)_L":
                rows[f"{factor}^3"] = Rational(0)
            for generator in chosen_generators:
                rows[f"{factor}^2-{generator}"] = Rational(0)
    for multiplet in items:
        representation = multiplet.representation
        multiplicity = multiplet.multiplicity
        dimension = representation.dimension
        for generator in chosen_generators:
            charge = representation.charge(generator)
            rows[f"{generator}^3"] += charge**3 * dimension * multiplicity
            rows[f"grav-{generator}"] += charge * dimension * multiplicity
            for other in chosen_generators:
                if other != generator:
                    rows[f"{generator}^2-{other}"] += (
                        charge**2 * representation.charge(other) * dimension * multiplicity
                    )
        for factor in groups:
            factor_dimension = representation.dimension_of_factor(factor)
            if factor_dimension not in (2, 3):
                continue
            index = representation.quadratic_index(factor)
            if index.is_zero():
                index = _nonabelian_index(factor_dimension)
            cubic_index = representation.cubic_index(factor)
            if cubic_index.is_zero():
                cubic_index = index
            sign = (
                Rational(-1) if representation.conjugate and factor_dimension == 3 else Rational(1)
            )
            if factor != "SU(2)_L":
                rows[f"{factor}^3"] += (
                    sign * cubic_index * _factor_multiplicity(representation, factor) * multiplicity
                )
            for generator in chosen_generators:
                rows[f"{factor}^2-{generator}"] += (
                    index
                    * representation.charge(generator)
                    * _factor_multiplicity(representation, factor)
                    * multiplicity
                )
    return AnomalyVector(rows)


def gauge_singlet(representations: Iterable[Representation]) -> bool:
    """Check an explicit low-rank tensor product for gauge-singlet compatibility."""

    values = tuple(representations)
    if not values:
        raise ValueError("a gauge-singlet product requires representations")
    group = values[0].group
    if any(value.group != group for value in values):
        raise IncompatibleConvention("representations use different gauge groups")
    for generator in {charge.generator for value in values for charge in value.charges}:
        if sum((value.charge(generator) for value in values), Rational(0)) != 0:
            return False
    for factor in group.factors:
        dimensions = [
            value.dimension_of_factor(factor)
            for value in values
            if value.dimension_of_factor(factor) != 1
        ]
        if not dimensions:
            continue
        if factor == "SU(2)_L":
            if len(dimensions) % 2 or any(dimension != 2 for dimension in dimensions):
                return False
        elif factor == "SU(3)_C":
            if len(dimensions) == 2:
                colored = [value for value in values if value.dimension_of_factor(factor) == 3]
                if len(colored) != 2 or colored[0].conjugate == colored[1].conjugate:
                    return False
            elif len(dimensions) == 3 and all(dimension == 3 for dimension in dimensions):
                if (
                    len(
                        {
                            value.conjugate
                            for value in values
                            if value.dimension_of_factor(factor) == 3
                        }
                    )
                    != 1
                ):
                    return False
            else:
                return False
        elif any(dimension != 1 for dimension in dimensions):
            return False
    return True


__all__ = [
    "AnomalyVector",
    "Charge",
    "CovariantDerivative",
    "FieldStrength",
    "GaugeConnection",
    "GaugeGroup",
    "GaugeKineticTerm",
    "GaugeTransformation",
    "LieGenerator",
    "Representation",
    "StructureConstants",
    "anomaly_vector",
    "gauge_singlet",
]
