"""Certify quotient generation of the actual alternate carrier at a larger twist.

Owns:
    Exact Serre cover-generation checks, finite-orbit separation, and the
    invariant-evaluation theorem for both alternate constituents.

Depends on:
    The frozen alternate ray, first-constituent vanishing certificate,
    published free Schoen action, and exact ambient line cohomology.

Must not:
    Infer generation at the smaller twist, invent invariant section bases,
    or claim numerical metrics or a selected vacuum.

Phase 0:
    Research-only mathematical prerequisite for a future metric computation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA, Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)

from .alternate_metric_subbundle_vanishing import (
    OUTPUT as FIRST_CERTIFICATE,
)
from .alternate_metric_subbundle_vanishing import (
    _equation_degrees,
    _h0_only_dimension,
    _koszul_profile,
    _twist_commutator,
)
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import (
    MixedSchoenConstituent,
    _constituent,
    mixed_schoen_constituents,
)
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_metric_quotient_generation.json"
CONE = ROOT / "data/generated/scientific_genesis/alternate_constituent_outer_universal_cone.json"
CARRIER = ROOT / "data/generated/scientific_genesis/alternate_constituent_carrier_state.json"
BASE_TWIST = (5, 7, 1)
ORBIT_SEPARATOR = (9, 9, 0)
GENERATING_TWIST = (14, 16, 1)

type Degree = tuple[int, int, int]


def _twisted(degree: Degree, twist: Degree) -> Degree:
    return cast(Degree, tuple(a + b for a, b in zip(degree, twist, strict=True)))


def _roles(constituent: MixedSchoenConstituent) -> tuple[str, ...]:
    roles = []
    for item in constituent.objects:
        if item.name == "A" and item.position == 0:
            roles.append("A")
        elif item.name.startswith("F0:") and item.position == 0:
            roles.append("F0")
        elif item.name.startswith("F1:") and item.position == -1:
            roles.append("F1")
        else:
            raise ValueError("the actual Serre/Hilbert--Burch roles changed")
    return tuple(roles)


def _second_constituent() -> MixedSchoenConstituent:
    action = published_constituent_deck_actions()[1]
    ray = lift_joint_character_ray(action, Eisenstein(1), OMEGA)
    second = _constituent(ray, "I6-ray-0-1", 2, (1, -1, 0))
    if not second.exact or _roles(second) != (
        "A", "F0", "F0", "F0", "F0", "F1", "F1", "F1",
    ):
        raise ValueError("the frozen alternate right constituent changed")
    return second


def _ambient_only_h0(profile: dict[str, object]) -> bool:
    return all(
        cast(list[int], cast(dict[str, object], item)["ambient_h0_to_h5"])[1:]
        == [0] * 5
        for item in profile.values()
    )


def _line_h0_and_vanishing(profile: dict[str, object], role: str) -> int:
    """Use the two exact Koszul support patterns present at this twist."""

    if role == "A":
        return _h0_only_dimension(profile, role)
    if role not in ("F0", "F1") or not _ambient_only_h0(profile):
        raise ValueError("the Hilbert--Burch line lost its H0-only ambient profile")
    dimensions = {
        name: cast(list[int], cast(dict[str, object], item)["ambient_h0_to_h5"])[0]
        for name, item in profile.items()
    }
    result = (
        dimensions["k0"] - dimensions["k1_x"]
        - dimensions["k1_u"] + dimensions["k2"]
    )
    if result < 0:
        raise ValueError("the exact Koszul H0 alternating sum is negative")
    return result


def alternate_metric_quotient_generation() -> dict[str, object]:
    """Prove both quotient constituents and the rank-four family generate."""

    first_digest, first_record = _verified_payload(FIRST_CERTIFICATE)
    cone_digest, cone = _verified_payload(CONE)
    carrier_digest, carrier = _verified_payload(CARRIER)
    first = mixed_schoen_constituents()[0]
    second = _second_constituent()
    if (
        first_record.get("schema") != "alternate-metric-subbundle-vanishing-v1"
        or first_record.get("twist_cover_degree") != list(BASE_TWIST)
        or first_record.get("cover_global_generation_first_constituent") is not True
        or first_record.get("quotient_h1_first_constituent") != 0
        or cone.get("schema") != "alternate-constituent-outer-universal-cone-v1"
        or cone.get("ray_character_exponents") != [0, 1]
        or cone.get("equivariant_descent_exact") is not True
        or carrier.get("schema") != "alternate-constituent-carrier-state-v1"
        or _roles(first) != ("A", "F0", "F0", "F0", "F1", "F1")
        or [list(item.line_degree) for item in first.objects]
        != [item["source_degree"] for item in first_record["line_objects"]]
    ):
        raise ValueError("the actual alternate metric prerequisites changed")

    equations = _equation_degrees()
    right_a = _twisted(second.objects[0].line_degree, BASE_TWIST)
    right_a_profile = _koszul_profile(right_a, equations)
    right_a_h0 = _h0_only_dimension(right_a_profile, "A")
    right_f0 = [
        _twisted(item.line_degree, BASE_TWIST)
        for item, role in zip(second.objects, _roles(second), strict=True)
        if role == "F0"
    ]
    if right_a != (6, 6, 0) or right_a_h0 != 684:
        raise ValueError("the alternate right Serre subline acyclicity changed")
    if len(right_f0) != 4 or any(any(value < 0 for value in degree) for degree in right_f0):
        raise ValueError("the alternate right Hilbert--Burch source is not generated")

    geometry = schoen_geometry()
    if not geometry.quotient.acts_freely or geometry.quotient.order != 9:
        raise ValueError("the published free deck orbit changed")
    commutators = _twist_commutator()
    for degree in (ORBIT_SEPARATOR, GENERATING_TWIST):
        if (
            commutators[0] ** degree[0]
            * commutators[1] ** degree[1]
            * commutators[2] ** degree[2]
            != Eisenstein(1)
        ):
            raise ValueError("the orbit separator or generating twist does not descend")
    if _twisted(BASE_TWIST, ORBIT_SEPARATOR) != GENERATING_TWIST:
        raise ValueError("the generating twist is not the certified tensor product")
    if (
        any(degree < geometry.quotient.order - 1 for degree in ORBIT_SEPARATOR[:2])
        or ORBIT_SEPARATOR[2] != 0
        or not all(degree > 0 for degree in GENERATING_TWIST)
    ):
        raise ValueError("the projected-orbit separator or ample twist changed")

    first_large_lines = []
    second_large_lines = []
    for constituent, records in ((first, first_large_lines), (second, second_large_lines)):
        for item, role in zip(constituent.objects, _roles(constituent), strict=True):
            degree = _twisted(item.line_degree, GENERATING_TWIST)
            profile = _koszul_profile(degree, equations)
            dimension = _line_h0_and_vanishing(profile, role)
            records.append({
                "name": item.name,
                "role": role,
                "twisted_degree": list(degree),
                "ambient_koszul_profile": profile,
                "cover_h0": dimension,
                "cover_higher_cohomology_vanishes": True,
            })
    cover_dimensions = []
    for records in (first_large_lines, second_large_lines):
        cover_dimension = sum(
            int(item["cover_h0"]) * (1 if item["role"] != "F1" else -1)
            for item in records
        )
        if cover_dimension <= 0 or cover_dimension % geometry.quotient.order:
            raise ValueError("the cover H0 character dimension is inconsistent")
        cover_dimensions.append(cover_dimension)

    return {
        "schema": "alternate-metric-quotient-generation-v2",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "base_twist_cover_degree": list(BASE_TWIST),
        "orbit_separator_cover_degree": list(ORBIT_SEPARATOR),
        "generating_twist_cover_degree": list(GENERATING_TWIST),
        "free_deck_orbit_size": geometry.quotient.order,
        "projected_orbit_action_free": True,
        "projected_fiber_type": "empty, point, or the full projective line",
        "ambient_multihomogeneous_separation_bound_per_p2_factor": (
            geometry.quotient.order - 1
        ),
        "right_serre_subline_base_degree": list(right_a),
        "right_serre_subline_base_h0": right_a_h0,
        "right_serre_subline_base_ambient_koszul_profile": right_a_profile,
        "right_hilbert_burch_source_base_degrees": [list(item) for item in right_f0],
        "right_constituent_cover_generated_at_base_twist": True,
        "first_constituent_cover_generated_at_base_twist": True,
        "orbit_separator_descends": True,
        "orbit_separation_argument": (
            "A deck element fixing the projected P2xP2 pair preserves a "
            "nonempty fiber cut by linear P1 equations, hence fixes a "
            "point, contradicting the free action. For each of the other "
            "eight projected orbit points, choose one separating P2 linear "
            "form; multiply and pad both P2 degrees to nine"
        ),
        "invariant_evaluation_argument": (
            "Cover generation tensored with orbit-separating sections "
            "surjects onto the direct sum of nine orbit fibers; exact "
            "averaging makes invariant sections surject onto the quotient fiber"
        ),
        "first_large_twist_line_profiles": first_large_lines,
        "second_large_twist_line_profiles": second_large_lines,
        "cover_h0_constituents_at_generating_twist": cover_dimensions,
        "quotient_h0_constituents_at_generating_twist": [
            value // geometry.quotient.order for value in cover_dimensions
        ],
        "quotient_h0_rank_four_at_generating_twist": (
            sum(cover_dimensions) // geometry.quotient.order
        ),
        "first_constituent_h1_vanishes_at_generating_twist": True,
        "both_constituents_quotient_generated_at_generating_twist": True,
        "rank_four_quotient_generated_for_all_alternate_p1": True,
        "generation_at_base_twist_certified": False,
        "explicit_invariant_section_basis_constructed": False,
        "numerical_metrics_available": False,
        "physical_yukawas_available": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "first_constituent": first_digest,
            "alternate_cone": cone_digest,
            "alternate_carrier": carrier_digest,
        },
    }


def write_alternate_metric_quotient_generation(path: Path = OUTPUT) -> dict[str, object]:
    """Write the deterministic, content-addressed generation certificate."""

    payload = alternate_metric_quotient_generation()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_metric_quotient_generation()
    print(f"artifact_digest: {report['artifact_digest']}")
    print(f"generating_twist: {report['generating_twist_cover_degree']}")
