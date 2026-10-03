"""Independently attack uniform uncertain-input projective root certificates.

Owns:
    Fraction-pair Taylor and error reconstruction, actual coefficient checks,
    all auxiliary component branches, moving infinity, and fail-closed attacks.

Depends on:
    Existing exact projective proposals, actual cubic equations, controlled
    input cells, and the research-only uniform root-inclusion construction.

Must not:
    Treat regression cells as independent samples or physical moduli, trust
    residuals as completeness, or assert integration or metric convergence.

Phase 0:
    Admitted-cell mathematical checks only; physical predictions remain absent.
"""

import json
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
from functools import cache
from itertools import combinations
from math import comb, isqrt

import pytest

from onetheory.math.numbers import Eisenstein, Rational
from onetheory.math.polynomials import Polynomial
from research.experiments.scientific_genesis import projective_uncertain_intersections as uncertain
from research.experiments.scientific_genesis.projective_uniform_input_cells import (
    InputPolicy,
    projective_input_cell,
)


def _fraction(value):
    return Fraction(value.numerator, value.denominator)


def _pair(value):
    return _fraction(value.a), _fraction(value.b)


def _add(a, b):
    return a[0] + b[0], a[1] + b[1]


def _multiply(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0] - a[1] * b[1]


def _power(a, exponent):
    result = Fraction(1), Fraction(0)
    for _ in range(exponent):
        result = _multiply(result, a)
    return result


def _norm(value):
    return value[0]**2 - value[0] * value[1] + value[1]**2


def _upper_modulus(value, bits):
    norm = _norm(value)
    scale = 1 << bits
    radicand = norm.numerator * norm.denominator * scale**2
    floor = isqrt(radicand)
    return Fraction(floor + int(floor**2 != radicand), norm.denominator * scale)


def _independent_margin(disk):
    witness = disk.witness
    coefficients = disk.cubic.chart_coefficients(disk.parameter_pivot)
    # Independent binomial substitution; no derivatives or Eisenstein products.
    center = _pair(witness.center)
    reconstructed = []
    for k in range(witness.polynomial.degree + 1):
        value = Fraction(0), Fraction(0)
        for j in range(k, 4):
            term = _multiply(_pair(coefficients[j].center), _power(center, j - k))
            value = _add(value, (comb(j, k) * term[0], comb(j, k) * term[1]))
        reconstructed.append(value)
    assert reconstructed == [_pair(value) for value in witness.taylor]
    for value, lower, upper in zip(reconstructed, witness.modulus_lower,
                                    witness.modulus_upper, strict=True):
        assert _fraction(lower)**2 <= _norm(value) <= _fraction(upper)**2
    radius = _fraction(witness.radius)
    maximum = _upper_modulus(center, coefficients[0].bits) + radius
    error = sum((_fraction(c.radius) * maximum**j for j, c in enumerate(coefficients)),
                Fraction(0))
    remainder = _fraction(witness.modulus_upper[0]) + sum((
        _fraction(value) * radius**k for k, value in enumerate(witness.modulus_upper) if k >= 2
    ), Fraction(0))
    margin = _fraction(witness.modulus_lower[1]) * radius - remainder - error
    assert error == _fraction(disk.coefficient_error_bound)
    assert margin == _fraction(disk.uniform_margin) > 0


def _ball(value, radius=None, bits=100):
    if radius is None:
        radius = Rational(1, 2**30)
    return uncertain.Ball(Eisenstein.coerce(value), radius, bits)


def _policy():
    return uncertain.roots.RootPolicy(Rational(1, 2**12), 64, 100, 128)


@cache
def _actual_inputs():
    policy = InputPolicy(40, 100, 40, 56)
    x = projective_input_cell((2**38, 3 * 2**38), (2**36, 11 * 2**36), policy=policy)
    u = projective_input_cell((5 * 2**37, 7 * 2**37), (5 * 2**36, 13 * 2**36), policy=policy)
    base = projective_input_cell((3 * 2**38,), (7 * 2**36,), policy=policy)
    return x, u, base


