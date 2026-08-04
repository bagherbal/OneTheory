"""Convention-frozen ten-dimensional heterotic field and action records.

Owns:
    Ten-dimensional metric, dilaton, B/H fields, visible and hidden gauge
    connections, torsionful curvature, fermion metadata, frame conventions, and
    the supported-order bosonic heterotic action.

Depends on:
    Exact rational arithmetic, gauge-group labels, and no selected compactification
    or source-document imports.

Must not:
    Silently combine trace or torsion conventions, insert measured constants, claim a
    hidden bundle from topology, solve a worldsheet theory, or import research.

Phase 0:
    The supported symbolic ten-dimensional action is executable as a law record;
    field solutions and carrier coefficients remain explicit unresolved inputs.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from onetheory.math.numbers import Rational, coerce_rational
from onetheory.physics.gauge import GaugeGroup


@dataclass(frozen=True, slots=True)
class PublishedPhysicalInput:
    """A traceable published input without executable source-document imports."""

    identifier: str
    citation: str
    locator: str
    statement: str

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (self.identifier, self.citation, self.locator, self.statement)
        ):
            raise ValueError("published physical inputs require complete provenance")


@dataclass(frozen=True, slots=True, init=False)
class CompactificationSpace:
    """Exact topological metadata for a compactification space."""

    name: str
    complex_dimension: int
    cover_degree: int
    fundamental_group_order: int
    input_record: PublishedPhysicalInput

    def __init__(
        self,
        name: str,
        complex_dimension: int,
        cover_degree: int,
        fundamental_group_order: int,
        input_record: PublishedPhysicalInput,
    ) -> None:
        if not name.strip():
            raise ValueError("a compactification requires a name")
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 1
            for value in (complex_dimension, cover_degree, fundamental_group_order)
        ):
            raise ValueError("compactification dimensions and orders must be positive")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "complex_dimension", complex_dimension)
        object.__setattr__(self, "cover_degree", cover_degree)
        object.__setattr__(self, "fundamental_group_order", fundamental_group_order)
        object.__setattr__(self, "input_record", input_record)


class BundleStatus(StrEnum):
    """Status labels that prevent required classes from becoming bundles."""

    PUBLISHED = "published"
    EXACT_CARRIER_RESULT = "exact_carrier_result"
    REQUIRED_TOPOLOGICAL_CLASS = "required_topological_class"


@dataclass(frozen=True, slots=True, init=False)
class Bundle:
    """A typed bundle descriptor with explicit status and Chern coordinates."""

    name: str
    rank: int
    structure_group: GaugeGroup
    c1: tuple[Rational, ...]
    c2: tuple[Rational, ...]
    c3: Rational
    status: BundleStatus

    def __init__(
        self,
        name: str,
        rank: int,
        structure_group: GaugeGroup,
        c1: Iterable[object],
        c2: Iterable[object],
        c3: object,
        status: BundleStatus,
    ) -> None:
        first = tuple(coerce_rational(value) for value in c1)
        second = tuple(coerce_rational(value) for value in c2)
        if not name.strip() or not first or len(first) != len(second):
            raise ValueError("bundle Chern coordinates must be nonempty and parallel")
        if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1:
            raise ValueError("bundle rank must be positive")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "rank", rank)
        object.__setattr__(self, "structure_group", structure_group)
        object.__setattr__(self, "c1", first)
        object.__setattr__(self, "c2", second)
        object.__setattr__(self, "c3", coerce_rational(c3))
        object.__setattr__(self, "status", status)


@dataclass(frozen=True, slots=True, init=False)
class WilsonLine:
    """A finite exact Wilson-line character assignment."""

    name: str
    gauge_group: GaugeGroup
    order: int
    characters: tuple[tuple[str, int], ...]

    def __init__(
        self,
        name: str,
        gauge_group: GaugeGroup,
        order: int,
        characters: Iterable[tuple[str, int]],
    ) -> None:
        values = tuple(characters)
        if not name.strip() or isinstance(order, bool) or not isinstance(order, int) or order < 2:
            raise ValueError("a Wilson line requires a name and order at least two")
        if len({label for label, _ in values}) != len(values):
            raise ValueError("Wilson-line labels must be unique")
        if any(
            not label.strip()
            or isinstance(character, bool)
            or not isinstance(character, int)
            or not 0 <= character < order
            for label, character in values
        ):
            raise ValueError("Wilson-line characters must be canonical integers modulo order")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "gauge_group", gauge_group)
        object.__setattr__(self, "order", order)
        object.__setattr__(self, "characters", values)

    def character(self, label: str) -> int:
        """Return one declared character."""

        for candidate, value in self.characters:
            if candidate == label:
                return value
        raise KeyError(label)


class FrameConvention(StrEnum):
    """The two frame conventions used by heterotic effective actions."""

    STRING = "string"
    EINSTEIN = "einstein"


@dataclass(frozen=True, slots=True)
class FrameTransformation:
    """An explicit string-to-Einstein-frame Weyl transformation record."""

    source: FrameConvention
    target: FrameConvention
    metric_relation: str
    dilaton_relation: str
    provenance: str

    def __init__(
        self,
        source: FrameConvention,
        target: FrameConvention,
        metric_relation: str,
        dilaton_relation: str,
        provenance: str,
    ) -> None:
        if source is target or any(
            not value.strip() for value in (metric_relation, dilaton_relation, provenance)
        ):
            raise ValueError("frame transformations require distinct frames and formulas")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "metric_relation", metric_relation)
        object.__setattr__(self, "dilaton_relation", dilaton_relation)
        object.__setattr__(self, "provenance", provenance)

    @property
    def string_to_einstein(self) -> bool:
        """Return whether this is the standard heterotic frame direction."""

        return self.source is FrameConvention.STRING and self.target is FrameConvention.EINSTEIN


def string_to_einstein_frame(
    provenance: str = "heterotic frame transformation",
) -> FrameTransformation:
    """Construct the symbolic ten-dimensional string-to-Einstein Weyl relation."""

    return FrameTransformation(
        FrameConvention.STRING,
        FrameConvention.EINSTEIN,
        "g_E = exp(-phi/2) g_string",
        "phi_E = phi_string",
        provenance,
    )


@dataclass(frozen=True, slots=True)
class HeteroticConventions:
    """A frozen bundle of alpha-prime, trace, sign, and frame conventions."""

    frame: FrameConvention
    alpha_prime_name: str
    trace_convention: str
    bianchi_sign: int
    torsionful_connection: str
    supported_alpha_prime_order: int
    provenance: str

    def __init__(
        self,
        frame: FrameConvention = FrameConvention.STRING,
        alpha_prime_name: str = "alpha_prime",
        trace_convention: str = "Tr_adj / 30",
        bianchi_sign: int = 1,
        torsionful_connection: str = "R_+",
        supported_alpha_prime_order: int = 1,
        provenance: str = "heterotic convention declaration",
    ) -> None:
        if (
            not alpha_prime_name.strip()
            or not trace_convention.strip()
            or not torsionful_connection.strip()
            or not provenance.strip()
            or bianchi_sign not in (-1, 1)
            or isinstance(supported_alpha_prime_order, bool)
            or not isinstance(supported_alpha_prime_order, int)
            or supported_alpha_prime_order < 0
        ):
            raise ValueError("heterotic conventions require explicit valid names and order")
        object.__setattr__(self, "frame", frame)
        object.__setattr__(self, "alpha_prime_name", alpha_prime_name)
        object.__setattr__(self, "trace_convention", trace_convention)
        object.__setattr__(self, "bianchi_sign", bianchi_sign)
        object.__setattr__(self, "torsionful_connection", torsionful_connection)
        object.__setattr__(self, "supported_alpha_prime_order", supported_alpha_prime_order)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class TenDimensionalMetric:
    """An explicit ten-dimensional metric-field declaration."""

    name: str
    signature: tuple[int, ...]
    frame: FrameConvention
    components: tuple[Any, ...]
    provenance: str

    def __init__(
        self,
        name: str = "g_10",
        signature: Iterable[int] = (1, -1, -1, -1, 1, 1, 1, 1, 1, 1),
        frame: FrameConvention = FrameConvention.STRING,
        components: Iterable[Any] = (),
        provenance: str = "ten-dimensional metric law",
    ) -> None:
        values = tuple(signature)
        if len(values) != 10 or any(value not in (-1, 1) for value in values):
            raise ValueError("ten-dimensional metrics require ten signature signs")
        if not name.strip() or not provenance.strip():
            raise ValueError("ten-dimensional metrics require name and provenance")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "signature", values)
        object.__setattr__(self, "frame", frame)
        object.__setattr__(self, "components", tuple(components))
        object.__setattr__(self, "provenance", provenance)

    @property
    def dimension(self) -> int:
        """Return the fixed ten-dimensional field dimension."""

        return 10


@dataclass(frozen=True, slots=True)
class DilatonField:
    """A ten-dimensional dilaton declaration with explicit field dependence."""

    name: str
    dependence: str
    frame: FrameConvention
    mass_dimension: Rational
    provenance: str

    def __init__(
        self,
        name: str = "phi",
        dependence: str = "phi(x)",
        frame: FrameConvention = FrameConvention.STRING,
        provenance: str = "ten-dimensional dilaton law",
    ) -> None:
        if not name.strip() or not dependence.strip() or not provenance.strip():
            raise ValueError("dilaton fields require explicit dependence and provenance")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "dependence", dependence)
        object.__setattr__(self, "frame", frame)
        object.__setattr__(self, "mass_dimension", Rational(0))
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class TwoFormField:
    """The ten-dimensional Kalb–Ramond two-form declaration."""

    name: str
    field_strength_name: str
    frame: FrameConvention
    provenance: str

    def __init__(
        self,
        name: str = "B_2",
        field_strength_name: str = "H_3",
        frame: FrameConvention = FrameConvention.STRING,
        provenance: str = "heterotic two-form law",
    ) -> None:
        if any(not value.strip() for value in (name, field_strength_name, provenance)):
            raise ValueError("two-form fields require explicit names and provenance")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "field_strength_name", field_strength_name)
        object.__setattr__(self, "frame", frame)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class ThreeFormField:
    """The torsion three-form with its frozen differential definition."""

    name: str
    definition: str
    bianchi_identity: str
    frame: FrameConvention
    provenance: str

    def __init__(
        self,
        name: str = "H_3",
        definition: str = "dB_2 + alpha_prime/4 (omega_L - omega_YM)",
        bianchi_identity: str = "dH_3 = alpha_prime/4 (Tr R_+^2 - Tr F^2)",
        frame: FrameConvention = FrameConvention.STRING,
        provenance: str = "heterotic Green-Schwarz convention",
    ) -> None:
        if any(not value.strip() for value in (name, definition, bianchi_identity, provenance)):
            raise ValueError("three-form fields require definition, identity, and provenance")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "definition", definition)
        object.__setattr__(self, "bianchi_identity", bianchi_identity)
        object.__setattr__(self, "frame", frame)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class HeteroticGaugeConnection:
    """One visible or hidden E8 gauge connection with explicit trace data."""

    sector: str
    name: str
    group: GaugeGroup
    curvature_name: str
    trace_convention: str
    provenance: str

    def __init__(
        self,
        sector: str,
        name: str,
        group: GaugeGroup,
        curvature_name: str,
        trace_convention: str,
        provenance: str,
    ) -> None:
        if any(
            not value.strip()
            for value in (sector, name, curvature_name, trace_convention, provenance)
        ):
            raise ValueError("gauge connections require complete convention metadata")
        if sector not in {"visible", "hidden"}:
            raise ValueError("heterotic gauge sectors are visible or hidden")
        object.__setattr__(self, "sector", sector)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "group", group)
        object.__setattr__(self, "curvature_name", curvature_name)
        object.__setattr__(self, "trace_convention", trace_convention)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class TorsionfulCurvature:
    """The curvature of one named torsionful connection and trace convention."""

    name: str
    connection_name: str
    torsion_sign: int
    trace_convention: str
    provenance: str

    def __init__(
        self,
        name: str = "R_+",
        connection_name: str = "nabla_+",
        torsion_sign: int = 1,
        trace_convention: str = "Tr_adj / 30",
        provenance: str = "heterotic torsionful curvature law",
    ) -> None:
        if torsion_sign not in (-1, 1) or any(
            not value.strip() for value in (name, connection_name, trace_convention, provenance)
        ):
            raise ValueError("torsionful curvature requires complete sign and convention data")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "connection_name", connection_name)
        object.__setattr__(self, "torsion_sign", torsion_sign)
        object.__setattr__(self, "trace_convention", trace_convention)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class TenDimensionalFermion:
    """Metadata for one ten-dimensional heterotic fermion species."""

    name: str
    chirality: str
    representation: str
    mass_dimension: Rational
    provenance: str

    def __init__(
        self,
        name: str,
        chirality: str,
        representation: str,
        mass_dimension: object = Rational(9, 2),
        provenance: str = "ten-dimensional fermion law",
    ) -> None:
        if any(not value.strip() for value in (name, chirality, representation, provenance)):
            raise ValueError("fermion metadata require complete names and provenance")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "chirality", chirality)
        object.__setattr__(self, "representation", representation)
        object.__setattr__(self, "mass_dimension", coerce_rational(mass_dimension))
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class HeteroticFieldContent:
    """The immutable field inventory used by the ten-dimensional action."""

    metric: TenDimensionalMetric
    dilaton: DilatonField
    two_form: TwoFormField
    three_form: ThreeFormField
    visible_connection: HeteroticGaugeConnection
    hidden_connection: HeteroticGaugeConnection
    torsionful_curvature: TorsionfulCurvature
    fermions: tuple[TenDimensionalFermion, ...]

    def __post_init__(self) -> None:
        if self.visible_connection.sector != "visible" or self.hidden_connection.sector != "hidden":
            raise ValueError("field content must contain one visible and one hidden connection")
        if (
            self.metric.frame is not self.dilaton.frame
            or self.metric.frame is not self.two_form.frame
        ):
            raise ValueError("ten-dimensional bosonic fields must share a frame")


@dataclass(frozen=True, slots=True)
class BosonicActionTerm:
    """One dimension-10 symbolic bosonic term with approximation provenance."""

    name: str
    expression: str
    mass_dimension: Rational
    alpha_prime_order: int
    frame: FrameConvention
    trace_convention: str
    torsionful_connection: str | None
    dependencies: tuple[str, ...]
    provenance: str

    def __init__(
        self,
        name: str,
        expression: str,
        alpha_prime_order: int,
        frame: FrameConvention,
        trace_convention: str,
        torsionful_connection: str | None,
        dependencies: Iterable[str],
        provenance: str,
        mass_dimension: object = 10,
    ) -> None:
        if any(not value.strip() for value in (name, expression, trace_convention, provenance)):
            raise ValueError("action terms require complete symbolic metadata")
        if (
            isinstance(alpha_prime_order, bool)
            or not isinstance(alpha_prime_order, int)
            or alpha_prime_order < 0
        ):
            raise ValueError("alpha-prime order must be a nonnegative integer")
        dependency_values = tuple(dependencies)
        if any(not dependency.strip() for dependency in dependency_values):
            raise ValueError("action dependencies require names")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "expression", expression)
        object.__setattr__(self, "mass_dimension", coerce_rational(mass_dimension))
        object.__setattr__(self, "alpha_prime_order", alpha_prime_order)
        object.__setattr__(self, "frame", frame)
        object.__setattr__(self, "trace_convention", trace_convention)
        object.__setattr__(self, "torsionful_connection", torsionful_connection)
        object.__setattr__(self, "dependencies", dependency_values)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class TenDimensionalHeteroticAction:
    """The supported-order symbolic bosonic heterotic action."""

    fields: HeteroticFieldContent
    conventions: HeteroticConventions
    terms: tuple[BosonicActionTerm, ...]
    provenance: str

    def __post_init__(self) -> None:
        if not self.terms or not self.provenance.strip():
            raise ValueError("heterotic actions require terms and provenance")
        if self.fields.metric.frame is not self.conventions.frame:
            raise ValueError("heterotic action fields and conventions use different frames")
        if any(
            term.frame is not self.conventions.frame
            or term.trace_convention != self.conventions.trace_convention
            or term.alpha_prime_order > self.conventions.supported_alpha_prime_order
            for term in self.terms
        ):
            raise ValueError("action terms do not share the frozen heterotic conventions")

    @property
    def mass_dimensions_valid(self) -> bool:
        """Return whether every symbolic integrand has ten-dimensional dimension."""

        return all(term.mass_dimension == Rational(10) for term in self.terms)

    @property
    def uses_one_torsionful_connection(self) -> bool:
        """Return whether all curvature terms use the frozen connection name."""

        chosen = self.conventions.torsionful_connection
        return all(term.torsionful_connection in (None, chosen) for term in self.terms)


def default_heterotic_field_content(
    visible_group: GaugeGroup,
    hidden_group: GaugeGroup,
    conventions: HeteroticConventions | None = None,
) -> HeteroticFieldContent:
    """Construct field declarations without supplying a metric or bundle solution."""

    selected = conventions or HeteroticConventions()
    return HeteroticFieldContent(
        TenDimensionalMetric(frame=selected.frame),
        DilatonField(frame=selected.frame),
        TwoFormField(frame=selected.frame),
        ThreeFormField(frame=selected.frame),
        HeteroticGaugeConnection(
            "visible",
            "A_vis",
            visible_group,
            "F_vis",
            selected.trace_convention,
            "declared visible E8 connection slot",
        ),
        HeteroticGaugeConnection(
            "hidden",
            "A_hid",
            hidden_group,
            "F_hid",
            selected.trace_convention,
            "declared hidden E8 connection slot",
        ),
        TorsionfulCurvature(
            selected.torsionful_connection,
            "nabla_+",
            1,
            selected.trace_convention,
            selected.provenance,
        ),
        (
            TenDimensionalFermion(
                "chi_10", "Majorana-Weyl", "adjoint(E8 x E8)", provenance=selected.provenance
            ),
            TenDimensionalFermion(
                "psi_10", "Majorana-Weyl", "vector-spinor", provenance=selected.provenance
            ),
        ),
    )


def heterotic_bosonic_action(
    fields: HeteroticFieldContent,
    conventions: HeteroticConventions | None = None,
) -> TenDimensionalHeteroticAction:
    """Construct the symbolic string-frame action through the supported order in alpha-prime."""

    selected = conventions or HeteroticConventions(frame=fields.metric.frame)
    terms = (
        BosonicActionTerm(
            "dilaton-weighted Einstein term",
            "exp(-2 phi) R(g_10)",
            0,
            selected.frame,
            selected.trace_convention,
            None,
            (fields.metric.name, fields.dilaton.name),
            selected.provenance,
        ),
        BosonicActionTerm(
            "dilaton kinetic term",
            "exp(-2 phi) 4 (d phi)^2",
            0,
            selected.frame,
            selected.trace_convention,
            None,
            (fields.dilaton.name,),
            selected.provenance,
        ),
        BosonicActionTerm(
            "H kinetic term",
            "-exp(-2 phi) H_3^2 / 12",
            0,
            selected.frame,
            selected.trace_convention,
            None,
            (fields.three_form.name,),
            selected.provenance,
        ),
        BosonicActionTerm(
            "visible and hidden gauge terms",
            "-alpha_prime exp(-2 phi) (Tr F_vis^2 + Tr F_hid^2) / 4",
            1,
            selected.frame,
            selected.trace_convention,
            None,
            (fields.visible_connection.name, fields.hidden_connection.name),
            selected.provenance,
        ),
        BosonicActionTerm(
            "torsionful curvature correction",
            "-alpha_prime exp(-2 phi) Tr R_+^2 / 4",
            1,
            selected.frame,
            selected.trace_convention,
            selected.torsionful_connection,
            (fields.torsionful_curvature.name,),
            selected.provenance,
        ),
    )
    return TenDimensionalHeteroticAction(fields, selected, terms, selected.provenance)


__all__ = [
    "BosonicActionTerm",
    "Bundle",
    "BundleStatus",
    "CompactificationSpace",
    "DilatonField",
    "FrameConvention",
    "FrameTransformation",
    "HeteroticConventions",
    "HeteroticFieldContent",
    "HeteroticGaugeConnection",
    "PublishedPhysicalInput",
    "TenDimensionalFermion",
    "TenDimensionalHeteroticAction",
    "TenDimensionalMetric",
    "ThreeFormField",
    "TorsionfulCurvature",
    "TwoFormField",
    "WilsonLine",
    "default_heterotic_field_content",
    "heterotic_bosonic_action",
    "string_to_einstein_frame",
]
