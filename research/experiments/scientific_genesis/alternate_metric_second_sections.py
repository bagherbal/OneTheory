"""Construct the actual alternate second constituent's complete section basis.

Owns:
    Stabilizer-aware scalar orbit sections, exact ideal Koszul quotients,
    non-split Serre lift templates, and full invariant V2 sections.

Depends on:
    The frozen alternate I6 ray, repaired homogeneous frames, actual Schoen
    equations, declared generating twist, and existing exact cover machinery.

Must not:
    Substitute the reference second ray, drop fixed monomials, treat quotient
    sections as Serre lifts, select a vacuum, or claim rank-four metrics.

Phase 0:
    Research-only section construction conditional on the heterotic realization.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from dataclasses import replace
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    ReducedBasisEntry,
    SparseOuterCechCochain,
    _include,
)

from .alternate_constituent_hom_actions import _common_frame
from .alternate_metric_first_quotient_sections import (
    ROOT_PAIRS,
    Monomial,
    Orbit,
    Polynomial,
    _act,
    _inputs,
    _modular_pivots,
    _multiply,
    _pair,
)
from .alternate_metric_first_serre_lifts import (
    CompactSection,
    _accumulate,
    _compact,
    _deck_from_frame,
    _freeze,
)
from .alternate_metric_first_subline_sections import _eliminant
from .alternate_metric_quotient_generation import CONE, _second_constituent
from .alternate_metric_quotient_generation import OUTPUT as GENERATION
from .mixed_schoen_common_dga import perturbed_homotopy
from .mixed_schoen_outer_actions import _full_action, _MixedContraction
from .mixed_schoen_outer_transfer import mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_metric_second_sections.json"
SECTIONS = OUTPUT.with_suffix(".sections.json.gz")
RELATIONS = OUTPUT.with_suffix(".relations.json.gz")
TWIST = (14, 16, 1)
GENERATORS = ((0, 2, 1), (1, 0, 2), (1, 1, 1), (2, 1, 0))


@cache
def _context():
    second = _second_constituent()
    twisted = replace(second, twist=tuple(a + b for a, b in zip(second.twist, TWIST, strict=True)),
                      objects=tuple(replace(item, line_degree=tuple(
                          a + b for a, b in zip(item.line_degree, TWIST, strict=True)
                      )) for item in second.objects))
    contraction = _MixedContraction(twisted, mixed_schoen_unit())
    from research.experiments.computable_carrier.schoen_sparse_actions import (
        schoen_sparse_deck_actions,
    )
    actions = schoen_sparse_deck_actions()
    frames = tuple(_common_frame(second, action).scale(unit)
                   for action, unit in zip(actions, (OMEGA, OMEGA2), strict=True))
    if [o.line_degree for o in twisted.objects] != (
        [(15, 15, 0)] + [(15, 12, 2)] * 4 + [(15, 11, 2)] * 3
    ):
        raise ValueError("the actual alternate second-constituent object degrees changed")
    actual = second.full.alignment.action.derived.extension.scheme.resolution.generators
    if tuple(g.terms for g in actual) != tuple(((m, Eisenstein(1)),) for m in GENERATORS):
        raise ValueError("the actual I6 Hilbert--Burch generators changed")
    for action, frame, scalar in zip(actions, frames, (OMEGA, OMEGA2), strict=True):
        for column, generator in enumerate(actual):
            left = generator.zero(3, scalar_type=Eisenstein)
            for row, g in enumerate(actual):
                left = left + g.scale(frame[row + 1][column + 1])
            if left != generator.substitute_monomials(action.u_images).scale(scalar):
                raise ValueError("the actual second ideal image frame is not (omega,omega^2)")
        if frame[0][0] != Eisenstein(1):
            raise ValueError("the actual second-subline frame is not trivial")
    return contraction, actions, frames


def _belongs(monomial: Monomial) -> bool:
    return any(all(a >= b for a, b in zip(monomial[3:6], g, strict=True)) for g in GENERATORS)


def _regular_sequence_inputs() -> None:
    """Check every input of the fat-axis Cohen--Macaulay regularity argument."""

    primary = (((0, 1, 0), (0, 0, 2)), ((0, 0, 1), (2, 0, 0)),
               ((1, 0, 0), (0, 2, 0)))
    intersection = {(0, 0, 0)}
    for ideal in primary:
        intersection = {tuple(max(a, b) for a, b in zip(left, right, strict=True))
                        for left in intersection for right in ideal}
    minimal = {m for m in intersection if not any(
        n != m and all(a <= b for a, b in zip(n, m, strict=True)) for n in intersection
    )}
    if minimal != set(GENERATORS):
        raise ValueError("the actual I6 ideal lost its fat-axis primary decomposition")
    cox = schoen_geometry().cover.cox
    pure = {(3, 0, 0), (0, 3, 0), (0, 0, 3)}
    if ({m for m, _c in cox.cubic_f.terms} != pure
        or not {m for m, _c in cox.cubic_g.terms} <= pure | {(1, 1, 1)}
        or cox.cubic_g.coefficient((1, 1, 1)).is_zero()
        or (1, 1, 1) not in GENERATORS):
        raise ValueError("the actual Schoen pencil no longer satisfies the axis proof inputs")


def _orbits(
    degree: tuple[int, int, int], p_frame: int, t_frame: int, ideal: bool,
) -> tuple[Orbit, ...]:
    """Return normalized invariant orbits, including admissible one-point stabilizers."""

    p, t, _equations = _inputs()
    seen = set()
    result = []
    x, u, base = degree
    for x0 in range(x + 1):
        for x1 in range(x - x0 + 1):
            for u0 in range(u + 1):
                for u1 in range(u - u0 + 1):
                    for mu in range(base + 1):
                        monomial = (x0, x1, x - x0 - x1, u0, u1, u - u0 - u1, mu, base - mu)
                        if monomial in seen or (ideal and not _belongs(monomial)):
                            continue
                        orbit = [monomial]
                        current = monomial
                        phase_sum = 0
                        for _ in range(3):
                            phase, current = _act(current, p, p_frame)
                            phase_sum = (phase_sum + phase) % 3
                            orbit.append(current)
                        if current != monomial or phase_sum:
                            raise ValueError("the scalar section P action lost order three")
                        seen.update(orbit)
                        canonical = min(orbit)
                        if _act(canonical, t, t_frame)[0]:
                            continue
                        phase, image = _act(canonical, p, p_frame)
                        if image == canonical and phase:
                            continue
                        current = canonical
                        value = 0
                        terms = []
                        for _ in range(len(set(orbit))):
                            terms.append((current, value))
                            phase, current = _act(current, p, p_frame)
                            value = (value + phase) % 3
                        if current != canonical or value:
                            raise ValueError("the normalized stabilizer orbit did not close")
                        result.append((canonical, tuple(terms)))
    return tuple(sorted(result))


def _columns(target: tuple[Orbit, ...], sources):
    """Multiply actual equations and reconstruct every exact invariant image."""

    target_index = {label: index for index, (label, _terms) in enumerate(target)}
    columns = []
    for name, source, polynomial in sources:
        for canonical, terms in source:
            product = {}
            for monomial, phase in terms:
                for m, coefficient in polynomial.items():
                    image = tuple(a + b for a, b in zip(monomial, m, strict=True))
                    _accumulate(product, image, _multiply(ROOT_PAIRS[phase], coefficient))
            coordinates = {target_index[m]: value for m, value in product.items()
                           if m in target_index}
            full = {}
            for index, coefficient in coordinates.items():
                for monomial, phase in target[index][1]:
                    _accumulate(full, monomial, _multiply(coefficient, ROOT_PAIRS[phase]))
            if full != product:
                raise ValueError("an actual second section relation escaped the invariant span")
            columns.append({"source": name, "source_canonical_monomial": list(canonical),
                            "coordinates": [[index, list(value)]
                                            for index, value in sorted(coordinates.items())]})
    return columns


def _quotient(target, sources, expected_rank, expected_dimension):
    columns = _columns(target, sources)
    rows, selected = _modular_pivots(columns, 7, 2)
    if len(rows) != expected_rank or len(selected) != expected_rank:
        raise ValueError("the exact second section relation minor did not reach its rank bound")
    pivot_set = set(rows)
    basis = [target[index][0] for index in range(len(target)) if index not in pivot_set]
    if len(basis) != expected_dimension:
        raise ValueError("the actual second section quotient dimension changed")
    return columns, basis, {"target_dimension": len(target), "source_dimensions": [
        len(source) for _name, source, _polynomial in sources
    ], "certified_rank": len(rows), "pivot_rows": list(rows), "minor_columns": list(selected),
        "basis_labels": [list(label) for label in basis]}


@cache
def _extension_polynomials():
    contraction, _actions, _frames = _context()
    groups = {}
    for term in contraction.left.extension_terms:
        if term.source not in range(1, 5):
            continue
        if (term.target != 0 or term.koszul_summand != "k0" or term.p_monomial != (-1, -1)
            or term.x_monomial != (0, 0, 0) or any(e < 0 for e in term.u_monomial)
            or term.cell[2] != (0, 1) or any(len(s) != 1 for s in term.cell[:2])):
            raise ValueError("the actual second extension lost its polynomial/P1-only shape")
        monomial = term.x_monomial + term.u_monomial + term.p_monomial
        value = _pair(term.coefficient * (-1 if term.parent_degree == 0 else 1))
        groups.setdefault((term.source, monomial), {})[term.cell[0][0], term.cell[1][0]] = value
    result = []
    for (index, monomial), charts in sorted(groups.items()):
        if (set(charts) != {(x, u) for x in range(3) for u in range(3)}
            or len(set(charts.values())) != 1):
            raise ValueError("the actual second extension has hidden plane-chart dependence")
        result.append((index, monomial, next(iter(charts.values()))))
    if len(result) != 12:
        raise ValueError("the actual second extension lost its twelve cubic terms")
    return tuple(result)


@cache
def _templates():
    contraction, _actions, _frames = _context()
    small = replace(contraction.left, twist=(contraction.left.twist[0] - 15,
                                            contraction.left.twist[1] - 12,
                                            contraction.left.twist[2]),
                    objects=tuple(replace(o, line_degree=(o.line_degree[0] - 15,
                                                          o.line_degree[1] - 12,
                                                          o.line_degree[2]))
                                  for o in contraction.left.objects))
    local = _MixedContraction(small, contraction.right)
    result = {}
    for index in range(1, 5):
        for base in ((2, 0), (1, 1), (0, 2)):
            seed = _include(ReducedBasisEntry(0, local.components[index, 0, "k0"],
                                            (0, 0, 0), (0, 0, 0), base))
            residual = local.differential(seed)
            primitive, depth = perturbed_homotopy(residual, local)
            if residual.is_zero() or depth != 1 or local.differential(primitive) != residual:
                raise ValueError("an actual second Serre template did not solve the residual")
            lift = seed + primitive.scale(-1)
            if not local.differential(lift).is_zero():
                raise ValueError("an actual second Serre template is not full-complex closed")
            result[index, base] = _compact(lift, 5)
    return result


def _deck(section, generator):
    return _deck_from_frame(section, _inputs()[generator], _context()[2][generator])


def verify_section(section: CompactSection) -> None:
    """Check exact full closure and strict invariance using actual V2 data."""

    contraction, _actions, _frames = _context()
    residual = {}
    terms = dict(section)
    if not terms or len(terms) != len(section):
        raise ValueError("the second section has an empty or repeated term list")
    for (index, monomial, chart), value in section:
        if index not in range(5) or chart not in (0, 1) or value == (0, 0):
            raise ValueError("invalid second section component or coefficient")
        if (any(e < 0 for e in monomial[:6])
            or any(e < 0 and i != chart for i, e in enumerate(monomial[6:]))
            or tuple(map(sum, (monomial[:3], monomial[3:6], monomial[6:])))
            != contraction.left.objects[index].line_degree):
            raise ValueError("a second section has the wrong degree or an illegal Laurent pole")
        if index == 0:
            _accumulate(residual, monomial, _multiply(value, (1 if chart else -1, 0)))
        else:
            if terms.get((index, monomial, 1 - chart)) != value:
                raise ValueError("the second F0 preimage is not global on P1")
            if chart == 1:
                for source, m, coefficient in _extension_polynomials():
                    if source == index:
                        image = tuple(a + b for a, b in zip(monomial, m, strict=True))
                        _accumulate(residual, image, _multiply(value, coefficient))
    if residual:
        raise ValueError("the actual second non-split section is not closed")
    if any(_deck(section, g) != section for g in (0, 1)):
        raise ValueError("the actual second section is not strictly invariant")


def quotient_lift(canonical: Monomial) -> CompactSection:
    """Transport an actual template and sum the source-checked P orbit."""

    if (not _belongs(canonical) or any(e < 0 for e in canonical)
        or tuple(map(sum, (canonical[:3], canonical[3:6], canonical[6:]))) != (15, 15, 2)):
        raise ValueError("the label is not an actual second ideal section")
    block = next(i for i, g in enumerate(GENERATORS)
                 if all(a >= b for a, b in zip(canonical[3:6], g, strict=True)))
    factor = canonical[:3] + tuple(a - b for a, b in zip(canonical[3:6], GENERATORS[block],
                                                        strict=True))
    values = {}
    for (index, monomial, chart), value in _templates()[block + 1, canonical[6:]]:
        target = tuple(a + b for a, b in zip(monomial[:6], factor, strict=True)) + monomial[6:]
        _accumulate(values, (index, target, chart), value)
    seed = _freeze(values)
    current = seed
    for _ in range(2):
        current = _deck(current, 0)
        for key, value in current:
            _accumulate(values, key, value)
    if _deck(current, 0) != seed:
        raise ValueError("the actual second lift lost P order three")
    result = _freeze(values)
    verify_section(result)
    return result


def expand_section(section: CompactSection) -> SparseOuterCechCochain:
    contraction, _actions, _frames = _context()
    return SparseOuterCechCochain(tuple(
        (OuterCechBasis(contraction.components[index, 0, "k0"], m[:3], m[3:6], m[6:],
                        ((x,), (u,), (chart,))), Eisenstein(*value))
        for (index, m, chart), value in section for x in range(3) for u in range(3)
    ))


def full_action(cochain, generator):
    contraction, actions, frames = _context()
    return _full_action(cochain, contraction.left, contraction.right, actions[generator],
                        (frames[generator], Matrix.identity(1, scalar_type=Eisenstein)))


def write_second_sections() -> dict[str, object]:
    """Construct all 2690 actual V2 sections with exact quotient certificates."""

    generation_digest, generation = _verified_payload(GENERATION)
    cone_digest, cone = _verified_payload(CONE)
    if (generation.get("generating_twist_cover_degree") != list(TWIST)
        or generation.get("quotient_h0_constituents_at_generating_twist") != [2655, 2690]
        or cone.get("ray_character_exponents") != [0, 1]
        or cone.get("common_flat_character_twist") != [1, 2]
        or generation.get("prerequisite_artifact_digests", {}).get("alternate_cone")
        != cone_digest):
        raise ValueError("the frozen alternate generating-twist inputs changed")
    _context()
    _regular_sequence_inputs()
    equations = _inputs()[2]
    eliminant: Polynomial = {cast(Monomial, (*m, 0, 0)): _pair(c) for m, c in _eliminant().items()}
    a_target = _orbits((15, 15, 0), 0, 0, False)
    a_source = _orbits((12, 12, 0), 0, 0, False)
    a_columns, a_basis, a_record = _quotient(
        a_target, (("eliminant", a_source, eliminant),), 921, 1135,
    )
    q_target = _orbits((15, 15, 2), 1, 2, True)
    # Multiplication by an equation of character e uses source frame q*e,
    # not q/e: q*g(s*p)=q*g(s)*e*p must equal s*p.
    q_sources = (_orbits((12, 15, 1), 0, 2, True), _orbits((15, 12, 1), 1, 2, True))
    syzygies = _orbits((12, 12, 0), 0, 2, True)
    upper = sum(map(len, q_sources)) - len(syzygies)
    q_columns, q_basis, q_record = _quotient(q_target, tuple(
        (f"equation{i + 1}", source, equations[i]) for i, source in enumerate(q_sources)
    ), upper, 1555)
    q_record["syzygy_dimension"] = len(syzygies)
    q_record["structural_relation_rank_upper_bound"] = upper
    q_record["source_frame_exponents"] = [[0, 2], [1, 2]]
    q_record["syzygy_frame_exponents"] = [0, 2]
    records = []
    for kind, basis in (("subline", a_basis), ("quotient_lift", q_basis)):
        for label in basis:
            if kind == "subline":
                terms = next(terms for canonical, terms in a_target if canonical == label)
                section = _freeze({(0, m, chart): ROOT_PAIRS[phase]
                                   for m, phase in terms for chart in (0, 1)})
                verify_section(section)
            else:
                section = quotient_lift(label)
            records.append({"kind": kind, "canonical_monomial": list(label),
                            "terms": [[index, list(m), chart, list(value)]
                                      for (index, m, chart), value in section]})
        print(f"constructed_second_{kind}_sections: {len(basis)}", flush=True)
    sections_raw = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    relations_raw = json.dumps({"subline": a_columns, "quotient": q_columns},
                               sort_keys=True, separators=(",", ":")).encode()
    archives = ((SECTIONS, sections_raw), (RELATIONS, relations_raw))
    payload = {
        "schema": "alternate-metric-second-sections-v1",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "ray_character_exponents": [0, 1], "common_flat_character_twist": [1, 2],
        "twist_cover_degree": list(TWIST), "subline_degree": [15, 15, 0],
        "ideal_degree": [15, 15, 2], "subline_frame_exponents": [0, 0],
        "ideal_frame_exponents": [1, 2], "ideal_generators_u": [list(g) for g in GENERATORS],
        "section_dimension": len(records), "subline_section_count": len(a_basis),
        "quotient_lift_count": len(q_basis), "subline_certificate": a_record,
        "quotient_certificate": q_record, "certificate_prime": 7, "certificate_omega_residue": 2,
        "subline_fixed_orbit_counts": [sum(len(terms) == 1 for _m, terms in orbits)
                                       for orbits in (a_target, a_source)],
        "full_differential_template_count": len(_templates()),
        "expanded_full_cover_term_count": 9 * sum(len(r["terms"]) for r in records),
        "chart_encoding": "each term repeats identically on all nine P2 x P2 vertex charts",
        "term_encoding": "[object_index, x_u_mu_nu_exponents, P1_vertex, [a,b]] for a+b*omega",
        "coefficient_ring": "Z[omega], omega^2+omega+1=0",
        "ideal_koszul_regular_sequence_on_fat_axis_quotient": True,
        "actual_ideal_frame_source_checked": True, "all_sections_full_differential_closed": True,
        "all_sections_strictly_p_t_invariant": True,
        "second_constituent_section_basis_available": True,
        "rank_four_section_basis_available": False, "numerical_metrics_available": False,
        "physical_yukawas_available": False, "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "generation": generation_digest, "alternate_cone": cone_digest,
        },
    }
    for name, (path, raw) in zip(("section", "relation"), archives, strict=True):
        archive = gzip.compress(raw, mtime=0)
        temporary = path.with_name(f".{path.name}.tmp")
        temporary.write_bytes(archive)
        temporary.replace(path)
        payload[f"{name}_archive"] = path.relative_to(ROOT).as_posix()
        payload[f"{name}_archive_sha256"] = hashlib.sha256(archive).hexdigest()
        payload[f"exact_{name}_stream_sha256"] = hashlib.sha256(raw).hexdigest()
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.tmp")
    temporary.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    temporary.replace(OUTPUT)
    return payload


if __name__ == "__main__":
    report = write_second_sections()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"second_constituent_section_dimension: {report['section_dimension']}")
