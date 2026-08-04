"""Test deterministic benchmark evolution and convergence evidence.

Owns:
    Replay determinism, refinement acceptance, conservation diagnostics, and the
    supported textbook benchmark law constructors.

Depends on:
    Generic engine solve and simulation modules plus pytest.

Must not:
    Treat benchmark trajectories as carrier predictions or import Standard Model
    observations, fitted parameters, or rendering software.

Phase 0:
    Controlled numerical benchmark tests are implemented; full Standard Model
    simulation remains explicitly out of scope.
"""

import pytest

from onetheory.core.errors import FailedConvergence
from onetheory.engine.simulate import (
    charged_particle_in_magnetic_field,
    free_complex_scalar,
    free_maxwell_mode,
    geodesic_motion,
    harmonic_oscillator,
    homogeneous_higgs_mode,
    simulate_system,
)
from onetheory.engine.solve import (
    ComponentFieldLagrangian,
    FiniteLagrangian,
    ParameterSet,
    component_field_euler_lagrange,
    euler_lagrange_equations,
    first_order_system_from_lagrangian,
)


def test_harmonic_oscillator_replays_deterministically_and_conserves_energy() -> None:
    system = harmonic_oscillator()
    parameters = {"mass": 1.0, "omega": 1.0}
    first = simulate_system(system, (1.0, 0.0), parameters, 1.0, 0.01)
    second = simulate_system(system, (1.0, 0.0), parameters, 1.0, 0.01)

    assert first == second
    assert first.convergence.converged
    assert first.diagnostics[0].passed


@pytest.mark.parametrize(
    ("system", "initial", "parameters"),
    (
        (free_complex_scalar(), (1.0, 0.0, 0.0, 1.0), {"mass": 1.0}),
        (homogeneous_higgs_mode(), (1.2, 0.0), {"mass": 1.0, "lambda": 1.0, "v": 1.0}),
        (
            charged_particle_in_magnetic_field(),
            (0.0, 0.0, 1.0, 0.0),
            {"mass": 1.0, "charge": 1.0, "magnetic_field": 1.0},
        ),
        (free_maxwell_mode(), (1.0, 0.0), {"omega": 2.0}),
    ),
)
def test_benchmark_systems_produce_converged_trajectories(system, initial, parameters) -> None:
    result = simulate_system(system, initial, parameters, 1.0, 0.01)

    assert len(result.trajectory.states) == 201
    assert result.convergence.converged
    assert result.diagnostics[0].passed


def test_failed_refinement_is_not_silently_accepted() -> None:
    with pytest.raises(FailedConvergence):
        simulate_system(
            harmonic_oscillator(),
            (1.0, 0.0),
            {"mass": 1.0, "omega": 1.0},
            1.0,
            0.1,
            1e-20,
        )


def test_supported_euler_lagrange_system_evolves_with_the_same_engine() -> None:
    def acceleration(
        _: float,
        coordinates: tuple[float, ...],
        __: tuple[float, ...],
        parameters: ParameterSet,
    ) -> tuple[float, ...]:
        return (-(parameters.get("omega") ** 2) * coordinates[0],)

    lagrangian = FiniteLagrangian(("q",), "L=1/2 qdot^2-1/2 omega^2 q^2", acceleration)
    system = first_order_system_from_lagrangian(
        lagrangian,
        lambda state, parameters: (
            (state[1] ** 2 + parameters.get("omega") ** 2 * state[0] ** 2) / 2
        ),
        ("omega",),
    )

    assert euler_lagrange_equations(lagrangian)[0].coordinate == "q"
    assert component_field_euler_lagrange("phi", "L(phi, dphi)").coordinate == "phi"
    assert (
        ComponentFieldLagrangian("phi", "L(phi, dphi)").equation.residual_definition
        == "EL_component(phi)"
    )
    result = simulate_system(system, (1.0, 0.0), {"omega": 1.0}, 1.0, 0.01)
    assert result.convergence.converged


def test_supplied_flat_connection_produces_deterministic_geodesic_motion() -> None:
    def christoffel(_: tuple[float, ...]) -> tuple[tuple[tuple[float, ...], ...], ...]:
        return (((0.0, 0.0), (0.0, 0.0)), ((0.0, 0.0), (0.0, 0.0)))

    system = geodesic_motion(
        2,
        christoffel,
        lambda _positions, velocities: sum(value * value for value in velocities) / 2,
    )
    result = simulate_system(system, (0.0, 0.0, 1.0, 2.0), {}, 1.0, 0.01)

    assert result.trajectory.states[-1].values[:2] == pytest.approx((1.0, 2.0))
    assert result.diagnostics[0].passed
