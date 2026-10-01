"""Independently verify complete certified roots of actual sampling cubics.

Owns:
    Binomial Taylor reconstruction, squared rational modulus checks, exact root
    counts, precision refinement, infinity branches, and counterfeit rejection.

Depends on:
    Exact polynomial arithmetic and field norms, frozen cubic coefficients,
    and the research projective root construction.

Must not:
    Use residual agreement as root existence, treat proposal centers as exact
    cover points, or claim numerical sampling and metric convergence.

Phase 0:
    Research root-inclusion tests only; physical metrics remain unresolved.
"""

import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
from itertools import combinations
from math import comb

import pytest

from onetheory.core.errors import FailedConvergence
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from onetheory.math.polynomials import Polynomial
from research.experiments.scientific_genesis import alternate_metric_projective_roots as roots


def _policy(bits=30, iterations=128):
    return roots.RootPolicy(Rational(1, 2**bits), 2 * bits, 2 * bits + 20, iterations)


def _configuration(policy=None, p=(1, 1), first=None, pivots=(0, 0)):
    first = first or roots.ProjectiveLine((1, 0, 0), (0, 1, 1))
    second = roots.ProjectiveLine((1, 1, 0), (0, 0, 1))
    return roots.intersection_roots(first, second, p, parameter_pivots=pivots,
                                    policy=policy or _policy())


def _independent_disk_check(disk):
    """Use the binomial theorem, not production derivatives or norm bounds."""

    degree = disk.polynomial.degree
    coefficients = {powers[0]: Eisenstein.coerce(c) for powers, c in disk.polynomial.terms}
    taylor = tuple(sum((coefficient * comb(power, k) * disk.center**(power - k)
                        for power, coefficient in coefficients.items() if power >= k),
                       Eisenstein(0)) for k in range(degree + 1))
    assert taylor == disk.taylor
    for coefficient, lo, hi in zip(taylor, disk.modulus_lower, disk.modulus_upper, strict=True):
        a, b = coefficient.a, coefficient.b
        absolute_squared = a**2 - a * b + b**2
        assert 0 <= lo <= hi
        assert lo**2 <= absolute_squared <= hi**2
    if disk.radius == 0:
        assert taylor[0].is_zero()
        assert not taylor[1].is_zero()
    else:
        dominant = disk.modulus_lower[1] * disk.radius
        remainder = sum((disk.modulus_upper[k] * disk.radius**k
                         for k in range(degree + 1) if k != 1), Rational(0))
        assert dominant > remainder


def _independent_complete_check(result):
    assert len(result.disks) == result.polynomial.degree
    for disk in result.disks:
        _independent_disk_check(disk)
    for first, second in combinations(result.disks, 2):
        difference = first.center - second.center
        a, b = difference.a, difference.b
        assert a**2 - a * b + b**2 > (first.radius + second.radius)**2


def test_actual_cubic_restrictions_have_all_nine_certified_intersections():
    configuration = _configuration()
    assert len(set(configuration.root_pairs)) == 9
    for side in (configuration.first, configuration.second):
        assert side.count == 3
        assert side.infinity_multiplicity == 0
        _independent_complete_check(side.finite)
    # Independently substitute the actual cubic monomials on the chosen lines.
    z = Polynomial.monomial((1,), scalar_type=Eisenstein)
    one = Polynomial.one(1, scalar_type=Eisenstein)
    f_first = one * (-3 - 3 * OMEGA) + z**3 * (3 + 3 * OMEGA)
    g_first = (one + 2 * z**3) * (-3 - 6 * OMEGA)
    g_first += z**2 * (36 + 18 * OMEGA)
    f_second = one * (-3 * OMEGA) + z**3 * (3 * OMEGA)
    g_second = (2 * one + z**3) * (-3 - 6 * OMEGA) + z * (36 + 18 * OMEGA)
    assert configuration.first.finite.polynomial == f_first + g_first
    assert configuration.second.finite.polynomial == 2 * f_second + g_second


