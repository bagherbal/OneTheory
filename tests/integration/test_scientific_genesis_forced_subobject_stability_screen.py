"""Test the structural forced-subobject stability screen.

Owns:
    Exact category partitioning, family and dimension counts, symbolic slope
    witnesses, prior-no-go composition, and the remaining carrier frontier.

Depends on:
    Complete invariant topology data, descended constituent certificates, and
    the deterministic forced-subobject screen.

Must not:
    Promote a sufficient coefficient test to a necessary criterion, infer a
    global bundle no-go, or select an extension point or polarization.

Phase 0:
    Structural stability-screen regression tests only.
"""

import json
from collections import Counter

from onetheory.math.numbers import Rational
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.forced_subobject_stability_screen import (
    EXPECTED_MIXED_SIGN_CANDIDATES,
    EXPECTED_NO_GO_CANDIDATES,
    EXPECTED_REMAINING_CANDIDATES,
    EXPECTED_ZERO_EXT_CANDIDATES,
    OUTPUT,
    forced_subobject_stability_screen,
)


def test_screen_partitions_every_declared_topology_once() -> None:
    """Zero, coefficient-positive, and mixed-sign blocks partition all 40."""

    result = forced_subobject_stability_screen()
    refuted = tuple(block.candidate_index for block in result.refuted_blocks)

    assert result.checked_candidate_count == 40
    assert result.checked_pair_count == 1440
    assert result.zero_ext_candidates == EXPECTED_ZERO_EXT_CANDIDATES
    assert refuted == EXPECTED_NO_GO_CANDIDATES
    assert result.mixed_sign_candidates == EXPECTED_MIXED_SIGN_CANDIDATES
    assert set(result.zero_ext_candidates).isdisjoint(refuted)
    assert set(result.zero_ext_candidates) | set(refuted) | set(
        result.mixed_sign_candidates
    ) == set(range(1, 41))


def test_all_648_refuted_families_have_exact_positive_witnesses() -> None:
    """Every retired topology has a nonzero coefficient-nonnegative slope."""

    result = forced_subobject_stability_screen()
    record = result.as_record()

    assert len(result.refuted_blocks) == 18
    assert record["coefficient_positive_no_go_family_count"] == 648
    assert sum(dict(result.refuted_dimension_counts).values()) == 648
    assert all(block.witness.coefficient_nonnegative for block in result.refuted_blocks)
    assert all(not block.witness.slope.is_zero() for block in result.refuted_blocks)
    assert record["automorphism_quotient_required"] is False
    assert record["explicit_extension_representative_required"] is False


def test_next_minimum_is_excluded_by_the_rank_three_preimage() -> None:
    """Candidates 18 and 38 have factor-exchanged positive preimage slopes."""

    result = forced_subobject_stability_screen()
    blocks = {block.candidate_index: block for block in result.refuted_blocks}
    expected = Polynomial(
        {
            (2, 0, 0): Rational(1, 9),
            (1, 1, 0): Rational(2, 3),
            (1, 0, 1): Rational(2, 3),
            (0, 2, 0): Rational(2, 9),
            (0, 1, 1): Rational(4, 3),
        },
        variable_count=3,
    )

    assert blocks[18].witness.name == "preimage(L_right)"
    assert blocks[18].witness.rank == 3
    assert blocks[18].witness.first_chern == (Rational(2), Rational(1), Rational(0))
    assert blocks[18].witness.slope == expected
    assert blocks[38].witness.name == "preimage(L_right)"
    assert blocks[38].witness.first_chern == (Rational(1), Rational(2), Rational(0))
    assert Counter(dict(result.remaining_dimension_counts))[18] == 36


def test_screen_preserves_mixed_sign_blocks_as_the_next_frontier() -> None:
    """The sufficient sign test leaves exactly eight nonzero blocks open."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    result = forced_subobject_stability_screen()

    assert stored == result.as_record()
    assert digest == _canonical_digest(stored)
    assert result.remaining_candidates == EXPECTED_REMAINING_CANDIDATES
    assert stored["remaining_family_count"] == 288
    assert stored["next_invariant_ext_dimension"] == 18
    assert stored["next_candidate_blocks"] == [15, 35]
    assert stored["global_computable_carrier_no_go"] is False
