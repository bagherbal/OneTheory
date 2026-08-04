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

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import NoReturn, cast

from onetheory.core.errors import MissingPhysicalInput
from onetheory.engine.graph import ComputationGraph, GraphNode
from onetheory.engine.solve import solve_exact
from onetheory.engine.state import PhysicalState, StateEntry
from onetheory.models.heterotic_schoen.consistency import topological_consistency
from onetheory.models.heterotic_schoen.flavor import (
    COMMON_DGA_MISSING_CHAIN,
    common_dga_input_status,
    finite_frontier_status,
    tree_level_flavor,
)
from onetheory.models.heterotic_schoen.geometry import SchoenGeometry, schoen_geometry
from onetheory.models.heterotic_schoen.hidden import (
    HIDDEN_BUNDLE_MISSING_CHAIN,
    hidden_bundle_input_status,
)
from onetheory.models.heterotic_schoen.instantons import (
    CONIC_PFAFFIAN_MISSING_CHAIN,
    conic_pfaffian_input_status,
)
from onetheory.models.heterotic_schoen.metrics import METRIC_MISSING_CHAIN, metric_input_status
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
from onetheory.physics.fields import (
    Action,
    Derivative,
    Field,
    FieldCodomain,
    LagrangianTerm,
    LocalProduct,
)
from onetheory.physics.gravity import (
    EinsteinHilbertAction,
    GaugeActionCoupling,
    MetricField,
    MinimalCoupling,
)
from onetheory.physics.quantum import Hamiltonian, HilbertSpace

PHYSICAL_4D_MISSING_CHAIN = (
    "established field and interaction laws",
    "gauge couplings",
    "normalized Yukawa matrices",
    "Higgs potential parameters",
    "gravitational normalization",
    "threshold corrections",
    "one common controlled vacuum",
)
STANDARD_MODEL_PROVENANCE = "established Standard Model law input"


@dataclass(frozen=True, slots=True)
class Established4DLaws:
    """The parameterized four-dimensional laws before physical parameter admission."""

    standard_model: StandardModel
    quantum_space: HilbertSpace
    quantum_hamiltonian: Hamiltonian
    metric_field: MetricField
    gravity_action: EinsteinHilbertAction
    matter_coupling: MinimalCoupling
    gauge_coupling: GaugeActionCoupling
    unresolved_parameters: tuple[str, ...]

    @property
    def exact_law_certificates_pass(self) -> bool:
        return (
            self.standard_model.anomalies.cancels
            and self.standard_model.b_minus_l_anomalies.cancels
            and self.standard_model.electric_charge_assignments_valid
            and self.standard_model.all_law_terms_are_invariant
            and self.standard_model.all_renormalizable_terms_dimension_four
            and self.quantum_hamiltonian.self_adjoint
            and self.gravity_action.mass_dimension == 4
            and self.matter_coupling.covariant
            and self.gauge_coupling.covariant
            and self.matter_coupling.action.is_hermitian
        )


@dataclass(frozen=True, slots=True)
class OneTheoryCarrierState:
    """The certified Schoen carrier composed with the same established law objects."""

    laws: Established4DLaws
    carrier: PhysicalState


def established_4d_laws() -> Established4DLaws:
    """Assemble established law structure with symbolic unresolved parameters."""

    model = standard_model()
    quantum_space = HilbertSpace("parameterized four-dimensional field state space")
    hamiltonian = Hamiltonian("parameterized Standard Model Hamiltonian", quantum_space, (model,))
    metric_field = MetricField("g", model.spacetime)
    gravity_action = EinsteinHilbertAction(metric_field)
    action_terms = []
    for matter_field in model.matter_fields:
        field = Field.spinor(
            matter_field.name,
            model.domain,
            FieldCodomain(matter_field.name, matter_field.representation.dimension),
            matter_field.mass_dimension,
            matter_field.representation,
        )
        action_terms.append(
            LagrangianTerm(
                LocalProduct((Derivative(field.conjugate_field(adjoint=True), 0), field)),
                None,
                STANDARD_MODEL_PROVENANCE,
                True,
            )
        )
    for scalar in model.scalar_multiplets:
        field = Field.scalar(
            scalar.name,
            model.domain,
            FieldCodomain(scalar.name, scalar.representation.dimension),
            scalar.mass_dimension,
            scalar.representation,
        )
        action_terms.append(
            LagrangianTerm(
                LocalProduct((Derivative(field, 0), Derivative(field, 0))),
                None,
                STANDARD_MODEL_PROVENANCE,
                True,
            )
        )
    matter_action = Action(
        "parameterized matter and Higgs kinetic action",
        model.domain,
        action_terms,
        STANDARD_MODEL_PROVENANCE,
    )
    return Established4DLaws(
        model,
        quantum_space,
        hamiltonian,
        metric_field,
        gravity_action,
        MinimalCoupling(matter_action, metric_field),
        GaugeActionCoupling((law.factor for law in model.gauge_bosons), metric_field),
        PHYSICAL_4D_MISSING_CHAIN[1:],
    )


def assemble_established_4d_laws() -> Established4DLaws:
    """Named composition-root alias for the established four-dimensional laws."""

    return established_4d_laws()


def _geometry(_: Mapping[str, object]) -> SchoenGeometry:
    return schoen_geometry()


def _standard_model(model: StandardModel | None) -> Callable[[Mapping[str, object]], object]:
    def evaluator(_: Mapping[str, object]) -> StandardModel:
        return model if model is not None else standard_model()

    return evaluator


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


