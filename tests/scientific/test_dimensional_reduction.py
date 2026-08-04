"""Scientific certificates for generic dimensional reduction structures.

Owns:
    Exact benchmark checks for arbitrary-dimensional forms, ten-dimensional action
    conventions, characteristic-class separation, compactification modes, N=1 symbolic
    formulas, anomaly gates, and the Schoen effective-action boundary.

Depends on:
    Production mathematical and physical modules only, plus pytest for assertions.

Must not:
    Register benchmark fixtures as carrier results, load observations, or supply missing
    Schoen metrics, cocycles, bundle matrices, thresholds, or vacuum coefficients.

Phase 0:
    Generic scientific certificates are implemented; unresolved carrier calculations
    remain fail-closed.
"""

from __future__ import annotations

import pytest

from onetheory.core.errors import IncompatibleConvention, MissingPhysicalInput
from onetheory.math.geometry import (
    Basis,
    CharacteristicClass,
    ChernCharacter,
    ChernWeilRepresentative,
    ClassKind,
    Normalization,
    PontryaginClass,
    VectorBundle,
)
from onetheory.math.linear import Matrix
from onetheory.models.heterotic_schoen.consistency import (
    differential_anomaly_package,
)
from onetheory.models.heterotic_schoen.effective import (
    SCHOEN_EFFECTIVE_MISSING_CHAIN,
    request_complete_effective_action,
    schoen_effective_action,
)
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from onetheory.physics.compactification import (
    CalabiYauStructure,
    CohomologySource,
    CohomologySpectrumCompiler,
    ComplexStructure,
    DimensionalReductionPackage,
    EquivariantProjection,
    HarmonicMode,
    HermitianStructure,
    HolomorphicVolumeForm,
    KahlerForm,
    KahlerStructure,
    ModeNormalization,
    ModeOrthogonality,
    ReductionContext,
    ReductionTerm,
    WilsonLineProjection,
    emit_zero_mode,
    four_plus_six_ansatz,
)
from onetheory.physics.gauge import Charge, GaugeGroup, Representation
from onetheory.physics.matter import Chirality
from onetheory.physics.spacetime import (
    DifferentialForm,
    MetricSignature,
    Orientation,
    PseudoRiemannianManifold,
    SpacetimeConvention,
)
from onetheory.physics.strings import (
    FrameConvention,
    HeteroticConventions,
    WilsonLine,
    default_heterotic_field_content,
    heterotic_bosonic_action,
    string_to_einstein_frame,
)
from onetheory.physics.vacuum import (
    DTermPotential,
    EffectiveExpression,
    FTermPotential,
    GaugeKineticMatrix,
    KaehlerPotential,
    KineticMatrix,
    ModuliPoint,
    MomentMap,
    ScalarPotential,
    Superpotential,
)
from onetheory.reality import (
    assemble_schoen_effective_action,
    request_normalized_four_dimensional_effective_action,
)


def _internal() -> PseudoRiemannianManifold:
    convention = SpacetimeConvention(MetricSignature((1, 1, 1, 1, 1, 1)), Orientation(range(6)))
    return PseudoRiemannianManifold("X6", convention)


def test_hodge_wedge_interior_and_differential_identities() -> None:
    manifold = _internal()
    one = DifferentialForm(manifold, 1, (((0,), 1),))
    two = DifferentialForm(manifold, 2, (((1, 2), 1),))
    assert one.wedge(two).component((0, 1, 2)) == 1
    assert two.wedge(one).component((0, 1, 2)) == 1
    assert one.hodge_star().degree == 5
    assert one.hodge_star().hodge_star().component((0,)) == -1
    assert one.exterior_derivative().exterior_derivative().components == ()
    assert two.interior_product((1, 0, 0, 0, 0, 0)).component((1,)) == 0
    volume = DifferentialForm.volume(manifold)
    assert volume.hodge_star().component(()) == 1


