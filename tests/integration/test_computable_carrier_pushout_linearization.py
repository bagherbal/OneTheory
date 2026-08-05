"""Test full presentation-level linearization gates for Tier A pushouts.

Owns:
    Exact relation equations, transpose action conventions, order-three checks,
    and the explicit I3/I6 commutator failures on the new pushouts.

Depends on:
    The derived Serre pushouts, Hilbert--Burch resolution actions, exact
    polynomial matrices, and the research linearization diagnostic.

Must not:
    Call an extension-line eigenvector a full bundle linearization or claim
    quotient descent when the presentation actions do not commute.

Phase 0:
    Presentation-level action failures are tested; global dP9 descent remains
    unresolved.
"""

from __future__ import annotations

from research.experiments.computable_carrier.pushout_linearization import (
    tier_a_pushout_relation_linearizations,
)


def test_pushout_relation_equations_are_exact_but_group_gates_remain_open() -> None:
    """Both presentations satisfy generators separately but fail commutation."""

    records = tier_a_pushout_relation_linearizations()

    assert tuple(record.scheme for record in records) == ("I3", "I6")
    assert all(record.relation_equations_hold for record in records)
    assert tuple(record.relation_actions_commute for record in records) == (True, False)
    assert tuple(record.middle_actions_commute for record in records) == (False, True)
    assert all(not record.group_relations_verified for record in records)
    assert records[0].failures == ("middle-generator P/T actions do not commute",)
    assert records[1].failures == ("relation-row P/T actions do not commute",)
