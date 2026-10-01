"""Construct actual first Serre-quotient sections by an ideal Koszul quotient.

Owns:
    Source-checked Hilbert--Burch ideal identification, scalar equivariant
    orbit sections, exact integral relation columns, and a modular minor
    certificate for a complementary Q(omega) section basis.

Depends on:
    The actual first constituent and repaired frames, frozen Schoen equations,
    the generating-twist theorem, and the verified ambient section artifact.

Must not:
    Interpret finite-field specialization as physical approximation, identify
    quotient sections with their non-split Serre lifts, or infer metrics.

Phase 0:
    Research-only section construction conditional on the selected carrier.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from collections.abc import Iterator
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA2, Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)

from .alternate_metric_first_resolution_ambient_sections import (
    OUTPUT as AMBIENT,
)
from .alternate_metric_first_resolution_ambient_sections import (
    _first_blocks,
)
from .alternate_metric_quotient_generation import OUTPUT as GENERATION
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_metric_first_quotient_sections.json"
RELATIONS = OUTPUT.with_suffix(".relations.json.gz")
PRIME = 7
OMEGA_RESIDUE = 2
ROOT_PAIRS = ((1, 0), (0, 1), (-1, -1))

type Monomial = tuple[int, int, int, int, int, int, int, int]
type Pair = tuple[int, int]
type Orbit = tuple[Monomial, tuple[tuple[Monomial, int], ...]]
type Polynomial = dict[Monomial, Pair]


def _add(left: Pair, right: Pair) -> Pair:
    return left[0] + right[0], left[1] + right[1]


def _multiply(left: Pair, right: Pair) -> Pair:
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c - b * d


def _pair(value: Eisenstein) -> Pair:
    if value.a.denominator != 1 or value.b.denominator != 1:
        raise ValueError("the relation certificate requires integral Z[omega] coefficients")
    return value.a.numerator, value.b.numerator


def _phase(value: Eisenstein) -> int:
    try:
        return ROOT_PAIRS.index(_pair(value))
    except ValueError as error:
        raise ValueError("the coordinate lift is not a cubic-root monomial action") from error


@cache
def _inputs() -> tuple[
    tuple[tuple[int, int], ...], tuple[tuple[int, int], ...], tuple[Polynomial, Polynomial],
]:
    """Check the actual ideal, its frame, and both frozen equation units."""

    first = mixed_schoen_constituents()[0]
    p, t, f0, _f1 = _first_blocks()
    extension = first.full.alignment.action.derived.extension
    generators = extension.scheme.resolution.generators
    expected = ((1, 1, 0), (1, 0, 1), (0, 1, 1))
    if tuple(tuple(poly.terms) for poly in generators) != tuple(
        ((monomial, Eisenstein(1)),) for monomial in expected
    ):
        raise ValueError("the first ideal is no longer the coordinate-point I3 ideal")
    for column in range(2):
        total = generators[0].zero(generators[0].variable_count, scalar_type=Eisenstein)
        for row, generator in enumerate(generators):
            total = total + generator * extension.scheme.resolution.matrix[row][column]
        if not total.is_zero():
            raise ValueError("the actual Hilbert--Burch ideal map is not a complex")
    for action, frames in ((p, f0[0]), (t, f0[1])):
        for column, generator in enumerate(generators):
            left = generator.zero(generator.variable_count, scalar_type=Eisenstein)
            for row, polynomial in enumerate(generators):
                left = left + polynomial.scale(frames[row][column])
            right = generator.substitute_monomials(action.x_images).scale(OMEGA2)
            if left != right:
                raise ValueError("the actual ideal image frame is not (omega^2,omega^2)")
    actions = []
    for action in (p, t):
        images = []
        for offset, block in ((0, action.x_images), (3, action.u_images), (6, action.p_images)):
            for value, monomial in block:
                if sum(monomial) != 1 or monomial.count(1) != 1:
                    raise ValueError("a frozen coordinate substitution stopped being a permutation")
                images.append((_phase(value), offset + monomial.index(1)))
        actions.append(tuple(images))
    cox = schoen_geometry().cover.cox
    if cox.equations != (
        "p1 = mu F(x) + nu G(x)", "p2 = 2 nu F(u) + mu G(u)",
    ):
        raise ValueError("the actual Schoen equation presentation changed")
    equations: list[Polynomial] = [{}, {}]
    for equation, variable, factor, scalar, polynomial in (
        (0, 6, 0, 1, cox.cubic_f), (0, 7, 0, 1, cox.cubic_g),
        (1, 7, 3, 2, cox.cubic_f), (1, 6, 3, 1, cox.cubic_g),
    ):
        for monomial, coefficient in polynomial.terms:
            target = [0] * 8
            target[factor:factor + 3] = monomial
            target[variable] = 1
            equations[equation][cast(Monomial, tuple(target))] = _pair(coefficient * scalar)
    for action, expected_units in zip(actions, ((2, 0), (0, 0)), strict=True):
        for equation, unit in zip(equations, expected_units, strict=True):
            image: Polynomial = {}
            for monomial, coefficient in equation.items():
                phase, target = _act(monomial, action)
                image[target] = _multiply(coefficient, ROOT_PAIRS[phase])
            if image != {m: _multiply(c, ROOT_PAIRS[unit]) for m, c in equation.items()}:
                raise ValueError("the scalar ideal Koszul equation character changed")
    # The axis quotient is Cohen--Macaulay. On each axis p1 is x_i^3
    # times a nonzero linear form in (mu,nu). The second equation avoids
    # these components and the affine origin because F(u),G(u) are independent.
    pure_cubes = {(3, 0, 0), (0, 3, 0), (0, 0, 3)}
    if (
        {m for m, _c in cox.cubic_f.terms} != pure_cubes
        or not {m for m, _c in cox.cubic_g.terms} <= pure_cubes | {(1, 1, 1)}
        or cox.cubic_g.coefficient((1, 1, 1)).is_zero()
    ):
        raise ValueError("the coordinate-axis regular-sequence proof no longer applies")
    return actions[0], actions[1], (equations[0], equations[1])


def _act(
    monomial: Monomial, images: tuple[tuple[int, int], ...], frame: int = 0,
) -> tuple[int, Monomial]:
    result = [0] * 8
    phase = frame
    for exponent, (scalar, target) in zip(monomial, images, strict=True):
        phase += scalar * exponent
        result[target] += exponent
    return phase % 3, cast(Monomial, tuple(result))


def _monomials(degree: tuple[int, int, int]) -> Iterator[Monomial]:
    x, u, p = degree
    for x0 in range(x + 1):
        for x1 in range(x - x0 + 1):
            x2 = x - x0 - x1
            if sum(value > 0 for value in (x0, x1, x2)) < 2:
                continue
            for u0 in range(u + 1):
                for u1 in range(u - u0 + 1):
                    for mu in range(p + 1):
                        yield x0, x1, x2, u0, u1, u - u0 - u1, mu, p - mu


def _orbits(degree: tuple[int, int, int], p_frame: int, t_frame: int = 2) -> tuple[Orbit, ...]:
    p, t, _equations = _inputs()
    seen: set[Monomial] = set()
    result = []
    for monomial in _monomials(degree):
        if monomial in seen:
            continue
        images = []
        current = monomial
        for _ in range(3):
            images.append(current)
            _phase_value, current = _act(current, p)
        if current != monomial or len(set(images)) != 3:
            raise ValueError("the scalar ideal coordinate orbit is not free of order three")
        seen.update(images)
        canonical = min(images)
        t_phase, t_image = _act(canonical, t, t_frame)
        if t_image != canonical:
            raise ValueError("the actual T action stopped being diagonal")
        if t_phase:
            continue
        terms = []
        current = canonical
        coefficient = 0
        for _ in range(3):
            terms.append((current, coefficient))
            phase, current = _act(current, p, p_frame)
            coefficient = (coefficient + phase) % 3
        if current != canonical or coefficient:
            raise ValueError("the actual scalar ideal orbit lost P invariance")
        result.append((canonical, tuple(terms)))
    return tuple(result)


def _relation_columns(target: tuple[Orbit, ...]) -> Iterator[dict[str, object]]:
    _p, _t, equations = _inputs()
    target_index = {orbit[0]: index for index, orbit in enumerate(target)}
    membership = {
        monomial: (index, ROOT_PAIRS[phase])
        for index, orbit in enumerate(target) for monomial, phase in orbit[1]
    }
    for equation, degree, frame, expected in (
        (0, (10, 17, 1), 1, 2394), (1, (13, 14, 1), 2, 2720),
    ):
        source = _orbits(degree, frame)
        if len(source) != expected:
            raise ValueError("an actual ideal Koszul source dimension changed")
        for canonical, terms in source:
            product: Polynomial = {}
            for monomial, phase in terms:
                for equation_monomial, coefficient in equations[equation].items():
                    image = cast(Monomial, tuple(a + b for a, b in zip(
                        monomial, equation_monomial, strict=True,
                    )))
                    value = _multiply(ROOT_PAIRS[phase], coefficient)
                    updated = _add(product.get(image, (0, 0)), value)
                    if updated == (0, 0):
                        product.pop(image, None)
                    else:
                        product[image] = updated
            column = {target_index[m]: value for m, value in product.items() if m in target_index}
            reconstructed = {
                m: _multiply(column.get(index, (0, 0)), phase)
                for m, (index, phase) in membership.items() if index in column
            }
            reconstructed = {m: value for m, value in reconstructed.items() if value != (0, 0)}
            if reconstructed != product:
                raise ValueError("an exact equation image escaped the invariant ideal section span")
            yield {
                "equation": equation + 1,
                "source_canonical_monomial": list(canonical),
                "coordinates": [[row, list(value)] for row, value in sorted(column.items())],
            }


def _modular_pivots(
    columns: list[dict[str, object]], prime: int, omega: int,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Select an exact nonzero minor over a declared finite-field embedding.

    The existing sparse span solver demands independent inputs and tracks
    coordinates. Koszul columns contain a known 840-dimensional syzygy space;
    this research-only elimination accepts dependencies without provenance fill.
    """

    if (omega * omega + omega + 1) % prime:
        raise ValueError("omega does not define the declared ring homomorphism")
    pivots: dict[int, dict[int, int]] = {}
    independent = []
    for index, record in enumerate(columns):
        column = {
            row: (pair[0] + omega * pair[1]) % prime
            for row, pair in record["coordinates"]
        }
        column = {row: value for row, value in column.items() if value}
        while column:
            pivot = min(column)
            previous = pivots.get(pivot)
            if previous is None:
                inverse = pow(column[pivot], -1, prime)
                pivots[pivot] = {row: value * inverse % prime for row, value in column.items()}
                independent.append(index)
                break
            factor = column[pivot]
            for row, value in previous.items():
                updated = (column.get(row, 0) - factor * value) % prime
                if updated:
                    column[row] = updated
                else:
                    column.pop(row, None)
        if index % 500 == 0:
            print(f"relation_columns_processed: {index + 1}; certified_rank: {len(pivots)}",
                  flush=True)
    return tuple(sorted(pivots)), tuple(independent)