@cache
def _actual_components():
    x, u, base = _actual_inputs()
    hx = uncertain.BoundedLine(x.coordinates, 0, (1, 2))
    hu = uncertain.BoundedLine(u.coordinates, 0, (1, 2))
    a = uncertain.line_base_line(hx, hu, base.coordinates, parameter_pivots=(0, 0),
                                 policy=_policy())
    bx = uncertain.point_line(x.coordinates, hu, source_side=1, parameter_pivot=0, policy=_policy())
    bu = uncertain.point_line(u.coordinates, hx, source_side=2, parameter_pivot=0, policy=_policy())
    return a, bx, bu


def test_all_actual_mixture_components_keep_their_complete_root_counts():
    a, bx, bu = _actual_components()
    assert tuple(len(component[0]) for component in (a, bx, bu)) == (9, 3, 3)
    for root_set in (*a[1], bx[1], bu[1]):
        assert len(root_set.disks) == 3
        for disk in root_set.disks:
            _independent_margin(disk)
        assert all(uncertain._projectively_disjoint(left, right)
                   for left, right in combinations(root_set.disks, 2))
    for component in (a, bx, bu):
        for point in component[0]:
            assert tuple(len(factor) for factor in point) == (3, 3, 2)
            assert any(value.radius > 0 for factor in point for value in factor)


@pytest.mark.parametrize("side", (1, 2))
@pytest.mark.parametrize("pivot,axes", ((0, (1, 2)), (1, (2, 0)), (2, (0, 1))))
def test_zero_error_restriction_equals_independent_original_exact_substitution(side, pivot, axes):
    line = uncertain.BoundedLine(tuple(_ball(c, Rational(0)) for c in (1, 2, 3)), pivot, axes)
    base = tuple(_ball(c, Rational(0)) for c in (2, Eisenstein(1, 1)))
    first, second = line.basis
    exact_line = uncertain.roots.ProjectiveLine(tuple(v.center for v in first),
                                               tuple(v.center for v in second))
    expected = uncertain.roots.restrict_pencil(exact_line, tuple(v.center for v in base), side)
    actual = uncertain.actual_restriction(line, base, side=side)
    assert actual.center_polynomial == expected
    assert all(c.radius == 0 for c in actual.coefficients)


@pytest.mark.parametrize("side", (1, 2))
def test_actual_restriction_encloses_independent_exact_input_corner(side):
    line = uncertain.BoundedLine(tuple(_ball(c) for c in (1, 2, 3)), 2, (0, 1))
    base = tuple(_ball(c) for c in (2, 1))
    actual = uncertain.actual_restriction(line, base, side=side)
    # Corner of the original covector/base cell, not its computed line-center box.
    eps = Eisenstein(Rational(1, 2**30))
    h = tuple(v.center + eps for v in line.covector)
    exact = uncertain.roots.ProjectiveLine((1, 0, -h[0] / h[2]), (0, 1, -h[1] / h[2]))
    restriction = uncertain.roots.restrict_pencil(exact, tuple(v.center - eps for v in base), side)
    assert all(value.contains(restriction.coefficient((3 - j, j)))
               for j, value in enumerate(actual.coefficients))


def test_actual_infinity_branch_moves_but_stays_in_reciprocal_disk():
    line = uncertain.BoundedLine(tuple(_ball(c) for c in (0, 1, 1)), 2, (0, 1))
    base = tuple(_ball(c) for c in (0, 1))
    cubic = uncertain.actual_restriction(line, base, side=1)
    assert cubic.center_polynomial.coefficient((0, 3)).is_zero()
    assert cubic.coefficients[3].radius > 0
    complete = uncertain.complete_uncertain_roots(cubic, parameter_pivot=0, policy=_policy())
    reciprocal = [disk for disk in complete.disks if disk.parameter_pivot == 1]
    assert len(reciprocal) == 1
    assert reciprocal[0].witness.center.is_zero()
    assert reciprocal[0].witness.radius > 0
    for disk in complete.disks:
        _independent_margin(disk)
    # The old fixed infinity marker would be wrong for this actual perturbed family.
    exact_line = uncertain.roots.ProjectiveLine((1, 0, 0), (0, 1, -1))
    moved = uncertain.roots.restrict_pencil(exact_line, (Rational(1, 2**31), 1), 1)
    assert all(c.contains(moved.coefficient((3 - j, j)))
               for j, c in enumerate(cubic.coefficients))
    assert not moved.coefficient((0, 3)).is_zero()
    refined = uncertain.roots.RootPolicy(Rational(1, 2**20), 80, 100, 128)
    exact = uncertain.roots.projective_roots(moved, parameter_pivot=1, policy=refined)
    assert exact.infinity_multiplicity == 0
    assert any(d.center.norm() < (reciprocal[0].witness.radius - d.radius)**2
               for d in exact.finite.disks)


