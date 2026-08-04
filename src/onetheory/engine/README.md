# `engine`

## Purpose

Engine contains generic execution machinery for direct physical dependencies and future deterministic simulation.

## Belongs here

`graph.py` records direct dependencies and unresolved prerequisite chains. `state.py` defines immutable physical and simulation state entries with explicit open outputs. `solve.py` evaluates exact graph nodes and validates parameterized law systems. `simulate.py` evolves benchmark law systems with deterministic refinement and conservation diagnostics into structured trajectories for external animation consumers.

## Does not belong here

Model adapters, speculative bridges, fabricated missing nodes, rendering dependencies, CLI behavior, or a simplified second physics implementation do not belong here.

## Dependencies

Engine may depend on core, math, physics, and its own generic machinery. It must not import models, reality, verification, research, or observations. The established carrier is injected by the composition root through direct graph evaluators.

## Promotion condition

Research may be promoted only when every direct prerequisite is defined and certified, state validity and failure behavior are explicit, exact or numerical evidence is recorded, and integration tests preserve fail-closed execution. Benchmark success does not promote carrier or phenomenological results.
