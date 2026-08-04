"""Immutable physical and simulation state containers.

Owns:
    Structured state records, validity boundaries, declared inputs, and the immutable
    state representation shared by scientific evaluation and future simulation.

Depends on:
    Core policy, reusable mathematics, and general physics; it remains generic and
    model-independent.

Must not:
    Store sample universes, supply default physical values, or create an alternate
    simulation-only representation of laws or observables.

Phase 0:
    Structural module only; no scientific implementation is provided yet.
"""
