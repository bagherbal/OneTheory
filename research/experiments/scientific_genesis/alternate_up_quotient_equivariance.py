"""Derive the quotient line's inherited frame and check the Higgs character.

Owns:
    The full global minor row, its uniquely induced B1 linearization,
    quotient and graded exterior frames, and exact connecting-map covariance.

Depends on:
    Certified native constituent frames, the fixed Schoen coordinate lifts,
    actual Serre quotients, and the frozen common flat determinant repair.

Must not:
    Choose a flat phase to fit a spectrum, confuse a covector with its
    dual Higgs before determinant repair, or certify a complete physical pairing.

Phase 0:
    Research-only equivariant comparison for the natural Higgs quotient.
"""

from __future__ import annotations

import json
from functools import cache
from itertools import product
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.computable_carrier.schoen_sparse_actions import schoen_sparse_deck_actions

from .alternate_constituent_hom_actions import _common_frame
from .alternate_constituent_outer_universal_cone import OUTPUT as OUTER_CONE
from .alternate_up_exterior_higgs_action import alternate_up_exterior_context
from .alternate_up_higgs_covector_comparison import QUOTIENT_LINE
from .alternate_up_higgs_hom_representative import HOM_CHARACTER
from .alternate_up_higgs_hom_representative import OUTPUT as HIGGS
from .alternate_up_higgs_quotient_cone import OUTPUT as QUOTIENT_CONE
from .alternate_up_higgs_quotient_cone import (
    alternate_higgs_quotient_connecting_arrow,
    alternate_higgs_quotient_covector,
    alternate_higgs_quotient_models,
)
from .alternate_up_mixed_scalar_trace import _a_line_pairing
from .mixed_constituent_schoen_arrows import MixedConstituentObject, mixed_schoen_constituents
from .mixed_schoen_exterior_square import graded_exterior_frame
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _full_action, _MixedContraction
from .mixed_schoen_outer_transfer import MixedSchoenUnit, mixed_schoen_unit
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_quotient_equivariance.json"


@cache
def global_first_quotient_cochain() -> SparseOuterCechCochain:
    """Represent the actual polynomial row on every product-cover vertex."""

    first = mixed_schoen_constituents()[0]
    line = MixedSchoenUnit(
        "B1", 0, QUOTIENT_LINE,
        (MixedConstituentObject("B1", 0, QUOTIENT_LINE),),
    )
    context = _MixedContraction(line, first)
    terms = []
    for row, polynomial in enumerate(_a_line_pairing(), start=1):
        component = context.components[(0, row, "k0")]
        for exponents, value in polynomial.terms:
            for x, u, p in product(range(3), range(3), range(2)):
                terms.append((OuterCechBasis(
                    component, cast(tuple[int, int, int], exponents[:3]),
                    (0, 0, 0), cast(tuple[int, int], exponents[3:]),
                    ((x,), (u,), (p,)),
                ), Eisenstein.coerce(value)))
    cochain = SparseOuterCechCochain(tuple(terms))
    if cochain.is_zero() or not context.differential(cochain).is_zero():
        raise ValueError("the global first quotient is not a nonzero full degree-zero map")
    return cochain


def _scalar_ratio(image: SparseOuterCechCochain, original: SparseOuterCechCochain) -> Eisenstein:
    """Derive a scalar only when it reproduces every exact coefficient."""

    if original.is_zero():
        raise ValueError("the natural quotient frame needs a nonzero map")
    basis, coefficient = original.terms[0]
    ratio = dict(image.terms).get(basis, Eisenstein(0)) / coefficient
    if ratio.is_zero() or image != original.scale(ratio):
        raise ValueError("the global quotient does not induce a scalar line frame")
    return ratio


@cache
def quotient_deck_frames(generator: str) -> tuple[Eisenstein, Matrix, Matrix]:
    """Return inherited B1, K, and exterior-F frames without fitting a phase."""

    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    if generator not in actions:
        raise ValueError("the declared quotient deck generator is unavailable")
    action = actions[generator]
    first = mixed_schoen_constituents()[0]
    second, _ = alternate_higgs_quotient_models()
    line = MixedSchoenUnit(
        "B1", 0, QUOTIENT_LINE,
        (MixedConstituentObject("B1", 0, QUOTIENT_LINE),),
    )
    q = global_first_quotient_cochain()
    identity = Matrix.identity(1, scalar_type=Eisenstein)
    first_frame = _common_frame(first, action)
    raw_image = _full_action(q, line, first, action, (identity, first_frame))
    # Left multiplication by this inverse is forced by q's equivariance.
    line_scalar = Eisenstein(1) / _scalar_ratio(raw_image, q)
    if line_scalar**3 != Eisenstein(1):
        raise ValueError("the induced B1 frame is not an order-three line character")
    if _full_action(q, line, first, action, (identity.scale(line_scalar), first_frame)) != q:
        raise ValueError("the inherited B1 frame does not make the full quotient equivariant")
    second_frame = _common_frame(second, action)
    if any(
        not second_frame[row][column].is_zero()
        for row in range(second_frame.row_count)
        for column in range(second_frame.column_count)
        if (row == 0) != (column == 0)
    ):
        raise ValueError("the constituent frame does not preserve its actual A quotient")
    quotient_frame = Matrix(tuple(tuple(
        Eisenstein.coerce(second_frame[row][column]) * line_scalar
        for column in range(1, second_frame.column_count)
    ) for row in range(1, second_frame.row_count)), scalar_type=Eisenstein)
    exterior, _ = alternate_up_exterior_context()
    return line_scalar, quotient_frame, graded_exterior_frame(exterior, second_frame)


