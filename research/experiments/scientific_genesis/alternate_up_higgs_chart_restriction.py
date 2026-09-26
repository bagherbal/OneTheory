"""Restrict the actual alternate up-Higgs Hom cochain to right affine charts.

Owns:
    Exact evaluation of its right Čech factors at the six I6 chart vertices,
    retaining the first-factor Čech and Koszul data.

Depends on:
    The persisted strict Hom representative and the same alternate mixed
    differential that established its full-cycle identity.

Must not:
    Discard right syzygy-dual terms, identify a chart restriction with a
    global tensor cocycle, or infer a Yukawa coefficient.

Phase 0:
    Research-only source data for localized Hom-to-tensor transport.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from onetheory.math.numbers import OMEGA
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pencil import BlowupChart, tier_a_pencil_model
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)

from .alternate_up_higgs_hom_representative import (
    FULL_OUTPUT,
    load_alternate_up_higgs_hom_full_cochain,
)
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import _constituent, mixed_schoen_constituents
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_higgs_chart_restriction.json"


def restrict_right_chart(
    cochain: SparseOuterCechCochain, chart: BlowupChart
) -> SparseOuterCechCochain:
    """Keep only singleton right-cover cells at one declared affine chart."""

    fiber_pivot = 0 if chart.fiber_chart == "mu" else 1
    return SparseOuterCechCochain(tuple(
        (basis, coefficient)
        for basis, coefficient in cochain.terms
        if basis.cell[1] == (chart.base_pivot,)
        and basis.cell[2] == (fiber_pivot,)
    ))


def alternate_up_higgs_chart_restriction() -> dict[str, object]:
    """Check local right-Čech closure of every saved strict Hom term."""

    full_digest, full_artifact = _verified_payload(FULL_OUTPUT)
    cochain = load_alternate_up_higgs_hom_full_cochain()
    first = mixed_schoen_constituents()[0]
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    right = _constituent(ray, "I6-ray-0-1", 2, (-1, 1, 0))
    contraction = _MixedContraction(first, right)
    if not contraction.differential(cochain).is_zero():
        raise ValueError("the saved alternate Hom source is not a full cycle")
    records = []
    for chart in tier_a_pencil_model().blowup_atlas.charts:
        local = restrict_right_chart(cochain, chart)
        residual = restrict_right_chart(contraction.differential(local), chart)
        if local.is_zero() or not residual.is_zero():
            raise ValueError("the alternate Hom restriction is not locally closed")
        right_counts = Counter(
            basis.component.right_index for basis, _coefficient in local.terms
        )
        records.append({
            "chart": chart.name,
            "term_count": len(local.terms),
            "digest": _cochain_digest((local,)),
            "right_object_term_counts": {
                str(index): count for index, count in sorted(right_counts.items())
            },
            "middle_term_count": sum(
                count for index, count in right_counts.items() if index <= 4
            ),
            "syzygy_dual_term_count": sum(
                count for index, count in right_counts.items() if index >= 5
            ),
            "right_chart_restricted_cycle_exact": True,
        })
    if len(records) != 6 or any(item["syzygy_dual_term_count"] == 0 for item in records):
        raise ValueError("the six-chart Hom syzygy support changed")
    overlap_counts = Counter(
        (len(basis.cell[1]), len(basis.cell[2]), basis.component.right_index)
        for basis, _coefficient in cochain.terms
        if len(basis.cell[1]) > 1 or len(basis.cell[2]) > 1
    )
    if (
        sum(overlap_counts.values()) != 135
        or any(base_size != 1 or fiber_size != 2 for base_size, fiber_size, _ in overlap_counts)
    ):
        raise ValueError("the alternate Hom overlap support changed")
    return {
        "schema": "alternate-up-higgs-chart-restriction-v1",
        "coefficient_field": "Q(omega)",
        "full_hom_cochain_artifact_digest": full_digest,
        "full_hom_term_digest": full_artifact["full_digest"],
        "right_chart_records": records,
        "right_fiber_overlap_term_count": sum(overlap_counts.values()),
        "right_fiber_overlap_middle_term_count": sum(
            count for (_base, _fiber, index), count in overlap_counts.items()
            if index <= 4
        ),
        "right_fiber_overlap_syzygy_term_count": sum(
            count for (_base, _fiber, index), count in overlap_counts.items()
            if index >= 5
        ),
        "all_right_restrictions_closed": True,
        "syzygy_dual_terms_retained": True,
        "hom_to_tensor_transport_constructed": False,
        "exterior_cone_higgs_cocycle_constructed": False,
        "next_required_object": (
            "apply the minor-open dual syzygy contraction to each actual "
            "right-chart Hom restriction, then glue the quotient images"
        ),
    }


def write_alternate_up_higgs_chart_restriction(path: Path = OUTPUT) -> dict[str, object]:
    """Persist six exact local support checks without a Higgs claim."""

    payload = alternate_up_higgs_chart_restriction()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    result = write_alternate_up_higgs_chart_restriction()
    print(f"artifact_digest: {result['artifact_digest']}")
    print(f"chart_terms: {[item['term_count'] for item in result['right_chart_records']]}")
