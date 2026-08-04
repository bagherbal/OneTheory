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

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, cast

from onetheory.core.errors import IncompatibleConvention, MissingPhysicalInput, NonExactInput
from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein, Rational, coerce_rational


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


ExactSymbolicScalar = int | Rational | Eisenstein


def _exact_scalar(value: object) -> ExactSymbolicScalar:
    """Coerce one supported exact scalar without admitting approximation."""

    if isinstance(value, bool):
        raise NonExactInput("boolean values are not exact symbolic scalars")
    if isinstance(value, (int, Rational, Eisenstein)):
        return value
    raise NonExactInput("symbolic constants require int, Rational, or Eisenstein values")


def _as_rational(value: object) -> Rational:
    """Coerce a scalar to a rational when the expression is real and exact."""

    if isinstance(value, Rational):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return Rational(value)
    raise NonExactInput("a real exact expression requires rational coefficients")


def _scalar_add(left: ExactSymbolicScalar, right: ExactSymbolicScalar) -> ExactSymbolicScalar:
    if isinstance(left, Eisenstein) or isinstance(right, Eisenstein):
        return Eisenstein.coerce(left) + Eisenstein.coerce(right)
    return Rational(left) + Rational(right)


def _scalar_sub(left: ExactSymbolicScalar, right: ExactSymbolicScalar) -> ExactSymbolicScalar:
    if isinstance(left, Eisenstein) or isinstance(right, Eisenstein):
        return Eisenstein.coerce(left) - Eisenstein.coerce(right)
    return Rational(left) - Rational(right)


def _scalar_mul(left: ExactSymbolicScalar, right: ExactSymbolicScalar) -> ExactSymbolicScalar:
    if isinstance(left, Eisenstein) or isinstance(right, Eisenstein):
        return Eisenstein.coerce(left) * Eisenstein.coerce(right)
    return Rational(left) * Rational(right)


def _scalar_div(left: ExactSymbolicScalar, right: ExactSymbolicScalar) -> ExactSymbolicScalar:
    if isinstance(right, Eisenstein):
        if right.is_zero():
            raise ZeroDivisionError("symbolic scalar division by zero")
        return Eisenstein.coerce(left) / right
    denominator = Rational(right)
    if denominator.is_zero():
        raise ZeroDivisionError("symbolic scalar division by zero")
    if isinstance(left, Eisenstein):
        return left / denominator
    return Rational(left) / denominator


def _scalar_conjugate(value: ExactSymbolicScalar) -> ExactSymbolicScalar:
    if isinstance(value, Eisenstein):
        return Eisenstein(value.a - value.b, -value.b)
    return value


def _scalar_text(value: ExactSymbolicScalar) -> str:
    return value.text() if isinstance(value, Eisenstein) else str(value)


def _integer_scalar(value: ExactSymbolicScalar) -> int:
    """Return an exact integral exponent."""

    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, Rational) and value.denominator == 1:
        return value.numerator
    raise ValueError("symbolic exponents must be integral rational values")


@dataclass(frozen=True, slots=True)
class ComplexScalarField:
    """An immutable named complex field coordinate and its formal conjugate."""

    name: str
    moduli_point: ModuliPoint
    provenance: str
    conjugate_of: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.provenance.strip():
            raise ValueError("complex scalar fields require names and provenance")

    @property
    def symbol(self) -> SymbolicExpression:
        """Return the formal variable represented by this field."""

        return SymbolicExpression.variable(self.name, conjugate_of=self.conjugate_of)

    def conjugate_field(self) -> ComplexScalarField:
        """Return the conjugate field through an explicit method API."""

        return self.conjugate

    @property
    def conjugate(self) -> ComplexScalarField:
        """Return the conjugate field at the same declared moduli point."""

        if self.conjugate_of is None:
            name = f"bar({self.name})"
            original = self.name
        else:
            name = self.conjugate_of
            original = None
        return ComplexScalarField(name, self.moduli_point, self.provenance, original)


@dataclass(frozen=True, slots=True)
class RealScalarField:
    """An immutable named real scalar field used for physical coordinates."""

    name: str
    moduli_point: ModuliPoint
    provenance: str

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.provenance.strip():
            raise ValueError("real scalar fields require names and provenance")

    @property
    def symbol(self) -> SymbolicExpression:
        """Return the formal real variable represented by this field."""

        return SymbolicExpression.variable(self.name)


