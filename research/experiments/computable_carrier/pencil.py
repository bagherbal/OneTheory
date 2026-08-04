"""Derive the exact rational-elliptic pencil input for Tier A patching.

Owns:
    The affine base-locus algebra of the frozen cubic pencil, its square-free
    degree-nine modulus, exact coordinate reconstruction, induced deck actions,
    and the coordinate singular-point/local-ideal certificates used by the
    Serre construction.

Depends on:
    The exact Schoen pencil in the production geometry module, exact
    Eisenstein polynomial arithmetic, and the published I3/I6 ideal schemes.
    This module derives algebraic input; it does not replace the surface model.

Must not:
    Treat a finite affine algebra as a completed blow-up, invent dP9 chart
    transition functions, identify a pencil point with a global Serre cocycle,
    or claim local-freeness, equivariant descent, or stability for a bundle.

Phase 0:
    The pencil base-locus and coordinate singular-point data are exact; the
    blow-up atlas, Serre patching, and constituent linearization remain open.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.math.sheaves import LaurentPolynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from onetheory.models.heterotic_schoen.visible import PointScheme, point_schemes


def _univariate_zero() -> Polynomial:
    """Return the exact zero in the base-locus polynomial ring."""

    return Polynomial.zero(1, scalar_type=Eisenstein)


@dataclass(frozen=True, slots=True)
class QuotientPolynomial:
    """One canonical element of a univariate exact quotient algebra."""

    modulus: Polynomial
    representative: Polynomial

    def __post_init__(self) -> None:
        if self.modulus.variable_count != 1 or self.modulus.is_zero():
            raise ValueError("a quotient algebra requires a nonzero univariate modulus")
        if self.modulus.scalar_type is not Eisenstein:
            raise TypeError("the base-locus quotient must use Eisenstein scalars")
        if self.modulus != self.modulus.monic():
            raise ValueError("quotient moduli must be monic")
        if self.representative.variable_count != 1:
            raise ValueError("quotient representatives must be univariate")
        if self.representative.scalar_type is not Eisenstein:
            raise TypeError("quotient representatives must use Eisenstein scalars")
        _, remainder = self.representative.divmod_univariate(self.modulus)
        object.__setattr__(self, "representative", remainder)

    @classmethod
    def zero(cls, modulus: Polynomial) -> QuotientPolynomial:
        """Return the exact quotient zero."""

        return cls(modulus, _univariate_zero())

    @classmethod
    def one(cls, modulus: Polynomial) -> QuotientPolynomial:
        """Return the exact quotient unit."""

        return cls(modulus, Polynomial.one(1, scalar_type=Eisenstein))

    def _check(self, other: QuotientPolynomial) -> None:
        if self.modulus != other.modulus:
            raise ValueError("quotient elements use different moduli")

    def __add__(self, other: QuotientPolynomial) -> QuotientPolynomial:
        self._check(other)
        return QuotientPolynomial(self.modulus, self.representative + other.representative)

    def __neg__(self) -> QuotientPolynomial:
        return QuotientPolynomial(self.modulus, -self.representative)

    def __sub__(self, other: QuotientPolynomial) -> QuotientPolynomial:
        return self + (-other)

    def __mul__(self, other: QuotientPolynomial) -> QuotientPolynomial:
        self._check(other)
        return QuotientPolynomial(self.modulus, self.representative * other.representative)

    def scale(self, scalar: object) -> QuotientPolynomial:
        """Multiply by one exact Eisenstein scalar."""

        return QuotientPolynomial(self.modulus, self.representative.scale(scalar))

    def __pow__(self, exponent: int) -> QuotientPolynomial:
        if isinstance(exponent, bool) or not isinstance(exponent, int) or exponent < 0:
            raise ValueError("quotient powers require a nonnegative integer")
        result = QuotientPolynomial.one(self.modulus)
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result

    @property
    def is_zero(self) -> bool:
        """Return whether this element vanishes in the quotient."""

        return self.representative.is_zero()

    def as_text(self) -> str:
        """Return the deterministic exact representative text."""

        return str(self.representative)


@dataclass(frozen=True, slots=True)
class BaseLocusAlgebra:
    """The exact affine algebra of the nine base points of the pencil."""

    modulus: Polynomial
    coordinate_x: QuotientPolynomial
    coordinate_y: QuotientPolynomial
    inverse_x: QuotientPolynomial
    affine_relation: Polynomial
    degree: int
    square_free: bool
    boundary_empty: bool
    transverse_jacobian_unit: bool
    pencil_relations_hold: bool

    @property
    def x_inverse_identity(self) -> bool:
        """Return whether the recorded inverse of x is exact."""

        return (self.coordinate_x * self.inverse_x).representative == Polynomial.one(
            1,
            scalar_type=Eisenstein,
        )

    @property
    def reduced_and_transverse(self) -> bool:
        """Return the exact finite-basepoint smoothness certificate."""

        return self.square_free and self.transverse_jacobian_unit

    def as_record(self) -> dict[str, object]:
        """Serialize the finite algebra without calling it a blow-up atlas."""

        return {
            "modulus": {
                "degree": self.modulus.univariate_degree,
                "terms": [
                    {"degree": exponents[0], "coefficient": str(coefficient)}
                    for exponents, coefficient in self.modulus.terms
                ],
            },
            "coordinate_x": self.coordinate_x.as_text(),
            "coordinate_y": self.coordinate_y.as_text(),
            "inverse_x": self.inverse_x.as_text(),
            "affine_relation": str(self.affine_relation),
            "degree": self.degree,
            "square_free": self.square_free,
            "boundary_empty": self.boundary_empty,
            "transverse_jacobian_unit": self.transverse_jacobian_unit,
            "reduced_and_transverse": self.reduced_and_transverse,
            "x_inverse_identity": self.x_inverse_identity,
            "pencil_relations_hold": self.pencil_relations_hold,
            "status": "exact affine base-locus algebra; blow-up atlas pending",
        }


@dataclass(frozen=True, slots=True)
class PencilDeckAction:
    """An exact induced action on the base-locus quotient algebra."""

    name: str
    image_x: QuotientPolynomial
    image_y: QuotientPolynomial
    order_three: bool

    def as_record(self) -> dict[str, object]:
        """Serialize the generator action and its exact order check."""

        return {
            "name": self.name,
            "image_x": self.image_x.as_text(),
            "image_y": self.image_y.as_text(),
            "order_three": self.order_three,
        }


@dataclass(frozen=True, slots=True)
class ProjectivePoint:
    """A named exact coordinate point in the frozen projective pencil plane."""

    name: str
    coordinates: tuple[int, int, int]

    def __post_init__(self) -> None:
        if not self.name.strip() or len(self.coordinates) != 3:
            raise ValueError("projective points require names and three coordinates")
        if all(value == 0 for value in self.coordinates):
            raise ValueError("projective points cannot be zero")


@dataclass(frozen=True, slots=True)
class SingularPencilPoint:
    """A coordinate singular point and its exact pencil member."""

    point: ProjectivePoint
    fiber_parameter: tuple[Eisenstein, Eisenstein]
    gradient: tuple[Eisenstein, Eisenstein, Eisenstein]
    singular: bool

    def as_record(self) -> dict[str, object]:
        """Serialize the singular-point certificate."""

        return {
            "name": self.point.name,
            "coordinates": list(self.point.coordinates),
            "fiber_parameter": [str(value) for value in self.fiber_parameter],
            "gradient": [str(value) for value in self.gradient],
            "singular": self.singular,
        }


@dataclass(frozen=True, slots=True)
class LocalIdealCertificate:
    """A chart-local monomial ideal type at one coordinate singular point."""

    scheme: str
    point: str
    chart_pivot: int
    linear_coordinate: str
    nilpotent_coordinate: str
    ideal_type: str
    generators: tuple[str, ...]
    verified: bool

    def as_record(self) -> dict[str, object]:
        """Serialize the local ideal computation."""

        return {
            "scheme": self.scheme,
            "point": self.point,
            "chart_pivot": self.chart_pivot,
            "linear_coordinate": self.linear_coordinate,
            "nilpotent_coordinate": self.nilpotent_coordinate,
            "ideal_type": self.ideal_type,
            "generators": list(self.generators),
            "verified": self.verified,
        }


@dataclass(frozen=True, slots=True)
class BlowupChart:
    """One exact affine chart of the pencil blow-up hypersurface."""

    name: str
    base_pivot: int
    fiber_chart: str
    variables: tuple[str, str, str]
    equation: Polynomial

    def as_record(self) -> dict[str, object]:
        """Serialize the affine chart equation and coordinate convention."""

        return {
            "name": self.name,
            "base_pivot": self.base_pivot,
            "fiber_chart": self.fiber_chart,
            "variables": list(self.variables),
            "equation": {
                "terms": [
                    {
                        "exponents": list(exponents),
                        "coefficient": str(coefficient),
                    }
                    for exponents, coefficient in self.equation.terms
                ]
            },
        }


@dataclass(frozen=True, slots=True)
class BlowupOverlap:
    """An exact Laurent transition and equation compatibility identity."""

    source: str
    target: str
    base_images: tuple[LaurentPolynomial, LaurentPolynomial]
    fiber_image: LaurentPolynomial
    equation_unit: LaurentPolynomial
    equation_compatible: bool

    def as_record(self) -> dict[str, object]:
        """Serialize one overlap map without hiding its Laurent inverses."""

        def terms(polynomial: LaurentPolynomial) -> list[dict[str, object]]:
            return [
                {
                    "exponents": list(exponents),
                    "coefficient": str(coefficient),
                }
                for exponents, coefficient in polynomial.terms
            ]

        return {
            "source": self.source,
            "target": self.target,
            "base_images": [terms(item) for item in self.base_images],
            "fiber_image": terms(self.fiber_image),
            "equation_unit": terms(self.equation_unit),
            "equation_compatible": self.equation_compatible,
        }


@dataclass(frozen=True, slots=True)
class PencilBlowupAtlas:
    """The exact six-chart hypersurface atlas of the cubic pencil blow-up."""

    charts: tuple[BlowupChart, ...]
    overlaps: tuple[BlowupOverlap, ...]
    equation_model: str
    atlas_consistent: bool

    def as_record(self) -> dict[str, object]:
        """Serialize charts, all ordered overlaps, and their identities."""

        return {
            "equation_model": self.equation_model,
            "charts": [chart.as_record() for chart in self.charts],
            "overlaps": [overlap.as_record() for overlap in self.overlaps],
            "overlap_count": len(self.overlaps),
            "atlas_consistent": self.atlas_consistent,
            "status": "exact blow-up hypersurface atlas; Serre patching pending",
        }


@dataclass(frozen=True, slots=True)
class TierAPencilModel:
    """Exact dP9 pencil data feeding the still-open global patching gate."""

    base_locus: BaseLocusAlgebra
    blowup_atlas: PencilBlowupAtlas
    actions: tuple[PencilDeckAction, ...]
    actions_commute: bool
    singular_points: tuple[SingularPencilPoint, ...]
    local_ideals: tuple[LocalIdealCertificate, ...]
    blowup_atlas_status: str
    serre_patching_status: str

    def as_record(self) -> dict[str, object]:
        """Serialize the exact pencil frontier and unresolved boundaries."""

        return {
            "base_locus": self.base_locus.as_record(),
            "blowup_atlas": self.blowup_atlas.as_record(),
            "actions": [action.as_record() for action in self.actions],
            "actions_commute": self.actions_commute,
            "singular_points": [point.as_record() for point in self.singular_points],
            "local_ideals": [ideal.as_record() for ideal in self.local_ideals],
            "blowup_atlas_status": self.blowup_atlas_status,
            "serre_patching_status": self.serre_patching_status,
        }


def _affine_cubics() -> tuple[Polynomial, Polynomial]:
    """Return the frozen cubic pencil in the affine chart c=1."""

    x = Polynomial.monomial((1, 0), scalar_type=Eisenstein)
    y = Polynomial.monomial((0, 1), scalar_type=Eisenstein)
    cox = schoen_geometry().cover.cox
    return cox.cubic_f.substitute((x, y, 1)), cox.cubic_g.substitute((x, y, 1))


def _base_locus_algebra() -> BaseLocusAlgebra:
    """Derive the nine-point quotient algebra from the two exact cubics."""

    f, g = _affine_cubics()
    x = Polynomial.monomial((1,), scalar_type=Eisenstein)
    one = Polynomial.one(1, scalar_type=Eisenstein)
    denominator = Eisenstein(4) + Eisenstein(2) * OMEGA
    alpha = OMEGA / denominator
    beta = -OMEGA2 / denominator
    # The exact affine relation is (4+2 omega) x y - omega x^3 + omega^2.
    # Its elimination from f is recorded as a polynomial identity below.
    y_numerator = (x**3).scale(alpha) + Polynomial.constant(beta, 1, scalar_type=Eisenstein)
    f_x3 = f.substitute((x, 0))
    f_y3_coefficient = f.coefficient((0, 3))
    modulus_raw = (
        y_numerator**3 * f_y3_coefficient
        + f_x3 * (x**3)
    )
    modulus = modulus_raw.monic()
    derivative_gcd = modulus.gcd(modulus.derivative())
    coefficient_zero = modulus.coefficient((0,))
    if coefficient_zero.is_zero():
        raise ValueError("the affine base-locus coordinate x must be a unit")
    inverse = (
        x**8
        + (x**5).scale(modulus.coefficient((6,)))
        + (x**2).scale(modulus.coefficient((3,)))
    ).scale(Eisenstein(-1) / coefficient_zero)
    quotient_x = QuotientPolynomial(modulus, x)
    quotient_inverse = QuotientPolynomial(modulus, inverse)
    quotient_y = (
        QuotientPolynomial(modulus, x**2).scale(alpha)
        + quotient_inverse.scale(beta)
    )
    relation = (
        Polynomial.monomial((1, 1), 4 + 2 * OMEGA, scalar_type=Eisenstein)
        + Polynomial.monomial((3, 0), -OMEGA, scalar_type=Eisenstein)
        + Polynomial.constant(OMEGA2, 2, scalar_type=Eisenstein)
    )
    h_identity = (
        g
        - f.scale(-1 - 2 * OMEGA)
        - relation.scale(9)
    ).is_zero()
    affine_relation = relation
    pencil_relations = (
        (QuotientPolynomial(modulus, f.substitute((x, quotient_y.representative)))
         .is_zero)
        and h_identity
    )
    jacobian = f.derivative(0) * g.derivative(1) - f.derivative(1) * g.derivative(0)
    jacobian_element = QuotientPolynomial(
        modulus,
        jacobian.substitute((x, quotient_y.representative)),
    )
    transverse_jacobian_unit = (
        not jacobian_element.is_zero
        and modulus.gcd(jacobian_element.representative).univariate_degree == 0
    )
    return BaseLocusAlgebra(
        modulus,
        quotient_x,
        quotient_y,
        quotient_inverse,
        affine_relation,
        modulus.univariate_degree,
        derivative_gcd == one,
        _boundary_has_no_basepoint(),
        transverse_jacobian_unit,
        pencil_relations,
    )


def _boundary_has_no_basepoint() -> bool:
    """Check the c=0 projective chart without numerical root finding."""

    f, g = schoen_geometry().cover.cox.cubic_f, schoen_geometry().cover.cox.cubic_g
    a = Polynomial.monomial((1, 0), scalar_type=Eisenstein)
    b = Polynomial.monomial((0, 1), scalar_type=Eisenstein)
    f_boundary = f.substitute((a, b, 0))
    g_boundary = g.substitute((a, b, 0))
    # The two cubic equations force a^3=b^3=0, hence no projective point.
    f_a = f_boundary.coefficient((3, 0))
    f_b = f_boundary.coefficient((0, 3))
    g_a = g_boundary.coefficient((3, 0))
    g_b = g_boundary.coefficient((0, 3))
    return f_a * g_b - f_b * g_a != 0


def _apply_polynomial(
    element: QuotientPolynomial,
    image_x: QuotientPolynomial,
) -> QuotientPolynomial:
    """Evaluate a quotient representative at an exact generator image."""

    result = QuotientPolynomial.zero(element.modulus)
    for (exponents,), coefficient in element.representative.terms:
        result = result + (image_x**exponents).scale(coefficient)
    return result


def _action_order_three(
    image_x: QuotientPolynomial,
    image_y: QuotientPolynomial,
    identity_x: QuotientPolynomial,
    identity_y: QuotientPolynomial,
) -> bool:
    """Check an action on both quotient coordinates by exact composition."""

    first_x = _apply_polynomial(image_x, image_x)
    second_x = _apply_polynomial(first_x, image_x)
    first_y = _apply_polynomial(image_y, image_x)
    second_y = _apply_polynomial(first_y, image_x)
    return (
        second_x == identity_x and second_y == identity_y
    )


def _pencil_actions(base: BaseLocusAlgebra) -> tuple[PencilDeckAction, ...]:
    """Derive the exact P and T actions in the c=1 chart."""

    x, y, inverse = base.coordinate_x, base.coordinate_y, base.inverse_x
    p_x = y * inverse
    p_x = p_x.scale(OMEGA)
    p_y = inverse.scale(OMEGA2)
    t_x = x.scale(OMEGA)
    t_y = y.scale(OMEGA2)
    return (
        PencilDeckAction("P", p_x, p_y, _action_order_three(p_x, p_y, x, y)),
        PencilDeckAction("T", t_x, t_y, _action_order_three(t_x, t_y, x, y)),
    )


def _pivot_images(pivot: int) -> tuple[Polynomial, Polynomial, Polynomial]:
    """Return the affine P2 coordinates for one projective pivot chart."""

    u = Polynomial.monomial((1, 0), scalar_type=Eisenstein)
    v = Polynomial.monomial((0, 1), scalar_type=Eisenstein)
    one = Polynomial.one(2, scalar_type=Eisenstein)
    if pivot == 0:
        return one, u, v
    if pivot == 1:
        return u, one, v
    if pivot == 2:
        return u, v, one
    raise ValueError("projective pivot charts are indexed by 0, 1, and 2")


def _embed_affine_polynomial(polynomial: Polynomial) -> Polynomial:
    """Add the affine fiber coordinate to a two-variable polynomial."""

    return Polynomial(
        (((exponents[0], exponents[1], 0), coefficient)
         for exponents, coefficient in polynomial.terms),
        variable_count=3,
        scalar_type=Eisenstein,
    )


def _blowup_chart(pivot: int, fiber_chart: str) -> BlowupChart:
    """Construct one affine equation of the pencil blow-up."""

    if fiber_chart not in {"mu", "nu"}:
        raise ValueError("the pencil fiber has mu and nu affine charts")
    cox = schoen_geometry().cover.cox
    images = _pivot_images(pivot)
    f = cox.cubic_f.substitute(images)
    g = cox.cubic_g.substitute(images)
    f_three = _embed_affine_polynomial(f)
    g_three = _embed_affine_polynomial(g)
    fiber = Polynomial.monomial((0, 0, 1), scalar_type=Eisenstein)
    equation = f_three + fiber * g_three if fiber_chart == "mu" else fiber * f_three + g_three
    fiber_variable = "r=nu/mu" if fiber_chart == "mu" else "s=mu/nu"
    return BlowupChart(
        f"U_{pivot}_{fiber_chart}",
        pivot,
        fiber_chart,
        ("u", "v", fiber_variable),
        equation,
    )


def _laurent_monomial(exponents: tuple[int, int, int]) -> LaurentPolynomial:
    """Return one exact Laurent monomial in a source affine chart."""

    return LaurentPolynomial.monomial(exponents, scalar_type=Eisenstein)


def _source_projective_coordinates(pivot: int) -> tuple[tuple[int, int, int], ...]:
    """Return monomial exponent vectors for (a,b,c) in one pivot chart."""

    zero = (0, 0, 0)
    u = (1, 0, 0)
    v = (0, 1, 0)
    if pivot == 0:
        return zero, u, v
    if pivot == 1:
        return u, zero, v
    if pivot == 2:
        return u, v, zero
    raise ValueError("projective pivot charts are indexed by 0, 1, and 2")


def _base_transition(
    source_pivot: int,
    target_pivot: int,
) -> tuple[LaurentPolynomial, LaurentPolynomial, LaurentPolynomial]:
    """Return target base coordinates and the cubic scaling factor."""

    source = _source_projective_coordinates(source_pivot)
    denominator = source[target_pivot]
    target_coordinates = {
        0: (source[1], source[2]),
        1: (source[0], source[2]),
        2: (source[0], source[1]),
    }[target_pivot]

    def ratio(numerator: tuple[int, int, int]) -> LaurentPolynomial:
        return _laurent_monomial(tuple(
            numerator[index] - denominator[index]
            for index in range(3)
        ))

    target_u, target_v = (ratio(item) for item in target_coordinates)
    cubic_factor = _laurent_monomial(tuple(-3 * value for value in denominator))
    return target_u, target_v, cubic_factor


def _fiber_transition(
    source_chart: str,
    target_chart: str,
) -> tuple[LaurentPolynomial, LaurentPolynomial]:
    """Return the target fiber coordinate and switch unit."""

    source_fiber = _laurent_monomial((0, 0, 1))
    if source_chart == target_chart:
        return source_fiber, LaurentPolynomial.one(3, scalar_type=Eisenstein)
    if source_chart == "mu" and target_chart == "nu":
        inverse = _laurent_monomial((0, 0, -1))
        return inverse, inverse
    if source_chart == "nu" and target_chart == "mu":
        inverse = _laurent_monomial((0, 0, -1))
        return inverse, inverse
    raise ValueError("the pencil fiber charts must be mu or nu")


def _monomial_image(polynomial: LaurentPolynomial) -> tuple[object, tuple[int, ...]]:
    """Extract a single Laurent monomial for exact substitution."""

    if len(polynomial.terms) != 1:
        raise ValueError("blow-up coordinate transitions must be monomials")
    exponents, coefficient = polynomial.terms[0]
    return coefficient, exponents


def _blowup_overlap(
    source: BlowupChart,
    target: BlowupChart,
) -> BlowupOverlap:
    """Construct and verify one ordered affine blow-up overlap."""

    target_u, target_v, cubic_factor = _base_transition(
        source.base_pivot,
        target.base_pivot,
    )
    target_fiber, fiber_switch_unit = _fiber_transition(
        source.fiber_chart,
        target.fiber_chart,
    )
    unit = cubic_factor * fiber_switch_unit
    source_equation = LaurentPolynomial.from_polynomial(source.equation)
    target_equation = LaurentPolynomial.from_polynomial(target.equation)
    images = (
        _monomial_image(target_u),
        _monomial_image(target_v),
        _monomial_image(target_fiber),
    )
    pulled_target = target_equation.substitute_monomials(images)
    return BlowupOverlap(
        source.name,
        target.name,
        (target_u, target_v),
        target_fiber,
        unit,
        pulled_target == source_equation * unit,
    )


def _pencil_blowup_atlas() -> PencilBlowupAtlas:
    """Build all exact affine charts and ordered overlap identities."""

    charts = tuple(
        _blowup_chart(pivot, fiber_chart)
        for pivot in range(3)
        for fiber_chart in ("mu", "nu")
    )
    overlaps = tuple(
        _blowup_overlap(source, target)
        for source in charts
        for target in charts
        if source != target
    )
    return PencilBlowupAtlas(
        charts,
        overlaps,
        "Bl(P2,(F,G)) = {mu F + nu G = 0} in P2 x P1",
        all(overlap.equation_compatible for overlap in overlaps),
    )


def _actions_commute(
    base: BaseLocusAlgebra,
    actions: tuple[PencilDeckAction, ...],
) -> bool:
    """Check the projective P/T commutator on both quotient coordinates."""

    p, t = actions
    p_then_t_x = _apply_polynomial(p.image_x, t.image_x)
    t_then_p_x = _apply_polynomial(t.image_x, p.image_x)
    p_then_t_y = _apply_polynomial(p.image_y, t.image_x)
    t_then_p_y = _apply_polynomial(t.image_y, p.image_x)
    return (
        p_then_t_x == t_then_p_x
        and p_then_t_y == t_then_p_y
        and base.coordinate_x.modulus == p.image_x.modulus
    )


def _projective_value(polynomial: Polynomial, coordinates: Iterable[int]) -> Eisenstein:
    """Evaluate a homogeneous exact polynomial at an integral point."""

    values = tuple(coordinates)
    result = Eisenstein(0)
    for exponents, coefficient in polynomial.terms:
        term = coefficient
        for coordinate, exponent in zip(values, exponents, strict=True):
            term = term * (Eisenstein(coordinate) ** exponent)
        result += term
    return result


def _projective_partial(
    polynomial: Polynomial,
    coordinates: tuple[int, int, int],
    variable: int,
) -> Eisenstein:
    """Evaluate one exact homogeneous partial derivative at a point."""

    result = Eisenstein(0)
    for exponents, coefficient in polynomial.terms:
        power = exponents[variable]
        if power == 0:
            continue
        term = coefficient * power
        for index, (coordinate, exponent) in enumerate(zip(coordinates, exponents, strict=True)):
            term *= Eisenstein(coordinate) ** (exponent - (1 if index == variable else 0))
        result += term
    return result


def _singular_points() -> tuple[SingularPencilPoint, ...]:
    """Certify the three coordinate singular points of the pencil."""

    f, g = schoen_geometry().cover.cox.cubic_f, schoen_geometry().cover.cox.cubic_g
    points = (
        ProjectivePoint("p_a", (1, 0, 0)),
        ProjectivePoint("p_b", (0, 1, 0)),
        ProjectivePoint("p_c", (0, 0, 1)),
    )
    records: list[SingularPencilPoint] = []
    for point in points:
        f_value = _projective_value(f, point.coordinates)
        g_value = _projective_value(g, point.coordinates)
        parameter = (g_value, -f_value)
        gradient = tuple(
            g_value * _projective_partial(f, point.coordinates, variable)
            - f_value * _projective_partial(g, point.coordinates, variable)
            for variable in range(3)
        )
        records.append(
            SingularPencilPoint(
                point,
                parameter,
                gradient,
                all(value.is_zero() for value in gradient),
            )
        )
    if len({record.fiber_parameter for record in records}) != len(records):
        raise ValueError("coordinate singular points must lie on distinct pencil fibers")
    return tuple(records)


def _local_ideal_certificates() -> tuple[LocalIdealCertificate, ...]:
    """Compute the I3/I6 local monomial types at each coordinate point."""

    schemes: tuple[PointScheme, ...] = point_schemes()
    points = ("p_a", "p_b", "p_c")
    pivots = (0, 1, 2)
    local_coordinates = (
        ("b/a", "c/a"),
        ("c/b", "a/b"),
        ("a/c", "b/c"),
    )
    u = Polynomial.monomial((1, 0), scalar_type=Eisenstein)
    v = Polynomial.monomial((0, 1), scalar_type=Eisenstein)
    one = Polynomial.one(2, scalar_type=Eisenstein)
    local_images = ((one, u, v), (v, one, u), (u, v, one))
    certificates: list[LocalIdealCertificate] = []
    for scheme in schemes:
        for point, pivot, coordinates, images in zip(
            points,
            pivots,
            local_coordinates,
            local_images,
            strict=True,
        ):
            linear, nilpotent = coordinates
            ideal_type = "(u,v)" if scheme.name == "I3" else "(u,v^2)"
            localized = tuple(generator.substitute(images) for generator in scheme.ideal_generators)
            expected = (u, v) if scheme.name == "I3" else (u, v**2)
            verified = all(any(item == target for item in localized) for target in expected)
            certificates.append(
                LocalIdealCertificate(
                    scheme.name,
                    point,
                    pivot,
                    linear,
                    nilpotent,
                    ideal_type,
                    tuple(str(generator) for generator in scheme.ideal_generators),
                    verified,
                )
            )
    return tuple(certificates)


def tier_a_pencil_model() -> TierAPencilModel:
    """Build the exact dP9 pencil frontier for the Tier A search."""

    base_locus = _base_locus_algebra()
    blowup_atlas = _pencil_blowup_atlas()
    if not base_locus.reduced_and_transverse:
        raise ValueError("the pencil base locus is not an exact reduced transverse scheme")
    if not blowup_atlas.atlas_consistent:
        raise ValueError("the exact blow-up overlap equations are inconsistent")
    actions = _pencil_actions(base_locus)
    if not all(action.order_three for action in actions):
        raise ValueError("the exact pencil deck actions failed order-three checks")
    actions_commute = _actions_commute(base_locus, actions)
    return TierAPencilModel(
        base_locus,
        blowup_atlas,
        actions,
        actions_commute,
        _singular_points(),
        _local_ideal_certificates(),
        "constructed: six affine hypersurface charts and 30 checked overlaps",
        "not constructed: global Serre cocycles and constituent patching are pending",
    )


__all__ = [
    "BaseLocusAlgebra",
    "BlowupChart",
    "BlowupOverlap",
    "LocalIdealCertificate",
    "PencilDeckAction",
    "PencilBlowupAtlas",
    "ProjectivePoint",
    "QuotientPolynomial",
    "SingularPencilPoint",
    "TierAPencilModel",
    "tier_a_pencil_model",
]
