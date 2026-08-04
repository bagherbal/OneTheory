"""Test exact graph execution and immutable state failure behavior.

Owns:
    Direct dependency order, cycle rejection, unresolved prerequisite chains,
    exact evaluation, and immutable physical state lookup.

Depends on:
    `onetheory.engine.graph`, `solve`, `state`, core errors, and pytest.

Must not:
    Import concrete models, fabricate unresolved values, or test a simulation-only
    physics implementation.

Phase 0:
    Generic execution tests only; no physical model assumptions are encoded here.
"""

from __future__ import annotations

import pytest

from onetheory.core.errors import InvalidDependency, MissingPhysicalInput
from onetheory.engine.graph import ComputationGraph, GraphNode
from onetheory.engine.solve import solve_exact
from onetheory.engine.state import PhysicalState, StateEntry


def test_graph_evaluates_direct_prerequisites_in_deterministic_order() -> None:
    graph = ComputationGraph((
        GraphNode("a", ("x",), lambda values: values["x"] + 1),
        GraphNode("b", ("a",), lambda values: values["a"] * 2),
    ))

    result = solve_exact(graph, "b", {"x": 3})

    assert result.value == 8
    assert result.evaluated_nodes == ("a", "b")


def test_graph_reports_unresolved_prerequisite_chain_without_fallback() -> None:
    graph = ComputationGraph((
        GraphNode("observable", ("normalized",), lambda values: values["normalized"]),
        GraphNode("normalized", ("metric",), lambda values: values["metric"]),
    ))

    with pytest.raises(MissingPhysicalInput) as failure:
        solve_exact(graph, "observable", {})
    assert failure.value.chain == ("observable", "normalized", "metric")


def test_graph_rejects_cycles_and_state_rejects_unresolved_outputs() -> None:
    with pytest.raises(InvalidDependency):
        ComputationGraph((
            GraphNode("a", ("b",), lambda values: values["b"]),
            GraphNode("b", ("a",), lambda values: values["a"]),
        ))

    state = PhysicalState(
        "carrier",
        (StateEntry("geometry", "established"),),
        ("physical CKM matrix",),
        True,
        {"physical CKM matrix": ("matter metrics", "stabilized common vacuum")},
    )
    assert state.value("geometry") == "established"
    with pytest.raises(MissingPhysicalInput) as failure:
        state.require("physical CKM matrix")
    assert failure.value.chain == (
        "physical CKM matrix",
        "matter metrics",
        "stabilized common vacuum",
    )
