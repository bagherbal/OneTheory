"""Attack conditional bit-prefix cover draws without asserting random sampling.

Owns:
    Independent finite probability counts, actual three-component continuation,
    immutable prefix and branch gates, retained failures and provenance attacks.

Depends on:
    The original projective input/root engines, auxiliary weights, Fraction
    arithmetic for independent counting and the research draw workflow.

Must not:
    Interpret deterministic regression addresses as IID, replace failed draws,
    infer an integral or choose a physical metric, coefficient or vacuum.

Phase 0:
    Conditional sampling-law regressions only; physical normalization is absent.
"""

import json
from collections import Counter
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
from functools import cache
from itertools import product

import pytest

from onetheory.math.numbers import Rational
from research.experiments.scientific_genesis import auxiliary_cover_draws as draws


@cache
def _actual():
    original = draws.declared_draws()
    policy = draws.declared_policy()
    finer = replace(policy, input=replace(policy.input, cell_bits=48),
                    root=replace(policy.root, radius=Rational(1, 2**16)))
    refined = tuple(draws.refine_draw(d, d.address, finer) for d in original)
    assert all(isinstance(d, draws.CoupledDraw) for d in (*original, *refined))
    return original, refined


@pytest.mark.parametrize("pairs", (1, 2, 3, 4))
def test_ternary_selector_matches_independent_exact_stopping_probabilities(pairs):
    counts = Counter()
    for bits in product((0, 1), repeat=2 * pairs):
        # Independent stopping-time definition, not the implementation's loop.
        groups = tuple(zip(bits[::2], bits[1::2], strict=True))
        admitted = next((pair for pair in groups if pair != (1, 1)), None)
        expected = None if admitted is None else ((0, 0), (0, 1), (1, 0)).index(admitted)
        prefix = draws.BitPrefix(bits)
        if expected is None:
            with pytest.raises(draws.PrefixExhausted):
                prefix.ternary()
            counts[None] += 1
        else:
            digit, consumed = prefix.ternary()
            assert digit == expected
            assert consumed == 2 * (groups.index(admitted) + 1)
            counts[digit] += 1
    mass = 4**pairs
    assert Fraction(counts[None], mass) == Fraction(1, 4**pairs)
    stopped_per_value = sum((Fraction(1, 4**k) for k in range(1, pairs + 1)), Fraction())
    assert [Fraction(counts[i], mass) for i in range(3)] == [stopped_per_value] * 3
    assert Fraction(counts[0], mass - counts[None]) == Fraction(1, 3)


def test_exact_component_mass_and_all_root_choice_counts():
    base = draws.declared_addresses()[0]
    components, branches = Counter(), Counter()
    for bitset in product((0, 1), repeat=3):
        address = replace(base, component=draws.BitPrefix(bitset))
        name, _ = address.choices()
        components[name] += 1
        for a, b in product(((0, 0), (0, 1), (1, 0)), repeat=2):
            choice = replace(address, first_root=draws.BitPrefix(a),
                             second_root=draws.BitPrefix(b)).choices()
            branches[choice] += 1
    assert {key: Fraction(value, 8) for key, value in components.items()} == {
        "A": Fraction(3, 4), "Bx": Fraction(1, 8), "Bu": Fraction(1, 8),
    }
    assert len(branches) == 15
    assert {value for (name, _), value in branches.items() if name == "A"} == {6}
    assert {value for (name, _), value in branches.items() if name != "A"} == {3}
    # Modulo reduction is independently shown NOT uniform for fair bit pairs.
    assert Counter(i % 3 for i in range(4)) == {0: 2, 1: 1, 2: 1}


@pytest.mark.parametrize("bits", ((True,), (False,), (2,), (-1,), ("0",)))
def test_bits_reject_python_aliases_and_nonbits(bits):
    with pytest.raises(ValueError, match="literal integer"):
        draws.BitPrefix(bits)


def test_immutable_prefixes_extend_without_overwriting_tied_bins():
    prefix = draws.BitPrefix([0, 1, 1])
    assert prefix.bits == (0, 1, 1)
    assert prefix.index(2) == 1
    assert draws.BitPrefix((0, 1, 1, 0)).extends(prefix)
    assert not draws.BitPrefix((0, 1)).extends(prefix)
    assert not draws.BitPrefix((0, 1, 0, 0)).extends(prefix)
    with pytest.raises(FrozenInstanceError):
        prefix.bits = (1,)
    with pytest.raises(draws.PrefixExhausted):
        prefix.index(4)
    repeated = draws.ProjectiveAddress((prefix, prefix), (prefix, prefix))
    cell = draws._cell(repeated, draws.inputs.InputPolicy(3, 60, 30, 40))
    assert cell.spacing_indices == (3, 3)
    assert cell.spacings[1].lower == 0


