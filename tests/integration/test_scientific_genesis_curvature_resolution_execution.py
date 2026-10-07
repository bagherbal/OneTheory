"""Check executed same-input sensitivity and an exact conditional curvature bound.

Owns:
    Actual immutable diagnostic-case identities, resolution outcomes, ancestry
    and scientific scope, plus the rank-four positive-curvature trace inequality.

Depends on:
    The executed retained-input packets, exact Rational arithmetic, and the
    independently normalized Chern-Weil targets on the declared reference class.

Must not:
    Replace the full cloud with two points, treat apparent plateaus as error
    bounds, or infer physical instability from an inaccurate empirical integral.

Phase 0:
    Research diagnostic and conditional-theorem checks; no physical metric export.
"""

import hashlib
import json
from fractions import Fraction
from itertools import product

import pytest

from onetheory.math.numbers import Rational
from research.experiments.scientific_genesis import retained_curvature_resolution as module

DIGESTS = {
    526: "8ef99ba30b04be60b9820f6a75ecaed3767bcb4a22e4491aa78d742b21071604",
    1360: "d8017c86955b985a5e5793374811e07f63873e638bfefbf4242d1ae7df553c07",
}


def _actual(ordinal):
    record = json.loads(module.output_path(ordinal).read_bytes())
    assert record["artifact_digest"] == DIGESTS[ordinal]
    assert module.full.cloud.inputs._digest({k: v for k, v in record.items()
                                           if k != "artifact_digest"}) == DIGESTS[ordinal]
    assert all(hashlib.sha256((module.ROOT / name).read_bytes()).hexdigest() == digest
               for name, digest in record["source_files_sha256"].items())
    return record


@pytest.mark.parametrize("ordinal", tuple(DIGESTS))
def test_executed_refinement_preserves_original_geometry_and_every_ancestry(ordinal):
    record = _actual(ordinal)
    assert record["original_sample_digest"] == module.SAMPLES[ordinal]
    assert record["original_section_count"] == 5345
    assert record["h1_factor_digest"] == module.nonunit.H1
    assert record["h1_profile_digest"] == module.comparison.H1_PROFILE
    assert record["original_geometry_reproduced_exactly"] is True
    assert len(record["streams"]) == 13
    assert record["levels"] == [16, 20, 24]
    assert record["work_cap_per_level"] == 65536
    # Drop only the newly computed curvature fields, not geometric fields.
    geometry = {key: value for key, value in record["history"][0].items()
                if key in record["original_history"][0] and key not in (
                    "floating_mantissa_bits", "complete_original_sections_consumed")}
    module.check_original_geometry(geometry, record["original_history"][0])
    assert record["history"][0]["h0_relative_l1_change_from_original_discovery"] == 0
    assert record["history"][0]["h1_relative_l1_change_from_original_discovery"] == 0
    for item in record["history"]:
        assert item["status"] == "admitted"
        assert item["curvature_status"] == "computed_discovery"
        assert item["floating_mantissa_bits"] == 53
        assert item["original_section_count"] == 5345
        assert item["frame_policy"]["input_center_bits"] == 8 * item["level"]
        assert item["fiber_basis_labels"] == record["original_history"][0]["fiber_basis_labels"]
        assert item["reference_volume_weight_discovery"] > 0
        if item["level"] > 16:
            assert item["root_parent_retained"] is True
            assert item["frame_parent_retained"] is True


def test_point_526_is_strongly_resolution_sensitive_without_an_asserted_plateau():
    coarse, medium, fine = _actual(526)["history"]
    assert fine["h1"]["trace_free_l1"] < coarse["h1"]["trace_free_l1"] / 10000
    assert medium["h1"]["trace_free_l1"] > 6 * fine["h1"]["trace_free_l1"]
    assert fine["h0"]["trace_free_l1"] < coarse["h0"]["trace_free_l1"] / 30
    assert abs(fine["reference_volume_weight_discovery"] /
               coarse["reference_volume_weight_discovery"] - 1) < 1e-5


def test_point_1360_retains_large_curvature_at_a_well_conditioned_refined_frame():
    coarse, medium, fine = _actual(1360)["history"]
    assert fine["h1"]["trace_free_l1"] < coarse["h1"]["trace_free_l1"] / 5
    assert fine["h1"]["trace_free_l1"] > 900000
    assert fine["h1"]["fiber_condition_number_discovery"] < 3
    assert abs(fine["h1"]["trace_free_l1"] / medium["h1"]["trace_free_l1"] - 1) < 0.01


@pytest.mark.parametrize("ordinal", tuple(DIGESTS))
def test_diagnostic_cases_cannot_be_a_hybrid_integral_or_physical_metric(ordinal):
    record = _actual(ordinal)
    for flag in (
        "new_entropy_obtained", "old_cloud_checkpoint_replaced",
        "hybrid_or_subset_integral_available", "h2_executed", "numerical_error_bound_certified",
        "cause_of_trace_discrepancy_established", "hym_convergence_established",
        "physical_yukawas_available", "common_stabilized_vacuum_available", "observations_used",
    ):
        assert record[flag] is False
    assert "post-selected" in record["case_selection"]
    assert record["parameter_point_status"] == "SELECTED"
    assert record["entropy_assumption_status"] == "ASSUMED"
    assert "full_population_tau_discovery" not in record


@pytest.mark.parametrize("signs", tuple(product((-1, 1), repeat=4)))
def test_every_exact_trace_free_sign_functional_is_bounded_on_the_positive_cone(signs):
    """These 16 functionals exhaust the absolute norm, not a finite eigenvalue sample."""

    mean_sign = Rational(sum(signs), 4)
    coefficients = tuple(Rational(sign) - mean_sign for sign in signs)
    assert all(coefficient <= Rational(3, 2) for coefficient in coefficients)


def test_the_sharp_conditional_continuum_tau_bound_uses_the_actual_c1_and_volume():
    targets = module.comparison.baseline.normalization_targets()
    trace_average_over_pi = Fraction(targets["trace_integral_pi_coefficient_exact"]) / Fraction(
        targets["quotient_volume_exact"]
    )
    assert trace_average_over_pi == 24
    assert Fraction(3, 2) * trace_average_over_pi / (2 * 4) == Fraction(9, 2)
    # Rank-one extreme ray attains the pointwise inequality exactly.
    eigenvalues = (Rational(1), Rational(0), Rational(0), Rational(0))
    mean = sum(eigenvalues, Rational(0)) / 4
    assert sum((abs(value - mean) for value in eigenvalues), Rational(0)) == Rational(3, 2)
