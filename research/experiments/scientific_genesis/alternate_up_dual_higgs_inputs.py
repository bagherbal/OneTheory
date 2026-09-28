"""Put actual alternate Higgs-action inputs in reciprocal line-valued Hom.

Owns:
    The global first-constituent quotient of both outer-extension
    cochains and the exact retargeting of the A-supported Higgs class.

Depends on:
    The certified Hilbert--Burch A-line map, frozen alternate F
    resolution, full Hom representatives, and exact mixed transfer.

Must not:
    Identify these inputs with a determinant-line primitive, infer a
    Yukawa coefficient, or replace the missing derived exterior product.

Phase 0:
    Research-only reciprocal covectors for the first-order Higgs action.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    _independent_columns,
    _SparseSpanSolver,
)

from .alternate_constituent_outer_universal_cone import INVARIANTS
from .alternate_up_higgs_hom_representative import FULL_OUTPUT as HIGGS
from .alternate_up_higgs_hom_representative import (
    load_alternate_up_higgs_hom_full_cochain,
)
from .alternate_up_mixed_scalar_trace import _a_line_pairing
from .distinct_constituent_ray_screen import lift_joint_character_ray
from .mixed_constituent_schoen_arrows import MixedConstituentObject, _constituent
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction, _perturbed_projection
from .mixed_schoen_outer_transfer import MixedSchoenUnit, _transfer_map
from .mixed_schoen_outer_universal_cone import _representative, _verified_payload
from .published_constituent_deck_actions import published_constituent_deck_actions

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_dual_higgs_inputs.json"


@dataclass(frozen=True, slots=True)
class DualHiggsInputs:
    """Exact reciprocal covectors, not their uncomputed exterior product."""

    outer_covectors: tuple[SparseOuterCechCochain, SparseOuterCechCochain]
    higgs_covector: SparseOuterCechCochain
    outer_coordinates: tuple[tuple[tuple[int, Eisenstein], ...], ...]
    higgs_coordinates: tuple[tuple[int, Eisenstein], ...]
    projection_depths: tuple[int, int, int]
    invariant_digest: str
    higgs_digest: str

    def as_record(self) -> dict[str, object]:
        """Record actual cochains and the remaining determinant-line gate."""

        return {
            "schema": "alternate-up-dual-higgs-inputs-v1",
            "coefficient_field": "Q(omega)",
            "outer_parameter_basis": ["a0", "a1"],
            "first_a_line_degree": [-1, 1, -1],
            "first_determinant_degree": [-2, 2, 0],
            "quotient_b_line_degree": [-1, 1, 1],
            "higgs_target_line_degree": [1, -1, -1],
            "outer_covectors": [
                {
                    "parameter": f"a{index}",
                    "term_count": len(cochain.terms),
                    "digest": _cochain_digest((cochain,)),
                    "full_cycle_exact": True,
                    "nonboundary_exact": True,
                    "projection_depth": self.projection_depths[index],
                    "reduced_coordinates": [[row, str(value)] for row, value in coordinates],
                }
                for index, (cochain, coordinates) in enumerate(zip(
                    self.outer_covectors, self.outer_coordinates, strict=True
                ))
            ],
            "higgs_covector": {
                "term_count": len(self.higgs_covector.terms),
                "digest": _cochain_digest((self.higgs_covector,)),
                "full_cycle_exact": True,
                "nonboundary_exact": True,
                "projection_depth": self.projection_depths[2],
                "reduced_coordinates": [[row, str(value)] for row, value in self.higgs_coordinates],
            },
            "outer_images_independent_mod_boundaries": True,
            "target_lines_reciprocal_exact": True,
            "minor_inversion_used": False,
            "hom_to_tensor_inverse_used": False,
            "determinant_line_higgs_action_computed": False,
            "determinant_line_higgs_primitive_computed": False,
            "null_to_null_yukawa_computed": False,
            "prerequisite_artifact_digests": {
                "outer_invariants": self.invariant_digest,
                "strict_higgs_hom": self.higgs_digest,
            },
            "next_required_object": (
                "form the signed derived exterior product of reciprocal "
                "F-dual covectors and solve its determinant-line primitive"
            ),
        }


def _quotient(
    extension: SparseOuterCechCochain, context: _MixedContraction
) -> SparseOuterCechCochain:
    """Push an E-valued Hom cochain through the exact quotient row."""

    terms = []
    pairings = _a_line_pairing()
    for basis, coefficient in extension.terms:
        row = basis.component.left_index
        if row not in range(6):
            raise ValueError("the quotient input has an unknown E object")
        if row in (0, 4, 5):
            continue
        component = context.components[(
            0, basis.component.right_index, basis.component.koszul_summand
        )]
        for exponents, scalar in pairings[row - 1].terms:
            terms.append((
                OuterCechBasis(
                    component,
                    tuple(basis.x_monomial[i] + exponents[i] for i in range(3)),
                    basis.u_monomial,
                    tuple(basis.p_monomial[i] + exponents[i + 3] for i in range(2)),
                    basis.cell,
                ),
                coefficient * scalar,
            ))
    return SparseOuterCechCochain(tuple(terms))


def _independent_image(
    cochain: SparseOuterCechCochain,
    context: _MixedContraction,
    span: tuple[dict[int, Eisenstein], ...],
) -> tuple[dict[int, Eisenstein], int]:
    """Require a full cycle outside the declared exact reduced span."""

    if cochain.is_zero() or not context.differential(cochain).is_zero():
        raise ValueError("a reciprocal Hom input is not a nonzero full cycle")
    reduced, depth = _perturbed_projection(cochain, context, 1)
    try:
        _SparseSpanSolver(span).coordinates(reduced)
    except ValueError as error:
        if str(error) != "transferred deck image escaped the cycle span":
            raise
    else:
        raise ValueError("a reciprocal Hom input lies in the previous reduced span")
    return reduced, depth


@cache
def alternate_up_dual_higgs_inputs() -> DualHiggsInputs:
    """Construct the actual smaller inputs without localized duality."""

    invariant_digest, invariant = _verified_payload(INVARIANTS)
    higgs_digest, _ = _verified_payload(HIGGS)
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    second = _constituent(ray, "I6-ray-0-1", 2, (1, -1, 0))
    b = MixedSchoenUnit(
        "B1", 0, (-1, 1, 1),
        (MixedConstituentObject("B1", 0, (-1, 1, 1)),),
    )
    inverse_b = MixedSchoenUnit(
        "B1 inverse", 0, (1, -1, -1),
        (MixedConstituentObject("B1 inverse", 0, (1, -1, -1)),),
    )
    context = _MixedContraction(b, second)
    incoming, _ = _transfer_map(b, second, 0)
    span = _independent_columns(incoming)
    covectors, coordinates, depths = [], [], []
    raw = invariant.get("strict_full_cech_representatives")
    if (
        invariant.get("schema") != "alternate-constituent-outer-invariants-v1"
        or not isinstance(raw, list)
        or len(raw) != 2
    ):
        raise ValueError("the frozen two-parameter extension basis changed")
    for item in raw:
        cochain = _quotient(_representative(item), context)
        reduced, depth = _independent_image(cochain, context, span)
        span += (reduced,)
        covectors.append(cochain)
        coordinates.append(tuple(sorted(reduced.items())))
        depths.append(depth)
    inverse_context = _MixedContraction(inverse_b, second)
    higgs_terms = []
    for basis, coefficient in load_alternate_up_higgs_hom_full_cochain().terms:
        if basis.component.left_index != 0:
            raise ValueError("the saved Higgs no longer has pure A output")
        component = inverse_context.components[(
            0, basis.component.right_index, basis.component.koszul_summand
        )]
        if component != basis.component:
            raise ValueError("the reciprocal Higgs retargeting changed its grading")
        higgs_terms.append((basis, coefficient))
    higgs = SparseOuterCechCochain(tuple(higgs_terms))
    inverse_incoming, _ = _transfer_map(inverse_b, second, 0)
    higgs_reduced, higgs_depth = _independent_image(
        higgs, inverse_context, _independent_columns(inverse_incoming)
    )
    return DualHiggsInputs(
        (covectors[0], covectors[1]), higgs,
        tuple(coordinates), tuple(sorted(higgs_reduced.items())),
        (depths[0], depths[1], higgs_depth), invariant_digest, higgs_digest,
    )


def write_alternate_up_dual_higgs_inputs(path: Path = OUTPUT) -> dict[str, object]:
    """Persist the reciprocal input reduction without an action claim."""

    payload = alternate_up_dual_higgs_inputs().as_record()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    result = write_alternate_up_dual_higgs_inputs()
    print(f"artifact_digest: {result['artifact_digest']}")
