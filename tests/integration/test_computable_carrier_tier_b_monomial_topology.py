"""Test the topology-first invariant monomial Tier B frontier.

Owns:
    Exact regressions for Betti-derived shift bounds, Schoen index filtering,
    determinant descent, common deck eigenrays, and the surviving length-six
    presentation count.

Depends on:
    The frozen computable-carrier specification and the monomial topology
    research screen.

Must not:
    Promote presentation eigenrays to descended sheaves, infer outer Ext
    classes, or generalize the finite result to unexamined invariant schemes.

Phase 0:
    Necessary topology and eigenclass gates are tested; physical promotion
    remains unavailable.
"""

from research.experiments.computable_carrier.tier_b_monomial_topology import (
    tier_b_monomial_topology_screen,
)


def test_monomial_resolution_types_have_exact_shift_dimensions() -> None:
    """The three Betti types reproduce their finite extension frontiers."""

    screen = tier_b_monomial_topology_screen()
    by_length = {item.length: item for item in screen.resolution_types}

    assert tuple(sorted(by_length)) == (3, 6, 9)
    assert [by_length[3].cokernel_dimension(shift) for shift in (-5, 0, 3, 4)] == [
        3,
        3,
        2,
        0,
    ]
    assert [by_length[6].cokernel_dimension(shift) for shift in (-7, 0, 3, 4, 5)] == [
        6,
        6,
        5,
        3,
        0,
    ]
    assert [by_length[9].cokernel_dimension(shift) for shift in (2, 3, 4, 5, 6)] == [
        9,
        8,
        6,
        3,
        0,
    ]


def test_topology_and_determinant_descent_leave_a_finite_frontier() -> None:
    """Index and determinant gates reduce the complete shift search exactly."""

    screen = tier_b_monomial_topology_screen()

    assert screen.raw_target_index_candidate_count == 1200
    assert screen.determinant_descended_candidate_count == 340
    assert len(screen.shift_audits) == 17
    assert screen.exact


def test_only_length_six_shifts_supply_locally_free_common_eigenrays() -> None:
    """Exact quotient actions retain shifts minus six and zero only."""

    screen = tier_b_monomial_topology_screen()

    assert screen.available_resolution_shifts == frozenset(
        {
            ("length-6-monomial", -6),
            ("length-6-monomial", 0),
        }
    )
    available = tuple(audit for audit in screen.shift_audits if audit.available)
    assert len(available) == 4
    assert all(audit.actions_commute for audit in available)
    assert all(audit.locally_free_eigenray_count == 3 for audit in available)
    assert all(audit.exact for audit in screen.shift_audits)


def test_surviving_length_six_topologies_are_not_promoted() -> None:
    """Forty topologies unlock outer Ext but do not construct an extension."""

    screen = tier_b_monomial_topology_screen()
    surviving = screen.surviving_topology_candidates
    record = screen.as_record()

    assert len(surviving) == 40
    assert {
        (
            item.left_factor,
            item.left_target_line_shift,
            item.right_factor,
            item.right_target_line_shift,
        )
        for item in surviving
    } == {
        (1, -6, 1, 0),
        (1, 0, 1, -6),
        (2, -6, 2, 0),
        (2, 0, 2, -6),
    }
    assert all(item.individual_line_twists_descend for item in surviving)
    assert screen.surviving_presentation_count == 1440
    assert record["outer_ext_computation_available"] is True
    assert record["outer_extension_constructed"] is False
    assert record["promotion_ready"] is False
