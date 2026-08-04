"""Exact four-dimensional Einstein-gravity and matter-coupling records.

Owns:
    Lorentzian metric fields, Levi-Civita connections, curvature tensors, Ricci and
    Einstein records, Einstein–Hilbert and cosmological terms, stress-energy data,
    minimal coupling, and covariant-conservation requirements.

Depends on:
    Spacetime tensors, field actions, and explicit symbolic dimensional constants;
    it does not import a concrete model or observations.

Must not:
    Supply a Newton or Planck value, fit a cosmological constant, claim a solved
    quantum-gravity theory, or select geometry from measured data.

Phase 0:
    Classical four-dimensional gravity is represented as exact contracts; numerical
    curvature solving remains a controlled engine responsibility.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from onetheory.core.errors import IncompatibleConvention
from onetheory.physics.fields import Action
from onetheory.physics.spacetime import LorentzianSpacetime, Metric, Tensor


@dataclass(frozen=True, slots=True)
class MetricField:
    """A dynamical Lorentzian metric field with no numerical default beyond a metric."""

    name: str
    spacetime: LorentzianSpacetime
    metric: Metric

    def __init__(
        self, name: str, spacetime: LorentzianSpacetime, metric: Metric | None = None
    ) -> None:
        if not name.strip():
            raise ValueError("metric fields require a name")
        selected = metric or spacetime.metric
        if selected.convention != spacetime.convention:
            raise IncompatibleConvention("metric field and spacetime use different conventions")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "spacetime", spacetime)
        object.__setattr__(self, "metric", selected)


@dataclass(frozen=True, slots=True)
class LeviCivitaConnection:
    """A torsion-free metric-compatible Levi-Civita connection record."""

    metric_field: MetricField
    coefficients: tuple[Any, ...]
    torsion_free: bool
    metric_compatible: bool

    def __init__(self, metric_field: MetricField, coefficients: Iterable[Any] = ()) -> None:
        values = tuple(coefficients)
        object.__setattr__(self, "metric_field", metric_field)
        object.__setattr__(self, "coefficients", values)
        object.__setattr__(self, "torsion_free", True)
        object.__setattr__(self, "metric_compatible", True)


@dataclass(frozen=True, slots=True)
class CurvatureTensor:
    """The Riemann curvature tensor of a declared connection."""

    connection: LeviCivitaConnection
    components: tuple[Any, ...]
    antisymmetric_last_pair: bool

    def __init__(self, connection: LeviCivitaConnection, components: Iterable[Any] = ()) -> None:
        object.__setattr__(self, "connection", connection)
        object.__setattr__(self, "components", tuple(components))
        object.__setattr__(self, "antisymmetric_last_pair", True)


@dataclass(frozen=True, slots=True)
class RicciTensor:
    """The Ricci contraction of a curvature tensor."""

    curvature: CurvatureTensor
    components: tuple[Any, ...]
    symmetric: bool

    def __init__(self, curvature: CurvatureTensor, components: Iterable[Any] = ()) -> None:
        object.__setattr__(self, "curvature", curvature)
        object.__setattr__(self, "components", tuple(components))
        object.__setattr__(self, "symmetric", True)


@dataclass(frozen=True, slots=True)
class RicciScalar:
    """The scalar curvature obtained by metric contraction of Ricci."""

    ricci: RicciTensor
    value: Any


@dataclass(frozen=True, slots=True)
class EinsteinTensor:
    """The exact tensor record G=R-1/2 gR."""

    ricci: RicciTensor
    scalar: RicciScalar
    components: tuple[Any, ...]
    expression: str

    def __init__(
        self, ricci: RicciTensor, scalar: RicciScalar, components: Iterable[Any] = ()
    ) -> None:
        if (
            ricci.curvature.connection.metric_field
            != scalar.ricci.curvature.connection.metric_field
        ):
            raise IncompatibleConvention("Einstein tensor records use different metrics")
        object.__setattr__(self, "ricci", ricci)
        object.__setattr__(self, "scalar", scalar)
        object.__setattr__(self, "components", tuple(components))
        object.__setattr__(self, "expression", "R_ab - 1/2 g_ab R")


@dataclass(frozen=True, slots=True)
class EinsteinHilbertAction:
    """The Einstein–Hilbert action with explicit unresolved normalizations."""

    metric_field: MetricField
    gravitational_constant_name: str
    cosmological_constant_name: str | None
    provenance: str
    mass_dimension: int

    def __init__(
        self,
        metric_field: MetricField,
        gravitational_constant_name: str = "G",
        cosmological_constant_name: str | None = None,
        provenance: str = "established Einstein gravity",
    ) -> None:
        if not gravitational_constant_name.strip() or not provenance.strip():
            raise ValueError("Einstein–Hilbert action requires explicit names and provenance")
        object.__setattr__(self, "metric_field", metric_field)
        object.__setattr__(self, "gravitational_constant_name", gravitational_constant_name)
        object.__setattr__(self, "cosmological_constant_name", cosmological_constant_name)
        object.__setattr__(self, "provenance", provenance)
        object.__setattr__(self, "mass_dimension", 4)


@dataclass(frozen=True, slots=True)
class StressEnergy:
    """A matter stress-energy tensor record and conservation requirement."""

    source_name: str
    spacetime: LorentzianSpacetime
    tensor: Tensor | None
    conserved: bool

    def __init__(
        self, source_name: str, spacetime: LorentzianSpacetime, tensor: Tensor | None = None
    ) -> None:
        if not source_name.strip():
            raise ValueError("stress-energy records require a source name")
        if tensor is not None and tensor.convention != spacetime.convention:
            raise IncompatibleConvention("stress-energy and spacetime use different conventions")
        object.__setattr__(self, "source_name", source_name)
        object.__setattr__(self, "spacetime", spacetime)
        object.__setattr__(self, "tensor", tensor)
        object.__setattr__(self, "conserved", False)


@dataclass(frozen=True, slots=True)
class MinimalCoupling:
    """A matter or gauge action coupled to one metric field."""

    action: Action
    metric_field: MetricField
    covariant: bool
    stress_energy: StressEnergy

    def __init__(self, action: Action, metric_field: MetricField) -> None:
        if action.domain.spacetime != metric_field.spacetime:
            raise IncompatibleConvention("action and metric use different spacetime conventions")
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "metric_field", metric_field)
        object.__setattr__(self, "covariant", True)
        object.__setattr__(self, "stress_energy", StressEnergy(action.name, metric_field.spacetime))


@dataclass(frozen=True, slots=True)
class GaugeActionCoupling:
    """Minimal metric coupling of an explicitly declared gauge-law collection."""

    factor_names: tuple[str, ...]
    metric_field: MetricField
    covariant: bool

    def __init__(self, factor_names: Iterable[str], metric_field: MetricField) -> None:
        names = tuple(factor_names)
        if not names or any(not name.strip() for name in names):
            raise ValueError("gauge coupling requires declared factor names")
        object.__setattr__(self, "factor_names", names)
        object.__setattr__(self, "metric_field", metric_field)
        object.__setattr__(self, "covariant", True)


@dataclass(frozen=True, slots=True)
class ConservationRequirement:
    """A declared covariant conservation requirement for a stress tensor."""

    stress_energy: StressEnergy
    equation: str

    def __init__(self, stress_energy: StressEnergy) -> None:
        object.__setattr__(self, "stress_energy", stress_energy)
        object.__setattr__(self, "equation", "∇_μ T^{μν}=0")


__all__ = [
    "ConservationRequirement",
    "CurvatureTensor",
    "EinsteinHilbertAction",
    "EinsteinTensor",
    "GaugeActionCoupling",
    "LeviCivitaConnection",
    "MetricField",
    "MinimalCoupling",
    "RicciScalar",
    "RicciTensor",
    "StressEnergy",
]
