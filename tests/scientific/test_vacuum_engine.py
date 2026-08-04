"""Test exact vacuum expressions, source scopes, and generic solver contracts.

Owns:
    Exact derivative, Kähler, charge-space, source-availability, solver, stability,
    control-ledger, and Schoen fail-closed boundary tests.

Depends on:
    Generic production vacuum structures and the carrier boundary only; synthetic
    values in this file never enter the assembled Schoen reality state.

Must not:
    Treat benchmark roots as physical carrier results or use observations to select
    a source, geometry, or vacuum.

Phase 0:
    Scientific tests are now promoted for the generic symbolic vacuum layer; the
    carrier-specific vacuum remains unresolved by design.
"""

from __future__ import annotations

from math import exp

import pytest

from onetheory.core.errors import IncompatibleConvention, MissingPhysicalInput
from onetheory.math.numbers import Rational
from onetheory.models.heterotic_schoen.vacuum import (
    SCHOEN_VACUUM_MISSING_CHAIN,
    request_schoen_vacuum,
    schoen_vacuum_boundary,
)
from onetheory.physics.vacuum import (
    ControlCriterion,
    ControlLedger,
    ControlStatus,
    DomainCondition,
    GauginoCondensate,
    KaehlerPotential,
    ModuliPoint,
    ParameterProvenance,
    RacetrackSuperpotential,
    SymbolicExpression,
    VacuumEquationSystem,
    ValidityDomain,
    canonical_real_hessian,
    classify_critical_point,
    four_term_sign_obstruction,
    solve_supersymmetric_vacuum,
    suppression_ratio,
    universal_affine_hyperplane_no_go,
)


def _context() -> tuple[ModuliPoint, ParameterProvenance]:
    return ModuliPoint("benchmark"), ParameterProvenance("test", "exact synthetic input")


def test_exact_complex_derivatives_and_kahler_covariance() -> None:
    point, provenance = _context()
    z = SymbolicExpression.variable("z")
    potential = KaehlerPotential.from_symbolic(z * z.conjugate(), ("z",), point, provenance)
    superpotential = (z - 1) ** 2

    assert potential.kahler_derivative("z").evaluate({"z": 2}) == 2
    assert potential.metric().entries[0][0].evaluate({"z": 2}) == 1
    transformed_k, transformed_w = potential.kahler_transform(z / 3, superpotential)
    assert transformed_k.derivative("z").evaluate({"z": 2}) == pytest.approx(2 + 1 / 3)
    assert transformed_w.evaluate({"z": 2}) == pytest.approx(exp(-2 / 3))


def test_kahler_metric_positivity_and_singular_boundary() -> None:
    point, provenance = _context()
    z = SymbolicExpression.variable("z")
    positive = KaehlerPotential.from_symbolic(z * z.conjugate(), ("z",), point, provenance)
    negative = KaehlerPotential.from_symbolic(-(z * z.conjugate()), ("z",), point, provenance)

    assert positive.metric().positive_definite({"z": 1})
    with pytest.raises(ValueError, match="non-positive"):
        negative.metric().inverse_at({"z": 1})


def test_charge_certificates_recompute_scoped_conclusions() -> None:
    assert four_term_sign_obstruction().status == "KILLED"
    assert universal_affine_hyperplane_no_go().status == "KILLED"
    assert universal_affine_hyperplane_no_go().charge_classification is not None


def test_missing_determinant_and_beta_keep_condensates_unavailable() -> None:
    point, provenance = _context()
    z = SymbolicExpression.variable("z")
    missing = GauginoCondensate(
        "hidden",
        SymbolicExpression.constant(1),
        gauge_kinetic_function=z,
        moduli_point=point,
        provenance=provenance,
    )
    assert not missing.available
    assert "determinant-line section" in missing.unavailable_reasons
    assert "hidden beta-function coefficient" in missing.unavailable_reasons


def test_racetrack_requires_one_function_unequal_exponents_and_compatible_scope() -> None:
    point, provenance = _context()
    z = SymbolicExpression.variable("z")
    first = GauginoCondensate(
        "first",
        SymbolicExpression.constant(1),
        gauge_kinetic_function=z,
        determinant_line_section="det-first",
        beta_function=3,
        moduli_point=point,
        provenance=provenance,
    )
    second = GauginoCondensate(
        "second",
        SymbolicExpression.constant(2),
        gauge_kinetic_function=z,
        determinant_line_section="det-second",
        beta_function=4,
        moduli_point=point,
        provenance=provenance,
    )
    track = RacetrackSuperpotential.from_terms(
        first, second, z, 3, 4, "principal", "zero", ValidityDomain()
    )
    assert track.expression.evaluate({"z": 1}).real == pytest.approx(exp(-3) + 2 * exp(-4))
    assert track.exponent_one != track.exponent_two

    other_point = ModuliPoint("other")
    mixed = GauginoCondensate(
        "mixed",
        SymbolicExpression.constant(3),
        gauge_kinetic_function=z,
        determinant_line_section="det-mixed",
        beta_function=5,
        moduli_point=other_point,
        provenance=provenance,
    )
    with pytest.raises(IncompatibleConvention):
        RacetrackSuperpotential.from_terms(
            first, mixed, z, 3, 4, "principal", "zero", ValidityDomain()
        )


def test_deterministic_solver_refines_and_deduplicates_roots() -> None:
    point, provenance = _context()
    z = SymbolicExpression.variable("z")
    potential = KaehlerPotential.from_symbolic(
        SymbolicExpression.constant(0), ("z",), point, provenance
    )
    system = VacuumEquationSystem(potential, (z - 1) ** 2, ("z",))
    report = solve_supersymmetric_vacuum(system, ({"z": 0}, {"z": 2}, {"z": 0}), (30, 60), 1e-12)
    replay = solve_supersymmetric_vacuum(system, ({"z": 0}, {"z": 2}, {"z": 0}), (30, 60), 1e-12)
    assert report == replay
    assert len(report.candidates) == 1
    assert report.duplicate_count == 2
    assert report.candidates[0].residual_norm <= 1e-12


def test_canonical_hessian_bf_and_control_ledger() -> None:
    x = SymbolicExpression.variable("x")
    hessian = canonical_real_hessian(x**2, ("x",), ((2.0,),), {"x": 0})
    assert hessian == ((1.0,),)
    critical = classify_critical_point(x**2, ("x",), ((1.0,),), {"x": 0}, True)
    assert critical.metastable
    assert critical.masses_squared == (2.0,)
    with pytest.raises(ValueError, match="positive kinetic"):
        canonical_real_hessian(x**2, ("x",), ((-1.0,),), {"x": 0})

    criterion = ControlCriterion(
        "large volume",
        ControlStatus.CONTROLLED,
        100.0,
        10.0,
        ParameterProvenance("t", "exact"),
        "bound passed",
    )
    assert ControlLedger.from_criteria((criterion,)).controlled
    assert suppression_ratio(1, 100) == Rational(1, 100)


def test_domain_conditions_and_schoen_boundary_fail_closed() -> None:
    z = SymbolicExpression.variable("z")
    condition = DomainCondition(z.real_part() - 1, ">", 0)
    assert condition.holds({"z": 2})
    boundary = schoen_vacuum_boundary()
    assert not boundary.complete
    assert boundary.earliest_missing == SCHOEN_VACUUM_MISSING_CHAIN[0]
    with pytest.raises(MissingPhysicalInput) as error:
        request_schoen_vacuum()
    assert error.value.chain == SCHOEN_VACUUM_MISSING_CHAIN
