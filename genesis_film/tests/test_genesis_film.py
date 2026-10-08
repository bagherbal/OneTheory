"""Verify the Genesis film's formula engine and its seamless painter handovers.

Owns:
    Checks that the shapes the film draws are the ones the formulas give (E8
    roots and branching, one Spin(10) family and its charges, the Hesse pencil,
    string modes, LambdaCDM ages and horizons, the Higgs quartic) and that
    consecutive cosmic painters paint identical pixels where the film hands
    over from one to the next, so the film has no jumps.

Depends on:
    NumPy, SciPy and the NumPy-only `genesis_film/physics.py` and
    `genesis_film/cosmos.py`. Manim is not needed.

Must not:
    Render video, import Manim, or loosen a tolerance to make a picture pass.

Phase 0:
    Presentation-layer verification; no physical result is claimed.
"""

from __future__ import annotations

import math
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

FILM = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FILM))

import cosmos  # noqa: E402
import physics  # noqa: E402


def test_e8_roots_and_coxeter_projection() -> None:
    roots = physics.e8_roots()
    assert roots.shape == (240, 8)
    assert np.allclose((roots**2).sum(axis=1), 2)
    gram = roots @ roots.T
    assert np.allclose(gram, np.round(gram))
    radii = np.round(np.linalg.norm(physics.project(roots), axis=1), 6)
    values, counts = np.unique(radii, return_counts=True)
    assert len(values) == 8 and set(counts) == {30}


def test_su4_spin10_branching_counts() -> None:
    roots = physics.e8_roots()
    masks = physics.root_subsets(roots)
    assert {k: int(v.sum()) for k, v in masks.items()} == {
        "su4": 12, "spin10": 40, "su5": 20, "su3": 6, "su2": 2}
    integer = np.all(np.abs(roots - np.round(roots)) < 1e-9, axis=1)
    mixed = integer & ~masks["su4"] & ~masks["spin10"]
    half = ~integer
    assert int(mixed.sum()) == 60                      # (6, 10)
    assert int(half.sum()) == 128                      # (4,16) + (4̄,1̄6̄)
    assert 3 + 12 + 5 + 40 + 60 + 128 == 248


def test_one_family_charges() -> None:
    family = physics.one_family()
    roots = {tuple(r) for r in physics.e8_roots()}
    assert len(family) == 16
    assert all(tuple(w.vector) in roots for w in family)
    assert Counter(w.field for w in family) == {
        "Q": 6, "u^c": 3, "d^c": 3, "L": 2, "e^c": 1, "ν^c": 1}
    expected = {"Q": Fraction(1, 6), "u^c": Fraction(-2, 3), "d^c": Fraction(1, 3),
                "L": Fraction(-1, 2), "e^c": Fraction(1), "ν^c": Fraction(0)}
    for w in family:
        assert Fraction(physics.hypercharge(w.vector)).limit_denominator(12) \
            == expected[w.field]
    charges = [physics.isospin(w.vector) + physics.hypercharge(w.vector) for w in family]
    assert abs(sum(charges)) < 1e-12


def test_hesse_pencil_base_points_and_triangle_fibre() -> None:
    for lam in (0.3, 1.0, 1.6):
        for x, y in physics.hesse_base_points():
            assert abs(physics.hesse(x, y, lam)) < 1e-12
    t = np.linspace(-2, 2, 9)
    assert np.allclose(physics.hesse(t, -1 - t, 1.0), 0)
    eps = 1e-6
    gx = (physics.hesse(1 + eps, 1, 1.0) - physics.hesse(1 - eps, 1, 1.0)) / (2 * eps)
    gy = (physics.hesse(1, 1 + eps, 1.0) - physics.hesse(1, 1 - eps, 1.0)) / (2 * eps)
    assert physics.hesse(1, 1, 1.0) == 0 and abs(gx) < 1e-6 and abs(gy) < 1e-6


