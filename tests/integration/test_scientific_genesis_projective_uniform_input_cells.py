"""Attack the auxiliary projective input law with independent exact and decimal checks.

Owns:
    Independent simplex moments, Chudnovsky/complex-series endpoint checks,
    tied-cell boundaries, refinement, immutability, and explicit input failures.

Depends on:
    Standard-library Fraction and Decimal, existing exact polynomial arithmetic,
    and the research-only projective input cell converter.

Must not:
    Treat regression cells as random draws, claim total-variation convergence,
    generate cover points from centers, or assert physical metric results.

Phase 0:
    Integration input verification only; actual cover sampling is unresolved.
"""

import json
from dataclasses import FrozenInstanceError
from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import product
from math import factorial

import pytest

from onetheory.math.numbers import Rational
from onetheory.math.polynomials import Polynomial
from research.experiments.scientific_genesis import projective_uniform_input_cells as cells


def _decimal(value):
    return Decimal(value.numerator) / Decimal(value.denominator)


def _independent_pi():
    """Chudnovsky, rather than the producer's alternating Machin series."""

    series = sum((Decimal((-1)**k * factorial(6 * k) * (13591409 + 545140134 * k))
                  / Decimal(factorial(3 * k) * factorial(k)**3 * 640320**(3 * k))
                  for k in range(8)), Decimal(0))
    return 426880 * Decimal(10005).sqrt() / series


def _independent_phase(angle):
    """One complex exponential series, not separate sin/cos Taylor implementations."""

    real, imaginary = Decimal(1), Decimal(0)
    term_real, term_imaginary = real, imaginary
    for k in range(1, 160):
        term_real, term_imaginary = (-term_imaginary * angle / k, term_real * angle / k)
        real += term_real
        imaginary += term_imaginary
    return real, imaginary


def _ideal_representative(spacing_values, phase_values):
    ordered = sorted(spacing_values)
    weights = [right - left for left, right in zip((Fraction(0), *ordered),
                                                  (*ordered, Fraction(1)), strict=True)]
    values = [(_decimal(weights[0]).sqrt(), Decimal(0))]
    for weight, phase in zip(weights[1:], phase_values, strict=True):
        real, imaginary = _independent_phase(2 * _independent_pi() * _decimal(phase))
        amplitude = _decimal(weight).sqrt()
        values.append((amplitude * real, amplitude * imaginary))
    return values


def _assert_encloses(cell, spacing_values, phase_values):
    values = _ideal_representative(spacing_values, phase_values)
    assert abs(sum((real**2 + imaginary**2 for real, imaginary in values), Decimal(0))
               - 1) < Decimal("1e-65")
    for disk, (real, imaginary) in zip(cell.coordinates, values, strict=True):
        center_real = _decimal(disk.center.a) - _decimal(disk.center.b) / 2
        center_imaginary = Decimal(3).sqrt() * _decimal(disk.center.b) / 2
        error_squared = (real - center_real)**2 + (imaginary - center_imaginary)**2
        assert error_squared <= _decimal(disk.radius)**2


@pytest.mark.parametrize("dimension", (1, 2))
def test_spacing_density_has_independent_dirichlet_moments(dimension):
    variables = tuple(Polynomial.monomial(tuple(int(i == j) for j in range(dimension)))
                      for i in range(dimension))
    one = Polynomial.constant(1, dimension)
    weights = ((variables[0], one - variables[0]) if dimension == 1 else
               (variables[0], variables[1] - variables[0], one - variables[1]))
    for powers in product(range(4), repeat=dimension + 1):
        integrand = Polynomial.constant(1, dimension)
        for weight, exponent in zip(weights, powers, strict=True):
            integrand *= weight**exponent
        # Direct ordered-domain integration: 0<u<1 or 0<u<v<1.
        actual = sum((Fraction(coefficient.numerator, coefficient.denominator) * (
            Fraction(1, monomial[0] + 1) if dimension == 1 else
            Fraction(2, (monomial[0] + 1) * (sum(monomial) + 2))
        ) for monomial, coefficient in integrand.terms), Fraction(0))
        expected = Fraction(factorial(dimension)
                            * product_factorials(powers), factorial(dimension + sum(powers)))
        assert actual == expected


