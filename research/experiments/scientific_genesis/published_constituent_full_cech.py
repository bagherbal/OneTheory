"""Lift the selected constituent Ext rays to the full dP9 Čech complex.

Owns:
    The two-factor standard-cover contraction, full Hilbert--Burch/Koszul/Čech
    differential, transferred-map comparison, and corrected ray inclusions.

Depends on:
    Exact dP9 Serre Ext totals, the source-selected mixed rays, projective
    monomial Čech contractions, and the frozen cubic pencils.

Must not:
    Drop Koszul correction terms, identify a nonzero edge component with a
    local unit without evaluation, or call an Ext cocycle a bundle atlas.

Phase 0:
    Research-only full Čech representatives of the selected extension rays.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.cech import (
    ProductProjectiveMonomialCechComplex,
    product_projective_monomial_cech_complex,
    projective_monomial_cech_complex,
)
from onetheory.math.homological import CoordinateVector
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.dp9_linebundles import (
    DPSurfaceLineBundle,
    _kunneth_space,
)
from research.experiments.computable_carrier.dp9_serre_ext import DPSurfaceSerreExt
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_outer import (
    SparseMap,
    _freeze_rows,
)

from .published_constituent_ray_alignment import (
    PublishedConstituentRayAlignment,
    published_constituent_ray_alignments,
)

Monomial3 = tuple[int, int, int]
Monomial2 = tuple[int, int]
Cell = tuple[tuple[int, ...], tuple[int, ...]]

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/published_constituent_full_cech.json"


@dataclass(frozen=True, slots=True, order=True)
class ConstituentCechComponent:
    """One resolution and hypersurface-Koszul summand."""

    parent_degree: int
    bundle_index: int
    koszul_degree: int
    base_degree: int
    fiber_degree: int

    @property
    def structural_degree(self) -> int:
        """Return resolution degree minus the Koszul wedge degree."""

        return self.parent_degree - self.koszul_degree


@dataclass(frozen=True, slots=True, order=True)
class ConstituentCechBasis:
    """One regular Laurent monomial on a product-cover cell."""

    component: ConstituentCechComponent
    base_monomial: Monomial3
    fiber_monomial: Monomial2
    cell: Cell

    @property
    def cech_degree(self) -> int:
        """Return the total two-factor Čech degree."""

        return sum(len(simplex) - 1 for simplex in self.cell)

    @property
    def total_degree(self) -> int:
        """Return structural plus Čech degree."""

        return self.component.structural_degree + self.cech_degree


@dataclass(frozen=True, slots=True)
class ConstituentFullCochain:
    """One normalized sparse cochain in the full dP9 Serre Ext complex."""

    terms: tuple[tuple[ConstituentCechBasis, Eisenstein], ...]

    def __init__(
        self,
        terms: tuple[tuple[ConstituentCechBasis, Eisenstein], ...] = (),
    ) -> None:
        values: dict[ConstituentCechBasis, Eisenstein] = {}
        for basis, coefficient in terms:
            values[basis] = values.get(basis, Eisenstein(0)) + coefficient
        object.__setattr__(
            self,
            "terms",
            tuple(
                (basis, coefficient)
                for basis, coefficient in sorted(values.items())
                if not coefficient.is_zero()
            ),
        )

    def __add__(self, other: ConstituentFullCochain) -> ConstituentFullCochain:
        return ConstituentFullCochain(self.terms + other.terms)

    def scale(self, scalar: int | Eisenstein) -> ConstituentFullCochain:
        """Scale every exact coefficient."""

        value = Eisenstein.coerce(scalar)
        return ConstituentFullCochain(
            tuple((basis, coefficient * value) for basis, coefficient in self.terms)
        )

    def is_zero(self) -> bool:
        """Return whether no normalized terms remain."""

        return not self.terms


@dataclass(frozen=True, slots=True)
class _ReducedEntry:
    """One reduced ambient-cohomology coordinate with full labels."""

    index: int
    component: ConstituentCechComponent
    base_monomial: Monomial3
    fiber_monomial: Monomial2


def _bundles(
    extension: DPSurfaceSerreExt,
    parent_degree: int,
) -> tuple[DPSurfaceLineBundle, ...]:
    """Return the generator or syzygy line summands."""

    if parent_degree == 0:
        return extension.generator_bundles
    if parent_degree == 1:
        return extension.syzygy_bundles
    raise ValueError("Serre resolution degrees are zero and one")


def _ambient_labels(
    base_degree: int,
    fiber_degree: int,
    cohomology_degree: int,
) -> tuple[tuple[Monomial3, Monomial2], ...]:
    """Expand one deterministic ambient Künneth basis."""

    _space, records = _kunneth_space(
        base_degree,
        fiber_degree,
        cohomology_degree,
    )
    return tuple(
        (cast(Monomial3, base), cast(Monomial2, fiber))
        for _base_h, _fiber_h, base_basis, fiber_basis in records
        for base in base_basis
        for fiber in fiber_basis
    )


@cache
def _reduced_entries(
    extension: DPSurfaceSerreExt,
    total_degree: int,
) -> tuple[_ReducedEntry, ...]:
    """Recover the exact coordinate order of the reduced total complex."""

    entries = []
    index = 0
    for parent_degree in (0, 1):
        sheaf_degree = total_degree - parent_degree
        for bundle_index, bundle in enumerate(_bundles(extension, parent_degree)):
            for base_monomial, fiber_monomial in _ambient_labels(
                bundle.base_degree,
                bundle.fiber_degree,
                sheaf_degree,
            ):
                entries.append(
                    _ReducedEntry(
                        index,
                        ConstituentCechComponent(
                            parent_degree,
                            bundle_index,
                            0,
                            bundle.base_degree,
                            bundle.fiber_degree,
                        ),
                        base_monomial,
                        fiber_monomial,
                    )
                )
                index += 1
            for base_monomial, fiber_monomial in _ambient_labels(
                bundle.base_degree - 3,
                bundle.fiber_degree - 1,
                sheaf_degree + 1,
            ):
                entries.append(
                    _ReducedEntry(
                        index,
                        ConstituentCechComponent(
                            parent_degree,
                            bundle_index,
                            1,
                            bundle.base_degree - 3,
                            bundle.fiber_degree - 1,
                        ),
                        base_monomial,
                        fiber_monomial,
                    )
                )
                index += 1
    expected = extension.total.spaces.space(total_degree).dimension
    if index != expected:
        raise ValueError("full Čech labels do not match the reduced total basis")
    return tuple(entries)


@cache
def _product_cech_support(
    base_support: tuple[int, ...],
    fiber_support: tuple[int, ...],
) -> ProductProjectiveMonomialCechComplex:
    """Return one cached product-cover contraction."""

    return product_projective_monomial_cech_complex(
        (
            projective_monomial_cech_complex(
                ("x0", "x1", "x2"),
                tuple(-1 if index in base_support else 0 for index in range(3)),
                scalar_type=Eisenstein,
            ),
            projective_monomial_cech_complex(
                ("p0", "p1"),
                tuple(-1 if index in fiber_support else 0 for index in range(2)),
                scalar_type=Eisenstein,
            ),
        )
    )


def _product_cech(
    basis: ConstituentCechBasis | _ReducedEntry,
) -> ProductProjectiveMonomialCechComplex:
    """Select a contraction from one Laurent monomial pair."""

    return _product_cech_support(
        tuple(index for index, value in enumerate(basis.base_monomial) if value < 0),
        tuple(index for index, value in enumerate(basis.fiber_monomial) if value < 0),
    )


def _include(entry: _ReducedEntry) -> ConstituentFullCochain:
    """Include one ambient class by its canonical product Čech cocycle."""

    cech = _product_cech(entry)
    representative = cech.canonical_representative()
    degree = sum(factor.expected_cohomology_degree or 0 for factor in cech.factors)
    return ConstituentFullCochain(
        tuple(
            (
                ConstituentCechBasis(
                    entry.component,
                    entry.base_monomial,
                    entry.fiber_monomial,
                    cast(Cell, cell),
                ),
                cast(Eisenstein, coefficient),
            )
            for cell, coefficient in zip(
                cech.cells_at(degree),
                representative.coordinates,
                strict=True,
            )
            if not coefficient.is_zero()
        )
    )


def _homotopy(cochain: ConstituentFullCochain) -> ConstituentFullCochain:
    """Apply the structurally signed product-cover contraction."""

    groups: dict[
        tuple[ConstituentCechComponent, Monomial3, Monomial2],
        dict[Cell, Eisenstein],
    ] = defaultdict(dict)
    for basis, coefficient in cochain.terms:
        groups[
            (basis.component, basis.base_monomial, basis.fiber_monomial)
        ][basis.cell] = coefficient
    result = []
    for (component, base_monomial, fiber_monomial), values in groups.items():
        sample = ConstituentCechBasis(
            component,
            base_monomial,
            fiber_monomial,
            next(iter(values)),
        )
        cech = _product_cech(sample)
        degrees = {
            sum(len(simplex) - 1 for simplex in cell)
            for cell in values
        }
        if len(degrees) != 1:
            raise ValueError("one Laurent monomial occupies multiple Čech degrees")
        degree = next(iter(degrees))
        contracted = cech.contracting_homotopy(cech.cochain(degree, values))
        sign = -1 if component.structural_degree % 2 else 1
        for cell, coefficient in zip(
            cech.cells_at(degree - 1),
            contracted.coordinates,
            strict=True,
        ):
            if not coefficient.is_zero():
                result.append(
                    (
                        ConstituentCechBasis(
                            component,
                            base_monomial,
                            fiber_monomial,
                            cast(Cell, cell),
                        ),
                        cast(Eisenstein, coefficient) * sign,
                    )
                )
    return ConstituentFullCochain(tuple(result))


def _cech_differential(cochain: ConstituentFullCochain) -> ConstituentFullCochain:
    """Apply the signed two-factor Čech differential."""

    result = []
    for basis, coefficient in cochain.terms:
        preceding_degree = 0
        structural_sign = -1 if basis.component.structural_degree % 2 else 1
        for factor_index, (simplex, size) in enumerate(
            zip(basis.cell, (3, 2), strict=True)
        ):
            for vertex in range(size):
                if vertex in simplex:
                    continue
                target_simplex = tuple(sorted((*simplex, vertex)))
                local_sign = -1 if target_simplex.index(vertex) % 2 else 1
                tensor_sign = -1 if preceding_degree % 2 else 1
                target_cell = list(basis.cell)
                target_cell[factor_index] = target_simplex
                result.append(
                    (
                        ConstituentCechBasis(
                            basis.component,
                            basis.base_monomial,
                            basis.fiber_monomial,
                            cast(Cell, tuple(target_cell)),
                        ),
                        coefficient * structural_sign * local_sign * tensor_sign,
                    )
                )
            preceding_degree += len(simplex) - 1
    return ConstituentFullCochain(tuple(result))


def _component(
    extension: DPSurfaceSerreExt,
    parent_degree: int,
    bundle_index: int,
    koszul_degree: int,
) -> ConstituentCechComponent:
    """Return one structurally adjacent component with exact line degrees."""

    bundle = _bundles(extension, parent_degree)[bundle_index]
    return ConstituentCechComponent(
        parent_degree,
        bundle_index,
        koszul_degree,
        bundle.base_degree - 3 * koszul_degree,
        bundle.fiber_degree - koszul_degree,
    )


def _add_base_polynomial(
    result: list[tuple[ConstituentCechBasis, Eisenstein]],
    basis: ConstituentCechBasis,
    coefficient: Eisenstein,
    target: ConstituentCechComponent,
    polynomial: Polynomial,
) -> None:
    """Append multiplication by one homogeneous P2 polynomial."""

    for exponents, scalar in polynomial.terms:
        result.append(
            (
                ConstituentCechBasis(
                    target,
                    cast(
                        Monomial3,
                        tuple(
                            left + right
                            for left, right in zip(
                                basis.base_monomial,
                                exponents,
                                strict=True,
                            )
                        ),
                    ),
                    basis.fiber_monomial,
                    basis.cell,
                ),
                coefficient * cast(Eisenstein, scalar),
            )
        )


def _add_equation(
    result: list[tuple[ConstituentCechBasis, Eisenstein]],
    basis: ConstituentCechBasis,
    coefficient: Eisenstein,
    target: ConstituentCechComponent,
    surface_factor: int,
) -> None:
    """Append the selected cubic-pencil hypersurface equation."""

    cox = schoen_geometry().cover.cox
    terms = (
        ((1, 0), cox.cubic_f, Eisenstein(1)),
        ((0, 1), cox.cubic_g, Eisenstein(1)),
    ) if surface_factor == 1 else (
        ((0, 1), cox.cubic_f, Eisenstein(2)),
        ((1, 0), cox.cubic_g, Eisenstein(1)),
    )
    for fiber_exponents, polynomial, prefactor in terms:
        for base_exponents, scalar in polynomial.terms:
            result.append(
                (
                    ConstituentCechBasis(
                        target,
                        cast(
                            Monomial3,
                            tuple(
                                left + right
                                for left, right in zip(
                                    basis.base_monomial,
                                    base_exponents,
                                    strict=True,
                                )
                            ),
                        ),
                        cast(
                            Monomial2,
                            tuple(
                                left + right
                                for left, right in zip(
                                    basis.fiber_monomial,
                                    fiber_exponents,
                                    strict=True,
                                )
                            ),
                        ),
                        basis.cell,
                    ),
                    coefficient * prefactor * cast(Eisenstein, scalar),
                )
            )


def _perturbation(
    cochain: ConstituentFullCochain,
    extension: DPSurfaceSerreExt,
) -> ConstituentFullCochain:
    """Apply Hilbert--Burch and hypersurface-Koszul maps."""

    result = []
    matrix = extension.scheme.resolution.matrix
    for basis, coefficient in cochain.terms:
        component = basis.component
        if component.koszul_degree == 1:
            _add_equation(
                result,
                basis,
                coefficient * (-1 if component.parent_degree % 2 else 1),
                _component(
                    extension,
                    component.parent_degree,
                    component.bundle_index,
                    0,
                ),
                extension.surface_factor,
            )
        if component.parent_degree == 0:
            for syzygy_index in range(len(matrix[0])):
                polynomial = matrix[component.bundle_index][syzygy_index]
                if not polynomial.is_zero():
                    _add_base_polynomial(
                        result,
                        basis,
                        coefficient,
                        _component(
                            extension,
                            1,
                            syzygy_index,
                            component.koszul_degree,
                        ),
                        polynomial,
                    )
    return ConstituentFullCochain(tuple(result))


def _full_differential(
    cochain: ConstituentFullCochain,
    extension: DPSurfaceSerreExt,
) -> ConstituentFullCochain:
    """Apply the raw Čech plus structural total differential."""

    return _cech_differential(cochain) + _perturbation(cochain, extension)


def _projection_index(
    basis: ConstituentCechBasis,
    target_indices: dict[
        tuple[ConstituentCechComponent, Monomial3, Monomial2],
        int,
    ],
) -> int | None:
    """Project a canonical product cocycle to one reduced coordinate."""

    supports = (
        tuple(index for index, value in enumerate(basis.base_monomial) if value < 0),
        tuple(index for index, value in enumerate(basis.fiber_monomial) if value < 0),
    )
    if any(
        support and len(support) != size
        for support, size in zip(supports, (3, 2), strict=True)
    ):
        return None
    pivot = cast(
        Cell,
        tuple(
            tuple(range(size)) if support else (0,)
            for support, size in zip(supports, (3, 2), strict=True)
        ),
    )
    if basis.cell != pivot:
        return None
    return target_indices.get(
        (basis.component, basis.base_monomial, basis.fiber_monomial)
    )


@cache
def _transferred_map(
    extension: DPSurfaceSerreExt,
    total_degree: int,
) -> tuple[SparseMap, int]:
    """Transfer one full differential to the ambient-cohomology basis."""

    source_entries = _reduced_entries(extension, total_degree)
    target_entries = _reduced_entries(extension, total_degree + 1)
    target_indices = {
        (entry.component, entry.base_monomial, entry.fiber_monomial): entry.index
        for entry in target_entries
    }
    rows: list[dict[int, Eisenstein]] = [dict() for _ in target_entries]
    maximum_depth = 0
    for source in source_entries:
        current = _include(source)
        depth = 0
        while not current.is_zero():
            image = _perturbation(current, extension)
            for basis, coefficient in image.terms:
                target_index = _projection_index(basis, target_indices)
                if target_index is not None:
                    rows[target_index][source.index] = rows[target_index].get(
                        source.index,
                        Eisenstein(0),
                    ) + coefficient
            current = _homotopy(image).scale(-1)
            depth += 1
            if depth > 8:
                raise ValueError("constituent Čech transfer did not terminate")
        maximum_depth = max(maximum_depth, depth)
    return (
        SparseMap(
            extension.total.spaces.space(total_degree),
            extension.total.spaces.space(total_degree + 1),
            _freeze_rows(rows),
        ),
        maximum_depth,
    )


def _corrected_basis_inclusion(
    entry: _ReducedEntry,
    extension: DPSurfaceSerreExt,
) -> tuple[ConstituentFullCochain, int]:
    """Return the finite HPL inclusion series for one reduced basis element."""

    current = _include(entry)
    result = current
    depth = 0
    while not current.is_zero():
        current = _homotopy(_perturbation(current, extension)).scale(-1)
        if not current.is_zero():
            result = result + current
        depth += 1
        if depth > 8:
            raise ValueError("constituent corrected inclusion did not terminate")
    return result, depth


def _lift_vector(
    extension: DPSurfaceSerreExt,
    vector: CoordinateVector,
    total_degree: int,
) -> tuple[ConstituentFullCochain, int]:
    """Lift one reduced coordinate vector through the exact contraction."""

    if vector.space != extension.total.spaces.space(total_degree):
        raise ValueError("the reduced vector belongs to a different total degree")
    result = ConstituentFullCochain()
    maximum_depth = 0
    for entry, coefficient in zip(
        _reduced_entries(extension, total_degree),
        vector.coordinates,
        strict=True,
    ):
        if coefficient.is_zero():
            continue
        lifted, depth = _corrected_basis_inclusion(entry, extension)
        result = result + lifted.scale(coefficient)
        maximum_depth = max(maximum_depth, depth)
    return result, maximum_depth


def _transferred_matches_reduced(extension: DPSurfaceSerreExt) -> bool:
    """Compare every transferred map with the existing finite total exactly."""

    return all(
        transferred.rows == tuple(
            tuple(
                (column, cast(Eisenstein, value))
                for column, value in enumerate(row)
                if not value.is_zero()
            )
            for row in extension.total.differential(degree).rows
        )
        for degree in extension.total.degrees
        for transferred, _depth in (_transferred_map(extension, degree),)
    )


@dataclass(frozen=True, slots=True)
class PublishedConstituentFullCech:
    """One selected mixed ray and its corrected full Čech representative."""

    alignment: PublishedConstituentRayAlignment
    representative: ConstituentFullCochain
    inclusion_depth: int
    transferred_matches_reduced: bool

    @property
    def full_closed(self) -> bool:
        """Return whether the raw full differential annihilates the lift."""

        return _full_differential(
            self.representative,
            self.alignment.action.derived.extension,
        ).is_zero()

    @property
    def koszul_term_count(self) -> int:
        """Count nonzero terms in the hypersurface correction summands."""

        return sum(
            basis.component.koszul_degree == 1
            for basis, _coefficient in self.representative.terms
        )

    @property
    def exact(self) -> bool:
        """Return all transfer and full-closure gates."""

        return (
            self.alignment.closed
            and self.transferred_matches_reduced
            and self.full_closed
            and self.koszul_term_count > 0
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the sparse full lift without claiming local freeness."""

        return {
            "constituent": self.alignment.action.published.name,
            "source_character": {
                "P": str(self.alignment.source_character[0]),
                "T": str(self.alignment.source_character[1]),
            },
            "full_term_count": len(self.representative.terms),
            "koszul_term_count": self.koszul_term_count,
            "inclusion_depth": self.inclusion_depth,
            "transferred_maps_match_reduced_total": self.transferred_matches_reduced,
            "full_cech_closed": self.full_closed,
            "exact": self.exact,
            "local_dualizing_units_evaluated": False,
            "status": (
                "source-selected mixed ray lifted to the full dP9 standard cover; "
                "local-unit evaluation remains open"
            ),
        }