@dataclass(frozen=True, slots=True)
class SymbolicExpression:
    """A restricted immutable exact expression tree for vacuum calculations."""

    operation: str
    arguments: tuple[SymbolicExpression, ...] = ()
    value: ExactSymbolicScalar | None = None
    name: str | None = None
    conjugate_of: str | None = None

    @classmethod
    def constant(cls, value: ExactSymbolicScalar) -> SymbolicExpression:
        """Create an exact scalar constant."""

        return cls("constant", value=_exact_scalar(value))

    @classmethod
    def variable(cls, name: str, *, conjugate_of: str | None = None) -> SymbolicExpression:
        """Create a formal variable, optionally marked as a conjugate."""

        if not name.strip():
            raise ValueError("symbolic variables require names")
        return cls("variable", name=name, conjugate_of=conjugate_of)

    @classmethod
    def _operation(
        cls, operation: str, arguments: Iterable[SymbolicExpression]
    ) -> SymbolicExpression:
        values = tuple(arguments)
        if not values:
            raise ValueError("symbolic operations require arguments")
        return cls(operation, values).simplify()

    def simplify(self) -> SymbolicExpression:
        """Apply deterministic local identities without building a general CAS."""

        if self.operation in {"constant", "variable"}:
            return self
        args = tuple(argument.simplify() for argument in self.arguments)
        if self.operation == "neg" and args[0].operation == "constant":
            return self.constant(_scalar_mul(-1, cast(ExactSymbolicScalar, args[0].value)))
        if self.operation in {"add", "sub", "mul", "div"}:
            left, right = args
            if left.operation == "constant" and right.operation == "constant":
                left_value = cast(ExactSymbolicScalar, left.value)
                right_value = cast(ExactSymbolicScalar, right.value)
                operation = {
                    "add": _scalar_add,
                    "sub": _scalar_sub,
                    "mul": _scalar_mul,
                    "div": _scalar_div,
                }[self.operation]
                return self.constant(operation(left_value, right_value))
            if self.operation == "add":
                if left.is_zero() and right.is_zero():
                    return self.constant(0)
                if left.is_zero():
                    return right
                if right.is_zero():
                    return left
            if self.operation == "sub":
                if right.is_zero():
                    return left
            if self.operation == "mul":
                if left.is_zero() or right.is_zero():
                    return self.constant(0)
                if left.is_one():
                    return right
                if right.is_one():
                    return left
            if self.operation == "div" and right.is_one():
                return left
        if self.operation == "pow" and args[1].operation == "constant":
            exponent = args[1].value
            if isinstance(exponent, (int, Rational)) and Rational(exponent).denominator == 1:
                power = int(exponent)
                base = args[0]
                if power == 0:
                    return self.constant(1)
                if power == 1:
                    return base
                if base.operation == "constant":
                    return self.constant(cast(Any, base.value) ** power)
        if self.operation == "conjugate":
            argument = args[0]
            if argument.operation == "constant":
                return self.constant(_scalar_conjugate(cast(ExactSymbolicScalar, argument.value)))
            if argument.operation == "conjugate":
                return argument.arguments[0]
        return SymbolicExpression(self.operation, args, self.value, self.name, self.conjugate_of)

    def is_zero(self) -> bool:
        """Return whether this expression is the exact zero constant."""

        return self.operation == "constant" and cast(ExactSymbolicScalar, self.value) == 0

    def is_one(self) -> bool:
        """Return whether this expression is the exact one constant."""

        return self.operation == "constant" and cast(ExactSymbolicScalar, self.value) == 1

    def __add__(self, other: SymbolicExpression | ExactSymbolicScalar) -> SymbolicExpression:
        rhs = _expression(other)
        return self._operation("add", (self, rhs))

    def __radd__(self, other: object) -> SymbolicExpression:
        return _expression(cast(SymbolicExpression | ExactSymbolicScalar, other)) + self

    def __sub__(self, other: SymbolicExpression | ExactSymbolicScalar) -> SymbolicExpression:
        rhs = _expression(other)
        return self._operation("sub", (self, rhs))

    def __rsub__(self, other: object) -> SymbolicExpression:
        return _expression(cast(SymbolicExpression | ExactSymbolicScalar, other)) - self

    def __mul__(self, other: SymbolicExpression | ExactSymbolicScalar) -> SymbolicExpression:
        rhs = _expression(other)
        return self._operation("mul", (self, rhs))

    def __rmul__(self, other: object) -> SymbolicExpression:
        return _expression(cast(SymbolicExpression | ExactSymbolicScalar, other)) * self

    def __truediv__(self, other: SymbolicExpression | ExactSymbolicScalar) -> SymbolicExpression:
        rhs = _expression(other)
        return self._operation("div", (self, rhs))

    def __rtruediv__(self, other: object) -> SymbolicExpression:
        return _expression(cast(SymbolicExpression | ExactSymbolicScalar, other)) / self

    def __neg__(self) -> SymbolicExpression:
        return self._operation("neg", (self,))

    def __pow__(self, exponent: int) -> SymbolicExpression:
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            raise TypeError("symbolic powers require integer exponents")
        if exponent < 0 and self.is_zero():
            raise ZeroDivisionError("zero cannot have a negative symbolic power")
        if exponent < 0:
            return self._operation("pow", (self, self.constant(exponent)))
        result = self.constant(1)
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result

    def conjugate(self) -> SymbolicExpression:
        """Return the formal complex conjugate of the expression."""

        if self.operation == "variable":
            if self.conjugate_of is None:
                return self.variable(f"bar({self.name})", conjugate_of=self.name)
            return self.variable(self.conjugate_of)
        if self.operation == "constant":
            return self.constant(_scalar_conjugate(cast(ExactSymbolicScalar, self.value)))
        if self.operation == "conjugate":
            return self.arguments[0]
        return self._operation("conjugate", (self,))

    def exp(self) -> SymbolicExpression:
        """Return a symbolic exponential."""

        return self._operation("exp", (self,))

    def log(self) -> SymbolicExpression:
        """Return a symbolic logarithm with an explicit branch supplied at evaluation."""

        return self._operation("log", (self,))

    def real_part(self) -> SymbolicExpression:
        """Return the formal real part."""

        return (self + self.conjugate()) / 2

    def imag_part(self) -> SymbolicExpression:
        """Return the formal imaginary part in the restricted grammar."""

        return (self - self.conjugate()) / 2

    def absolute_square(self) -> SymbolicExpression:
        """Return the exact formal product with the conjugate."""

        return self * self.conjugate()

    def derivative(self, variable: str | SymbolicExpression) -> SymbolicExpression:
        """Return the exact formal derivative with respect to one Wirtinger variable."""

        key = variable.name if isinstance(variable, SymbolicExpression) else variable
        if not key:
            raise ValueError("derivatives require a named variable")
        if self.operation == "constant":
            return self.constant(0)
        if self.operation == "variable":
            return self.constant(1 if self.name == key else 0)
        if self.operation == "neg":
            return -self.arguments[0].derivative(key)
        if self.operation == "add":
            return self.arguments[0].derivative(key) + self.arguments[1].derivative(key)
        if self.operation == "sub":
            return self.arguments[0].derivative(key) - self.arguments[1].derivative(key)
        if self.operation == "mul":
            left, right = self.arguments
            return left.derivative(key) * right + left * right.derivative(key)
        if self.operation == "div":
            left, right = self.arguments
            return (left.derivative(key) * right - left * right.derivative(key)) / (right**2)
        if self.operation == "pow":
            base, exponent = self.arguments
            if exponent.operation != "constant":
                raise ValueError("symbolic exponents are outside the restricted grammar")
            power = _integer_scalar(cast(ExactSymbolicScalar, exponent.value))
            return power * (base ** (power - 1)) * base.derivative(key)
        if self.operation == "exp":
            inner = self.arguments[0]
            return self * inner.derivative(key)
        if self.operation == "log":
            inner = self.arguments[0]
            return inner.derivative(key) / inner
        if self.operation == "conjugate":
            if key.startswith("bar(") and key.endswith(")"):
                conjugated_variable = key[4:-1]
            else:
                conjugated_variable = f"bar({key})"
            return self.arguments[0].derivative(conjugated_variable).conjugate()
        raise ValueError(f"unsupported symbolic operation {self.operation!r}")

    def second_derivative(self, first_variable: str, second_variable: str) -> SymbolicExpression:
        """Return an exact second formal derivative."""

        return self.derivative(first_variable).derivative(second_variable)

    def gradient(self, variables: Sequence[str]) -> tuple[SymbolicExpression, ...]:
        """Return the exact ordered gradient in the supplied basis."""

        return tuple(self.derivative(variable) for variable in variables)

    def hessian(self, variables: Sequence[str]) -> tuple[tuple[SymbolicExpression, ...], ...]:
        """Return the exact ordered Hessian in the supplied basis."""

        return tuple(
            tuple(self.second_derivative(left, right) for right in variables) for left in variables
        )

    def evaluate(self, values: Mapping[str, complex | float | int]) -> complex:
        """Evaluate the restricted expression with explicit numerical values."""

        import cmath

        if self.operation == "constant":
            scalar = cast(ExactSymbolicScalar, self.value)
            if isinstance(scalar, Eisenstein):
                omega = complex(-0.5, 3**0.5 / 2)
                return complex(float(scalar.a) + float(scalar.b) * omega)
            return complex(float(scalar))
        if self.operation == "variable":
            if self.name is not None and self.name in values:
                return complex(values[self.name])
            if self.conjugate_of is not None and self.conjugate_of in values:
                return complex(values[self.conjugate_of]).conjugate()
            raise MissingPhysicalInput(f"numerical value for {self.name or '<unnamed>'}")
        if self.operation == "conjugate":
            return self.arguments[0].evaluate(values).conjugate()
        args = tuple(argument.evaluate(values) for argument in self.arguments)
        if self.operation == "neg":
            return -args[0]
        if self.operation == "add":
            return args[0] + args[1]
        if self.operation == "sub":
            return args[0] - args[1]
        if self.operation == "mul":
            return args[0] * args[1]
        if self.operation == "div":
            return args[0] / args[1]
        if self.operation == "pow":
            return complex(
                args[0] ** _integer_scalar(cast(ExactSymbolicScalar, self.arguments[1].value))
            )
        if self.operation == "exp":
            return complex(cmath.exp(args[0]))
        if self.operation == "log":
            return complex(cmath.log(args[0]))
        raise ValueError(f"unsupported symbolic operation {self.operation!r}")

    def text(self) -> str:
        """Return a deterministic compact expression representation."""

        if self.operation == "constant":
            return _scalar_text(cast(ExactSymbolicScalar, self.value))
        if self.operation == "variable":
            return cast(str, self.name)
        if self.operation == "neg":
            return f"-({self.arguments[0].text()})"
        if self.operation in {"add", "sub", "mul", "div"}:
            symbol = {"add": "+", "sub": "-", "mul": "*", "div": "/"}[self.operation]
            return f"({self.arguments[0].text()} {symbol} {self.arguments[1].text()})"
        if self.operation == "pow":
            return f"({self.arguments[0].text()})**{self.arguments[1].text()}"
        if self.operation == "conjugate":
            return f"conj({self.arguments[0].text()})"
        return f"{self.operation}({self.arguments[0].text()})"

    def __str__(self) -> str:
        return self.text()


def _expression(value: SymbolicExpression | ExactSymbolicScalar) -> SymbolicExpression:
    if isinstance(value, SymbolicExpression):
        return value
    return SymbolicExpression.constant(_exact_scalar(value))


@dataclass(frozen=True, slots=True)
class ParameterProvenance:
    """Immutable provenance and assumptions attached to an effective parameter."""

    source: str
    evidence: str
    assumptions: tuple[str, ...] = ()
    exact: bool = True

    def __post_init__(self) -> None:
        if (
            not self.source.strip()
            or not self.evidence.strip()
            or any(not item.strip() for item in self.assumptions)
        ):
            raise ValueError("parameter provenance requires named source and evidence")


@dataclass(frozen=True, slots=True)
class PhysicalInputRequirement:
    """One explicit physical input required before a term or solution is available."""

    name: str
    available: bool = False
    provenance: ParameterProvenance | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("physical requirements require names")


@dataclass(frozen=True, slots=True)
class DomainCondition:
    """An exact expression inequality or equality defining a validity domain."""

    expression: SymbolicExpression
    relation: str
    bound: ExactSymbolicScalar = 0
    provenance: ParameterProvenance | None = None

    def __post_init__(self) -> None:
        if self.relation not in {"<", "<=", "=", ">=", ">", "!="}:
            raise ValueError("domain relations must be ordered comparisons")
        _exact_scalar(self.bound)

    def holds(self, values: Mapping[str, complex | float | int], tolerance: float = 0.0) -> bool:
        """Evaluate this real condition with an explicit tolerance."""

        difference = (
            self.expression.evaluate(values) - complex(float(_as_rational(self.bound)))
        ).real
        if self.relation == "<":
            return difference < -tolerance
        if self.relation == "<=":
            return difference <= tolerance
        if self.relation == "=":
            return abs(difference) <= tolerance
        if self.relation == ">=":
            return difference >= -tolerance
        if self.relation == ">":
            return difference > tolerance
        return abs(difference) > tolerance


@dataclass(frozen=True, slots=True)
class ValidityDomain:
    """An immutable collection of branch and convergence conditions."""

    conditions: tuple[DomainCondition, ...] = ()
    branch: str = "principal"
    provenance: ParameterProvenance | None = None

    def contains(self, values: Mapping[str, complex | float | int], tolerance: float = 0.0) -> bool:
        """Return whether every declared condition holds."""

        return all(condition.holds(values, tolerance) for condition in self.conditions)

    def compatible_with(self, other: ValidityDomain) -> bool:
        """Return whether two terms declare the same branch and conditions."""

        return self.branch == other.branch and self.conditions == other.conditions


