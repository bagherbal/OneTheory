"""Dimensional language for physical quantities.

Owns:
    Physical dimensions, units, conversion policy, and the rules that identify
    dimensionally inconsistent expressions.

Depends on:
    The core package and standard-library primitives; it does not require physics
    models or selected carrier data.

Must not:
    Encode a physical law, choose normalization conventions silently, store
    observations, or register scientific certificates.

Phase 0:
    Structural module only; no scientific implementation is provided yet.
"""
