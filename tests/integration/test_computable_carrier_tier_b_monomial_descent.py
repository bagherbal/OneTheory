"""Test exact descent of the surviving monomial constituent sheaves.

Owns:
    Regression assertions for full affine Fitting covers, graded projective
    cocycles, exact Chern data, and conditional free-quotient descent of all
    surviving length-six eigenrays.

Depends on:
    The internal monomial constituent-descent research frontier.

Must not:
    Select a physical constituent, infer an outer extension, or generalize the
    finite certificate to unexamined invariant schemes.

Phase 0:
    Constituent descent is tested; rank-four and physical gates remain open.
"""

from onetheory.math.numbers import Rational
from research.experiments.computable_carrier.tier_b_monomial_descent import (
    tier_b_monomial_constituent_descent_frontier,
)


def test_all_length_six_rays_have_exact_projective_fitting_covers() -> None:
    """Every surviving ray has three explicit affine unit identities."""

    frontier = tier_b_monomial_constituent_descent_frontier()

    assert len(frontier.lines) == 12
    assert {
        (line.target_line_shift, line.scheme)
        for line in frontier.lines
    } == {
        (-6, "B-monomial-coordinate-orbit-1"),
        (-6, "B-monomial-coordinate-orbit-2"),
        (0, "B-monomial-coordinate-orbit-1"),
        (0, "B-monomial-coordinate-orbit-2"),
    }
    assert all(
        len(line.fitting_certificates) == 3
        and all(
            certificate.minor_count == 10
            and certificate.nonzero_minor_count == 10
            and len(certificate.coefficients) == 2
            and certificate.exact
            for certificate in line.fitting_certificates
        )
        and line.locally_free_sheaf_verified
        for line in frontier.lines
    )
    assert {
        line.target_line_shift: tuple(
            certificate.coefficient_degree_bound
            for certificate in line.fitting_certificates
        )
        for line in frontier.lines
    } == {-6: (8, 8, 8), 0: (2, 2, 2)}


def test_projective_cocycles_descend_all_twelve_constituents() -> None:
    """Central graded cocycles give equivariant dP9 pullbacks and descent."""

    frontier = tier_b_monomial_constituent_descent_frontier()

    assert all(
        line.projective_cocycle.exact
        and line.dp9_deck_atlas_verified
        and line.determinant_linearizable
        and line.equivariant_dp9_pullback_verified
        and line.schoen_action_free
        and line.quotient_order == 9
        and line.internal_descent_certificate
        for line in frontier.lines
    )
    assert frontier.descended_constituent_count == 12


def test_constituent_chern_data_matches_the_two_surviving_shifts() -> None:
    """Both shift families have rank two and second Chern degree six."""

    frontier = tier_b_monomial_constituent_descent_frontier()

    assert {
        line.target_line_shift: (
            line.rank,
            line.first_chern_hyperplane,
            line.second_chern_hyperplane_squared,
        )
        for line in frontier.lines
    } == {
        -6: (2, 6, Rational(6)),
        0: (2, 0, Rational(6)),
    }


def test_descended_constituents_unlock_but_do_not_build_outer_ext() -> None:
    """All 1,440 pairs reach outer Ext without becoming rank-four bundles."""

    frontier = tier_b_monomial_constituent_descent_frontier()
    record = frontier.as_record()

    assert frontier.surviving_topology_candidate_count == 40
    assert frontier.surviving_presentation_pair_count == 1440
    assert frontier.all_surviving_line_twists_descend
    assert frontier.descended_presentation_pair_count == 1440
    assert frontier.exact
    assert record["outer_ext_computation_available"] is True
    assert record["outer_extension_constructed"] is False
    assert record["selected_as_physics"] is False
    assert record["promotion_ready"] is False
    assert all(
        line["independent_external_constituent_certificate"] is False
        for line in record["lines"]
    )
