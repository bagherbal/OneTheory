"""Compute exact Serre extension spaces on each published dP9 factor.

Owns:
    The fiber-sensitive Hilbert--Burch/Koszul bicomplex computing
    ``Ext^1(I_Z(f), O(-f))`` for an explicitly supplied point scheme and dP9
    hypersurface factor.

Depends on:
    Published point-scheme resolutions, exact dP9 line-bundle cones, and the
    generic basis-aware homological engine.

Must not:
    Import the published Serre action matrices as computed output, choose an
    equivariant extension ray, or infer quotient descent and bundle physics
    from an extension-space dimension.

Phase 0:
    Exact constituent extension complexes are executable; deck actions and
    equivariant representative selection remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.homological import (
    Bicomplex,
    CochainComplex,
    CoordinateVector,
    LinearMap,
    VectorSpace,
)
from onetheory.math.numbers import Eisenstein
from onetheory.models.heterotic_schoen.visible import PointScheme, point_schemes

from .dp9_linebundles import (
    DP9_DIFFERENTIAL_DEGREES,
    DP9_TOTAL_DEGREES,
    DPSurfaceLineBundle,
    dp9_line_bundle,
)


def _resolution_degrees(
    scheme: PointScheme,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Recover homogeneous generator and syzygy shifts exactly."""

    generator_degrees = tuple(generator.degree for generator in scheme.ideal_generators)
    syzygy_degrees = []
    for column in range(len(scheme.resolution.matrix[0])):
        shifts = {
            generator_degrees[row] + entry.degree
            for row, matrix_row in enumerate(scheme.resolution.matrix)
            if not (entry := matrix_row[column]).is_zero()
        }
        if len(shifts) != 1:
            raise ValueError("Hilbert--Burch column has incompatible homogeneous shifts")
        syzygy_degrees.append(shifts.pop())
    return generator_degrees, tuple(syzygy_degrees)


def _sum_space(
    name: str,
    bundles: tuple[DPSurfaceLineBundle, ...],
    degree: int,
) -> VectorSpace:
    """Return an ordered direct sum of line-bundle cone terms."""

    if not bundles:
        return VectorSpace(name, (), Eisenstein)
    result = bundles[0].complex.spaces.space(degree)
    for bundle in bundles[1:]:
        result = result.direct_sum(bundle.complex.spaces.space(degree))
    return result


def _direct_sum_maps(maps: tuple[LinearMap, ...]) -> LinearMap:
    """Return the block-diagonal sum of a nonempty map family."""

    if not maps:
        raise ValueError("a Serre resolution term requires at least one summand")
    result = maps[0]
    for map_ in maps[1:]:
        result = LinearMap.direct_sum(result, map_)
    return result


def _horizontal_map(
    scheme: PointScheme,
    source: tuple[DPSurfaceLineBundle, ...],
    target: tuple[DPSurfaceLineBundle, ...],
    sheaf_degree: int,
) -> LinearMap:
    """Evaluate the transposed Hilbert--Burch map on dP9 cones."""

    blocks: list[list[LinearMap]] = []
    for column, target_bundle in enumerate(target):
        row: list[LinearMap] = []
        for generator, source_bundle in enumerate(source):
            polynomial = scheme.resolution.matrix[generator][column]
            if polynomial.is_zero():
                row.append(
                    LinearMap.zero(
                        source_bundle.complex.spaces.space(sheaf_degree),
                        target_bundle.complex.spaces.space(sheaf_degree),
                    )
                )
            else:
                row.append(
                    source_bundle.multiplication(target_bundle, polynomial).component(
                        sheaf_degree
                    )
                )
        blocks.append(row)
    return LinearMap.block(blocks)


