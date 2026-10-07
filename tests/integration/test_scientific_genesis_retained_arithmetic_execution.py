"""Inspect executed whole-population arithmetic evidence without repairing a mean.

Owns:
    The complete raw failure and executed multiprecision native comparisons,
    including original scope and the still-open physical dependency chain.

Depends on:
    Actual immutable population artifacts and original input provenance.

Must not:
    Substitute successful subsets or treat native spot agreement as global accuracy.

Phase 0:
    Executed research evidence only; no physical normalization.
"""

import json
import math
from fractions import Fraction

import pytest

from research.experiments.scientific_genesis import retained_precise_population as module

REQUEST = "60db9b62ad646f9917d7ea641285aa5cdb8df8b254096e4408d06c4234c7db7b"


@pytest.fixture(scope="module")
def actual_request():
    return module.read_request(expected_digest=REQUEST)


def test_complete_binary64_failure_remains_complete_without_a_subset_mean():
    raw = json.loads(module.previous.OUTPUT.read_bytes())
    assert raw["artifact_digest"] == module.RAW
    assert module.full.cloud.inputs._digest({k: v for k, v in raw.items()
        if k != "artifact_digest"}) == module.RAW
    assert [p["ordinal"] for p in raw["points"]] == list(range(2048))
    failed = [p for p in raw["points"] if p["status"] == "unresolved"]
    assert [p["ordinal"] for p in failed] == raw["unresolved_ordinals"]
    assert len(failed) == 12
    assert all(p["reason"] == "actual numerical cover equation residual exceeds policy"
               for p in failed)
    assert not any("population_" in key and "tau" in key for key in raw)
    assert "empirical_reference_volume_discovery" not in raw


@pytest.mark.parametrize("ordinal", (17, 101, 1819, 1980))
def test_actual_multiprecision_request_reuses_all_native_cases_and_full_h1(ordinal, actual_request):
    record = next(p for p in actual_request["multiprecision_method_comparisons"]
                  if p["ordinal"] == ordinal)
    ref = next(p for p in actual_request["independent_native_method_checks"]
               if p["ordinal"] == ordinal)
    native = json.loads((module.full.ROOT / ref["path"]).read_bytes())
    assert record["native_packet_digest"] == native["artifact_digest"] == ref["artifact_digest"]
    assert record["original_sample_digest"] == native["original_sample_digest"]
    assert record["status"] == "computed_comparison"
    assert record["geometry_discovery"]["geometry_working_precision_bits"] == 256
    assert record["geometry_discovery"]["floating_mantissa_bits"] == 53
    assert record["geometry_discovery"]["native_cover_membership_certified"] is False
    assert record["numerical_diagnostics_discovery"]["original_section_count"] == 5345
    low, high = map(Fraction, native["native_weight_interval"])
    assert low <= Fraction(record["numerical_diagnostics_discovery"][
        "omega_quotient_weight_without_pi_cubed_discovery"]) <= high
    native_l1 = native["native_center_diagnostics_discovery"]["h1"]["trace_free_l1"]
    current_l1 = record["numerical_diagnostics_discovery"]["h1"]["trace_free_l1"]
    assert record["h1_relative_l1_difference_discovery"] == current_l1/native_l1-1
    assert actual_request["h1_factor_digest"] == module.previous.nonunit.H1
    assert actual_request["hybrid_or_subset_mean_available"] is False
    assert actual_request["numerical_error_bound_certified"] is False


def test_uniform_complete_result_has_all_original_points_and_no_hybrid_or_physical_promotion():
    from research.experiments.scientific_genesis import audit

    packet = audit._retained_population_summary()
    assert packet["artifact_digest"] == (
        "9f06c6a120f10b3e2b2c0f1507c751e258e8e108ebeadbaa3ef3285687e90ae8")
    assert packet["sample_count"] == 2048 and packet["unresolved_ordinals"] == []
    assert packet["status"] == "computed_discovery"
    assert len(packet["failed_binary64_ordinals"]) == 12
    assert packet["full_population_h0_tau_discovery"] == 1.0413634317367264
    assert packet["full_population_h1_tau_discovery"] == 796.5049768063988
    assert packet["full_population_h1_tau_discovery"] > packet["full_population_h0_tau_discovery"]
    assert all(packet[key] is False for key in (
        "hybrid_or_subset_mean_available", "h1_rebuilt", "h2_executed",
        "hym_convergence_established", "physical_yukawas_available"))
    record = json.loads(module.OUTPUT.read_bytes())
    volume = float(Fraction(record["reference_quotient_volume_exact"]))
    for h in ("h0", "h1"):
        expected = math.fsum(p["reference_volume_weight_discovery"]*p[h]["trace_free_l1"]
                             for p in record["points"])/(2048*2*math.pi*volume*4)
        assert record[f"full_population_{h}_tau_discovery"] == expected
        assert record[f"{h}_role_tau_discovery"]["training"]*0.75 + record[
            f"{h}_role_tau_discovery"]["validation"]*0.25 == pytest.approx(expected)


def test_live_ledger_records_arithmetic_progress_without_enabling_physics():
    from research.experiments.scientific_genesis import audit

    nodes, edges = audit._nodes(), audit._edges()
    claims = {n["id"]: n for n in nodes}
    assert claims["retained_population_arithmetic_resolution"]["status"] == "COMPUTED"
    for identifier in ("retained_polarization_stability", "visible_metrics", "physical_yukawas"):
        assert claims[identifier]["status"] == "BLOCKED"
    state = {"claims": nodes, "dependencies": edges, "fitted_inputs": []}
    state["artifact_digest"] = audit._canonical_digest(state)
    audit.validate_state(state)
    task = next(t for t in audit._scheduler() if t["task"] == "alternate_metric_convergence")
    assert "uniform 256-bit geometry resolves every original input" in task["rationale"]
    assert "independent sampling" in task["rationale"]
