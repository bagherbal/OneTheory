"""Guard the exact reverse central direct-trace research path.

Owns:
    Input-boundary and linear contraction-order checks for the unresolved trace.

Depends on:
    The research-only reverse central matter-leg experiment.

Must not:
    Claim a computed Yukawa value from a partial or nonclosed trace.

Phase 0:
    Fast regressions for fail-closed parameter selection and bounded-memory order.
"""

from types import SimpleNamespace

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.scientific_genesis import (
    mixed_schoen_reverse_central_matter_leg as reverse_module,
)
from research.experiments.scientific_genesis.diagonal_schoen_lines import (
    _FullBasis,
    _FullCochain,
)
from research.experiments.scientific_genesis.mixed_schoen_reverse_central_matter_leg import (
    reverse_central_direct_trace,
)


@pytest.mark.parametrize("parameter_index", (-1, 6))
def test_direct_trace_rejects_unavailable_parameters(parameter_index: int) -> None:
    """No source reconstruction starts for an out-of-basis parameter."""

    with pytest.raises(ValueError, match="parameter index is unavailable"):
        reverse_central_direct_trace(parameter_index)


def test_direct_trace_contracts_each_order_before_scalar_addition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The two ordered products need not coexist as one large tensor."""

    basis = _FullBasis(
        (), (0, 0, 0, 0),
        ((0, 0, 0), (0, 0), (0, 0, 0), (0, 0)),
        ((0,), (0,), (0,), (0,)),
    )
    calls: list[tuple[str, object]] = []
    first = SimpleNamespace(terms=(1, 2))
    second = SimpleNamespace(terms=(3,))
    higgs = object()

    monkeypatch.setattr(
        reverse_module, "_physical_lifts",
        lambda _index: ("b0", "row_v1", "column_v1", "row_v2", "column_v2"),
    )
    monkeypatch.setattr(
        reverse_module, "chain_diagonal_objects",
        lambda: (SimpleNamespace(first_index=1, second_index=1),),
    )
    monkeypatch.setattr(reverse_module, "_pairing_terms", lambda *_indices: (1,))
    monkeypatch.setattr(
        reverse_module, "load_certified_higgs_representative", lambda: higgs
    )

    def tensor(left: str, right: str, _pairs: object) -> SimpleNamespace:
        calls.append(("tensor", (left, right)))
        return first if left == "row_v1" else second

    def contract(raw: SimpleNamespace, selected_higgs: object) -> _FullCochain:
        assert selected_higgs is higgs
        calls.append(("contract", raw))
        coefficient = 1 if raw is first else 2
        return _FullCochain(((basis, Eisenstein(coefficient)),))

    monkeypatch.setattr(reverse_module, "external_lifted_matter_tensor", tensor)
    monkeypatch.setattr(reverse_module, "contract_with_strict_higgs", contract)
    monkeypatch.setattr(
        reverse_module, "scalar_full_differential", lambda _cochain: _FullCochain()
    )

    result = reverse_central_direct_trace(0)

    assert calls == [
        ("tensor", ("row_v1", "column_v2")),
        ("contract", first),
        ("tensor", ("column_v1", "row_v2")),
        ("contract", second),
    ]
    assert result.ordered_matter_terms == 3
    assert result.scalar.terms == ((basis, Eisenstein(3)),)
    assert result.scalar_residual.is_zero()
    assert result.as_record()["central_yukawa_coefficient_available"] is False
