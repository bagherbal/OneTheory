"""Derive the up-sector rank floor from exact mixed cover residues.

Owns:
    Nonzero two-by-two minors forced by the already computed mixed blocks
    throughout the frozen alternate outer-extension family.

Depends on:
    Content-pinned mixed scalar traces, exterior-filtration support, and
    exact Eisenstein arithmetic in the declared cover basis.

Must not:
    Supply the missing second/second block, infer rank three, or identify
    cover residues with canonically normalized physical couplings.

Phase 0:
    Research-only rank obstruction and lower bound, not a Yukawa matrix.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .alternate_up_mixed_scalar_trace import OUTPUT as MIXED
from .alternate_up_yukawa_support import OUTPUT as SUPPORT
from .mixed_schoen_chain_actions import _parse_eisenstein_text
from .mixed_schoen_outer_universal_cone import _verified_payload

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_up_rank_floor.json"


def _residue(entry: dict[str, object], key: str) -> Eisenstein:
    value = entry.get(key)
    if not isinstance(value, str):
        raise ValueError(f"the mixed trace lacks {key}")
    return _parse_eisenstein_text(value)


def alternate_up_rank_floor() -> dict[str, object]:
    """Prove four nonzero mixed two-by-two minors without the F--F block."""

    mixed_digest, mixed = _verified_payload(MIXED)
    support_digest, support = _verified_payload(SUPPORT)
    entries = mixed.get("mixed_entries")
    if (
        mixed.get("schema") != "alternate-up-mixed-scalar-trace-v1"
        or mixed.get("all_four_cover_scalar_cycles_exact") is not True
        or mixed.get("all_four_cover_residues_nonzero") is not True
        or mixed.get("reverse_exchange_sign_exact") is not True
        or support.get("schema") != "alternate-up-yukawa-support-v1"
        or support.get("entry_parameter_degrees")
        != [[[], [0], [0]], [[0], [1], [1]], [[0], [1], [1]]]
        or not isinstance(entries, list)
        or len(entries) != 4
    ):
        raise ValueError("the alternate rank-floor premises changed")
    typed = cast(list[dict[str, object]], entries)
    for index, entry in enumerate(typed):
        expected_first = [1, 0] if index < 2 else [0, 0]
        expected_second = [0, 0] if index < 2 else [1, 0]
        expected_seed = 0 if index % 2 == 0 else 5
        if (
            entry.get("first_matter_character") != expected_first
            or entry.get("second_matter_character") != expected_second
            or entry.get("second_matter_seed_index") != expected_seed
            or entry.get("full_scalar_cycle_exact") is not True
            or entry.get("reverse_exchange_exact") is not True
        ):
            raise ValueError("the mixed blocks no longer share the declared bases")
        if _residue(entry, "reverse_order_residue") != -_residue(
            entry, "ordered_cover_residue"
        ):
            raise ValueError("the reversed mixed contraction changed sign")

    # Rows are (E_left,F_left_0,F_left_5); columns are
    # (E_right,F_right_0,F_right_5).  Reversing the first two traces
    # gives the F_left--E_right block in the same ordered cup convention.
    row = tuple(_residue(entry, "ordered_cover_residue") for entry in typed[2:])
    column = tuple(_residue(entry, "reverse_order_residue") for entry in typed[:2])
    minors = tuple(tuple(-left * right for right in column) for left in row)
    if any(value.is_zero() for pair in minors for value in pair):
        raise ValueError("a supposedly forced two-by-two minor vanished")
    return {
        "schema": "alternate-up-rank-floor-v1",
        "coefficient_field": "Q(omega)",
        "carrier_locus": "frozen nonsplit alternate P1 family",
        "basis_order": {
            "rows": ["E(0,0)", "F(0,0):seed0", "F(0,0):seed5"],
            "columns": ["E(1,0)", "F(1,0):seed0", "F(1,0):seed5"],
        },
        "zero_first_first_entry": True,
        "mixed_row_cover_residues": [str(value) for value in row],
        "mixed_column_reverse_cover_residues": [str(value) for value in column],
        "two_by_two_minors_rows_F_columns_F": [
            [str(value) for value in pair] for pair in minors
        ],
        "all_four_minors_nonzero_exact": True,
        "holomorphic_rank_lower_bound": 2,
        "rank_floor_valid_for_every_nonsplit_extension": True,
        "rank_three_established": False,
        "complete_holomorphic_up_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "observational_inputs_used": False,
        "prerequisite_artifact_digests": {
            "mixed_cover_traces": mixed_digest,
            "exterior_filtration_support": support_digest,
        },
        "next_required_object": (
            "derive the same-cone Higgs correction and the parameter-linear "
            "F-F block to decide the two determinant coefficients"
        ),
    }


def write_alternate_up_rank_floor(path: Path = OUTPUT) -> dict[str, object]:
    """Write the exact rank floor with pinned scientific prerequisites."""

    payload = alternate_up_rank_floor()
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    record = write_alternate_up_rank_floor()
    print(f"artifact_digest: {record['artifact_digest']}")
    print(f"holomorphic_rank_lower_bound: {record['holomorphic_rank_lower_bound']}")
