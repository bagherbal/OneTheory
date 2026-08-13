"""Test maximal quotient-generator restrictions in the next carrier block.

Owns:
    Eigenline counts, exact induced ranks, projective kernel dimensions, slope
    exclusion, generic finite-union complement, and the lower-line boundary.

Depends on:
    Frozen invariant cocycles and the maximal-generator restriction classifier.

Must not:
    Infer full stability, omit lower proper sublines, or select a generic
    extension coordinate.

Phase 0:
    Maximal-generator lifting-stratum regression tests only.
"""

import json
from collections import Counter

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.next_survivor_generator_restrictions import (
    OUTPUT,
    next_survivor_generator_restrictions,
)


def test_four_generator_eigenlines_are_checked_for_every_pair() -> None:
    """The exact screen contains four equivariant lines in all 72 families."""

    result = next_survivor_generator_restrictions()

    assert len(result.restrictions) == 288
    assert Counter(item.global_pair_index for item in result.restrictions) == Counter(
        {
            index: 4
            for start, end in ((109, 144), (829, 864))
            for index in range(start, end + 1)
        }
    )
    assert Counter(item.candidate_index for item in result.restrictions) == {
        4: 144,
        24: 144,
    }


def test_all_induced_restrictions_have_exact_proper_kernels() -> None:
    """Every maximal generator line is excluded away from a proper kernel."""

    result = next_survivor_generator_restrictions()

    assert dict(result.target_dimension_counts) == {450: 288}
    assert dict(result.rank_counts) == {36: 36, 38: 36, 40: 216}
    assert dict(result.kernel_counts) == {10: 108, 12: 108, 14: 72}
    assert all(item.exact for item in result.restrictions)
    assert all(
        item.kernel_dimension == item.source_dimension - item.induced_rank
        for item in result.restrictions
    )


def test_finite_unstable_union_leaves_a_generic_open_complement() -> None:
    """Opposite slopes exclude every lifting kernel without choosing a point."""

    record = next_survivor_generator_restrictions().as_record()

    assert record["slope_identity"] == (
        "mu(L_left)+mu(generator_line)=0"
    )
    assert record["every_lifting_kernel_is_proper"] is True
    assert record["every_lifting_kernel_is_unstable"] is True
    assert record["finite_union_complement_nonempty"] is True
    assert record["generic_class_avoids_all_maximal_generator_lifts"] is True
    assert record["arbitrary_extension_point_selected"] is False


def test_generator_artifact_preserves_the_lower_subline_gate() -> None:
    """The content-addressed result does not overstate generic stability."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == next_survivor_generator_restrictions().as_record()
    assert digest == _canonical_digest(stored)
    assert stored["full_slope_stability_proved"] is False
    assert stored["lower_proper_subline_restrictions_classified"] is False
    assert "O(3*tau1-phi)" in stored["next_required_object"]