def product_factorials(powers):
    value = 1
    for exponent in powers:
        value *= factorial(exponent)
    return value


def test_machin_identity_has_exact_positive_complex_argument():
    # (5+i)^4/(239+i) is proportional to 1+i, with positive real part.
    real, imaginary = Fraction(1), Fraction(0)
    for _ in range(4):
        real, imaginary = 5 * real - imaginary, real + 5 * imaginary
    numerator_real, numerator_imaginary = 239 * real + imaginary, 239 * imaginary - real
    assert numerator_real == numerator_imaginary > 0


@pytest.mark.parametrize("terms", (1, 2, 8, 24))
def test_pi_encloses_independent_chudnovsky_value(terms):
    policy = cells.InputPolicy(8, 80, terms, 32)
    interval = cells.pi_interval(policy)
    with localcontext() as context:
        context.prec = 80
        assert _decimal(interval.lower) < _independent_pi() < _decimal(interval.upper)


@pytest.mark.parametrize("spacing,phases", (
    ((0,), (0,)), ((255,), (255,)),
    ((127, 127), (0, 255)), ((0, 255), (128, 64)),
    ((240, 16), (17, 201)), ((0, 0), (0, 0)), ((255, 255), (255, 255)),
))
def test_every_cell_corner_encloses_coupled_unit_representative(spacing, phases):
    cell = cells.projective_input_cell(spacing, phases,
                                       policy=cells.InputPolicy(8, 60, 30, 40))
    n = len(spacing)
    with localcontext() as context:
        context.prec = 80
        for endpoints in product((0, 1), repeat=2 * n):
            values = tuple(Fraction(index + endpoint, 256)
                           for index, endpoint in zip((*spacing, *phases), endpoints, strict=True))
            _assert_encloses(cell, values[:n], values[n:])


def test_refining_original_cells_contracts_certified_input_diameter():
    coarse = cells.projective_input_cell((5, 11), (3, 13),
                                         policy=cells.InputPolicy(4, 60, 30, 40))
    fine = cells.projective_input_cell((5 * 256 + 91, 11 * 256 + 18),
                                       (3 * 256 + 75, 13 * 256 + 11),
                                       policy=cells.InputPolicy(12, 60, 30, 40))
    assert fine.projective_chordal_diameter_bound < coarse.projective_chordal_diameter_bound / 50
    with localcontext() as context:
        context.prec = 80
        midpoint_spacing = tuple(Fraction(2 * k + 1, 8192) for k in fine.spacing_indices)
        midpoint_phases = tuple(Fraction(2 * k + 1, 8192) for k in fine.phase_indices)
        _assert_encloses(coarse, midpoint_spacing, midpoint_phases)
        _assert_encloses(fine, midpoint_spacing, midpoint_phases)


def test_tied_bins_include_zero_spacings_without_rejection():
    cell = cells.projective_input_cell((7, 7), (0, 0),
                                       policy=cells.InputPolicy(4, 48, 24, 32))
    assert cell.spacings[1].lower == Rational(0)
    assert cell.spacings[1].upper == Rational(1, 16)
    assert cell.coordinates[1].radius > 0
    with pytest.raises(FrozenInstanceError):
        cell.coordinates = ()


@pytest.mark.parametrize("invalid", (0, -1, True, 1.5))
@pytest.mark.parametrize("field", range(4))
def test_invalid_precision_or_work_limit_fails(field, invalid):
    arguments = [8, 48, 24, 32]
    arguments[field] = invalid
    with pytest.raises(ValueError, match="positive integers"):
        cells.InputPolicy(*arguments)


@pytest.mark.parametrize("spacing,phases", (
    ((), ()), ((1, 2, 3), (1, 2, 3)), ((1,), ()),
    ((-1,), (1,)), ((256,), (1,)), ((True,), (1,)), ((1,), (256,)),
))
def test_invalid_input_indices_or_dimension_fail_explicitly(spacing, phases):
    with pytest.raises(ValueError):
        cells.projective_input_cell(spacing, phases, policy=cells.InputPolicy(8, 48, 24, 32))


