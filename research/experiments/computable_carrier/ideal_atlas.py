"""Pull Hilbert--Burch ideal resolutions onto the dP9 blow-up atlas.

Owns:
    Exact chart-local Hilbert--Burch matrices for I3 and I6, their homogeneous
    line-bundle degree conventions, and all Laurent chain-comparison identities
    across the six-chart cubic-pencil blow-up atlas.

Depends on:
    Production point-scheme resolutions, the exact pencil blow-up atlas, and
    Laurent/polynomial arithmetic. The result is a sheaf-resolution input for
    the Serre computation, not an extension class.

Must not:
    Interpret a pulled-back ideal resolution as a vector-bundle construction,
    invent global Serre cocycles, skip overlap checks, or claim descent or
    stability from the resolution alone.

Phase 0:
    I3/I6 ideal resolutions and overlap comparisons are exact; the Serre
    extension, global pushout, and equivariant linearization remain pending.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.math.sheaves import LaurentPolynomial
from onetheory.models.heterotic_schoen.visible import PointScheme, point_schemes

from .pencil import (
    BlowupChart,
    BlowupOverlap,
    TierAPencilModel,
    _embed_affine_polynomial,
    _monomial_image,
    _source_projective_coordinates,
    tier_a_pencil_model,
)

MatrixEntries = tuple[tuple[Polynomial, ...], ...]


@dataclass(frozen=True, slots=True)
class IdealResolutionOverlap:
    """One exact chain-comparison result on an atlas overlap."""

    source: str
    target: str
    source_base_pivot: int
    target_base_pivot: int
    generator_degree: int
    chain_comparison: bool

    def as_record(self) -> dict[str, object]:
        """Serialize the degree and exact comparison status."""

        return {
            "source": self.source,
            "target": self.target,
            "source_base_pivot": self.source_base_pivot,
            "target_base_pivot": self.target_base_pivot,
            "generator_degree": self.generator_degree,
            "chain_comparison": self.chain_comparison,
        }


@dataclass(frozen=True, slots=True)
class AtlasIdealResolution:
    """A Hilbert--Burch resolution represented on every blow-up chart."""

    scheme: str
    generator_degree: int
    chart_matrices: tuple[tuple[str, MatrixEntries], ...]
    overlap_comparisons: tuple[IdealResolutionOverlap, ...]
    local_resolution_shapes: tuple[tuple[str, tuple[int, int]], ...]
    all_chain_comparisons: bool
    status: str

    def as_record(self) -> dict[str, object]:
        """Serialize exact local matrices and all comparison certificates."""

        def matrix_record(matrix: MatrixEntries) -> list[list[list[object]]]:
            return [
                [
                    [
                        {
                            "exponents": list(exponents),
                            "coefficient": str(coefficient),
                        }
                        for exponents, coefficient in entry.terms
                    ]
                    for entry in row
                ]
                for row in matrix
            ]

        return {
            "scheme": self.scheme,
            "generator_degree": self.generator_degree,
            "chart_matrices": [
                {"chart": chart, "matrix": matrix_record(matrix)}
                for chart, matrix in self.chart_matrices
            ],
            "overlap_comparisons": [item.as_record() for item in self.overlap_comparisons],
            "local_resolution_shapes": [
                [chart, list(shape)] for chart, shape in self.local_resolution_shapes
            ],
            "all_chain_comparisons": self.all_chain_comparisons,
            "status": self.status,
        }


def _chart_matrix(scheme: PointScheme, chart: BlowupChart) -> MatrixEntries:
    """Pull one homogeneous Hilbert--Burch matrix to a chart."""

    # The chart variables are symbolic names; replace them with exact local
    # polynomial variables before pulling back the homogeneous matrix.
    local_u = Polynomial.monomial((1, 0), scalar_type=Eisenstein)
    local_v = Polynomial.monomial((0, 1), scalar_type=Eisenstein)
    local_images = {
        0: (Polynomial.one(2, scalar_type=Eisenstein), local_u, local_v),
        1: (local_u, Polynomial.one(2, scalar_type=Eisenstein), local_v),
        2: (local_u, local_v, Polynomial.one(2, scalar_type=Eisenstein)),
    }[chart.base_pivot]
    return tuple(
        tuple(_embed_affine_polynomial(entry.substitute(local_images)) for entry in row)
        for row in scheme.resolution.matrix
    )


def _laurent_matrix(matrix: MatrixEntries) -> tuple[tuple[LaurentPolynomial, ...], ...]:
    """Embed a chart matrix into its three-variable Laurent ring."""

    return tuple(
        tuple(LaurentPolynomial.from_polynomial(entry) for entry in row)
        for row in matrix
    )


def _source_pivot_unit(source: BlowupChart, target: BlowupChart) -> LaurentPolynomial:
    """Return the target projective pivot in source-chart coordinates."""

    coordinates = _source_projective_coordinates(source.base_pivot)
    exponents = coordinates[target.base_pivot]
    return LaurentPolynomial.monomial(exponents, scalar_type=Eisenstein)


def _compare_overlap(
    scheme: PointScheme,
    source: BlowupChart,
    target: BlowupChart,
    overlap: BlowupOverlap,
    source_matrix: MatrixEntries,
    target_matrix: MatrixEntries,
) -> IdealResolutionOverlap:
    """Verify the degree-one chain map on one ordered overlap."""

    source_laurent = _laurent_matrix(source_matrix)
    target_laurent = _laurent_matrix(target_matrix)
    images = (
        _monomial_image(overlap.base_images[0]),
        _monomial_image(overlap.base_images[1]),
        _monomial_image(overlap.fiber_image),
    )
    pulled_target = tuple(
        tuple(entry.substitute_monomials(images) for entry in row)
        for row in target_laurent
    )
    pivot = _source_pivot_unit(source, target)
    inverse_pivot = LaurentPolynomial.monomial(
        tuple(-value for value in pivot.terms[0][0]),
        scalar_type=Eisenstein,
    )
    expected = tuple(
        tuple(entry * inverse_pivot for entry in row)
        for row in source_laurent
    )
    comparison = pulled_target == expected
    return IdealResolutionOverlap(
        source.name,
        target.name,
        source.base_pivot,
        target.base_pivot,
        max(generator.degree for generator in scheme.resolution.generators),
        comparison,
    )


def _one_ideal_resolution(
    scheme: PointScheme,
    model: TierAPencilModel,
) -> AtlasIdealResolution:
    """Construct one exact atlas resolution and verify every overlap."""

    charts = model.blowup_atlas.charts
    matrices = tuple((chart.name, _chart_matrix(scheme, chart)) for chart in charts)
    matrix_by_chart = dict(matrices)
    overlap_by_pair = {
        (overlap.source, overlap.target): overlap
        for overlap in model.blowup_atlas.overlaps
    }
    comparisons = tuple(
        _compare_overlap(
            scheme,
            source,
            target,
            overlap_by_pair[(source.name, target.name)],
            matrix_by_chart[source.name],
            matrix_by_chart[target.name],
        )
        for source in charts
        for target in charts
        if source != target
    )
    shapes = tuple(
        (chart.name, (len(matrix_by_chart[chart.name]), len(matrix_by_chart[chart.name][0])))
        for chart in charts
    )
    return AtlasIdealResolution(
        scheme.name,
        max(generator.degree for generator in scheme.resolution.generators),
        matrices,
        comparisons,
        shapes,
        all(item.chain_comparison for item in comparisons),
        "exact pulled-back ideal resolution; Serre extension map pending",
    )


def tier_a_atlas_ideal_resolutions(
    model: TierAPencilModel | None = None,
) -> tuple[AtlasIdealResolution, ...]:
    """Return exact I3/I6 resolutions on the complete blow-up atlas."""

    current = tier_a_pencil_model() if model is None else model
    return tuple(_one_ideal_resolution(scheme, current) for scheme in point_schemes())


__all__ = [
    "AtlasIdealResolution",
    "IdealResolutionOverlap",
    "tier_a_atlas_ideal_resolutions",
]
