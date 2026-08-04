"""Test the exact four-dimensional physics kernel.

Owns:
    Dimensional validation, Lorentzian tensor operations, field actions, gauge
    covariance, matter singlets, quantum adjoints, and Einstein-law records.

Depends on:
    Core units, general physics modules, exact Standard Model metadata, and pytest.

Must not:
    Import observations, choose carrier parameters, or claim numerical interacting
    quantum-field-theory results.

Phase 0:
    Exact law-structure tests are implemented; numerical values remain explicit.
"""

from fractions import Fraction

import pytest

from onetheory.core.errors import IncompatibleConvention, InconsistentDimensions
from onetheory.core.units import (
    LENGTH,
    DimensionVector,
    Quantity,
    Unit,
    UnitConversion,
    UnitSystem,
)
from onetheory.math.numbers import Rational
from onetheory.models.standard_model import standard_model
from onetheory.physics.fields import (
    Action,
    Derivative,
    Field,
    FieldCodomain,
    FieldDomain,
    LagrangianTerm,
    LocalProduct,
    SymbolicCoefficient,
)
from onetheory.physics.gauge import (
    CovariantDerivative,
    FieldStrength,
    GaugeConnection,
    GaugeTransformation,
    anomaly_vector,
    gauge_singlet,
)
from onetheory.physics.gravity import (
    CurvatureTensor,
    EinsteinHilbertAction,
    EinsteinTensor,
    LeviCivitaConnection,
    MetricField,
    RicciScalar,
    RicciTensor,
)
from onetheory.physics.quantum import (
    CanonicalRelation,
    Hamiltonian,
    HilbertSpace,
    Operator,
    QuantumState,
    UnitaryEvolution,
)
from onetheory.physics.spacetime import (
    DifferentialForm,
    IndexSpace,
    IndexVariance,
    LorentzianSpacetime,
    Tensor,
)


def test_units_require_exact_dimensions_and_explicit_cross_system_conversion() -> None:
    meter = Unit("m", LENGTH)
    natural_length = Unit("natural-length", LENGTH, system=UnitSystem.NATURAL)
    quantity = Quantity(Fraction(3, 2), meter)

    assert quantity.convert_to(meter).value == Fraction(3, 2)
    with pytest.raises(IncompatibleConvention):
        quantity.convert_to(natural_length)
    conversion = UnitConversion(UnitSystem.SI, UnitSystem.NATURAL, 2, "declared test conversion")
    assert quantity.convert_to(natural_length, conversion).value == 3
    with pytest.raises(InconsistentDimensions):
        quantity.convert_to(Unit("dimensionless", DimensionVector()))


def test_lorentzian_tensor_contraction_raising_lowering_and_forms() -> None:
    spacetime = LorentzianSpacetime()
    contravariant = IndexSpace("v", 4, IndexVariance.CONTRAVARIANT, spacetime.convention)
    covariant = IndexSpace("w", 4, IndexVariance.COVARIANT, spacetime.convention)
    tensor = Tensor((contravariant, covariant), (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))

    assert tensor.contract(0, 1).components == (Rational(4),)
    vector = Tensor((contravariant,), (1, 2, 3, 4))
    lowered = spacetime.metric.lower_index(vector, 0)
    assert lowered.components == (Rational(1), Rational(-2), Rational(-3), Rational(-4))
    assert spacetime.metric.raise_index(lowered, 0).components == vector.components
    one_form = DifferentialForm(spacetime, 1, (((0,), 1),))
    two_form = DifferentialForm(spacetime, 2, (((1, 2), 2),))
    assert one_form.wedge(two_form).component((0, 1, 2)) == 2


def test_field_action_terms_are_dimension_checked_and_domains_are_explicit() -> None:
    spacetime = LorentzianSpacetime()
    domain = FieldDomain("M4", spacetime)
    scalar = Field.scalar("phi", domain, FieldCodomain("scalar", 1), 1)
    coefficient = SymbolicCoefficient("lambda", 0, "test provenance")
    product = LocalProduct((Derivative(scalar, 0), Derivative(scalar, 0)))
    term = LagrangianTerm(product, None, "test provenance")
    assert term.product.mass_dimension == Rational(4)
    assert Action("free scalar", domain, (term,), "test provenance").terms == (term,)
    with pytest.raises(InconsistentDimensions):
        LagrangianTerm(LocalProduct((scalar,)), coefficient, "test provenance")


def test_gauge_field_strength_covariance_and_standard_model_anomalies() -> None:
    model = standard_model()
    connection = GaugeConnection(
        LorentzianSpacetime(), model.extended_gauge_group, (0, 0, 0, 0), "g"
    )
    field_strength = FieldStrength(connection, ((0, 1, "F01"),))
    assert field_strength.component(1, 0) == "-F01"
    transformation = GaugeTransformation(model.extended_gauge_group, "alpha", True)
    covariant = CovariantDerivative(
        connection,
        model.spectrum.by_name("Q").representation,
        "∂Q",
        "A·Q",
    )
    assert covariant.transforms_covariantly("Q'", transformation)
    assert field_strength.transforms_covariantly(transformation)
    assert model.anomalies.cancels
    assert model.b_minus_l_anomalies.cancels
    assert anomaly_vector(model.spectrum.sector("quark")).value("Y^3") != 0
    assert gauge_singlet(
        (
            model.spectrum.by_name("Q").representation,
            model.spectrum.by_name("u^c").representation,
            model.scalar_multiplets[0].representation,
        )
    )


def test_quantum_canonical_relations_and_gravity_records_require_consistency() -> None:
    space = HilbertSpace("finite", 2)
    creation = Operator("a†", space, fermionic=False)
    annihilation = creation.adjoint()
    assert CanonicalRelation.bosonic(creation, annihilation).bracket.value == "commutator"
    state = QuantumState(space, "psi", True, (1, 0))
    state.require_normalized()
    Hamiltonian("H", space, (creation,))
    assert UnitaryEvolution(Hamiltonian("H2", space, (creation,))).unitary
    spacetime = LorentzianSpacetime()
    metric_field = MetricField("g", spacetime)
    connection = LeviCivitaConnection(metric_field)
    curvature = CurvatureTensor(connection)
    ricci = RicciTensor(curvature)
    scalar = RicciScalar(ricci, 0)
    assert EinsteinTensor(ricci, scalar).expression == "R_ab - 1/2 g_ab R"
    assert EinsteinHilbertAction(metric_field).gravitational_constant_name == "G"
