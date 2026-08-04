"""Numerical metric and connection data for the Schoen carrier.

Owns:
    Ricci-flat metric, Hermitian Yang–Mills connection, harmonic representatives, and
    matter metrics after controlled numerical construction and convergence evidence.

Depends on:
    Core precision and units, reusable geometry and linear algebra, general spacetime,
    gauge, matter, and gravity physics, and established Schoen geometry and bundles.

Must not:
    Return guessed metrics, silently normalize states, or use observations to choose
    numerical moduli or geometry.

Phase 0:
    Generic exact section machinery lives in `onetheory.math.sections`; the
    carrier extension cocycle and numerical metric package remain unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass

METRIC_MISSING_CHAIN = (
    "four local non-split extension cocycles e_A in one common Cech basis",
    "848 lawful Cech lifts from the quotient section basis",
    "canonical equivariant 404-section basis at H*=(5,7,1)",
    "global rank-four evaluation certificate for S(x) in Mat(4,404)",
    "converged Ricci-flat metric with residual and refinement evidence",
    "visible HYM connection and residual certificate",
    "harmonic representatives and positive matter/Higgs Gram matrices",
)


@dataclass(frozen=True, slots=True)
class MetricInputStatus:
    """Fail-closed status of the positive-twist metric gateway."""

    first_missing_input: str
    prerequisite_chain: tuple[str, ...]
    positive_twist_dimension_ledger_available: bool
    section_bases_available: bool
    extension_cocycle_available: bool
    cech_lifts_available: bool
    full_section_basis_available: bool
    global_generation_certified: bool
    ricci_flat_metric_available: bool
    visible_hym_available: bool
    matter_higgs_metrics_available: bool


def metric_input_status() -> MetricInputStatus:
    """Return the metric boundary without fabricating a carrier section basis."""

    return MetricInputStatus(
        METRIC_MISSING_CHAIN[0],
        METRIC_MISSING_CHAIN,
        True,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    )
