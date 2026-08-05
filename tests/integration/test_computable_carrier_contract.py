"""Test the frozen contract and finite search boundary for the new carrier.

Owns:
    Identity separation, target constraints, ordered tier locks, determinant
    cancellation, and content-addressed frontier-artifact integrity.

Depends on:
    The research computable-carrier specification, search, artifact, JSON, and
    exact production Schoen/Serre checks.

Must not:
    Treat a descriptor as a selected bundle, import observations, or validate
    the published reference carrier as the new candidate.

Phase 0:
    Contract and finite-category tests only; downstream construction remains
    unpromoted until its explicit gates pass.
"""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from research.experiments.computable_carrier.artifact import write_artifact
from research.experiments.computable_carrier.search import finite_tier_search
from research.experiments.computable_carrier.specification import (
    computable_carrier_specification,
)
from research.experiments.computable_carrier.tier_b_dp9_actions import (
    tier_b_dp9_deck_action_audits,
)
from research.experiments.computable_carrier.tier_b_dp9_ideals import (
    tier_b_dp9_monomial_ideal_resolutions,
)
from research.experiments.computable_carrier.tier_b_global_serre import (
    tier_b_global_serre_audits,
)
from research.experiments.computable_carrier.tier_b_local_serre import (
    tier_b_local_monomial_serre_audits,
)
from research.experiments.computable_carrier.tier_b_monomial import (
    tier_b_invariant_monomial_schemes,
    tier_b_monomial_resolution_actions,
)
from research.experiments.computable_carrier.tier_b_serre_atlas import (
    tier_b_serre_atlas_audits,
)
from research.experiments.computable_carrier.tier_b_serre_cocycles import (
    tier_b_local_cocycle_audits,
)
from research.experiments.computable_carrier.tier_b_serre_extensions import (
    tier_b_serre_dual_cokernels,
    tier_b_serre_eigenrays,
)
from research.experiments.computable_carrier.tier_b_serre_sections import (
    tier_b_projective_serre_section_audits,
)
from research.experiments.computable_carrier.tier_b_twists import (
    tier_b_twist_descent_screen,
)


def test_computable_carrier_contract_is_distinct_and_selection_safe() -> None:
    """The new target remains separate from the published benchmark."""

    specification = computable_carrier_specification()

    assert specification.identifier != specification.reference_carrier_identifier
    assert specification.geometry_identifier == "Schoen quotient"
    assert specification.rank == 4
    assert specification.first_chern_class == (0, 0, 0)
    assert specification.structure_group == "SU(4)"
    assert specification.selection_constraints_are_not_predictions
    assert "measured masses" in specification.forbidden_inputs
    assert tuple(tier.name for tier in specification.tiers) == (
        "Tier A",
        "Tier B",
        "Tier C",
    )


def test_finite_search_keeps_later_tiers_locked() -> None:
    """Tier B and Tier C descriptors cannot silently become active."""

    report = finite_tier_search()

    assert len(report.tier_a) == 1
    assert report.tier_a[0].left_scheme == "I3"
    assert report.tier_a[0].right_scheme == "I6"
    assert not report.tier_a[0].is_constructed
    assert report.tier_b
    assert all(candidate.status == "locked" for candidate in report.tier_b)
    assert report.tier_c == ()
    assert report.tier_b_locked
    assert report.tier_c_locked
    assert report.candidate_count == 500


def test_tier_b_coordinate_monomial_schemes_are_exact() -> None:
    """The bounded coordinate-supported invariant scheme family is certified."""

    schemes = tier_b_invariant_monomial_schemes()

    assert len(schemes) == 6
    assert [scheme.length for scheme in schemes] == [3, 6, 6, 9, 9, 9]
    assert all(scheme.exact for scheme in schemes)
    assert all(scheme.resolution.verifies_generators() for scheme in schemes)
    assert [scheme.resolution.scheme_length for scheme in schemes] == [3, 6, 6, 9, 9, 9]
    assert all(scheme.p_invariant and scheme.t_invariant for scheme in schemes)
    assert all(scheme.irrelevant_saturated for scheme in schemes)


def test_tier_b_monomial_resolution_actions_stop_before_serre_descent() -> None:
    """Resolution lifts pass finite gates without being called linearizations."""

    audits = tier_b_monomial_resolution_actions()

    assert len(audits) == 6
    assert all(audit.exact_resolution_gate for audit in audits)
    assert all(not audit.common_projective_commutator for audit in audits)


def test_tier_b_twists_apply_only_the_necessary_descent_congruence() -> None:
    """The radius-two class screen is exact but does not claim linearization."""

    screen = tier_b_twist_descent_screen()

    assert len(screen.audits) == 125
    assert len(screen.compatible_audits) == 45
    assert (-1, 1, 0) in {item.left_twist for item in screen.compatible_audits}


def test_tier_b_projective_serre_sections_are_explicit_and_scope_limited() -> None:
    """Projective quotient sections expose local units without claiming dP9 Ext."""

    audits = tier_b_projective_serre_section_audits()

    assert len(audits) == 6
    assert [audit.degree for audit in audits] == [1, 2, 2, 3, 3, 3]
    assert [audit.extension_space_dimension for audit in audits] == [3, 6, 6, 9, 9, 9]
    assert [len(audit.character_sections) for audit in audits] == [0, 0, 0, 9, 9, 9]
    assert [len(audit.unit_character_sections) for audit in audits] == [0, 0, 0, 3, 3, 3]
    assert all(audit.projective_serre_candidate for audit in audits[3:])


