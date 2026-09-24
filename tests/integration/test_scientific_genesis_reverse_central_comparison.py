"""Guard fail-closed scalar comparison for the reverse central entry.

Owns:
    Fast boundary and non-cocycle rejection checks for the research runner.

Depends on:
    The reverse comparison experiment and exact sparse scalar cochains.

Must not:
    Interpret synthetic cochains as a physical Yukawa certificate.

Phase 0:
    Research-runner gate tests; the physical coefficient remains unresolved.
"""

from types import SimpleNamespace

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.scientific_genesis import (
    mixed_schoen_reverse_central_comparison as comparison_module,
)
from research.experiments.scientific_genesis.diagonal_schoen_lines import (
    _FullBasis,
    _FullCochain,
)


@pytest.mark.parametrize("parameter_index", (-1, 6))
def test_comparison_rejects_out_of_basis_parameters(parameter_index: int) -> None:
    with pytest.raises(ValueError, match="parameter index is unavailable"):
        comparison_module.reverse_central_comparison(parameter_index)


def test_comparison_rejects_nonclosed_scalar_before_residue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    basis = _FullBasis(
        (), (0, 0, 0, 0),
        ((0, 0, 0), (0, 0), (0, 0, 0), (0, 0)),
        ((0,), (0,), (0,), (0,)),
    )
    nonzero = _FullCochain(((basis, Eisenstein(1)),))
    zero = _FullCochain()
    trace = SimpleNamespace(
        scalar_residual=nonzero,
        as_record=lambda: {"central_yukawa_coefficient_available": False},
    )
    monkeypatch.setattr(
        comparison_module, "reverse_central_direct_trace", lambda _index: trace
    )
    monkeypatch.setattr(
        comparison_module, "physical_v1_pluecker_pairing",
        lambda: SimpleNamespace(equivariant_pairing=zero),
    )
    monkeypatch.setattr(
        comparison_module, "reverse_higgs_lift_coefficient",
        lambda _index: SimpleNamespace(canonical_action=zero),
    )
    monkeypatch.setattr(
        comparison_module, "diagonal_line_product", lambda *_args: zero
    )
    monkeypatch.setattr(
        comparison_module, "scalar_full_differential", lambda _cochain: nonzero
    )
    stages: list[str] = []

    with pytest.raises(ValueError, match="comparison is not a cycle"):
        comparison_module.reverse_central_comparison(
            0, lambda stage, _record: stages.append(stage)
        )

    assert stages == ["direct_trace", "comparison"]
