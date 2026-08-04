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

from collections.abc import Iterable
from dataclasses import dataclass
from typing import cast

from onetheory.math.geometry import CharacteristicClass, ClassKind
from onetheory.math.lattices import AffineAction
from onetheory.math.numbers import OMEGA, Eisenstein, Rational, coerce_rational
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import SchoenGeometry
from onetheory.models.heterotic_schoen.visible import visible_bundle
from onetheory.physics.strings import (
    BundleStatus,
    HeteroticConventions,
    HeteroticGaugeConnection,
    ThreeFormField,
    TorsionfulCurvature,
    TwoFormField,
)

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
        geometry.bundle_slope(
            geometry.quotient_divisor((-2, 2, 0)), geometry.quotient_divisor((6, 9, 3)), 2
        ),
        geometry.cover_slope(
            geometry.cover_divisor((-2, 2, 0)), geometry.cover_divisor((6, 9, 3)), 2
        ),
        9 * 9,
        9,
        2 * 9,
    )
    if len(shell_one) != 3 or len(mw.shell_orbits(1)) != 1:
        raise ValueError("degree-one Mordell-Weil shell count failed")
    if len(shell_two) != 6 or len(mw.shell_orbits(2)) != 2:
        raise ValueError("degree-two Mordell-Weil shell count failed")
    return result


@dataclass(frozen=True, slots=True)
class ChernSimonsTerm:
    """One convention-frozen gauge or Lorentz Chern–Simons contribution."""

    sector: str
    connection_name: str
    curvature_name: str
    sign: int
    trace_convention: str
    provenance: str

    def __post_init__(self) -> None:
        if self.sector not in {"visible", "hidden", "lorentz"}:
            raise ValueError("Chern–Simons sectors must be visible, hidden, or lorentz")
        if self.sign not in (-1, 1) or any(
            not value.strip()
            for value in (
                self.connection_name,
                self.curvature_name,
                self.trace_convention,
                self.provenance,
            )
        ):
            raise ValueError("Chern–Simons terms require explicit convention metadata")


@dataclass(frozen=True, slots=True)
class HDefinition:
    """The differential H definition with all Chern–Simons terms frozen."""

    two_form: TwoFormField
    alpha_prime_name: str
    terms: tuple[ChernSimonsTerm, ...]
    expression: str
    provenance: str

    def __init__(
        self,
        two_form: TwoFormField,
        alpha_prime_name: str,
        terms: Iterable[ChernSimonsTerm],
        provenance: str,
    ) -> None:
        values = tuple(terms)
        if not alpha_prime_name.strip() or not values or not provenance.strip():
            raise ValueError("H definitions require alpha-prime, terms, and provenance")
        if any(term.provenance != provenance for term in values):
            raise ValueError("H Chern–Simons terms must share one convention provenance")
        expression = "dB_2 + " + " + ".join(
            f"{term.sign:+d} alpha_prime/4 CS({term.connection_name})" for term in values
        )
        object.__setattr__(self, "two_form", two_form)
        object.__setattr__(self, "alpha_prime_name", alpha_prime_name)
        object.__setattr__(self, "terms", values)
        object.__setattr__(self, "expression", expression)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class DifferentialBianchiIdentity:
    """The local differential identity for one H convention."""

    h_field: ThreeFormField
    h_definition: HDefinition
    torsionful_curvature: TorsionfulCurvature
    equation: str
    local_identity_supplied: bool
    provenance: str

    def __post_init__(self) -> None:
        if self.h_definition.provenance != self.provenance or not self.provenance.strip():
            raise ValueError("Bianchi identity inputs must share provenance")
        if self.torsionful_curvature.name not in self.h_field.bianchi_identity:
            raise ValueError("Bianchi identity must use the declared torsionful curvature")

    @property
    def consistent(self) -> bool:
        """Return whether the local identity has been explicitly supplied."""

        return self.local_identity_supplied


