"""Test exact Hilbert--Burch resolutions on the dP9 blow-up atlas."""

from __future__ import annotations

from research.experiments.computable_carrier.ideal_atlas import tier_a_atlas_ideal_resolutions
from research.experiments.computable_carrier.pencil import tier_a_pencil_model


def test_i3_i6_resolutions_pull_back_to_all_atlas_charts() -> None:
    """Both point-scheme resolutions have the expected local shapes."""

    resolutions = tier_a_atlas_ideal_resolutions(tier_a_pencil_model())
    assert tuple(item.scheme for item in resolutions) == ("I3", "I6")
    assert tuple(item.generator_degree for item in resolutions) == (2, 3)
    assert all(len(item.chart_matrices) == 6 for item in resolutions)
    assert all(all(shape[1] for _, shape in item.local_resolution_shapes) for item in resolutions)


def test_i3_i6_resolution_maps_agree_on_every_ordered_overlap() -> None:
    """Every pulled-back Hilbert--Burch matrix satisfies its chain comparison."""

    resolutions = tier_a_atlas_ideal_resolutions(tier_a_pencil_model())
    assert all(len(item.overlap_comparisons) == 30 for item in resolutions)
    assert all(item.all_chain_comparisons for item in resolutions)
    assert all(
        comparison.chain_comparison
        for item in resolutions
        for comparison in item.overlap_comparisons
    )
