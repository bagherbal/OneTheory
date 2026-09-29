"""Reproduce the constant mixed entries in the canonical quotient order.

Owns:
    Actual four-entry traces, independent Hom-composer comparisons,
    exact exterior exchange, and basis-corruption attacks.

Depends on:
    Frozen carrier cochains, the global quotient, explicit trace frame,
    and exact Eisenstein arithmetic.

Must not:
    Treat four entries as a complete matrix or hide a relative sign
    inside a Higgs phase or a family-basis change.

Phase 0:
    Research regressions for actual partial holomorphic couplings.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis import (
    alternate_constituent_up_matter_representatives as matter_inputs,
)
from research.experiments.scientific_genesis.alternate_up_mixed_quotient_pairing import (
    OUTPUT,
    first_matter_quotient,
    mixed_quotient_entries,
    quotient_mixed_product,
    write_mixed_quotient_pairing,
)
from research.experiments.scientific_genesis.alternate_up_mixed_scalar_trace import (
    alternate_up_mixed_scalar_trace,
)
from research.experiments.scientific_genesis.alternate_up_pairing_exchange import (
    direct_ordered_scalar_residue,
)


def test_actual_four_entries_and_the_declared_quotient_trace(tmp_path: Path) -> None:
    """Recompute complete scalar cycles without filling the four absent entries."""

    saved = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert write_mixed_quotient_pairing(tmp_path / "mixed.json") == saved
    entries = mixed_quotient_entries()
    assert [(entry.row, entry.column) for entry in entries] == [(0, 1), (0, 2), (1, 0), (2, 0)]
    assert [entry.cover_residue for entry in entries] == [
        Eisenstein(-3) / 2, Eisenstein(9, 6) / 14,
        -Eisenstein(3) * OMEGA / 2, -Eisenstein(3, 9) / 14,
    ]
    assert [record["quotient_residue"] for record in saved["evaluated_entries"]] == [
        str(entry.cover_residue * Rational(1, 9)) for entry in entries
    ]
    assert all(len(entry.scalar.terms) == 2257 for entry in entries)
    assert all(entry.scalar == entry.reverse_scalar for entry in entries)
    assert all(entry.exchange_primitive.is_zero() for entry in entries)
    assert saved["first_first_entry_zero_by_B_wedge_B"] is True
    for field in (
        "second_second_entries_assigned", "complete_holomorphic_up_matrix_available",
        "physical_yukawa_matrix_available", "higgs_phase_adjusted",
        "extension_point_selected", "observational_inputs_used",
    ):
        assert saved[field] is False


def test_actual_order_comparison_with_the_independent_hom_composer() -> None:
    """Changing scalar order is verified literally, not repaired by a phase."""

    old = alternate_up_mixed_scalar_trace()
    new = mixed_quotient_entries()
    # Old entries evaluate E cup (h applied to F). The canonical entries
    # evaluate h first on the B-F wedge. Degree-one exchange contributes
    # a minus sign. The old determinant's column already used reverse order.
    for entry, old_index in zip(new, (2, 3, 0, 1), strict=True):
        assert entry.scalar == old[old_index].scalar_cochain.scale(-1)
        assert entry.cover_residue == -old[old_index].residue
        assert direct_ordered_scalar_residue(entry.scalar) == entry.cover_residue
    assert new[0].cover_residue == -old[2].residue
    assert new[2].cover_residue == old[0].reverse_residue
    assert -new[0].cover_residue * new[2].cover_residue == -Eisenstein(9) * OMEGA / 4
    assert new[1].cover_residue / new[0].cover_residue == old[3].residue / old[2].residue
    assert new[3].cover_residue / new[2].cover_residue == old[1].residue / old[0].residue


def test_undeclared_first_character_has_no_automatic_class() -> None:
    """An unavailable family direction remains unavailable."""

    with pytest.raises(ValueError, match="unique declared character class"):
        first_matter_quotient((2, 0))


@pytest.mark.parametrize("part", ("line_basis", "vector_basis", "vector_position"))
def test_mixed_product_rejects_corrupted_actual_input_grading(part: str) -> None:
    """A matching coordinate list cannot substitute for the declared resolution."""

    line = first_matter_quotient((0, 0))
    vector = matter_inputs.alternate_constituent_up_matter_representatives().classes[0].full_cochain
    target = line if part == "line_basis" else vector
    basis, value = target.terms[0]
    component = replace(
        basis.component,
        **({"object_degree": 1} if part == "vector_position" else {
            "left_index": 1 if part == "line_basis" else 100,
        }),
    )
    broken = SparseOuterCechCochain((
        (replace(basis, component=component), value), *target.terms[1:],
    ))
    with pytest.raises(ValueError, match="actual quotient line|actual even F support"):
        quotient_mixed_product(
            broken if part == "line_basis" else line,
            vector if part == "line_basis" else broken,
            line_first=True,
        )
