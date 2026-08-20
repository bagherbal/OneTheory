"""Tests for deck pullback on full Serre outer Čech cochains."""

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
    _full_differential,
    _homotopy,
    _include,
    _perturbation,
    _reduced_basis,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    _full_action,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.scientific_genesis.published_outer_reduced_mismatch import (
    published_outer_reduced_mismatch,
)


def test_full_deck_action_preserves_differential_on_reduced_generators() -> None:
    mismatch = published_outer_reduced_mismatch()
    for outer in (mismatch.forward, mismatch.reverse):
        left = outer.left
        right = outer.right
        samples = tuple(
            entry
            for degree in (0, 1, 2, 3)
            for entry in _reduced_basis(left, right, degree)[:3]
        )
        assert samples
        for action in schoen_sparse_deck_actions():
            for entry in samples:
                source = _include(entry)
                assert _full_action(
                    _full_differential(source, left, right),
                    left,
                    right,
                    action,
                ) == _full_differential(
                    _full_action(source, left, right, action),
                    left,
                    right,
                )


def test_full_deck_generators_obey_group_laws_on_cech_samples() -> None:
    mismatch = published_outer_reduced_mismatch()
    left = mismatch.forward.left
    right = mismatch.forward.right
    p, t = schoen_sparse_deck_actions()
    entries = _reduced_basis(left, right, 1)
    source = sum(
        (_include(entry).scale(index + 1) for index, entry in enumerate(entries[:4])),
        SparseOuterCechCochain(),
    )

    def apply(action, cochain):
        return _full_action(cochain, left, right, action)

    assert apply(p, apply(p, apply(p, source))) == source
    assert apply(t, apply(t, apply(t, source))) == source
    assert apply(p, apply(t, source)) == apply(t, apply(p, source))
    assert not source.scale(Eisenstein(0)).terms


def test_homotopy_generated_extension_sector_has_square_zero() -> None:
    """The fiber Čech cup carries its tensor sign past preceding cover degree."""

    outer = published_outer_reduced_mismatch().forward
    source = _include(_reduced_basis(outer.left, outer.right, 1)[432])
    correction = _homotopy(_perturbation(source, outer.left, outer.right))
    image = _full_differential(correction, outer.left, outer.right)

    assert correction.terms
    assert _full_differential(image, outer.left, outer.right).is_zero()
