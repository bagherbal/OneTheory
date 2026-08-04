"""Immutable exact sparse polynomial algebra over declared scalar fields.

Owns:
    Monomial normalization, sparse polynomial arithmetic and substitution,
    polynomial-matrix determinants and maximal minors, and exact univariate
    division, derivatives, and monic greatest common divisors.

Depends on:
    `onetheory.math.numbers` for exact Rational and Eisenstein scalar coercion and
    arithmetic. The algorithms are shared across both supported coefficient fields.

Must not:
    Implement ideals, Groebner bases, geometry, carrier objects, physical claims,
    approximate roots, numerical algorithms, or interpretations of algebraic data.

Phase 0:
    The reusable exact polynomial foundation is implemented; higher symbolic and
    physical domains remain structural only.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations
from typing import Any, cast

from onetheory.math.numbers import Eisenstein, Rational, coerce_rational

Scalar = Rational | Eisenstein
type ScalarType = type[Rational] | type[Eisenstein]
type Monomial = tuple[int, ...]


def _scalar_type_for_values(values: Iterable[object]) -> ScalarType:
    return Eisenstein if any(isinstance(value, Eisenstein) for value in values) else Rational


def _coerce(value: object, scalar_type: ScalarType) -> Scalar:
    if scalar_type is Rational:
        return coerce_rational(value)
    if scalar_type is Eisenstein:
        return Eisenstein.coerce(value)
    raise TypeError("scalar_type must be Rational or Eisenstein")


def _zero(scalar_type: ScalarType) -> Scalar:
    return _coerce(0, scalar_type)


def _one(scalar_type: ScalarType) -> Scalar:
    return _coerce(1, scalar_type)


def _add(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) + right)


def _subtract(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) - right)


def _multiply(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) * right)


def _negate(value: Scalar) -> Scalar:
    return cast(Scalar, -cast(Any, value))


def _divide(left: Scalar, right: Scalar) -> Scalar:
    return cast(Scalar, cast(Any, left) / right)


def _is_zero(value: Scalar) -> bool:
    return value.is_zero()


def _validate_variable_count(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("variable_count must be a nonnegative integer")
    return value


def _validate_monomial(exponents: Iterable[int], variable_count: int) -> Monomial:
    monomial = tuple(exponents)
    if len(monomial) != variable_count:
        raise ValueError("monomial dimension does not match variable_count")
    if any(isinstance(exponent, bool) or not isinstance(exponent, int) for exponent in monomial):
        raise TypeError("monomial exponents must be integers")
    if any(exponent < 0 for exponent in monomial):
        raise ValueError("monomial exponents must be nonnegative")
    return monomial


def _require_compatible(left: Polynomial, right: Polynomial) -> None:
    if left.variable_count != right.variable_count:
        raise ValueError("polynomial variable counts do not agree")
    if left.scalar_type is not right.scalar_type:
        raise TypeError("polynomials must use the same exact scalar type")


@dataclass(frozen=True, slots=True, init=False)
class Polynomial:
    """An immutable normalized sparse polynomial over one exact scalar field."""

    _terms: tuple[tuple[Monomial, Scalar], ...]
    _variable_count: int
    _scalar_type: ScalarType

    def __init__(
        self,
        terms: Mapping[Monomial, object] | Iterable[tuple[Iterable[int], object]] = (),
        *,
        variable_count: int | None = None,
        scalar_type: ScalarType | None = None,
    ) -> None:
        raw_input = tuple(terms.items()) if isinstance(terms, Mapping) else tuple(terms)
        raw_terms = tuple(
            (tuple(exponents), coefficient) for exponents, coefficient in raw_input
        )
        if variable_count is None:
            inferred_count = len(raw_terms[0][0]) if raw_terms else 0
        else:
            inferred_count = _validate_variable_count(variable_count)
        resolved = (
            _scalar_type_for_values(coefficient for _, coefficient in raw_terms)
            if scalar_type is None
            else scalar_type
        )
        combined: dict[Monomial, Scalar] = {}
        for raw_exponents, raw_coefficient in raw_terms:
            exponents = _validate_monomial(raw_exponents, inferred_count)
            coefficient = _coerce(raw_coefficient, resolved)
            combined[exponents] = _add(combined.get(exponents, _zero(resolved)), coefficient)
        normalized = tuple(
            sorted(
                (
                    (exponents, coefficient)
                    for exponents, coefficient in combined.items()
                    if not _is_zero(coefficient)
                ),
                key=lambda item: item[0],
                reverse=True,
            )
        )
        object.__setattr__(self, "_terms", normalized)
        object.__setattr__(self, "_variable_count", inferred_count)
        object.__setattr__(self, "_scalar_type", resolved)

    @classmethod
    def zero(
        cls,
        variable_count: int = 0,
        *,
        scalar_type: ScalarType = Rational,
    ) -> Polynomial:
        """Construct the normalized zero polynomial in the requested ring."""

        return cls((), variable_count=variable_count, scalar_type=scalar_type)

    @classmethod
    def one(
        cls,
        variable_count: int = 0,
        *,
        scalar_type: ScalarType = Rational,
    ) -> Polynomial:
        """Construct the multiplicative identity in the requested ring."""

        return cls.monomial(
            (0,) * _validate_variable_count(variable_count),
            1,
            scalar_type=scalar_type,
        )

    @classmethod
    def constant(
        cls,
        value: object,
        variable_count: int = 0,
        *,
        scalar_type: ScalarType | None = None,
    ) -> Polynomial:
        """Construct an exact constant polynomial."""

        count = _validate_variable_count(variable_count)
        return cls(
            (((0,) * count, value),),
            variable_count=count,
            scalar_type=scalar_type,
        )

    @classmethod
    def monomial(
        cls,
        exponents: Iterable[int],
        coefficient: object = 1,
        *,
        scalar_type: ScalarType | None = None,
    ) -> Polynomial:
        """Construct one normalized monomial with exact coefficient."""

        normalized_exponents = tuple(exponents)
        return cls(
            ((normalized_exponents, coefficient),),
            variable_count=len(normalized_exponents),
            scalar_type=scalar_type,
        )

    @classmethod
    def from_coefficients(
        cls,
        coefficients: Sequence[object],
        *,
        scalar_type: ScalarType | None = None,
    ) -> Polynomial:
        """Construct a univariate polynomial from ascending coefficients."""

        return cls(
            (((degree,), coefficient) for degree, coefficient in enumerate(coefficients)),
            variable_count=1,
            scalar_type=scalar_type,
        )

    @property
    def terms(self) -> tuple[tuple[Monomial, Scalar], ...]:
        """Return normalized nonzero terms in deterministic order."""

        return self._terms

    @property
    def variable_count(self) -> int:
        """Return the number of commuting variables."""

        return self._variable_count

    @property
    def scalar_type(self) -> ScalarType:
        """Return the exact coefficient type of this polynomial."""

        return self._scalar_type

    @property
    def degree(self) -> int:
        """Return total degree, or -1 for the normalized zero polynomial."""

        if self.is_zero():
            return -1
        return max(sum(exponents) for exponents, _ in self._terms)

    @property
    def univariate_degree(self) -> int:
        """Return degree in one variable, or -1 for zero."""

        self._require_univariate()
        return -1 if self.is_zero() else self._terms[0][0][0]

    @property
    def leading_coefficient(self) -> Scalar:
        """Return the leading coefficient of a nonzero univariate polynomial."""

        self._require_univariate()
        if self.is_zero():
            raise ValueError("zero polynomial has no leading coefficient")
        return self._terms[0][1]

    def coefficient(self, exponents: Iterable[int]) -> Scalar:
        """Return an exact coefficient, using zero for an absent monomial."""

        monomial = _validate_monomial(exponents, self.variable_count)
        for existing, coefficient in self._terms:
            if existing == monomial:
                return coefficient
        return _zero(self._scalar_type)

    def __len__(self) -> int:
        return len(self._terms)

    def __iter__(self) -> Iterator[tuple[Monomial, Scalar]]:
        return iter(self._terms)

    def __getitem__(self, exponents: Monomial) -> Scalar:
        return self.coefficient(exponents)

    def __bool__(self) -> bool:
        return not self.is_zero()

    def is_zero(self) -> bool:
        """Return whether normalization removed every term."""

        return not self._terms

    def _require_univariate(self) -> None:
        if self.variable_count != 1:
            raise ValueError("the operation requires a univariate polynomial")

    def _combine(self, other: Polynomial, subtract: bool) -> Polynomial:
        _require_compatible(self, other)
        result: dict[Monomial, Scalar] = dict(self._terms)
        for exponents, coefficient in other._terms:
            current = result.get(exponents, _zero(self._scalar_type))
            result[exponents] = (
                _subtract(current, coefficient) if subtract else _add(current, coefficient)
            )
        return Polynomial(
            result,
            variable_count=self.variable_count,
            scalar_type=self._scalar_type,
        )

    def __add__(self, other: Polynomial) -> Polynomial:
        return self._combine(other, subtract=False)

    def __sub__(self, other: Polynomial) -> Polynomial:
        return self._combine(other, subtract=True)

    def __neg__(self) -> Polynomial:
        return Polynomial(
            ((exponents, _negate(coefficient)) for exponents, coefficient in self._terms),
            variable_count=self.variable_count,
            scalar_type=self._scalar_type,
        )

    def scale(self, scalar: object) -> Polynomial:
        """Multiply every coefficient by one exact scalar."""

        factor = _coerce(scalar, self._scalar_type)
        return Polynomial(
            (
                (exponents, _multiply(factor, coefficient))
                for exponents, coefficient in self._terms
            ),
            variable_count=self.variable_count,
            scalar_type=self._scalar_type,
        )

    def __mul__(self, other: object) -> Polynomial:
        if not isinstance(other, Polynomial):
            return self.scale(other)
        _require_compatible(self, other)
        result: dict[Monomial, Scalar] = {}
        for left_exponents, left_coefficient in self._terms:
            for right_exponents, right_coefficient in other._terms:
                exponents = tuple(
                    left + right
                    for left, right in zip(left_exponents, right_exponents, strict=True)
                )
                product = _multiply(left_coefficient, right_coefficient)
                result[exponents] = _add(
                    result.get(exponents, _zero(self._scalar_type)),
                    product,
                )
        return Polynomial(
            result,
            variable_count=self.variable_count,
            scalar_type=self._scalar_type,
        )

    def __rmul__(self, other: object) -> Polynomial:
        return self * other

    def __pow__(self, exponent: int) -> Polynomial:
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            raise TypeError("the exponent must be an integer")
        if exponent < 0:
            raise ValueError("polynomial powers must be nonnegative")
        result = Polynomial.one(self.variable_count, scalar_type=self._scalar_type)
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result

    def derivative(self, variable: int = 0) -> Polynomial:
        """Return the exact formal derivative with respect to one variable."""

        if self.variable_count == 0:
            raise ValueError("a constant polynomial has no variable derivative")
        if isinstance(variable, bool) or not isinstance(variable, int):
            raise TypeError("variable index must be an integer")
        if not 0 <= variable < self.variable_count:
            raise IndexError("variable index is out of range")
        terms: list[tuple[Monomial, Scalar]] = []
        for exponents, coefficient in self._terms:
            power = exponents[variable]
            if power == 0:
                continue
            derivative_exponents = list(exponents)
            derivative_exponents[variable] -= 1
            terms.append(
                (
                    tuple(derivative_exponents),
                    _multiply(coefficient, _coerce(power, self._scalar_type)),
                )
            )
        return Polynomial(
            terms,
            variable_count=self.variable_count,
            scalar_type=self._scalar_type,
        )

    def substitute(self, images: Sequence[object]) -> Polynomial:
        """Substitute exact scalar or polynomial images for every variable."""

        if len(images) != self.variable_count:
            raise ValueError("substitution count must match variable_count")
        polynomial_images = tuple(image for image in images if isinstance(image, Polynomial))
        target_counts = {image.variable_count for image in polynomial_images}
        if len(target_counts) > 1:
            raise ValueError("substitution images must use one target variable count")
        target_count = next(iter(target_counts), 0)
        normalized_images: list[Polynomial] = []
        for image in images:
            if isinstance(image, Polynomial):
                if image.scalar_type is not self.scalar_type:
                    raise TypeError("substitution images must use the source scalar type")
                normalized_images.append(image)
            else:
                normalized_images.append(
                    Polynomial.constant(
                        image,
                        variable_count=target_count,
                        scalar_type=self.scalar_type,
                    )
                )
        result = Polynomial.zero(target_count, scalar_type=self.scalar_type)
        for exponents, coefficient in self._terms:
            term = Polynomial.constant(
                coefficient,
                variable_count=target_count,
                scalar_type=self.scalar_type,
            )
            for image, power in zip(normalized_images, exponents, strict=True):
                if power:
                    term = term * (image**power)
            result = result + term
        return result

    def substitute_monomials(
        self,
        images: Sequence[tuple[object, Iterable[int]]],
    ) -> Polynomial:
        """Substitute exact scalar multiples of target monomials."""

        if len(images) != self.variable_count:
            raise ValueError("substitution count must match variable_count")
        raw_images = tuple((scalar, tuple(exponents)) for scalar, exponents in images)
        target_count = len(raw_images[0][1]) if raw_images else 0
        normalized_images = tuple(
            Polynomial.monomial(
                _validate_monomial(exponents, target_count),
                scalar,
                scalar_type=self.scalar_type,
            )
            for scalar, exponents in raw_images
        )
        return self.substitute(normalized_images)

    def monic(self) -> Polynomial:
        """Return the exact monic normalization of a nonzero univariate polynomial."""

        leading = self.leading_coefficient
        return self.scale(_divide(_one(self.scalar_type), leading))

    def divmod_univariate(self, divisor: Polynomial) -> tuple[Polynomial, Polynomial]:
        """Return exact quotient and remainder for univariate division."""

        _require_compatible(self, divisor)
        self._require_univariate()
        divisor._require_univariate()
        if divisor.is_zero():
            raise ZeroDivisionError("polynomial division by zero")
        quotient = Polynomial.zero(1, scalar_type=self.scalar_type)
        remainder = self
        divisor_degree = divisor.univariate_degree
        while not remainder.is_zero() and remainder.univariate_degree >= divisor_degree:
            shift = remainder.univariate_degree - divisor_degree
            factor = _divide(remainder.leading_coefficient, divisor.leading_coefficient)
            term = Polynomial.monomial((shift,), factor, scalar_type=self.scalar_type)
            quotient = quotient + term
            remainder = remainder - term * divisor
        return quotient, remainder

    def gcd(self, other: Polynomial) -> Polynomial:
        """Return the monic exact greatest common divisor of two univariates."""

        _require_compatible(self, other)
        self._require_univariate()
        other._require_univariate()
        left, right = self, other
        while not right.is_zero():
            _, remainder = left.divmod_univariate(right)
            left, right = right, remainder
        return Polynomial.zero(1, scalar_type=self.scalar_type) if left.is_zero() else left.monic()


@dataclass(frozen=True, slots=True, init=False)
class PolynomialMatrix:
    """An immutable matrix map between finite free polynomial modules."""

    rows: tuple[tuple[Polynomial, ...], ...]

    def __init__(self, rows: Iterable[Iterable[Polynomial]]) -> None:
        object.__setattr__(self, "rows", _matrix_rows(rows))

    @property
    def shape(self) -> tuple[int, int]:
        """Return the codomain and domain ranks."""

        return len(self.rows), len(self.rows[0])

    @property
    def variable_count(self) -> int:
        """Return the common polynomial variable count."""

        return self.rows[0][0].variable_count

    @property
    def scalar_type(self) -> ScalarType:
        """Return the common exact coefficient field."""

        return self.rows[0][0].scalar_type

    def compose(self, previous: PolynomialMatrix) -> PolynomialMatrix:
        """Compose this map after a compatible polynomial matrix map."""

        if self.shape[1] != previous.shape[0]:
            raise ValueError("polynomial matrix maps have incompatible ranks")
        return PolynomialMatrix(
            tuple(
                tuple(
                    sum(
                        (
                            self.rows[row][inner] * previous.rows[inner][column]
                            for inner in range(self.shape[1])
                        ),
                        Polynomial.zero(self.variable_count, scalar_type=self.scalar_type),
                    )
                    for column in range(previous.shape[1])
                )
                for row in range(self.shape[0])
            )
        )

    def is_zero(self) -> bool:
        """Return whether every polynomial entry is exactly zero."""

        return all(entry.is_zero() for row in self.rows for entry in row)


@dataclass(frozen=True, slots=True)
class PolynomialFreeModule:
    """A named finite free module with exact basis shifts."""

    name: str
    basis: tuple[str, ...]
    shifts: tuple[tuple[int, ...], ...]
    variable_count: int
    scalar_type: ScalarType

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.basis:
            raise ValueError("polynomial free modules require a name and basis")
        if len(set(self.basis)) != len(self.basis):
            raise ValueError("polynomial free-module basis labels must be unique")
        if len(self.shifts) != len(self.basis):
            raise ValueError("every free-module basis vector needs one shift")
        if _validate_variable_count(self.variable_count) != self.variable_count:
            raise ValueError("variable_count must be a nonnegative integer")
        if any(len(shift) != self.variable_count for shift in self.shifts):
            raise ValueError("free-module shifts must use the declared variable count")
        if self.scalar_type not in (Rational, Eisenstein):
            raise TypeError("free modules require Rational or Eisenstein coefficients")

    @property
    def rank(self) -> int:
        """Return the number of named free generators."""

        return len(self.basis)

    def direct_sum(
        self,
        other: PolynomialFreeModule,
        name: str | None = None,
    ) -> PolynomialFreeModule:
        """Return the ordered direct sum of two compatible free modules."""

        if self.variable_count != other.variable_count:
            raise ValueError("free modules use incompatible polynomial variables")
        if self.scalar_type is not other.scalar_type:
            raise TypeError("free modules use incompatible exact coefficient fields")
        prefix = name or f"{self.name}⊕{other.name}"
        return PolynomialFreeModule(
            prefix,
            tuple(f"left:{label}" for label in self.basis)
            + tuple(f"right:{label}" for label in other.basis),
            self.shifts + other.shifts,
            self.variable_count,
            self.scalar_type,
        )


@dataclass(frozen=True, slots=True, init=False)
class PolynomialMap:
    """An exact polynomial-valued map between named free modules."""

    domain: PolynomialFreeModule
    codomain: PolynomialFreeModule
    matrix: PolynomialMatrix

    def __init__(
        self,
        domain: PolynomialFreeModule,
        codomain: PolynomialFreeModule,
        matrix: PolynomialMatrix,
    ) -> None:
        if matrix.shape != (codomain.rank, domain.rank):
            raise ValueError("polynomial map matrix shape does not match its modules")
        if matrix.variable_count != domain.variable_count:
            raise ValueError("polynomial map variables do not match its modules")
        if matrix.scalar_type is not domain.scalar_type:
            raise TypeError("polynomial map coefficients do not match its modules")
        if codomain.variable_count != domain.variable_count:
            raise ValueError("polynomial map modules use incompatible variables")
        if codomain.scalar_type is not domain.scalar_type:
            raise TypeError("polynomial map modules use incompatible coefficient fields")
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "codomain", codomain)
        object.__setattr__(self, "matrix", matrix)

    @classmethod
    def zero(cls, domain: PolynomialFreeModule, codomain: PolynomialFreeModule) -> PolynomialMap:
        """Construct the exact zero map between positive-rank modules."""

        zero = Polynomial.zero(domain.variable_count, scalar_type=domain.scalar_type)
        return cls(
            domain,
            codomain,
            PolynomialMatrix(tuple(tuple(zero for _ in domain.basis) for _ in codomain.basis)),
        )

    @classmethod
    def identity(cls, module: PolynomialFreeModule) -> PolynomialMap:
        """Construct the exact identity map in one named module basis."""

        one = Polynomial.one(module.variable_count, scalar_type=module.scalar_type)
        zero = Polynomial.zero(module.variable_count, scalar_type=module.scalar_type)
        return cls(
            module,
            module,
            PolynomialMatrix(
                tuple(
                    tuple(one if row == column else zero for column in range(module.rank))
                    for row in range(module.rank)
                )
            ),
        )

    @classmethod
    def block(cls, blocks: Sequence[Sequence[PolynomialMap]]) -> PolynomialMap:
        """Assemble a complete rectangular block map over compatible modules."""

        if not blocks or not blocks[0] or any(len(row) != len(blocks[0]) for row in blocks):
            raise ValueError("a polynomial block map must be nonempty and rectangular")
        column_domains = tuple(blocks[0][column].domain for column in range(len(blocks[0])))
        row_codomains = tuple(blocks[row][0].codomain for row in range(len(blocks)))
        for row_index, row in enumerate(blocks):
            for column_index, block in enumerate(row):
                if block.domain != column_domains[column_index]:
                    raise ValueError("polynomial block domains are incompatible")
                if block.codomain != row_codomains[row_index]:
                    raise ValueError("polynomial block codomains are incompatible")
        rows: list[tuple[Polynomial, ...]] = []
        for block_row, codomain in zip(blocks, row_codomains, strict=True):
            for local_row in range(codomain.rank):
                rows.append(
                    tuple(
                        entry
                        for block in block_row
                        for entry in block.matrix.rows[local_row]
                    )
                )
        domain = column_domains[0]
        for component in column_domains[1:]:
            domain = domain.direct_sum(component)
        codomain = row_codomains[0]
        for component in row_codomains[1:]:
            codomain = codomain.direct_sum(component)
        return cls(domain, codomain, PolynomialMatrix(rows))

    def compose(self, previous: PolynomialMap) -> PolynomialMap:
        """Compose this map after a compatible exact polynomial map."""

        if previous.codomain != self.domain:
            raise ValueError("polynomial maps require matching named modules")
        return PolynomialMap(
            previous.domain,
            self.codomain,
            self.matrix.compose(previous.matrix),
        )

    def scale(self, scalar: object) -> PolynomialMap:
        """Scale every matrix entry by one exact coefficient."""

        return PolynomialMap(
            self.domain,
            self.codomain,
            PolynomialMatrix(
                tuple(
                    tuple(entry.scale(scalar) for entry in row)
                    for row in self.matrix.rows
                )
            ),
        )

    def __neg__(self) -> PolynomialMap:
        """Return the exact additive inverse map."""

        return self.scale(-1)

    def is_zero(self) -> bool:
        """Return whether every entry of the map vanishes exactly."""

        return self.matrix.is_zero()


@dataclass(frozen=True, slots=True, init=False)
class PolynomialChainComplex:
    """A finite chain complex of positive-rank polynomial free modules."""

    modules: tuple[tuple[int, PolynomialFreeModule], ...]
    differentials: tuple[tuple[int, PolynomialMap], ...]

    def __init__(
        self,
        modules: Mapping[int, PolynomialFreeModule]
        | Iterable[tuple[int, PolynomialFreeModule]],
        differentials: Mapping[int, PolynomialMap]
        | Iterable[tuple[int, PolynomialMap]],
    ) -> None:
        module_pairs = tuple(sorted(modules.items() if isinstance(modules, Mapping) else modules))
        differential_pairs = tuple(
            sorted(differentials.items() if isinstance(differentials, Mapping) else differentials)
        )
        module_map = dict(module_pairs)
        if not module_pairs or len(module_map) != len(module_pairs):
            raise ValueError("polynomial complexes require unique nonempty terms")
        if len(dict(differential_pairs)) != len(differential_pairs):
            raise ValueError("polynomial differentials require unique source degrees")
        for degree, differential in differential_pairs:
            if module_map.get(degree) != differential.domain:
                raise ValueError("polynomial differential domain does not match its term")
            if module_map.get(degree - 1) != differential.codomain:
                raise ValueError("polynomial differential codomain does not match its term")
        object.__setattr__(self, "modules", module_pairs)
        object.__setattr__(self, "differentials", differential_pairs)
        differential_map = dict(differential_pairs)
        for degree, differential in differential_pairs:
            previous = differential_map.get(degree - 1)
            if previous is not None and not previous.compose(differential).is_zero():
                raise ValueError("polynomial complex differentials must square to zero")

    @property
    def degrees(self) -> tuple[int, ...]:
        """Return the ordered degrees of the free-module terms."""

        return tuple(degree for degree, _ in self.modules)

    def module(self, degree: int) -> PolynomialFreeModule:
        """Return one named term module."""

        try:
            return dict(self.modules)[degree]
        except KeyError as error:
            raise KeyError(f"polynomial complex has no degree {degree}") from error

    @property
    def squared_zero(self) -> bool:
        """Return the exact polynomial square-zero certificate."""

        differential_map = dict(self.differentials)
        return all(
            degree - 1 not in differential_map
            or differential_map[degree - 1].compose(differential).is_zero()
            for degree, differential in self.differentials
        )


@dataclass(frozen=True, slots=True, init=False)
class PolynomialChainMap:
    """A degree-preserving polynomial chain map with exact commutation."""

    source: PolynomialChainComplex
    target: PolynomialChainComplex
    components: tuple[tuple[int, PolynomialMap], ...]

    def __init__(
        self,
        source: PolynomialChainComplex,
        target: PolynomialChainComplex,
        components: Mapping[int, PolynomialMap]
        | Iterable[tuple[int, PolynomialMap]],
    ) -> None:
        if source.degrees != target.degrees:
            raise ValueError("polynomial chain maps require equal degree supports")
        pairs = tuple(sorted(components.items() if isinstance(components, Mapping) else components))
        if tuple(degree for degree, _ in pairs) != source.degrees:
            raise ValueError("polynomial chain maps require one component per degree")
        for degree, component in pairs:
            if component.domain != source.module(degree):
                raise ValueError("polynomial chain-map component has the wrong domain")
            if component.codomain != target.module(degree):
                raise ValueError("polynomial chain-map component has the wrong codomain")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "components", pairs)
        component_map = dict(pairs)
        source_differentials = dict(source.differentials)
        target_differentials = dict(target.differentials)
        for degree, differential in source_differentials.items():
            left = target_differentials[degree].compose(component_map[degree])
            right = component_map[degree - 1].compose(differential)
            if not (left.matrix == right.matrix):
                raise ValueError("polynomial chain-map components must commute exactly")

    def component(self, degree: int) -> PolynomialMap:
        """Return one exact degree component."""

        return dict(self.components)[degree]


def polynomial_mapping_cone(chain_map: PolynomialChainMap) -> PolynomialChainComplex:
    """Construct the exact two-term mapping cone of a polynomial chain map."""

    if chain_map.source.degrees != (0, 1) or chain_map.target.degrees != (0, 1):
        raise ValueError("the polynomial mapping-cone helper currently requires degrees 0 and 1")
    source_differential = dict(chain_map.source.differentials)[1]
    target_differential = dict(chain_map.target.differentials)[1]
    source_one = chain_map.source.module(1)
    target_one = chain_map.target.module(1)
    target_zero = chain_map.target.module(0)
    source_zero = chain_map.source.module(0)
    cone_one = target_one.direct_sum(source_zero)
    differential_one = PolynomialMap.block((
        (
            target_differential,
            chain_map.component(0),
        ),
    ))
    negative_source_differential = PolynomialMap(
        source_one,
        source_zero,
        PolynomialMatrix(
            tuple(
                tuple(entry.scale(-1) for entry in row)
                for row in source_differential.matrix.rows
            )
        ),
    )
    differential_two = PolynomialMap.block((
        (chain_map.component(1),),
        (negative_source_differential,),
    ))
    return PolynomialChainComplex(
        {0: target_zero, 1: cone_one, 2: source_one},
        {1: differential_one, 2: differential_two},
    )


@dataclass(frozen=True, slots=True, init=False)
class PolynomialFreeResolution:
    """A finite chain of free polynomial modules with exact square-zero checks."""

    name: str
    term_ranks: tuple[tuple[int, int], ...]
    differentials: tuple[tuple[int, PolynomialMatrix], ...]

    def __init__(
        self,
        name: str,
        term_ranks: Mapping[int, int] | Iterable[tuple[int, int]],
        differentials: Mapping[int, PolynomialMatrix]
        | Iterable[tuple[int, PolynomialMatrix]],
    ) -> None:
        ranks = tuple(sorted(term_ranks.items() if isinstance(term_ranks, Mapping) else term_ranks))
        maps = tuple(
            sorted(differentials.items() if isinstance(differentials, Mapping) else differentials)
        )
        if not name.strip() or not ranks:
            raise ValueError("free resolutions require a name and nonempty term ranks")
        if len({degree for degree, _ in ranks}) != len(ranks):
            raise ValueError("free-resolution degrees must be unique")
        if any(rank < 0 for _, rank in ranks):
            raise ValueError("free-resolution ranks must be nonnegative")
        rank_map = dict(ranks)
        if len({degree for degree, _ in maps}) != len(maps):
            raise ValueError("free-resolution differential degrees must be unique")
        for degree, differential in maps:
            if (
                rank_map.get(degree) != differential.shape[1]
                or rank_map.get(degree - 1) != differential.shape[0]
            ):
                raise ValueError("free-resolution differential ranks do not match its terms")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "term_ranks", ranks)
        object.__setattr__(self, "differentials", maps)
        for degree, differential in maps:
            next_map = dict(maps).get(degree - 1)
            if next_map is not None and not next_map.compose(differential).is_zero():
                raise ValueError("free-resolution differentials must square to zero")

    @property
    def squared_zero(self) -> bool:
        """Return the exact chain-complex square-zero certificate."""

        maps = dict(self.differentials)
        return all(
            degree - 1 not in maps or maps[degree - 1].compose(differential).is_zero()
            for degree, differential in self.differentials
        )


def polynomial_determinant(matrix: Iterable[Iterable[Polynomial]]) -> Polynomial:
    """Return the exact determinant of a nonempty square polynomial matrix."""

    rows = _matrix_rows(matrix)
    size = len(rows)
    if len(rows[0]) != size:
        raise ValueError("polynomial determinant requires a nonempty square matrix")
    if size == 1:
        return rows[0][0]
    zero = Polynomial.zero(rows[0][0].variable_count, scalar_type=rows[0][0].scalar_type)
    result = zero
    for column in range(size):
        minor = tuple(
            tuple(entry for index, entry in enumerate(row) if index != column)
            for row in rows[1:]
        )
        term = rows[0][column] * polynomial_determinant(minor)
        result = result + (term if column % 2 == 0 else -term)
    return result


def maximal_minors(matrix: Iterable[Iterable[Polynomial]]) -> tuple[Polynomial, ...]:
    """Return all maximal row minors of a polynomial matrix."""

    rows = _matrix_rows(matrix)
    row_count, column_count = len(rows), len(rows[0])
    if row_count < column_count:
        raise ValueError("maximal minors require at least as many rows as columns")
    if row_count == column_count + 1:
        row_sets = tuple(
            tuple(index for index in range(row_count) if index != removed)
            for removed in range(row_count)
        )
    else:
        row_sets = tuple(combinations(range(row_count), column_count))
    return tuple(
        polynomial_determinant(
            tuple(tuple(rows[row][column] for column in range(column_count)) for row in row_set)
        )
        for row_set in row_sets
    )


def _matrix_rows(matrix: Iterable[Iterable[Polynomial]]) -> tuple[tuple[Polynomial, ...], ...]:
    rows = tuple(tuple(row) for row in matrix)
    if not rows or not rows[0]:
        raise ValueError("polynomial matrix must be nonempty and rectangular")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("polynomial matrix must be rectangular")
    first = rows[0][0]
    for row in rows:
        for entry in row:
            if entry.variable_count != first.variable_count:
                raise ValueError("polynomial matrix variable counts do not agree")
            if entry.scalar_type is not first.scalar_type:
                raise TypeError("polynomial matrix scalar types do not agree")
    return rows


def determinant(matrix: Iterable[Iterable[Polynomial]]) -> Polynomial:
    """Return a polynomial-matrix determinant."""

    return polynomial_determinant(matrix)


def derivative(polynomial: Polynomial, variable: int = 0) -> Polynomial:
    """Return an exact formal derivative."""

    return polynomial.derivative(variable)


def substitute(polynomial: Polynomial, images: Sequence[object]) -> Polynomial:
    """Substitute exact scalar or polynomial images for every variable."""

    return polynomial.substitute(images)


def divmod_univariate(
    dividend: Polynomial,
    divisor: Polynomial,
) -> tuple[Polynomial, Polynomial]:
    """Return exact quotient and remainder for univariate division."""

    return dividend.divmod_univariate(divisor)


def gcd(left: Polynomial, right: Polynomial) -> Polynomial:
    """Return the monic exact greatest common divisor of two univariates."""

    return left.gcd(right)


def monic(polynomial: Polynomial) -> Polynomial:
    """Return the monic normalization of a nonzero univariate polynomial."""

    return polynomial.monic()


def substitute_monomials(
    polynomial: Polynomial,
    images: Sequence[tuple[object, Iterable[int]]],
) -> Polynomial:
    """Substitute exact scalar multiples of target monomials."""

    return polynomial.substitute_monomials(images)


__all__ = [
    "Monomial",
    "Polynomial",
    "PolynomialChainComplex",
    "PolynomialChainMap",
    "PolynomialFreeResolution",
    "PolynomialFreeModule",
    "PolynomialMap",
    "PolynomialMatrix",
    "derivative",
    "determinant",
    "divmod_univariate",
    "gcd",
    "maximal_minors",
    "monic",
    "polynomial_determinant",
    "polynomial_mapping_cone",
    "substitute",
    "substitute_monomials",
]
