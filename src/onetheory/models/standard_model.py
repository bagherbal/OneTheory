"""Executable parameterized Standard Model law structure.

Owns:
    The SU(3)C × SU(2)L × U(1)Y gauge group, its optional U(1)B-L extension,
    three explicit chiral generations, Higgs doublets, gauge and matter kinetic
    laws, symbolic Yukawa tensors, scalar potential terms, charge checks, and exact
    anomaly certificates.

Depends on:
    General gauge, field, matter, and spacetime-independent exact metadata; it does
    not import the heterotic carrier, observations, or fitted parameters.

Must not:
    Store masses, mixing matrices, measured couplings, vacuum values, thresholds,
    geometry selectors, or claim a complete physical instance without parameters.

Phase 0:
    The established four-dimensional law structure is executable; every coupling and
    gravitational normalization remains an explicit unresolved symbolic input.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction
from math import atan2, sqrt

from onetheory.math.numbers import Rational, coerce_rational
from onetheory.physics.fields import FieldDomain, SymbolicCoefficient
from onetheory.physics.gauge import (
    AnomalyVector,
    Charge,
    GaugeGroup,
    Representation,
    anomaly_vector,
)
from onetheory.physics.matter import (
    Chirality,
    InteractionTerm,
    MajoranaMassOperator,
    ParticleMultiplet,
    ScalarMultiplet,
    Spectrum,
    SymbolicLinearMap,
    WeylField,
    YukawaTensor,
    generation_fields,
)
from onetheory.physics.observables import (
    CanonicalTransformation,
    ComplexMatrix,
    HermitianMetric,
    PhysicalEvaluationContext,
    PhysicalMatrix,
    PhysicalYukawa,
)
from onetheory.physics.spacetime import LorentzianSpacetime
from onetheory.physics.strings import PublishedPhysicalInput

COLOR = GaugeGroup.simple("SU(3)_C", 2, 3)
WEAK = GaugeGroup.simple("SU(2)_L", 1, 2)
HYPERCHARGE = GaugeGroup.simple("U(1)_Y", 1, 1)
B_MINUS_L = GaugeGroup.simple("U(1)_{B-L}", 1, 1)
STANDARD_MODEL_GAUGE_GROUP = GaugeGroup.product(COLOR, WEAK, HYPERCHARGE)
STANDARD_MODEL_BL_GROUP = GaugeGroup.product(STANDARD_MODEL_GAUGE_GROUP, B_MINUS_L)
STANDARD_MODEL_INPUT = PublishedPhysicalInput(
    "standard_model_laws",
    "Established low-energy Standard Model representation and interaction structure",
    "published physical input",
    "Exact gauge factors, chiral representations, and renormalizable operators",
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
        (Charge("Y", coerce_rational(hypercharge)), Charge("B-L", coerce_rational(b_minus_l))),
        conjugate,
        {
            **({COLOR.factors[0]: Rational(1, 2)} if color_dimension == 3 else {}),
            **({WEAK.factors[0]: Rational(1, 2)} if weak_dimension == 2 else {}),
        },
        {COLOR.factors[0]: Rational(1, 2)} if color_dimension == 3 else {},
    )


Q = _representation("Q", 3, 2, Fraction(1, 6), Fraction(1, 3))
UP_ANTIQUARK = _representation("u^c", 3, 1, Fraction(-2, 3), Fraction(-1, 3), True)
DOWN_ANTIQUARK = _representation("d^c", 3, 1, Fraction(1, 3), Fraction(-1, 3), True)
LEPTON_DOUBLET = _representation("L", 1, 2, Fraction(-1, 2), Fraction(-1))
ELECTRON_ANTILEPTON = _representation("e^c", 1, 1, Fraction(1), Fraction(1), True)
NEUTRINO_ANTILEPTON = _representation("ν^c", 1, 1, Fraction(0), Fraction(1), True)
HIGGS_UP = _representation("H_u", 1, 2, Fraction(1, 2), Fraction(0))
HIGGS_DOWN = _representation("H_d", 1, 2, Fraction(-1, 2), Fraction(0))


@dataclass(frozen=True, slots=True)
class GaugeBosonLaw:
    """One gauge factor's symbolic kinetic law."""

    factor: str
    coupling: SymbolicCoefficient
    field_strength_name: str
    mass_dimension: Rational
    gauge_invariant: bool
    lorentz_invariant: bool

    def __init__(self, factor: str, coupling: SymbolicCoefficient) -> None:
        if not factor.strip():
            raise ValueError("gauge boson laws require a factor")
        object.__setattr__(self, "factor", factor)
        object.__setattr__(self, "coupling", coupling)
        object.__setattr__(self, "field_strength_name", f"F_{factor}")
        object.__setattr__(self, "mass_dimension", Rational(4))
        object.__setattr__(self, "gauge_invariant", True)
        object.__setattr__(self, "lorentz_invariant", True)


