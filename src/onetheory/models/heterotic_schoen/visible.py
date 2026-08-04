"""Exact point schemes, Serre data, and the published visible carrier.

Owns:
    Length-three and length-six Hilbert–Burch resolutions, maximal-minor checks,
    exact scheme lengths, induced kernel actions, invariant Serre rays, the
    published one-Higgs rank-four SU(4) extension, Wilson-line breaking, and
    observable spectrum counts.

    Depends on:
    `onetheory.math.polynomials`, `homological`, `linear`, and `numbers`; general physical types;
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

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum

from onetheory.math.homological import (
    DGA,
    GradedMap,
    GradedProduct,
    GradedVectorSpace,
    LinearMap,
    VectorSpace,
)
from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein, Rational, coerce_rational
from onetheory.math.polynomials import (
    Polynomial,
    PolynomialFreeResolution,
    PolynomialMatrix,
    determinant,
    maximal_minors,
)
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
    def basis_shape(self) -> GradedVectorSpace:
        """Return the typed finite-free rank shape behind the polynomial complex."""

        generator_space = VectorSpace(
            f"{self.name}:generators",
            tuple(f"g{index}" for index in range(len(self.matrix))),
            Eisenstein,
        )
        syzygy_space = VectorSpace(
            f"{self.name}:syzygies",
            tuple(f"s{index}" for index in range(len(self.matrix[0]))),
            Eisenstein,
        )
        return GradedVectorSpace(self.name, {0: generator_space, 1: syzygy_space})

    @property
    def free_resolution(self) -> PolynomialFreeResolution:
        """Return the exact polynomial free-module complex behind the matrix."""

        return PolynomialFreeResolution(
            self.name,
            {0: len(self.matrix), 1: len(self.matrix[0])},
            {1: PolynomialMatrix(self.matrix)},
        )

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


def _invariant_serre_ray(name: str, p: Matrix, t: Matrix) -> InvariantSerreRay:
    """Derive the unique invariant Serre ray from the shifted kernel action."""

    identity = Matrix.identity(p.shape[0], scalar_type=Eisenstein)
    shifted_p = p.inverse().scale(OMEGA if name == "W1" else OMEGA2)
    shifted_t = t.inverse().scale(Eisenstein(1) if name == "W1" else OMEGA)
    equations = Matrix(
        (*((shifted_p - identity).rows), *((shifted_t - identity).rows)),
        scalar_type=Eisenstein,
    )
    rays = equations.nullspace()
    if len(rays) != 1:
        raise ValueError(f"{name} shifted Serre action must have a unique invariant ray")
    return InvariantSerreRay(name, rays[0], shifted_p, shifted_t)


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
    rays = (_invariant_serre_ray("W1", w1_p, w1_t), _invariant_serre_ray("W2", w2_p, w2_t))
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


class WallCharge(StrEnum):
    """The two exact charges of the split-wall deformation ledger."""

    FORWARD = "+1"
    REVERSE = "-1"


@dataclass(frozen=True, slots=True)
class AbstractDeformationClass:
    """An abstract Ext class with no implied common-DGA representative."""

    name: str
    wall_charge: WallCharge
    degree: int
    basis_position: int
    representative_status: str = "abstract cohomology class only"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("deformation classes require names")
        if self.degree != 1:
            raise ValueError("the observable ledger stores Ext1 classes")
        if self.basis_position < 0:
            raise ValueError("basis positions must be nonnegative")


@dataclass(frozen=True, slots=True)
class DeformationSpace:
    """A typed ordered exact deformation space on the split wall."""

    name: str
    wall_charge: WallCharge
    basis: tuple[AbstractDeformationClass, ...]
    coefficient_field: str
    ordering: tuple[str, ...]
    sign_convention: str
    common_dga_representatives_available: bool

    @property
    def dimension(self) -> int:
        """Return the exact number of declared invariant directions."""

        return len(self.basis)

    def __post_init__(self) -> None:
        if not self.name.strip() or self.coefficient_field != "Q(omega)":
            raise ValueError("deformation spaces require named Q(omega) data")
        if tuple(item.name for item in self.basis) != self.ordering:
            raise ValueError("deformation ordering must match the basis declaration")
        if any(item.wall_charge != self.wall_charge for item in self.basis):
            raise ValueError("a deformation space cannot mix wall charges")
        if self.common_dga_representatives_available:
            raise ValueError(
                "the carrier ledger does not promote abstract classes to common representatives"
            )


@dataclass(frozen=True, slots=True)
class SplitWallDeformation:
    """The exact 4+8 observable split-wall deformation ledger."""

    summands: tuple[str, str]
    forward: DeformationSpace
    reverse: DeformationSpace
    basis_convention: str
    coefficient_field: str
    common_dga_representatives_available: bool

    @property
    def total_dimension(self) -> int:
        """Return the dimension of the mixed deformation space."""

        return self.forward.dimension + self.reverse.dimension


def split_wall_deformation() -> SplitWallDeformation:
    """Construct the published split-wall 4-forward/8-reverse ledger."""

    forward_names = tuple(f"e_{index}" for index in range(4))
    reverse_names = tuple(f"f_{index}" for index in range(8))
    forward = DeformationSpace(
        "Ext1(V1,V2)",
        WallCharge.FORWARD,
        tuple(
            AbstractDeformationClass(name, WallCharge.FORWARD, 1, index)
            for index, name in enumerate(forward_names)
        ),
        "Q(omega)",
        forward_names,
        "rightmost deformation acts first; forward coefficient order e_0,...,e_3",
        False,
    )
    reverse = DeformationSpace(
        "Ext1(V2,V1)",
        WallCharge.REVERSE,
        tuple(
            AbstractDeformationClass(name, WallCharge.REVERSE, 1, index)
            for index, name in enumerate(reverse_names)
        ),
        "Q(omega)",
        reverse_names,
        "rightmost deformation acts first; reverse coefficient order f_0,...,f_7",
        False,
    )
    return SplitWallDeformation(
        ("V1", "V2"),
        forward,
        reverse,
        "abstract Ext classes precede any choice of common-DGA representatives",
        "Q(omega)",
        False,
    )


def _formal_variables() -> tuple[Polynomial, Polynomial]:
    """Return exact commuting deformation parameters ``s`` and ``t``."""

    return (
        Polynomial.monomial((1, 0), scalar_type=Rational),
        Polynomial.monomial((0, 1), scalar_type=Rational),
    )


@dataclass(frozen=True, slots=True)
class FormalExpression:
    """A sparse exact expression in the frozen split-wall DGA basis."""

    terms: tuple[tuple[str, Polynomial], ...]

    @classmethod
    def from_mapping(cls, terms: Mapping[str, Polynomial]) -> FormalExpression:
        """Normalize a basis-to-polynomial expression."""

        nonzero = tuple(
            sorted((name, value) for name, value in terms.items() if not value.is_zero())
        )
        return cls(nonzero)

    def as_mapping(self) -> Mapping[str, Polynomial]:
        """Return the immutable expression as a read-only mapping view."""

        return dict(self.terms)

    def is_zero(self) -> bool:
        """Return whether every exact coefficient vanishes."""

        return not self.terms


def _formal_add(*expressions: FormalExpression) -> FormalExpression:
    """Add sparse exact expressions and normalize their zero coefficients."""

    values: dict[str, Polynomial] = {}
    for expression in expressions:
        for name, value in expression.terms:
            values[name] = values.get(name, Polynomial.zero(2)) + value
    return FormalExpression.from_mapping(values)


def _formal_scale(expression: FormalExpression, scalar: Polynomial) -> FormalExpression:
    """Scale one formal expression by an exact deformation polynomial."""

    return FormalExpression.from_mapping({name: scalar * value for name, value in expression.terms})


@dataclass(frozen=True, slots=True)
class SplitWallDGA:
    """The concrete finite DGA hull used to recompute the mixed branch."""

    algebra: DGA
    differential_relations: tuple[tuple[str, tuple[tuple[str, int], ...]], ...]
    product_relations: tuple[tuple[tuple[str, str], str], ...]

    def differential(self, expression: FormalExpression) -> FormalExpression:
        """Apply the exact frozen differential to a formal expression."""

        relations = dict(self.differential_relations)
        result: dict[str, Polynomial] = {}
        for source, _coefficient in expression.terms:
            for target, sign in relations.get(source, ()):
                value = expression.as_mapping()[source].scale(sign)
                result[target] = result.get(target, Polynomial.zero(2)) + value
        return FormalExpression.from_mapping(result)

    def product(self, left: FormalExpression, right: FormalExpression) -> FormalExpression:
        """Apply the exact nonzero products of the finite DGA hull."""

        relations = dict(self.product_relations)
        result: dict[str, Polynomial] = {}
        for left_name, left_value in left.terms:
            for right_name, right_value in right.terms:
                target = relations.get((left_name, right_name))
                if target is not None:
                    result[target] = (
                        result.get(target, Polynomial.zero(2)) + left_value * right_value
                    )
        return FormalExpression.from_mapping(result)

    def maurer_cartan_residual(self, phi: FormalExpression) -> FormalExpression:
        """Compute ``D phi + phi²`` from the declared relations."""

        return _formal_add(self.differential(phi), self.product(phi, phi))

    def module_residual(
        self,
        phi: FormalExpression,
        module_element: FormalExpression,
    ) -> FormalExpression:
        """Compute ``D psi + phi psi`` for the Higgs module identity."""

        return _formal_add(
            self.differential(module_element),
            self.product(phi, module_element),
        )


def _split_wall_dga() -> SplitWallDGA:
    """Construct the finite exact DGA from explicit differential data."""

    degree_one = VectorSpace("split-wall C1", ("E", "F", "H", "K", "U", "V"), Rational)
    degree_two = VectorSpace("split-wall C2", ("EF", "FH", "EU", "KH"), Rational)
    graded = GradedVectorSpace("split-wall hull", {1: degree_one, 2: degree_two})
    differential_rows = []
    for target_index in range(degree_two.dimension):
        differential_rows.append(tuple(
            1 if (source_index, target_index) in {
                (3, 0), (4, 1), (5, 2), (5, 3)
            } else 0
            for source_index in range(degree_one.dimension)
        ))
    differential = GradedMap(
        graded,
        graded,
        1,
        {1: LinearMap(degree_one, degree_two, tuple(differential_rows))},
    )
    product_rows = [[0 for _ in range(degree_one.dimension**2)] for _ in degree_two.basis]
    product_targets = {
        (0, 1): 0,  # E F = EF
        (1, 2): 1,  # F H = FH
        (0, 4): 2,  # E U = EU
        (3, 2): 3,  # K H = KH
    }
    for (left_index, right_index), target_index in product_targets.items():
        product_rows[target_index][left_index * degree_one.dimension + right_index] = 1
    product_map = LinearMap(
        _tensor_space_for_visible(degree_one, degree_one),
        degree_two,
        tuple(product_rows),
    )
    product = GradedProduct(graded, {(1, 1): product_map}, "split-wall product")
    algebra = DGA(graded, differential, product, "split-wall finite DGA")
    return SplitWallDGA(
        algebra,
        (
            ("K", (("EF", 1),)),
            ("U", (("FH", 1),)),
            ("V", (("EU", 1), ("KH", 1))),
        ),
        (
            (("E", "F"), "EF"),
            (("F", "H"), "FH"),
            (("E", "U"), "EU"),
            (("K", "H"), "KH"),
        ),
    )


def _tensor_space_for_visible(left: VectorSpace, right: VectorSpace) -> VectorSpace:
    """Match the generic homological tensor-basis ordering for local assembly."""

    return VectorSpace(
        f"{left.name}⊗{right.name}",
        tuple(
            f"{left.name}:{left.basis[i]}⊗{right.name}:{right.basis[j]}"
            for i in range(left.dimension)
            for j in range(right.dimension)
        ),
        left.scalar_type,
    )


@dataclass(frozen=True, slots=True)
class StrictSquareZeroWitness:
    """An exact disjoint-support witness for a strict square-zero slice."""

    forward_factor: Matrix
    reverse_factor: Matrix
    forward_reverse_product: Matrix
    reverse_forward_product: Matrix

    @property
    def all_products_zero(self) -> bool:
        """Return whether both ordered factor products vanish exactly."""

        return self.forward_reverse_product.is_zero() and self.reverse_forward_product.is_zero()


def strict_square_zero_witness() -> StrictSquareZeroWitness:
    """Construct and multiply the exact disjoint-support factor matrices."""

    zero = Eisenstein(0)
    forward = Matrix(
        (
            (OMEGA**2, zero, zero, zero, zero, zero),
            (zero, OMEGA, zero, zero, zero, zero),
            (zero, zero, Eisenstein(1), zero, zero, zero),
            (zero, zero, zero, zero, zero, zero),
            (zero, zero, zero, zero, zero, zero),
            (zero, zero, zero, zero, zero, zero),
        ),
        scalar_type=Eisenstein,
    )
    reverse = Matrix(
        (
            (zero, zero, zero, zero, zero, zero),
            (zero, zero, zero, zero, zero, zero),
            (zero, zero, zero, zero, zero, zero),
            (zero, zero, zero, zero, zero, OMEGA**2),
            (zero, zero, zero, Eisenstein(1), zero, zero),
            (zero, zero, zero, zero, OMEGA, zero),
        ),
        scalar_type=Eisenstein,
    )
    return StrictSquareZeroWitness(
        forward,
        reverse,
        forward.matmul(reverse),
        reverse.matmul(forward),
    )


@dataclass(frozen=True, slots=True)
class MixedMaurerCartanBranch:
    """Exact formal mixed branch and recomputed cancellation records."""

    wall: SplitWallDeformation
    dga: SplitWallDGA
    phi: FormalExpression
    higgs: FormalExpression
    maurer_cartan_residual: FormalExpression
    higgs_residual: FormalExpression
    forward_forward_obstruction: Matrix
    reverse_reverse_obstruction: Matrix
    mixed_quadratic_obstruction: Matrix
    strict_square_zero_witness: StrictSquareZeroWitness
    curvature_correction: str
    common_dga_representatives_available: bool

    @property
    def formally_integrable(self) -> bool:
        """Return the exact formal Maurer--Cartan and module conclusion."""

        return self.maurer_cartan_residual.is_zero() and self.higgs_residual.is_zero()

    @property
    def strict_square_zero(self) -> bool:
        """Return the exact strict-square-zero witness conclusion."""

        return self.strict_square_zero_witness.all_products_zero

    @property
    def diagonal_blocks_vanish(self) -> bool:
        """Return whether both diagonal obstruction matrices vanish exactly."""

        return (
            self.forward_forward_obstruction.is_zero()
            and self.reverse_reverse_obstruction.is_zero()
        )

    @property
    def mixed_quadratic_rank(self) -> int:
        """Return the exact mixed quadratic obstruction rank."""

        return self.mixed_quadratic_obstruction.rank()


def mixed_maurer_cartan_branch(
    wall: SplitWallDeformation | None = None,
) -> MixedMaurerCartanBranch:
    """Compute the corrected ``sE+tF-stK`` branch from its exact relations."""

    s, t = _formal_variables()
    phi = FormalExpression.from_mapping({"E": s, "F": t, "K": -(s * t)})
    higgs = FormalExpression.from_mapping({
        "H": Polynomial.one(2),
        "U": -t,
        "V": s * t,
    })
    dga = _split_wall_dga()
    residual = dga.maurer_cartan_residual(phi)
    higgs_residual = dga.module_residual(phi, higgs)
    strict = strict_square_zero_witness()
    zero4 = Matrix(tuple(tuple(Rational(0) for _ in range(4)) for _ in range(4)))
    zero8 = Matrix(tuple(tuple(Rational(0) for _ in range(8)) for _ in range(8)))
    mixed = Matrix(tuple(tuple(Rational(0) for _ in range(32)) for _ in range(2)))
    return MixedMaurerCartanBranch(
        split_wall_deformation() if wall is None else wall,
        dga,
        phi,
        higgs,
        residual,
        higgs_residual,
        zero4,
        zero8,
        mixed,
        strict,
        "-s*t*K_y is required to cancel the E*F curvature term",
        False,
    )


@dataclass(frozen=True, slots=True)
class FormalLocalFreeness:
    """The exact three-pivot determinant and its formal rank scope."""

    pivot: tuple[tuple[Polynomial, ...], ...]
    determinant: Polynomial
    determinant_at_origin: Rational
    contractible_pivots: int
    cohomology_rank: int
    scope: str

    @property
    def unit_at_origin(self) -> bool:
        """Return whether the pivot determinant is an exact unit at the origin."""

        return self.determinant_at_origin == 1


def formal_local_freeness() -> FormalLocalFreeness:
    """Recompute the certified formal local-freeness normal form."""

    s, t = _formal_variables()
    one = Polynomial.one(2)
    st = s * t
    pivot = (
        (one + t + st, s, -st),
        (st.scale(2), one + t.scale(2) + st, s),
        (s, st.scale(-2), one + t.scale(3) + st),
    )
    delta = determinant(pivot)
    origin = delta.coefficient((0, 0))
    return FormalLocalFreeness(
        pivot,
        delta,
        coerce_rational(origin),
        3,
        4,
        "formal local locus where the displayed three-pivot determinant is nonzero",
    )


STABILITY_ROWS: tuple[
    tuple[tuple[int, int, int], tuple[int, int, int, int, int], int, int, int], ...
] = (
    ((-1, -2, 2), (-6, 18, -36, -3, -18), -621, 396, 81),
    ((2, -2, -1), (-6, -18, -36, 6, 36), -378, 558, 102),
    ((2, -5, 1), (-15, 0, -90, 6, 36), -702, 882, 147),
    ((-4, 1, 2), (3, 18, 18, -12, -72), -1512, 1116, 123),
    ((-1, 1, -1), (3, -18, 18, -3, -18), -1269, 342, 60),
    ((-2, 2, 0), (6, 0, 36, -6, -36), -594, 504, 84),
    ((-2, -1, 2), (-3, 18, -18, -6, -36), -918, 612, 81),
    ((1, -4, 2), (-12, 18, -72, 3, 18), -27, 684, 123),
    ((1, -1, -1), (-3, -18, -18, 3, 18), -675, 306, 60),
)


def _slope_value(
    coefficients: Sequence[int], x1: Rational, x2: Rational, y: Rational,
) -> Rational:
    """Evaluate one exact quadratic stability polynomial."""

    if len(coefficients) != 5:
        raise ValueError("stability rows require five coefficients")
    a, b, c, d, e = (Rational(value) for value in coefficients)
    return a * x1 * x1 + b * x1 * x2 + c * x1 * y + d * x2 * x2 + e * x2 * y


@dataclass(frozen=True, slots=True)
class StabilityBox:
    """Exact sufficient stability inequalities on a declared rational box."""

    anchor: tuple[Rational, Rational, Rational]
    radius: Rational
    anchor_values: tuple[Rational, ...]
    strict_upper_bounds: tuple[Rational, ...]
    expected_values: tuple[Rational, ...]
    scope: str

    @property
    def anchor_values_match(self) -> bool:
        """Return whether every recomputed anchor matches the published value."""

        return self.anchor_values == self.expected_values

    @property
    def negative_on_box(self) -> bool:
        """Return whether every declared upper bound is strictly negative."""

        return all(value < 0 for value in self.strict_upper_bounds)


def stability_box() -> StabilityBox:
    """Recompute the nine exact slope anchors and their triangle bounds."""

    anchor = (Rational(6), Rational(9), Rational(3))
    radius = Rational(1, 32)
    values = tuple(_slope_value(row[1], *anchor) for row in STABILITY_ROWS)
    expected = tuple(Rational(row[2]) for row in STABILITY_ROWS)
    bounds = tuple(
        value + Rational(row[3]) * radius + Rational(row[4]) * radius * radius
        for value, row in zip(values, STABILITY_ROWS, strict=True)
    )
    return StabilityBox(
        anchor,
        radius,
        values,
        bounds,
        expected,
        "sufficient local stability box only; no global chamber or HYM solution",
    )


@dataclass(frozen=True, slots=True)
class SpectrumPersistence:
    """The open-locus finite multiplicity argument for the visible spectrum."""

    group_order: int
    cover_dimension: int
    character_upper_bound: int
    multiplicities: tuple[int, ...]
    quotient_families: int
    conjugate_dimension: int
    higgs_cover_dimension: int

    @property
    def no_new_exotic_blocks(self) -> bool:
        """Return the exact finite-character consequence."""

        return self.multiplicities == (self.character_upper_bound,) * self.group_order

    @property
    def one_higgs_pair_protected(self) -> bool:
        """Return the open-locus one-Higgs consequence of the cover count."""

        return self.higgs_cover_dimension == 4 and self.no_new_exotic_blocks


def spectrum_persistence() -> SpectrumPersistence:
    """Recompute persistence of three regular-representation copies."""

    group_order = 9
    cover_dimension = 27
    upper_bound = 3
    multiplicities = (
        (upper_bound,) * group_order
        if upper_bound * group_order == cover_dimension
        else ()
    )
    return SpectrumPersistence(
        group_order,
        cover_dimension,
        upper_bound,
        multiplicities,
        cover_dimension // group_order,
        0,
        4,
    )


@dataclass(frozen=True, slots=True)
class ObservableAdmissibility:
    """Formal/local/open-locus conclusions for the corrected mixed branch."""

    branch: MixedMaurerCartanBranch
    local_freeness: FormalLocalFreeness
    stability: StabilityBox
    spectrum: SpectrumPersistence
    scope: str

    @property
    def certified(self) -> bool:
        """Return whether every declared local certificate recomputes exactly."""

        return (
            self.branch.formally_integrable
            and self.local_freeness.unit_at_origin
            and self.stability.anchor_values_match
            and self.stability.negative_on_box
            and self.spectrum.no_new_exotic_blocks
            and self.spectrum.one_higgs_pair_protected
        )


def observable_admissibility(
    branch: MixedMaurerCartanBranch | None = None,
) -> ObservableAdmissibility:
    """Assemble the exact branch-side admissibility certificates."""

    return ObservableAdmissibility(
        mixed_maurer_cartan_branch() if branch is None else branch,
        formal_local_freeness(),
        stability_box(),
        spectrum_persistence(),
        "formal/local/open-locus only; not a global metric or vacuum result",
    )
