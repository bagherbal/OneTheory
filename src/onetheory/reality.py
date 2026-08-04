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
from onetheory.models.heterotic_schoen.flavor import finite_frontier_status, tree_level_flavor
from onetheory.models.heterotic_schoen.geometry import SchoenGeometry, schoen_geometry
from onetheory.models.heterotic_schoen.visible import (
    MixedMaurerCartanBranch,
    ObservableAdmissibility,
    ObservableBundle,
    SplitWallDeformation,
    mixed_maurer_cartan_branch,
    observable_admissibility,
    split_wall_deformation,
    visible_bundle,
)
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


def _split_wall(_: Mapping[str, object]) -> SplitWallDeformation:
    return split_wall_deformation()


def _mixed(values: Mapping[str, object]) -> MixedMaurerCartanBranch:
    return mixed_maurer_cartan_branch(cast(SplitWallDeformation, values["split_wall_deformation"]))


def _admissibility(values: Mapping[str, object]) -> ObservableAdmissibility:
    return observable_admissibility(
        cast(MixedMaurerCartanBranch, values["mixed_deformation_branch"])
    )


def _frontier(_: Mapping[str, object]) -> object:
    return finite_frontier_status()


def _assemble(values: Mapping[str, object]) -> tuple[StateEntry, ...]:
    return (
        StateEntry("standard_model", values["standard_model"]),
        StateEntry("geometry", values["geometry"]),
        StateEntry("visible_bundle", values["visible_bundle"]),
        StateEntry("tree_level_flavor", values["tree_level_flavor"]),
        StateEntry("topological_consistency", values["topological_consistency"]),
        StateEntry("split_wall_deformation", values["split_wall_deformation"]),
        StateEntry("mixed_deformation_branch", values["mixed_deformation_branch"]),
        StateEntry("observable_admissibility", values["observable_admissibility"]),
        StateEntry("finite_flavor_frontier", values["finite_flavor_frontier"]),
    )


def _reality_graph() -> ComputationGraph:
    """Build the direct exact graph for the established carrier slice."""

    return ComputationGraph((
        GraphNode("standard_model", (), _standard_model),
        GraphNode("geometry", (), _geometry),
        GraphNode("visible_bundle", ("geometry",), _visible),
        GraphNode("tree_level_flavor", (), _flavor),
        GraphNode("topological_consistency", ("geometry",), _topology),
        GraphNode("split_wall_deformation", (), _split_wall),
        GraphNode("mixed_deformation_branch", ("split_wall_deformation",), _mixed),
        GraphNode("observable_admissibility", ("mixed_deformation_branch",), _admissibility),
        GraphNode(
            "finite_flavor_frontier",
            ("visible_bundle", "tree_level_flavor", "split_wall_deformation"),
            _frontier,
        ),
        GraphNode(
            "established_carrier_state",
            (
                "standard_model",
                "geometry",
                "visible_bundle",
                "tree_level_flavor",
                "topological_consistency",
                "split_wall_deformation",
                "mixed_deformation_branch",
                "observable_admissibility",
                "finite_flavor_frontier",
            ),
            _assemble,
        ),
    ))


UNRESOLVED_REALITY_OUTPUTS = (
    "metrics",
    "instanton amplitudes",
    "hidden bundle",
    "vacuum",
    "physical Yukawa matrices",
    "rank-three holomorphic Yukawa matrix",
    "physical masses",
    "CKM and CP observables",
    "low-energy predictions",
)

UNRESOLVED_REALITY_CHAINS = {
    "rank-three holomorphic Yukawa matrix": (
        "nonzero null-family normal displacement",
        "sector Hessian / second-normal form",
        "twelve physical amplitudes",
        "normalized carrier residues",
        "complete common-DGA representatives and contractions",
    ),
    "physical Yukawa matrices": (
        "rank-three holomorphic Yukawa matrix",
        "nonzero null-family normal displacement",
        "sector Hessian / second-normal form",
        "twelve physical amplitudes",
        "normalized carrier residues",
        "complete common-DGA representatives and contractions",
        "matter metrics",
        "stabilized common vacuum",
    ),
    "physical masses": (
        "rank-three holomorphic Yukawa matrix",
        "matter metrics",
        "canonical normalization",
        "stabilized common vacuum",
    ),
    "CKM and CP observables": (
        "rank-three physical Yukawa matrices",
        "matter metrics",
        "canonical normalization",
        "stabilized common vacuum",
    ),
}


def assemble_reality() -> PhysicalState:
    """Assemble only the established carrier state from the exact graph."""

    evaluation = solve_exact(_reality_graph(), "established_carrier_state", {})
    entries = cast(tuple[StateEntry, ...], evaluation.value)
    return PhysicalState(
        "published one-Higgs heterotic Schoen carrier",
        entries,
        UNRESOLVED_REALITY_OUTPUTS,
        True,
        UNRESOLVED_REALITY_CHAINS,
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
    """Reject physical Yukawa requests before the rank lift and normalization exist."""

    _missing_output(
        "physical Yukawa matrices",
        (
            "rank-three holomorphic Yukawa matrix",
            "nonzero null-family normal displacement",
            "sector Hessian / second-normal form",
            "twelve physical amplitudes",
            "normalized carrier residues",
            "complete common-DGA representatives and contractions",
            "matter metrics",
            "stabilized common vacuum",
        ),
    )


def request_rank_three_yukawa() -> NoReturn:
    """Reject rank-three holomorphic Yukawa requests at the exact frontier."""

    _missing_output(
        "rank-three holomorphic Yukawa matrix",
        (
            "nonzero null-family normal displacement",
            "sector Hessian / second-normal form",
            "twelve physical amplitudes",
            "normalized carrier residues",
            "complete common-DGA representatives and contractions",
        ),
    )


def request_masses() -> NoReturn:
    """Reject mass requests until physical Yukawas, metrics, and vacuum exist."""

    _missing_output(
        "physical masses",
        (
            "rank-three holomorphic Yukawa matrix",
            "matter metrics",
            "canonical normalization",
            "stabilized common vacuum",
        ),
    )


def request_ckm_cp() -> NoReturn:
    """Reject CKM and CP requests until common normalized flavor exists."""

    _missing_output(
        "CKM and CP observables",
        (
            "rank-three physical Yukawa matrices",
            "matter metrics",
            "canonical normalization",
            "stabilized common vacuum",
        ),
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