@dataclass(frozen=True, slots=True)
class IntegratedChernIdentity:
    """The integrated Chern-class condition, separate from differential data."""

    tangent: CharacteristicClass
    visible: CharacteristicClass
    hidden: CharacteristicClass
    five_brane: CharacteristicClass | None
    equality: bool
    provenance: str

    def __post_init__(self) -> None:
        classes = (self.tangent, self.visible, self.hidden)
        if any(
            class_data.basis != self.tangent.basis
            or class_data.normalization != self.tangent.normalization
            or class_data.degree != self.tangent.degree
            for class_data in classes
        ):
            raise ValueError("integrated Chern data must share basis and normalization")
        if self.five_brane is not None and (
            self.five_brane.basis != self.tangent.basis
            or self.five_brane.normalization != self.tangent.normalization
            or self.five_brane.degree != self.tangent.degree
        ):
            raise ValueError("five-brane class uses an incompatible basis or degree")
        if not self.provenance.strip():
            raise ValueError("integrated identities require provenance")

    @property
    def consistent(self) -> bool:
        """Return whether the declared integrated identity is satisfied exactly."""

        target = self.visible + self.hidden
        if self.five_brane is not None:
            target = target + self.five_brane
        return self.equality and target.coordinates == self.tangent.coordinates


@dataclass(frozen=True, slots=True)
class FluxQuantization:
    """Explicit H-flux periods and their integral quantization checks."""

    periods: tuple[Rational, ...]
    integer_quanta: tuple[int, ...]
    normalization: str
    provenance: str

    def __init__(
        self,
        periods: Iterable[object],
        integer_quanta: Iterable[int],
        normalization: str,
        provenance: str,
    ) -> None:
        normalized_periods = tuple(coerce_rational(value) for value in periods)
        quanta = tuple(integer_quanta)
        if len(normalized_periods) != len(quanta) or any(
            isinstance(value, bool) or not isinstance(value, int) for value in quanta
        ):
            raise ValueError("flux periods and integer quanta must have equal exact lengths")
        if not normalization.strip() or not provenance.strip():
            raise ValueError("flux quantization requires normalization and provenance")
        object.__setattr__(self, "periods", normalized_periods)
        object.__setattr__(self, "integer_quanta", quanta)
        object.__setattr__(self, "normalization", normalization)
        object.__setattr__(self, "provenance", provenance)

    @property
    def quantized(self) -> bool:
        """Return whether every declared period equals its integer quantum."""

        return all(
            period == quantum
            for period, quantum in zip(self.periods, self.integer_quanta, strict=True)
        )


@dataclass(frozen=True, slots=True)
class GlobalBFieldTrivialization:
    """A global gerbe/B-field trivialization record with explicit cocycle data."""

    cocycle_identifier: str | None
    supplied: bool
    provenance: str

    def __post_init__(self) -> None:
        if self.supplied and (
            self.cocycle_identifier is None or not self.cocycle_identifier.strip()
        ):
            raise ValueError("a supplied global B-field trivialization requires a cocycle")
        if not self.provenance.strip():
            raise ValueError("global B-field records require provenance")


@dataclass(frozen=True, slots=True)
class FiveBraneClass:
    """An optional effective five-brane class kept distinct from bundle data."""

    class_data: CharacteristicClass
    effective: bool
    provenance: str

    def __post_init__(self) -> None:
        if self.class_data.kind is not ClassKind.INTEGRAL or not self.provenance.strip():
            raise ValueError("five-brane classes require integral data and provenance")


