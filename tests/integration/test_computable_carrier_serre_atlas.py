"""Test atlas-local Serre presentations without promoting global bundles."""

from __future__ import annotations

from research.experiments.computable_carrier.pencil import tier_a_pencil_model
from research.experiments.computable_carrier.serre_atlas import (
    tier_a_atlas_serre_locals,
    tier_a_serre_pushout_atlases,
)


def test_all_coordinate_points_have_checked_local_unit_pushouts() -> None:
    """Every I3/I6 coordinate point has a free local unit presentation."""

    locals_ = tier_a_atlas_serre_locals(tier_a_pencil_model())
    assert len(locals_) == 6
    assert all(item.hypersurface_incidence for item in locals_)
    assert all(item.fiber_derivative_nonzero for item in locals_)
    assert all(item.local_model.locally_free for item in locals_)
    assert all(item.local_cocycle_exact for item in locals_)


def test_local_serre_atlas_keeps_global_gluing_unresolved() -> None:
    """The local certificate cannot silently become a global constituent."""

    locals_ = tier_a_atlas_serre_locals(tier_a_pencil_model())
    assert {
        item.global_gluing_status for item in locals_
    } == {"global Cech gluing and Serre linearization pending"}


def test_punctured_cocycles_record_the_i3_and_i6_pole_orders() -> None:
    """The local Cech classes have pole orders one and two in the nilpotent direction."""

    locals_ = tier_a_atlas_serre_locals(tier_a_pencil_model())
    pole_orders = {
        item.scheme: item.punctured_cocycle.rows[0][1].terms[0][0]
        for item in locals_
    }
    assert pole_orders == {"I3": (-1, -1), "I6": (-1, -2)}


def test_bare_pushout_atlases_have_exact_torus_transitions() -> None:
    """The ideal-level chart transitions pass inverse and triple-cocycle gates."""

    atlases = tier_a_serre_pushout_atlases(tier_a_pencil_model())

    assert {item.scheme for item in atlases} == {"I3", "I6"}
    assert all(len(item.transitions) == 30 for item in atlases)
    assert all(item.all_invertible for item in atlases)
    assert all(item.cocycle_consistent for item in atlases)
    assert all("line frames" in item.status for item in atlases)