def test_opposite_chart_origins_are_projectively_distinct_not_equal_complex_centers():
    cubic = uncertain.UncertainCubic(tuple(_ball(c, Rational(0)) for c in (0, -1, 1, 0)))
    origins = tuple(uncertain.UniformRootDisk(cubic, pivot, uncertain._positive_witness(
        Polynomial.from_coefficients(tuple(c.center for c in cubic.chart_coefficients(pivot)),
                                     scalar_type=Eisenstein), Eisenstein(0), _policy(),
    )) for pivot in (0, 1))
    assert {disk.parameter_pivot for disk in origins} == {0, 1}
    assert uncertain._projectively_disjoint(*origins)


def test_same_projective_root_in_opposite_charts_cannot_be_counted_twice():
    cubic = uncertain.UncertainCubic(tuple(_ball(c, Rational(0)) for c in (0, -1, 1, 0)))
    duplicate = tuple(uncertain.UniformRootDisk(cubic, pivot, uncertain._positive_witness(
        Polynomial.from_coefficients(tuple(c.center for c in cubic.chart_coefficients(pivot)),
                                     scalar_type=Eisenstein), Eisenstein(1), _policy(),
    )) for pivot in (0, 1))
    assert not uncertain._projectively_disjoint(*duplicate)


def test_duplicate_projective_root_witnesses_cannot_certify_completeness():
    root_set = _actual_components()[0][1][0]
    with pytest.raises(ValueError, match="overlap"):
        replace(root_set, disks=(root_set.disks[0],) * 3)
    with pytest.raises(ValueError, match="three same-family"):
        replace(root_set, disks=root_set.disks[:2])


def test_coefficient_error_cannot_be_removed_by_reusing_exact_center_witnesses():
    disk = _actual_components()[0][1][0].disks[0]
    widened = uncertain.UncertainCubic(tuple(_ball(v.center, Rational(10))
                                             for v in disk.cubic.coefficients))
    with pytest.raises(ValueError, match="strict uniform one-root margin"):
        replace(disk, cubic=widened)


def test_zero_radius_or_unrelated_polynomial_witness_is_rejected():
    cubic = uncertain.UncertainCubic(tuple(_ball(c) for c in (0, -1, 1, 0)))
    exact = uncertain.roots.certify_disk(Polynomial.from_coefficients((0, -1, 1),
        scalar_type=Eisenstein), Eisenstein(0), Rational(1, 4096), 100)
    assert exact.radius == 0
    with pytest.raises(ValueError, match="positive-radius"):
        uncertain.UniformRootDisk(cubic, 0, exact)
    with pytest.raises(FrozenInstanceError):
        cubic.coefficients = ()


@pytest.mark.parametrize("pivot,axes", ((True, (1, 2)), (0, (0, 1)), (0, (1, 1))))
def test_invalid_explicit_line_frame_fails(pivot, axes):
    with pytest.raises(ValueError, match="explicit pivot"):
        uncertain.BoundedLine(tuple(_ball(c) for c in (1, 2, 3)), pivot, axes)


