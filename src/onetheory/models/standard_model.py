"""Exact low-energy Standard Model representation metadata.

Owns:
    The SU(3)_C × SU(2)_L × U(1)_Y gauge structure, its U(1)_{B-L} extension,
    quark, lepton, right-handed-neutrino, and one Higgs-pair representations.

Depends on:
    `onetheory.physics.gauge`, `matter`, and `strings` plus exact reusable
    metadata; it does not import the heterotic carrier or measured observations.

Must not:
    Store masses, mixing angles, fitted couplings, geometry selectors, or claim
    that representation metadata proves a concrete ultraviolet realization.

Phase 0:
    The established exact representation structure is implemented; observables
    remain terminal comparison data and unresolved normalization is unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from onetheory.math.numbers import coerce_rational
from onetheory.physics.gauge import Charge, GaugeGroup, Representation
from onetheory.physics.matter import Chirality, ParticleMultiplet, Spectrum
from onetheory.physics.strings import PublishedPhysicalInput

COLOR = GaugeGroup.simple("SU(3)_C", 2, 3)
WEAK = GaugeGroup.simple("SU(2)_L", 1, 2)
HYPERCHARGE = GaugeGroup.simple("U(1)_Y", 1, 1)
B_MINUS_L = GaugeGroup.simple("U(1)_{B-L}", 1, 1)
STANDARD_MODEL_GAUGE_GROUP = GaugeGroup.product(COLOR, WEAK, HYPERCHARGE)
STANDARD_MODEL_BL_GROUP = GaugeGroup.product(STANDARD_MODEL_GAUGE_GROUP, B_MINUS_L)
STANDARD_MODEL_INPUT = PublishedPhysicalInput(
    "standard_model_representations",
    "Established low-energy Standard Model representation content",
    "published physical input",
    "Exact gauge factors and rational charge assignments",
)


def _representation(
    name: str,
    color_dimension: int,
    weak_dimension: int,
    hypercharge: Fraction,
    b_minus_l: Fraction,
    conjugate: bool = False,
) -> Representation:
    return Representation(
        name,
        STANDARD_MODEL_BL_GROUP,
        (
            (COLOR.factors[0], color_dimension),
            (WEAK.factors[0], weak_dimension),
            (HYPERCHARGE.factors[0], 1),
            (B_MINUS_L.factors[0], 1),
        ),
        (
            Charge("Y", coerce_rational(hypercharge)),
            Charge("B-L", coerce_rational(b_minus_l)),
        ),
        conjugate,
    )


Q = _representation("Q", 3, 2, Fraction(1, 6), Fraction(1, 3))
UP_ANTIQUARK = _representation("u^c", 3, 1, Fraction(-2, 3), Fraction(-1, 3), True)
DOWN_ANTIQUARK = _representation("d^c", 3, 1, Fraction(1, 3), Fraction(-1, 3), True)
LEPTON_DOUBLEt = _representation("L", 1, 2, Fraction(-1, 2), Fraction(-1))
ELECTRON_ANTILEPTON = _representation("e^c", 1, 1, Fraction(1), Fraction(1), True)
NEUTRINO_ANTILEPTON = _representation("ν^c", 1, 1, Fraction(0), Fraction(1), True)
HIGGS_UP = _representation("H_u", 1, 2, Fraction(1, 2), Fraction(0))
HIGGS_DOWN = _representation("H_d", 1, 2, Fraction(-1, 2), Fraction(0))


@dataclass(frozen=True, slots=True)
class StandardModel:
    """The exact representation-level Standard Model structure."""

    gauge_group: GaugeGroup
    extended_gauge_group: GaugeGroup
    spectrum: Spectrum
    input_record: PublishedPhysicalInput


def standard_model_spectrum() -> Spectrum:
    """Return three matter generations and one Higgs pair as metadata."""

    return Spectrum((
        ParticleMultiplet("Q", Q, Chirality.LEFT, 3, "quark"),
        ParticleMultiplet("u^c", UP_ANTIQUARK, Chirality.LEFT, 3, "quark"),
        ParticleMultiplet("d^c", DOWN_ANTIQUARK, Chirality.LEFT, 3, "quark"),
        ParticleMultiplet("L", LEPTON_DOUBLEt, Chirality.LEFT, 3, "lepton"),
        ParticleMultiplet("e^c", ELECTRON_ANTILEPTON, Chirality.LEFT, 3, "lepton"),
        ParticleMultiplet("ν^c", NEUTRINO_ANTILEPTON, Chirality.LEFT, 3, "neutrino"),
        ParticleMultiplet("H_u", HIGGS_UP, Chirality.SCALAR, 1, "higgs"),
        ParticleMultiplet("H_d", HIGGS_DOWN, Chirality.SCALAR, 1, "higgs"),
    ))


def standard_model() -> StandardModel:
    """Assemble exact representation metadata without observational inputs."""

    return StandardModel(
        STANDARD_MODEL_GAUGE_GROUP,
        STANDARD_MODEL_BL_GROUP,
        standard_model_spectrum(),
        STANDARD_MODEL_INPUT,
    )