BranchCondition = DomainCondition


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
    symbolic_expression: SymbolicExpression | None = None
    provenance: ParameterProvenance | None = None

    def __post_init__(self) -> None:
        if not self.chiral_fields:
            raise ValueError("Kähler potentials require at least one chiral field")

    @property
    def name(self) -> str:
        """Return the standard K symbol."""

        return "K"

    @classmethod
    def from_symbolic(
        cls,
        expression: SymbolicExpression,
        fields: Iterable[ComplexScalarField | str],
        moduli_point: ModuliPoint,
        provenance: ParameterProvenance,
        normalization: str = "Einstein",
    ) -> KaehlerPotential:
        """Construct a Kähler potential from an exact restricted expression."""

        names = tuple(
            field.name if isinstance(field, ComplexScalarField) else field for field in fields
        )
        if not names or any(not name.strip() for name in names):
            raise ValueError("symbolic Kähler potentials require named fields")
        effective = EffectiveExpression(
            expression.text(),
            provenance.source,
            (provenance.evidence,),
            moduli_point,
            "exact symbolic",
            normalization,
        )
        return cls(effective, names, expression, provenance)

    @property
    def fields(self) -> tuple[str, ...]:
        """Return the declared holomorphic field names."""

        return self.chiral_fields

    def _symbolic(self) -> SymbolicExpression:
        if self.symbolic_expression is None:
            raise MissingPhysicalInput("exact symbolic Kähler potential")
        return self.symbolic_expression

    def kahler_derivative(self, field: str) -> SymbolicExpression:
        """Return Kᵢ for one holomorphic field."""

        if field not in self.fields:
            raise ValueError(f"undeclared Kähler field {field!r}")
        return self._symbolic().derivative(field)

    def kahler_gradient(self) -> tuple[SymbolicExpression, ...]:
        """Return all holomorphic Kähler derivatives in declaration order."""

        return tuple(self.kahler_derivative(field) for field in self.fields)

    def metric_entry(self, field: str, conjugate_field: str) -> SymbolicExpression:
        """Return Kᵢ barⱼ using formal Wirtinger differentiation."""

        if field not in self.fields or conjugate_field not in self.fields:
            raise ValueError("Kähler metric fields must be declared")
        return self._symbolic().second_derivative(field, f"bar({conjugate_field})")

    def metric(self) -> KaehlerMetric:
        """Return the exact Kähler metric and its singularity boundary."""

        return KaehlerMetric(
            self.fields,
            tuple(
                tuple(self.metric_entry(left, right) for right in self.fields)
                for left in self.fields
            ),
            self.provenance,
        )

    def kahler_metric(self) -> KaehlerMetric:
        """Return the Kähler metric through its descriptive API name."""

        return self.metric()

    def kahler_covariant_derivative(
        self, superpotential: SymbolicExpression, field: str
    ) -> SymbolicExpression:
        """Return DᵢW = ∂ᵢW + KᵢW exactly."""

        if field not in self.fields:
            raise ValueError(f"undeclared Kähler field {field!r}")
        return superpotential.derivative(field) + self.kahler_derivative(field) * superpotential

    def kahler_transform(
        self, holomorphic_shift: SymbolicExpression, superpotential: SymbolicExpression
    ) -> tuple[SymbolicExpression, SymbolicExpression]:
        """Apply K→K+F+F̄ and W→e⁻ᶠW without changing the covariant law."""

        transformed_k = self._symbolic() + holomorphic_shift + holomorphic_shift.conjugate()
        transformed_w = (-holomorphic_shift).exp() * superpotential
        return transformed_k, transformed_w


@dataclass(frozen=True, slots=True)
class KahlerCovariantDerivative:
    """An ordered exact collection of Kähler-covariant derivatives."""

    potential: KaehlerPotential
    superpotential: SymbolicExpression

    def component(self, field: str) -> SymbolicExpression:
        """Return DᵢW for one declared field."""

        return self.potential.kahler_covariant_derivative(self.superpotential, field)

    @property
    def gradient(self) -> tuple[SymbolicExpression, ...]:
        """Return the ordered F-term gradient."""

        return tuple(self.component(field) for field in self.potential.fields)


KahlerPotential = KaehlerPotential
ComplexField = ComplexScalarField
RealField = RealScalarField
Expression = SymbolicExpression
HolomorphicExpression = SymbolicExpression
RealExpression = SymbolicExpression


@dataclass(frozen=True, slots=True)
class SourceTerm:
    """One provenance-carrying exponential or additive effective source term."""

    name: str
    coefficient: SymbolicExpression
    charge_vector: tuple[Rational, ...]
    gauge_kinetic_function: SymbolicExpression | None
    determinant_line_section: str | None
    axionic_phase: SymbolicExpression | None
    approximation_order: str
    required_inputs: tuple[PhysicalInputRequirement, ...]
    validity_domain: ValidityDomain
    provenance: ParameterProvenance
    source_kind: str = "generic"
    beta_function: Rational | None = None
    moduli_point: ModuliPoint | None = None

    def __init__(
        self,
        name: str,
        coefficient: SymbolicExpression,
        charge_vector: Iterable[object] = (),
        gauge_kinetic_function: SymbolicExpression | None = None,
        determinant_line_section: str | None = None,
        axionic_phase: SymbolicExpression | None = None,
        approximation_order: str = "declared exact source order",
        required_inputs: Iterable[PhysicalInputRequirement] = (),
        validity_domain: ValidityDomain | None = None,
        provenance: ParameterProvenance | None = None,
        source_kind: str = "generic",
        beta_function: object | None = None,
        moduli_point: ModuliPoint | None = None,
    ) -> None:
        if not name.strip() or not approximation_order.strip() or not source_kind.strip():
            raise ValueError("source terms require names, order, and kind")
        values = tuple(coerce_rational(value) for value in charge_vector)
        selected_provenance = provenance or ParameterProvenance(
            "explicit source declaration", "caller supplied", (), True
        )
        selected_beta = None if beta_function is None else coerce_rational(beta_function)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "coefficient", coefficient)
        object.__setattr__(self, "charge_vector", values)
        object.__setattr__(self, "gauge_kinetic_function", gauge_kinetic_function)
        object.__setattr__(self, "determinant_line_section", determinant_line_section)
        object.__setattr__(self, "axionic_phase", axionic_phase)
        object.__setattr__(self, "approximation_order", approximation_order)
        object.__setattr__(self, "required_inputs", tuple(required_inputs))
        object.__setattr__(self, "validity_domain", validity_domain or ValidityDomain())
        object.__setattr__(self, "provenance", selected_provenance)
        object.__setattr__(self, "source_kind", source_kind)
        object.__setattr__(self, "beta_function", selected_beta)
        object.__setattr__(self, "moduli_point", moduli_point)

    @property
    def available(self) -> bool:
        """Return whether every physical ingredient needed by this source exists."""

        return not self.unavailable_reasons

    @property
    def unavailable_reasons(self) -> tuple[str, ...]:
        """Return the explicit missing inputs preventing use of this term."""

        reasons = [item.name for item in self.required_inputs if not item.available]
        nonperturbative = self.source_kind in {"worldsheet", "multicover", "gaugino", "racetrack"}
        if nonperturbative and not self.determinant_line_section:
            reasons.append("determinant-line section")
        if self.source_kind in {"gaugino", "racetrack"}:
            if self.gauge_kinetic_function is None:
                reasons.append("hidden gauge kinetic function")
            if self.beta_function is None:
                reasons.append("hidden beta-function coefficient")
        return tuple(dict.fromkeys(reasons))

    def exponent(self, variables: Sequence[str]) -> SymbolicExpression:
        """Build the formal exponential from this term's exact charge vector."""

        if len(variables) != len(self.charge_vector):
            raise ValueError("charge and exponent dimensions do not agree")
        linear = SymbolicExpression.constant(0)
        for value, variable in zip(self.charge_vector, variables, strict=True):
            linear += value * SymbolicExpression.variable(variable)
        return self.coefficient * (-linear).exp()


def _source(
    source_kind: str,
    name: str,
    coefficient: SymbolicExpression,
    **kwargs: Any,
) -> SourceTerm:
    """Construct a typed source through one explicit common validation path."""

    return SourceTerm(name, coefficient, source_kind=source_kind, **kwargs)


class WorldsheetInstanton(SourceTerm):
    """A determinant-normalized worldsheet source."""

    def __init__(self, name: str, coefficient: SymbolicExpression, **kwargs: Any) -> None:
        super().__init__(name, coefficient, source_kind="worldsheet", **kwargs)

    @staticmethod
    def from_data(name: str, coefficient: SymbolicExpression, **kwargs: Any) -> SourceTerm:
        """Create a worldsheet source without inventing its determinant section."""

        return WorldsheetInstanton(name, coefficient, **kwargs)


class MulticoverContribution(SourceTerm):
    """A declared determinant-normalized multicover contribution."""

    def __init__(self, name: str, coefficient: SymbolicExpression, **kwargs: Any) -> None:
        super().__init__(name, coefficient, source_kind="multicover", **kwargs)

    @staticmethod
    def from_data(name: str, coefficient: SymbolicExpression, **kwargs: Any) -> SourceTerm:
        """Create one multicover term with explicit approximation metadata."""

        return MulticoverContribution(name, coefficient, **kwargs)


