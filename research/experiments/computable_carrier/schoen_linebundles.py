"""Compute exact line-bundle cohomology on the Schoen cover.

Owns:
    Künneth bases on ``P2_x x P2_u x P1``, multiplication by the two fixed
    Schoen equations, and the signed two-equation Koszul complexes computing
    restricted line-bundle cohomology on the complete-intersection cover.

Depends on:
    Exact Eisenstein polynomials, basis-aware cochain maps, and the published
    Schoen cubic pencil. This is a research calculation on the cover.

Must not:
    Treat a line-bundle complex as bundle-valued physics, infer quotient
    invariants without an explicit deck action, or import observations.

Phase 0:
    Exact cover line-bundle cohomology is available; outer Ext comparison,
    quotient descent, stability, and physical promotion remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from itertools import product

from onetheory.math.homological import (
    ChainMap,
    CochainComplex,
    GradedVectorSpace,
    LinearMap,
    VectorSpace,
)
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry

Monomial = tuple[int, ...]
Factor = str
_FACTORS = ("x", "u", "p")
_KOSZUL_TOTAL_DEGREES = tuple(range(-2, 6))
_KOSZUL_DIFFERENTIAL_DEGREES = tuple(range(-2, 5))


@cache
def _p2_basis(degree: int, cohomology_degree: int) -> tuple[Monomial, ...]:
    """Return the monomial basis of one exact P2 cohomology group."""

    if cohomology_degree == 0 and degree >= 0:
        return tuple(
            exponents
            for exponents in product(range(degree + 1), repeat=3)
            if sum(exponents) == degree
        )
    if cohomology_degree == 2 and degree <= -3:
        return tuple(
            exponents
            for exponents in product(range(degree, 0), repeat=3)
            if sum(exponents) == degree
        )
    return ()


@cache
def _p1_basis(degree: int, cohomology_degree: int) -> tuple[Monomial, ...]:
    """Return the monomial basis of one exact P1 cohomology group."""

    if cohomology_degree == 0 and degree >= 0:
        return tuple(
            exponents
            for exponents in product(range(degree + 1), repeat=2)
            if sum(exponents) == degree
        )
    if cohomology_degree == 1 and degree <= -2:
        return tuple(
            exponents
            for exponents in product(range(degree, 0), repeat=2)
            if sum(exponents) == degree
        )
    return ()


def _dual_monomial(monomial: Monomial) -> Monomial:
    """Return the Serre-dual monomial index."""

    return tuple(-value - 1 for value in monomial)


@cache
def _factor_basis(
    factor: Factor,
    degree: int,
    cohomology_degree: int,
) -> tuple[Monomial, ...]:
    """Return one factor's exact cohomology basis."""

    if factor in ("x", "u"):
        return _p2_basis(degree, cohomology_degree)
    if factor == "p":
        return _p1_basis(degree, cohomology_degree)
    raise ValueError(f"unknown Schoen ambient factor: {factor}")


@cache
def _factor_matrix(
    factor: Factor,
    source_degree: int,
    target_degree: int,
    cohomology_degree: int,
    polynomial_terms: tuple[tuple[Monomial, Eisenstein], ...],
) -> tuple[tuple[Monomial, ...], tuple[tuple[Eisenstein, ...], ...]]:
    """Return exact multiplication rows in factor monomial bases."""

    source_basis = _factor_basis(factor, source_degree, cohomology_degree)
    target_basis = _factor_basis(factor, target_degree, cohomology_degree)
    rows = [
        [Eisenstein(0) for _ in source_basis]
        for _ in target_basis
    ]
    if cohomology_degree == 0:
        target_indices = {
            monomial: index for index, monomial in enumerate(target_basis)
        }
        for source_index, source_monomial in enumerate(source_basis):
            for exponent, coefficient in polynomial_terms:
                image = tuple(
                    left + right
                    for left, right in zip(
                        source_monomial,
                        exponent,
                        strict=True,
                    )
                )
                target_index = target_indices.get(image)
                if target_index is not None:
                    rows[target_index][source_index] += coefficient
    elif cohomology_degree in (1, 2):
        source_dual = tuple(_dual_monomial(item) for item in source_basis)
        target_dual = tuple(_dual_monomial(item) for item in target_basis)
        source_indices = {
            monomial: index for index, monomial in enumerate(source_dual)
        }
        for target_index, target_monomial in enumerate(target_dual):
            for exponent, coefficient in polynomial_terms:
                image = tuple(
                    left + right
                    for left, right in zip(
                        target_monomial,
                        exponent,
                        strict=True,
                    )
                )
                source_index = source_indices.get(image)
                if source_index is not None:
                    rows[target_index][source_index] += coefficient
    else:
        raise ValueError("factor cohomology degree is outside the ambient range")
    return target_basis, tuple(tuple(row) for row in rows)


