"""Certify complete native projective roots by declared adaptive subdivision.

Owns:
    Exact zero exclusion, two explicit parameter charts, positive-radius uniform
    Rouche admission and bounded-work subdivision of actual binary cubic cells.

Depends on:
    Existing Eisenstein modulus and Taylor certificates, complete uncertain-root
    constructors and the unchanged coupled auxiliary input transformations.

Must not:
    Fall back from failed simultaneous proposals, drop pending input addresses,
    choose physical moduli, claim an IID cloud or infer metric convergence.

Phase 0:
    Research admission machinery only; physical integration remains unresolved.
"""

from __future__ import annotations

import hashlib
import json
from collections import deque
from dataclasses import dataclass, replace
from functools import cache
from pathlib import Path

from onetheory.core.errors import FailedConvergence
from onetheory.math.numbers import Eisenstein, Rational, coerce_rational
from onetheory.math.polynomials import Polynomial

from . import auxiliary_cover_draws as draws
from . import projective_uncertain_intersections as native

ROOT = native.ROOT
OUTPUT = ROOT / "data/generated/scientific_genesis/projective_subdivision_roots.json"
PROOF = Path(__file__).with_name("PROJECTIVE_SUBDIVISION_ROOTS_NOTE.md")


@dataclass(frozen=True, slots=True)
class SubdivisionPolicy:
    """Caller-declared radius, norm precision, work caps and ordered chart atlas."""

    radius: Rational
    modulus_bits: int
    max_cells: int
    max_depth: int
    chart_order: tuple[int, int]

    def __post_init__(self):
        radius = coerce_rational(self.radius)
        if radius <= 0:
            raise ValueError("subdivision requires a positive root radius")
        if any(type(v) is not int or v < 1 for v in
               (self.modulus_bits, self.max_cells, self.max_depth)):
            raise ValueError("positive integer subdivision precision and work caps required")
        order = tuple(self.chart_order)
        if (len(order) != 2 or any(type(v) is not int for v in order)
            or set(order) != {0, 1}):
            raise ValueError("both ordered projective parameter charts must be declared")
        object.__setattr__(self, "radius", radius)
        object.__setattr__(self, "chart_order", order)


@dataclass(frozen=True, slots=True)
class _Cell:
    pivot: int
    lower_a: Rational
    lower_b: Rational
    width: Rational
    depth: int

    @property
    def center(self):
        return Eisenstein(self.lower_a + self.width/2, self.lower_b + self.width/2)

    def children(self):
        half = self.width/2
        return tuple(_Cell(self.pivot, self.lower_a + i*half, self.lower_b + j*half,
                           half, self.depth + 1) for i, j in ((0, 0), (0, 1), (1, 0), (1, 1)))


def _inside_admitted(cell, disk, bits):
    """Prove containment of the whole cell disk, including reciprocal charts."""

    c, h = cell.center, cell.width
    d, r = disk.witness.center, disk.witness.radius
    if cell.pivot == disk.parameter_pivot:
        gap = r-h
        return gap > 0 and (c-d).norm() < gap**2
    c_lower = native.roots.modulus_bounds(c, bits)[0]
    if c_lower <= h:
        return False
    numerator = native.roots.modulus_bounds(1-d*c, bits)[1]
    d_upper = native.roots.modulus_bounds(d, bits)[1]
    return numerator + d_upper*h < r*(c_lower-h)


def _cell_data(cubic, cell, bits):
    coefficients = cubic.chart_coefficients(cell.pivot)
    polynomial = Polynomial.from_coefficients(tuple(c.center for c in coefficients),
                                              scalar_type=Eisenstein)
    taylor = native.roots._taylor_coefficients(polynomial, cell.center)
    bounds = tuple(native.roots.modulus_bounds(c, bits) for c in taylor)
    maximum = native.roots.modulus_bounds(cell.center, bits)[1] + cell.width
    uncertainty = sum((c.radius*maximum**j for j, c in enumerate(coefficients)), Rational(0))
    variation = sum((b[1]*cell.width**j for j, b in enumerate(bounds) if j), Rational(0))
    return polynomial, taylor, bounds, bounds[0][0] > variation + uncertainty


