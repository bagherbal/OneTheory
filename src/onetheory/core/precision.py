"""Exact and numerical computation policy for the engine.

Owns:
    The distinction between exact inputs and numerical evaluation, declared
    tolerances, precision escalation, and convergence-policy vocabulary.

Depends on:
    The core package and standard-library primitives; it remains independent of
    physical models and evidence registries.

Must not:
    Approximate exact input without declaration, supply fallback values, or decide
    whether a scientific claim is physically established.

Phase 0:
    Structural module only; no scientific implementation is provided yet.
"""
