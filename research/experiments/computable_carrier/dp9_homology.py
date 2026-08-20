"""Assemble exact dP9 total complexes from line-bundle restrictions.

Owns:
    The finite bicomplex obtained by applying the polynomial presentation Hom
    differential to exact dP9 line-bundle Koszul cones, together with its
    signed cochain totalization and square-zero record.

Depends on:
    The generic polynomial Hom complex, exact dP9 line-bundle multiplication,
    and the reusable basis-aware bicomplex and cochain-complex primitives.

Must not:
    Treat presentation-term line bundles as a sheafified bundle, infer
    quotient descent or stability, or promote total cohomology to physical
    Ext data without the missing global comparison certificates.

Phase 0:
    The presentation-level dP9 total complex is exact and executable; global
    sheafification, quotient descent, and carrier promotion remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.homological import (
    Bicomplex,
    CochainComplex,
    LinearMap,
    VectorSpace,
)
from onetheory.math.numbers import Eisenstein

from .dp9_linebundles import (
    DP9_DIFFERENTIAL_DEGREES,
    DP9_TOTAL_DEGREES,
    DPSurfaceLineBundle,
    dp9_line_bundle,
)
from .polynomial_hom import PolynomialHomComplex
from .projective_hom_search import (
    TierAProjectiveHomPairAudit,
    tier_a_projective_hom_pair_audits,
)


def _term_bundles(
    parent: PolynomialHomComplex,
    fiber_degree: int,
) -> tuple[tuple[int, tuple[DPSurfaceLineBundle, ...]], ...]:
    """Construct one exact restricted line bundle per Hom generator."""

    return tuple(
        (
            degree,
            tuple(
                dp9_line_bundle(-shift[0], fiber_degree)
                for shift in module.shifts
            ),
        )
        for degree, module in parent.terms
    )


def _sum_space(
    name: str,
    bundles: tuple[DPSurfaceLineBundle, ...],
    degree: int,
) -> VectorSpace:
    """Build the ordered direct sum of one line-bundle cohomology degree."""

    if not bundles:
        return VectorSpace(name, (), Eisenstein)
    result = bundles[0].complex.spaces.space(degree)
    for bundle in bundles[1:]:
        result = result.direct_sum(bundle.complex.spaces.space(degree))
    return result


def _term_spaces(
    parent: PolynomialHomComplex,
    bundles: tuple[tuple[int, tuple[DPSurfaceLineBundle, ...]], ...],
) -> dict[tuple[int, int], VectorSpace]:
    """Create every bicomplex cell with deterministic direct-sum bases."""

    spaces: dict[tuple[int, int], VectorSpace] = {}
    for parent_degree, selected in bundles:
        for sheaf_degree in DP9_TOTAL_DEGREES:
            spaces[(parent_degree, sheaf_degree)] = _sum_space(
                f"{parent.left.scheme.name}/{parent.right.scheme.name} dP9 "
                f"Hom^{parent_degree},H^{sheaf_degree}",
                selected,
                sheaf_degree,
            )
    return spaces


def _direct_sum_maps(
    maps: tuple[LinearMap, ...],
) -> LinearMap:
    """Assemble a block-diagonal map in the matching generator order."""

    if not maps:
        raise ValueError("a term map requires at least one generator")
    result = maps[0]
    for map_ in maps[1:]:
        result = LinearMap.direct_sum(result, map_)
    return result


def _vertical_maps(
    bundles: tuple[tuple[int, tuple[DPSurfaceLineBundle, ...]], ...],
) -> dict[tuple[int, int], LinearMap]:
    """Return the unsigned line-bundle differentials in each parent column."""

    maps: dict[tuple[int, int], LinearMap] = {}
    for parent_degree, selected in bundles:
        for sheaf_degree in DP9_DIFFERENTIAL_DEGREES:
            maps[(parent_degree, sheaf_degree)] = _direct_sum_maps(
                tuple(
                    bundle.complex.differential(sheaf_degree)
                    for bundle in selected
                )
            )
    return maps


def _horizontal_map(
    parent: PolynomialHomComplex,
    parent_degree: int,
    sheaf_degree: int,
    source_bundles: tuple[DPSurfaceLineBundle, ...],
    target_bundles: tuple[DPSurfaceLineBundle, ...],
) -> LinearMap:
    """Evaluate one polynomial Hom differential on line-bundle cones."""

    polynomial_map = parent.differential(parent_degree)
    blocks: list[list[LinearMap]] = []
    for target_index, target_bundle in enumerate(target_bundles):
        row: list[LinearMap] = []
        for source_index, source_bundle in enumerate(source_bundles):
            polynomial = polynomial_map.matrix.rows[target_index][source_index]
            if polynomial.is_zero():
                row.append(
                    LinearMap.zero(
                        source_bundle.complex.spaces.space(sheaf_degree),
                        target_bundle.complex.spaces.space(sheaf_degree),
                    )
                )
                continue
            row.append(
                source_bundle.multiplication(target_bundle, polynomial).component(
                    sheaf_degree
                )
            )
        blocks.append(row)
    return LinearMap.block(blocks)


@dataclass(frozen=True, slots=True)
class DPSurfaceDerivedHom:
    """Exact signed totalization for one presentation Hom pair on dP9."""

    parent: PolynomialHomComplex
    fiber_degree: int
    bundles: tuple[tuple[int, tuple[DPSurfaceLineBundle, ...]], ...]
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
    def total_h1_dimension(self) -> int:
        """Return the exact degree-one total cohomology dimension."""

        return self.total.cohomology_dimension(1)

    @property
    def all_line_bundles_squared_zero(self) -> bool:
        """Return whether every restricted line-bundle cone is exact."""

        return all(bundle.squared_zero for _, selected in self.bundles for bundle in selected)

    def as_record(self) -> dict[str, object]:
        """Serialize the total-complex shape without physical interpretation."""

        return {
            "left_scheme": self.parent.left.scheme.name,
            "right_scheme": self.parent.right.scheme.name,
            "fiber_degree": self.fiber_degree,
            "bicomplex_cells": [
                [parent_degree, sheaf_degree, space.dimension]
                for (parent_degree, sheaf_degree), space in self.bicomplex.components
            ],
            "total_degrees": list(self.total.degrees),
            "total_dimensions": [
                [degree, self.total.spaces.space(degree).dimension]
                for degree in self.total.degrees
            ],
            "total_h1_dimension": self.total_h1_dimension,
            "squared_zero": self.squared_zero,
            "all_line_bundles_squared_zero": self.all_line_bundles_squared_zero,
            "status": (
                "exact presentation-level dP9 line-bundle totalization; global "
                "sheafification and quotient descent remain unresolved"
            ),
        }


def dp9_derived_hom(
    parent: PolynomialHomComplex,
    fiber_degree: int = 0,
) -> DPSurfaceDerivedHom:
    """Build the signed dP9 derived-Hom total complex for one parent pair."""

    if isinstance(fiber_degree, bool) or not isinstance(fiber_degree, int):
        raise TypeError("fiber degree must be an integer")
    bundles = _term_bundles(parent, fiber_degree)
    spaces = _term_spaces(parent, bundles)
    vertical = _vertical_maps(bundles)
    horizontal = {}
    bundle_map = dict(bundles)
    for parent_degree, _ in parent.differentials:
        for sheaf_degree in DP9_TOTAL_DEGREES:
            horizontal[(parent_degree, sheaf_degree)] = _horizontal_map(
                parent,
                parent_degree,
                sheaf_degree,
                bundle_map[parent_degree],
                bundle_map[parent_degree + 1],
            )
    bicomplex = Bicomplex(
        "dP9 presentation Hom",
        spaces,
        horizontal=horizontal,
        vertical=vertical,
    )
    return DPSurfaceDerivedHom(
        parent,
        fiber_degree,
        bundles,
        bicomplex,
        bicomplex.totalize(),
    )


def tier_a_dp9_derived_homs(
    pair_audits: tuple[TierAProjectiveHomPairAudit, ...] | None = None,
) -> tuple[DPSurfaceDerivedHom, ...]:
    """Build the exact dP9 totalization for every declared ray pair."""

    audits = tier_a_projective_hom_pair_audits() if pair_audits is None else pair_audits
    return tuple(dp9_derived_hom(audit.hypercohomology.parent) for audit in audits)


__all__ = [
    "DPSurfaceDerivedHom",
    "dp9_derived_hom",
    "tier_a_dp9_derived_homs",
]