@dataclass(frozen=True, slots=True)
class SubdivisionResult:
    """Native complete certificates plus explicit finite execution counters."""

    roots: native.CompleteUncertainRoots
    policy: SubdivisionPolicy
    examined_cells: int
    deepest_level: int
    zero_free_cells: int
    contained_cells: int

    def __post_init__(self):
        if (not isinstance(self.roots, native.CompleteUncertainRoots)
            or not isinstance(self.policy, SubdivisionPolicy)
            or type(self.examined_cells) is not int
            or not 1 <= self.examined_cells <= self.policy.max_cells
            or type(self.deepest_level) is not int
            or not 0 <= self.deepest_level <= self.policy.max_depth
            or any(type(n) is not int or not 0 <= n <= self.examined_cells
                   for n in (self.zero_free_cells, self.contained_cells))
            or any(d.witness.radius != self.policy.radius for d in self.roots.disks)):
            raise ValueError("native certificates and subdivision work accounting disagree")


@cache
def complete_subdivision_roots(cubic, policy):
    """A separately selected solver, never an automatic fallback or center result.

    Both charts start with the coefficient square [-2,2]^2 in (1,omega).
    A square of width h lies in the complex disk of radius h about its center.
    Breadth-first children have a fixed lexicographic order. The caller's fixed
    positive radius is used for every admitted root, including exact centers.
    """

    if not isinstance(cubic, native.UncertainCubic) or not isinstance(policy, SubdivisionPolicy):
        raise TypeError("an actual uncertain binary cubic and explicit subdivision policy required")
    queue = deque(_Cell(p, Rational(-2), Rational(-2), Rational(4), 0)
                  for p in policy.chart_order)
    disks = []
    examined = deepest = excluded = contained = 0
    while queue:
        if examined == policy.max_cells:
            raise FailedConvergence("projective subdivision exhausted its declared cell cap")
        cell = queue.popleft()
        examined += 1
        deepest = max(deepest, cell.depth)
        bits = policy.modulus_bits + cell.depth
        if any(_inside_admitted(cell, d, bits) for d in disks):
            contained += 1
            continue
        polynomial, taylor, bounds, zero_free = _cell_data(cubic, cell, bits)
        if zero_free:
            excluded += 1
            continue
        if cell.width < policy.radius/8:
            try:
                witness = native.roots.RootDisk(polynomial, cell.center, policy.radius, taylor,
                    tuple(v[0] for v in bounds), tuple(v[1] for v in bounds))
                disk = native.UniformRootDisk(cubic, cell.pivot, witness)
            except ValueError:
                disk = None  # This candidate is not a result; its cell remains in subdivision.
            if disk is not None and all(native._projectively_disjoint(disk, old) for old in disks):
                disks.append(disk)
                if len(disks) == 3:
                    return SubdivisionResult(native.CompleteUncertainRoots(cubic, tuple(disks)),
                        policy, examined, deepest, excluded, contained)
        if cell.depth < policy.max_depth:
            queue.extend(cell.children())
    raise FailedConvergence("projective subdivision has unresolved cells at its declared depth cap")


def attempt_subdivision_draw(address, geometric_policy, *, max_cells, max_depth, chart_order):
    """Keep native draw semantics while explicitly replacing the proposal method.

    The geometric policy supplies input conversion, ordered line bases and root
    radius/modulus precision. Its single-chart parameter pivots and Durand--Kerner
    mesh/iteration fields are unused here; the separately supplied subdivision
    work caps and ordered two-chart atlas govern this call.
    No simultaneous proposer is run, inspected or used as a fallback.
    """

    if not isinstance(address, draws.DrawAddress) or not isinstance(geometric_policy,
                                                                    draws.DrawPolicy):
        raise TypeError("a retained actual address and explicit geometric policy required")
    policy = SubdivisionPolicy(geometric_policy.root.radius, geometric_policy.root.modulus_bits,
                               max_cells, max_depth, chart_order)
    try:
        component, branch = address.choices()

        def line(a, frame):
            return native.BoundedLine(draws._cell(a, geometric_policy.input).coordinates,
                                      frame.pivot, frame.axes)

        if component == "A":
            first = line(address.first, geometric_policy.first)
            second = line(address.second, geometric_policy.second)
            base = draws._cell(address.base, geometric_policy.input).coordinates
            roots = tuple(complete_subdivision_roots(native.actual_restriction(line_, base, side=s),
                                                    policy).roots
                          for s, line_ in ((1, first), (2, second)))
            configuration = native.LineBaseLineConfiguration(first, second, base, *roots)
        else:
            source, partner, frame, side = ((address.first, address.second,
                geometric_policy.second, 1) if component == "Bx" else
                (address.second, address.first, geometric_policy.first, 2))
            source = draws._cell(source, geometric_policy.input).coordinates
            partner = line(partner, frame)
            cox = native.schoen_geometry().cover.cox
            f, g = tuple(native.polynomial_value(p, source) for p in (cox.cubic_f, cox.cubic_g))
            base = (-g, f) if side == 1 else (-f*2, g)
            if not native._nonzero(base):
                raise ValueError("the same source input cell may meet a pencil base point")
            roots = complete_subdivision_roots(native.actual_restriction(partner, base,
                side=3-side), policy).roots
            configuration = native.PointLineConfiguration(source, side, partner, roots)
        return draws.CoupledDraw(address, geometric_policy, configuration, branch)
    except draws.PrefixExhausted as error:
        return draws.PendingDraw(address, geometric_policy, "prefix", str(error))
    except (ValueError, ZeroDivisionError, FailedConvergence) as error:
        return draws.PendingDraw(address, geometric_policy, "input/frame/root", str(error))