def test_tier_b_d_p9_ideal_resolutions_are_exact_but_not_serre_objects() -> None:
    """The dP9 ideal comparison is square-zero and explicitly scope-limited."""

    resolutions = tier_b_dp9_monomial_ideal_resolutions()

    assert len(resolutions) == 6
    assert all(item.squared_zero and item.all_line_bundles_squared_zero for item in resolutions)
    assert [dict(item.cohomology_dimensions)[1] for item in resolutions] == [2, 5, 5, 8, 8, 8]


def test_tier_b_d_p9_deck_actions_are_exact_but_not_descent() -> None:
    """The dP9 ideal totalizations have exact commuting deck actions."""

    audits = tier_b_dp9_deck_action_audits()

    assert len(audits) == 6
    assert all(item.total_squared_zero for item in audits)
    assert all(item.actions_commute and item.actions_order_three for item in audits)
    assert [item.invariant_h1_dimension for item in audits] == [0, 0, 0, 0, 0, 0]


def test_tier_b_local_serre_gate_excludes_only_the_non_lci_staircase() -> None:
    """Unit local pushouts exist exactly for the five lci local ideals."""

    audits = tier_b_local_monomial_serre_audits()

    assert len(audits) == 6
    assert [audit.lci for audit in audits] == [True, True, True, True, False, True]
    assert [audit.unit_extension_available for audit in audits] == [
        True,
        True,
        True,
        True,
        False,
        True,
    ]


def test_tier_b_bare_serre_atlases_are_exact_and_non_lci_safe() -> None:
    """Bare chart transitions pass exact gates only for lci local types."""

    audits = tier_b_serre_atlas_audits()

    assert len(audits) == 6
    assert [audit.transitions_available for audit in audits] == [
        True,
        True,
        True,
        True,
        False,
        True,
    ]
    assert all(
        audit.all_invertible and audit.cocycle_consistent
        for audit in audits
        if audit.transitions_available
    )
    assert sum(
        len(audit.atlas.transitions) for audit in audits if audit.atlas is not None
    ) == 150


def test_tier_b_local_cocycles_are_exact_and_non_lci_safe() -> None:
    """Local unit cocycles pass exact tests only for the five lci types."""

    audits = tier_b_local_cocycle_audits()

    assert len(audits) == 6
    assert [audit.available for audit in audits] == [
        True,
        True,
        True,
        True,
        False,
        True,
    ]
    assert all(audit.exact and audit.nonboundary for audit in audits if audit.available)


def test_tier_b_graded_serre_rays_are_explicit_and_scope_limited() -> None:
    """The fixed-target-line comparison produces only exact local rays."""

    cokernels = tier_b_serre_dual_cokernels()
    rays = tier_b_serre_eigenrays()

    assert [item.dimension for item in cokernels] == [2, 5, 5, 8, 8, 8]
    assert all(item.relations_preserved and item.actions_commute for item in cokernels)
    assert len(rays) == 14
    assert [
        sum(ray.cokernel.scheme.name == f"B-monomial-coordinate-orbit-{index}" for ray in rays)
        for index in range(6)
    ] == [2, 3, 3, 3, 0, 3]
    assert all(ray.locally_free_at_support for ray in rays)


def test_tier_b_global_serre_gate_records_successes_and_failures() -> None:
    """The complete dP9 atlas distinguishes global presentation outcomes."""

    audits = tier_b_global_serre_audits()

    assert len(audits) == 14
    assert all(item.graded_relation and item.relation_composition_verified for item in audits)
    assert [item.globally_locally_free for item in audits] == [
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        False,
        False,
        False,
        False,
        False,
        False,
    ]
    assert all(
        item.line_frame_all_invertible and item.line_frame_cocycle_consistent
        for item in audits[:8]
    )
    assert all(
        any(chart == "U_0_mu" for chart, _ in item.fitting_failures)
        for item in audits[8:]
    )


def test_computable_carrier_artifact_digest_and_promotion_gate() -> None:
    """The generated frontier artifact is reproducible and unpromoted."""

    root = Path(__file__).resolve().parents[2]
    path = root / "data/generated/computable_carrier/computable_carrier_artifact.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    digest = artifact.pop("artifact_digest")
    canonical = json.dumps(artifact, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    assert sha256(canonical.encode("utf-8")).hexdigest() == digest
    assert artifact["identity"]["identity_or_isomorphism_proved"] is False
    assert artifact["construction"]["selected_candidate"] is None
    assert artifact["promotion"]["production_import_allowed"] is False
    assert artifact["tier_a_chain_inputs"]["rank_four_frontier"]["candidate_count"] == 14
    assert (
        artifact["tier_a_chain_inputs"]["bounded_equivariant_extensions"]["candidate_count"]
        == 14
    )
    linearization = artifact["tier_a_chain_inputs"]["tier_b_linearization_audits"]
    assert len(linearization) == 8
    assert all(item["complete_variant_pair_count"] == 0 for item in linearization)
    horseshoe = artifact["tier_a_chain_inputs"]["rank_four_horseshoe"]
    assert horseshoe["candidate_count"] == 30
    assert horseshoe["presentation_gate_count"] == 30
    assert horseshoe["local_freeness_on_atlas_count"] == 30
    assert horseshoe["invariant_outer_class_count"] == 0
    assert artifact["tier_a_chain_inputs"]["downstream_frontier"]["promotable"] is False
    assert write_artifact(root) == {**artifact, "artifact_digest": digest}
