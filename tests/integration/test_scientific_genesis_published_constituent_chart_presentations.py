"""Test affine presentations induced by the selected constituent rays.

Owns:
    Twelve chart maps, relation identities, rank-two cokernels, support units,
    complement freeness, retired-map exclusion, and artifact addressing.

Depends on:
    The Scientific Genesis selected constituent chart experiment.

Must not:
    Infer uncomputed overlap transitions or quotient descent.

Phase 0:
    Affine mixed-ray presentation regression tests only.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_constituent_chart_presentations import (
    OUTPUT,
    published_constituent_chart_presentations,
)


def test_selected_mixed_rays_give_twelve_exact_affine_presentations() -> None:
    """Both constituents are presented on every base/fiber affine chart."""

    presentations = published_constituent_chart_presentations()

    assert len(presentations) == 12
    assert tuple(item.constituent for item in presentations) == ("I3",) * 6 + ("I6",) * 6
    assert all(item.relation_composes_to_zero for item in presentations)
    assert all(item.middle_rank == 2 for item in presentations)
    assert all(item.exact for item in presentations)


def test_support_and_complement_form_a_local_free_cover() -> None:
    """Residue units handle the support while ideal generators handle its complement."""

    presentations = published_constituent_chart_presentations()

    assert all(item.support_local_free for item in presentations)
    assert all(item.complement_local_free for item in presentations)
    assert tuple(item.support_image_rank for item in presentations) == (1,) * 6 + (2,) * 6
    assert tuple(item.support_augmented_rank for item in presentations) == (2,) * 6 + (3,) * 6


def test_chart_presentation_artifact_is_current_and_content_addressed() -> None:
    """The frozen chart data keeps overlap gluing explicitly unresolved."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored["presentation_count"] == 12
    assert stored["all_affine_presentations_exact"] is True
    assert stored["selected_mixed_cocycles_used"] is True
    assert stored["retired_projective_pushout_maps_used"] is False
    assert stored["overlap_transition_matrices_materialized"] is False