@dataclass(frozen=True, slots=True)
class AmbientSchoenSpace:
    """One explicitly Künneth-based ambient cohomology space."""

    degrees: tuple[int, int, int]
    cohomology_degree: int
    vector_space: VectorSpace
    labels: tuple[tuple[int, int, int, Monomial, Monomial, Monomial], ...]


@cache
def _ambient_space(
    degrees: tuple[int, int, int],
    cohomology_degree: int,
) -> AmbientSchoenSpace:
    """Build one ordered Künneth space on the three ambient factors."""

    x_degree, u_degree, p_degree = degrees
    records: list[
        tuple[
            int,
            int,
            int,
            tuple[Monomial, ...],
            tuple[Monomial, ...],
            tuple[Monomial, ...],
        ]
    ] = []
    for x_h, u_h, p_h in product((0, 2), (0, 2), (0, 1)):
        if x_h + u_h + p_h != cohomology_degree:
            continue
        x_basis = _factor_basis("x", x_degree, x_h)
        u_basis = _factor_basis("u", u_degree, u_h)
        p_basis = _factor_basis("p", p_degree, p_h)
        if x_basis and u_basis and p_basis:
            records.append((x_h, u_h, p_h, x_basis, u_basis, p_basis))
    labels = tuple(
        (x_h, u_h, p_h, x_monomial, u_monomial, p_monomial)
        for x_h, u_h, p_h, x_basis, u_basis, p_basis in records
        for x_monomial in x_basis
        for u_monomial in u_basis
        for p_monomial in p_basis
    )
    vector_space = VectorSpace(
        f"O({x_degree},{u_degree},{p_degree}):H^{cohomology_degree}",
        tuple(str(label) for label in labels),
        Eisenstein,
    )
    return AmbientSchoenSpace(degrees, cohomology_degree, vector_space, labels)


def _polynomial_terms(polynomial: Polynomial) -> tuple[tuple[Monomial, Eisenstein], ...]:
    """Coerce one exact polynomial's terms to the Schoen coefficient field."""

    if polynomial.variable_count != 3 or polynomial.scalar_type is not Eisenstein:
        raise TypeError("Schoen multiplication requires Eisenstein cubics in three variables")
    return tuple((exponents, coefficient) for exponents, coefficient in polynomial.terms)


