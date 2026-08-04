"""Test exact Tier A constituent chart data without promoting it.

Owns:
    Ambient-resolution attachment, invariant-ray dimensions, transition
    cocycle identities, pairwise inverses, and determinant-one local checks.

Depends on:
    The computable-carrier constituent experiment, exact I3/I6 production
    schemes, Laurent localization, and pytest.

Must not:
    Call formal chart cocycles Serre extensions, claim a Schoen cover, or reuse
    the published carrier as the new bundle.

Phase 0:
    Exact local candidate data are tested; Serre identification remains gated.
"""

from __future__ import annotations

from research.experiments.computable_carrier.constituents import tier_a_constituents


def test_tier_a_constituents_carry_complexes_and_unique_rays() -> None:
    """I3/I6 candidates retain their ambient exact resolution and ray size."""

    candidates = tier_a_constituents()

    assert tuple(candidate.scheme.name for candidate in candidates) == ("I3", "I6")
    assert tuple(candidate.invariant_ray_dimension for candidate in candidates) == (2, 5)
    assert tuple(len(candidate.invariant_ray_coordinates) for candidate in candidates) == (2, 5)
    assert all(
        candidate.scheme.resolution.polynomial_complex.squared_zero
        for candidate in candidates
    )
    assert all(
        candidate.as_record()["resolution"]["scheme_resolution_certified"]
        for candidate in candidates
    )


def test_tier_a_transition_candidates_verify_exact_local_identities() -> None:
    """Every generated local matrix satisfies the declared exact identities."""

    candidates = tier_a_constituents()

    assert all(candidate.cocycle.verifies_cocycle() for candidate in candidates)
    assert all(candidate.pairwise_inverse for candidate in candidates)
    assert all(candidate.determinant_one for candidate in candidates)
    assert all(
        candidate.extension_identification_status
        == "formal chart cocycle only; Serre identification pending"
        for candidate in candidates
    )
