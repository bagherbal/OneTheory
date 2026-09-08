"""Test the exact equivariant comparison of split matter products.

Owns:
    Regression gates for finite HPL comparison, correction closure, deck
    character, distinct family slots, and the fail-closed trace frontier.

Depends on:
    The strict matter tensor audit and lawful four-factor grouped contraction.

Must not:
    Supply a determinant pairing, normalize a cyclic trace, or identify the
    restricted product hull with a holomorphic Yukawa matrix.

Phase 0:
    Integration tests for the exact matter-to-Higgs chain comparison.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_comparison import (
    OUTPUT,
    mixed_schoen_matter_comparison,
)


def test_all_split_products_have_exact_equivariant_comparisons() -> None:
    """Finite HPL and Reynolds projection close all four family slots."""

    witnesses = mixed_schoen_matter_comparison()
    assert tuple((item.row, item.column) for item in witnesses) == (
        (0, 1),
        (0, 2),
        (1, 0),
        (2, 0),
    )
    assert all(
        item.character == (0, 2)
        and len(item.direct_product.terms) == 42_171
        and len(item.direct_residual.terms) == 43_917
        and len(item.reduced_representative.terms) == 168
        and len(item.strict_representative.terms) == 20_842
        and len(item.equivariant_representative.terms) == 23_439
        and len(item.correction.terms) == 35_625
        and item.projection_depth == 5
        and item.inclusion_depth == 5
        and item.projection_idempotent
        and item.strict_representative_is_cycle
        and item.equivariant_representative_is_cycle
        and item.correction_closes_direct_residual
        and item.character_exact
        and item.exact
        for item in witnesses
    )


def test_comparison_artifact_stops_before_determinant_tracing() -> None:
    """The frozen product hull exposes no scalar before a lawful trace."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert payload["all_comparisons_exact"] is True
    assert payload["equivariant_representatives_are_distinct"] is True
    assert payload["direct_product_hull_available"] is True
    assert payload["fiber_cover_substitution_used"] is False
    assert payload["extension_point_selected"] is False
    assert payload["cyclic_trace_available"] is False
    assert payload["holomorphic_yukawa_matrix_available"] is False
    assert payload["next_required_object"].startswith(
        "the determinant pairing and cyclic trace"
    )
