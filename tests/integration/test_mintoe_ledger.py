"""Check the MinTOE evidence ledger.

Owns:
    Port fidelity against MinTOE's build outputs, the registered-prediction
    hash, the Koide-Brannen measurement, the precision audit and the cores.

Depends on:
    The research ledger, the observation manifest, and pytest.

Must not:
    Retune formulas or treat comparison data as inputs.

Phase 0:
    Regression checks for a research-only ledger.
"""

import json

from research.experiments.mintoe_ledger.ledger import (
    MINTOE_BUILD,
    OUTPUT,
    cores,
    koide,
    mintoe,
    pulls,
    registered_predictions,
)


def test_port_reproduces_mintoe_build_outputs() -> None:
    port = mintoe()
    for key, value in MINTOE_BUILD.items():
        assert abs(port[key] / value - 1) < 1e-9


def test_registered_predictions_are_frozen() -> None:
    registered = json.loads(OUTPUT.read_text())["registered_predictions"]
    assert registered == registered_predictions()
    assert registered["registered_on"] == "2026-10-08"
    assert registered["values"]["delta_CP_PMNS_deg"] == 270.0
    assert registered["values"]["m1_eV"] == 0.0


def test_koide_brannen_holds_within_tau_uncertainty() -> None:
    result = koide()
    assert abs(result["Q_minus_two_thirds"]) < result["Q_sigma_from_tau"]
    assert abs(result["delta_minus_two_ninths"]) < result["delta_sigma_from_tau"]


def test_precision_audit_records_the_superseded_tau_match() -> None:
    table = pulls()
    assert abs(table["mtau_vs_superseded_average"]["relative_difference"]) < 1e-7
    assert -1 < table["mtau_MeV"]["pull"] < -0.5
    assert table["delta_CP_PMNS_deg"]["gaussian_pull_unreliable"]


def test_cores_are_close_but_post_hoc() -> None:
    result = cores()
    v_core = result["ln(MbarP/v) = 12 pi - sqrt3/2"]
    assert abs(v_core["absolute_gap"]) < 0.003
    assert 0.005 < v_core["nominal_post_hoc_probability"] < 0.05
