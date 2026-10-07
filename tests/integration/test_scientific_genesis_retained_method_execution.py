"""Inspect actual native comparison packets and their full-population request.

Owns:
    Original identity checks, exact weight-enclosure comparisons and the explicit
    discovery/certification boundary on all four predeclared native outcomes.

Depends on:
    Executed retained native method packets, unchanged inputs and source pins.

Must not:
    Replace failures, infer IID confidence from four cases or certify global
    roundoff, a continuum integral, HYM convergence or physical flavor.

Phase 0:
    Actual executed scientific regression evidence only.
"""

import json
from fractions import Fraction

import pytest

from research.experiments.scientific_genesis import retained_numerical_checks as checks

DIGESTS = {
    17: "80bea55b47b08a47c6cdadf295291666f61f3e2758de48cbe2671e049c66af26",
    101: "65b12b6f099662b73e6c88f1c7e1f9d1b4003498cd7e1cc5df48ad2942546eae",
    1819: "58888e5f5b4697788285947323ba1e81d24948ccc834f7502a14b3f554c46ad2",
    1980: "10101f2920c70c3dd093e9e03fde92ccdf98cf1fb7c2cd96de26475320b1709a",
}
REQUEST = "93b5c88b51d47a6e13a468c1ef80f10c1f409906611b2d9d513d5fff02f777e4"


@pytest.fixture(scope="module")
def original_inputs():
    full = checks.full
    request = full.read_request(expected_digest=checks.population.curvature.PARENT_REQUEST)
    inputs = full.cloud.inputs.read_inputs(expected_digest=request["input_digest"],
                                          path=full.INPUTS)
    return request, inputs, checks._sources()


@pytest.mark.parametrize("ordinal", tuple(DIGESTS))
def test_executed_native_comparison_preserves_original_identity_and_scope(ordinal, original_inputs):
    request, inputs, sources = original_inputs
    full = checks.full
    record = json.loads(checks.output_path(ordinal).read_bytes())
    unsigned = {k: v for k, v in record.items() if k != "artifact_digest"}
    assert record["artifact_digest"] == full.cloud.inputs._digest(unsigned) == DIGESTS[ordinal]
    assert record["source_files_sha256"] == sources
    assert all(record.get(k) == v for k, v in full.cloud.inputs.sample_identity(
        inputs, ordinal).items())
    saved = full._read_sample(request, inputs, ordinal)
    assert record["original_sample_digest"] == saved["artifact_digest"]
    assert record["role"] == saved["role"]
    assert record["status"] == "computed_comparison"
    fine = record["native_finer_history"]
    assert fine["status"] == "admitted" and fine["level"] == 32
    assert fine["root_parent_retained"] is True and fine["frame_parent_retained"] is True
    assert fine["selected_branch"] == saved["history"][0]["selected_branch"]
    assert fine["component"] == saved["history"][0]["component"]
    assert record["geometry_discovery"]["input_prefix_bits"] == 128
    assert record["geometry_discovery"]["native_cover_membership_certified"] is False
    assert all(record[key] is False for key in (
        "new_entropy_obtained", "old_checkpoint_replaced", "numerical_error_bound_certified",
        "global_accuracy_established", "hym_convergence_established", "physical_yukawas_available"))
    low, high = map(Fraction, record["native_weight_interval"])
    assert low <= Fraction(record["numerical_weight_discovery"]) <= high
    native_bounds = [bound for group in fine["coordinate_bounds"] for bound in group]
    for candidate, bound in zip(record["coordinates_real_imag_discovery"], native_bounds,
                                strict=True):
        native = checks.population.curvature.features._complex(
            checks.population.curvature.Eisenstein(*(Fraction(x) for x in bound["center"])))
        # Same comparison policy as the existing native benchmark regression.
        # This engineering allowance is not a numerical error certificate.
        assert abs(complex(*candidate)-native) <= (
            float(Fraction(bound["radius"])) + 1e-12*max(1, abs(native)))
    for key in ("native_center_diagnostics_discovery", "numerical_diagnostics_discovery"):
        assert record[key]["original_section_count"] == 5345
    native_l1 = record["native_center_diagnostics_discovery"]["h1"]["trace_free_l1"]
    numerical_l1 = record["numerical_diagnostics_discovery"]["h1"]["trace_free_l1"]
    assert record["h1_relative_l1_difference_discovery"] == numerical_l1/native_l1 - 1


def test_complete_population_request_binds_all_native_outcomes_without_reselecting_h1():
    population = checks.population
    record = population.read_request(expected_digest=REQUEST)
    actual = {r["ordinal"]: r["artifact_digest"] for r in record["independent_method_checks"]}
    assert actual == DIGESTS
    assert record["sample_count"] == 2048
    assert record["h1_factor_digest"] == population.nonunit.H1
    assert record["old_validation_is_blind"] is False
    assert record["numerical_error_bound_certified"] is False
