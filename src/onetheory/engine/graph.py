"""Direct fail-closed computational dependency graphs.

Owns:
    Immutable graph nodes, direct prerequisite edges, deterministic dependency
    order, cycle detection, and unresolved prerequisite-chain reporting.

Depends on:
    `onetheory.core.errors` only; the engine remains generic and does not import
    concrete models, reality, verification, research, or observations.

Must not:
    Create speculative bridges, infer absent nodes, import model-specific physics,
    or replace a missing prerequisite with a fallback result.

Phase 0:
    Exact dependency graph execution support is implemented for established slices;
    numerical and simulation consumers remain separate engine concerns.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from onetheory.core.errors import InvalidDependency, MissingPhysicalInput

Evaluator = Callable[[Mapping[str, object]], object]


@dataclass(frozen=True, slots=True)
class GraphNode:
    """An immutable node with named direct prerequisites and an evaluator."""

    name: str
    prerequisites: tuple[str, ...]
    evaluator: Evaluator

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("graph nodes require nonempty names")
        if any(not dependency.strip() for dependency in self.prerequisites):
            raise ValueError("graph prerequisites require nonempty names")
        if self.name in self.prerequisites:
            raise InvalidDependency("a graph node cannot depend directly on itself")


@dataclass(frozen=True, slots=True, init=False)
class ComputationGraph:
    """An immutable named graph with deterministic prerequisite traversal."""

    nodes: tuple[GraphNode, ...]
    _index: tuple[tuple[str, GraphNode], ...]

    def __init__(self, nodes: Iterable[GraphNode] = ()) -> None:
        values = tuple(nodes)
        if len({node.name for node in values}) != len(values):
            raise InvalidDependency("graph node names must be unique")
        index = tuple(sorted(((node.name, node) for node in values), key=lambda item: item[0]))
        object.__setattr__(self, "nodes", values)
        object.__setattr__(self, "_index", index)
        self._validate_cycles()

    def node(self, name: str) -> GraphNode:
        """Return one declared node or raise an explicit key error."""

        for candidate, node in self._index:
            if candidate == name:
                return node
        raise KeyError(name)

    def with_node(self, node: GraphNode) -> ComputationGraph:
        """Return a new graph containing one additional direct node."""

        if any(existing.name == node.name for existing in self.nodes):
            raise InvalidDependency(f"graph node {node.name!r} already exists")
        return ComputationGraph((*self.nodes, node))

    def dependency_chain(self, target: str, available: Mapping[str, object]) -> tuple[str, ...]:
        """Return the first unresolved chain from target to an unavailable input."""

        visiting: set[str] = set()

        def visit(name: str) -> tuple[str, ...]:
            if name in available:
                return ()
            try:
                node = self.node(name)
            except KeyError:
                return (name,)
            if name in visiting:
                raise InvalidDependency(f"cycle encountered while resolving {name!r}")
            visiting.add(name)
            for prerequisite in node.prerequisites:
                chain = visit(prerequisite)
                if chain:
                    visiting.remove(name)
                    return (name, *chain)
            visiting.remove(name)
            return ()

        return visit(target)

    def require_dependencies(self, target: str, available: Mapping[str, object]) -> None:
        """Raise a missing-input error when target cannot be reached exactly."""

        chain = self.dependency_chain(target, available)
        if chain:
            raise MissingPhysicalInput(chain[0], chain[1:])

    def execution_order(
        self, target: str, available: Mapping[str, object]
    ) -> tuple[GraphNode, ...]:
        """Return deterministic topological order for one target."""

        self.require_dependencies(target, available)
        visited: set[str] = set()
        ordered: list[GraphNode] = []

        def visit(name: str) -> None:
            if name in available or name in visited:
                return
            node = self.node(name)
            for prerequisite in node.prerequisites:
                visit(prerequisite)
            visited.add(name)
            ordered.append(node)

        visit(target)
        return tuple(ordered)

    def _validate_cycles(self) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(name: str) -> None:
            if name not in {candidate for candidate, _ in self._index}:
                return
            if name in visiting:
                raise InvalidDependency(f"computation graph contains a cycle at {name!r}")
            if name in visited:
                return
            visiting.add(name)
            for prerequisite in self.node(name).prerequisites:
                visit(prerequisite)
            visiting.remove(name)
            visited.add(name)

        for name, _ in self._index:
            visit(name)
