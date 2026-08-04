"""Direct computational dependency graph machinery.

Owns:
    Graph nodes, direct prerequisite edges, unresolved prerequisite chains, and graph
    validation for computations whose physical inputs are explicitly available.

Depends on:
    Core, reusable mathematics, and general physics; it is not a model adapter.

Must not:
    Connect mathematically unconnected theories, infer missing nodes, or import
    concrete models, research, reality, or verification.

Phase 0:
    Structural module only; no scientific implementation is provided yet.
"""
