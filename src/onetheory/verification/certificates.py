"""Deterministic certificates inspected outside production physics.

Owns:
    Exact equality certificates, deterministic value digests, and scoped
    certificates for the established carrier and observable finite frontier.

Depends on:
    `onetheory.verification.evidence`, immutable production state, and established
    carrier objects solely as inspection targets. Production never imports this
    module.

Must not:
    Supply a missing result, certify guessed coefficients, or make a required
    hidden class into an existing hidden bundle.

Phase 0:
    Exact certificate construction is implemented for the promoted carrier and
    formal/local observable frontier; no numerical convergence certificate or
    physical residue is claimed.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from typing import cast

from onetheory.engine.state import PhysicalState
from onetheory.models.heterotic_schoen.consistency import TopologicalConsistency
from onetheory.models.heterotic_schoen.flavor import (
    COMMON_DGA_MISSING_CHAIN,
    TreeLevelFlavorResult,
    common_dga_input_status,
    finite_frontier_status,
)
from onetheory.models.heterotic_schoen.geometry import SchoenGeometry
from onetheory.models.heterotic_schoen.instantons import (
    CONIC_PFAFFIAN_MISSING_CHAIN,
    ConicPfaffianInputStatus,
)
from onetheory.models.heterotic_schoen.visible import (
    MixedMaurerCartanBranch,
    ObservableAdmissibility,
    ObservableBundle,
    SplitWallDeformation,
)
from onetheory.verification.evidence import (
    EXACT_PROJECT,
    PUBLISHED_CARRIER,
    EvidenceClass,
    EvidenceRecord,
    Provenance,
)
from onetheory.verification.gates import GateResult, gate_missing_input


@dataclass(frozen=True, slots=True)
class ExactCertificate:
    """A deterministic equality certificate with a traceable evidence record."""

    identifier: str
    expected: object
    observed: object
    passed: bool
    evidence: EvidenceRecord
    digest: str


def exact_certificate(
    identifier: str,
    expected: object,
    observed: object,
    *,
    evidence_class: EvidenceClass = EvidenceClass.EXACT_THEOREM,
    statement: str,
    provenance: tuple[Provenance, ...] = (EXACT_PROJECT,),
    scope: str = "established carrier vertical slice",
    prerequisites: tuple[str, ...] = (),
) -> ExactCertificate:
    """Create a deterministic exact equality certificate."""

    passed = observed == expected
    payload = f"{identifier}|{expected!r}|{observed!r}|{passed!r}".encode()
    digest = sha256(payload).hexdigest()
    record = EvidenceRecord(
        identifier,
        evidence_class,
        statement,
        provenance,
        scope,
        prerequisites,
    )
    return ExactCertificate(identifier, expected, observed, passed, record, digest)


def certify_established_carrier(state: PhysicalState) -> tuple[ExactCertificate, ...]:
    """Certify the established geometry, visible spectrum, flavor, and topology."""

    geometry = cast(SchoenGeometry, state.value("geometry"))
    visible = cast(ObservableBundle, state.value("visible_bundle"))
    flavor = cast(TreeLevelFlavorResult, state.value("tree_level_flavor"))
    topology = cast(TopologicalConsistency, state.value("topological_consistency"))
    certificates = (
        exact_certificate(
            "carrier.quotient.order", 9, geometry.quotient.order,
            statement="The established carrier uses a free order-nine quotient.",
            provenance=(PUBLISHED_CARRIER, EXACT_PROJECT),
        ),
        exact_certificate(
            "carrier.spectrum.families", 3, visible.spectrum.families,
            evidence_class=EvidenceClass.PUBLISHED_INPUT,
            statement="Wilson-line projection leaves three observable families.",
            provenance=(PUBLISHED_CARRIER,),
        ),
        exact_certificate(
            "carrier.spectrum.higgs_pairs", 1, visible.spectrum.higgs_pairs,
            evidence_class=EvidenceClass.PUBLISHED_INPUT,
            statement="The selected visible carrier has one Higgs pair.",
            provenance=(PUBLISHED_CARRIER,),
        ),
        exact_certificate(
            "carrier.flavor.det_zero", True, flavor.up.determinant.is_zero(),
            statement="The holomorphic tree-level determinant vanishes identically.",
        ),
        exact_certificate(
            "carrier.topology.bianchi", True, topology.bianchi_identity,
            statement="Visible plus required hidden Chern data match the tangent target.",
        ),
        exact_certificate(
            "carrier.topology.cover_slope", -297, topology.cover_slope,
            statement="The visible constituent slope uses the ninefold cover normalization.",
        ),
    )
    return certificates


def certify_observable_frontier(state: PhysicalState) -> tuple[ExactCertificate, ...]:
    """Certify only recomputed formal/local frontier conclusions."""

    wall = cast(SplitWallDeformation, state.value("split_wall_deformation"))
    branch = cast(MixedMaurerCartanBranch, state.value("mixed_deformation_branch"))
    admissibility = cast(ObservableAdmissibility, state.value("observable_admissibility"))
    frontier = finite_frontier_status()
    return (
        exact_certificate(
            "observable.ledger.forward_dimension",
            4,
            wall.forward.dimension,
            statement="The exact split-wall ledger has four forward invariant directions.",
            scope="abstract Ext1 ledger; no common-DGA representatives",
        ),
        exact_certificate(
            "observable.ledger.reverse_dimension",
            8,
            wall.reverse.dimension,
            statement="The exact split-wall ledger has eight reverse invariant directions.",
            scope="abstract Ext1 ledger; no common-DGA representatives",
        ),
        exact_certificate(
            "observable.branch.maurer_cartan",
            True,
            branch.formally_integrable,
            statement="The corrected mixed Maurer–Cartan and Higgs residuals cancel exactly.",
            scope="formal split-wall DGA branch",
        ),
        exact_certificate(
            "observable.branch.diagonal_blocks",
            True,
            branch.diagonal_blocks_vanish,
            statement="Forward-forward and reverse-reverse obstruction blocks vanish exactly.",
            scope="formal split-wall obstruction ledger",
        ),
        exact_certificate(
            "observable.branch.mixed_quadratic_rank",
            0,
            branch.mixed_quadratic_rank,
            statement="The exact mixed quadratic obstruction matrix has rank zero.",
            scope="bi-Leray mixed obstruction ledger",
        ),
        exact_certificate(
            "observable.branch.strict_square_zero",
            True,
            branch.strict_square_zero,
            statement="The disjoint-support strict square-zero witness cancels in both orders.",
            scope="selected strict witness only",
        ),
        exact_certificate(
            "observable.admissibility.local",
            True,
            admissibility.local_freeness.unit_at_origin,
            statement="The three-pivot local determinant is a unit at the split origin.",
            scope=admissibility.local_freeness.scope,
        ),
        exact_certificate(
            "observable.admissibility.stability_box",
            True,
            admissibility.stability.negative_on_box,
            statement=(
                "The declared sufficient stability inequalities remain negative "
                "on the exact box."
            ),
            scope=admissibility.stability.scope,
        ),
        exact_certificate(
            "observable.admissibility.higgs_protection",
            True,
            admissibility.spectrum.one_higgs_pair_protected,
            statement="The declared open-locus character ledger protects one Higgs pair.",
            scope="formal/local/open-locus spectrum result",
        ),
        exact_certificate(
            "observable.frontier.direct_order_five_count",
            42,
            frontier["direct_order_five_count"],
            statement="The complete directly tested order-five ledger contains 42 rows.",
            scope="direct E^3 F^2 rows only",
        ),
        exact_certificate(
            "observable.frontier.generic_residue_count",
            24,
            frontier["generic_residue_count"],
            statement="The restricted-hull compiler requires 24 exact residue entries.",
            scope="finite holomorphic residue workload",
        ),
        exact_certificate(
            "observable.frontier.direction_refined_count",
            20,
            frontier["direction_refined_residue_count"],
            statement="The exact f3 selection identities reduce the scalar workload to 20.",
            scope="finite holomorphic residue workload",
        ),
        exact_certificate(
            "observable.frontier.first_test_count",
            4,
            frontier["first_simultaneous_test_count"],
            statement="The first simultaneous test consumes four normalized scalar traces.",
            scope="finite holomorphic residue workload",
        ),
        exact_certificate(
            "observable.frontier.typing_nonidentifiable",
            False,
            frontier["star_triangular_typing_identifiable"],
            statement="Branch support alone does not identify star or triangular transport typing.",
            scope="exact countermodel theorem; not a carrier typing claim",
        ),
    )


def unresolved_frontier_evidence() -> tuple[EvidenceRecord, ...]:
    """Return explicit evidence records for the still-missing physical layer."""

    status = common_dga_input_status()
    return (
        EvidenceRecord(
            "observable.common_dga_representatives",
            EvidenceClass.MISSING_INPUT,
            (
                f"First missing input: {status['first_missing_input']}. "
                "Prerequisites: "
                + " -> ".join(COMMON_DGA_MISSING_CHAIN)
                + "."
            ),
            (EXACT_PROJECT,),
            "finite holomorphic frontier",
        ),
        EvidenceRecord(
            "observable.rank_three_yukawa",
            EvidenceClass.MISSING_INPUT,
            "Rank-three holomorphic Yukawa matrices remain unresolved after the finite frontier.",
            (EXACT_PROJECT,),
            "finite holomorphic frontier",
        ),
        EvidenceRecord(
            "observable.physical_normalization",
            EvidenceClass.OPEN,
            "Matter metrics and a common stabilized vacuum are not supplied.",
            (EXACT_PROJECT,),
            "physical observables",
        ),
    )


def certify_instanton_boundary(state: PhysicalState) -> tuple[ExactCertificate, ...]:
    """Certify the unresolved conic Pfaffian boundary without attaching values."""

    status = cast(ConicPfaffianInputStatus, state.value("conic_pfaffian_input_status"))
    return (
        exact_certificate(
            "instanton.first_missing_input",
            CONIC_PFAFFIAN_MISSING_CHAIN[0],
            status.first_missing_input,
            evidence_class=EvidenceClass.MISSING_INPUT,
            statement="The first conic Pfaffian input is absent from the declared data.",
            scope="physical seed-conic reconstruction",
            prerequisites=status.prerequisite_chain,
        ),
        exact_certificate(
            "instanton.common_determinant_line",
            False,
            status.common_determinant_line_available,
            evidence_class=EvidenceClass.MISSING_INPUT,
            statement="No common determinant-line trivialization is available.",
            scope="eighteen conic orbit transport and instanton sum",
            prerequisites=status.prerequisite_chain,
        ),
    )


def conic_pfaffian_input_gate(state: PhysicalState) -> GateResult:
    """Expose the first missing conic input as a fail-closed scientific gate."""

    status = cast(ConicPfaffianInputStatus, state.value("conic_pfaffian_input_status"))
    return gate_missing_input(
        "instanton.conic_pfaffian_inputs",
        f"First missing input: {status.first_missing_input}.",
        "physical conic Pfaffian reconstruction",
        status.prerequisite_chain,
    )


def common_dga_input_gate(state: PhysicalState) -> GateResult:
    """Inspect the assembled state and expose the common-DGA missing chain."""

    status = cast(Mapping[str, object], state.value("common_dga_input_status"))
    chain = tuple(cast(tuple[str, ...], status["prerequisite_chain"]))
    return gate_missing_input(
        "observable.common_dga",
        f"First missing input: {status['first_missing_input']}.",
        "carrier-specific common-DGA reconstruction",
        chain,
    )
