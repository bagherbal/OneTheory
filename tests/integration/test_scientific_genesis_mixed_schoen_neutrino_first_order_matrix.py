"""Test the complete universal Dirac-neutrino Yukawa matrix.

Owns:
    Regression gates for all eight exact coefficients, polynomial assembly,
    generic rank, filtration completion, provenance, and scientific scope.

Depends on:
    The content-addressed universal neutrino matrix artifact.

Must not:
    Recompute dense source complexes in routine tests, select a carrier point,
    or treat an unnormalized holomorphic matrix as a physical observable.

Phase 0:
    Integration tests for the all-orders Dirac-neutrino flavor calculation.
"""

from __future__ import annotations

import json

import pytest

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_first_order_matrix import (
    OUTPUT as UP_FIRST_ORDER_ARTIFACT,
)
from research.experiments.scientific_genesis.mixed_schoen_neutrino_first_order_matrix import (
    OUTPUT,
    _coefficient_from_record,
)


def _payload() -> dict[str, object]:
    """Load the immutable matrix artifact and verify its content address."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    return payload


def test_exact_coefficient_cache_records_round_trip_fail_closed() -> None:
    """A real exact coefficient record rehydrates while tampering is rejected."""

    upstream = json.loads(UP_FIRST_ORDER_ARTIFACT.read_text(encoding="utf-8"))
    raw = upstream["coefficients"][0]
    result = _coefficient_from_record(raw)
    assert result.as_record() == raw

    tampered = json.loads(json.dumps(raw))
    tampered["complete_scalar_cochain"]["is_cycle"] = False
    with pytest.raises(ValueError, match="canonical reconstruction"):
        _coefficient_from_record(tampered)


def test_all_neutrino_coefficients_close_in_declared_bases() -> None:
    """Every parameter and local-family coefficient has complete evidence."""

    payload = _payload()
    coefficients = payload["coefficients"]
    assert isinstance(coefficients, list)
    assert [
        (
            coefficient["parameter"],
            coefficient["row_local_family_index"],
            coefficient["column_local_family_index"],
        )
        for coefficient in coefficients
    ] == [
        (parameter, row, column)
        for parameter in ("a0", "a1")
        for row in (1, 2)
        for column in (1, 2)
    ]
    assert all(
        coefficient["matter_scalar_character_exact"] is True
        and coefficient["higgs_correction_character_exact"] is True
        and coefficient["leibniz_identity_exact"] is True
        and coefficient["comparison_residual"]["is_cycle"] is True
        and coefficient["raw_comparison_primitive"]["identity_exact"] is True
        and coefficient["strict_comparison_primitive"]["identity_exact"] is True
        and coefficient["strict_comparison_primitive"]["character_exact"] is True
        and coefficient["complete_scalar_cochain"]["is_cycle"] is True
        and coefficient["complete_scalar_cochain"]["projection_depth"] == 4
        and coefficient["exact"] is True
        for coefficient in coefficients
    )
    assert [
        coefficient["complete_scalar_cochain"]["term_count"]
        for coefficient in coefficients
    ] == [347727, 318099, 345252, 347658, 339381, 302487, 334251, 338754]
    assert [
        coefficient["complete_scalar_cochain"]["digest"]
        for coefficient in coefficients
    ] == [
        "fa10235720171098509b6a1bea684275b32461892c06b95c86734c3da5915d94",
        "afdd62801080f789dede2c25f6ced92f3bbf5e15b7ac9cbbce238d8eab2bf120",
        "347233067350cfed84b35b2fb3700ff62a3c4119fb1b8b4b82d8904413354b1d",
        "053c6f2368c1b0d632275de10538c95f4e4db33732348b3cd287b881d64d0101",
        "679d3b5be95b22a442d431e2f569c7c9edae1e25816a2e8caa9ac4d0c3c8377e",
        "3764325ee618cd961c518615100938eb7328dba8f92f16cc185efd31df446208",
        "102f8a0ab6358bc1ff0ab2db092287ee98ecc3be8f639a120f8f29a5bb695827",
        "387ce320fbdcc037787772cda4dbf1b7c7ff99ee8f71b13a464453cd51ed9433",
    ]
    assert {
        coefficient["complete_scalar_cochain"]["residue"]
        for coefficient in coefficients
    } == {"0"}


def test_neutrino_matrix_is_complete_without_selecting_a_point() -> None:
    """Exterior filtration makes the two-parameter matrix all-orders exact."""

    payload = _payload()
    assert payload["parameter_basis"] == ["a0", "a1"]
    assert payload["first_order_slots"] == [
        [1, 1],
        [1, 2],
        [2, 1],
        [2, 2],
    ]
    assert payload["maximum_exterior_allowed_parameter_order"] == 1
    assert payload["higher_orders_structurally_zero"] is True
    assert payload["all_eight_coefficients_exact"] is True
    assert payload["complete_universal_holomorphic_neutrino_matrix_available"] is True
    assert payload["physical_yukawa_matrix_available"] is False
    assert payload["extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
    assert payload["generic_rank"] in (0, 1, 2)
    assert payload["nontrivial"] is (payload["generic_rank"] > 0)
    assert payload["coefficient_matrices"] == {
        "a0": [["0", "0", "0"]] * 3,
        "a1": [["0", "0", "0"]] * 3,
    }
    assert payload["universal_lower_determinant"] == []
    assert payload["generic_rank"] == 0
    assert payload["nontrivial"] is False
