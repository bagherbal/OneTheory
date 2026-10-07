"""Check terminal finer-input diagnostics without declaring local convergence.

Owns:
    Actual terminal packet identities, unchanged parent histories and H1,
    retained native ancestry, captured-prefix use and nonphysical result scope.

Depends on:
    Executed finer-resolution packets and their immutable predecessor reader.

Must not:
    Turn two cases into an integral, assert an error bound from a small change,
    rebuild H1, drop difficult points, or claim a physical HYM solution.

Phase 0:
    Research execution checks only; global and physical gates remain open.
"""

import hashlib
import json

import pytest

from research.experiments.scientific_genesis import continue_curvature_resolution as module

DIGESTS = {
    526: "0ac036db82db3adf47aa6ecdad620a97ff15a45b1d4f30eb5e1b37beaa8ac2ea",
    1360: "e44b19d10547bbc60914e7069f42f4b49e2df6449fa7b2e2ab4d16d6d2c1a897",
}


def _actual(ordinal):
    record = json.loads(module.output_path(ordinal).read_bytes())
    assert record["artifact_digest"] == DIGESTS[ordinal]
    assert module.prior.full.cloud.inputs._digest({k: v for k, v in record.items()
                                                 if k != "artifact_digest"}) == DIGESTS[ordinal]
    assert all(hashlib.sha256((module.prior.ROOT / name).read_bytes()).hexdigest() == digest
               for name, digest in record["source_files_sha256"].items())
    return record


@pytest.mark.parametrize("ordinal", tuple(DIGESTS))
def test_terminal_cases_keep_every_predecessor_and_new_admitted_ancestry(ordinal):
    record = _actual(ordinal)
    parent = module.read_prior(ordinal)
    assert record["prior_resolution_digest"] == parent["artifact_digest"]
    assert record["original_history"] == parent["original_history"]
    assert record["history"][:3] == parent["history"]
    assert record["streams"] == parent["streams"]
    assert record["original_sample_digest"] == parent["original_sample_digest"]
    assert record["h1_factor_digest"] == module.prior.nonunit.H1
    assert record["all_prior_geometric_histories_replayed_exactly"] is True
    assert record["levels"] == [16, 20, 24, 28, 32]
    assert record["captured_bits_per_stream"] == 256
    assert record["input_prefix_bits_at_last_level"] == 128
    for item in record["history"][3:]:
        assert item["status"] == "admitted"
        assert item["curvature_status"] == "computed_discovery"
        assert item["root_parent_retained"] is True
        assert item["frame_parent_retained"] is True
        assert item["original_section_count"] == 5345
        assert item["floating_mantissa_bits"] == 53


@pytest.mark.parametrize("ordinal", tuple(DIGESTS))
def test_small_finer_changes_remain_discovery_observations_not_error_bounds(ordinal):
    record = _actual(ordinal)
    previous, last = record["history"][-2:]
    assert abs(last["h1"]["trace_free_l1"] / previous["h1"]["trace_free_l1"] - 1) < 1e-4
    if ordinal == 526:
        assert 1300 < last["h1"]["trace_free_l1"] < 1400
    else:
        assert last["h1"]["trace_free_l1"] > 900000
        assert last["h1"]["fiber_condition_number_discovery"] < 3
    assert record["local_resolution_error_bound_certified"] is False
    assert record["numerical_error_bound_certified"] is False
    assert record["cause_of_trace_discrepancy_established"] is False


@pytest.mark.parametrize("ordinal", tuple(DIGESTS))
def test_complete_diagnostic_cases_cannot_change_the_global_or_physical_scope(ordinal):
    record = _actual(ordinal)
    for flag in ("h1_rebuilt", "new_entropy_obtained", "old_cloud_checkpoint_replaced",
                 "hybrid_or_subset_integral_available", "h2_executed",
                 "hym_convergence_established", "physical_yukawas_available",
                 "common_stabilized_vacuum_available", "observations_used"):
        assert record[flag] is False
    assert "full_population_tau_discovery" not in record
    assert record["parameter_point_status"] == "SELECTED"
    assert record["entropy_assumption_status"] == "ASSUMED"
