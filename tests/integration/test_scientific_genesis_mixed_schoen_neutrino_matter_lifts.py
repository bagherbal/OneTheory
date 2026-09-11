"""Test universal matter lifts for the Dirac-neutrino sector.

Owns:
    Regression gates for both source-selected characters, all local families,
    every carrier-parameter correction, and artifact provenance.

Depends on:
    The content-addressed exact neutrino-matter lift certificate.

Must not:
    Select an extension point, infer one correction from another, or interpret
    a valid matter lift as a computed Yukawa coefficient.

Phase 0:
    Integration tests for exact universal Dirac-neutrino matter inputs.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_neutrino_matter_lifts import (
    OUTPUT,
)


def _payload() -> dict[str, object]:
    """Load the lift artifact after checking its content digest."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    return payload


def test_neutrino_matter_bases_cover_both_exact_characters() -> None:
    """Each selected character has one V1 and two V2 family classes."""

    payload = _payload()
    v1 = payload["v1_constant_classes"]
    v2 = payload["v2_parameter_linear_lifts"]

    assert payload["selected_sector"] == "dirac_neutrino"
    assert payload["matter_character_exponents"] == [[0, 0], [0, 2]]
    assert [record["character_exponents"] for record in v1] == [
        [0, 0],
        [0, 2],
    ]
    assert [record["term_count"] for record in v1] == [684, 684]
    assert {
        (tuple(record["character_exponents"]), record["local_family_index"])
        for record in v2
    } == {
        ((0, 0), 1),
        ((0, 0), 2),
        ((0, 2), 1),
        ((0, 2), 2),
    }
    assert {record["v2_term_count"] for record in v2} == {576}
    assert all(record["exact"] is True for record in v2)


def test_all_eight_neutrino_corrections_are_independently_certified() -> None:
    """Every family and parameter slot has a distinct exact sparse digest."""

    payload = _payload()
    coefficients = [
        coefficient
        for lift in payload["v2_parameter_linear_lifts"]
        for coefficient in lift["parameter_coefficients"]
    ]

    assert len(coefficients) == 8
    assert {record["parameter"] for record in coefficients} == {"a0", "a1"}
    assert len({record["product_digest"] for record in coefficients}) == 8
    assert len({record["correction_digest"] for record in coefficients}) == 8
    assert payload["new_matter_parameter_correction_count"] == 8
    assert payload["all_coefficientwise_cone_identities_exact"] is True
    assert payload["all_lifts_strict_in_declared_characters"] is True
    assert payload["all_neutrino_matter_lifts_exact"] is True
    assert payload["arbitrary_extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert payload["yukawa_coefficient_computed"] is False
