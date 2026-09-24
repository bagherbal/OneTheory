"""Test the finite screen of unused constituent Serre Ext rays.

Owns:
    Joint-character exhaustion, exact full lifts, local-unit profiles, and
    provenance of the unused locally free I6 candidates.

Depends on:
    The research-only ray screen and its content-addressed artifact.

Must not:
    Promote local units to quotient descent or infer Higgs characters.

Phase 0:
    Finite candidate-screen regression tests only.
"""

import json

from onetheory.math.numbers import OMEGA
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.distinct_constituent_ray_screen import (
    OUTPUT,
    distinct_constituent_ray_screen,
)
from research.experiments.scientific_genesis.local_constituent_frames import (
    published_local_constituent_frames,
)
from research.experiments.scientific_genesis.published_constituent_full_cech import (
    published_constituent_full_cech,
)
from research.experiments.scientific_genesis.published_constituent_local_units import (
    evaluate_local_unit,
)


def test_joint_sectors_exhaust_both_ext_spaces() -> None:
    """Every exact Ext character sector is tested without projective sampling."""

    report = distinct_constituent_ray_screen()
    first, second = report["constituents"]
    assert (first["scheme"], first["ext_dimension"]) == ("I3", 2)
    assert (second["scheme"], second["ext_dimension"]) == ("I6", 5)
    assert len(first["sectors"]) == 2
    assert len(second["sectors"]) == 5
    assert all(
        sector["reduced_closed"] and sector["full_cech_closed"]
        for constituent in (first, second)
        for sector in constituent["sectors"]
    )


def test_local_units_leave_two_unused_i6_rays() -> None:
    """Only exact stalkwise units remain in the alternate-ray frontier."""

    report = distinct_constituent_ray_screen()
    profiles = {
        constituent["scheme"]: {
            tuple(sector["character_exponents"]): sector["all_local_units"]
            for sector in constituent["sectors"]
        }
        for constituent in report["constituents"]
    }
    assert profiles == {
        "I3": {(0, 0): False, (1, 0): True},
        "I6": {
            (0, 0): False,
            (0, 1): True,
            (1, 0): False,
            (1, 1): True,
            (2, 1): True,
        },
    }
    assert report["unused_i6_local_unit_rays"] == [[0, 1], [1, 1]]
    assert report["selected_quotient_determinant_character"] == [2, 1]
    assert report["ray_only_quotient_determinant_t_characters"] == [1, 1]
    assert report["ray_only_trivial_determinant_possible"] is False
    assert report["alternate_deck_atlases_constructed"] is False
    assert report["alternate_quotient_determinants_certified"] is False
    assert report["alternate_higgs_characters_computed"] is False


def test_local_unit_gate_ignores_projective_ray_scale() -> None:
    """A nonzero scalar change of an Ext representative preserves its units."""

    selected = published_constituent_full_cech()[1]
    extension = selected.alignment.action.derived.extension
    frame = published_local_constituent_frames()[1][0]
    original = evaluate_local_unit(extension, selected.representative, frame)
    rescaled = evaluate_local_unit(
        extension, selected.representative.scale(OMEGA), frame
    )
    assert original.unit_in_local_dualizing_algebra
    assert rescaled.unit_in_local_dualizing_algebra
    assert original.every_chart_nonzero_in_cokernel
    assert rescaled.every_chart_nonzero_in_cokernel


def test_ray_screen_artifact_is_current() -> None:
    """The candidate screen is reproducible and content addressed."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    assert digest == _canonical_digest(stored)
    assert stored == distinct_constituent_ray_screen()
