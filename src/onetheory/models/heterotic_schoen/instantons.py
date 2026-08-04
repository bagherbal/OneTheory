"""Worldsheet instanton and determinant-line data for the carrier.

Owns:
    Rational curves, bundle restrictions, Pfaffians, determinant lines, and Quillen
    normalization directly belonging to the one-Higgs Schoen model.

Depends on:
    Core precision, reusable geometry, polynomials, homological mathematics, general
    quantum and string physics, and established Schoen bundles and geometry.

Must not:
    Treat nonphysical witness quartics as amplitudes, invent determinant phases, or
    claim a physical instanton sum without restriction and line-bundle inputs.

Phase 0:
    The exact conic census remains separate from the missing physical input
    boundary; no Pfaffian or determinant-line implementation is promoted.
"""

from __future__ import annotations

from dataclasses import dataclass

CONIC_PFAFFIAN_MISSING_CHAIN = (
    "explicit embeddings of the two seed conics in frozen Schoen Cox coordinates",
    "visible-bundle constituent resolutions restricted to both seed conics",
    "tensor-structured relative-duality chain maps with certified signs",
    "physical seed Pfaffian quartics and their determinant-line sections",
    "eighteen transported line-valued sections with cocycle consistency",
    "common determinant-line trivialization, hidden factors, B-field, and Quillen data",
)


@dataclass(frozen=True, slots=True)
class ConicPfaffianInputStatus:
    """Fail-closed status of the physical conic Pfaffian reconstruction."""

    first_missing_input: str
    prerequisite_chain: tuple[str, ...]
    physical_seed_maps_available: bool
    physical_seed_quartics_available: bool
    orbit_sections_available: bool
    common_determinant_line_available: bool
    instanton_sum_available: bool


def conic_pfaffian_input_status() -> ConicPfaffianInputStatus:
    """Return the exact boundary before physical seed-map construction."""

    return ConicPfaffianInputStatus(
        CONIC_PFAFFIAN_MISSING_CHAIN[0],
        CONIC_PFAFFIAN_MISSING_CHAIN,
        False,
        False,
        False,
        False,
        False,
    )