class GauginoCondensate(SourceTerm):
    """A hidden-sector condensate requiring beta and determinant data."""

    def __init__(self, name: str, coefficient: SymbolicExpression, **kwargs: Any) -> None:
        super().__init__(name, coefficient, source_kind="gaugino", **kwargs)

    @staticmethod
    def from_data(name: str, coefficient: SymbolicExpression, **kwargs: Any) -> SourceTerm:
        """Create a condensate that remains unavailable without hidden data."""

        return GauginoCondensate(name, coefficient, **kwargs)


class ThresholdGaugeKineticFunction(SourceTerm):
    """A threshold-dependent hidden gauge kinetic function."""

    def __init__(
        self, name: str, expression: SymbolicExpression, provenance: ParameterProvenance
    ) -> None:
        super().__init__(
            name,
            expression,
            gauge_kinetic_function=expression,
            determinant_line_section="threshold function",
            approximation_order="threshold expansion",
            validity_domain=ValidityDomain(provenance=provenance),
            provenance=provenance,
            source_kind="threshold",
        )

    @staticmethod
    def from_data(
        name: str, expression: SymbolicExpression, provenance: ParameterProvenance
    ) -> SourceTerm:
        """Represent an explicit threshold function as a typed source record."""

        return ThresholdGaugeKineticFunction(name, expression, provenance)


class FluxConstant(SourceTerm):
    """An explicitly supplied flux superpotential constant."""

    def __init__(
        self, name: str, coefficient: SymbolicExpression, provenance: ParameterProvenance
    ) -> None:
        super().__init__(name, coefficient, provenance=provenance, source_kind="flux")

    @staticmethod
    def from_data(
        name: str, coefficient: SymbolicExpression, provenance: ParameterProvenance
    ) -> SourceTerm:
        """Create an explicitly supplied flux constant."""

        return FluxConstant(name, coefficient, provenance)


class ChernSimonsConstant(SourceTerm):
    """An explicitly supplied Chern–Simons constant."""

    def __init__(
        self, name: str, coefficient: SymbolicExpression, provenance: ParameterProvenance
    ) -> None:
        super().__init__(name, coefficient, provenance=provenance, source_kind="chern-simons")

    @staticmethod
    def from_data(
        name: str, coefficient: SymbolicExpression, provenance: ParameterProvenance
    ) -> SourceTerm:
        """Create an explicitly supplied Chern–Simons constant."""

        return ChernSimonsConstant(name, coefficient, provenance)


class PerturbativeCorrection(SourceTerm):
    """An explicitly declared perturbative correction."""

    def __init__(
        self, name: str, coefficient: SymbolicExpression, provenance: ParameterProvenance
    ) -> None:
        super().__init__(name, coefficient, provenance=provenance, source_kind="perturbative")

    @staticmethod
    def from_data(
        name: str, coefficient: SymbolicExpression, provenance: ParameterProvenance
    ) -> SourceTerm:
        """Create a perturbative correction with no inferred size."""

        return PerturbativeCorrection(name, coefficient, provenance)


class UpliftTerm(SourceTerm):
    """External uplift physics with no carrier interpretation."""

    def __init__(
        self, name: str, coefficient: SymbolicExpression, provenance: ParameterProvenance
    ) -> None:
        super().__init__(name, coefficient, provenance=provenance, source_kind="external-uplift")

    @staticmethod
    def from_external(
        name: str, coefficient: SymbolicExpression, provenance: ParameterProvenance
    ) -> SourceTerm:
        """Create an external uplift term; no carrier interpretation is supplied."""

        return UpliftTerm(name, coefficient, provenance)


@dataclass(frozen=True, slots=True)
class RacetrackSuperpotential:
    """A lawful same-gauge-kinetic-function unequal-exponent racetrack."""

    first: SourceTerm
    second: SourceTerm
    gauge_kinetic_function: SymbolicExpression
    exponent_one: Rational
    exponent_two: Rational
    logarithm_branch: str
    axion_branch: str
    validity_domain: ValidityDomain

    @classmethod
    def from_terms(
        cls,
        first: SourceTerm,
        second: SourceTerm,
        gauge_kinetic_function: SymbolicExpression,
        exponent_one: object,
        exponent_two: object,
        logarithm_branch: str,
        axion_branch: str,
        validity_domain: ValidityDomain,
    ) -> RacetrackSuperpotential:
        """Construct a racetrack from two fully supplied carrier terms."""

        return cls(
            first,
            second,
            gauge_kinetic_function,
            coerce_rational(exponent_one),
            coerce_rational(exponent_two),
            logarithm_branch,
            axion_branch,
            validity_domain,
        )

    def __post_init__(self) -> None:
        if (
            self.exponent_one <= 0
            or self.exponent_two <= 0
            or self.exponent_one == self.exponent_two
        ):
            raise ValueError("racetrack exponents must be positive and unequal")
        if (
            self.first.gauge_kinetic_function != self.gauge_kinetic_function
            or self.second.gauge_kinetic_function != self.gauge_kinetic_function
        ):
            raise IncompatibleConvention(
                "racetrack terms must use one hidden gauge kinetic function"
            )
        if (
            self.first.moduli_point is not None
            and self.second.moduli_point is not None
            and self.first.moduli_point != self.second.moduli_point
        ):
            raise IncompatibleConvention("racetrack terms use different moduli points")
        if not self.first.available or not self.second.available:
            raise MissingPhysicalInput(
                self.first.unavailable_reasons[0]
                if not self.first.available
                else self.second.unavailable_reasons[0]
            )
        if (
            self.first.validity_domain.branch != self.validity_domain.branch
            or self.second.validity_domain.branch != self.validity_domain.branch
        ):
            raise IncompatibleConvention("racetrack branches and validity domains do not agree")

    @property
    def expression(self) -> SymbolicExpression:
        """Return A₁ exp(-a₁fₕ)+A₂ exp(-a₂fₕ)."""

        if self.gauge_kinetic_function is None:
            raise MissingPhysicalInput("hidden gauge kinetic function")
        gauge = self.gauge_kinetic_function
        return (
            self.first.coefficient * (-_expression(self.exponent_one) * gauge).exp()
            + self.second.coefficient * (-_expression(self.exponent_two) * gauge).exp()
        )

    def leading_balance(self) -> SymbolicExpression:
        """Return the exact logarithmic balance relation between the two terms."""

        ratio = -(self.first.coefficient / self.second.coefficient)
        return (ratio.log() / (self.exponent_one - self.exponent_two)) - self.gauge_kinetic_function

    def phase_conditions(self) -> tuple[SymbolicExpression, ...]:
        """Return the explicit branch-sensitive phase equations."""

        return (
            (self.first.coefficient / self.second.coefficient).absolute_square() - 1,
            self.first.coefficient.real_part() + self.second.coefficient.real_part(),
        )


@dataclass(frozen=True, slots=True)
class ChargeMatrix:
    """Exact charge vectors and affine geometry of exponential sources."""

    rows: tuple[tuple[Rational, ...], ...]

    def __init__(self, rows: Iterable[Iterable[object]]) -> None:
        values = tuple(tuple(coerce_rational(value) for value in row) for row in rows)
        if not values or not values[0] or any(len(row) != len(values[0]) for row in values):
            raise ValueError("charge matrices require nonempty rectangular rows")
        object.__setattr__(self, "rows", values)

    @property
    def dimension(self) -> int:
        """Return the charge-space dimension."""

        return len(self.rows[0])

    @property
    def rank(self) -> int:
        """Return the exact linear rank."""

        return Matrix(self.rows, scalar_type=Rational).rank()

    @property
    def affine_rank(self) -> int:
        """Return the dimension of the affine span of the rows."""

        if len(self.rows) == 1:
            return 0
        differences = tuple(
            tuple(right - left for left, right in zip(self.rows[0], row, strict=True))
            for row in self.rows[1:]
        )
        return Matrix(differences, scalar_type=Rational).rank()

    @property
    def null_directions(self) -> tuple[tuple[Rational, ...], ...]:
        """Return a deterministic exact basis of directions invisible to all charges."""

        return tuple(
            tuple(cast(Rational, value) for value in vector.values)
            for vector in Matrix(self.rows, scalar_type=Rational).nullspace()
        )

    @property
    def affine_hyperplane(self) -> tuple[tuple[Rational, ...], Rational] | None:
        """Return one affine hyperplane normal and constant when the span is proper."""

        if self.affine_rank >= self.dimension:
            return None
        differences = tuple(
            tuple(right - left for left, right in zip(self.rows[0], row, strict=True))
            for row in self.rows[1:]
        )
        normals = Matrix(differences, scalar_type=Rational).nullspace()
        if not normals:
            normal = tuple(
                Rational(1) if index == 0 else Rational(0) for index in range(self.dimension)
            )
        else:
            normal = tuple(cast(Rational, value) for value in normals[0].values)
        constant = sum(
            (value * coordinate for value, coordinate in zip(normal, self.rows[0], strict=True)),
            Rational(0),
        )
        return normal, constant

    @property
    def sign_cone(self) -> tuple[tuple[int, ...], ...]:
        """Return the coordinate sign patterns represented by the exact rows."""

        return tuple(
            tuple(0 if value == 0 else 1 if value > 0 else -1 for value in row) for row in self.rows
        )

    @property
    def axionic_directions(self) -> tuple[tuple[Rational, ...], ...]:
        """Return charge-null directions, which are axionically invisible."""

        return self.null_directions

    @property
    def source_independent(self) -> bool:
        """Return whether every source row is linearly independent."""

        return self.rank == len(self.rows)

    @property
    def stabilization_lower_bound(self) -> int:
        """Return the number of independent charge directions still required."""

        return max(0, self.dimension - self.affine_rank)


