"""Exercise context-safe low-energy algorithms with synthetic mathematical inputs.

Owns:
    Regression checks for context admission, canonical normalization, flavor and
    neutrino algebra, matching, running, uncertainty propagation, and prediction
    leakage protection.

Depends on:
    Generic production algorithms only; no observations or carrier output is used.

Must not:
    Treat synthetic matrices as OneTheory physical predictions or weaken the
    fail-closed Schoen composition boundary.

Phase 0:
    Scientific algorithms are tested with explicit synthetic inputs; carrier
    promotion remains unresolved.
"""

from math import isclose

import pytest

from onetheory.core.errors import IncompatibleConvention, MissingPhysicalInput
from onetheory.math.numbers import Rational
from onetheory.physics.observables import (
    ComplexMatrix,
    CovarianceMatrix,
    DataManifest,
    DiracNeutrinoMatrix,
    EffectiveTheory,
    FalsificationScope,
    HermitianMetric,
    HolomorphicYukawa,
    MajoranaMatrix,
    MatchingCondition,
    MonteCarloConfig,
    OperatorBasis,
    PhysicalEvaluationContext,
    PhysicalMatrix,
    PredictionRecord,
    PredictionRegistry,
    PredictionRole,
    RGETheory,
    RGState,
    SelectionRecord,
    UncertaintyComponent,
    UncertainValue,
    canonicalize_yukawa,
    compare_with_data,
    falsification_report,
    jarlskog_invariant,
    match_threshold,
    mixing_matrix,
    monte_carlo_propagate,
    principal_uncertainty_directions,
    run_rge,
    singular_value_decomposition,
    type_i_seesaw,
)
from onetheory.reality import request_held_out_prediction


def context(
    *,
    scheme: str = "MSbar",
    scale: int = 100,
    vacuum: str = "vacuum-a",
) -> PhysicalEvaluationContext:
    """Create one explicit test context without introducing model data."""

    return PhysicalEvaluationContext(
        "synthetic-compactification",
        "geometry-digest",
        "bundle-digest",
        vacuum,
        {"t": Rational(1)},
        scheme,
        Rational(scale),
        "test-units",
        40,
        1e-10,
        "tree",
        ("synthetic test input",),
    )


def physical(
    rows: tuple[tuple[object, ...], ...],
    current: PhysicalEvaluationContext | None = None,
    basis: str = "generation",
) -> PhysicalMatrix:
    """Bind a small synthetic matrix to one explicit context and basis."""

    return PhysicalMatrix(
        ComplexMatrix(rows), current or context(), basis, ("synthetic test matrix",)
    )


def test_context_rejects_scheme_vacuum_and_scale_mixing() -> None:
    """Context checks reject all untransported physical mixing."""

    with pytest.raises(IncompatibleConvention):
        context().assert_compatible(context(scheme="on-shell"))
    with pytest.raises(IncompatibleConvention):
        context().assert_compatible(context(vacuum="vacuum-b"))
    with pytest.raises(IncompatibleConvention):
        context().assert_compatible(context(scale=200))
    context().assert_compatible(context(scale=200), allow_scale_transport=True)


def test_canonical_normalization_preserves_rank_and_has_positive_root() -> None:
    """Positive Hermitian normalization is invertible and rank preserving."""

    current = context()
    metric = HermitianMetric(
        ((2, 1), (1, 2)), current, "left", "left metric", ("synthetic metric",)
    )
    assert metric.positive_definite
    root = metric.inverse_sqrt()
    identity = root @ metric.matrix @ root
    assert identity.is_close(ComplexMatrix.identity(2), 1e-8)
    holomorphic = HolomorphicYukawa(
        physical(((1, 0), (0, 0)), current, "left"), "left", "right", "higgs"
    )
    right = HermitianMetric(((1, 0), (0, 1)), current, "right", "right metric", ("test",))
    higgs = HermitianMetric(((1,),), current, "higgs", "Higgs metric", ("test",))
    normalized = canonicalize_yukawa(holomorphic, metric, right, higgs)
    assert normalized.rank_preserved
    assert normalized.matrix.rank == holomorphic.matrix.rank


def test_flavor_unitarity_rephasing_invariance_and_degeneracy_guard() -> None:
    """Mixing is unitary, its CP invariant is rephasing-safe, and degeneracy is open."""

    current = context()
    unitary = ComplexMatrix(
        (
            (0.8, 0.0, 0.6),
            (-0.3, 0.5, 0.4),
            (0.3, -0.5, 0.4),
        )
    )
    # The test matrix is intentionally real; this still exercises unitarity and J=0.
    left = physical(unitary.rows, current)
    right = physical(ComplexMatrix.identity(3).rows, current)
    mixed = mixing_matrix(singular_value_decomposition(left), singular_value_decomposition(right))
    assert mixed.unitarity_residual < 1e-8
    phase_rows = ComplexMatrix(((1j, 0, 0), (0, 1, 0), (0, 0, -1)))
    phase_columns = ComplexMatrix(((1, 0, 0), (0, -1j, 0), (0, 0, 1)))
    rephased = phase_rows @ mixed.matrix.matrix @ phase_columns
    assert isclose(
        jarlskog_invariant(mixed.matrix),
        jarlskog_invariant(physical(rephased.rows, current)),
        abs_tol=1e-10,
    )
    degenerate = mixing_matrix(
        singular_value_decomposition(right), singular_value_decomposition(right)
    )
    assert not degenerate.physical


