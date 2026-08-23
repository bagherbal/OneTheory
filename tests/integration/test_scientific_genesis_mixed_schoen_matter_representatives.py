"""Integration tests for strict synchronized matter representatives."""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_representatives import (
    OUTPUT,
    mixed_schoen_matter_representatives,
)


def test_constituent_matter_characters_are_strict_full_complex_classes() -> None:
    """Both mixed constituents lift every derived character class exactly."""

    first, second = mixed_schoen_matter_representatives()

    assert first.exact
    assert second.exact
    assert first.representatives.domain.dimension == 9
    assert second.representatives.domain.dimension == 18
    assert tuple(sector.dimension for sector in first.sectors) == (1,) * 9
    assert tuple(sector.dimension for sector in second.sectors) == (2,) * 9
    assert all(sector.full_representatives for sector in first.sectors)
    assert all(sector.full_representatives for sector in second.sectors)


def test_matter_representative_artifact_is_content_addressed() -> None:
    """The committed certificate binds the strict sparse representative bases."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")

    assert digest == _canonical_digest(payload)
    assert payload["all_strict_character_representatives_exact"] is True
    assert payload["universal_cone_matter_lifts_computed"] is False
    assert payload["outer_extension_coordinate_selected"] is False
    assert payload["expected_character_multiplicities_imported"] is False
