"""Exact scalar systems for reusable algebraic computation.

Owns:
    Rational arithmetic, algebraic coefficient fields such as Q(ω), and exact scalar
    representations with declared equality and normalization behavior.

Depends on:
    Core precision and error policy and standard-library mathematics; it is
    independent of physical interpretation.

Must not:
    Turn coefficients into physical parameters, fit data, or silently replace exact
    input with floating-point approximations.

Phase 0:
    Structural module only; no scientific implementation is provided yet.
"""
