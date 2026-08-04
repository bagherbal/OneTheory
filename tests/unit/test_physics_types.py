"""Test the minimal exact physical vocabulary.

Owns:
    Gauge-group products, exact representation charges, immutable spectra, and
    traceable compactification and bundle metadata.

Depends on:
    `onetheory.physics.gauge`, `matter`, `strings`, exact Rational values, and
    pytest.

Must not:
    Test a concrete carrier, observations, fitted values, metrics, or dynamical
    Lie-algebra calculations.

Phase 0:
    Physical metadata tests only; no numerical or phenomenological implementation
    is provided here.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from onetheory.math.numbers import Rational
from onetheory.physics.gauge import Charge, GaugeGroup, Representation
from onetheory.physics.matter import Chirality, ParticleMultiplet, Spectrum
from onetheory.physics.strings import (
    Bundle,
    BundleStatus,
    CompactificationSpace,
    PublishedPhysicalInput,
    WilsonLine,
)


def test_gauge_groups_and_exact_representations_are_typed() -> None:
    color = GaugeGroup.simple("SU(3)_C", 2, 3)
    weak = GaugeGroup.simple("SU(2)_L", 1, 2)
    product = GaugeGroup.product(color, weak)
    quark = Representation(
        "Q",
        product,
        (("SU(3)_C", 3), ("SU(2)_L", 2)),
        (Charge("Y", Fraction(1, 6)),),
    )

    assert product.factors == ("SU(3)_C", "SU(2)_L")
    assert product.rank == 3
    assert quark.dimension == 6
    assert quark.charge("Y") == Rational(1, 6)

    with pytest.raises(KeyError):
        quark.charge("B-L")


def test_spectrum_preserves_multiplet_metadata_without_observables() -> None:
    group = GaugeGroup.simple("U(1)", 1, 1)
    representation = Representation("singlet", group, (("U(1)", 1),))
    spectrum = Spectrum((
        ParticleMultiplet("left", representation, Chirality.LEFT, 3, "matter"),
        ParticleMultiplet("higgs", representation, Chirality.SCALAR, 1, "higgs"),
    ))

    assert spectrum.total_multiplicity == 4
    assert spectrum.sector("matter")[0].multiplicity == 3
    assert spectrum.by_name("higgs").chirality is Chirality.SCALAR


def test_published_inputs_compactifications_bundles_and_wilson_lines_are_explicit() -> None:
    source = PublishedPhysicalInput(
        "carrier", "published carrier record", "https://example.invalid/carrier", "exact input"
    )
    space = CompactificationSpace("X", 3, 9, 9, source)
    group = GaugeGroup.simple("SU(4)", 3, 4)
    bundle = Bundle("visible", 4, group, (0, 0, 0), (1, 2, 3), 0, BundleStatus.PUBLISHED)
    line = WilsonLine("deck", GaugeGroup.simple("Spin(10)", 5, 16), 3, (("Q", 1),))

    assert space.fundamental_group_order == 9
    assert bundle.c2 == (Rational(1), Rational(2), Rational(3))
    assert line.character("Q") == 1
