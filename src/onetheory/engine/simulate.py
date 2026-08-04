"""Deterministic numerical evolution and textbook benchmark dynamics.

Owns:
    Explicitly parameterized first-order law integration, refinement-based
    convergence records, conservation diagnostics, immutable trajectories, and
    harmonic, scalar, Higgs, electromagnetic, Maxwell, and geodesic benchmarks.

Depends on:
    Core precision/errors, generic engine state and solve contracts, and Python's
    standard numerical primitives; no model-specific or rendering dependency.

Must not:
    Invent initial conditions or parameters, silently accept nonconvergence, create
    a simplified Standard Model universe, or claim benchmark output is a prediction.

Phase 0:
    Controlled benchmark evolution is implemented; carrier and interacting-QFT
    simulation remain outside this numerical boundary.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from fractions import Fraction

from onetheory.core.precision import PrecisionPolicy
from onetheory.engine.solve import HamiltonianSystem, ParameterSet
from onetheory.engine.state import (
    ConservationDiagnostic,
    ConvergenceRecord,
    SimulationResult,
    SimulationState,
    Trajectory,
)


def _add(left: tuple[float, ...], right: tuple[float, ...], scale: float) -> tuple[float, ...]:
    return tuple(a + scale * b for a, b in zip(left, right, strict=True))


def _rk4_step(
    system: HamiltonianSystem,
    time: float,
    state: tuple[float, ...],
    step: float,
    parameters: ParameterSet,
) -> tuple[float, ...]:
    k1 = system.derivative(time, state, parameters)
    k2 = system.derivative(time + step / 2, _add(state, k1, step / 2), parameters)
    k3 = system.derivative(time + step / 2, _add(state, k2, step / 2), parameters)
    k4 = system.derivative(time + step, _add(state, k3, step), parameters)
    return tuple(
        value + step * (a + 2 * b + 2 * c + d) / 6
        for value, a, b, c, d in zip(state, k1, k2, k3, k4, strict=True)
    )


def _integrate(
    system: HamiltonianSystem,
    initial: tuple[float, ...],
    parameters: ParameterSet,
    duration: float,
    step_size: float,
) -> tuple[SimulationState, ...]:
    steps = round(duration / step_size)
    if steps < 1 or abs(steps * step_size - duration) > 1e-10:
        raise ValueError("duration must be an integer multiple of step_size")
    values = [SimulationState(0.0, initial, system.labels)]
    state = initial
    time = 0.0
    for _ in range(steps):
        state = _rk4_step(system, time, state, step_size, parameters)
        time += step_size
        values.append(SimulationState(time, state, system.labels))
    return tuple(values)


def simulate_system(
    system: HamiltonianSystem,
    initial: tuple[float, ...],
    parameters: Mapping[str, float],
    duration: float,
    step_size: float,
    tolerance: float = 1e-7,
) -> SimulationResult:
    """Integrate a law and accept it only after a deterministic refinement check."""

    if duration <= 0 or step_size <= 0 or tolerance < 0:
        raise ValueError("simulation duration, step, and tolerance must be valid")
    initial_state = system.validate_state(initial)
    parameter_set = system.validate_parameters(parameters)
    policy = PrecisionPolicy.numerical(16, Fraction(str(tolerance)), Fraction(str(tolerance)))
    coarse = _integrate(system, initial_state, parameter_set, duration, step_size)
    fine = _integrate(system, initial_state, parameter_set, duration, step_size / 2)
    endpoint_error = max(
        abs(left - right) for left, right in zip(coarse[-1].values, fine[-1].values, strict=True)
    )
    convergence = ConvergenceRecord((step_size, step_size / 2), (endpoint_error,), tolerance)
    policy.require_converged(convergence.converged)
    initial_energy = system.energy(initial_state, parameter_set)
    final_energy = system.energy(fine[-1].values, parameter_set)
    diagnostics = (ConservationDiagnostic("Hamiltonian", initial_energy, final_energy, tolerance),)
    return SimulationResult(
        Trajectory(system.name, fine, step_size / 2),
        convergence,
        diagnostics,
    )


def harmonic_oscillator() -> HamiltonianSystem:
    """Return the parameterized textbook harmonic oscillator law."""

    def derivative(
        _: float, state: tuple[float, ...], parameters: ParameterSet
    ) -> tuple[float, ...]:
        mass = parameters.get("mass")
        omega = parameters.get("omega")
        return state[1] / mass, -mass * omega * omega * state[0]

    def energy(state: tuple[float, ...], parameters: ParameterSet) -> float:
        mass = parameters.get("mass")
        omega = parameters.get("omega")
        return state[1] ** 2 / (2 * mass) + mass * omega * omega * state[0] ** 2 / 2

    return HamiltonianSystem(
        "harmonic oscillator", ("q", "p"), derivative, energy, ("mass", "omega")
    )


def free_complex_scalar() -> HamiltonianSystem:
    """Return two uncoupled real components of a free complex scalar mode."""

    def derivative(
        _: float, state: tuple[float, ...], parameters: ParameterSet
    ) -> tuple[float, ...]:
        mass = parameters.get("mass")
        return state[2], state[3], -mass * mass * state[0], -mass * mass * state[1]

    def energy(state: tuple[float, ...], parameters: ParameterSet) -> float:
        mass = parameters.get("mass")
        return (state[2] ** 2 + state[3] ** 2) / 2 + mass * mass * (
            state[0] ** 2 + state[1] ** 2
        ) / 2

    return HamiltonianSystem(
        "free complex scalar mode",
        ("phi_re", "phi_im", "pi_re", "pi_im"),
        derivative,
        energy,
        ("mass",),
    )


def homogeneous_higgs_mode() -> HamiltonianSystem:
    """Return a homogeneous Higgs mode with an explicit quartic potential."""

    def derivative(
        _: float, state: tuple[float, ...], parameters: ParameterSet
    ) -> tuple[float, ...]:
        mass = parameters.get("mass")
        coupling = parameters.get("lambda")
        vacuum = parameters.get("v")
        return state[1] / mass, -coupling * (state[0] * state[0] - vacuum * vacuum) * state[0]

    def energy(state: tuple[float, ...], parameters: ParameterSet) -> float:
        mass = parameters.get("mass")
        coupling = parameters.get("lambda")
        vacuum = parameters.get("v")
        potential = coupling * (state[0] * state[0] - vacuum * vacuum) ** 2 / 4
        return state[1] ** 2 / (2 * mass) + potential

    return HamiltonianSystem(
        "homogeneous Higgs mode",
        ("h", "pi_h"),
        derivative,
        energy,
        ("mass", "lambda", "v"),
    )


def charged_particle_in_magnetic_field() -> HamiltonianSystem:
    """Return canonical planar charged-particle motion in a supplied B field."""

    def derivative(
        _: float, state: tuple[float, ...], parameters: ParameterSet
    ) -> tuple[float, ...]:
        mass = parameters.get("mass")
        charge = parameters.get("charge")
        magnetic = parameters.get("magnetic_field")
        kinetic_x = state[2] + charge * magnetic * state[1] / 2
        kinetic_y = state[3] - charge * magnetic * state[0] / 2
        velocity_x = kinetic_x / mass
        velocity_y = kinetic_y / mass
        return (
            velocity_x,
            velocity_y,
            charge * magnetic * velocity_y / 2,
            -charge * magnetic * velocity_x / 2,
        )

    def energy(state: tuple[float, ...], parameters: ParameterSet) -> float:
        mass = parameters.get("mass")
        charge = parameters.get("charge")
        magnetic = parameters.get("magnetic_field")
        kinetic_x = state[2] + charge * magnetic * state[1] / 2
        kinetic_y = state[3] - charge * magnetic * state[0] / 2
        return (kinetic_x * kinetic_x + kinetic_y * kinetic_y) / (2 * mass)

    return HamiltonianSystem(
        "charged particle in fixed electromagnetic field",
        ("x", "y", "p_x", "p_y"),
        derivative,
        energy,
        ("mass", "charge", "magnetic_field"),
    )


def free_maxwell_mode() -> HamiltonianSystem:
    """Return one transverse free Maxwell mode as a harmonic oscillator."""

    def derivative(
        _: float, state: tuple[float, ...], parameters: ParameterSet
    ) -> tuple[float, ...]:
        omega = parameters.get("omega")
        return state[1], -omega * omega * state[0]

    def energy(state: tuple[float, ...], parameters: ParameterSet) -> float:
        omega = parameters.get("omega")
        return (state[1] ** 2 + omega * omega * state[0] ** 2) / 2

    return HamiltonianSystem("free Maxwell mode", ("A", "Pi_A"), derivative, energy, ("omega",))


def geodesic_motion(
    dimension: int,
    christoffel: Callable[[tuple[float, ...]], tuple[tuple[tuple[float, ...], ...], ...]],
    metric_energy: Callable[[tuple[float, ...], tuple[float, ...]], float],
) -> HamiltonianSystem:
    """Return geodesic motion for a supplied Christoffel field and metric energy."""

    if dimension < 1:
        raise ValueError("geodesic dimension must be positive")
    labels = tuple([f"x{i}" for i in range(dimension)] + [f"v{i}" for i in range(dimension)])

    def derivative(_: float, state: tuple[float, ...], __: ParameterSet) -> tuple[float, ...]:
        positions = state[:dimension]
        velocities = state[dimension:]
        symbols = christoffel(positions)
        accelerations = tuple(
            -sum(
                symbols[coordinate][mu][nu] * velocities[mu] * velocities[nu]
                for mu in range(dimension)
                for nu in range(dimension)
            )
            for coordinate in range(dimension)
        )
        return tuple(velocities) + accelerations

    def energy(state: tuple[float, ...], __: ParameterSet) -> float:
        return metric_energy(state[:dimension], state[dimension:])

    return HamiltonianSystem(f"{dimension}D geodesic motion", labels, derivative, energy)


__all__ = [
    "charged_particle_in_magnetic_field",
    "free_complex_scalar",
    "free_maxwell_mode",
    "geodesic_motion",
    "harmonic_oscillator",
    "homogeneous_higgs_mode",
    "simulate_system",
]
