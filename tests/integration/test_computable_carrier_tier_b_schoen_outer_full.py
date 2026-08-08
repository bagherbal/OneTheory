"""Test the declared full Tier B Schoen-cover pair category.

Owns:
    Regression checks for deterministic enumeration of every topology/eigenray
    presentation pair before sparse cover Hom evaluation.

Depends on:
    The research-only Tier B topology and Serre-eigenray enumerators.

Must not:
    Treat pair enumeration as an Ext calculation, infer quotient invariants,
    or promote the declared category into a physical carrier.

Phase 0:
    Enumeration coverage is exact; the exhaustive sparse evaluation remains a
    research computation and quotient-level gates remain unresolved.
"""

from collections import Counter

from research.experiments.computable_carrier.tier_b_schoen_outer_full import (
    declared_schoen_outer_pairs,
)


def test_declared_outer_pair_category_has_1440_pairs() -> None:
    """Every candidate is paired with the six-by-six length-six rays."""

    pairs = declared_schoen_outer_pairs()

    assert len(pairs) == 1440
    counts = Counter(pair[0] for pair in pairs)
    assert len(counts) == 40
    assert set(counts.values()) == {36}
