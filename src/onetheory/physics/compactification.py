"""Exact compactification geometry, supersymmetry, and mode-reduction machinery.

Owns:
    Product and warped ten-to-four ansaetze, complex/Hermitian/Kähler/Calabi–Yau
    structure records, holomorphic and HYM conditions, stability chambers, internal
    mode decompositions, explicit zero-mode sources, KK towers, truncation manifests,
    Wilson-line projections, and cohomology-to-spectrum compilation.

Depends on:
    Exact spacetime forms and conventions, exact geometry classes, gauge/matter
    metadata, heterotic field conventions, and core fail-closed errors.

Must not:
    Prove existence from a topological class, solve a metric or HYM equation without
    supplied data, infer zero modes from dimensions, select a carrier from observations,
    or import a Schoen model or research experiment.

Phase 0:
    Generic symbolic reduction contracts are implemented; numerical internal fields,
    missing cocycles, and carrier-specific cohomology remain explicit inputs.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import NoReturn

from onetheory.core.errors import IncompatibleConvention, MissingPhysicalInput
from onetheory.math.geometry import Basis, VectorBundle
from onetheory.math.numbers import Rational, coerce_rational
from onetheory.physics.gauge import GaugeGroup, Representation
from onetheory.physics.matter import Chirality
from onetheory.physics.spacetime import (
    DifferentialForm,
    Metric,
    MetricSignature,
    Orientation,
    PseudoRiemannianManifold,
    SpacetimeConvention,
)
from onetheory.physics.strings import FrameConvention, FrameTransformation, WilsonLine
from onetheory.physics.vacuum import ModuliPoint


@dataclass(frozen=True, slots=True)
class CompactificationAnsatz:
    """A direct product or warped ten-dimensional reduction ansatz."""

    external_dimension: int
    internal_dimension: int
    warped: bool
    warp_factor: str | None
    frame: FrameConvention
    external_coordinates: tuple[str, ...]
    internal_coordinates: tuple[str, ...]
    provenance: str

    def __init__(
        self,
        external_dimension: int = 4,
        internal_dimension: int = 6,
        warped: bool = False,
        warp_factor: str | None = None,
        frame: FrameConvention = FrameConvention.STRING,
        external_coordinates: Iterable[str] = ("x0", "x1", "x2", "x3"),
        internal_coordinates: Iterable[str] = ("y0", "y1", "y2", "y3", "y4", "y5"),
        provenance: str = "ten-to-four compactification ansatz",
    ) -> None:
        external = tuple(external_coordinates)
        internal = tuple(internal_coordinates)
        if (
            isinstance(external_dimension, bool)
            or not isinstance(external_dimension, int)
            or external_dimension < 1
            or isinstance(internal_dimension, bool)
            or not isinstance(internal_dimension, int)
            or internal_dimension < 1
            or external_dimension + internal_dimension != 10
            or len(external) != external_dimension
            or len(internal) != internal_dimension
            or not provenance.strip()
        ):
            raise ValueError("compactification ansaetze must partition ten dimensions")
        if warped and (warp_factor is None or not warp_factor.strip()):
            raise ValueError("warped ansaetze require an explicit warp factor")
        if not warped and warp_factor is not None:
            raise ValueError("unwarped ansaetze cannot carry a warp factor")
        object.__setattr__(self, "external_dimension", external_dimension)
        object.__setattr__(self, "internal_dimension", internal_dimension)
        object.__setattr__(self, "warped", warped)
        object.__setattr__(self, "warp_factor", warp_factor)
        object.__setattr__(self, "frame", frame)
        object.__setattr__(self, "external_coordinates", external)
        object.__setattr__(self, "internal_coordinates", internal)
        object.__setattr__(self, "provenance", provenance)

    @property
    def total_dimension(self) -> int:
        """Return the ten-dimensional total explicitly partitioned by the ansatz."""

        return self.external_dimension + self.internal_dimension


def four_plus_six_ansatz(
    warped: bool = False,
    warp_factor: str | None = None,
    frame: FrameConvention = FrameConvention.STRING,
) -> CompactificationAnsatz:
    """Construct the standard four-dimensional plus six-dimensional ansatz."""

    return CompactificationAnsatz(4, 6, warped, warp_factor, frame)


def _internal_manifold(name: str = "X6") -> PseudoRiemannianManifold:
    """Construct a six-dimensional convention record without selecting a metric solution."""

    convention = SpacetimeConvention(
        MetricSignature((1, 1, 1, 1, 1, 1)),
        Orientation(range(6)),
    )
    return PseudoRiemannianManifold(name, convention, Metric(convention))


@dataclass(frozen=True, slots=True)
class ComplexStructure:
    """An integrability record for an even-dimensional internal manifold."""

    manifold: PseudoRiemannianManifold
    integrable: bool
    operator_name: str
    provenance: str

    def __init__(
        self,
        manifold: PseudoRiemannianManifold,
        integrable: bool,
        operator_name: str = "J",
        provenance: str = "complex-structure input",
    ) -> None:
        if manifold.dimension % 2 or not operator_name.strip() or not provenance.strip():
            raise ValueError("complex structures require an even manifold and provenance")
        object.__setattr__(self, "manifold", manifold)
        object.__setattr__(self, "integrable", integrable)
        object.__setattr__(self, "operator_name", operator_name)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class KahlerForm:
    """A degree-two internal form with positivity and closure status."""

    form: DifferentialForm
    positive: bool
    closed: bool
    provenance: str

    def __init__(
        self,
        form: DifferentialForm,
        positive: bool,
        closed: bool,
        provenance: str = "Kähler-form input",
    ) -> None:
        if form.degree != 2 or not provenance.strip():
            raise ValueError("Kähler forms must have degree two and provenance")
        object.__setattr__(self, "form", form)
        object.__setattr__(self, "positive", positive)
        object.__setattr__(self, "closed", closed)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class HermitianStructure:
    """A complex manifold with an explicitly supplied compatible Hermitian form."""

    complex_structure: ComplexStructure
    kahler_form: KahlerForm
    compatible: bool
    provenance: str

    def __post_init__(self) -> None:
        if self.kahler_form.form.manifold != self.complex_structure.manifold:
            raise IncompatibleConvention("Hermitian data use different internal manifolds")
        if not self.provenance.strip():
            raise ValueError("Hermitian structures require provenance")


@dataclass(frozen=True, slots=True)
class KahlerStructure:
    """A Hermitian structure with an explicitly verified closed Kähler form."""

    hermitian: HermitianStructure
    kahler: bool
    closure_certificate: str
    provenance: str

    def __post_init__(self) -> None:
        if not self.hermitian.compatible or not self.hermitian.kahler_form.closed:
            raise ValueError("Kähler structures require compatible closed Hermitian data")
        if not self.closure_certificate.strip() or not self.provenance.strip():
            raise ValueError("Kähler structures require exact closure provenance")


@dataclass(frozen=True, slots=True)
class HolomorphicVolumeForm:
    """A nowhere-vanishing internal holomorphic top-form record."""

    form: DifferentialForm
    holomorphic: bool
    nowhere_vanishing: bool
    provenance: str

    def __init__(
        self,
        form: DifferentialForm,
        holomorphic: bool,
        nowhere_vanishing: bool,
        provenance: str = "holomorphic volume-form input",
    ) -> None:
        if not provenance.strip():
            raise ValueError("holomorphic volume forms require provenance")
        object.__setattr__(self, "form", form)
        object.__setattr__(self, "holomorphic", holomorphic)
        object.__setattr__(self, "nowhere_vanishing", nowhere_vanishing)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class CalabiYauStructure:
    """A Calabi–Yau structure distinguished from an existence theorem or solution."""

    kahler_structure: KahlerStructure
    holomorphic_volume: HolomorphicVolumeForm
    ricci_flat: bool
    status: str
    provenance: str

    def __post_init__(self) -> None:
        if (
            self.holomorphic_volume.form.manifold
            != self.kahler_structure.hermitian.complex_structure.manifold
        ):
            raise IncompatibleConvention("Calabi–Yau forms use different internal manifolds")
        if self.status not in {"theorem", "explicit_solution", "numerical_field", "unresolved"}:
            raise ValueError("Calabi–Yau status must distinguish theorem and field evidence")
        if not self.provenance.strip():
            raise ValueError("Calabi–Yau structures require provenance")

    @property
    def certified(self) -> bool:
        """Return whether all supplied structure conditions are marked true."""

        return (
            self.kahler_structure.kahler
            and self.holomorphic_volume.holomorphic
            and self.holomorphic_volume.nowhere_vanishing
            and self.ricci_flat
        )


@dataclass(frozen=True, slots=True)
class HolomorphicBundle:
    """A bundle with explicit holomorphic and connection-status metadata."""

    bundle: VectorBundle
    holomorphic: bool
    connection: object | None
    provenance: str

    def __post_init__(self) -> None:
        if not self.provenance.strip():
            raise ValueError("holomorphic bundles require provenance")

    @property
    def has_connection(self) -> bool:
        """Return whether a connection was supplied independently of topology."""

        return self.connection is not None


@dataclass(frozen=True, slots=True)
class HYMCondition:
    """The two exact Hermitian Yang–Mills equations for one bundle."""

    bundle: HolomorphicBundle
    f02_zero: bool
    kahler_contraction_zero: bool
    connection_name: str | None
    provenance: str

    def __post_init__(self) -> None:
        if not self.provenance.strip():
            raise ValueError("HYM conditions require provenance")
        if self.connection_name is None and self.bundle.connection is not None:
            raise ValueError("a supplied bundle connection requires a named HYM connection")

    @property
    def satisfied(self) -> bool:
        """Return whether both equations are certified for the supplied connection."""

        return (
            self.bundle.holomorphic
            and self.bundle.has_connection
            and self.f02_zero
            and self.kahler_contraction_zero
        )


@dataclass(frozen=True, slots=True)
class SlopeRequirement:
    """A zero-slope and polystability requirement for a bundle chamber."""

    bundle: HolomorphicBundle
    slope: Rational
    polystable: bool
    provenance: str

    def __init__(
        self,
        bundle: HolomorphicBundle,
        slope: object,
        polystable: bool,
        provenance: str,
    ) -> None:
        if not provenance.strip():
            raise ValueError("slope requirements require provenance")
        object.__setattr__(self, "bundle", bundle)
        object.__setattr__(self, "slope", coerce_rational(slope))
        object.__setattr__(self, "polystable", polystable)
        object.__setattr__(self, "provenance", provenance)

    @property
    def satisfied(self) -> bool:
        """Return whether zero slope and polystability are both supplied."""

        return self.slope == 0 and self.polystable


@dataclass(frozen=True, slots=True)
class KillingSpinorCondition:
    """An internal Killing-spinor condition with explicit torsion and status."""

    equation: str
    spinor_name: str
    satisfied: bool
    provenance: str

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.equation, self.spinor_name, self.provenance)):
            raise ValueError("Killing-spinor conditions require complete symbolic metadata")


@dataclass(frozen=True, slots=True)
class SupersymmetryConditions:
    """The combined geometric, HYM, and Killing-spinor compactification contract."""

    calabi_yau: CalabiYauStructure
    visible_hym: HYMCondition
    hidden_hym: HYMCondition
    killing_spinor: KillingSpinorCondition

    @property
    def satisfied(self) -> bool:
        """Return whether all supplied supersymmetry conditions pass."""

        return (
            self.calabi_yau.certified
            and self.visible_hym.satisfied
            and self.hidden_hym.satisfied
            and self.killing_spinor.satisfied
        )


@dataclass(frozen=True, slots=True)
class CompatibleChamber:
    """A chamber requiring compatible visible and hidden HYM slope data."""

    label: str
    visible: SlopeRequirement
    hidden: SlopeRequirement
    moduli_point: str
    provenance: str

    def __post_init__(self) -> None:
        if not self.label.strip() or not self.moduli_point.strip() or not self.provenance.strip():
            raise ValueError("compatible chambers require label, moduli point, and provenance")

    @property
    def compatible(self) -> bool:
        """Return whether both bundles share the exact zero-slope chamber."""

        return self.visible.satisfied and self.hidden.satisfied


@dataclass(frozen=True, slots=True)
class CompactificationState:
    """One compactification ansatz and its explicitly supplied internal structures."""

    ansatz: CompactificationAnsatz
    internal_manifold: PseudoRiemannianManifold
    geometry: CalabiYauStructure
    visible_bundle: HolomorphicBundle
    hidden_bundle: HolomorphicBundle
    supersymmetry: SupersymmetryConditions
    chamber: CompatibleChamber
    moduli_point: str
    provenance: str

    def __post_init__(self) -> None:
        if self.internal_manifold.dimension != self.ansatz.internal_dimension:
            raise IncompatibleConvention("internal manifold dimension differs from ansatz")
        if not self.moduli_point.strip() or not self.provenance.strip():
            raise ValueError("compactification states require a named moduli point")
        if (
            self.geometry.kahler_structure.hermitian.complex_structure.manifold
            != self.internal_manifold
        ):
            raise IncompatibleConvention("compactification geometry differs from internal manifold")
        if self.chamber.moduli_point != self.moduli_point:
            raise IncompatibleConvention("compactification structures use different moduli points")


@dataclass(frozen=True, slots=True)
class TensorDecomposition:
    """A typed external/internal index decomposition for one ten-dimensional tensor."""

    field_name: str
    external_rank: int
    internal_rank: int
    external_dimension: int
    internal_dimension: int
    provenance: str

    def __init__(
        self,
        field_name: str,
        external_rank: int,
        internal_rank: int,
        external_dimension: int = 4,
        internal_dimension: int = 6,
        provenance: str = "tensor decomposition input",
    ) -> None:
        if (
            not field_name.strip()
            or external_rank < 0
            or internal_rank < 0
            or external_dimension + internal_dimension != 10
            or not provenance.strip()
        ):
            raise ValueError("tensor decompositions require a ten-dimensional partition")
        object.__setattr__(self, "field_name", field_name)
        object.__setattr__(self, "external_rank", external_rank)
        object.__setattr__(self, "internal_rank", internal_rank)
        object.__setattr__(self, "external_dimension", external_dimension)
        object.__setattr__(self, "internal_dimension", internal_dimension)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class InternalEigenvalueProblem:
    """An internal operator problem whose eigenvalues must be supplied or solved."""

    operator_name: str
    manifold: PseudoRiemannianManifold
    equation: str
    boundary_conditions: str
    provenance: str

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (
                self.operator_name,
                self.equation,
                self.boundary_conditions,
                self.provenance,
            )
        ):
            raise ValueError("internal eigenvalue problems require complete equations")


@dataclass(frozen=True, slots=True)
class ModeNormalization:
    """A declared internal mode normalization and overlap value."""

    convention: str
    norm: Rational
    provenance: str

    def __init__(self, convention: str, norm: object, provenance: str) -> None:
        if not convention.strip() or not provenance.strip():
            raise ValueError("mode normalizations require convention and provenance")
        normalized = coerce_rational(norm)
        if normalized <= 0:
            raise ValueError("mode norms must be positive")
        object.__setattr__(self, "convention", convention)
        object.__setattr__(self, "norm", normalized)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class HarmonicMode:
    """One explicit harmonic or massive internal mode."""

    name: str
    field_kind: str
    form_degree: int | None
    eigenvalue: Rational
    normalization: ModeNormalization
    source: str
    is_harmonic: bool
    provenance: str

    def __init__(
        self,
        name: str,
        field_kind: str,
        form_degree: int | None,
        eigenvalue: object,
        normalization: ModeNormalization,
        source: str,
        is_harmonic: bool,
        provenance: str,
    ) -> None:
        if any(not value.strip() for value in (name, field_kind, source, provenance)):
            raise ValueError("internal modes require explicit source and provenance")
        if form_degree is not None and (form_degree < 0 or form_degree > 6):
            raise ValueError("internal form degrees must lie between zero and six")
        normalized = coerce_rational(eigenvalue)
        if normalized < 0 or (is_harmonic and normalized != 0):
            raise ValueError("harmonic modes require zero eigenvalue")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "field_kind", field_kind)
        object.__setattr__(self, "form_degree", form_degree)
        object.__setattr__(self, "eigenvalue", normalized)
        object.__setattr__(self, "normalization", normalization)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "is_harmonic", is_harmonic)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class ModeExpansion:
    """A finite explicit expansion of one higher-dimensional field."""

    field_name: str
    decomposition: TensorDecomposition
    modes: tuple[HarmonicMode, ...]
    coefficient_names: tuple[str, ...]
    provenance: str

    def __post_init__(self) -> None:
        if len(self.modes) != len(self.coefficient_names) or not self.provenance.strip():
            raise ValueError("mode expansions require one coefficient per explicit mode")


@dataclass(frozen=True, slots=True)
class MassiveKKTower:
    """A declared tower of massive modes for one internal eigenproblem."""

    problem: InternalEigenvalueProblem
    modes: tuple[HarmonicMode, ...]
    cutoff: Rational | None
    provenance: str

    def __post_init__(self) -> None:
        if any(mode.is_harmonic for mode in self.modes):
            raise ValueError("massive KK towers cannot contain harmonic zero modes")
        if self.cutoff is not None and self.cutoff <= 0:
            raise ValueError("KK cutoffs must be positive")
        if not self.provenance.strip():
            raise ValueError("KK towers require provenance")


@dataclass(frozen=True, slots=True)
class CohomologySource:
    """An explicit bundle-valued cohomology input for zero-mode emission."""

    name: str
    bundle_name: str
    degree: int
    representation: Representation
    multiplicity: int
    chirality: Chirality
    index_contribution: int
    provenance: str

    def __init__(
        self,
        name: str,
        bundle_name: str,
        degree: int,
        representation: Representation,
        multiplicity: int,
        chirality: Chirality,
        index_contribution: int,
        provenance: str,
    ) -> None:
        if any(not value.strip() for value in (name, bundle_name, provenance)):
            raise ValueError("cohomology sources require names and provenance")
        if degree < 0 or multiplicity < 0:
            raise ValueError("cohomology degrees and multiplicities must be nonnegative")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "bundle_name", bundle_name)
        object.__setattr__(self, "degree", degree)
        object.__setattr__(self, "representation", representation)
        object.__setattr__(self, "multiplicity", multiplicity)
        object.__setattr__(self, "chirality", chirality)
        object.__setattr__(self, "index_contribution", index_contribution)
        object.__setattr__(self, "provenance", provenance)

    @property
    def conjugate_representation(self) -> Representation:
        """Return the representation conjugate to this explicit source."""

        return self.representation.conjugate_representation()


@dataclass(frozen=True, slots=True)
class ZeroMode:
    """A four-dimensional field emitted only from one explicit internal mode source."""

    name: str
    source: CohomologySource
    mode: HarmonicMode
    representation: Representation
    chirality: Chirality
    provenance: str

    def __post_init__(self) -> None:
        if not self.mode.is_harmonic or self.mode.source != self.source.name:
            raise ValueError("zero modes require a matching explicit harmonic source")
        if (
            self.representation != self.source.representation
            or self.chirality != self.source.chirality
        ):
            raise IncompatibleConvention("zero mode and cohomology source metadata differ")
        if not self.provenance.strip():
            raise ValueError("zero modes require provenance")


def emit_zero_mode(source: CohomologySource, mode: HarmonicMode, name: str) -> ZeroMode:
    """Emit one zero mode only when its harmonic source is explicit."""

    return ZeroMode(name, source, mode, source.representation, source.chirality, source.provenance)


@dataclass(frozen=True, slots=True)
class ModeOrthogonality:
    """An exact overlap table for a declared mode basis."""

    mode_names: tuple[str, ...]
    overlaps: tuple[tuple[tuple[str, str], Rational], ...]
    normalization: str
    provenance: str

    def __init__(
        self,
        mode_names: Iterable[str],
        overlaps: Mapping[tuple[str, str], object],
        normalization: str,
        provenance: str,
    ) -> None:
        names = tuple(mode_names)
        if (
            not names
            or len(set(names)) != len(names)
            or not normalization.strip()
            or not provenance.strip()
        ):
            raise ValueError("mode orthogonality requires unique names and provenance")
        values = tuple(sorted((key, coerce_rational(value)) for key, value in overlaps.items()))
        if any(left not in names or right not in names for (left, right), _ in values):
            raise ValueError("orthogonality table contains an undeclared mode")
        object.__setattr__(self, "mode_names", names)
        object.__setattr__(self, "overlaps", values)
        object.__setattr__(self, "normalization", normalization)
        object.__setattr__(self, "provenance", provenance)

    def overlap(self, left: str, right: str) -> Rational:
        """Return one exact mode overlap."""

        return dict(self.overlaps).get((left, right), Rational(0))

    @property
    def orthonormal(self) -> bool:
        """Return whether the supplied overlap table is the identity."""

        return all(
            self.overlap(left, right) == (1 if left == right else 0)
            for left in self.mode_names
            for right in self.mode_names
        )


@dataclass(frozen=True, slots=True)
class TruncationManifest:
    """A reproducible finite truncation of explicit internal modes."""

    field_name: str
    retained_modes: tuple[str, ...]
    omitted_modes: tuple[str, ...]
    cutoff: Rational | None
    source: str
    provenance: str

    def __post_init__(self) -> None:
        if not self.field_name.strip() or not self.source.strip() or not self.provenance.strip():
            raise ValueError("truncation manifests require field source and provenance")
        if set(self.retained_modes) & set(self.omitted_modes):
            raise ValueError("a truncation cannot both retain and omit a mode")


@dataclass(frozen=True, slots=True)
class WilsonLineProjection:
    """A finite character filter applied to explicit mode labels."""

    wilson_line: WilsonLine
    labels: tuple[tuple[str, int], ...]
    provenance: str

    def __init__(self, wilson_line: WilsonLine, labels: Mapping[str, int], provenance: str) -> None:
        if not provenance.strip():
            raise ValueError("Wilson-line projections require provenance")
        values = tuple(sorted(labels.items()))
        if any(
            label not in dict(wilson_line.characters) or character != wilson_line.character(label)
            for label, character in values
        ):
            raise ValueError("projection labels must use the declared Wilson-line characters")
        object.__setattr__(self, "wilson_line", wilson_line)
        object.__setattr__(self, "labels", values)
        object.__setattr__(self, "provenance", provenance)

    def survives(self, label: str, required_character: int = 0) -> bool:
        """Return whether a mode label passes the specified invariant character."""

        character = dict(self.labels).get(label)
        return (
            character is not None
            and character % self.wilson_line.order == required_character % self.wilson_line.order
        )

    def surviving_labels(self, required_character: int = 0) -> tuple[str, ...]:
        """Return deterministic labels passing the finite projection."""

        return tuple(label for label, _ in self.labels if self.survives(label, required_character))


@dataclass(frozen=True, slots=True)
class BranchingRule:
    """An explicit parent-to-commutant representation branching record."""

    parent: GaugeGroup
    commutant: GaugeGroup
    source_representation: str
    branches: tuple[tuple[str, int], ...]
    provenance: str

    def __post_init__(self) -> None:
        if not self.source_representation.strip() or not self.provenance.strip():
            raise ValueError("branching rules require source and provenance")


@dataclass(frozen=True, slots=True)
class IndexTheoremCheck:
    """A consistency comparison between cohomology multiplicities and an index."""

    source_name: str
    computed_index: int
    declared_index: int
    provenance: str

    @property
    def consistent(self) -> bool:
        """Return whether the explicit multiplicity index agrees."""

        return self.computed_index == self.declared_index


@dataclass(frozen=True, slots=True)
class CompiledSpectrumEntry:
    """One compiled four-dimensional representation and its physical source."""

    source_name: str
    representation: Representation
    chirality: Chirality
    multiplicity: int
    projected: bool
    provenance: str


@dataclass(frozen=True, slots=True)
class CohomologySpectrumCompiler:
    """Compile only explicit cohomology sources through explicit finite projections."""

    quotient_order: int
    equivariant_projection: EquivariantProjection | None
    wilson_projection: WilsonLineProjection | None
    branching_rules: tuple[BranchingRule, ...]
    provenance: str

    def __init__(
        self,
        quotient_order: int,
        wilson_projection: WilsonLineProjection | None = None,
        branching_rules: Iterable[BranchingRule] = (),
        provenance: str = "cohomology-to-spectrum compiler",
        equivariant_projection: EquivariantProjection | None = None,
    ) -> None:
        if (
            isinstance(quotient_order, bool)
            or not isinstance(quotient_order, int)
            or quotient_order < 1
        ):
            raise ValueError("quotient order must be positive")
        if not provenance.strip():
            raise ValueError("spectrum compilers require provenance")
        object.__setattr__(self, "quotient_order", quotient_order)
        object.__setattr__(self, "equivariant_projection", equivariant_projection)
        object.__setattr__(self, "wilson_projection", wilson_projection)
        object.__setattr__(self, "branching_rules", tuple(branching_rules))
        object.__setattr__(self, "provenance", provenance)

    def compile(self, sources: Iterable[CohomologySource]) -> tuple[CompiledSpectrumEntry, ...]:
        """Compile explicit sources; no representation dimension is treated as a multiplicity."""

        entries: list[CompiledSpectrumEntry] = []
        for source in sources:
            projected = True
            if self.equivariant_projection is not None:
                projected = self.equivariant_projection.survives(source.name)
            if self.wilson_projection is not None:
                projected = projected and any(
                    self.wilson_projection.survives(label)
                    for label in (source.representation.name, source.name)
                )
            entries.append(
                CompiledSpectrumEntry(
                    source.name,
                    source.representation,
                    source.chirality,
                    source.multiplicity if projected else 0,
                    projected,
                    source.provenance,
                )
            )
        return tuple(entries)

    def check_index(self, source: CohomologySource) -> IndexTheoremCheck:
        """Check an explicit source's declared index against its chirality count."""

        signed = source.multiplicity if source.chirality is Chirality.LEFT else -source.multiplicity
        return IndexTheoremCheck(source.name, signed, source.index_contribution, source.provenance)


