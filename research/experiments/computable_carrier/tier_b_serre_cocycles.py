"""Construct local punctured-chart Serre cocycle diagnostics.

Owns:
    Exact Laurent transition matrices for the unit local Serre pushouts of
    the five lci monomial types, including inverse, cocycle, and non-boundary
    checks.

Depends on:
    Exact local monomial Serre gates and the reusable Laurent-polynomial
    punctured-chart construction. It does not consume observations or global
    bundle data.

Must not:
    Treat a punctured local cocycle as a global dP9 Cech class, infer an Ext
    group from its existence, hide a line-frame choice, or claim linearization,
    quotient descent, or a physical constituent.

Phase 0:
    Local cocycles are exact for the lci cases; global chart comparison,
    sheaf gluing, equivariance, and quotient descent remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.sheaves import LaurentMatrix

from .serre_atlas import _local_cocycle_nonboundary, _punctured_transitions
from .tier_b_local_serre import LocalMonomialSerreAudit, tier_b_local_monomial_serre_audits
from .tier_b_monomial import InvariantMonomialScheme, tier_b_invariant_monomial_schemes


@dataclass(frozen=True, slots=True)
class TierBLocalCocycleAudit:
    """One exact local punctured-chart cocycle result."""

    scheme: InvariantMonomialScheme
    local_audit: LocalMonomialSerreAudit
    multiplicity: int
    local_to_du: LaurentMatrix | None
    local_to_dv: LaurentMatrix | None
    punctured_cocycle: LaurentMatrix | None
    exact: bool
    nonboundary: bool

    @property
    def available(self) -> bool:
        """Return whether a local unit cocycle was constructed."""

        return self.exact and self.nonboundary and self.local_audit.lci

    def as_record(self) -> dict[str, object]:
        """Serialize local Laurent matrices without a global Cech claim."""

        def matrix_record(matrix: LaurentMatrix | None) -> object:
            if matrix is None:
                return None
            return [
                [
                    [
                        {
                            "exponents": list(exponents),
                            "coefficient": str(coefficient),
                        }
                        for exponents, coefficient in entry.terms
                    ]
                    for entry in row
                ]
                for row in matrix.rows
            ]

        return {
            "scheme": self.scheme.name,
            "multiplicity": self.multiplicity,
            "local_to_du": matrix_record(self.local_to_du),
            "local_to_dv": matrix_record(self.local_to_dv),
            "punctured_cocycle": matrix_record(self.punctured_cocycle),
            "exact": self.exact,
            "nonboundary": self.nonboundary,
            "available": self.available,
            "status": (
                "local punctured-chart cocycle only; global dP9 Cech gluing, "
                "linearization, and quotient descent remain unresolved"
            ),
        }


def tier_b_local_cocycle_audits(
    schemes: tuple[InvariantMonomialScheme, ...] | None = None,
) -> tuple[TierBLocalCocycleAudit, ...]:
    """Construct local unit cocycles for every lci monomial type."""

    selected = tier_b_invariant_monomial_schemes() if schemes is None else schemes
    local_audits = tier_b_local_monomial_serre_audits(selected)
    results = []
    for scheme, local_audit in zip(selected, local_audits, strict=True):
        multiplicity = len(scheme.local_standard_monomials)
        if not local_audit.unit_extension_available:
            results.append(
                TierBLocalCocycleAudit(
                    scheme,
                    local_audit,
                    multiplicity,
                    None,
                    None,
                    None,
                    False,
                    False,
                )
            )
            continue
        local_to_du, local_to_dv, punctured_cocycle, exact = _punctured_transitions(
            multiplicity
        )
        nonboundary, _ = _local_cocycle_nonboundary(multiplicity)
        result = TierBLocalCocycleAudit(
            scheme,
            local_audit,
            multiplicity,
            local_to_du,
            local_to_dv,
            punctured_cocycle,
            exact,
            nonboundary,
        )
        if not result.available:
            raise ValueError("lci local Serre cocycle failed its exact gate")
        results.append(result)
    return tuple(results)


__all__ = ["TierBLocalCocycleAudit", "tier_b_local_cocycle_audits"]
