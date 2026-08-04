"""Test local Serre pushouts and their exact freeness boundary.

Owns:
    Local syzygy identities, pushout presentations, Fitting-ideal checks, and
    the unit-versus-nilpotent I6 extension-class distinction.

Depends on:
    The computable-carrier local Serre experiment and exact polynomial ideals.

Must not:
    Call local freeness a global bundle construction, infer chart transitions,
    or claim equivariant descent or a global Serre cocycle.

Phase 0:
    Local algebra is certified; global patching and linearization remain open.
"""

from __future__ import annotations

from research.experiments.computable_carrier.serre_local import (
    local_serre_model,
    tier_a_local_serre_models,
)


def test_tier_a_unit_local_pushouts_are_exactly_free() -> None:
    """The unit classes give free local middle presentations for I3/I6."""

    models = tier_a_local_serre_models()

    assert tuple(model.scheme for model in models) == ("I3", "I6")
    assert tuple(model.multiplicity for model in models) == (1, 2)
    assert all(
        model.relation_composes_to_zero
        and model.locally_free
        and model.fitting_ideal.generators[-1].terms[0][0] == (0, 0)
        for model in models
    )


def test_i6_nilpotent_class_fails_the_local_fitting_gate() -> None:
    """The nilpotent local direction is excluded by the exact Fitting ideal."""

    model = local_serre_model("I6", "nilpotent")

    assert model.relation_composes_to_zero
    assert not model.locally_free
    assert all(
        term[0] != (0, 0)
        for generator in model.fitting_ideal.generators
        for term in generator.terms
    )
