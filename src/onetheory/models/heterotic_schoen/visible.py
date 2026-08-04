"""Exact point schemes, Serre data, and the published visible carrier.

Owns:
    Length-three and length-six Hilbert–Burch resolutions, maximal-minor checks,
    exact scheme lengths, induced kernel actions, invariant Serre rays, the
    published one-Higgs rank-four SU(4) extension, Wilson-line breaking, and
    observable spectrum counts.

Depends on:
    `onetheory.math.polynomials`, `linear`, and `numbers`; general physical types;
    the sibling Standard Model metadata; and concrete Schoen geometry. It must
    not import engine, verification, research, or unresolved metric data.

Must not:
    Instantiate the superseded two-Higgs carrier, fabricate cohomology bases,
    use measured observables, claim a hidden bundle, or represent normalized
    physical Yukawa matrices as holomorphic data.

Phase 0:
    Exact published visible-carrier and point-scheme data are implemented;
    downstream metrics, instantons, and physical normalization remain unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein, Rational
from onetheory.math.polynomials import Polynomial, maximal_minors
from onetheory.models.heterotic_schoen.geometry import SchoenGeometry
from onetheory.models.standard_model import standard_model
from onetheory.physics.gauge import GaugeGroup
from onetheory.physics.matter import Spectrum
from onetheory.physics.strings import Bundle, BundleStatus


def _variables() -> tuple[Polynomial, Polynomial, Polynomial]:
    """Return exact Eisenstein coordinate variables a, b, c."""

    return (
        Polynomial.monomial((1, 0, 0), scalar_type=Eisenstein),
        Polynomial.monomial((0, 1, 0), scalar_type=Eisenstein),
        Polynomial.monomial((0, 0, 1), scalar_type=Eisenstein),
    )


def _associate(left: Polynomial, right: Polynomial) -> bool:
    """Return whether two nonzero polynomials differ by an exact scalar unit."""

    if left.is_zero() or right.is_zero() or left.variable_count != right.variable_count:
        return left == right
    left_term = left.terms[0]
    right_coefficient = right.coefficient(left_term[0])
    if right_coefficient.is_zero():
        return False
    unit = left_term[1] / right_coefficient
    return right.scale(unit) == left


@dataclass(frozen=True, slots=True)
class HilbertBurchResolution:
    """A polynomial Hilbert–Burch matrix with exact generator checks."""

    name: str
    matrix: tuple[tuple[Polynomial, ...], ...]
    generators: tuple[Polynomial, ...]
    hilbert_numerator: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.matrix or not self.matrix[0]:
            raise ValueError("a Hilbert–Burch matrix must be nonempty")
        columns = len(self.matrix[0])
        if len(self.matrix) != columns + 1:
            raise ValueError("a Hilbert–Burch matrix must have shape (n+1) x n")
        if any(len(row) != columns for row in self.matrix):
            raise ValueError("a Hilbert–Burch matrix must be rectangular")
        if len(self.generators) != len(self.matrix):
            raise ValueError("generator count must equal the maximal-minor count")
        if len(self.hilbert_numerator) < 1:
            raise ValueError("a Hilbert numerator must be nonempty")

    @property
    def maximal_minors(self) -> tuple[Polynomial, ...]:
        """Return exact signed maximal minors."""

        return maximal_minors(self.matrix)

    @property
    def scheme_length(self) -> Rational:
        """Return the projective zero-scheme length from the Hilbert numerator."""

        return sum(
            (
                Rational(index * (index - 1), 2) * Rational(coefficient)
                for index, coefficient in enumerate(self.hilbert_numerator)
            ),
            Rational(0),
        )

    def verifies_generators(self) -> bool:
        """Check that every maximal minor is associated to a declared generator."""

        return all(
            any(_associate(minor, generator) for generator in self.generators)
            for minor in self.maximal_minors
        )


@dataclass(frozen=True, slots=True)
class PointScheme:
    """A finite projective point scheme represented by its exact resolution."""

    name: str
    ideal_generators: tuple[Polynomial, ...]
    resolution: HilbertBurchResolution

    @property
    def length(self) -> Rational:
        """Return the exact scheme length."""

        return self.resolution.scheme_length

    @property
    def is_certified(self) -> bool:
        """Return whether the resolution and its minors agree exactly."""

        return self.resolution.verifies_generators()


@dataclass(frozen=True, slots=True)
class SerreKernelAction:
    """An induced exact P,T action on one Serre kernel."""

    name: str
    p: Matrix
    t: Matrix
    p_character_multiplicities: tuple[tuple[tuple[Eisenstein, Eisenstein], int], ...]

    @property
    def dimension(self) -> int:
        """Return the kernel dimension."""

        return self.p.shape[0]

    @property
    def commutes(self) -> bool:
        """Return whether the induced central cocycle cancels."""

        return self.p @ self.t == self.t @ self.p

    def character_multiplicity(self, p_value: Eisenstein, t_value: Eisenstein) -> int:
        """Return one exact simultaneous-character multiplicity."""

        for values, multiplicity in self.p_character_multiplicities:
            if values == (p_value, t_value):
                return multiplicity
        return 0


@dataclass(frozen=True, slots=True)
class InvariantSerreRay:
    """A nonzero projective ray fixed by shifted P and T actions."""

    name: str
    vector: Vector
    shifted_p: Matrix
    shifted_t: Matrix

    @property
    def p_fixed(self) -> bool:
        """Return whether shifted P fixes the chosen representative."""

        return self.shifted_p @ self.vector == self.vector

    @property
    def t_fixed(self) -> bool:
        """Return whether shifted T fixes the chosen representative."""

        return self.shifted_t @ self.vector == self.vector


@dataclass(frozen=True, slots=True)
class LocalI6Characters:
    """The exact unit and nilpotent local character data."""

    unit: Eisenstein
    nilpotent: Eisenstein


@dataclass(frozen=True, slots=True)
class SerreData:
    """Exact kernel actions, character decompositions, rays, and local classes."""

    actions: tuple[SerreKernelAction, ...]
    rays: tuple[InvariantSerreRay, ...]
    local_i6: LocalI6Characters

    def action(self, name: str) -> SerreKernelAction:
        """Return one named kernel action."""

        for action in self.actions:
            if action.name == name:
                return action
        raise KeyError(name)


@dataclass(frozen=True, slots=True)
class ObservableSpectrum:
    """Published cover and quotient spectrum counts for the visible carrier."""

    cover_h1_visible: int
    cover_h1_dual: int
    cover_h1_wedge2: int
    families: int
    right_handed_neutrinos: int
    higgs_pairs: int
    anti_families: int
    exotic_zero_modes: int
    geometric_moduli: int
    observable_bundle_moduli: int
    standard_model: Spectrum


@dataclass(frozen=True, slots=True)
class LineConstituent:
    """One twisted rank-two constituent of the visible rank-four extension."""

    name: str
    twist: tuple[Rational, Rational, Rational]
    point_scheme: PointScheme
    rank: int


@dataclass(frozen=True, slots=True)
class WilsonLineBreaking:
    """The published intermediate Spin(10) to observable gauge breaking."""

    parent: GaugeGroup
    unbroken: GaugeGroup
    order: int
    is_published: bool


@dataclass(frozen=True, slots=True)
class ObservableBundle:
    """The published one-Higgs observable SU(4) bundle handoff."""

    bundle: Bundle
    constituent_one: LineConstituent
    constituent_two: LineConstituent
    outer_extension: str
    determinant_c1: tuple[Rational, Rational, Rational]
    equivariant_descent: bool
    commutant: GaugeGroup
    wilson_breaking: WilsonLineBreaking
    spectrum: ObservableSpectrum
    serre: SerreData

    @property
    def is_one_higgs_carrier(self) -> bool:
        """Return the carrier identity firewall result."""

        return self.spectrum.higgs_pairs == 1


def point_schemes() -> tuple[PointScheme, PointScheme]:
    """Construct the exact length-three and length-six point schemes."""

    a, b, c = _variables()
    zero = Polynomial.zero(3, scalar_type=Eisenstein)
    m3 = ((c, c), (-b, zero), (zero, -a))
    m6 = (
        (a, zero, zero),
        (zero, b, zero),
        (-b, -c, a),
        (zero, zero, -c),
    )
    i3 = (a * b, a * c, b * c)
    i6 = (b**2 * c, a * c**2, a * b * c, a**2 * b)
    scheme3 = PointScheme(
        "I3",
        i3,
        HilbertBurchResolution("I3", m3, i3, (1, 0, -3, 2)),
    )
    scheme6 = PointScheme(
        "I6",
        i6,
        HilbertBurchResolution("I6", m6, i6, (1, 0, 0, -4, 3)),
    )
    if not all(scheme.is_certified for scheme in (scheme3, scheme6)):
        raise ValueError("published Hilbert-Burch minors failed exact verification")
    return scheme3, scheme6


def _simultaneous_multiplicity(p: Matrix, t: Matrix, p_value: Eisenstein,
                               t_value: Eisenstein) -> int:
    """Compute one exact simultaneous eigenspace dimension."""

    size = p.shape[0]
    identity = Matrix.identity(size, scalar_type=Eisenstein)
    equations = Matrix(
        (*((p - identity.scale(p_value)).rows),
         *((t - identity.scale(t_value)).rows)),
        scalar_type=Eisenstein,
    )
    return len(equations.nullspace())


def _action(name: str, p: Matrix, t: Matrix) -> SerreKernelAction:
    """Create one kernel action with its exact character decomposition."""

    values = tuple(
        ((p_value, t_value), _simultaneous_multiplicity(p, t, p_value, t_value))
        for p_value in (Eisenstein(1), OMEGA, OMEGA2)
        for t_value in (Eisenstein(1), OMEGA, OMEGA2)
        if _simultaneous_multiplicity(p, t, p_value, t_value)
    )
    return SerreKernelAction(name, p, t, values)


def serre_data() -> SerreData:
    """Construct the exact induced kernel actions and unique invariant rays."""

    w1_p = Matrix(((1, -2 - 4 * OMEGA), (0, OMEGA)), scalar_type=Eisenstein)
    w1_t = Matrix.identity(2, scalar_type=Eisenstein)
    w2_p = Matrix(
        (
            (0, 0, 0, -1 - OMEGA, 0),
            (0, OMEGA, 0, 0, 0),
            (1, 0, 0, 4 + 2 * OMEGA, 0),
            (2 + 4 * OMEGA, 0, OMEGA, 0, 0),
            (0, -2 - 4 * OMEGA, 0, 0, 1),
        ),
        scalar_type=Eisenstein,
    )
    w2_t = Matrix(
        (
            (OMEGA, 0, 0, 0, 0),
            (0, 1, 0, 0, 0),
            (0, 0, OMEGA, 0, 0),
            (0, 0, 0, OMEGA, 0),
            (0, 0, 0, 0, 1),
        ),
        scalar_type=Eisenstein,
    )
    actions = (_action("W1", w1_p, w1_t), _action("W2", w2_p, w2_t))
    rays = (
        InvariantSerreRay(
            "W1", Vector((2 * OMEGA, 1), scalar_type=Eisenstein),
            w1_p.inverse().scale(OMEGA), w1_t.inverse(),
        ),
        InvariantSerreRay(
            "W2", Vector((1, 0, -2 + 3 * OMEGA, 1, 0), scalar_type=Eisenstein),
            w2_p.inverse().scale(OMEGA2), w2_t.inverse().scale(OMEGA),
        ),
    )
    local = LocalI6Characters(OMEGA2 * OMEGA, OMEGA)
    data = SerreData(actions, rays, local)
    if not all(action.commutes for action in actions):
        raise ValueError("induced Serre kernel actions must commute")
    if not all(ray.p_fixed and ray.t_fixed for ray in rays):
        raise ValueError("published invariant Serre rays failed exact fixed-point checks")
    if local.unit != Eisenstein(1) or local.nilpotent != OMEGA:
        raise ValueError("local I6 character data are inconsistent")
    return data


def visible_bundle(geometry: SchoenGeometry) -> ObservableBundle:
    """Assemble the published one-Higgs visible bundle from established data."""

    schemes = point_schemes()
    serre = serre_data()
    visible_group = GaugeGroup.simple("SU(4)", 3, 4)
    commutant = GaugeGroup.simple("Spin(10)", 5, 16)
    bundle = Bundle(
        "published one-Higgs visible SU(4) bundle",
        4,
        visible_group,
        (0, 0, 0),
        (Rational(8, 3), Rational(5, 3), Rational(4)),
        Rational(-6),
        BundleStatus.PUBLISHED,
    )
    constituent_one = LineConstituent("V1", (Rational(-1), Rational(1), Rational(0)), schemes[0], 2)
    constituent_two = LineConstituent("V2", (Rational(1), Rational(-1), Rational(0)), schemes[1], 2)
    observable_spectrum = ObservableSpectrum(
        27, 0, 4, 3, 3, 1, 0, 0, 6, 13, standard_model().spectrum
    )
    breaking = WilsonLineBreaking(commutant, standard_model().extended_gauge_group, 3, True)
    result = ObservableBundle(
        bundle,
        constituent_one,
        constituent_two,
        "0 -> V1 -> Vvis -> V2 -> 0",
        (Rational(0), Rational(0), Rational(0)),
        True,
        commutant,
        breaking,
        observable_spectrum,
        serre,
    )
    if geometry.quotient.order != 9:
        raise ValueError("the visible carrier requires the published order-nine quotient")
    if not result.is_one_higgs_carrier or not result.equivariant_descent:
        raise ValueError("the visible carrier identity firewall failed")
    return result