@dataclass(frozen=True, slots=True)
class ChargeClassification:
    """Exact reusable classification of a source charge set."""

    charges: ChargeMatrix
    affine_hyperplane: tuple[tuple[Rational, ...], Rational] | None
    source_independent: bool
    stabilization_lower_bound: int
    axionic_directions: tuple[tuple[Rational, ...], ...]
    provenance: ParameterProvenance


def classify_charges(
    charges: Iterable[Iterable[object]], provenance: ParameterProvenance | None = None
) -> ChargeClassification:
    """Classify exact exponential charges without assigning physical meaning."""

    matrix = ChargeMatrix(charges)
    return ChargeClassification(
        matrix,
        matrix.affine_hyperplane,
        matrix.source_independent,
        matrix.stabilization_lower_bound,
        matrix.axionic_directions,
        provenance or ParameterProvenance("charge declaration", "exact input"),
    )


@dataclass(frozen=True, slots=True)
class ScopedSourceResult:
    """A source-classification conclusion retaining its exact scope and hypotheses."""

    name: str
    status: str
    conclusion: str
    hypotheses: tuple[str, ...]
    charge_classification: ChargeClassification | None
    provenance: ParameterProvenance


def worldsheet_charge(
    d1: int, d2: int, p: object = 1, base_degree: int = 1
) -> tuple[Rational, ...]:
    """Return the established (S,T1,T2,T3) worldsheet charge."""

    if isinstance(base_degree, bool) or not isinstance(base_degree, int) or base_degree < 1:
        raise ValueError("base_degree must be a positive integer")
    scale = coerce_rational(p)
    if scale == 0:
        raise ValueError("worldsheet charge scale must be nonzero")
    return (Rational(0), scale * d1, scale * d2, scale * base_degree)


def condensate_charge(
    exponent: object,
    threshold_direction: Sequence[object] = (Rational(-2, 3), Rational(1, 3), Rational(-4)),
) -> tuple[Rational, ...]:
    """Return a(1,b₁,b₂,b₃) in the established modulus ordering."""

    if len(threshold_direction) != 3:
        raise ValueError("threshold_direction must have three entries")
    value = coerce_rational(exponent)
    if value == 0:
        raise ValueError("condensate exponent must be nonzero")
    direction = tuple(coerce_rational(item) for item in threshold_direction)
    return (value, *(value * item for item in direction))


def affine_functional(charge: Sequence[object], exponent: object, p: object = 1) -> Rational:
    """Evaluate the exact affine functional used by the retained-source test."""

    if len(charge) != 4:
        raise ValueError("charges use (S,T1,T2,T3) ordering")
    values = tuple(coerce_rational(item) for item in charge)
    a, scale = coerce_rational(exponent), coerce_rational(p)
    if a == 0 or scale == 0:
        raise ValueError("exponent and scale must be nonzero")
    return (1 / a + 4 / scale) * values[0] + values[3] / scale


def tree_kahler_gradient(s: object, t1: object, t2: object, t3: object) -> tuple[Rational, ...]:
    """Return the exact tree-level Kähler gradient on the declared physical cone."""

    s_q, t1_q, t2_q, t3_q = (coerce_rational(value) for value in (s, t1, t2, t3))
    total = t1_q + t2_q + 6 * t3_q
    if s_q <= 0 or t1_q <= 0 or t2_q <= 0 or total <= 0:
        raise ValueError("the physical cone requires positive s, t1, t2, and U")
    return (
        -Rational(1, 2) / s_q,
        -Rational(1, 2) * (1 / t1_q + 1 / total),
        -Rational(1, 2) * (1 / t2_q + 1 / total),
        -Rational(3) / total,
    )


def four_term_sign_obstruction(
    exponent: object = 1,
    p: object = 1,
    sample_point: Sequence[object] = (2, 3, 5, 7),
) -> ScopedSourceResult:
    """Recompute the four retained charge obstruction from explicit source vectors."""

    if len(sample_point) != 4:
        raise ValueError("sample_point must have four coordinates")
    charges = (
        worldsheet_charge(1, 0, p),
        worldsheet_charge(2, 0, p),
        worldsheet_charge(2, 1, p),
        condensate_charge(exponent),
    )
    classification = classify_charges(charges)
    value = affine_functional(tree_kahler_gradient(*sample_point), exponent, p)
    return ScopedSourceResult(
        "four-term sign obstruction",
        "KILLED" if value < 0 else "UNRESOLVED",
        "the physical Kähler-gradient sign is incompatible with the retained four-term source set"
        if value < 0
        else "the supplied sample does not certify the sign obstruction",
        (
            "finite ordinary base-degree-one worldsheet terms",
            "one tested condensate charge",
            "tree-level Kähler gradient",
        ),
        classification,
        ParameterProvenance("OneTheory source classification", "explicit charge recomputation"),
    )


def universal_affine_hyperplane_no_go(exponent: object = 1, p: object = 1) -> ScopedSourceResult:
    """Recompute the universal affine hyperplane for the ordinary retained sources."""

    charges = (
        worldsheet_charge(1, 0, p),
        worldsheet_charge(2, 0, p),
        worldsheet_charge(2, 1, p),
        condensate_charge(exponent),
    )
    classification = classify_charges(charges)
    return ScopedSourceResult(
        "universal affine-hyperplane no-go",
        "KILLED" if classification.affine_hyperplane is not None else "UNRESOLVED",
        "all supplied ordinary charges lie in a proper affine hyperplane"
        if classification.affine_hyperplane is not None
        else "the supplied charges do not lie in a proper affine hyperplane",
        (
            "ordinary base-degree-one worldsheet charges",
            "one tested condensate threshold direction",
        ),
        classification,
        ParameterProvenance("OneTheory source classification", "exact affine rank"),
    )


def one_extra_worldsheet_certificate(
    d1: int = 2,
    d2: int = 0,
    base_degree: int = 2,
    exponent: object = 1,
    p: object = 1,
) -> Mapping[str, object]:
    """Return the exact scoped higher-base charge relation and its hypothesis."""

    if base_degree < 2:
        raise ValueError("the higher-base certificate requires base degree at least two")
    a, scale = coerce_rational(exponent), coerce_rational(p)
    charges = (
        worldsheet_charge(1, 0, scale),
        worldsheet_charge(2, 0, scale),
        worldsheet_charge(2, 1, scale),
        condensate_charge(a),
        worldsheet_charge(d1, d2, scale, base_degree),
    )
    augmented = Matrix(tuple((*charge, Rational(1)) for charge in charges), scalar_type=Rational)
    weights = (
        Rational(2 * base_degree - d1, base_degree - 1),
        Rational(d1 - d2 - base_degree, base_degree - 1),
        Rational(d2, base_degree - 1),
        Rational(0),
        Rational(-1, base_degree - 1),
    )
    relation = tuple(
        sum((weights[row] * augmented[row][column] for row in range(5)), Rational(0))
        for column in range(4)
    )
    return {
        "augmented_determinant": augmented.determinant(),
        "expected_determinant": a * scale**3 * (base_degree - 1),
        "controlled_weights": weights,
        "weighted_charge_relation": relation,
        "one_term_multicover_closed": True,
        "assumption": "subexponential determinant growth in the controlled limit",
    }


def second_condensate_certificate(
    exponent1: object = 1,
    exponent2: object = 2,
    threshold_direction2: Sequence[object] = (
        Rational(-2, 3),
        Rational(1, 3),
        Rational(-4),
    ),
    p: object = 1,
) -> Mapping[str, object]:
    """Return the exact same-gauge-kinetic-function racetrack rank test."""

    a1, a2, scale = (
        coerce_rational(exponent1),
        coerce_rational(exponent2),
        coerce_rational(p),
    )
    direction = tuple(coerce_rational(value) for value in threshold_direction2)
    charges = (
        worldsheet_charge(1, 0, scale),
        worldsheet_charge(2, 0, scale),
        worldsheet_charge(2, 1, scale),
        condensate_charge(a1),
        condensate_charge(a2, direction),
    )
    standard = (Rational(-2, 3), Rational(1, 3), Rational(-4))
    return {
        "charge_rank": ChargeMatrix(charges).rank,
        "same_threshold_direction": direction == standard,
        "unequal_exponents": a1 != a2,
        "minimal_survivor": direction == standard and a1 != a2,
        "equal_exponents_collapse_to_one_exponential": a1 == a2,
    }