def test_precision_refinement_has_unique_root_correspondence_without_fitted_values():
    coarse = _configuration(_policy(25))
    fine = _configuration(_policy(50))
    for first, second in ((coarse.first, fine.first), (coarse.second, fine.second)):
        _independent_complete_check(second.finite)
        for disk in second.finite.disks:
            assert disk.radius <= Rational(1, 2**50)
            containing = []
            for outer in first.finite.disks:
                room = outer.radius - disk.radius
                if room > 0 and (disk.center - outer.center).norm() < room**2:
                    containing.append(outer)
            assert len(containing) == 1


def test_actual_leading_zero_branch_keeps_the_root_at_infinity():
    line = roots.ProjectiveLine((1, 0, 0), (0, 1, -1))
    configuration = _configuration(p=(0, 1), first=line)
    assert configuration.first.finite.polynomial.degree == 2
    assert configuration.first.infinity_multiplicity == 1
    assert configuration.first.count == 3
    assert sum(a == "infinity" for a, _ in configuration.root_pairs) == 3
    assert len(configuration.root_pairs) == 9
    _independent_complete_check(configuration.first.finite)
    alternate = _configuration(p=(0, 1), first=line, pivots=(1, 0))
    assert alternate.first.infinity_multiplicity == 0
    _independent_complete_check(alternate.first.finite)
    assert sum(d.center.norm() <= d.radius**2 for d in alternate.first.finite.disks) == 1


@pytest.mark.parametrize("coefficients,known_roots", (
    ((0, 2, -3, 1), (Eisenstein(0), Eisenstein(1), Eisenstein(2))),
    ((-1, 0, 0, 1), (Eisenstein(1), OMEGA, OMEGA**2)),
))
def test_known_exact_roots_are_enclosed_not_used_to_construct_the_certificates(
    coefficients, known_roots,
):
    polynomial = Polynomial.from_coefficients(coefficients, scalar_type=Eisenstein)
    result = roots.complete_roots(polynomial, _policy())
    _independent_complete_check(result)
    for exact in known_roots:
        assert sum((exact - disk.center).norm() <= disk.radius**2 for disk in result.disks) == 1


def test_real_quadratic_with_nonreal_roots_does_not_get_real_only_proposals():
    polynomial = Polynomial.from_coefficients((1, 0, 1), scalar_type=Eisenstein)
    result = roots.complete_roots(polynomial, _policy())
    _independent_complete_check(result)
    assert result.disks[0].center.b * result.disks[1].center.b < 0


def test_exact_linear_root_needs_no_numerical_approximation():
    polynomial = Polynomial.from_coefficients((OMEGA, Eisenstein(2, 1)), scalar_type=Eisenstein)
    result = roots.complete_roots(polynomial, _policy())
    assert result.iterations == 0
    assert result.disks[0].radius == 0
    assert result.disks[0].center == -OMEGA / Eisenstein(2, 1)
    _independent_complete_check(result)


def test_bad_certificates_cannot_pass_on_a_small_residual_alone():
    polynomial = Polynomial.from_coefficients((-2, 0, 1), scalar_type=Eisenstein)
    result = roots.complete_roots(polynomial, _policy())
    disk = result.disks[0]
    with pytest.raises(ValueError, match="Rouche dominance"):
        replace(disk, radius=Rational(100))
    with pytest.raises(ValueError, match="Taylor coefficients"):
        replace(disk, taylor=(Eisenstein(0), *disk.taylor[1:]))
    with pytest.raises(ValueError, match="modulus bound"):
        replace(disk, modulus_upper=(Rational(0),) * len(disk.taylor))
    with pytest.raises(ValueError, match="exact simple root"):
        replace(disk, radius=Rational(0))
    with pytest.raises(ValueError, match="exhaust"):
        replace(result, disks=result.disks[:1])
    with pytest.raises(ValueError, match="pairwise disjoint"):
        replace(result, disks=(disk, disk))
    with pytest.raises(FrozenInstanceError):
        disk.radius = Rational(100)


