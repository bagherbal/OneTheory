"""Check the seed-chamber invariant audit and the exact wall stability proof.

Owns:
    Regression of Lorentz/flavor invariant counts in the inherited defect
    chamber and of constituent stability along the entire j1 = j2 wall.

Depends on:
    The research seed audit, the wall stability certificate, the trusted
    retained line-Hom certificate, and pytest.

Must not:
    Assign physical meaning to inherited integers, choose a polarization, or
    use observations.

Phase 0:
    Regression checks for research-only audits.
"""

from fractions import Fraction

import pytest

from research.experiments.hierarchy_valuation.seed_audit import (
    VECTOR,
    _exterior_square,
    _tensor,
    audit_seed_chamber,
    lorentz_invariant_count,
)
from research.experiments.hierarchy_valuation.wall_stability import (
    build_report,
    certified_vanishing_lines,
    constituent_wall_rows,
    extension_case_bounds,
    wall_affine,
)


def test_invariant_counter_reproduces_known_lorentz_invariants() -> None:
    bivectors = _exterior_square(VECTOR)
    assert sum(bivectors.values()) == 6
    assert lorentz_invariant_count(_tensor(VECTOR, VECTOR)) == 1
    assert lorentz_invariant_count(_tensor(bivectors, bivectors)) == 2
    four = _tensor(_tensor(VECTOR, VECTOR), _tensor(VECTOR, VECTOR))
    assert lorentz_invariant_count(four) == 4


def test_defect_chamber_has_no_canonical_identity_line() -> None:
    audit = audit_seed_chamber()
    assert audit.chamber_dimension == 432
    assert audit.lorentz_invariants_in_bivector_times_octave == 0
    assert audit.invariants_under_lorentz_and_flavor == 0
    assert audit.flavor_traceless_dimension == 384
    assert not audit.canonical_identity_line_exists


def test_only_four_certified_lines_ever_reach_nonnegative_wall_degree() -> None:
    rows = constituent_wall_rows()
    nonnegative = {(row.constituent, row.line) for row in rows if row.hom_vanishing_used}
    assert nonnegative == set(certified_vanishing_lines())
    assert all(row.nonnegative_for_s_up_to in (None, "1/6") for row in rows)
    assert all(row.strictly_negative_bound_for_all_s for row in rows)


@pytest.mark.parametrize("line", ((-4, 1, 2), (0, 0, 1), (-2, 2, 0)))
def test_wall_degrees_are_exactly_affine(line: tuple[int, int, int]) -> None:
    alpha, beta = wall_affine(line)
    assert isinstance(alpha, Fraction) and isinstance(beta, Fraction)


def test_v1_determinant_vanishes_identically_on_the_wall() -> None:
    assert wall_affine((-2, 2, 0)) == (0, 0)


def test_only_the_v1_determinant_case_reaches_zero_at_the_wall() -> None:
    bounds = extension_case_bounds((1, 1, Fraction(1, 6)))
    assert bounds[(2, 0)] == 0
    assert all(value < 0 for case, value in bounds.items() if case != (2, 0))


def test_report_is_scoped_and_observation_free() -> None:
    report = build_report()
    assert report.constituents_stable_on_entire_wall
    assert report.opposite_side_destabilized_by_v1
    assert all(ok for _, ok in report.stable_side_spot_checks)
    assert report.hidden_compatible_wall_s_interval == ("0", "11/12")
    assert "('1', '101/100', '1/6')" in report.hidden_compatible_stable_points
    assert "('1', '11/10', '2')" not in report.hidden_compatible_stable_points
    assert not report.full_kahler_chamber_claimed
    assert not report.observations_used


def test_exceptional_section_instantons_are_neutral_under_the_wall_u1() -> None:
    from research.experiments.hierarchy_valuation.instanton_charge import audit as charges

    result = charges()
    assert result.curve_count_on_cover == 81
    assert result.curve_degrees == (0, 0, 1)
    assert result.wall_u1_flux == 0 and result.neutral_under_wall_u1
