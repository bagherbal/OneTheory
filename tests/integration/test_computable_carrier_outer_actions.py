"""Test the bounded outer-extension deck-action diagnostic.

Owns:
    Exact simplex orientation, local-gauge transport, coefficient-window
    closure counts, and the explicit absence of a bounded invariant projector.

Depends on:
    The bounded Hom Cech complex, exact constituent gauge equations, and the
    research outer-action diagnostic.

Must not:
    Treat escaped terms as a complete no-go theorem, call the bounded complex
    the full Ext complex, or infer quotient descent from local generators.

Phase 0:
    The current bound-zero action obstruction is tested; full Ext convergence
    and honest equivariant carrier construction remain unresolved.
"""

from __future__ import annotations

from research.experiments.computable_carrier.outer_actions import bounded_outer_action


def test_bounded_outer_actions_preserve_the_basis_boundary_explicitly() -> None:
    """The exact P/T transport records which terms escape the finite basis."""

    frontier = bounded_outer_action()

    assert tuple(action.generator for action in frontier.actions) == ("P", "T")
    assert tuple(action.degree_closed for action in frontier.actions) == (
        (False, False, False),
        (False, True, True),
    )
    assert tuple(action.escaped_term_counts for action in frontier.actions) == (
        (31, 34, 5),
        (10, 0, 0),
    )
    assert frontier.invariant_projector_defined is False
    assert frontier.invariant_representatives == ()


def test_bounded_outer_actions_do_not_claim_group_descent() -> None:
    """A nonclosed finite window cannot report a quotient linearization."""

    frontier = bounded_outer_action()

    assert all(not action.closed for action in frontier.actions)
    assert all(not action.differential_compatible for action in frontier.actions)
    assert "basis closes" in frontier.status
