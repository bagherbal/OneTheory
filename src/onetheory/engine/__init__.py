"""Generic execution machinery for direct physical dependencies.

Owns:
    The namespace for dependency graphs, immutable states, exact or numerical
    evaluation, and simulation trajectory production.

Depends on:
    Core, reusable mathematics, and general physics; it must not import concrete
    models, reality, research, or verification.

Must not:
    Act as a bridge between unconnected theories, invent missing graph nodes, or
    contain a second simplified physics implementation.

Phase 0:
    Structural module only; no scientific implementation is provided yet.
"""
