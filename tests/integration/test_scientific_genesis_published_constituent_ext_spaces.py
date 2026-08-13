"""Test exact fiber-sensitive constituent Serre extension spaces.

Owns:
    dP9 factor assignment, Hilbert--Burch shifts, total-complex dimensions,
    exact Ext-one dimensions, and content-addressed evidence.

Depends on:
    The research-only dP9 Serre Ext engine and its scientific-genesis record.

Must not:
    Treat dimension agreement as an equivariant ray, descent certificate, or
    reconstruction of the published outer extension.

Phase 0:
    Constituent extension-space regression tests only.
"""

import json

from research.experiments.computable_carrier.dp9_serre_ext import (
    published_constituent_serre_exts,
)
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_constituent_ext_spaces import (
    OUTPUT,
    published_constituent_ext_spaces,
)


def test_published_serre_complexes_use_both_d_p9_equations() -> None:
    """W1 and W2 are computed on their distinct cubic-pencil factors."""

    w1, w2 = published_constituent_serre_exts()

    assert (w1.surface_factor, w2.surface_factor) == (1, 2)
    assert w1.generator_degrees == (2, 2, 2)
    assert w1.syzygy_degrees == (3, 3)
    assert w2.generator_degrees == (3, 3, 3, 3)
    assert w2.syzygy_degrees == (4, 4, 4)


def test_constituent_total_complexes_are_exact_complexes() -> None:
    """Both signed Hilbert--Burch/Koszul total differentials square to zero."""

    w1, w2 = published_constituent_serre_exts()

    assert w1.squared_zero
    assert w2.squared_zero
    assert tuple(item.total.degrees for item in (w1, w2)) == (
        (0, 1, 2, 3, 4),
        (0, 1, 2, 3, 4),
    )


def test_constituent_ext_dimensions_are_derived_as_two_and_five() -> None:
    """Total cohomology independently reproduces the source-ledger dimensions."""

    result = published_constituent_ext_spaces()

    assert result.computed_dimensions == (2, 5)
    assert result.computed_dimensions == result.source_bound_dimensions
    assert tuple(
        len(item.ext_one_representatives) for item in result.constituents
    ) == (2, 5)


def test_dimension_certificate_does_not_overclaim_equivariance() -> None:
    """The result leaves deck actions and selected extension rays unresolved."""

    record = published_constituent_ext_spaces().as_record()

    assert record["dimension_match_exact"] is True
    assert record["published_action_matrices_used_in_computation"] is False
    assert record["equivariant_extension_rays_selected"] is False
    assert record["constituent_descent_claimed"] is False
    assert "deck action" in record["next_required_object"]


def test_constituent_ext_artifact_is_content_addressed() -> None:
    """The frozen record equals a fresh exact total-cohomology computation."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == published_constituent_ext_spaces().as_record()
    assert digest == _canonical_digest(stored)