@dataclass(frozen=True, slots=True)
class EquivariantProjection:
    """An explicit finite quotient-character projection."""

    group_order: int
    characters: tuple[tuple[str, int], ...]
    provenance: str

    def __init__(
        self,
        group_order: int,
        characters: Mapping[str, int],
        provenance: str,
    ) -> None:
        if isinstance(group_order, bool) or not isinstance(group_order, int) or group_order < 1:
            raise ValueError("equivariant group order must be positive")
        if not provenance.strip() or any(
            not label.strip() or isinstance(value, bool) or not isinstance(value, int)
            for label, value in characters.items()
        ):
            raise ValueError("equivariant characters require integral labels and provenance")
        object.__setattr__(self, "group_order", group_order)
        object.__setattr__(self, "characters", tuple(sorted(characters.items())))
        object.__setattr__(self, "provenance", provenance)

    def survives(self, label: str) -> bool:
        """Return whether one declared character is invariant under the quotient."""

        character = dict(self.characters).get(label)
        return character is not None and character % self.group_order == 0


@dataclass(frozen=True, slots=True)
class GaugeCommutant:
    """An explicit unbroken gauge group and parent-to-commutant map."""

    parent: GaugeGroup
    unbroken: GaugeGroup
    branching: tuple[BranchingRule, ...]
    provenance: str

    def __post_init__(self) -> None:
        if not self.provenance.strip():
            raise ValueError("gauge commutants require provenance")
        if any(
            rule.parent != self.parent or rule.commutant != self.unbroken for rule in self.branching
        ):
            raise IncompatibleConvention("branching rules use a different gauge commutant")


