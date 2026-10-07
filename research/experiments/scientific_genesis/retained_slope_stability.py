"""Refine the source stability bound at the original section polarization.

Owns:
    Actual mixed-arrow line-Hom vanishing, independent rational rank checks,
    source-ordered descendant bounds and all proper-rank extension cases.

Depends on:
    The frozen alternate constituents, exact mixed Cech/Koszul transfer,
    trusted generation and stability prerequisites and published line ordering.

Must not:
    Change sections or samples, choose a vacuum, infer cover stability from
    quotient stability, or claim a computed HYM connection or matter metric.

Phase 0:
    Research-only source-conditioned slope-stability refinement.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
from functools import cache
from pathlib import Path

from research.experiments.computable_carrier.schoen_serre_outer import schoen_serre_outer_hom

from .alternate_metric_quotient_generation import _second_constituent
from .metric_polarization_scope import (
    DIRECTORY,
    GENERATION_DIGEST,
    ROOT,
    STABILITY_DIGEST,
    _digest,
    _trusted,
    ambient_cover_triple,
)
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_outer_transfer import _skeleton, _transfer_map, mixed_schoen_unit

OUTPUT = DIRECTORY / "retained_slope_stability.json"
NOTE = Path(__file__).with_name("RETAINED_SLOPE_STABILITY_NOTE.md")
POLARIZATION = (14, 16, 1)
# All six largest source bounds: the actual Serre subline and five bounds for
# maps to the ideal quotient (0602073, equations 25--31 and their I6 analogue).
LINE_BOUNDS = (
    ((-1, 1, -1), (-1, 1, -2), (-4, 1, 2), (-3, 0, 1),
     (-2, -1, 1), (-1, -2, 2)),
    ((1, -1, -1), (1, -1, -2), (-2, -1, 2), (-1, -2, 1),
     (0, -3, 1), (1, -4, 2)),
)
# Negatives of the five maximal proper equivariant sublines of O_X, eq. 67.
MINIMAL_EFFECTIVE = ((0, 0, 1), (3, 0, -1), (2, 1, 0), (1, 2, 0), (0, 3, -1))


def _slope(line):
    return Fraction(ambient_cover_triple(line, POLARIZATION, POLARIZATION))


def rational_restriction_rank(entries, row_count, column_count):
    """Rank over Q of multiplication blocks for a matrix over Q(omega).

    This does not use Eisenstein operations or the producer's sparse-column
    elimination. In basis (1, omega), a+b*omega acts as ((a,-b),(b,a-b)).
    Rank over Q is twice rank over Q(omega); no modular or numeric rank is used.
    """

    if any(type(size) is not int or size < 0 for size in (row_count, column_count)):
        raise ValueError("matrix dimensions require nonnegative integers")
    rows = [{} for _ in range(2 * row_count)]
    seen = set()
    for i, j, a_text, b_text in entries:
        if (type(i) is not int or type(j) is not int or not 0 <= i < row_count
                or not 0 <= j < column_count or (i, j) in seen):
            raise ValueError("invalid or duplicate exact matrix coordinate")
        if not isinstance(a_text, str) or not isinstance(b_text, str):
            raise ValueError("coefficients require exact rational text")
        a, b = Fraction(a_text), Fraction(b_text)
        if (str(a), str(b)) != (a_text, b_text) or not (a or b):
            raise ValueError("coefficients must be canonical nonzero exact pairs")
        seen.add((i, j))
        for r, c, value in ((2*i, 2*j, a), (2*i, 2*j+1, -b),
                             (2*i+1, 2*j, b), (2*i+1, 2*j+1, a-b)):
            if value:
                rows[r][c] = value
    pivots = {}
    for vector in rows:
        while vector:
            pivot = min(vector)
            coefficient = vector[pivot]
            if pivot not in pivots:
                pivots[pivot] = {j: value / coefficient for j, value in vector.items()}
                break
            for column, value in pivots[pivot].items():
                updated = vector.get(column, Fraction(0)) - coefficient * value
                if updated:
                    vector[column] = updated
                else:
                    vector.pop(column, None)
    return len(pivots)


def _basis_record(space):
    return {"name": space.name, "ordered_basis": list(space.basis),
            "coefficient_field": "Q(omega), omega^2+omega+1=0"}


def line_hom_probe(index, line):
    """Compute Hom(O(line), V_index) on the cover using unchanged actual arrows."""

    if (type(index) is not int or index not in (0, 1)
            or not isinstance(line, tuple) or len(line) != 3
            or any(type(coordinate) is not int for coordinate in line)
            or line not in LINE_BOUNDS[index]):
        raise ValueError("a probe requires an actual source candidate and constituent")
    return deepcopy(_line_hom_probe(index, line))


@cache
def _line_hom_probe(index, line):
    """Memoize only validated exact inputs; never expose mutable cached evidence."""

    constituent = (mixed_schoen_constituents()[0], _second_constituent())[index]
    shifted = replace(
        constituent,
        name=f"{constituent.name} tensor O{tuple(-c for c in line)}",
        twist=tuple(a-b for a, b in zip(constituent.twist, line, strict=True)),
        objects=tuple(replace(obj, line_degree=tuple(
            a-b for a, b in zip(obj.line_degree, line, strict=True)
        )) for obj in constituent.objects),
    )
    if (not constituent.exact or not shifted.exact
            or shifted.resolution_arrows != constituent.resolution_arrows
            or shifted.extension_terms != constituent.extension_terms):
        raise ValueError("the actual uniformly twisted Serre arrows changed")
    unit = mixed_schoen_unit()
    reduced = schoen_serre_outer_hom(_skeleton(shifted), _skeleton(unit))
    spaces = dict(reduced.total_spaces)
    if any(space.dimension for degree, space in reduced.total_spaces if degree < 0):
        raise ValueError("degree-zero injectivity is insufficient with negative terms")
    differential, depth = _transfer_map(shifted, unit, 0)
    if differential.domain != spaces[0] or differential.codomain != spaces[1]:
        raise ValueError("the transferred degree-zero map changed its ordered bases")
    entries = [[i, j, str(value.a), str(value.b)]
               for i, row in enumerate(differential.rows) for j, value in row]
    rank = differential.rank()
    rational_rank = rational_restriction_rank(
        entries, differential.codomain.dimension, differential.domain.dimension,
    )
    if rational_rank != 2 * rank or rank != differential.domain.dimension:
        raise ValueError("the actual positive candidate line Hom does not vanish")
    return {
        "constituent_index": index, "constituent": constituent.name,
        "candidate_line_class": list(line), "cover_line_slope_exact": str(_slope(line)),
        "uniform_tensor_shift": [-c for c in line],
        "actual_shifted_objects": [[obj.name, obj.position, list(obj.line_degree)]
                                   for obj in shifted.objects],
        "domain": _basis_record(differential.domain),
        "codomain": _basis_record(differential.codomain),
        "space_dimensions": [[degree, space.dimension] for degree, space in
                             reduced.total_spaces],
        "degree_zero_entries": entries, "transfer_path_depth": depth,
        "degree_zero_rank_over_Qomega": rank,
        "independent_rank_over_Q": rational_rank,
        "cover_line_hom_dimension": 0,
        "every_flat_equivariant_character_excluded": True,
    }


def source_order_bounds():
    """Bound every constituent line and every proper-rank extension case.

    Uses the quantified published line-order premise, not a finite list declared
    exhaustive from experiment. Positive maximal classes are removed only after
    the actual cover Hom vanishes; proper descendants lose at least the gap.
    """

    effective = [{"class": list(line), "cover_degree_exact": str(_slope(line))}
                 for line in MINIMAL_EFFECTIVE]
    gap = min(Fraction(row["cover_degree_exact"]) for row in effective)
    if gap <= 0:
        raise ValueError("the proper-effective-divisor gap is not strictly positive")
    rows, maxima = [], []
    for index, candidates in enumerate(LINE_BOUNDS):
        local = []
        for line in candidates:
            slope = _slope(line)
            if slope >= 0:
                probe = line_hom_probe(index, line)
                if probe["cover_line_hom_dimension"] != 0:
                    raise ValueError("a maximal candidate was removed without Hom vanishing")
                upper = slope - gap
            else:
                upper = slope
            if upper >= 0:
                raise ValueError("a proper descendant may still destabilize")
            local.append({"line_class": list(line), "cover_slope_exact": str(slope),
                          "maximal_line_excluded_by_cover_Hom": slope >= 0,
                          "remaining_cover_degree_upper_bound": str(upper)})
        maxima.append(max(Fraction(row["remaining_cover_degree_upper_bound"])
                          for row in local))
        rows.append({"constituent_index": index, "source_order_rows": local,
                     "all_line_degrees_upper_bound": str(maxima[-1])})
    determinants = tuple(_slope(tuple(2*c for c in twist))
                         for twist in ((-1, 1, 0), (1, -1, 0)))
    cases = []
    for left_rank, right_rank in ((1, 0), (0, 1), (2, 0), (1, 1),
                                 (0, 2), (2, 1), (1, 2)):
        left = (Fraction(0), maxima[0], determinants[0])[left_rank]
        right = (Fraction(0), maxima[1], determinants[1])[right_rank]
        reason = "constituent line/determinant bounds and additivity of c1"
        if (left_rank, right_rank) == (0, 2):
            right -= gap
            reason = (
                "positive determinant-divisor case loses the effective gap; "
                "zero divisor would extend an inverse across codimension two "
                "by reflexivity and split the nonzero outer extension"
            )
        total = left + right
        if total >= 0:
            raise ValueError("a proper-rank extension case has nonnegative slope")
        cases.append({"intersection_rank": left_rank, "image_rank": right_rank,
                      "total_rank": left_rank + right_rank,
                      "cover_determinant_degree_upper_bound": str(total),
                      "cover_slope_upper_bound": str(total / (left_rank + right_rank)),
                      "reason": reason})
    return {"minimal_proper_effective_divisors": effective,
            "minimum_proper_effective_cover_degree": str(gap),
            "constituent_line_bounds": rows,
            "constituent_determinant_cover_degrees": list(map(str, determinants)),
            "proper_rank_extension_cases": cases}


def _sources():
    files = (Path(__file__), NOTE,
             Path(__file__).with_name("ALTERNATE_STABILITY_NOTE.md"),
             ROOT / "data/published/visible_carrier/source_manifest.json",
             ROOT / "src/onetheory/math/numbers.py",
             Path(__file__).with_name("metric_polarization_scope.py"),
             Path(__file__).with_name("alternate_metric_quotient_generation.py"),
             Path(__file__).with_name("mixed_constituent_schoen_arrows.py"),
             Path(__file__).with_name("mixed_schoen_outer_transfer.py"),
             ROOT / "research/experiments/computable_carrier/schoen_serre_outer.py",
             ROOT / "research/experiments/computable_carrier/schoen_serre_outer_transfer.py",
             ROOT / "research/experiments/computable_carrier/schoen_sparse_outer.py")
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files}


def build_record():
    generation = _trusted("alternate_metric_quotient_generation", GENERATION_DIGEST)
    stability = _trusted("alternate_constituent_outer_stability_locus", STABILITY_DIGEST)
    if (tuple(generation["generating_twist_cover_degree"]) != POLARIZATION
            or generation["quotient_h0_rank_four_at_generating_twist"] != 5345
            or stability["all_nonzero_parameters_stable_in_chamber"] is not True
            or stability["alternate_serre_ray_nontrivial_and_locally_free"] is not True
            or stability["source_stability_bound_uses_serre_sequences_not_ray_coordinates"]
            is not True):
        raise ValueError("the frozen Serre/outer family prerequisites changed")
    bounds = source_order_bounds()
    probes = [line_hom_probe(index, line) for index, candidates in enumerate(LINE_BOUNDS)
              for line in candidates if _slope(line) >= 0]
    return {
        "schema": "retained-slope-stability-v1", "status": "PROVED",
        "claim": "the descended alternate nonzero outer family is slope-stable at (14,16,1)",
        "polarization": list(POLARIZATION), "original_section_count": 5345,
        "normalization": "cover determinant degrees; quotient slopes divide by nine and rank",
        "parameter_quantifier": "every nonzero alternate P1 outer class",
        "prerequisite_digests": {"generation": GENERATION_DIGEST, "stability": STABILITY_DIGEST},
        "published_sources": stability["sources"],
        "source_order_premises": [
            "0602073 equations 25--31 and I6 analogue bound all constituent line maps",
            "0602073 equation 67 bounds every proper integral equivariant effective divisor",
            "0512205 section 2.1 filters any subsheaf through both constituents",
            "locally free Serre constituents and nonsplit outer family are already certified",
        ],
        "actual_cover_line_Hom_probes": probes,
        "source_order_refinement": bounds,
        "descended_slope_stability_established": True,
        "full_stability_chamber_computed": False, "non_equivariant_cover_stability_claimed": False,
        "original_sections_or_cloud_inputs_changed": False, "physical_kahler_class_selected": False,
        "observations_used": False, "compatible_background_algorithm_derived": False,
        "ricci_flat_or_hym_metric_available": False, "matter_and_higgs_metrics_available": False,
        "physical_yukawas_available": False, "common_stabilized_vacuum_available": False,
        "first_missing_input": (
            "compatible controlled background geometry and line untwisting, "
            "then useful integration bounds and an actual convergent HYM calculation"
        ),
        "source_files_sha256": _sources(),
    }


def read_certificate(*, expected_digest, path=OUTPUT):
    """Reproduce actual transferred maps and independent ranks without writing."""

    record = json.loads(path.read_bytes())
    unsigned = {key: value for key, value in record.items() if key != "artifact_digest"}
    if record.get("artifact_digest") != expected_digest or _digest(unsigned) != expected_digest:
        raise ValueError("the trusted retained stability certificate changed")
    if unsigned != build_record():
        raise ValueError("the actual line-Hom calculation or source-order proof changed")
    return record


def write_certificate(path=OUTPUT):
    record = build_record()
    record["artifact_digest"] = _digest(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return record


if __name__ == "__main__":
    report = write_certificate()
    print(f"artifact_digest: {report['artifact_digest']}")
    print("descended_slope_stability_established:", report["descended_slope_stability_established"])
