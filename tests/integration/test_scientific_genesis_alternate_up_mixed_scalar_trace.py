"""Reproduce exact alternate mixed-family cover residues and their scope."""

from __future__ import annotations

import json

from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_up_mixed_scalar_trace import (
    OUTPUT,
    alternate_up_mixed_scalar_trace,
)
from research.experiments.scientific_genesis.mixed_schoen_v1_pluecker_chain_map import (
    _overlap_quotients,
)


def test_mixed_pluecker_entries_need_no_hypersurface_correction() -> None:
    """All actual F0--A overlap corrections vanish exactly."""

    quotients = _overlap_quotients()
    assert quotients
    for _source, _target, quotient in quotients:
        assert quotient.shape == (4, 4)
        assert all(
            quotient.rows[row][3].is_zero()
            and quotient.rows[3][row].is_zero()
            for row in range(4)
        )


def test_four_exact_mixed_cover_residues() -> None:
    """Recompute scalar cycles, reverse exchange, and saved exact traces."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert payload["schema"] == "alternate-up-mixed-scalar-trace-v1"
    assert payload["all_four_cover_scalar_cycles_exact"] is True
    assert payload["all_four_cover_residues_nonzero"] is True
    assert payload["reverse_exchange_sign_exact"] is True
    assert payload["yoneda_ratios_reproduced_exact"] is True
    assert payload["quotient_trace_normalization_constructed"] is False
    assert payload["same_cone_higgs_cocycle_constructed"] is False
    assert payload["complete_holomorphic_up_matrix_available"] is False
    assert payload["physical_yukawa_matrix_available"] is False
    entries = alternate_up_mixed_scalar_trace()
    assert [entry.as_record() for entry in entries] == payload["mixed_entries"]
    assert [entry.residue for entry in entries] == [
        Eisenstein(3) * OMEGA / 2,
        Eisenstein(3, 9) / 14,
        Eisenstein(3) / 2,
        Eisenstein(-9, -6) / 14,
    ]
    assert all(entry.reverse_residue == -entry.residue for entry in entries)
    assert all(len(entry.scalar_cochain.terms) == 2257 for entry in entries)
