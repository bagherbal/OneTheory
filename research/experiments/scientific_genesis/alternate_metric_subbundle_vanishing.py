"""Certify one alternate-carrier metric twist's first-constituent H1 vanishing.

Owns:
    Exact ambient Künneth profiles, Koszul/Serre/Hilbert--Burch vanishing
    deductions, cover generation, and quotient descent for one twist.

Depends on:
    The actual unchanged first constituent, the published Schoen complete
    intersection and free deck action, and exact ambient line cohomology.

Must not:
    Reuse reference-carrier section dimensions as inputs, infer global
    quotient generation from cover generation, or claim physical metrics.

Phase 0:
    Research-only exact prerequisite certificate for the metric frontier.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_linebundles import (
    ambient_schoen_line_bundle,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    _compose_images,
    schoen_sparse_deck_actions,
)

from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_metric_subbundle_vanishing.json"
CONE = ROOT / "data/generated/scientific_genesis/alternate_constituent_outer_universal_cone.json"
CARRIER = ROOT / "data/generated/scientific_genesis/alternate_constituent_carrier_state.json"
ARROWS = ROOT / "data/generated/scientific_genesis/mixed_constituent_schoen_arrows.json"
TWIST = (5, 7, 1)

type Degree = tuple[int, int, int]


def _difference(left: Degree, right: Degree) -> Degree:
    return cast(Degree, tuple(a - b for a, b in zip(left, right, strict=True)))


def _ambient_profile(degree: Degree) -> tuple[int, ...]:
    ambient = ambient_schoen_line_bundle(*degree)
    return tuple(ambient.space(index).vector_space.dimension for index in range(6))


def _equation_degrees() -> tuple[Degree, Degree]:
    """Read the two actual Cox equation degrees in x/u/base order."""

    cox = schoen_geometry().cover.cox
    degrees = dict(cox.multidegrees)
    if cox.equations != (
        "p1 = mu F(x) + nu G(x)", "p2 = 2 nu F(u) + mu G(u)",
    ):
        raise ValueError("the Schoen complete-intersection equations changed")
    result = tuple(
        (coordinates[0], coordinates[2], coordinates[1])
        for coordinates in (degrees["p1"], degrees["p2"])
    )
    if result != ((3, 0, 1), (0, 3, 1)):
        raise ValueError("the Schoen equation multidegrees changed")
    return cast(tuple[Degree, Degree], result)


def _koszul_profile(degree: Degree, equations: tuple[Degree, Degree]) -> dict[str, object]:
    first, second = equations
    pieces = {
        "k0": degree,
        "k1_x": _difference(degree, first),
        "k1_u": _difference(degree, second),
        "k2": _difference(_difference(degree, first), second),
    }
    return {
        name: {"degree": list(piece), "ambient_h0_to_h5": list(_ambient_profile(piece))}
        for name, piece in pieces.items()
    }


def _h0_only_dimension(profile: dict[str, object], role: str) -> int:
    """Apply only the two exact ambient-support patterns used in this proof."""

    dimensions = {
        name: cast(list[int], cast(dict[str, object], item)["ambient_h0_to_h5"])
        for name, item in profile.items()
    }
    zero = [0] * 6
    if dimensions["k0"][1:] != zero[1:]:
        raise ValueError("the untwisted ambient term has higher cohomology")
    if role == "A":
        if (
            dimensions["k1_x"] != zero
            or dimensions["k1_u"] != zero
            or dimensions["k2"][0] != 0
            or dimensions["k2"][2:] != zero[2:]
        ):
            raise ValueError("the Serre subline no longer has the acyclic-K1 pattern")
        result = dimensions["k0"][0] - dimensions["k2"][1]
    elif role in ("F0", "F1"):
        if (
            dimensions["k1_x"] != zero
            or dimensions["k1_u"][1:] != zero[1:]
            or dimensions["k2"] != zero
        ):
            raise ValueError("a Hilbert--Burch line lost its H0-only Koszul pattern")
        result = dimensions["k0"][0] - dimensions["k1_u"][0]
    else:
        raise ValueError("only the actual A/F0/F1 Serre roles are admissible")
    if result < 0:
        raise ValueError("the Koszul Euler characteristic is inconsistent")
    return result


def _twist_commutator() -> tuple[Eisenstein, Eisenstein, Eisenstein]:
    """Check the ambient line's exact P/T commutator before descent."""

    first, second = schoen_sparse_deck_actions()
    scalars = []
    for factor in ("x_images", "u_images", "p_images"):
        pt = _compose_images(getattr(first, factor), getattr(second, factor))
        tp = _compose_images(getattr(second, factor), getattr(first, factor))
        if any(left[1] != right[1] for left, right in zip(pt, tp, strict=True)):
            raise ValueError("the published deck commutator is not scalar")
        ratios = {left[0] / right[0] for left, right in zip(pt, tp, strict=True)}
        if len(ratios) != 1:
            raise ValueError("the deck commutator changed across coordinates")
        scalars.append(ratios.pop())
    result = cast(tuple[Eisenstein, Eisenstein, Eisenstein], tuple(scalars))
    if not all(action.order_three_coordinates for action in (first, second)):
        raise ValueError("a deck generator lost its order-three lift")
    if (
        result[0] ** TWIST[0] * result[1] ** TWIST[1] * result[2] ** TWIST[2]
        != Eisenstein(1)
    ):
        raise ValueError("the declared twist has no commuting ambient linearization")
    return result


