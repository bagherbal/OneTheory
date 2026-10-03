"""Retain actual auxiliary cover draws across explicit precision refinement.

Owns:
    Immutable named bit prefixes, unbiased finite selectors, native coupled
    configurations, pending numerical requests and certified root continuation.

Depends on:
    The derived positive auxiliary mixture, existing projective input cells,
    complete uncertain roots and unchanged homogeneous weight enclosures.

Must not:
    Resample difficult inputs, infer independence from deterministic addresses,
    silently change a basis, count correlated roots as IID or assert metrics.

Phase 0:
    Research conditional draw workflow only; independent integration is open.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from functools import cache
from pathlib import Path

from onetheory.math.numbers import Rational

from . import projective_uncertain_intersections as intersections
from . import projective_uniform_input_cells as inputs
from . import uncertain_cover_weights as weights

ROOT = intersections.ROOT
OUTPUT = ROOT / "data/generated/scientific_genesis/auxiliary_cover_draws.json"
PROOF = Path(__file__).with_name("AUXILIARY_COVER_DRAWS_NOTE.md")


class PrefixExhausted(ValueError):
    """The same caller-supplied stream needs more bits; a new draw is forbidden."""


@dataclass(frozen=True, slots=True)
class BitPrefix:
    """A finite prefix of one declared stream, not a certified random source."""

    bits: tuple[int, ...]

    def __post_init__(self):
        bits = tuple(self.bits)
        if any(type(bit) is not int or bit not in (0, 1) for bit in bits):
            raise ValueError("bit prefixes require literal integer zero or one")
        object.__setattr__(self, "bits", bits)

    def index(self, count):
        if type(count) is not int or count < 1:
            raise ValueError("a positive integer prefix length is required")
        if len(self.bits) < count:
            raise PrefixExhausted(f"need {count} bits from the same input stream")
        result = 0
        for bit in self.bits[:count]:
            result = 2 * result + bit
        return result

    def extends(self, old):
        return isinstance(old, BitPrefix) and self.bits[:len(old.bits)] == old.bits

    def ternary(self):
        """Consume 11 pairs on the SAME stream, never take an integer modulo three."""

        for offset in range(0, len(self.bits) - 1, 2):
            digit = 2 * self.bits[offset] + self.bits[offset + 1]
            if digit < 3:
                return digit, offset + 2
        raise PrefixExhausted("ternary selector needs more bits from the same stream")


@dataclass(frozen=True, slots=True)
class ProjectiveAddress:
    """Separate named spacing and phase prefixes, before any numerical conversion."""

    spacing: tuple[BitPrefix, ...]
    phases: tuple[BitPrefix, ...]

    def __post_init__(self):
        spacing, phases = tuple(self.spacing), tuple(self.phases)
        if (len(spacing) not in (1, 2) or len(phases) != len(spacing)
            or any(not isinstance(p, BitPrefix) for p in (*spacing, *phases))):
            raise ValueError("CP1 or CP2 needs separate spacing and phase prefixes")
        object.__setattr__(self, "spacing", spacing)
        object.__setattr__(self, "phases", phases)

    def extends(self, old):
        return (isinstance(old, ProjectiveAddress) and len(self.spacing) == len(old.spacing)
                and all(p.extends(q) for p, q in zip((*self.spacing, *self.phases),
                    (*old.spacing, *old.phases), strict=True)))


@cache
def _cell(address, policy):
    return inputs.projective_input_cell(
        tuple(p.index(policy.cell_bits) for p in address.spacing),
        tuple(p.index(policy.cell_bits) for p in address.phases), policy=policy,
    )


@dataclass(frozen=True, slots=True)
class DrawAddress:
    """All streams for one ideal draw; finite equal-looking values do not prove IID."""

    component: BitPrefix
    first: ProjectiveAddress
    second: ProjectiveAddress
    base: ProjectiveAddress
    first_root: BitPrefix
    second_root: BitPrefix

    def __post_init__(self):
        if any(not isinstance(p, BitPrefix)
               for p in (self.component, self.first_root, self.second_root)):
            raise TypeError("three named discrete bit streams are required")
        if any(not isinstance(p, ProjectiveAddress) for p in
               (self.first, self.second, self.base)):
            raise TypeError("three named projective addresses are required")
        if tuple(len(p.spacing) for p in (self.first, self.second, self.base)) != (2, 2, 1):
            raise ValueError("the named first, second and base inputs have dimensions 2,2,1")

    def extends(self, old):
        return isinstance(old, DrawAddress) and all(
            getattr(self, name).extends(getattr(old, name)) for name in
            ("component", "first", "second", "base", "first_root", "second_root")
        )

    def choices(self):
        component = self.component.index(3)
        if component < 6:
            return "A", (self.first_root.ternary()[0], self.second_root.ternary()[0])
        if component == 6:
            return "Bx", ("fixed", self.second_root.ternary()[0])
        return "Bu", (self.first_root.ternary()[0], "fixed")


@dataclass(frozen=True, slots=True)
class LineFrame:
    """Caller-named line pivot, ordered free axes and binary parameter chart."""

    pivot: int
    axes: tuple[int, int]
    parameter_pivot: int

    def __post_init__(self):
        axes = tuple(self.axes)
        if (type(self.pivot) is not int or self.pivot not in (0, 1, 2)
            or len(axes) != 2 or any(type(i) is not int for i in axes)
            or set(axes) != set(range(3)) - {self.pivot}
            or type(self.parameter_pivot) is not int or self.parameter_pivot not in (0, 1)):
            raise ValueError("an explicit ordered projective line and parameter frame is required")
        object.__setattr__(self, "axes", axes)


@dataclass(frozen=True, slots=True)
class DrawPolicy:
    """Explicit input/root work limits and frames, never automatically chosen."""

    input: inputs.InputPolicy
    root: intersections.roots.RootPolicy
    first: LineFrame
    second: LineFrame

    def __post_init__(self):
        if (not isinstance(self.input, inputs.InputPolicy)
            or not isinstance(self.root, intersections.roots.RootPolicy)
            or any(not isinstance(p, LineFrame) for p in (self.first, self.second))):
            raise TypeError("explicit typed input/root policies and two line frames are required")
        if self.input.bound_bits != self.root.modulus_bits:
            raise ValueError("input and root modulus bounds require the same explicit precision")


def _configuration(address, policy):
    component, branch = address.choices()

    def line(address_, frame):
        return intersections.BoundedLine(_cell(address_, policy.input).coordinates,
                                        frame.pivot, frame.axes)

    if component == "A":
        first, second = line(address.first, policy.first), line(address.second, policy.second)
        base = _cell(address.base, policy.input).coordinates
        _, families = intersections.line_base_line(first, second, base,
            parameter_pivots=(policy.first.parameter_pivot, policy.second.parameter_pivot),
            policy=policy.root)
        configuration = intersections.LineBaseLineConfiguration(first, second, base, *families)
    else:
        source, partner, frame, side = ((address.first, address.second, policy.second, 1)
            if component == "Bx" else (address.second, address.first, policy.first, 2))
        source_point = _cell(source, policy.input).coordinates
        partner_line = line(partner, frame)
        _, roots = intersections.point_line(source_point, partner_line, source_side=side,
            parameter_pivot=frame.parameter_pivot, policy=policy.root)
        configuration = intersections.PointLineConfiguration(
            source_point, side, partner_line, roots,
        )
    return configuration, branch


@dataclass(frozen=True, slots=True)
class CoupledDraw:
    """One selected native branch; refinement may reorder its complete root family."""

    address: DrawAddress
    policy: DrawPolicy
    configuration: intersections.LineBaseLineConfiguration | intersections.PointLineConfiguration
    branch: tuple
    admitted_parent: CoupledDraw | None = None

    def __post_init__(self):
        # Root sets are certified by native constructors. Recompute source inputs,
        # not roots, to forbid a foreign configuration carrying this address.
        if not isinstance(self.address, DrawAddress) or not isinstance(self.policy, DrawPolicy):
            raise TypeError("an actual draw address and policy are required")
        name, chosen = self.address.choices()
        c, p = self.configuration, self.policy
        if name == "A":
            valid = (isinstance(c, intersections.LineBaseLineConfiguration)
                and c.first_line == intersections.BoundedLine(
                    _cell(self.address.first, p.input).coordinates, p.first.pivot, p.first.axes)
                and c.second_line == intersections.BoundedLine(
                    _cell(self.address.second, p.input).coordinates, p.second.pivot, p.second.axes)
                and c.base == _cell(self.address.base, p.input).coordinates)
            root_sets = (c.first, c.second) if valid else ()
        else:
            source, partner, frame, side = ((self.address.first, self.address.second, p.second, 1)
                if name == "Bx" else (self.address.second, self.address.first, p.first, 2))
            valid = (isinstance(c, intersections.PointLineConfiguration)
                and c.source_side == side and c.source_point == _cell(source, p.input).coordinates
                and c.partner_line == intersections.BoundedLine(
                    _cell(partner, p.input).coordinates, frame.pivot, frame.axes))
            root_sets = (c.partner,) if valid else ()
        if (not valid or not isinstance(self.branch, tuple) or len(self.branch) != 2
            or any(type(i) is not int and i != "fixed" for i in self.branch)
            or self.branch not in c.root_pairs):
            raise ValueError("the selected native branch must belong to this actual input address")
        if any(d.witness.radius != p.root.radius for r in root_sets for d in r.disks):
            raise ValueError("actual root bounds must retain the declared policy radius")
        parent = self.admitted_parent
        if parent is None:
            expected = chosen
        else:
            if (not isinstance(parent, CoupledDraw) or not self.address.extends(parent.address)
                or (p.first, p.second) != (parent.policy.first, parent.policy.second)):
                raise ValueError("an actual same-prefix parent in the same line frames is required")
            expected = _continued_branch(c, parent)
        if self.branch != expected:
            raise ValueError("branch must equal its bit choice or certified parent continuation")

    @property
    def coordinates(self):
        return self.configuration.points[self.configuration.root_pairs.index(self.branch)]


@dataclass(frozen=True, slots=True)
class PendingDraw:
    """An unresolved draw that must remain in the workload, never be discarded."""

    address: DrawAddress
    policy: DrawPolicy
    stage: str
    reason: str
    admitted_parent: CoupledDraw | None = None

    def __post_init__(self):
        if (not isinstance(self.address, DrawAddress) or not isinstance(self.policy, DrawPolicy)
            or self.stage not in ("prefix", "input/frame/root", "branch-continuation")
            or not isinstance(self.reason, str) or not self.reason):
            raise ValueError("a pending draw must retain its actual address, policy and reason")
        if self.admitted_parent is not None and (
            not isinstance(self.admitted_parent, CoupledDraw)
            or not self.address.extends(self.admitted_parent.address)
        ):
            raise ValueError("a pending continuation must retain its same-prefix admitted parent")


def attempt_draw(address, policy):
    """Admit or retain a single supplied address; no random replacement or fallback."""

    if not isinstance(address, DrawAddress) or not isinstance(policy, DrawPolicy):
        raise TypeError("an immutable draw address and an explicit policy are required")
    try:
        configuration, branch = _configuration(address, policy)
        return CoupledDraw(address, policy, configuration, branch)
    except PrefixExhausted as error:
        return PendingDraw(address, policy, "prefix", str(error))
    except (ValueError, ZeroDivisionError) as error:
        return PendingDraw(address, policy, "input/frame/root", str(error))


def _inside(new, old):
    """Strict projective containment, not a nearest-center or residual heuristic."""

    ball = intersections.Ball(new.witness.center, new.witness.radius,
                             new.cubic.coefficients[0].bits)
    if new.parameter_pivot != old.parameter_pivot:
        try:
            ball = ball.inverse()
        except (ValueError, ZeroDivisionError):
            return False
    gap = old.witness.radius - ball.radius
    return gap > 0 and (ball.center - old.witness.center).norm() < gap**2


def _permutation(new, old):
    mapping = []
    for disk in new.disks:
        candidates = [i for i, parent in enumerate(old.disks) if _inside(disk, parent)]
        if len(candidates) != 1:
            raise ValueError("the same selected ideal root is not certified by disk containment")
        mapping.append(candidates[0])
    if set(mapping) != set(range(3)):
        raise ValueError("refined complete roots do not bijectively continue the old branches")
    return tuple(mapping)


def _continued_branch(new, parent):
    old = parent.configuration
    if isinstance(old, intersections.LineBaseLineConfiguration):
        if not isinstance(new, intersections.LineBaseLineConfiguration):
            raise ValueError("continuation cannot change the mixture component")
        maps = (_permutation(new.first, old.first), _permutation(new.second, old.second))
        return tuple(mapping.index(i) for mapping, i in zip(maps, parent.branch, strict=True))
    if (not isinstance(new, intersections.PointLineConfiguration)
        or new.source_side != old.source_side):
        raise ValueError("continuation cannot change the mixture component")
    mapping = _permutation(new.partner, old.partner)
    side = 1 if old.source_side == 1 else 0
    branch = list(parent.branch)
    branch[side] = mapping.index(parent.branch[side])
    return tuple(branch)


def refine_draw(previous, address, policy):
    """Keep every prefix and, if admitted, the original ideal branch identity."""

    if not isinstance(previous, (CoupledDraw, PendingDraw)):
        raise TypeError("an existing admitted or pending draw is required")
    if not isinstance(address, DrawAddress) or not address.extends(previous.address):
        raise ValueError(
            "refinement must extend every original stream; replacing a draw is forbidden",
        )
    if not isinstance(policy, DrawPolicy):
        raise TypeError("an explicit draw policy is required")
    old = previous.policy
    if (policy.first != old.first or policy.second != old.second
        or any(a < b for a, b in zip(
            (policy.input.cell_bits, policy.input.bound_bits, policy.input.atan_terms,
             policy.input.taylor_terms, policy.root.coefficient_bits, policy.root.max_iterations),
            (old.input.cell_bits, old.input.bound_bits, old.input.atan_terms,
             old.input.taylor_terms, old.root.coefficient_bits, old.root.max_iterations),
            strict=True))
        or policy.root.radius > old.root.radius):
        raise ValueError(
            "continuation requires unchanged frames and nondecreasing explicit precision",
        )
    parent = previous if isinstance(previous, CoupledDraw) else previous.admitted_parent
    result = attempt_draw(address, policy)
    if isinstance(result, PendingDraw):
        return replace(result, admitted_parent=parent)
    if parent is None:
        return result
    try:
        branch = _continued_branch(result.configuration, parent)
        return replace(result, branch=branch, admitted_parent=parent)
    except ValueError as error:
        return PendingDraw(address, policy, "branch-continuation", str(error), parent)


def selected_weight(draw, *, volume_scale, covering_degree):
    """Reuse actual member bounds; no weights are fabricated for pending requests."""

    if not isinstance(draw, CoupledDraw):
        raise TypeError("a native admitted draw is required; pending draws have no local weight")
    return weights._weight_bounds(draw.coordinates, volume_scale=volume_scale,
                                  covering_degree=covering_degree)


def _prefix(index, bits):
    return BitPrefix(tuple((index >> i) & 1 for i in reversed(range(bits))))


def declared_addresses():
    """Predeclared regression addresses, NEVER IID evidence or a sampling cloud."""

    def projective(spacing, phases):
        return ProjectiveAddress(tuple(_prefix(i, 48) for i in spacing),
                                 tuple(_prefix(i, 48) for i in phases))

    first = projective((2**46, 3 * 2**46), (2**44, 11 * 2**44))
    second = projective((5 * 2**45, 7 * 2**45), (5 * 2**44, 13 * 2**44))
    base = projective((3 * 2**46,), (7 * 2**44,))
    return tuple(DrawAddress(_prefix(component, 3), first, second, base,
                            BitPrefix((1, 1, 0, 1)), BitPrefix((1, 0)))
                 for component in (0, 6, 7))


def declared_policy():
    return DrawPolicy(inputs.InputPolicy(40, 100, 40, 56),
        intersections.roots.RootPolicy(Rational(1, 2**12), 64, 100, 128),
        LineFrame(0, (1, 2), 0), LineFrame(0, (1, 2), 0))


@cache
def declared_draws():
    return tuple(attempt_draw(address, declared_policy()) for address in declared_addresses())


def _policy_record(policy):
    return {"input": {key: getattr(policy.input, key) for key in
            ("cell_bits", "bound_bits", "atan_terms", "taylor_terms")},
        "root": {"radius": str(policy.root.radius), **{key: getattr(policy.root, key) for key in
            ("coefficient_bits", "modulus_bits", "max_iterations")}},
        "frames": [{"pivot": frame.pivot, "axes": list(frame.axes),
                    "parameter_pivot": frame.parameter_pivot} for frame in
                   (policy.first, policy.second)]}


def _address_record(address):
    def text(p):
        return "".join(str(bit) for bit in p.bits)
    def projective(p):
        return {"spacing": [text(q) for q in p.spacing], "phases": [text(q) for q in p.phases]}
    return {"component": text(address.component), "first": projective(address.first),
        "second": projective(address.second), "base": projective(address.base),
        "first_root": text(address.first_root), "second_root": text(address.second_root)}


def _draw_record(draw):
    record = {"address": _address_record(draw.address), "policy": _policy_record(draw.policy)}
    if isinstance(draw, PendingDraw):
        return {**record, "status": "unresolved", "stage": draw.stage, "reason": draw.reason,
                "admitted_parent_retained": draw.admitted_parent is not None}
    weight = selected_weight(draw, volume_scale=1, covering_degree=9)
    c = draw.configuration
    root_sets = (c.first, c.second) if isinstance(c, intersections.LineBaseLineConfiguration) else (
        c.partner,
    )
    return {**record, "status": "admitted", "component": draw.address.choices()[0],
        "complete_branch_count": len(c.root_pairs), "selected_branch": list(draw.branch),
        "all_root_families": [intersections._roots_record(r) for r in root_sets],
        "coupled_coordinates": [[intersections._ball_record(b) for b in group]
                                for group in draw.coordinates],
        "cover_weight_without_pi_cubed": weights._interval_record(
            weight.cover_weight_without_pi_cubed),
        "quotient_weight_without_pi_cubed": weights._interval_record(
            weight.quotient_weight_without_pi_cubed)}


def draw_record():
    """Execute three finite probes and same-prefix refinements; never infer IID."""

    parent = intersections.read_uncertain_intersections()
    if intersections._digest(parent) != (
        "97981cfe6a6d67fd40287c8902a99f4ce3a73729fea6a64b4f133fdce82c0d26"
    ):
        raise ValueError("the actual uniform root prerequisites changed")
    positive_path = OUTPUT.with_name("alternate_metric_positive_measure.json")
    positive = json.loads(positive_path.read_text(encoding="utf-8"))
    digest = positive.pop("artifact_digest", None)
    proof_sha = hashlib.sha256((ROOT / positive["proof"]).read_bytes()).hexdigest()
    if (digest != intersections._digest(positive)
        or digest != "c95486f83301f30fe55906ae773981d3a18d5662b56587de769f9744638cd66e"
        or proof_sha != positive["proof_sha256"]
        or positive["component_probabilities"] != ["3/4", "1/8", "1/8"]):
        raise ValueError("the intersection-derived auxiliary probabilities changed")
    original = declared_draws()
    if any(isinstance(draw, PendingDraw) for draw in original):
        raise ValueError("a predeclared regression draw remains unresolved")
    policy = declared_policy()
    finer = replace(policy, input=replace(policy.input, cell_bits=48),
                    root=replace(policy.root, radius=Rational(1, 2**16)))
    refined = tuple(refine_draw(draw, draw.address, finer) for draw in original)
    if any(isinstance(draw, PendingDraw) for draw in refined):
        raise ValueError("a predeclared same-draw continuation remains unresolved")
    coarse = attempt_draw(original[0].address, replace(policy,
                           input=replace(policy.input, cell_bits=1)))
    exhausted = attempt_draw(replace(original[0].address, first_root=BitPrefix((1, 1))), policy)
    if not isinstance(coarse, PendingDraw) or not isinstance(exhausted, PendingDraw):
        raise ValueError("declared precision/prefix exhaustion probes did not remain pending")
    return {"schema": "auxiliary-cover-draws-v1", "proof_sha256": hashlib.sha256(
            PROOF.read_bytes()).hexdigest(),
        "uncertain_roots_parent_digest": intersections._digest(parent),
        "positive_law_parent_digest": digest,
        "positive_law_proof_sha256": positive["proof_sha256"],
        "probability_assumption": "mutually independent infinite fair named bit streams",
        "component_probabilities": ["3/4", "1/8", "1/8"],
        "declared_regression_draws": [_draw_record(draw) for draw in original],
        "same_address_refinements": [_draw_record(draw) for draw in refined],
        "pending_regression_requests": [_draw_record(coarse), _draw_record(exhausted)],
        "law_preserving_prefix_workflow_available": True,
        "certified_branch_continuation_available": True,
        "failed_draws_resampled_or_dropped": False,
        "rng_implemented_or_certified": False,
        "independent_cover_cloud_available": False,
        "global_numerical_input_coverage_certified": False,
        "complete_section_integrands_available": False,
        "controlled_integral_available": False,
        "ricci_flat_or_hym_metric_available": False,
        "physical_yukawas_available": False, "common_stabilized_vacuum_available": False,
        "physical_moduli_selected": False, "observations_used": False}


def write_draws(path=OUTPUT):
    record = draw_record()
    record["artifact_digest"] = intersections._digest(record)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return record


def read_draws(path=OUTPUT):
    """Recompute all law, actual root/weight, continuation, failure and scope fields."""

    record = json.loads(path.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest", None)
    if digest != intersections._digest(record) or digest != intersections._digest(draw_record()):
        raise ValueError("the conditional draw workflow changed its inputs, roots, proof or scope")
    return record


if __name__ == "__main__":
    print(write_draws()["artifact_digest"])