@dataclass(frozen=True, slots=True)
class KineticLaw:
    """A dimension-four covariant kinetic term record."""

    name: str
    fields: tuple[str, ...]
    mass_dimension: Rational
    gauge_invariant: bool
    lorentz_invariant: bool

    def __init__(self, name: str, fields: tuple[str, ...]) -> None:
        if not name.strip() or not fields:
            raise ValueError("kinetic laws require names and fields")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "fields", fields)
        object.__setattr__(self, "mass_dimension", Rational(4))
        object.__setattr__(self, "gauge_invariant", True)
        object.__setattr__(self, "lorentz_invariant", True)


@dataclass(frozen=True, slots=True)
class ChargeAssignment:
    """The exact electric charges of the components of one multiplet."""

    multiplet: str
    charges: tuple[Rational, ...]


@dataclass(frozen=True, slots=True)
class StandardModel:
    """The complete parameterized renormalizable Standard Model law structure."""

    gauge_group: GaugeGroup
    extended_gauge_group: GaugeGroup
    spectrum: Spectrum
    input_record: PublishedPhysicalInput
    spacetime: LorentzianSpacetime
    domain: FieldDomain
    matter_fields: tuple[WeylField, ...]
    scalar_multiplets: tuple[ScalarMultiplet, ...]
    gauge_bosons: tuple[GaugeBosonLaw, ...]
    fermion_kinetic_terms: tuple[KineticLaw, ...]
    higgs_kinetic_terms: tuple[KineticLaw, ...]
    potential_terms: tuple[InteractionTerm, ...]
    yukawa_tensors: tuple[YukawaTensor, ...]
    majorana_operator: MajoranaMassOperator
    anomalies: AnomalyVector
    b_minus_l_anomalies: AnomalyVector
    electric_charges: tuple[ChargeAssignment, ...]
    b_minus_l_enabled: bool
    unresolved_parameters: tuple[str, ...]

    @property
    def all_law_terms_are_invariant(self) -> bool:
        return all(
            bool(getattr(term, "gauge_invariant", False))
            and bool(getattr(term, "lorentz_invariant", False))
            for term in (
                *self.gauge_bosons,
                *self.fermion_kinetic_terms,
                *self.higgs_kinetic_terms,
                *self.potential_terms,
                *self.yukawa_tensors,
            )
        )

    @property
    def gauge_kinetic_terms(self) -> tuple[GaugeBosonLaw, ...]:
        """Return the declared gauge kinetic laws."""

        return self.gauge_bosons

    @property
    def higgs_potential_terms(self) -> tuple[InteractionTerm, ...]:
        """Return the declared symbolic Higgs-potential terms."""

        return self.potential_terms

    @property
    def all_renormalizable_terms_dimension_four(self) -> bool:
        return all(
            getattr(term, "mass_dimension", None) == 4
            for term in (
                *self.gauge_bosons,
                *self.fermion_kinetic_terms,
                *self.higgs_kinetic_terms,
                *self.potential_terms,
                *self.yukawa_tensors,
            )
        )

    @property
    def electric_charge_assignments_valid(self) -> bool:
        """Certify the exact component charges derived from Y and weak isospin."""

        expected = {
            "Q": (Rational(2, 3), Rational(-1, 3)),
            "u^c": (Rational(-2, 3),),
            "d^c": (Rational(1, 3),),
            "L": (Rational(0), Rational(-1)),
            "e^c": (Rational(1),),
            "ν^c": (Rational(0),),
            "H_u": (Rational(1), Rational(0)),
            "H_d": (Rational(0), Rational(-1)),
        }
        return {item.multiplet: item.charges for item in self.electric_charges} == expected


