"""Check actual trace descent without assigning an unfinished matrix entry.

Owns:
    The full closed scalar generator, both deck-boundary witnesses,
    explicit volume normalization, and attacks on the finite-cover hypothesis.

Depends on:
    Exact scalar cochains, the published free quotient, and rational arithmetic.

Must not:
    Substitute fixture traces for carrier coefficients or normalize matter states.

Phase 0:
    Research trace regressions only; no Yukawa matrix is asserted.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein, Rational
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.scientific_genesis import alternate_up_quotient_trace as trace
from research.experiments.scientific_genesis.alternate_up_mixed_scalar_trace import _scalar_context
from research.experiments.scientific_genesis.alternate_up_pairing_exchange import (
    direct_ordered_scalar_residue,
)


def test_trace_uses_the_full_closed_generator_not_the_raw_seed() -> None:
    """The top Koszul monomial needs genuine lower-subset corrections."""

    generator = trace.scalar_trace_generator()
    context = _scalar_context()
    assert len(generator.harmonic_seed.terms) == 1
    assert len(generator.full_cochain.terms) == 55
    assert generator.inclusion_depth == 3
    assert not context.differential(generator.harmonic_seed).is_zero()
    with pytest.raises(ValueError, match="cannot trace a nonclosed scalar"):
        direct_ordered_scalar_residue(generator.harmonic_seed)
    assert context.differential(generator.full_cochain).is_zero()
    assert direct_ordered_scalar_residue(generator.full_cochain) == Eisenstein(1)


def test_both_actual_deck_actions_preserve_the_class_with_full_primitives() -> None:
    """P is fixed modulo a verified boundary; T is strictly fixed."""

    context = _scalar_context()
    full = trace.scalar_trace_generator().full_cochain
    witnesses = trace.scalar_trace_deck_witnesses()
    assert [witness.generator for witness in witnesses] == ["P", "T"]
    assert [len(witness.difference.terms) for witness in witnesses] == [30, 0]
    assert [len(witness.primitive.terms) for witness in witnesses] == [16, 0]
    assert [witness.homotopy_depth for witness in witnesses] == [2, 0]
    for witness in witnesses:
        assert context.differential(witness.image).is_zero()
        assert witness.difference == witness.image + full.scale(-1)
        assert context.differential(witness.primitive) == witness.difference
        assert direct_ordered_scalar_residue(witness.image) == Eisenstein(1)
        if not witness.difference.is_zero():
            assert context.differential(witness.primitive.scale(-1)) != witness.difference


def test_saved_trace_frame_matches_fresh_exact_checks(tmp_path: Path) -> None:
    """The ninefold factor is attached to a stated form, not silently inserted."""

    saved = json.loads(trace.OUTPUT.read_text(encoding="utf-8"))
    fresh = trace.write_alternate_up_quotient_trace(tmp_path / "trace.json")
    assert fresh == saved
    digest = fresh.pop("artifact_digest")
    assert digest == _canonical_digest(fresh)
    assert fresh["cover_to_quotient_trace_factor"] == "1/9"
    assert fresh["quotient_trace_of_pullback_generator_class"] == "1/9"
    assert fresh["volume_form_convention"] == {
        "cover": "dual to the fixed cover H3(O) generator with trace one",
        "quotient": "the unique form whose pullback is that cover form",
        "relation": "pi*Omega_quotient=Omega_cover",
    }
    assert fresh["scalar_class_descent_certified"] is True
    assert fresh["quotient_trace_normalization_constructed"] is True
    for field in (
        "physical_null_coefficient_assigned", "complete_holomorphic_up_matrix_available",
        "physical_yukawa_matrix_available", "extension_point_selected", "observational_inputs_used",
    ):
        assert fresh[field] is False


@pytest.mark.parametrize("degree", (1, 3, 9))
@pytest.mark.parametrize("value", (Rational(5, 7), Eisenstein(Rational(2, 5), Rational(-3, 7))))
def test_split_finite_etale_algebra_trace_of_pullback(
    degree: int, value: Rational | Eisenstein,
) -> None:
    """The local algebra trace counts every sheet, over either exact field."""

    # These split algebras test Tr_pi(pi*alpha)=degree*alpha. They are
    # mathematical fixtures, not actual cover classes or Yukawa entries.
    multiplication = Matrix.identity(degree, scalar_type=type(value)).scale(value)
    algebra_trace = sum((multiplication[i][i] for i in range(degree)), type(value)(0))
    assert algebra_trace == value * degree
    assert algebra_trace * Rational(1, degree) == value


@pytest.mark.parametrize("mutation", ("not_free", "wrong_order", "wrong_degree", "wrong_group"))
def test_trace_rejects_an_incompatible_cover_hypothesis(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, mutation: str,
) -> None:
    """A declared normalization factor cannot survive a changed quotient."""

    geometry = trace.schoen_geometry()
    quotient = geometry.quotient
    if mutation == "not_free":
        quotient = replace(quotient, acts_freely=False)
    elif mutation == "wrong_order":
        quotient = replace(quotient, order=3)
    elif mutation == "wrong_degree":
        quotient = replace(quotient, space=replace(quotient.space, cover_degree=3))
    else:
        quotient = replace(quotient, group_name="different group")
    monkeypatch.setattr(trace, "schoen_geometry", lambda: replace(geometry, quotient=quotient))
    output = tmp_path / "trace.json"
    with pytest.raises(ValueError, match="declared free Schoen quotient"):
        trace.write_alternate_up_quotient_trace(output)
    assert not output.exists()
