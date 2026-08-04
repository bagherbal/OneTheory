"""Scientific gate states and fail-closed decision vocabulary.

Owns:
    Explicit accepted, failed, unresolved, missing-input, and killed conditions with
    declared scope and consequences for downstream computation.

Depends on:
    Evidence and certificate records and any production object being inspected; it is
    not a dependency of production physics.

Must not:
    Infer a bridge, suppress an unresolved prerequisite, or change a scientific result
    merely to satisfy an execution path.

Phase 0:
    Structural module only; no scientific implementation is provided yet.
"""
