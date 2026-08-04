"""Fail-closed errors for exact scientific execution.

Owns:
    Explicit exception types for missing physical inputs, incompatible
    conventions, invalid normalizations, non-exact data, failed convergence,
    dimensional inconsistencies, and invalid dependency requests.

Depends on:
    Python exception and immutable tuple primitives only; this lowest layer does
    not import mathematics, physics, models, engine, research, or verification.

Must not:
    Supply fallback values, classify evidence, hide unresolved prerequisites, or
    contain physical algorithms or model-specific constants.

Phase 0:
    Fail-closed errors are implemented for the executable reality slice; other
    core policy remains independent of physical model interpretation.
"""

from __future__ import annotations

from collections.abc import Iterable


class OneTheoryError(Exception):
    """Base class for explicit OneTheory computation failures."""


class MissingPhysicalInput(OneTheoryError):
    """Signal that a requested result lacks a required physical prerequisite."""

    def __init__(self, prerequisite: str, chain: Iterable[str] = ()) -> None:
        if not isinstance(prerequisite, str) or not prerequisite.strip():
            raise ValueError("a missing prerequisite requires a nonempty name")
        normalized_chain = tuple(chain)
        if any(not isinstance(item, str) or not item.strip() for item in normalized_chain):
            raise ValueError("missing-input chains require nonempty names")
        self.prerequisite = prerequisite
        self.chain = (prerequisite, *normalized_chain)
        super().__init__(self.render())

    def render(self) -> str:
        """Render the unresolved prerequisite chain as a compact tree."""

        if len(self.chain) == 1:
            return f"missing physical input: {self.chain[0]}"
        lines = [f"missing physical input: {self.chain[0]}"]
        for index, item in enumerate(self.chain[1:]):
            lines.append(f"{'  ' * index}└── {item}")
        return "\n".join(lines)


class IncompatibleConvention(OneTheoryError):
    """Signal that exact objects use different declared conventions."""


class InvalidNormalization(OneTheoryError):
    """Signal that a quotient, cover, or other normalization is invalid."""


class NonExactInput(OneTheoryError):
    """Signal that an approximate value entered an exact computation."""


class FailedConvergence(OneTheoryError):
    """Signal that a numerical computation has no declared convergence result."""


class InconsistentDimensions(OneTheoryError):
    """Signal that a dimensional operation has incompatible physical dimensions."""


class InvalidDependency(OneTheoryError):
    """Signal that an execution request violates a direct dependency contract."""


class UnresolvedComputation(OneTheoryError):
    """Signal that a graph node is known but cannot yet be evaluated."""
