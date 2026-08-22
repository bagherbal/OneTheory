"""Test source-selected W1/W2 rays in the exact derived Ext bases.

Owns:
    Character selection, simultaneous-intertwiner pullback, total closure,
    mixed edge-map support, retired trivial rays, and artifact addressing.

Depends on:
    The Scientific Genesis constituent-ray alignment experiment.

Must not:
    Infer local freeness from a nonzero correction or call a reduced cocycle a
    completed published constituent.

Phase 0:
    Corrected source-ray alignment regression tests only.
"""

import json

from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_constituent_ray_alignment import (
    OUTPUT,
    published_constituent_ray_alignments,
)


def test_source_selected_rays_use_the_declared_nontrivial_characters() -> None:
    """The source rays are not replaced by fixed vectors of the kernel action."""

    first, second = published_constituent_ray_alignments()

    assert first.source_character == (OMEGA, Eisenstein(1))
    assert second.source_character == (OMEGA2, OMEGA)
    assert first.old_trivial_character_is_different
    assert second.old_trivial_character_is_different


def test_source_rays_pull_back_to_exact_mixed_total_cocycles() -> None:
    """Both selected rays are closed eigenvectors with nonzero edge components."""

    alignments = published_constituent_ray_alignments()

    assert all(result.selected_chain_eigenvector for result in alignments)
    assert all(result.closed for result in alignments)
    assert all(result.has_syzygy_koszul_component for result in alignments)
    assert tuple(
        sum(not value.is_zero() for value in result.correction_coordinates)
        for result in alignments
    ) == (4, 6)


def test_derived_coordinates_are_exact_and_deterministic() -> None:
    """The simultaneous intertwiners fix one reproducible basis expression."""

    first, second = published_constituent_ray_alignments()

    assert tuple(str(value) for value in first.derived_coordinates) == (
        "-18-18*omega",
        "1",
    )
    assert tuple(str(value) for value in second.derived_coordinates) == (
        "0",
        "-omega",
        "0",
        "1+omega",
        "1",
    )


def test_ray_alignment_artifact_is_current_and_content_addressed() -> None:
    """The frozen correction certificate equals a fresh exact reconstruction."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored["trivial_character_selection_retired"] is True
    assert stored[
        "existing_pure_cech_mapping_cones_identified_with_published_W1_W2"
    ] is False
