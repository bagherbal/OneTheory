"""Exact-versus-numerical computation policy.

Owns:
    Immutable computation modes, declared precision and tolerance policy, exact
    input admission, and explicit convergence requirements for numerical work.

Depends on:
    Python’s `fractions` and `enum` modules plus `core.errors`; it does not import
    reusable mathematics, physics, models, engine, research, or verification.

Must not:
    Approximate exact inputs silently, choose tolerances implicitly, provide
    fallback values, or decide whether a physical claim is scientifically valid.

Phase 0:
    Exact and controlled numerical policy primitives are implemented; no numerical
    solver or physical calculation is supplied here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction

from onetheory.core.errors import FailedConvergence, NonExactInput


class ComputationMode(StrEnum):
    """The two explicitly declared evaluation modes."""

    EXACT = "exact"
    NUMERICAL = "numerical"


@dataclass(frozen=True, slots=True)
class PrecisionPolicy:
    """Declared precision and tolerance policy for one computation."""

    mode: ComputationMode
    digits: int
    absolute_tolerance: Fraction
    relative_tolerance: Fraction

    def __post_init__(self) -> None:
        if isinstance(self.digits, bool) or not isinstance(self.digits, int) or self.digits < 0:
            raise ValueError("precision digits must be a nonnegative integer")
        if self.absolute_tolerance < 0 or self.relative_tolerance < 0:
            raise ValueError("precision tolerances must be nonnegative")
        if self.mode is ComputationMode.EXACT and (
            self.digits != 0
            or self.absolute_tolerance != 0
            or self.relative_tolerance != 0
        ):
            raise ValueError("exact mode must have zero tolerances and zero numerical digits")
        if self.mode is ComputationMode.NUMERICAL and self.digits <= 0:
            raise ValueError("numerical mode requires positive precision digits")

    @classmethod
    def exact(cls) -> PrecisionPolicy:
        """Return the only policy that admits exact symbolic evaluation."""

        return cls(ComputationMode.EXACT, 0, Fraction(0), Fraction(0))

    @classmethod
    def numerical(
        cls,
        digits: int,
        absolute_tolerance: Fraction,
        relative_tolerance: Fraction,
    ) -> PrecisionPolicy:
        """Construct a numerical policy with explicit precision and tolerances."""

        return cls(
            ComputationMode.NUMERICAL,
            digits,
            Fraction(absolute_tolerance),
            Fraction(relative_tolerance),
        )

    @property
    def is_exact(self) -> bool:
        """Return whether this policy permits exact operations only."""

        return self.mode is ComputationMode.EXACT

    def require_exact(self) -> None:
        """Reject use of a numerical policy in an exact calculation."""

        if not self.is_exact:
            raise NonExactInput("an exact calculation requires PrecisionPolicy.exact()")

    def require_converged(self, converged: bool) -> None:
        """Require a true convergence flag before accepting numerical output."""

        if self.is_exact:
            return
        if not converged:
            raise FailedConvergence("numerical output has no convergence certificate")


def require_exact_input[ExactValue](value: ExactValue) -> ExactValue:
    """Admit immutable integer or rational-like exact inputs, rejecting floats."""

    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise NonExactInput("exact input requires an integer or Fraction value")
    return value
