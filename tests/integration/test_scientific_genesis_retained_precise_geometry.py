"""Attack explicit retained-input multiprecision against native geometry.

Owns:
    Exact dyadic recovery, native comparisons, retained equation failures and
    arithmetic-isolation checks without promoting numerical cover membership.

Depends on:
    Actual original inputs, existing native packets and the precise evaluator.

Must not:
    Interpret precision improvement as a uniform bound or hide consumer rounding.

Phase 0:
    Research arithmetic verification only.
"""

import json
from fractions import Fraction

import pytest
from mpmath import mp

from research.experiments.scientific_genesis import retained_numerical_checks as checks
from research.experiments.scientific_genesis import retained_precise_geometry as module


@pytest.fixture(scope="module")
def inputs_and_request():
    request = checks.full.read_request(expected_digest=checks.population.curvature.PARENT_REQUEST)
    inputs = checks.full.cloud.inputs.read_inputs(expected_digest=request["input_digest"],
                                                  path=checks.full.INPUTS)
    return inputs, request


@pytest.mark.parametrize("value", ("0", "1/3", "-7/19", "1e-90", "1e90"))
def test_context_dyadic_recovery_preserves_the_actual_value(value):
    ctx = mp.clone()
    ctx.prec = 256
    x = module._rational(ctx, Fraction(value))
    recovered = module._exact_real(ctx, x)
    assert module._rational(ctx, recovered) == x
    assert recovered.denominator & (recovered.denominator-1) == 0


@pytest.mark.parametrize("ordinal", checks.CASES)
def test_actual_precise_geometry_agrees_with_existing_independent_native_checks(
    ordinal, inputs_and_request,
):
    inputs, request = inputs_and_request
    saved = checks.full._read_sample(request, inputs, ordinal)
    before = mp.prec
    coordinates, weight, record = module.evaluate_geometry(
        checks.full.cloud.inputs.address(inputs, ordinal), saved["history"][0], bits=128,
        steps=8, residual_tolerance=1e-12, volume_scale=1, covering_degree=9, precision_bits=256)
    assert mp.prec == before
    native = json.loads(checks.output_path(ordinal).read_bytes())
    low, high = map(Fraction, native["native_weight_interval"])
    assert low <= Fraction(weight) <= high
    bounds = [v for group in native["native_finer_history"]["coordinate_bounds"] for v in group]
    for point, bound in zip(coordinates, bounds, strict=True):
        center = checks.population.curvature.features._complex(
            checks.population.curvature.Eisenstein(*(Fraction(x) for x in bound["center"])))
        assert abs(point-center) <= float(Fraction(bound["radius"])) + 1e-12*max(1, abs(center))
    assert record["geometry_working_precision_bits"] == 256
    assert record["floating_mantissa_bits"] == 53
    assert record["native_cover_membership_certified"] is False
    assert record["numerical_error_bound_certified"] is False
    assert max(record["cover_equation_residuals_discovery"]) < 1e-12
    assert all(root["candidate_inside_original_disk_exact"] for family in
               record["root_families_discovery"] for root in family)


@pytest.mark.parametrize("ordinal", (345, 478, 587, 711, 735, 967, 1340, 1356,
                                     1610, 1720, 1777, 1981))
def test_each_actual_binary64_failure_retains_its_input_under_explicit_precision(
    ordinal, inputs_and_request,
):
    inputs, request = inputs_and_request
    raw = json.loads(checks.population.sample_path(ordinal).read_bytes())
    assert raw["status"] == "unresolved"
    assert raw["reason"] == "actual numerical cover equation residual exceeds policy"
    saved = checks.full._read_sample(request, inputs, ordinal)
    coordinates, weight, record = module.evaluate_geometry(
        checks.full.cloud.inputs.address(inputs, ordinal), saved["history"][0], bits=128,
        steps=8, residual_tolerance=1e-12, volume_scale=1, covering_degree=9, precision_bits=256)
    assert raw["original_sample_digest"] == saved["artifact_digest"]
    assert coordinates.shape == (8,) and weight > 0
    assert record["selected_branch"] == saved["history"][0]["selected_branch"]
    assert max(record["cover_equation_residuals_discovery"]) < 1e-12


@pytest.mark.parametrize("precision", (True, 53, 127, 256.0))
def test_arithmetic_precision_is_declared_and_not_an_automatic_fallback(precision):
    with pytest.raises(ValueError, match="explicit compatible"):
        module.evaluate_geometry(None, None, bits=128, steps=8, residual_tolerance=1e-12,
            volume_scale=1, covering_degree=9, precision_bits=precision)