def test_integration_orientation_and_convention_are_explicit() -> None:
    manifold = _internal()
    form = DifferentialForm.volume(manifold)
    from onetheory.physics.spacetime import IntegrationRecord

    assert (
        IntegrationRecord(manifold, manifold.convention.orientation, "benchmark").integrate(form)
        == 1
    )
    opposite = SpacetimeConvention(manifold.convention.signature, Orientation((1, 0, 2, 3, 4, 5)))
    with pytest.raises(IncompatibleConvention):
        DifferentialForm(PseudoRiemannianManifold("Y6", opposite), 1, (((0,), 1),)).wedge(
            DifferentialForm(manifold, 1, (((0,), 1),))
        )


def test_ten_dimensional_action_terms_keep_frame_and_dimension() -> None:
    group = GaugeGroup.simple("E8", 8, 248)
    conventions = HeteroticConventions(frame=FrameConvention.STRING)
    fields = default_heterotic_field_content(group, group, conventions)
    action = heterotic_bosonic_action(fields, conventions)
    assert action.mass_dimensions_valid
    assert action.uses_one_torsionful_connection
    assert all(term.frame is FrameConvention.STRING for term in action.terms)
    with pytest.raises(ValueError):
        heterotic_bosonic_action(fields, HeteroticConventions(frame=FrameConvention.EINSTEIN))


def test_chern_weil_data_do_not_promote_to_integral_topology() -> None:
    basis = Basis("H", ("h0", "h1", "h2"))
    normalization = Normalization("quotient")
    c1 = CharacteristicClass(basis, (1, 0, 0), 1, normalization)
    c2 = CharacteristicClass(basis, (0, 1, 0), 2, normalization)
    differential = CharacteristicClass(basis, (1, 0, 0), 1, normalization, ClassKind.DIFFERENTIAL)
    bundle = VectorBundle("V", 2, basis, normalization, c1, c2, provenance="published topology")
    character = ChernCharacter.from_bundle(bundle)
    assert character.rank == 2
    assert character.component(1) == c1
    representative = ChernWeilRepresentative(
        differential, "F", "Tr(F)/(2 pi)", "supplied curvature representative"
    )
    assert not representative.represents_integral_class
    assert PontryaginClass.p1_from_c2(c2).class_data.coordinates == (0, -2, 0)
    with pytest.raises(ValueError):
        _ = c1 + differential


def test_zero_modes_require_cohomology_and_wilson_character_inputs() -> None:
    manifold = _internal()
    group = GaugeGroup.simple("U(1)", 1, 1)
    representation = Representation("singlet", group, (("U(1)", 1),), (Charge("Q", 0),))
    source = CohomologySource("H1", "V", 1, representation, 3, Chirality.LEFT, 3, "published H1")
    mode = HarmonicMode(
        "H1-mode",
        "spinor",
        0,
        0,
        ModeNormalization("L2", 1, "orthonormal input"),
        "H1",
        True,
        "published H1",
    )
    zero_mode = emit_zero_mode(source, mode, "psi")
    assert zero_mode.representation == representation
    line = WilsonLine("Z2", group, 2, (("singlet", 0), ("odd", 1)))
    projection = WilsonLineProjection(line, {"singlet": 0, "odd": 1}, "finite character input")
    equivariant = EquivariantProjection(2, {"H1": 0}, "quotient character input")
    compiler = CohomologySpectrumCompiler(2, projection, equivariant_projection=equivariant)
    assert compiler.compile((source,))[0].multiplicity == 3
    assert compiler.check_index(source).consistent
    assert ModeOrthogonality(("H1-mode",), {("H1-mode", "H1-mode"): 1}, "L2", "input").orthonormal
    assert mode.provenance == source.provenance
    assert manifold.dimension == 6


