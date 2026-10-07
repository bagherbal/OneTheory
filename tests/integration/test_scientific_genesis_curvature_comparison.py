"""Check the unfavorable complete H0-H1 comparison without favorable subsets.

Owns:
    Real complete-population join and aggregate checks, dominant-point retention,
    and scientific-scope and original-identity mutation attacks.

Depends on:
    The actual executed H0 and H1 curvature profiles and their research readers.

Must not:
    Use synthetic carrier values, calibrate weights, mistake old validation for
    a blind test, or elevate finite diagnostics into a continuum HYM no-go.

Phase 0:
    Research discovery comparison tests only.
"""

import json
from copy import deepcopy
from functools import cache

import pytest

from research.experiments.scientific_genesis import connection_curvature_comparison as module


@cache
def _actual():
    return json.loads(module.nonunit.OUTPUT.read_bytes()), module.baseline.read_profile(
        expected_digest=module.baseline.PROFILE,
    )


def test_complete_comparison_records_failure_without_using_favorable_validation():
    result = module.summarize()
    assert result["sample_count"] == 2048
    assert result["original_section_count"] == 5345
    assert result["h1_tau_discovery"] > 3000 * result["h0_tau_discovery"]
    assert result["h1_role_tau_discovery"]["validation"] < result["h0_role_tau_discovery"][
        "validation"
    ]
    assert result["whole_population_reference_residual_improves"] is False
    assert result["dominant_points_removed_from_mean"] is False
    assert result["large_l1_point_count_discovery"] == 1185
    assert result["dominant_points_discovery"][0]["ordinal"] == 526
    assert result["h1_trace_target_relative_offset_discovery"] > 1000
    assert result["cause_of_trace_discrepancy_established"] is False
    assert result["continuum_instability_or_hym_no_go_proved"] is False
    assert result["hym_convergence_established"] is False
    assert result["physical_yukawas_available"] is False


@pytest.mark.parametrize("flag", (
    "h2_executed", "conditioning_guard_relaxed", "gauge_is_physical_normalization",
    "old_validation_is_blind", "hym_convergence_established", "physical_yukawas_available",
    "common_stabilized_vacuum_available", "numerical_and_sampling_error_certified",
    "admitted_subset_mean_available", "reference_background_is_ricci_flat", "observations_used",
))
def test_h1_comparison_cannot_promote_its_scientific_scope(flag):
    h1, h0 = _actual()
    changed = deepcopy(h1)
    changed[flag] = True
    with pytest.raises(ValueError, match="scientific boundary"):
        module.validate_h1(changed, h0)


@pytest.mark.parametrize("change", ("remove", "role", "weight", "branch", "mean", "source"))
def test_h1_comparison_preserves_each_identity_weight_and_full_mean(change):
    h1, h0 = _actual()
    changed = deepcopy(h1)
    if change == "remove":
        changed["points"].pop(526)
    elif change == "role":
        changed["points"][526]["role"] = "validation"
    elif change == "weight":
        changed["points"][526]["reference_volume_weight"] *= 2
    elif change == "branch":
        changed["points"][526]["selected_branch"] = [99, 99]
    elif change == "source":
        source = next(iter(changed["source_files_sha256"]))
        changed["source_files_sha256"][source] = "0" * 64
    else:
        changed["full_population_tau_discovery"] = changed["role_tau_discovery"]["validation"]
    with pytest.raises(ValueError):
        module.validate_h1(changed, h0)
