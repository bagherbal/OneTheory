"""Contract alternate mixed-family Yoneda classes to scalar residues.

Owns:
    The exact first-constituent alternating contraction of strict I3
    matter classes with nonboundary Hom-evaluated I6 classes, and the
    global Hilbert--Burch pairing with an actual A-line cochain.

Depends on:
    The frozen carrier's first Pluecker form, exact common-cover
    cochains, and the ordered Schoen scalar-residue convention.

Must not:
    Call a partial holomorphic block a full matrix, infer a physical
    Yukawa, choose an outer-extension point, or suppress a failed closure.

Phase 0:
    Research-only mixed-family scalar calculation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Eisenstein
from onetheory.math.sheaves import LaurentPolynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    KOSZUL_DEGREES,
    OuterCechBasis,
    SparseOuterCechCochain,
    _reduced_basis,
)

from .alternate_constituent_up_cone_matter_lifts import OUTPUT as CONE_MATTER
from .alternate_constituent_up_cone_matter_lifts import _first_representatives
from .alternate_up_yoneda_evaluation import OUTPUT as YONEDA
from .alternate_up_yoneda_evaluation import _ratio, alternate_up_yoneda_evaluation
from .mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
    mixed_schoen_constituents,
)
from .mixed_outer_yoneda import _cup_cells
from .mixed_schoen_determinant_pairing import OUTPUT as PAIRING
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction, _perturbed_projection
from .mixed_schoen_outer_transfer import (
    KOSZUL_SUBSETS,
    SUBSET_KOSZUL,
    MixedSchoenUnit,
    _transfer_map,
)
from .mixed_schoen_outer_universal_cone import _verified_payload
from .mixed_schoen_v1_pluecker_chain_map import _local_pairings
from .mixed_schoen_yukawa_trace import _complementary_minor_polynomials
from .published_constituent_overlap_transitions import _embed_polynomial

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_mixed_scalar_trace.json"


@cache
def _a_line_pairing() -> tuple[LaurentPolynomial, ...]:
    """Certify the global quotient map paired with the first A-line.

    The signed maximal-minor row annihilates the Hilbert--Burch matrix.
    The constituent extension arrows land in A, whose A--A pairing is
    zero. Hence the degree-zero map kills both A and the syzygy objects,
    commutes with the full differential, and needs no minor inversion.
    """

    first = mixed_schoen_constituents()[0]
    matrix = first.full.alignment.action.derived.extension.scheme.resolution.matrix
    minors = _complementary_minor_polynomials(1)
    if len(minors) != 3 or len(matrix) != 3 or len(matrix[0]) != 2:
        raise ValueError("the first A-line quotient resolution changed")
    for column in range(2):
        value = minors[0] * matrix[0][column]
        for row in range(1, 3):
            value += minors[row] * matrix[row][column]
        if not value.is_zero():
            raise ValueError("the A-line maximal-minor row does not kill syzygies")
    if any(term.target != 0 for term in first.extension_terms):
        raise ValueError("the first constituent extension no longer lands in A")
    result = tuple(_embed_polynomial(minor) for minor in minors)
    for pairing in _local_pairings().values():
        if any(pairing.rows[row][3] != result[row] for row in range(3)):
            raise ValueError("the global A-line orientation differs from local Pluecker data")
    return result


@cache
def _scalar_context() -> _MixedContraction:
    """Use the same determinant line on both sides of the scalar Hom."""

    determinant = MixedSchoenUnit(
        "det V1", 0, (-2, 2, 0),
        (MixedConstituentObject("det V1", 0, (-2, 2, 0)),),
    )
    context = _MixedContraction(determinant, determinant)
    generator = _reduced_basis(context.left_skeleton, context.right_skeleton, 3)
    if (
        len(generator) != 1
        or generator[0].component.koszul_summand != "k2"
        or generator[0].x_monomial != (-1, -1, -1)
        or generator[0].u_monomial != (-1, -1, -1)
        or generator[0].p_monomial != (-1, -1)
    ):
        raise ValueError("the ordered scalar residue generator changed")
    incoming, _ = _transfer_map(determinant, determinant, 2)
    if not incoming.is_zero():
        raise ValueError("the ordered scalar residue generator became a boundary")
    return context


def _contract(
    matter: SparseOuterCechCochain,
    evaluated: SparseOuterCechCochain,
    *,
    reverse: bool = False,
) -> SparseOuterCechCochain:
    """Pair a full V1-resolution cochain with an A-line cochain.

    A and syzygy inputs map to zero by the certified degree-zero quotient
    chain map, not by a truncation of an unconstructed physical pairing.
    """

    scalar_context = _scalar_context()
    components = scalar_context.components
    first = mixed_schoen_constituents()[0]
    expected_a_degree = tuple(
        left - right for left, right in zip(
            first.objects[0].line_degree, scalar_context.right.twist, strict=True
        )
    )
    pairings = _a_line_pairing()
    result: list[tuple[OuterCechBasis, Eisenstein]] = []
    if any(
        basis.component.left_index != 0
        or basis.component.right_index != 0
        or basis.component.object_degree != 0
        or basis.component.line_degree != expected_a_degree
        for basis, _ in evaluated.terms
    ):
        raise ValueError("the direct mixed trace needs the actual A-line support")
    for matter_basis, matter_coefficient in matter.terms:
        row = matter_basis.component.left_index
        if row not in range(6) or matter_basis.component.right_index != 0:
            raise ValueError("the A-line pairing needs the actual first constituent resolution")
        if (
            matter_basis.component.object_degree != first.objects[row].position
            or matter_basis.component.line_degree != first.objects[row].line_degree
        ):
            raise ValueError("the A-line pairing received an incompatible first-object grading")
        if row in (0, 4, 5):
            continue
        for evaluated_basis, evaluated_coefficient in evaluated.terms:
            left_basis, right_basis = (
                (evaluated_basis, matter_basis)
                if reverse else (matter_basis, evaluated_basis)
            )
            cup = _cup_cells(left_basis, right_basis)
            if cup is None:
                continue
            left_subset = KOSZUL_SUBSETS[left_basis.component.koszul_summand]
            right_subset = KOSZUL_SUBSETS[right_basis.component.koszul_summand]
            if set(left_subset) & set(right_subset):
                continue
            subset = tuple(sorted((*left_subset, *right_subset)))
            target = components[(0, 0, SUBSET_KOSZUL[subset])]
            cover_sign, cell = cup
            crossing = (
                left_basis.cech_degree
                * KOSZUL_DEGREES[right_basis.component.koszul_summand]
            )
            inversions = sum(first > second for first in left_subset for second in right_subset)
            sign = -1 if (crossing + inversions) % 2 else 1
            pairing = -pairings[row - 1] if reverse else pairings[row - 1]
            for exponents, scalar in pairing.terms:
                x_monomial = cast(tuple[int, int, int], tuple(
                    matter_basis.x_monomial[index]
                    + evaluated_basis.x_monomial[index]
                    + exponents[index]
                    for index in range(3)
                ))
                u_monomial = cast(tuple[int, int, int], tuple(
                    matter_basis.u_monomial[index]
                    + evaluated_basis.u_monomial[index]
                    for index in range(3)
                ))
                p_monomial = cast(tuple[int, int], tuple(
                    matter_basis.p_monomial[index]
                    + evaluated_basis.p_monomial[index]
                    + exponents[index + 3]
                    for index in range(2)
                ))
                result.append((
                    OuterCechBasis(target, x_monomial, u_monomial, p_monomial, cell),
                    matter_coefficient * evaluated_coefficient * scalar * sign * cover_sign,
                ))
    return SparseOuterCechCochain(tuple(result))


@dataclass(frozen=True, slots=True)
class MixedScalar:
    """One exact degree-three scalar cocycle and its ordered residue."""

    matter_character: tuple[int, int]
    matter_seed_index: int
    evaluated_character: tuple[int, int]
    evaluated_seed_index: int
    scalar_cochain: SparseOuterCechCochain
    residue: Eisenstein
    projection_depth: int
    reverse_residue: Eisenstein
    reverse_projection_depth: int

    def as_record(self) -> dict[str, object]:
        """Record one exact cover trace in explicit cochain conventions."""

        return {
            "first_matter_character": list(self.matter_character),
            "first_matter_seed_index": self.matter_seed_index,
            "second_matter_character": list(self.evaluated_character),
            "second_matter_seed_index": self.evaluated_seed_index,
            "scalar_cochain_term_count": len(self.scalar_cochain.terms),
            "scalar_cochain_digest": _cochain_digest((self.scalar_cochain,)),
            "ordered_cover_residue": str(self.residue),
            "projection_depth": self.projection_depth,
            "reverse_order_residue": str(self.reverse_residue),
            "reverse_projection_depth": self.reverse_projection_depth,
            "full_scalar_cycle_exact": True,
            "reverse_exchange_exact": True,
        }


def alternate_up_mixed_scalar_trace() -> tuple[MixedScalar, ...]:
    """Evaluate all four constant mixed entries in the fixed exact bases."""

    first = {item.character: item for item in _first_representatives()}
    evaluated = alternate_up_yoneda_evaluation()
    jobs = (
        (first[(1, 0)], evaluated[0]),
        (first[(1, 0)], evaluated[1]),
        (first[(0, 0)], evaluated[2]),
        (first[(0, 0)], evaluated[3]),
    )
    scalar_context = _scalar_context()
    results = []
    for matter, hom_image in jobs:
        scalar = _contract(matter.full_cochain, hom_image.full_cochain)
        if not scalar.terms or any(basis.total_degree != 3 for basis, _ in scalar.terms):
            raise ValueError("the mixed scalar contraction has no degree-three support")
        if not scalar_context.differential(scalar).is_zero():
            raise ValueError("the mixed scalar contraction is not a full cycle")
        coordinates, depth = _perturbed_projection(scalar, scalar_context, 3)
        if set(coordinates) - {0}:
            raise ValueError("the scalar residue has an unexpected reduced basis")
        reverse = _contract(
            matter.full_cochain, hom_image.full_cochain, reverse=True
        )
        if not scalar_context.differential(reverse).is_zero():
            raise ValueError("the reversed mixed contraction is not a full cycle")
        reverse_coordinates, reverse_depth = _perturbed_projection(
            reverse, scalar_context, 3
        )
        if set(reverse_coordinates) - {0} or reverse_coordinates.get(
            0, Eisenstein(0)
        ) != -coordinates.get(0, Eisenstein(0)):
            raise ValueError("the two ordered exterior contractions disagree")
        results.append(MixedScalar(
            matter.character,
            matter.seed_index,
            hom_image.character,
            hom_image.seed_index,
            scalar,
            coordinates.get(0, Eisenstein(0)),
            depth,
            reverse_coordinates.get(0, Eisenstein(0)),
            reverse_depth,
        ))
    if (
        results[0].residue.is_zero()
        or results[2].residue.is_zero()
        or results[1].residue != _ratio(evaluated[0], evaluated[1]) * results[0].residue
        or results[3].residue != _ratio(evaluated[2], evaluated[3]) * results[2].residue
    ):
        raise ValueError("the mixed scalar entries disagree with Yoneda cohomology")
    return tuple(results)


def write_alternate_up_mixed_scalar_trace(path: Path = OUTPUT) -> dict[str, object]:
    """Persist all four direct mixed cover residues without a full-matrix claim."""

    yoneda_digest, yoneda = _verified_payload(YONEDA)
    matter_digest, matter = _verified_payload(CONE_MATTER)
    pairing_digest, pairing = _verified_payload(PAIRING)
    if (
        yoneda.get("all_nonboundary_exact") is not True
        or matter.get("all_coefficientwise_cone_identities_exact") is not True
        or pairing.get("pairing", {}).get("corrected_overlap_covariance_exact")
        is not True
    ):
        raise ValueError("the mixed scalar trace prerequisites are not certified")
    entries = alternate_up_mixed_scalar_trace()
    if any(entry.residue.is_zero() for entry in entries):
        raise ValueError("a declared mixed holomorphic cover entry vanished")
    payload: dict[str, object] = {
        "schema": "alternate-up-mixed-scalar-trace-v1",
        "coefficient_field": "Q(omega)",
        "ray_character_exponents": [0, 1],
        "residue_normalization": (
            "ordered k2 Laurent generator x^(-1,-1,-1) "
            "u^(-1,-1,-1) p^(-1,-1) has trace one on the cover"
        ),
        "determinant_orientation": "signed complementary minors in F0,F0,F0,A order",
        "prerequisite_artifact_digests": {
            "nonboundary_yoneda_images": yoneda_digest,
            "same_cone_matter_lifts": matter_digest,
            "first_constituent_pluecker_pairing": pairing_digest,
        },
        "mixed_entries": [entry.as_record() for entry in entries],
        "all_four_cover_scalar_cycles_exact": True,
        "all_four_cover_residues_nonzero": True,
        "reverse_exchange_sign_exact": True,
        "yoneda_ratios_reproduced_exact": True,
        "quotient_trace_normalization_constructed": False,
        "same_cone_higgs_cocycle_constructed": False,
        "complete_holomorphic_up_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "observational_inputs_used": False,
        "next_required_object": (
            "construct the same-cone exterior Higgs class and parameter-linear "
            "F-F block, then complete the quotient-normalized 3x3 matrix"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    record = write_alternate_up_mixed_scalar_trace()
    print(f"artifact_digest: {record['artifact_digest']}")
    print(f"entry_count: {len(record['mixed_entries'])}")
