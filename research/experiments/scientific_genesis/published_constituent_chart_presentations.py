"""Materialize affine presentations of the selected Serre constituents.

Owns:
    Six-chart dehomogenization of the mixed parent-one extension maps, exact
    Hilbert--Burch pushout relations, quotient identities, and local-free cover.

Depends on:
    The full selected constituent Čech lifts, six local dualizing units, exact
    blow-up charts, and sparse Eisenstein polynomial arithmetic.

Must not:
    Substitute the retired projective pushout maps, infer overlap transitions
    from matching ranks, or claim quotient deck descent.

Phase 0:
    Research-only affine module presentations; overlap gluing remains open.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialMatrix
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pencil import BlowupChart, tier_a_pencil_model

from .published_constituent_full_cech import (
    PublishedConstituentFullCech,
    published_constituent_full_cech,
)
from .published_constituent_local_units import (
    LocalDualizingUnit,
    published_constituent_local_units,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/published_constituent_chart_presentations.json"
)


def _variables() -> tuple[Polynomial, Polynomial, Polynomial]:
    """Return the two affine plane coordinates and one fiber coordinate."""

    return tuple(
        Polynomial.monomial(
            tuple(int(index == position) for index in range(3)),
            scalar_type=Eisenstein,
        )
        for position in range(3)
    )  # type: ignore[return-value]


def _chart_images(chart: BlowupChart) -> tuple[Polynomial | Eisenstein, ...]:
    """Return homogeneous base coordinates in one affine chart ring."""

    first, second, _fiber = _variables()
    images: list[Polynomial | Eisenstein] = []
    local = iter((first, second))
    for coordinate in range(3):
        images.append(Eisenstein(1) if coordinate == chart.base_pivot else next(local))
    return tuple(images)


def _affine_base_polynomial(
    polynomial: Polynomial,
    chart: BlowupChart,
) -> Polynomial:
    """Dehomogenize one P2 polynomial in the three-variable chart ring."""

    return polynomial.substitute(_chart_images(chart))


def _affine_laurent_term(
    base_monomial: tuple[int, int, int],
    fiber_monomial: tuple[int, int],
    chart: BlowupChart,
    coefficient: Eisenstein,
) -> Polynomial:
    """Dehomogenize one term known to be regular on its singleton chart."""

    exponents = []
    for coordinate, exponent in enumerate(base_monomial):
        if coordinate != chart.base_pivot:
            if exponent < 0:
                raise ValueError("a base pole escaped its declared affine chart")
            exponents.append(exponent)
    fiber_pivot = 0 if chart.fiber_chart == "mu" else 1
    for coordinate, exponent in enumerate(fiber_monomial):
        if coordinate != fiber_pivot:
            if exponent < 0:
                raise ValueError("a fiber pole escaped its declared affine chart")
            exponents.append(exponent)
    return Polynomial.monomial(
        tuple(exponents),
        coefficient,
        scalar_type=Eisenstein,
    )


def _extension_map(
    result: PublishedConstituentFullCech,
    chart: BlowupChart,
) -> tuple[Polynomial, ...]:
    """Extract the regular parent-one extension map on one affine chart."""

    extension = result.alignment.action.derived.extension
    fiber_pivot = 0 if chart.fiber_chart == "mu" else 1
    maps = []
    for syzygy_index in range(len(extension.syzygy_bundles)):
        value = Polynomial.zero(3, scalar_type=Eisenstein)
        for basis, coefficient in result.representative.terms:
            if not (
                basis.component.parent_degree == 1
                and basis.component.bundle_index == syzygy_index
                and basis.component.koszul_degree == 0
                and basis.cell == ((chart.base_pivot,), (fiber_pivot,))
            ):
                continue
            value += _affine_laurent_term(
                basis.base_monomial,
                basis.fiber_monomial,
                chart,
                coefficient,
            )
        maps.append(value)
    return tuple(maps)


def _relation(
    result: PublishedConstituentFullCech,
    chart: BlowupChart,
    extension_map: tuple[Polynomial, ...],
) -> PolynomialMatrix:
    """Push out the localized Hilbert--Burch relation by the mixed ray."""

    matrix = result.alignment.action.derived.extension.scheme.resolution.matrix
    if len(extension_map) != len(matrix[0]):
        raise ValueError("extension map must have one entry per syzygy")
    return PolynomialMatrix(
        tuple(
            tuple(
                _affine_base_polynomial(matrix[row][column], chart)
                for row in range(len(matrix))
            )
            + (-extension_map[column],)
            for column in range(len(matrix[0]))
        )
    )


def _quotient(
    result: PublishedConstituentFullCech,
    chart: BlowupChart,
) -> PolynomialMatrix:
    """Return the local pushout quotient row onto the ideal sheaf."""

    scheme = result.alignment.action.derived.extension.scheme
    return PolynomialMatrix(
        (
            tuple(
                _affine_base_polynomial(generator, chart)
                for generator in scheme.ideal_generators
            )
            + (Polynomial.zero(3, scalar_type=Eisenstein),),
        )
    )


def _evaluate(polynomial: Polynomial, point: tuple[Eisenstein, ...]) -> Eisenstein:
    """Evaluate one exact affine polynomial."""

    return cast(Eisenstein, polynomial.substitute(point).coefficient(()))


def _support_point(
    chart: BlowupChart,
    unit: LocalDualizingUnit,
) -> tuple[Eisenstein, Eisenstein, Eisenstein]:
    """Return the support point in the declared affine chart coordinates."""

    fiber_pivot = 0 if chart.fiber_chart == "mu" else 1
    other = 1 - fiber_pivot
    parameter = unit.fiber_parameter
    if parameter[fiber_pivot].is_zero():
        raise ValueError("the support point is absent from this fiber chart")
    return Eisenstein(0), Eisenstein(0), parameter[other] / parameter[fiber_pivot]


def _residue_unit(
    relation: PolynomialMatrix,
    extension_map: tuple[Polynomial, ...],
    point: tuple[Eisenstein, Eisenstein, Eisenstein],
) -> tuple[int, int]:
    """Return boundary and augmented ranks at one supported residue field."""

    image_rows = tuple(
        tuple(
            _evaluate(relation.rows[syzygy][generator], point)
            for syzygy in range(relation.shape[0])
        )
        for generator in range(relation.shape[1] - 1)
    )
    values = tuple(_evaluate(entry, point) for entry in extension_map)
    image_rank = Matrix(image_rows, scalar_type=Eisenstein).rank()
    augmented_rank = Matrix(
        (*image_rows, values),
        scalar_type=Eisenstein,
    ).rank()
    return image_rank, augmented_rank


@dataclass(frozen=True, slots=True)
class ConstituentChartPresentation:
    """One affine finite presentation of a selected rank-two constituent."""

    constituent: str
    chart: BlowupChart
    extension_map: tuple[Polynomial, ...]
    relation: PolynomialMatrix
    quotient: PolynomialMatrix
    support_image_rank: int
    support_augmented_rank: int
    support_unit: LocalDualizingUnit

    @property
    def relation_composes_to_zero(self) -> bool:
        """Return the exact quotient-after-relation identity."""

        quotient_column = PolynomialMatrix(
            tuple((entry,) for entry in self.quotient.rows[0])
        )
        return self.relation.compose(quotient_column).is_zero()

    @property
    def middle_rank(self) -> int:
        """Return the generic cokernel rank of the presentation."""

        return self.relation.shape[1] - self.relation.shape[0]

    @property
    def support_local_free(self) -> bool:
        """Return the exact residue-unit local-freeness gate."""

        return (
            self.support_unit.unit_in_local_dualizing_algebra
            and self.support_augmented_rank == self.support_image_rank + 1
            and self.support_augmented_rank == len(self.extension_map)
        )

    @property
    def complement_local_free(self) -> bool:
        """Use the ideal-unit cover away from its finite support."""

        return self.relation_composes_to_zero and bool(self.quotient.rows[0][:-1])

    @property
    def exact(self) -> bool:
        """Return all affine presentation and local-free cover gates."""

        return (
            self.middle_rank == 2
            and self.relation_composes_to_zero
            and self.support_local_free
            and self.complement_local_free
        )

    def as_record(self) -> dict[str, object]:
        """Serialize one chart presentation without inventing overlap maps."""

        def polynomial_record(polynomial: Polynomial) -> list[dict[str, object]]:
            return [
                {"monomial": list(monomial), "coefficient": str(coefficient)}
                for monomial, coefficient in polynomial.terms
            ]

        return {
            "constituent": self.constituent,
            "chart": self.chart.name,
            "relation_shape": list(self.relation.shape),
            "middle_rank": self.middle_rank,
            "extension_map": [
                polynomial_record(polynomial) for polynomial in self.extension_map
            ],
            "relation_composes_to_zero": self.relation_composes_to_zero,
            "support_image_rank": self.support_image_rank,
            "support_augmented_rank": self.support_augmented_rank,
            "support_local_free": self.support_local_free,
            "complement_local_free": self.complement_local_free,
            "exact": self.exact,
        }


def _presentation(
    result: PublishedConstituentFullCech,
    chart: BlowupChart,
    unit: LocalDualizingUnit,
) -> ConstituentChartPresentation:
    """Construct one exact affine pushout from the selected mixed cocycle."""

    extension_map = _extension_map(result, chart)
    relation = _relation(result, chart, extension_map)
    image_rank, augmented_rank = _residue_unit(
        relation,
        extension_map,
        _support_point(chart, unit),
    )
    presentation = ConstituentChartPresentation(
        result.alignment.action.derived.extension.scheme.name,
        chart,
        extension_map,
        relation,
        _quotient(result, chart),
        image_rank,
        augmented_rank,
        unit,
    )
    if not presentation.exact:
        raise ValueError("a selected constituent chart presentation failed")
    return presentation


@cache
def published_constituent_chart_presentations(
) -> tuple[ConstituentChartPresentation, ...]:
    """Materialize all twelve selected W1/W2 affine presentations."""

    model = tier_a_pencil_model()
    full = published_constituent_full_cech()
    units = published_constituent_local_units()
    by_unit = {(unit.constituent, unit.frame.pivot): unit for unit in units}
    return tuple(
        _presentation(
            result,
            chart,
            by_unit[(result.alignment.action.derived.extension.scheme.name, chart.base_pivot)],
        )
        for result in full
        for chart in model.blowup_atlas.charts
    )


def write_published_constituent_chart_presentations(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed affine constituent presentations."""

    presentations = published_constituent_chart_presentations()
    payload: dict[str, object] = {
        "schema": "published-constituent-chart-presentations-v1",
        "presentations": [item.as_record() for item in presentations],
        "presentation_count": len(presentations),
        "all_affine_presentations_exact": all(item.exact for item in presentations),
        "selected_mixed_cocycles_used": True,
        "retired_projective_pushout_maps_used": False,
        "overlap_transition_matrices_materialized": False,
        "next_required_object": (
            "presentation comparison maps on all ordered chart overlaps, "
            "including the parent-zero Cech gauge components"
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
    """Regenerate the exact selected constituent chart presentations."""

    payload = write_published_constituent_chart_presentations()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"presentation_count: {payload['presentation_count']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ConstituentChartPresentation",
    "published_constituent_chart_presentations",
]
