"""Test the representation-level Standard Model structure.

Owns:
    Exact gauge factors, rational hypercharge and B-L assignments, three matter
    generations, right-handed neutrinos, and one Higgs pair.

Depends on:
    `onetheory.models.standard_model`, exact Rational values, and pytest.

Must not:
    Introduce measured observables, fitted couplings, geometry selectors, or a
    physical Yukawa matrix.

Phase 0:
    Established representation metadata only; ultraviolet calculations remain in
    the concrete carrier modules.
"""

from __future__ import annotations

from onetheory.math.numbers import Rational
from onetheory.models.standard_model import (
    STANDARD_MODEL_BL_GROUP,
    STANDARD_MODEL_GAUGE_GROUP,
    standard_model,
)


def test_standard_model_has_the_carrier_gauge_structure() -> None:
    model = standard_model()

    assert model.gauge_group == STANDARD_MODEL_GAUGE_GROUP
    assert model.extended_gauge_group == STANDARD_MODEL_BL_GROUP
    assert model.gauge_group.factors == ("SU(3)_C", "SU(2)_L", "U(1)_Y")
    assert model.extended_gauge_group.factors[-1] == "U(1)_{B-L}"


def test_standard_model_spectrum_has_three_families_and_one_higgs_pair() -> None:
    spectrum = standard_model().spectrum

    assert spectrum.by_name("Q").multiplicity == 3
    assert spectrum.by_name("ν^c").multiplicity == 3
    assert spectrum.by_name("H_u").multiplicity == 1
    assert spectrum.by_name("H_d").multiplicity == 1
    assert spectrum.by_name("Q").representation.charge("Y") == Rational(1, 6)
    assert spectrum.by_name("ν^c").representation.charge("B-L") == Rational(1)
    assert sum(item.multiplicity for item in spectrum.sector("higgs")) == 2
