"""Transport actual alternate Hom sections across right fiber overlaps.

Owns:
    Gauge-corrected middle numerators and exact Koszul divisibility on
    every fiber overlap of the saved strict up-Higgs Hom cochain.

Depends on:
    The persisted local syzygy sections, full Hom terms, alternate
    overlap atlas, and selected mixed right differential.

Must not:
    Identify these localized fiber-overlap data with a global tensor
    chain map, an exterior-cone Higgs cocycle, or a Yukawa entry.

Phase 0:
    Research-only explicit input for the remaining Čech--Koszul gluing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA, Eisenstein
from onetheory.math.sheaves import LaurentPolynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pencil import tier_a_pencil_model
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)

from .alternate_up_higgs_hom_representative import (
    FULL_OUTPUT,
    load_alternate_up_higgs_hom_full_cochain,
)
from .alternate_up_higgs_local_syzygy_section import OUTPUT as LOCAL_SECTION
from .alternate_up_higgs_local_syzygy_section import (
    _multiply_vector,
    _right_mixed_matrix,
    _vector_record,
)
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import _constituent
from .mixed_schoen_chain_actions import _parse_eisenstein_text
from .mixed_schoen_outer_universal_cone import _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions
from .published_constituent_overlap_transitions import (
    _atlas,
    _hypersurface_equation,
    _laurent_term,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_higgs_fiber_overlap_transport.json"


def _zero() -> LaurentPolynomial:
    return LaurentPolynomial.zero(5, scalar_type=Eisenstein)


def _polynomial(raw: object) -> LaurentPolynomial:
    """Load one content-addressed exact Laurent coordinate."""

    if not isinstance(raw, list):
        raise ValueError("a local Hom coordinate is not a term list")
    terms = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("a local Hom term is not a record")
        exponents = item.get("exponents")
        coefficient = item.get("coefficient")
        if (
            not isinstance(exponents, list)
            or len(exponents) != 5
            or not all(isinstance(value, int) for value in exponents)
            or not isinstance(coefficient, str)
        ):
            raise ValueError("a local Hom term has invalid exact data")
        terms.append((tuple(exponents), _parse_eisenstein_text(coefficient)))
    return LaurentPolynomial(terms, variable_count=5, scalar_type=Eisenstein)


def _vector(raw: object, length: int) -> tuple[LaurentPolynomial, ...]:
    """Load one typed exact local vector."""

    if not isinstance(raw, list) or len(raw) != length:
        raise ValueError("a local Hom vector has the wrong length")
    return tuple(_polynomial(item) for item in raw)


def _overlap_vectors(
    cochain: SparseOuterCechCochain,
    base_pivot: int,
    x_cell: tuple[int, ...],
) -> tuple[tuple[LaurentPolynomial, ...], tuple[LaurentPolynomial, ...], int, int]:
    """Extract actual middle and Koszul-syzygy fiber-edge terms."""

    middle = [_zero() for _ in range(5)]
    koszul = [_zero() for _ in range(3)]
    middle_count = 0
    koszul_count = 0
    for basis, coefficient in cochain.terms:
        if basis.cell != (x_cell, (base_pivot,), (0, 1)):
            continue
        if basis.x_monomial != (0, 0, 0) or basis.component.left_index != 0:
            raise ValueError("the alternate fiber overlap left factor changed")
        index = basis.component.right_index
        if basis.component.koszul_summand == "k0" and 0 <= index < 5:
            middle[index] += _laurent_term(
                basis.u_monomial, basis.p_monomial, coefficient
            )
            middle_count += 1
        elif basis.component.koszul_summand == "k1_u" and 5 <= index < 8:
            koszul[index - 5] += _laurent_term(
                basis.u_monomial, basis.p_monomial, coefficient
            )
            koszul_count += 1
        else:
            raise ValueError("the alternate fiber overlap has an unexpected object")
    if middle_count != 9 or koszul_count != 6:
        raise ValueError("the strict Hom fiber-overlap support changed")
    return tuple(middle), tuple(koszul), middle_count, koszul_count


def alternate_up_higgs_fiber_overlap_transport() -> dict[str, object]:
    """Cancel chart syzygies and retain exact hypersurface overlap residuals."""

    full_digest, _full = _verified_payload(FULL_OUTPUT)
    section_digest, section_artifact = _verified_payload(LOCAL_SECTION)
    inputs = section_artifact.get("prerequisite_artifact_digests", {})
    if (
        section_artifact.get("schema") != "alternate-up-higgs-local-syzygy-section-v1"
        or inputs.get("full_hom_cochain") != full_digest
        or section_artifact.get("all_actual_syzygy_blocks_contracted_exactly") is not True
    ):
        raise ValueError("the actual Hom local section is not certified")
    records = {item["chart"]: item for item in section_artifact["charts"]}
    cochain = load_alternate_up_higgs_hom_full_cochain()
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    right = _constituent(ray, "I6-ray-0-1", 2, (-1, 1, 0))
    atlas = _atlas(ray)
    equation = _hypersurface_equation(ray)
    chart_lookup = {
        (chart.base_pivot, chart.fiber_chart): chart
        for chart in tier_a_pencil_model().blowup_atlas.charts
    }
    results = []
    for base_pivot in range(3):
        mu = chart_lookup[(base_pivot, "mu")]
        nu = chart_lookup[(base_pivot, "nu")]
        transition = next(
            item for item in atlas.transitions
            if item.source == mu and item.target == nu
        )
        mu_record = records[mu.name]
        nu_record = records[nu.name]
        d_mu = _polynomial(mu_record["minor_denominator"])
        d_nu = _polynomial(nu_record["minor_denominator"])
        if d_mu.is_zero() or d_nu.is_zero():
            raise ValueError("a declared principal-open minor vanished")
        mu_blocks = {tuple(item["x_cell"]): item for item in mu_record["blocks"]}
        nu_blocks = {tuple(item["x_cell"]): item for item in nu_record["blocks"]}
        reference_numerator: tuple[LaurentPolynomial, ...] | None = None
        reference_koszul: tuple[LaurentPolynomial, ...] | None = None
        for x_pivot in range(3):
            x_cell = (x_pivot,)
            source_mu = _vector(mu_blocks[x_cell]["syzygy_source"], 3)
            source_nu = _vector(nu_blocks[x_cell]["syzygy_source"], 3)
            middle_mu = _vector(mu_blocks[x_cell]["middle_numerator_object_order"], 5)
            middle_nu = _vector(nu_blocks[x_cell]["middle_numerator_object_order"], 5)
            overlap_middle, overlap_koszul, middle_count, koszul_count = (
                _overlap_vectors(cochain, base_pivot, x_cell)
            )
            differential = _right_mixed_matrix(right, nu, x_cell)
            original_residual = _multiply_vector(differential, overlap_middle)
            if any(
                source_mu[index] - source_nu[index]
                + original_residual[index] - equation * overlap_koszul[index]
                != _zero()
                for index in range(3)
            ):
                raise ValueError("the actual Hom fiber-overlap equation failed")
            if not any(not entry.is_zero() for entry in overlap_koszul):
                raise ValueError("the actual Hom overlap no longer needs its Koszul term")
            transported_mu = (
                middle_mu[0],
                *(
                    middle_mu[index + 1]
                    - transition.gauge[index] * middle_mu[0]
                    for index in range(4)
                ),
            )
            numerator = tuple(
                d_mu * d_nu * overlap_middle[index]
                + d_nu * transported_mu[index]
                - d_mu * middle_nu[index]
                for index in range(5)
            )
            koszul_numerator = tuple(
                d_nu * (
                    d_mu * overlap_koszul[index]
                    + transition.hypersurface_homotopy[index] * middle_mu[0]
                )
                for index in range(3)
            )
            if _multiply_vector(differential, numerator) != tuple(
                equation * entry for entry in koszul_numerator
            ):
                raise ValueError("the gauge-corrected Hom overlap failed Koszul divisibility")
            if reference_numerator is None:
                reference_numerator = numerator
                reference_koszul = koszul_numerator
                results.append({
                    "base_pivot": base_pivot,
                    "first_factor_x_cells_checked": [[0], [1], [2]],
                    "source_chart": mu.name,
                    "target_chart": nu.name,
                    "minor_product_denominator": _vector_record((d_mu * d_nu,))[0],
                    "middle_source_term_count_per_x_cell": middle_count,
                    "koszul_source_term_count_per_x_cell": koszul_count,
                    "corrected_middle_numerator_object_order": _vector_record(numerator),
                    "koszul_residual_numerator": _vector_record(koszul_numerator),
                    "original_overlap_equation_exact": True,
                    "koszul_term_necessary_exact": True,
                    "corrected_koszul_divisibility_exact": True,
                    "x_cell_independence_exact": True,
                })
            elif numerator != reference_numerator or koszul_numerator != reference_koszul:
                raise ValueError("the first-factor Hom overlap formulas differ")
    if len(results) != 3:
        raise ValueError("the alternate Hom fiber overlaps are incomplete")
    independent_fields = (
        "minor_product_denominator",
        "middle_source_term_count_per_x_cell",
        "koszul_source_term_count_per_x_cell",
        "corrected_middle_numerator_object_order",
        "koszul_residual_numerator",
    )
    if any(
        record[field] != results[0][field]
        for record in results[1:]
        for field in independent_fields
    ):
        raise ValueError("the base-chart Hom fiber formulas differ")
    representative = {
        field: results[0][field] for field in independent_fields
    }
    representative.update({
        "base_pivots_checked": [0, 1, 2],
        "first_factor_x_cells_checked": [[0], [1], [2]],
        "original_overlap_equation_exact": True,
        "koszul_term_necessary_exact": True,
        "corrected_koszul_divisibility_exact": True,
    })
    return {
        "schema": "alternate-up-higgs-fiber-overlap-transport-v1",
        "coefficient_field": "Q(omega)",
        "prerequisite_artifact_digests": {
            "full_hom_cochain": full_digest,
            "local_syzygy_section": section_digest,
        },
        "fiber_overlap_representative": representative,
        "fiber_overlap_blocks_checked": 9,
        "first_factor_x_cell_independence_exact": True,
        "base_chart_formula_independence_exact": True,
        "all_original_overlap_equations_exact": True,
        "all_corrected_koszul_divisibility_exact": True,
        "base_overlap_gluing_constructed": False,
        "global_hom_to_tensor_chain_map_constructed": False,
        "exterior_cone_higgs_cocycle_constructed": False,
        "next_required_object": (
            "use the explicit nine corrected overlap blocks to solve the "
            "remaining base-cover and minor-open Cech-Koszul gluing"
        ),
    }


def write_alternate_up_higgs_fiber_overlap_transport(path: Path = OUTPUT) -> dict[str, object]:
    """Persist corrected overlap data without claiming global completion."""

    payload = alternate_up_higgs_fiber_overlap_transport()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    result = write_alternate_up_higgs_fiber_overlap_transport()
    representative = cast(dict[str, object], result["fiber_overlap_representative"])
    print(f"artifact_digest: {result['artifact_digest']}")
    print(f"fiber_overlap_blocks: {result['fiber_overlap_blocks_checked']}")
    print(f"base_pivots: {representative['base_pivots_checked']}")