def test_reduction_terms_preserve_frame_source_basis_and_moduli_identity() -> None:
    point = ModuliPoint("p", ("T",), "reduction point")
    context = ReductionContext(
        "Schoen-p",
        "X6-p",
        "Vvis-p",
        "Vhid-p",
        "gX-p",
        point,
        "reduction context",
    )
    basis = Basis("H2", ("J",))
    term = ReductionTerm(
        "Planck",
        "ten-dimensional Einstein term",
        "integral_X exp(-2 phi) vol_X",
        basis,
        context,
        "alpha_prime^0",
        "Einstein frame",
        "M_Pl^2",
        ("Ricci-flat internal metric",),
        "reduction certificate",
    )
    package = DimensionalReductionPackage(context, string_to_einstein_frame(), (term,), "package")
    assert package.unresolved_dependencies == ("Ricci-flat internal metric",)
    assert package.frame_transformation.string_to_einstein
    assert term.combine(term).context == context
    other_point = ModuliPoint("q", ("T",), "other reduction point")
    other_context = ReductionContext(
        "Schoen-q", "X6-q", "Vvis-q", "Vhid-q", "gX-q", other_point, "other context"
    )
    other = ReductionTerm(
        "other",
        "ten-dimensional term",
        "different integral",
        basis,
        other_context,
        "alpha_prime^0",
        "Einstein frame",
        "other",
        (),
        "other certificate",
    )
    with pytest.raises(IncompatibleConvention):
        term.combine(other)


def test_compactification_conditions_keep_geometry_and_solution_status_distinct() -> None:
    manifold = _internal()
    complex_structure = ComplexStructure(manifold, True, provenance="benchmark complex structure")
    kahler = KahlerForm(
        DifferentialForm(manifold, 2, (((0, 1), 1), ((2, 3), 1), ((4, 5), 1))),
        True,
        True,
        "benchmark Kahler form",
    )
    hermitian = HermitianStructure(complex_structure, kahler, True, "benchmark Hermitian structure")
    kahler_structure = KahlerStructure(hermitian, True, "dJ=0", "benchmark Kahler structure")
    volume = HolomorphicVolumeForm(
        DifferentialForm(manifold, 3, (((0, 1, 2), 1),)), True, True, "benchmark volume form"
    )
    structure = CalabiYauStructure(
        kahler_structure, volume, True, "explicit_solution", "benchmark compactification"
    )
    assert structure.certified
    assert four_plus_six_ansatz().total_dimension == 10


def test_n1_terms_require_one_moduli_point_and_positive_kinetic_data() -> None:
    point = ModuliPoint("p", ("T",), "benchmark moduli")

    def expression(text: str) -> EffectiveExpression:
        return EffectiveExpression(text, "benchmark", ("input",), point, "tree", "Einstein")

    kahler = KaehlerPotential(expression("K"), ("T",))
    superpotential = Superpotential(expression("W"), ("T",))
    gauge = GaugeKineticMatrix(("U(1)",), {("U(1)", "U(1)"): expression("f")})
    moment = MomentMap("U(1)", expression("D"))
    f_term = FTermPotential.from_data(kahler, superpotential)
    d_term = DTermPotential.from_data(gauge, (moment,))
    potential = ScalarPotential.from_terms(f_term, d_term)
    assert potential.expression.moduli_point == point
    assert KineticMatrix(
        "K_matter", Matrix(((1, 0), (0, 2))), point, "metric input"
    ).positive_definite
    other = ModuliPoint("q", ("T",), "other point")
    with pytest.raises(IncompatibleConvention):
        expression("K").combine(
            EffectiveExpression("other", "other", ("input",), other, "tree", "Einstein")
        )


def test_anomaly_package_separates_local_and_integrated_gates() -> None:
    geometry = schoen_geometry()
    group = GaugeGroup.simple("E8", 8, 248)
    fields = default_heterotic_field_content(group, group)
    package = differential_anomaly_package(geometry, fields.visible_connection)
    assert package.integrated_gate
    assert not package.local_gate
    assert not package.resolved


def test_schoen_effective_boundary_and_reality_fail_closed() -> None:
    state = schoen_effective_action()
    assert state.ten_dimensional_action.mass_dimensions_valid
    assert state.visible_carrier.spectrum.standard_model == state.observable_spectrum
    assert state.symbolic_slots.K.moduli_point == state.symbolic_slots.W.moduli_point
    assert state.dependency_chain() == (
        "normalized four-dimensional effective action",
        "one common compactification point",
    )
    assert SCHOEN_EFFECTIVE_MISSING_CHAIN[-1] == "controlled common vacuum"
    assert assemble_schoen_effective_action().geometry == state.geometry
    with pytest.raises(MissingPhysicalInput):
        request_complete_effective_action(state)
    with pytest.raises(MissingPhysicalInput):
        request_normalized_four_dimensional_effective_action()
