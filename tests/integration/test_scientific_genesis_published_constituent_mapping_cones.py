"""Test exact Čech mapping-cone inputs for W1 and W2.

Owns:
    Sparse overlap representatives, maximal-minor identification, Čech and
    Hilbert--Burch closure, chain-level deck invariance, and artifact digest.

Depends on:
    Source-aligned constituent actions and exact dP9 Serre Čech lifts.

Must not:
    Treat a derived cone certificate as local transition matrices, reprove
    local freeness, or claim the outer SU(4) extension is available.

Phase 0:
    Constituent derived-cone regression tests only.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_constituent_mapping_cones import (
    OUTPUT,
    published_constituent_mapping_cones,
)


def test_invariant_cocycles_are_maximal_minor_tuples() -> None:
    """The sparse W1/W2 overlap maps equal their certified ideal generators."""

    cones = published_constituent_mapping_cones()

    for cone in cones:
        assert cone.cocycle.generator_polynomials == (
            cone.action.derived.extension.scheme.ideal_generators
        )
    assert tuple(len(cone.cocycle.terms) for cone in cones) == (3, 4)


def test_constituent_overlap_terms_use_the_canonical_o_minus_two_class() -> None:
    """Every term is a base minor divided by both homogeneous fiber coordinates."""

    for cone in published_constituent_mapping_cones():
        assert all(
            term.fiber_monomial == (-1, -1)
            for term in cone.cocycle.terms
        )


def test_hilbert_burch_and_cech_differentials_close_exactly() -> None:
    """Both directions annihilate each constituent hypercocycle."""

    for cone in published_constituent_mapping_cones():
        assert cone.cocycle.cech_closed
        assert cone.cocycle.horizontal_closed
        assert all(
            residue.is_zero() for residue in cone.cocycle.horizontal_residues
        )
        assert cone.cocycle.total_closed


def test_constituent_derived_cones_are_square_zero_and_chain_fixed() -> None:
    """The exact block differential and both deck generators preserve each cone input."""

    cones = published_constituent_mapping_cones()

    assert all(cone.cocycle.derived_cone_squared_zero for cone in cones)
    assert all(cone.chain_fixed for cone in cones)
    assert all(cone.exact for cone in cones)


def test_constituent_mapping_cone_artifact_is_content_addressed() -> None:
    """The frozen cone record equals a fresh exact Čech reconstruction."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    fresh = {
        "schema": "published-constituent-mapping-cones-v1",
        "constituents": [
            result.as_record() for result in published_constituent_mapping_cones()
        ],
        "all_derived_cones_exact": True,
        "schoen_outer_extension_reconstructed": False,
        "next_required_object": (
            "synchronized Schoen Cech-Koszul total complexes for the two "
            "derived constituent cones and their outer RHom"
        ),
    }

    assert stored == fresh
    assert digest == _canonical_digest(stored)