def refine_subdivision_draw(previous, address, policy, *, max_cells, max_depth, chart_order):
    """Retain every prefix and native admitted parent while selecting subdivision.

    This uses the existing projective containment bijection, not new branch
    matching mathematics. First-admission disk indices never replace an already
    admitted root. A failed continuation retains the last certified parent.
    """

    if not isinstance(previous, (draws.CoupledDraw, draws.PendingDraw)):
        raise TypeError("an actual existing admitted or pending native draw required")
    if not isinstance(address, draws.DrawAddress) or not address.extends(previous.address):
        raise ValueError("every original bit prefix must extend; a replacement draw is forbidden")
    if not isinstance(policy, draws.DrawPolicy):
        raise TypeError("an explicit native geometric policy required")
    old = previous.policy
    if ((policy.first, policy.second) != (old.first, old.second)
        or any(a < b for a, b in zip(
            (policy.input.cell_bits, policy.input.bound_bits, policy.input.atan_terms,
             policy.input.taylor_terms, policy.root.modulus_bits),
            (old.input.cell_bits, old.input.bound_bits, old.input.atan_terms,
             old.input.taylor_terms, old.root.modulus_bits), strict=True))
        or policy.root.radius > old.root.radius):
        raise ValueError(
            "same line frames and nondecreasing declared input/root precision required")
    parent = previous if isinstance(previous, draws.CoupledDraw) else previous.admitted_parent
    result = attempt_subdivision_draw(address, policy, max_cells=max_cells, max_depth=max_depth,
                                     chart_order=chart_order)
    if isinstance(result, draws.PendingDraw):
        return replace(result, admitted_parent=parent)
    if parent is None:
        return result
    try:
        branch = draws._continued_branch(result.configuration, parent)
        return replace(result, branch=branch, admitted_parent=parent)
    except ValueError as error:
        return draws.PendingDraw(address, policy, "branch-continuation", str(error), parent)


def _digest(record):
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


def refinement_policy(level, *, first_frame, second_frame):
    """The explicit theorem schedule, without providing or replacing input bits."""

    if type(level) is not int or level < 2:
        raise ValueError("the declared refinement level must be an integer at least two")
    return draws.DrawPolicy(draws.inputs.InputPolicy(4*level, 8*level, 4*level, 8*level),
        native.roots.RootPolicy(Rational(1, 2**level), 8*level+8, 8*level, 1),
        first_frame, second_frame), {
            "max_cells": 1 << (8*level), "max_depth": 4*level, "chart_order": (0, 1),
        }


