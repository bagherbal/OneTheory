"""Exact line-bundle cohomology on the cubic-pencil dP9 hypersurface.

Owns:
    Kunneth bases on ``P2 x P1``, multiplication by the two frozen cubics,
    the bidegree-(3,1) Koszul map, and exact restricted line-bundle complexes
    on the dP9 hypersurface.

Depends on:
    Exact Eisenstein polynomial arithmetic, the generic cochain engine, and
    the frozen Schoen cubic pencil. It is independent of bundle physics.

Must not:
    Infer a Serre constituent, quotient descent, stability, or a physical
    spectrum from line-bundle cohomology alone.

Phase 0:
    Arbitrary integral base and fiber line-bundle twists have exact finite
    cohomology complexes; bundle-valued promotion remains outside this module.
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
FactorLabel = tuple[int, ...]
KunnethLabel = tuple[Monomial, Monomial]

DP9_TOTAL_DEGREES = tuple(range(-1, 4))
DP9_DIFFERENTIAL_DEGREES = tuple(range(-1, 3))
DP9_COHOMOLOGY_DEGREES = tuple(range(3))


def _p2_basis(degree: int, cohomology_degree: int) -> tuple[Monomial, ...]:
    """Return the exact monomial basis of one P2 line-bundle cohomology."""

    if cohomology_degree == 0 and degree >= 0:
        return tuple(
            exponent
            for exponent in product(range(degree + 1), repeat=3)
            if sum(exponent) == degree
        )
    if cohomology_degree == 2 and degree <= -3:
        return tuple(
            exponent
            for exponent in product(range(degree, 0), repeat=3)
            if sum(exponent) == degree
        )
    return ()


def _p1_basis(degree: int, cohomology_degree: int) -> tuple[Monomial, ...]:
    """Return the exact monomial basis of one P1 line-bundle cohomology."""

    if cohomology_degree == 0 and degree >= 0:
        return tuple(
            exponent
            for exponent in product(range(degree + 1), repeat=2)
            if sum(exponent) == degree
        )
    if cohomology_degree == 1 and degree <= -2:
        return tuple(
            exponent
            for exponent in product(range(degree, 0), repeat=2)
            if sum(exponent) == degree
        )
    return ()


def _dual_monomial(monomial: Monomial) -> Monomial:
    """Return the Serre-dual monomial index for a negative basis monomial."""

    return tuple(-value - 1 for value in monomial)


def _factor_space(
    name: str,
    basis: tuple[Monomial, ...],
) -> VectorSpace:
    """Create one exact factor space with deterministic monomial labels."""

    return VectorSpace(name, tuple(str(item) for item in basis), Eisenstein)


def _factor_multiplication(
    source_degree: int,
    target_degree: int,
    source_cohomology_degree: int,
    target_cohomology_degree: int,
    source_basis: tuple[Monomial, ...],
    target_basis: tuple[Monomial, ...],
    terms: tuple[tuple[Monomial, Eisenstein], ...],
    prefix: str,
) -> LinearMap:
    """Build multiplication on H0 or its exact Serre-dual top group."""

    source_space = _factor_space(
        f"{prefix}:O({source_degree}):H^{source_cohomology_degree}",
        source_basis,
    )
    target_space = _factor_space(
        f"{prefix}:O({target_degree}):H^{target_cohomology_degree}",
        target_basis,
    )
    rows = [
        [Eisenstein(0) for _ in source_basis]
        for _ in target_basis
    ]
    if source_cohomology_degree == 0:
        target_index = {monomial: index for index, monomial in enumerate(target_basis)}
        for source_index, source_monomial in enumerate(source_basis):
            for exponent, coefficient in terms:
                image = tuple(
                    left + right
                    for left, right in zip(source_monomial, exponent, strict=True)
                )
                target_index_value = target_index.get(image)
                if target_index_value is not None:
                    rows[target_index_value][source_index] += coefficient
    elif source_cohomology_degree in (1, 2):
        source_dual = tuple(_dual_monomial(item) for item in source_basis)
        target_dual = tuple(_dual_monomial(item) for item in target_basis)
        source_dual_index = {monomial: index for index, monomial in enumerate(source_dual)}
        for target_index, target_monomial in enumerate(target_dual):
            for exponent, coefficient in terms:
                image = tuple(
                    left + right
                    for left, right in zip(target_monomial, exponent, strict=True)
                )
                source_index = source_dual_index.get(image)
                if source_index is not None:
                    rows[target_index][source_index] += coefficient
    else:
        raise ValueError("factor multiplication supports H0, H1, and H2 only")
    return LinearMap(source_space, target_space, rows)


def _p2_multiplication(
    source_degree: int,
    target_degree: int,
    cohomology_degree: int,
    polynomial: Polynomial,
) -> LinearMap:
    """Multiply one P2 cohomology factor by a homogeneous polynomial."""

    source_basis = _p2_basis(source_degree, cohomology_degree)
    target_basis = _p2_basis(target_degree, cohomology_degree)
    terms = tuple(
        (exponents, coefficient)
        for exponents, coefficient in polynomial.terms
    )
    return _factor_multiplication(
        source_degree,
        target_degree,
        cohomology_degree,
        cohomology_degree,
        source_basis,
        target_basis,
        terms,
        "P2",
    )


def _p1_multiplication(
    source_degree: int,
    target_degree: int,
    cohomology_degree: int,
    terms: tuple[tuple[Monomial, Eisenstein], ...],
) -> LinearMap:
    """Multiply one P1 cohomology factor by a homogeneous linear form."""

    return _factor_multiplication(
        source_degree,
        target_degree,
        cohomology_degree,
        cohomology_degree,
        _p1_basis(source_degree, cohomology_degree),
        _p1_basis(target_degree, cohomology_degree),
        terms,
        "P1",
    )


def _kunneth_space(
    base_degree: int,
    fiber_degree: int,
    total_degree: int,
) -> tuple[VectorSpace, tuple[tuple[int, int, tuple[Monomial, ...], tuple[Monomial, ...]], ...]]:
    """Build one total Kunneth space and retain its factor basis records."""

    records = []
    for base_cohomology_degree, fiber_cohomology_degree in ((0, 0), (0, 1), (2, 0), (2, 1)):
        if base_cohomology_degree + fiber_cohomology_degree != total_degree:
            continue
        base_basis = _p2_basis(base_degree, base_cohomology_degree)
        fiber_basis = _p1_basis(fiber_degree, fiber_cohomology_degree)
        records.append((base_cohomology_degree, fiber_cohomology_degree, base_basis, fiber_basis))
    labels = tuple(
        str((base_cohomology_degree, fiber_cohomology_degree, base, fiber))
        for base_cohomology_degree, fiber_cohomology_degree, base_basis, fiber_basis in records
        for base in base_basis
        for fiber in fiber_basis
    )
    return (
        VectorSpace(
            f"O({base_degree},{fiber_degree}):H^{total_degree}",
            labels,
            Eisenstein,
        ),
        tuple(records),
    )


def _tensor_map(
    source_space: VectorSpace,
    target_space: VectorSpace,
    source_records: tuple[tuple[int, int, tuple[Monomial, ...], tuple[Monomial, ...]], ...],
    target_records: tuple[tuple[int, int, tuple[Monomial, ...], tuple[Monomial, ...]], ...],
    base_map: LinearMap,
    fiber_map: LinearMap,
) -> LinearMap:
    """Tensor two factor maps in the deterministic Kunneth bases."""

    def indexed_labels(
        records: tuple[tuple[int, int, tuple[Monomial, ...], tuple[Monomial, ...]], ...],
    ) -> dict[tuple[int, int, Monomial, Monomial], int]:
        labels: dict[tuple[int, int, Monomial, Monomial], int] = {}
        offset = 0
        for base_degree, fiber_degree, base_basis, fiber_basis in records:
            for base in base_basis:
                for fiber in fiber_basis:
                    labels[(base_degree, fiber_degree, base, fiber)] = offset
                    offset += 1
        return labels

    source_labels = indexed_labels(source_records)
    target_labels = indexed_labels(target_records)
    rows = [
        [Eisenstein(0) for _ in range(source_space.dimension)]
        for _ in range(target_space.dimension)
    ]
    base_source_index = {label: index for index, label in enumerate(base_map.domain.basis)}
    base_target_index = {label: index for index, label in enumerate(base_map.codomain.basis)}
    fiber_source_index = {label: index for index, label in enumerate(fiber_map.domain.basis)}
    fiber_target_index = {label: index for index, label in enumerate(fiber_map.codomain.basis)}
    for source_label, source_index in source_labels.items():
        _, _, base, fiber = source_label
        base_index = base_source_index[str(base)]
        fiber_index = fiber_source_index[str(fiber)]
        for target_label, target_index in target_labels.items():
            _, _, target_base, target_fiber = target_label
            target_base_index = base_target_index[str(target_base)]
            target_fiber_index = fiber_target_index[str(target_fiber)]
            rows[target_index][source_index] = (
                base_map.rows[target_base_index][base_index]
                * fiber_map.rows[target_fiber_index][fiber_index]
            )
    return LinearMap(source_space, target_space, rows)


def _equation_map(
    source_base_degree: int,
    source_fiber_degree: int,
    total_degree: int,
    surface_factor: int = 1,
) -> LinearMap:
    """Build multiplication by the selected dP9 equation on one ambient degree."""

    if surface_factor not in (1, 2):
        raise ValueError("dP9 surface factors are indexed by one and two")

    target_base_degree = source_base_degree + 3
    target_fiber_degree = source_fiber_degree + 1
    source_space, source_records = _kunneth_space(
        source_base_degree,
        source_fiber_degree,
        total_degree,
    )
    target_space, target_records = _kunneth_space(
        target_base_degree,
        target_fiber_degree,
        total_degree,
    )
    f, g = schoen_geometry().cover.cox.cubic_f, schoen_geometry().cover.cox.cubic_g
    maps = []
    for base_cohomology_degree, fiber_cohomology_degree, _, _ in source_records:
        base_f = _p2_multiplication(
            source_base_degree,
            target_base_degree,
            base_cohomology_degree,
            f,
        )
        base_g = _p2_multiplication(
            source_base_degree,
            target_base_degree,
            base_cohomology_degree,
            g,
        )
        first_fiber_terms = (
            (((1, 0), Eisenstein(1)),)
            if surface_factor == 1
            else (((0, 1), Eisenstein(2)),)
        )
        second_fiber_terms = (
            (((0, 1), Eisenstein(1)),)
            if surface_factor == 1
            else (((1, 0), Eisenstein(1)),)
        )
        first_fiber_map = _p1_multiplication(
            source_fiber_degree,
            target_fiber_degree,
            fiber_cohomology_degree,
            first_fiber_terms,
        )
        second_fiber_map = _p1_multiplication(
            source_fiber_degree,
            target_fiber_degree,
            fiber_cohomology_degree,
            second_fiber_terms,
        )
        maps.append((base_f, first_fiber_map, base_g, second_fiber_map))
    rows = [
        [Eisenstein(0) for _ in range(source_space.dimension)]
        for _ in range(target_space.dimension)
    ]
    source_offset = 0
    target_offset = 0
    for record_index, (base_f, mu, base_g, nu) in enumerate(maps):
        source_dimension = base_f.domain.dimension * mu.domain.dimension
        target_dimension = base_f.codomain.dimension * mu.codomain.dimension
        source_records_local = (source_records[record_index],)
        target_record = next(
            record
            for record in target_records
            if record[0] == source_records_local[0][0]
            and record[1] == source_records_local[0][1]
        )
        local_source_space = VectorSpace(
            "equation source block",
            tuple(
                str((base, fiber))
                for base in source_records_local[0][2]
                for fiber in source_records_local[0][3]
            ),
            Eisenstein,
        )
        local_target_space = VectorSpace(
            "equation target block",
            tuple(
                str((base, fiber))
                for base in target_record[2]
                for fiber in target_record[3]
            ),
            Eisenstein,
        )
        f_tensor = _tensor_map(
            local_source_space,
            local_target_space,
            source_records_local,
            (target_record,),
            base_f,
            mu,
        )
        g_tensor = _tensor_map(
            local_source_space,
            local_target_space,
            source_records_local,
            (target_record,),
            base_g,
            nu,
        )
        local_rows = [
            [
                f_tensor.rows[row][column] + g_tensor.rows[row][column]
                for column in range(source_dimension)
            ]
            for row in range(target_dimension)
        ]
        for row in range(target_dimension):
            for column in range(source_dimension):
                rows[target_offset + row][source_offset + column] = local_rows[row][column]
        source_offset += source_dimension
        target_offset += target_dimension
    return LinearMap(source_space, target_space, rows)


def _ambient_multiplication(
    source_base_degree: int,
    target_base_degree: int,
    fiber_degree: int,
    total_degree: int,
    polynomial: Polynomial,
) -> LinearMap:
    """Multiply one ambient Kunneth space by a base polynomial."""

    source_space, source_records = _kunneth_space(
        source_base_degree,
        fiber_degree,
        total_degree,
    )
    target_space, target_records = _kunneth_space(
        target_base_degree,
        fiber_degree,
        total_degree,
    )
    base_maps = []
    for base_cohomology_degree, fiber_cohomology_degree, _, _ in source_records:
        base_maps.append(
            (
                _p2_multiplication(
                    source_base_degree,
                    target_base_degree,
                    base_cohomology_degree,
                    polynomial,
                ),
                _p1_multiplication(
                    fiber_degree,
                    fiber_degree,
                    fiber_cohomology_degree,
                    (((0, 0), Eisenstein(1)),),
                ),
            )
        )
    rows = [
        [Eisenstein(0) for _ in range(source_space.dimension)]
        for _ in range(target_space.dimension)
    ]
    source_offset = 0
    target_offset = 0
    for record_index, (base_map, fiber_map) in enumerate(base_maps):
        source_record = (source_records[record_index],)
        target_record = tuple(
            record
            for record in target_records
            if record[0] == source_records[record_index][0]
            and record[1] == source_records[record_index][1]
        )
        local_source = VectorSpace(
            "ambient multiplication source",
            tuple(
                str((base, fiber))
                for base in source_record[0][2]
                for fiber in source_record[0][3]
            ),
            Eisenstein,
        )
        local_target = VectorSpace(
            "ambient multiplication target",
            tuple(
                str((base, fiber))
                for base in target_record[0][2]
                for fiber in target_record[0][3]
            ),
            Eisenstein,
        )
        local = _tensor_map(
            local_source,
            local_target,
            source_record,
            target_record,
            base_map,
            fiber_map,
        )
        for row in range(local.codomain.dimension):
            for column in range(local.domain.dimension):
                rows[target_offset + row][source_offset + column] = local.rows[row][column]
        source_offset += local.domain.dimension
        target_offset += local.codomain.dimension
    return LinearMap(source_space, target_space, rows)


@dataclass(frozen=True, slots=True)
class AmbientLineBundle:
    """Ambient Kunneth cohomology spaces for one ``P2 x P1`` line bundle."""

    base_degree: int
    fiber_degree: int
    spaces: tuple[tuple[int, VectorSpace], ...]

    def space(self, degree: int) -> VectorSpace:
        """Return one total ambient cohomology space."""

        return dict(self.spaces).get(
            degree,
            VectorSpace(
                f"O({self.base_degree},{self.fiber_degree}):H^{degree}",
                (),
                Eisenstein,
            ),
        )


def ambient_line_bundle(base_degree: int, fiber_degree: int) -> AmbientLineBundle:
    """Construct exact Kunneth cohomology spaces on ``P2 x P1``."""

    return AmbientLineBundle(
        base_degree,
        fiber_degree,
        tuple(
            (
                degree,
                _kunneth_space(base_degree, fiber_degree, degree)[0],
            )
            for degree in range(4)
        ),
    )


@dataclass(frozen=True, slots=True)
class DPSurfaceLineBundle:
    """Exact cochain model for a line bundle restricted to the dP9 surface."""

    base_degree: int
    fiber_degree: int
    surface_factor: int
    ambient_source: AmbientLineBundle
    ambient_target: AmbientLineBundle
    complex: CochainComplex

    @property
    def cohomology_dimensions(self) -> tuple[tuple[int, int], ...]:
        """Return exact dP9 line-bundle dimensions in geometric degrees."""

        return tuple(
            (degree, self.complex.cohomology_dimension(degree))
            for degree in DP9_COHOMOLOGY_DEGREES
        )

    @property
    def squared_zero(self) -> bool:
        """Return the exact cone square-zero certificate."""

        return all(
            self.complex.differential(degree + 1).compose(
                self.complex.differential(degree)
            ).is_zero()
            for degree in self.complex.degrees
        )

    def as_record(self) -> dict[str, object]:
        """Serialize dimensions and the exact Koszul cone scope."""

        return {
            "base_degree": self.base_degree,
            "fiber_degree": self.fiber_degree,
            "surface_factor": self.surface_factor,
            "cohomology_dimensions": [list(item) for item in self.cohomology_dimensions],
            "squared_zero": self.squared_zero,
            "ambient_source_fiber_degree": self.ambient_source.fiber_degree,
            "ambient_target_fiber_degree": self.ambient_target.fiber_degree,
            "status": "exact dP9 line-bundle Koszul cone; no bundle interpretation",
        }

    def multiplication(self, target: DPSurfaceLineBundle, polynomial: Polynomial) -> ChainMap:
        """Return multiplication by a homogeneous base polynomial on the cone."""

        if self.fiber_degree != target.fiber_degree:
            raise ValueError("line-bundle multiplication requires equal fiber degrees")
        if self.surface_factor != target.surface_factor:
            raise ValueError("line-bundle multiplication requires one dP9 factor")
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
        if target.base_degree != self.base_degree + polynomial.degree:
            raise ValueError("polynomial degree does not match line-bundle degrees")
        components = {}
        for degree in self.complex.degrees:
            target_space = target.complex.spaces.space(degree)
            source_space = self.complex.spaces.space(degree)
            base_map = _ambient_multiplication(
                self.base_degree,
                target.base_degree,
                self.fiber_degree,
                degree,
                polynomial,
            )
            source_correction = _ambient_multiplication(
                self.base_degree - 3,
                target.base_degree - 3,
                self.fiber_degree - 1,
                degree + 1,
                polynomial,
            )
            components[degree] = LinearMap.block(
                (
                    (
                        base_map,
                        LinearMap.zero(
                            self.ambient_source.space(degree + 1),
                            target.ambient_target.space(degree),
                        ),
                    ),
                    (
                        LinearMap.zero(
                            self.ambient_target.space(degree),
                            target.ambient_source.space(degree + 1),
                        ),
                        source_correction,
                    ),
                )
            )
            if components[degree].domain != source_space:
                raise ValueError("line-bundle multiplication source frame mismatch")
            if components[degree].codomain != target_space:
                raise ValueError("line-bundle multiplication target frame mismatch")
        return ChainMap(self.complex, target.complex, components)


@cache
def dp9_line_bundle(
    base_degree: int,
    fiber_degree: int,
    surface_factor: int = 1,
) -> DPSurfaceLineBundle:
    """Construct the exact restriction cone for ``O_D(base_degree,fiber_degree)``."""

    if surface_factor not in (1, 2):
        raise ValueError("dP9 surface factors are indexed by one and two")

    source = ambient_line_bundle(base_degree - 3, fiber_degree - 1)
    target = ambient_line_bundle(base_degree, fiber_degree)
    spaces = {
        degree: target.space(degree).direct_sum(
            source.space(degree + 1),
        )
        for degree in DP9_TOTAL_DEGREES
    }
    graded = GradedVectorSpace(
        f"O_D({base_degree},{fiber_degree})",
        spaces,
    )
    differentials = {}
    for degree in DP9_DIFFERENTIAL_DEGREES:
        target_next = target.space(degree + 1)
        source_next = source.space(degree + 1)
        source_after_next = source.space(degree + 2)
        equation = _equation_map(
            source.base_degree,
            source.fiber_degree,
            degree + 1,
            surface_factor,
        )
        top_left = LinearMap.zero(target.space(degree), target_next)
        top_right = equation
        bottom_left = LinearMap.zero(target.space(degree), source_after_next)
        bottom_right = LinearMap.zero(source_next, source_after_next)
        differentials[degree] = LinearMap.block(
            ((top_left, top_right), (bottom_left, bottom_right))
        )
    return DPSurfaceLineBundle(
        base_degree,
        fiber_degree,
        surface_factor,
        source,
        target,
        CochainComplex(graded, differentials),
    )


__all__ = [
    "AmbientLineBundle",
    "DP9_COHOMOLOGY_DEGREES",
    "DP9_DIFFERENTIAL_DEGREES",
    "DP9_TOTAL_DEGREES",
    "DPSurfaceLineBundle",
    "ambient_line_bundle",
    "dp9_line_bundle",
]