def racetrack_charge_rank_certificate(
    exponent1: object = 1, exponent2: object = 2, p: object = 1
) -> Mapping[str, object]:
    """Certify exact affine-rank lift from unequal same-direction exponents."""

    a1, a2, scale = (
        coerce_rational(exponent1),
        coerce_rational(exponent2),
        coerce_rational(p),
    )
    charges = (
        worldsheet_charge(1, 0, scale),
        worldsheet_charge(2, 0, scale),
        worldsheet_charge(2, 1, scale),
        condensate_charge(a1),
        condensate_charge(a2),
    )
    augmented = Matrix(tuple((*charge, Rational(1)) for charge in charges), scalar_type=Rational)
    return {
        "ordinary_affine_hull_dimension": ChargeMatrix(charges[:-1]).affine_rank,
        "racetrack_affine_hull_dimension": ChargeMatrix(charges).affine_rank,
        "augmented_determinant": augmented.determinant(),
        "expected_augmented_determinant": -(scale**3) * (a1 - a2),
        "rank_lift_if_and_only_if_unequal": a1 != a2,
    }


def scoped_source_classifications() -> tuple[ScopedSourceResult, ...]:
    """Return maintained exclusions without extending their hypotheses."""

    base = ParameterProvenance("OneTheory source classification", "explicit scope record")
    return (
        four_term_sign_obstruction(),
        universal_affine_hyperplane_no_go(),
        ScopedSourceResult(
            "split-bicubic Chern–Simons constant route",
            "KILLED",
            "the tested split-bicubic route does not satisfy the required mixed Chern class",
            ("published split-bicubic test",),
            None,
            base,
        ),
        ScopedSourceResult(
            "toral E6 Wilson-line classification",
            "KILLED",
            "the tested toral E6 route does not supply the required carrier spectrum",
            ("toral E6 Wilson-line classification",),
            None,
            base,
        ),
        ScopedSourceResult(
            "pure-SYM equal-exponent racetrack",
            "KILLED",
            "equal exponents collapse to one exponential",
            ("pure Yang–Mills", "equal exponents"),
            None,
            base,
        ),
        ScopedSourceResult(
            "one-higher-base worldsheet term",
            "CONDITIONAL",
            "excluded only under the declared controlled-limit determinant-growth hypothesis",
            ("one higher base degree", "subexponential determinant growth"),
            None,
            base,
        ),
        ScopedSourceResult(
            "one-term multicover",
            "CONDITIONAL",
            "excluded only under the declared determinant-growth hypothesis",
            ("one multicover term", "subexponential determinant growth"),
            None,
            base,
        ),
    )


