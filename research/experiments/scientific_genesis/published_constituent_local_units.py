"""Evaluate the selected constituent rays in the local dualizing algebras.

Owns:
    Exact support-fiber evaluation of the parent-one Čech lifts, quotient by
    the Hilbert--Burch residue image, chart independence, and local-unit gates.

Depends on:
    Full selected dP9 Čech representatives, exact coordinate-point lci frames,
    the frozen cubic pencils, and finite Eisenstein linear algebra.

Must not:
    Infer global transition matrices from stalkwise units, reuse the retired
    pure Čech ray, or claim equivariant quotient descent.

Phase 0:
    Research-only local-freeness certificate for the selected Serre rays.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.dp9_serre_ext import DPSurfaceSerreExt
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .local_constituent_frames import (
    LocalKoszulSerreFrame,
    published_local_constituent_frames,
)
from .published_constituent_full_cech import (
    ConstituentFullCochain,
    PublishedConstituentFullCech,
    published_constituent_full_cech,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/published_constituent_local_units.json"


def _evaluate_monomial(
    monomial: tuple[int, ...],
    coordinates: tuple[Eisenstein, ...],
) -> Eisenstein:
    """Evaluate one Laurent monomial where its declared chart is regular."""

    value = Eisenstein(1)
    for exponent, coordinate in zip(monomial, coordinates, strict=True):
        if exponent < 0 and coordinate.is_zero():
            raise ZeroDivisionError("a Laurent pole escaped its declared chart")
        value *= coordinate**exponent
    return value


def _projective_value(
    extension: DPSurfaceSerreExt,
    representative: ConstituentFullCochain,
    pivot: int,
    fiber_chart: int,
    fiber_parameter: tuple[Eisenstein, Eisenstein],
) -> tuple[Eisenstein, ...]:
    """Evaluate the parent-one local extension map on one affine chart."""

    base_point = tuple(Eisenstein(int(index == pivot)) for index in range(3))
    values = []
    for syzygy_index in range(len(extension.syzygy_bundles)):
        value = Eisenstein(0)
        for basis, coefficient in representative.terms:
            if not (
                basis.component.parent_degree == 1
                and basis.component.bundle_index == syzygy_index
                and basis.component.koszul_degree == 0
                and basis.cell == ((pivot,), (fiber_chart,))
            ):
                continue
            value += (
                coefficient
                * _evaluate_monomial(basis.base_monomial, base_point)
                * _evaluate_monomial(basis.fiber_monomial, fiber_parameter)
            )
        values.append(value)
    return tuple(values)


def _fiber_parameter(
    surface_factor: int,
    pivot: int,
) -> tuple[Eisenstein, Eisenstein]:
    """Return the exact fiber point of one coordinate support point."""

    point = tuple(int(index == pivot) for index in range(3))
    cox = schoen_geometry().cover.cox
    f_value = cast(Eisenstein, cox.cubic_f.substitute(point).coefficient(()))
    g_value = cast(Eisenstein, cox.cubic_g.substitute(point).coefficient(()))
    if surface_factor == 1:
        return g_value, -f_value
    if surface_factor == 2:
        return 2 * f_value, -g_value
    raise ValueError("dP9 surface factors are one and two")


def _residue_image_rows(
    extension: DPSurfaceSerreExt,
    pivot: int,
) -> tuple[tuple[Eisenstein, ...], ...]:
    """Evaluate the transposed Hilbert--Burch image at one support point."""

    point = tuple(int(index == pivot) for index in range(3))
    matrix = extension.scheme.resolution.matrix
    return tuple(
        tuple(
            cast(Eisenstein, polynomial.substitute(point).coefficient(()))
            for polynomial in row
        )
        for row in matrix
    )


def _rank(rows: tuple[tuple[Eisenstein, ...], ...]) -> int:
    """Return exact row rank over the Eisenstein field."""

    return Matrix(rows, scalar_type=Eisenstein).rank()


@dataclass(frozen=True, slots=True)
class LocalDualizingUnit:
    """One selected extension class in a local lci dualizing module."""

    constituent: str
    frame: LocalKoszulSerreFrame
    fiber_parameter: tuple[Eisenstein, Eisenstein]
    chart_values: tuple[tuple[int, tuple[Eisenstein, ...]], ...]
    residue_image: tuple[tuple[Eisenstein, ...], ...]

    @property
    def residue_image_rank(self) -> int:
        """Return the rank of the local Hilbert--Burch coboundaries."""

        return _rank(self.residue_image)

    @property
    def local_ext_residue_dimension(self) -> int:
        """Return the residue-field dimension of the local Ext-one module."""

        return len(self.chart_values[0][1]) - self.residue_image_rank

    @property
    def every_chart_nonzero_in_cokernel(self) -> bool:
        """Return whether each regular fiber chart gives a nonzero Ext residue."""

        return all(
            _rank((*self.residue_image, values)) > self.residue_image_rank
            for _chart, values in self.chart_values
        )

    @property
    def chart_independent_modulo_boundaries(self) -> bool:
        """Return whether chart representatives differ by a residue boundary."""

        first = self.chart_values[0][1]
        return all(
            _rank(
                (
                    *self.residue_image,
                    tuple(
                        right - left
                        for left, right in zip(first, values, strict=True)
                    ),
                )
            )
            == self.residue_image_rank
            for _chart, values in self.chart_values[1:]
        )

    @property
    def unit_in_local_dualizing_algebra(self) -> bool:
        """Apply the lci-Gorenstein residue criterion for a local unit."""

        return (
            self.frame.exact
            and self.frame.algebra.is_local_complete_intersection
            and self.local_ext_residue_dimension == 1
            and self.every_chart_nonzero_in_cokernel
            and self.chart_independent_modulo_boundaries
        )

    def as_record(self) -> dict[str, object]:
        """Serialize one stalkwise unit and its exact quotient calculation."""

        return {
            "constituent": self.constituent,
            "support_pivot": self.frame.pivot,
            "local_generators": [list(item) for item in self.frame.algebra.generators],
            "local_length": self.frame.algebra.length,
            "fiber_parameter": [str(value) for value in self.fiber_parameter],
            "chart_values": [
                {
                    "fiber_chart": chart,
                    "syzygy_values": [str(value) for value in values],
                }
                for chart, values in self.chart_values
            ],
            "residue_image_rank": self.residue_image_rank,
            "local_ext_residue_dimension": self.local_ext_residue_dimension,
            "every_chart_nonzero_in_cokernel": self.every_chart_nonzero_in_cokernel,
            "chart_independent_modulo_boundaries": (
                self.chart_independent_modulo_boundaries
            ),
            "unit_in_local_dualizing_algebra": (
                self.unit_in_local_dualizing_algebra
            ),
        }


def evaluate_local_unit(
    extension: DPSurfaceSerreExt,
    representative: ConstituentFullCochain,
    frame: LocalKoszulSerreFrame,
) -> LocalDualizingUnit:
    """Evaluate any exact constituent cocycle without assuming it is a unit."""

    parameter = _fiber_parameter(extension.surface_factor, frame.pivot)
    chart_values = tuple(
        (
            chart,
            _projective_value(
                extension, representative, frame.pivot, chart, parameter
            ),
        )
        for chart, coordinate in enumerate(parameter)
        if not coordinate.is_zero()
    )
    unit = LocalDualizingUnit(
        extension.scheme.name,
        frame,
        parameter,
        chart_values,
        _residue_image_rows(extension, frame.pivot),
    )
    return unit


def _local_unit(
    result: PublishedConstituentFullCech,
    frame: LocalKoszulSerreFrame,
) -> LocalDualizingUnit:
    """Require the published selected ray to be a local dualizing unit."""

    unit = evaluate_local_unit(
        result.alignment.action.derived.extension,
        result.representative,
        frame,
    )
    if not unit.unit_in_local_dualizing_algebra:
        raise ValueError("a source-selected Serre ray is not a local dualizing unit")
    return unit


@cache
def published_constituent_local_units() -> tuple[LocalDualizingUnit, ...]:
    """Evaluate the selected W1/W2 rays at all six supported points."""

    full = published_constituent_full_cech()
    frames = published_local_constituent_frames()
    return tuple(
        _local_unit(result, frame)
        for result, group in zip(full, frames, strict=True)
        for frame in group
    )


def write_published_constituent_local_units(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed six-stalk local-unit certificate."""

    units = published_constituent_local_units()
    payload: dict[str, object] = {
        "schema": "published-constituent-local-units-v1",
        "local_units": [unit.as_record() for unit in units],
        "unit_count": len(units),
        "all_selected_rays_are_local_units": all(
            unit.unit_in_local_dualizing_algebra for unit in units
        ),
        "constituent_middle_terms_locally_free_at_support": True,
        "global_transition_matrices_materialized": False,
        "next_required_object": (
            "finite locally free chart presentations induced by the six units, "
            "with exact overlap transitions and deck linearization"
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
    """Regenerate the exact local dualizing-unit artifact."""

    payload = write_published_constituent_local_units()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "all_selected_rays_are_local_units: "
        f"{payload['all_selected_rays_are_local_units']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "LocalDualizingUnit",
    "evaluate_local_unit",
    "published_constituent_local_units",
]
