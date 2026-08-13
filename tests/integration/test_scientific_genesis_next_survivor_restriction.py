"""Test the exact right-line restriction in the next carrier block.

Owns:
    Exhaustive chain-map gates, induced cohomology ranks, projective lifting
    kernels, their slope obstruction, and the remaining open complement.

Depends on:
    Frozen invariant/action artifacts and exact sparse restriction machinery.

Must not:
    Infer stability on the nonlifting locus, select an extension point, or
    extrapolate beyond candidates 4 and 24.

Phase 0:
    Next-survivor restriction and unstable-kernel regression tests only.
"""

import json
from collections import Counter

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.next_survivor_restriction import (
    OUTPUT,
    next_survivor_restriction,
)


def test_restriction_covers_every_next_survivor_family() -> None:
    """Both factor orientations contribute all 72 exact chain audits."""

    result = next_survivor_restriction()

    assert len(result.pairs) == 72
    assert Counter(pair.candidate_index for pair in result.pairs) == {4: 36, 24: 36}
    assert dict(result.source_dimension_counts) == {50: 36, 52: 36}
    assert dict(result.orbit_space_counts) == {
        "P^49(Q(omega))": 36,
        "P^51(Q(omega))": 36,
    }
    assert all(pair.chain_exact for pair in result.pairs)


def test_induced_map_has_uniform_rank_twenty() -> None:
    """Exact quotient reduction gives the same restriction rank in every pair."""

    result = next_survivor_restriction()

    assert {pair.target_cohomology_dimension for pair in result.pairs} == {216}
    assert {pair.induced_rank for pair in result.pairs} == {20}
    assert dict(result.kernel_dimension_counts) == {30: 36, 32: 36}
    assert all(
        pair.kernel_dimension == pair.source_dimension - pair.induced_rank
        for pair in result.pairs
    )


def test_lifting_kernels_are_unstable_but_complements_remain_open() -> None:
    """The zero-sum slope identity excludes only the exact lifting kernels."""

    record = next_survivor_restriction().as_record()

    assert record["projective_lifting_loci"] == {
        "P^49(Q(omega))": "P^29(Q(omega))",
        "P^51(Q(omega))": "P^31(Q(omega))",
    }
    assert record["kernel_slope_identity"] == (
        "3*mu(preimage(L_right))+mu(L_right)=0"
    )
    assert record["kernel_contains_no_stable_extension"] is True
    assert record["nonlifting_open_complement_nonempty"] is True
    assert record["nonlifting_open_complement_stability_proved"] is False
    assert record["global_computable_carrier_no_go"] is False


def test_restriction_artifact_is_current_and_content_addressed() -> None:
    """The stored certificate exactly reproduces the executable result."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == next_survivor_restriction().as_record()
    assert digest == _canonical_digest(stored)
    assert stored["next_invariant_ext_dimension"] == 50
    assert stored["next_candidate_blocks"] == [4, 24]