@dataclass(frozen=True, slots=True)
class ReductionContext:
    """Identity metadata preventing reduction terms from crossing physical states."""

    compactification_point: str
    geometry_id: str
    visible_bundle_id: str
    hidden_bundle_id: str
    metric_id: str
    moduli_point: ModuliPoint
    provenance: str

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (
                self.compactification_point,
                self.geometry_id,
                self.visible_bundle_id,
                self.hidden_bundle_id,
                self.metric_id,
                self.provenance,
            )
        ):
            raise ValueError("reduction contexts require all state identities")


@dataclass(frozen=True, slots=True)
class ReductionTerm:
    """One dimensionally reduced term with complete source and integration metadata."""

    name: str
    source_ten_dimensional_term: str
    internal_integral: str
    basis: Basis
    context: ReductionContext
    approximation_order: str
    normalization: str
    expression: str
    unresolved_dependencies: tuple[str, ...]
    provenance: str

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (
                self.name,
                self.source_ten_dimensional_term,
                self.internal_integral,
                self.approximation_order,
                self.normalization,
                self.expression,
                self.provenance,
            )
        ):
            raise ValueError("reduction terms require source, integral, basis, and provenance")
        if any(not value.strip() for value in self.unresolved_dependencies):
            raise ValueError("reduction dependencies require names")

    def combine(self, other: ReductionTerm) -> ReductionTerm:
        """Combine terms only when every compactification identity is equal."""

        if self.context != other.context:
            raise IncompatibleConvention(
                "reduction terms use different geometry, bundles, metrics, or moduli"
            )
        if self.basis != other.basis or self.normalization != other.normalization:
            raise IncompatibleConvention("reduction terms use different bases or normalizations")
        return ReductionTerm(
            f"{self.name}+{other.name}",
            f"{self.source_ten_dimensional_term}; {other.source_ten_dimensional_term}",
            f"{self.internal_integral}; {other.internal_integral}",
            self.basis,
            self.context,
            f"{self.approximation_order}; {other.approximation_order}",
            self.normalization,
            f"({self.expression}) + ({other.expression})",
            (*self.unresolved_dependencies, *other.unresolved_dependencies),
            f"{self.provenance}; {other.provenance}",
        )


