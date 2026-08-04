# `engine`

## Purpose

Engine contains generic execution machinery for direct physical dependencies and future deterministic simulation.

## Belongs here

`graph.py` will record direct dependencies and unresolved prerequisite chains. `state.py` will define immutable physical and simulation state. `solve.py` will evaluate exact and controlled numerical nodes. `simulate.py` will evolve valid states into structured trajectories for external animation consumers.

## Does not belong here

Model adapters, speculative bridges, fabricated missing nodes, rendering dependencies, CLI behavior, or a simplified second physics implementation do not belong here.

## Dependencies

Engine may depend on core, math, physics, and its own generic machinery. It must not import models, reality, verification, research, or observations.

## Promotion condition

Research may be promoted only when every direct prerequisite is defined and certified, state validity and failure behavior are explicit, exact or numerical evidence is recorded, and integration tests preserve fail-closed execution.
