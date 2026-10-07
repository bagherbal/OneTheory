"""Attack numerical retained-input geometry without promoting it to certification.

Owns:
    Exact-spacing tests, original-root chart preservation, rational disk
    containment, homogeneous weight covariance and actual native comparisons.

Depends on:
    Numerical discovery geometry, existing native receipts and exact polynomials.

Must not:
    Interpret fixtures as physical results or equation residuals as root proofs.

Phase 0:
    Discovery/certification boundary tests only.
"""

import json
from fractions import Fraction

import numpy as np
import pytest

from research.experiments.scientific_genesis import retained_numerical_geometry as module
from research.experiments.scientific_genesis import retained_root_benchmark as benchmark


def _prefix(index, bits):
    return module.certified.draws.BitPrefix(tuple((index >> shift) & 1
                                                for shift in range(bits-1, -1, -1)))


def test_exact_spacings_are_not_lost_when_binary64_uniforms_round_together():
    bits, index = 128, 2**127
    address = module.certified.draws.ProjectiveAddress(
        (_prefix(index, bits), _prefix(index+1, bits)),
        (_prefix(0, bits), _prefix(0, bits)),
    )
    value = module.projective_midpoint(address, bits=bits)
    assert value.shape == (3,)
    assert value[1] != 0
    assert abs(value[1]) == float(Fraction(1, 2**128))**0.5
    assert np.vdot(value, value).real == pytest.approx(1)


@pytest.mark.parametrize("bits", (0, -1, True, 1.0))
def test_input_resolution_is_explicit_and_never_silently_extended(bits):
    address = module.certified.draws.ProjectiveAddress((_prefix(0, 8),), (_prefix(0, 8),))
    with pytest.raises(ValueError, match="prefix length"):
        module.projective_midpoint(address, bits=bits)


def test_exhausted_captured_prefix_is_not_replaced():
    address = module.certified.draws.ProjectiveAddress((_prefix(0, 8),), (_prefix(0, 8),))
    with pytest.raises(module.certified.draws.PrefixExhausted):
        module.projective_midpoint(address, bits=16)


def _root_receipt():
    return {"root_disks": [{"parameter_pivot": pivot,
        "center": [str(Fraction(root) + Fraction(1, 1024)), "1/1024"], "radius": "1/16"}
        for pivot, root in ((0, 0), (0, 1), (1, 0))]}


def test_all_retained_charts_including_infinity_are_preserved_without_native_claims():
    parameters, records = module.numerical_roots((0, -1, 1, 0), _root_receipt(),
                                                steps=8, residual_tolerance=1e-12)
    assert np.allclose(parameters, ((1, 0), (1, 1), (0, 1)), atol=1e-15)
    assert [r["parameter_pivot"] for r in records] == [0, 0, 1]
    assert all(r["candidate_inside_original_disk_exact"] for r in records)
    assert all(r["native_root_certificate_available"] is False for r in records)


def test_small_residual_at_a_different_root_is_not_retained_identity():
    with pytest.raises(ArithmeticError, match="original certified root disk"):
        module.numerical_roots((0, 1, 0, 0), _root_receipt(), steps=8, residual_tolerance=1e-12)


@pytest.mark.parametrize("center,inside", ((0j, True), (complex(1/8), False),
    (complex(1/8 - 2**-55), True), (complex(1/8 + 2**-55), False), (complex(float('nan')), False)))
def test_exact_candidate_containment_does_not_accept_a_boundary_or_nonfinite_number(center, inside):
    assert module.inside_saved_disk(center, {"center": ["0", "0"], "radius": "1/8"}) is inside


def test_restriction_compiles_actual_exact_cubics_in_the_declared_line_basis():
    # An engineering probe of coefficient compilation, not a carrier result.
    basis = np.asarray(((1, 2, 3), (2, -1, 1)), dtype=np.complex128)
    cox = module.certified.native.schoen_geometry().cover.cox
    for program, polynomial in zip(module.pencil_program(), (cox.cubic_f, cox.cubic_g),
                                   strict=True):
        coefficients = module._restrict(program, basis)
        for parameter in (0, 1, 2):
            point = tuple(int(x.real) for x in basis[0] + parameter*basis[1])
            exact = polynomial.substitute(point).coefficient(())
            assert np.dot(coefficients, parameter**np.arange(4)) == pytest.approx(
                module.curvature.features._complex(exact), rel=1e-14)


@pytest.mark.parametrize("ordinal", (526, 1360))
def test_actual_numerical_centers_and_weights_agree_with_independent_native_finer_data(ordinal):
    inputs = module.curvature.full.cloud.inputs.read_inputs(
        expected_digest="cfaac611b57142a0c291a3c3336c6bf34c61c64aecfd3370af50aa0474380d6e",
        path=module.curvature.full.INPUTS)
    record = json.loads(benchmark.output_path(ordinal).read_bytes())
    address = module.curvature.full.cloud.inputs.address(inputs, ordinal)
    coordinates, weight, diagnostics = module.evaluate_geometry(address,
        record["original_history"][-1], bits=128, steps=8, residual_tolerance=1e-12,
        volume_scale=1, covering_degree=9)
    bounds = [value for group in record["finer_history"]["coordinate_bounds"] for value in group]
    for center, bound in zip(coordinates, bounds, strict=True):
        a, b = (Fraction(value) for value in bound["center"])
        native_center = module.curvature.features._complex(module.curvature.Eisenstein(a, b))
        # Binary64 source coordinates cannot generally lie inside a 128-bit
        # input interval. This declared comparison tolerance is not a proof.
        assert abs(center - native_center) <= (float(Fraction(bound["radius"]))
                                               + 1e-12*max(1, abs(native_center)))
    interval = record["finer_history"]["quotient_weight_without_pi_cubed"]
    assert float(Fraction(interval[0])) <= weight <= float(Fraction(interval[1]))
    assert diagnostics["native_cover_membership_certified"] is False
    assert max(diagnostics["cover_equation_residuals_discovery"]) < 1e-12
    x, u, p = coordinates[:3], coordinates[3:6], coordinates[6:]
    scaled, _ = module.homogeneous_weight((x*(2+3j), u*(-5j), p*(7-2j)),
                                         volume_scale=1, covering_degree=9)
    assert scaled == pytest.approx(weight, rel=1e-12)
    other_scale, _ = module.homogeneous_weight((x, u, p), volume_scale=2, covering_degree=9)
    assert other_scale == pytest.approx(4*weight)
