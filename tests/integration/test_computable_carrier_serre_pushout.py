"""Test exact Hilbert--Burch Serre pushout construction.

Owns:
    Pushout relation identities, support-local Fitting gates, selected
    extension-class eigenvectors, and rank-two middle-module certificates.

Depends on:
    The computable-carrier pushout experiment, exact production resolutions,
    and pytest. It does not consume observations or the published carrier.

Must not:
    Treat a base projective pushout as a descended dP9 bundle, infer stability
    or spectrum, or suppress an unresolved line-frame or quotient gate.

Phase 0:
    Exact base pushouts are tested; global dP9 descent and physical promotion
    remain unresolved.
"""

from __future__ import annotations

from onetheory.math.numbers import Rational
from research.experiments.computable_carrier.serre_pushout import tier_a_serre_pushouts


def test_tier_a_pushouts_have_exact_rank_two_relations() -> None:
    """Both Hilbert--Burch pushouts have the required exact presentation."""

    candidates = tier_a_serre_pushouts()

    assert tuple(item.scheme.name for item in candidates) == ("I3", "I6")
    assert tuple(item.relation.shape for item in candidates) == ((2, 4), (3, 5))
    assert tuple(item.middle_rank for item in candidates) == (2, 2)
    assert all(item.relation_composes_to_zero for item in candidates)
    assert tuple(item.source_shifts for item in candidates) == ((3, 3), (4, 4, 4))
    assert tuple(item.target_shifts for item in candidates) == (
        (2, 2, 2, 3),
        (3, 3, 3, 3, 3),
    )
    assert all(item.graded_relation for item in candidates)
    assert tuple(
        (
            item.base_chern.rank,
            item.base_chern.determinant_degree,
            item.base_chern.ch2_degree,
            item.base_chern.c2_degree,
        )
        for item in candidates
    ) == (
        (2, Rational(-3), Rational(3, 2), Rational(3)),
        (2, Rational(-3), Rational(-3, 2), Rational(6)),
    )
    assert all(len(item.chart_records) == 6 for item in candidates)
    assert all(
        all(record.relation_composes_to_zero for record in item.chart_records)
        for item in candidates
    )


def test_tier_a_pushouts_are_free_at_every_declared_support_point() -> None:
    """Every support point has a nonzero maximal relation minor."""

    candidates = tier_a_serre_pushouts()

    assert all(item.locally_free_at_support for item in candidates)
    assert all(
        all(unit and indices for _, unit, indices in item.local_fitting)
        for item in candidates
    )


def test_selected_extension_classes_have_exact_character_actions() -> None:
    """The selected maps are eigenclasses with order-three commuting actions."""

    candidates = tier_a_serre_pushouts()

    assert all(
        all(
            action.class_eigenvector
            and action.full_action_order_three
            and action.full_actions_commute
            for action in candidate.linearizations
        )
        for candidate in candidates
    )
