"""Explicit failure vocabulary for fail-closed computation.

Owns:
    Error categories for missing physical input, invalid normalization, failed
    convergence, inconsistent dimensions, and other explicit computation failures.

Depends on:
    The core package and standard-library exception machinery only.

Must not:
    Hide errors behind defaults, classify scientific evidence, or contain physical
    algorithms and model-specific assumptions.

Phase 0:
    Structural module only; no scientific implementation is provided yet.
"""