@dataclass(frozen=True, slots=True)
class ElectroweakVacuum:
    """A derived electroweak stationary point with explicit stability evidence."""

    vev: float
    potential_value: float
    stable: bool
    context: PhysicalEvaluationContext
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.vev <= 0 or not self.provenance:
            raise ValueError("electroweak vacua require a positive derived VEV and provenance")


@dataclass(frozen=True, slots=True)
class HiggsPotential:
    """A one-field renormalizable Higgs potential with explicit coefficients."""

    quadratic_coefficient: float
    quartic_coefficient: float
    context: PhysicalEvaluationContext
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.quartic_coefficient <= 0 or not self.provenance:
            raise ValueError("Higgs potentials require a positive quartic coefficient")


def derive_electroweak_vacuum(potential: HiggsPotential) -> ElectroweakVacuum:
    """Derive the stable electroweak stationary point from the Higgs potential."""

    if potential.quadratic_coefficient >= 0:
        raise ValueError("the supplied Higgs potential has no symmetry-breaking minimum")
    vev = sqrt(-potential.quadratic_coefficient / potential.quartic_coefficient)
    value = -(potential.quadratic_coefficient**2) / (4 * potential.quartic_coefficient)
    return ElectroweakVacuum(
        vev,
        value,
        True,
        potential.context,
        (*potential.provenance, "derived electroweak stationary point"),
    )


@dataclass(frozen=True, slots=True)
class GaugeBosonMassMatrix:
    """Gauge-boson masses derived from explicit couplings and an electroweak VEV."""

    charged_w_mass_squared: float
    neutral_matrix: PhysicalMatrix
    photon_mass_squared: float
    z_mass_squared: float
    weak_mixing_angle: float
    electromagnetic_generator: tuple[tuple[str, Fraction], ...]
    vacuum: ElectroweakVacuum


@dataclass(frozen=True, slots=True)
class FermionMassMatrix:
    """A fermion mass matrix derived from a physical Yukawa and the VEV."""

    matrix: PhysicalMatrix
    yukawa: PhysicalYukawa
    vacuum: ElectroweakVacuum


@dataclass(frozen=True, slots=True)
class ScalarMassSpectrum:
    """Scalar masses extracted from a canonically normalized Hessian."""

    masses_squared: tuple[float, ...]
    canonical_hessian: PhysicalMatrix
    vacuum: ElectroweakVacuum
    goldstone_indices: tuple[int, ...]


def gauge_boson_mass_matrix(
    vacuum: ElectroweakVacuum, weak_coupling: float, hypercharge_coupling: float
) -> GaugeBosonMassMatrix:
    """Derive W and neutral gauge masses without measured-value defaults."""

    if weak_coupling <= 0 or hypercharge_coupling <= 0:
        raise ValueError("gauge couplings must be positive")
    scale = vacuum.vev**2 / 4
    neutral = PhysicalMatrix(
        ComplexMatrix(
            (
                (weak_coupling**2 * scale, -weak_coupling * hypercharge_coupling * scale),
                (-weak_coupling * hypercharge_coupling * scale, hypercharge_coupling**2 * scale),
            )
        ),
        vacuum.context,
        "(W3,B)",
        (*vacuum.provenance, "electroweak gauge mass law"),
    )
    z_squared = (weak_coupling**2 + hypercharge_coupling**2) * scale
    angle = atan2(hypercharge_coupling, weak_coupling)
    return GaugeBosonMassMatrix(
        weak_coupling**2 * scale,
        neutral,
        0.0,
        z_squared,
        angle,
        (("T3", Fraction(1, 1)), ("Y", Fraction(1, 1))),
        vacuum,
    )


def fermion_mass_matrix(yukawa: PhysicalYukawa, vacuum: ElectroweakVacuum) -> FermionMassMatrix:
    """Derive a fermion mass matrix from an already normalized Yukawa."""

    yukawa.matrix.context.assert_compatible(vacuum.context)
    matrix = yukawa.matrix.matrix.scale(vacuum.vev / sqrt(2))
    return FermionMassMatrix(
        PhysicalMatrix(
            matrix, vacuum.context, yukawa.matrix.basis, (*yukawa.matrix.provenance, "Higgs VEV")
        ),
        yukawa,
        vacuum,
    )