def refinement_address(available, level):
    """Expose declared prefixes only; never fabricate or replace missing bits.

    Spacing/phase streams expose 4j bits. Root selectors expose up to 2j
    bits, stopping after the first accepted pair; a terminated selector needs
    no more bits. An uncompleted shorter prefix requires more of that stream.
    """

    if not isinstance(available, draws.DrawAddress):
        raise TypeError("caller-supplied named input prefixes are required")
    if type(level) is not int or level < 2:
        raise ValueError("the declared refinement level must be an integer at least two")

    def uniform(prefix):
        prefix.index(4*level)  # Fail explicitly if the same stream is too short.
        return draws.BitPrefix(prefix.bits[:4*level])

    def root(prefix):
        exposed = draws.BitPrefix(prefix.bits[:2*level])
        try:
            _, used = exposed.ternary()
        except draws.PrefixExhausted as error:
            if len(exposed.bits) < 2*level:
                raise draws.PrefixExhausted(
                    "need more of the same uncompleted root-selector stream") from error
            return exposed  # All pairs are 11; the actual draw remains pending.
        return draws.BitPrefix(exposed.bits[:used])

    def projective(address):
        return draws.ProjectiveAddress(tuple(map(uniform, address.spacing)),
                                       tuple(map(uniform, address.phases)))

    available.component.index(3)
    return draws.DrawAddress(draws.BitPrefix(available.component.bits[:3]),
        projective(available.first), projective(available.second), projective(available.base),
        root(available.first_root), root(available.second_root))