def test_completed_input_record_recomputes_all_actual_disks():
    unsigned = cells.read_input_cells()
    assert cells._digest(unsigned) == (
        "b8db32fa76846ebbc8fba44ff5fcb67b1a92f9961d05f8b61355141d8fd7cade"
    )
    assert len(unsigned["declared_boundary_probes"]) == 4
    assert unsigned["independent_cover_sampling_cloud_available"] is False


@pytest.mark.parametrize("flag", (
    "random_generator_implemented", "independent_cover_sampling_cloud_available",
    "uncertain_input_intersection_roots_certified", "centers_are_exact_cover_points",
    "total_variation_convergence_claimed", "numerical_metrics_available",
    "physical_yukawas_available", "extension_point_selected", "vacuum_selected",
    "observational_inputs_used",
))
def test_rehashed_scope_promotion_fails(tmp_path, flag):
    record = json.loads(cells.OUTPUT.read_text(encoding="utf-8"))
    record.pop("artifact_digest")
    record[flag] = True
    record["artifact_digest"] = cells._digest(record)
    path = tmp_path / "scope.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="bounds, inputs, proof, or scope"):
        cells.read_input_cells(path)


def test_rehashed_coordinate_radius_cannot_discard_input_uncertainty(tmp_path):
    record = json.loads(cells.OUTPUT.read_text(encoding="utf-8"))
    record.pop("artifact_digest")
    record["declared_boundary_probes"][0]["coordinate_disks"][0]["radius"] = "0"
    record["artifact_digest"] = cells._digest(record)
    path = tmp_path / "zero_radius.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="bounds, inputs, proof, or scope"):
        cells.read_input_cells(path)


def test_work_limits_are_not_silently_increased_for_wide_cells():
    policy = cells.InputPolicy(1, 8, 1, 1)
    cell = cells.projective_input_cell((0,), (1,), policy=policy)
    assert cell.policy == policy
    with localcontext() as context:
        context.prec = 80
        _assert_encloses(cell, (Fraction(1, 4),), (Fraction(3, 4),))


def test_refinement_does_not_assume_bound_mesh_resolves_original_bit_cells():
    policy = cells.InputPolicy(12, 8, 8, 20)
    cell = cells.projective_input_cell((300, 200), (1500, 1700), policy=policy)
    with localcontext() as context:
        context.prec = 80
        _assert_encloses(cell, (Fraction(601, 8192), Fraction(401, 8192)),
                         (Fraction(3001, 8192), Fraction(3401, 8192)))


def test_scoped_cell_claim_has_direct_edges_but_does_not_complete_sampling():
    from research.experiments.scientific_genesis import audit

    state = json.loads(audit.OUTPUT.read_text(encoding="utf-8"))
    node = next(n for n in state["claims"] if n["id"] == "projective_uniform_input_cells")
    assert node["status"] == "DERIVED"
    assert "independent uniform input cell indices" in node["assumptions"]
    assert "branch-complete roots for uncertain inputs" in node["missing_prerequisites"]
    edges = {(edge["source"], edge["target"]) for edge in state["dependencies"]}
    assert ("alternate_metric_positive_measure", node["id"]) in edges
    assert (node["id"], "visible_metrics") in edges
    assert state["projective_uniform_input_cells"] == cells.read_input_cells()
    assert state["projective_uniform_input_cells"]["physical_yukawas_available"] is False


@pytest.mark.parametrize("interval", (
    cells.Interval(Rational(-1), Rational(0), 48),
    cells.Interval(Rational(0), Rational(1), 24),
))
def test_phase_bounds_reject_out_of_contract_intervals(interval):
    with pytest.raises(ValueError, match="compatible interval inside the unit cell"):
        cells.phase_rectangles(interval, cells.InputPolicy(8, 48, 24, 32))
