"""Attack retained-root acceleration independently of Newton residuals.

Owns:
    Fraction-pair verification, reciprocal moving roots, strict native ancestry,
    literal receipt restoration, and explicit finite-work failures.

Depends on:
    Existing native cubic certificates and the research retained-root consumer.

Must not:
    Treat mathematical fixtures as carrier outputs, accept proposals without
    certificates, or infer integration accuracy from successful local refinement.

Phase 0:
    Exact mathematical and retained-input regression tests only.
"""

from dataclasses import replace
from fractions import Fraction
from math import comb

import pytest

from onetheory.core.errors import FailedConvergence
from onetheory.math.numbers import Eisenstein, Rational
from onetheory.math.polynomials import Polynomial
from research.experiments.scientific_genesis import retained_root_refinement as module


def _cubic(error=0, coefficients=(0, -1, 1, 0)):
    return module.native.UncertainCubic(tuple(
        module.native.Ball(Eisenstein(value), Rational(error), 128) for value in coefficients
    ))


def _policy(radius=None):
    if radius is None:
        radius = Rational(1, 16)
    return module.native.roots.RootPolicy(radius, 136, 128, 1)


def _parent(offset=None):
    if offset is None:
        offset = Rational(1, 1024)
    cubic, policy = _cubic(), _policy()
    disks = []
    for pivot, root in ((0, 0), (0, 1), (1, 0)):
        polynomial = Polynomial.from_coefficients(
            tuple(c.center for c in cubic.chart_coefficients(pivot)), scalar_type=Eisenstein,
        )
        center = Eisenstein(root + offset, offset)
        disks.append(module.native.UniformRootDisk(cubic, pivot,
            module.native._positive_witness(polynomial, center, policy)))
    return module.native.CompleteUncertainRoots(cubic, tuple(disks))


def _pair(value):
    return Fraction(value.a), Fraction(value.b)


def _add(a, b):
    return a[0] + b[0], a[1] + b[1]


def _multiply(a, b):
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0] - a[1]*b[1]


def _power(value, exponent):
    result = (Fraction(1), Fraction(0))
    for _ in range(exponent):
        result = _multiply(result, value)
    return result


def _independent_disk(disk):
    coefficients = disk.cubic.chart_coefficients(disk.parameter_pivot)
    center = _pair(disk.witness.center)
    for k, actual in enumerate(disk.witness.taylor):
        expected = (Fraction(0), Fraction(0))
        for j in range(k, 4):
            term = _multiply(_pair(coefficients[j].center), _power(center, j-k))
            expected = _add(expected, (comb(j, k)*term[0], comb(j, k)*term[1]))
        assert _pair(actual) == expected
        squared = expected[0]**2 - expected[0]*expected[1] + expected[1]**2
        assert Fraction(disk.witness.modulus_lower[k])**2 <= squared
        assert squared <= Fraction(disk.witness.modulus_upper[k])**2
    witness = disk.witness
    upper_center = Fraction(module.native.roots.modulus_bounds(
        witness.center, coefficients[0].bits)[1])
    radius = Fraction(witness.radius)
    coefficient_error = sum(Fraction(c.radius)*(upper_center + radius)**j
                            for j, c in enumerate(coefficients))
    remainder = Fraction(witness.modulus_upper[0]) + sum(
        Fraction(witness.modulus_upper[j])*radius**j for j in range(2, len(witness.taylor))
    )
    assert Fraction(witness.modulus_lower[1])*radius > remainder + coefficient_error


@pytest.mark.parametrize("error", (0, Rational(1, 2**50)))
def test_seeded_proposals_require_uniform_native_certificates_including_infinity(error):
    parent = _parent()
    family, counts = module.refine_family(_cubic(error), parent,
        _policy(Rational(1, 2**24)), max_steps=8)
    assert all(0 < count <= 8 for count in counts)
    assert module.draws._permutation(family, parent) == (0, 1, 2)
    assert tuple(d.parameter_pivot for d in family.disks) == (0, 0, 1)
    for disk, old in zip(family.disks, parent.disks, strict=True):
        _independent_disk(disk)
        assert disk.witness.radius == Rational(1, 2**24)
        difference = _pair(disk.witness.center - old.witness.center)
        norm = difference[0]**2 - difference[0]*difference[1] + difference[1]**2
        assert norm < Fraction(old.witness.radius - disk.witness.radius)**2


def test_exact_center_keeps_positive_radius_when_coefficients_move():
    parent = _parent(offset=Rational(0))
    family, counts = module.refine_family(_cubic(Rational(1, 2**60)), parent,
        _policy(Rational(1, 2**24)), max_steps=0)
    assert counts == (0, 0, 0)
    assert all(d.witness.radius > 0 for d in family.disks)
    assert family.disks[-1].coefficient_error_bound > 0


@pytest.mark.parametrize("coefficients,error", (((0, -1, 1, 0), 0),
    ((0, 1, 0, 0), 0), ((0, -1, 1, 0), Rational(1, 4))))
def test_unresolved_proposals_do_not_export_roots_or_change_the_parent(coefficients, error):
    parent = _parent()
    receipt = module.native._roots_record(parent)
    with pytest.raises(FailedConvergence):
        module.refine_family(_cubic(error, coefficients), parent,
            _policy(Rational(1, 2**24)), max_steps=0)
    assert module.native._roots_record(parent) == receipt


@pytest.mark.parametrize("cap", (-1, True, 1.0))
def test_work_cap_rejects_invalid_aliases(cap):
    with pytest.raises(ValueError, match="work cap"):
        module.refine_family(_cubic(), _parent(), _policy(Rational(1, 1024)), max_steps=cap)


@pytest.mark.parametrize("radius", (Rational(1, 16), Rational(1, 8)))
def test_equal_or_larger_disks_are_not_refinement(radius):
    with pytest.raises(ValueError, match="smaller radius"):
        module.refine_family(_cubic(), _parent(), _policy(radius), max_steps=8)


def test_saved_subdivision_bounds_restore_literally_and_reject_mutations():
    parent = _parent()
    cubic, policy = parent.cubic, _policy()
    # Reconstruct the original solver's depth-dependent modulus convention.
    disks = tuple(module.native.UniformRootDisk(cubic, d.parameter_pivot,
        module.native._positive_witness(d.witness.polynomial, d.witness.center,
            replace(policy, modulus_bits=139))) for d in parent.disks)
    receipt = module.native._roots_record(module.native.CompleteUncertainRoots(cubic, disks))
    restored = module.restore_family(cubic, receipt, policy)
    assert module.native._roots_record(restored) == receipt
    receipt['root_disks'][0]['uniform_margin'] = '0'
    with pytest.raises(ValueError, match="literally"):
        module.restore_family(cubic, receipt, policy)


@pytest.mark.parametrize("center", (Eisenstein(0), Eisenstein(Rational(1, 3), Rational(1, 3)),
    Eisenstein(Rational(1, 4), Rational(1, 8)), Eisenstein(3, 3)))
def test_receipt_restoration_does_not_guess_subdivision_depth(center):
    with pytest.raises(ValueError, match="midpoint"):
        module._subdivision_depth(center)
