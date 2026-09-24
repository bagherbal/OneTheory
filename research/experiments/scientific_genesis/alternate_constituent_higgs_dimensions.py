"""Compute cover Higgs dimensions for unused locally free I6 Ext rays.

Owns:
    Exact full mixed-complex rank calculations for two fixed alternate rays,
    with the rank-two determinant identity made explicit.

Depends on:
    The finite local-unit screen, full constituent Čech lifts, synchronized
    Schoen mixed-arrow transfer, and exact sparse linear algebra.

Must not:
    Infer alternate quotient descent, deck characters, Wilson projection,
    or a physical Higgs spectrum from cover dimensions.

Phase 0:
    Research-only reproducible necessary calculation.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer import (
    schoen_serre_outer_hom,
)

from .distinct_constituent_ray_screen import (
    OUTPUT as RAY_SCREEN,
)
from .distinct_constituent_ray_screen import (
    lift_joint_character_ray,
)
from .mixed_constituent_schoen_arrows import _constituent, mixed_schoen_constituents
from .mixed_schoen_higgs_character_audit import _map_digest
from .mixed_schoen_outer_transfer import _skeleton, _transfer_map
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_constituent_higgs_dimensions.json"
ALTERNATE_RAYS = ((0, 1), (1, 1))


def alternate_constituent_higgs_dimensions() -> dict[str, object]:
    """Compute exact cover H1 ranks without claiming quotient Higgs states."""

    screen = json.loads(RAY_SCREEN.read_text(encoding="utf-8"))
    digest = screen.pop("artifact_digest", None)
    if (
        digest != _canonical_digest(screen)
        or screen.get("unused_i6_local_unit_rays")
        != [list(ray) for ray in ALTERNATE_RAYS]
    ):
        raise ValueError("the locally free alternate-ray screen changed")

    first = mixed_schoen_constituents()[0]
    action = published_constituent_deck_actions()[1]
    jobs = {}
    cases = {}
    for p_exponent, t_exponent in ALTERNATE_RAYS:
        lifted = lift_joint_character_ray(
            action, OMEGA**p_exponent, OMEGA**t_exponent
        )
        if not (
            lifted.alignment.source_ray.p_fixed
            and lifted.alignment.source_ray.t_fixed
            and lifted.alignment.selected_chain_eigenvector
        ):
            raise ValueError("an alternate ray lacks its exact joint deck action")
        # For rank-two V1, V1* tensor det(V1) is canonically V1.
        # Its cover determinant degree is (-2, 2, 0), so this is the
        # required twist for Hom(V1, V2 tensor det(V1)).
        second = _constituent(
            lifted, f"I6-ray-{p_exponent}-{t_exponent}", 2, (-1, 1, 0)
        )
        reduced = schoen_serre_outer_hom(_skeleton(first), _skeleton(second))
        spaces = dict(reduced.total_spaces)
        label = (p_exponent, t_exponent)
        cases[label] = (spaces, lifted.inclusion_depth)
        jobs[label] = second

    records = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures = {
            (label, degree): pool.submit(_transfer_map, first, second, degree)
            for label, second in jobs.items()
            for degree in (0, 1)
        }
        for label in ALTERNATE_RAYS:
            spaces, lift_depth = cases[label]
            map0, depth0 = futures[label, 0].result()
            map1, depth1 = futures[label, 1].result()
            if not map1.compose(map0).is_zero():
                raise ValueError("alternate transferred differential does not square to zero")
            rank0, rank1 = map0.rank(), map1.rank()
            records.append({
                "ray_character_exponents": list(label),
                "space_dimensions": [
                    [degree, space.dimension] for degree, space in sorted(spaces.items())
                ],
                "differential_ranks": [[0, rank0], [1, rank1]],
                "h1_dimension": spaces[1].dimension - rank0 - rank1,
                "squared_zero_through_degree_one": True,
                "full_lift_depth": lift_depth,
                "transfer_path_depths": [[0, depth0], [1, depth1]],
                "map_digests": [[0, _map_digest(map0)], [1, _map_digest(map1)]],
            })
    return {
        "schema": "alternate-constituent-higgs-dimensions-v1",
        "scope": "cover H1 only for two local-unit I6 rays in the fixed presentation",
        "identity": "Hom(V1,V2 tensor det(V1)) = V1 tensor V2 for rank-two V1",
        "v1_determinant_cover_degree": [-2, 2, 0],
        "v2_hom_twist_after_identity": [-1, 1, 0],
        "cases": records,
        "alternate_deck_atlases_constructed": False,
        "alternate_quotient_determinants_certified": False,
        "alternate_higgs_characters_computed": False,
        "physical_higgs_spectrum_established": False,
        "next_required_object": (
            "alternate common-Schoen deck transfer and quotient determinant; "
            "then invariant cover H1 characters and Wilson projection"
        ),
    }


def write_alternate_constituent_higgs_dimensions(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed exact cover-rank certificate."""

    payload = alternate_constituent_higgs_dimensions()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    report = write_alternate_constituent_higgs_dimensions()
    print(f"artifact_digest: {report['artifact_digest']}")
    for case in cast(list[dict[str, object]], report["cases"]):
        print(f"ray {case['ray_character_exponents']}: H1={case['h1_dimension']}")
