"""Test the published deck action on the exact dP9 blow-up atlas.

Owns:
    Regression assertions for all affine P/T chart maps, derived cubic and
    fiber characters, hypersurface equation units, order-three laws, and the
    affine commutator.

Depends on:
    The exact geometric dP9 deck-atlas research audit.

Must not:
    Attach a bundle candidate to the geometric action, infer quotient sheaf
    descent, or select physical extension data.

Phase 0:
    The geometric deck atlas is tested; candidate frame descent remains open.
"""

from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from research.experiments.computable_carrier.dp9_deck_atlas import (
    dp9_deck_atlas_audit,
)


def test_dp9_deck_maps_preserve_all_six_blowup_charts() -> None:
    """Every affine P/T map carries the target equation to a source unit."""

    audit = dp9_deck_atlas_audit()

    assert len(audit.actions) == 12
    assert all(action.equation_compatible for action in audit.actions)
    assert [
        (action.source_chart, action.target_chart)
        for action in audit.actions
        if action.generator == "P"
    ] == [
        ("U_0_mu", "U_2_mu"),
        ("U_0_nu", "U_2_nu"),
        ("U_1_mu", "U_0_mu"),
        ("U_1_nu", "U_0_nu"),
        ("U_2_mu", "U_1_mu"),
        ("U_2_nu", "U_1_nu"),
    ]
    assert audit.p_order_three
    assert audit.t_order_three
    assert audit.actions_commute
    assert audit.exact


def test_dp9_fiber_scalings_are_derived_from_cubic_characters() -> None:
    """P rescales the two fiber charts inversely while T fixes both."""

    record = dp9_deck_atlas_audit().as_record()

    assert record["cubic_characters"] == {
        "P": [str(OMEGA2), str(Eisenstein(1))],
        "T": [str(Eisenstein(1)), str(Eisenstein(1))],
    }
    p_actions = [
        action
        for action in dp9_deck_atlas_audit().actions
        if action.generator == "P"
    ]
    assert all(
        action.coordinate_images[2][0]
        == (OMEGA2 if action.source_chart.endswith("_mu") else OMEGA)
        for action in p_actions
    )
    assert all(
        action.coordinate_images[2][0] == Eisenstein(1)
        for action in dp9_deck_atlas_audit().actions
        if action.generator == "T"
    )
