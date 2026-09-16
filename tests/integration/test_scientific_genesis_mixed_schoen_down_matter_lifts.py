"""Test convention-corrected universal down-matter lifts.

Owns:
    Regression gates for physical source-character routing, forward chain
    sectors, family multiplicities, and coefficientwise lift certificates.

Depends on:
    The content-addressed exact down-matter lift artifact.

Must not:
    Recompute expensive lifts during routine tests, select an extension point,
    or interpret exact matter representatives as Yukawa coefficients.

Phase 0:
    Integration tests for exact universal physical down-matter inputs.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_down_matter_lifts import (
    OUTPUT,
)

EXPECTED_ARTIFACT_DIGEST = (
    "4d4feac1c424abc6df62b241f298200e11087682e109e07fe5e19373d290977e"
)


def _payload() -> dict[str, object]:
    """Load the down-lift artifact after checking its content digest."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == EXPECTED_ARTIFACT_DIGEST
    assert digest == _canonical_digest(payload)
    return payload


def test_down_matter_bases_follow_the_corrected_character_direction() -> None:
    """Source sectors are inverted exactly before chain representatives are used."""

    payload = _payload()
    physical_slice = payload["physical_slice"]
    v1 = payload["v1_constant_classes"]
    v2 = payload["v2_parameter_linear_lifts"]

    assert physical_slice["matrix"] == "down-type holomorphic Yukawa"
    assert physical_slice["source_matter_character_exponents"] == [
        [2, 1],
        [1, 0],
    ]
    assert physical_slice["forward_matter_character_exponents"] == [
        [1, 2],
        [2, 0],
    ]
    assert physical_slice["source_higgs_character_exponents"] == [0, 2]
    assert physical_slice["forward_higgs_character_exponents"] == [0, 1]
    assert [record["source_character_exponents"] for record in v1] == [
        [2, 1],
        [1, 0],
    ]
    assert [record["forward_character_exponents"] for record in v1] == [
        [1, 2],
        [2, 0],
    ]
    assert {
        (
            tuple(record["forward_character_exponents"]),
            record["local_family_index"],
        )
        for record in v2
    } == {
        ((1, 2), 1),
        ((1, 2), 2),
        ((2, 0), 1),
        ((2, 0), 2),
    }
    assert [record["term_count"] for record in v1] == [684, 684]
    assert {record["v2_term_count"] for record in v2} == {576}


def test_all_down_lift_coefficients_are_exact_and_independent() -> None:
    """Every family and parameter coefficient carries separate exact evidence."""

    payload = _payload()
    lifts = payload["v2_parameter_linear_lifts"]
    coefficients = [
        coefficient
        for lift in lifts
        for coefficient in lift["parameter_coefficients"]
    ]

    assert len(lifts) == 4
    assert all(lift["exact"] is True for lift in lifts)
    assert len(coefficients) == 8
    assert {record["parameter"] for record in coefficients} == {"a0", "a1"}
    assert len({record["product_digest"] for record in coefficients}) == 8
    assert len({record["correction_digest"] for record in coefficients}) == 8
    assert sorted(record["product_term_count"] for record in coefficients) == [
        60_309,
        61_722,
        65_583,
        65_622,
        69_795,
        69_879,
        71_241,
        71_739,
    ]
    assert sorted(record["correction_term_count"] for record in coefficients) == [
        33_689,
        34_672,
        36_195,
        36_438,
        37_818,
        37_944,
        38_550,
        38_787,
    ]
    assert payload["all_coefficientwise_cone_identities_exact"] is True
    assert payload["all_lifts_strict_in_forward_characters"] is True
    assert payload["source_characters_obtained_only_by_exact_inversion"] is True
    assert payload["arbitrary_extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert payload["exact"] is True