def test_nontransverse_intersections_and_exhausted_work_fail_explicitly():
    z = Polynomial.monomial((1,), scalar_type=Eisenstein)
    with pytest.raises(ValueError, match="repeated root"):
        roots.complete_roots((z - Polynomial.one(1, scalar_type=Eisenstein))**2, _policy())
    s = Polynomial.monomial((1, 0), scalar_type=Eisenstein)
    t = Polynomial.monomial((0, 1), scalar_type=Eisenstein)
    with pytest.raises(ValueError, match="at infinity is repeated"):
        roots.projective_roots(s**2 * t, parameter_pivot=0, policy=_policy())
    with pytest.raises(ValueError, match="nonzero homogeneous cubic"):
        roots.projective_roots(Polynomial.zero(2, scalar_type=Eisenstein),
                               parameter_pivot=0, policy=_policy())
    with pytest.raises(FailedConvergence, match="work cap"):
        _configuration(_policy(iterations=1))
    with pytest.raises(ValueError, match="miscounted"):
        replace(_configuration().first, infinity_multiplicity=1)


def test_input_bases_policy_and_exact_scalar_contracts_are_explicit():
    with pytest.raises(ValueError, match="basis is dependent"):
        roots.ProjectiveLine((1, 0, 0), (2, 0, 0))
    with pytest.raises(TypeError):
        roots.ProjectiveLine((1.0, 0, 0), (0, 1, 0))
    with pytest.raises(ValueError, match="P1 point"):
        _configuration(p=(0, 0))
    with pytest.raises(ValueError, match="parameter chart"):
        _configuration(pivots=(True, 0))
    with pytest.raises(ValueError, match="mesh units"):
        roots.RootPolicy(Rational(1, 2**30), 30, 80, 128)
    with pytest.raises(ValueError, match="positive integers"):
        roots.RootPolicy(Rational(1, 2**30), True, 80, 128)
    assert _configuration(p=iter((1, 1))) == _configuration()


def test_saved_actual_configuration_certificates_rebuild_and_verify_independently():
    payload = json.loads(roots.OUTPUT.read_text())
    assert payload == roots.root_artifact()
    digest = payload.pop("artifact_digest")
    assert digest == hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"))
                                    .encode()).hexdigest()

    def scalar(pair):
        return Eisenstein(Fraction(pair[0]), Fraction(pair[1]))

    for configuration in payload["actual_configurations"]:
        assert len(configuration["all_nine_root_pairs"]) == 9
        for side in ("first", "second"):
            record = configuration[side]
            polynomial = Polynomial(((tuple(m), scalar(c)) for m, c in record["finite_polynomial"]),
                                    variable_count=1, scalar_type=Eisenstein)
            disks = tuple(roots.RootDisk(
                polynomial, scalar(disk["center"]), Rational(Fraction(disk["radius"])),
                tuple(scalar(c) for c in disk["taylor"]),
                tuple(Rational(Fraction(c)) for c in disk["modulus_lower"]),
                tuple(Rational(Fraction(c)) for c in disk["modulus_upper"]),
            ) for disk in record["finite_disks"])
            _independent_complete_check(roots.CompleteRoots(
                polynomial, disks, _policy(), record["iterations"],
            ))
            assert len(disks) + record["infinity_multiplicity"] == 3
    for flag in ("centers_are_exact_cover_points", "projective_uniform_sampling_law_implemented",
                 "controlled_numerical_sampling_available", "numerical_metrics_available",
                 "bounded_section_and_density_evaluation_available", "physical_yukawas_available",
                 "extension_point_selected", "vacuum_selected", "observational_inputs_used"):
        assert payload[flag] is False


@pytest.mark.parametrize("value", (Eisenstein(0), Eisenstein(3), Eisenstein(2, 1),
                                   Eisenstein(Rational(1, 7), Rational(-2, 11))))
def test_integer_sqrt_modulus_bounds_are_outward_and_refine(value):
    lo, hi = roots.modulus_bounds(value, 20)
    fine_lo, fine_hi = roots.modulus_bounds(value, 80)
    assert lo**2 <= value.norm() <= hi**2
    assert lo <= fine_lo <= fine_hi <= hi
    if value in (Eisenstein(0), Eisenstein(3)):
        assert lo == hi
    else:
        assert fine_hi - fine_lo < hi - lo
