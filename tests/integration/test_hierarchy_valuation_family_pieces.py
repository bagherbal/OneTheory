"""Check the family-piece theorem and the three-slot line-sum screen.

Owns:
    Regression of Serre-subline cohomology, the two-piece tropical no-go,
    exact E2-page line cohomology with d2 refusal, Euler characteristics,
    and the content-addressed box-four screen artifact.

Depends on:
    The research family-piece and line-sum modules, the exact Schoen line
    engine, the recorded constituent matter profile, and pytest.

Must not:
    Construct a carrier, assign charges or moduli, or use observations.

Phase 0:
    Regression checks for research-only structural screens.
"""

import hashlib
import json

import pytest

from research.experiments.hierarchy_valuation.family_pieces import (
    audit_family_pieces,
    koszul_line_cohomology,
    tropical_orders,
    two_piece_violations,
)
from research.experiments.hierarchy_valuation.line_sum_screen import (
    OUTPUT,
    euler_characteristic,
    line_cohomology,
    screen,
)


def test_serre_sublines_carry_no_families() -> None:
    assert koszul_line_cohomology((-1, 1, -1)) == (0, 0, 9, 0)
    assert koszul_line_cohomology((1, -1, -1)) == (0, 0, 9, 0)


def test_families_occupy_only_two_graded_pieces() -> None:
    pieces = audit_family_pieces()
    assert pieces.occupied_graded_pieces == ("V1/L1", "V/(V1+L2)")
    assert pieces.family_count_by_piece == {"L1": 0, "V1/L1": 1, "L2": 0, "V/(V1+L2)": 2}
    assert pieces.charges_obstruct_three_level_hierarchy


def test_shared_two_piece_charges_never_give_three_levels() -> None:
    cases, violations = two_piece_violations()
    assert cases == 1377
    assert violations == ()


def test_tropical_orders_reproduce_carrier_and_three_piece_patterns() -> None:
    assert tropical_orders((-1, 0, 0), (-1, 0, 0), 1) == (0.0, 0.0, 1.0)
    assert tropical_orders((4, 2, 0), (4, 2, 0), 0) == (0.0, 4.0, 8.0)


@pytest.mark.parametrize(
    ("degree", "expected"),
    (((0, 0, 0), (1, 0, 0, 1)), ((-1, 1, 1), (0, 9, 0, 0)), ((1, -1, -1), (0, 0, 9, 0))),
)
def test_e2_line_cohomology_matches_known_lines(degree, expected) -> None:
    assert line_cohomology(degree) == expected
    h = expected
    assert euler_characteristic(degree) == h[0] - h[1] + h[2] - h[3]


def test_known_higher_transgression_line_is_refused() -> None:
    assert line_cohomology((4, 8, 0)) is None


def test_small_box_screen_has_no_three_slot_sum() -> None:
    result = screen(box=1)
    assert result.three_slot_candidates == ()
    assert result.optimistic_three_slot_candidates == ()


def test_euler_prefilter_changes_no_family_sum() -> None:
    full, filtered = screen(box=2), screen(box=2, prefilter=True)
    assert full.family_sums_any_slots == filtered.family_sums_any_slots
    assert full.optimistic_three_slot_candidates == filtered.optimistic_three_slot_candidates


def test_box_four_artifact_is_content_addressed_and_empty() -> None:
    record = json.loads(OUTPUT.read_text())
    unsigned = {key: value for key, value in record.items() if key != "artifact_digest"}
    payload = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    assert record["artifact_digest"] == hashlib.sha256(payload).hexdigest()
    assert record["box"] == 8 and record["descending_lines"] == 1649
    assert record["three_slot_candidates"] == []
    assert record["optimistic_three_slot_candidates"] == []
    assert all(chi not in (-9,) for chi in record["unresolved_euler_characteristics"])
    slot_counts = {sum(1 for h in families if h) for _, families in record["family_sums_any_slots"]}
    assert slot_counts <= {1, 2}
    assert not record["observations_used"]


def test_no_line_sum_has_a_one_heavy_leading_texture() -> None:
    from collections import Counter

    from research.experiments.hierarchy_valuation.line_sum_screen import TEXTURES

    record = json.loads(TEXTURES.read_text())
    unsigned = {key: value for key, value in record.items() if key != "artifact_digest"}
    payload = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    assert record["artifact_digest"] == hashlib.sha256(payload).hexdigest()
    assert record["screen_digest"] == json.loads(OUTPUT.read_text())["artifact_digest"]
    assert not record["one_heavy_texture_found"]
    counts = Counter(row["texture"] for row in record["rows"])
    assert set(counts) <= {
        "no leading Yukawa",
        "cross: two unsuppressed families, one massless at leading order",
    }
    assert sum(counts.values()) == len(json.loads(OUTPUT.read_text())["family_sums_any_slots"])


def test_one_family_lines_and_partial_splits_in_box_four() -> None:
    from research.experiments.hierarchy_valuation.line_sum_screen import (
        one_family_lines,
        partial_split_hits,
    )

    assert one_family_lines(4) == ((-1, 1, 1), (-1, 4, 0), (1, -1, 1), (4, -1, 0))
    assert partial_split_hits(4) == {"V1": (), "V2": ()}
