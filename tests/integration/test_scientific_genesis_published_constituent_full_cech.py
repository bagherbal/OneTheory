"""Test full standard-cover lifts of the selected W1/W2 Ext rays.

Owns:
    Reduced-basis reconstruction, transferred differential equality, finite
    corrected inclusions, full closure, Koszul retention, and artifact digest.

Depends on:
    The Scientific Genesis full constituent Čech experiment.

Must not:
    Infer local dualizing units or identify an Ext cocycle with a bundle atlas.

Phase 0:
    Full mixed-ray Čech lift regression tests only.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_constituent_full_cech import (
    OUTPUT,
    published_constituent_full_cech,
)


def test_full_cech_transfer_reproduces_both_reduced_ext_totals() -> None:
    """No differential is lost when passing through ambient cohomology."""

    results = published_constituent_full_cech()

    assert all(result.transferred_matches_reduced for result in results)
    assert all(result.inclusion_depth > 0 for result in results)


def test_selected_mixed_rays_are_closed_on_the_raw_standard_cover() -> None:
    """The corrected inclusions satisfy the full Čech/Koszul/HB differential."""

    first, second = published_constituent_full_cech()

    assert first.full_closed
    assert second.full_closed
    assert first.exact
    assert second.exact
    assert first.koszul_term_count > 0
    assert second.koszul_term_count > 0


def test_full_cech_artifact_is_current_and_content_addressed() -> None:
    """The frozen full-lift certificate retains its exact epistemic boundary."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored["all_full_cech_lifts_exact"] is True
    assert stored["pure_cech_trivial_character_cones_retired"] is True
    assert all(
        item["local_dualizing_units_evaluated"] is False
        for item in stored["constituents"]
    )
