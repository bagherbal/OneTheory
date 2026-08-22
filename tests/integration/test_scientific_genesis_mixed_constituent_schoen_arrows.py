"""Test common-Schoen embedding of the selected mixed constituent arrows.

Owns:
    Object counts, mixed term sectors, multidegrees, cover regularity, closure,
    deck eigencharacters, and generated-artifact integrity.

Depends on:
    The Scientific Genesis mixed constituent Schoen-arrow experiment.

Must not:
    Infer outer cohomology, a rank-four extension, or physical Higgs states.

Phase 0:
    Selected constituent arrow regression tests only.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    OUTPUT,
    mixed_schoen_constituents,
)


def test_selected_mixed_arrows_embed_in_the_common_schoen_grading() -> None:
    """Every extension term has lawful total degree and multidegree."""

    first, second = mixed_schoen_constituents()

    assert first.name == "V1"
    assert second.name == "V2"
    assert len(first.objects) == 6
    assert len(second.objects) == 8
    assert len(first.extension_terms) == 216
    assert len(second.extension_terms) == 351
    assert first.all_terms_total_degree_one
    assert second.all_terms_total_degree_one
    assert first.all_multidegrees_compatible
    assert second.all_multidegrees_compatible
    assert first.exact
    assert second.exact


def test_mixed_arrows_retain_local_maps_and_hypersurface_homotopies() -> None:
    """Neither selected constituent collapses to a pure Cech extension arrow."""

    for constituent in mixed_schoen_constituents():
        sectors = {
            (term.parent_degree, term.koszul_degree, term.cech_degree)
            for term in constituent.extension_terms
        }

        assert (0, 0, 1) in sectors
        assert (1, 0, 0) in sectors
        assert (1, 1, 1) in sectors
        assert all(term.regular_on_cell for term in constituent.extension_terms)


def test_mixed_arrows_pull_back_over_every_unused_factor_patch() -> None:
    """A factor cocycle is constant across the other projective cover."""

    for constituent in mixed_schoen_constituents():
        unused_factor = 1 if constituent.factor == 1 else 0
        grouped: dict[tuple[object, ...], set[tuple[int, ...]]] = {}
        for term in constituent.extension_terms:
            key = (
                term.source,
                term.target,
                term.parent_degree,
                term.koszul_equation,
                term.x_monomial,
                term.u_monomial,
                term.p_monomial,
                tuple(
                    cell
                    for index, cell in enumerate(term.cell)
                    if index != unused_factor
                ),
                term.coefficient,
            )
            grouped.setdefault(key, set()).add(term.cell[unused_factor])

        assert grouped
        assert all(cells == {(0,), (1,), (2,)} for cells in grouped.values())


def test_mixed_schoen_arrow_artifact_is_current() -> None:
    """The frozen arrow certificate retains the outer-convolution boundary."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored["all_common_schoen_arrows_exact"] is True
    assert stored["retired_pure_cech_arrows_used"] is False
    assert stored["outer_hom_transfer_constructed"] is True
