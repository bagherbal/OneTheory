"""Guard exact alternate-ray matter cohomology on the same stable cone.

Owns:
    Recomputed mixed-transfer ranks, all-parameter long-exact-sequence
    collapse, free-action character multiplicities, and artifact integrity.

Depends on:
    The alternate matter experiment and its content-addressed certificate.

Must not:
    Import published spectrum dimensions as rank inputs, select an extension
    point, or identify cover matter classes with physical Yukawa inputs.

Phase 0:
    Research-only regression for the first alternate matter gate.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_constituent_matter_profile import (
    OUTPUT,
    alternate_constituent_matter_profile,
)


def test_alternate_constituent_matter_profile_is_exact() -> None:
    """The saved gate must match a fresh exact transfer, not a source count."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    assert digest == _canonical_digest(stored)
    assert stored == alternate_constituent_matter_profile()
    assert stored["ray_character_exponents"] == [0, 1]
    assert stored["first_constituent_cover_h0_to_h3"] == [0, 9, 0, 0]
    second = stored["second_constituent"]
    assert second["space_dimensions"] == [[0, 189], [1, 288], [2, 81]]
    assert second["differential_ranks"] == [[0, 189], [1, 81]]
    assert second["squared_zero"] is True
    assert second["cover_h0_to_h3"] == [0, 18, 0, 0]
    assert stored["long_exact_sequence_collapses_if_constituents_pure_h1"] is True
    assert stored["visible_cover_h0_to_h3"] == [0, 27, 0, 0]
    deck = stored["deck_representation"]
    assert deck["regular_multiplicity"] == 3
    assert len(deck["joint_character_multiplicities"]) == 9
    assert all(item["multiplicity"] == 3 for item in deck["joint_character_multiplicities"])
    assert stored["published_matter_dimensions_used_as_rank_inputs"] is False
    assert stored["physical_spectrum_established"] is False
    assert stored["explicit_alternate_matter_cocycles_computed"] is False
    assert stored["explicit_alternate_higgs_cocycles_computed"] is False