def alternate_metric_subbundle_vanishing() -> dict[str, object]:
    """Derive H1(X,V1(H))=0 without a global non-split matrix."""

    cone_digest, cone = _verified_payload(CONE)
    carrier_digest, carrier = _verified_payload(CARRIER)
    arrows_digest, arrows = _verified_payload(ARROWS)
    first = mixed_schoen_constituents()[0]
    carrier_state = carrier.get("computable_one_theory_carrier_state")
    if not isinstance(carrier_state, dict):
        raise ValueError("the alternate carrier state lost its certificate ledger")
    certificates = carrier_state.get("certificate_digests")
    first_arrows = arrows.get("constituents")
    if (
        cone.get("schema") != "alternate-constituent-outer-universal-cone-v1"
        or cone.get("equivariant_descent_exact") is not True
        or carrier.get("schema") != "alternate-constituent-carrier-state-v1"
        or not isinstance(certificates, dict)
        or certificates.get("universal_cone") != cone_digest
        or arrows.get("schema") != "mixed-constituent-schoen-arrows-v1"
        or not isinstance(first_arrows, list)
        or not first_arrows
        or first_arrows[0] != first.as_record()
        or not first.exact
        or first.name != "V1"
        or first.factor != 1
    ):
        raise ValueError("the actual descended first constituent is not certified")
    equation_degrees = _equation_degrees()
    commutators = _twist_commutator()
    lines = []
    for item in first.objects:
        if item.name == "A" and item.position == 0:
            role = "A"
        elif item.name.startswith("F0:") and item.position == 0:
            role = "F0"
        elif item.name.startswith("F1:") and item.position == -1:
            role = "F1"
        else:
            raise ValueError("the Serre/Hilbert--Burch line-object roles changed")
        degree = cast(Degree, tuple(a + b for a, b in zip(
            item.line_degree, TWIST, strict=True,
        )))
        profile = _koszul_profile(degree, equation_degrees)
        dimension = _h0_only_dimension(profile, role)
        commutator = (
            commutators[0] ** degree[0]
            * commutators[1] ** degree[1]
            * commutators[2] ** degree[2]
        )
        lines.append({
            "name": item.name,
            "role": role,
            "source_degree": list(item.line_degree),
            "twisted_degree": list(degree),
            "ambient_koszul_profile": profile,
            "cover_h0": dimension,
            "cover_h1_to_h3": [0, 0, 0],
            "ambient_line_deck_commutator": str(commutator),
            "ambient_line_lift_commutes": commutator == Eisenstein(1),
            "ambient_nonnegative_and_cover_generated": all(value >= 0 for value in degree),
        })
    if [item["role"] for item in lines] != ["A", "F0", "F0", "F0", "F1", "F1"]:
        raise ValueError("the first constituent's exact Serre resolution changed")
    if (
        any(not item["ambient_nonnegative_and_cover_generated"] for item in lines[:4])
        or [item["ambient_line_lift_commutes"] for item in lines]
        != [True, False, False, False, True, True]
    ):
        raise ValueError("the cover-generation or ambient deck-lift pattern changed")
    subline = lines[0]
    subline_koszul = cast(dict[str, dict[str, object]], subline["ambient_koszul_profile"])
    subline_d2_rank = cast(list[int], subline_koszul["k2"]["ambient_h0_to_h5"])[1]
    if subline_d2_rank != 63:
        raise ValueError("the required Koszul higher transgression changed")
    cover_h0 = sum(
        int(item["cover_h0"]) * (1 if item["role"] in ("A", "F0") else -1)
        for item in lines
    )
    geometry = schoen_geometry()
    if not geometry.quotient.acts_freely or geometry.quotient.order != 9:
        raise ValueError("the published free quotient changed")
    if cover_h0 <= 0 or cover_h0 % geometry.quotient.order:
        raise ValueError("the H0-only free-action multiplicity is inconsistent")
    return {
        "schema": "alternate-metric-subbundle-vanishing-v1",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "twist_cover_degree": list(TWIST),
        "twist_status": "declared mathematical candidate; no metric modulus selected",
        "equation_degrees_x_u_base": [list(degree) for degree in equation_degrees],
        "deck_coordinate_commutators": [str(value) for value in commutators],
        "twist_descends_by_commuting_lifts": True,
        "line_objects": lines,
        "subline_koszul_higher_transgression_rank": subline_d2_rank,
        "ambient_first_page_alone_incomplete_for_subline": True,
        "cover_h0_first_constituent": cover_h0,
        "cover_h1_to_h3_first_constituent": [0, 0, 0],
        "quotient_h0_first_constituent": cover_h0 // geometry.quotient.order,
        "quotient_h1_first_constituent": 0,
        "cover_global_generation_first_constituent": True,
        "cover_generation_argument": (
            "A and the three F0 lines are restrictions of basepoint-free "
            "ambient lines; Q is a quotient of F0; H1(cover,A)=0 lifts "
            "every Q section through the actual Serre extension"
        ),
        "quotient_global_generation_first_constituent_certified": False,
        "individual_f0_ambient_lifts_commute": False,
        "result_independent_of_outer_extension_parameter": True,
        "global_generation_of_constituents_certified": False,
        "rank_four_global_generation_certified": False,
        "numerical_metrics_available": False,
        "physical_yukawas_available": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "alternate_cone": cone_digest,
            "alternate_carrier": carrier_digest,
            "first_constituent_arrows": arrows_digest,
        },
    }


def write_alternate_metric_subbundle_vanishing(path: Path = OUTPUT) -> dict[str, object]:
    """Write one exact, content-addressed metric-prerequisite result."""

    payload = alternate_metric_subbundle_vanishing()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    result = write_alternate_metric_subbundle_vanishing()
    print(f"artifact_digest: {result['artifact_digest']}")
    print(f"quotient_h1_first_constituent: {result['quotient_h1_first_constituent']}")