def test_seesaw_requires_symmetric_majorana_data_and_matches_reduced_form() -> None:
    """The seesaw uses explicit symmetric data and reports its Schur complement."""

    current = context()
    dirac = DiracNeutrinoMatrix(physical(((1, 0), (0, 2)), current, "neutrino"))
    majorana = MajoranaMatrix(physical(((5, 1), (1, 4)), current, "neutrino"))
    result = type_i_seesaw(dirac, majorana)
    assert result.light_matrix.matrix.transpose().is_close(result.light_matrix.matrix)
    assert result.reduced_agreement_residual < 1e-12
    with pytest.raises(ValueError):
        MajoranaMatrix(physical(((1, 2), (3, 4)), current, "neutrino"))


def test_matching_requires_ordered_threshold_and_explicit_calculation() -> None:
    """Threshold matching is available only for named fields and explicit maps."""

    ultraviolet_context = context(scale=1000)
    infrared_context = context(scale=10)
    basis = OperatorBasis("test basis", ("O",), "MSbar", ("published test law",))
    ultraviolet = EffectiveTheory("UV", basis, ultraviolet_context, 1, "UV")
    infrared = EffectiveTheory("IR", basis, infrared_context, 1, "IR")
    from onetheory.physics.observables import ThresholdEvent

    event = ThresholdEvent(
        "heavy field threshold",
        ("X",),
        (100,),
        Rational(100),
        context(scale=100),
        lambda values: {"O": values["O"]},
    )
    report = match_threshold(ultraviolet, infrared, event, {"O": 2.0}, 1e-12, 0.0)
    assert report.status == "PASS"
    assert report.condition is not None
    assert isinstance(report.condition, MatchingCondition)


def test_rge_refinement_and_threshold_ordering_are_deterministic() -> None:
    """The piecewise solver records threshold order and refinement evidence."""

    current = context(scale=1000)
    theory = RGETheory(
        "linear test flow",
        ("x",),
        lambda scale, values: {"x": values["x"] / scale},
        1,
        current,
    )
    initial = RGState(1000, (("x", 1.0),), current)
    result = run_rge(theory, initial, 10, 25, 1e-8)
    assert result.converged
    assert isclose(float(complex(result.states[-1].mapping()["x"]).real), 0.01, rel_tol=1e-5)


def test_covariance_is_traceable_and_seeded_sampling_replays() -> None:
    """Correlated covariance and numerical propagation remain reproducible."""

    covariance = CovarianceMatrix(((1.0, 0.5), (0.5, 1.0)), ("input",))
    component = UncertaintyComponent(
        "input", covariance.values, "input", "68%", ("input manifest",)
    )
    assert component.covariance == covariance.values
    directions = principal_uncertainty_directions(covariance)
    assert directions and directions[0].variance >= directions[-1].variance
    first = monte_carlo_propagate(
        lambda values: values,
        (0.0, 0.0),
        covariance,
        MonteCarloConfig(100, 7),
    )
    second = monte_carlo_propagate(
        lambda values: values,
        (0.0, 0.0),
        covariance,
        MonteCarloConfig(100, 7),
    )
    assert first == second


def test_prediction_registry_rejects_leakage_and_scope_is_explicit() -> None:
    """Held-out records reject upstream influence and comparison scope is retained."""

    current = context()
    uncertain = UncertainValue(
        (1.0,), CovarianceMatrix(((0.1,),), ("theory",)), (component("theory"),), current
    )
    manifest = DataManifest("held-out", "digest", "2026-01-01")
    leaked = SelectionRecord("geometry", "branch-a", True, "observed fit")
    with pytest.raises(ValueError):
        PredictionRecord(
            PredictionRole.HELD_OUT_PREDICTION,
            "mass",
            current,
            "model",
            "vacuum",
            (leaked,),
            (),
            manifest,
            uncertain,
            "combined covariance",
            "chi2 <= 3.84",
            ("certificate",),
            "software",
        )
    record = PredictionRecord(
        PredictionRole.HELD_OUT_PREDICTION,
        "mass",
        current,
        "model",
        "vacuum",
        (),
        (),
        manifest,
        uncertain,
        "combined covariance",
        "chi2 <= 3.84",
        ("certificate",),
        "software",
    )
    registry = PredictionRegistry().register(record).freeze()
    comparison = compare_with_data(
        uncertain,
        (2.0,),
        CovarianceMatrix(((0.1,),), ("exp",)),
        1,
        "vacuum",
        ("test",),
    )
    report = falsification_report(comparison, FalsificationScope.VACUUM, ("protocol",))
    assert report.falsifies and report.scope is FalsificationScope.VACUUM
    assert record in registry.held_out()


def component(name: str) -> UncertaintyComponent:
    """Build one minimal traceable uncertainty component."""

    return UncertaintyComponent(name, ((0.1,),), "theory", "68%", ("test",))


def test_reality_remains_fail_closed_for_held_out_predictions() -> None:
    """No prediction state exists while the carrier closure chain is open."""

    with pytest.raises(MissingPhysicalInput, match="held-out low-energy prediction"):
        request_held_out_prediction()
