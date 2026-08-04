"""Test fail-closed computation policy and explicit core errors.

Owns:
    Exact-input admission, declared precision, convergence failure, and missing
    physical prerequisite behavior.

Depends on:
    `onetheory.core.errors`, `onetheory.core.precision`, pytest, and the standard
    library’s exact Fraction type.

Must not:
    Test physical models, observations, numerical solvers, or scientific claims.

Phase 0:
    Core policy tests only; no physical implementation is provided here.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from onetheory.core.errors import (
    FailedConvergence,
    MissingPhysicalInput,
    NonExactInput,
)
from onetheory.core.precision import ComputationMode, PrecisionPolicy, require_exact_input


def test_exact_policy_rejects_approximation_and_accepts_exact_inputs() -> None:
    policy = PrecisionPolicy.exact()

    assert policy.mode is ComputationMode.EXACT
    assert policy.is_exact
    assert require_exact_input(3) == 3
    assert require_exact_input(Fraction(2, 3)) == Fraction(2, 3)

    with pytest.raises(NonExactInput):
        require_exact_input(0.5)
    with pytest.raises(NonExactInput):
        PrecisionPolicy.numerical(40, Fraction(1, 10**20), Fraction(1, 10**20)).require_exact()


def test_numerical_policy_requires_explicit_convergence() -> None:
    policy = PrecisionPolicy.numerical(50, Fraction(1, 10**20), Fraction(1, 10**20))

    policy.require_converged(True)
    with pytest.raises(FailedConvergence):
        policy.require_converged(False)


def test_missing_input_preserves_the_unresolved_prerequisite_chain() -> None:
    error = MissingPhysicalInput(
        "physical CKM matrix",
        ("normalized Yukawa matrices", "matter metrics", "stabilized common vacuum"),
    )

    assert error.chain == (
        "physical CKM matrix",
        "normalized Yukawa matrices",
        "matter metrics",
        "stabilized common vacuum",
    )
    assert "matter metrics" in str(error)