def _ambient_multiplication(
    source: AmbientSchoenSpace,
    target: AmbientSchoenSpace,
    polynomial: Polynomial | None,
    factor: Factor | None,
) -> LinearMap:
    """Multiply one ambient cohomology space by a factor polynomial."""

    if polynomial is None:
        if source.degrees != target.degrees or source.cohomology_degree != target.cohomology_degree:
            raise ValueError("identity multiplication requires matching ambient degrees")
        factor_terms = (((0, 0, 0), Eisenstein(1)),)
        factor = "scalar"
    else:
        if polynomial.is_zero():
            return LinearMap.zero(source.vector_space, target.vector_space)
        if factor not in ("x", "u", "p"):
            raise ValueError("nonzero ambient multiplication requires x, u, or p")
        factor_terms = _polynomial_terms(polynomial)
    target_indices = {label: index for index, label in enumerate(target.labels)}
    rows = [[Eisenstein(0) for _ in source.labels] for _ in target.labels]
    source_factor_degrees = source.degrees
    target_factor_degrees = target.degrees
    factor_position = {"x": 0, "u": 1, "p": 2}.get(factor)
    local_data = {}
    for x_h, u_h, p_h in {
        (label[0], label[1], label[2]) for label in source.labels
    }:
        cohomology = (x_h, u_h, p_h)
        if factor == "scalar":
            local_data[(x_h, u_h, p_h)] = (
                ((0, 0, 0),),
                ((Eisenstein(1),),),
            )
            continue
        assert factor_position is not None
        local_data[(x_h, u_h, p_h)] = _factor_matrix(
            factor,
            source_factor_degrees[factor_position],
            target_factor_degrees[factor_position],
            cohomology[factor_position],
            factor_terms,
        )
    for source_index, label in enumerate(source.labels):
        x_h, u_h, p_h, x_monomial, u_monomial, p_monomial = label
        cohomology = (x_h, u_h, p_h)
        factor_basis, factor_rows = local_data[(x_h, u_h, p_h)]
        source_factor_basis = (
            ((0, 0, 0),)
            if factor == "scalar"
            else _factor_basis(
                factor,
                source_factor_degrees[factor_position],
                cohomology[factor_position],
            )
        )
        local_source = (
            (x_monomial, u_monomial, p_monomial)[factor_position]
            if factor_position is not None
            else (0, 0, 0)
        )
        try:
            source_local_index = source_factor_basis.index(local_source)
        except ValueError as error:
            raise ValueError("ambient label is outside its factor basis") from error
        for target_local_index, target_monomial in enumerate(factor_basis):
            coefficient = factor_rows[target_local_index][source_local_index]
            if coefficient.is_zero():
                continue
            target_label = (
                x_h,
                u_h,
                p_h,
                target_monomial if factor == "x" else x_monomial,
                target_monomial if factor == "u" else u_monomial,
                target_monomial if factor == "p" else p_monomial,
            )
            target_index = target_indices.get(target_label)
            if target_index is None:
                raise ValueError("ambient multiplication escaped the target Künneth basis")
            rows[target_index][source_index] += coefficient
    return LinearMap(source.vector_space, target.vector_space, rows)


def _equation_one(
    source_degrees: tuple[int, int, int],
    target_degrees: tuple[int, int, int],
    cohomology_degree: int,
) -> LinearMap:
    """Multiply by ``mu F(x) + nu G(x)`` exactly."""

    cox = schoen_geometry().cover.cox
    source = _ambient_space(source_degrees, cohomology_degree)
    target = _ambient_space(target_degrees, cohomology_degree)
    mu = Polynomial.monomial((1, 0), scalar_type=Eisenstein)
    nu = Polynomial.monomial((0, 1), scalar_type=Eisenstein)
    # The ambient map is represented by a tensor product. Since the compact
    # polynomial type has one variable count, build the three factors here.
    return _sum_tensor_equation(
        source,
        target,
        ((cox.cubic_f, "x", mu, "p"), (cox.cubic_g, "x", nu, "p")),
    )


def _equation_two(
    source_degrees: tuple[int, int, int],
    target_degrees: tuple[int, int, int],
    cohomology_degree: int,
) -> LinearMap:
    """Multiply by ``2 nu F(u) + mu G(u)`` exactly."""

    cox = schoen_geometry().cover.cox
    source = _ambient_space(source_degrees, cohomology_degree)
    target = _ambient_space(target_degrees, cohomology_degree)
    mu = Polynomial.monomial((1, 0), scalar_type=Eisenstein)
    nu = Polynomial.monomial((0, 1), scalar_type=Eisenstein)
    return _sum_tensor_equation(
        source,
        target,
        ((cox.cubic_f.scale(2), "u", nu, "p"), (cox.cubic_g, "u", mu, "p")),
    )