@cache
def published_constituent_full_cech(
) -> tuple[PublishedConstituentFullCech, ...]:
    """Lift both selected constituent rays to full standard-cover cocycles."""

    results = []
    for alignment in published_constituent_ray_alignments():
        extension = alignment.action.derived.extension
        lifted, depth = _lift_vector(extension, alignment.representative, 1)
        result = PublishedConstituentFullCech(
            alignment,
            lifted,
            depth,
            _transferred_matches_reduced(extension),
        )
        if not result.exact:
            raise ValueError("a selected constituent full Čech lift failed")
        results.append(result)
    return tuple(results)


def write_published_constituent_full_cech(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed full constituent Čech certificate."""

    payload: dict[str, object] = {
        "schema": "published-constituent-full-cech-v1",
        "constituents": [
            result.as_record() for result in published_constituent_full_cech()
        ],
        "all_full_cech_lifts_exact": True,
        "pure_cech_trivial_character_cones_retired": True,
        "next_required_object": (
            "evaluation of each mixed cocycle in the six local dualizing "
            "algebras, followed by finite locally free presentations"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the full selected constituent Čech artifact."""

    payload = write_published_constituent_full_cech()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"all_full_cech_lifts_exact: {payload['all_full_cech_lifts_exact']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ConstituentCechBasis",
    "ConstituentFullCochain",
    "PublishedConstituentFullCech",
    "published_constituent_full_cech",
]
