"""Compute presentation Hom complexes on the Schoen cover.

Owns:
    Multigraded line terms for two exact Serre presentations, factor-aware
    multiplication by their polynomial differentials, and the signed global
    cover totalization used to measure the outer-extension cohomology.

Depends on:
    Exact Schoen cover line-bundle Koszul complexes, the generic polynomial
    presentation Hom complex, and the bounded monomial Serre rays.

Must not:
    Identify cover cohomology with quotient-invariant Ext, select a physical
    extension from a nonzero dimension, or bypass honest deck-action descent.

Phase 0:
    The cover-level outer Hom calculation is executable for declared rays;
    quotient invariants, extension representatives, stability, and physics
    remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from onetheory.math.homological import (
    Bicomplex,
    CochainComplex,
    LinearMap,
    VectorSpace,
)

from .pencil import tier_a_pencil_model
from .polynomial_hom import PolynomialHomComplex, polynomial_hom_complex
from .schoen_linebundles import SchoenLineBundle, schoen_line_bundle
from .serre_pushout import SerrePushoutCandidate
from .tier_b_outer import _candidate
from .tier_b_serre_extensions import TierBSerreExtensionRay

Twist = tuple[int, int, int]
LineDegree = tuple[int, int, int]


def _line_degree(
    factor: int,
    scalar_shift: int,
    twist: Twist,
) -> LineDegree:
    """Convert one graded presentation shift into a Schoen line degree."""

    if factor not in (0, 1):
        raise ValueError("Schoen constituent factors are indexed by zero and one")
    return tuple(
        twist[index] - scalar_shift * int(index == factor)
        for index in range(3)
    )


@dataclass(frozen=True, slots=True)
class SchoenPresentation:
    """One pushed-out presentation with an explicit factor and divisor twist."""

    ray: TierBSerreExtensionRay
    candidate: SerrePushoutCandidate
    factor: int
    twist: Twist
    source_line_degrees: tuple[LineDegree, ...]
    target_line_degrees: tuple[LineDegree, ...]

    @property
    def polynomial_factor(self) -> str:
        """Return the ambient projective factor carrying the presentation."""

        return "x" if self.factor == 0 else "u"


def schoen_presentation(
    ray: TierBSerreExtensionRay,
    factor: int,
    twist: Twist,
) -> SchoenPresentation:
    """Build one exact multigraded presentation on the Schoen cover."""

    if len(twist) != 3 or any(
        isinstance(value, bool) or not isinstance(value, int) for value in twist
    ):
        raise TypeError("Schoen presentation twists must be integral triples")
    candidate = _candidate(ray, tier_a_pencil_model())
    source_lines = tuple(
        _line_degree(factor, shift, twist)
        for shift in candidate.source_shifts
    )
    target_lines = tuple(
        _line_degree(factor, shift, twist)
        for shift in candidate.target_shifts
    )
    return SchoenPresentation(
        ray,
        candidate,
        factor,
        twist,
        source_lines,
        target_lines,
    )


def _hom_lines(
    target: tuple[LineDegree, ...],
    source: tuple[LineDegree, ...],
) -> tuple[LineDegree, ...]:
    """Return target-minus-source line degrees in Hom basis order."""

    return tuple(
        tuple(
            target_value - source_value
            for target_value, source_value in zip(
                target_degree,
                source_degree,
                strict=True,
            )
        )
        for target_degree in target
        for source_degree in source
    )


def _hom_term_lines(
    left: SchoenPresentation,
    right: SchoenPresentation,
) -> tuple[tuple[int, tuple[LineDegree, ...]], ...]:
    """Build the four multigraded terms of the presentation Hom complex."""

    return (
        (
            -1,
            _hom_lines(left.source_line_degrees, right.target_line_degrees),
        ),
        (
            0,
            _hom_lines(left.target_line_degrees, right.target_line_degrees)
            + _hom_lines(left.source_line_degrees, right.source_line_degrees),
        ),
        (
            1,
            _hom_lines(left.target_line_degrees, right.source_line_degrees),
        ),
    )


def _line_sum_space(
    name: str,
    bundles: tuple[SchoenLineBundle, ...],
    degree: int,
) -> VectorSpace:
    """Build one ordered direct sum of cover line-bundle spaces."""

    if not bundles:
        return VectorSpace(name, (), schoen_line_bundle(0, 0, 0).complex.spaces.scalar_type)
    result = bundles[0].complex.spaces.space(degree)
    for bundle in bundles[1:]:
        result = result.direct_sum(bundle.complex.spaces.space(degree))
    return result


def _term_bundles(
    lines: tuple[tuple[int, tuple[LineDegree, ...]], ...],
) -> tuple[tuple[int, tuple[SchoenLineBundle, ...]], ...]:
    """Construct the exact cover line bundle for every Hom basis element."""

    return tuple(
        (
            degree,
            tuple(schoen_line_bundle(*line_degree) for line_degree in line_degrees),
        )
        for degree, line_degrees in lines
    )


def _direct_sum_maps(maps: tuple[LinearMap, ...]) -> LinearMap:
    """Assemble a block-diagonal map over all Hom line terms."""

    if not maps:
        raise ValueError("a direct-sum differential needs at least one block")
    result = maps[0]
    for map_ in maps[1:]:
        result = LinearMap.direct_sum(result, map_)
    return result


def _factor_for_entry(
    parent: PolynomialHomComplex,
    degree: int,
    row: int,
    column: int,
    left_factor: int,
    right_factor: int,
) -> str:
    """Return the x/u factor owning one Hom differential entry."""

    left_map = parent.left
    right_map = parent.right
    left_target_rank = len(left_map.target_shifts)
    right_target_rank = len(right_map.target_shifts)
    if degree == -1:
        first_rows = left_target_rank * right_target_rank
        factor = left_factor if row < first_rows else right_factor
        return "x" if factor == 0 else "u"
    if degree == 0:
        first_columns = left_target_rank * right_target_rank
        return "x" if column >= first_columns and left_factor == 0 else (
            "u" if column >= first_columns else ("x" if right_factor == 0 else "u")
        )
    raise ValueError("presentation Hom has differentials only in degrees -1 and 0")


def _factor_matrix(
    parent: PolynomialHomComplex,
    degree: int,
    left_factor: int,
    right_factor: int,
) -> tuple[tuple[str, ...], ...]:
    """Label every entry of one presentation Hom differential by its factor."""

    map_ = parent.differential(degree)
    return tuple(
        tuple(
            _factor_for_entry(
                parent,
                degree,
                row,
                column,
                left_factor,
                right_factor,
            )
            for column in range(map_.domain.rank)
        )
        for row in range(map_.codomain.rank)
    )


def _horizontal_map(
    parent: PolynomialHomComplex,
    degree: int,
    sheaf_degree: int,
    source_bundles: tuple[SchoenLineBundle, ...],
    target_bundles: tuple[SchoenLineBundle, ...],
    factors: tuple[tuple[str, ...], ...],
) -> LinearMap:
    """Evaluate one factor-aware polynomial Hom differential on cohomology."""

    polynomial_map = parent.differential(degree)
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
            else:
                row.append(
                    source_bundle.multiplication(
                        target_bundle,
                        polynomial,
                        factors[target_index][source_index],
                    ).component(sheaf_degree)
                )
        blocks.append(row)
    return LinearMap.block(blocks)


@dataclass(frozen=True, slots=True)
class SchoenOuterHom:
    """Exact signed cover totalization for one ordered presentation pair."""

    left: SchoenPresentation
    right: SchoenPresentation
    parent: PolynomialHomComplex
    lines: tuple[tuple[int, tuple[LineDegree, ...]], ...]
    bundles: tuple[tuple[int, tuple[SchoenLineBundle, ...]], ...]
    bicomplex: Bicomplex
    total: CochainComplex

    @property
    def squared_zero(self) -> bool:
        """Return the exact total differential square-zero gate."""

        return all(
            self.total.differential(degree + 1).compose(
                differential
            ).is_zero()
            for degree, differential in self.total.differentials
        )

    @property
    def all_line_bundles_squared_zero(self) -> bool:
        """Return whether every constituent Koszul complex is exact as a complex."""

        return all(
            bundle.squared_zero
            for _, selected in self.bundles
            for bundle in selected
        )

    @property
    def cover_ext_one_dimension(self) -> int:
        """Return the exact cover-level degree-one cohomology dimension."""

        return self.total.cohomology_dimension(1)

    def as_record(self) -> dict[str, object]:
        """Serialize the cover computation without a quotient claim."""

        return {
            "left_scheme": self.left.candidate.scheme.name,
            "right_scheme": self.right.candidate.scheme.name,
            "left_factor": self.left.factor,
            "right_factor": self.right.factor,
            "left_twist": list(self.left.twist),
            "right_twist": list(self.right.twist),
            "term_line_degrees": [
                [degree, [list(line) for line in line_degrees]]
                for degree, line_degrees in self.lines
            ],
            "total_dimensions": [
                [degree, self.total.spaces.space(degree).dimension]
                for degree in self.total.degrees
            ],
            "cover_ext_one_dimension": self.cover_ext_one_dimension,
            "squared_zero": self.squared_zero,
            "all_line_bundles_squared_zero": self.all_line_bundles_squared_zero,
            "status": (
                "exact Schoen cover Hom totalization; quotient-invariant Ext, "
                "extension representatives, and physical promotion remain unresolved"
            ),
        }


@cache
def schoen_outer_hom(
    left_ray: TierBSerreExtensionRay,
    right_ray: TierBSerreExtensionRay,
    left_factor: int,
    left_twist: Twist,
    right_factor: int,
    right_twist: Twist,
) -> SchoenOuterHom:
    """Compute one exact cover-level outer Hom totalization."""

    left = schoen_presentation(left_ray, left_factor, left_twist)
    right = schoen_presentation(right_ray, right_factor, right_twist)
    parent = polynomial_hom_complex(left.candidate, right.candidate)
    lines = _hom_term_lines(left, right)
    bundles = _term_bundles(lines)
    bundle_map = dict(bundles)
    spaces = {
        (parent_degree, sheaf_degree): _line_sum_space(
            f"Schoen Hom^{parent_degree},H^{sheaf_degree}",
            bundle_map[parent_degree],
            sheaf_degree,
        )
        for parent_degree, _ in lines
        for sheaf_degree in range(4)
    }
    vertical = {
        (parent_degree, sheaf_degree): _direct_sum_maps(
            tuple(
                bundle.complex.differential(sheaf_degree)
                for bundle in bundle_map[parent_degree]
            )
        )
        for parent_degree, _ in lines
        for sheaf_degree in range(3)
    }
    horizontal = {}
    factors = {
        degree: _factor_matrix(
            parent,
            degree,
            left_factor,
            right_factor,
        )
        for degree, _ in parent.differentials
    }
    for parent_degree, _ in parent.differentials:
        horizontal.update(
            {
                (parent_degree, sheaf_degree): _horizontal_map(
                    parent,
                    parent_degree,
                    sheaf_degree,
                    bundle_map[parent_degree],
                    bundle_map[parent_degree + 1],
                    factors[parent_degree],
                )
                for sheaf_degree in range(4)
            }
        )
    bicomplex = Bicomplex(
        "Schoen cover presentation Hom",
        spaces,
        horizontal=horizontal,
        vertical=vertical,
    )
    return SchoenOuterHom(
        left,
        right,
        parent,
        lines,
        bundles,
        bicomplex,
        bicomplex.totalize(),
    )


__all__ = [
    "SchoenOuterHom",
    "SchoenPresentation",
    "schoen_outer_hom",
    "schoen_presentation",
]