@pytest.mark.parametrize("component", range(3))
def test_actual_native_components_continue_the_same_ideal_branch(component):
    original, refined = _actual()
    old, new = original[component], refined[component]
    assert new.address == old.address
    assert new.admitted_parent == old
    assert new.policy.input.cell_bits == 48
    assert len(old.configuration.root_pairs) == (9, 3, 3)[component]
    assert new.branch == draws._continued_branch(new.configuration, old)
    before = draws.selected_weight(old, volume_scale=1, covering_degree=9)
    after = draws.selected_weight(new, volume_scale=1, covering_degree=9)
    assert before.denominator.lower > 0
    assert after.denominator.lower > 0
    assert after.cover_weight_without_pi_cubed.width < before.cover_weight_without_pi_cubed.width
    assert after.quotient_weight_without_pi_cubed == after.cover_weight_without_pi_cubed / 9
    # The unchanged native point type accepts the SAME chosen member.
    point = draws.intersections.UncertainCoverPoint(
        new.configuration, new.branch, (0, 0, 0), 100, 100,
    )
    assert any(b.radius > 0 for factor in (point.x, point.u, point.p) for b in factor)


def test_complete_family_reordering_cannot_change_the_chosen_root(monkeypatch):
    originals, refined = _actual()
    old, new = originals[0], refined[0]
    c = new.configuration
    first = replace(c.first, disks=(*c.first.disks[1:], c.first.disks[0]))
    reordered = replace(c, first=first)
    # A new initial draw uses the selector's index in this newly ordered family.
    incoming = draws.CoupledDraw(new.address, new.policy, reordered, new.address.choices()[1])
    monkeypatch.setattr(draws, "attempt_draw", lambda address, policy: incoming)
    continued = draws.refine_draw(old, old.address, new.policy)
    assert isinstance(continued, draws.CoupledDraw)
    assert continued.branch[0] == (new.branch[0] - 1) % 3
    assert continued.coordinates == new.coordinates
    with pytest.raises(ValueError, match="bit choice or certified"):
        replace(continued, admitted_parent=None)


def test_independent_fraction_norms_certify_every_refined_root_containment():
    originals, refined = _actual()
    for old_draw, new_draw in zip(originals, refined, strict=True):
        old, new = old_draw.configuration, new_draw.configuration
        families = ((old.first, new.first), (old.second, new.second)) if isinstance(
            old, draws.intersections.LineBaseLineConfiguration,
        ) else ((old.partner, new.partner),)
        for parent, child in families:
            independent_mapping = []
            for disk in child.disks:
                contained = []
                for i, previous in enumerate(parent.disks):
                    assert disk.parameter_pivot == previous.parameter_pivot
                    a = Fraction(disk.witness.center.a.numerator,
                                 disk.witness.center.a.denominator) - Fraction(
                                     previous.witness.center.a.numerator,
                                     previous.witness.center.a.denominator)
                    b = Fraction(disk.witness.center.b.numerator,
                                 disk.witness.center.b.denominator) - Fraction(
                                     previous.witness.center.b.numerator,
                                     previous.witness.center.b.denominator)
                    gap = Fraction(previous.witness.radius.numerator,
                                   previous.witness.radius.denominator) - Fraction(
                                       disk.witness.radius.numerator,
                                       disk.witness.radius.denominator)
                    if gap > 0 and a*a - a*b + b*b < gap*gap:
                        contained.append(i)
                assert len(contained) == 1
                independent_mapping.append(contained[0])
            assert sorted(independent_mapping) == [0, 1, 2]
            assert tuple(independent_mapping) == draws._permutation(child, parent)


def test_reciprocal_continuation_does_not_invert_a_disk_containing_zero():
    _, _, family = draws.intersections.declared_probes()
    infinity = next(d for d in family.disks if d.parameter_pivot == 1)
    finite = next(d for d in family.disks if d.parameter_pivot == 0)
    assert infinity.witness.center.is_zero()
    assert draws._inside(infinity, finite) is False


@pytest.mark.parametrize("field", ("component", "first", "second", "base", "first_root",
                                   "second_root"))
def test_refinement_rejects_replacement_of_any_original_stream(field):
    address = draws.declared_addresses()[0]
    pending = draws.PendingDraw(address, draws.declared_policy(), "prefix", "needs more bits")
    value = getattr(address, field)
    if isinstance(value, draws.BitPrefix):
        replacement = draws.BitPrefix((1 - value.bits[0], *value.bits[1:]))
    else:
        prefix = value.spacing[0]
        replacement = replace(value, spacing=(draws.BitPrefix(
            (1 - prefix.bits[0], *prefix.bits[1:])), *value.spacing[1:]))
    with pytest.raises(ValueError, match="replacing a draw is forbidden"):
        draws.refine_draw(pending, replace(address, **{field: replacement}), pending.policy)