@dataclass(frozen=True, slots=True)
class PlanckNormalization:
    """The four-dimensional gravitational normalization derived from one reduction term."""

    reduction_term: ReductionTerm
    four_dimensional_planck_symbol: str
    gravitational_constant_symbol: str

    def __post_init__(self) -> None:
        if (
            not self.four_dimensional_planck_symbol.strip()
            or not self.gravitational_constant_symbol.strip()
        ):
            raise ValueError("Planck normalization requires explicit symbols")


@dataclass(frozen=True, slots=True)
class ModuliKineticTerm:
    """A moduli kinetic term retaining its internal metric integral."""

    reduction_term: ReductionTerm
    moduli_names: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.moduli_names or any(not value.strip() for value in self.moduli_names):
            raise ValueError("moduli kinetic terms require named moduli")


@dataclass(frozen=True, slots=True)
class GaugeKineticFunction:
    """A gauge kinetic function derived from a named reduction term."""

    factor: str
    reduction_term: ReductionTerm

    def __post_init__(self) -> None:
        if not self.factor.strip():
            raise ValueError("gauge kinetic functions require a factor")


@dataclass(frozen=True, slots=True)
class MatterKineticMatrix:
    """A matter kinetic matrix prerequisite with explicit basis and reduction source."""

    field_names: tuple[str, ...]
    reduction_term: ReductionTerm

    def __post_init__(self) -> None:
        if not self.field_names or any(not value.strip() for value in self.field_names):
            raise ValueError("matter kinetic matrices require field names")


