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

from onetheory.core.errors import MissingPhysicalInput
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
    monkeypatch.setattr(
        comparison_module, "determinant_descent_audit",
        lambda: {"equivariantly_trivial_determinant_certified": True},
    )
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


def test_comparison_projects_the_closed_scalar_not_its_raw_primitive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A non-pure raw trace is projected only after its boundary cancels."""

    basis = _FullBasis(
        (), (0, 0, 0, 0),
        ((0, 0, 0), (0, 0), (0, 0, 0), (0, 0)),
        ((0,), (0,), (0,), (0,)),
    )
    raw = _FullCochain(((basis, Eisenstein(3)),))
    primitive = _FullCochain(((basis, Eisenstein(1)),))
    zero = _FullCochain()
    monkeypatch.setattr(
        comparison_module, "determinant_descent_audit",
        lambda: {"equivariantly_trivial_determinant_certified": True},
    )
    trace = SimpleNamespace(
        scalar=raw,
        scalar_residual=primitive,
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
        lambda _index: SimpleNamespace(
            canonical_action=zero, canonical_correction=zero
        ),
    )
    monkeypatch.setattr(
        comparison_module, "diagonal_line_product", lambda *_args: zero
    )
    monkeypatch.setattr(
        comparison_module, "scalar_full_differential", lambda _cochain: zero
    )
    monkeypatch.setattr(
        comparison_module, "scalar_primitive", lambda _cochain: (primitive, 1)
    )
    monkeypatch.setattr(
        comparison_module, "constituent_determinant_character",
        lambda factor: (1, 0) if factor == 1 else (1, 1),
    )
    projected_inputs: list[_FullCochain] = []

    def project(source: _FullCochain, _character: object, _frame: object) -> _FullCochain:
        projected_inputs.append(source)
        return source.scale(3)

    monkeypatch.setattr(comparison_module, "project_line_character", project)
    monkeypatch.setattr(comparison_module, "line_has_character", lambda *_args: True)
    monkeypatch.setattr(
        comparison_module, "scalar_residue", lambda _cochain: (Eisenstein(7), 1)
    )
    stages: list[str] = []

    result = comparison_module.reverse_central_comparison(
        0, lambda stage, _record: stages.append(stage)
    )

    assert projected_inputs == [_FullCochain(((basis, Eisenstein(2)),))]
    assert stages == [
        "direct_trace", "comparison", "primitive", "raw_complete",
        "strict_complete", "result",
    ]
    assert result["residue"] == "7"
    assert result["exact"] is True


def test_physical_comparison_stops_before_large_trace_on_determinant_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden_trace(_index: int) -> None:
        raise AssertionError("an invalid physical trace must not begin")

    monkeypatch.setattr(comparison_module, "reverse_central_direct_trace", forbidden_trace)

    with pytest.raises(MissingPhysicalInput, match="equivariantly trivial determinant"):
        comparison_module.reverse_central_comparison(0)