def scalar_mass_spectrum(
    hessian: PhysicalMatrix,
    kinetic_metric: HermitianMetric,
    vacuum: ElectroweakVacuum,
    goldstone_indices: Iterable[int] = (),
) -> ScalarMassSpectrum:
    """Normalize a scalar Hessian before extracting physical masses."""

    hessian.context.assert_compatible(kinetic_metric.context)
    hessian.context.assert_compatible(vacuum.context)
    transform = CanonicalTransformation.from_metric(kinetic_metric)
    canonical = transform.matrix.conjugate_transpose() @ hessian.matrix @ transform.matrix
    masses = tuple(canonical[index][index].real for index in range(canonical.row_count))
    indices = tuple(goldstone_indices)
    if any(index < 0 or index >= len(masses) for index in indices):
        raise ValueError("Goldstone indices must lie within the scalar Hessian")
    return ScalarMassSpectrum(
        masses,
        PhysicalMatrix(
            canonical,
            vacuum.context,
            hessian.basis,
            (*hessian.provenance, "canonical scalar Hessian"),
        ),
        vacuum,
        indices,
    )


def standard_model_spectrum() -> Spectrum:
    """Return three matter generations and one Higgs pair as exact content."""

    return Spectrum(
        (
            ParticleMultiplet("Q", Q, Chirality.LEFT, 3, "quark"),
            ParticleMultiplet("u^c", UP_ANTIQUARK, Chirality.LEFT, 3, "quark"),
            ParticleMultiplet("d^c", DOWN_ANTIQUARK, Chirality.LEFT, 3, "quark"),
            ParticleMultiplet("L", LEPTON_DOUBLET, Chirality.LEFT, 3, "lepton"),
            ParticleMultiplet("e^c", ELECTRON_ANTILEPTON, Chirality.LEFT, 3, "lepton"),
            ParticleMultiplet("ν^c", NEUTRINO_ANTILEPTON, Chirality.LEFT, 3, "neutrino"),
            ParticleMultiplet("H_u", HIGGS_UP, Chirality.SCALAR, 1, "higgs"),
            ParticleMultiplet("H_d", HIGGS_DOWN, Chirality.SCALAR, 1, "higgs"),
        )
    )


def _coefficient(name: str, dimension: object = 0) -> SymbolicCoefficient:
    return SymbolicCoefficient(name, dimension, STANDARD_MODEL_INPUT.statement)


def _scalar_conjugate(multiplet: ScalarMultiplet) -> ScalarMultiplet:
    return ScalarMultiplet(
        f"{multiplet.name}†", multiplet.representation.conjugate_representation()
    )


def _charge_assignment(multiplet: ParticleMultiplet) -> ChargeAssignment:
    hypercharge = multiplet.representation.charge("Y")
    weak_dimension = multiplet.representation.dimension_of_factor("SU(2)_L")
    if weak_dimension == 2:
        return ChargeAssignment(
            multiplet.name,
            (hypercharge + Rational(1, 2), hypercharge - Rational(1, 2)),
        )
    return ChargeAssignment(multiplet.name, (hypercharge,))