@dataclass(frozen=True, slots=True)
class HolomorphicCoupling:
    """A reduced holomorphic coupling with its source term and unresolved inputs."""

    name: str
    reduction_term: ReductionTerm

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("holomorphic couplings require a name")


@dataclass(frozen=True, slots=True)
class AxionicCoupling:
    """A reduced axion/gauge coupling with explicit internal origin."""

    axion_name: str
    gauge_factor: str
    reduction_term: ReductionTerm

    def __post_init__(self) -> None:
        if not self.axion_name.strip() or not self.gauge_factor.strip():
            raise ValueError("axionic couplings require axion and gauge names")


@dataclass(frozen=True, slots=True)
class ThresholdPlaceholder:
    """A threshold slot accepted only when backed by a named calculation."""

    name: str
    named_calculation: str
    reduction_term: ReductionTerm

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.named_calculation.strip():
            raise ValueError("threshold placeholders require a named calculation")


@dataclass(frozen=True, slots=True)
class DimensionalReductionPackage:
    """All reduced terms from one common compactification context."""

    context: ReductionContext
    frame_transformation: FrameTransformation
    terms: tuple[ReductionTerm, ...]
    provenance: str

    def __post_init__(self) -> None:
        if not self.terms or not self.provenance.strip():
            raise ValueError("dimensional reduction packages require terms and provenance")
        if any(term.context != self.context for term in self.terms):
            raise IncompatibleConvention("reduction package mixes compactification states")

    @property
    def unresolved_dependencies(self) -> tuple[str, ...]:
        """Return deterministic unique prerequisites retained by all reduced terms."""

        return tuple(
            dict.fromkeys(
                dependency for term in self.terms for dependency in term.unresolved_dependencies
            )
        )


