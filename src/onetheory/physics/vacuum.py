"""Symbolic four-dimensional N=1 effective-action and vacuum structures.

Owns:
    Chiral and vector multiplets, provenance-carrying Kähler potentials, superpotentials,
    gauge kinetic matrices, moment maps, F/D-term potentials, gravitino masses, kinetic
    matrices, critical-point conditions, vacuum classifications, Hessians, and stability.

Depends on:
    Exact rational linear algebra and explicit fail-closed errors only; it is independent
    of any selected compactification, carrier, observation, or research experiment.

Must not:
    Guess carrier coefficients, combine terms from different moduli points, report a
    stabilized vacuum without supplied equations, or use measured data upstream.

Phase 0:
    Symbolic N=1 structures are implemented; carrier coefficients and controlled vacuum
    solutions remain unresolved prerequisites.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum

from onetheory.core.errors import IncompatibleConvention
from onetheory.math.linear import Matrix
from onetheory.math.numbers import Rational


@dataclass(frozen=True, slots=True)
class ModuliPoint:
    """An immutable named point at which all effective data are evaluated."""

    label: str
    coordinates: tuple[str, ...]
    provenance: str

    def __init__(
        self,
        label: str,
        coordinates: Iterable[str] = (),
        provenance: str = "moduli-point declaration",
    ) -> None:
        values = tuple(coordinates)
        if (
            not label.strip()
            or any(not value.strip() for value in values)
            or not provenance.strip()
        ):
            raise ValueError("moduli points require named exact coordinates and provenance")
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "coordinates", values)
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class EffectiveExpression:
    """A symbolic effective-action expression with complete evaluation metadata."""

    expression: str
    provenance: str
    dependencies: tuple[str, ...]
    moduli_point: ModuliPoint
    approximation_order: str
    normalization: str

    def __init__(
        self,
        expression: str,
        provenance: str,
        dependencies: Iterable[str],
        moduli_point: ModuliPoint,
        approximation_order: str,
        normalization: str,
    ) -> None:
        values = tuple(dependencies)
        if (
            not expression.strip()
            or not provenance.strip()
            or any(not value.strip() for value in values)
            or not approximation_order.strip()
            or not normalization.strip()
        ):
            raise ValueError("effective expressions require complete provenance metadata")
        object.__setattr__(self, "expression", expression)
        object.__setattr__(self, "provenance", provenance)
        object.__setattr__(self, "dependencies", values)
        object.__setattr__(self, "moduli_point", moduli_point)
        object.__setattr__(self, "approximation_order", approximation_order)
        object.__setattr__(self, "normalization", normalization)

    def combine(self, *others: EffectiveExpression, operator: str = "+") -> EffectiveExpression:
        """Combine expressions only at the same moduli point and normalization."""

        expressions = (self, *others)
        if any(item.moduli_point != self.moduli_point for item in expressions):
            raise IncompatibleConvention(
                "effective terms were evaluated at different moduli points"
            )
        if any(item.normalization != self.normalization for item in expressions):
            raise IncompatibleConvention("effective terms use different normalizations")
        if not operator.strip():
            raise ValueError("expression combinations require an operator")
        return EffectiveExpression(
            f" {operator} ".join(f"({item.expression})" for item in expressions),
            " + ".join(item.provenance for item in expressions),
            tuple(dependency for item in expressions for dependency in item.dependencies),
            self.moduli_point,
            "; ".join(item.approximation_order for item in expressions),
            self.normalization,
        )


@dataclass(frozen=True, slots=True)
class ChiralMultiplet:
    """A named N=1 chiral multiplet with a moduli-space identity."""

    name: str
    scalar_name: str
    fermion_name: str
    moduli_point: ModuliPoint
    provenance: str

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (self.name, self.scalar_name, self.fermion_name, self.provenance)
        ):
            raise ValueError("chiral multiplets require complete names and provenance")


@dataclass(frozen=True, slots=True)
class VectorMultiplet:
    """A named N=1 vector multiplet for one gauge factor."""

    name: str
    gauge_factor: str
    vector_name: str
    gaugino_name: str
    moduli_point: ModuliPoint
    provenance: str

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (
                self.name,
                self.gauge_factor,
                self.vector_name,
                self.gaugino_name,
                self.provenance,
            )
        ):
            raise ValueError("vector multiplets require complete names and provenance")


@dataclass(frozen=True, slots=True)
class KaehlerPotential:
    """A symbolic Kähler potential and its declared moduli dependencies."""

    expression: EffectiveExpression
    chiral_fields: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.chiral_fields:
            raise ValueError("Kähler potentials require at least one chiral field")

    @property
    def name(self) -> str:
        """Return the standard K symbol."""

        return "K"


KahlerPotential = KaehlerPotential


@dataclass(frozen=True, slots=True)
class Superpotential:
    """A holomorphic superpotential expression with explicit source provenance."""

    expression: EffectiveExpression
    chiral_fields: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.chiral_fields:
            raise ValueError("superpotentials require at least one chiral field")

    @property
    def name(self) -> str:
        """Return the standard W symbol."""

        return "W"


@dataclass(frozen=True, slots=True)
class GaugeKineticMatrix:
    """A symbolic symmetric gauge kinetic matrix f_ab."""

    factors: tuple[str, ...]
    entries: tuple[tuple[tuple[str, str], EffectiveExpression], ...]

    def __init__(
        self,
        factors: Iterable[str],
        entries: Mapping[tuple[str, str], EffectiveExpression],
    ) -> None:
        names = tuple(factors)
        if not names or len(set(names)) != len(names):
            raise ValueError("gauge kinetic matrices require unique factors")
        values = tuple(sorted(entries.items()))
        if any(left not in names or right not in names for (left, right), _ in values):
            raise ValueError("gauge kinetic matrix contains an undeclared factor")
        if any(entries.get((right, left)) != expression for (left, right), expression in values):
            raise ValueError("gauge kinetic matrices must be explicitly symmetric")
        object.__setattr__(self, "factors", names)
        object.__setattr__(self, "entries", values)

    def entry(self, left: str, right: str) -> EffectiveExpression:
        """Return one explicitly supplied matrix entry."""

        return dict(self.entries)[(left, right)]


@dataclass(frozen=True, slots=True)
class MomentMap:
    """A symbolic moment-map expression for one gauge factor."""

    gauge_factor: str
    expression: EffectiveExpression

    def __post_init__(self) -> None:
        if not self.gauge_factor.strip():
            raise ValueError("moment maps require a gauge factor")


@dataclass(frozen=True, slots=True)
class FTermPotential:
    """The N=1 F-term potential formula before carrier coefficient substitution."""

    kahler: KaehlerPotential
    superpotential: Superpotential
    expression: EffectiveExpression

    @classmethod
    def from_data(cls, kahler: KaehlerPotential, superpotential: Superpotential) -> FTermPotential:
        """Construct the standard symbolic F-term formula."""

        base = kahler.expression.combine(superpotential.expression, operator="+")
        expression = EffectiveExpression(
            "exp(K) (K^{i bar j} D_i W D_bar j W_bar - 3 |W|^2)",
            "N=1 supergravity F-term formula",
            (*base.dependencies, "inverse Kahler metric"),
            base.moduli_point,
            base.approximation_order,
            base.normalization,
        )
        return cls(kahler, superpotential, expression)


@dataclass(frozen=True, slots=True)
class DTermPotential:
    """The N=1 D-term potential assembled from explicit moment maps and f_ab."""

    gauge_kinetic: GaugeKineticMatrix
    moment_maps: tuple[MomentMap, ...]
    expression: EffectiveExpression

    @classmethod
    def from_data(
        cls,
        gauge_kinetic: GaugeKineticMatrix,
        moment_maps: Iterable[MomentMap],
    ) -> DTermPotential:
        values = tuple(moment_maps)
        if {item.gauge_factor for item in values} - set(gauge_kinetic.factors):
            raise ValueError("D-term moment maps use undeclared gauge factors")
        if not values:
            raise ValueError("D-term potentials require explicit moment maps")
        first = values[0].expression
        if any(item.expression.moduli_point != first.moduli_point for item in values):
            raise IncompatibleConvention("D-term inputs use different moduli points")
        expression = EffectiveExpression(
            "1/2 Re(f)^(-1)^{ab} D_a D_b",
            "N=1 supergravity D-term formula",
            tuple(dependency for item in values for dependency in item.expression.dependencies),
            first.moduli_point,
            first.approximation_order,
            first.normalization,
        )
        return cls(gauge_kinetic, values, expression)


@dataclass(frozen=True, slots=True)
class ScalarPotential:
    """The total F-plus-D scalar potential at one common moduli point."""

    f_term: FTermPotential
    d_term: DTermPotential
    expression: EffectiveExpression

    @classmethod
    def from_terms(cls, f_term: FTermPotential, d_term: DTermPotential) -> ScalarPotential:
        expression = f_term.expression.combine(d_term.expression)
        return cls(f_term, d_term, expression)


@dataclass(frozen=True, slots=True)
class GravitinoMass:
    """The symbolic N=1 gravitino mass expression."""

    expression: EffectiveExpression

    @classmethod
    def from_data(cls, kahler: KaehlerPotential, superpotential: Superpotential) -> GravitinoMass:
        base = kahler.expression.combine(superpotential.expression)
        return cls(
            EffectiveExpression(
                "exp(K/2) W / M_Pl^2",
                "N=1 gravitino mass formula",
                (*base.dependencies, "Planck normalization"),
                base.moduli_point,
                base.approximation_order,
                base.normalization,
            )
        )


@dataclass(frozen=True, slots=True)
class KineticMatrix:
    """An exact symmetric kinetic matrix with a positivity certificate."""

    name: str
    matrix: Matrix
    moduli_point: ModuliPoint
    provenance: str

    def __post_init__(self) -> None:
        if (
            self.matrix.row_count != self.matrix.column_count
            or not self.name.strip()
            or not self.provenance.strip()
        ):
            raise ValueError("kinetic matrices must be square and named")

    @property
    def positive_definite(self) -> bool:
        """Check positive definiteness by exact leading principal minors."""

        for size in range(1, self.matrix.row_count + 1):
            minor = Matrix(
                tuple(
                    tuple(self.matrix[row][column] for column in range(size)) for row in range(size)
                ),
                scalar_type=self.matrix.scalar_type,
            ).determinant()
            if not isinstance(minor, Rational) or minor <= 0:
                return False
        return True


@dataclass(frozen=True, slots=True)
class CriticalPointConditions:
    """The symbolic F-flat, D-flat, and stationarity conditions."""

    equations: tuple[str, ...]
    moduli_point: ModuliPoint
    supersymmetric: bool
    provenance: str

    def __post_init__(self) -> None:
        if (
            not self.equations
            or any(not equation.strip() for equation in self.equations)
            or not self.provenance.strip()
        ):
            raise ValueError("critical-point conditions require equations and provenance")


class VacuumType(StrEnum):
    """Cosmological classification of a critical point."""

    MINKOWSKI = "Minkowski"
    ADS = "AdS"
    DESITTER = "de Sitter"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True, slots=True)
class Hessian:
    """An exact or symbolic Hessian with its evaluation point."""

    matrix: Matrix | None
    expression: str
    moduli_point: ModuliPoint
    provenance: str

    def __post_init__(self) -> None:
        if not self.expression.strip() or not self.provenance.strip():
            raise ValueError("Hessians require symbolic expression and provenance")


@dataclass(frozen=True, slots=True)
class StabilityCondition:
    """A stability result separated from the existence of a critical point."""

    hessian: Hessian
    stable: bool
    criterion: str
    provenance: str

    def __post_init__(self) -> None:
        if not self.criterion.strip() or not self.provenance.strip():
            raise ValueError("stability conditions require a criterion and provenance")


@dataclass(frozen=True, slots=True)
class N1EffectiveAction:
    """A complete symbolic N=1 action structure at one moduli point."""

    chiral_multiplets: tuple[ChiralMultiplet, ...]
    vector_multiplets: tuple[VectorMultiplet, ...]
    kahler_potential: KaehlerPotential
    superpotential: Superpotential
    gauge_kinetic: GaugeKineticMatrix
    moment_maps: tuple[MomentMap, ...]
    f_term: FTermPotential
    d_term: DTermPotential
    scalar_potential: ScalarPotential
    gravitino_mass: GravitinoMass
    kinetic_matrices: tuple[KineticMatrix, ...]
    critical_point: CriticalPointConditions
    vacuum_type: VacuumType
    hessian: Hessian
    stability: StabilityCondition

    def __post_init__(self) -> None:
        point = self.kahler_potential.expression.moduli_point
        expressions = (
            self.superpotential.expression,
            self.gauge_kinetic.entry(self.gauge_kinetic.factors[0], self.gauge_kinetic.factors[0]),
            self.f_term.expression,
            self.d_term.expression,
            self.scalar_potential.expression,
            self.gravitino_mass.expression,
        )
        if any(expression.moduli_point != point for expression in expressions):
            raise IncompatibleConvention("N=1 action terms use different moduli points")
        if self.critical_point.moduli_point != point or self.hessian.moduli_point != point:
            raise IncompatibleConvention("vacuum conditions use a different moduli point")

    @property
    def kinetic_matrices_positive(self) -> bool:
        """Return whether every supplied kinetic matrix has an exact positivity certificate."""

        return all(matrix.positive_definite for matrix in self.kinetic_matrices)


EffectiveAction = N1EffectiveAction
N1Action = N1EffectiveAction


__all__ = [
    "ChiralMultiplet",
    "CriticalPointConditions",
    "DTermPotential",
    "EffectiveAction",
    "EffectiveExpression",
    "FTermPotential",
    "GaugeKineticMatrix",
    "GravitinoMass",
    "Hessian",
    "KahlerPotential",
    "KaehlerPotential",
    "KineticMatrix",
    "ModuliPoint",
    "MomentMap",
    "N1EffectiveAction",
    "N1Action",
    "ScalarPotential",
    "StabilityCondition",
    "Superpotential",
    "VacuumType",
    "VectorMultiplet",
]
