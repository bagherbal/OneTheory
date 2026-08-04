"""Test the exact dP9 pencil frontier used by the Tier A search.

The tests cover the finite affine base-locus algebra, exact projective deck
actions, coordinate singular fibers, and local I3/I6 ideal certificates. They
do not treat these records as a completed global Serre construction.
"""

from __future__ import annotations

from research.experiments.computable_carrier.pencil import tier_a_pencil_model


def test_frozen_pencil_has_a_square_free_degree_nine_base_locus() -> None:
    """The affine elimination algebra is exact and has no boundary basepoint."""

    model = tier_a_pencil_model()
    base_locus = model.base_locus
    assert base_locus.degree == 9
    assert base_locus.square_free
    assert base_locus.boundary_empty
    assert base_locus.x_inverse_identity
    assert base_locus.pencil_relations_hold
    assert base_locus.modulus == base_locus.modulus.monic()


def test_pencil_deck_actions_are_exact_order_three_and_commuting() -> None:
    """The affine quotient actions preserve the base-locus algebra exactly."""

    model = tier_a_pencil_model()
    assert tuple(action.name for action in model.actions) == ("P", "T")
    assert all(action.order_three for action in model.actions)
    assert model.actions_commute


def test_coordinate_singular_points_have_distinct_singular_fibers() -> None:
    """The three coordinate support points are exact singular points."""

    model = tier_a_pencil_model()
    assert tuple(point.point.name for point in model.singular_points) == (
        "p_a",
        "p_b",
        "p_c",
    )
    assert all(point.singular for point in model.singular_points)
    assert len({point.fiber_parameter for point in model.singular_points}) == 3


def test_i3_i6_local_ideal_certificates_are_verified() -> None:
    """Every coordinate chart records the reduced and doubled local scheme."""

    model = tier_a_pencil_model()
    assert len(model.local_ideals) == 6
    assert all(certificate.verified for certificate in model.local_ideals)
    assert {
        certificate.ideal_type
        for certificate in model.local_ideals
        if certificate.scheme == "I3"
    } == {"(u,v)"}
    assert {
        certificate.ideal_type
        for certificate in model.local_ideals
        if certificate.scheme == "I6"
    } == {"(u,v^2)"}
