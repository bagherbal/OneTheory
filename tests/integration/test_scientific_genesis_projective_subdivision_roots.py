"""Independently attack subdivision certificates on actual native cubic families.

Owns:
    Fraction-pair Taylor checks, exact mathematical roots, reciprocal branches,
    finite failures, retained addresses and trusted source/scope reconstruction.

Depends on:
    Native uncertain cubic and coupled-input certificates, the explicit research
    subdivision method and pytest for exact assertions and failure probes.

Must not:
    Call regression addresses IID, equate centers with cover points, discard
    finite-prefix failures or infer a physical metric from root admission.

Phase 0:
    Conditional mathematical admission tests; no physical output is claimed.
"""

import copy
import json
from fractions import Fraction
from itertools import combinations
from math import comb

import pytest

from onetheory.core.errors import FailedConvergence
from onetheory.math.numbers import Eisenstein, Rational
from research.experiments.scientific_genesis import projective_subdivision_roots as module

DIGEST = "27169bb7b404a863bee7791512169e03ab9ad3790596cd3baf1736c0f58ff768"


def _pair(value):
    return Fraction(str(value.a)), Fraction(str(value.b))


def _add(a, b):
    return a[0]+b[0], a[1]+b[1]


def _mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]-a[1]*b[1]


def _power(a, n):
    result = (Fraction(1), Fraction(0))
    for _ in range(n):
        result = _mul(result, a)
    return result


def _norm(a):
    return a[0]**2-a[0]*a[1]+a[1]**2


def _independent_certificate(disk):
    coefficients = disk.cubic.chart_coefficients(disk.parameter_pivot)
    center = _pair(disk.witness.center)
    for k, value in enumerate(disk.witness.taylor):
        expected = (Fraction(0), Fraction(0))
        for j in range(k, 4):
            term = _mul(_pair(coefficients[j].center), _power(center, j-k))
            expected = _add(expected, (comb(j, k)*term[0], comb(j, k)*term[1]))
        assert _pair(value) == expected
        lo = Fraction(str(disk.witness.modulus_lower[k]))
        hi = Fraction(str(disk.witness.modulus_upper[k]))
        assert lo**2 <= _norm(expected) <= hi**2
    assert disk.uniform_margin > 0 and disk.witness.radius > 0


def _cubic(coefficients, error=0):
    return module.native.UncertainCubic(tuple(module.native.Ball(Eisenstein.coerce(c), error, 80)
                                             for c in coefficients))


def _policy(order=(0, 1), radius=None, cells=10000, depth=24):
    if radius is None:
        radius = Rational(1, 32)
    return module.SubdivisionPolicy(radius, 80, cells, depth, order)


@pytest.mark.parametrize("order", ((0, 1), (1, 0)))
@pytest.mark.parametrize("large_root", (Rational(1), Rational(10**20)))
def test_two_explicit_charts_exhaust_exact_roots_without_affine_size_assumptions(order, large_root):
    # s*t*(t-s) includes infinity; t*(t-s)*(t-large_root*s) does not.
    if large_root == 1:
        cubic = _cubic((0, -1, 1, 0))
        roots = ((1, 0), (1, 1), (0, 1))
    else:
        cubic = _cubic((0, large_root, -1-large_root, 1))
        roots = ((1, 0), (1, 1), (1, large_root))
    result = module.complete_subdivision_roots(cubic, _policy(order))
    assert len(result.roots.disks) == 3
    for disk in result.roots.disks:
        _independent_certificate(disk)
        matches = []
        for s, t in roots:
            if (s if disk.parameter_pivot == 0 else t) == 0:
                continue
            z = Rational(t)/s if disk.parameter_pivot == 0 else Rational(s)/t
            difference = _add(_pair(Eisenstein(z)), tuple(-v for v in _pair(disk.witness.center)))
            if _norm(difference) < Fraction(str(disk.witness.radius))**2:
                matches.append((s, t))
        assert len(matches) == 1
    assert result.examined_cells <= result.policy.max_cells
    assert result.deepest_level <= result.policy.max_depth
    assert result.zero_free_cells > 0


def test_uncertain_leading_coefficient_keeps_a_moving_positive_reciprocal_root():
    cubic = _cubic((0, -1, 1, 0), Rational(1, 2**30))
    result = module.complete_subdivision_roots(cubic, _policy())
    assert any(d.parameter_pivot == 1 and d.witness.center.norm() < d.witness.radius**2
               for d in result.roots.disks)
    for disk in result.roots.disks:
        _independent_certificate(disk)
        assert disk.coefficient_error_bound > 0


@pytest.mark.parametrize("coefficients", ((0, 1, 0, 0), (0, Rational(1, 1024),
                                                        -1-Rational(1, 1024), 1)))
