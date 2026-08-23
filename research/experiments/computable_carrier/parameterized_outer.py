"""Represent exact parameter-linear full-Cech outer cochains.

Owns:
    Immutable sparse cochains over named Eisenstein polynomial parameters and
    exact specialization back to ordinary full-Cech cochains.

Depends on:
    Exact polynomial arithmetic and the reusable sparse outer-Cech basis.

Must not:
    Choose parameter values, attach a physical carrier interpretation, infer
    local freeness, or decide a non-split or stability locus.

Phase 0:
    Research-only generic parameterized outer-cochain machinery.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial

from .schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)


def _constant(polynomial: Polynomial) -> Eisenstein:
    """Extract one exact scalar after complete specialization."""

    if polynomial.variable_count != 0:
        raise ValueError("outer specialization left an unresolved parameter")
    return cast(Eisenstein, polynomial.coefficient(()))


@dataclass(frozen=True, slots=True)
class ParameterizedOuterCechCochain:
    """An immutable full-Cech cochain with named linear coefficients."""

    parameters: tuple[str, ...]
    terms: tuple[tuple[OuterCechBasis, Polynomial], ...]

    def __init__(
        self,
        parameters: tuple[str, ...],
        terms: tuple[tuple[OuterCechBasis, Polynomial], ...] = (),
    ) -> None:
        if not parameters or len(set(parameters)) != len(parameters):
            raise ValueError("outer parameters must be nonempty and unique")
        if any(not parameter.isidentifier() for parameter in parameters):
            raise ValueError("outer parameter names must be identifiers")
        values: dict[OuterCechBasis, Polynomial] = {}
        for basis, coefficient in terms:
            if coefficient.variable_count != len(parameters):
                raise ValueError(
                    "outer coefficient ring does not match its parameter basis"
                )
            if coefficient.scalar_type is not Eisenstein or coefficient.degree > 1:
                raise ValueError(
                    "outer coefficients must be linear over Q(omega)"
                )
            values[basis] = values.get(
                basis,
                Polynomial.zero(len(parameters), scalar_type=Eisenstein),
            ) + coefficient
        object.__setattr__(self, "parameters", parameters)
        object.__setattr__(
            self,
            "terms",
            tuple(
                (basis, coefficient)
                for basis, coefficient in sorted(values.items())
                if not coefficient.is_zero()
            ),
        )

    def specialize(self, values: tuple[Eisenstein, ...]) -> SparseOuterCechCochain:
        """Evaluate the cochain at one exact affine parameter point."""

        if len(values) != len(self.parameters):
            raise ValueError("outer specialization has the wrong parameter count")
        return SparseOuterCechCochain(
            tuple(
                (basis, _constant(coefficient.substitute(values)))
                for basis, coefficient in self.terms
            )
        )


__all__ = ["ParameterizedOuterCechCochain"]
