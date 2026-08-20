"""Test exact local free frames for the published Serre constituents.

Owns:
    Affine generator reconstruction, Koszul injections, and localized
    Hilbert--Burch syzygy factorization at all six supported points.

Depends on:
    The research local constituent frame construction.

Must not:
    Treat local frames as global transition data or as full Higgs cocycles.

Phase 0:
    Local Serre frame regression tests only.
"""

from research.experiments.scientific_genesis.local_constituent_frames import (
    published_bound_punctured_frames,
    published_local_constituent_frames,
)


def test_all_local_constituent_frames_are_exact_and_free() -> None:
    """Every supported point has the canonical free rank-two Serre middle term."""

    first, second = published_local_constituent_frames()

    assert len(first) == len(second) == 3
    assert all(frame.exact for frame in (*first, *second))
    assert all(frame.global_generators_reconstructed for frame in (*first, *second))
    assert all(frame.koszul_composition_zero for frame in (*first, *second))
    assert all(frame.syzygies_factor_through_koszul for frame in (*first, *second))


def test_local_frames_recover_reduced_and_fat_lci_types() -> None:
    """I3 localizes to maximal ideals while I6 retains one doubled direction."""

    first, second = published_local_constituent_frames()

    assert tuple(frame.algebra.generators for frame in first) == (
        ((0, 1), (1, 0)),
        ((0, 1), (1, 0)),
        ((0, 1), (1, 0)),
    )
    assert tuple(frame.algebra.generators for frame in second) == (
        ((0, 2), (1, 0)),
        ((0, 1), (2, 0)),
        ((0, 2), (1, 0)),
    )
    assert tuple(frame.algebra.length for frame in first) == (1, 1, 1)
    assert tuple(frame.algebra.length for frame in second) == (2, 2, 2)


def test_global_syzygies_reduce_to_local_koszul_multiples() -> None:
    """Every nonzero localized Hilbert--Burch relation uses one Koszul column."""

    for frames in published_local_constituent_frames():
        for frame in frames:
            first, second = frame.local_generators
            for image_first, image_second in frame.syzygy_images:
                assert (first * image_first + second * image_second).is_zero()


def test_local_frames_bind_to_existing_punctured_atlas_cocycles() -> None:
    """The published frames reuse all six exact nonboundary unit pushouts."""

    bindings = published_bound_punctured_frames()

    assert len(bindings) == 6
    assert all(binding.exact for binding in bindings)
    assert tuple(binding.multiplicity for binding in bindings) == (1, 1, 1, 2, 2, 2)
    assert tuple(
        binding.atlas.cocycle_monomial_exponents for binding in bindings
    ) == ((-1, -1),) * 3 + ((-1, -2),) * 3
