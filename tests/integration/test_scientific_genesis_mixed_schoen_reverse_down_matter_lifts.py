"""Test universal physical matter lifts for the reverse Schoen carrier.

Owns:
    Regression gates for reverse-cone family multiplicities, physical character
    routing, coefficientwise lift evidence, and unresolved downstream scope.

Depends on:
    The content-addressed exact reverse down-matter lift artifact.

Must not:
    Recompute expensive sparse primitives during routine tests, choose a P5
    point, or interpret matter representatives as Yukawa coefficients.

Phase 0:
    Integration tests for exact reverse universal down-matter inputs.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_reverse_down_matter_lifts import (
    OUTPUT,
)

EXPECTED_ARTIFACT_DIGEST = (
    "820f186e534aaa2f6e0d0c886f5b6a24c509b1a59cec7958fc224cf35c23b3ac"
)


def _payload() -> dict[str, object]:
    """Load the reverse matter artifact after checking its content digest."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == EXPECTED_ARTIFACT_DIGEST
    assert digest == _canonical_digest(payload)
    return payload


def test_reverse_matter_basis_uses_the_physical_character_direction() -> None:
    """Source characters are inverted before strict chain classes are used."""

    payload = _payload()
    physical_slice = payload["physical_slice"]
    constants = payload["v2_constant_classes"]
    lifts = payload["v1_parameter_linear_lifts"]

    assert payload["schema"] == "mixed-schoen-reverse-down-matter-lifts-v1"
    assert payload["extension_sequence"] == "0 -> V2 -> E_reverse -> V1 -> 0"
    assert payload["carrier_parameter_basis"] == [
        "b0",
        "b1",
        "b2",
        "b3",
        "b4",
        "b5",
    ]
    assert payload["carrier_locus"] == "P^5(Q(omega)) x K_reverse^s"
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
    assert {
        (
            tuple(record["forward_character_exponents"]),
            record["local_family_index"],
        )
        for record in constants
    } == {
        ((1, 2), 1),
        ((1, 2), 2),
        ((2, 0), 1),
        ((2, 0), 2),
    }
    assert {record["term_count"] for record in constants} == {576}
    assert [record["forward_character_exponents"] for record in lifts] == [
        [1, 2],
        [2, 0],
    ]
    assert {record["v1_term_count"] for record in lifts} == {684}


def test_reverse_matter_lifts_cover_every_parameter_exactly() -> None:
    """Each quotient class carries six separately certified corrections."""

    payload = _payload()
    lifts = payload["v1_parameter_linear_lifts"]
    coefficients = [
        coefficient
        for lift in lifts
        for coefficient in lift["parameter_coefficients"]
    ]

    assert len(lifts) == 2
    assert all(lift["exact"] is True for lift in lifts)
    assert len(coefficients) == 12
    assert {
        coefficient["parameter"] for coefficient in coefficients
    } == {f"b{index}" for index in range(6)}
    assert len({record["product_digest"] for record in coefficients}) == 12
    assert len({record["correction_digest"] for record in coefficients}) == 12
    assert sorted(record["product_term_count"] for record in coefficients) == [
        80_982,
        82_011,
        93_777,
        93_957,
        94_650,
        94_962,
        100_554,
        101_958,
        108_687,
        110_514,
        114_306,
        117_270,
    ]
    assert sorted(record["correction_term_count"] for record in coefficients) == [
        45_783,
        46_134,
        48_540,
        48_717,
        49_809,
        49_917,
        55_197,
        55_959,
        56_238,
        56_640,
        59_838,
        60_966,
    ]
    assert payload["all_coefficientwise_cone_identities_exact"] is True
    assert payload["all_lifts_strict_in_forward_characters"] is True
    assert payload["source_characters_obtained_only_by_exact_inversion"] is True
    assert payload["arbitrary_extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert payload["exact"] is True
    assert payload["next_required_object"] == (
        "a strict reverse universal H_d lift in forward character (0,1)"
    )