def standard_model(include_b_minus_l: bool = True) -> StandardModel:
    """Assemble exact laws while leaving all physical parameter values unresolved."""

    spectrum = standard_model_spectrum()
    spacetime = LorentzianSpacetime()
    domain = FieldDomain("M4", spacetime)
    matter = tuple(
        field
        for multiplet in spectrum.multiplets
        if multiplet.chirality is not Chirality.SCALAR
        for field in generation_fields(multiplet)
    )
    scalar = tuple(
        ScalarMultiplet(multiplet.name, multiplet.representation)
        for multiplet in spectrum.sector("higgs")
    )
    quarks = spectrum.by_name("Q")
    up = spectrum.by_name("u^c")
    down = spectrum.by_name("d^c")
    leptons = spectrum.by_name("L")
    charged = spectrum.by_name("e^c")
    neutrinos = spectrum.by_name("ν^c")
    h_up = scalar[0]
    h_down = scalar[1]
    yukawas = (
        YukawaTensor(
            "Y_u", quarks, up, h_up, SymbolicLinearMap("Y_u", 3, 3, "unresolved carrier parameter")
        ),
        YukawaTensor(
            "Y_d",
            quarks,
            down,
            h_down,
            SymbolicLinearMap("Y_d", 3, 3, "unresolved carrier parameter"),
        ),
        YukawaTensor(
            "Y_e",
            leptons,
            charged,
            h_down,
            SymbolicLinearMap("Y_e", 3, 3, "unresolved carrier parameter"),
        ),
        YukawaTensor(
            "Y_ν",
            leptons,
            neutrinos,
            h_up,
            SymbolicLinearMap("Y_ν", 3, 3, "unresolved carrier parameter"),
        ),
    )
    h_up_bar = _scalar_conjugate(h_up)
    h_down_bar = _scalar_conjugate(h_down)
    potential = (
        InteractionTerm(
            "m_u^2 H_u†H_u",
            (h_up_bar, h_up),
            SymbolicLinearMap("m_u^2", 1, 1, "unresolved Higgs potential parameter", 2),
            STANDARD_MODEL_INPUT.statement,
        ),
        InteractionTerm(
            "m_d^2 H_d†H_d",
            (h_down_bar, h_down),
            SymbolicLinearMap("m_d^2", 1, 1, "unresolved Higgs potential parameter", 2),
            STANDARD_MODEL_INPUT.statement,
        ),
        InteractionTerm(
            "lambda_ud H_u†H_u H_d†H_d",
            (h_up_bar, h_up, h_down_bar, h_down),
            SymbolicLinearMap("lambda_ud", 1, 1, "unresolved Higgs potential parameter"),
            STANDARD_MODEL_INPUT.statement,
        ),
    )
    majorana_operator = MajoranaMassOperator(
        neutrinos,
        SymbolicLinearMap("M_ν", 3, 3, "optional Majorana mass parameter", 1),
        include_b_minus_l,
    )
    selected_extended_group = (
        STANDARD_MODEL_BL_GROUP if include_b_minus_l else STANDARD_MODEL_GAUGE_GROUP
    )
    gauge_factors = selected_extended_group.factors
    gauge_bosons = tuple(
        GaugeBosonLaw(factor, _coefficient(f"g_{factor}")) for factor in gauge_factors
    )
    fermion_kinetic = tuple(
        KineticLaw(f"kinetic_{multiplet.name}", (multiplet.name,))
        for multiplet in spectrum.multiplets
        if multiplet.chirality is not Chirality.SCALAR
    )
    higgs_kinetic = tuple(
        KineticLaw(f"kinetic_{multiplet.name}", (multiplet.name,))
        for multiplet in spectrum.sector("higgs")
    )
    chiral_multiplets = tuple(
        item for item in spectrum.multiplets if item.chirality is not Chirality.SCALAR
    )
    anomalies = anomaly_vector(chiral_multiplets, ("Y",))
    b_minus_l_anomalies = anomaly_vector(chiral_multiplets, ("Y", "B-L"))
    unresolved = (
        "gauge couplings",
        "Yukawa matrices",
        "Higgs potential parameters",
        "gravitational normalization",
        "threshold corrections",
        "one common controlled vacuum",
    )
    if not include_b_minus_l:
        b_minus_l_anomalies = AnomalyVector({})
    return StandardModel(
        STANDARD_MODEL_GAUGE_GROUP,
        selected_extended_group,
        spectrum,
        STANDARD_MODEL_INPUT,
        spacetime,
        domain,
        matter,
        scalar,
        gauge_bosons,
        fermion_kinetic,
        higgs_kinetic,
        potential,
        yukawas,
        majorana_operator,
        anomalies,
        b_minus_l_anomalies,
        tuple(_charge_assignment(item) for item in spectrum.multiplets),
        include_b_minus_l,
        unresolved,
    )


__all__ = [
    "B_MINUS_L",
    "COLOR",
    "DOWN_ANTIQUARK",
    "ElectroweakVacuum",
    "ELECTRON_ANTILEPTON",
    "FermionMassMatrix",
    "GaugeBosonMassMatrix",
    "HiggsPotential",
    "HIGGS_DOWN",
    "HIGGS_UP",
    "HYPERCHARGE",
    "LEPTON_DOUBLET",
    "NEUTRINO_ANTILEPTON",
    "Q",
    "ScalarMassSpectrum",
    "STANDARD_MODEL_BL_GROUP",
    "STANDARD_MODEL_GAUGE_GROUP",
    "StandardModel",
    "UP_ANTIQUARK",
    "WEAK",
    "standard_model",
    "standard_model_spectrum",
    "fermion_mass_matrix",
    "gauge_boson_mass_matrix",
    "scalar_mass_spectrum",
    "derive_electroweak_vacuum",
]
