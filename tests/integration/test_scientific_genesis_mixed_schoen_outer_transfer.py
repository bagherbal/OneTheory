"""Test the selected mixed outer-Hom transfer on the Schoen cover.

Owns:
    Totalization signs, contracted-path closure, exact transferred ranks,
    cohomology dimensions, and generated-artifact integrity.

Depends on:
    The Scientific Genesis mixed constituent and outer-transfer experiments.

Must not:
    Import retired pure-Cech dimensions, infer quotient invariants, or promote
    cover cohomology as a physical spectrum.

Phase 0:
    Research-only exact mixed outer-Hom transfer regression tests.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
    _cech_differential,
    _components,
    _homotopy,
    _include,
    _reduced_basis,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    mixed_schoen_constituents,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    OUTPUT,
    _CompatibleTermIndex,
    _mixed_perturbation,
    _skeleton,
)


def test_mixed_outer_differential_closes_along_contracted_paths() -> None:
    """Canonical and contracted cochains obey the same square-zero law."""

    left, right = mixed_schoen_constituents()
    left_skeleton = _skeleton(left)
    right_skeleton = _skeleton(right)
    components = {
        (item.left_index, item.right_index, item.koszul_summand): item
        for item in _components(left_skeleton, right_skeleton)
    }
    left_index = _CompatibleTermIndex(left)
    right_index = _CompatibleTermIndex(right)

    def perturbation(
        cochain: SparseOuterCechCochain,
    ) -> SparseOuterCechCochain:
        return _mixed_perturbation(
            cochain,
            left,
            right,
            left_skeleton,
            right_skeleton,
            components,
            left_index,
            right_index,
        )

    def differential(
        cochain: SparseOuterCechCochain,
    ) -> SparseOuterCechCochain:
        return _cech_differential(cochain) + perturbation(cochain)

    entries = _reduced_basis(left_skeleton, right_skeleton, 0)
    for entry in (entries[0], entries[252]):
        current = _include(entry)
        for _depth in range(2):
            assert differential(differential(current)).is_zero()
            current = _homotopy(perturbation(current)).scale(-1)


def test_mixed_outer_transfer_artifact_is_current() -> None:
    """The frozen certificate records only independently derived cover data."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    orientations = stored["orientations"]

    assert digest == _canonical_digest(stored)
    assert stored["all_transferred_differentials_square_zero"] is True
    assert stored["source_outer_dimensions_imported"] is False
    assert stored["retired_pure_cech_arrows_used"] is False
    assert stored["deck_actions_transferred"] is False
    assert [item["cohomology_dimensions"] for item in orientations] == [
        [
            [-3, 0],
            [-2, 0],
            [-1, 0],
            [0, 0],
            [1, 18],
            [2, 54],
            [3, 0],
            [4, 0],
            [5, 0],
            [6, 0],
        ],
        [
            [-3, 0],
            [-2, 0],
            [-1, 0],
            [0, 0],
            [1, 54],
            [2, 18],
            [3, 0],
            [4, 0],
            [5, 0],
            [6, 0],
        ],
    ]
    assert [item["differential_ranks"] for item in orientations] == [
        [
            [-3, 0],
            [-2, 0],
            [-1, 0],
            [0, 1512],
            [1, 3006],
            [2, 1764],
            [3, 0],
            [4, 0],
            [5, 0],
            [6, 0],
        ],
        [
            [-3, 0],
            [-2, 0],
            [-1, 0],
            [0, 1764],
            [1, 3006],
            [2, 1512],
            [3, 0],
            [4, 0],
            [5, 0],
            [6, 0],
        ],
    ]