@cache
def _factor_matrix_for_terms(
    factor: Factor,
    source_degree: int,
    target_degree: int,
    cohomology_degree: int,
    polynomial: Polynomial,
) -> tuple[tuple[Monomial, ...], tuple[tuple[Eisenstein, ...], ...]]:
    """Return a factor matrix after validating its variable convention."""

    if factor == "p":
        if polynomial.variable_count != 2:
            raise ValueError("P1 forms use two variables")
        if polynomial.scalar_type is not Eisenstein:
            raise TypeError("P1 forms require Eisenstein coefficients")
        terms = tuple(
            (exponents, coefficient)
            for exponents, coefficient in polynomial.terms
        )
        return _factor_matrix(
            factor,
            source_degree,
            target_degree,
            cohomology_degree,
            terms,
        )
    return _factor_matrix(
        factor,
        source_degree,
        target_degree,
        cohomology_degree,
        _polynomial_terms(polynomial),
    )


def _sum_tensor_equation(
    source: AmbientSchoenSpace,
    target: AmbientSchoenSpace,
    terms: tuple[tuple[Polynomial, Factor, Polynomial, Factor], ...],
) -> LinearMap:
    """Assemble sums of separated factor multiplications."""

    target_indices = {label: index for index, label in enumerate(target.labels)}
    rows = [
        [Eisenstein(0) for _ in source.labels]
        for _ in target.labels
    ]
    for polynomial, polynomial_factor, fiber_form, fiber_factor in terms:
        factor_position = {"x": 0, "u": 1}[polynomial_factor]
        local_data = {}
        for x_h, u_h, p_h in {
            (label[0], label[1], label[2]) for label in source.labels
        }:
            h = (x_h, u_h, p_h)
            polynomial_basis, polynomial_rows = _factor_matrix_for_terms(
                polynomial_factor,
                source.degrees[factor_position],
                target.degrees[factor_position],
                h[factor_position],
                polynomial,
            )
            fiber_basis, fiber_rows = _factor_matrix_for_terms(
                fiber_factor,
                source.degrees[2],
                target.degrees[2],
                p_h,
                fiber_form,
            )
            local_data[h] = (
                polynomial_basis,
                polynomial_rows,
                fiber_basis,
                fiber_rows,
            )
        for source_index, label in enumerate(source.labels):
            x_h, u_h, p_h, x_monomial, u_monomial, p_monomial = label
            (
                polynomial_basis,
                polynomial_rows,
                fiber_basis,
                fiber_rows,
            ) = local_data[(x_h, u_h, p_h)]
            polynomial_source = _factor_basis(
                polynomial_factor,
                source.degrees[factor_position],
                h[factor_position],
            ).index((x_monomial, u_monomial)[factor_position])
            fiber_source = _factor_basis("p", source.degrees[2], p_h).index(p_monomial)
            for polynomial_target, polynomial_monomial in enumerate(polynomial_basis):
                first = polynomial_rows[polynomial_target][polynomial_source]
                if first.is_zero():
                    continue
                for fiber_target, fiber_monomial in enumerate(fiber_basis):
                    coefficient = first * fiber_rows[fiber_target][fiber_source]
                    if coefficient.is_zero():
                        continue
                    target_label = (
                        x_h,
                        u_h,
                        p_h,
                        polynomial_monomial if polynomial_factor == "x" else x_monomial,
                        polynomial_monomial if polynomial_factor == "u" else u_monomial,
                        fiber_monomial,
                    )
                    target_index = target_indices.get(target_label)
                    if target_index is None:
                        raise ValueError("equation multiplication escaped the Künneth basis")
                    rows[target_index][source_index] += coefficient
    return LinearMap(source.vector_space, target.vector_space, rows)


@dataclass(frozen=True, slots=True)
class SchoenAmbientLineBundle:
    """Exact ambient Künneth cohomology for ``O(a,b,c)``."""

    degrees: tuple[int, int, int]
    spaces: tuple[tuple[int, AmbientSchoenSpace], ...]

    def space(self, degree: int) -> AmbientSchoenSpace:
        """Return one ambient cohomology space."""

        for current, space in self.spaces:
            if current == degree:
                return space
        return _ambient_space(self.degrees, degree)


