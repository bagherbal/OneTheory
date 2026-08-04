"""Immutable fields and dimension-checked action terms.

Owns:
    Scalar, spinor, vector, and tensor field declarations, domains and codomains,
    statistics, mass dimensions, conjugation, derivatives, local products,
    Lagrangian terms, and actions with provenance.

Depends on:
    Core dimensional records, exact rational arithmetic, spacetime conventions, and
    gauge representation metadata; it is independent of concrete models.

Must not:
    Insert field values, measured parameters, a selected carrier, a second simulation
    physics implementation, or a numerical quantum-field-theory claim.

Phase 0:
    Structural field and action laws are executable; unresolved coefficients remain
    symbolic inputs.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction

from onetheory.core.errors import IncompatibleConvention, InconsistentDimensions
from onetheory.math.numbers import Rational, coerce_rational
from onetheory.physics.gauge import Representation
from onetheory.physics.spacetime import LorentzianSpacetime


class FieldKind(StrEnum):
    """The Lorentz tensor type of a field declaration."""

    SCALAR = "scalar"
    SPINOR = "spinor"
    VECTOR = "vector"
    TENSOR = "tensor"


class Statistics(StrEnum):
    """Exchange statistics used by local products."""

    BOSONIC = "bosonic"
    FERMIONIC = "fermionic"


class Conjugation(StrEnum):
    """Conjugation state of a field declaration."""

    ORIGINAL = "original"
    COMPLEX_CONJUGATE = "complex_conjugate"
    DIRAC_ADJOINT = "dirac_adjoint"


@dataclass(frozen=True, slots=True)
class FieldDomain:
    """A named field domain with one spacetime convention."""

    name: str
    spacetime: LorentzianSpacetime

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("field domains require a name")


@dataclass(frozen=True, slots=True)
class FieldCodomain:
    """A named target representation with an exact component dimension."""

    name: str
    dimension: int

    def __post_init__(self) -> None:
        if not self.name.strip() or self.dimension < 1:
            raise ValueError("field codomains require a name and positive dimension")


@dataclass(frozen=True, slots=True)
class SymbolicCoefficient:
    """A coefficient whose value is not supplied by the law declaration."""

    name: str
    dimension: Fraction
    provenance: str

    def __init__(self, name: str, dimension: object = 0, provenance: str = "") -> None:
        if not name.strip() or not provenance.strip():
            raise ValueError("symbolic coefficients require name and provenance")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "dimension", coerce_rational(dimension))
        object.__setattr__(self, "provenance", provenance)


@dataclass(frozen=True, slots=True)
class Field:
    """A typed local field declaration without a numerical configuration."""

    name: str
    domain: FieldDomain
    codomain: FieldCodomain
    kind: FieldKind
    statistics: Statistics
    mass_dimension: Rational
    representation: Representation | None
    conjugation: Conjugation

    def __init__(
        self,
        name: str,
        domain: FieldDomain,
        codomain: FieldCodomain,
        kind: FieldKind,
        statistics: Statistics,
        mass_dimension: object,
        representation: Representation | None = None,
        conjugation: Conjugation = Conjugation.ORIGINAL,
    ) -> None:
        if not name.strip():
            raise ValueError("fields require a name")
        if kind in (FieldKind.SPINOR,) and statistics is not Statistics.FERMIONIC:
            raise ValueError("spinor fields must be fermionic")
        if kind is not FieldKind.SPINOR and statistics is Statistics.FERMIONIC:
            raise ValueError("only spinor fields may be fermionic in this kernel")
        dimension = coerce_rational(mass_dimension)
        if dimension < 0:
            raise ValueError("field mass dimensions must be nonnegative")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "codomain", codomain)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "statistics", statistics)
        object.__setattr__(self, "mass_dimension", dimension)
        object.__setattr__(self, "representation", representation)
        object.__setattr__(self, "conjugation", conjugation)

    @classmethod
    def scalar(
        cls,
        name: str,
        domain: FieldDomain,
        codomain: FieldCodomain,
        mass_dimension: object,
        representation: Representation | None = None,
    ) -> Field:
        return cls(
            name,
            domain,
            codomain,
            FieldKind.SCALAR,
            Statistics.BOSONIC,
            mass_dimension,
            representation,
        )

    @classmethod
    def spinor(
        cls,
        name: str,
        domain: FieldDomain,
        codomain: FieldCodomain,
        mass_dimension: object,
        representation: Representation | None = None,
    ) -> Field:
        return cls(
            name,
            domain,
            codomain,
            FieldKind.SPINOR,
            Statistics.FERMIONIC,
            mass_dimension,
            representation,
        )

    @classmethod
    def vector(
        cls,
        name: str,
        domain: FieldDomain,
        codomain: FieldCodomain,
        mass_dimension: object,
        representation: Representation | None = None,
    ) -> Field:
        return cls(
            name,
            domain,
            codomain,
            FieldKind.VECTOR,
            Statistics.BOSONIC,
            mass_dimension,
            representation,
        )

    @classmethod
    def tensor(
        cls,
        name: str,
        domain: FieldDomain,
        codomain: FieldCodomain,
        mass_dimension: object,
        representation: Representation | None = None,
    ) -> Field:
        return cls(
            name,
            domain,
            codomain,
            FieldKind.TENSOR,
            Statistics.BOSONIC,
            mass_dimension,
            representation,
        )

    def conjugate_field(self, adjoint: bool = False) -> Field:
        """Return an explicitly marked conjugate or Dirac-adjoint declaration."""

        state = Conjugation.DIRAC_ADJOINT if adjoint else Conjugation.COMPLEX_CONJUGATE
        return Field(
            f"{self.name}†" if adjoint else f"{self.name}*",
            self.domain,
            self.codomain,
            self.kind,
            self.statistics,
            self.mass_dimension,
            self.representation.conjugate_representation() if self.representation else None,
            state,
        )


def ScalarField(*args: object, **kwargs: object) -> Field:
    """Construct a bosonic scalar field through the canonical field API."""

    return Field.scalar(*args, **kwargs)  # type: ignore[arg-type]


def SpinorField(*args: object, **kwargs: object) -> Field:
    """Construct a fermionic spinor field through the canonical field API."""

    return Field.spinor(*args, **kwargs)  # type: ignore[arg-type]


def VectorField(*args: object, **kwargs: object) -> Field:
    """Construct a bosonic vector field through the canonical field API."""

    return Field.vector(*args, **kwargs)  # type: ignore[arg-type]


def TensorField(*args: object, **kwargs: object) -> Field:
    """Construct a bosonic tensor field through the canonical field API."""

    return Field.tensor(*args, **kwargs)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class FieldConfiguration:
    """A field and its immutable component configuration."""

    field: Field
    values: tuple[object, ...]

    def __init__(self, field: Field, values: Iterable[object]) -> None:
        components = tuple(values)
        if len(components) != field.codomain.dimension:
            raise ValueError("field configuration does not match its codomain")
        object.__setattr__(self, "field", field)
        object.__setattr__(self, "values", components)


@dataclass(frozen=True, slots=True)
class Derivative:
    """A first spacetime derivative with mass dimension increased by one."""

    field: Field | Derivative
    direction: int

    def __post_init__(self) -> None:
        if not 0 <= self.direction < 4:
            raise ValueError("derivative directions are four-dimensional")

    @property
    def mass_dimension(self) -> Rational:
        return coerce_rational(self.field.mass_dimension) + 1

    @property
    def domain(self) -> FieldDomain:
        return self.field.domain

    @property
    def statistics(self) -> Statistics:
        return self.field.statistics


@dataclass(frozen=True, slots=True)
class LocalProduct:
    """An ordered local product retaining its fermionic sign ordering."""

    factors: tuple[Field | Derivative, ...]
    coefficient: SymbolicCoefficient | None
    mass_dimension: Rational

    def __init__(
        self,
        factors: Iterable[Field | Derivative],
        coefficient: SymbolicCoefficient | None = None,
    ) -> None:
        values = tuple(factors)
        if not values:
            raise ValueError("local products require at least one factor")
        domains = {factor.domain for factor in values}
        if len(domains) != 1:
            raise IncompatibleConvention("local-product factors use different domains")
        dimension = sum((factor.mass_dimension for factor in values), Rational(0))
        if coefficient is not None:
            dimension += coefficient.dimension
        object.__setattr__(self, "factors", values)
        object.__setattr__(self, "coefficient", coefficient)
        object.__setattr__(self, "mass_dimension", dimension)

    @property
    def fermion_count(self) -> int:
        return sum(factor.statistics is Statistics.FERMIONIC for factor in self.factors)

    @property
    def lorentz_scalar(self) -> bool:
        return self.fermion_count % 2 == 0


@dataclass(frozen=True, slots=True)
class LagrangianTerm:
    """A dimension-four local action term with explicit provenance."""

    product: LocalProduct
    coefficient: SymbolicCoefficient | None
    hermitian_conjugate: bool
    provenance: str

    def __init__(
        self,
        product: LocalProduct,
        coefficient: SymbolicCoefficient | None,
        provenance: str,
        hermitian_conjugate: bool = False,
    ) -> None:
        if not provenance.strip():
            raise ValueError("Lagrangian terms require provenance")
        if not product.lorentz_scalar:
            raise ValueError("Lagrangian terms require a Lorentz-scalar fermion contraction")
        dimension = product.mass_dimension + (coefficient.dimension if coefficient else 0)
        if dimension != 4:
            raise InconsistentDimensions(
                "renormalizable Lagrangian terms must have mass dimension four"
            )
        object.__setattr__(self, "product", product)
        object.__setattr__(self, "coefficient", coefficient)
        object.__setattr__(self, "hermitian_conjugate", hermitian_conjugate)
        object.__setattr__(self, "provenance", provenance)

    @property
    def is_hermitian(self) -> bool:
        """Return whether the term carries an explicit Hermitian-conjugate contract."""

        return self.hermitian_conjugate


@dataclass(frozen=True, slots=True)
class Action:
    """An immutable action assembled from dimension-four and declared terms."""

    name: str
    domain: FieldDomain
    terms: tuple[LagrangianTerm, ...]
    provenance: str

    def __init__(
        self, name: str, domain: FieldDomain, terms: Iterable[LagrangianTerm], provenance: str
    ) -> None:
        values = tuple(terms)
        if not name.strip() or not provenance.strip():
            raise ValueError("actions require names and provenance")
        if any(next(iter(term.product.factors)).domain != domain for term in values):
            raise IncompatibleConvention("action terms use a different field domain")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "terms", values)
        object.__setattr__(self, "provenance", provenance)

    @property
    def is_hermitian(self) -> bool:
        """Return whether every assembled term has a Hermitian contract."""

        return all(term.is_hermitian for term in self.terms)


__all__ = [
    "Action",
    "Conjugation",
    "Derivative",
    "Field",
    "FieldCodomain",
    "FieldConfiguration",
    "FieldDomain",
    "FieldKind",
    "LagrangianTerm",
    "LocalProduct",
    "ScalarField",
    "SpinorField",
    "Statistics",
    "SymbolicCoefficient",
    "TensorField",
    "VectorField",
]
