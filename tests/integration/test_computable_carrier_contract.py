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

from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.artifact import write_artifact
from research.experiments.computable_carrier.search import finite_tier_search
from research.experiments.computable_carrier.specification import (
    computable_carrier_specification,
)
from research.experiments.computable_carrier.tier_b_curvilinear_actions import (
    tier_b_curvilinear_resolution_actions,
)
from research.experiments.computable_carrier.tier_b_curvilinear_eigenclasses import (
    tier_b_curvilinear_eigenclass_audits,
)
from research.experiments.computable_carrier.tier_b_curvilinear_global import (
    tier_b_global_curvilinear_specializations,
)
from research.experiments.computable_carrier.tier_b_curvilinear_linearization import (
    tier_b_curvilinear_linearization_audits,
)
from research.experiments.computable_carrier.tier_b_curvilinear_outer import (
    tier_b_curvilinear_outer_frontier,
)
from research.experiments.computable_carrier.tier_b_curvilinear_serre import (
    tier_b_curvilinear_serre_audits,
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
from research.experiments.computable_carrier.tier_b_local_families import (
    tier_b_local_invariant_normal_forms,
)
from research.experiments.computable_carrier.tier_b_local_serre import (
    tier_b_local_monomial_serre_audits,
)
from research.experiments.computable_carrier.tier_b_monomial import (
    tier_b_invariant_monomial_schemes,
    tier_b_monomial_resolution_actions,
)
from research.experiments.computable_carrier.tier_b_orbits import (
    projective_orbit,
    tier_b_reduced_orbit_classification,
)
from research.experiments.computable_carrier.tier_b_reduced_actions import (
    tier_b_reduced_resolution_actions,
)
from research.experiments.computable_carrier.tier_b_reduced_schemes import (
    tier_b_reduced_orbit_schemes,
)
from research.experiments.computable_carrier.tier_b_reduced_serre import (
    tier_b_reduced_serre_prerequisites,
)
from research.experiments.computable_carrier.tier_b_reduced_thickenings import (
    tier_b_transported_invariant_schemes,
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
from research.experiments.computable_carrier.tier_b_transported_actions import (
    tier_b_transported_resolution_actions,
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


def test_tier_b_reduced_orbit_types_include_nonmonomial_fixed_orbits() -> None:
    """The fixed projective action has four special reduced length-three orbits."""

    classification = tier_b_reduced_orbit_classification()

    assert classification.complete_for_reduced_orbit_types
    assert classification.nonidentity_fixed_point_count == 12
    assert classification.special_orbit_sizes == (3, 3, 3, 3)
    assert classification.reduced_lengths_within_bound == (3, 6, 9)
    assert len(projective_orbit(classification.special_orbits[0].points[0])) == 3
    assert len(projective_orbit((1, 2, 3))) == 9
    assert all(orbit.invariant and orbit.exact for orbit in classification.special_orbits)


def test_tier_b_reduced_orbit_schemes_have_exact_invariant_presentations() -> None:
    """All four reduced special orbits have exact quadratic resolutions."""

    schemes = tier_b_reduced_orbit_schemes()

    assert len(schemes) == 4
    assert [scheme.length for scheme in schemes] == [3, 3, 3, 3]
    assert all(scheme.exact for scheme in schemes)
    assert all(scheme.p_invariant and scheme.t_invariant for scheme in schemes)
    assert not any(
        len(generator.terms) > 1
        for generator in schemes[0].generators
    )
    assert all(
        any(len(generator.terms) > 1 for generator in scheme.generators)
        for scheme in schemes[1:]
    )


def test_tier_b_reduced_serre_prerequisites_remain_local() -> None:
    """Reduced supports have local-unit characters without global promotion."""

    prerequisites = tier_b_reduced_serre_prerequisites()

    assert len(prerequisites) == 4
    assert all(item.exact for item in prerequisites)
    assert all(item.extension_space_dimension == 3 for item in prerequisites)
    assert all(item.local_unit_character_count == 3 for item in prerequisites)
    assert all(not item.global_serre_constructed for item in prerequisites)


def test_tier_b_reduced_resolution_lifts_have_no_finite_commuting_pair() -> None:
    """The finite reduced-resolution lift family stops before descent."""

    audits = tier_b_reduced_resolution_actions()

    assert len(audits) == 4
    assert all(audit.exact for audit in audits)
    assert [len(audit.p_actions) for audit in audits] == [3, 3, 3, 3]
    assert [len(audit.t_actions) for audit in audits] == [6, 6, 6, 6]
    assert all(audit.scoped_no_pair for audit in audits)


def test_tier_b_transported_special_orbit_schemes_are_exact() -> None:
    """All four special supports carry the six declared local scheme types."""

    schemes = tier_b_transported_invariant_schemes()

    assert len(schemes) == 24
    assert all(scheme.exact for scheme in schemes)
    assert all(scheme.p_invariant and scheme.t_invariant for scheme in schemes)
    assert [
        sum(scheme.length == length for scheme in schemes)
        for length in (3, 6, 9)
    ] == [4, 8, 12]


def test_tier_b_transported_resolution_lifts_have_no_finite_commuting_pair() -> None:
    """All transported presentations fail only the scoped finite lift pair gate."""

    audits = tier_b_transported_resolution_actions()

    assert len(audits) == 24
    assert all(audit.exact for audit in audits)
    assert all(audit.scoped_no_pair for audit in audits)
    assert all(audit.complete_commuting_pair_count == 0 for audit in audits)


def test_tier_b_local_normal_forms_expose_parameterized_curves() -> None:
    """The bounded local category includes non-monomial length-three families."""

    report = tier_b_local_invariant_normal_forms()

    assert report.exact
    assert report.special_orbit_count == 4
    assert report.finite_normal_form_count == 24
    assert report.parameterized_family_count == 8
    assert {
        item.name
        for item in report.normal_forms
        if item.parameterized
    } == {
        "length-three-u-curve-family",
        "length-three-v-curve-family",
    }
    assert all(item.tangent_weights == (1, 2) for item in report.normal_forms)


def test_tier_b_curvilinear_specializations_have_global_hilbert_burch_data() -> None:
    """Exact nonphysical parameter specializations are globally presented."""

    for parameter in (Eisenstein(1), OMEGA):
        specializations = tier_b_global_curvilinear_specializations(parameter)

        assert len(specializations) == 8
        assert all(item.exact for item in specializations)
        assert all(item.length == 9 for item in specializations)
        assert all(item.parameter_is_selected_physics is False for item in specializations)
        assert {item.family for item in specializations} == {"u", "v"}
        assert all(item.p_invariant and item.t_invariant for item in specializations)


def test_tier_b_curvilinear_resolution_lifts_have_no_finite_commuting_pair() -> None:
    """Global curvilinear presentations stop at the finite lift boundary."""

    audits = tier_b_curvilinear_resolution_actions()

    assert len(audits) == 8
    assert all(audit.exact for audit in audits)
    assert all(audit.scoped_no_pair for audit in audits)
    assert all(audit.commuting_pairs == () for audit in audits)


def test_tier_b_curvilinear_serre_presentations_are_locally_free() -> None:
    """Global curvilinear extensions pass presentation-level Fitting gates."""

    audits = tier_b_curvilinear_serre_audits()

    assert len(audits) == 8
    assert [audit.cokernel.dimension for audit in audits] == [8] * 8
    assert all(audit.presentation_locally_free for audit in audits)
    assert all(audit.support_fitting_verified for audit in audits)
    assert all(audit.chart_fitting_verified for audit in audits)
    assert all(audit.line_frame_all_invertible for audit in audits)
    assert all(audit.line_frame_cocycle_consistent for audit in audits)
    assert all(len(audit.line_frame_transitions) == 30 for audit in audits)
    assert all(
        {certificate.coefficient_degree_bound for certificate in audit.fitting_certificates}
        == {1}
        for audit in audits
    )
    assert all(audit.exact for audit in audits)


def test_tier_b_curvilinear_common_eigenclasses_precede_linearization() -> None:
    """Class-level invariance yields three support-free lines per scheme."""

    audits = tier_b_curvilinear_eigenclass_audits()

    assert len(audits) == 8
    assert all(audit.eigenclass_count == 8 for audit in audits)
    assert all(audit.support_locally_free_eigenclass_count == 3 for audit in audits)
    assert all(audit.commuting_pairs_diagonalize_completely for audit in audits)
    assert all(audit.exact for audit in audits)


def test_tier_b_curvilinear_extension_actions_stop_before_descent() -> None:
    """Induced actions are exact but no declared pair linearizes the witness."""

    audits = tier_b_curvilinear_linearization_audits()

    assert len(audits) == 8
    assert all(audit.induced_actions_exact for audit in audits)
    assert all(audit.source_commuting_pair_count == 0 for audit in audits)
    assert all(audit.complete_variant_pair_count == 0 for audit in audits)
    assert all(audit.mixed_action_solves_exact for audit in audits)
    assert all(audit.mixed_complete_variant_pair_count == 0 for audit in audits)
    assert [
        (len(audit.p_compatible_variants), len(audit.t_compatible_variants))
        for audit in audits
    ] == [(0, 12), (0, 12), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
    assert all(audit.scoped_no_complete_pair for audit in audits)


def test_tier_b_curvilinear_outer_presentations_are_complete_and_unpromoted() -> None:
    """Every ordered witness pair has exact raw Hom data only."""

    frontier = tier_b_curvilinear_outer_frontier()

    assert frontier.candidate_count == 8
    assert len(frontier.pair_audits) == 64
    assert frontier.projective_pair_count == 64
    assert frontier.diagonal_pair_count == 8
    assert frontier.dp9_pair_count == 64
    assert frontier.raw_projective_ext1_total == 1480
    assert [audit.dp9_h1_dimension for audit in frontier.pair_audits] == [
        24 if audit.left == audit.right else 23
        for audit in frontier.pair_audits
    ]
    assert frontier.complete_for_declared_category
    assert frontier.exact
    assert all(
        audit.parent_squared_zero
        and audit.parent_homogeneous
        and audit.dp9.squared_zero
        and audit.dp9.all_line_bundles_squared_zero
        and (
            audit.projective is None
            or audit.raw_projective_ext_one_dimension is not None
        )
        for audit in frontier.pair_audits
    )
    assert [
        audit.raw_projective_ext_one_dimension for audit in frontier.pair_audits
    ] == [
        24 if audit.left == audit.right else 23
        for audit in frontier.pair_audits
    ]
    assert frontier.no_equivariant_candidate_selected


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
    record = audits[0].as_record()
    assert len(record["line_frame_base_transitions"]) == 9
    assert len(record["line_frame_transitions"]) == 30
    assert all(
        "base_pair" in transition and "matrix" not in transition
        for transition in record["line_frame_transitions"]
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
    assert all(item["mixed_action_solves_exact"] for item in linearization)
    assert all(item["mixed_complete_variant_pair_count"] == 0 for item in linearization)
    assert all(item["mixed_scoped_no_complete_pair"] for item in linearization)
    horseshoe = artifact["tier_a_chain_inputs"]["rank_four_horseshoe"]
    assert horseshoe["candidate_count"] == 30
    assert horseshoe["presentation_gate_count"] == 30
    assert horseshoe["local_freeness_on_atlas_count"] == 30
    assert horseshoe["invariant_outer_class_count"] == 0
    outer = artifact["tier_a_chain_inputs"]["tier_b_outer_frontier"]
    assert outer["pair_count"] == 12
    assert outer["complete_for_declared_category"] is True
    assert outer["invariant_outer_class_count"] == 0
    assert outer["no_candidate_in_declared_category"] is True
    reduced_orbits = artifact["tier_a_chain_inputs"]["tier_b_reduced_orbit_classification"]
    assert reduced_orbits["complete_for_reduced_orbit_types"] is True
    assert reduced_orbits["special_orbit_sizes"] == [3, 3, 3, 3]
    assert reduced_orbits["nonreduced_schemes"] == "unresolved"
    reduced_schemes = artifact["tier_a_chain_inputs"]["tier_b_reduced_orbit_schemes"]
    assert len(reduced_schemes) == 4
    assert all(item["exact"] for item in reduced_schemes)
    reduced_serre = artifact["tier_a_chain_inputs"]["tier_b_reduced_serre_prerequisites"]
    assert len(reduced_serre) == 4
    assert all(item["exact"] for item in reduced_serre)
    assert all(item["global_serre_constructed"] is False for item in reduced_serre)
    reduced_actions = artifact["tier_a_chain_inputs"]["tier_b_reduced_resolution_actions"]
    assert len(reduced_actions) == 4
    assert all(item["scoped_no_pair"] for item in reduced_actions)
    transported = artifact["tier_a_chain_inputs"]["tier_b_transported_invariant_schemes"]
    assert len(transported) == 24
    assert all(item["exact"] for item in transported)
    transported_actions = artifact["tier_a_chain_inputs"]["tier_b_transported_resolution_actions"]
    assert len(transported_actions) == 24
    assert all(item["scoped_no_pair"] for item in transported_actions)
    local_families = artifact["tier_a_chain_inputs"]["tier_b_local_invariant_normal_forms"]
    assert local_families["exact"] is True
    assert local_families["normal_form_count"] == 32
    assert local_families["parameterized_family_count"] == 8
    global_curvilinear = artifact["tier_a_chain_inputs"][
        "tier_b_global_curvilinear_specializations"
    ]
    assert len(global_curvilinear) == 8
    assert all(item["exact"] for item in global_curvilinear)
    assert all(item["parameter_is_selected_physics"] is False for item in global_curvilinear)
    curvilinear_actions = artifact["tier_a_chain_inputs"][
        "tier_b_curvilinear_resolution_actions"
    ]
    assert len(curvilinear_actions) == 8
    assert all(item["exact"] for item in curvilinear_actions)
    assert all(item["scoped_no_pair"] for item in curvilinear_actions)
    curvilinear_eigenclasses = artifact["tier_a_chain_inputs"][
        "tier_b_curvilinear_eigenclass_audits"
    ]
    assert len(curvilinear_eigenclasses) == 8
    assert all(item["eigenclass_count"] == 8 for item in curvilinear_eigenclasses)
    assert all(
        item["support_locally_free_eigenclass_count"] == 3
        for item in curvilinear_eigenclasses
    )
    assert all(item["exact"] for item in curvilinear_eigenclasses)
    curvilinear_corrections = artifact["tier_a_chain_inputs"][
        "tier_b_curvilinear_correction_audits"
    ]
    assert len(curvilinear_corrections) == 8
    assert [item["corrected_eigenline_count"] for item in curvilinear_corrections] == [
        3,
        3,
        0,
        0,
        0,
        0,
        0,
        0,
    ]
    assert all(
        item["strict_group_law_eigenline_count"] == 0
        for item in curvilinear_corrections
    )
    assert all(item["exact"] for item in curvilinear_corrections)
    curvilinear_projective_cocycles = artifact["tier_a_chain_inputs"][
        "tier_b_curvilinear_projective_cocycle_audits"
    ]
    assert len(curvilinear_projective_cocycles) == 8
    assert [
        item["projective_cocycle_eigenline_count"]
        for item in curvilinear_projective_cocycles
    ] == [3, 3, 0, 0, 0, 0, 0, 0]
    assert all(
        line["complete_cocycle_occurrence_count"] == 72
        and line["central_relation_equation"] is True
        for item in curvilinear_projective_cocycles[:2]
        for line in item["lines"]
    )
    assert all(item["exact"] for item in curvilinear_projective_cocycles)
    curvilinear_serre = artifact["tier_a_chain_inputs"][
        "tier_b_curvilinear_serre_audits"
    ]
    assert len(curvilinear_serre) == 8
    assert all(item["presentation_locally_free"] for item in curvilinear_serre)
    assert all(len(item["line_frame_base_transitions"]) == 9 for item in curvilinear_serre)
    assert all(item["line_frame_transition_count"] == 30 for item in curvilinear_serre)
    assert all(item["line_frame_all_invertible"] for item in curvilinear_serre)
    assert all(item["line_frame_cocycle_consistent"] for item in curvilinear_serre)
    assert all(item["finite_lift_no_pair"] for item in curvilinear_serre)
    assert all(item["parameter_is_selected_physics"] is False for item in curvilinear_serre)
    curvilinear_linearization = artifact["tier_a_chain_inputs"][
        "tier_b_curvilinear_linearization_audits"
    ]
    assert len(curvilinear_linearization) == 8
    assert all(item["induced_actions_exact"] for item in curvilinear_linearization)
    assert all(item["source_commuting_pair_count"] == 0 for item in curvilinear_linearization)
    assert all(item["complete_variant_pair_count"] == 0 for item in curvilinear_linearization)
    assert all(item["mixed_action_solves_exact"] for item in curvilinear_linearization)
    assert all(
        item["mixed_complete_variant_pair_count"] == 0
        for item in curvilinear_linearization
    )
    assert all(item["mixed_scoped_no_complete_pair"] for item in curvilinear_linearization)
    curvilinear_outer = artifact["tier_a_chain_inputs"][
        "tier_b_curvilinear_outer_frontier"
    ]
    assert curvilinear_outer["candidate_count"] == 8
    assert curvilinear_outer["ordered_pair_count"] == 64
    assert curvilinear_outer["diagonal_pair_count"] == 8
    assert curvilinear_outer["projective_pair_count"] == 64
    assert curvilinear_outer["dP9_pair_count"] == 64
    assert curvilinear_outer["raw_projective_ext1_total"] == 1480
    assert [
        item["dP9_total_h1_dimension"]
        for item in curvilinear_outer["pair_audits"]
    ] == [
        24
        if item["left"]["scheme"] == item["right"]["scheme"]
        else 23
        for item in curvilinear_outer["pair_audits"]
    ]
    assert curvilinear_outer["complete_for_declared_category"] is True
    assert curvilinear_outer["exact"] is True
    assert curvilinear_outer["no_equivariant_candidate_selected"] is True
    external = artifact["external_algebra"]
    assert external["status"] == "passed"
    assert external["image_digest"].startswith("sha256:")
    assert len(external["script_sha256"]) == 64
    assert external["output"][-1] == "split_rank_four_status: excluded"
    assert artifact["tier_a_chain_inputs"]["downstream_frontier"]["promotable"] is False
    assert write_artifact(root) == {**artifact, "artifact_digest": digest}
