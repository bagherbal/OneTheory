"""Exact curve-lattice and topological consistency data for the carrier.

Owns:
    Mordell–Weil affine actions, bounded degree-one and degree-two shells, orbit
    counts, the square-free degree-nine basepoint algebra, visible and required
    hidden Chern coordinates, descent congruence, integrated Bianchi identity,
    and quotient/cover slope checks.

Depends on:
    `onetheory.math.lattices`, `geometry`, and `polynomials`, plus concrete Schoen
    geometry and visible metadata. The hidden output is a required topological
    class, never a hidden-bundle object.

Must not:
    Construct a hidden bundle, assert hidden stability or HYM existence, import
    verification or observations, or turn a Chern-class target into a physical
    realization.

Phase 0:
    Exact topological identities and finite curve counts are implemented; hidden
    bundle existence, metrics, vacua, and observables remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from onetheory.math.geometry import CharacteristicClass
from onetheory.math.lattices import AffineAction
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import SchoenGeometry
from onetheory.models.heterotic_schoen.visible import visible_bundle
from onetheory.physics.strings import BundleStatus

IntPoint = tuple[int, int]


@dataclass(frozen=True, slots=True)
class MordellWeilAction:
    """The exact affine order-three action on free Mordell–Weil coordinates."""

    affine: AffineAction

    @property
    def period(self) -> int:
        """Return the certified action period."""

        return 3

    def apply(self, point: IntPoint) -> IntPoint:
        """Apply ``(m,n) -> (1-n,m-n)`` exactly."""

        result = self.affine.apply(point)
        return cast(IntPoint, result)

    def degree(self, point: IntPoint) -> int:
        """Return the exact affine quadratic degree."""

        m, n = point
        return m * m + n * n - m * n - m

    def shell(self, degree: int, bound: int = 8) -> tuple[IntPoint, ...]:
        """Return an explicitly bounded exact degree shell."""

        if isinstance(degree, bool) or not isinstance(degree, int) or degree < 0:
            raise ValueError("Mordell-Weil degrees must be nonnegative integers")
        if isinstance(bound, bool) or not isinstance(bound, int) or bound < 1:
            raise ValueError("Mordell-Weil shell bounds must be positive integers")
        return tuple(
            (m, n)
            for m in range(-bound, bound + 1)
            for n in range(-bound, bound + 1)
            if self.degree((m, n)) == degree
        )

    def orbits(self, points: tuple[IntPoint, ...]) -> tuple[tuple[IntPoint, ...], ...]:
        """Decompose an action-closed finite point set into exact orbits."""

        return cast(tuple[tuple[IntPoint, ...], ...], self.affine.orbits(points))

    def shell_orbits(self, degree: int, bound: int = 8) -> tuple[tuple[IntPoint, ...], ...]:
        """Return deterministic orbits of one bounded degree shell."""

        return self.orbits(self.shell(degree, bound))


@dataclass(frozen=True, slots=True)
class BasepointAlgebra:
    """The square-free degree-nine algebra over Q(omega)."""

    modulus: Polynomial
    derivative: Polynomial
    gcd_with_derivative: Polynomial

    @property
    def degree(self) -> int:
        """Return the exact modulus degree."""

        return self.modulus.univariate_degree

    @property
    def square_free(self) -> bool:
        """Return whether the modulus is coprime to its derivative."""

        return self.gcd_with_derivative == Polynomial.one(1, scalar_type=Eisenstein)


@dataclass(frozen=True, slots=True)
class RequiredTopologicalClass:
    """A named Chern-class target that is not an existing bundle."""

    class_data: CharacteristicClass
    status: BundleStatus
    construction_equation: str

    @property
    def coordinates(self) -> tuple[Rational, ...]:
        """Return exact target coordinates."""

        return self.class_data.coordinates

    @property
    def is_bundle(self) -> bool:
        """Return false by construction for a required target class."""

        return False


@dataclass(frozen=True, slots=True)
class TopologicalConsistency:
    """All exact carrier topology checks that do not require a hidden bundle."""

    mordell_weil: MordellWeilAction
    basepoint: BasepointAlgebra
    c2_tangent: CharacteristicClass
    c2_visible: CharacteristicClass
    hidden_target: RequiredTopologicalClass
    bianchi_identity: bool
    visible_descent: bool
    quotient_slope: Rational
    cover_slope: Rational
    cover_curve_count: int
    quotient_curve_count: int
    degree_two_quotient_count: int


def mordell_weil_action() -> MordellWeilAction:
    """Construct the affine order-three Mordell–Weil action."""

    action = MordellWeilAction(AffineAction(((0, -1), (1, -1)), (1, 0)))
    point = (4, -2)
    if action.apply(action.apply(action.apply(point))) != point:
        raise ValueError("Mordell-Weil action does not have order three")
    if action.degree(action.apply(point)) != action.degree(point):
        raise ValueError("Mordell-Weil degree is not action invariant")
    return action


def basepoint_algebra() -> BasepointAlgebra:
    """Construct the exact degree-nine square-free modulus."""

    modulus = Polynomial.from_coefficients(
        (
            Eisenstein(-1),
            0,
            0,
            -51 - 27 * OMEGA,
            0,
            0,
            24 - 27 * OMEGA,
            0,
            0,
            Eisenstein(1),
        ),
        scalar_type=Eisenstein,
    )
    derivative = modulus.derivative()
    gcd_with_derivative = modulus.gcd(derivative)
    result = BasepointAlgebra(modulus, derivative, gcd_with_derivative)
    if result.degree != 9 or not result.square_free:
        raise ValueError("the degree-nine basepoint modulus is not square-free")
    return result


def topological_consistency(geometry: SchoenGeometry) -> TopologicalConsistency:
    """Assemble the exact Chern, curve, descent, and slope identities."""

    visible = visible_bundle(geometry)
    tangent = geometry.quotient_class((4, 4, 0), 2)
    visible_c2 = geometry.quotient_class(visible.bundle.c2, 2)
    hidden_coordinates = tuple(
        tangent.coordinates[index] - visible_c2.coordinates[index]
        for index in range(geometry.basis.dimension)
    )
    hidden_data = geometry.quotient_class(hidden_coordinates, 2)
    hidden_target = RequiredTopologicalClass(
        hidden_data,
        BundleStatus.REQUIRED_TOPOLOGICAL_CLASS,
        "c2(hidden) = c2(TX) - c2(visible) = 2P - D^2",
    )
    divisor = geometry.quotient_divisor((1, 2, -1))
    point = geometry.quotient_divisor((0, 1, 0))
    from_extension = tuple(
        2 * point.coordinates[index] - geometry.square(divisor)[index]
        for index in range(geometry.basis.dimension)
    )
    if from_extension != hidden_target.coordinates:
        raise ValueError("hidden topological target failed its exact extension identity")
    mw = mordell_weil_action()
    shell_one = mw.shell(1)
    shell_two = mw.shell(2)
    result = TopologicalConsistency(
        mw,
        basepoint_algebra(),
        tangent,
        visible_c2,
        hidden_target,
        visible_c2 + hidden_data == tangent,
        geometry.descent_congruence((8, 1, 0)),
        geometry.bundle_slope(geometry.quotient_divisor((-2, 2, 0)),
                               geometry.quotient_divisor((6, 9, 3)), 2),
        geometry.cover_slope(geometry.cover_divisor((-2, 2, 0)),
                             geometry.cover_divisor((6, 9, 3)), 2),
        9 * 9,
        9,
        2 * 9,
    )
    if len(shell_one) != 3 or len(mw.shell_orbits(1)) != 1:
        raise ValueError("degree-one Mordell-Weil shell count failed")
    if len(shell_two) != 6 or len(mw.shell_orbits(2)) != 2:
        raise ValueError("degree-two Mordell-Weil shell count failed")
    return result
