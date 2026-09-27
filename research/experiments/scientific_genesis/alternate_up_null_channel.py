"""Isolate the determinant-sensitive null channels of the alternate up sector.

Owns:
    Exact mixed-block null combinations, full Yoneda-boundary primitives,
    and the symbolic reduction of the rank-three test to two coefficients.

Depends on:
    Strict alternate Yoneda cochains, certified mixed cover residues,
    the synchronized contraction, and exact polynomial algebra.

Must not:
    Assign the unknown null-to-null F--F coupling, infer rank three,
    or identify unnormalized cover data with physical Yukawas.

Phase 0:
    Research-only homotopies for the next same-cone calculation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, polynomial_determinant
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)

from .alternate_up_rank_floor import OUTPUT as RANK_FLOOR
from .alternate_up_yoneda_evaluation import OUTPUT as YONEDA
from .alternate_up_yoneda_evaluation import (
    _ratio,
    alternate_up_yoneda_evaluation,
)
from .mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
    mixed_schoen_constituents,
)
from .mixed_schoen_chain_actions import _parse_eisenstein_text
from .mixed_schoen_common_dga import exact_mixed_primitive
from .mixed_schoen_matter_representatives import _cochain_digest
from .mixed_schoen_outer_actions import _MixedContraction
from .mixed_schoen_outer_transfer import MixedSchoenUnit, mixed_transferred_outer_hom
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_null_channel.json"


@dataclass(frozen=True, slots=True)
class NullYonedaChannel:
    """One exact null matter combination and its Yoneda homotopy."""

    matter_character: tuple[int, int]
    evaluated_character: tuple[int, int]
    seed5_over_seed0: Eisenstein
    null_evaluation: SparseOuterCechCochain
    primitive: SparseOuterCechCochain
    projection_depth: int
    inclusion_depth: int
    homotopy_depth: int

    def as_record(self) -> dict[str, object]:
        """Return the checked full-cochain boundary, not an F--F coupling."""

        return {
            "matter_character": list(self.matter_character),
            "evaluated_character": list(self.evaluated_character),
            "null_matter_combination": "seed5 - ratio * seed0",
            "seed5_over_seed0": str(self.seed5_over_seed0),
            "null_evaluation_term_count": len(self.null_evaluation.terms),
            "null_evaluation_digest": _cochain_digest((self.null_evaluation,)),
            "primitive_term_count": len(self.primitive.terms),
            "primitive_digest": _cochain_digest((self.primitive,)),
            "primitive_projection_depth": self.projection_depth,
            "primitive_inclusion_depth": self.inclusion_depth,
            "primitive_homotopy_depth": self.homotopy_depth,
            "full_yoneda_boundary_identity_exact": True,
        }


def _formal_determinant_identity(
    row: tuple[Eisenstein, Eisenstein],
    column: tuple[Eisenstein, Eisenstein],
    left_null: tuple[Eisenstein, Eisenstein],
    right_null: tuple[Eisenstein, Eisenstein],
) -> bool:
    """Check the determinant identity over four *formal* F--F entries."""

    variables = tuple(
        Polynomial.monomial(
            tuple(int(position == index) for position in range(4)),
            scalar_type=Eisenstein,
        )
        for index in range(4)
    )
    zero = Polynomial.zero(4, scalar_type=Eisenstein)
    constants = tuple(
        Polynomial.constant(value, 4, scalar_type=Eisenstein)
        for value in (*row, *column)
    )
    determinant = polynomial_determinant((
        (zero, constants[0], constants[1]),
        (constants[2], variables[0], variables[1]),
        (constants[3], variables[2], variables[3]),
    ))
    projected = Polynomial.zero(4, scalar_type=Eisenstein)
    for left_index in range(2):
        for right_index in range(2):
            projected += variables[2 * left_index + right_index].scale(
                -row[0] * column[0] * left_null[left_index] * right_null[right_index]
            )
    return determinant == projected


@cache
def alternate_up_null_channels() -> tuple[NullYonedaChannel, NullYonedaChannel]:
    """Compute exact primitives for both determinant-sensitive F directions."""

    _, rank_floor = _verified_payload(RANK_FLOOR)
    _, yoneda = _verified_payload(YONEDA)
    if (
        rank_floor.get("schema") != "alternate-up-rank-floor-v1"
        or rank_floor.get("holomorphic_rank_lower_bound") != 2
        or rank_floor.get("rank_three_established") is not False
        or yoneda.get("schema") != "alternate-up-yoneda-evaluation-v1"
        or yoneda.get("all_nonboundary_exact") is not True
    ):
        raise ValueError("the alternate null-channel premises changed")
    row_values = rank_floor["mixed_row_cover_residues"]
    column_values = rank_floor["mixed_column_reverse_cover_residues"]
    if not isinstance(row_values, list) or not isinstance(column_values, list):
        raise ValueError("the mixed cover blocks are unavailable")
    row = tuple(_parse_eisenstein_text(value) for value in row_values)
    column = tuple(_parse_eisenstein_text(value) for value in column_values)
    if len(row) != 2 or len(column) != 2 or row[0].is_zero() or column[0].is_zero():
        raise ValueError("the mixed blocks lack nonzero reference pivots")
    left_ratio, right_ratio = column[1] / column[0], row[1] / row[0]
    left_null = (-left_ratio, Eisenstein(1))
    right_null = (-right_ratio, Eisenstein(1))
    if (
        column[0] * left_null[0] + column[1] * left_null[1]
        != Eisenstein(0)
        or row[0] * right_null[0] + row[1] * right_null[1]
        != Eisenstein(0)
        or not _formal_determinant_identity(row, column, left_null, right_null)
    ):
        raise ValueError("the null-channel determinant reduction failed")

    evaluations = alternate_up_yoneda_evaluation()
    first = mixed_schoen_constituents()[0]
    determinant = MixedSchoenUnit(
        "det V1", 0, (-2, 2, 0),
        (MixedConstituentObject("det V1", 0, (-2, 2, 0)),),
    )
    context = _MixedContraction(first, determinant)
    transfer = mixed_transferred_outer_hom(first, determinant)
    channels = []
    for pair, expected_character, expected_evaluation, expected_ratio in (
        (evaluations[:2], (0, 0), (2, 0), left_ratio),
        (evaluations[2:], (1, 0), (0, 0), right_ratio),
    ):
        reference, candidate = pair
        ratio = _ratio(reference, candidate)
        if (
            reference.character != candidate.character
            or reference.character != expected_character
            or ratio != expected_ratio
        ):
            raise ValueError("the null direction differs from the Yoneda ratio")
        null = candidate.full_cochain + reference.full_cochain.scale(-ratio)
        if not null.terms or not context.differential(null).is_zero():
            raise ValueError("the null Yoneda combination is not a full cycle")
        solution = exact_mixed_primitive(null, context, transfer, 2)
        if not solution.exact or context.differential(solution.primitive) != null:
            raise ValueError("the null Yoneda combination has no exact primitive")
        channels.append(NullYonedaChannel(
            expected_character,
            expected_evaluation,
            ratio,
            null,
            solution.primitive,
            solution.projection_depth,
            solution.inclusion_depth,
            solution.homotopy_depth,
        ))
    return channels[0], channels[1]


def write_alternate_up_null_channels(path: Path = OUTPUT) -> dict[str, object]:
    """Persist two exact homotopies and a formal determinant compression."""

    rank_digest, rank_floor = _verified_payload(RANK_FLOOR)
    yoneda_digest, _ = _verified_payload(YONEDA)
    channels = alternate_up_null_channels()
    payload: dict[str, object] = {
        "schema": "alternate-up-null-channel-v1",
        "coefficient_field": "Q(omega)",
        "carrier_locus": "frozen nonsplit alternate P1 family",
        "declared_cover_orientation": rank_floor["basis_order"],
        "null_channels": [channel.as_record() for channel in channels],
        "determinant_formula": (
            "det Y(a) = -B0*C0 * L^T*D(a)*R; "
            "L=(-C1/C0,1), R=(-B1/B0,1)"
        ),
        "determinant_prefactor": str(
            -_parse_eisenstein_text(rank_floor["mixed_row_cover_residues"][0])
            * _parse_eisenstein_text(rank_floor["mixed_column_reverse_cover_residues"][0])
        ),
        "formal_four_entry_identity_exact": True,
        "determinant_sensitive_unknown_coefficients": 2,
        "null_to_null_coefficients_computed": False,
        "rank_three_established": False,
        "complete_holomorphic_up_matrix_available": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "rank_floor": rank_digest,
            "strict_yoneda_evaluations": yoneda_digest,
        },
        "next_required_object": (
            "compute the two same-cone extension-linear null-to-null "
            "F-F couplings using the certified Yoneda primitives"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    record = write_alternate_up_null_channels()
    print(f"artifact_digest: {record['artifact_digest']}")
    print(f"null_channels: {len(record['null_channels'])}")