@cache
def ambient_schoen_line_bundle(
    x_degree: int,
    u_degree: int,
    p_degree: int,
) -> SchoenAmbientLineBundle:
    """Construct all finite ambient Künneth spaces for one line bundle."""

    degrees = (x_degree, u_degree, p_degree)
    return SchoenAmbientLineBundle(
        degrees,
        tuple((degree, _ambient_space(degrees, degree)) for degree in range(6)),
    )


@dataclass(frozen=True, slots=True)
class SchoenLineBundle:
    """Exact Koszul cochain model for ``O_X(a,b,c)`` on the cover."""

    degrees: tuple[int, int, int]
    ambient_k0: SchoenAmbientLineBundle
    ambient_k1_x: SchoenAmbientLineBundle
    ambient_k1_u: SchoenAmbientLineBundle
    ambient_k2: SchoenAmbientLineBundle
    complex: CochainComplex

    @property
    def cohomology_dimensions(self) -> tuple[tuple[int, int], ...]:
        """Return exact restricted line-bundle dimensions."""

        return tuple(
            (degree, self.complex.cohomology_dimension(degree))
            for degree in range(4)
        )

    @property
    def squared_zero(self) -> bool:
        """Return the exact two-equation Koszul square-zero certificate."""

        return all(
            self.complex.differential(degree + 1).compose(
                self.complex.differential(degree)
            ).is_zero()
            for degree in self.complex.degrees
        )

    def multiplication(
        self,
        target: SchoenLineBundle,
        polynomial: Polynomial,
        factor: Factor,
    ) -> ChainMap:
        """Return multiplication by an x- or u-factor polynomial."""

        if polynomial.is_zero():
            return ChainMap(
                self.complex,
                target.complex,
                {
                    degree: LinearMap.zero(
                        self.complex.spaces.space(degree),
                        target.complex.spaces.space(degree),
                    )
                    for degree in self.complex.degrees
                },
            )
        if factor not in ("x", "u"):
            raise ValueError("line-bundle multiplication accepts x or u polynomials")
        position = {"x": 0, "u": 1}[factor]
        expected = list(self.degrees)
        expected[position] += polynomial.degree
        if tuple(expected) != target.degrees:
            raise ValueError("factor polynomial degree does not match Schoen line bundles")
        components: dict[int, LinearMap] = {}
        for degree in self.complex.degrees:
            source_blocks = (
                self.ambient_k0.space(degree),
                self.ambient_k1_x.space(degree + 1),
                self.ambient_k1_u.space(degree + 1),
                self.ambient_k2.space(degree + 2),
            )
            target_blocks = (
                target.ambient_k0.space(degree),
                target.ambient_k1_x.space(degree + 1),
                target.ambient_k1_u.space(degree + 1),
                target.ambient_k2.space(degree + 2),
            )
            blocks = []
            for source_block, target_block in zip(source_blocks, target_blocks, strict=True):
                blocks.append(
                    _ambient_multiplication(
                        source_block,
                        target_block,
                        polynomial,
                        factor,
                    )
                )
            components[degree] = LinearMap.block(
                tuple(
                    tuple(
                        block if row == column else LinearMap.zero(
                            source_blocks[column].vector_space,
                            target_blocks[row].vector_space,
                        )
                        for column, block in enumerate(blocks)
                    )
                    for row in range(4)
                )
            )
        return ChainMap(self.complex, target.complex, components)


