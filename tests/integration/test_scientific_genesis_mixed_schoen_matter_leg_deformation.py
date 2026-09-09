"""Test the first exact matter-leg deformation certificate.

Owns:
    Regression gates for the family-symmetric raw term, grouped transfer,
    noncycle obstruction, and zero partial scalar residue.

Depends on:
    The committed content-addressed matter-leg deformation artifact.

Must not:
    Promote a partial residue to a higher product or a Yukawa matrix entry.

Phase 0:
    Integration tests for the scoped first-order matter-leg result.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_leg_deformation import (
    OUTPUT,
)


def test_first_matter_leg_deformation_is_exact_and_fail_closed() -> None:
    """The partial coefficient records its obstruction instead of a Yukawa."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")

    assert digest == _canonical_digest(payload)
    assert payload["parameter"] == "a0"
    assert payload["row_character_exponents"] == [2, 1]
    assert payload["column_character_exponents"] == [1, 1]
    assert payload["family_exchange_sign"] == 1
    assert payload["raw_exchange_symmetric"] is True
    assert payload["raw_product"]["term_count"] == 1_715_173
    assert payload["grouped_hpl"] == {
        "inclusion_depth": 5,
        "projected_term_count": 866,
        "projection_depth": 6,
        "strict_term_count": 56_679,
    }
    equivariant = payload["equivariant_projection"]
    assert equivariant["character_exponents"] == [0, 2]
    assert equivariant["term_count"] == 72_099
    assert equivariant["residual_term_count"] == 7_797
    assert equivariant["is_cycle"] is False
    assert equivariant["character_exact"] is True
    scalar = payload["partial_scalar_trace"]
    assert scalar["term_count"] == 9_414
    assert scalar["residual_term_count"] == 378
    assert scalar["is_cycle"] is False
    assert scalar["residue"] == "0"
    assert scalar["projection_depth"] == 4
    assert payload["classification"] == "SCOPED_MATTER_LEG_VANISHING"
    assert payload["scoped_result_exact"] is True
    assert payload["full_higher_product_available"] is False
    assert payload["holomorphic_yukawa_entry_available"] is False
    assert payload["extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