def test_pending_prefix_exhaustion_resumes_on_same_stream():
    address = draws.declared_addresses()[0]
    address = replace(address, first_root=draws.BitPrefix((1, 1)))
    pending = draws.attempt_draw(address, draws.declared_policy())
    assert isinstance(pending, draws.PendingDraw)
    assert pending.address == address and pending.stage == "prefix"
    with pytest.raises(TypeError, match="pending draws"):
        draws.selected_weight(pending, volume_scale=1, covering_degree=9)
    extended = replace(address, first_root=draws.BitPrefix((1, 1, 0, 1)))
    result = draws.refine_draw(pending, extended, pending.policy)
    assert isinstance(result, draws.CoupledDraw)
    assert result.branch == (1, 2)


def test_geometry_failure_is_retained_and_not_resampled():
    address = draws.declared_addresses()[0]
    policy = draws.declared_policy()
    coarse = replace(policy, input=replace(policy.input, cell_bits=1))
    pending = draws.attempt_draw(address, coarse)
    assert isinstance(pending, draws.PendingDraw)
    assert pending.address is address and pending.stage == "input/frame/root"
    resumed = draws.refine_draw(pending, address, policy)
    assert isinstance(resumed, draws.CoupledDraw)
    assert resumed.address == address


def test_uncertified_continuation_keeps_parent_through_retry(monkeypatch):
    originals, refined = _actual()
    old, new = originals[0], refined[0]
    with monkeypatch.context() as patch:
        patch.setattr(draws, "_continued_branch", lambda c, p: (_ for _ in ()).throw(
            ValueError("no certified containment")))
        pending = draws.refine_draw(old, old.address, new.policy)
    assert isinstance(pending, draws.PendingDraw)
    assert pending.admitted_parent == old and pending.stage == "branch-continuation"
    retried = draws.refine_draw(pending, pending.address, pending.policy)
    assert isinstance(retried, draws.CoupledDraw)
    assert retried.coordinates == new.coordinates
    assert retried.admitted_parent == old


@pytest.mark.parametrize("change", ("input", "root", "frame"))
def test_precision_and_frame_replacement_rejected(change):
    policy = draws.declared_policy()
    address = draws.declared_addresses()[0]
    previous = draws.PendingDraw(address, policy, "prefix", "needs input")
    replacement = {"input": replace(policy, input=replace(policy.input, cell_bits=39)),
                   "root": replace(policy, root=replace(policy.root, radius=Rational(1, 2048))),
                   "frame": replace(policy, first=draws.LineFrame(0, (2, 1), 0))}[change]
    with pytest.raises(ValueError, match="unchanged frames"):
        draws.refine_draw(previous, address, replacement)


def test_foreign_configurations_and_unselected_branches_rejected():
    originals, _ = _actual()
    a, bx, _bu = originals
    with pytest.raises(ValueError, match="actual input address"):
        replace(a, configuration=bx.configuration)
    with pytest.raises(ValueError, match="bit choice or certified"):
        replace(a, branch=(0, 0))
    with pytest.raises(ValueError, match="actual input address"):
        replace(a, branch=(True, 2))


@cache
def _record():
    return draws.draw_record()


def test_executed_packet_reproduces_with_all_unresolved_scope():
    record = draws.read_draws()
    assert record == _record()
    assert [r["complete_branch_count"] for r in record["declared_regression_draws"]] == [9, 3, 3]
    assert all(r["status"] == "unresolved" for r in record["pending_regression_requests"])
    assert record["law_preserving_prefix_workflow_available"] is True
    assert record["independent_cover_cloud_available"] is False
    assert record["controlled_integral_available"] is False


@pytest.mark.parametrize("field", ("component_probabilities", "proof_sha256",
    "uncertain_roots_parent_digest", "independent_cover_cloud_available",
    "global_numerical_input_coverage_certified", "complete_section_integrands_available",
    "controlled_integral_available", "ricci_flat_or_hym_metric_available",
    "physical_yukawas_available", "common_stabilized_vacuum_available",
    "physical_moduli_selected", "observations_used", "declared_regression_draws",
    "same_address_refinements", "pending_regression_requests"))
def test_rehashed_changes_fail_closed(field, tmp_path, monkeypatch):
    original = _record()
    changed = json.loads(json.dumps(original))
    value = changed[field]
    changed[field] = (not value if type(value) is bool else
                      ("changed" if isinstance(value, str) else []))
    changed["artifact_digest"] = draws.intersections._digest(changed)
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(changed), encoding="utf-8")
    # Actual original computation is independently exercised above; do not repeat
    # it for each byte-level mutation of that SAME immutable expected packet.
    monkeypatch.setattr(draws, "draw_record", lambda: original)
    with pytest.raises(ValueError, match="inputs, roots, proof or scope"):
        draws.read_draws(path)


def test_boolean_integer_alias_rejected_by_canonical_digest(tmp_path, monkeypatch):
    original = _record()
    changed = json.loads(json.dumps(original))
    changed["declared_regression_draws"][0]["selected_branch"][0] = True
    changed["artifact_digest"] = draws.intersections._digest(changed)
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(changed), encoding="utf-8")
    monkeypatch.setattr(draws, "draw_record", lambda: original)
    with pytest.raises(ValueError):
        draws.read_draws(path)
