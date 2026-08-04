"""Test atlas-local Serre presentations without promoting global bundles."""

from __future__ import annotations

from research.experiments.computable_carrier.pencil import tier_a_pencil_model
from research.experiments.computable_carrier.serre_atlas import tier_a_atlas_serre_locals


def test_all_coordinate_points_have_checked_local_unit_pushouts() -> None:
    """Every I3/I6 coordinate point has a free local unit presentation."""

    locals_ = tier_a_atlas_serre_locals(tier_a_pencil_model())
    assert len(locals_) == 6
    assert all(item.hypersurface_incidence for item in locals_)
    assert all(item.fiber_derivative_nonzero for item in locals_)
    assert all(item.local_model.locally_free for item in locals_)


def test_local_serre_atlas_keeps_global_gluing_unresolved() -> None:
    """The local certificate cannot silently become a global constituent."""

    locals_ = tier_a_atlas_serre_locals(tier_a_pencil_model())
    assert {
        item.global_gluing_status for item in locals_
    } == {"global Cech gluing and Serre linearization pending"}