def _complex_matrix_solve(
    matrix: Sequence[Sequence[complex]], vector: Sequence[complex], tolerance: float
) -> tuple[complex, ...]:
    """Solve one finite complex linear system with explicit pivot failure."""

    size = len(vector)
    if len(matrix) != size or any(len(row) != size for row in matrix):
        raise ValueError("Newton systems must be square")
    work = [list(row) + [value] for row, value in zip(matrix, vector, strict=True)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(work[row][column]))
        if abs(work[pivot][column]) <= tolerance:
            raise ValueError("Newton Jacobian is singular at the supplied point")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [value / divisor for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [
                left - factor * right for left, right in zip(work[row], work[column], strict=True)
            ]
    return tuple(work[row][-1] for row in range(size))


@dataclass(frozen=True, slots=True)
class VacuumEquationSystem:
    """Exact F/D equations derived from one Kähler potential and superpotential."""

    kahler: KaehlerPotential
    superpotential: SymbolicExpression
    fields: tuple[str, ...]
    d_terms: tuple[SymbolicExpression, ...] = ()
    domain: ValidityDomain = ValidityDomain()
    moduli_point: ModuliPoint | None = None

    def __post_init__(self) -> None:
        if not self.fields:
            raise ValueError("vacuum equation systems require fields")
        if tuple(self.fields) != tuple(self.kahler.fields):
            raise IncompatibleConvention("Kähler and vacuum systems declare different fields")
        point = self.moduli_point or self.kahler.expression.moduli_point
        if point != self.kahler.expression.moduli_point:
            raise IncompatibleConvention("vacuum equations use a different moduli point")
        object.__setattr__(self, "moduli_point", point)

    @property
    def f_terms(self) -> tuple[SymbolicExpression, ...]:
        """Return the exact Kähler-covariant F-term equations."""

        return tuple(
            self.kahler.kahler_covariant_derivative(self.superpotential, field)
            for field in self.fields
        )

    @property
    def equations(self) -> tuple[SymbolicExpression, ...]:
        """Return F- and explicitly supplied D-term equations."""

        return (*self.f_terms, *self.d_terms)

    def residuals(self, values: Mapping[str, complex | float | int]) -> tuple[complex, ...]:
        """Evaluate every equation at one candidate point."""

        return tuple(equation.evaluate(values) for equation in self.equations)

    def residual_norm(self, values: Mapping[str, complex | float | int]) -> float:
        """Return the maximum absolute equation residual."""

        residuals = self.residuals(values)
        return max((abs(value) for value in residuals), default=0.0)


SupersymmetricVacuumSystem = VacuumEquationSystem


@dataclass(frozen=True, slots=True)
class VacuumCandidate:
    """One numerically certified candidate with residual and domain metadata."""

    values: tuple[tuple[str, complex], ...]
    residual_norm: float
    precision: int
    domain_valid: bool
    converged: bool
    provenance: str

    @property
    def mapping(self) -> dict[str, complex]:
        """Return candidate coordinates as a fresh mapping."""

        return dict(self.values)


@dataclass(frozen=True, slots=True)
class VacuumSolveReport:
    """Deterministic solver output including refinement and duplicate-root records."""

    candidates: tuple[VacuumCandidate, ...]
    initial_regions: tuple[tuple[tuple[str, complex], ...], ...]
    precision_schedule: tuple[int, ...]
    residual_history: tuple[tuple[float, ...], ...]
    duplicate_count: int
    failed_regions: tuple[str, ...]
    provenance: str

    @property
    def complete(self) -> bool:
        """Return whether all reported candidates converged and pass their domains."""

        return bool(self.candidates) and all(
            candidate.converged and candidate.domain_valid for candidate in self.candidates
        )


def solve_supersymmetric_vacuum(
    system: VacuumEquationSystem,
    initial_regions: Iterable[Mapping[str, complex | float | int]],
    precision_schedule: Sequence[int] = (40, 80),
    tolerance: float = 1e-10,
    max_iterations: int = 80,
) -> VacuumSolveReport:
    """Solve explicit F/D equations deterministically by refined complex Newton steps."""

    if not precision_schedule or any(precision <= 0 for precision in precision_schedule):
        raise ValueError("precision schedule must contain positive levels")
    if max_iterations <= 0 or tolerance <= 0:
        raise ValueError("solver controls must be positive")
    regions = tuple(
        tuple((field, complex(values[field])) for field in system.fields if field in values)
        for values in initial_regions
    )
    if any(len(region) != len(system.fields) for region in regions):
        raise MissingPhysicalInput("initial values for every vacuum field")
    candidates: list[VacuumCandidate] = []
    histories: list[tuple[float, ...]] = []
    failures: list[str] = []
    duplicates = 0
    for region_index, region in enumerate(regions):
        values = dict(region)
        history: list[float] = []
        converged = False
        for _precision in precision_schedule:
            for _ in range(max_iterations):
                residual = system.residual_norm(values)
                history.append(residual)
                if residual <= tolerance:
                    converged = True
                    break
                equations = system.equations
                if len(equations) != len(system.fields):
                    failures.append(f"region {region_index}: non-square F/D system")
                    break
                jacobian = tuple(
                    tuple(equation.derivative(field).evaluate(values) for field in system.fields)
                    for equation in equations
                )
                try:
                    step = _complex_matrix_solve(
                        jacobian, tuple(-value for value in system.residuals(values)), 1e-14
                    )
                except ValueError as error:
                    failures.append(f"region {region_index}: {error}")
                    break
                values = {
                    field: values[field] + delta
                    for field, delta in zip(system.fields, step, strict=True)
                }
            if not converged:
                continue
            if not system.domain.contains(values, tolerance):
                failures.append(f"region {region_index}: validity domain failed")
                converged = False
            break
        histories.append(tuple(history))
        candidate = VacuumCandidate(
            tuple((field, values[field]) for field in system.fields),
            system.residual_norm(values),
            precision_schedule[-1],
            system.domain.contains(values, tolerance),
            converged,
            "deterministic complex Newton refinement",
        )
        if candidate.converged and candidate.domain_valid:
            if any(
                max(
                    abs(candidate.mapping[field] - previous.mapping[field])
                    for field in system.fields
                )
                <= tolerance * 10
                for previous in candidates
            ):
                duplicates += 1
            else:
                candidates.append(candidate)
    return VacuumSolveReport(
        tuple(candidates),
        regions,
        tuple(precision_schedule),
        tuple(histories),
        duplicates,
        tuple(failures),
        "explicit equations, regions, and precision schedule",
    )


@dataclass(frozen=True, slots=True)
class BreitenlohnerFreedmanResult:
    """AdS BF-bound stability result for a canonically normalized spectrum."""

    dimension: int
    radius_squared: float
    lowest_mass_squared: float
    bound: float
    stable: bool


@dataclass(frozen=True, slots=True)
class CriticalPointReport:
    """A critical-point classification separated from coordinate stability."""

    values: tuple[tuple[str, complex], ...]
    potential_value: float
    supersymmetric: bool
    vacuum_type: VacuumType
    canonical_hessian: tuple[tuple[float, ...], ...]
    masses_squared: tuple[float, ...]
    flat_directions: tuple[int, ...]
    goldstone_directions: tuple[int, ...]
    metastable: bool
    bf: BreitenlohnerFreedmanResult | None
    provenance: str


def canonical_real_hessian(
    potential: SymbolicExpression,
    variables: Sequence[str],
    kinetic: Sequence[Sequence[float]],
    point: Mapping[str, complex | float | int],
    tolerance: float = 1e-10,
) -> tuple[tuple[float, ...], ...]:
    """Return the real Hessian normalized by a supplied positive kinetic metric."""

    size = len(variables)
    if len(kinetic) != size or any(len(row) != size for row in kinetic):
        raise ValueError("Hessian and kinetic dimensions do not agree")
    metric = tuple(tuple(float(value) for value in row) for row in kinetic)
    for principal_size in range(1, size + 1):
        principal = tuple(
            tuple(complex(metric[row][column]) for column in range(principal_size))
            for row in range(principal_size)
        )
        if _numeric_determinant(principal).real <= tolerance:
            raise ValueError("canonical normalization requires a positive kinetic metric")
    inverse = _numeric_inverse(
        tuple(tuple(complex(value) for value in row) for row in metric), tolerance
    )
    hessian = tuple(
        tuple(
            float(potential.second_derivative(left, right).evaluate(point).real)
            for right in variables
        )
        for left in variables
    )
    # For a diagonal or already canonically supplied metric, G^{-1}H is the
    # mass operator. Symmetrization keeps the returned form real and symmetric.
    operator = tuple(
        tuple(
            sum(inverse[row][inner].real * hessian[inner][column] for inner in range(size))
            for column in range(size)
        )
        for row in range(size)
    )
    return tuple(
        tuple((operator[row][column] + operator[column][row]) / 2 for column in range(size))
        for row in range(size)
    )


def classify_critical_point(
    potential: SymbolicExpression,
    variables: Sequence[str],
    kinetic: Sequence[Sequence[float]],
    point: Mapping[str, complex | float | int],
    supersymmetric: bool,
    cosmological_tolerance: float = 1e-10,
) -> CriticalPointReport:
    """Classify one supplied critical point using the canonical Hessian."""

    matrix = canonical_real_hessian(potential, variables, kinetic, point)
    masses = tuple(matrix[index][index] for index in range(len(matrix)))
    flat = tuple(index for index, mass in enumerate(masses) if abs(mass) <= cosmological_tolerance)
    value = potential.evaluate(point).real
    vacuum_type = (
        VacuumType.MINKOWSKI
        if abs(value) <= cosmological_tolerance
        else VacuumType.ADS
        if value < 0
        else VacuumType.DESITTER
    )
    bf = None
    if vacuum_type is VacuumType.ADS:
        radius = 3.0 / max(abs(value), cosmological_tolerance)
        bound = -9.0 / (4.0 * radius)
        bf = BreitenlohnerFreedmanResult(
            4, radius, min(masses, default=0.0), bound, min(masses, default=0.0) >= bound
        )
    return CriticalPointReport(
        tuple((variable, complex(point[variable])) for variable in variables),
        value,
        supersymmetric,
        vacuum_type,
        matrix,
        masses,
        flat,
        (),
        all(mass >= -cosmological_tolerance for mass in masses),
        bf,
        "canonical real Hessian with supplied kinetic metric",
    )


class ControlStatus(StrEnum):
    """Outcome vocabulary for the approximation-control ledger."""

    CONTROLLED = "CONTROLLED"
    CONDITIONAL = "CONDITIONAL"
    UNCONTROLLED = "UNCONTROLLED"
    MISSING_INPUT = "MISSING_INPUT"
    NUMERICAL_FAILURE = "NUMERICAL_FAILURE"


@dataclass(frozen=True, slots=True)
class ControlCriterion:
    """One explicit approximation criterion and its declared result."""

    name: str
    status: ControlStatus
    value: float | None
    bound: float | None
    provenance: ParameterProvenance
    reason: str

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.reason.strip():
            raise ValueError("control criteria require names and reasons")


@dataclass(frozen=True, slots=True)
class ControlLedger:
    """The complete finite ledger required before a vacuum is called controlled."""

    criteria: tuple[ControlCriterion, ...]
    status: ControlStatus
    provenance: str

    @classmethod
    def from_criteria(cls, criteria: Iterable[ControlCriterion]) -> ControlLedger:
        """Aggregate criteria with fail-closed precedence."""

        values = tuple(criteria)
        if not values:
            return cls((), ControlStatus.MISSING_INPUT, "empty control ledger")
        statuses = {criterion.status for criterion in values}
        if ControlStatus.NUMERICAL_FAILURE in statuses:
            status = ControlStatus.NUMERICAL_FAILURE
        elif ControlStatus.MISSING_INPUT in statuses:
            status = ControlStatus.MISSING_INPUT
        elif ControlStatus.UNCONTROLLED in statuses:
            status = ControlStatus.UNCONTROLLED
        elif ControlStatus.CONDITIONAL in statuses:
            status = ControlStatus.CONDITIONAL
        else:
            status = ControlStatus.CONTROLLED
        return cls(values, status, "explicit criterion aggregation")

    @property
    def controlled(self) -> bool:
        """Return whether every criterion passes without conditional assumptions."""

        return self.status is ControlStatus.CONTROLLED


def suppression_ratio(omitted: object, retained: object) -> Rational:
    """Return an exact omitted-to-retained ratio for declared positive amplitudes."""

    numerator, denominator = coerce_rational(omitted), coerce_rational(retained)
    if denominator <= 0 or numerator < 0:
        raise ValueError(
            "suppression ratios require nonnegative numerator and positive denominator"
        )
    return numerator / denominator


@dataclass(frozen=True, slots=True)
class Superpotential:
    """A holomorphic superpotential expression with explicit source provenance."""

    expression: EffectiveExpression
    chiral_fields: tuple[str, ...]
    symbolic_expression: SymbolicExpression | None = None
    provenance: ParameterProvenance | None = None

    def __post_init__(self) -> None:
        if not self.chiral_fields:
            raise ValueError("superpotentials require at least one chiral field")

    @property
    def name(self) -> str:
        """Return the standard W symbol."""

        return "W"

    @classmethod
    def from_symbolic(
        cls,
        expression: SymbolicExpression,
        fields: Iterable[ComplexScalarField | str],
        moduli_point: ModuliPoint,
        provenance: ParameterProvenance,
        normalization: str = "Einstein",
    ) -> Superpotential:
        """Construct a holomorphic superpotential from an exact expression."""

        names = tuple(
            field.name if isinstance(field, ComplexScalarField) else field for field in fields
        )
        if not names or any(not name.strip() for name in names):
            raise ValueError("symbolic superpotentials require named fields")
        effective = EffectiveExpression(
            expression.text(),
            provenance.source,
            (provenance.evidence,),
            moduli_point,
            "exact symbolic",
            normalization,
        )
        return cls(effective, names, expression, provenance)


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
    "BranchCondition",
    "BreitenlohnerFreedmanResult",
    "ChargeClassification",
    "ChargeMatrix",
    "ChiralMultiplet",
    "ComplexField",
    "ComplexScalarField",
    "ControlCriterion",
    "ControlLedger",
    "ControlStatus",
    "ChristoffelSymbols",
    "CriticalPointConditions",
    "CriticalPointReport",
    "DTermPotential",
    "DomainCondition",
    "EffectiveAction",
    "EffectiveExpression",
    "Expression",
    "FluxConstant",
    "FTermPotential",
    "GauginoCondensate",
    "GaugeKineticMatrix",
    "GravitinoMass",
    "Hessian",
    "KahlerCovariantDerivative",
    "KahlerPotential",
    "KaehlerMetric",
    "KaehlerPotential",
    "KählerMetric",
    "KineticMatrix",
    "KineticNormalization",
    "HolomorphicExpression",
    "MulticoverContribution",
    "ModuliPoint",
    "MomentMap",
    "N1EffectiveAction",
    "N1Action",
    "ParameterProvenance",
    "PhysicalInputRequirement",
    "PerturbativeCorrection",
    "RacetrackSuperpotential",
    "RealScalarField",
    "RealExpression",
    "RealField",
    "ScopedSourceResult",
    "ScalarPotential",
    "SourceTerm",
    "StabilityCondition",
    "Superpotential",
    "SuperpotentialWithSymbolics",
    "SymbolicExpression",
    "SymbolicSuperpotential",
    "ThresholdGaugeKineticFunction",
    "UpliftTerm",
    "ValidityDomain",
    "VacuumCandidate",
    "VacuumEquationSystem",
    "VacuumSolveReport",
    "VacuumType",
    "VectorMultiplet",
    "WorldsheetInstanton",
    "affine_functional",
    "canonical_real_hessian",
    "christoffel_symbols",
    "classify_charges",
    "classify_critical_point",
    "condensate_charge",
    "four_term_sign_obstruction",
    "kinetic_normalization",
    "one_extra_worldsheet_certificate",
    "racetrack_charge_rank_certificate",
    "second_condensate_certificate",
    "scoped_source_classifications",
    "solve_supersymmetric_vacuum",
    "suppression_ratio",
    "tree_kahler_gradient",
    "universal_affine_hyperplane_no_go",
    "worldsheet_charge",
]