def test_repeated_or_unresolved_clustered_roots_are_not_merged_into_completeness(coefficients):
    with pytest.raises(FailedConvergence):
        module.complete_subdivision_roots(_cubic(coefficients), _policy(cells=1500, depth=13))


@pytest.mark.parametrize("cells,depth", ((1, 24), (10000, 1)))
def test_finite_work_limits_are_explicit_failures_not_exclusion_certificates(cells, depth):
    with pytest.raises(FailedConvergence, match="cap"):
        module.complete_subdivision_roots(_cubic((0, -1, 1, 0)), _policy(cells=cells, depth=depth))


@pytest.mark.parametrize("order", ((0, 0), (0,), (True, 0), (0, 2)))
def test_missing_or_implicit_parameter_atlas_is_rejected(order):
    with pytest.raises(ValueError, match="charts"):
        _policy(order)


def test_actual_native_components_without_old_proposer(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("the old simultaneous proposer must not be invoked")

    module.complete_subdivision_roots.cache_clear()
    monkeypatch.setattr(module.native.roots, "complete_roots", forbidden)
    policy = module.draws.declared_policy()
    for component, address, count in zip(("A", "Bx", "Bu"), module.draws.declared_addresses(),
                                          (9, 3, 3), strict=True):
        draw = module.attempt_subdivision_draw(address, policy, max_cells=20000, max_depth=28,
                                               chart_order=(0, 1))
        assert isinstance(draw, module.draws.CoupledDraw)
        assert draw.address == address and address.choices()[0] == component
        assert len(draw.configuration.root_pairs) == count
        c = draw.configuration
        root_sets = ((c.first, c.second)
                     if isinstance(c, module.native.LineBaseLineConfiguration) else (c.partner,))
        for roots in root_sets:
            for disk in roots.disks:
                _independent_certificate(disk)
            for a, b in combinations(roots.disks, 2):
                ca, cb = _pair(a.witness.center), _pair(b.witness.center)
                ra, rb = map(lambda v: Fraction(str(v)), (a.witness.radius, b.witness.radius))
                if a.parameter_pivot == b.parameter_pivot:
                    assert _norm(_add(ca, tuple(-v for v in cb))) > (ra+rb)**2
                else:
                    numerator = _add(_mul(ca, cb), (Fraction(-1), Fraction(0)))
                    ua = Fraction(str(module.native.roots.modulus_bounds(a.witness.center, 100)[1]))
                    ub = Fraction(str(module.native.roots.modulus_bounds(b.witness.center, 100)[1]))
                    assert ua**2 >= _norm(ca) and ub**2 >= _norm(cb)
                    assert _norm(numerator) > (ua*rb + ub*ra + ra*rb)**2
        # Weights consume actual coupled configurations, not off-cover centers.
        weight = module.draws.selected_weight(draw, volume_scale=1, covering_degree=9)
        assert weight.cover_weight_without_pi_cubed.lower > 0
        assert weight.quotient_weight_without_pi_cubed.lower > 0


def test_failed_same_address_stays_pending_and_can_be_admitted_with_more_declared_work():
    address = module.draws.declared_addresses()[0]
    policy = module.draws.declared_policy()
    pending = module.attempt_subdivision_draw(address, policy, max_cells=1, max_depth=28,
                                              chart_order=(0, 1))
    assert isinstance(pending, module.draws.PendingDraw)
    assert pending.address == address and "cap" in pending.reason
    result = module.attempt_subdivision_draw(pending.address, policy, max_cells=20000, max_depth=28,
                                             chart_order=(0, 1))
    assert isinstance(result, module.draws.CoupledDraw) and result.address == pending.address


def test_refinement_schedule_supplies_no_bits_or_chosen_physical_parameter():
    frames = module.draws.declared_policy()
    for j in (2, 8, 32):
        policy, work = module.refinement_policy(j, first_frame=frames.first,
                                                second_frame=frames.second)
        assert policy.input.cell_bits == 4*j and policy.input.bound_bits == 8*j
        assert policy.root.radius == Rational(1, 2**j)
        assert work == {"max_cells": 2**(8*j), "max_depth": 4*j, "chart_order": (0, 1)}
        assert (policy.first, policy.second) == (frames.first, frames.second)


def test_subdivision_continuation_retains_native_parent_across_a_failed_work_cap():
    record = module.subdivision_record()
    assert record["native_root_continuation_controller_executed"] is True
    assert record["full_frame_or_integrand_controller_executed"] is False
    assert len(record["same_stream_root_continuations"]) == 3
    for continued in record["same_stream_root_continuations"]:
        parent, pending, child = (continued[k] for k in ("parent", "retained_pending", "child"))
        assert parent["status"] == child["status"] == "admitted"
        assert pending["status"] == "unresolved" and pending["admitted_parent_retained"] is True
        assert pending["address"] == child["address"]
        for name in ("first", "second", "base"):
            for group in ("spacing", "phases"):
                for before, after in zip(parent["address"][name][group],
                                         child["address"][name][group], strict=True):
                    assert len(before) == 32 and len(after) == 48 and after.startswith(before)
        for name in ("component", "first_root", "second_root"):
            assert child["address"][name] == parent["address"][name]
        assert parent["policy"]["input"]["cell_bits"] == 32
        assert child["policy"]["input"]["cell_bits"] == 48


def test_explicit_method_change_continues_an_old_proposer_parent_instead_of_reselecting():
    from dataclasses import replace

    parent = module.draws.declared_draws()[0]
    fine = replace(parent.policy, input=replace(parent.policy.input, cell_bits=48),
                   root=replace(parent.policy.root, radius=Rational(1, 2**16)))
    result = module.refine_subdivision_draw(parent, parent.address, fine,
        max_cells=20000, max_depth=32, chart_order=(1, 0))
    assert isinstance(result, module.draws.CoupledDraw)
    assert result.admitted_parent == parent and result.address == parent.address
    assert result.branch == module.draws._continued_branch(result.configuration, parent)
    old = parent.configuration
    new = result.configuration
    for new_roots, old_roots in ((new.first, old.first), (new.second, old.second)):
        permutation = module.draws._permutation(new_roots, old_roots)
        assert set(permutation) == {0, 1, 2}
        for disk, index in zip(new_roots.disks, permutation, strict=True):
            assert module.draws._inside(disk, old_roots.disks[index])


@pytest.mark.parametrize("change", ("prefix", "line", "precision", "radius"))
def test_continuation_rejects_replaced_streams_frames_or_decreased_precision(change):
    from dataclasses import replace

    address = module.draws.declared_addresses()[0]
    policy = module.draws.declared_policy()
    pending = module.attempt_subdivision_draw(address, policy, max_cells=1, max_depth=28,
                                             chart_order=(0, 1))
    if change == "prefix":
        address = replace(address, component=module.draws.BitPrefix((1, 1, 1)))
    elif change == "line":
        policy = replace(policy, first=module.draws.LineFrame(0, (2, 1), 0))
    elif change == "precision":
        policy = replace(policy, input=replace(policy.input, cell_bits=39))
    else:
        policy = replace(policy, root=replace(policy.root, radius=2*policy.root.radius))
    with pytest.raises(ValueError, match="prefix|frames|precision"):
        module.refine_subdivision_draw(pending, address, policy, max_cells=20000, max_depth=28,
                                       chart_order=(0, 1))


def test_prefix_exhaustion_retains_the_original_address_without_constructing_a_root():
    from dataclasses import replace

    address = replace(module.draws.declared_addresses()[0],
                      first_root=module.draws.BitPrefix((1, 1)))
    pending = module.attempt_subdivision_draw(address, module.draws.declared_policy(),
        max_cells=20000, max_depth=28, chart_order=(0, 1))
    assert isinstance(pending, module.draws.PendingDraw)
    assert pending.address == address and pending.stage == "prefix"


def test_declared_exposure_grows_source_prefixes_without_fabricating_selector_bits():
    from dataclasses import replace

    available = module.draws.declared_addresses()[0]
    early = module.refinement_address(available, 8)
    late = module.refinement_address(available, 12)
    assert late.extends(early) and early.first_root == late.first_root == available.first_root
    assert len(early.first.spacing[0].bits) == 32
    assert len(late.first.spacing[0].bits) == 48
    with pytest.raises(module.draws.PrefixExhausted):
        module.refinement_address(available, 13)
    missing_root = replace(available, first_root=module.draws.BitPrefix((1, 1)))
    with pytest.raises(module.draws.PrefixExhausted, match="same uncompleted"):
        module.refinement_address(missing_root, 8)
    available_root = replace(available, first_root=module.draws.BitPrefix((1,)*24))
    exposed = module.refinement_address(available_root, 8)
    assert exposed.first_root.bits == (1,)*16
    pending = module.attempt_subdivision_draw(exposed,
        module.refinement_policy(8, first_frame=module.draws.declared_policy().first,
                                second_frame=module.draws.declared_policy().second)[0],
        max_cells=1, max_depth=32, chart_order=(0, 1))
    assert isinstance(pending, module.draws.PendingDraw) and pending.stage == "prefix"
    assert pending.address == exposed


def test_exclusion_keeps_an_exact_root_on_a_subdivision_boundary():
    cubic = _cubic((0, -1, 1, 0), Rational(1, 2**30))
    for pivot in (0, 1):
        for depth in (2, 8, 20):
            cell = module._Cell(pivot, Rational(0), Rational(0), Rational(1, 2**depth), depth)
            assert module._cell_data(cubic, cell, 80+depth)[3] is False


def test_nonreal_exact_scalar_roots_are_certified_in_the_named_omega_basis():
    from onetheory.math.numbers import OMEGA

    cubic = _cubic((0, 2*OMEGA**2, -3*OMEGA, 1))
    result = module.complete_subdivision_roots(cubic, _policy())
    known = tuple(Eisenstein.coerce(c) for c in (0, OMEGA, 2*OMEGA))
    for disk in result.roots.disks:
        _independent_certificate(disk)
        assert sum(
            (root - disk.witness.center).norm() < disk.witness.radius**2
            if disk.parameter_pivot == 0 else
            (root.inverse() - disk.witness.center).norm() < disk.witness.radius**2
            for root in known if disk.parameter_pivot == 0 or not root.is_zero()
        ) == 1


@pytest.mark.parametrize("field", (
    "source_files_sha256", "proof_sha256", "complete_native_regressions",
    "subdivision_root_admission_under_refinement_proved",
    "old_simultaneous_proposer_convergence_proved", "finite_prefix_failures_discardable",
    "independent_cover_cloud_available", "controlled_integral_available",
))
def test_rehashed_scope_source_or_output_attack_cannot_pass_the_trusted_reader(field, tmp_path):
    record = json.loads(module.OUTPUT.read_text())
    record[field] = not record[field] if type(record[field]) is bool else "changed"
    record.pop("artifact_digest")
    record["artifact_digest"] = module._digest(record)
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="trusted execution"):
        module.read_subdivision(expected_digest=DIGEST, path=path)


