"""Lift simple dP9 Serre Ext classes to exact Čech hypercocycles.

Owns:
    Extraction of pure generator/H1 representatives, their Laurent-monomial
    realization on the standard ``P1`` cover, Hilbert--Burch closure checks,
    and the resulting derived mapping-cone square-zero certificate.

Depends on:
    Exact dP9 Serre total complexes, projective Čech monomial complexes, and
    sparse Eisenstein polynomial arithmetic.

Must not:
    Lift representatives with unresolved lower-resolution corrections, infer
    local freeness, or identify a derived cone with a physical bundle before
    the relevant source and descent gates are supplied.

Phase 0:
    Pure H1 constituent classes have executable Čech hypercocycles and exact
    derived-cone identities; synchronized Schoen outer Hom remains separate.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.cech import (
    ProjectiveMonomialCechComplex,
    projective_monomial_cech_complex,
)
from onetheory.math.homological import CoordinateVector
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial

from .dp9_linebundles import _kunneth_space
from .dp9_serre_ext import DPSurfaceSerreExt


@dataclass(frozen=True, slots=True, order=True)
class SerreCechTerm:
    """One generator-valued Laurent monomial on the fiber-chart overlap."""

    generator_index: int
    base_monomial: tuple[int, int, int]
    fiber_monomial: tuple[int, int]
    coefficient: Eisenstein

    def __post_init__(self) -> None:
        if self.generator_index < 0:
            raise ValueError("generator indices must be nonnegative")
        if self.fiber_monomial != (-1, -1):
            raise ValueError("the current Serre lift requires the canonical O(-2) class")
        if self.coefficient.is_zero():
            raise ValueError("normalized Čech terms must be nonzero")


@dataclass(frozen=True, slots=True)
class DPSurfaceSerreCechCocycle:
    """Exact degree-one Čech/resolution cocycle for a Serre extension."""

    extension: DPSurfaceSerreExt
    source_representative: CoordinateVector
    terms: tuple[SerreCechTerm, ...]
    generator_polynomials: tuple[Polynomial, ...]
    horizontal_residues: tuple[Polynomial, ...]
    fiber_cech: ProjectiveMonomialCechComplex

    @property
    def cech_closed(self) -> bool:
        """Return whether the overlap class has no outgoing Čech differential."""

        representative = self.fiber_cech.cochain(1, {(0, 1): 1})
        return self.fiber_cech.complex.differential(1)(representative).is_zero()

    @property
    def horizontal_closed(self) -> bool:
        """Return whether composition with every syzygy vanishes exactly."""

        return all(residue.is_zero() for residue in self.horizontal_residues)

    @property
    def total_closed(self) -> bool:
        """Return the exact Čech plus resolution hypercocycle gate."""

        return self.cech_closed and self.horizontal_closed

    @property
    def derived_cone_squared_zero(self) -> bool:
        """Return the block-cone identity ``D_L phi + phi D_I = 0``."""

        return self.extension.squared_zero and self.total_closed

    def as_record(self) -> dict[str, object]:
        """Serialize sparse cocycle data and its derived-cone boundary."""

        return {
            "scheme": self.extension.scheme.name,
            "surface_factor": self.extension.surface_factor,
            "terms": [
                {
                    "generator_index": term.generator_index,
                    "base_monomial": list(term.base_monomial),
                    "fiber_monomial": list(term.fiber_monomial),
                    "coefficient": str(term.coefficient),
                    "fiber_overlap": ["mu", "nu"],
                }
                for term in self.terms
            ],
            "generator_polynomials": [
                [
                    {"monomial": list(monomial), "coefficient": str(coefficient)}
                    for monomial, coefficient in polynomial.terms
                ]
                for polynomial in self.generator_polynomials
            ],
            "horizontal_residues_zero": self.horizontal_closed,
            "cech_closed": self.cech_closed,
            "total_closed": self.total_closed,
            "derived_mapping_cone": {
                "differential": "D_W=[[D_L,phi],[0,D_I]]",
                "squared_zero": self.derived_cone_squared_zero,
                "finite_local_module_matrix_materialized": False,
            },
            "status": (
                "exact sparse Cech hypercocycle and derived mapping-cone "
                "certificate; local module materialization remains pending"
            ),
        }


def _generator_coordinates(
    extension: DPSurfaceSerreExt,
    representative: CoordinateVector,
) -> tuple[tuple[tuple[tuple[int, int, int], tuple[int, int], Eisenstein], ...], ...]:
    """Decode the generator/H1 cell and reject hidden correction components."""

    if representative.space != extension.total.spaces.space(1):
        raise ValueError("the Serre representative must live in total degree one")
    offset = 0
    decoded = []
    for bundle in extension.generator_bundles:
        ambient, records = _kunneth_space(
            bundle.base_degree,
            bundle.fiber_degree,
            1,
        )
        source_correction = bundle.ambient_source.space(2)
        values = representative.coordinates[offset : offset + ambient.dimension]
        labels = tuple(
            (base, fiber)
            for _, _, base_basis, fiber_basis in records
            for base in base_basis
            for fiber in fiber_basis
        )
        decoded.append(
            tuple(
                (base, fiber, coefficient)
                for (base, fiber), coefficient in zip(labels, values, strict=True)
                if not coefficient.is_zero()
            )
        )
        offset += ambient.dimension
        correction_values = representative.coordinates[
            offset : offset + source_correction.dimension
        ]
        if any(not coefficient.is_zero() for coefficient in correction_values):
            raise ValueError("the Serre class needs an unresolved Koszul correction lift")
        offset += source_correction.dimension
    if any(not coefficient.is_zero() for coefficient in representative.coordinates[offset:]):
        raise ValueError("the Serre class needs an unresolved syzygy/Cech correction lift")
    return tuple(decoded)


def dp9_serre_cech_cocycle(
    extension: DPSurfaceSerreExt,
    representative: CoordinateVector,
) -> DPSurfaceSerreCechCocycle:
    """Lift one pure invariant Ext representative to a Čech hypercocycle."""

    decoded = _generator_coordinates(extension, representative)
    polynomials = tuple(
        Polynomial(
            ((base, coefficient) for base, _, coefficient in entries),
            variable_count=3,
            scalar_type=Eisenstein,
        )
        for entries in decoded
    )
    residues = tuple(
        sum(
            (
                polynomials[row] * extension.scheme.resolution.matrix[row][column]
                for row in range(len(polynomials))
            ),
            Polynomial.zero(3, scalar_type=Eisenstein),
        )
        for column in range(len(extension.scheme.resolution.matrix[0]))
    )
    terms = tuple(
        sorted(
            SerreCechTerm(index, base, fiber, coefficient)
            for index, entries in enumerate(decoded)
            for base, fiber, coefficient in entries
        )
    )
    fiber_cech = projective_monomial_cech_complex(
        ("mu", "nu"),
        (-1, -1),
        scalar_type=Eisenstein,
    )
    result = DPSurfaceSerreCechCocycle(
        extension,
        representative,
        terms,
        polynomials,
        residues,
        fiber_cech,
    )
    if not result.total_closed:
        raise ValueError("the decoded Serre representative is not a Čech hypercocycle")
    return result


__all__ = [
    "DPSurfaceSerreCechCocycle",
    "SerreCechTerm",
    "dp9_serre_cech_cocycle",
]
