"""Exact graph evaluation and parameterized finite-dimensional law systems.

Owns:
    Deterministic exact graph evaluation, immutable evaluation records, validated
    parameter sets, supported Euler–Lagrange equation records, and Hamiltonian law
    systems consumed by the numerical integrator.

Depends on:
    `onetheory.engine.graph` and `onetheory.core.precision`; it remains independent
    of concrete models, reality, verification, research, and observations.

Must not:
    Invent graph nodes, return placeholders, select numerical approximations
    silently, or turn an unresolved physical request into a successful result.

    Phase 0:
    Exact graph solving and generic parameterized law contracts are implemented;
    numerical acceptance still requires explicit refinement evidence.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from math import isfinite

from onetheory.core.precision import PrecisionPolicy
from onetheory.engine.graph import ComputationGraph
from onetheory.engine.state import VacuumEngineState
from onetheory.physics.vacuum import (
    ControlCriterion,
    ControlLedger,
    CriticalPointReport,
    VacuumEquationSystem,
    VacuumSolveReport,
    solve_supersymmetric_vacuum,
)

NumericState = tuple[float, ...]
DerivativeFunction = Callable[[float, NumericState, "ParameterSet"], NumericState]
EnergyFunction = Callable[[NumericState, "ParameterSet"], float]
AccelerationFunction = Callable[[float, NumericState, NumericState, "ParameterSet"], NumericState]


@dataclass(frozen=True, slots=True)
class Evaluation:
    """An immutable exact target value with the nodes evaluated to obtain it."""

    target: str
    value: object
    evaluated_nodes: tuple[str, ...]


def solve_exact(
    graph: ComputationGraph,
    target: str,
    inputs: dict[str, object],
) -> Evaluation:
    """Evaluate one graph target using exact policy and no fallback values."""

    PrecisionPolicy.exact().require_exact()
    values: dict[str, object] = dict(inputs)
    ordered = graph.execution_order(target, values)
    for node in ordered:
        arguments = {name: values[name] for name in node.prerequisites}
        values[node.name] = node.evaluator(arguments)
    if target not in values:
        values[target] = graph.node(target).evaluator(
            {name: values[name] for name in graph.node(target).prerequisites}
        )
    return Evaluation(target, values[target], tuple(node.name for node in ordered))


def solve_vacuum(
    system: VacuumEquationSystem,
    initial_regions: Iterable[Mapping[str, complex | float | int]],
    criteria: Iterable[ControlCriterion],
    precision_schedule: tuple[int, ...] = (40, 80),
    critical_points: Iterable[CriticalPointReport] = (),
) -> VacuumEngineState:
    """Solve one explicit vacuum system and aggregate its supplied control ledger."""

    report: VacuumSolveReport = solve_supersymmetric_vacuum(
        system, initial_regions, precision_schedule
    )
    return VacuumEngineState(report, ControlLedger.from_criteria(criteria), tuple(critical_points))


@dataclass(frozen=True, slots=True)
class ParameterSet:
    """A finite numerical parameter set with explicit required names."""

    values: tuple[tuple[str, float], ...]

    def __init__(self, values: Mapping[str, float], required: Iterable[str] | None = None) -> None:
        required_names = tuple(values) if required is None else tuple(required)
        if len(set(required_names)) != len(required_names) or any(
            not name.strip() for name in required_names
        ):
            raise ValueError("parameter requirements must be unique and named")
        if set(values) != set(required_names):
            missing = set(required_names) - set(values)
            extra = set(values) - set(required_names)
            raise ValueError(
                f"parameter set mismatch: missing={sorted(missing)}, extra={sorted(extra)}"
            )
        normalized = tuple(sorted((name, float(value)) for name, value in values.items()))
        if any(not isfinite(value) for _, value in normalized):
            raise ValueError("parameters must be finite numerical values")
        object.__setattr__(self, "values", normalized)

    def get(self, name: str) -> float:
        return dict(self.values)[name]


@dataclass(frozen=True, slots=True)
class EulerLagrangeEquation:
    """A supported finite-dimensional Euler–Lagrange equation record."""

    coordinate: str
    equation: str
    residual_definition: str


@dataclass(frozen=True, slots=True)
class ComponentFieldLagrangian:
    """A supported component-field Euler–Lagrange expression record."""

    field_name: str
    expression: str
    equation: EulerLagrangeEquation

    def __init__(self, field_name: str, expression: str) -> None:
        if not field_name.strip() or not expression.strip():
            raise ValueError("component-field Lagrangians require field and expression")
        object.__setattr__(self, "field_name", field_name)
        object.__setattr__(self, "expression", expression)
        object.__setattr__(
            self,
            "equation",
            EulerLagrangeEquation(
                field_name,
                f"∂L/∂{field_name} - ∂_μ(∂L/∂(∂_μ{field_name})) = 0",
                f"EL_component({field_name})",
            ),
        )


def component_field_euler_lagrange(field_name: str, expression: str) -> EulerLagrangeEquation:
    """Return the supported component-field Euler–Lagrange equation record."""

    return ComponentFieldLagrangian(field_name, expression).equation


@dataclass(frozen=True, slots=True)
class FiniteLagrangian:
    """A finite-dimensional Lagrangian with declared derivative expressions."""

    coordinates: tuple[str, ...]
    expression: str
    equations: tuple[EulerLagrangeEquation, ...]
    acceleration: AccelerationFunction | None

    def __init__(
        self,
        coordinates: Iterable[str],
        expression: str,
        acceleration: AccelerationFunction | None = None,
    ) -> None:
        names = tuple(coordinates)
        if not names or len(set(names)) != len(names) or any(not name.strip() for name in names):
            raise ValueError("finite Lagrangians require unique coordinate names")
        if not expression.strip():
            raise ValueError("finite Lagrangians require an expression")
        object.__setattr__(self, "coordinates", names)
        object.__setattr__(self, "expression", expression)
        object.__setattr__(self, "acceleration", acceleration)
        object.__setattr__(
            self,
            "equations",
            tuple(
                EulerLagrangeEquation(
                    coordinate,
                    f"d/dt(∂L/∂{coordinate}dot) - ∂L/∂{coordinate} = 0",
                    f"EL({coordinate})",
                )
                for coordinate in names
            ),
        )


def euler_lagrange_equations(lagrangian: FiniteLagrangian) -> tuple[EulerLagrangeEquation, ...]:
    """Return the declared supported Euler–Lagrange equations."""

    return lagrangian.equations


def euler_lagrange_acceleration(
    lagrangian: FiniteLagrangian,
    time: float,
    coordinates: NumericState,
    velocities: NumericState,
    parameters: ParameterSet,
) -> NumericState:
    """Evaluate an explicitly supplied supported Euler–Lagrange acceleration law."""

    if lagrangian.acceleration is None:
        raise ValueError("this Lagrangian has no supported acceleration evaluator")
    if len(coordinates) != len(lagrangian.coordinates) or len(velocities) != len(coordinates):
        raise ValueError("Euler–Lagrange coordinates and velocities have the wrong dimension")
    result = lagrangian.acceleration(time, coordinates, velocities, parameters)
    if len(result) != len(coordinates):
        raise ValueError("Euler–Lagrange acceleration has the wrong dimension")
    return result


@dataclass(frozen=True, slots=True)
class HamiltonianSystem:
    """A finite-dimensional Hamiltonian or first-order law system."""

    name: str
    labels: tuple[str, ...]
    derivative: DerivativeFunction
    energy: EnergyFunction
    required_parameters: tuple[str, ...]

    def __init__(
        self,
        name: str,
        labels: Iterable[str],
        derivative: DerivativeFunction,
        energy: EnergyFunction,
        required_parameters: Iterable[str] = (),
    ) -> None:
        names = tuple(labels)
        required = tuple(required_parameters)
        if not name.strip() or not names or len(set(names)) != len(names):
            raise ValueError("law systems require a name and unique state labels")
        if any(not label.strip() for label in names):
            raise ValueError("law-system labels must be nonempty")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "labels", names)
        object.__setattr__(self, "derivative", derivative)
        object.__setattr__(self, "energy", energy)
        object.__setattr__(self, "required_parameters", required)

    @property
    def dimension(self) -> int:
        return len(self.labels)

    def validate_state(self, state: Iterable[float]) -> NumericState:
        values = tuple(float(value) for value in state)
        if len(values) != self.dimension or any(not isfinite(value) for value in values):
            raise ValueError("law-system state has the wrong finite dimension")
        return values

    def validate_parameters(self, values: Mapping[str, float]) -> ParameterSet:
        return ParameterSet(values, self.required_parameters)


def first_order_system_from_lagrangian(
    lagrangian: FiniteLagrangian,
    energy: EnergyFunction,
    required_parameters: Iterable[str] = (),
) -> HamiltonianSystem:
    """Convert a supported second-order Lagrangian law into engine state form."""

    labels = (*lagrangian.coordinates, *(f"v_{name}" for name in lagrangian.coordinates))

    def derivative(time: float, state: NumericState, parameters: ParameterSet) -> NumericState:
        count = len(lagrangian.coordinates)
        coordinates = state[:count]
        velocities = state[count:]
        accelerations = euler_lagrange_acceleration(
            lagrangian, time, coordinates, velocities, parameters
        )
        return (*velocities, *accelerations)

    return HamiltonianSystem(
        f"Euler-Lagrange system: {lagrangian.expression}",
        labels,
        derivative,
        energy,
        required_parameters,
    )