def dimensional_reduction(
    context: ReductionContext,
    frame_transformation: FrameTransformation,
    terms: Iterable[ReductionTerm],
    provenance: str,
) -> DimensionalReductionPackage:
    """Build one reduction package and reject terms from another physical state."""

    return DimensionalReductionPackage(
        context,
        frame_transformation,
        tuple(terms),
        provenance,
    )


def require_explicit_zero_mode_source(source: str) -> NoReturn:
    """Fail closed when a caller asks for a mode without an internal source."""

    raise MissingPhysicalInput(
        "internal zero mode", (source, "explicit harmonic or published cohomology input")
    )


__all__ = [
    "BranchingRule",
    "CalabiYauStructure",
    "CohomologySource",
    "CohomologySpectrumCompiler",
    "CompatibleChamber",
    "CompactificationAnsatz",
    "CompactificationState",
    "ComplexStructure",
    "CompiledSpectrumEntry",
    "DimensionalReductionPackage",
    "EquivariantProjection",
    "GaugeCommutant",
    "HYMCondition",
    "HarmonicMode",
    "HermitianStructure",
    "HolomorphicBundle",
    "HolomorphicVolumeForm",
    "IndexTheoremCheck",
    "InternalEigenvalueProblem",
    "KahlerForm",
    "KahlerStructure",
    "KillingSpinorCondition",
    "MassiveKKTower",
    "ModeExpansion",
    "ModeNormalization",
    "ModeOrthogonality",
    "MatterKineticMatrix",
    "ModuliKineticTerm",
    "PlanckNormalization",
    "ReductionContext",
    "ReductionTerm",
    "SlopeRequirement",
    "SupersymmetryConditions",
    "TensorDecomposition",
    "TruncationManifest",
    "ThresholdPlaceholder",
    "AxionicCoupling",
    "GaugeKineticFunction",
    "HolomorphicCoupling",
    "WilsonLineProjection",
    "ZeroMode",
    "emit_zero_mode",
    "four_plus_six_ansatz",
    "dimensional_reduction",
    "require_explicit_zero_mode_source",
]
