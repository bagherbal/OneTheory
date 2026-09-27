"""Contract actual alternate Hom syzygy blocks on minor principal opens.

Owns:
    Exact localized middle-object numerators for the saved strict Hom
    representative, checked against the right mixed-resolution arrows.

Depends on:
    The content-addressed Hom cochain, selected alternate constituent,
    published chart relation, and certified adjugate dual contraction.

Must not:
    Divide outside a minor principal open, discard fiber-overlap terms,
    assert global gluing, or identify a local correction with a Higgs state.

Phase 0:
    Research-only local homotopy data for the missing tensor transfer.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA, Eisenstein
from onetheory.math.sheaves import LaurentMatrix, LaurentPolynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pencil import BlowupChart, tier_a_pencil_model

from .alternate_constituent_duality_local_inverse import OUTPUT as LOCAL_INVERSE
from .alternate_constituent_duality_local_inverse import local_dual_contraction
from .alternate_up_higgs_chart_restriction import OUTPUT as CHART_RESTRICTION
from .alternate_up_higgs_chart_restriction import restrict_right_chart
from .alternate_up_higgs_hom_representative import (
    FULL_OUTPUT,
    load_alternate_up_higgs_hom_full_cochain,
)
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import MixedSchoenConstituent, _constituent
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions
from .published_constituent_overlap_transitions import (
    _embed_polynomial,
    _laurent_term,
    _relation_columns,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_higgs_local_syzygy_section.json"


def _zero() -> LaurentPolynomial:
    return LaurentPolynomial.zero(5, scalar_type=Eisenstein)


def _vector_record(vector: tuple[LaurentPolynomial, ...]) -> list[list[dict[str, object]]]:
    """Serialize exact homogeneous Laurent coordinates without division."""

    return [
        [
            {"exponents": list(exponents), "coefficient": str(coefficient)}
            for exponents, coefficient in polynomial.terms
        ]
        for polynomial in vector
    ]


def _right_mixed_matrix(
    right: MixedSchoenConstituent,
    chart: BlowupChart,
    x_cell: tuple[int, ...],
) -> LaurentMatrix:
    """Build syzygy targets of the actual Hom differential from its arrows."""

    values = [[_zero() for _ in range(5)] for _ in range(3)]
    for arrow in right.resolution_arrows:
        if arrow.source not in (5, 6, 7) or arrow.target not in (1, 2, 3, 4):
            continue
        values[arrow.source - 5][arrow.target] -= _embed_polynomial(arrow.polynomial)
    fiber_pivot = 0 if chart.fiber_chart == "mu" else 1
    for term in right.extension_terms:
        if (
            term.source not in (5, 6, 7)
            or term.target != 0
            or term.parent_degree != 1
            or term.koszul_equation is not None
            or term.cell != (x_cell, (chart.base_pivot,), (fiber_pivot,))
        ):
            continue
        if term.x_monomial != (0, 0, 0):
            raise ValueError("the right extension has unexpected x dependence")
        values[term.source - 5][0] -= _laurent_term(
            term.u_monomial, term.p_monomial, term.coefficient
        )
    return LaurentMatrix(tuple(tuple(row) for row in values))


def _multiply_vector(
    matrix: LaurentMatrix, vector: tuple[LaurentPolynomial, ...]
) -> tuple[LaurentPolynomial, ...]:
    """Multiply one exact Laurent matrix by a column vector."""

    if matrix.shape[1] != len(vector):
        raise ValueError("the local syzygy vector has the wrong length")
    return tuple(
        sum((entry * value for entry, value in zip(row, vector, strict=True)), _zero())
        for row in matrix.rows
    )


def alternate_up_higgs_local_syzygy_section() -> dict[str, object]:
    """Apply the exact adjugate section to every actual right-chart Hom block."""

    full_digest, _full = _verified_payload(FULL_OUTPUT)
    chart_digest, chart_artifact = _verified_payload(CHART_RESTRICTION)
    inverse_digest, inverse_artifact = _verified_payload(LOCAL_INVERSE)
    principal_opens = inverse_artifact.get("principal_open_row_pairs", {})
    if (
        chart_artifact.get("full_hom_cochain_artifact_digest") != full_digest
        or chart_artifact.get("all_right_restrictions_closed") is not True
        or inverse_artifact.get("schema")
        != "alternate-constituent-duality-local-inverse-v1"
        or inverse_artifact.get("dual_syzygy_contraction_exact") is not True
        or len(principal_opens) != 6
        or any([0, 1] not in pairs for pairs in principal_opens.values())
    ):
        raise ValueError("the saved Hom restriction or minor inverse is not certified")
    cochain = load_alternate_up_higgs_hom_full_cochain()
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    right = _constituent(ray, "I6-ray-0-1", 2, (-1, 1, 0))
    records = []
    for chart in tier_a_pencil_model().blowup_atlas.charts:
        relation = _relation_columns(ray, chart)
        contraction = local_dual_contraction(relation, 0, 1)
        denominator = contraction.denominator
        local = restrict_right_chart(cochain, chart)
        grouped: dict[
            tuple[tuple[int, ...], tuple[int, int, int], str],
            list[LaurentPolynomial],
        ] = defaultdict(lambda: [_zero(), _zero(), _zero()])
        for basis, coefficient in local.terms:
            index = basis.component.right_index
            if basis.component.left_index != 0 or index not in (5, 6, 7):
                raise ValueError("the local Hom source has a non-syzygy object")
            key = basis.cell[0], basis.x_monomial, basis.component.koszul_summand
            grouped[key][index - 5] += _laurent_term(
                basis.u_monomial, basis.p_monomial, coefficient
            )
        blocks = []
        for (x_cell, x_monomial, koszul), source_list in sorted(grouped.items()):
            source = tuple(source_list)
            section_relation_order = _multiply_vector(
                contraction.section_numerator, source
            )
            middle = (
                section_relation_order[4],
                *(-entry for entry in section_relation_order[:4]),
            )
            right_differential = _right_mixed_matrix(right, chart, x_cell)
            if any(
                right_differential.rows[syzygy][0]
                != relation.rows[4][syzygy]
                or any(
                    right_differential.rows[syzygy][middle_index + 1]
                    != -relation.rows[middle_index][syzygy]
                    for middle_index in range(4)
                )
                for syzygy in range(3)
            ):
                raise ValueError("the actual right differential disagrees with the local relation")
            if _multiply_vector(right_differential, middle) != tuple(
                denominator * entry for entry in source
            ):
                raise ValueError("the actual Hom syzygy block did not contract")
            blocks.append({
                "x_cell": list(x_cell),
                "x_monomial": list(x_monomial),
                "koszul_summand": koszul,
                "syzygy_source": _vector_record(source),
                "middle_numerator_object_order": _vector_record(middle),
                "right_differential_identity_exact": True,
            })
        if not blocks:
            raise ValueError("an alternate Hom chart has no local syzygy blocks")
        records.append({
            "chart": chart.name,
            "minor_rows": [0, 1],
            "minor_denominator": _vector_record((denominator,))[0],
            "block_count": len(blocks),
            "blocks": blocks,
            "localized_contraction_exact": True,
        })
    return {
        "schema": "alternate-up-higgs-local-syzygy-section-v1",
        "coefficient_field": "Q(omega)",
        "prerequisite_artifact_digests": {
            "full_hom_cochain": full_digest,
            "right_chart_restriction": chart_digest,
            "minor_open_inverse": inverse_digest,
        },
        "charts": records,
        "all_actual_syzygy_blocks_contracted_exactly": True,
        "minor_denominators_inverted_only_on_principal_opens": True,
        "fiber_overlap_gluing_constructed": False,
        "hom_to_tensor_chain_map_constructed": False,
        "exterior_cone_higgs_cocycle_constructed": False,
        "next_required_object": (
            "compare these localized middle numerators on fiber overlaps, "
            "then solve the full Cech-Koszul gluing homotopies"
        ),
    }


def write_alternate_up_higgs_local_syzygy_section(path: Path = OUTPUT) -> dict[str, object]:
    """Persist exact local middle numerators with explicit unfinished gates."""

    payload = alternate_up_higgs_local_syzygy_section()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    result = write_alternate_up_higgs_local_syzygy_section()
    print(f"artifact_digest: {result['artifact_digest']}")
    charts = cast(list[dict[str, object]], result["charts"])
    print(f"blocks: {[record['block_count'] for record in charts]}")
