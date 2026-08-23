"""Test stability and genuine SU(4) on the lawful mixed outer family.

Owns:
    Nontrivial-extension quantifiers, exact chamber witnesses, proper-holonomy
    reduction exclusion, source provenance, and artifact integrity.

Depends on:
    The lawful universal P1 cone and published extension-stability theorems.

Must not:
    Choose an extension coordinate, import retired P3 representatives, claim a
    computed HYM metric, or infer a low-energy spectrum.

Phase 0:
    Stable genuine-SU(4) family regression tests only.
"""

import json

from onetheory.math.numbers import Rational
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_stability_locus import (
    BOUNDS_SOURCE_SHA256,
    OUTPUT,
    STABILITY_SOURCE_SHA256,
    mixed_schoen_outer_stability_locus,
)


def test_every_lawful_nonzero_extension_obeys_the_stability_bound() -> None:
    """The source lower bound depends on nonsplitting, not P3 coordinates."""

    locus = mixed_schoen_outer_stability_locus()
    record = locus.as_record()

    assert locus.extension_bound_applies_to_every_nonsplit
    assert locus.universal_nonzero_locus_is_nonsplit
    assert locus.all_nonzero_parameters_stable_in_chamber
    assert record["extension_parameter_space"] == "P^1(Q(omega))"
    assert record["parameter_quantifier"] == {
        "every_nonzero_parameter": True,
        "reason": (
            "the sufficient lower stability bound depends only on "
            "constituent subsheaves and nonsplitting; every P1 point "
            "is a nontrivial extension"
        ),
        "genericity_assumed": False,
        "retired_P3_embedding_used": False,
        "arbitrary_parameter_selected": False,
    }
    assert record["dimension_mismatch_affects_stability_implication"] is False


def test_lawful_stability_chamber_has_genuine_su4() -> None:
    """Exact negative slopes and nonzero cover c3 close the structure group."""

    locus = mixed_schoen_outer_stability_locus()

    assert locus.anchor == (Rational(6), Rational(9), Rational(3))
    assert locus.anchor_values == tuple(
        Rational(value)
        for value in (-621, -378, -702, -1512, -1269, -594, -918, -27, -675)
    )
    assert locus.anchor_values_match
    assert locus.box_radius == Rational(1, 32)
    assert locus.box_is_stable
    assert all(bound < 0 for bound in locus.box_upper_bounds)
    assert locus.cover_c3 == Rational(-54)
    assert locus.proper_connected_irreducible_reduction_excluded
    assert locus.genuine_su4_on_certified_locus


def test_lawful_stability_artifact_is_current_and_sourced() -> None:
    """The frozen certificate binds both exact source archives and no point."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored == mixed_schoen_outer_stability_locus().as_record()
    assert [source["source_archive_sha256"] for source in stored["sources"]] == [
        STABILITY_SOURCE_SHA256,
        BOUNDS_SOURCE_SHA256,
    ]
    assert stored["certified_stable_locus"] == "P^1(Q(omega)) x K^s"
    assert stored["all_nonzero_parameters_stable_in_chamber"] is True
    assert stored["structure_group"]["genuine_su4_on_certified_locus"] is True
    assert stored["arbitrary_extension_point_selected"] is False