def _sources():
    import inspect

    paths = (Path(__file__), PROOF, Path(native.__file__), Path(native.roots.__file__),
             Path(draws.__file__), Path(draws.inputs.__file__),
             Path(draws.weights.__file__), ROOT / "src/onetheory/core/errors.py",
             Path(inspect.getfile(native.Ball)), Path(inspect.getfile(native.schoen_geometry)),
             ROOT / "src/onetheory/math/numbers.py", ROOT / "src/onetheory/math/polynomials.py",
             ROOT / "data/published/visible_carrier/source_manifest.json",
             ROOT / "Experimental_Draft_OneTheory.py", ROOT / "Experimental_Draft_OneTheory.docx")
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def subdivision_record():
    """Replay actual bounded families and failures, not a randomized cloud."""

    before = _sources()
    parents = {}
    for name, digest in (
        ("alternate_metric_positive_measure.json",
         "c95486f83301f30fe55906ae773981d3a18d5662b56587de769f9744638cd66e"),
        ("projective_uncertain_intersections.json",
         "97981cfe6a6d67fd40287c8902a99f4ce3a73729fea6a64b4f133fdce82c0d26"),
    ):
        record = json.loads(OUTPUT.with_name(name).read_text())
        actual_digest = record.pop("artifact_digest", None)
        if actual_digest != digest or _digest(record) != digest:
            raise ValueError("an actual auxiliary law or uncertain-root parent changed")
        proof = ROOT / record["proof"] if "proof" in record else native.PROOF
        if hashlib.sha256(proof.read_bytes()).hexdigest() != record["proof_sha256"]:
            raise ValueError("an actual auxiliary law or uncertain-root proof changed")
        parents[name] = digest
    policy = draws.declared_policy()
    work = {"max_cells": 20000, "max_depth": 28, "chart_order": (0, 1)}
    admission_policy = SubdivisionPolicy(policy.root.radius, policy.root.modulus_bits, **work)
    admitted = tuple(attempt_subdivision_draw(a, policy, **work)
                     for a in draws.declared_addresses())
    if any(not isinstance(d, draws.CoupledDraw) for d in admitted):
        raise ValueError("a declared subdivision regression remains unresolved")
    records = []
    for draw in admitted:
        configuration = draw.configuration
        families = ((configuration.first, configuration.second)
                    if isinstance(configuration, native.LineBaseLineConfiguration)
                    else (configuration.partner,))
        results = tuple(complete_subdivision_roots(r.cubic, admission_policy) for r in families)
        records.append({**draws._draw_record(draw), "root_work": [{
            "examined_cells": r.examined_cells, "deepest_level": r.deepest_level,
            "zero_free_cells": r.zero_free_cells, "contained_cells": r.contained_cells,
        } for r in results], "native_uniform_certificates": [[{
            "parameter_pivot": disk.parameter_pivot,
            "center": [str(disk.witness.center.a), str(disk.witness.center.b)],
            "radius": str(disk.witness.radius),
            "taylor": [[str(c.a), str(c.b)] for c in disk.witness.taylor],
            "modulus_lower": [str(v) for v in disk.witness.modulus_lower],
            "modulus_upper": [str(v) for v in disk.witness.modulus_upper],
        } for disk in r.roots.disks] for r in results]})
    capped = attempt_subdivision_draw(admitted[0].address, policy, **{**work, "max_cells": 1})
    if not isinstance(capped, draws.PendingDraw) or capped.address != admitted[0].address:
        raise ValueError("a work-cap failure did not retain its exact original input address")
    coarse_policy, coarse_work = refinement_policy(8, first_frame=policy.first,
                                                   second_frame=policy.second)
    fine_policy, fine_work = refinement_policy(12, first_frame=policy.first,
                                                second_frame=policy.second)
    continued = []
    for address in draws.declared_addresses():
        coarse_address = refinement_address(address, 8)
        fine_address = refinement_address(address, 12)
        if not fine_address.extends(coarse_address):
            raise ValueError("the declared exposed stream prefixes did not extend")
        parent = attempt_subdivision_draw(coarse_address, coarse_policy, **coarse_work)
        if not isinstance(parent, draws.CoupledDraw):
            raise ValueError("a declared theorem-schedule parent remains unresolved")
        pending = refine_subdivision_draw(parent, fine_address, fine_policy,
                                           **{**fine_work, "max_cells": 1})
        if not isinstance(pending, draws.PendingDraw) or pending.admitted_parent != parent:
            raise ValueError("failed subdivision continuation lost its admitted parent")
        child = refine_subdivision_draw(pending, fine_address, fine_policy, **fine_work)
        if not isinstance(child, draws.CoupledDraw) or child.admitted_parent != parent:
            raise ValueError("same-stream continuation did not certify the retained parent root")
        continued.append({"parent": draws._draw_record(parent),
            "retained_pending": draws._draw_record(pending), "child": draws._draw_record(child),
            "first_admission_work": {**coarse_work,
                                     "chart_order": list(coarse_work["chart_order"])},
            "continuation_work": {**fine_work, "chart_order": list(fine_work["chart_order"])}})
    if _sources() != before:
        raise ValueError("a native solver, input, original artifact or proof changed during replay")
    return {
        "schema": "projective-subdivision-roots-v1", "source_files_sha256": before,
        "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(), "parents": parents,
        "method": "explicit projective subdivision; no simultaneous proposer or fallback",
        "regression_work": {**work, "chart_order": list(work["chart_order"])},
        "unused_old_proposal_fields": ["coefficient_bits", "max_iterations"],
        "unused_single_chart_fields": ["first.parameter_pivot", "second.parameter_pivot"],
        "complete_native_regressions": records,
        "retained_work_cap_failure": draws._draw_record(capped),
        "same_stream_root_continuations": continued,
        "refinement_schedule": {
            "minimum_level": 2, "radius": "2^-j", "input_cell_bits": "4j",
            "bound_bits": "8j", "atan_terms": "4j", "taylor_terms": "8j",
            "modulus_bits": "8j + cell depth", "maximum_cells": "2^(8j)",
            "maximum_depth": "4j", "same_input_prefixes_required": True,
            "spacing_and_phase_exposed_prefix_bits": "4j",
            "root_selector_exposed_prefix_bits": "up to 2j, stop at first accepted pair",
            "component_exposed_prefix_bits": 3, "missing_bits_fabricated": False,
        },
        "probability_assumption": "mutually independent infinite fair named bit streams",
        "subdivision_root_admission_under_refinement_proved": True,
        "proper_actual_discriminant_failure_loci": True,
        "old_simultaneous_proposer_convergence_proved": False,
        "all_finite_input_cells_admissible": False, "finite_prefix_failures_discardable": False,
        "native_root_continuation_controller_executed": True,
        "full_frame_or_integrand_controller_executed": False,
        "global_numerical_input_coverage_certified": False,
        "rng_implemented_or_certified": False, "independent_cover_cloud_available": False,
        "controlled_integral_available": False, "ricci_flat_or_hym_metric_available": False,
        "physical_yukawas_available": False, "common_stabilized_vacuum_available": False,
        "physical_moduli_selected": False, "observations_used": False,
    }


def write_subdivision(path=OUTPUT):
    record = subdivision_record()
    record["artifact_digest"] = _digest(record)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n")
    temporary.replace(path)
    return record


def read_subdivision(*, expected_digest, path=OUTPUT):
    record = json.loads(path.read_text())
    digest = record.pop("artifact_digest", None)
    if digest != expected_digest or _digest(record) != expected_digest:
        raise ValueError("the subdivision result differs from its trusted execution digest")
    if record != subdivision_record():
        raise ValueError("the actual subdivision source, certificates, proof or scope changed")
    return {"artifact_digest": digest, **record}


if __name__ == "__main__":
    print(write_subdivision()["artifact_digest"])