def _common_dga(_: Mapping[str, object]) -> object:
    return common_dga_input_status()


def _conic_pfaffians(_: Mapping[str, object]) -> object:
    return conic_pfaffian_input_status()


def _hidden_bundle(_: Mapping[str, object]) -> object:
    return hidden_bundle_input_status()


def _metric_input(_: Mapping[str, object]) -> object:
    return metric_input_status()


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
        StateEntry("common_dga_input_status", values["common_dga_input_status"]),
        StateEntry("conic_pfaffian_input_status", values["conic_pfaffian_input_status"]),
        StateEntry("hidden_bundle_input_status", values["hidden_bundle_input_status"]),
        StateEntry("metric_input_status", values["metric_input_status"]),
    )


def _reality_graph(model: StandardModel | None = None) -> ComputationGraph:
    """Build the direct exact graph for the established carrier slice."""

    return ComputationGraph(
        (
            GraphNode("standard_model", (), _standard_model(model)),
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
            GraphNode("common_dga_input_status", (), _common_dga),
            GraphNode("conic_pfaffian_input_status", (), _conic_pfaffians),
            GraphNode("hidden_bundle_input_status", (), _hidden_bundle),
            GraphNode("metric_input_status", (), _metric_input),
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
                    "common_dga_input_status",
                    "conic_pfaffian_input_status",
                    "hidden_bundle_input_status",
                    "metric_input_status",
                ),
                _assemble,
            ),
        )
    )


UNRESOLVED_REALITY_OUTPUTS = (
    "physical four-dimensional model",
    "metrics",
    "instanton amplitudes",
    "nonperturbative superpotential",
    "hidden bundle",
    "hidden spectrum",
    "metric package",
    "vacuum",
    "physical Yukawa matrices",
    "rank-three holomorphic Yukawa matrix",
    "physical masses",
    "CKM and CP observables",
    "low-energy predictions",
)

UNRESOLVED_REALITY_CHAINS = {
    "physical four-dimensional model": PHYSICAL_4D_MISSING_CHAIN,
    "rank-three holomorphic Yukawa matrix": (
        "nonzero null-family normal displacement",
        "sector Hessian / second-normal form",
        "twelve physical amplitudes",
        "normalized carrier residues",
        *COMMON_DGA_MISSING_CHAIN,
    ),
    "physical Yukawa matrices": (
        "rank-three holomorphic Yukawa matrix",
        "nonzero null-family normal displacement",
        "sector Hessian / second-normal form",
        "twelve physical amplitudes",
        "normalized carrier residues",
        *COMMON_DGA_MISSING_CHAIN,
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
    "instanton amplitudes": CONIC_PFAFFIAN_MISSING_CHAIN,
    "nonperturbative superpotential": (
        *CONIC_PFAFFIAN_MISSING_CHAIN,
        "stabilized common vacuum",
    ),
    "hidden bundle": HIDDEN_BUNDLE_MISSING_CHAIN,
    "hidden spectrum": (*HIDDEN_BUNDLE_MISSING_CHAIN, "certified descended hidden bundle"),
    "metric package": METRIC_MISSING_CHAIN,
}


def assemble_reality(model: StandardModel | None = None) -> PhysicalState:
    """Assemble only the established carrier state from the exact graph."""

    evaluation = solve_exact(_reality_graph(model), "established_carrier_state", {})
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


def one_theory_carrier_state() -> OneTheoryCarrierState:
    """Assemble the carrier using the exact Standard Model object from established laws."""

    laws = established_4d_laws()
    return OneTheoryCarrierState(laws, assemble_reality(laws.standard_model))


def assemble_one_theory_carrier_state() -> OneTheoryCarrierState:
    """Named composition-root alias for the carrier-plus-laws state."""

    return one_theory_carrier_state()


def request_physical_four_dimensional_model() -> NoReturn:
    """Reject a physical instance until every unresolved parameter is supplied."""

    _missing_output("physical four-dimensional model", PHYSICAL_4D_MISSING_CHAIN)


def _missing_output(output: str, chain: tuple[str, ...]) -> NoReturn:
    raise MissingPhysicalInput(output, chain)


def request_metrics() -> NoReturn:
    """Reject unresolved metric requests explicitly."""

    _missing_output("metrics", METRIC_MISSING_CHAIN)


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
            *COMMON_DGA_MISSING_CHAIN,
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
            *COMMON_DGA_MISSING_CHAIN,
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

    _missing_output("instanton amplitudes", CONIC_PFAFFIAN_MISSING_CHAIN)


def request_nonperturbative_superpotential() -> NoReturn:
    """Reject the instanton sum until visible, hidden, phase, and vacuum data exist."""

    _missing_output(
        "nonperturbative superpotential",
        (*CONIC_PFAFFIAN_MISSING_CHAIN, "stabilized common vacuum"),
    )


def request_hidden_bundle() -> NoReturn:
    """Reject hidden-bundle requests because only its Chern target is established."""

    _missing_output("hidden bundle", HIDDEN_BUNDLE_MISSING_CHAIN)


def request_hidden_spectrum() -> NoReturn:
    """Reject hidden-spectrum requests until a certified bundle exists."""

    _missing_output(
        "hidden spectrum",
        (*HIDDEN_BUNDLE_MISSING_CHAIN, "certified descended hidden bundle"),
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
