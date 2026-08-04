"""Test exact integral lattices, reductions, roots, and affine shells.

Owns:
    Reproduction tests for the E8 hyperbolic embedding, D5 root and survivor
    counts, and degree-one and degree-two affine lattice shells and orbits.

Depends on:
    `onetheory.math.finite`, `onetheory.math.lattices`, pytest, and Python’s
    standard-library counting and dataclass utilities.

Must not:
    Interpret lattice data as particle or carrier structure, import draft code,
    select geometry from observations, or use unbounded search as a certificate.

Phase 0:
    Mathematical foundation tests only; no physical implementation is provided yet.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import FrozenInstanceError

import pytest

from onetheory.math.finite import PrimeField, enumerate_vectors
from onetheory.math.lattices import AffineAction, AffineQuadraticForm, IntegralLattice

E8_CARTAN = (
    (2, 0, -1, 0, 0, 0, 0, 0),
    (0, 2, -1, 0, 0, 0, 0, 0),
    (-1, -1, 2, -1, 0, 0, 0, 0),
    (0, 0, -1, 2, -1, 0, 0, 0),
    (0, 0, 0, -1, 2, -1, 0, 0),
    (0, 0, 0, 0, -1, 2, -1, 0),
    (0, 0, 0, 0, 0, -1, 2, -1),
    (0, 0, 0, 0, 0, 0, -1, 2),
)

D5_CARTAN = (
    (2, -1, 0, 0, 0),
    (-1, 2, -1, 0, 0),
    (0, -1, 2, -1, -1),
    (0, 0, -1, 2, 0),
    (0, 0, -1, 0, 2),
)


def test_integral_lattice_pairings_roots_and_reduction_are_exact() -> None:
    lattice = IntegralLattice(((2, -1), (-1, 2)))

    assert lattice.pair((1, 0), (0, 1)) == -1
    assert lattice.norm((1, -1)) == 6
    assert lattice.reduce_mod_prime((-1, 4), 3) == (2, 1)
    assert lattice.reduced_vector((-1, 4), 3).values == (2, 1)
    assert lattice.norm_mod_prime((1, -1), 3) == 0
    assert lattice.quadratic_mod_prime((1, -1), 3) == 0

    with pytest.raises(FrozenInstanceError):
        lattice._gram = ()  # type: ignore[misc]
    with pytest.raises(ValueError):
        IntegralLattice(((1, 2), (3, 1)))


def test_e8_mod_three_contains_the_hyperbolic_plane_embedding() -> None:
    lattice = IntegralLattice(E8_CARTAN)
    u = (0, 0, 0, 0, 0, 1, 2, 0)
    v = (0, 0, 0, 0, 2, 1, 0, 0)
    field = PrimeField(3)

    assert lattice.quadratic_mod_prime(u, field) == 0
    assert lattice.quadratic_mod_prime(v, field) == 0
    assert lattice.pairing_mod_prime(u, v, field) == 1
    assert lattice.reduced_vector(u, field).field == field


def test_d5_root_isotropic_pair_and_survivor_counts() -> None:
    lattice = IntegralLattice(D5_CARTAN)
    field = PrimeField(3)
    roots = lattice.roots(bound=3)
    isotropic = tuple(
        vector
        for vector in enumerate_vectors(field, lattice.rank)
        if not vector.is_zero()
        and lattice.quadratic_mod_prime(vector.values, field) == 0
    )
    hyperbolic_pairs = tuple(
        (left, right)
        for left in isotropic
        for right in isotropic
        if lattice.pairing_mod_prime(left.values, right.values, field) == 1
    )
    survivors = Counter(
        sum(
            1
            for root in roots
            if lattice.pairing_mod_prime(left.values, root, field) == 0
            and lattice.pairing_mod_prime(right.values, root, field) == 0
        )
        for left, right in hyperbolic_pairs
    )

    assert len(roots) == 40
    assert len(isotropic) == 80
    assert len(hyperbolic_pairs) == 2160
    assert survivors == Counter({2: 960, 4: 960, 6: 240})


def test_affine_mordell_weil_style_shells_and_orbits() -> None:
    degree = AffineQuadraticForm(((1, -1), (0, 1)), (-1, 0))
    action = AffineAction(((0, -1), (1, -1)), (1, 0))
    shell_one = degree.shell(1, bound=8)
    shell_two = degree.shell(2, bound=8)

    assert shell_one == ((0, -1), (0, 1), (2, 1))
    assert shell_two == ((-1, -1), (-1, 0), (1, -1), (1, 2), (2, 0), (2, 2))
    assert action.orbit((0, -1)) == ((0, -1), (2, 1), (0, 1))
    assert len(action.shell_orbits(degree, 1, 8)) == 1
    assert len(action.shell_orbits(degree, 2, 8)) == 2
    assert tuple(sorted(map(len, action.shell_orbits(degree, 2, 8)))) == (3, 3)

    with pytest.raises(ValueError):
        action.orbit((0, -1), period=2)