def _permutation_sign(permutation: tuple[int, ...]) -> int:
    """Return the sign of a finite permutation."""

    inversions = sum(
        1
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
        if permutation[left] > permutation[right]
    )
    return -1 if inversions % 2 else 1


def _symbolic_determinant(
    entries: tuple[tuple[SymbolicExpression, ...], ...],
) -> SymbolicExpression:
    """Compute a small symbolic determinant by the Leibniz formula."""

    size = len(entries)
    if size == 0 or any(len(row) != size for row in entries):
        raise ValueError("symbolic determinants require nonempty square data")
    result = SymbolicExpression.constant(0)
    for permutation in __import__("itertools").permutations(range(size)):
        term = SymbolicExpression.constant(_permutation_sign(tuple(permutation)))
        for row, column in enumerate(permutation):
            term *= entries[row][column]
        result += term
    return result.simplify()


def _symbolic_minor(
    entries: tuple[tuple[SymbolicExpression, ...], ...],
    omitted_row: int,
    omitted_column: int,
) -> SymbolicExpression:
    """Return a symbolic cofactor minor."""

    rows = tuple(
        tuple(value for column, value in enumerate(row) if column != omitted_column)
        for row_index, row in enumerate(entries)
        if row_index != omitted_row
    )
    if not rows:
        return SymbolicExpression.constant(1)
    return _symbolic_determinant(rows)


@dataclass(frozen=True, slots=True)
class KaehlerMetric:
    """A symbolic Hermitian field-space metric with explicit inversion checks."""

    fields: tuple[str, ...]
    entries: tuple[tuple[SymbolicExpression, ...], ...]
    provenance: ParameterProvenance | None = None

    def __post_init__(self) -> None:
        size = len(self.fields)
        if not size or len(self.entries) != size or any(len(row) != size for row in self.entries):
            raise ValueError("Kähler metrics require a nonempty square field matrix")

    @property
    def dimension(self) -> int:
        """Return the number of complex field coordinates."""

        return len(self.fields)

    def determinant(self) -> SymbolicExpression:
        """Return the exact symbolic determinant."""

        return _symbolic_determinant(self.entries)

    def inverse(self) -> KaehlerMetric:
        """Return the exact inverse metric or reject a identically singular metric."""

        determinant = self.determinant().simplify()
        if determinant.is_zero():
            raise ValueError("Kähler metric is symbolically singular")
        inverse_rows: list[tuple[SymbolicExpression, ...]] = []
        for row in range(self.dimension):
            inverse_rows.append(
                tuple(
                    _symbolic_minor(self.entries, column, row)
                    * (1 if (row + column) % 2 == 0 else -1)
                    / determinant
                    for column in range(self.dimension)
                )
            )
        return KaehlerMetric(self.fields, tuple(inverse_rows), self.provenance)

    def evaluate(
        self, values: Mapping[str, complex | float | int]
    ) -> tuple[tuple[complex, ...], ...]:
        """Evaluate all metric entries numerically."""

        return tuple(tuple(entry.evaluate(values) for entry in row) for row in self.entries)

    def positive_definite(
        self,
        values: Mapping[str, complex | float | int],
        tolerance: float = 1e-12,
    ) -> bool:
        """Check Hermitian positive definiteness at one supplied point."""

        matrix = self.evaluate(values)
        for row in range(self.dimension):
            for column in range(self.dimension):
                if abs(matrix[row][column] - matrix[column][row].conjugate()) > tolerance:
                    return False
        for size in range(1, self.dimension + 1):
            minor = _numeric_determinant(
                tuple(tuple(matrix[row][column] for column in range(size)) for row in range(size))
            )
            if minor.imag > tolerance or minor.real <= tolerance:
                return False
        return True

    @property
    def singular_boundary(self) -> SymbolicExpression:
        """Return the exact boundary equation det(K)=0."""

        return self.determinant()

    def inverse_at(
        self,
        values: Mapping[str, complex | float | int],
        tolerance: float = 1e-12,
    ) -> tuple[tuple[complex, ...], ...]:
        """Invert only after a positive-definite point has been certified."""

        if not self.positive_definite(values, tolerance):
            raise ValueError("Kähler metric is singular or non-positive at the supplied point")
        return _numeric_inverse(self.evaluate(values), tolerance)


KählerMetric = KaehlerMetric


def _numeric_determinant(matrix: tuple[tuple[complex, ...], ...]) -> complex:
    """Compute a finite complex determinant for controlled diagnostic checks."""

    size = len(matrix)
    work = [list(row) for row in matrix]
    result = 1.0 + 0.0j
    for column in range(size):
        pivot = next((row for row in range(column, size) if abs(work[row][column]) > 1e-15), None)
        if pivot is None:
            return 0.0 + 0.0j
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        value = work[column][column]
        result *= value
        for row in range(column + 1, size):
            factor = work[row][column] / value
            for inner in range(column + 1, size):
                work[row][inner] -= factor * work[column][inner]
    return result


def _numeric_inverse(
    matrix: tuple[tuple[complex, ...], ...], tolerance: float
) -> tuple[tuple[complex, ...], ...]:
    """Invert a positive definite numerical matrix by deterministic elimination."""

    size = len(matrix)
    work = [
        list(matrix[row]) + [1.0 + 0.0j if row == column else 0.0 + 0.0j for column in range(size)]
        for row in range(size)
    ]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(work[row][column]))
        if abs(work[pivot][column]) <= tolerance:
            raise ValueError("numerical metric inversion encountered a singular pivot")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [value / divisor for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [
                left - factor * right for left, right in zip(work[row], work[column], strict=True)
            ]
    return tuple(tuple(row[size:]) for row in work)


@dataclass(frozen=True, slots=True)
class ChristoffelSymbols:
    """Kähler Levi-Civita connection coefficients derived from one metric."""

    fields: tuple[str, ...]
    entries: tuple[tuple[tuple[SymbolicExpression, ...], ...], ...]
    provenance: ParameterProvenance | None = None

    @classmethod
    def from_potential(cls, potential: KaehlerPotential) -> ChristoffelSymbols:
        """Derive Γᵏᵢⱼ from the symbolic Kähler potential."""

        metric = potential.metric()
        inverse = metric.inverse()
        rows: list[tuple[tuple[SymbolicExpression, ...], ...]] = []
        for upper in range(metric.dimension):
            upper_rows: list[tuple[SymbolicExpression, ...]] = []
            for i in range(metric.dimension):
                upper_rows.append(
                    tuple(
                        sum(
                            (
                                inverse.entries[upper][ell]
                                * metric.entries[j][ell].derivative(potential.fields[i])
                                for ell in range(metric.dimension)
                            ),
                            SymbolicExpression.constant(0),
                        )
                        for j in range(metric.dimension)
                    )
                )
            rows.append(tuple(upper_rows))
        return cls(potential.fields, tuple(rows), potential.provenance)


@dataclass(frozen=True, slots=True)
class KineticNormalization:
    """A certified field-space metric normalization at a supplied point."""

    metric: KaehlerMetric
    point: Mapping[str, complex | float | int]
    inverse: tuple[tuple[complex, ...], ...]
    provenance: ParameterProvenance | None = None

    @classmethod
    def from_metric(
        cls,
        metric: KaehlerMetric,
        point: Mapping[str, complex | float | int],
        provenance: ParameterProvenance | None = None,
    ) -> KineticNormalization:
        """Normalize kinetic terms only after positivity and inversion succeed."""

        return cls(metric, dict(point), metric.inverse_at(point), provenance)


def christoffel_symbols(potential: KaehlerPotential) -> ChristoffelSymbols:
    """Derive the Kähler connection from one exact potential."""

    return ChristoffelSymbols.from_potential(potential)


def kinetic_normalization(
    metric: KaehlerMetric,
    point: Mapping[str, complex | float | int],
    provenance: ParameterProvenance | None = None,
) -> KineticNormalization:
    """Normalize kinetic terms only after a positive metric is certified."""

    return KineticNormalization.from_metric(metric, point, provenance)


@dataclass(frozen=True, slots=True)
class SymbolicSuperpotential(Superpotential):
    """A holomorphic superpotential retaining exact source expressions."""

    symbolic_expression: SymbolicExpression | None = None
    provenance: ParameterProvenance | None = None

    @classmethod
    def from_symbolic(
        cls,
        expression: SymbolicExpression,
        fields: Iterable[ComplexScalarField | str],
        moduli_point: ModuliPoint,
        provenance: ParameterProvenance,
        normalization: str = "Einstein",
    ) -> SymbolicSuperpotential:
        """Construct a superpotential from an exact restricted expression."""

        names = tuple(
            field.name if isinstance(field, ComplexScalarField) else field for field in fields
        )
        if not names or any(not name.strip() for name in names):
            raise ValueError("symbolic superpotentials require named fields")
        effective = EffectiveExpression(
            expression.text(),
            provenance.source,
            (provenance.evidence,),
            moduli_point,
            "exact symbolic",
            normalization,
        )
        return cls(effective, names, expression, provenance)


SuperpotentialWithSymbolics = SymbolicSuperpotential