def write_alternate_metric_first_quotient_sections() -> dict[str, object]:
    """Write an actual 1540-section quotient basis and its algebraic certificate."""

    ambient_digest, ambient = _verified_payload(AMBIENT)
    generation_digest, generation = _verified_payload(GENERATION)
    if (
        ambient.get("schema") != "alternate-metric-first-resolution-ambient-sections-v1"
        or ambient.get("twist_cover_degree") != [14, 16, 1]
        or ambient.get("common_flat_character_twist") != [1, 2]
        or ambient.get("prerequisite_artifact_digests", {}).get("generation") != generation_digest
        or generation.get("generating_twist_cover_degree") != [14, 16, 1]
    ):
        raise ValueError("the actual metric-section prerequisites changed")
    target = _orbits((13, 17, 2), 2)
    syzygies = _orbits((10, 14, 0), 1)
    if len(target) != 5814 or len(syzygies) != 840:
        raise ValueError("the actual scalar ideal Koszul dimensions changed")
    columns = list(_relation_columns(target))
    if len(columns) != 5114:
        raise ValueError("the complete two-equation relation presentation changed")
    print(f"exact_relation_columns_constructed: {len(columns)}", flush=True)
    pivot_rows, independent = _modular_pivots(columns, PRIME, OMEGA_RESIDUE)
    if len(pivot_rows) != 4274 or len(independent) != 4274:
        raise ValueError("the actual relation rank does not reach its structural upper bound")
    pivot_set = set(pivot_rows)
    basis = [list(orbit[0]) for index, orbit in enumerate(target) if index not in pivot_set]
    if len(basis) != 1540:
        raise ValueError("the actual first Serre quotient basis dimension changed")
    raw = json.dumps(columns, sort_keys=True, separators=(",", ":")).encode("utf-8")
    archive = gzip.compress(raw, mtime=0)
    payload = {
        "schema": "alternate-metric-first-quotient-sections-v1",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "twist_cover_degree": [14, 16, 1],
        "twist_linearization": "natural commuting ambient P/T coordinate lifts",
        "ideal_image_degree": [13, 17, 2],
        "actual_ideal_image_frame_p_t_exponents": [2, 2],
        "ideal_generators_x": [[1, 1, 0], [1, 0, 1], [0, 1, 1]],
        "ambient_ideal_invariant_dimension": 5814,
        "ideal_koszul_source_dimensions": [2394, 2720],
        "ideal_koszul_syzygy_dimension": 840,
        "structural_relation_rank_upper_bound": 4274,
        "certificate_prime": PRIME,
        "certificate_omega_residue": OMEGA_RESIDUE,
        "certified_relation_minor_rank": len(pivot_rows),
        "relation_minor_pivot_rows": list(pivot_rows),
        "relation_minor_column_indices": list(independent),
        "quotient_section_dimension": len(basis),
        "quotient_basis_canonical_monomials": basis,
        "relation_archive": RELATIONS.relative_to(ROOT).as_posix(),
        "relation_archive_sha256": hashlib.sha256(archive).hexdigest(),
        "exact_integral_relation_columns_sha256": hashlib.sha256(raw).hexdigest(),
        "hilbert_burch_ideal_identification_equivariant": True,
        "exact_equation_images_in_invariant_span": True,
        "schoen_sequence_regular_on_coordinate_axis_quotient": True,
        "serre_lifts_constructed": False,
        "full_constituent_section_basis_available": False,
        "rank_four_section_basis_available": False,
        "numerical_metrics_available": False,
        "physical_yukawas_available": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "ambient": ambient_digest, "generation": generation_digest,
        },
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary_archive = RELATIONS.with_name(f".{RELATIONS.name}.tmp")
    temporary_archive.write_bytes(archive)
    temporary_archive.replace(RELATIONS)
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.tmp")
    temporary.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    temporary.replace(OUTPUT)
    return payload


if __name__ == "__main__":
    report = write_alternate_metric_first_quotient_sections()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"quotient_section_dimension: {report['quotient_section_dimension']}")
