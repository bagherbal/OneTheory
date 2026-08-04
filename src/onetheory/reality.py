"""Composition root for the established one-Higgs Schoen carrier state.

Owns:
    Direct assembly of the Standard Model metadata, published Schoen geometry,
    visible carrier, holomorphic flavor theorem, and exact topological checks into
    one immutable physical state.

Depends on:
    Concrete model modules and generic engine graph, solve, and state machinery;
    it does not import verification, research, observations, or source documents.

Must not:
    Contain original mathematics or physics algorithms, invent unresolved metrics,
    instantons, hidden bundles, vacua, physical Yukawas, or low-energy predictions,
    or report complete reality while prerequisites remain open.

Phase 0:
    The first established executable reality slice is assembled; unresolved
    downstream physical outputs fail explicitly through MissingPhysicalInput.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import NoReturn, cast

from onetheory.core.errors import MissingPhysicalInput
from onetheory.engine.graph import ComputationGraph, GraphNode
from onetheory.engine.solve import solve_exact
from onetheory.engine.state import PhysicalState, StateEntry
from onetheory.models.heterotic_schoen.consistency import topological_consistency
from onetheory.models.heterotic_schoen.flavor import tree_level_flavor
from onetheory.models.heterotic_schoen.geometry import SchoenGeometry, schoen_geometry
from onetheory.models.heterotic_schoen.visible import ObservableBundle, visible_bundle
from onetheory.models.standard_model import StandardModel, standard_model


def _geometry(_: Mapping[str, object]) -> SchoenGeometry:
    return schoen_geometry()


def _standard_model(_: Mapping[str, object]) -> StandardModel:
    return standard_model()


def _visible(values: Mapping[str, object]) -> ObservableBundle:
    return visible_bundle(cast(SchoenGeometry, values["geometry"]))


def _flavor(_: Mapping[str, object]) -> object:
    return tree_level_flavor()


def _topology(values: Mapping[str, object]) -> object:
    return topological_consistency(cast(SchoenGeometry, values["geometry"]))


def _assemble(values: Mapping[str, object]) -> tuple[StateEntry, ...]:
    return (
        StateEntry("standard_model", values["standard_model"]),
        StateEntry("geometry", values["geometry"]),
        StateEntry("visible_bundle", values["visible_bundle"]),
        StateEntry("tree_level_flavor", values["tree_level_flavor"]),
        StateEntry("topological_consistency", values["topological_consistency"]),
    )


def _reality_graph() -> ComputationGraph:
    """Build the direct exact graph for the established carrier slice."""

    return ComputationGraph((
        GraphNode("standard_model", (), _standard_model),
        GraphNode("geometry", (), _geometry),
        GraphNode("visible_bundle", ("geometry",), _visible),
        GraphNode("tree_level_flavor", (), _flavor),
        GraphNode("topological_consistency", ("geometry",), _topology),
        GraphNode(
            "established_carrier_state",
            ("standard_model", "geometry", "visible_bundle", "tree_level_flavor",
             "topological_consistency"),
            _assemble,
        ),
    ))


UNRESOLVED_REALITY_OUTPUTS = (
    "metrics",
    "instanton amplitudes",
    "hidden bundle",
    "vacuum",
    "physical Yukawa matrices",
    "low-energy predictions",
)


def assemble_reality() -> PhysicalState:
    """Assemble only the established carrier state from the exact graph."""

    evaluation = solve_exact(_reality_graph(), "established_carrier_state", {})
    entries = cast(tuple[StateEntry, ...], evaluation.value)
    return PhysicalState(
        "published one-Higgs heterotic Schoen carrier",
        entries,
        UNRESOLVED_REALITY_OUTPUTS,
        True,
    )


def established_carrier_state() -> PhysicalState:
    """Return the immutable established reality slice."""

    return assemble_reality()


def _missing_output(output: str, chain: tuple[str, ...]) -> NoReturn:
    raise MissingPhysicalInput(output, chain)


def request_metrics() -> NoReturn:
    """Reject unresolved metric requests explicitly."""

    _missing_output("metrics", ("Ricci-flat metric", "HYM connection", "matter metrics"))


def request_physical_yukawas() -> NoReturn:
    """Reject physical Yukawa requests before canonical normalization exists."""

    _missing_output(
        "physical Yukawa matrices",
        ("normalized Yukawa matrices", "matter metrics", "stabilized common vacuum"),
    )


def request_instanton_amplitudes() -> NoReturn:
    """Reject instanton requests before Pfaffians and determinant lines exist."""

    _missing_output(
        "instanton amplitudes",
        ("bundle restrictions", "Pfaffians", "Quillen normalization"),
    )


def request_hidden_bundle() -> NoReturn:
    """Reject hidden-bundle requests because only its Chern target is established."""

    _missing_output(
        "hidden bundle", ("required hidden topological class", "stable equivariant bundle")
    )


def request_vacuum() -> NoReturn:
    """Reject vacuum requests before a controlled stabilization exists."""

    _missing_output("vacuum", ("carrier superpotential", "stabilized moduli", "controlled vacuum"))


def request_low_energy_predictions() -> NoReturn:
    """Reject low-energy predictions until all upstream physical inputs exist."""

    _missing_output(
        "low-energy predictions",
        ("physical Yukawa matrices", "vacuum", "thresholds", "running"),
    )
