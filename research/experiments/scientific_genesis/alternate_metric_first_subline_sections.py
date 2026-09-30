"""Construct actual invariant sections of the alternate first Serre subline.

Owns:
    Exact projected-Schoen quotient ring, deck-character orbit sums, and a
    sparse ideal quotient basis at the certified generating twist.

Depends on:
    The frozen first constituent frame, exact Schoen cubics and deck lifts,
    the generating-twist certificate, and sparse exact span elimination.

Must not:
    Treat subline sections as full rank-two or rank-four sections, invent
    Serre lifts, or infer numerical metrics from a symbolic basis.

Phase 0:
    Research-only first component of the carrier section construction.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    _SparseSpanSolver,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    SchoenSparseDeckAction,
    _monomial_action,
    schoen_sparse_deck_actions,
)

from .alternate_constituent_hom_actions import _common_frame
from .alternate_metric_quotient_generation import CONE
from .alternate_metric_quotient_generation import OUTPUT as GENERATION
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_metric_first_subline_sections.json"

type Monomial6 = tuple[int, int, int, int, int, int]
type SparsePolynomial = dict[Monomial6, Eisenstein]
type Orbit = tuple[Monomial6, tuple[tuple[Monomial6, Eisenstein], ...]]


def _monomials(x_degree: int, u_degree: int) -> tuple[Monomial6, ...]:
    return tuple(
        (x0, x1, x_degree - x0 - x1, u0, u1, u_degree - u0 - u1)
        for x0 in range(x_degree + 1)
        for x1 in range(x_degree - x0 + 1)
        for u0 in range(u_degree + 1)
        for u1 in range(u_degree - u0 + 1)
    )


def _act_monomial(
    monomial: Monomial6,
    action: SchoenSparseDeckAction,
    frame: Eisenstein | None = None,
) -> tuple[Eisenstein, Monomial6]:
    x_scalar, x_image = _monomial_action(monomial[:3], action.x_images)
    u_scalar, u_image = _monomial_action(monomial[3:], action.u_images)
    return (
        (Eisenstein(1) if frame is None else frame) * x_scalar * u_scalar,
        cast(Monomial6, x_image + u_image),
    )


def _eliminant() -> SparsePolynomial:
    """Eliminate the shared P1 coordinate from the two actual Schoen equations."""

    cox = schoen_geometry().cover.cox
    if cox.equations != (
        "p1 = mu F(x) + nu G(x)", "p2 = 2 nu F(u) + mu G(u)",
    ):
        raise ValueError("the published linear-in-P1 Schoen equations changed")
    result: SparsePolynomial = {}
    for sign, left, right in (
        (Eisenstein(2), cox.cubic_f, cox.cubic_f),
        (Eisenstein(-1), cox.cubic_g, cox.cubic_g),
    ):
        for x_monomial, x_value in left.terms:
            for u_monomial, u_value in right.terms:
                monomial = cast(Monomial6, x_monomial + u_monomial)
                value = result.get(monomial, Eisenstein(0)) + sign * x_value * u_value
                if value.is_zero():
                    result.pop(monomial, None)
                else:
                    result[monomial] = value
    if not result or any(sum(m[:3]) != 3 or sum(m[3:]) != 3 for m in result):
        raise ValueError("the projected eliminant lost bidegree (3,3)")
    return result


def _orbit_basis(
    x_degree: int,
    u_degree: int,
    p_action: SchoenSparseDeckAction,
    t_action: SchoenSparseDeckAction,
    p_frame: Eisenstein,
    t_frame: Eisenstein,
) -> tuple[Orbit, ...]:
    """Return canonical P orbit sums in the T-fixed character sector."""

    seen: set[Monomial6] = set()
    result = []
    for monomial in _monomials(x_degree, u_degree):
        if monomial in seen:
            continue
        images = [monomial]
        current = monomial
        scalar = Eisenstein(1)
        for _ in range(3):
            factor, current = _act_monomial(current, p_action, p_frame)
            scalar *= factor
            images.append(current)
        if current != monomial or scalar != Eisenstein(1) or len(set(images[:3])) != 3:
            raise ValueError("the first subline P action lost its exact cubic orbit")
        seen.update(images[:3])
        canonical = min(images[:3])
        t_scalar, t_image = _act_monomial(canonical, t_action, t_frame)
        if t_image != canonical:
            raise ValueError("the T action is not diagonal on ambient monomials")
        if t_scalar != Eisenstein(1):
            continue
        terms = []
        current = canonical
        coefficient = Eisenstein(1)
        for _ in range(3):
            terms.append((current, coefficient))
            factor, current = _act_monomial(current, p_action, p_frame)
            coefficient *= factor
        if current != canonical or coefficient != Eisenstein(1):
            raise ValueError("the canonical invariant orbit did not close")
        result.append((canonical, tuple(terms)))
    return tuple(result)


def _multiply_orbit(orbit: Orbit, eliminant: SparsePolynomial) -> SparsePolynomial:
    result: SparsePolynomial = {}
    for monomial, coefficient in orbit[1]:
        for relation, value in eliminant.items():
            target = cast(Monomial6, tuple(a + b for a, b in zip(
                monomial, relation, strict=True,
            )))
            updated = result.get(target, Eisenstein(0)) + coefficient * value
            if updated.is_zero():
                result.pop(target, None)
            else:
                result[target] = updated
    return result


def alternate_metric_first_subline_sections() -> dict[str, object]:
    """Return an exact 1115-vector quotient basis in the actual subline frame."""

    generation_digest, generation = _verified_payload(GENERATION)
    cone_digest, cone = _verified_payload(CONE)
    if (
        generation.get("schema") != "alternate-metric-quotient-generation-v2"
        or generation.get("generating_twist_cover_degree") != [14, 16, 1]
        or generation.get("quotient_h0_constituents_at_generating_twist")
        != [2655, 2690]
        or generation.get("prerequisite_artifact_digests", {}).get("alternate_cone")
        != cone_digest
        or cone.get("schema") != "alternate-constituent-outer-universal-cone-v1"
        or cone.get("common_flat_character_twist") != [1, 2]
    ):
        raise ValueError("the alternate generating twist or repaired character changed")
    first = mixed_schoen_constituents()[0]
    if first.name != "V1" or first.objects[0].line_degree != (-1, 1, -1):
        raise ValueError("the actual first Serre subline changed")
    degree = tuple(
        left + right for left, right in zip(
            first.objects[0].line_degree, (14, 16, 1), strict=True,
        )
    )
    if degree != (13, 17, 0):
        raise ValueError("the projected first-subline degree changed")
    p_action, t_action = schoen_sparse_deck_actions()
    p_frame = _common_frame(first, p_action)[0][0] * OMEGA
    t_frame = _common_frame(first, t_action)[0][0] * OMEGA2
    if (p_frame, t_frame) != (Eisenstein(1), OMEGA2):
        raise ValueError("the repaired first-subline equivariant frame changed")
    eliminant = _eliminant()
    for action in (p_action, t_action):
        transformed: SparsePolynomial = {}
        for monomial, value in eliminant.items():
            scalar, image = _act_monomial(monomial, action)
            transformed[image] = transformed.get(image, Eisenstein(0)) + scalar * value
        if transformed != eliminant:
            raise ValueError("the projected Schoen eliminant is not deck invariant")

    target_orbits = _orbit_basis(13, 17, p_action, t_action, p_frame, t_frame)
    source_orbits = _orbit_basis(10, 14, p_action, t_action, p_frame, t_frame)
    if (len(target_orbits), len(source_orbits)) != (1995, 880):
        raise ValueError("the exact invariant orbit dimensions changed")
    target_index = {orbit[0]: index for index, orbit in enumerate(target_orbits)}
    ideal_columns = []
    for orbit in source_orbits:
        product = _multiply_orbit(orbit, eliminant)
        coordinates = {
            target_index[monomial]: value
            for monomial, value in product.items()
            if monomial in target_index
        }
        reconstructed: SparsePolynomial = {}
        for index, coefficient in coordinates.items():
            for monomial, value in target_orbits[index][1]:
                reconstructed[monomial] = reconstructed.get(
                    monomial, Eisenstein(0)
                ) + coefficient * value
        if reconstructed != product or not coordinates:
            raise ValueError("an ideal relation escaped the invariant orbit frame")
        ideal_columns.append(coordinates)

    solver = _SparseSpanSolver(tuple(ideal_columns))
    pivots = tuple(sorted(solver._pivots))
    complement = tuple(
        index for index in range(len(target_orbits)) if index not in solver._pivots
    )
    if len(pivots) != 880 or len(complement) != 1115:
        raise ValueError("the actual first-subline quotient dimension changed")
    return {
        "schema": "alternate-metric-first-subline-sections-v1",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "twisted_subline_cover_degree": list(degree),
        "metric_twist_linearization": "natural commuting ambient P/T coordinate lifts",
        "actual_subline_frame_p_t": [str(p_frame), str(t_frame)],
        "projected_eliminant_bidegree": [3, 3],
        "projected_eliminant_terms": [
            {"monomial": list(monomial), "coefficient": str(value)}
            for monomial, value in sorted(eliminant.items())
        ],
        "projected_eliminant_deck_invariant": True,
        "ambient_invariant_orbit_count": len(target_orbits),
        "ideal_invariant_orbit_count": len(source_orbits),
        "ideal_inclusion_rank": len(pivots),
        "ideal_inclusion_matrix_digest": _canonical_digest([
            [[index, str(value)] for index, value in sorted(column.items())]
            for column in ideal_columns
        ]),
        "quotient_subline_section_count": len(complement),
        "quotient_basis_monomials_x_u": [
            list(target_orbits[index][0]) for index in complement
        ],
        "basis_construction": (
            "canonical actual-frame P orbit sums in the T-fixed sector, "
            "modulo multiplication by the invariant projected eliminant"
        ),
        "full_constituent_section_basis_available": False,
        "rank_four_section_basis_available": False,
        "numerical_metrics_available": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "generation": generation_digest,
            "alternate_cone": cone_digest,
        },
    }


def write_alternate_metric_first_subline_sections(path: Path = OUTPUT) -> dict[str, object]:
    """Write the deterministic first-subline quotient-section basis."""

    payload = alternate_metric_first_subline_sections()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_metric_first_subline_sections()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"quotient_subline_section_count: {report['quotient_subline_section_count']}")