def test_complete_executed_packet_replays_with_trusted_digest_and_cached_native_certificates():
    assert module.read_subdivision(expected_digest=DIGEST) == json.loads(module.OUTPUT.read_text())


def test_saved_actual_certificates_have_independent_fraction_pair_taylor_and_norm_checks():
    record = json.loads(module.OUTPUT.read_text())
    checked = 0
    for draw in record["complete_native_regressions"]:
        for family, certificates in zip(draw["all_root_families"],
                                        draw["native_uniform_certificates"], strict=True):
            for certificate, disk in zip(certificates, family["root_disks"], strict=True):
                assert certificate["center"] == disk["center"]
                assert certificate["radius"] == disk["radius"]
                coefficients = tuple(tuple(map(Fraction, c["center"]))
                                     for c in family["binary_coefficients"])
                if certificate["parameter_pivot"]:
                    coefficients = tuple(reversed(coefficients))
                center = tuple(map(Fraction, certificate["center"]))
                for k, (value, lo, hi) in enumerate(zip(certificate["taylor"],
                    certificate["modulus_lower"], certificate["modulus_upper"], strict=True)):
                    expected = (Fraction(0), Fraction(0))
                    for j in range(k, 4):
                        term = _mul(coefficients[j], _power(center, j-k))
                        expected = _add(expected, (comb(j, k)*term[0], comb(j, k)*term[1]))
                    assert tuple(map(Fraction, value)) == expected
                    assert Fraction(lo)**2 <= _norm(expected) <= Fraction(hi)**2
                r = Fraction(certificate["radius"])
                lower = tuple(map(Fraction, certificate["modulus_lower"]))
                upper = tuple(map(Fraction, certificate["modulus_upper"]))
                margin = (lower[1]*r-upper[0]-sum(upper[k]*r**k for k in range(2, len(upper)))
                          -Fraction(disk["coefficient_error_bound"]))
                assert margin == Fraction(disk["uniform_margin"]) > 0
                checked += 1
    assert checked == 12


def test_new_digest_does_not_disable_fresh_source_and_scope_reconstruction(tmp_path):
    record = copy.deepcopy(json.loads(module.OUTPUT.read_text()))
    record["old_simultaneous_proposer_convergence_proved"] = True
    record.pop("artifact_digest")
    digest = module._digest(record)
    record["artifact_digest"] = digest
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="source, certificates, proof or scope"):
        module.read_subdivision(expected_digest=digest, path=path)


def test_proof_bytes_are_rechecked_even_with_populated_root_caches(monkeypatch):
    from pathlib import Path

    original = Path.read_bytes

    def changed_proof(path):
        content = original(path)
        return content+b"\nchanged proof\n" if path == module.PROOF else content

    monkeypatch.setattr(Path, "read_bytes", changed_proof)
    with pytest.raises(ValueError, match="source, certificates, proof or scope"):
        module.read_subdivision(expected_digest=DIGEST)