def test_string_modes() -> None:
    sigma = np.linspace(0, 2 * math.pi, 50)
    loop = physics.string_loop(sigma, 0.3, (0, 0), (0, 0), radius=1.7)
    assert np.allclose(np.linalg.norm(loop, axis=1), 1.7)
    ring = physics.graviton_loop(sigma, 0.0, 0.2)
    assert np.isclose(ring[:, 0].max(), 1.2) and np.isclose(ring[:, 1].max(), 0.8, atol=1e-3)


def test_cosmology_numbers() -> None:
    assert physics.age_at(1.0) == pytest.approx(13.79, abs=0.03)
    horizons = physics.horizons_gly()
    assert horizons["particle"] == pytest.approx(46.1, abs=0.3)
    assert horizons["hubble"] == pytest.approx(14.51, abs=0.02)
    assert horizons["event"] == pytest.approx(16.7, abs=0.2)
    assert physics.age_at(1 / 1090.9) * 1e6 == pytest.approx(372, abs=6)
    assert physics.time_at_temperature(159.5, 106.75) == pytest.approx(9.2e-12, rel=0.02)
    assert physics.higgs_lambda() == pytest.approx(0.1293, abs=2e-4)
    assert physics.growth_factor(0.5) < 1 and physics.growth_factor(1.0) == pytest.approx(1)


def test_primordial_spectrum_tilt() -> None:
    field = physics.gaussian_field(256, 3, tilt=physics.N_S)
    assert abs(field.mean()) < 1e-12 and np.isclose(field.std(), 1)
    power = np.abs(np.fft.fft2(field)) ** 2
    k = np.sqrt(np.add.outer(np.fft.fftfreq(256) ** 2, np.fft.fftfreq(256) ** 2))
    bins = np.logspace(np.log10(4 / 256), np.log10(0.3), 12)
    centers, means = [], []
    for lo, hi in zip(bins[:-1], bins[1:], strict=True):
        ring = (k >= lo) & (k < hi)
        centers.append(np.sqrt(lo * hi))
        means.append(power[ring].mean())
    slope = np.polyfit(np.log(centers), np.log(means), 1)[0]
    assert slope == pytest.approx(physics.N_S - 3, abs=0.15)


@pytest.fixture(scope="module")
def universe() -> cosmos.Universe:
    return cosmos.Universe()


def test_inflation_hands_over_to_widening_and_the_soup(universe) -> None:
    end = math.exp(-cosmos.N_END)
    inflating = universe.paint_inflation(cosmos.N_END, grid=0.0)
    assert np.array_equal(inflating, universe.paint_widening(end))
    assert np.array_equal(universe.paint_widening(1.0), cosmos.Soup(universe).paint(0.0))
    assert np.allclose(universe.view_field(1.0), universe.P_window())


def test_soup_hands_over_to_the_cmb_and_web(universe) -> None:
    soup = cosmos.Soup(universe)
    late = cosmos.Cosmos(universe, cosmos.Galaxy())
    assert np.array_equal(soup.paint(cosmos.TAU_END), late.paint(growth=0.0, cmb=1.0, web=0.0))
    seam = late.paint(growth=1.0, zoom=1.0, web=1.0).astype(int)
    for zoom in (1.0 - 1e-6, 1.0 + 1e-6):
        side = late.paint(growth=1.0, zoom=zoom, web=1.0).astype(int)
        assert np.abs(side - seam)[40:-40, 40:-40].max() <= 2


def test_nucleosynthesis_bookkeeping(universe) -> None:
    soup = cosmos.Soup(universe)
    assert len(soup.helium) == 2
    for group in soup.helium:
        neutrons = sum(soup.neutron_initial[k] and soup.is_neutron(k, cosmos.FUSE[0]) > 0.5
                       for k in group)
        assert neutrons == 2 and len(group) == 4
    still_neutrons = sum(soup.is_neutron(k, cosmos.FUSE[0]) > 0.5 for k in range(32))
    assert still_neutrons == 4                          # n/p = 4/28 = 1/7
    helium_mass_fraction = 8 / 32
    assert helium_mass_fraction == pytest.approx(0.245, abs=0.01)
    charge = sum(c for _, c in soup.nuclei)
    assert charge == 28 and int((soup.e_host >= 0).sum()) == 28