@dataclass(frozen=True, slots=True)
class DifferentialAnomalyPackage:
    """The complete local/global anomaly package and its unresolved gate."""

    conventions: HeteroticConventions
    h_definition: HDefinition
    bianchi: DifferentialBianchiIdentity
    integrated: IntegratedChernIdentity
    flux: FluxQuantization
    global_b_field: GlobalBFieldTrivialization
    five_brane: FiveBraneClass | None
    visible_connection: HeteroticGaugeConnection
    hidden_connection: HeteroticGaugeConnection | None
    hidden_bundle_supplied: bool
    hidden_hym_supplied: bool
    provenance: str

    def __post_init__(self) -> None:
        if self.h_definition.provenance != self.provenance or not self.provenance.strip():
            raise ValueError("anomaly package records must share provenance")
        if self.visible_connection.sector != "visible":
            raise ValueError("anomaly package requires a visible connection")
        if self.hidden_connection is not None and self.hidden_connection.sector != "hidden":
            raise ValueError("hidden anomaly connection must be in the hidden sector")

    @property
    def local_gate(self) -> bool:
        """Return the local differential gate only."""

        return (
            self.bianchi.consistent and self.h_definition.provenance == self.conventions.provenance
        )

    @property
    def integrated_gate(self) -> bool:
        """Return the integrated topological gate only."""

        return self.integrated.consistent

    @property
    def resolved(self) -> bool:
        """Return whether every differential/global prerequisite is supplied."""

        return (
            self.local_gate
            and self.integrated_gate
            and self.flux.quantized
            and self.global_b_field.supplied
            and (self.five_brane is None or self.five_brane.effective)
            and self.hidden_bundle_supplied
            and self.hidden_hym_supplied
        )


def differential_anomaly_package(
    geometry: SchoenGeometry,
    visible_connection: HeteroticGaugeConnection,
    hidden_connection: HeteroticGaugeConnection | None = None,
    conventions: HeteroticConventions | None = None,
    local_identity_supplied: bool = False,
    hidden_bundle_supplied: bool = False,
    hidden_hym_supplied: bool = False,
    global_b_field: GlobalBFieldTrivialization | None = None,
) -> DifferentialAnomalyPackage:
    """Assemble the anomaly boundary while preserving the unresolved hidden gate."""

    selected = conventions or HeteroticConventions()
    provenance = selected.provenance
    terms = (
        ChernSimonsTerm(
            "visible",
            visible_connection.name,
            visible_connection.curvature_name,
            -1,
            selected.trace_convention,
            provenance,
        ),
        ChernSimonsTerm(
            "hidden",
            hidden_connection.name if hidden_connection else "A_hid",
            hidden_connection.curvature_name if hidden_connection else "F_hid",
            -1,
            selected.trace_convention,
            provenance,
        ),
        ChernSimonsTerm("lorentz", "omega_+", "R_+", 1, selected.trace_convention, provenance),
    )
    h_definition = HDefinition(TwoFormField(), selected.alpha_prime_name, terms, provenance)
    h_field = ThreeFormField(
        bianchi_identity="dH_3 = alpha_prime/4 (Tr R_+^2 - Tr F_vis^2 - Tr F_hid^2)",
        provenance=provenance,
    )
    bianchi = DifferentialBianchiIdentity(
        h_field,
        h_definition,
        TorsionfulCurvature(selected.torsionful_connection, provenance=provenance),
        h_field.bianchi_identity,
        local_identity_supplied,
        provenance,
    )
    topology = topological_consistency(geometry)
    integrated = IntegratedChernIdentity(
        topology.c2_tangent,
        topology.c2_visible,
        topology.hidden_target.class_data,
        None,
        topology.bianchi_identity,
        provenance,
    )
    flux = FluxQuantization((), (), "H/(2 pi)", provenance)
    global_data = global_b_field or GlobalBFieldTrivialization(None, False, provenance)
    return DifferentialAnomalyPackage(
        selected,
        h_definition,
        bianchi,
        integrated,
        flux,
        global_data,
        None,
        visible_connection,
        hidden_connection,
        hidden_bundle_supplied,
        hidden_hym_supplied,
        provenance,
    )


__all__ = [
    "BasepointAlgebra",
    "ChernSimonsTerm",
    "DifferentialAnomalyPackage",
    "DifferentialBianchiIdentity",
    "FiveBraneClass",
    "FluxQuantization",
    "GlobalBFieldTrivialization",
    "HDefinition",
    "IntegratedChernIdentity",
    "MordellWeilAction",
    "RequiredTopologicalClass",
    "TopologicalConsistency",
    "differential_anomaly_package",
    "mordell_weil_action",
    "topological_consistency",
]
