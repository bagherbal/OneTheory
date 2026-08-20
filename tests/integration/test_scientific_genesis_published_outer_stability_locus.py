"""Tests for the published generic outer-family stability certificate.

Owns:
    Exact slope, open-box, provenance, generic-locus, descent, and genuine-SU(4)
    regression gates for the reconstructed published extension family.

Depends on:
    The source-bound stability constructor and its content-addressed artifact.

Must not:
    Select a projective coordinate, enlarge the generic locus to all P3, or
    treat a stability theorem as an explicit HYM metric solution.

Phase 0:
    Generic stability-certificate tests only; exceptional equations stay open.
"""

import json

from onetheory.math.numbers import Rational
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_outer_stability_locus import (
    OUTPUT,
    published_outer_stability_locus,
)


def test_published_stability_chamber_has_an_exact_open_witness() -> None:
    """The nine strict inequalities hold on a rational neighborhood."""

    locus = published_outer_stability_locus()

    assert locus.anchor == (Rational(6), Rational(9), Rational(3))
    assert locus.anchor_values == tuple(
        Rational(value)
        for value in (-621, -378, -702, -1512, -1269, -594, -918, -27, -675)
    )
    assert locus.anchor_values_match
    assert locus.box_radius == Rational(1, 32)
    assert locus.box_is_stable
    assert all(bound < 0 for bound in locus.box_upper_bounds)


def test_generic_stable_locus_has_genuine_su4_without_a_chosen_point() -> None:
    """Nonzero c3 excludes proper connected irreducible reductions."""

    locus = published_outer_stability_locus()
    record = locus.as_record()

    assert locus.cover_c3 == Rational(-54)
    assert locus.proper_connected_irreducible_reduction_excluded
    assert locus.generic_genuine_su4_locus_certified
    assert record["certified_stable_locus"] == "U_pub x K^s"
    assert record["certified_parameter_locus"] == {
        "name": "U_pub",
        "description": (
            "the nonempty Zariski-open locus of generic published nonsplit "
            "invariant extensions"
        ),
        "nonempty": True,
        "open": True,
        "every_nonzero_parameter_claimed": False,
        "exceptional_locus_ideal_computed": False,
        "arbitrary_parameter_selected": False,
    }
    assert record["full_parameterwise_stability_classification"] is False
    assert record["arbitrary_extension_point_selected"] is False
    assert record["structure_group"]["genuine_su4_on_certified_locus"] is True


def test_published_stability_artifact_is_current_and_content_addressed() -> None:
    """The frozen certificate matches exact reconstruction and its digest."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored == published_outer_stability_locus().as_record()
    assert stored["source"]["source_archive_sha256"] == (
        "8e38123b9d2de8751deecbf295015497ab2ed891244215455fffe756bebf0aea"
    )
