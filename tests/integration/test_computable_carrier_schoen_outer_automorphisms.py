"""Test exact Schoen constituent automorphisms and outer-Ext orbit actions.

Owns:
    A chain-level prototype regression for invariant endomorphism algebra,
    induced outer Ext-one actions, and canonical projective normal forms.

Depends on:
    The research-only sparse Schoen Hom and automorphism calculations.

Must not:
    Promote the prototype to a rank-four bundle, choose a projective point,
    infer stability, or treat one pair as an exhaustive action screen.

Phase 0:
    One positive-dimensional invariant pair has an exact automorphism and
    projective-orbit certificate; the exhaustive action screen remains open.
"""

from functools import cache

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_sparse_outer import (
    sparse_outer_hom,
)
from research.experiments.computable_carrier.schoen_sparse_outer_actions import (
    sparse_invariant_cohomology_dimension,
    sparse_outer_invariant_audit,
    sparse_outer_invariant_cocycles,
)
from research.experiments.computable_carrier.schoen_sparse_outer_automorphisms import (
    SparseOuterAutomorphismActionAudit,
    SparseOuterCoverScalarActionAudit,
    SparseOuterOrbitClassification,
    canonical_square_zero_orbit_representative,
    classify_sparse_outer_automorphism_orbits,
    classify_sparse_square_zero_orbits,
    sparse_constituent_endomorphism_algebra,
    sparse_outer_automorphism_action,
    sparse_outer_cover_scalar_action,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_full import (
    _clear_worker_caches,
    declared_schoen_outer_pairs,
)


@cache
def _prototype() -> tuple[
    SparseOuterAutomorphismActionAudit,
    SparseOuterOrbitClassification,
    SparseOuterCoverScalarActionAudit,
]:
    """Return candidate 3's first exact positive-dimensional pair action."""

    _, candidate, left_ray, right_ray = declared_schoen_outer_pairs()[72]
    try:
        outer = sparse_outer_hom(
            left_ray,
            right_ray,
            candidate.left_factor,
            candidate.left_twist,
            candidate.right_factor,
            candidate.right_twist,
        )
        invariant = sparse_outer_invariant_audit(outer, 36)
        cocycles = sparse_outer_invariant_cocycles(invariant)
        left = sparse_constituent_endomorphism_algebra(
            left_ray,
            candidate.left_factor,
            candidate.left_twist,
        )
        right = sparse_constituent_endomorphism_algebra(
            right_ray,
            candidate.right_factor,
            candidate.right_twist,
        )
        action = sparse_outer_automorphism_action(cocycles, left, right)
        cover_action = sparse_outer_cover_scalar_action(
            outer,
            cocycles.cover_representatives,
            left,
            right,
        )
        return action, classify_sparse_outer_automorphism_orbits(action), cover_action
    finally:
        _clear_worker_caches()


def test_prototype_automorphism_algebras_and_projective_orbits_are_exact() -> None:
    """Nilpotent automorphisms act trivially and leave exact projective orbits."""

    action, orbits, cover_action = _prototype()
    left = action.left_algebra
    right = action.right_algebra

    assert sparse_invariant_cohomology_dimension(left.invariant, 0) == 4
    assert left.cocycles.representatives.domain.dimension == 4
    assert left.identity_coordinates == (
        Eisenstein(0),
        Eisenstein(0),
        Eisenstein(0),
        Eisenstein(1),
    )
    assert left.unit_polynomial == left.unit_polynomial.monomial(
        (0, 0, 0, 4),
        scalar_type=Eisenstein,
    )
    assert left.ordinary_chain_maps
    assert left.associative
    assert left.identity_exact
    assert left.exact

    assert sparse_invariant_cohomology_dimension(right.invariant, 0) == 1
    assert right.identity_coordinates == (Eisenstein(1),)
    assert right.unit_polynomial == right.unit_polynomial.monomial(
        (1,),
        scalar_type=Eisenstein,
    )
    assert right.exact

    assert action.outer.representatives.domain.dimension == 4
    assert all(map_.is_zero() for map_ in action.left_actions[:3])
    assert action.left_actions[3].rank() == 4
    assert action.right_actions[0].rank() == 4
    assert action.module_laws_exact
    assert action.actions_commute
    assert action.exact

    assert orbits.left_character == (
        Eisenstein(0),
        Eisenstein(0),
        Eisenstein(0),
        Eisenstein(1),
    )
    assert orbits.right_character == (Eisenstein(1),)
    assert orbits.scalar_actions
    assert orbits.unit_characters_exact
    assert orbits.exact
    assert cover_action.left_character == orbits.left_character
    assert cover_action.right_character == orbits.right_character
    assert cover_action.left_cover_equalities
    assert cover_action.right_cover_equalities
    assert cover_action.unit_characters_exact
    assert cover_action.exact
    record = orbits.as_record()
    assert record["nonzero_orbit_space"] == "P^3(Q(omega))"
    assert len(record["canonical_normal_form_charts"]) == 4
    assert record["outer_extension_constructed"] is False


def test_square_zero_normal_form_is_constant_on_exact_unit_orbits() -> None:
    """Scalar-unipotent transforms reduce to one deterministic representative."""

    _, candidate, left_ray, right_ray = declared_schoen_outer_pairs()[216]
    try:
        outer = sparse_outer_hom(
            left_ray,
            right_ray,
            candidate.left_factor,
            candidate.left_twist,
            candidate.right_factor,
            candidate.right_twist,
        )
        invariant = sparse_outer_invariant_audit(outer, 342)
        cocycles = sparse_outer_invariant_cocycles(invariant)
        left = sparse_constituent_endomorphism_algebra(
            left_ray,
            candidate.left_factor,
            candidate.left_twist,
        )
        right = sparse_constituent_endomorphism_algebra(
            right_ray,
            candidate.right_factor,
            candidate.right_twist,
        )
        action = sparse_outer_automorphism_action(cocycles, left, right)
        classification = classify_sparse_square_zero_orbits(action)
        coordinates = tuple(Eisenstein(index + 1) for index in range(38))
        radical_image = tuple(
            sum(
                (
                    coefficient * coordinates[column]
                    for column, coefficient in row
                ),
                Eisenstein(0),
            )
            for row in classification.radical_actions[0].rows
        )
        transformed = tuple(
            Eisenstein(2) * (value + Eisenstein(3) * image)
            for value, image in zip(coordinates, radical_image, strict=True)
        )

        assert classification.unit_characters_exact
        assert classification.radical_square_zero
        assert [map_.rank() for map_ in classification.radical_actions] == [2, 2, 2]
        assert classification.exact
        assert canonical_square_zero_orbit_representative(
            classification,
            coordinates,
        ) == canonical_square_zero_orbit_representative(
            classification,
            transformed,
        )
    finally:
        _clear_worker_caches()