@dataclass(frozen=True, slots=True)
class DPSurfaceSerreExt:
    """Exact total complex for one dP9 Serre extension space."""

    scheme: PointScheme
    surface_factor: int
    generator_degrees: tuple[int, ...]
    syzygy_degrees: tuple[int, ...]
    generator_bundles: tuple[DPSurfaceLineBundle, ...]
    syzygy_bundles: tuple[DPSurfaceLineBundle, ...]
    bicomplex: Bicomplex
    total: CochainComplex

    @property
    def squared_zero(self) -> bool:
        """Return the exact total-differential square-zero certificate."""

        return all(
            self.total.differential(degree + 1).compose(
                self.total.differential(degree)
            ).is_zero()
            for degree in self.total.degrees
        )

    @property
    def ext_one_dimension(self) -> int:
        """Return ``dim Ext^1(I_Z(f), O(-f))`` from the total complex."""

        return self.total.cohomology_dimension(1)

    @property
    def ext_one_representatives(self) -> tuple[CoordinateVector, ...]:
        """Return deterministic exact total-cocycle representatives."""

        return self.total.cohomology_representatives(1)

    def as_record(self) -> dict[str, object]:
        """Serialize exact dimensions without asserting an equivariant ray."""

        return {
            "scheme": self.scheme.name,
            "surface_factor": self.surface_factor,
            "generator_degrees": list(self.generator_degrees),
            "syzygy_degrees": list(self.syzygy_degrees),
            "total_dimensions": [
                [degree, self.total.spaces.space(degree).dimension]
                for degree in self.total.degrees
            ],
            "ext_one_dimension": self.ext_one_dimension,
            "representative_count": len(self.ext_one_representatives),
            "squared_zero": self.squared_zero,
            "status": (
                "exact fiber-sensitive Serre extension space; deck action and "
                "equivariant extension ray remain unresolved"
            ),
        }


def dp9_serre_ext(
    scheme: PointScheme,
    surface_factor: int,
) -> DPSurfaceSerreExt:
    """Build the exact ``RHom(I_Z(f), O(-f))`` total complex."""

    if surface_factor not in (1, 2):
        raise ValueError("dP9 surface factors are indexed by one and two")
    if not scheme.is_certified:
        raise ValueError("the point scheme needs a certified Hilbert--Burch resolution")

    generator_degrees, syzygy_degrees = _resolution_degrees(scheme)
    generators = tuple(
        dp9_line_bundle(degree, -2, surface_factor)
        for degree in generator_degrees
    )
    syzygies = tuple(
        dp9_line_bundle(degree, -2, surface_factor)
        for degree in syzygy_degrees
    )
    components = {
        (parent_degree, sheaf_degree): _sum_space(
            f"{scheme.name}:Serre^{parent_degree},H^{sheaf_degree}",
            bundles,
            sheaf_degree,
        )
        for parent_degree, bundles in ((0, generators), (1, syzygies))
        for sheaf_degree in DP9_TOTAL_DEGREES
    }
    vertical = {
        (parent_degree, sheaf_degree): _direct_sum_maps(
            tuple(bundle.complex.differential(sheaf_degree) for bundle in bundles)
        )
        for parent_degree, bundles in ((0, generators), (1, syzygies))
        for sheaf_degree in DP9_DIFFERENTIAL_DEGREES
    }
    horizontal = {
        (0, sheaf_degree): _horizontal_map(
            scheme,
            generators,
            syzygies,
            sheaf_degree,
        )
        for sheaf_degree in DP9_TOTAL_DEGREES
    }
    bicomplex = Bicomplex(
        f"{scheme.name} dP9 Serre Ext",
        components,
        horizontal=horizontal,
        vertical=vertical,
    )
    return DPSurfaceSerreExt(
        scheme,
        surface_factor,
        generator_degrees,
        syzygy_degrees,
        generators,
        syzygies,
        bicomplex,
        bicomplex.totalize(),
    )


def published_constituent_serre_exts() -> tuple[DPSurfaceSerreExt, ...]:
    """Compute the W1 and W2 constituent extension spaces in factor order."""

    length_three, length_six = point_schemes()
    return (
        dp9_serre_ext(length_three, 1),
        dp9_serre_ext(length_six, 2),
    )


__all__ = [
    "DPSurfaceSerreExt",
    "dp9_serre_ext",
    "published_constituent_serre_exts",
]
