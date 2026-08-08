"""Test exact sparse deck actions on the Schoen cover line cone.

Owns:
    Regression assertions for the shared P1 action, equation-unit correction,
    chain-map commutation, and order-three certificates.

Depends on:
    The research-only sparse Schoen action module.

Must not:
    Infer quotient-invariant outer Ext or physical equivariance from one line
    bundle action.

Phase 0:
    The deck action is certified only on the exact cover line complex.
"""

from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
    schoen_sparse_line_action_audit,
)
from research.experiments.computable_carrier.schoen_sparse_outer import (
    sparse_line_bundle,
)


def test_shared_base_deck_actions_preserve_both_schoen_equations() -> None:
    """The derived P1 action gives exact chain maps for both generators."""

    record = schoen_sparse_line_action_audit()

    assert record["exact"] is True
    assert [item["first_equation_unit"] for item in record["actions"]] == [
        "-1-omega",
        "1",
    ]
    assert [item["second_equation_unit"] for item in record["actions"]] == [
        "1",
        "1",
    ]


def test_trivial_line_cone_has_commuting_order_three_actions() -> None:
    """The two exact cover actions commute on the trivial line cone."""

    line = sparse_line_bundle(0, 0, 0)
    actions = schoen_sparse_deck_actions()

    for degree in range(4):
        left = actions[0].line_component(line, degree)
        right = actions[1].line_component(line, degree)
        assert left.compose(right) == right.compose(left)