def write_alternate_up_quotient_equivariance(path: Path = OUTPUT) -> dict[str, object]:
    """Check actual covariance before recording the repaired Higgs character."""

    quotient_digest, _ = _verified_payload(QUOTIENT_CONE)
    cone_digest, cone = _verified_payload(OUTER_CONE)
    higgs_digest, higgs_reference = _verified_payload(HIGGS)
    if (
        cone.get("schema") != "alternate-constituent-outer-universal-cone-v1"
        or cone.get("common_flat_character_twist") != [1, 2]
        or cone.get("determinant_character_after_common_twist") != [0, 0]
        or higgs_reference.get("hom_character") != list(HOM_CHARACTER)
    ):
        raise ValueError("the frozen determinant repair or native Higgs character changed")
    _, quotient = alternate_higgs_quotient_models()
    exterior, _ = alternate_up_exterior_context()
    covector = alternate_higgs_quotient_covector()
    unit = mixed_schoen_unit()
    identity = Matrix.identity(1, scalar_type=Eisenstein)
    records = []
    for generator_index, action in enumerate(schoen_sparse_deck_actions()):
        if action.name not in ("P", "T"):
            raise ValueError("the quotient has an undeclared deck generator")
        line_scalar, quotient_frame, exterior_frame = quotient_deck_frames(action.name)
        image = _full_action(covector, unit, quotient, action, (identity, quotient_frame))
        expected = OMEGA**HOM_CHARACTER[generator_index]
        if image != covector.scale(expected):
            raise ValueError("the inherited quotient Higgs has a different exact native character")
        arrow_records = []
        for parameter_index in range(2):
            arrow = alternate_higgs_quotient_connecting_arrow(parameter_index)
            transported = _full_action(
                arrow, quotient, exterior, action, (quotient_frame, exterior_frame),
            )
            if transported != arrow:
                raise ValueError("a natural quotient connecting arrow is not strictly deck fixed")
            arrow_records.append({
                "parameter": f"a{parameter_index}",
                "full_connecting_arrow_digest": _cochain_digest((arrow,)),
                "full_connecting_arrow_strictly_fixed_exact": True,
            })
        records.append({
            "generator": action.name,
            "inherited_B1_line_frame": str(line_scalar),
            "full_global_quotient_strictly_equivariant_exact": True,
            "native_higgs_eigenvalue": str(expected),
            "full_quotient_higgs_character_exact": True,
            "connecting_arrows": arrow_records,
        })
    twist = cast(list[int], cone["common_flat_character_twist"])
    repaired = [(value - 2 * phase) % 3 for value, phase in zip(HOM_CHARACTER, twist, strict=True)]
    if repaired != higgs_reference.get("repaired_higgs_forward_character"):
        raise ValueError("the repaired quotient covector misses the actual up-Higgs sector")
    payload: dict[str, object] = {
        "schema": "alternate-up-quotient-equivariance-v1",
        "coefficient_field": "Q(omega)",
        "global_first_quotient_term_count": len(global_first_quotient_cochain().terms),
        "global_first_quotient_digest": _cochain_digest((global_first_quotient_cochain(),)),
        "generator_checks": records,
        "native_quotient_covector_character": list(HOM_CHARACTER),
        "common_flat_twist": twist,
        "covector_common_twist_weight": -2,
        "repaired_up_higgs_character": repaired,
        "determinant_repair_makes_covector_and_forward_higgs_characters_equal": True,
        "line_frame_selected_to_fit_spectrum": False,
        "physical_pairing_chain_map_constructed": False,
        "complete_holomorphic_up_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "quotient_cone": quotient_digest, "outer_cone": cone_digest,
            "native_higgs": higgs_digest,
        },
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    record = write_alternate_up_quotient_equivariance()
    print(f"artifact_digest: {record['artifact_digest']}")
