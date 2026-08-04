"""Exact published geometry and symmetry data for the Schoen carrier.

Owns:
    The Schoen fiber-product cover, free Z3 × Z3 quotient, frozen Cox
    presentation, quotient divisor basis, intersection normalizations, descent
    congruence, Heisenberg lifts, and exact eigen-cubic characters.

Depends on:
    `onetheory.math.geometry`, `linear`, `numbers`, and `polynomials`, plus
    general compactification metadata from `physics.strings`. No engine,
    verification, observation, or research dependency is permitted.

Must not:
    Duplicate generic geometric algorithms, select geometry from observations,
    assert a native-origin derivation, or create metric, bundle, vacuum, or
    physical-Yukawa objects that are not established here.

Phase 0:
    The published carrier geometry and exact project symmetry identities are
    implemented; unresolved downstream physical constructions remain unavailable.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import cast

from onetheory.math.geometry import (
    Basis,
    CharacteristicClass,
    Divisor,
    Normalization,
    TripleIntersectionTensor,
    divisor_square,
    quotient_to_cover,
    slope,
    triple_product,
)
from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, OMEGA2, Eisenstein, Rational
from onetheory.math.polynomials import Polynomial
from onetheory.physics.strings import CompactificationSpace, PublishedPhysicalInput

SCHOEN_COVERING_DEGREE = 9
SCHOEN_GROUP_ORDER = 9
QUOTIENT_BASIS = Basis("Schoen quotient", ("tau1", "tau2", "phi"))
QUOTIENT_NORMALIZATION = Normalization("quotient")
COVER_NORMALIZATION = Normalization("cover")
SCHOEN_INPUT = PublishedPhysicalInput(
    "schoen_quotient_2004",
    "Braun, Ovrut, Pantev, and Reinbacher, Elliptic Calabi-Yau Threefolds "
    "with Z3 x Z3 Wilson Lines",
    "https://arxiv.org/abs/hep-th/0410055",
    "A free Z3 x Z3 quotient of a Schoen fiber-product Calabi-Yau threefold",
)


@dataclass(frozen=True, slots=True)
class FrozenCoxPresentation:
    """The frozen ambient Cox variables, multidegrees, and carrier equations."""

    variables: tuple[str, ...]
    coefficient_relation: str
    multidegrees: tuple[tuple[str, tuple[int, int, int]], ...]
    equations: tuple[str, ...]
    base_identification: str
    cubic_f: Polynomial
    cubic_g: Polynomial


@dataclass(frozen=True, slots=True)
class SchoenFiberProduct:
    """The simply connected fiber-product cover before quotienting."""

    name: str
    base_surfaces: tuple[str, str]
    base_maps: tuple[str, str]
    fiber_product_equation: str
    cox: FrozenCoxPresentation
    space: CompactificationSpace


@dataclass(frozen=True, slots=True)
class FreeQuotient:
    """A declared free finite quotient with its deck-generator names."""

    cover: SchoenFiberProduct
    group_name: str
    generators: tuple[str, str]
    order: int
    acts_freely: bool
    space: CompactificationSpace


@dataclass(frozen=True, slots=True)
class HeisenbergLifts:
    """Exact coordinate lifts whose projectivization gives the deck action."""

    p: Matrix
    t: Matrix
    coefficient: Eisenstein

    @property
    def identity(self) -> Matrix:
        """Return the exact identity in the lift representation."""

        return Matrix.identity(3, scalar_type=Eisenstein)

    @property
    def order_three_p(self) -> bool:
        """Return whether P cubed is the identity."""

        return self.p**3 == self.identity

    @property
    def order_three_t(self) -> bool:
        """Return whether T cubed is the identity."""

        return self.t**3 == self.identity

    @property
    def projective_commutator(self) -> bool:
        """Return whether PT equals omega times TP."""

        return self.p @ self.t == (self.t @ self.p).scale(self.coefficient)

    @property
    def deck_commutator(self) -> bool:
        """Return whether the commutator is scalar and hence projectively trivial."""

        return self.projective_commutator and self.coefficient**3 == Eisenstein(1)


@dataclass(frozen=True, slots=True)
class EigenCubic:
    """A frozen cubic with exact P and T transformation characters."""

    name: str
    polynomial: Polynomial
    p_character: Eisenstein
    t_character: Eisenstein

    def transform_p(self, images: Iterable[tuple[object, Iterable[int]]]) -> Polynomial:
        """Apply the exact P monomial substitution."""

        return self.polynomial.substitute_monomials(tuple(images))

    def transform_t(self, images: Iterable[tuple[object, Iterable[int]]]) -> Polynomial:
        """Apply the exact T monomial substitution."""

        return self.polynomial.substitute_monomials(tuple(images))


@dataclass(frozen=True, slots=True)
class SchoenGeometry:
    """The complete exact carrier geometry handoff used by later model modules."""

    cover: SchoenFiberProduct
    quotient: FreeQuotient
    basis: Basis
    quotient_intersections: TripleIntersectionTensor
    cover_intersections: TripleIntersectionTensor
    heisenberg: HeisenbergLifts
    eigen_cubics: tuple[EigenCubic, ...]
    descent_modulus: int

    def quotient_divisor(self, coordinates: Iterable[object]) -> Divisor:
        """Create a divisor in the named quotient basis and normalization."""

        return Divisor(self.basis, coordinates, QUOTIENT_NORMALIZATION)

    def cover_divisor(self, coordinates: Iterable[object]) -> Divisor:
        """Create a divisor in the named cover basis and normalization."""

        return Divisor(self.basis, coordinates, COVER_NORMALIZATION)

    def quotient_class(
        self, coordinates: Iterable[object], degree: int
    ) -> CharacteristicClass:
        """Create a characteristic class in quotient normalization."""

        return CharacteristicClass(self.basis, coordinates, degree, QUOTIENT_NORMALIZATION)

    def cover_class(self, coordinates: Iterable[object], degree: int) -> CharacteristicClass:
        """Create a characteristic class in cover normalization."""

        return CharacteristicClass(self.basis, coordinates, degree, COVER_NORMALIZATION)

    def descent_congruence(self, coordinates: Iterable[object]) -> bool:
        """Check the necessary a+b congruence for a quotient line class."""

        values = tuple(coordinates)
        if len(values) != self.basis.dimension:
            raise ValueError("descent coordinates must use the quotient basis")
        if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
            raise TypeError("descent congruence requires integral coordinates")
        integer_values = cast(tuple[int, ...], values)
        return (integer_values[0] + integer_values[1]) % self.descent_modulus == 0

    def square(self, divisor: Divisor) -> tuple[Rational, ...]:
        """Return the exact basis coordinates of a divisor square."""

        return divisor_square(self.quotient_intersections, divisor).coordinates

    def triple(self, left: Divisor, middle: Divisor, right: Divisor) -> Rational:
        """Evaluate one exact carrier triple intersection."""

        return triple_product(self.quotient_intersections, left, middle, right)

    def bundle_slope(self, first_chern: Divisor, kahler: Divisor, rank: int) -> Rational:
        """Evaluate an exact quotient-normalized slope."""

        return slope(self.quotient_intersections, first_chern, kahler, rank)

    def cover_slope(self, first_chern: Divisor, kahler: Divisor, rank: int) -> Rational:
        """Evaluate the corresponding cover-normalized slope."""

        return slope(self.cover_intersections, first_chern, kahler, rank)


def _frozen_cubics() -> FrozenCoxPresentation:
    """Construct the exact frozen Cox presentation and eigen-cubics."""

    x0 = Polynomial.monomial((1, 0, 0), scalar_type=Eisenstein)
    x1 = Polynomial.monomial((0, 1, 0), scalar_type=Eisenstein)
    x2 = Polynomial.monomial((0, 0, 1), scalar_type=Eisenstein)
    f = (
        (x0**3).scale(-3 - 3 * OMEGA)
        + (x1**3).scale(3)
        + (x2**3).scale(3 * OMEGA)
    )
    g = (
        (x0**3 + x1**3 + x2**3).scale(-3 - 6 * OMEGA)
        + (x0 * x1 * x2).scale(36 + 18 * OMEGA)
    )
    return FrozenCoxPresentation(
        ("x0", "x1", "x2", "mu", "nu", "u0", "u1", "u2"),
        "omega^2 + omega + 1 = 0",
        (
            ("(x0,x1,x2)", (1, 0, 0)),
            ("(mu,nu)", (0, 1, 0)),
            ("(u0,u1,u2)", (0, 0, 1)),
            ("p1", (3, 1, 0)),
            ("p2", (0, 1, 3)),
        ),
        ("p1 = mu F(x) + nu G(x)", "p2 = 2 nu F(u) + mu G(u)"),
        "mu:nu = 2 nu^2:mu^2",
        f,
        g,
    )


def _heisenberg() -> HeisenbergLifts:
    """Construct the exact P, D, T coordinate lift used by the carrier."""

    p = Matrix(((0, 1, 0), (0, 0, 1), (1, 0, 0)), scalar_type=Eisenstein)
    diagonal = Matrix(
        ((1, 0, 0), (0, OMEGA, 0), (0, 0, OMEGA2)),
        scalar_type=Eisenstein,
    )
    return HeisenbergLifts(p, p.matmul(diagonal), OMEGA)


def schoen_geometry() -> SchoenGeometry:
    """Assemble the published cover, quotient, intersections, and symmetry data."""

    cover_space = CompactificationSpace("Schoen cover", 3, 1, 1, SCHOEN_INPUT)
    quotient_space = CompactificationSpace("Schoen quotient", 3, 9, 9, SCHOEN_INPUT)
    cox = _frozen_cubics()
    cover = SchoenFiberProduct(
        "Schoen fiber-product cover",
        ("B1", "B2"),
        ("beta1", "beta2"),
        "beta1(p1) = beta2(p2)",
        cox,
        cover_space,
    )
    quotient = FreeQuotient(
        cover,
        "Z3 x Z3",
        ("g1", "g2"),
        SCHOEN_GROUP_ORDER,
        True,
        quotient_space,
    )
    intersections = TripleIntersectionTensor(
        QUOTIENT_BASIS,
        {
            (0, 0, 1): Rational(1, 3),
            (0, 1, 1): Rational(1, 3),
            (0, 1, 2): Rational(1),
        },
        QUOTIENT_NORMALIZATION,
    )
    p_images = ((OMEGA, (0, 1, 0)), (OMEGA2, (0, 0, 1)), (1, (1, 0, 0)))
    t_images = ((1, (1, 0, 0)), (OMEGA, (0, 1, 0)), (OMEGA2, (0, 0, 1)))
    eigen_cubics = (
        EigenCubic("F", cox.cubic_f, OMEGA2, Eisenstein(1)),
        EigenCubic("G", cox.cubic_g, Eisenstein(1), Eisenstein(1)),
    )
    for cubic, expected_p, expected_t in (
        (eigen_cubics[0], p_images, t_images),
        (eigen_cubics[1], p_images, t_images),
    ):
        transformed_p = cubic.transform_p(expected_p)
        transformed_t = cubic.transform_t(expected_t)
        if transformed_p != cubic.polynomial.scale(cubic.p_character):
            raise ValueError(f"frozen P character failed for {cubic.name}")
        if transformed_t != cubic.polynomial.scale(cubic.t_character):
            raise ValueError(f"frozen T character failed for {cubic.name}")
    geometry = SchoenGeometry(
        cover,
        quotient,
        QUOTIENT_BASIS,
        intersections,
        intersections.to_cover(SCHOEN_COVERING_DEGREE),
        _heisenberg(),
        eigen_cubics,
        3,
    )
    if not geometry.quotient.acts_freely or geometry.quotient.order != 9:
        raise ValueError("the published Schoen quotient must be free of order nine")
    return geometry


def quotient_to_cover_divisor(divisor: Divisor) -> Divisor:
    """Convert quotient divisor normalization with the explicit degree nine."""

    return cast(Divisor, quotient_to_cover(divisor, SCHOEN_COVERING_DEGREE))
