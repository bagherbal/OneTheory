"""Check the same-constituent Wilson-spectrum obstruction.

Owns:
    Independent nine-character enumeration against the two-case support proof.

Depends on:
    The certified full-chain Higgs support and fixed Wilson characters.

Must not:
    Exclude a distinct carrier or use measured flavor data as an input.

Phase 0:
    Research-only scoped no-go regressions.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_observable_spectrum import (
    WILSON_HIGGS_CHARACTERS,
)
from research.experiments.scientific_genesis.mixed_schoen_wilson_shift_no_go import (
    OUTPUT,
    wilson_shift_no_go_audit,
)


def test_wilson_shift_no_go_certificate_is_current() -> None:
    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    assert digest == _canonical_digest(stored)
    assert stored == wilson_shift_no_go_audit()
    assert stored["both_doublets_without_triplets_possible"] is False
    assert stored["extension_parameters_can_change_h1_character_support"] is False
    assert stored["distinct_underlying_constituents_excluded"] is False
    assert stored["source_action_convention_applied"] is True
    assert stored["atlas_bound_source_action_shift_from_mixed"] == [2, 0]
    assert stored["atlas_bound_wilson_multiplicities"] == {
        "up_higgs_doublet": 0,
        "down_higgs_doublet": 1,
        "color_triplet": 0,
        "color_antitriplet": 1,
    }


def test_independent_nine_shift_enumeration_agrees_with_support_proof() -> None:
    audit = wilson_shift_no_go_audit()
    current = tuple(tuple(item) for item in audit["source_action_h1_characters"])
    both_doublet_shifts = []
    for first in range(3):
        for second in range(3):
            shifted = {
                ((a + first) % 3, (b + second) % 3)
                for a, b in current
            }
            multiplicities = {
                label: int(tuple(-value % 3 for value in wilson) in shifted)
                for label, wilson in WILSON_HIGGS_CHARACTERS.items()
            }
            if (
                multiplicities["up_higgs_doublet"] == 1
                and multiplicities["down_higgs_doublet"] == 1
            ):
                both_doublet_shifts.append((first, second))
                assert (
                    multiplicities["color_triplet"]
                    + multiplicities["color_antitriplet"]
                ) == 1
    assert both_doublet_shifts == [(0, 2), (2, 2)]
    assert both_doublet_shifts == [
        tuple(item["shift"]) for item in audit["both_doublet_shift_cases"]
    ]