def _line_bundle_space(
    ambient_k0: SchoenAmbientLineBundle,
    ambient_k1_x: SchoenAmbientLineBundle,
    ambient_k1_u: SchoenAmbientLineBundle,
    ambient_k2: SchoenAmbientLineBundle,
    degree: int,
) -> VectorSpace:
    """Build the ordered four-block Koszul space in one cohomology degree."""

    blocks = (
        ambient_k0.space(degree).vector_space,
        ambient_k1_x.space(degree + 1).vector_space,
        ambient_k1_u.space(degree + 1).vector_space,
        ambient_k2.space(degree + 2).vector_space,
    )
    result = blocks[0]
    for block in blocks[1:]:
        result = result.direct_sum(block)
    return result


@cache
def schoen_line_bundle(
    x_degree: int,
    u_degree: int,
    p_degree: int,
) -> SchoenLineBundle:
    """Construct the exact restricted Koszul complex for ``O_X(a,b,c)``."""

    degrees = (x_degree, u_degree, p_degree)
    k0 = ambient_schoen_line_bundle(*degrees)
    k1_x = ambient_schoen_line_bundle(x_degree - 3, u_degree, p_degree - 1)
    k1_u = ambient_schoen_line_bundle(x_degree, u_degree - 3, p_degree - 1)
    k2 = ambient_schoen_line_bundle(x_degree - 3, u_degree - 3, p_degree - 2)
    spaces = {
        degree: _line_bundle_space(
            k0,
            k1_x,
            k1_u,
            k2,
            degree,
        )
        for degree in _KOSZUL_TOTAL_DEGREES
    }
    graded = GradedVectorSpace(f"O_X({x_degree},{u_degree},{p_degree})", spaces)
    differentials: dict[int, LinearMap] = {}
    for degree in _KOSZUL_DIFFERENTIAL_DEGREES:
        k0_source = k0.space(degree).vector_space
        k1_x_source = k1_x.space(degree + 1).vector_space
        k1_u_source = k1_u.space(degree + 1).vector_space
        k2_source = k2.space(degree + 2).vector_space
        k0_target = k0.space(degree + 1).vector_space
        k1_x_target = k1_x.space(degree + 2).vector_space
        k1_u_target = k1_u.space(degree + 2).vector_space
        k2_target = k2.space(degree + 3).vector_space
        def zero(domain: VectorSpace, codomain: VectorSpace) -> LinearMap:
            """Construct one typed zero block."""

            return LinearMap.zero(domain, codomain)
        equation_one = _equation_one(
            k1_x.space(degree + 1).degrees,
            k0.space(degree + 1).degrees,
            degree + 1,
        )
        equation_two = _equation_two(
            k1_u.space(degree + 1).degrees,
            k0.space(degree + 1).degrees,
            degree + 1,
        )
        equation_two_from_k2 = _equation_two(
            k2.space(degree + 2).degrees,
            k1_x.space(degree + 2).degrees,
            degree + 2,
        )
        equation_one_from_k2 = _equation_one(
            k2.space(degree + 2).degrees,
            k1_u.space(degree + 2).degrees,
            degree + 2,
        )
        differentials[degree] = LinearMap.block(
            (
                (
                    zero(k0_source, k0_target),
                    equation_one,
                    equation_two,
                    zero(k2_source, k0_target),
                ),
                (
                    zero(k0_source, k1_x_target),
                    zero(k1_x_source, k1_x_target),
                    zero(k1_u_source, k1_x_target),
                    -equation_two_from_k2,
                ),
                (
                    zero(k0_source, k1_u_target),
                    zero(k1_x_source, k1_u_target),
                    zero(k1_u_source, k1_u_target),
                    equation_one_from_k2,
                ),
                (
                    zero(k0_source, k2_target),
                    zero(k1_x_source, k2_target),
                    zero(k1_u_source, k2_target),
                    zero(k2_source, k2_target),
                ),
            )
        )
    provisional = SchoenLineBundle(
        degrees,
        k0,
        k1_x,
        k1_u,
        k2,
        CochainComplex(graded, differentials),
    )
    return provisional


__all__ = [
    "AmbientSchoenSpace",
    "SchoenAmbientLineBundle",
    "SchoenLineBundle",
    "ambient_schoen_line_bundle",
    "schoen_line_bundle",
]
