"""Totalize monomial ideal resolutions on the dP9 presentation surface.

Owns:
    Exact dP9 line-bundle cone totalizations for the six monomial
    Hilbert--Burch resolutions, including the signed total differential,
    cohomology dimensions, and line-bundle square-zero checks.

Depends on:
    Monomial Hilbert--Burch certificates, exact dP9 line-bundle Koszul cones,
    polynomial multiplication, and the basis-aware bicomplex primitives.

Must not:
    Call the ideal-resolution hypercohomology a Serre Ext group, infer a
    locally free rank-two sheaf, supply missing global transition functions,
    or claim quotient descent, stability, or physical spectrum.

Phase 0:
    The dP9 ideal-resolution comparison is exact at presentation level;
    global sheafification, Serre extension data, and equivariant descent remain
    unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.homological import Bicomplex, CochainComplex, LinearMap, VectorSpace
from onetheory.math.numbers import Eisenstein

from .dp9_linebundles import DPSurfaceLineBundle, dp9_line_bundle
from .tier_b_monomial import InvariantMonomialScheme, tier_b_invariant_monomial_schemes


def _generator_degrees(scheme: InvariantMonomialScheme) -> tuple[int, ...]:
    """Return the exact homogeneous degrees of the ideal generators."""

    return tuple(generator.degree for generator in scheme.ideal.generators)


def _syzygy_degrees(scheme: InvariantMonomialScheme) -> tuple[int, ...]:
    """Recover one homogeneous shift from every Hilbert--Burch column."""

    generator_degrees = _generator_degrees(scheme)
    degrees = []
    for column in range(len(scheme.resolution.matrix[0])):
        column_degrees = {
            generator_degrees[row] + scheme.resolution.matrix[row][column].degree
            for row in range(len(generator_degrees))
            if not scheme.resolution.matrix[row][column].is_zero()
        }
        if len(column_degrees) != 1:
            raise ValueError("Hilbert--Burch column has incompatible homogeneous shifts")
        degrees.append(next(iter(column_degrees)))
    return tuple(degrees)


def _sum_space(
    name: str,
    bundles: tuple[DPSurfaceLineBundle, ...],
    degree: int,
) -> VectorSpace:
    """Build one ordered direct sum of line-bundle cohomology spaces."""

    if not bundles:
        return VectorSpace(name, (), Eisenstein)
    result = bundles[0].complex.spaces.space(degree)
    for bundle in bundles[1:]:
        result = result.direct_sum(bundle.complex.spaces.space(degree))
    return result


def _direct_sum_maps(maps: tuple[LinearMap, ...]) -> LinearMap:
    """Assemble exact block-diagonal maps in generator order."""

    if not maps:
        raise ValueError("direct-sum maps require at least one component")
    result = maps[0]
    for map_ in maps[1:]:
        result = LinearMap.direct_sum(result, map_)
    return result


def _vertical_maps(
    bundles: tuple[DPSurfaceLineBundle, ...],
) -> dict[int, LinearMap]:
    """Return the unsigned dP9 cone differential in each resolution column."""

    return {
        degree: _direct_sum_maps(
            tuple(bundle.complex.differential(degree) for bundle in bundles)
        )
        for degree in range(3)
    }


def _horizontal_map(
    scheme: InvariantMonomialScheme,
    source_bundles: tuple[DPSurfaceLineBundle, ...],
    target_bundles: tuple[DPSurfaceLineBundle, ...],
    degree: int,
) -> LinearMap:
    """Evaluate the Hilbert--Burch matrix on one dP9 cone degree."""

    blocks: list[list[LinearMap]] = []
    for target_index, target_bundle in enumerate(target_bundles):
        row: list[LinearMap] = []
        for source_index, source_bundle in enumerate(source_bundles):
            polynomial = scheme.resolution.matrix[target_index][source_index]
            if polynomial.is_zero():
                row.append(
                    LinearMap.zero(
                        source_bundle.complex.spaces.space(degree),
                        target_bundle.complex.spaces.space(degree),
                    )
                )
            else:
                row.append(
                    source_bundle.multiplication(target_bundle, polynomial).component(degree)
                )
        blocks.append(row)
    return LinearMap.block(blocks)


@dataclass(frozen=True, slots=True)
class DPSurfaceMonomialIdealResolution:
    """Exact presentation-level dP9 totalization of one monomial ideal."""

    scheme: InvariantMonomialScheme
    fiber_degree: int
    generator_degrees: tuple[int, ...]
    syzygy_degrees: tuple[int, ...]
    source_bundles: tuple[DPSurfaceLineBundle, ...]
    target_bundles: tuple[DPSurfaceLineBundle, ...]
    bicomplex: Bicomplex
    total: CochainComplex

    @property
    def squared_zero(self) -> bool:
        """Return the exact square-zero certificate for the total differential."""

        return all(
            self.total.differential(degree + 1).compose(
                self.total.differential(degree)
            ).is_zero()
            for degree in self.total.degrees
        )

    @property
    def all_line_bundles_squared_zero(self) -> bool:
        """Return whether every dP9 line-bundle cone is square-zero."""

        return all(
            bundle.squared_zero
            for bundle in (*self.source_bundles, *self.target_bundles)
        )

    @property
    def cohomology_dimensions(self) -> tuple[tuple[int, int], ...]:
        """Return exact total hypercohomology dimensions by total degree."""

        return tuple(
            (degree, self.total.cohomology_dimension(degree))
            for degree in self.total.degrees
        )

    def as_record(self) -> dict[str, object]:
        """Serialize dP9 ideal-resolution data without a sheaf claim."""

        return {
            "scheme": self.scheme.name,
            "fiber_degree": self.fiber_degree,
            "generator_degrees": list(self.generator_degrees),
            "syzygy_degrees": list(self.syzygy_degrees),
            "source_bundles": [item.as_record() for item in self.source_bundles],
            "target_bundles": [item.as_record() for item in self.target_bundles],
            "total_degrees": list(self.total.degrees),
            "total_dimensions": [
                [degree, self.total.spaces.space(degree).dimension]
                for degree in self.total.degrees
            ],
            "cohomology_dimensions": [list(item) for item in self.cohomology_dimensions],
            "squared_zero": self.squared_zero,
            "all_line_bundles_squared_zero": self.all_line_bundles_squared_zero,
            "status": (
                "exact dP9 ideal-resolution totalization; Serre Ext, global "
                "local freeness, and quotient descent remain unresolved"
            ),
        }


def dp9_monomial_ideal_resolution(
    scheme: InvariantMonomialScheme,
    fiber_degree: int = 0,
) -> DPSurfaceMonomialIdealResolution:
    """Build one exact dP9 cone totalization from a monomial resolution."""

    if isinstance(fiber_degree, bool) or not isinstance(fiber_degree, int):
        raise TypeError("fiber degree must be an integer")
    generator_degrees = _generator_degrees(scheme)
    syzygy_degrees = _syzygy_degrees(scheme)
    source_bundles = tuple(
        dp9_line_bundle(-degree, fiber_degree) for degree in syzygy_degrees
    )
    target_bundles = tuple(
        dp9_line_bundle(-degree, fiber_degree) for degree in generator_degrees
    )
    components = {
        (horizontal, vertical): _sum_space(
            f"{scheme.name} dP9 ideal ({horizontal},{vertical})",
            source_bundles if horizontal == -1 else target_bundles,
            vertical,
        )
        for horizontal in (-1, 0)
        for vertical in range(4)
    }
    horizontal = {
        (-1, vertical): _horizontal_map(
            scheme,
            source_bundles,
            target_bundles,
            vertical,
        )
        for vertical in range(4)
    }
    vertical = {}
    for horizontal_degree, bundles in ((-1, source_bundles), (0, target_bundles)):
        for degree, map_ in _vertical_maps(bundles).items():
            vertical[(horizontal_degree, degree)] = map_
    bicomplex = Bicomplex(
        f"{scheme.name} dP9 ideal resolution",
        components,
        horizontal=horizontal,
        vertical=vertical,
    )
    result = DPSurfaceMonomialIdealResolution(
        scheme,
        fiber_degree,
        generator_degrees,
        syzygy_degrees,
        source_bundles,
        target_bundles,
        bicomplex,
        bicomplex.totalize(),
    )
    if not result.squared_zero or not result.all_line_bundles_squared_zero:
        raise ValueError("dP9 monomial ideal totalization failed square-zero checks")
    return result


def tier_b_dp9_monomial_ideal_resolutions(
    schemes: tuple[InvariantMonomialScheme, ...] | None = None,
    fiber_degree: int = 0,
) -> tuple[DPSurfaceMonomialIdealResolution, ...]:
    """Build dP9 ideal-resolution comparisons for the bounded family."""

    selected = tier_b_invariant_monomial_schemes() if schemes is None else schemes
    return tuple(
        dp9_monomial_ideal_resolution(scheme, fiber_degree)
        for scheme in selected
    )


__all__ = [
    "DPSurfaceMonomialIdealResolution",
    "dp9_monomial_ideal_resolution",
    "tier_b_dp9_monomial_ideal_resolutions",
]
