"""Fail-closed direct dimensional-reduction boundary for the Schoen carrier.

Owns:
    The one common Schoen geometry handoff, published visible spectrum, established
    ten-dimensional heterotic action, exact topological identities, tree-level
    holomorphic texture, symbolic K/W/f/D slots, and the complete unresolved
    prerequisite graph for a normalized four-dimensional effective action.

Depends on:
    Generic physics compactification and vacuum records, exact heterotic laws, the
    published Schoen geometry/visible modules, and general Standard Model metadata.
    It must not import the engine, reality, verification, research, observations, or
    any speculative adapter.

Must not:
    Claim hidden-bundle, metric, instanton, threshold, Yukawa-normalization, or vacuum
    coefficients; combine distinct moduli points; or report a complete effective action
    while any prerequisite remains unresolved.

Phase 0:
    The direct symbolic effective-action boundary is implemented; carrier-specific
    differential cocycles, metrics, normalized couplings, and common vacuum remain absent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NoReturn

from onetheory.core.errors import MissingPhysicalInput
from onetheory.models.heterotic_schoen.consistency import (
    TopologicalConsistency,
    topological_consistency,
)
from onetheory.models.heterotic_schoen.flavor import TreeLevelFlavorResult, tree_level_flavor
from onetheory.models.heterotic_schoen.geometry import SchoenGeometry, schoen_geometry
from onetheory.models.heterotic_schoen.visible import ObservableBundle, visible_bundle
from onetheory.physics.gauge import GaugeGroup
from onetheory.physics.matter import Spectrum
from onetheory.physics.strings import (
    HeteroticConventions,
    TenDimensionalHeteroticAction,
    default_heterotic_field_content,
    heterotic_bosonic_action,
)
from onetheory.physics.vacuum import EffectiveExpression, ModuliPoint

SCHOEN_EFFECTIVE_MISSING_CHAIN = (
    "one common compactification point",
    "Ricci-flat internal metric",
    "visible HYM connection",
    "stable hidden bundle and hidden HYM connection",
    "differential anomaly trivialization",
    "matter and moduli metrics",
    "physical holomorphic couplings",
    "determinant-line normalized instanton terms",
    "thresholds and gauge kinetic functions",
    "controlled common vacuum",
)


@dataclass(frozen=True, slots=True)
class EffectivePrerequisite:
    """One direct prerequisite node with no inferred fallback evaluator."""

    name: str
    prerequisites: tuple[str, ...]
    available: bool
    provenance: str

    def __post_init__(self) -> None:
        if (
            not self.name.strip()
            or any(not value.strip() for value in self.prerequisites)
            or not self.provenance.strip()
        ):
            raise ValueError("effective prerequisites require names and provenance")


@dataclass(frozen=True, slots=True)
class SymbolicEffectiveSlots:
    """Named K, W, f, and D expressions whose coefficients remain unresolved."""

    moduli_point: ModuliPoint
    kahler_potential: EffectiveExpression
    superpotential: EffectiveExpression
    gauge_kinetic: EffectiveExpression
    d_terms: EffectiveExpression

    @property
    def K(self) -> EffectiveExpression:
        """Return the Kähler-potential slot."""

        return self.kahler_potential

    @property
    def W(self) -> EffectiveExpression:
        """Return the superpotential slot."""

        return self.superpotential

    @property
    def f(self) -> EffectiveExpression:
        """Return the gauge-kinetic slot."""

        return self.gauge_kinetic

    @property
    def D(self) -> EffectiveExpression:
        """Return the D-term slot."""

        return self.d_terms


@dataclass(frozen=True, slots=True)
class SchoenEffectiveActionState:
    """The established Schoen reduction boundary before normalized coefficients exist."""

    ten_dimensional_action: TenDimensionalHeteroticAction
    geometry: SchoenGeometry
    visible_carrier: ObservableBundle
    observable_gauge_group: GaugeGroup
    observable_spectrum: Spectrum
    topological_identities: TopologicalConsistency
    tree_level_holomorphic_texture: TreeLevelFlavorResult
    symbolic_slots: SymbolicEffectiveSlots
    prerequisite_graph: tuple[EffectivePrerequisite, ...]
    provenance: str

    def __post_init__(self) -> None:
        if self.visible_carrier.spectrum.standard_model != self.observable_spectrum:
            raise ValueError("effective action spectrum must reuse the published visible spectrum")
        if not self.provenance.strip():
            raise ValueError("effective-action states require provenance")
        names = {node.name for node in self.prerequisite_graph}
        if len(names) != len(self.prerequisite_graph):
            raise ValueError("effective prerequisite names must be unique")
        if any(
            dependency not in names
            for node in self.prerequisite_graph
            for dependency in node.prerequisites
        ):
            raise ValueError("effective prerequisite graph references an undeclared node")

    @property
    def complete(self) -> bool:
        """Return whether every prerequisite is explicitly available."""

        return all(node.available for node in self.prerequisite_graph)

    def dependency_chain(
        self, target: str = "normalized four-dimensional effective action"
    ) -> tuple[str, ...]:
        """Return the first unresolved direct chain for the requested target."""

        nodes = {node.name: node for node in self.prerequisite_graph}
        visiting: set[str] = set()

        def visit(name: str) -> tuple[str, ...]:
            node = nodes[name]
            if node.available:
                return ()
            if name in visiting:
                raise ValueError("effective prerequisite graph contains a cycle")
            visiting.add(name)
            for dependency in node.prerequisites:
                result = visit(dependency)
                if result:
                    visiting.remove(name)
                    return (name, *result)
            visiting.remove(name)
            return (name,)

        return visit(target)


def _effective_slots() -> SymbolicEffectiveSlots:
    """Create symbolic slots at one named unresolved moduli point."""

    point = ModuliPoint(
        "unresolved common compactification point", provenance="Schoen reduction boundary"
    )
    dependencies = SCHOEN_EFFECTIVE_MISSING_CHAIN
    return SymbolicEffectiveSlots(
        point,
        EffectiveExpression(
            "K(moduli, matter)",
            "symbolic K slot",
            dependencies,
            point,
            "tree level + unresolved corrections",
            "four-dimensional Einstein frame",
        ),
        EffectiveExpression(
            "W_tree + W_instanton",
            "symbolic W slot",
            dependencies,
            point,
            "holomorphic tree and nonperturbative sectors",
            "four-dimensional Einstein frame",
        ),
        EffectiveExpression(
            "f_ab(moduli, thresholds)",
            "symbolic f slot",
            dependencies,
            point,
            "tree level + unresolved thresholds",
            "four-dimensional Einstein frame",
        ),
        EffectiveExpression(
            "D_a",
            "symbolic D slot",
            dependencies,
            point,
            "N=1 effective action",
            "four-dimensional Einstein frame",
        ),
    )


def _prerequisites() -> tuple[EffectivePrerequisite, ...]:
    """Return the complete direct unresolved coefficient graph."""

    return (
        EffectivePrerequisite(
            "one common compactification point", (), False, "required common-state identity"
        ),
        EffectivePrerequisite(
            "Ricci-flat internal metric",
            ("one common compactification point",),
            False,
            "carrier metric frontier",
        ),
        EffectivePrerequisite(
            "visible HYM connection",
            ("one common compactification point",),
            False,
            "visible connection frontier",
        ),
        EffectivePrerequisite(
            "stable hidden bundle and hidden HYM connection",
            ("one common compactification point",),
            False,
            "hidden bundle frontier",
        ),
        EffectivePrerequisite(
            "differential anomaly trivialization",
            ("stable hidden bundle and hidden HYM connection",),
            False,
            "differential B-field frontier",
        ),
        EffectivePrerequisite(
            "matter and moduli metrics",
            (
                "Ricci-flat internal metric",
                "visible HYM connection",
                "stable hidden bundle and hidden HYM connection",
            ),
            False,
            "metric frontier",
        ),
        EffectivePrerequisite(
            "physical holomorphic couplings",
            ("visible HYM connection", "matter and moduli metrics"),
            False,
            "holomorphic normalization frontier",
        ),
        EffectivePrerequisite(
            "determinant-line normalized instanton terms",
            ("differential anomaly trivialization", "matter and moduli metrics"),
            False,
            "instanton normalization frontier",
        ),
        EffectivePrerequisite(
            "thresholds and gauge kinetic functions",
            ("one common compactification point", "matter and moduli metrics"),
            False,
            "threshold frontier",
        ),
        EffectivePrerequisite(
            "controlled common vacuum",
            (
                "physical holomorphic couplings",
                "determinant-line normalized instanton terms",
                "thresholds and gauge kinetic functions",
            ),
            False,
            "vacuum frontier",
        ),
        EffectivePrerequisite(
            "normalized four-dimensional effective action",
            SCHOEN_EFFECTIVE_MISSING_CHAIN,
            False,
            "direct reduction target",
        ),
    )


def schoen_effective_action(
    geometry: SchoenGeometry | None = None,
    visible_carrier: ObservableBundle | None = None,
) -> SchoenEffectiveActionState:
    """Assemble the symbolic effective boundary from one shared geometry handoff."""

    selected_geometry = geometry or schoen_geometry()
    selected_visible = visible_carrier or visible_bundle(selected_geometry)
    conventions = HeteroticConventions()
    e8 = GaugeGroup.simple("E8", 8, 248)
    fields = default_heterotic_field_content(e8, e8, conventions)
    action = heterotic_bosonic_action(fields, conventions)
    return SchoenEffectiveActionState(
        action,
        selected_geometry,
        selected_visible,
        selected_visible.wilson_breaking.unbroken,
        selected_visible.spectrum.standard_model,
        topological_consistency(selected_geometry),
        tree_level_flavor(),
        _effective_slots(),
        _prerequisites(),
        "published Schoen carrier plus established heterotic law boundary",
    )


def request_complete_effective_action(state: SchoenEffectiveActionState | None = None) -> NoReturn:
    """Reject a normalized action until every direct reduction prerequisite exists."""

    selected = state or schoen_effective_action()
    chain = selected.dependency_chain()
    raise MissingPhysicalInput(chain[0], chain[1:])


__all__ = [
    "EffectivePrerequisite",
    "SCHOEN_EFFECTIVE_MISSING_CHAIN",
    "SchoenEffectiveActionState",
    "SymbolicEffectiveSlots",
    "request_complete_effective_action",
    "schoen_effective_action",
]
