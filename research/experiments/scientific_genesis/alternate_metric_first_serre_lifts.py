"""Lift actual quotient sections through the frozen first Serre extension.

Owns:
    Explicit equivariant Hilbert--Burch preimages, actual extension residuals,
    finite ambient Čech--Koszul primitives, and strict invariant lift checks.

Depends on:
    The certified first quotient basis, actual mixed constituent cochains,
    repaired homogeneous frames, and the existing full-cover contraction.

Must not:
    Replace a non-split lift by an ideal polynomial, assume deck averaging
    commutes with the differential, or claim a rank-four basis or metrics.

Phase 0:
    Research-only actual first-constituent section lifting calculation.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from dataclasses import dataclass, replace
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    ReducedBasisEntry,
    SparseOuterCechCochain,
    _include,
)
from research.experiments.computable_carrier.schoen_sparse_actions import SchoenSparseDeckAction

from .alternate_constituent_hom_actions import _common_frame
from .alternate_metric_first_quotient_sections import OUTPUT as QUOTIENT
from .alternate_metric_first_quotient_sections import (
    ROOT_PAIRS,
    Monomial,
    Pair,
    _act,
    _add,
    _inputs,
    _multiply,
    _pair,
)
from .alternate_metric_first_resolution_ambient_sections import _first_blocks
from .alternate_metric_first_subline_sections import OUTPUT as SUBLINE
from .alternate_metric_quotient_generation import OUTPUT as GENERATION
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_common_dga import perturbed_homotopy
from .mixed_schoen_outer_actions import _full_action, _MixedContraction
from .mixed_schoen_outer_transfer import mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload

TWIST = (14, 16, 1)
IDEAL_GENERATORS = ((1, 1, 0), (1, 0, 1), (0, 1, 1))
ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_metric_first_serre_lifts.json"
SECTIONS = OUTPUT.with_suffix(".sections.json.gz")

# Each term represents the same polynomial on all nine P2 x P2 vertex charts.
# The P1 chart remains explicit, including every permitted Laurent pole.
type SectionKey = tuple[int, Monomial, int]
type CompactSection = tuple[tuple[SectionKey, Pair], ...]


@cache
def _context() -> tuple[
    _MixedContraction,
    tuple[SchoenSparseDeckAction, SchoenSparseDeckAction],
    tuple[Matrix, Matrix],
]:
    first = mixed_schoen_constituents()[0]
    twisted = replace(
        first,
        twist=cast(tuple[int, int, int], tuple(a + b for a, b in zip(
            first.twist, TWIST, strict=True,
        ))),
        objects=tuple(replace(item, line_degree=cast(tuple[int, int, int], tuple(
            a + b for a, b in zip(item.line_degree, TWIST, strict=True)
        ))) for item in first.objects),
    )
    contraction = _MixedContraction(twisted, mixed_schoen_unit())
    p, t, _f0, _f1 = _first_blocks()
    frames = (_common_frame(first, p).scale(OMEGA), _common_frame(first, t).scale(OMEGA2))
    if twisted.objects[0].line_degree != (13, 17, 0):
        raise ValueError("the actual first Serre subline degree changed")
    return contraction, (p, t), frames


def _action(cochain: SparseOuterCechCochain, generator: int) -> SparseOuterCechCochain:
    contraction, actions, frames = _context()
    return _full_action(
        cochain, contraction.left, contraction.right, actions[generator],
        (frames[generator], Matrix.identity(1, scalar_type=Eisenstein)),
    )


def _hilbert_burch_preimage(canonical: Monomial) -> SparseOuterCechCochain:
    """Choose a declared divisor of the ideal monomial, then sum its P orbit."""

    if (
        len(canonical) != 8 or any(value < 0 for value in canonical)
        or (sum(canonical[:3]), sum(canonical[3:6]), sum(canonical[6:])) != (13, 17, 2)
    ):
        raise ValueError("a quotient label must have the actual nonnegative ideal degree")
    block = next((index for index, generator in enumerate(IDEAL_GENERATORS)
                  if all(a >= b for a, b in zip(canonical[:3], generator, strict=True))), None)
    if block is None:
        raise ValueError("the quotient monomial is outside the actual coordinate-point ideal")
    contraction, _actions, _frames = _context()
    component = contraction.components[(1 + block, 0, "k0")]
    x = cast(tuple[int, int, int], tuple(a - b for a, b in zip(
        canonical[:3], IDEAL_GENERATORS[block], strict=True,
    )))
    seed = _include(ReducedBasisEntry(
        0, component, x, cast(tuple[int, int, int], canonical[3:6]),
        cast(tuple[int, int], canonical[6:]),
    ))
    if _action(seed, 1) != seed:
        raise ValueError("the declared quotient seed is not in the T-fixed sector")
    p_seed = _action(seed, 0)
    p2_seed = _action(p_seed, 0)
    if _action(p2_seed, 0) != seed:
        raise ValueError("the actual Hilbert--Burch preimage lost P order three")
    result = seed + p_seed + p2_seed
    if _action(result, 0) != result or _action(result, 1) != result:
        raise ValueError("the actual Hilbert--Burch preimage is not invariant")
    return result


def _project(cochain: SparseOuterCechCochain) -> SparseOuterCechCochain:
    """Use the explicitly normalized 1/9 Reynolds sum in the actual frame."""

    result = SparseOuterCechCochain()
    p_term = cochain
    for _ in range(3):
        term = p_term
        for _ in range(3):
            result = result + term
            term = _action(term, 1)
        if term != p_term:
            raise ValueError("the full first-section T action lost order three")
        p_term = _action(p_term, 0)
    if p_term != cochain:
        raise ValueError("the full first-section P action lost order three")
    projected = result.scale(Eisenstein(1) / 9)
    if _action(projected, 0) != projected or _action(projected, 1) != projected:
        raise ValueError("the Reynolds sum is not fixed by the two full deck actions")
    return projected


@dataclass(frozen=True, slots=True)
class FirstSerreLift:
    """One exact actual quotient lift with its retained non-split correction."""

    canonical_monomial: Monomial
    preimage: SparseOuterCechCochain
    extension_residual: SparseOuterCechCochain
    primitive: SparseOuterCechCochain
    invariant_lift: SparseOuterCechCochain
    homotopy_depth: int


def lift_first_quotient_section(canonical: Monomial) -> FirstSerreLift:
    """Solve the genuine full-complex lifting equation and verify the deck sum."""

    contraction, _actions, _frames = _context()
    preimage = _hilbert_burch_preimage(canonical)
    residual = contraction.differential(preimage)
    if any(basis.component.left_index != 0 or basis.total_degree != 1
           for basis, _coefficient in residual.terms):
        raise ValueError("the actual extension residual is not a subline degree-one cocycle")
    if not contraction.differential(residual).is_zero():
        raise ValueError("the actual first extension residual is not closed")
    primitive, depth = perturbed_homotopy(residual, contraction)
    if contraction.differential(primitive) != residual:
        raise ValueError("the actual positive-twist subline contraction did not solve the residual")
    raw = preimage + primitive.scale(-1)
    if not contraction.differential(raw).is_zero():
        raise ValueError("the constructed non-split Serre lift is not closed")
    lift = _project(raw)
    if not contraction.differential(lift).is_zero():
        raise ValueError("the actual deck projector destroyed full-complex Serre closure")
    quotient_part = SparseOuterCechCochain(tuple(
        (basis, coefficient) for basis, coefficient in lift.terms
        if basis.component.left_index != 0
    ))
    if quotient_part != preimage:
        raise ValueError("the invariant Serre lift changed its specified quotient representative")
    return FirstSerreLift(canonical, preimage, residual, primitive, lift, depth)


def _freeze(values: dict[SectionKey, Pair]) -> CompactSection:
    return tuple((key, value) for key, value in sorted(values.items()) if value != (0, 0))


def _accumulate(values: dict, key: tuple, value: Pair) -> None:
    updated = _add(values.get(key, (0, 0)), value)
    if updated == (0, 0):
        values.pop(key, None)
    else:
        values[key] = updated


def _compact(cochain: SparseOuterCechCochain, object_count: int = 4) -> CompactSection:
    """Check, rather than assume, polynomial constancy on the nine plane charts."""

    groups: dict[SectionKey, dict[tuple[int, int], Pair]] = {}
    for basis, value in cochain.terms:
        if (
            basis.total_degree != 0 or basis.component.koszul_summand != "k0"
            or basis.component.right_index != 0
            or basis.component.left_index not in range(object_count)
            or any(len(simplex) != 1 for simplex in basis.cell)
            or any(exponent < 0 for exponent in (*basis.x_monomial, *basis.u_monomial))
        ):
            raise ValueError("the first-section polynomial-chart compression does not apply")
        monomial = cast(Monomial, basis.x_monomial + basis.u_monomial + basis.p_monomial)
        key = (basis.component.left_index, monomial, basis.cell[2][0])
        groups.setdefault(key, {})[(basis.cell[0][0], basis.cell[1][0])] = _pair(value)
    result = {}
    for key, charts in groups.items():
        if set(charts) != {(x, u) for x in range(3) for u in range(3)}:
            raise ValueError("a section is not defined identically on every plane vertex")
        if len(set(charts.values())) != 1:
            raise ValueError("a section has a hidden plane-chart dependence")
        result[key] = next(iter(charts.values()))
    return _freeze(result)


def expand_section(section: CompactSection) -> SparseOuterCechCochain:
    """Expand every declared chart term into its actual full-cover cochain."""

    contraction, _actions, _frames = _context()
    return SparseOuterCechCochain(tuple(
        (OuterCechBasis(
            contraction.components[(index, 0, "k0")],
            cast(tuple[int, int, int], monomial[:3]),
            cast(tuple[int, int, int], monomial[3:6]),
            cast(tuple[int, int], monomial[6:]), ((x,), (u,), (chart,)),
        ), Eisenstein(*coefficient))
        for (index, monomial, chart), coefficient in section
        for x in range(3) for u in range(3)
    ))


@cache
def first_lift_templates() -> tuple[tuple[int, tuple[int, int], CompactSection], ...]:
    """Prove all nine generator/P1 lifts once in the actual full differential."""

    contraction, _actions, _frames = _context()
    small = replace(contraction.left, twist=(
        contraction.left.twist[0] - 11, contraction.left.twist[1] - 17,
        contraction.left.twist[2],
    ), objects=tuple(
        replace(item, line_degree=(item.line_degree[0] - 11, item.line_degree[1] - 17,
                                   item.line_degree[2])) for item in contraction.left.objects
    ))
    small_contraction = _MixedContraction(small, contraction.right)
    result = []
    for index in (1, 2, 3):
        for p in ((2, 0), (1, 1), (0, 2)):
            seed = _include(ReducedBasisEntry(
                0, small_contraction.components[(index, 0, "k0")], (0, 0, 0), (0, 0, 0), p,
            ))
            residual = small_contraction.differential(seed)
            if residual.is_zero() or any(
                basis.component.left_index != 0 or basis.component.koszul_summand != "k0"
                or basis.cell[2] != (0, 1) or basis.cech_degree != 1
                or any(e < 0 for e in (*basis.x_monomial, *basis.u_monomial))
                for basis, _value in residual.terms
            ):
                raise ValueError("the actual residual lost its polynomial/P1-only shape")
            primitive, depth = perturbed_homotopy(residual, small_contraction)
            if depth != 1 or small_contraction.differential(primitive) != residual:
                raise ValueError("the finite P1 lift template is not a genuine primitive")
            lift = seed + primitive.scale(-1)
            if not small_contraction.differential(lift).is_zero():
                raise ValueError("the finite full-complex lift template is not closed")
            result.append((index, p, _compact(lift)))
    return tuple(result)


@cache
def _extension_polynomials() -> tuple[tuple[int, Monomial, Pair], ...]:
    """Read actual F0-to-A Laurent arrows and check their entire chart pattern."""

    contraction, _actions, _frames = _context()
    groups: dict[tuple[int, Monomial], dict[tuple[int, int], Pair]] = {}
    for term in contraction.left.extension_terms:
        if term.source not in (1, 2, 3):
            continue
        if (
            term.target != 0 or term.koszul_summand != "k0"
            or term.cell[2] != (0, 1) or any(len(s) != 1 for s in term.cell[:2])
            or term.cech_degree != 1 or term.u_monomial != (0, 0, 0)
            or term.p_monomial != (-1, -1) or any(e < 0 for e in term.x_monomial)
        ):
            raise ValueError("the first extension is not polynomial with a sole P1 pole")
        monomial = cast(Monomial, term.x_monomial + term.u_monomial + term.p_monomial)
        signed = term.coefficient * (-1 if term.parent_degree == 0 else 1)
        groups.setdefault((term.source, monomial), {})[
            term.cell[0][0], term.cell[1][0]
        ] = _pair(signed)
    result = []
    for (index, monomial), charts in sorted(groups.items()):
        if set(charts) != {(x, u) for x in range(3) for u in range(3)}:
            raise ValueError("an actual extension coefficient has missing plane charts")
        if len(set(charts.values())) != 1:
            raise ValueError("an actual extension coefficient depends on the plane chart")
        result.append((index, monomial, next(iter(charts.values()))))
    if len(result) != 6 or {index for index, _m, _c in result} != {1, 2, 3}:
        raise ValueError("the actual first extension has changed its six polynomial terms")
    return tuple(result)


def _deck(section: CompactSection, generator: int) -> CompactSection:
    """Act on compact cochains using the source-checked coordinate and object frames."""

    images = _inputs()[generator]
    _contraction, _actions, frames = _context()
    return _deck_from_frame(section, images, frames[generator])


def _deck_from_frame(
    section: CompactSection, images: tuple[tuple[int, int], ...], frame: Matrix,
) -> CompactSection:
    """Apply a declared homogeneous frame to polynomial-plane section terms."""

    if any(target != source for source, (_phase, target) in enumerate(images[6:], 6)):
        raise ValueError("the P1 chart-preserving compression no longer applies")
    result = {}
    for (index, monomial, chart), coefficient in section:
        phase, image = _act(monomial, images)
        geometric = _multiply(coefficient, ROOT_PAIRS[phase])
        for target in range(frame.row_count):
            value = _multiply(geometric, _pair(cast(Eisenstein, frame[target][index])))
            _accumulate(result, (target, image, chart), value)
    return _freeze(result)


def verify_compact_section(section: CompactSection) -> None:
    """Check exact regularity, full closure, and both strict deck invariances."""

    contraction, _actions, _frames = _context()
    if not section or len({key for key, _value in section}) != len(section):
        raise ValueError("a section must have a nonempty normalized term list")
    residual: dict[Monomial, Pair] = {}
    by_key = dict(section)
    extensions = _extension_polynomials()
    for (index, monomial, chart), coefficient in section:
        if index not in range(4) or chart not in (0, 1) or coefficient == (0, 0):
            raise ValueError("invalid compact first-section index or coefficient")
        if any(e < 0 for e in monomial[:6]) or any(
            e < 0 and coordinate != chart for coordinate, e in enumerate(monomial[6:])
        ):
            raise ValueError("a compact section has an unpermitted Laurent pole")
        if tuple(map(sum, (monomial[:3], monomial[3:6], monomial[6:]))) != (
            contraction.left.objects[index].line_degree
        ):
            raise ValueError("a compact first-section multidegree is incorrect")
        if index == 0:
            _accumulate(residual, monomial, _multiply(coefficient, (1 if chart else -1, 0)))
        else:
            if by_key.get((index, monomial, 1 - chart)) != coefficient:
                raise ValueError("an F0 preimage is not a global polynomial")
            if chart == 1:  # Alexander--Whitney: the right vertex is the overlap's suffix.
                for source, arrow_monomial, arrow_value in extensions:
                    if source == index:
                        image = cast(Monomial, tuple(a + b for a, b in zip(
                            monomial, arrow_monomial, strict=True,
                        )))
                        _accumulate(residual, image, _multiply(coefficient, arrow_value))
    if residual:
        raise ValueError("the actual non-split compact section is not closed")
    if _deck(section, 0) != section or _deck(section, 1) != section:
        raise ValueError("the actual compact section is not strictly deck invariant")


def compressed_first_quotient_section(canonical: Monomial) -> CompactSection:
    """Transport exact templates by global plane polynomials, then sum the P orbit."""

    if (
        len(canonical) != 8 or any(e < 0 for e in canonical)
        or tuple(map(sum, (canonical[:3], canonical[3:6], canonical[6:]))) != (13, 17, 2)
    ):
        raise ValueError("a quotient label must have the actual nonnegative ideal degree")
    block = next((i for i, g in enumerate(IDEAL_GENERATORS)
                  if all(a >= b for a, b in zip(canonical[:3], g, strict=True))), None)
    if block is None:
        raise ValueError("the quotient label is outside the actual coordinate-point ideal")
    monomial = cast(Monomial, tuple(
        a - b for a, b in zip(canonical[:3], IDEAL_GENERATORS[block], strict=True)
    ) + canonical[3:])
    template = next(terms for index, p, terms in first_lift_templates()
                    if index == block + 1 and p == canonical[6:])
    values = {}
    for (index, template_monomial, chart), coefficient in template:
        target = cast(Monomial, tuple(
            a + b for a, b in zip(template_monomial[:6], monomial[:6], strict=True)
        ) + template_monomial[6:])
        _accumulate(values, (index, target, chart), coefficient)
    seed = _freeze(values)
    current = seed
    for _ in range(2):
        current = _deck(current, 0)
        for key, value in current:
            _accumulate(values, key, value)
    if _deck(current, 0) != seed:
        raise ValueError("the transported first lift lost P order three")
    result = _freeze(values)
    verify_compact_section(result)
    return result


def _subline_section(canonical: tuple[int, ...]) -> CompactSection:
    monomial = cast(Monomial, (*canonical, 0, 0))
    current: CompactSection = (((0, monomial, 0), (1, 0)), ((0, monomial, 1), (1, 0)))
    values = dict(current)
    seed = current
    for _ in range(2):
        current = _deck(current, 0)
        for key, value in current:
            _accumulate(values, key, value)
    if _deck(current, 0) != seed:
        raise ValueError("the actual subline orbit lost P order three")
    result = _freeze(values)
    verify_compact_section(result)
    return result


def write_first_serre_lifts() -> dict[str, object]:
    """Construct the full actual first-constituent basis without repeated homotopy solves."""

    subline_digest, subline = _verified_payload(SUBLINE)
    quotient_digest, quotient = _verified_payload(QUOTIENT)
    generation_digest, generation = _verified_payload(GENERATION)
    if (
        generation.get("quotient_h0_constituents_at_generating_twist") != [2655, 2690]
        or generation.get("first_constituent_h1_vanishes_at_generating_twist") is not True
        or subline.get("quotient_subline_section_count") != 1115
        or quotient.get("quotient_section_dimension") != 1540
        or subline.get("prerequisite_artifact_digests", {}).get("generation") != generation_digest
        or quotient.get("prerequisite_artifact_digests", {}).get("generation") != generation_digest
    ):
        raise ValueError("the full first-constituent exact-sequence prerequisites changed")
    records = []
    expanded_count = 0
    for kind, labels in (
        ("subline", subline["quotient_basis_monomials_x_u"]),
        ("quotient_lift", quotient["quotient_basis_canonical_monomials"]),
    ):
        for label in labels:
            terms = (_subline_section(tuple(label)) if kind == "subline"
                     else compressed_first_quotient_section(cast(Monomial, tuple(label))))
            records.append({
                "kind": kind, "canonical_monomial": label,
                "terms": [[index, list(monomial), chart, list(value)]
                          for (index, monomial, chart), value in terms],
            })
            expanded_count += len(terms) * 9
        print(f"constructed_{kind}_sections: {len(labels)}", flush=True)
    if len(records) != 2655:
        raise ValueError("the exact first-constituent section dimension was not reached")
    raw = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    archive = gzip.compress(raw, mtime=0)
    payload = {
        "schema": "alternate-metric-first-serre-lifts-v1",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "twist_cover_degree": list(TWIST), "common_flat_character_twist": [1, 2],
        "section_dimension": len(records), "subline_section_count": 1115,
        "quotient_lift_count": 1540,
        "full_differential_template_count": len(first_lift_templates()),
        "structural_compression_question": (
            "Do polynomial plane factors transport all actual first Serre lifts?"
        ),
        "structural_compression_answer": (
            "Yes: the F0 extension residual is polynomial on both planes and supported "
            "only on the P1 overlap; nine exact templates transport by plane monomials."
        ),
        "coefficient_ring": "Z[omega], omega^2+omega+1=0",
        "chart_encoding": "each term repeats identically on all nine P2 x P2 vertex charts",
        "term_encoding": "[object_index, x_u_mu_nu_exponents, P1_vertex, [a,b]] for a+b*omega",
        "expanded_full_cover_term_count": expanded_count,
        "section_archive": SECTIONS.relative_to(ROOT).as_posix(),
        "section_archive_sha256": hashlib.sha256(archive).hexdigest(),
        "exact_section_stream_sha256": hashlib.sha256(raw).hexdigest(),
        "all_sections_full_differential_closed": True,
        "all_sections_strictly_p_t_invariant": True,
        "first_constituent_section_basis_available": True,
        "second_constituent_section_basis_available": False,
        "rank_four_section_basis_available": False,
        "numerical_metrics_available": False, "physical_yukawas_available": False,
        "observational_inputs_used": False,
        "basis_proof": "injective subline basis plus lifts of the full quotient basis in H0",
        "prerequisite_artifact_digests": {
            "subline": subline_digest, "quotient": quotient_digest, "generation": generation_digest,
        },
    }
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary_archive = SECTIONS.with_name(f".{SECTIONS.name}.tmp")
    temporary_archive.write_bytes(archive)
    temporary_archive.replace(SECTIONS)
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.tmp")
    temporary.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    temporary.replace(OUTPUT)
    return payload


if __name__ == "__main__":
    report = write_first_serre_lifts()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"first_constituent_section_dimension: {report['section_dimension']}")