def test_pivot_and_source_base_uncertainty_cannot_trigger_silent_fallback():
    with pytest.raises(ZeroDivisionError, match="may contain zero"):
        uncertain.BoundedLine(tuple(_ball(c) for c in (0, 1, 1)), 0, (1, 2))
    source = tuple(_ball(c, Rational(10)) for c in (1, 0, 0))
    line = uncertain.BoundedLine(tuple(_ball(c) for c in (1, 2, 3)), 2, (0, 1))
    with pytest.raises(ValueError, match="pencil base point"):
        uncertain.point_line(source, line, source_side=1, parameter_pivot=0, policy=_policy())


def test_zero_polynomial_possible_in_the_coefficient_cell_is_rejected():
    with pytest.raises(ValueError, match="zero polynomial"):
        uncertain.UncertainCubic(tuple(_ball(0) for _ in range(4)))


def test_mixed_bound_precisions_and_invalid_chart_fail():
    with pytest.raises(ValueError, match="same declared precision"):
        uncertain.UncertainCubic(tuple(_ball(1, bits=bits) for bits in (100, 100, 80, 100)))
    cubic = uncertain.UncertainCubic(tuple(_ball(c) for c in (-1, 0, 0, 1)))
    with pytest.raises(ValueError, match="explicit binary parameter chart"):
        cubic.chart_coefficients(True)


def test_completed_packet_replays_actual_admitted_cell_witnesses():
    record = uncertain.read_uncertain_intersections()
    assert uncertain._digest(record) == (
        "97981cfe6a6d67fd40287c8902a99f4ce3a73729fea6a64b4f133fdce82c0d26"
    )
    assert [component["complete_root_count"] for component in
            record["all_mixture_component_probes"]] == [9, 3, 3]
    assert len(record["moving_infinity_probe"]["root_disks"]) == 3
    assert record["independent_cover_sampling_cloud_available"] is False


@pytest.mark.parametrize("field", (
    "centers_are_exact_cover_points", "independent_cover_sampling_cloud_available",
    "global_numeric_input_coverage_certified", "input_cell_rejection_used_as_resampling",
    "new_domain_density_and_section_bounds_available", "integration_error_control_available",
    "numerical_metrics_available", "physical_yukawas_available", "extension_point_selected",
    "vacuum_selected", "observational_inputs_used",
))
def test_rehashed_sampling_or_physical_scope_promotion_fails(tmp_path, field):
    record = json.loads(uncertain.OUTPUT.read_text(encoding="utf-8"))
    record.pop("artifact_digest")
    record[field] = True
    record["artifact_digest"] = uncertain._digest(record)
    path = tmp_path / "scope.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="roots, inputs, proof, or scope"):
        uncertain.read_uncertain_intersections(path)


def test_rehashed_uniform_margin_cannot_be_fabricated(tmp_path):
    record = json.loads(uncertain.OUTPUT.read_text(encoding="utf-8"))
    record.pop("artifact_digest")
    record["all_mixture_component_probes"][0]["root_families"][0]["root_disks"][0][
        "uniform_margin"
    ] = "999"
    record["artifact_digest"] = uncertain._digest(record)
    path = tmp_path / "margin.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="roots, inputs, proof, or scope"):
        uncertain.read_uncertain_intersections(path)


def test_admitted_cell_node_cannot_complete_sampling_or_physical_normalization():
    from research.experiments.scientific_genesis import audit

    state = json.loads(audit.OUTPUT.read_text(encoding="utf-8"))
    node = next(node for node in state["claims"]
                if node["id"] == "projective_uncertain_intersections")
    assert node["status"] == "COMPUTED"
    assert "strict uniform root margins" in node["assumptions"]
    assert "law-preserving independent bit-stream workflow" in node["missing_prerequisites"]
    edges = {(edge["source"], edge["target"]) for edge in state["dependencies"]}
    assert ("projective_uniform_input_cells", node["id"]) in edges
    assert ("alternate_metric_projective_roots", node["id"]) in edges
    assert (node["id"], "visible_metrics") in edges
    record = state["projective_uncertain_intersections"]
    assert record["global_numeric_input_coverage_certified"] is False
    assert record["physical_yukawas_available"] is False
