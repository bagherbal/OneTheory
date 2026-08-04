"""Exact evaluation of direct dependency graphs.

Owns:
    Deterministic exact graph evaluation, immutable evaluation records, and
    fail-closed propagation of missing prerequisite chains.

Depends on:
    `onetheory.engine.graph` and `onetheory.core.precision`; it remains independent
    of concrete models, reality, verification, research, and observations.

Must not:
    Invent graph nodes, return placeholders, select numerical approximations
    silently, or turn an unresolved physical request into a successful result.

Phase 0:
    Exact graph solving is implemented; controlled numerical solving remains
    unavailable until a real numerical node declares convergence evidence.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.core.precision import PrecisionPolicy
from onetheory.engine.graph import ComputationGraph


@dataclass(frozen=True, slots=True)
class Evaluation:
    """An immutable exact target value with the nodes evaluated to obtain it."""

    target: str
    value: object
    evaluated_nodes: tuple[str, ...]


def solve_exact(
    graph: ComputationGraph,
    target: str,
    inputs: dict[str, object],
) -> Evaluation:
    """Evaluate one graph target using exact policy and no fallback values."""

    PrecisionPolicy.exact().require_exact()
    values: dict[str, object] = dict(inputs)
    ordered = graph.execution_order(target, values)
    for node in ordered:
        arguments = {name: values[name] for name in node.prerequisites}
        values[node.name] = node.evaluator(arguments)
    if target not in values:
        values[target] = graph.node(target).evaluator({
            name: values[name] for name in graph.node(target).prerequisites
        })
    return Evaluation(target, values[target], tuple(node.name for node in ordered))
